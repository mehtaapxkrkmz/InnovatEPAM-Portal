from datetime import datetime, timezone
from datetime import timedelta
from uuid import uuid4

import jwt
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.security import hash_password
from app.core.security import verify_password
from app.models.user import UserCreate, UserInDB, UserRead


class AuthService:
    def __init__(self, user_repository) -> None:
        self.user_repository = user_repository

    async def register_user(self, payload: UserCreate | dict) -> UserRead:
        user_create = self._normalize_payload(payload)

        existing = await self.user_repository.get_by_email(user_create.email)
        if existing:
            raise ValueError("User with this email already exists")

        now = datetime.now(timezone.utc)
        user_in_db = UserInDB(
            _id=str(uuid4()),
            email=user_create.email,
            full_name=user_create.full_name,
            role=user_create.role,
            hashed_password=hash_password(user_create.password),
            created_at=now,
            is_active=True,
        )

        saved = await self.user_repository.create(user_in_db.model_dump(by_alias=True))

        return UserRead(
            id=str(saved.get("_id", user_in_db.id)),
            email=saved.get("email", user_in_db.email),
            full_name=saved.get("full_name", user_in_db.full_name),
            role=saved.get("role", user_in_db.role),
            created_at=saved.get("created_at", user_in_db.created_at),
            is_active=saved.get("is_active", user_in_db.is_active),
        )

    async def authenticate_user(self, email: str, password: str) -> dict:
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        hashed_password = user.get("hashed_password")
        if not hashed_password or not verify_password(password, hashed_password):
            raise ValueError("Invalid credentials")

        return user

    def create_access_token(self, data: dict) -> str:
        settings = get_settings()
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    def create_refresh_token(self, data: dict) -> str:
        settings = get_settings()
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.refresh_secret_key, algorithm=settings.algorithm)

    def _normalize_payload(self, payload: UserCreate | dict) -> UserCreate:
        if isinstance(payload, UserCreate):
            return payload

        try:
            return UserCreate.model_validate(payload)
        except ValidationError as exc:
            if any(err.get("loc") and err["loc"][-1] == "role" for err in exc.errors()):
                raise ValueError("Invalid role") from exc
            raise ValueError("Invalid registration payload") from exc
