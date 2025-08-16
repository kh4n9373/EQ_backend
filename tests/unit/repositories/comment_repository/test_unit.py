import pytest
from sqlalchemy.orm import Session

from app.models import Situation, Topic, User
from app.repositories.comment_repository import CommentRepository


def _ensure_user_and_situation(db: Session):
    user = User(email="repo_user@example.com", name="RepoUser")
    db.add(user)
    db.commit()
    db.refresh(user)

    topic = Topic(name="RepoTopicCmt")
    db.add(topic)
    db.commit()
    db.refresh(topic)

    sit = Situation(topic_id=topic.id, context="ctx", question="q?")
    db.add(sit)
    db.commit()
    db.refresh(sit)

    return user, sit


def test_comment_repository_crud(db_session: Session):
    repo = CommentRepository()
    user, sit = _ensure_user_and_situation(db_session)

    # create with sentiment
    c = repo.create_with_sentiment(
        db_session,
        {"situation_id": sit.id, "content": "hello"},
        user_id=user.id,
        sentiment_result={"sentiment": "positive"},
    )
    assert c.id is not None and c.user_id == user.id

    # get by id
    g = repo.get_comment_by_id(db_session, c.id)
    assert g.id == c.id

    # list by situation
    lst = repo.get_by_situation(db_session, sit.id)
    assert any(x.id == c.id for x in lst)

    # list all
    la = repo.list_comments(db_session)
    assert isinstance(la, list) and len(la) >= 1
