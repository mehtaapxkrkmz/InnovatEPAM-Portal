from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    SUBMITTER = "submitter"
    EVALUATOR = "evaluator"
    ADMIN = "admin"


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)
    role: UserRole = UserRole.SUBMITTER


class UserCreate(UserBase):
    model_config = ConfigDict(from_attributes=True)

    password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(min_length=1)
    created_at: datetime
    is_active: bool = True


class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str = Field(alias="_id", min_length=1)
    hashed_password: str = Field(min_length=1)
    created_at: datetime
    is_active: bool = True


class CurrentUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    role: UserRole
