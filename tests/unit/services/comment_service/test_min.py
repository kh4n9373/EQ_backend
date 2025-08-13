from types import SimpleNamespace
from unittest.mock import Mock

from app.services.comment_service import CommentService


def test_update_comment_authorized(monkeypatch):
    repo = Mock()
    service = CommentService(repo=repo, sentiment_service=Mock())

    comment = SimpleNamespace(
        id=1, user_id=10, content="c1", situation_id=1, created_at=None, user=None
    )
    repo.get.return_value = comment
    updated = SimpleNamespace(
        id=1, user_id=10, content="c2", situation_id=1, created_at=None, user=None
    )
    repo.update.return_value = updated

    # CommentUpdate pydantic model expects attribute access; provide a tiny dummy with the attribute
    comment_data = SimpleNamespace(content="c2")
    out = service.update_comment(comment_id=1, comment_in=comment_data)
    assert out.content == "c2"


def test_update_comment_not_found(monkeypatch):
    repo = Mock()
    service = CommentService(repo=repo, sentiment_service=Mock())
    repo.get.return_value = None

    try:
        service.update_comment(1, SimpleNamespace(content="x"))
        assert False, "should raise"
    except Exception as exc:
        assert "not found" in str(exc).lower()
