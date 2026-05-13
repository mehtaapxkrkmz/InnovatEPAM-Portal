from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.endpoints.ideas import get_idea_service
from app.core.deps import get_current_user
from app.main import app
from app.models.idea import IdeaCategory, IdeaRead, IdeaStatus


class MockIdeaService:
    def __init__(self) -> None:
        self.last_payload = None
        self.last_user = None

    async def create_idea(self, payload, current_user: dict) -> IdeaRead:
        self.last_payload = payload
        self.last_user = current_user
        return IdeaRead(
            id="idea-upload-1",
            title=payload.title,
            description=payload.description,
            category=payload.category,
            status=IdeaStatus.SUBMITTED,
            created_by=current_user["email"],
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            attachment_url=payload.attachment_url,
        )

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
                attachment_url=None,
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
            "attachment_url": None,
        }
    ]


def test_submit_idea_with_file_returns_201_and_attachment_url():
    service = MockIdeaService()
    app.dependency_overrides[get_current_user] = (
        lambda: {"email": "owner.user@epam.com", "role": "submitter"}
    )
    app.dependency_overrides[get_idea_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.post(
            "/ideas/submit",
            data={
                "title": "Upload-enabled Idea",
                "description": "Idea submission with one text attachment.",
                "category": "Product",
            },
            files={"file": ("note.txt", b"attachment payload", "text/plain")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Upload-enabled Idea"
    assert body["created_by"] == "owner.user@epam.com"
    assert body["attachment_url"] is not None
    assert body["attachment_url"].startswith("/uploads/")

    uploaded_file = Path(__file__).resolve().parents[2] / body["attachment_url"].lstrip("/")
    if uploaded_file.exists():
        uploaded_file.unlink()
