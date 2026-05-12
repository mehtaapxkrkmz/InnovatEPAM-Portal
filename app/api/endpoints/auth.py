from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr, Field

from app.db.client import get_database
from app.db.repositories.user_repository import UserRepository
from app.models.token import Token
from app.models.user import UserCreate, UserRead
from app.services.auth_service import AuthService

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> AuthService:
    return AuthService(user_repository=UserRepository(db))


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    payload: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    try:
        return await auth_service.register_user(payload)
    except ValueError as exc:
        message = str(exc)
        if "already exists" in message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message) from exc


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Authenticate a user and return tokens",
)
async def login_user(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    try:
        user = await auth_service.authenticate_user(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc

    claims = {
        "sub": user.get("email"),
        "role": str(user.get("role")),
    }
    return Token(
        access_token=auth_service.create_access_token(claims),
        refresh_token=auth_service.create_refresh_token(claims),
        token_type="bearer",
    )
