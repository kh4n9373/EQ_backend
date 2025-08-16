from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Request, Response

from app.core.config import settings
from app.services.auth_service import AuthService


class FakeOAuthGoogle:
    async def authorize_redirect(self, request, redirect_uri):
        return {"redirect_to": str(redirect_uri)}

    async def authorize_access_token(self, request):
        return {
            "userinfo": {
                "sub": "gid",
                "email": "u@example.com",
                "name": "U",
                "picture": "",
            },
            "refresh_token": "r",
        }


class FakeUserService:
    def __init__(self, exists=False):
        self._exists = exists
        self.created = None
        self.updated_refresh = None

    def get_user_by_email(self, email):
        return SimpleNamespace(id=1, name="U", picture="") if self._exists else None

    def update_user(self, user_id, update_data):
        return True

    def create_user(self, data):
        self.created = SimpleNamespace(id=2)
        return self.created

    def update_user_refresh_token(self, user_id, token):
        self.updated_refresh = (user_id, token)
        return True


@pytest.mark.asyncio
async def test_login_google_redirect(monkeypatch):
    svc = AuthService(user_service=FakeUserService())
    from app.core import security

    monkeypatch.setattr(security, "oauth", SimpleNamespace(google=FakeOAuthGoogle()))
    req = Request({"type": "http", "path": "/login/google"})
    # Inject url_for
    req.url_for = lambda name: "/callback/google"
    out = await svc.login_google(req)
    assert out["redirect_to"].endswith("/callback/google")


@pytest.mark.asyncio
async def test_auth_callback_success_creates_user(monkeypatch):
    fake_user_service = FakeUserService(exists=False)
    svc = AuthService(user_service=fake_user_service)
    from app.core import security

    monkeypatch.setattr(security, "oauth", SimpleNamespace(google=FakeOAuthGoogle()))
    req = Request({"type": "http", "path": "/callback/google"})
    result = await svc.auth_callback(req)
    # Should return a RedirectResponse to frontend
    assert hasattr(result, "status_code") and 300 <= result.status_code < 400


@pytest.mark.asyncio
async def test_auth_callback_missing_userinfo_401(monkeypatch):
    class NoInfoOAuth(FakeOAuthGoogle):
        async def authorize_access_token(self, request):
            return {}

    svc = AuthService(user_service=FakeUserService())
    from app.core import security

    monkeypatch.setattr(security, "oauth", SimpleNamespace(google=NoInfoOAuth()))
    req = Request({"type": "http", "path": "/callback/google"})
    with pytest.raises(HTTPException) as ex:
        await svc.auth_callback(req)
    assert ex.value.status_code == 401


def test_logout_deletes_cookie():
    svc = AuthService(user_service=FakeUserService())
    resp = Response()
    out = svc.logout(resp)
    assert out["message"] == "Logged out"
