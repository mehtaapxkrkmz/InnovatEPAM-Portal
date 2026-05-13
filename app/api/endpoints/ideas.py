from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_current_user
from app.db.client import get_database
from app.db.repositories.idea_repository import IdeaRepository
from app.models.idea import IdeaCreate, IdeaRead
from app.services.idea_service import IdeaService

router = APIRouter()


def get_idea_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> IdeaService:
    return IdeaService(idea_repository=IdeaRepository(db))


@router.post(
    "/submit",
    response_model=IdeaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new idea",
)
async def submit_idea(
    payload: IdeaCreate,
    current_user: dict = Depends(get_current_user),
    idea_service: IdeaService = Depends(get_idea_service),
) -> IdeaRead:
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
