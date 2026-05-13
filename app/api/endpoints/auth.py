from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_current_user
from app.db.client import get_database
from app.db.repositories.user_repository import UserRepository
from app.models.auth import LoginRequest
from app.models.token import Token
from app.models.user import CurrentUser, UserCreate, UserRead
from app.services.auth_service import AuthService

router = APIRouter()

REGISTER_RESPONSES = {
    201: {
        "description": "Succeed Request Example",
        "content": {
            "application/json": {
                "example": {
                    "id": "user-1",
                    "email": "jane.doe@epam.com",
                    "full_name": "Jane Doe",
                    "role": "submitter",
                    "created_at": "2026-05-13T09:00:00Z",
                    "is_active": True,
                }
            }
        },
    },
    400: {
        "description": "Failed Request Example",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Invalid registration payload",
                }
            }
        },
    },
    409: {
        "description": "Failed Request Example",
        "content": {
            "application/json": {
                "example": {
                    "detail": "User with this email already exists",
                }
            }
        },
    },
}

LOGIN_RESPONSES = {
    200: {
        "description": "Succeed Request Example",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access-token",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh-token",
                    "token_type": "bearer",
                }
            }
        },
    },
    400: {
        "description": "Failed Request Example",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Validation failed",
                }
            }
        },
    },
    401: {
        "description": "Failed Request Example",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Invalid credentials",
                }
            }
        },
    },
}


LOGOUT_RESPONSES = {
    200: {
        "description": "Logged out successfully",
        "content": {
            "application/json": {
                "example": {"message": "Logged out successfully"}
            }
        },
    },
    401: {
        "description": "Not authenticated",
        "content": {
            "application/json": {
                "example": {"detail": "Not authenticated"}
            }
        },
    },
}


def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> AuthService:
    return AuthService(user_repository=UserRepository(db))


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses=REGISTER_RESPONSES,
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Authenticate a user and return tokens",
    responses=LOGIN_RESPONSES,
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


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout the current user",
    responses=LOGOUT_RESPONSES,
)
async def logout_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    # Stateless JWT: the access token remains valid until expiry.
    # The client is responsible for discarding both tokens on receipt of 200.
    return {"message": "Logged out successfully"}
