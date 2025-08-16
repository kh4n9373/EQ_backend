from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services.topic_service import TopicService


def make_topic(id=1, name="T"):
    return SimpleNamespace(id=id, name=name, description=None, created_at=None)


def test_list_topics_maps_schema():
    repo = Mock()
    repo.get_multi.return_value = [make_topic(1, "A"), make_topic(2, "B")]
    service = TopicService(repo=repo)
    out = service.list_topics()
    assert [t.name for t in out] == ["A", "B"]


def test_get_topic_found():
    repo = Mock()
    repo.get.return_value = make_topic(3, "C")
    service = TopicService(repo=repo)
    out = service.get_topic(3)
    assert out.id == 3 and out.name == "C"


def test_get_topic_not_found():
    repo = Mock()
    repo.get.return_value = None
    service = TopicService(repo=repo)
    with pytest.raises(Exception):
        service.get_topic(999)


def test_create_update_delete_topic():
    repo = Mock()
    created = make_topic(10, "X")
    repo.create.return_value = created
    repo.get.return_value = created
    repo.update.return_value = created
    service = TopicService(repo=repo)
    out = service.create_topic(SimpleNamespace(name="X"))
    assert out.id == 10
    out2 = service.update_topic(10, SimpleNamespace(name="X2"))
    assert out2.id == 10
    repo.get.return_value = created
    out3 = service.delete_topic(10)
    assert out3["message"].lower().startswith("topic deleted")
