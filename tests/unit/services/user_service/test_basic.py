from datetime import datetime, timezone
from unittest.mock import ANY, Mock, patch

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.users import UserProfileOut, UserShortOut
from app.services.user_service import UserService


class TestUserService:
    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def user_service(self, mock_repository):
        return UserService(mock_repository)

    @pytest.fixture
    def sample_user_data(self):
        user = Mock()
        user.id = 1
        user.email = "test@example.com"
        user.name = "Test User"
        user.picture = "https://example.com/pic.jpg"
        user.bio = "Test bio"
        user.google_id = "123456"
        user.is_active = True
        user.created_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        return user

    def test_list_users_success(self, user_service, mock_repository, sample_user_data):
        """Test successful user listing."""
        # Arrange
        mock_repository.list_users.return_value = [sample_user_data]

        # Act
        result = user_service.list_users(search="test", page=1, size=10)

        # Assert
        mock_repository.list_users.assert_called_once_with(
            ANY, search="test", page=1, size=10
        )
        assert len(result) == 1
        assert result[0].name == "Test User"

    def test_search_users_empty_query(self, user_service, mock_repository):
        """Test search users with empty query returns empty list."""
        # Act
        result = user_service.search_users("", limit=10)

        # Assert
        assert result == []
        mock_repository.search_users_by_name.assert_not_called()

    def test_search_users_short_query(self, user_service, mock_repository):
        """Test search users with short query returns empty list."""
        # Act
        result = user_service.search_users("a", limit=10)

        # Assert
        assert result == []
        mock_repository.search_users_by_name.assert_not_called()

    def test_search_users_success(
        self, user_service, mock_repository, sample_user_data
    ):
        """Test successful user search."""
        # Arrange
        mock_repository.search_users_by_name.return_value = [sample_user_data]

        # Act
        result = user_service.search_users("test", limit=10)

        # Assert
        mock_repository.search_users_by_name.assert_called_once_with(
            ANY, query="test", limit=10
        )
        assert len(result) == 1
        assert isinstance(result[0], UserShortOut)
        assert result[0].name == "Test User"

    def test_get_user_profile_success(
        self, user_service, mock_repository, sample_user_data
    ):
        """Test successful user profile retrieval."""
        # Arrange
        mock_repository.get_user_by_id.return_value = sample_user_data

        # Act
        result = user_service.get_user_profile(user_id=1)

        # Assert
        mock_repository.get_user_by_id.assert_called_once_with(ANY, user_id=1)
        assert isinstance(result, UserProfileOut)
        assert result.name == "Test User"
        assert result.email == "test@example.com"

    def test_get_user_profile_not_found(self, user_service, mock_repository):
        """Test user profile retrieval when user not found."""
        # Arrange
        mock_repository.get_user_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            user_service.get_user_profile(user_id=999)

        assert "User" in str(exc_info.value)
        assert "999" in str(exc_info.value)

    def test_get_user_by_email_success(
        self, user_service, mock_repository, sample_user_data
    ):
        """Test successful user retrieval by email."""
        # Arrange
        mock_repository.get_user_by_email.return_value = sample_user_data

        # Act
        result = user_service.get_user_by_email("test@example.com")

        # Assert
        mock_repository.get_user_by_email.assert_called_once_with(
            ANY, email="test@example.com"
        )
        assert result.email == "test@example.com"

    def test_get_user_by_email_not_found(self, user_service, mock_repository):
        """Test user retrieval by email when user not found."""
        # Arrange
        mock_repository.get_user_by_email.return_value = None

        # Act
        result = user_service.get_user_by_email("nonexistent@example.com")

        # Assert
        assert result is None

    def test_create_user_success(self, user_service, mock_repository, sample_user_data):
        """Test successful user creation."""
        # Arrange
        user_data = {"email": "new@example.com", "name": "New User", "google_id": "789"}
        mock_repository.create_user.return_value = sample_user_data

        # Act
        result = user_service.create_user(user_data)

        # Assert
        mock_repository.create_user.assert_called_once_with(ANY, user_data=user_data)
        assert result.name == "Test User"

    def test_update_user_success(self, user_service, mock_repository, sample_user_data):
        """Test successful user update."""
        # Arrange
        update_data = {"name": "Updated Name"}
        mock_repository.get_user_by_id.return_value = sample_user_data
        updated_user = Mock()
        updated_user.id = 1
        updated_user.email = "test@example.com"
        updated_user.name = "Updated Name"
        updated_user.picture = "https://example.com/pic.jpg"
        updated_user.bio = "Test bio"
        updated_user.google_id = "123456"
        updated_user.is_active = True
        updated_user.created_at = datetime.now(timezone.utc)
        updated_user.updated_at = datetime.now(timezone.utc)
        mock_repository.update_user.return_value = updated_user

        # Act
        result = user_service.update_user(user_id=1, update_data=update_data)

        # Assert
        mock_repository.get_user_by_id.assert_called_once_with(ANY, user_id=1)
        mock_repository.update_user.assert_called_once_with(
            ANY, user=sample_user_data, update_data=update_data
        )
        assert result.name == "Updated Name"

    def test_update_user_not_found(self, user_service, mock_repository):
        """Test user update when user not found."""
        # Arrange
        mock_repository.get_user_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            user_service.update_user(user_id=999, update_data={"name": "New Name"})

    def test_update_user_refresh_token_success(
        self, user_service, mock_repository, sample_user_data
    ):
        """Test successful refresh token update."""
        # Arrange
        mock_repository.update_user_refresh_token.return_value = sample_user_data

        # Act
        result = user_service.update_user_refresh_token(
            user_id=1, refresh_token="new_token"
        )

        # Assert
        mock_repository.update_user_refresh_token.assert_called_once_with(
            ANY, user_id=1, refresh_token="new_token"
        )
        assert result.id == 1
