from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AnswerCreate(BaseModel):
    situation_id: int
    answer_text: str = Field(
        ..., min_length=1, description="Answer text cannot be empty"
    )


class AnswerOut(BaseModel):
    id: int
    situation_id: int
    answer_text: str
    scores: Dict[str, Any]
    reasoning: Dict[str, Any]
    question: str
    context: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnswerUpdate(BaseModel):
    answer_text: Optional[str] = None


class SentimentAnalysisRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Content cannot be empty")


# class ResultCreate(BaseModel):
#     situation_id: int
#     user_id: int
#     scores: Dict[str, Any]
#     reasoning: str

# class ResultOut(BaseModel):
#     id: int
#     situation_id: int
#     user_id: int
#     scores: Dict[str, Any]
#     reasoning: str
#     created_at: datetime

#     class Config:
#         orm_mode = True
