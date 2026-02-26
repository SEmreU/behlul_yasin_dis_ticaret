from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.user import SubscriptionTier


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    subscription_tier: SubscriptionTier
    query_credits: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
