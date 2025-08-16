from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SituationBase(BaseModel):
    topic_id: Optional[int] = None
    context: str = Field(..., min_length=1, description="Context cannot be empty")
    question: str = Field(..., min_length=1, description="Question cannot be empty")
    # image_url: Optional[str] = None


class SituationCreate(SituationBase):
    topic_id: Optional[int] = None
    user_id: Optional[int] = None


class SituationUpdate(BaseModel):
    context: Optional[str] = Field(
        None, min_length=1, description="Context cannot be empty"
    )
    question: Optional[str] = Field(
        None, min_length=1, description="Question cannot be empty"
    )
    image_url: Optional[str] = None
    topic_id: Optional[int] = None


class SituationOut(SituationBase):
    id: int
    topic_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SituationContributeOut(BaseModel):
    id: int
    topic_id: Optional[int] = None
    user_id: int
    image_url: Optional[str] = None
    context: str
    question: str
    created_at: datetime

    class Config:
        from_attributes = True


class SituationFeedOut(BaseModel):
    id: int
    topic_id: Optional[int] = None
    user_id: Optional[int] = None
    user: Optional[dict] = None  # UserShortOut
    image_url: Optional[str] = None
    context: str
    question: str
    created_at: str

    class Config:
        from_attributes = True
