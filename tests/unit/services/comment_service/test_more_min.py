from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services.comment_service import CommentService


def make_user(id=1, email="e@x.com", name="U", picture=None):
    return SimpleNamespace(id=id, email=email, name=name, picture=picture)


def test_get_comment_success_maps_user():
    repo = Mock()
    service = CommentService(repo=repo, sentiment_service=Mock())
    comment = SimpleNamespace(
        id=1, content="c", situation_id=2, user_id=3, created_at=None, user=make_user()
    )
    repo.get.return_value = comment
    out = service.get_comment(1)
    assert out.id == 1
    assert out.user["email"] == "e@x.com"


def test_get_comment_not_found():
    repo = Mock()
    service = CommentService(repo=repo, sentiment_service=Mock())
    repo.get.return_value = None
    with pytest.raises(Exception):
        service.get_comment(999)


def test_delete_comment_not_found():
    repo = Mock()
    service = CommentService(repo=repo, sentiment_service=Mock())
    repo.get.return_value = None
    with pytest.raises(Exception):
        service.delete_comment(1)


def test_get_comments_by_situation_maps_list():
    repo = Mock()
    service = CommentService(repo=repo, sentiment_service=Mock())
    c1 = SimpleNamespace(
        id=1, content="a", situation_id=2, user_id=3, created_at=None, user=None
    )
    c2 = {
        "id": 2,
        "content": "b",
        "situation_id": 2,
        "user_id": 3,
        "created_at": None,
        "user": None,
    }
    repo.get_by_situation.return_value = [c1, c2]
    out = service.get_comments_by_situation(2)
    assert [x.id for x in out] == [1, 2]
