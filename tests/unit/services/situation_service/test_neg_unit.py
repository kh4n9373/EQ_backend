from types import SimpleNamespace

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.situations import SituationBase, SituationUpdate
from app.services.situation_service import SituationService


class DummyRepo:
    def __init__(self, get_map=None):
        self.get_map = get_map or {}
        self.created = None
        self.updated = None
        self.deleted = None

    def get(self, db, sid):
        return self.get_map.get(sid)

    def create(self, db, situation_in):
        self.created = situation_in
        return SimpleNamespace(
            id=10, topic_id=None, user_id=1, context="c", question="q?", created_at=None
        )

    def update(self, db, obj, upd):
        self.updated = upd
        return SimpleNamespace(
            id=obj.id,
            topic_id=obj.topic_id,
            user_id=1,
            context="c2",
            question="q2?",
            created_at=None,
        )

    def delete(self, db, sid):
        self.deleted = sid
        return True


def test_get_update_delete_not_found():
    svc = SituationService(repo=DummyRepo(get_map={}))
    with pytest.raises(NotFoundError):
        svc.get_situation(99)
    with pytest.raises(NotFoundError):
        svc.update_situation(99, SituationUpdate(context="x"))
    with pytest.raises(NotFoundError):
        svc.delete_situation(99)


def test_create_situation_with_nonexistent_topic(monkeypatch):
    svc = SituationService(repo=DummyRepo())

    # monkeypatch TopicRepository.get to return None so topic_id becomes None
    from app.services import situation_service as ss

    class FakeTopicRepo:
        def get(self, db, tid):
            return None

    monkeypatch.setattr(ss, "TopicRepository", lambda: FakeTopicRepo())

    created = svc.create_situation(
        SituationBase(context="c", question="q?", topic_id=123), user_id=1
    )
    assert created.topic_id is None
