from datetime import datetime, timedelta

import pytest

from app.repositories.user_repository import UserRepository


@pytest.mark.integration
def test_user_crud_and_queries(db_session):
    repo = UserRepository()
    u = repo.create(
        db_session, {"email": "int@ex.com", "name": "Int", "google_id": "g1"}
    )
    assert u.id
    assert repo.get_user_by_email(db_session, "int@ex.com").id == u.id
    assert repo.get_user_by_google_id(db_session, "g1").id == u.id
    u = repo.update(db_session, u, {"name": "Int2"})
    assert u.name == "Int2"
    u = repo.update_user_refresh_token(db_session, u.id, "enc_rt")
    assert u.encrypted_refresh_token == "enc_rt"
    users = repo.list_users(db_session, search="Int", page=1, size=10)
    assert any(x.id == u.id for x in users)
    users2 = repo.search_users_by_name(db_session, "Int")
    assert any(x.id == u.id for x in users2)
    users3 = repo.get_users_by_date_range(
        db_session,
        datetime.utcnow() - timedelta(days=1),
        datetime.utcnow() + timedelta(days=1),
    )
    assert any(x.id == u.id for x in users3)
    deleted = repo.delete(db_session, u.id)
    assert deleted is not None
    assert repo.get(db_session, u.id) is None
