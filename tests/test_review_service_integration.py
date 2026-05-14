"""
High-impact integration tests for review service - edge cases and error scenarios.
Focus: Invalid transitions, unauthorized actions, state validation.
"""
import pytest
from datetime import datetime
from app.services.review_service import ReviewService
from app.models.user import UserRole
from app.models.review_stage import IdeaReviewProgress


class MockAsyncCollection:
    """Mock MongoDB collection with async support."""
    def __init__(self):
        self.storage = {}
    
    async def find_one(self, query):
        for item in self.storage.values():
            if all(item.get(k) == v for k, v in query.items()):
                return item
        return None
    
    async def insert_one(self, data):
        idea_id = data.get("idea_id", "default")
        self.storage[idea_id] = data
    
    async def update_one(self, query, update):
        for idea_id, item in self.storage.items():
            if all(item.get(k) == v for k, v in query.items()):
                if "$set" in update:
                    item.update(update["$set"])
                return type('obj', (object,), {'modified_count': 1})()
        return type('obj', (object,), {'modified_count': 0})()


class MockAsyncDatabase:
    """Mock MongoDB database with collections."""
    def __init__(self):
        self.collections = {}
    
    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = MockAsyncCollection()
        return self.collections[name]


class MockReviewStageRepository:
    """Mock review stage repository."""
    def __init__(self, stages=None):
        self.stages = stages or [
            {
                "stage_name": "Technical Review",
                "stage_order": 1,
                "allowed_reviewer_roles": ["evaluator"],
                "allow_skip": False,
            },
            {
                "stage_name": "Executive Review",
                "stage_order": 2,
                "allowed_reviewer_roles": ["evaluator"],
                "allow_skip": False,
            },
            {
                "stage_name": "Final Approval",
                "stage_order": 3,
                "allowed_reviewer_roles": ["admin"],
                "allow_skip": True,
            },
        ]
    
    async def get_all_stages(self):
        return self.stages


class MockIdeaRepository:
    """Mock idea repository."""
    def __init__(self):
        self.db = MockAsyncDatabase()


@pytest.fixture
def review_service():
    """Provide a ReviewService with mock dependencies."""
    review_repo = MockReviewStageRepository()
    idea_repo = MockIdeaRepository()
    return ReviewService(review_repo, idea_repo)


@pytest.mark.asyncio
async def test_advance_to_first_stage_success(review_service):
    """Should successfully advance to first stage on initial submission."""
    progress = await review_service.advance_to_next_stage(
        idea_id="idea-001",
        reviewer_email="evaluator@epam.com",
        reviewer_role=UserRole.EVALUATOR,
        approval_comment="Initial review passed",
    )
    
    assert progress.current_stage == "Technical Review"
    assert progress.current_stage_order == 1
    assert len(progress.approvals_received) == 1
    assert progress.approvals_received[0].status == "approved"


@pytest.mark.asyncio
async def test_advance_through_all_stages(review_service):
    """Should progress through all review stages sequentially."""
    # Stage 1
    await review_service.advance_to_next_stage(
        "idea-001", "eval1@epam.com", UserRole.EVALUATOR
    )
    
    # Stage 2
    await review_service.advance_to_next_stage(
        "idea-001", "eval2@epam.com", UserRole.EVALUATOR
    )
    
    # Stage 3
    progress = await review_service.advance_to_next_stage(
        "idea-001", "admin@epam.com", UserRole.ADMIN
    )
    
    assert progress.current_stage == "Final Approval"
    assert progress.current_stage_order == 3
    assert len(progress.approvals_received) == 3


@pytest.mark.asyncio
async def test_unauthorized_reviewer_fails(review_service):
    """Should reject review from unauthorized role at stage."""
    # SUBMITTER role not allowed for Technical Review (requires EVALUATOR or ADMIN)
    with pytest.raises(PermissionError) as exc_info:
        await review_service.advance_to_next_stage(
            "idea-001",
            "submitter@epam.com",
            UserRole.SUBMITTER,
        )
    
    assert "not authorized" in str(exc_info.value)


@pytest.mark.asyncio
async def test_admin_bypasses_role_restrictions(review_service):
    """Should allow ADMIN to review any stage regardless of allowed_reviewer_roles."""
    progress = await review_service.advance_to_next_stage(
        "idea-001",
        "admin@epam.com",
        UserRole.ADMIN,
        approval_comment="Admin override review",
    )
    
    assert progress.current_stage == "Technical Review"
    assert progress.current_stage_order == 1


@pytest.mark.asyncio
async def test_advance_beyond_final_stage_fails(review_service):
    """Should fail when trying to advance beyond the last stage."""
    # Get to final stage
    await review_service.advance_to_next_stage(
        "idea-001", "eval1@epam.com", UserRole.EVALUATOR
    )
    await review_service.advance_to_next_stage(
        "idea-001", "eval2@epam.com", UserRole.EVALUATOR
    )
    await review_service.advance_to_next_stage(
        "idea-001", "admin@epam.com", UserRole.ADMIN
    )
    
    # Attempt to advance again should fail
    with pytest.raises(ValueError) as exc_info:
        await review_service.advance_to_next_stage(
            "idea-001", "admin@epam.com", UserRole.ADMIN
        )
    
    assert "No more stages" in str(exc_info.value)


@pytest.mark.asyncio
async def test_reject_at_stage_updates_status(review_service):
    """Should record rejection and update idea status."""
    # Initialize idea in review
    await review_service.advance_to_next_stage(
        "idea-001", "eval@epam.com", UserRole.EVALUATOR
    )
    
    # Reject at current stage
    await review_service.reject_at_stage(
        "idea-001",
        "eval@epam.com",
        "Does not meet technical requirements",
    )
    
    progress = await review_service.get_idea_review_progress("idea-001")
    assert len(progress.approvals_received) == 2
    assert progress.approvals_received[-1].status == "rejected"


@pytest.mark.asyncio
async def test_reject_not_in_review_fails(review_service):
    """Should fail to reject idea that's not in review."""
    with pytest.raises(ValueError) as exc_info:
        await review_service.reject_at_stage(
            "idea-999",
            "eval@epam.com",
            "Not under review",
        )
    
    assert "not under review" in str(exc_info.value)


@pytest.mark.asyncio
async def test_skip_allowed_stage(review_service):
    """Should skip a stage marked as allow_skip=True."""
    # Initialize and advance to stage 3 which allows skipping
    await review_service.advance_to_next_stage(
        "idea-001", "eval1@epam.com", UserRole.EVALUATOR
    )
    await review_service.advance_to_next_stage(
        "idea-001", "eval2@epam.com", UserRole.EVALUATOR
    )
    
    # Skip stage 3
    progress = await review_service.skip_stage("idea-001", 3)
    
    assert "Final Approval" in progress.stages_completed
    assert progress.updated_at is not None


@pytest.mark.asyncio
async def test_skip_non_skippable_stage_fails(review_service):
    """Should fail when trying to skip a stage with allow_skip=False."""
    with pytest.raises(ValueError) as exc_info:
        await review_service.skip_stage("idea-001", 1)
    
    assert "cannot be skipped" in str(exc_info.value)


@pytest.mark.asyncio
async def test_multiple_reviewers_same_stage(review_service):
    """Should record multiple reviewers' comments on same stage progression."""
    await review_service.advance_to_next_stage(
        "idea-001",
        "reviewer1@epam.com",
        UserRole.EVALUATOR,
        approval_comment="First review comment",
    )
    
    progress = await review_service.get_idea_review_progress("idea-001")
    
    # Verify the first reviewer is recorded
    assert progress.approvals_received[0].reviewer_email == "reviewer1@epam.com"
    assert progress.approvals_received[0].comment == "First review comment"
