from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    situations = relationship("Situation", back_populates="topic")

class Situation(Base):
    __tablename__ = "situations"
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    context = Column(String)
    question = Column(String)
    is_contributed = Column(Boolean, default=False)  # Đánh dấu tình huống do user đóng góp
    topic = relationship("Topic", back_populates="situations")
    answers = relationship("Answer", back_populates="situation")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    situation_id = Column(Integer, ForeignKey("situations.id"))
    answer_text = Column(String)
    scores = Column(JSON)  # 5 trụ EQ
    reasoning = Column(JSON)  # Giải thích cho từng trụ EQ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    situation = relationship("Situation", back_populates="answers")

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("users.id"))  # Để sau khi có user
    total_scores = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
