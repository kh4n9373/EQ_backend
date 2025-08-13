import asyncio

import pytest
from fastapi import HTTPException, Request

from app.services.auth_service import AuthService


class OAuthExisting:
    class google:
        @staticmethod
        async def authorize_access_token(request):
            return {
                "userinfo": {
                    "sub": "gid",
                    "email": "exists@example.com",
                    "name": "New Name",
                    "picture": "newpic",
                },
                "refresh_token": "r2",
            }


class DummyExistingUser:
    def __init__(self):
        self.id = 42
        self.email = "exists@example.com"
        self.name = "Old Name"
        self.picture = "oldpic"


class UserSvcExisting:
    def __init__(self):
        self.updated_args = None
        self.refresh_updated_id = None

    def get_user_by_email(self, email):
        return DummyExistingUser()

    def update_user(self, user_id, update_data):
        self.updated_args = (user_id, update_data)

    def update_user_refresh_token(self, user_id, token):
        self.refresh_updated_id = user_id


def test_auth_callback_updates_existing_and_refresh(monkeypatch):
    from app.core import security as sec

    monkeypatch.setattr(sec, "oauth", OAuthExisting)
    us = UserSvcExisting()
    svc = AuthService(user_service=us)

    class R(Request):
        scope = {"type": "http", "path": "/"}

    resp = asyncio.get_event_loop().run_until_complete(svc.auth_callback(R()))
    assert resp.status_code in (302, 307)
    assert us.updated_args is not None
    uid, data = us.updated_args
    assert uid == 42
    assert data.get("name") == "New Name"
    assert data.get("picture") == "newpic"
    assert us.refresh_updated_id == 42


class OAuthNoUserinfo:
    class google:
        @staticmethod
        async def authorize_access_token(request):
            return {"access_token": "x"}  # no userinfo


def test_auth_callback_missing_userinfo_raises_401(monkeypatch):
    from app.core import security as sec

    monkeypatch.setattr(sec, "oauth", OAuthNoUserinfo)
    svc = AuthService(user_service=UserSvcExisting())

    class R(Request):
        scope = {"type": "http", "path": "/"}

    with pytest.raises(HTTPException) as ei:
        asyncio.get_event_loop().run_until_complete(svc.auth_callback(R()))
    assert ei.value.status_code == 401
