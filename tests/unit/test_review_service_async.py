"""
Tests for review service layer - ReviewService async operations.
"""
import pytest
from datetime import datetime, timezone
from app.services.review_service import ReviewService
from app.models.user import UserRole


class MockAsyncReviewCollection:
    def __init__(self):
        self.storage = {}
    
    async def find_one(self, query):
        for item in self.storage.values():
            match = all(item.get(k) == v for k, v in query.items())
            if match:
                return item
        return None
    
    async def insert_one(self, data):
        idea_id = data.get("idea_id", "default")
        self.storage[idea_id] = data
    
    async def update_one(self, query, update):
        for idea_id, item in self.storage.items():
            match = all(item.get(k) == v for k, v in query.items())
            if match:
                if "$set" in update:
                    item.update(update["$set"])
                return type('obj', (object,), {'modified_count': 1})()
        return type('obj', (object,), {'modified_count': 0})()


class MockReviewDatabase:
    def __init__(self):
        self.reviews_collection = MockAsyncReviewCollection()
    
    def __getitem__(self, name):
        if name == "idea_reviews":
            return self.reviews_collection
        raise KeyError(name)


class MockReviewStageRepository:
    async def get_all_stages(self):
        return [
            {
                "stage_name": "Technical Review",
                "stage_order": 1,
                "required_approvals": 1,
                "allowed_reviewer_roles": [UserRole.ADMIN.value],
            },
            {
                "stage_name": "Budget Review",
                "stage_order": 2,
                "required_approvals": 1,
                "allowed_reviewer_roles": [UserRole.ADMIN.value],
            },
        ]


class MockIdeaRepository:
    def __init__(self):
        self.db = MockReviewDatabase()


@pytest.mark.asyncio
async def test_review_service_get_idea_review_progress_creates_if_missing():
    """Test get_idea_review_progress initializes new review progress."""
    review_repo = MockReviewStageRepository()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    progress = await service.get_idea_review_progress("idea-1")
    
    assert progress is not None
    assert progress.idea_id == "idea-1"
    assert progress.current_stage is None
    assert progress.current_stage_order == 0
    assert progress.approvals_received == []


@pytest.mark.asyncio
async def test_review_service_get_idea_review_progress_returns_existing():
    """Test get_idea_review_progress returns existing progress."""
    review_repo = MockReviewStageRepository()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    # Insert existing progress
    await idea_repo.db["idea_reviews"].insert_one({
        "idea_id": "idea-1",
        "current_stage": "Technical Review",
        "current_stage_order": 1,
        "approvals_received": [],
        "stages_completed": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    
    progress = await service.get_idea_review_progress("idea-1")
    
    assert progress.current_stage == "Technical Review"
    assert progress.current_stage_order == 1


@pytest.mark.asyncio
async def test_review_service_advance_to_next_stage_first_time():
    """Test advance_to_next_stage moves from initial to first stage."""
    review_repo = MockReviewStageRepository()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    progress = await service.advance_to_next_stage(
        "idea-1",
        "admin@epam.com",
        UserRole.ADMIN,
        approval_comment="Looks good",
    )
    
    assert progress.current_stage == "Technical Review"
    assert progress.current_stage_order == 1
    assert len(progress.approvals_received) == 1
    assert progress.approvals_received[0].reviewer_email == "admin@epam.com"


@pytest.mark.asyncio
async def test_review_service_advance_to_next_stage_sequential():
    """Test advance_to_next_stage progresses through stages."""
    review_repo = MockReviewStageRepository()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    # Move to first stage
    progress1 = await service.advance_to_next_stage(
        "idea-1",
        "admin@epam.com",
        UserRole.ADMIN,
    )
    assert progress1.current_stage_order == 1
    
    # Move to second stage
    progress2 = await service.advance_to_next_stage(
        "idea-1",
        "admin@epam.com",
        UserRole.ADMIN,
    )
    assert progress2.current_stage_order == 2
    assert progress2.current_stage == "Budget Review"


@pytest.mark.asyncio
async def test_review_service_advance_to_next_stage_no_stages_configured():
    """Test advance_to_next_stage raises error when no stages exist."""
    class EmptyReviewStageRepository:
        async def get_all_stages(self):
            return []
    
    review_repo = EmptyReviewStageRepository()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    with pytest.raises(ValueError, match="No review stages configured"):
        await service.advance_to_next_stage(
            "idea-1",
            "admin@epam.com",
            UserRole.ADMIN,
        )


@pytest.mark.asyncio
async def test_review_service_advance_rejects_unauthorized_role():
    """Test advance_to_next_stage rejects unauthorized roles."""
    review_repo = MockReviewStageRepository()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    # Create a stage that only allows EVALUATOR role
    class RestrictedReviewRepo:
        async def get_all_stages(self):
            return [
                {
                    "stage_name": "Restricted",
                    "stage_order": 1,
                    "required_approvals": 1,
                    "allowed_reviewer_roles": [UserRole.EVALUATOR.value],
                }
            ]
    
    review_repo = RestrictedReviewRepo()
    service = ReviewService(review_repo, idea_repo)
    
    with pytest.raises(PermissionError):
        await service.advance_to_next_stage(
            "idea-1",
            "submitter@epam.com",
            UserRole.SUBMITTER,
        )


@pytest.mark.asyncio
async def test_review_service_admin_always_authorized():
    """Test ADMIN role bypasses reviewer role restrictions."""
    class RestrictedReviewRepo:
        async def get_all_stages(self):
            return [
                {
                    "stage_name": "Evaluator Only",
                    "stage_order": 1,
                    "required_approvals": 1,
                    "allowed_reviewer_roles": [UserRole.EVALUATOR.value],
                }
            ]
    
    review_repo = RestrictedReviewRepo()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    # Admin should bypass the evaluator-only restriction
    progress = await service.advance_to_next_stage(
        "idea-1",
        "admin@epam.com",
        UserRole.ADMIN,
    )
    
    assert progress.current_stage == "Evaluator Only"


@pytest.mark.asyncio
async def test_review_service_approval_records_comment():
    """Test approval records the reviewer comment."""
    review_repo = MockReviewStageRepository()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    comment = "Excellent proposal, approved for next phase"
    progress = await service.advance_to_next_stage(
        "idea-1",
        "admin@epam.com",
        UserRole.ADMIN,
        approval_comment=comment,
    )
    
    assert len(progress.approvals_received) == 1
    assert progress.approvals_received[0].comment == comment


@pytest.mark.asyncio
async def test_review_service_approval_without_comment():
    """Test approval works without comment."""
    review_repo = MockReviewStageRepository()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    progress = await service.advance_to_next_stage(
        "idea-1",
        "admin@epam.com",
        UserRole.ADMIN,
        approval_comment=None,
    )
    
    assert len(progress.approvals_received) == 1
    assert progress.approvals_received[0].comment is None


@pytest.mark.asyncio
async def test_review_service_advance_beyond_max_stage():
    """Test advance_to_next_stage raises error when all stages complete."""
    review_repo = MockReviewStageRepository()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    # Move through all stages
    await service.advance_to_next_stage("idea-1", "admin@epam.com", UserRole.ADMIN)
    await service.advance_to_next_stage("idea-1", "admin@epam.com", UserRole.ADMIN)
    
    # Try to advance beyond max - should raise error
    with pytest.raises(ValueError, match="No more stages"):
        await service.advance_to_next_stage("idea-1", "admin@epam.com", UserRole.ADMIN)


@pytest.mark.asyncio
async def test_review_service_evaluator_authorized_role():
    """Test EVALUATOR can approve if authorized in stage config."""
    class EvaluatorAuthReviewRepo:
        async def get_all_stages(self):
            return [
                {
                    "stage_name": "Evaluator Stage",
                    "stage_order": 1,
                    "required_approvals": 1,
                    "allowed_reviewer_roles": [UserRole.EVALUATOR.value],
                }
            ]
    
    review_repo = EvaluatorAuthReviewRepo()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    progress = await service.advance_to_next_stage(
        "idea-1",
        "evaluator@epam.com",
        UserRole.EVALUATOR,
    )
    
    assert progress.current_stage == "Evaluator Stage"


@pytest.mark.asyncio
async def test_review_service_multiple_approvals_recorded():
    """Test multiple approvals are recorded sequentially."""
    review_repo = MockReviewStageRepository()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    # First approval
    progress = await service.advance_to_next_stage(
        "idea-1",
        "reviewer1@epam.com",
        UserRole.ADMIN,
        approval_comment="First review",
    )
    assert len(progress.approvals_received) == 1
    
    # Get current progress
    current = await service.get_idea_review_progress("idea-1")
    assert current.current_stage_order == 1


@pytest.mark.asyncio
async def test_review_service_stages_completed_tracking():
    """Test stages_completed list is updated when all stages are done."""
    # Create a repo with only 1 stage
    class SingleStageRepo:
        async def get_all_stages(self):
            return [
                {
                    "stage_name": "Only Stage",
                    "stage_order": 1,
                    "required_approvals": 1,
                    "allowed_reviewer_roles": [UserRole.ADMIN.value],
                }
            ]
    
    review_repo = SingleStageRepo()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    progress = await service.advance_to_next_stage(
        "idea-1",
        "admin@epam.com",
        UserRole.ADMIN,
    )
    
    # Since max stage is 1 and current is 1, the stage should be marked complete
    assert "Only Stage" in progress.stages_completed


@pytest.mark.asyncio
async def test_review_service_approval_status_is_approved():
    """Test approval status is set to 'approved'."""
    review_repo = MockReviewStageRepository()
    idea_repo = MockIdeaRepository()
    service = ReviewService(review_repo, idea_repo)
    
    progress = await service.advance_to_next_stage(
        "idea-1",
        "admin@epam.com",
        UserRole.ADMIN,
    )
    
    assert progress.approvals_received[0].status == "approved"

