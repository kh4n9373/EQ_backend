import pytest
from sqlalchemy.orm import Session

from app.models import Situation, Topic, User
from app.repositories.reaction_repository import ReactionRepository


def _ensure_user_and_situation(db: Session):
    user = User(email="react_user@example.com", name="ReactUser")
    db.add(user)
    db.commit()
    db.refresh(user)

    topic = Topic(name="RepoTopicReact")
    db.add(topic)
    db.commit()
    db.refresh(topic)

    sit = Situation(topic_id=topic.id, context="ctx", question="q?")
    db.add(sit)
    db.commit()
    db.refresh(sit)

    return user, sit


def test_reaction_repository_crud(db_session: Session):
    repo = ReactionRepository()
    user, sit = _ensure_user_and_situation(db_session)

    # create
    r = repo.create(
        db_session,
        {"situation_id": sit.id, "user_id": user.id, "reaction_type": "like"},
    )
    assert r.id is not None

    # get by situation (joined with user)
    lst = repo.get_by_situation(db_session, sit.id)
    assert any(x.id == r.id for x in lst)

    # get by user and situation
    one = repo.get_by_user_and_situation(db_session, user.id, sit.id)
    assert one and one.id == r.id

    # update reaction
    updated = repo.update_reaction(db_session, r.id, "dislike")
    assert updated.reaction_type == "dislike"
