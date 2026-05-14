"""
Review Service - handles the multi-stage review workflow logic.
"""

from datetime import datetime
from app.models.review_stage import ReviewApproval, IdeaReviewProgress
from app.models.user import UserRole
from app.db.repositories.review_stage_repository import ReviewStageRepository
from app.db.repositories.idea_repository import IdeaRepository


class ReviewService:
    """Service for managing multi-stage review workflows."""

    def __init__(self, review_repo: ReviewStageRepository, idea_repo: IdeaRepository):
        self.review_repo = review_repo
        self.idea_repo = idea_repo

    async def get_idea_review_progress(self, idea_id: str) -> IdeaReviewProgress | None:
        """Get the current review progress for an idea."""
        review_progress = await self.idea_repo.db["idea_reviews"].find_one(
            {"idea_id": idea_id}
        )
        
        if not review_progress:
            # Initialize review progress for new idea
            progress = {
                "idea_id": idea_id,
                "current_stage": None,
                "current_stage_order": 0,
                "approvals_received": [],
                "stages_completed": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            await self.idea_repo.db["idea_reviews"].insert_one(progress)
            return IdeaReviewProgress(**progress)
        
        return IdeaReviewProgress(**review_progress)

    async def advance_to_next_stage(
        self,
        idea_id: str,
        reviewer_email: str,
        reviewer_role: UserRole,
        approval_comment: str | None = None,
    ) -> IdeaReviewProgress | None:
        """Advance an idea to the next review stage after approval."""
        
        # Get current review progress
        progress = await self.get_idea_review_progress(idea_id)
        if not progress:
            raise ValueError("Idea not found")
        
        # Get all stages
        all_stages = await self.review_repo.get_all_stages()
        if not all_stages:
            raise ValueError("No review stages configured")
        
        # Determine next stage
        if progress.current_stage_order == 0:
            # First time through - go to first stage
            next_stage = all_stages[0]
        else:
            # Find next stage after current
            current = next(
                (s for s in all_stages if s["stage_order"] == progress.current_stage_order),
                None,
            )
            if not current:
                raise ValueError("Current stage not found")
            
            next_stage_idx = all_stages.index(current) + 1
            if next_stage_idx >= len(all_stages):
                raise ValueError("No more stages to advance to")
            
            next_stage = all_stages[next_stage_idx]
        
        # Validate reviewer role for this stage
        allowed_roles = next_stage.get("allowed_reviewer_roles", [])
        reviewer_role_str = reviewer_role.value if isinstance(reviewer_role, UserRole) else str(reviewer_role)
        
        if reviewer_role_str not in allowed_roles and reviewer_role != UserRole.ADMIN:
            raise PermissionError(
                f"Role {reviewer_role} not authorized to review stage {next_stage['stage_name']}"
            )
        
        # Record approval
        approval = ReviewApproval(
            reviewer_email=reviewer_email,
            stage_name=next_stage["stage_name"],
            comment=approval_comment,
            status="approved",
        )
        
        # Update review progress
        progress.approvals_received.append(approval)
        progress.current_stage = next_stage["stage_name"]
        progress.current_stage_order = next_stage["stage_order"]
        progress.updated_at = datetime.utcnow()
        
        # Check if all stages are complete
        max_stage_order = max((s["stage_order"] for s in all_stages), default=0)
        if progress.current_stage_order >= max_stage_order:
            progress.stages_completed.append(next_stage["stage_name"])
        
        # Persist updates
        await self.idea_repo.db["idea_reviews"].update_one(
            {"idea_id": idea_id},
            {
                "$set": {
                    "current_stage": progress.current_stage,
                    "current_stage_order": progress.current_stage_order,
                    "approvals_received": [a.model_dump() for a in progress.approvals_received],
                    "stages_completed": progress.stages_completed,
                    "updated_at": progress.updated_at,
                }
            },
        )
        
        return progress

    async def reject_at_stage(
        self,
        idea_id: str,
        reviewer_email: str,
        rejection_reason: str,
    ) -> None:
        """Reject an idea at the current review stage."""
        
        progress = await self.get_idea_review_progress(idea_id)
        if not progress or not progress.current_stage:
            raise ValueError("Idea is not under review")
        
        # Record rejection
        rejection = ReviewApproval(
            reviewer_email=reviewer_email,
            stage_name=progress.current_stage,
            comment=rejection_reason,
            status="rejected",
        )
        
        progress.approvals_received.append(rejection)
        progress.updated_at = datetime.utcnow()
        
        # Update idea status to rejected
        await self.idea_repo.db["ideas"].update_one(
            {"_id": idea_id},
            {"$set": {"status": "rejected"}},
        )
        
        # Update review progress
        await self.idea_repo.db["idea_reviews"].update_one(
            {"idea_id": idea_id},
            {
                "$set": {
                    "approvals_received": [a.model_dump() for a in progress.approvals_received],
                    "updated_at": progress.updated_at,
                }
            },
        )

    async def skip_stage(
        self,
        idea_id: str,
        current_stage_order: int,
    ) -> IdeaReviewProgress | None:
        """Skip a stage if it's allowed and advance to next."""
        
        all_stages = await self.review_repo.get_all_stages()
        current_stage = next(
            (s for s in all_stages if s["stage_order"] == current_stage_order),
            None,
        )
        
        if not current_stage or not current_stage.get("allow_skip"):
            raise ValueError(f"Stage cannot be skipped: {current_stage}")
        
        progress = await self.get_idea_review_progress(idea_id)
        if not progress:
            raise ValueError("Idea not found")
        
        # Mark as completed
        progress.stages_completed.append(current_stage["stage_name"])
        progress.updated_at = datetime.utcnow()
        
        # Update review progress
        await self.idea_repo.db["idea_reviews"].update_one(
            {"idea_id": idea_id},
            {
                "$set": {
                    "stages_completed": progress.stages_completed,
                    "updated_at": progress.updated_at,
                }
            },
        )
        
        return progress
