from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(min_length=1)
    refresh_token: str = Field(min_length=1)
    token_type: str = Field(default="bearer", min_length=1)


class TokenData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    role: UserRole
    exp: datetime
