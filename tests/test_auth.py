import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_register_user_success() -> None:
    payload = {
        "email": "test.user@example.com",
        "password": "StrongPass123",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/auth/register", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == payload["email"]
    assert data["role"] == "submitter"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data
