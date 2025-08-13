import pytest
from fastapi import Request, Response

from app.services.auth_service import AuthService


class DummyOAuth:
    class google:
        @staticmethod
        async def authorize_redirect(request, redirect_uri):
            # return a simple string to assert path executed
            return f"redirect:{redirect_uri}"

        @staticmethod
        async def authorize_access_token(request):
            return {
                "userinfo": {
                    "sub": "gid",
                    "email": "u@example.com",
                    "name": "U",
                    "picture": "p",
                },
                "refresh_token": "r",
            }


class DummyUser:
    def __init__(self, id=1, email="u@example.com", name="U", picture="p"):
        self.id = id
        self.email = email
        self.name = name
        self.picture = picture


class DummyUserService:
    def __init__(self):
        self.updated = False
        self.created = False
        self.refresh_updated = False

    def get_user_by_email(self, email):
        return None

    def create_user(self, data):
        self.created = True
        return DummyUser(id=1)

    def update_user(self, user_id, update_data):
        self.updated = True

    def update_user_refresh_token(self, user_id, token):
        self.refresh_updated = True


def test_login_google_redirect(monkeypatch):
    from app.core import security as sec

    monkeypatch.setattr(sec, "oauth", DummyOAuth)
    svc = AuthService(user_service=DummyUserService())

    class R(Request):
        scope = {"type": "http", "path": "/"}

    r = (
        pytest.run_in_loop(svc.login_google(R()))
        if hasattr(pytest, "run_in_loop")
        else (
            __import__("asyncio")
            .get_event_loop()
            .run_until_complete(svc.login_google(R()))
        )
    )
    assert isinstance(r, str) and r.startswith("redirect:")


def test_auth_callback_creates_user_and_sets_cookie(monkeypatch):
    from app.core import security as sec

    monkeypatch.setattr(sec, "oauth", DummyOAuth)
    # use a real token creator
    svc = AuthService(user_service=DummyUserService())

    class R(Request):
        scope = {"type": "http", "path": "/"}

    resp = (
        __import__("asyncio")
        .get_event_loop()
        .run_until_complete(svc.auth_callback(R()))
    )
    assert resp.status_code in (302, 307)
    # cookie should be set
    set_cookie_headers = [h for h in resp.raw_headers if h[0].lower() == b"set-cookie"]
    assert any(b"access_token=" in v for _, v in set_cookie_headers)


def test_logout_deletes_cookie():
    svc = AuthService(user_service=DummyUserService())
    response = Response()
    svc.logout(response)
    # starlette stores deleted cookies in headers
    cookies = dict(response.raw_headers)
    assert any(h.lower() == b"set-cookie" for h, _ in response.raw_headers)
