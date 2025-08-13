from types import SimpleNamespace

import pytest

from app.services.user_service import UserService


class Repo:
    def __init__(self):
        self.users = [
            SimpleNamespace(id=1, name="AA", email="aa@x", picture=None, bio=None),
            SimpleNamespace(id=2, name="BB", email="bb@x", picture=None, bio=None),
        ]

    def list_users(self, db, search=None, page=1, size=10):
        return self.users

    def get_user_by_id(self, db, user_id):
        return next((u for u in self.users if u.id == user_id), None)

    def get_user_by_email(self, db, email):
        return next((u for u in self.users if u.email == email), None)


def test_list_users_none_search_and_pagination_defaults():
    svc = UserService(user_repo=Repo())
    res = svc.list_users()
    assert len(res) == 2


def test_get_user_by_email_not_found_returns_none():
    svc = UserService(user_repo=Repo())
    assert svc.get_user_by_email("no@no") is None


def test_get_user_profile_found_to_schema():
    svc = UserService(user_repo=Repo())
    prof = svc.get_user_profile(1)
    assert prof.id == 1 and prof.email == "aa@x"
