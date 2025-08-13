from datetime import datetime
from unittest.mock import ANY, Mock, patch

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.comments import CommentCreate, CommentOut, CommentUpdate
from app.services.comment_service import CommentService


class TestCommentService:
    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def mock_sentiment_service(self):
        return Mock()

    @pytest.fixture
    def comment_service(self, mock_repository, mock_sentiment_service):
        return CommentService(mock_repository, mock_sentiment_service)

    @pytest.fixture
    def sample_comment_data(self):
        return {
            "id": 1,
            "situation_id": 1,
            "user_id": 1,
            "content": "Tôi thấy tình huống này rất thú vị",
            "sentiment_analysis": {
                "sentiment": "positive",
                "score": 0.5,
                "severity": "low",
            },
            "created_at": datetime.now(),
        }

    def test_get_comments_by_situation_success(
        self, comment_service, mock_repository, sample_comment_data
    ):
        """Test successful comments retrieval by situation."""
        # Arrange
        mock_repository.get_by_situation.return_value = [sample_comment_data]

        # Act
        result = comment_service.get_comments_by_situation(situation_id=1)

        # Assert
        mock_repository.get_by_situation.assert_called_once_with(ANY, 1)
        assert len(result) == 1
        assert isinstance(result[0], CommentOut)
        assert result[0].content == "Tôi thấy tình huống này rất thú vị"

    def test_create_comment_with_sentiment_success(
        self,
        comment_service,
        mock_repository,
        mock_sentiment_service,
        sample_comment_data,
    ):
        """Test successful comment creation with sentiment analysis."""
        # Arrange
        comment_in = CommentCreate(
            situation_id=1, content="Tôi thấy tình huống này rất thú vị"
        )
        user_id = 1
        sentiment_result = {"sentiment": "positive", "score": 0.5, "severity": "low"}
        mock_sentiment_service.analyze_sentiment.return_value = sentiment_result
        mock_repository.create_with_sentiment.return_value = sample_comment_data

        # Act
        result = comment_service.create_comment(comment_in, user_id)

        # Assert
        mock_sentiment_service.analyze_sentiment.assert_called_once_with(
            comment_in.content
        )
        mock_repository.create_with_sentiment.assert_called_once_with(
            ANY, comment_in.dict(), user_id, sentiment_result
        )
        assert isinstance(result, CommentOut)
        assert result.content == "Tôi thấy tình huống này rất thú vị"

    def test_create_comment_sentiment_failure(
        self,
        comment_service,
        mock_repository,
        mock_sentiment_service,
        sample_comment_data,
    ):
        """Test comment creation when sentiment analysis fails."""
        # Arrange
        comment_in = CommentCreate(
            situation_id=1, content="Tôi thấy tình huống này rất thú vị"
        )
        user_id = 1
        mock_sentiment_service.analyze_sentiment.side_effect = Exception(
            "Sentiment analysis failed"
        )
        mock_repository.create_with_sentiment.return_value = sample_comment_data

        # Act
        result = comment_service.create_comment(comment_in, user_id)

        # Assert
        mock_sentiment_service.analyze_sentiment.assert_called_once_with(
            comment_in.content
        )
        mock_repository.create_with_sentiment.assert_called_once_with(
            ANY, comment_in.dict(), user_id
        )
        assert isinstance(result, CommentOut)

    def test_get_comment_success(
        self, comment_service, mock_repository, sample_comment_data
    ):
        """Test successful comment retrieval."""
        # Arrange
        mock_repository.get.return_value = sample_comment_data

        # Act
        result = comment_service.get_comment(comment_id=1)

        # Assert
        mock_repository.get.assert_called_once_with(ANY, 1)
        assert isinstance(result, CommentOut)
        assert result.content == "Tôi thấy tình huống này rất thú vị"

    def test_get_comment_not_found(self, comment_service, mock_repository):
        """Test comment retrieval when comment not found."""
        # Arrange
        mock_repository.get.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            comment_service.get_comment(comment_id=999)

        assert "Comment" in str(exc_info.value)
        assert "999" in str(exc_info.value)

    def test_update_comment_success(
        self, comment_service, mock_repository, sample_comment_data
    ):
        """Test successful comment update."""
        # Arrange
        comment_in = CommentUpdate(content="Updated comment content")
        updated_data = {**sample_comment_data, "content": "Updated comment content"}
        mock_repository.get.return_value = sample_comment_data
        mock_repository.update.return_value = updated_data

        # Act
        result = comment_service.update_comment(comment_id=1, comment_in=comment_in)

        # Assert
        mock_repository.get.assert_called_once_with(ANY, 1)
        mock_repository.update.assert_called_once_with(
            ANY, sample_comment_data, comment_in
        )
        assert result.content == "Updated comment content"

    def test_update_comment_not_found(self, comment_service, mock_repository):
        """Test comment update when comment not found."""
        # Arrange
        mock_repository.get.return_value = None
        comment_in = CommentUpdate(content="Updated content")

        # Act & Assert
        with pytest.raises(NotFoundError):
            comment_service.update_comment(comment_id=999, comment_in=comment_in)

    def test_delete_comment_success(
        self, comment_service, mock_repository, sample_comment_data
    ):
        """Test successful comment deletion."""
        # Arrange
        mock_repository.get.return_value = sample_comment_data
        mock_repository.delete.return_value = sample_comment_data

        # Act
        result = comment_service.delete_comment(comment_id=1)

        # Assert
        mock_repository.get.assert_called_once_with(ANY, 1)
        mock_repository.delete.assert_called_once_with(ANY, 1)
        assert result["message"] == "Comment deleted successfully"

    def test_delete_comment_not_found(self, comment_service, mock_repository):
        """Test comment deletion when comment not found."""
        # Arrange
        mock_repository.get.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            comment_service.delete_comment(comment_id=999)
