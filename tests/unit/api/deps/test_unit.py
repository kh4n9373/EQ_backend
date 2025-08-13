import types

import pytest
from fastapi import Request

import app.api.v1.deps as deps


class DummyRequest:
    def __init__(self, headers=None, cookies=None):
        self.headers = headers or {}
        self.cookies = cookies or {}


def test_get_redis_returns_none_when_module_missing(monkeypatch):
    # Simulate redis import is None
    monkeypatch.setattr(deps, "redis", None)
    # Reset cached client
    monkeypatch.setattr(deps, "_redis_client", None)
    assert deps._get_redis() is None


def test_get_redis_reuse_cached_client(monkeypatch):
    class FakeClient:
        def ping(self):
            return True

    # Inject a cached client
    monkeypatch.setattr(deps, "_redis_client", FakeClient())
    assert deps._get_redis().__class__ is FakeClient


def test_get_redis_connect_failure(monkeypatch):
    class FakeRedisModule:
        class Redis:
            @staticmethod
            def from_url(url, decode_responses):
                raise RuntimeError("cannot connect")

    monkeypatch.setattr(deps, "redis", FakeRedisModule)
    # Clear cache first
    monkeypatch.setattr(deps, "_redis_client", None)

    assert deps._get_redis() is None


def test_get_current_user_with_touch_no_token(monkeypatch):
    # Ensure _get_redis returns None (no touch)
    monkeypatch.setattr(deps, "_get_redis", lambda: None)

    req = DummyRequest()
    with pytest.raises(Exception):
        # get_current_user raises HTTPException when missing token
        deps._get_current_user_with_touch(req)


def test_get_current_user_with_touch_sets_key(monkeypatch):
    # Fake underlying get_current_user to return a user
    def fake_get_current_user(request: Request):  # type: ignore[override]
        return {"id": 123, "email": "u@example.com"}

    # Fake redis client to capture setex
    calls = {}

    class FakeClient:
        def setex(self, key, ttl, value):
            calls[(key, ttl, value)] = True

    monkeypatch.setattr(deps, "_get_redis", lambda: FakeClient())
    monkeypatch.setattr(deps, "get_current_user", fake_get_current_user)

    req = DummyRequest(headers={"Authorization": "Bearer token"})
    user = deps._get_current_user_with_touch(req)
    assert user["id"] == 123
    assert any(k[0].startswith("active_user:") for k in calls.keys())
