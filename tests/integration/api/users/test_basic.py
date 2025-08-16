from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def test_get_user_profile_success(client, sample_user, auth_headers):
    """Test getting user profile by ID with authentication."""
    response = client.get(f"/api/v1/users/{sample_user.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "User profile retrieved successfully"
    assert data["data"]["id"] == sample_user.id
    assert data["data"]["email"] == sample_user.email
    assert data["data"]["name"] == sample_user.name


def test_get_user_profile_not_found(client, auth_headers):
    """Test getting non-existent user profile."""
    response = client.get("/api/v1/users/999", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_get_user_profile_invalid_id(client, auth_headers):
    """Test getting user profile with invalid ID."""
    response = client.get("/api/v1/users/invalid", headers=auth_headers)
    assert response.status_code == 422  # Validation error


def test_search_users_success(client, sample_user, auth_headers):
    """Test searching users by name."""
    response = client.get("/api/v1/users/search?query=Test", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Users search completed successfully"
    assert isinstance(data["data"], list)


def test_search_users_empty(client, auth_headers):
    """Test searching users with no results."""
    response = client.get(
        "/api/v1/users/search?query=NonExistent", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Users search completed successfully"
    assert len(data["data"]) == 0


def test_search_users_missing_query(client, auth_headers):
    """Test searching users without query parameter."""
    response = client.get("/api/v1/users/search", headers=auth_headers)
    assert response.status_code == 422  # Validation error


def test_search_users_short_query(client, auth_headers):
    """Test searching users with query too short."""
    response = client.get("/api/v1/users/search?query=a", headers=auth_headers)
    assert response.status_code == 422  # Validation error


def test_list_users_success(client, sample_user, auth_headers):
    """Test listing users with authentication."""
    response = client.get("/api/v1/users/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Users retrieved successfully"
    assert isinstance(data["data"], list)


def test_list_users_with_search(client, sample_user, auth_headers):
    """Test listing users with search parameter."""
    response = client.get("/api/v1/users/?search=Test", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Users retrieved successfully"


def test_list_users_with_pagination(client, sample_user, auth_headers):
    """Test listing users with pagination."""
    response = client.get("/api/v1/users/?page=1&size=10", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Users retrieved successfully"


def test_list_users_unauthorized(client):
    """Test listing users without authentication."""
    response = client.get("/api/v1/users/")
    assert response.status_code == 401  # Unauthorized


def test_get_user_profile_unauthorized(client, sample_user):
    """Test getting user profile without authentication."""
    response = client.get(f"/api/v1/users/{sample_user.id}")
    assert response.status_code == 401  # Unauthorized


def test_search_users_unauthorized(client):
    """Test searching users without authentication."""
    response = client.get("/api/v1/users/search?query=test")
    assert response.status_code == 200  # Search doesn't require auth


def test_get_current_user_success(client, sample_user, auth_headers):
    """Test getting current user info."""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Current user retrieved successfully"
    assert data["data"]["email"] == sample_user.email
    assert data["data"]["name"] == sample_user.name


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401  # Unauthorized
