from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class Token(BaseModel):
    access_token: str = Field(min_length=1)
    refresh_token: str = Field(min_length=1)
    token_type: str = Field(default="bearer", min_length=1)


class TokenData(BaseModel):
    email: EmailStr
    role: UserRole
    exp: datetime
