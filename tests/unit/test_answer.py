from fastapi.testclient import TestClient


def test_analyze_answer_success(client: TestClient, sample_data):
    situation = sample_data["situation"]

    answer_data = {
        "situation_id": situation.id,
        "answer_text": "I would try to understand the other person's perspective and communicate calmly.",
    }
    response = client.post("/analyze", json=answer_data)
    assert response.status_code == 200
    data = response.json()
    assert "scores" in data
    assert "reasoning" in data
    assert "question" in data


def test_analyze_answer_invalid_situation(client: TestClient):
    answer_data = {"situation_id": 999, "answer_text": "Test answer"}
    response = client.post("/analyze", json=answer_data)
    assert response.status_code == 404


def test_get_answers_by_situation(client: TestClient, sample_data):
    situation = sample_data["situation"]
    response = client.get(f"/answers-by-situation?situation_id={situation.id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
