from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    SUBMITTER = "submitter"
    EVALUATOR = "evaluator"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)
    role: UserRole = UserRole.SUBMITTER


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    id: str = Field(min_length=1)
    created_at: datetime
    is_active: bool = True


class UserInDB(UserBase):
    id: str = Field(alias="_id", min_length=1)
    hashed_password: str = Field(min_length=1)
    created_at: datetime
    is_active: bool = True
