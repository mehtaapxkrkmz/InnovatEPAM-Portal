from pathlib import Path
from typing import Annotated, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.client import get_database
from app.db.repositories.idea_repository import IdeaRepository
from app.models.idea import (
    IdeaCategory,
    IdeaCreate,
    IdeaPriority,
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


def get_idea_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> IdeaService:
    return IdeaService(idea_repository=IdeaRepository(db))

@router.get(
    "",
    response_model=list[IdeaRead],
    status_code=status.HTTP_200_OK,
    summary="List ideas for dashboard",
)
async def list_ideas(
    idea_service: IdeaService = Depends(get_idea_service),
    status: Annotated[
        IdeaStatus | None,
        Query(alias="status", description="Filter ideas by status"),
    ] = None,
) -> list[IdeaRead]:
    # Public list endpoint for live demo use.
    return await idea_service.get_user_ideas(
        email=None,
        role=UserRole.ADMIN,
        status=status
    )

@router.post(
    "",
    response_model=IdeaRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_idea(
    title: str = Form(...),
    description: str = Form(...),
    category: IdeaCategory = Form(...),
    priority: IdeaPriority = Form(...),
    estimated_budget: float = Form(...),
    attachment: Optional[UploadFile] = File(None),
    idea_service: IdeaService = Depends(get_idea_service),
) -> IdeaRead:
    idea_create = IdeaCreate(
        title=title,
        description=description,
        category=category,
        priority=priority,
        estimated_budget=estimated_budget,
    )
    if attachment is not None:
        if attachment.content_type not in ALLOWED_ATTACHMENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported attachment type",
            )
        content = await attachment.read()
        if len(content) > MAX_ATTACHMENT_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attachment exceeds maximum size of 5MB",
            )
        extension = Path(attachment.filename or "attachment").suffix
        unique_name = f"{uuid4()}{extension}"
        target_path = UPLOADS_DIR / unique_name
        target_path.write_bytes(content)
        idea_create.attachment_url = f"/uploads/{unique_name}"

    demo_current_user = CurrentUser(email="demo_user@example.com", role=UserRole.SUBMITTER)
    return await idea_service.create_idea(payload=idea_create, current_user=demo_current_user)

@router.get("/{id}", response_model=IdeaRead)
async def get_idea_by_id(
    id: str,
    idea_service: IdeaService = Depends(get_idea_service),
) -> IdeaRead:
    try:
        return await idea_service.get_idea_by_id(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Idea not found")

@router.patch("/{id}/status", response_model=IdeaStatusUpdateResponse)
async def update_idea_status(
    id: str,
    payload: IdeaStatusUpdate,
    idea_service: IdeaService = Depends(get_idea_service),
) -> IdeaStatusUpdateResponse:
    try:
        await idea_service.update_idea_status(
            id,
            payload.status.value,
            UserRole.ADMIN,
            evaluator_comment=payload.evaluator_comment,
        )
        return IdeaStatusUpdateResponse(
            status=payload.status,
            evaluator_comment=payload.evaluator_comment,
        )
    except PermissionError:
        raise HTTPException(status_code=403, detail="Unauthorized role")
    except ValueError:
        raise HTTPException(status_code=404, detail="Idea not found")