from types import SimpleNamespace

import pytest

from app.services.reaction_service import ReactionService


class DummyRepo:
    def __init__(self, existing=None, items=None):
        self._existing = existing
        self._items = items or []
        self.updated = None
        self.created = None
        self.deleted = None

    def get_by_situation(self, db, situation_id):
        return self._items

    def get_by_user_and_situation(self, db, user_id, situation_id):
        return self._existing

    def update_reaction(self, db, rid, rtype):
        self.updated = (rid, rtype)
        return SimpleNamespace(
            id=rid, situation_id=1, user_id=1, reaction_type=rtype, created_at=None
        )

    def create(self, db, data):
        self.created = data
        return SimpleNamespace(id=2, created_at=None, **data)

    def delete(self, db, rid):
        self.deleted = rid
        return True


def test_get_reactions_by_situation_maps_list(monkeypatch):
    svc = ReactionService()
    monkeypatch.setattr(
        svc,
        "repo",
        DummyRepo(
            items=[
                SimpleNamespace(
                    id=1,
                    situation_id=1,
                    user_id=1,
                    reaction_type="like",
                    created_at=None,
                )
            ]
        ),
    )
    out = svc.get_reactions_by_situation(1)
    assert len(out) == 1 and out[0].reaction_type == "like"


def test_create_reaction_updates_existing(monkeypatch):
    svc = ReactionService()
    existing = SimpleNamespace(
        id=10, situation_id=1, user_id=1, reaction_type="like", created_at=None
    )
    repo = DummyRepo(existing=existing)
    monkeypatch.setattr(svc, "repo", repo)
    out = svc.create_reaction(1, "dislike", 1)
    assert repo.updated == (10, "dislike")
    assert out.reaction_type == "dislike"


def test_create_reaction_creates_new(monkeypatch):
    svc = ReactionService()
    repo = DummyRepo(existing=None)
    monkeypatch.setattr(svc, "repo", repo)
    out = svc.create_reaction(1, "upvote", 1)
    assert repo.created == {"situation_id": 1, "user_id": 1, "reaction_type": "upvote"}
    assert out.reaction_type == "upvote"


def test_delete_reaction_when_match(monkeypatch):
    svc = ReactionService()
    repo = DummyRepo(
        existing=SimpleNamespace(id=5, situation_id=1, user_id=1, reaction_type="like")
    )
    monkeypatch.setattr(svc, "repo", repo)
    svc.delete_reaction(1, "like", 1)
    assert repo.deleted == 5
