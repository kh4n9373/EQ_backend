import uuid

import pytest
from sqlalchemy.orm import Session

from app.repositories.situation_repository import SituationRepository
from app.repositories.topic_repository import TopicRepository


@pytest.fixture()
def topic_repo():
    return TopicRepository()


@pytest.fixture()
def situation_repo():
    return SituationRepository()


def test_create_and_get_topic(db_session: Session, topic_repo: TopicRepository):
    topic = topic_repo.create(db_session, {"name": f"T_{uuid.uuid4().hex[:6]}"})
    assert topic.id is not None
    fetched = topic_repo.get(db_session, topic.id)
    assert fetched is not None and fetched.id == topic.id


def test_create_situation_and_get(
    db_session: Session,
    topic_repo: TopicRepository,
    situation_repo: SituationRepository,
):
    topic = topic_repo.create(db_session, {"name": f"T_{uuid.uuid4().hex[:6]}"})
    sit = situation_repo.create(
        db_session,
        {
            "topic_id": topic.id,
            "context": "ctx",
            "question": "q?",
        },
    )
    assert sit.id is not None
    fetched = situation_repo.get(db_session, sit.id)
    assert fetched is not None and fetched.id == sit.id
