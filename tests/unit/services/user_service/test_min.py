from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services.user_service import UserService


def make_user(id=1, name="N", email="e@x.com", picture=None, bio=None):
    return SimpleNamespace(id=id, name=name, email=email, picture=picture, bio=bio)


def test_list_users_maps_to_short_schema():
    repo = Mock()
    repo.list_users.return_value = [make_user(1, "A"), make_user(2, "B")]
    service = UserService(user_repo=repo)
    out = service.list_users(search="A", page=1, size=10)
    assert [u.name for u in out] == ["A", "B"]


def test_search_users_min_length_guard():
    service = UserService(user_repo=Mock())
    assert service.search_users("") == []
    assert service.search_users("a") == []


def test_search_users_happy():
    repo = Mock()
    repo.search_users_by_name.return_value = [make_user(3, "C")]
    service = UserService(user_repo=repo)
    out = service.search_users("Ce")
    assert out[0].name == "C"


def test_get_user_profile_found():
    repo = Mock()
    repo.get_user_by_id.return_value = make_user(5, "X", "x@x.com")
    service = UserService(user_repo=repo)
    out = service.get_user_profile(5)
    assert out.id == 5 and out.email == "x@x.com"


def test_get_user_profile_not_found():
    repo = Mock()
    repo.get_user_by_id.return_value = None
    service = UserService(user_repo=repo)
    with pytest.raises(Exception):
        service.get_user_profile(999)


def test_create_update_refresh_token():
    repo = Mock()
    created = make_user(7, "Y", "y@x.com")
    repo.create_user.return_value = created
    repo.get_user_by_id.return_value = created
    repo.update_user.return_value = created
    repo.update_user_refresh_token.return_value = created
    service = UserService(user_repo=repo)
    u = service.create_user({"email": "y@x.com"})
    assert u.id == 7
    u2 = service.update_user(7, {"name": "Y2"})
    assert u2.id == 7
    u3 = service.update_user_refresh_token(7, "rt")
    assert u3.id == 7
