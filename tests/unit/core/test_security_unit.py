import pytest
from fastapi import HTTPException
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decrypt_refresh_token,
    encrypt_refresh_token,
    get_current_user,
    get_current_user_optional,
)


class DummyRequest:
    def __init__(self, cookies=None, headers=None):
        self.cookies = cookies or {}
        self.headers = headers or {}


def test_create_access_token_and_decode():
    token = create_access_token({"sub": "u@example.com"})
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["sub"] == "u@example.com"
    assert "exp" in payload


def test_get_current_user_missing_token_raises():
    req = DummyRequest()
    with pytest.raises(HTTPException) as ex:
        get_current_user(req)  # type: ignore[arg-type]
    assert ex.value.status_code == 401


def test_get_current_user_optional_missing_returns_none():
    req = DummyRequest()
    assert get_current_user_optional(req) is None  # type: ignore[arg-type]


def test_refresh_token_encrypt_roundtrip():
    token = encrypt_refresh_token("refresh123")
    dec = decrypt_refresh_token(token)
    assert dec == "refresh123"
