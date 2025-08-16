from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.core.config import settings
from app.core.security import get_current_user


class DummyRequest:
    def __init__(self, cookies=None, headers=None):
        self.cookies = cookies or {}
        self.headers = headers or {}


def _make_token(sub: str, secret: str, exp_delta_seconds: int):
    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=exp_delta_seconds)
    payload = {"sub": sub, "exp": exp}
    return jwt.encode(payload, secret, algorithm=settings.algorithm)


def test_get_current_user_expired_token_raises():
    token = _make_token("u@example.com", settings.secret_key, exp_delta_seconds=-10)
    req = DummyRequest(cookies={"access_token": token})
    with pytest.raises(HTTPException) as ex:
        get_current_user(req)  # type: ignore[arg-type]
    assert ex.value.status_code == 401


def test_get_current_user_invalid_signature_raises():
    token = _make_token("u@example.com", "wrong-secret", exp_delta_seconds=3600)
    req = DummyRequest(cookies={"access_token": token})
    with pytest.raises(HTTPException) as ex:
        get_current_user(req)  # type: ignore[arg-type]
    assert ex.value.status_code == 401
