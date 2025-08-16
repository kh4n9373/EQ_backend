import pytest
from fastapi.testclient import TestClient

from app.models import Situation


def test_get_situations_by_topic_success(client, sample_situation, sample_topic):
    """Test getting situations by topic ID."""
    response = client.get(f"/api/v1/topics/{sample_topic.id}/situations")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Situations retrieved successfully"
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


def test_get_situations_by_topic_empty(client, sample_topic, db_session):
    """Test getting situations by topic when empty."""
    # Clear all situations for this topic
    db_session.query(Situation).filter(Situation.topic_id == sample_topic.id).delete()
    db_session.commit()

    response = client.get(f"/api/v1/topics/{sample_topic.id}/situations")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Situations retrieved successfully"
    assert len(data["data"]) == 0


def test_get_situations_by_topic_not_found(client):
    """Test getting situations for non-existent topic."""
    response = client.get("/api/v1/topics/999/situations")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Situations retrieved successfully"
    assert len(data["data"]) == 0


def test_get_situation_by_id_success(client, sample_situation):
    """Test getting situation by ID."""
    response = client.get(f"/api/v1/situations/{sample_situation.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Situation retrieved successfully"
    assert data["data"]["id"] == sample_situation.id
    assert data["data"]["question"] == sample_situation.question


def test_get_situation_by_id_not_found(client):
    """Test getting non-existent situation."""
    response = client.get("/api/v1/situations/999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_get_situation_by_id_invalid_id(client):
    """Test getting situation with invalid ID."""
    response = client.get("/api/v1/situations/invalid")
    assert response.status_code == 422  # Validation error


def test_create_situation_success(client, sample_topic, auth_headers):
    """Test creating a new situation."""
    situation_data = {
        "question": "What would you do in this new situation?",
        "context": "This is a new test situation context.",
        "topic_id": sample_topic.id,
    }
    response = client.post(
        "/api/v1/situations", json=situation_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Situation created successfully"
    assert data["data"]["question"] == situation_data["question"]


def test_create_situation_invalid_data(client, sample_topic, auth_headers):
    """Test creating situation with invalid data."""
    situation_data = {
        "question": "",  # Empty question should be invalid
        "context": "This is a test situation context.",
        "topic_id": sample_topic.id,
    }
    response = client.post(
        "/api/v1/situations", json=situation_data, headers=auth_headers
    )
    assert response.status_code == 422  # Validation error


def test_create_situation_missing_required_fields(client, auth_headers):
    """Test creating situation with missing required fields."""
    situation_data = {}
    response = client.post(
        "/api/v1/situations", json=situation_data, headers=auth_headers
    )
    assert response.status_code == 422  # Validation error


def test_create_situation_unauthorized(client, sample_topic):
    """Test creating situation without authentication."""
    situation_data = {
        "question": "What would you do in this new situation?",
        "context": "This is a new test situation context.",
        "topic_id": sample_topic.id,
    }
    response = client.post("/api/v1/situations", json=situation_data)
    assert response.status_code == 401  # Unauthorized


def test_update_situation_success(client, sample_situation, auth_headers):
    """Test updating a situation."""
    update_data = {
        "question": "Updated question for this situation?",
        "context": "Updated context for this situation.",
    }
    response = client.put(
        f"/api/v1/situations/{sample_situation.id}",
        json=update_data,
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Situation updated successfully"
    assert data["data"]["question"] == update_data["question"]


def test_update_situation_not_found(client, auth_headers):
    """Test updating non-existent situation."""
    update_data = {
        "question": "Updated question for this situation?",
        "context": "Updated context for this situation.",
    }
    response = client.put(
        "/api/v1/situations/999", json=update_data, headers=auth_headers
    )
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_update_situation_unauthorized(client, sample_situation):
    """Test updating situation without authentication."""
    update_data = {
        "question": "Updated question for this situation?",
        "context": "Updated context for this situation.",
    }
    response = client.put(f"/api/v1/situations/{sample_situation.id}", json=update_data)
    assert response.status_code == 401  # Unauthorized


def test_delete_situation_success(client, sample_situation, auth_headers):
    """Test deleting a situation."""
    response = client.delete(
        f"/api/v1/situations/{sample_situation.id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Situation deleted successfully"


def test_delete_situation_not_found(client, auth_headers):
    """Test deleting non-existent situation."""
    response = client.delete("/api/v1/situations/999", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_delete_situation_unauthorized(client, sample_situation):
    """Test deleting situation without authentication."""
    response = client.delete(f"/api/v1/situations/{sample_situation.id}")
    assert response.status_code == 401  # Unauthorized


def test_get_contributed_situations_success(client, sample_situation, auth_headers):
    """Test getting contributed situations."""
    response = client.get("/api/v1/situations/contributed", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Contributed situations retrieved successfully"
    assert isinstance(data["data"], list)


def test_get_contributed_situations_unauthorized(client):
    """Test getting contributed situations without authentication."""
    response = client.get("/api/v1/situations/contributed")
    assert response.status_code == 401


def test_get_my_situations_success(client, sample_situation, auth_headers):
    """Test getting situations created by current user."""
    response = client.get("/api/v1/situations/user/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "User situations retrieved successfully"
    assert isinstance(data["data"], list)


def test_get_my_situations_unauthorized(client):
    """Test getting user situations without authentication."""
    response = client.get("/api/v1/situations/user/me")
    assert response.status_code == 401


def test_get_user_situations_success(client, sample_situation, sample_user):
    """Test getting situations of a specific user."""
    response = client.get(f"/api/v1/situations/user/{sample_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "User situations retrieved successfully"
    assert isinstance(data["data"], list)


def test_get_user_situations_not_found(client):
    """Test getting situations of non-existent user."""
    response = client.get("/api/v1/situations/user/999")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "User situations retrieved successfully"
    assert len(data["data"]) == 0  # Unauthorized
