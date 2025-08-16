import pytest

from app.repositories.comment_repository import CommentRepository


@pytest.mark.integration
def test_comment_crud_and_queries(db_session, test_user, test_situation):
    repo = CommentRepository()
    c = repo.create_with_sentiment(
        db_session, {"content": "c1", "situation_id": test_situation.id}, test_user.id
    )
    assert c.id
    assert repo.get_comment_by_id(db_session, c.id).id == c.id
    assert any(
        x.id == c.id for x in repo.get_by_situation(db_session, test_situation.id)
    )
    all_comments = repo.list_comments(db_session)
    assert any(x.id == c.id for x in all_comments)
