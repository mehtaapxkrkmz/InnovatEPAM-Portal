"""
Tests for database repository layer - IdeaRepository
"""
import pytest
from datetime import datetime, timezone
from app.db.repositories.idea_repository import IdeaRepository
from app.models.idea import IdeaInDB


class MockAsyncCursor:
    def __init__(self, data):
        self.data = data
    
    async def to_list(self, length=None):
        return self.data


class MockAsyncCollection:
    def __init__(self):
        self.storage = {}
        self.find_data = []
    
    async def insert_one(self, payload):
        idea_id = payload.get("_id", "id-1")
        self.storage[idea_id] = payload
    
    async def find_one(self, query):
        for item in self.storage.values():
            match = all(item.get(k) == v for k, v in query.items())
            if match:
                return item
        return None
    
    def find(self, query):
        results = []
        for item in self.storage.values():
            match = all(item.get(k) == v for k, v in query.items())
            if match:
                results.append(item)
        return MockAsyncCursor(results)
    
    async def update_one(self, query, update):
        for item in self.storage.values():
            match = all(item.get(k) == v for k, v in query.items())
            if match:
                if "$set" in update:
                    item.update(update["$set"])
                return type('obj', (object,), {'modified_count': 1})()
        return type('obj', (object,), {'modified_count': 0})()


class MockAsyncDatabase:
    def __init__(self):
        self.collections = {}
    
    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = MockAsyncCollection()
        return self.collections[name]


@pytest.mark.asyncio
async def test_idea_repository_create_with_idea_object():
    """Test IdeaRepository.create with IdeaInDB object."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    idea = IdeaInDB(
        id="idea-1",
        title="Test Idea",
        description="Test description",
        category="Product",
        status="submitted",
        created_by="user@epam.com",
        created_at=datetime.now(timezone.utc),
    )
    
    result = await repo.create(idea)
    assert result["title"] == "Test Idea"
    assert result["created_by"] == "user@epam.com"


@pytest.mark.asyncio
async def test_idea_repository_create_with_dict():
    """Test IdeaRepository.create with plain dict."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    payload = {
        "_id": "idea-2",
        "title": "Dict Idea",
        "description": "Dict description",
        "category": "Process",
        "status": "draft",
        "created_by": "dict@epam.com",
        "created_at": datetime.now(timezone.utc),
    }
    
    result = await repo.create(payload)
    assert result["title"] == "Dict Idea"


@pytest.mark.asyncio
async def test_idea_repository_find_by_owner():
    """Test IdeaRepository.find_by_owner filters by email."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    await repo.create({
        "_id": "idea-1",
        "created_by": "owner@epam.com",
        "status": "submitted",
        "title": "Idea 1",
    })
    await repo.create({
        "_id": "idea-2",
        "created_by": "other@epam.com",
        "status": "submitted",
        "title": "Idea 2",
    })
    
    results = await repo.find_by_owner("owner@epam.com")
    assert len(results) == 1
    assert results[0]["created_by"] == "owner@epam.com"


@pytest.mark.asyncio
async def test_idea_repository_find_by_owner_with_status_filter():
    """Test IdeaRepository.find_by_owner with status filter."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    await repo.create({
        "_id": "idea-1",
        "created_by": "owner@epam.com",
        "status": "submitted",
        "title": "Submitted",
    })
    await repo.create({
        "_id": "idea-2",
        "created_by": "owner@epam.com",
        "status": "draft",
        "title": "Draft",
    })
    
    results = await repo.find_by_owner("owner@epam.com", status="draft")
    assert len(results) == 1
    assert results[0]["status"] == "draft"


@pytest.mark.asyncio
async def test_idea_repository_get_by_id():
    """Test IdeaRepository.get_by_id retrieves by ID."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    await repo.create({
        "_id": "idea-1",
        "title": "Get Test",
        "created_by": "user@epam.com",
    })
    
    result = await repo.get_by_id("idea-1")
    assert result is not None
    assert result["title"] == "Get Test"


@pytest.mark.asyncio
async def test_idea_repository_get_by_id_not_found():
    """Test IdeaRepository.get_by_id returns None when not found."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    result = await repo.get_by_id("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_idea_repository_find_all():
    """Test IdeaRepository.find_all retrieves all ideas."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    await repo.create({"_id": "idea-1", "title": "Idea 1", "status": "submitted"})
    await repo.create({"_id": "idea-2", "title": "Idea 2", "status": "draft"})
    
    results = await repo.find_all()
    assert len(results) == 2


@pytest.mark.asyncio
async def test_idea_repository_find_all_with_status_filter():
    """Test IdeaRepository.find_all filters by status."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    await repo.create({"_id": "idea-1", "title": "Idea 1", "status": "submitted"})
    await repo.create({"_id": "idea-2", "title": "Idea 2", "status": "submitted"})
    await repo.create({"_id": "idea-3", "title": "Idea 3", "status": "draft"})
    
    results = await repo.find_all(status="submitted")
    assert len(results) == 2
    assert all(r["status"] == "submitted" for r in results)


@pytest.mark.asyncio
async def test_idea_repository_update_status():
    """Test IdeaRepository.update_status changes status."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    await repo.create({"_id": "idea-1", "title": "Idea", "status": "submitted"})
    
    result = await repo.update_status("idea-1", "accepted")
    assert result is True
    
    idea = await repo.get_by_id("idea-1")
    assert idea["status"] == "accepted"


@pytest.mark.asyncio
async def test_idea_repository_update_status_with_comment():
    """Test IdeaRepository.update_status with evaluator comment."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    await repo.create({"_id": "idea-1", "title": "Idea"})
    
    result = await repo.update_status(
        "idea-1",
        "under_review",
        evaluator_comment="Needs more details"
    )
    assert result is True
    
    idea = await repo.get_by_id("idea-1")
    assert idea["evaluator_comment"] == "Needs more details"


@pytest.mark.asyncio
async def test_idea_repository_update_status_with_score():
    """Test IdeaRepository.update_status with score."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    await repo.create({"_id": "idea-1", "title": "Idea"})
    
    result = await repo.update_status("idea-1", "accepted", score=5)
    assert result is True
    
    idea = await repo.get_by_id("idea-1")
    assert idea["score"] == 5


@pytest.mark.asyncio
async def test_idea_repository_update_status_not_found():
    """Test IdeaRepository.update_status returns False for missing idea."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    result = await repo.update_status("nonexistent", "accepted")
    assert result is False


@pytest.mark.asyncio
async def test_idea_repository_list_by_owner():
    """Test IdeaRepository.list_by_owner aliases find_by_owner."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    await repo.create({
        "_id": "idea-1",
        "created_by": "owner@epam.com",
        "title": "My Idea",
    })
    
    results = await repo.list_by_owner("owner@epam.com")
    assert len(results) == 1
    assert results[0]["created_by"] == "owner@epam.com"


@pytest.mark.asyncio
async def test_idea_repository_find_by_id():
    """Test IdeaRepository.find_by_id aliases get_by_id."""
    db = MockAsyncDatabase()
    repo = IdeaRepository(db)
    
    await repo.create({"_id": "idea-1", "title": "Find Test"})
    
    result = await repo.find_by_id("idea-1")
    assert result is not None
    assert result["title"] == "Find Test"
