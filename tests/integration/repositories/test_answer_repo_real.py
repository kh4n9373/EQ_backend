import pytest

from app.repositories.answer_repository import AnswerRepository


@pytest.mark.integration
def test_answer_crud_and_queries(db_session, test_user, test_situation):
    repo = AnswerRepository()
    a = repo.create_answer(
        db_session,
        {
            "situation_id": test_situation.id,
            "user_id": test_user.id,
            "answer_text": "txt",
            "scores": {"empathy": 5},
            "reasoning": {"empathy": "ok"},
        },
    )
    assert a.id
    assert repo.get_by_id(db_session, a.id).id == a.id
    assert any(x.id == a.id for x in repo.list_answers(db_session))
    assert any(
        x.id == a.id for x in repo.get_by_situation(db_session, test_situation.id)
    )
    a = repo.update_answer(db_session, a, {"answer_text": "txt2"})
    assert a.answer_text == "txt2"
    assert repo.delete_answer(db_session, a) is True
