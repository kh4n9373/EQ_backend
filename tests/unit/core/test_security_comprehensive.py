"""Comprehensive tests for core.security to boost coverage"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, Request
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decrypt_refresh_token,
    encrypt_refresh_token,
    get_current_user,
    get_current_user_optional,
    get_new_access_token,
)
from app.models import User


@pytest.fixture
def sample_user():
    return User(
        id=1,
        email="test@example.com",
        name="Test User",
        google_id="123456789",
        encrypted_refresh_token="encrypted_token",
    )


@pytest.fixture
def mock_request():
    return Mock(spec=Request)


class TestTokenCreation:
    """Test token creation functions"""

    def test_create_access_token_success(self):
        """Test create_access_token with valid data"""
        data = {"sub": "test@example.com", "user_id": "1"}

        token = create_access_token(data)

        assert isinstance(token, str)
        # Decode to verify structure
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == "1"
        assert "exp" in payload

    def test_create_access_token_empty_data(self):
        """Test create_access_token with empty data"""
        token = create_access_token({})

        assert isinstance(token, str)
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert "exp" in payload

    def test_create_access_token_expiry_calculation(self):
        """Test token expiry is set correctly"""
        data = {"sub": "test@example.com"}

        token = create_access_token(data)

        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        exp_time = datetime.utcfromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        # Allow 60 second tolerance
        assert abs((exp_time - expected_exp).total_seconds()) < 60


class TestRefreshTokenEncryption:
    """Test refresh token encryption/decryption"""

    def test_encrypt_refresh_token_success(self):
        """Test encrypt_refresh_token creates valid JWT"""
        refresh_token = "sample_refresh_token_123"

        encrypted = encrypt_refresh_token(refresh_token)

        assert isinstance(encrypted, str)
        payload = jwt.decode(
            encrypted, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["refresh_token"] == refresh_token

    def test_decrypt_refresh_token_success(self):
        """Test decrypt_refresh_token extracts token correctly"""
        refresh_token = "sample_refresh_token_123"
        encrypted = encrypt_refresh_token(refresh_token)

        decrypted = decrypt_refresh_token(encrypted)

        assert decrypted == refresh_token

    def test_decrypt_refresh_token_invalid(self):
        """Test decrypt_refresh_token with invalid token"""
        invalid_token = "invalid.token.here"

        with pytest.raises(JWTError):
            decrypt_refresh_token(invalid_token)

    def test_encrypt_decrypt_roundtrip(self):
        """Test encrypt-decrypt roundtrip maintains data integrity"""
        original_token = "complex_refresh_token_with_special_chars!@#$%"

        encrypted = encrypt_refresh_token(original_token)
        decrypted = decrypt_refresh_token(encrypted)

        assert decrypted == original_token


class TestGetCurrentUser:
    """Test get_current_user function"""

    @patch("app.core.security.UserService")
    def test_get_current_user_with_cookie_token(
        self, mock_user_service_class, mock_request, sample_user
    ):
        """Test get_current_user with valid cookie token"""
        # Create valid token
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        # Mock request with cookie
        mock_request.cookies.get.return_value = token
        mock_request.headers.get.return_value = None

        # Mock UserService
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.get_user_by_email.return_value = sample_user

        result = get_current_user(mock_request)

        expected = {
            "id": 1,
            "email": "test@example.com",
            "name": "Test User",
            "picture": None,
        }
        assert result == expected
        mock_request.cookies.get.assert_called_once_with("access_token")
        mock_user_service.get_user_by_email.assert_called_once_with("test@example.com")

    @patch("app.core.security.UserService")
    def test_get_current_user_with_bearer_token(
        self, mock_user_service_class, mock_request, sample_user
    ):
        """Test get_current_user with Authorization Bearer token"""
        # Create valid token
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        # Mock request with Authorization header
        mock_request.cookies.get.return_value = None
        mock_request.headers.get.return_value = f"Bearer {token}"

        # Mock UserService
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.get_user_by_email.return_value = sample_user

        result = get_current_user(mock_request)

        expected = {
            "id": 1,
            "email": "test@example.com",
            "name": "Test User",
            "picture": None,
        }
        assert result == expected

    def test_get_current_user_no_token(self, mock_request):
        """Test get_current_user with no token"""
        mock_request.cookies.get.return_value = None
        mock_request.headers.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    def test_get_current_user_invalid_token(self, mock_request):
        """Test get_current_user with invalid token"""
        mock_request.cookies.get.return_value = "invalid.token"
        mock_request.headers.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"

    @patch("app.core.security.UserService")
    def test_get_current_user_no_email_in_token(
        self, mock_user_service_class, mock_request
    ):
        """Test get_current_user with token missing email"""
        # Create token without 'sub' field
        data = {"user_id": "1"}
        token = create_access_token(data)

        mock_request.cookies.get.return_value = token
        mock_request.headers.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"

    @patch("app.core.security.UserService")
    def test_get_current_user_user_not_found(
        self, mock_user_service_class, mock_request
    ):
        """Test get_current_user when user not found in database"""
        # Create valid token
        data = {"sub": "notfound@example.com"}
        token = create_access_token(data)

        mock_request.cookies.get.return_value = token
        mock_request.headers.get.return_value = None

        # Mock UserService - user not found
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.get_user_by_email.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "User not found"


class TestGetCurrentUserOptional:
    """Test get_current_user_optional function"""

    @patch("app.core.security.UserService")
    def test_get_current_user_optional_success(
        self, mock_user_service_class, mock_request, sample_user
    ):
        """Test get_current_user_optional with valid token"""
        # Create valid token
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        mock_request.cookies.get.return_value = token
        mock_request.headers.get.return_value = None

        # Mock UserService
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.get_user_by_email.return_value = sample_user

        result = get_current_user_optional(mock_request)

        expected = {
            "id": 1,
            "email": "test@example.com",
            "name": "Test User",
            "picture": None,
        }
        assert result == expected

    def test_get_current_user_optional_no_token(self, mock_request):
        """Test get_current_user_optional with no token returns None"""
        mock_request.cookies.get.return_value = None
        mock_request.headers.get.return_value = None

        result = get_current_user_optional(mock_request)

        assert result is None

    def test_get_current_user_optional_invalid_token(self, mock_request):
        """Test get_current_user_optional with invalid token returns None"""
        mock_request.cookies.get.return_value = "invalid.token"
        mock_request.headers.get.return_value = None

        result = get_current_user_optional(mock_request)

        assert result is None

    @patch("app.core.security.UserService")
    def test_get_current_user_optional_user_not_found(
        self, mock_user_service_class, mock_request
    ):
        """Test get_current_user_optional when user not found returns None"""
        # Create valid token
        data = {"sub": "notfound@example.com"}
        token = create_access_token(data)

        mock_request.cookies.get.return_value = token
        mock_request.headers.get.return_value = None

        # Mock UserService - user not found
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.get_user_by_email.return_value = None

        result = get_current_user_optional(mock_request)

        assert result is None


class TestGetNewAccessToken:
    """Test get_new_access_token function"""

    @patch("app.core.security.UserService")
    @patch("app.core.security.oauth")
    def test_get_new_access_token_success(
        self, mock_oauth, mock_user_service_class, sample_user
    ):
        """Test get_new_access_token with valid refresh token"""
        # Mock UserService
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.get_user_by_id.return_value = sample_user

        # Mock OAuth client
        mock_client = Mock()
        mock_client.refresh_token.return_value = {
            "access_token": "new_access_token_123"
        }
        mock_oauth.google.server_metadata.return_value = {
            "token_endpoint": "https://oauth.googleapis.com/token"
        }
        mock_oauth.google._get_oauth_client.return_value = mock_client

        result = get_new_access_token(user_id=1)

        assert result == "new_access_token_123"
        mock_user_service.get_user_by_id.assert_called_once_with(1)

    @patch("app.core.security.UserService")
    def test_get_new_access_token_user_not_found(self, mock_user_service_class):
        """Test get_new_access_token when user not found"""
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.get_user_by_id.return_value = None

        result = get_new_access_token(user_id=999)

        assert result is None
        mock_user_service.get_user_by_id.assert_called_once_with(999)

    @patch("app.core.security.UserService")
    def test_get_new_access_token_no_refresh_token(self, mock_user_service_class):
        """Test get_new_access_token when user has no refresh token"""
        user_without_refresh = User(
            id=1,
            email="test@example.com",
            name="Test User",
            google_id="123456789",
            encrypted_refresh_token=None,
        )

        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.get_user_by_id.return_value = user_without_refresh

        result = get_new_access_token(user_id=1)

        assert result is None

    @patch("app.core.security.UserService")
    @patch("app.core.security.oauth")
    def test_get_new_access_token_oauth_error(
        self, mock_oauth, mock_user_service_class, sample_user
    ):
        """Test get_new_access_token when OAuth refresh fails"""
        # Mock UserService
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.get_user_by_id.return_value = sample_user

        # Mock OAuth client that raises exception
        mock_client = Mock()
        mock_client.refresh_token.side_effect = Exception("OAuth error")
        mock_oauth.google.server_metadata.return_value = {
            "token_endpoint": "https://oauth.googleapis.com/token"
        }
        mock_oauth.google._get_oauth_client.return_value = mock_client

        result = get_new_access_token(user_id=1)

        assert result is None
        # Should update user to clear expired refresh token
        mock_user_service.update_user.assert_called_once_with(
            1, {"encrypted_refresh_token": None}
        )


class TestAuthorizationHeader:
    """Test Authorization header parsing"""

    @patch("app.core.security.UserService")
    def test_bearer_token_case_insensitive(
        self, mock_user_service_class, mock_request, sample_user
    ):
        """Test that Bearer token parsing is case insensitive"""
        # Create valid token
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        # Test various case combinations
        test_headers = [
            f"Bearer {token}",
            f"bearer {token}",
            f"BEARER {token}",
            f"BeArEr {token}",
        ]

        for header_value in test_headers:
            mock_request.cookies.get.return_value = None
            mock_request.headers.get.return_value = header_value

            # Mock UserService
            mock_user_service = Mock()
            mock_user_service_class.return_value = mock_user_service
            mock_user_service.get_user_by_email.return_value = sample_user

            result = get_current_user(mock_request)

            assert result["email"] == "test@example.com"

    def test_malformed_authorization_header(self, mock_request):
        """Test malformed Authorization header"""
        mock_request.cookies.get.return_value = None
        mock_request.headers.get.return_value = "InvalidHeader"

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    @patch("app.core.security.UserService")
    def test_bearer_token_with_extra_spaces(
        self, mock_user_service_class, mock_request, sample_user
    ):
        """Test Bearer token with extra spaces is handled correctly"""
        # Create valid token
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        # Header with extra spaces
        mock_request.cookies.get.return_value = None
        mock_request.headers.get.return_value = f"Bearer   {token}   "

        # Mock UserService
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.get_user_by_email.return_value = sample_user

        result = get_current_user(mock_request)

        assert result["email"] == "test@example.com"
