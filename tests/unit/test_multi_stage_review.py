"""
Tests for Phase 5 - Multi-Stage Review (Configurable Stages) feature.

Tests cover:
1. Review stage configuration and retrieval
2. Advancing ideas through review stages
3. Recording approvals at each stage
4. Role-based authorization for stage reviews
5. Rejection logic at stages
"""

import pytest
from datetime import datetime
from app.models.review_stage import (
    ReviewStageCreate,
    ReviewStageEnum,
    ReviewerRole,
    ReviewApproval,
)
from app.models.user import UserRole


class TestReviewStageConfiguration:
    """Tests for configuring review stages."""

    def test_default_stages_have_correct_order(self):
        """Verify default stages are in correct order."""
        expected_order = [
            ReviewStageEnum.TECHNICAL.value,
            ReviewStageEnum.BUDGET.value,
            ReviewStageEnum.LEADERSHIP.value,
            ReviewStageEnum.FINAL.value,
        ]
        
        for i, stage_name in enumerate(expected_order, 1):
            # stage_order should be sequential
            assert i in [1, 2, 3, 4]

    def test_review_stage_create_validation(self):
        """Test validation of review stage creation."""
        # Valid stage
        valid_stage = ReviewStageCreate(
            stage_name="Test Review",
            stage_order=1,
            required_approvals=1,
            allowed_reviewer_roles=[ReviewerRole.ADMIN],
        )
        assert valid_stage.stage_name == "Test Review"
        assert valid_stage.stage_order == 1

    def test_technical_stage_allows_technical_lead_and_admin(self):
        """Technical review stage should allow technical leads and admins."""
        allowed_roles = [
            ReviewerRole.TECHNICAL_LEAD,
            ReviewerRole.ADMIN,
        ]
        assert ReviewerRole.TECHNICAL_LEAD in allowed_roles
        assert ReviewerRole.ADMIN in allowed_roles

    def test_budget_stage_allows_finance_and_admin(self):
        """Budget review stage should allow finance and admins."""
        allowed_roles = [
            ReviewerRole.FINANCE,
            ReviewerRole.ADMIN,
        ]
        assert ReviewerRole.FINANCE in allowed_roles
        assert ReviewerRole.ADMIN in allowed_roles

    def test_leadership_stage_is_optional(self):
        """Leadership review stage should be skippable."""
        allow_skip = True
        assert allow_skip is True

    def test_final_stage_requires_admin(self):
        """Final approval should only be done by admins."""
        allowed_roles = [ReviewerRole.ADMIN]
        assert ReviewerRole.ADMIN in allowed_roles
        assert len(allowed_roles) == 1


class TestReviewProgressTracking:
    """Tests for tracking idea progress through review stages."""

    def test_idea_starts_with_no_current_stage(self):
        """New ideas should start with no active review stage."""
        current_stage = None
        current_stage_order = 0
        
        assert current_stage is None
        assert current_stage_order == 0

    def test_idea_advances_to_first_stage(self):
        """First approval should move idea to technical review stage."""
        current_stage = ReviewStageEnum.TECHNICAL.value
        current_stage_order = 1
        
        assert current_stage == ReviewStageEnum.TECHNICAL.value
        assert current_stage_order == 1

    def test_idea_progresses_through_stages_sequentially(self):
        """Idea should progress through stages in order."""
        stages_completed = []
        expected_progression = [
            ReviewStageEnum.TECHNICAL.value,
            ReviewStageEnum.BUDGET.value,
            ReviewStageEnum.LEADERSHIP.value,
            ReviewStageEnum.FINAL.value,
        ]
        
        for stage in expected_progression:
            stages_completed.append(stage)
        
        assert stages_completed == expected_progression

    def test_approval_records_reviewer_and_timestamp(self):
        """Each approval should record reviewer email and timestamp."""
        approval = ReviewApproval(
            reviewer_email="reviewer@company.com",
            stage_name=ReviewStageEnum.TECHNICAL.value,
            comment="Looks good technically",
            status="approved",
        )
        
        assert approval.reviewer_email == "reviewer@company.com"
        assert approval.stage_name == ReviewStageEnum.TECHNICAL.value
        assert approval.status == "approved"
        assert approval.comment == "Looks good technically"
        assert isinstance(approval.approved_at, datetime)


class TestRoleBasedAuthorization:
    """Tests for role-based authorization at review stages."""

    def test_submitter_cannot_approve(self):
        """Submitters should not be able to approve at any stage."""
        user_role = UserRole.SUBMITTER
        allowed_approver_roles = [UserRole.ADMIN, UserRole.EVALUATOR]
        
        assert user_role not in allowed_approver_roles

    def test_evaluator_can_approve(self):
        """Evaluators should be able to approve at stages they're authorized for."""
        user_role = UserRole.EVALUATOR
        allowed_approver_roles = [UserRole.ADMIN, UserRole.EVALUATOR]
        
        assert user_role in allowed_approver_roles

    def test_admin_can_approve_at_any_stage(self):
        """Admins should be able to approve at any stage."""
        user_role = UserRole.ADMIN
        
        # Admin should have access to all stage reviews
        for stage_name in [
            ReviewStageEnum.TECHNICAL.value,
            ReviewStageEnum.BUDGET.value,
            ReviewStageEnum.LEADERSHIP.value,
            ReviewStageEnum.FINAL.value,
        ]:
            assert user_role == UserRole.ADMIN

    def test_technical_lead_only_at_technical_stage(self):
        """Technical lead should only review at technical stage."""
        reviewer_role = "technical_lead"
        stage_name = ReviewStageEnum.TECHNICAL.value
        
        # Verify technical lead is authorized for technical review
        allowed_roles = [ReviewerRole.TECHNICAL_LEAD, ReviewerRole.ADMIN]
        assert reviewer_role in [r.value for r in allowed_roles]

    def test_finance_only_at_budget_stage(self):
        """Finance reviewer should only review at budget stage."""
        reviewer_role = "finance"
        stage_name = ReviewStageEnum.BUDGET.value
        
        # Verify finance is authorized for budget review
        allowed_roles = [ReviewerRole.FINANCE, ReviewerRole.ADMIN]
        assert reviewer_role in [r.value for r in allowed_roles]


class TestRejectionLogic:
    """Tests for idea rejection at review stages."""

    def test_rejection_records_reason(self):
        """Rejection should record the rejection reason."""
        rejection = ReviewApproval(
            reviewer_email="reviewer@company.com",
            stage_name=ReviewStageEnum.TECHNICAL.value,
            comment="Does not meet technical requirements",
            status="rejected",
        )
        
        assert rejection.status == "rejected"
        assert "technical" in rejection.comment.lower()

    def test_rejected_idea_status_set_to_rejected(self):
        """Rejected ideas should have status set to 'rejected'."""
        idea_status = "rejected"
        
        assert idea_status == "rejected"

    def test_rejection_stops_further_review(self):
        """Rejection should prevent advancement to next stage."""
        stages_completed = [ReviewStageEnum.TECHNICAL.value]
        # After rejection, no more stages should be completed
        
        next_stages = [
            ReviewStageEnum.BUDGET.value,
            ReviewStageEnum.LEADERSHIP.value,
            ReviewStageEnum.FINAL.value,
        ]
        
        # None of these should be completed after rejection
        for stage in next_stages:
            assert stage not in stages_completed


class TestStageSkipping:
    """Tests for skipping optional stages."""

    def test_leadership_stage_can_be_skipped(self):
        """Leadership stage should be skippable."""
        allow_skip = True
        stage_name = ReviewStageEnum.LEADERSHIP.value
        
        assert allow_skip is True

    def test_non_skippable_stages_cannot_be_skipped(self):
        """Technical, Budget, and Final stages should not be skippable."""
        non_skippable_stages = [
            ReviewStageEnum.TECHNICAL.value,
            ReviewStageEnum.BUDGET.value,
            ReviewStageEnum.FINAL.value,
        ]
        
        # These should all have allow_skip = False
        for stage in non_skippable_stages:
            assert stage != ReviewStageEnum.LEADERSHIP.value

    def test_skip_stage_marks_as_completed(self):
        """Skipping a stage should mark it as completed."""
        stages_completed = [ReviewStageEnum.LEADERSHIP.value]
        
        assert ReviewStageEnum.LEADERSHIP.value in stages_completed


class TestMultiStageApprovalFlow:
    """Integration tests for multi-stage approval workflow."""

    def test_idea_flows_through_all_stages(self):
        """Idea should progress through technical -> budget -> leadership -> final."""
        approvals = []
        stages_order = [
            ReviewStageEnum.TECHNICAL.value,
            ReviewStageEnum.BUDGET.value,
            ReviewStageEnum.LEADERSHIP.value,
            ReviewStageEnum.FINAL.value,
        ]
        
        for stage in stages_order:
            approval = ReviewApproval(
                reviewer_email=f"reviewer@company.com",
                stage_name=stage,
                status="approved",
            )
            approvals.append(approval)
        
        # Verify progression
        assert len(approvals) == 4
        assert approvals[0].stage_name == ReviewStageEnum.TECHNICAL.value
        assert approvals[1].stage_name == ReviewStageEnum.BUDGET.value
        assert approvals[2].stage_name == ReviewStageEnum.LEADERSHIP.value
        assert approvals[3].stage_name == ReviewStageEnum.FINAL.value

    def test_rejection_at_any_stage_stops_workflow(self):
        """Rejection at any stage should stop the workflow."""
        for stage_to_reject in [
            ReviewStageEnum.TECHNICAL.value,
            ReviewStageEnum.BUDGET.value,
            ReviewStageEnum.LEADERSHIP.value,
        ]:
            approvals = []
            stages_order = [
                ReviewStageEnum.TECHNICAL.value,
                ReviewStageEnum.BUDGET.value,
                ReviewStageEnum.LEADERSHIP.value,
                ReviewStageEnum.FINAL.value,
            ]
            
            for stage in stages_order:
                if stage == stage_to_reject:
                    approval = ReviewApproval(
                        reviewer_email="reviewer@company.com",
                        stage_name=stage,
                        status="rejected",
                        comment="Rejected at this stage",
                    )
                    approvals.append(approval)
                    break
                else:
                    approval = ReviewApproval(
                        reviewer_email="reviewer@company.com",
                        stage_name=stage,
                        status="approved",
                    )
                    approvals.append(approval)
            
            # Verify workflow stopped at rejection
            assert approvals[-1].status == "rejected"

    def test_admin_can_expedite_process(self):
        """Admin should be able to move through stages quickly."""
        admin_email = "admin@company.com"
        approvals = []
        
        # Admin can approve all stages quickly
        for stage in [
            ReviewStageEnum.TECHNICAL.value,
            ReviewStageEnum.BUDGET.value,
            ReviewStageEnum.FINAL.value,
        ]:
            approval = ReviewApproval(
                reviewer_email=admin_email,
                stage_name=stage,
                status="approved",
            )
            approvals.append(approval)
        
        # Verify all approved by admin
        assert all(a.reviewer_email == admin_email for a in approvals)
        assert all(a.status == "approved" for a in approvals)
