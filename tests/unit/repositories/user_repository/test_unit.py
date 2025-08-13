import uuid

import pytest
from sqlalchemy.orm import Session

from app.models import User
from app.repositories.user_repository import UserRepository


@pytest.fixture()
def repo():
    return UserRepository()


def _unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def test_create_and_get_user(db_session: Session, repo: UserRepository):
    email = _unique_email()
    user = repo.create_user(db_session, {"email": email, "name": "U"})
    assert user.id is not None

    fetched = repo.get_user_by_email(db_session, email)
    assert fetched is not None and fetched.id == user.id


def test_get_user_not_found(db_session: Session, repo: UserRepository):
    user = repo.get_user_by_email(db_session, "notfound@example.com")
    assert user is None


def test_unique_email_constraint(db_session: Session, repo: UserRepository):
    email = _unique_email()
    repo.create_user(db_session, {"email": email, "name": "A"})
    # Second insert with same email should raise or be handled upstream.
    with pytest.raises(Exception):
        repo.create_user(db_session, {"email": email, "name": "B"})
