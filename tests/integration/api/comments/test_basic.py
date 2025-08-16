from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.models import Comment


def test_get_comments_by_situation_success(
    client, sample_situation, sample_user, db_session
):
    """Test getting comments by situation ID."""
    # Create a test comment
    comment = Comment(
        content="This is a test comment",
        situation_id=sample_situation.id,
        user_id=sample_user.id,
        sentiment_score=0.5,
        sentiment_label="positive",
    )
    db_session.add(comment)
    db_session.commit()

    response = client.get(f"/api/v1/situations/{sample_situation.id}/comments")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Comments retrieved successfully"
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


def test_get_comments_by_situation_empty(client, sample_situation, db_session):
    """Test getting comments by situation when empty."""
    # Clear all comments for this situation
    db_session.query(Comment).filter(
        Comment.situation_id == sample_situation.id
    ).delete()
    db_session.commit()

    response = client.get(f"/api/v1/situations/{sample_situation.id}/comments")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Comments retrieved successfully"
    assert len(data["data"]) == 0


def test_get_comments_by_situation_invalid_id(client):
    """Test getting comments with invalid situation ID."""
    response = client.get("/api/v1/situations/invalid/comments")
    assert response.status_code == 422  # Validation error


def test_create_comment_success(client, sample_situation, auth_headers):
    """Test creating a new comment."""
    comment_data = {"content": "This is a new test comment"}
    response = client.post(
        f"/api/v1/situations/{sample_situation.id}/comments",
        json=comment_data,
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Comment created successfully"
    assert data["data"]["content"] == comment_data["content"]


def test_create_comment_invalid_data(client, sample_situation, auth_headers):
    """Test creating comment with invalid data."""
    comment_data = {"content": ""}  # Empty content should be invalid
    response = client.post(
        f"/api/v1/situations/{sample_situation.id}/comments",
        json=comment_data,
        headers=auth_headers,
    )
    assert response.status_code == 422  # Validation error


def test_create_comment_missing_content(client, sample_situation, auth_headers):
    """Test creating comment with missing content."""
    comment_data = {}
    response = client.post(
        f"/api/v1/situations/{sample_situation.id}/comments",
        json=comment_data,
        headers=auth_headers,
    )
    assert response.status_code == 422  # Validation error


def test_create_comment_unauthorized(client, sample_situation):
    """Test creating comment without authentication."""
    comment_data = {"content": "This is a new test comment"}
    response = client.post(
        f"/api/v1/situations/{sample_situation.id}/comments", json=comment_data
    )
    assert response.status_code == 401  # Unauthorized


def test_get_comment_by_id_success(client, sample_situation, sample_user, db_session):
    """Test getting comment by ID."""
    # Create a test comment
    comment = Comment(
        content="This is a test comment",
        situation_id=sample_situation.id,
        user_id=sample_user.id,
        sentiment_score=0.5,
        sentiment_label="positive",
    )
    db_session.add(comment)
    db_session.commit()

    response = client.get(f"/api/v1/comments/{comment.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Comment retrieved successfully"
    assert data["data"]["id"] == comment.id
    assert data["data"]["content"] == comment.content


def test_get_comment_by_id_not_found(client):
    """Test getting non-existent comment."""
    response = client.get("/api/v1/comments/999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_get_comment_by_id_invalid_id(client):
    """Test getting comment with invalid ID."""
    response = client.get("/api/v1/comments/invalid")
    assert response.status_code == 422  # Validation error


def test_update_comment_success(
    client, sample_situation, sample_user, db_session, auth_headers
):
    """Test updating a comment."""
    # Create a test comment
    comment = Comment(
        content="This is a test comment",
        situation_id=sample_situation.id,
        user_id=sample_user.id,
        sentiment_score=0.5,
        sentiment_label="positive",
    )
    db_session.add(comment)
    db_session.commit()

    update_data = {"content": "Updated comment content"}
    response = client.put(
        f"/api/v1/comments/{comment.id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Comment updated successfully"
    assert data["data"]["content"] == update_data["content"]


def test_update_comment_not_found(client, auth_headers):
    """Test updating non-existent comment."""
    update_data = {"content": "Updated comment content"}
    response = client.put(
        "/api/v1/comments/999", json=update_data, headers=auth_headers
    )
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_update_comment_unauthorized(client, sample_situation, sample_user, db_session):
    """Test updating comment without authentication."""
    # Create a test comment
    comment = Comment(
        content="This is a test comment",
        situation_id=sample_situation.id,
        user_id=sample_user.id,
        sentiment_score=0.5,
        sentiment_label="positive",
    )
    db_session.add(comment)
    db_session.commit()

    update_data = {"content": "Updated comment content"}
    response = client.put(f"/api/v1/comments/{comment.id}", json=update_data)
    assert response.status_code == 401  # Unauthorized


def test_delete_comment_success(
    client, sample_situation, sample_user, db_session, auth_headers
):
    """Test deleting a comment."""
    # Create a test comment
    comment = Comment(
        content="This is a test comment",
        situation_id=sample_situation.id,
        user_id=sample_user.id,
        sentiment_score=0.5,
        sentiment_label="positive",
    )
    db_session.add(comment)
    db_session.commit()

    response = client.delete(f"/api/v1/comments/{comment.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Comment deleted successfully"


def test_delete_comment_not_found(client, auth_headers):
    """Test deleting non-existent comment."""
    response = client.delete("/api/v1/comments/999", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_delete_comment_unauthorized(client, sample_situation, sample_user, db_session):
    """Test deleting comment without authentication."""
    # Create a test comment
    comment = Comment(
        content="This is a test comment",
        situation_id=sample_situation.id,
        user_id=sample_user.id,
        sentiment_score=0.5,
        sentiment_label="positive",
    )
    db_session.add(comment)
    db_session.commit()

    response = client.delete(f"/api/v1/comments/{comment.id}")
    assert response.status_code == 401  # Unauthorized
