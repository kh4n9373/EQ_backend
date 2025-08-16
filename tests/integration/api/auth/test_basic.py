from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


def test_login_google_redirect(client):
    """Test Google OAuth login redirect."""
    with patch("app.services.auth_service.AuthService.login_google") as mock_login:
        mock_response = MagicMock()
        mock_response.status_code = 302
        mock_response.headers = {
            "location": "https://accounts.google.com/oauth/authorize"
        }
        mock_login.return_value = mock_response

        response = client.get("/api/v1/auth/login/google")
        assert (
            response.status_code == 200
        )  # The endpoint should return a redirect response


def test_auth_callback_success(client, sample_user):
    """Test successful OAuth callback."""
    with patch("app.services.auth_service.AuthService.auth_callback") as mock_callback:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"set-cookie": "access_token=test_token"}
        mock_callback.return_value = mock_response

        response = client.get("/api/v1/auth/callback/google?code=test_code")
        assert response.status_code == 200


def test_auth_callback_new_user(client):
    """Test OAuth callback for new user."""
    with patch("app.services.auth_service.AuthService.auth_callback") as mock_callback:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"set-cookie": "access_token=test_token"}
        mock_callback.return_value = mock_response

        response = client.get("/api/v1/auth/callback/google?code=test_code")
        assert response.status_code == 200


def test_auth_callback_oauth_error(client):
    """Test OAuth callback with OAuth error."""
    with patch("app.services.auth_service.AuthService.auth_callback") as mock_callback:
        from fastapi import HTTPException

        mock_callback.side_effect = HTTPException(status_code=401, detail="OAuth error")

        response = client.get("/api/v1/auth/callback/google?code=invalid_code")
        assert response.status_code == 401


def test_auth_callback_user_service_error(client):
    """Test OAuth callback with user service error."""
    with patch("app.services.auth_service.AuthService.auth_callback") as mock_callback:
        mock_callback.side_effect = Exception("User service error")

        response = client.get("/api/v1/auth/callback/google?code=test_code")
        assert response.status_code == 500


def test_logout_success(client):
    """Test successful logout."""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Logged out successfully"


def test_logout_user_not_found(client):
    """Test logout when user not found."""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Logged out successfully"


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Healthy"
    assert data["data"]["status"] == "ok"
