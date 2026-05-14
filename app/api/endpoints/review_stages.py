"""
Review Stage API Endpoints - for managing multi-stage review workflows.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import get_current_user, require_admin
from app.models.user import CurrentUser, UserRole
from app.models.review_stage import (
    ReviewStageCreate,
    ReviewStageRead,
    IdeaReviewProgress,
)
from app.services.review_service import ReviewService
from app.db.repositories.review_stage_repository import ReviewStageRepository
from app.db.repositories.idea_repository import IdeaRepository
from app.db.client import mongo_manager

router = APIRouter(prefix="/review-stages", tags=["review-stages"])

# Global service instance (to be initialized)
review_service: ReviewService = None


async def get_review_service() -> ReviewService:
    """Dependency to get the review service."""
    from app.main import app
    global review_service
    if review_service is None:
        db = mongo_manager.database
        review_service = ReviewService(
            ReviewStageRepository(db),
            IdeaRepository(db),
        )
    return review_service


@router.get("", response_model=list[ReviewStageRead])
async def get_review_stages(
    current_user: CurrentUser = Depends(get_current_user),
) -> list[ReviewStageRead]:
    """
    Get all configured review stages.
    
    Anyone can view the stages, but only admins/evaluators can use them.
    """
    db = mongo_manager.database
    repo = ReviewStageRepository(db)
    stages = await repo.get_all_stages()
    return [ReviewStageRead(**stage) for stage in stages]


@router.post("", response_model=ReviewStageRead, status_code=status.HTTP_201_CREATED)
async def create_review_stage(
    stage: ReviewStageCreate,
    current_user: CurrentUser = Depends(require_admin),
) -> ReviewStageRead:
    """
    Create a new review stage.
    
    Only admins can create/modify review stages.
    """
    db = mongo_manager.database
    repo = ReviewStageRepository(db)
    
    created_stage = await repo.create_stage(stage)
    return ReviewStageRead(**created_stage)


@router.get("/progress/{idea_id}", response_model=IdeaReviewProgress)
async def get_idea_review_progress(
    idea_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> IdeaReviewProgress:
    """
    Get the review progress for a specific idea.
    
    Shows current stage, completed stages, and all approvals.
    """
    db = mongo_manager.database
    service = ReviewService(ReviewStageRepository(db), IdeaRepository(db))
    
    progress = await service.get_idea_review_progress(idea_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return progress


@router.post("/approve/{idea_id}")
async def approve_and_advance_stage(
    idea_id: str,
    comment: str | None = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Approve current stage and advance to next stage.
    
    Only evaluators/admins can approve.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.EVALUATOR]:
        raise HTTPException(status_code=403, detail="Not authorized to approve ideas")
    
    db = mongo_manager.database
    service = ReviewService(ReviewStageRepository(db), IdeaRepository(db))
    
    try:
        progress = await service.advance_to_next_stage(
            idea_id,
            current_user.email,
            current_user.role,
            comment,
        )
        return {
            "status": "success",
            "message": f"Advanced to stage: {progress.current_stage}",
            "progress": progress.model_dump(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/reject/{idea_id}")
async def reject_at_stage(
    idea_id: str,
    reason: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Reject an idea at the current review stage.
    
    Only evaluators/admins can reject.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.EVALUATOR]:
        raise HTTPException(status_code=403, detail="Not authorized to reject ideas")
    
    db = mongo_manager.database
    service = ReviewService(ReviewStageRepository(db), IdeaRepository(db))
    
    try:
        await service.reject_at_stage(idea_id, current_user.email, reason)
        return {
            "status": "success",
            "message": f"Idea rejected at current stage",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
