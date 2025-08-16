from types import SimpleNamespace

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.comments import CommentCreate, CommentUpdate
from app.services.comment_service import CommentService


class DummyRepo:
    def __init__(self, items=None):
        self.items = items or []
        self.deleted = None

    def get_by_situation(self, db, situation_id):
        return self.items

    def create_with_sentiment(self, db, data, user_id, sentiment=None):
        return SimpleNamespace(
            id=1,
            content=data["content"],
            situation_id=data["situation_id"],
            user_id=user_id,
            created_at=None,
            sentiment_analysis=sentiment,
        )

    def get(self, db, cid):
        if cid == 1:
            return SimpleNamespace(
                id=1, content="c", situation_id=1, user_id=1, created_at=None
            )
        return None

    def update(self, db, obj, update_in):
        payload = update_in.dict() if hasattr(update_in, "dict") else update_in
        return SimpleNamespace(
            id=obj.id,
            content=payload.get("content", obj.content),
            situation_id=1,
            user_id=1,
            created_at=None,
        )

    def delete(self, db, cid):
        self.deleted = cid
        return True


class DummySentiment:
    def __init__(self, boom=False):
        self.boom = boom

    def analyze_sentiment(self, text):
        if self.boom:
            raise RuntimeError("fail")
        return {"sentiment": "positive", "score": 0.2}


def test_get_comments_by_situation_maps_list():
    svc = CommentService(
        repo=DummyRepo(
            items=[
                SimpleNamespace(
                    id=1, content="c", situation_id=1, user_id=1, created_at=None
                )
            ]
        ),
        sentiment_service=DummySentiment(),
    )
    out = svc.get_comments_by_situation(1)
    assert len(out) == 1 and out[0].id == 1


def test_create_comment_with_sentiment_and_fallback():
    svc_ok = CommentService(repo=DummyRepo(), sentiment_service=DummySentiment())
    out_ok = svc_ok.create_comment(
        CommentCreate(situation_id=1, content="c"), user_id=10
    )
    assert out_ok.id == 1 and out_ok.sentiment_analysis

    svc_fb = CommentService(
        repo=DummyRepo(), sentiment_service=DummySentiment(boom=True)
    )
    out_fb = svc_fb.create_comment(
        CommentCreate(situation_id=1, content="c"), user_id=10
    )
    assert out_fb.id == 1  # fallback path still creates


def test_get_update_delete_comment_and_not_found():
    svc = CommentService(repo=DummyRepo(), sentiment_service=DummySentiment())
    # get ok
    got = svc.get_comment(1)
    assert got.id == 1
    # update ok
    upd = svc.update_comment(1, CommentUpdate(content="x"))
    assert upd.content == "x"
    # delete ok
    res = svc.delete_comment(1)
    assert res["message"].startswith("Comment deleted")
    # not found branches
    with pytest.raises(NotFoundError):
        svc.get_comment(999)
    with pytest.raises(NotFoundError):
        svc.update_comment(999, CommentUpdate(content="x"))
    with pytest.raises(NotFoundError):
        svc.delete_comment(999)
