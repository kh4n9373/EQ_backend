from unittest.mock import patch

from fastapi.testclient import TestClient


@patch("app.openai_utils.analyze_eq")
def test_analyze_answer_success(mock_analyze, client: TestClient, sample_data):
    mock_analyze.return_value = (
        {
            "self_awareness": 8,
            "empathy": 7,
            "self_regulation": 6,
            "communication": 8,
            "decision_making": 7,
        },
        {
            "self_awareness": "Good awareness",
            "empathy": "Shows empathy",
            "self_regulation": "Basic control",
            "communication": "Good communication",
            "decision_making": "Good decisions",
        },
    )

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

    # Verify the mock was called
    mock_analyze.assert_called_once()


@patch("app.openai_utils.analyze_eq")
def test_analyze_answer_invalid_situation(mock_analyze, client: TestClient):
    mock_analyze.return_value = ({}, {})

    answer_data = {"situation_id": 999, "answer_text": "Test answer"}
    response = client.post("/analyze", json=answer_data)
    assert response.status_code == 404

    mock_analyze.assert_not_called()


def test_get_answers_by_situation(client: TestClient, sample_data):
    situation = sample_data["situation"]
    response = client.get(f"/answers-by-situation?situation_id={situation.id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
