from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.api.endpoints.ideas import get_idea_service
from app.core.deps import get_current_user
from app.main import app
from app.models.idea import IdeaCategory, IdeaRead, IdeaStatus


class MockIdeaService:
    async def get_user_ideas(self, email: str) -> list[IdeaRead]:
        return [
            IdeaRead(
                id="idea-1",
                title="Owner Idea",
                description="Owner-specific idea",
                category=IdeaCategory.PRODUCT,
                status=IdeaStatus.SUBMITTED,
                created_by=email,
                created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            )
        ]


def test_get_ideas_returns_200_and_owner_ideas_list():
    app.dependency_overrides[get_current_user] = (
        lambda: {"email": "owner.user@epam.com", "role": "submitter"}
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.get("/ideas")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "idea-1",
            "title": "Owner Idea",
            "description": "Owner-specific idea",
            "category": "Product",
            "status": "submitted",
            "created_by": "owner.user@epam.com",
            "created_at": "2026-01-01T00:00:00Z",
        }
    ]
