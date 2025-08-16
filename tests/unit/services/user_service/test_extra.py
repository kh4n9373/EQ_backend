from types import SimpleNamespace

from app.services.user_service import UserService


class DummyRepo:
    def __init__(self):
        self.users = [
            SimpleNamespace(id=1, name="A", email="a@x", picture="p1", bio=None),
            SimpleNamespace(id=2, name="B", email="b@x", picture="p2", bio="bio"),
        ]

    # list with pagination and optional search
    def list_users(self, db, search=None, page=1, size=10):
        data = self.users
        if search:
            data = [u for u in data if search.lower() in u.name.lower()]
        start = (page - 1) * size
        end = start + size
        return data[start:end]

    def search_users_by_name(self, db, query, limit=10):
        return [u for u in self.users if query.lower() in u.name.lower()][:limit]

    def get_user_by_id(self, db, user_id):
        return next((u for u in self.users if u.id == user_id), None)

    def get_user_by_email(self, db, email):
        return next((u for u in self.users if u.email == email), None)

    def create_user(self, db, user_data):
        u = SimpleNamespace(id=3, **user_data)
        self.users.append(u)
        return u

    def update_user(self, db, user, update_data):
        for k, v in update_data.items():
            setattr(user, k, v)
        return user

    def update_user_refresh_token(self, db, user_id, refresh_token):
        return True


def test_list_users_pagination_and_search(monkeypatch):
    svc = UserService(user_repo=DummyRepo())
    page1 = svc.list_users(page=1, size=1)
    assert len(page1) == 1
    searched = svc.list_users(search="B")
    assert any(u.name == "B" for u in searched)


def test_get_user_profile_not_found(monkeypatch):
    svc = UserService(user_repo=DummyRepo())
    try:
        svc.get_user_profile(999)
        assert False, "should raise"
    except Exception as e:
        assert "User" in str(e)


def test_get_user_by_email_found():
    svc = UserService(user_repo=DummyRepo())
    assert svc.get_user_by_email("a@x").email == "a@x"
