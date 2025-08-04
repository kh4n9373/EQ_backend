from fastapi.testclient import TestClient


def test_get_comments_by_situation(client: TestClient):
    response = client.get("/situations/1/comments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_comment_unauthorized(client: TestClient):
    comment_data = {"content": "This is a test comment"}
    response = client.post("/situations/1/comments", json=comment_data)
    assert response.status_code == 401


def test_analyze_sentiment(client: TestClient):
    text_data = {"content": "I am feeling very happy today!"}
    response = client.post("/analyze-sentiment", json=text_data)
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "score" in data
    assert "severity" in data
