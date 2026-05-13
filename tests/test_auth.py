import pytest
from httpx import ASGITransport, AsyncClient

from app.api.endpoints.auth import get_auth_service
from app.main import app
from app.models.user import UserCreate, UserRead, UserRole


class MockAuthService:
    async def register_user(self, payload: UserCreate) -> UserRead:
        return UserRead(
            id="user-1",
            email=payload.email,
            full_name=payload.full_name,
            role=payload.role,
            created_at="2026-01-01T00:00:00Z",
            is_active=True,
        )


@pytest.mark.asyncio
async def test_register_user_success() -> None:
    payload = {
        "email": "test.user@example.com",
        "full_name": "Test User",
        "password": "StrongPass123",
    }

    app.dependency_overrides[get_auth_service] = lambda: MockAuthService()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/auth/register", json=payload)

    app.dependency_overrides.clear()

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == payload["email"]
    assert data["role"] == UserRole.SUBMITTER.value
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_logout_user_success() -> None:
    """POST /auth/logout with a valid Bearer token returns 200 and success message."""
    from app.core.deps import get_current_user
    from app.models.user import CurrentUser

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        email="test.user@example.com", role=UserRole.SUBMITTER
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/auth/logout")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out successfully"}


@pytest.mark.asyncio
async def test_logout_user_unauthenticated_returns_401() -> None:
    """POST /auth/logout without an Authorization header returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/auth/logout")

    assert response.status_code == 401
