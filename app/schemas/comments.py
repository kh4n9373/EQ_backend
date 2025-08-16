from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    content: str = Field(
        ..., min_length=1, description="Comment content cannot be empty"
    )
    situation_id: Optional[int] = None


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(
        None, min_length=1, description="Comment content cannot be empty"
    )


class CommentOut(CommentBase):
    id: int
    user_id: int
    sentiment_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime
    user: Optional[dict] = None

    class Config:
        from_attributes = True
