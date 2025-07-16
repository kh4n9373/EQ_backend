from fastapi import FastAPI, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app import models, schemas, crud, database, openai_utils
from fastapi.middleware.cors import CORSMiddleware
from app.authorization import oauth, create_access_token, encrypt_refresh_token, decrypt_refresh_token, get_current_user
import json
from sqlalchemy import DateTime, func
from datetime import datetime, timezone
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
from fastapi.responses import RedirectResponse


config = Config(".env")

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=config('SECRET_KEY'),
)
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/users/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    refresh_token = token.get("refresh_token")
    db_user = crud.get_user_by_email(db, email=user_info.get("email"))
    if db_user:
        update_data = {}
        if db_user.name != user_info['name']:
            update_data['name'] = user_info['name']
        if db_user.picture != user_info['picture']:
            update_data['picture'] = user_info['picture']
        if update_data:
            crud.update_user(db, db_user=db_user, data_to_update=update_data)
    else:
        new_user = {
            "google_id": user_info['sub'],
            "email": user_info['email'],
            "name": user_info['name'],
            "picture": user_info['picture'],
            "encrypted_refresh_token": encrypt_refresh_token(refresh_token) if refresh_token else None,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        db_user = crud.create_user(db=db, user=new_user)

    if refresh_token:
        encrypted_refresh_token = encrypt_refresh_token(refresh_token)
        crud.update_user_refresh_token(db, db_user.id, encrypted_refresh_token)

    access_token = create_access_token(data={"sub": db_user.email})
    # return {
    #     "access_token": access_token,
    #     "token_type": "bearer",
    #     "user_info": {
    #         "id": db_user.id,
    #         "email": db_user.email,
    #         "name": db_user.name,
    #         "picture": db_user.picture
    #     }
    # }
    response = RedirectResponse(url="http://localhost:3000/")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=True
    )
    return response
@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"message": "Logged out"}
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
    situation = db.query(models.Situation).filter(models.Situation.id == answer.situation_id).first()
    if not situation:
        raise HTTPException(status_code=404, detail="Situation not found")
    question = situation.question

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
        topic_id=db_situation.topic_id,
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
            topic_id=s.topic_id,
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
