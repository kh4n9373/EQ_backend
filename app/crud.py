from sqlalchemy.orm import Session
from app import models, schemas

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

def contribute_situation(db: Session, situation: schemas.SituationContribute):
    db_situation = models.Situation(
        context=situation.context,
        question=situation.question,
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
