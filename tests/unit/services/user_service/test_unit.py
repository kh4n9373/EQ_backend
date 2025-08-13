from types import SimpleNamespace

import pytest

from app.core.exceptions import NotFoundError
from app.services.user_service import UserService


class DummyRepo:
    def __init__(self, users=None):
        self.users = users or []
        self.by_id = {u.id: u for u in self.users}
        self.updated = None
        self.refresh = None

    def list_users(self, db, search=None, page=1, size=10):
        return [
            u
            for u in self.users
            if (not search or (u.name and search.lower() in u.name.lower()))
        ]

    def search_users_by_name(self, db, query: str, limit: int = 10):
        return [u for u in self.users if u.name and query.lower() in u.name.lower()][
            :limit
        ]

    def get_user_by_id(self, db, user_id: int):
        return self.by_id.get(user_id)

    def get_user_by_email(self, db, email: str):
        for u in self.users:
            if getattr(u, "email", None) == email:
                return u
        return None

    def create_user(self, db, user_data: dict):
        u = SimpleNamespace(id=99, **user_data)
        return u

    def update_user(self, db, user, update_data: dict):
        self.updated = (user.id, update_data)
        return SimpleNamespace(**{**user.__dict__, **update_data})

    def update_user_refresh_token(self, db, user_id: int, refresh_token: str):
        self.refresh = (user_id, refresh_token)
        return True


def _u(i, name="U", email="u@example.com"):
    return SimpleNamespace(id=i, name=name, email=email, picture=None, bio=None)


def test_list_and_search_users(monkeypatch):
    users = [_u(1, "Alice"), _u(2, "Bob"), _u(3, "Charlie")]
    svc = UserService(user_repo=DummyRepo(users))

    lst = svc.list_users()
    assert len(lst) == 3

    srch = svc.search_users("bo")
    assert len(srch) == 1 and srch[0].name == "Bob"

    empty = svc.search_users("")
    assert empty == []


def test_get_profile_and_update_refresh_token(monkeypatch):
    users = [_u(1, "Alice"), _u(2, "Bob")]
    repo = DummyRepo(users)
    svc = UserService(user_repo=repo)

    prof = svc.get_user_profile(1)
    assert prof.name == "Alice"

    svc.update_user_refresh_token(1, "enc_ref")
    assert repo.refresh == (1, "enc_ref")


def test_update_user_and_not_found():
    users = [_u(1, "Alice")]
    repo = DummyRepo(users)
    svc = UserService(user_repo=repo)

    out = svc.update_user(1, {"name": "A1"})
    assert out.name == "A1"

    with pytest.raises(NotFoundError):
        svc.update_user(99, {"name": "X"})
