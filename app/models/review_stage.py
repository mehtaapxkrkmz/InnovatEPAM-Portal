"""
Phase 5 - Multi-Stage Review (Configurable Stages)

This model defines the review stages that ideas progress through during evaluation.
Each stage can have configurable reviewers, approval requirements, and transitions.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class ReviewStageEnum(str, Enum):
    """Pre-defined review stages for the evaluation workflow."""
    TECHNICAL = "technical_review"
    BUDGET = "budget_review"
    LEADERSHIP = "leadership_review"
    FINAL = "final_approval"


class ReviewerRole(str, Enum):
    """Roles that can perform reviews at each stage."""
    TECHNICAL_LEAD = "technical_lead"
    FINANCE = "finance"
    LEADERSHIP = "leadership"
    ADMIN = "admin"


class ReviewStage(BaseModel):
    """Definition of a single review stage in the workflow."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: str = Field(alias="_id", min_length=1)
    stage_name: str = Field(min_length=1, max_length=100)
    stage_order: int = Field(ge=1)
    description: Optional[str] = Field(default=None, max_length=500)
    required_approvals: int = Field(default=1, ge=1)
    allowed_reviewer_roles: List[ReviewerRole] = Field(default_factory=list)
    allow_skip: bool = False  # Can this stage be skipped?
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewStageCreate(BaseModel):
    """Request model for creating a review stage."""
    stage_name: str = Field(min_length=1, max_length=100)
    stage_order: int = Field(ge=1)
    description: Optional[str] = Field(default=None, max_length=500)
    required_approvals: int = Field(default=1, ge=1)
    allowed_reviewer_roles: List[ReviewerRole] = Field(default_factory=list)
    allow_skip: bool = False


class ReviewStageRead(BaseModel):
    """Response model for review stages."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    stage_name: str
    stage_order: int
    description: Optional[str]
    required_approvals: int
    allowed_reviewer_roles: List[ReviewerRole]
    allow_skip: bool
    created_at: datetime


class ReviewApproval(BaseModel):
    """Tracks a single approval at a review stage."""
    model_config = ConfigDict(from_attributes=True)
    
    reviewer_email: str
    stage_name: str
    approved_at: datetime = Field(default_factory=datetime.utcnow)
    comment: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="approved")  # "approved" or "rejected"


class IdeaReviewProgress(BaseModel):
    """Tracks the review progress of an idea through all stages."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    idea_id: str
    current_stage: Optional[str] = None
    current_stage_order: int = 0
    approvals_received: List[ReviewApproval] = Field(default_factory=list)
    stages_completed: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
