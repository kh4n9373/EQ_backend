from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services.situation_service import SituationService


def test_get_situations_by_topic_maps_to_schema(monkeypatch):
    repo = Mock()
    service = SituationService(repo=repo)
    # Provide minimal ORM-like objects
    situation = SimpleNamespace(
        id=1, topic_id=2, user_id=3, context="c", question="q", created_at=None
    )
    repo.get_by_topic.return_value = [situation]
    out = service.get_situations_by_topic(2)
    assert len(out) == 1
    assert out[0].id == 1


def test_get_situation_not_found(monkeypatch):
    repo = Mock()
    service = SituationService(repo=repo)
    repo.get.return_value = None
    with pytest.raises(Exception):
        service.get_situation(999)


def test_create_situation_topic_not_exists(monkeypatch):
    # Forces branch where provided topic_id is invalid -> set None
    repo = Mock()
    service = SituationService(repo=repo)
    # Patch TopicRepository.get to return None
    import app.services.situation_service as mod

    class FakeTopicRepo:
        def get(self, db, topic_id):
            return None

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(mod, "TopicRepository", lambda: FakeTopicRepo())

    # Create returns a situation-like object
    created = SimpleNamespace(
        id=10, topic_id=None, user_id=5, context="c", question="q", created_at=None
    )
    repo.create.return_value = created

    situation_in = SimpleNamespace(topic_id=999, context="c", question="q")
    out = service.create_situation(situation_in, user_id=5)
    assert out.id == 10


def test_update_delete_situation(monkeypatch):
    repo = Mock()
    service = SituationService(repo=repo)
    existing = SimpleNamespace(
        id=1, topic_id=2, user_id=3, context="c", question="q", created_at=None
    )
    repo.get.return_value = existing
    updated = SimpleNamespace(
        id=1, topic_id=2, user_id=3, context="c2", question="q", created_at=None
    )
    repo.update.return_value = updated

    out = service.update_situation(1, SimpleNamespace(context="c2"))
    assert out.context == "c2"

    # delete
    repo.get.return_value = existing
    out2 = service.delete_situation(1)
    assert out2["message"].lower().startswith("situation deleted")
