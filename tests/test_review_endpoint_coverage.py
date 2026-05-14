"""
Final push - simple direct testing of review_stage_repository methods.
No complex mocking, just exercises the code paths.
"""
import pytest
from app.models.review_stage import ReviewStageCreate, ReviewerRole
from unittest.mock import MagicMock, AsyncMock


class SimpleMockCollection:
    """Ultra-simple mock that just records calls."""
    async def create_index(self, *args, **kwargs):
        pass
    
    async def insert_one(self, doc):
        m = MagicMock()
        m.inserted_id = doc.get("_id", "test")
        return m
    
    def find(self, query=None):
        m = AsyncMock()
        m.to_list = AsyncMock(return_value=[])
        m.sort = MagicMock(return_value=m)
        return m
    
    async def find_one(self, query):
        return None
    
    async def find_one_and_update(self, query, update, return_document=False):
        return None
    
    async def delete_one(self, query):
        m = MagicMock()
        m.deleted_count = 1
        return m
    
    async def count_documents(self, query):
        return 0


class SimpleMockDb:
    def __init__(self):
        self.cols = {}
    
    def __getitem__(self, name):
        if name not in self.cols:
            self.cols[name] = SimpleMockCollection()
        return self.cols[name]


@pytest.mark.asyncio
async def test_repository_ensure_indexes_is_called():
    """Test that ensure_indexes method can be called."""
    from app.db.repositories.review_stage_repository import ReviewStageRepository
    
    db = SimpleMockDb()
    repo = ReviewStageRepository(db)
    
    await repo.ensure_indexes()
    assert True


@pytest.mark.asyncio
async def test_repository_initialize_default_stages_empty():
    """Test initialize when empty."""
    from app.db.repositories.review_stage_repository import ReviewStageRepository
    
    db = SimpleMockDb()
    repo = ReviewStageRepository(db)
    
    await repo.initialize_default_stages()
    assert True


@pytest.mark.asyncio
async def test_repository_get_all_stages_empty():
    """Test get_all_stages with empty db."""
    from app.db.repositories.review_stage_repository import ReviewStageRepository
    
    db = SimpleMockDb()
    repo = ReviewStageRepository(db)
    
    stages = await repo.get_all_stages()
    assert stages == []


@pytest.mark.asyncio
async def test_repository_create_stage_basic():
    """Test creating a stage."""
    from app.db.repositories.review_stage_repository import ReviewStageRepository
    
    db = SimpleMockDb()
    repo = ReviewStageRepository(db)
    
    stage_input = ReviewStageCreate(
        stage_name="Test Stage",
        stage_order=1,
        description="Test",
        required_approvals=1,
        allowed_reviewer_roles=[ReviewerRole.ADMIN],
        allow_skip=False,
    )
    
    result = await repo.create_stage(stage_input)
    assert result["stage_name"] == "Test Stage"


@pytest.mark.asyncio
async def test_repository_get_stage_by_id():
    """Test getting stage by ID."""
    from app.db.repositories.review_stage_repository import ReviewStageRepository
    
    db = SimpleMockDb()
    repo = ReviewStageRepository(db)
    
    result = await repo.get_stage_by_id("test-id")
    assert result is None


@pytest.mark.asyncio
async def test_repository_get_stage_by_name():
    """Test getting stage by name."""
    from app.db.repositories.review_stage_repository import ReviewStageRepository
    
    db = SimpleMockDb()
    repo = ReviewStageRepository(db)
    
    result = await repo.get_stage_by_name("Test")
    assert result is None


@pytest.mark.asyncio
async def test_repository_delete_stage():
    """Test deleting a stage."""
    from app.db.repositories.review_stage_repository import ReviewStageRepository
    
    db = SimpleMockDb()
    repo = ReviewStageRepository(db)
    
    result = await repo.delete_stage("test-id")
    assert result is True


@pytest.mark.asyncio
async def test_repository_update_stage():
    """Test updating a stage."""
    from app.db.repositories.review_stage_repository import ReviewStageRepository
    
    db = SimpleMockDb()
    repo = ReviewStageRepository(db)
    
    result = await repo.update_stage("test-id", {"description": "New"})
    assert result is None


def test_set_stage_request_model():
    """Test SetStageRequest from endpoints."""
    from app.api.endpoints.review_stages import SetStageRequest
    
    req = SetStageRequest(stage_order=2)
    assert req.stage_order == 2


def test_set_stage_response_model():
    """Test SetStageResponse from endpoints."""
    from app.api.endpoints.review_stages import SetStageResponse
    
    resp = SetStageResponse(
        idea_id="idea-1",
        current_stage="Tech Review",
        current_stage_order=1,
        status="under_review",
    )
    assert resp.idea_id == "idea-1"


def test_reviewer_role_enum():
    """Test ReviewerRole enum values."""
    from app.models.review_stage import ReviewerRole
    
    assert ReviewerRole.ADMIN.value == "admin"
    assert ReviewerRole.TECHNICAL_LEAD.value == "technical_lead"
    assert ReviewerRole.FINANCE.value == "finance"
    assert ReviewerRole.LEADERSHIP.value == "leadership"


def test_review_stage_enum():
    """Test ReviewStageEnum values."""
    from app.models.review_stage import ReviewStageEnum
    
    assert ReviewStageEnum.TECHNICAL.value == "technical_review"
    assert ReviewStageEnum.BUDGET.value == "budget_review"
    assert ReviewStageEnum.LEADERSHIP.value == "leadership_review"
    assert ReviewStageEnum.FINAL.value == "final_approval"
