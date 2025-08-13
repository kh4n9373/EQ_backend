import pytest
from sqlalchemy.orm import Session

from app.models import Topic
from app.repositories.base import BaseRepository


def test_base_repository_crud_topic(db_session: Session):
    repo = BaseRepository(Topic)

    # create
    t = repo.create(db_session, {"name": "BaseRepoTopic"})
    assert t.id is not None and t.name == "BaseRepoTopic"

    # get
    g = repo.get(db_session, t.id)
    assert g is not None and g.id == t.id

    # get_multi
    lst = repo.get_multi(db_session, 0, 10)
    assert isinstance(lst, list)

    # update
    u = repo.update(db_session, g, {"name": "BaseRepoTopic2"})
    assert u.name == "BaseRepoTopic2"

    # delete
    d = repo.delete(db_session, t.id)
    assert d is not None and d.id == t.id
    assert repo.get(db_session, t.id) is None
