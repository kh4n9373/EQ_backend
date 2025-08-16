import pytest

from app.repositories.situation_repository import SituationRepository


@pytest.mark.integration
def test_situation_crud_and_counts(db_session, test_user, test_topic):
    repo = SituationRepository()
    s = repo.create(
        db_session,
        {
            "context": "ctx",
            "question": "q",
            "topic_id": test_topic.id,
            "user_id": test_user.id,
            "is_contributed": True,
        },
    )
    assert s.id
    assert repo.get(db_session, s.id).id == s.id
    by_topic = repo.get_by_topic(db_session, test_topic.id)
    assert any(x.id == s.id for x in by_topic)
    contrib = repo.get_contributed_situations(db_session)
    assert any(x.id == s.id for x in contrib)
    by_user = repo.get_by_user(db_session, test_user.id)
    assert any(x.id == s.id for x in by_user)
    s = repo.update(db_session, s, {"context": "ctx2"})
    assert s.context == "ctx2"
    deleted = repo.delete(db_session, s.id)
    assert deleted is not None
    assert repo.get(db_session, s.id) is None
