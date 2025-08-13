from datetime import datetime
from unittest.mock import ANY, Mock

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.topics import TopicCreate, TopicOut, TopicUpdate
from app.services.topic_service import TopicService


class TestTopicService:
    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def topic_service(self, mock_repository):
        return TopicService(mock_repository)

    @pytest.fixture
    def sample_topic_data(self):
        return {
            "id": 1,
            "name": "Tình yêu",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    def test_list_topics_success(
        self, topic_service, mock_repository, sample_topic_data
    ):
        """Test successful topic listing."""
        # Arrange
        mock_repository.get_multi.return_value = [sample_topic_data]

        # Act
        result = topic_service.list_topics()

        # Assert
        mock_repository.get_multi.assert_called_once()
        assert len(result) == 1
        assert isinstance(result[0], TopicOut)
        assert result[0].name == "Tình yêu"

    def test_get_topic_success(self, topic_service, mock_repository, sample_topic_data):
        """Test successful topic retrieval."""
        # Arrange
        mock_repository.get.return_value = sample_topic_data

        # Act
        result = topic_service.get_topic(topic_id=1)

        # Assert
        mock_repository.get.assert_called_once_with(ANY, 1)
        assert isinstance(result, TopicOut)
        assert result.name == "Tình yêu"

    def test_get_topic_not_found(self, topic_service, mock_repository):
        """Test topic retrieval when topic not found."""
        # Arrange
        mock_repository.get.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            topic_service.get_topic(topic_id=999)

        assert "Topic" in str(exc_info.value)
        assert "999" in str(exc_info.value)

    def test_create_topic_success(
        self, topic_service, mock_repository, sample_topic_data
    ):
        """Test successful topic creation."""
        # Arrange
        topic_in = TopicCreate(name="Công sở")
        mock_repository.create.return_value = sample_topic_data

        # Act
        result = topic_service.create_topic(topic_in)

        # Assert
        mock_repository.create.assert_called_once_with(ANY, topic_in)
        assert isinstance(result, TopicOut)
        assert result.name == "Tình yêu"

    def test_update_topic_success(
        self, topic_service, mock_repository, sample_topic_data
    ):
        """Test successful topic update."""
        # Arrange
        topic_in = TopicUpdate(name="Updated Topic")
        updated_data = {**sample_topic_data, "name": "Updated Topic"}
        mock_repository.get.return_value = sample_topic_data
        mock_repository.update.return_value = updated_data

        # Act
        result = topic_service.update_topic(topic_id=1, topic_in=topic_in)

        # Assert
        mock_repository.get.assert_called_once_with(ANY, 1)
        mock_repository.update.assert_called_once_with(ANY, sample_topic_data, topic_in)
        assert result.name == "Updated Topic"

    def test_update_topic_not_found(self, topic_service, mock_repository):
        """Test topic update when topic not found."""
        # Arrange
        mock_repository.get.return_value = None
        topic_in = TopicUpdate(name="Updated Topic")

        # Act & Assert
        with pytest.raises(NotFoundError):
            topic_service.update_topic(topic_id=999, topic_in=topic_in)

    def test_delete_topic_success(
        self, topic_service, mock_repository, sample_topic_data
    ):
        """Test successful topic deletion."""
        # Arrange
        mock_repository.get.return_value = sample_topic_data
        mock_repository.delete.return_value = sample_topic_data

        # Act
        result = topic_service.delete_topic(topic_id=1)

        # Assert
        mock_repository.get.assert_called_once_with(ANY, 1)
        mock_repository.delete.assert_called_once_with(ANY, 1)
        assert result["message"] == "Topic deleted successfully"

    def test_delete_topic_not_found(self, topic_service, mock_repository):
        """Test topic deletion when topic not found."""
        # Arrange
        mock_repository.get.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            topic_service.delete_topic(topic_id=999)
