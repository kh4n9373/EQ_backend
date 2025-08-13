from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from app.services.auth_service import AuthService


class TestAuthService:
    @pytest.fixture
    def mock_user_service(self):
        return Mock()

    @pytest.fixture
    def auth_service(self, mock_user_service):
        return AuthService(mock_user_service)

    @pytest.fixture
    def sample_user_data(self):
        user = Mock()
        user.id = 1
        user.email = "test@example.com"
        user.name = "Test User"
        user.picture = "https://example.com/pic.jpg"
        user.google_id = "123456"
        user.is_active = True
        return user

    @pytest.fixture
    def mock_oauth_token(self):
        return {
            "userinfo": {
                "sub": "123456",
                "email": "test@example.com",
                "name": "Test User",
                "picture": "https://example.com/pic.jpg",
            },
            "refresh_token": "refresh_token_123",
        }

    @pytest.fixture
    def mock_request(self):
        request = Mock()
        request.url_for.return_value = "http://localhost:8000/auth/callback"
        return request

    @pytest.mark.asyncio
    async def test_login_google_success(self, auth_service, mock_request):
        """Test successful Google OAuth login initiation."""
        # Arrange
        mock_oauth = Mock()
        mock_oauth.google.authorize_redirect = AsyncMock(
            return_value="redirect_response"
        )

        with patch("app.services.auth_service.oauth", mock_oauth):
            # Act
            result = await auth_service.login_google(mock_request)

            # Assert
            mock_request.url_for.assert_called_once_with("auth_callback")
            mock_oauth.google.authorize_redirect.assert_called_once_with(
                mock_request, "http://localhost:8000/auth/callback"
            )
            assert result == "redirect_response"

    @pytest.mark.asyncio
    async def test_auth_callback_new_user_success(
        self, auth_service, mock_request, mock_oauth_token, sample_user_data
    ):
        """Test successful OAuth callback for new user."""
        # Arrange
        mock_oauth = Mock()
        mock_oauth.google.authorize_access_token = AsyncMock(
            return_value=mock_oauth_token
        )

        auth_service.user_service.get_user_by_email.return_value = None
        auth_service.user_service.create_user.return_value = sample_user_data
        auth_service.user_service.update_user_refresh_token.return_value = (
            sample_user_data
        )

        with patch("app.services.auth_service.oauth", mock_oauth):
            with patch(
                "app.services.auth_service.create_access_token"
            ) as mock_create_token:
                with patch(
                    "app.services.auth_service.encrypt_refresh_token"
                ) as mock_encrypt:
                    mock_create_token.return_value = "access_token_123"
                    mock_encrypt.return_value = "encrypted_token_123"

                    # Act
                    result = await auth_service.auth_callback(mock_request)

                    # Assert
                    mock_oauth.google.authorize_access_token.assert_called_once_with(
                        mock_request
                    )
                    auth_service.user_service.get_user_by_email.assert_called_once_with(
                        "test@example.com"
                    )
                    auth_service.user_service.create_user.assert_called_once()
                    auth_service.user_service.update_user_refresh_token.assert_called_once_with(
                        1, "encrypted_token_123"
                    )
                    mock_create_token.assert_called_once_with(
                        data={"sub": "test@example.com"}
                    )
                    assert result.status_code == 307  # RedirectResponse

    @pytest.mark.asyncio
    async def test_auth_callback_existing_user_success(
        self, auth_service, mock_request, mock_oauth_token, sample_user_data
    ):
        """Test successful OAuth callback for existing user."""
        # Arrange
        mock_oauth = Mock()
        mock_oauth.google.authorize_access_token = AsyncMock(
            return_value=mock_oauth_token
        )

        # Existing user with different name
        existing_user = Mock()
        existing_user.id = 1
        existing_user.email = "test@example.com"
        existing_user.name = "Old Name"
        existing_user.picture = "https://example.com/pic.jpg"
        existing_user.google_id = "123456"
        existing_user.is_active = True
        auth_service.user_service.get_user_by_email.return_value = existing_user
        auth_service.user_service.update_user.return_value = sample_user_data
        auth_service.user_service.update_user_refresh_token.return_value = (
            sample_user_data
        )

        with patch("app.services.auth_service.oauth", mock_oauth):
            with patch(
                "app.services.auth_service.create_access_token"
            ) as mock_create_token:
                with patch(
                    "app.services.auth_service.encrypt_refresh_token"
                ) as mock_encrypt:
                    mock_create_token.return_value = "access_token_123"
                    mock_encrypt.return_value = "encrypted_token_123"

                    # Act
                    result = await auth_service.auth_callback(mock_request)

                    # Assert
                    auth_service.user_service.get_user_by_email.assert_called_once_with(
                        "test@example.com"
                    )
                    auth_service.user_service.update_user.assert_called_once()
                    auth_service.user_service.update_user_refresh_token.assert_called_once_with(
                        1, "encrypted_token_123"
                    )
                    assert result.status_code == 307

    @pytest.mark.asyncio
    async def test_auth_callback_oauth_error(self, auth_service, mock_request):
        """Test OAuth callback when OAuth fails."""
        # Arrange
        mock_oauth = Mock()
        mock_oauth.google.authorize_access_token = AsyncMock(
            side_effect=Exception("OAuth Error")
        )

        with patch("app.services.auth_service.oauth", mock_oauth):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.auth_callback(mock_request)

            assert exc_info.value.status_code == 401
            assert "Could not validate credentials" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_auth_callback_no_userinfo(self, auth_service, mock_request):
        """Test OAuth callback when no userinfo in token."""
        # Arrange
        mock_oauth = Mock()
        mock_oauth.google.authorize_access_token = AsyncMock(return_value={})

        with patch("app.services.auth_service.oauth", mock_oauth):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.auth_callback(mock_request)

            assert exc_info.value.status_code == 401
            assert "Could not validate credentials" in str(exc_info.value.detail)

    def test_logout_success(self, auth_service):
        """Test successful logout."""
        # Arrange
        mock_response = Mock()

        # Act
        result = auth_service.logout(mock_response)

        # Assert
        mock_response.delete_cookie.assert_called_once_with("access_token", path="/")
        assert result == {"message": "Logged out"}

    @pytest.mark.asyncio
    async def test_auth_callback_no_refresh_token(
        self, auth_service, mock_request, sample_user_data
    ):
        """Test OAuth callback when no refresh token provided."""
        # Arrange
        token_without_refresh = {
            "userinfo": {
                "sub": "123456",
                "email": "test@example.com",
                "name": "Test User",
                "picture": "https://example.com/pic.jpg",
            }
        }

        mock_oauth = Mock()
        mock_oauth.google.authorize_access_token = AsyncMock(
            return_value=token_without_refresh
        )

        auth_service.user_service.get_user_by_email.return_value = None
        auth_service.user_service.create_user.return_value = sample_user_data

        with patch("app.services.auth_service.oauth", mock_oauth):
            with patch(
                "app.services.auth_service.create_access_token"
            ) as mock_create_token:
                mock_create_token.return_value = "access_token_123"

                # Act
                result = await auth_service.auth_callback(mock_request)

                # Assert
                auth_service.user_service.create_user.assert_called_once()
                # Should not call update_user_refresh_token when no refresh token
                auth_service.user_service.update_user_refresh_token.assert_not_called()
                assert result.status_code == 307
