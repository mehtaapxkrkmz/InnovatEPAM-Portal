from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from app.models.idea import IdeaCategory, IdeaRead, IdeaStatus
from app.models.user import CurrentUser, UserRole

from app.api.endpoints.ideas import get_idea_service
from app.core.deps import get_current_user
from app.main import app


class MockIdeaService:
    def __init__(self) -> None:
        self.ideas = {
            "idea-1": {
                "id": "idea-1",
                "title": "Owner Idea",
                "description": "Owner-specific idea",
                "category": "Product",
                "status": "submitted",
                "created_by": "owner.user@epam.com",
                "created_at": "2026-01-01T00:00:00Z",
                "attachment_url": None,
            }
        }

    async def get_idea_by_id(self, idea_id: str):
        if idea_id not in self.ideas:
            raise ValueError("Idea not found")
        return self.ideas[idea_id]

    async def update_idea_status(self, idea_id: str, status: str, user_role: UserRole):
        if user_role not in [UserRole.ADMIN, UserRole.EVALUATOR]:
            raise PermissionError("Unauthorized role")
        if idea_id not in self.ideas:
            raise ValueError("Idea not found")
        self.ideas[idea_id]["status"] = status

    async def create_idea(self, payload, current_user: CurrentUser):
        idea_id = f"idea-{len(self.ideas) + 1}"
        self.ideas[idea_id] = {
            "id": idea_id,
            "title": payload.title,
            "description": payload.description,
            "category": payload.category,
            "status": "submitted",
            "created_by": str(current_user.email),
            "created_at": "2026-01-01T00:00:00Z",
            "attachment_url": payload.attachment_url,
        }
        return self.ideas[idea_id]

    async def get_user_ideas(self, email: str, role: UserRole = UserRole.SUBMITTER, status=None):
        ideas = list(self.ideas.values()) if role in (UserRole.ADMIN, UserRole.EVALUATOR) else [
            idea for idea in self.ideas.values() if idea["created_by"] == email
        ]
        if status is not None:
            ideas = [idea for idea in ideas if idea["status"] == status.value]
        return ideas


def test_get_ideas_with_status_filter_returns_only_matching():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        # The seeded idea has status "submitted" — filter for "accepted" should return empty
        response = client.get("/ideas", params={"status": "accepted"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []


def test_get_ideas_with_mixed_case_status_filter_does_not_422():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.get("/ideas", params={"status": "Submitted"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_ideas_invalid_status_filter_returns_400_not_422():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.get("/ideas", params={"status": "in-progress"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400


def test_get_ideas_empty_status_filter_returns_400_not_422():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.get("/ideas", params={"status": ""})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400


def test_get_ideas_as_admin_returns_all_ideas():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.get("/ideas")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1  # MockIdeaService seeds one idea
    assert body[0]["created_by"] == "owner.user@epam.com"


def test_get_ideas_returns_200_and_owner_ideas_list():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="owner.user@epam.com", role=UserRole.SUBMITTER)
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
        lambda: CurrentUser(email="owner.user@epam.com", role=UserRole.SUBMITTER)
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


def test_get_idea_by_id_returns_correct_idea():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="owner.user@epam.com", role=UserRole.SUBMITTER)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.get("/ideas/idea-1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "idea-1"
    assert body["title"] == "Owner Idea"
    assert body["created_by"] == "owner.user@epam.com"


def test_update_idea_status_allows_admin():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.patch(
            "/ideas/idea-1/status",
            json={"status": IdeaStatus.ACCEPTED.value},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == IdeaStatus.ACCEPTED.value


def test_update_idea_status_forbidden_for_submitter():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="owner.user@epam.com", role=UserRole.SUBMITTER)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.patch(
            "/ideas/idea-1/status",
            json={"status": IdeaStatus.ACCEPTED.value},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_update_idea_status_accepts_enum_name_without_422():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.patch(
            "/ideas/idea-1/status",
            json={"status": "ACCEPTED"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == IdeaStatus.ACCEPTED.value


def test_update_idea_status_accepts_plain_string_body_without_422():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.patch(
            "/ideas/idea-1/status",
            json="accepted",
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400


def test_update_idea_status_invalid_payload_returns_400_not_422():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.patch(
            "/ideas/idea-1/status",
            json={"state": "accepted"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
