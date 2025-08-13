from types import SimpleNamespace

from app.services.user_service import UserService


class Repo:
    def __init__(self):
        self.u = SimpleNamespace(id=1, name="A", email="a@x", picture="p", bio=None)
        self.updated = None

    def get_user_by_id(self, db, user_id):
        return self.u if user_id == 1 else None

    def update_user(self, db, user, update_data):
        self.updated = update_data
        for k, v in update_data.items():
            setattr(user, k, v)
        return user

    def update_user_refresh_token(self, db, user_id, refresh_token):
        return True

    def create_user(self, db, user_data):
        return SimpleNamespace(id=2, **user_data)


def test_update_user_nominal():
    svc = UserService(user_repo=Repo())
    res = svc.update_user(1, {"name": "X"})
    assert res.name == "X"


def test_update_user_refresh_token():
    svc = UserService(user_repo=Repo())
    assert svc.update_user_refresh_token(1, "token") is True


def test_create_user_nominal():
    svc = UserService(user_repo=Repo())
    u = svc.create_user({"name": "B", "email": "b@x", "picture": "p", "bio": ""})
    assert u.id == 2
