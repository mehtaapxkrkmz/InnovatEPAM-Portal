from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class IdeaStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    TECH_REVIEW = "tech_review"
    BUSINESS_REVIEW = "business_review"
    LEADERSHIP_REVIEW = "leadership_review"
    FINAL_REVIEW = "final_review"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower().replace(" ", "_")
            for member in cls:
                if normalized in (member.value.lower(), member.name.lower()):
                    return member
        return None


class IdeaCategory(str, Enum):
    PRODUCT = "Product"
    PROCESS = "Process"
    COST_SAVINGS = "Cost-Savings"
    CUSTOMER_EXPERIENCE = "Customer-Experience"


class IdeaPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class IdeaCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10, max_length=5000)
    category: IdeaCategory
    priority: IdeaPriority = IdeaPriority.MEDIUM
    estimated_budget: float | None = None
    attachment_urls: list[str] = Field(default_factory=list)
    initial_status: IdeaStatus = IdeaStatus.SUBMITTED


class IdeaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(min_length=1)
    title: str
    description: str
    category: IdeaCategory
    priority: IdeaPriority = IdeaPriority.MEDIUM
    estimated_budget: float | None = None
    status: IdeaStatus = IdeaStatus.SUBMITTED
    created_by: str
    created_at: datetime
    attachment_urls: list[str] = Field(default_factory=list)
    evaluator_comment: Optional[str] = None
    score: Optional[int] = Field(default=None, ge=1, le=5)


class IdeaInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str = Field(alias="_id", min_length=1)
    title: str
    description: str
    category: IdeaCategory
    priority: IdeaPriority = IdeaPriority.MEDIUM
    estimated_budget: float | None = None
    status: IdeaStatus = IdeaStatus.SUBMITTED
    created_by: str
    created_at: datetime
    attachment_urls: list[str] = Field(default_factory=list)
    evaluator_comment: Optional[str] = None
    score: Optional[int] = Field(default=None, ge=1, le=5)


class IdeaStatusUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: IdeaStatus
    evaluator_comment: Optional[str] = None
    score: Optional[int] = Field(default=None, ge=1, le=5)


class IdeaStatusUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: IdeaStatus
    evaluator_comment: Optional[str] = None
    score: Optional[int] = Field(default=None, ge=1, le=5)
