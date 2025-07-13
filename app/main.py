from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, crud, database, openai_utils
from fastapi.middleware.cors import CORSMiddleware
import json
from sqlalchemy import DateTime, func

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Cho phép CORS cho frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/topics", response_model=list[schemas.TopicOut])
def read_topics(db: Session = Depends(get_db)):
    return crud.get_topics(db)

@app.get("/situations", response_model=list[schemas.SituationOut])
def read_situations(topic_id: int, db: Session = Depends(get_db)):
    return crud.get_situations_by_topic(db, topic_id)

def safe_json_loads(val):
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return {}
    return {}

@app.post("/analyze", response_model=schemas.AnswerOut)
def analyze_answer(answer: schemas.AnswerCreate, db: Session = Depends(get_db)):
    # Lấy question gốc từ situation_id
    situation = db.query(models.Situation).filter(models.Situation.id == answer.situation_id).first()
    if not situation:
        raise HTTPException(status_code=404, detail="Situation not found")
    question = situation.question

    # Gọi hàm phân tích EQ (mock hoặc LLM)
    scores, reasoning = openai_utils.analyze_eq(situation.context, question, answer.answer_text)
    db_answer, _ = crud.create_answer(db, answer, scores, reasoning)
    scores_val = safe_json_loads(db_answer.scores)
    reasoning_val = safe_json_loads(db_answer.reasoning)
    return schemas.AnswerOut(
        id=db_answer.id,
        situation_id=db_answer.situation_id,
        answer_text=db_answer.answer_text,
        scores=scores_val,
        reasoning=reasoning_val,
        question=question,
        context=situation.context,
        created_at=db_answer.created_at
    )

@app.post("/results", response_model=schemas.ResultOut)
def create_result(result: schemas.ResultCreate, db: Session = Depends(get_db)):
    db_result = crud.create_result(db, result)
    return db_result

@app.post("/contribute-situation", response_model=schemas.SituationContributeOut)
def contribute_situation(situation: schemas.SituationContribute, db: Session = Depends(get_db)):
    db_situation = crud.contribute_situation(db, situation)
    return schemas.SituationContributeOut(
        id=db_situation.id,
        context=db_situation.context,
        question=db_situation.question,
        created_at=db_situation.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/contributed-situations", response_model=list[schemas.SituationContributeOut])
def get_contributed_situations(db: Session = Depends(get_db)):
    situations = crud.get_contributed_situations(db)
    return [
        schemas.SituationContributeOut(
            id=s.id,
            context=s.context,
            question=s.question,
            created_at=s.created_at.strftime("%Y-%m-%d %H:%M:%S")   
        ) for s in situations
    ]

@app.get("/answers-by-situation", response_model=list[schemas.AnswerOut])
def get_answers_by_situation(situation_id: int, db: Session = Depends(get_db)):
    answers = crud.get_answers_by_situation(db, situation_id)
    result = []
    for a in answers:
        scores_val = safe_json_loads(a.scores)
        reasoning_val = safe_json_loads(a.reasoning)
        result.append(schemas.AnswerOut(
            id=a.id,
            situation_id=a.situation_id,
            answer_text=a.answer_text,
            scores=scores_val,
            reasoning=reasoning_val,
            question=a.situation.question if a.situation else None,
            context=a.situation.context if a.situation else None,
            created_at=a.created_at
        ))
    return result
