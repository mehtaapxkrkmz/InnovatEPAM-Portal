from pathlib import Path
from uuid import uuid4

from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_current_user
from app.db.client import get_database
from app.db.repositories.idea_repository import IdeaRepository
from app.models.idea import (
    IdeaCategory,
    IdeaCreate,
    IdeaRead,
    IdeaStatus,
    IdeaStatusUpdate,
    IdeaStatusUpdateResponse,
)
from app.models.user import CurrentUser, UserRole
from app.services.idea_service import IdeaService

router = APIRouter()
MAX_ATTACHMENT_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_ATTACHMENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/plain",
}
UPLOADS_DIR = Path(__file__).resolve().parents[3] / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

IDEA_CREATED_EXAMPLE = {
    "id": "idea-123",
    "title": "AI Review Assistant",
    "description": "Automates first-pass review comments for internal pull requests.",
    "category": "Product",
    "status": "submitted",
    "created_by": "jane.doe@epam.com",
    "created_at": "2026-05-13T10:00:00Z",
    "attachment_url": "/uploads/spec-note.txt",
}

IDEA_LIST_EXAMPLE = [
    IDEA_CREATED_EXAMPLE,
    {
        "id": "idea-456",
        "title": "Cost Dashboard",
        "description": "Tracks cloud usage trends and flags over-budget projects.",
        "category": "Cost-Savings",
        "status": "accepted",
        "created_by": "john.smith@epam.com",
        "created_at": "2026-05-12T15:30:00Z",
        "attachment_url": None,
    },
]

GENERIC_400_RESPONSE = {
    "description": "Failed Request Example",
    "content": {
        "application/json": {
            "example": {
                "detail": "Validation failed",
            }
        }
    },
}

UNAUTHORIZED_401_RESPONSE = {
    "description": "Failed Request Example",
    "content": {
        "application/json": {
            "example": {
                "detail": "Not authenticated",
            }
        }
    },
}

FORBIDDEN_403_RESPONSE = {
    "description": "Failed Request Example",
    "content": {
        "application/json": {
            "example": {
                "detail": "Unauthorized role",
            }
        }
    },
}

NOT_FOUND_404_RESPONSE = {
    "description": "Failed Request Example",
    "content": {
        "application/json": {
            "example": {
                "detail": "Idea not found",
            }
        }
    },
}


def get_idea_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> IdeaService:
    return IdeaService(idea_repository=IdeaRepository(db))


@router.post(
    "/submit",
    response_model=IdeaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new idea",
    responses={
        201: {
            "description": "Succeed Request Example",
            "content": {
                "application/json": {
                    "example": IDEA_CREATED_EXAMPLE,
                }
            },
        },
        400: {
            "description": "Failed Request Example",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Unsupported attachment type",
                    }
                }
            },
        },
        401: UNAUTHORIZED_401_RESPONSE,
    },
)
async def submit_idea(
    title: str = Form(...),
    description: str = Form(...),
    category: IdeaCategory = Form(...),
    file: UploadFile | None = File(None),
    current_user: CurrentUser = Depends(get_current_user),
    idea_service: IdeaService = Depends(get_idea_service),
) -> IdeaRead:
    attachment_url: str | None = None
    if file is not None:
        if file.content_type not in ALLOWED_ATTACHMENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported attachment type",
            )
        content = await file.read()
        if len(content) > MAX_ATTACHMENT_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attachment exceeds maximum size of 5MB",
            )
        extension = Path(file.filename or "attachment").suffix
        unique_name = f"{uuid4()}{extension}"
        target_path = UPLOADS_DIR / unique_name
        target_path.write_bytes(content)
        attachment_url = f"/uploads/{unique_name}"

    payload = IdeaCreate(
        title=title,
        description=description,
        category=category,
        attachment_url=attachment_url,
    )
    return await idea_service.create_idea(payload=payload, current_user=current_user)


@router.get(
    "",
    response_model=list[IdeaRead],
    status_code=status.HTTP_200_OK,
    summary="List ideas for current user",
    responses={
        200: {
            "description": "Succeed Request Example",
            "content": {
                "application/json": {
                    "example": IDEA_LIST_EXAMPLE,
                }
            },
        },
        400: GENERIC_400_RESPONSE,
        401: UNAUTHORIZED_401_RESPONSE,
    },
)
async def list_ideas(
    current_user: CurrentUser = Depends(get_current_user),
    idea_service: IdeaService = Depends(get_idea_service),
    status: Annotated[
        IdeaStatus | None,
        Query(
            alias="status",
            description="Filter ideas by status",
        ),
    ] = None,
) -> list[IdeaRead]:
    return await idea_service.get_user_ideas(
        email=current_user.email,
        role=current_user.role,
        status=status,
    )


@router.get(
    "/{id}",
    response_model=IdeaRead,
    status_code=status.HTTP_200_OK,
    summary="Get an idea by ID",
    responses={
        200: {
            "description": "Succeed Request Example",
            "content": {
                "application/json": {
                    "example": IDEA_CREATED_EXAMPLE,
                }
            },
        },
        401: UNAUTHORIZED_401_RESPONSE,
        404: NOT_FOUND_404_RESPONSE,
    },
)
async def get_idea_by_id(
    id: str,
    idea_service: IdeaService = Depends(get_idea_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> IdeaRead:
    try:
        return await idea_service.get_idea_by_id(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Idea not found")


@router.patch(
    "/{id}/status",
    response_model=IdeaStatusUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an idea's status",
    responses={
        200: {
            "description": "Succeed Request Example",
            "content": {
                "application/json": {
                    "example": {
                        "status": "accepted",
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
        401: UNAUTHORIZED_401_RESPONSE,
        403: FORBIDDEN_403_RESPONSE,
        404: NOT_FOUND_404_RESPONSE,
    },
)
async def update_idea_status(
    id: str,
    payload: IdeaStatusUpdate,
    idea_service: IdeaService = Depends(get_idea_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> IdeaStatusUpdateResponse:
    if current_user.role not in [UserRole.ADMIN, UserRole.EVALUATOR]:
        raise HTTPException(status_code=403, detail="Unauthorized role")

    try:
        await idea_service.update_idea_status(id, payload.status.value, current_user.role)
        return IdeaStatusUpdateResponse(status=payload.status)
    except ValueError:
        raise HTTPException(status_code=404, detail="Idea not found")
