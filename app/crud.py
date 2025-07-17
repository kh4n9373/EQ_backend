from sqlalchemy.orm import Session
from app import models, schemas


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def update_user_refresh_token(db: Session, user_id: int, encrypted_refresh_token: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.encrypted_refresh_token = encrypted_refresh_token
        db.commit()
        db.refresh(db_user)
    return db_user

def create_user(db: Session, user: dict):
    db_user = models.User(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_topics(db: Session):
    return db.query(models.Topic).all()

def get_situations_by_topic(db: Session, topic_id: int):
    return db.query(models.Situation).filter(models.Situation.topic_id == topic_id).all()

def create_answer(db: Session, answer: schemas.AnswerCreate, scores: dict, reasoning: dict):
    db_answer = models.Answer(
        situation_id=answer.situation_id,
        answer_text=answer.answer_text,
        scores=scores,
        reasoning=reasoning
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    question = db_answer.situation.question if db_answer.situation else None
    return db_answer, question

def create_result(db: Session, result: schemas.ResultCreate):
    db_result = models.Result(total_scores=result.total_scores)
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def contribute_situation(db: Session, situation: schemas.SituationContribute, user_id: int):
    db_situation = models.Situation(
        topic_id=situation.topic_id,
        user_id=user_id,
        context=situation.context,
        question=situation.question,
        image_url=situation.image_url,
        is_contributed=True
    )
    db.add(db_situation)
    db.commit()
    db.refresh(db_situation)
    return db_situation

def get_contributed_situations(db: Session):
    return db.query(models.Situation).filter(models.Situation.is_contributed == True).all()

def get_answers_by_situation(db: Session, situation_id: int):
    return db.query(models.Answer).filter(models.Answer.situation_id == situation_id).all()
