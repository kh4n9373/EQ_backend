from types import SimpleNamespace

import pytest

import app.api.v1.deps as deps


def test_get_redis_ping_ok(monkeypatch):
    class FakeClient:
        def ping(self):
            return True

    class FakeRedisModule:
        class Redis:
            @staticmethod
            def from_url(url, decode_responses):
                return FakeClient()

    monkeypatch.setattr(deps, "redis", FakeRedisModule)
    monkeypatch.setattr(deps, "_redis_client", None)
    client = deps._get_redis()
    assert client is not None


def test_current_user_with_touch_no_id_no_setex(monkeypatch):
    # Fake get_current_user returns object without id
    monkeypatch.setattr(
        deps, "get_current_user", lambda req: {"email": "u@example.com"}
    )
    called = {"setex": 0}

    class FakeClient:
        def setex(self, *a, **k):
            called["setex"] += 1

    monkeypatch.setattr(deps, "_get_redis", lambda: FakeClient())

    req = SimpleNamespace(headers={}, cookies={})
    out = deps._get_current_user_with_touch(req)
    assert called["setex"] == 0


def test_get_redis_none_when_redis_not_installed(monkeypatch):
    monkeypatch.setattr(deps, "redis", None)
    monkeypatch.setattr(deps, "_redis_client", None, raising=False)
    assert deps._get_redis() is None


def test_get_redis_cache_hit(monkeypatch):
    fake_client = object()

    # have a redis module present to not short-circuit
    class FakeRedisModule:
        class Redis:
            @staticmethod
            def from_url(*a, **k):
                return fake_client

    monkeypatch.setattr(deps, "redis", FakeRedisModule)
    monkeypatch.setattr(deps, "_redis_client", fake_client, raising=False)
    assert deps._get_redis() is fake_client


def test_get_redis_connect_fail(monkeypatch):
    class FakeRedisModule:
        class Redis:
            @staticmethod
            def from_url(*args, **kwargs):
                class C:
                    def ping(self):
                        raise RuntimeError("boom")

                return C()

    monkeypatch.setattr(deps, "redis", FakeRedisModule)
    monkeypatch.setattr(deps, "_redis_client", None, raising=False)
    assert deps._get_redis() is None


def test_current_user_with_touch_setex_error(monkeypatch):
    monkeypatch.setattr(deps, "get_current_user", lambda req: {"id": 123})

    class Client:
        def setex(self, *a, **k):
            raise RuntimeError("redis down")

    monkeypatch.setattr(deps, "_get_redis", lambda: Client())
    req = SimpleNamespace(headers={}, cookies={})
    assert deps._get_current_user_with_touch(req) == {"id": 123}
