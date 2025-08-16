from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def test_complete_user_workflow(
    client, sample_user, sample_topic, sample_situation, auth_headers
):
    """Test a complete user workflow from login to analysis."""

    # 1. Get current user info
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == sample_user.email

    # 2. List topics
    response = client.get("/api/v1/topics")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1

    # 3. Get situations for a topic
    response = client.get(f"/api/v1/topics/{sample_topic.id}/situations")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1

    # 4. Get a specific situation
    response = client.get(f"/api/v1/situations/{sample_situation.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == sample_situation.id

    # 5. Create a comment on the situation
    comment_data = {"content": "This is a test comment for the workflow"}
    response = client.post(
        f"/api/v1/situations/{sample_situation.id}/comments",
        json=comment_data,
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    comment_id = data["data"]["id"]

    # 6. Get comments for the situation
    response = client.get(f"/api/v1/situations/{sample_situation.id}/comments")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1

    # 7. Analyze an answer
    with patch("app.services.openai_service.OpenAIService.analyze_eq") as mock_analyze:
        mock_analyze.return_value = (
            {"relationship_management": 7, "self_awareness": 8},
            {
                "relationship_management": "Good response",
                "self_awareness": "Excellent insight",
            },
        )

        answer_data = {
            "answer_text": "This is my answer to the situation in the workflow test",
            "situation_id": sample_situation.id,
        }
        response = client.post(
            "/api/v1/analysis/analyze", json=answer_data, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "scores" in data["data"]

    # 8. Get answers for the situation
    response = client.get(
        f"/api/v1/analysis/situations/{sample_situation.id}/answers",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

    # 9. Update the comment
    update_data = {"content": "Updated comment content from workflow test"}
    response = client.put(
        f"/api/v1/comments/{comment_id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # 10. Delete the comment
    response = client.delete(f"/api/v1/comments/{comment_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_error_handling_workflow(client, auth_headers):
    """Test error handling in the workflow."""

    # Test getting non-existent resources
    response = client.get("/api/v1/users/999", headers=auth_headers)
    assert response.status_code == 404

    response = client.get("/api/v1/topics/999")
    assert response.status_code == 404

    response = client.get("/api/v1/situations/999")
    assert response.status_code == 404

    # Test invalid data
    response = client.post("/api/v1/topics", json={"name": ""})
    assert response.status_code == 422

    # Test unauthorized access
    response = client.get("/api/v1/users/")
    assert response.status_code == 401

    response = client.post("/api/v1/situations", json={})
    assert response.status_code == 401


def test_health_and_status(client):
    """Test health check and basic status endpoints."""

    # Health check
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Healthy"

    # API docs should be available
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200
