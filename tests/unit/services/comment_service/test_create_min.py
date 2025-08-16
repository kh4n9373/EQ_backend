from types import SimpleNamespace
from unittest.mock import Mock

from app.services.comment_service import CommentService


def test_create_comment_with_sentiment_success(monkeypatch):
    repo = Mock()
    senti = Mock()
    service = CommentService(repo=repo, sentiment_service=senti)
    senti.analyze_sentiment.return_value = {"sentiment": "pos"}

    created = SimpleNamespace(
        id=1,
        content="c",
        situation_id=2,
        user_id=3,
        created_at=None,
        user=None,
        sentiment_analysis={"sentiment": "pos"},
    )
    repo.create_with_sentiment.return_value = created

    comment_in = SimpleNamespace(content="c", situation_id=2)
    out = service.create_comment(comment_in, user_id=3)
    assert out.id == 1
    assert out.sentiment_analysis == {"sentiment": "pos"}


def test_create_comment_sentiment_fallback(monkeypatch):
    repo = Mock()
    senti = Mock()
    service = CommentService(repo=repo, sentiment_service=senti)
    # make analyze_sentiment raise, so fallback branch runs
    senti.analyze_sentiment.side_effect = RuntimeError("model down")
    created = SimpleNamespace(
        id=2, content="c2", situation_id=4, user_id=5, created_at=None, user=None
    )
    repo.create_with_sentiment.return_value = created

    comment_in = SimpleNamespace(content="c2", situation_id=4)
    out = service.create_comment(comment_in, user_id=5)
    assert out.id == 2
