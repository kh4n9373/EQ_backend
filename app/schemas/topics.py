from pydantic import BaseModel, Field


class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, description="Topic name cannot be empty")


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    name: str = Field(..., min_length=1, description="Topic name cannot be empty")


class TopicOut(TopicBase):
    id: int

    class Config:
        from_attributes = True
