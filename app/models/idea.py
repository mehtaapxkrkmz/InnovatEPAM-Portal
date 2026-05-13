from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class IdeaStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class IdeaCategory(str, Enum):
    PRODUCT = "Product"
    PROCESS = "Process"
    COST_SAVINGS = "Cost-Savings"
    CUSTOMER_EXPERIENCE = "Customer-Experience"


class IdeaCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10, max_length=5000)
    category: IdeaCategory
    attachment_url: str | None = None


class IdeaRead(BaseModel):
    id: str = Field(min_length=1)
    title: str
    description: str
    category: IdeaCategory
    status: IdeaStatus = IdeaStatus.SUBMITTED
    created_by: str
    created_at: datetime
    attachment_url: str | None = None


class IdeaInDB(BaseModel):
    id: str = Field(alias="_id", min_length=1)
    title: str
    description: str
    category: IdeaCategory
    status: IdeaStatus = IdeaStatus.SUBMITTED
    created_by: str
    created_at: datetime
    attachment_url: str | None = None
