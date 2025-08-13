from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Comment
from app.repositories.comment_repository import CommentRepository


def make_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def test_comment_crud_paths():
    db = make_db()
    repo = CommentRepository()
    c = repo.create(db, {"content": "c1", "situation_id": 1, "user_id": 1})
    assert isinstance(c, Comment)
    got = repo.get(db, c.id)
    assert got.id == c.id
    updated = repo.update(db, got, {"content": "c2"})
    assert updated.content == "c2"
    all_items = repo.get_by_situation(db, 1)
    assert len(all_items) >= 1
