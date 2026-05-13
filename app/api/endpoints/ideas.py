from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_current_user
from app.db.client import get_database
from app.db.repositories.idea_repository import IdeaRepository
from app.models.idea import IdeaCategory, IdeaCreate, IdeaRead
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


@router.post(
    "/submit",
    response_model=IdeaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new idea",
)
async def submit_idea(
    title: str = Form(...),
    description: str = Form(...),
    category: IdeaCategory = Form(...),
    file: UploadFile | None = File(None),
    current_user: dict = Depends(get_current_user),
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
)
async def list_ideas(
    current_user: dict = Depends(get_current_user),
    idea_service: IdeaService = Depends(get_idea_service),
) -> list[IdeaRead]:
    return await idea_service.get_user_ideas(email=current_user["email"])
