from types import SimpleNamespace

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.topics import TopicCreate, TopicUpdate
from app.services.topic_service import TopicService


class DummyRepo:
    def __init__(self, items=None, get_map=None):
        self.items = items or []
        self.get_map = get_map or {}
        self.updated = None
        self.deleted = None

    def get_multi(self, db):
        return self.items

    def get(self, db, tid):
        return self.get_map.get(tid)

    def create(self, db, data):
        return SimpleNamespace(id=3, name=data.name)

    def update(self, db, obj, upd):
        self.updated = upd
        return SimpleNamespace(id=obj.id, name=upd.name)

    def delete(self, db, tid):
        self.deleted = tid
        return True


def test_list_get_create_update_delete_topic(monkeypatch):
    repo = DummyRepo(
        items=[SimpleNamespace(id=1, name="A"), SimpleNamespace(id=2, name="B")],
        get_map={1: SimpleNamespace(id=1, name="A")},
    )
    svc = TopicService(repo=repo)

    lst = svc.list_topics()
    assert [x.name for x in lst] == ["A", "B"]

    got = svc.get_topic(1)
    assert got.id == 1

    created = svc.create_topic(TopicCreate(name="C"))
    assert created.id == 3 and created.name == "C"

    updated = svc.update_topic(1, TopicUpdate(name="A1"))
    assert updated.name == "A1"

    deleted = svc.delete_topic(1)
    assert repo.deleted == 1


def test_topic_not_found(monkeypatch):
    svc = TopicService(repo=DummyRepo(get_map={}))
    with pytest.raises(NotFoundError):
        svc.get_topic(99)
    with pytest.raises(NotFoundError):
        svc.update_topic(99, TopicUpdate(name="X"))
    with pytest.raises(NotFoundError):
        svc.delete_topic(99)
