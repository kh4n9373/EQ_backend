from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id: Optional[int] = Column(Integer, primary_key=True, index=True)
    google_id: Optional[str] = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name: Optional[str] = Column(String)
    picture: Optional[str] = Column(String)
    bio: Optional[str] = Column(String, nullable=True)
    encrypted_refresh_token: Optional[str] = Column(String)
    is_active: bool = True
    created_at: Optional[datetime] = Column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Optional[datetime] = Column(
        DateTime(timezone=True), server_default=func.now()
    )


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    situations = relationship("Situation", back_populates="topic")


class Situation(Base):
    __tablename__ = "situations"
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    user = relationship("User")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    context = Column(String)
    question = Column(String)
    image_url = Column(String, nullable=True)
    is_contributed = Column(
        Boolean, default=False
    )  # Đánh dấu tình huống do user đóng góp
    topic = relationship("Topic", back_populates="situations")
    answers = relationship("Answer", back_populates="situation")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    situation_id = Column(Integer, ForeignKey("situations.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    answer_text = Column(String)
    scores = Column(JSON)  # 5 trụ EQ
    reasoning = Column(JSON)  # Giải thích cho từng trụ EQ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    situation = relationship("Situation", back_populates="answers")
    user = relationship("User")


class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("users.id"))  # Để sau khi có user
    total_scores = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    situation_id = Column(Integer, ForeignKey("situations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    sentiment_score = Column(Integer, nullable=True)
    sentiment_label = Column(String, nullable=True)
    sentiment_analysis = Column(JSON, nullable=True)  # Lưu kết quả sentiment analysis
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    situation = relationship("Situation")
    user = relationship("User")


class Reaction(Base):
    __tablename__ = "reactions"
    id = Column(Integer, primary_key=True, index=True)
    situation_id = Column(Integer, ForeignKey("situations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    reaction_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    situation = relationship("Situation")
    user = relationship("User")
