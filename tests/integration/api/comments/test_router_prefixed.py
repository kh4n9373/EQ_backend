from app.models import Comment


def test_prefixed_get_comments_by_situation(
    client, sample_situation, sample_user, db_session
):
    c = Comment(content="hi", situation_id=sample_situation.id, user_id=sample_user.id)
    db_session.add(c)
    db_session.commit()
    res = client.get(f"/api/v1/comments/situations/{sample_situation.id}/comments")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_prefixed_create_comment_unauthorized(client, sample_situation):
    res = client.post(
        f"/api/v1/comments/situations/{sample_situation.id}/comments",
        json={"content": "hello"},
    )
    assert res.status_code == 401


def test_prefixed_create_comment_authorized(client, sample_situation, auth_headers):
    res = client.post(
        f"/api/v1/comments/situations/{sample_situation.id}/comments",
        json={"content": "hello"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["content"] == "hello"
