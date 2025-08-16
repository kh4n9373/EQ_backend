from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.models import Answer


def test_analyze_answer_success(client, sample_situation, auth_headers):
    """Test analyzing an answer."""
    answer_data = {
        "answer_text": "This is my answer to the situation",
        "situation_id": sample_situation.id,
    }

    with patch("app.services.openai_service.OpenAIService.analyze_eq") as mock_analyze:
        mock_analyze.return_value = (
            {"relationship_management": 7, "self_awareness": 8},
            {
                "relationship_management": "Good response",
                "self_awareness": "Excellent insight",
            },
        )

        response = client.post(
            "/api/v1/analysis/analyze", json=answer_data, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Answer analyzed successfully"
        assert "scores" in data["data"]
        assert "reasoning" in data["data"]


def test_analyze_answer_invalid_data(client, auth_headers):
    """Test analyzing answer with invalid data."""
    answer_data = {
        "answer_text": "",  # Empty answer should be invalid
        "situation_id": 1,
    }
    response = client.post(
        "/api/v1/analysis/analyze", json=answer_data, headers=auth_headers
    )
    assert response.status_code == 422  # Validation error


def test_analyze_answer_missing_required_fields(client, auth_headers):
    """Test analyzing answer with missing required fields."""
    answer_data = {}
    response = client.post(
        "/api/v1/analysis/analyze", json=answer_data, headers=auth_headers
    )
    assert response.status_code == 422  # Validation error


def test_analyze_answer_situation_not_found(client, auth_headers):
    """Test analyzing answer with non-existent situation."""
    answer_data = {
        "answer_text": "This is my answer to the situation",
        "situation_id": 999,
    }
    response = client.post(
        "/api/v1/analysis/analyze", json=answer_data, headers=auth_headers
    )
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_analyze_answer_unauthorized(client, sample_situation):
    """Test analyzing answer without authentication."""
    answer_data = {
        "answer_text": "This is my answer to the situation",
        "situation_id": sample_situation.id,
    }
    response = client.post("/api/v1/analysis/analyze", json=answer_data)
    assert response.status_code == 401  # Unauthorized


def test_analyze_sentiment_success(client, auth_headers):
    """Test analyzing sentiment."""
    sentiment_data = {"content": "I am very happy and excited about this!"}

    with patch(
        "app.services.sentiment_service.SentimentService.analyze_sentiment"
    ) as mock_sentiment:
        mock_sentiment.return_value = {
            "sentiment_score": 0.8,
            "sentiment_label": "very_positive",
            "keywords": ["happy", "excited"],
        }

        response = client.post(
            "/api/v1/analysis/analyze-sentiment",
            json=sentiment_data,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Sentiment analyzed successfully"
        assert "sentiment_score" in data["data"]


def test_analyze_sentiment_invalid_data(client, auth_headers):
    """Test analyzing sentiment with invalid data."""
    sentiment_data = {"content": ""}  # Empty content should be invalid
    response = client.post(
        "/api/v1/analysis/analyze-sentiment", json=sentiment_data, headers=auth_headers
    )
    assert response.status_code == 422  # Validation error


def test_analyze_sentiment_missing_content(client, auth_headers):
    """Test analyzing sentiment with missing content."""
    sentiment_data = {}
    response = client.post(
        "/api/v1/analysis/analyze-sentiment", json=sentiment_data, headers=auth_headers
    )
    assert response.status_code == 422  # Validation error


def test_analyze_sentiment_unauthorized(client):
    """Test analyzing sentiment without authentication."""
    sentiment_data = {"content": "I am very happy and excited about this!"}
    response = client.post("/api/v1/analysis/analyze-sentiment", json=sentiment_data)
    assert response.status_code == 401  # Unauthorized


def test_get_answers_by_situation_success(
    client, sample_situation, sample_user, db_session, auth_headers
):
    """Test getting answers by situation ID."""
    # Create a test answer
    answer = Answer(
        answer_text="This is a test answer",
        situation_id=sample_situation.id,
        user_id=sample_user.id,
        scores={"relationship_management": 7, "self_awareness": 8},
        reasoning={
            "relationship_management": "Good response",
            "self_awareness": "Excellent insight",
        },
    )
    db_session.add(answer)
    db_session.commit()

    response = client.get(
        f"/api/v1/analysis/situations/{sample_situation.id}/answers",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Answers retrieved successfully"
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


def test_get_answers_by_situation_empty(
    client, sample_situation, db_session, auth_headers
):
    """Test getting answers by situation when empty."""
    # Clear all answers for this situation
    db_session.query(Answer).filter(Answer.situation_id == sample_situation.id).delete()
    db_session.commit()

    response = client.get(
        f"/api/v1/analysis/situations/{sample_situation.id}/answers",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Answers retrieved successfully"
    assert len(data["data"]) == 0


def test_get_answers_by_situation_not_found(client, auth_headers):
    """Test getting answers for non-existent situation."""
    response = client.get(
        "/api/v1/analysis/situations/999/answers", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Answers retrieved successfully"
    assert len(data["data"]) == 0


def test_get_answers_by_situation_invalid_id(client, auth_headers):
    """Test getting answers with invalid situation ID."""
    response = client.get(
        "/api/v1/analysis/situations/invalid/answers", headers=auth_headers
    )
    assert response.status_code == 422  # Validation error


def test_get_answers_by_situation_unauthorized(client, sample_situation):
    """Test getting answers without authentication."""
    response = client.get(f"/api/v1/analysis/situations/{sample_situation.id}/answers")
    assert response.status_code == 401  # Unauthorized
