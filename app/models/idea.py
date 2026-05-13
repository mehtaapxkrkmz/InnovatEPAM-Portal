from datetime import datetime
from enum import Enum

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


class IdeaCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10, max_length=5000)
    category: IdeaCategory
    attachment_url: str | None = None


class IdeaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(min_length=1)
    title: str
    description: str
    category: IdeaCategory
    status: IdeaStatus = IdeaStatus.SUBMITTED
    created_by: str
    created_at: datetime
    attachment_url: str | None = None


class IdeaInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str = Field(alias="_id", min_length=1)
    title: str
    description: str
    category: IdeaCategory
    status: IdeaStatus = IdeaStatus.SUBMITTED
    created_by: str
    created_at: datetime
    attachment_url: str | None = None


class IdeaStatusUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: IdeaStatus


class IdeaStatusUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: IdeaStatus
