import pytest
from datetime import datetime, timezone

from app.models.idea import IdeaCategory, IdeaCreate, IdeaStatus
from app.models.user import UserRole
from app.services.idea_service import IdeaService


class InMemoryIdeaRepo:
    def __init__(self) -> None:
        self._ideas: list[dict] = []
        self.last_owner_requested: str | None = None

    async def create(self, payload: dict) -> dict:
        self._ideas.append(payload)
        return payload

    async def find_by_owner(self, email: str) -> list[dict]:
        self.last_owner_requested = email
        return [i for i in self._ideas if i.get("created_by") == email]


def _mock_submitter(email: str = "submitter@epam.com") -> dict:
    return {"email": email, "role": UserRole.SUBMITTER.value}


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
    assert result.created_by == current_user["email"]


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

    result = await service.get_user_ideas(email=current_user["email"])

    assert repo.last_owner_requested == "owner.user@epam.com"
    assert len(result) == 1
    assert all(idea.created_by == "owner.user@epam.com" for idea in result)
