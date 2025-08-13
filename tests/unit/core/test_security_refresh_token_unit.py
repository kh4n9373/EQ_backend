from types import SimpleNamespace

import pytest

from app.core.security import get_new_access_token


class FakeUserService:
    def __init__(self, has_token=True):
        enc = "enc_token" if has_token else None
        self._user = SimpleNamespace(id=1, encrypted_refresh_token=enc)
        self.cleared = False

    def get_user_by_id(self, user_id):
        return self._user if user_id == 1 else None

    def update_user(self, user_id, update_data):
        if update_data.get("encrypted_refresh_token") is None:
            self.cleared = True
        return True


class FakeOAuthClient:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def refresh_token(self, refresh_token):
        if self.should_fail:
            raise RuntimeError("expired")
        return {"access_token": "new_access"}


@pytest.mark.parametrize(
    "should_fail, expected_token, cleared",
    [
        (False, "new_access", False),
        (True, None, True),
    ],
)
def test_get_new_access_token_paths(monkeypatch, should_fail, expected_token, cleared):
    # Patch user service used inside security.get_new_access_token
    import app.core.security as sec

    usvc = FakeUserService(has_token=True)
    monkeypatch.setattr(sec, "UserService", lambda: usvc)

    # Patch oauth internals
    class FakeGoogle:
        def server_metadata(self):
            return {"token_endpoint": "http://example/token"}

        def _get_oauth_client(self, **kwargs):
            return FakeOAuthClient(should_fail=should_fail)

    fake_oauth = SimpleNamespace(google=FakeGoogle())
    monkeypatch.setattr(sec, "oauth", fake_oauth)

    token = get_new_access_token(1)
    assert token == expected_token
    assert usvc.cleared is cleared
