from fastapi.testclient import TestClient


def test_get_situations_by_topic(client: TestClient):
    response = client.get("/situations?topic_id=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_situations_structure(client: TestClient):
    response = client.get("/situations?topic_id=1")
    situations = response.json()
    if situations:
        situation = situations[0]
        assert "id" in situation
        assert "context" in situation
        assert "question" in situation


def test_get_contributed_situations(client: TestClient):
    response = client.get("/contributed-situations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
