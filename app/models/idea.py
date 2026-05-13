from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class IdeaStatus(str, Enum):
    SUBMITTED = "submitted"
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
    attachment_url: str | None = None


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
    attachment_url: str | None = None
    evaluator_comment: Optional[str] = None


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
    attachment_url: str | None = None
    evaluator_comment: Optional[str] = None


class IdeaStatusUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: IdeaStatus
    evaluator_comment: Optional[str] = None


class IdeaStatusUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: IdeaStatus
    evaluator_comment: Optional[str] = None
