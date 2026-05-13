import pytest
from app.models.idea import IdeaCategory, IdeaCreate, IdeaStatus
from app.models.user import CurrentUser, UserRole
from app.services.idea_service import IdeaService
from datetime import datetime, timezone


class InMemoryIdeaRepo:
    def __init__(self) -> None:
        self._ideas: list[dict] = []
        self.last_owner_requested: str | None = None

    async def create(self, payload: dict) -> dict:
        self._ideas.append(payload)
        return payload

    async def find_by_owner(self, email: str, status: str | None = None) -> list[dict]:
        self.last_owner_requested = email
        results = [i for i in self._ideas if i.get("created_by") == email]
        if status is not None:
            results = [i for i in results if i.get("status") == status]
        return results

    async def get_by_id(self, idea_id: str) -> dict | None:
        return next((idea for idea in self._ideas if idea["_id"] == idea_id), None)

    async def update_status(
        self,
        idea_id: str,
        status: str,
        evaluator_comment: str | None = None,
    ) -> bool:
        for idea in self._ideas:
            if idea["_id"] == idea_id:
                idea["status"] = status
                if evaluator_comment is not None:
                    idea["evaluator_comment"] = evaluator_comment
                return True
        return False

    async def find_all(self, status: str | None = None) -> list[dict]:
        if status is not None:
            return [i for i in self._ideas if i.get("status") == status]
        return list(self._ideas)


def _mock_submitter(email: str = "submitter@epam.com") -> CurrentUser:
    return CurrentUser(email=email, role=UserRole.SUBMITTER)


@pytest.mark.asyncio
async def test_create_idea_success_returns_idea_with_id():
    repo = InMemoryIdeaRepo()
    service = IdeaService(idea_repository=repo)
    current_user = _mock_submitter()

    result = await service.create_idea(
        payload=IdeaCreate(
            title="AI Code Reviewer",
            description="An AI tool that reviews code automatically before PR merge.",
            category=IdeaCategory.PRODUCT,
        ),
        current_user=current_user,
    )

    assert result.id is not None
    assert result.title == "AI Code Reviewer"
    assert result.category == IdeaCategory.PRODUCT
    assert result.status == IdeaStatus.SUBMITTED
    assert result.created_by == str(current_user.email)


@pytest.mark.asyncio
async def test_create_idea_assigns_submitted_status_by_default():
    repo = InMemoryIdeaRepo()
    service = IdeaService(idea_repository=repo)
    current_user = _mock_submitter()

    result = await service.create_idea(
        payload=IdeaCreate(
            title="Process Optimizer",
            description="Automates repetitive internal processes to save engineer hours.",
            category=IdeaCategory.PROCESS,
        ),
        current_user=current_user,
    )

    assert result.status == IdeaStatus.SUBMITTED


@pytest.mark.asyncio
async def test_create_idea_tracks_ownership_from_current_user():
    repo = InMemoryIdeaRepo()
    service = IdeaService(idea_repository=repo)
    current_user = _mock_submitter("owner.user@epam.com")

    result = await service.create_idea(
        payload=IdeaCreate(
            title="Cost Dashboard",
            description="Real-time dashboard showing team cost efficiency metrics.",
            category=IdeaCategory.COST_SAVINGS,
        ),
        current_user=current_user,
    )

    assert result.created_by == "owner.user@epam.com"


@pytest.mark.asyncio
async def test_get_user_ideas_returns_only_current_user_ideas():
    repo = InMemoryIdeaRepo()
    service = IdeaService(idea_repository=repo)
    current_user = _mock_submitter("owner.user@epam.com")

    repo._ideas = [
        {
            "_id": "idea-1",
            "title": "Owner Idea",
            "description": "Idea created by owner user.",
            "category": IdeaCategory.PRODUCT,
            "status": IdeaStatus.SUBMITTED,
            "created_by": "owner.user@epam.com",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "_id": "idea-2",
            "title": "Other Idea",
            "description": "Idea created by another user.",
            "category": IdeaCategory.PROCESS,
            "status": IdeaStatus.SUBMITTED,
            "created_by": "another.user@epam.com",
            "created_at": datetime.now(timezone.utc),
        },
    ]

    result = await service.get_user_ideas(email=str(current_user.email), role=UserRole.SUBMITTER)

    assert repo.last_owner_requested == "owner.user@epam.com"
    assert len(result) == 1
    assert all(idea.created_by == "owner.user@epam.com" for idea in result)


@pytest.mark.asyncio
async def test_get_user_ideas_returns_all_ideas_for_admin():
    repo = InMemoryIdeaRepo()
    service = IdeaService(idea_repository=repo)

    repo._ideas = [
        {
            "_id": "idea-1",
            "title": "Owner Idea",
            "description": "Idea created by owner user.",
            "category": IdeaCategory.PRODUCT,
            "status": IdeaStatus.SUBMITTED,
            "created_by": "owner.user@epam.com",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "_id": "idea-2",
            "title": "Other Idea",
            "description": "Idea created by another user.",
            "category": IdeaCategory.PROCESS,
            "status": IdeaStatus.SUBMITTED,
            "created_by": "another.user@epam.com",
            "created_at": datetime.now(timezone.utc),
        },
    ]

    result = await service.get_user_ideas(email="admin@epam.com", role="admin")

    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_user_ideas_filters_by_status_for_admin():
    repo = InMemoryIdeaRepo()
    service = IdeaService(idea_repository=repo)

    repo._ideas = [
        {
            "_id": "idea-1",
            "title": "Submitted Idea",
            "description": "Still pending.",
            "category": IdeaCategory.PRODUCT,
            "status": IdeaStatus.SUBMITTED,
            "created_by": "owner.user@epam.com",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "_id": "idea-2",
            "title": "Accepted Idea",
            "description": "Already accepted.",
            "category": IdeaCategory.PROCESS,
            "status": IdeaStatus.ACCEPTED,
            "created_by": "another.user@epam.com",
            "created_at": datetime.now(timezone.utc),
        },
    ]

    result = await service.get_user_ideas(email="admin@epam.com", role="admin", status=IdeaStatus.SUBMITTED)

    assert len(result) == 1
    assert result[0].status == IdeaStatus.SUBMITTED


@pytest.mark.asyncio
async def test_get_idea_by_id_returns_correct_idea():
    repo = InMemoryIdeaRepo()
    service = IdeaService(idea_repository=repo)
    current_user = _mock_submitter("owner.user@epam.com")

    repo._ideas = [
        {
            "_id": "idea-1",
            "title": "Owner Idea",
            "description": "Idea created by owner user.",
            "category": IdeaCategory.PRODUCT,
            "status": IdeaStatus.SUBMITTED,
            "created_by": "owner.user@epam.com",
            "created_at": datetime.now(timezone.utc),
        }
    ]

    result = await service.get_idea_by_id("idea-1")

    assert result.id == "idea-1"
    assert result.title == "Owner Idea"
    assert result.created_by == "owner.user@epam.com"


@pytest.mark.asyncio
async def test_update_idea_status_allows_admin_to_change_status():
    repo = InMemoryIdeaRepo()
    service = IdeaService(idea_repository=repo)
    admin_user = UserRole.ADMIN

    repo._ideas = [
        {
            "_id": "idea-1",
            "title": "Owner Idea",
            "description": "Idea created by owner user.",
            "category": IdeaCategory.PRODUCT,
            "status": IdeaStatus.SUBMITTED,
            "created_by": "owner.user@epam.com",
            "created_at": datetime.now(timezone.utc),
        }
    ]

    await service.update_idea_status("idea-1", IdeaStatus.ACCEPTED, admin_user)

    updated_idea = await service.get_idea_by_id("idea-1")
    assert updated_idea.status == IdeaStatus.ACCEPTED


@pytest.mark.asyncio
async def test_update_idea_status_forbidden_for_submitter():
    repo = InMemoryIdeaRepo()
    service = IdeaService(idea_repository=repo)
    submitter_user = UserRole.SUBMITTER

    repo._ideas = [
        {
            "_id": "idea-1",
            "title": "Owner Idea",
            "description": "Idea created by owner user.",
            "category": IdeaCategory.PRODUCT,
            "status": IdeaStatus.SUBMITTED,
            "created_by": "owner.user@epam.com",
            "created_at": datetime.now(timezone.utc),
        }
    ]

    with pytest.raises(PermissionError):
        await service.update_idea_status("idea-1", IdeaStatus.ACCEPTED, submitter_user)


@pytest.mark.asyncio
async def test_update_idea_status_saves_evaluator_comment_when_provided():
    repo = InMemoryIdeaRepo()
    service = IdeaService(idea_repository=repo)

    repo._ideas = [
        {
            "_id": "idea-1",
            "title": "Owner Idea",
            "description": "Idea created by owner user.",
            "category": IdeaCategory.PRODUCT,
            "status": IdeaStatus.SUBMITTED,
            "created_by": "owner.user@epam.com",
            "created_at": datetime.now(timezone.utc),
        }
    ]

    await service.update_idea_status(
        "idea-1",
        IdeaStatus.UNDER_REVIEW,
        UserRole.ADMIN,
        evaluator_comment="Needs risk assessment section before final review.",
    )

    assert repo._ideas[0]["status"] == IdeaStatus.UNDER_REVIEW
    assert (
        repo._ideas[0]["evaluator_comment"]
        == "Needs risk assessment section before final review."
    )
