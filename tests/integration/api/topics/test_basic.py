import pytest
from fastapi.testclient import TestClient

from app.models import Topic


def test_list_topics_success(client, sample_topic):
    """Test listing all topics."""
    response = client.get("/api/v1/topics")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Topics retrieved successfully"
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


def test_list_topics_empty(client, db_session):
    """Test listing topics when empty."""
    # Clear all topics
    db_session.query(Topic).delete()
    db_session.commit()

    response = client.get("/api/v1/topics")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Topics retrieved successfully"
    assert len(data["data"]) == 0


def test_get_topic_by_id_success(client, sample_topic):
    """Test getting topic by ID."""
    response = client.get(f"/api/v1/topics/{sample_topic.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Topic retrieved successfully"
    assert data["data"]["id"] == sample_topic.id
    assert data["data"]["name"] == sample_topic.name


def test_get_topic_by_id_not_found(client):
    """Test getting non-existent topic."""
    response = client.get("/api/v1/topics/999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_get_topic_by_id_invalid_id(client):
    """Test getting topic with invalid ID."""
    response = client.get("/api/v1/topics/invalid")
    assert response.status_code == 422  # Validation error


def test_create_topic_success(client):
    """Test creating a new topic."""
    topic_data = {"name": "New Test Topic"}
    response = client.post("/api/v1/topics", json=topic_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Topic created successfully"
    assert data["data"]["name"] == "New Test Topic"


def test_create_topic_invalid_data(client):
    """Test creating topic with invalid data."""
    topic_data = {"name": ""}  # Empty name should be invalid
    response = client.post("/api/v1/topics", json=topic_data)
    assert response.status_code == 422  # Validation error


def test_create_topic_missing_required_fields(client):
    """Test creating topic with missing required fields."""
    topic_data = {}
    response = client.post("/api/v1/topics", json=topic_data)
    assert response.status_code == 422  # Validation error


def test_update_topic_success(client, sample_topic):
    """Test updating a topic."""
    update_data = {"name": "Updated Topic Name"}
    response = client.put(f"/api/v1/topics/{sample_topic.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Topic updated successfully"
    assert data["data"]["name"] == "Updated Topic Name"


def test_update_topic_not_found(client):
    """Test updating non-existent topic."""
    update_data = {"name": "Updated Topic Name"}
    response = client.put("/api/v1/topics/999", json=update_data)
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_update_topic_invalid_data(client, sample_topic):
    """Test updating topic with invalid data."""
    update_data = {"name": ""}  # Empty name should be invalid
    response = client.put(f"/api/v1/topics/{sample_topic.id}", json=update_data)
    assert response.status_code == 422  # Validation error


def test_delete_topic_success(client, sample_topic):
    """Test deleting a topic."""
    response = client.delete(f"/api/v1/topics/{sample_topic.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Topic deleted successfully"


def test_delete_topic_not_found(client):
    """Test deleting non-existent topic."""
    response = client.delete("/api/v1/topics/999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_delete_topic_invalid_id(client):
    """Test deleting topic with invalid ID."""
    response = client.delete("/api/v1/topics/invalid")
    assert response.status_code == 422  # Validation error
