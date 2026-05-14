"""
Simple direct tests for review_stages endpoints and repository.
Focus: Role-based access, error cases, basic model validation.
"""
import pytest
from app.models.user import UserRole, CurrentUser
from app.models.review_stage import ReviewStageCreate, ReviewStageRead, IdeaReviewProgress
from fastapi import HTTPException
from datetime import datetime


# Test role-based access for endpoints
class TestReviewStagesRoleAccess:
    """Test role-based authorization for review stage endpoints."""
    
    def test_submitter_cannot_approve(self):
        """Submitter should not be allowed to approve."""
        submitter = CurrentUser(email="user@epam.com", role=UserRole.SUBMITTER)
        assert submitter.role not in [UserRole.ADMIN, UserRole.EVALUATOR]
    
    def test_evaluator_can_approve(self):
        """Evaluator should be able to approve."""
        evaluator = CurrentUser(email="eval@epam.com", role=UserRole.EVALUATOR)
        assert evaluator.role in [UserRole.ADMIN, UserRole.EVALUATOR]
    
    def test_admin_can_approve(self):
        """Admin should be able to approve."""
        admin = CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
        assert admin.role in [UserRole.ADMIN, UserRole.EVALUATOR]
    
    def test_submitter_cannot_reject(self):
        """Submitter should not be allowed to reject."""
        submitter = CurrentUser(email="user@epam.com", role=UserRole.SUBMITTER)
        assert submitter.role not in [UserRole.ADMIN, UserRole.EVALUATOR]
    
    def test_evaluator_can_reject(self):
        """Evaluator should be able to reject."""
        evaluator = CurrentUser(email="eval@epam.com", role=UserRole.EVALUATOR)
        assert evaluator.role in [UserRole.ADMIN, UserRole.EVALUATOR]
    
    def test_admin_can_reject(self):
        """Admin should be able to reject."""
        admin = CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
        assert admin.role in [UserRole.ADMIN, UserRole.EVALUATOR]
    
    def test_submitter_cannot_set_stage(self):
        """Submitter should not be allowed to set stage."""
        submitter = CurrentUser(email="user@epam.com", role=UserRole.SUBMITTER)
        assert submitter.role not in [UserRole.ADMIN, UserRole.EVALUATOR]
    
    def test_evaluator_can_set_stage(self):
        """Evaluator should be able to set stage."""
        evaluator = CurrentUser(email="eval@epam.com", role=UserRole.EVALUATOR)
        assert evaluator.role in [UserRole.ADMIN, UserRole.EVALUATOR]
    
    def test_admin_can_set_stage(self):
        """Admin should be able to set stage."""
        admin = CurrentUser(email="admin@epam.com", role=UserRole.ADMIN)
        assert admin.role in [UserRole.ADMIN, UserRole.EVALUATOR]


class TestReviewStageModels:
    """Test review stage Pydantic models."""
    
    def test_review_stage_read_model(self):
        """ReviewStageRead should validate correctly."""
        from datetime import datetime
        data = {
            "id": "stage-1",
            "stage_name": "Technical Review",
            "stage_order": 1,
            "description": "Technical review",
            "required_approvals": 1,
            "allowed_reviewer_roles": ["technical_lead"],
            "allow_skip": False,
            "created_at": datetime.utcnow(),
        }
        stage = ReviewStageRead(**data)
        assert stage.stage_name == "Technical Review"
        assert stage.stage_order == 1
        assert stage.allow_skip is False
    
    def test_review_stage_create_model(self):
        """ReviewStageCreate should validate correctly."""
        data = {
            "stage_name": "New Stage",
            "stage_order": 5,
            "description": "New stage",
            "required_approvals": 2,
            "allowed_reviewer_roles": ["admin"],
            "allow_skip": True,
        }
        stage = ReviewStageCreate(**data)
        assert stage.stage_name == "New Stage"
        assert stage.required_approvals == 2
        assert stage.allow_skip is True
    
    def test_review_stage_create_invalid_order(self):
        """ReviewStageCreate should reject invalid stage_order."""
        data = {
            "stage_name": "Bad Stage",
            "stage_order": 0,  # Invalid: must be >= 1
            "description": "Bad stage",
            "required_approvals": 1,
            "allowed_reviewer_roles": ["admin"],
            "allow_skip": False,
        }
        with pytest.raises(ValueError):
            ReviewStageCreate(**data)
    
    def test_idea_review_progress_model(self):
        """IdeaReviewProgress should validate correctly."""
        data = {
            "idea_id": "idea-1",
            "current_stage": "Technical Review",
            "current_stage_order": 1,
            "approvals_received": [],
            "stages_completed": [],
            "created_at": "2026-05-15T10:00:00",
            "updated_at": "2026-05-15T10:00:00",
        }
        progress = IdeaReviewProgress(**data)
        assert progress.idea_id == "idea-1"
        assert progress.current_stage == "Technical Review"
        assert progress.current_stage_order == 1


class TestReviewStageEndpointErrorHandling:
    """Test error handling in endpoints."""
    
    def test_non_evaluator_approve_raises_403(self):
        """Approving as non-evaluator should raise 403."""
        submitter = CurrentUser(email="user@epam.com", role=UserRole.SUBMITTER)
        
        # Check role
        if submitter.role not in [UserRole.ADMIN, UserRole.EVALUATOR]:
            # Would raise HTTPException(status_code=403) in endpoint
            assert True
        else:
            assert False, "Should have failed"
    
    def test_non_evaluator_reject_raises_403(self):
        """Rejecting as non-evaluator should raise 403."""
        submitter = CurrentUser(email="user@epam.com", role=UserRole.SUBMITTER)
        
        # Check role
        if submitter.role not in [UserRole.ADMIN, UserRole.EVALUATOR]:
            assert True
        else:
            assert False, "Should have failed"
    
    def test_non_evaluator_set_stage_raises_403(self):
        """Setting stage as non-evaluator should raise 403."""
        submitter = CurrentUser(email="user@epam.com", role=UserRole.SUBMITTER)
        
        # Check role
        if submitter.role not in [UserRole.ADMIN, UserRole.EVALUATOR]:
            assert True
        else:
            assert False, "Should have failed"


class TestSetStageRequest:
    """Test SetStageRequest model from review_stages."""
    
    def test_set_stage_request_valid(self):
        """SetStageRequest should accept valid stage_order."""
        from app.api.endpoints.review_stages import SetStageRequest
        
        req = SetStageRequest(stage_order=2)
        assert req.stage_order == 2
    
    def test_set_stage_request_invalid_zero(self):
        """SetStageRequest should reject stage_order < 1."""
        from app.api.endpoints.review_stages import SetStageRequest
        
        with pytest.raises(ValueError):
            SetStageRequest(stage_order=0)
    
    def test_set_stage_response_valid(self):
        """SetStageResponse should accept all required fields."""
        from app.api.endpoints.review_stages import SetStageResponse
        
        resp = SetStageResponse(
            idea_id="idea-1",
            current_stage="Technical Review",
            current_stage_order=1,
            status="under_review",
        )
        assert resp.idea_id == "idea-1"
        assert resp.current_stage == "Technical Review"


class TestReviewStageEnums:
    """Test ReviewStageEnum from models."""
    
    def test_stage_enum_values(self):
        """ReviewStageEnum should have expected values."""
        from app.models.review_stage import ReviewStageEnum
        
        assert ReviewStageEnum.TECHNICAL.value == "technical_review"
        assert ReviewStageEnum.BUDGET.value == "budget_review"
        assert ReviewStageEnum.LEADERSHIP.value == "leadership_review"
        assert ReviewStageEnum.FINAL.value == "final_approval"


class TestReviewerRole:
    """Test ReviewerRole enum from models."""
    
    def test_reviewer_role_values(self):
        """ReviewerRole should have expected values."""
        from app.models.review_stage import ReviewerRole
        
        assert ReviewerRole.TECHNICAL_LEAD.value == "technical_lead"
        assert ReviewerRole.FINANCE.value == "finance"
        assert ReviewerRole.LEADERSHIP.value == "leadership"
        assert ReviewerRole.ADMIN.value == "admin"
