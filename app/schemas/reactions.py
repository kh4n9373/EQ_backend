from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.users import UserShortOut


class ReactionBase(BaseModel):
    situation_id: int
    user_id: int
    reaction_type: str


class ReactionCreate(ReactionBase):
    pass


class ReactionUpdate(BaseModel):
    reaction_type: str


class ReactionOut(ReactionBase):
    id: int
    created_at: Optional[datetime] = None
    user: Optional[UserShortOut] = None

    class Config:
        from_attributes = True
