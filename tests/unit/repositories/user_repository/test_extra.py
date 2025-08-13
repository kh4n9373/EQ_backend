from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.repositories.user_repository import UserRepository


def make_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def test_user_repository_list_and_search():
    db = make_db()
    repo = UserRepository()
    u1 = repo.create_user(
        db,
        {
            "google_id": "g1",
            "email": "a@x",
            "name": "Alice",
            "picture": "",
            "is_active": True,
        },
    )
    u2 = repo.create_user(
        db,
        {
            "google_id": "g2",
            "email": "b@x",
            "name": "Bob",
            "picture": "",
            "is_active": True,
        },
    )
    lst = repo.list_users(db, page=1, size=10)
    assert len(lst) >= 2
    search = repo.search_users_by_name(db, query="bo", limit=10)
    assert any(u.name == "Bob" for u in search)
