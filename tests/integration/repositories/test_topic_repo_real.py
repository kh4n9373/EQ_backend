import pytest

from app.repositories.topic_repository import TopicRepository


@pytest.mark.integration
def test_topic_crud_flow(db_session):
    repo = TopicRepository()
    t = repo.create(db_session, {"name": "A", "description": "B"})
    assert t.id and t.name == "A"
    t2 = repo.get(db_session, t.id)
    assert t2.id == t.id
    all_topics = repo.get_multi(db_session)
    assert any(x.id == t.id for x in all_topics)
    t = repo.update(db_session, t, {"name": "A2"})
    assert t.name == "A2"
    deleted = repo.delete(db_session, t.id)
    assert deleted is not None
    assert repo.get(db_session, t.id) is None
