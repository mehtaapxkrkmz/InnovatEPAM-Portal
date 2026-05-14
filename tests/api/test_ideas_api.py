from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from app.models.idea import IdeaCategory, IdeaPriority, IdeaRead, IdeaStatus
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
                "attachment_urls": [],
                "score": None,
            }
        }

    async def get_idea_by_id(self, idea_id: str):
        if idea_id not in self.ideas:
            raise ValueError("Idea not found")
        return self.ideas[idea_id]

    async def update_idea_status(
        self,
        idea_id: str,
        status: str,
        user_role: UserRole,
        current_user_email: str | None = None,
        evaluator_comment: str | None = None,
        score: int | None = None,
    ):
        if user_role not in [UserRole.ADMIN, UserRole.EVALUATOR]:
            raise PermissionError("Unauthorized role")
        if idea_id not in self.ideas:
            raise ValueError("Idea not found")
        self.ideas[idea_id]["status"] = status
        if evaluator_comment is not None:
            self.ideas[idea_id]["evaluator_comment"] = evaluator_comment
        if score is not None:
            self.ideas[idea_id]["score"] = score

    async def create_idea(self, payload, current_user: CurrentUser):
        idea_id = f"idea-{len(self.ideas) + 1}"
        self.ideas[idea_id] = {
            "id": idea_id,
            "title": payload.title,
            "description": payload.description,
            "category": payload.category,
            "priority": payload.priority,
            "estimated_budget": payload.estimated_budget,
            "status": getattr(payload, "initial_status", "submitted"),
            "created_by": str(current_user.email),
            "created_at": "2026-01-01T00:00:00Z",
            "attachment_urls": payload.attachment_urls,
            "score": None,
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


def test_draft_not_visible_to_other_admin_user():
    """A draft created by one user must NOT be visible to an admin with a different email."""
    from tests.unit.test_idea_service import InMemoryIdeaRepo
    from app.core.deps import get_current_user_optional
    from app.services.idea_service import IdeaService

    repo = InMemoryIdeaRepo()
    repo._ideas.append({
        "_id": "draft-1",
        "title": "Private Draft",
        "description": "Private draft idea description.",
        "category": "Product",
        "status": "draft",
        "created_by": "owner.user@epam.com",
        "created_at": datetime.now(timezone.utc),
        "priority": "MEDIUM",
        "attachment_urls": [],
    })
    service = IdeaService(idea_repository=repo)
    app.dependency_overrides[get_current_user_optional] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.get("/ideas")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    ids = [idea["id"] for idea in response.json()]
    assert "draft-1" not in ids


def test_logged_in_submitter_sees_public_ideas_and_own_drafts_only():
    from tests.unit.test_idea_service import InMemoryIdeaRepo
    from app.core.deps import get_current_user_optional
    from app.services.idea_service import IdeaService

    repo = InMemoryIdeaRepo()
    repo._ideas.extend(
        [
            {
                "_id": "public-1",
                "title": "Public Submitted",
                "description": "Visible to all users.",
                "category": "Product",
                "status": "submitted",
                "created_by": "owner.user@epam.com",
                "created_at": datetime.now(timezone.utc),
                "priority": "MEDIUM",
                "attachment_urls": [],
            },
            {
                "_id": "public-2",
                "title": "Other Public",
                "description": "Also visible to all users.",
                "category": "Process",
                "status": "accepted",
                "created_by": "someone.else@epam.com",
                "created_at": datetime.now(timezone.utc),
                "priority": "MEDIUM",
                "attachment_urls": [],
            },
            {
                "_id": "owner-draft",
                "title": "Owner Draft",
                "description": "Visible only to owner.",
                "category": "Product",
                "status": "draft",
                "created_by": "owner.user@epam.com",
                "created_at": datetime.now(timezone.utc),
                "priority": "MEDIUM",
                "attachment_urls": [],
            },
            {
                "_id": "other-draft",
                "title": "Other Draft",
                "description": "Must stay hidden.",
                "category": "Product",
                "status": "draft",
                "created_by": "someone.else@epam.com",
                "created_at": datetime.now(timezone.utc),
                "priority": "MEDIUM",
                "attachment_urls": [],
            },
        ]
    )
    service = IdeaService(idea_repository=repo)
    app.dependency_overrides[get_current_user_optional] = (
        lambda: CurrentUser(email="owner.user@epam.com", role=UserRole.SUBMITTER)
    )
    app.dependency_overrides[get_idea_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.get("/ideas")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    ids = {idea["id"] for idea in response.json()}
    assert ids == {"public-1", "public-2", "owner-draft"}


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
            "priority": "MEDIUM",
            "estimated_budget": None,
            "status": "submitted",
            "created_by": "owner.user@epam.com",
            "created_at": "2026-01-01T00:00:00Z",
            "attachment_urls": [],
            "evaluator_comment": None,
            "score": None,
        }
    ]


def test_submit_idea_with_file_returns_201_and_attachment_urls():
    service = MockIdeaService()
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="owner.user@epam.com", role=UserRole.SUBMITTER)
    )
    app.dependency_overrides[get_idea_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.post(
            "/ideas",
            data={
                "title": "Upload-enabled Idea",
                "description": "Idea submission with one text attachment.",
                "category": "Product",
            },
            files={"files": ("note.txt", b"attachment payload", "text/plain")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Upload-enabled Idea"
    assert body["created_by"] == "owner.user@epam.com"
    assert len(body["attachment_urls"]) == 1
    assert body["attachment_urls"][0].startswith("/uploads/")

    uploaded_file = Path(__file__).resolve().parents[2] / body["attachment_urls"][0].lstrip("/")
    if uploaded_file.exists():
        uploaded_file.unlink()


def test_submit_idea_allows_admin_role():
    service = MockIdeaService()
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.post(
            "/ideas",
            data={
                "title": "Admin Submitted Idea",
                "description": "Admins can submit ideas while also evaluating other submissions.",
                "category": "Process",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["created_by"] == "admin@epam.com"


def test_submit_idea_with_dynamic_fields_returns_priority_and_estimated_budget():
    service = MockIdeaService()
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="owner.user@epam.com", role=UserRole.SUBMITTER)
    )
    app.dependency_overrides[get_idea_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.post(
            "/ideas",
            data={
                "title": "Budgeted Idea",
                "description": "Idea submission with dynamic planning inputs for prioritization.",
                "category": "Product",
                "priority": IdeaPriority.HIGH.value,
                "estimated_budget": "25000.5",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["priority"] == IdeaPriority.HIGH.value
    assert body["estimated_budget"] == 25000.5
    assert body["status"] == IdeaStatus.SUBMITTED.value


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


def test_update_idea_status_allows_admin_with_evaluator_comment():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.patch(
            "/ideas/idea-1/status",
            json={
                "status": "under_review",
                "evaluator_comment": "Great direction. Please add measurable KPIs.",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "under_review",
        "evaluator_comment": "Great direction. Please add measurable KPIs.",
        "score": None,
    }


def test_update_idea_status_allows_admin_to_assign_score_and_persists():
    from tests.unit.test_idea_service import InMemoryIdeaRepo
    from app.services.idea_service import IdeaService

    repo = InMemoryIdeaRepo()
    repo._ideas = [
        {
            "_id": "idea-1",
            "title": "Owner Idea",
            "description": "Owner-specific idea",
            "category": "Product",
            "status": "submitted",
            "created_by": "owner.user@epam.com",
            "created_at": datetime.now(timezone.utc),
            "attachment_urls": [],
            "score": None,
        }
    ]
    service = IdeaService(idea_repository=repo)
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
    )
    app.dependency_overrides[get_idea_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.patch(
            "/ideas/idea-1/status",
            json={"status": "under_review", "score": 4},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["score"] == 4
    assert repo._ideas[0]["score"] == 4


def test_update_idea_status_forbidden_for_regular_user_when_setting_score():
    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(email="owner.user@epam.com", role=UserRole.SUBMITTER)
    )
    app.dependency_overrides[get_idea_service] = lambda: MockIdeaService()

    try:
        client = TestClient(app)
        response = client.patch(
            "/ideas/idea-1/status",
            json={"status": IdeaStatus.ACCEPTED.value, "score": 5},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


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
