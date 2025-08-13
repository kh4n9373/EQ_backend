import json

import pytest
from sqlalchemy.orm import Session

from app.models import Situation, Topic
from app.repositories.answer_repository import AnswerRepository


def _ensure_situation(db: Session):
    topic = Topic(name="RepoTestTopic")
    db.add(topic)
    db.commit()
    db.refresh(topic)

    sit = Situation(topic_id=topic.id, context="ctx", question="q?")
    db.add(sit)
    db.commit()
    db.refresh(sit)
    return sit


def test_create_answer_with_analysis_and_get_by_situation(db_session: Session):
    repo = AnswerRepository()
    sit = _ensure_situation(db_session)

    ans = repo.create_answer_with_analysis(
        db_session,
        {"situation_id": sit.id, "answer_text": "A"},
        scores={"k": 1},
        reasoning={"k": "r"},
    )
    assert ans.id is not None
    # stored as JSON string
    assert isinstance(ans.scores, str) and json.loads(ans.scores)["k"] == 1

    lst = repo.get_by_situation(db_session, sit.id)
    assert len(lst) == 1 and lst[0].id == ans.id
