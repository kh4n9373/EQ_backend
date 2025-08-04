import json
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from app import crud, database, models, openai_utils, schemas
from app.authorization import (  # decrypt_refresh_token,
    create_access_token,
    encrypt_refresh_token,
    get_current_user,
    oauth,
)

config = Config(".env")

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=config("SECRET_KEY"),
)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def read_root():
    return {"status": "Healthy!"}


@app.get("/users/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user


@app.get("/users/search")
def search_users(query: str, db: Session = Depends(get_db)):

    if not query or len(query) < 2:
        return []

    users = (
        db.query(models.User)
        .filter(models.User.name.ilike(f"%{query}%"))
        .limit(10)
        .all()
    )

    return [
        schemas.UserShortOut(id=user.id, name=user.name, picture=user.picture)
        for user in users
    ]


@app.get("/users/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return schemas.UserProfileOut(
        id=user.id, name=user.name, email=user.email, picture=user.picture, bio=user.bio
    )


@app.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Could not validate credentials, Error: {e}"
        )
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    refresh_token = token.get("refresh_token")
    db_user = crud.get_user_by_email(db, email=user_info.get("email"))
    if db_user:
        update_data = {}
        if db_user.name != user_info["name"]:
            update_data["name"] = user_info["name"]
        if db_user.picture != user_info["picture"]:
            update_data["picture"] = user_info["picture"]
        if update_data:
            crud.update_user(db, db_user=db_user, data_to_update=update_data)
    else:
        new_user = {
            "google_id": user_info["sub"],
            "email": user_info["email"],
            "name": user_info["name"],
            "picture": user_info["picture"],
            "encrypted_refresh_token": (
                encrypt_refresh_token(refresh_token) if refresh_token else None
            ),
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
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
        secure=True,
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
    situation = (
        db.query(models.Situation)
        .filter(models.Situation.id == answer.situation_id)
        .first()
    )
    if not situation:
        raise HTTPException(status_code=404, detail="Situation not found")
    question = situation.question

    scores, reasoning = openai_utils.analyze_eq(
        situation.context, question, answer.answer_text
    )
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
        created_at=db_answer.created_at,
    )


@app.post("/results", response_model=schemas.ResultOut)
def create_result(result: schemas.ResultCreate, db: Session = Depends(get_db)):
    db_result = crud.create_result(db, result)
    return db_result


@app.post("/contribute-situation", response_model=schemas.SituationContributeOut)
def contribute_situation(
    situation: schemas.SituationContribute,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_situation = crud.contribute_situation(db, situation, current_user["id"])
    return schemas.SituationContributeOut(
        id=db_situation.id,
        topic_id=db_situation.topic_id,
        user_id=current_user["id"],
        image_url=db_situation.image_url,
        context=db_situation.context,
        question=db_situation.question,
        created_at=db_situation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.get("/contributed-situations", response_model=list[schemas.SituationFeedOut])
def get_contributed_situations(db: Session = Depends(get_db)):
    situations = (
        db.query(models.Situation).filter(models.Situation.topic_id is not None).all()
    )
    result = []
    for s in situations:
        user = db.query(models.User).filter(models.User.id == s.user_id).first()
        if not user:
            continue
        result.append(
            schemas.SituationFeedOut(
                id=s.id,
                topic_id=s.topic_id,
                user=(
                    schemas.UserShortOut(
                        id=user.id, name=user.name, picture=user.picture
                    )
                    if user
                    else None
                ),
                image_url=s.image_url,
                context=s.context,
                question=s.question,
                created_at=s.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
    return result


@app.get("/answers-by-situation", response_model=list[schemas.AnswerOut])
def get_answers_by_situation(situation_id: int, db: Session = Depends(get_db)):
    answers = crud.get_answers_by_situation(db, situation_id)
    result = []
    for a in answers:
        scores_val = safe_json_loads(a.scores)
        reasoning_val = safe_json_loads(a.reasoning)
        result.append(
            schemas.AnswerOut(
                id=a.id,
                situation_id=a.situation_id,
                answer_text=a.answer_text,
                scores=scores_val,
                reasoning=reasoning_val,
                question=a.situation.question if a.situation else None,
                context=a.situation.context if a.situation else None,
                created_at=a.created_at,
            )
        )
    return result


@app.get("/situations/{situation_id}/comments")
def get_comments_by_situation(situation_id: int, db: Session = Depends(get_db)):
    comments = crud.get_comments_by_situation(db, situation_id)
    return [
        schemas.CommentOut(
            id=c.id,
            situation_id=c.situation_id,
            user=(
                schemas.UserShortOut(
                    id=c.user.id, name=c.user.name, picture=c.user.picture
                )
                if c.user
                else None
            ),
            content=c.content,
            sentiment_analysis=c.sentiment_analysis,
            created_at=c.created_at,
        )
        for c in comments
    ]


@app.post("/situations/{situation_id}/comments")
def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Phân tích sentiment trước khi lưu comment
    try:
        sentiment_result = analyze_sentiment_content(comment.content)
        db_comment = crud.create_comment(
            db, comment, current_user["id"], sentiment_result
        )
    except Exception:
        # Nếu phân tích sentiment thất bại, vẫn lưu comment
        db_comment = crud.create_comment(db, comment, current_user["id"])

    return db_comment


def analyze_sentiment_content(content: str):
    """Hàm helper để phân tích sentiment"""
    # Từ khóa tiêu cực và stress
    negative_keywords = [
        "chán",
        "mệt",
        "stress",
        "khó chịu",
        "bực",
        "tức",
        "giận",
        "buồn",
        "thất vọng",
        "không thích",
        "ghét",
        "khó khăn",
        "vấn đề",
        "lo lắng",
        "sợ",
        "hoảng",
        "tuyệt vọng",
        "đau khổ",
        "khổ sở",
        "mệt mỏi",
        "kiệt sức",
        "bế tắc",
    ]

    # Từ khóa tích cực
    positive_keywords = [
        "vui",
        "hạnh phúc",
        "tốt",
        "tuyệt",
        "thích",
        "yêu",
        "thú vị",
        "thành công",
        "may mắn",
        "tích cực",
        "lạc quan",
        "hy vọng",
        "niềm vui",
        "hài lòng",
    ]

    text_lower = content.lower()

    # Đếm từ khóa
    negative_count = sum(1 for word in negative_keywords if word in text_lower)
    positive_count = sum(1 for word in positive_keywords if word in text_lower)

    # Tính sentiment score (-1 đến 1)
    total_words = len(text_lower.split())
    if total_words == 0:
        sentiment_score = 0
    else:
        sentiment_score = (positive_count - negative_count) / max(total_words, 1)
        sentiment_score = max(-1, min(1, sentiment_score))  # Giới hạn trong [-1, 1]

    # Xác định sentiment
    if sentiment_score > 0.1:
        sentiment = "positive"
        severity = "low"
    elif sentiment_score < -0.1:
        sentiment = "negative"
        severity = "high" if negative_count > 3 else "medium"
    else:
        sentiment = "neutral"
        severity = "low"

    # Tạo cảnh báo và gợi ý
    warning = None
    suggestions = []

    if sentiment == "negative":
        if severity == "high":
            warning = (
                "⚠️ Phát hiện dấu hiệu stress/tiêu cực cao. Hãy cân nhắc tìm sự hỗ trợ."
            )
            suggestions = [
                "Hít thở sâu và thư giãn một chút",
                "Chia sẻ với bạn bè hoặc người thân",
                "Tập trung vào những điều tích cực",
                "Tìm hoạt động giải trí để thư giãn",
            ]
        else:
            warning = "💡 Có vẻ bạn đang hơi tiêu cực. Mọi thứ sẽ ổn thôi!"
            suggestions = [
                "Thử nhìn vấn đề từ góc độ khác",
                "Tập trung vào giải pháp thay vì vấn đề",
                "Chia sẻ để được lắng nghe và hỗ trợ",
            ]
    elif sentiment == "positive":
        suggestions = [
            "Tuyệt vời! Hãy lan tỏa năng lượng tích cực này",
            "Chia sẻ niềm vui với mọi người xung quanh",
            "Ghi nhớ cảm giác này để vượt qua khó khăn sau này",
        ]
    else:
        suggestions = [
            "Hãy chia sẻ thêm về cảm xúc của bạn",
            "Thử bày tỏ rõ ràng hơn về suy nghĩ của mình",
        ]

    return {
        "sentiment": sentiment,
        "score": sentiment_score,
        "severity": severity,
        "warning": warning,
        "suggestions": suggestions,
        "analysis": {
            "positive_words": positive_count,
            "negative_words": negative_count,
            "total_words": total_words,
        },
    }


@app.post("/analyze-sentiment")
def analyze_sentiment(
    text: schemas.SentimentAnalysisRequest, db: Session = Depends(get_db)
):
    """Phân tích sentiment của text và đưa ra cảnh báo nếu cần"""
    try:

        negative_keywords = [
            "chán",
            "mệt",
            "stress",
            "khó chịu",
            "bực",
            "tức",
            "giận",
            "buồn",
            "thất vọng",
            "không thích",
            "ghét",
            "khó khăn",
            "vấn đề",
            "lo lắng",
            "sợ",
            "hoảng",
            "tuyệt vọng",
            "đau khổ",
            "khổ sở",
            "mệt mỏi",
            "kiệt sức",
            "bế tắc",
            "vl",
        ]

        positive_keywords = [
            "vui",
            "hạnh phúc",
            "tốt",
            "tuyệt",
            "thích",
            "yêu",
            "thú vị",
            "thành công",
            "may mắn",
            "tích cực",
            "lạc quan",
            "hy vọng",
            "niềm vui",
            "hài lòng",
        ]

        text_lower = text.content.lower()

        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        positive_count = sum(1 for word in positive_keywords if word in text_lower)

        total_words = len(text_lower.split())
        if total_words == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / max(total_words, 1)
            sentiment_score = max(-1, min(1, sentiment_score))

        if sentiment_score > 0.1:
            sentiment = "positive"
            severity = "low"
        elif sentiment_score < -0.1:
            sentiment = "negative"
            severity = "high" if negative_count > 3 else "medium"
        else:
            sentiment = "neutral"
            severity = "low"

        warning = None
        suggestions = []

        if sentiment == "negative":
            if severity == "high":
                warning = "⚠️ Phát hiện dấu hiệu stress/tiêu cực cao."
                suggestions = [
                    "Hít thở sâu và thư giãn một chút",
                    "Chia sẻ với bạn bè hoặc người thân",
                    "Tập trung vào những điều tích cực",
                    "Tìm hoạt động giải trí để thư giãn",
                ]
            else:
                warning = "💡 Có vẻ bạn đang hơi tiêu cực. Mọi thứ sẽ ổn thôi!"
                suggestions = [
                    "Thử nhìn vấn đề từ góc độ khác",
                    "Tập trung vào giải pháp thay vì vấn đề",
                    "Chia sẻ để được lắng nghe và hỗ trợ",
                ]
        elif sentiment == "positive":
            suggestions = [
                "Tuyệt vời! Hãy lan tỏa năng lượng tích cực này",
                "Chia sẻ niềm vui với mọi người xung quanh",
                "Ghi nhớ cảm giác này để vượt qua khó khăn sau này",
            ]
        else:
            suggestions = [
                "Hãy chia sẻ thêm về cảm xúc của bạn",
                "Thử bày tỏ rõ ràng hơn về suy nghĩ của mình",
            ]

        return {
            "sentiment": sentiment,
            "score": sentiment_score,
            "severity": severity,
            "warning": warning,
            "suggestions": suggestions,
            "analysis": {
                "positive_words": positive_count,
                "negative_words": negative_count,
                "total_words": total_words,
            },
        }

    except Exception as e:
        return {"error": f"Không thể phân tích sentiment: {str(e)}"}


@app.get("/situations/{situation_id}/reactions")
def get_reactions_by_situation(situation_id: int, db: Session = Depends(get_db)):
    reactions = crud.get_reactions_by_situation(db, situation_id)
    return [
        schemas.ReactionOut(
            id=r.id,
            situation_id=r.situation_id,
            user=(
                schemas.UserShortOut(
                    id=r.user.id, name=r.user.name, picture=r.user.picture
                )
                if r.user
                else None
            ),
            reaction_type=r.reaction_type,
            created_at=r.created_at,
        )
        for r in reactions
    ]


@app.post("/situations/{situation_id}/reactions")
def create_reaction(
    reaction: schemas.ReactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_reaction = crud.create_reaction(db, reaction, current_user["id"])
    return db_reaction


@app.delete("/situations/{situation_id}/reactions")
def delete_reaction(
    request: schemas.ReactionDelete,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if crud.delete_reaction(
        db, request.situation_id, current_user["id"], request.reaction_type
    ):
        return {"message": "Reaction deleted"}
    raise HTTPException(status_code=404, detail="Reaction not found")
