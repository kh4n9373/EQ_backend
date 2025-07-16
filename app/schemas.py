from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class TopicBase(BaseModel):
    name: str

class TopicCreate(TopicBase):
    pass

class TopicOut(TopicBase):
    id: int
    class Config:
        orm_mode = True

class SituationBase(BaseModel):
    context: str
    question: str
    topic_id: Optional[int] = None
    is_contributed: Optional[bool] = False

class SituationCreate(SituationBase):
    pass

class SituationOut(SituationBase):
    id: int
    class Config:
        orm_mode = True

class SituationContribute(BaseModel):
    topic_id: int
    context: str
    question: str
    created_at: Optional[datetime] = None

class SituationContributeOut(BaseModel):
    id: int
    context: str
    topic_id: int
    question: str
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True

class AnswerBase(BaseModel):
    situation_id: int
    answer_text: str

class AnswerCreate(AnswerBase):
    pass

class AnswerOut(AnswerBase):
    id: int
    scores: Dict[str, int]
    reasoning: Dict[str, str]
    question: str
    context: Optional[str] = None
    created_at: datetime
    class Config:
        orm_mode = True

class ResultBase(BaseModel):
    total_scores: Dict[str, int]

class ResultCreate(ResultBase):
    pass

class ResultOut(ResultBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True
