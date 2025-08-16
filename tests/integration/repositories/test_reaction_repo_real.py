import pytest

from app.repositories.reaction_repository import ReactionRepository


@pytest.mark.integration
def test_reaction_crud_and_queries(db_session, test_user, test_situation):
    repo = ReactionRepository()
    r = repo.create_reaction(
        db_session,
        {
            "reaction_type": "like",
            "situation_id": test_situation.id,
            "user_id": test_user.id,
        },
    )
    assert r.id
    assert repo.get_by_id(db_session, r.id).id == r.id
    assert (
        repo.get_by_user_and_situation(db_session, test_user.id, test_situation.id).id
        == r.id
    )
    assert any(
        x.id == r.id for x in repo.get_by_situation(db_session, test_situation.id)
    )
    assert repo.count_by_situation(db_session, test_situation.id) >= 1
    deleted = repo.delete_reaction(db_session, r)
    assert deleted is True
