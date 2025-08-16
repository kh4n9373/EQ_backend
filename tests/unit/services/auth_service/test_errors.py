import asyncio

import pytest
from fastapi import HTTPException, Request

from app.services.auth_service import AuthService


class OAuthRaises:
    class google:
        @staticmethod
        async def authorize_access_token(request):
            raise RuntimeError("boom")


def test_auth_callback_oauth_raises_401(monkeypatch):
    from app.core import security as sec

    monkeypatch.setattr(sec, "oauth", OAuthRaises)
    svc = AuthService()

    class R(Request):
        scope = {"type": "http", "path": "/"}

    with pytest.raises(HTTPException) as ei:
        asyncio.get_event_loop().run_until_complete(svc.auth_callback(R()))
    assert ei.value.status_code == 401


class OAuthOK:
    class google:
        @staticmethod
        async def authorize_access_token(request):
            return {
                "userinfo": {
                    "sub": "gid",
                    "email": "u@example.com",
                    "name": "U",
                    "picture": "p",
                }
            }


def test_auth_callback_user_service_exception_to_500(monkeypatch):
    from app.core import security as sec

    monkeypatch.setattr(sec, "oauth", OAuthOK)

    class BadUserService:
        def get_user_by_email(self, email):
            return None

        def create_user(self, data):
            raise RuntimeError("db fail")

    svc = AuthService(user_service=BadUserService())

    class R(Request):
        scope = {"type": "http", "path": "/"}

    with pytest.raises(HTTPException) as ei:
        asyncio.get_event_loop().run_until_complete(svc.auth_callback(R()))
    assert ei.value.status_code == 500
