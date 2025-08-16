from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserShortOut(BaseModel):
    id: int
    name: str
    picture: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfileOut(BaseModel):
    id: int
    name: str
    email: str
    picture: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    google_id: str
    email: str
    name: str
    picture: Optional[str] = None
    encrypted_refresh_token: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None
    bio: Optional[str] = None
    encrypted_refresh_token: Optional[str] = None
    is_active: Optional[bool] = None
    updated_at: Optional[datetime] = None
