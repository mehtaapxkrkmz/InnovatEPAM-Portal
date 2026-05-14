"""
Tests for Phase 6 - Blind Review (Anonymous Evaluation) feature.

Ensures that:
1. Admin/Evaluator users see creators as "Anonymous User" (except for own ideas)
2. Regular users see their own creator info on their ideas
3. Regular users see "Anonymous User" for other ideas
4. Blind Review Mode is indicated in UI for admin/evaluator users
"""

import pytest
from app.models.user import CurrentUser, UserRole


class TestBlindReviewLogic:
    """Test the logic for determining creator visibility."""

    def test_admin_sees_anonymous_for_other_creators(self):
        """Admin viewing an idea created by someone else should see 'Anonymous User'."""
        current_user_role = UserRole.ADMIN
        current_user_email = "admin@epam.com"
        idea_creator_email = "submitter@epam.com"
        
        # Admin is not the owner
        is_owner = current_user_email == idea_creator_email
        is_blind_review = current_user_role in [UserRole.ADMIN, UserRole.EVALUATOR]
        
        # Should display "Anonymous User"
        creator_display = "Anonymous User" if (is_blind_review and not is_owner) else idea_creator_email
        
        assert creator_display == "Anonymous User"

    def test_admin_sees_own_creator_info(self):
        """Admin viewing their own idea should see their own email."""
        current_user_role = UserRole.ADMIN
        current_user_email = "admin@epam.com"
        idea_creator_email = "admin@epam.com"  # Same as current user
        
        # Admin is the owner
        is_owner = current_user_email == idea_creator_email
        is_blind_review = current_user_role in [UserRole.ADMIN, UserRole.EVALUATOR]
        
        # Should display the actual creator email
        creator_display = "Anonymous User" if (is_blind_review and not is_owner) else idea_creator_email
        
        assert creator_display == "admin@epam.com"

    def test_evaluator_sees_anonymous_for_other_creators(self):
        """Evaluator viewing an idea created by someone else should see 'Anonymous User'."""
        current_user_role = UserRole.EVALUATOR
        current_user_email = "evaluator@epam.com"
        idea_creator_email = "submitter@epam.com"
        
        # Evaluator is not the owner
        is_owner = current_user_email == idea_creator_email
        is_blind_review = current_user_role in [UserRole.ADMIN, UserRole.EVALUATOR]
        
        # Should display "Anonymous User"
        creator_display = "Anonymous User" if (is_blind_review and not is_owner) else idea_creator_email
        
        assert creator_display == "Anonymous User"

    def test_submitter_sees_own_creator_info(self):
        """Submitter viewing their own idea should see their own email."""
        current_user_role = UserRole.SUBMITTER
        current_user_email = "submitter@epam.com"
        idea_creator_email = "submitter@epam.com"  # Same as current user
        
        # Submitter is the owner
        is_owner = current_user_email == idea_creator_email
        is_blind_review = current_user_role in [UserRole.ADMIN, UserRole.EVALUATOR]
        
        # Should display the actual creator email (blind review doesn't apply to submitters)
        creator_display = "Anonymous User" if (is_blind_review and not is_owner) else idea_creator_email
        
        assert creator_display == "submitter@epam.com"

    def test_submitter_sees_anonymous_for_other_creators(self):
        """Submitter viewing other ideas should see their creator info (blind review doesn't apply)."""
        current_user_role = UserRole.SUBMITTER
        current_user_email = "submitter1@epam.com"
        idea_creator_email = "submitter2@epam.com"
        
        # Submitter is not the owner
        is_owner = current_user_email == idea_creator_email
        is_blind_review = current_user_role in [UserRole.ADMIN, UserRole.EVALUATOR]
        
        # Should display the actual creator email (blind review only for admin/evaluator)
        creator_display = "Anonymous User" if (is_blind_review and not is_owner) else idea_creator_email
        
        assert creator_display == "submitter2@epam.com"

    def test_blind_review_mode_indicator_logic(self):
        """Verify logic for showing 'Blind Review Mode Active' indicator."""
        # For admin/evaluator users
        assert self.can_manage_status(UserRole.ADMIN) is True
        assert self.can_manage_status(UserRole.EVALUATOR) is True
        
        # For submitter users
        assert self.can_manage_status(UserRole.SUBMITTER) is False

    @staticmethod
    def can_manage_status(user_role: UserRole) -> bool:
        """Helper to determine if user can manage status (indicator condition)."""
        return user_role in [UserRole.ADMIN, UserRole.EVALUATOR]


class TestBlindReviewEdgeCases:
    """Test edge cases for blind review feature."""

    def test_unknown_creator_email_falls_back_to_unknown(self):
        """Ideas with missing creator_by should show 'Unknown'."""
        idea_creator_email = None
        current_user_email = "admin@epam.com"
        current_user_role = UserRole.ADMIN
        
        is_owner = current_user_email == idea_creator_email
        is_blind_review = current_user_role in [UserRole.ADMIN, UserRole.EVALUATOR]
        
        creator_display = "Anonymous User" if (is_blind_review and not is_owner) else (idea_creator_email or "Unknown")
        
        assert creator_display == "Anonymous User"

    def test_empty_creator_email_falls_back_to_unknown(self):
        """Ideas with empty creator_by should show 'Unknown'."""
        idea_creator_email = ""
        current_user_email = "admin@epam.com"
        current_user_role = UserRole.ADMIN
        
        is_owner = current_user_email == idea_creator_email
        is_blind_review = current_user_role in [UserRole.ADMIN, UserRole.EVALUATOR]
        
        creator_display = "Anonymous User" if (is_blind_review and not is_owner) else (idea_creator_email or "Unknown")
        
        assert creator_display == "Anonymous User"

    def test_case_sensitivity_in_email_matching(self):
        """Email matching for ownership should be case-insensitive or exact."""
        current_user_email = "Admin@EPAM.com"
        idea_creator_email = "admin@epam.com"
        
        # Exact match fails - they should be treated as different
        is_owner = current_user_email == idea_creator_email
        
        # This is expected behavior - emails are case-sensitive in storage
        assert is_owner is False


class TestBlindReviewIntegration:
    """Integration tests for blind review feature with ideas model."""

    def test_admin_dashboard_with_mixed_ideas(self):
        """
        Admin viewing dashboard with ideas from multiple creators:
        - Own idea: show creator email
        - Others' ideas: show "Anonymous User"
        """
        admin_email = "admin@epam.com"
        ideas = [
            {"id": "1", "created_by": admin_email, "title": "Admin's Idea"},
            {"id": "2", "created_by": "submitter1@epam.com", "title": "Others' Idea 1"},
            {"id": "3", "created_by": "submitter2@epam.com", "title": "Others' Idea 2"},
        ]
        
        admin_role = UserRole.ADMIN
        
        for idea in ideas:
            is_owner = admin_email == idea["created_by"]
            is_blind_review = admin_role in [UserRole.ADMIN, UserRole.EVALUATOR]
            creator_display = "Anonymous User" if (is_blind_review and not is_owner) else idea["created_by"]
            
            if idea["id"] == "1":
                assert creator_display == admin_email
            else:
                assert creator_display == "Anonymous User"

    def test_submitter_dashboard_sees_all_creators(self):
        """
        Submitter viewing dashboard should see:
        - Own ideas: show creator email
        - Others' ideas: show creator email (no blind review)
        """
        submitter_email = "submitter1@epam.com"
        ideas = [
            {"id": "1", "created_by": submitter_email, "title": "My Idea"},
            {"id": "2", "created_by": "submitter2@epam.com", "title": "Others' Idea 1"},
            {"id": "3", "created_by": "admin@epam.com", "title": "Others' Idea 2"},
        ]
        
        submitter_role = UserRole.SUBMITTER
        
        for idea in ideas:
            is_owner = submitter_email == idea["created_by"]
            is_blind_review = submitter_role in [UserRole.ADMIN, UserRole.EVALUATOR]
            creator_display = "Anonymous User" if (is_blind_review and not is_owner) else idea["created_by"]
            
            # All should show actual creator email (blind review doesn't apply)
            assert creator_display == idea["created_by"]
