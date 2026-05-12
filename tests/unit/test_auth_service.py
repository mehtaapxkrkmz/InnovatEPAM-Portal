import pytest

from app.core.security import hash_password
from app.models.user import UserCreate, UserRole
from app.services.auth_service import AuthService


class InMemoryUserRepo:
    def __init__(self) -> None:
        self._users_by_email: dict[str, dict] = {}

    async def get_by_email(self, email: str):
        return self._users_by_email.get(email)

    async def create(self, payload: dict):
        self._users_by_email[payload["email"]] = payload
        return payload


@pytest.mark.asyncio
async def test_register_user_success_with_valid_data():
    repo = InMemoryUserRepo()
    service = AuthService(user_repository=repo)

    result = await service.register_user(
        UserCreate(
            email="jane.doe@epam.com",
            full_name="Jane Doe",
            role=UserRole.SUBMITTER,
            password="StrongPass123!",
        )
    )

    assert result.email == "jane.doe@epam.com"
    assert result.role == UserRole.SUBMITTER
    assert result.is_active is True


@pytest.mark.asyncio
async def test_register_user_rejects_duplicate_email():
    repo = InMemoryUserRepo()
    service = AuthService(user_repository=repo)

    payload = UserCreate(
        email="duplicate@epam.com",
        full_name="Duplicate User",
        role=UserRole.SUBMITTER,
        password="StrongPass123!",
    )

    await service.register_user(payload)

    with pytest.raises(ValueError, match="already exists"):
        await service.register_user(payload)


@pytest.mark.asyncio
async def test_register_user_rejects_invalid_role():
    repo = InMemoryUserRepo()
    service = AuthService(user_repository=repo)

    with pytest.raises(ValueError, match="Invalid role"):
        await service.register_user(
            {
                "email": "invalid.role@epam.com",
                "full_name": "Role Error",
                "role": "owner",
                "password": "StrongPass123!",
            }
        )


@pytest.mark.asyncio
async def test_authenticate_user_success_with_valid_credentials():
    repo = InMemoryUserRepo()
    service = AuthService(user_repository=repo)

    email = "login.success@epam.com"
    plain_password = "StrongPass123!"
    repo._users_by_email[email] = {
        "_id": "user-1",
        "email": email,
        "full_name": "Login Success",
        "role": UserRole.SUBMITTER,
        "hashed_password": hash_password(plain_password),
        "created_at": "2026-05-13T00:00:00Z",
        "is_active": True,
    }

    result = await service.authenticate_user(email=email, password=plain_password)

    assert result is not None
    assert result.get("email") == email


@pytest.mark.asyncio
async def test_authenticate_user_raises_on_wrong_password():
    repo = InMemoryUserRepo()
    service = AuthService(user_repository=repo)

    email = "wrong.password@epam.com"
    repo._users_by_email[email] = {
        "_id": "user-2",
        "email": email,
        "full_name": "Wrong Password",
        "role": UserRole.SUBMITTER,
        "hashed_password": hash_password("CorrectPass123!"),
        "created_at": "2026-05-13T00:00:00Z",
        "is_active": True,
    }

    with pytest.raises(ValueError, match="Invalid credentials"):
        await service.authenticate_user(email=email, password="WrongPass123!")


@pytest.mark.asyncio
async def test_authenticate_user_raises_when_user_not_found():
    repo = InMemoryUserRepo()
    service = AuthService(user_repository=repo)

    with pytest.raises(ValueError, match="Invalid credentials"):
        await service.authenticate_user(
            email="not.found@epam.com",
            password="SomePass123!",
        )
