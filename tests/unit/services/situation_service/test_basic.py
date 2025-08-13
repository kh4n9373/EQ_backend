from datetime import datetime
from unittest.mock import ANY, Mock

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.situations import (
    SituationContributeOut,
    SituationCreate,
    SituationOut,
    SituationUpdate,
)
from app.services.situation_service import SituationService


class TestSituationService:
    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def situation_service(self, mock_repository):
        return SituationService(mock_repository)

    @pytest.fixture
    def sample_situation_data(self):
        situation = Mock()
        situation.id = 1
        situation.topic_id = 1
        situation.user_id = 1
        situation.context = "Bạn đang trong một cuộc họp quan trọng"
        situation.question = "Bạn sẽ phản ứng như thế nào?"
        situation.image_url = "https://example.com/image.jpg"
        situation.created_at = (
            datetime.now().isoformat()
        )  # Convert to string for Pydantic
        return situation

    def test_get_situations_by_topic_success(
        self, situation_service, mock_repository, sample_situation_data
    ):
        """Test successful situations retrieval by topic."""
        # Arrange
        mock_repository.get_by_topic.return_value = [sample_situation_data]

        # Act
        result = situation_service.get_situations_by_topic(topic_id=1)

        # Assert
        mock_repository.get_by_topic.assert_called_once_with(ANY, 1)
        assert len(result) == 1
        assert isinstance(result[0], SituationOut)
        assert result[0].context == "Bạn đang trong một cuộc họp quan trọng"

    def test_get_contributed_situations_success(
        self, situation_service, mock_repository, sample_situation_data
    ):
        """Test successful contributed situations retrieval."""
        # Arrange
        mock_repository.get_contributed_situations.return_value = [
            sample_situation_data
        ]

        # Act
        result = situation_service.get_contributed_situations()

        # Assert
        mock_repository.get_contributed_situations.assert_called_once_with(ANY)
        assert len(result) == 1
        assert isinstance(result[0], SituationOut)

    def test_get_situation_success(
        self, situation_service, mock_repository, sample_situation_data
    ):
        """Test successful situation retrieval."""
        # Arrange
        mock_repository.get.return_value = sample_situation_data

        # Act
        result = situation_service.get_situation(situation_id=1)

        # Assert
        mock_repository.get.assert_called_once_with(ANY, 1)
        assert isinstance(result, SituationOut)
        assert result.context == "Bạn đang trong một cuộc họp quan trọng"

    def test_get_situation_not_found(self, situation_service, mock_repository):
        """Test situation retrieval when situation not found."""
        # Arrange
        mock_repository.get.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            situation_service.get_situation(situation_id=999)

        assert "Situation" in str(exc_info.value)
        assert "999" in str(exc_info.value)

    def test_create_situation_success(
        self, situation_service, mock_repository, sample_situation_data
    ):
        """Test successful situation creation."""
        # Arrange
        situation_in = SituationCreate(
            context="Test context", question="Test question", topic_id=1
        )
        mock_repository.create.return_value = sample_situation_data

        # Act
        result = situation_service.create_situation(situation_in)

        # Assert
        mock_repository.create.assert_called_once_with(ANY, situation_in)
        assert isinstance(result, SituationOut)
        assert result.context == "Bạn đang trong một cuộc họp quan trọng"

    def test_contribute_situation_success(
        self, situation_service, mock_repository, sample_situation_data
    ):
        """Test successful situation contribution."""
        # Arrange
        situation_data = {
            "context": "Test context",
            "question": "Test question",
            "topic_id": 1,
            "image_url": "https://example.com/image.jpg",
        }
        user_id = 1
        mock_repository.create_contributed_situation.return_value = (
            sample_situation_data
        )

        # Act
        result = situation_service.contribute_situation(situation_data, user_id)

        # Assert
        mock_repository.create_contributed_situation.assert_called_once_with(
            ANY, situation_data, user_id
        )
        assert isinstance(result, SituationContributeOut)
        assert result.user_id == 1

    def test_update_situation_success(
        self, situation_service, mock_repository, sample_situation_data
    ):
        """Test successful situation update."""
        # Arrange
        situation_in = SituationUpdate(context="Updated context")
        updated_data = Mock()
        updated_data.id = 1
        updated_data.topic_id = 1
        updated_data.user_id = 1
        updated_data.context = "Updated context"
        updated_data.question = "Bạn sẽ phản ứng như thế nào?"
        updated_data.image_url = "https://example.com/image.jpg"
        updated_data.created_at = datetime.now().isoformat()
        mock_repository.get.return_value = sample_situation_data
        mock_repository.update.return_value = updated_data

        # Act
        result = situation_service.update_situation(
            situation_id=1, situation_in=situation_in
        )

        # Assert
        mock_repository.get.assert_called_once_with(ANY, 1)
        mock_repository.update.assert_called_once_with(
            ANY, sample_situation_data, situation_in
        )
        assert result.context == "Updated context"

    def test_update_situation_not_found(self, situation_service, mock_repository):
        """Test situation update when situation not found."""
        # Arrange
        mock_repository.get.return_value = None
        situation_in = SituationUpdate(context="Updated context")

        # Act & Assert
        with pytest.raises(NotFoundError):
            situation_service.update_situation(
                situation_id=999, situation_in=situation_in
            )

    def test_delete_situation_success(
        self, situation_service, mock_repository, sample_situation_data
    ):
        """Test successful situation deletion."""
        # Arrange
        mock_repository.get.return_value = sample_situation_data
        mock_repository.delete.return_value = sample_situation_data

        # Act
        result = situation_service.delete_situation(situation_id=1)

        # Assert
        mock_repository.get.assert_called_once_with(ANY, 1)
        mock_repository.delete.assert_called_once_with(ANY, 1)
        assert result["message"] == "Situation deleted successfully"

    def test_delete_situation_not_found(self, situation_service, mock_repository):
        """Test situation deletion when situation not found."""
        # Arrange
        mock_repository.get.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            situation_service.delete_situation(situation_id=999)
