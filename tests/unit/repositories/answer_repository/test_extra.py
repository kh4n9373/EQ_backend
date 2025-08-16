from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Answer
from app.repositories.answer_repository import AnswerRepository


def make_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def test_create_answer_and_get_by_situation():
    db = make_db()
    repo = AnswerRepository()
    # create
    created = repo.create_answer(
        db, {"answer_text": "t", "situation_id": 1, "user_id": None}
    )
    assert isinstance(created, Answer)
    # list by situation
    items = repo.get_by_situation(db, 1)
    assert len(items) == 1


def test_create_answer_with_analysis_json_encoding():
    db = make_db()
    repo = AnswerRepository()
    ans = repo.create_answer_with_analysis(
        db,
        {"answer_text": "t2", "situation_id": 2, "user_id": None},
        scores={"a": 1},
        reasoning={"b": "x"},
    )
    assert ans.scores and ans.reasoning
