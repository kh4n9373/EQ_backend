from datetime import datetime
from unittest.mock import ANY, Mock, patch

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.analysis import AnswerCreate, AnswerOut, SentimentAnalysisRequest
from app.services.analysis_service import AnalysisService


class TestAnalysisService:
    @pytest.fixture
    def mock_answer_repo(self):
        return Mock()

    @pytest.fixture
    def mock_situation_repo(self):
        return Mock()

    @pytest.fixture
    def mock_sentiment_service(self):
        return Mock()

    @pytest.fixture
    def analysis_service(
        self, mock_answer_repo, mock_situation_repo, mock_sentiment_service
    ):
        return AnalysisService(
            mock_answer_repo, mock_situation_repo, mock_sentiment_service
        )

    @pytest.fixture
    def sample_situation_data(self):
        situation = Mock()
        situation.id = 1
        situation.context = "Bạn đang trong một cuộc họp quan trọng"
        situation.question = "Bạn sẽ phản ứng như thế nào?"
        situation.topic_id = 1
        return situation

    @pytest.fixture
    def sample_answer_data(self):
        answer = Mock()
        answer.id = 1
        answer.situation_id = 1
        answer.answer_text = "Tôi sẽ bình tĩnh lắng nghe và đưa ra ý kiến"
        answer.scores = '{"self_awareness": 8, "empathy": 7, "self_regulation": 9, "communication": 8, "decision_making": 7}'
        answer.reasoning = '{"self_awareness": "Tốt", "empathy": "Khá", "self_regulation": "Rất tốt", "communication": "Tốt", "decision_making": "Khá"}'
        answer.created_at = datetime.now()

        # Add situation relationship
        situation = Mock()
        situation.question = "Bạn sẽ phản ứng như thế nào?"
        situation.context = "Bạn đang trong một cuộc họp quan trọng"
        answer.situation = situation

        return answer

    def test_analyze_answer_success(
        self,
        analysis_service,
        mock_situation_repo,
        mock_answer_repo,
        sample_situation_data,
        sample_answer_data,
    ):
        """Test successful answer analysis."""
        # Arrange
        answer_in = AnswerCreate(
            situation_id=1, answer_text="Tôi sẽ bình tĩnh lắng nghe và đưa ra ý kiến"
        )
        scores = {"self_awareness": 8, "empathy": 7}
        reasoning = {"self_awareness": "Tốt", "empathy": "Khá"}

        mock_situation_repo.get.return_value = sample_situation_data
        mock_answer_repo.create_answer.return_value = (sample_answer_data, None)

        with patch(
            "app.services.openai_service.OpenAIService.analyze_eq"
        ) as mock_analyze_eq:
            mock_analyze_eq.return_value = (scores, reasoning)

            # Act
            result = analysis_service.analyze_answer(answer_in)

            # Assert
            mock_situation_repo.get.assert_called_once_with(ANY, 1)
            mock_analyze_eq.assert_called_once_with(
                sample_situation_data.context,
                sample_situation_data.question,
                answer_in.answer_text,
            )
            mock_answer_repo.create_answer.assert_called_once_with(
                ANY, answer_in, scores, reasoning
            )
            assert isinstance(result, AnswerOut)
            assert result.situation_id == 1

    def test_analyze_answer_situation_not_found(
        self, analysis_service, mock_situation_repo
    ):
        """Test answer analysis when situation not found."""
        # Arrange
        answer_in = AnswerCreate(situation_id=999, answer_text="Test answer")
        mock_situation_repo.get.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            analysis_service.analyze_answer(answer_in)

        assert "Situation" in str(exc_info.value)
        assert "999" in str(exc_info.value)

    def test_analyze_sentiment_success(self, analysis_service, mock_sentiment_service):
        """Test successful sentiment analysis."""
        # Arrange
        text_in = SentimentAnalysisRequest(content="Tôi rất vui và hạnh phúc")
        sentiment_result = {"sentiment": "positive", "score": 0.8, "severity": "low"}
        mock_sentiment_service.analyze_sentiment.return_value = sentiment_result

        # Act
        result = analysis_service.analyze_sentiment(text_in)

        # Assert
        mock_sentiment_service.analyze_sentiment.assert_called_once_with(
            text_in.content
        )
        assert result == sentiment_result

    def test_get_answers_by_situation_success(
        self, analysis_service, mock_answer_repo, sample_answer_data
    ):
        """Test successful answers retrieval by situation."""
        # Arrange
        mock_answer_repo.get_by_situation.return_value = [sample_answer_data]

        # Act
        result = analysis_service.get_answers_by_situation(situation_id=1)

        # Assert
        mock_answer_repo.get_by_situation.assert_called_once_with(ANY, 1)
        assert len(result) == 1
        assert isinstance(result[0], AnswerOut)
        assert result[0].situation_id == 1

    def test_safe_json_loads_dict(self, analysis_service):
        """Test safe_json_loads with dictionary input."""
        # Arrange
        test_dict = {"key": "value"}

        # Act
        result = analysis_service.safe_json_loads(test_dict)

        # Assert
        assert result == test_dict

    def test_safe_json_loads_string(self, analysis_service):
        """Test safe_json_loads with valid JSON string."""
        # Arrange
        test_json = '{"key": "value"}'

        # Act
        result = analysis_service.safe_json_loads(test_json)

        # Assert
        assert result == {"key": "value"}

    def test_safe_json_loads_invalid_string(self, analysis_service):
        """Test safe_json_loads with invalid JSON string."""
        # Arrange
        test_invalid_json = '{"key": "value"'  # Missing closing brace

        # Act
        result = analysis_service.safe_json_loads(test_invalid_json)

        # Assert
        assert result == {}

    def test_safe_json_loads_other_types(self, analysis_service):
        """Test safe_json_loads with other data types."""
        # Arrange
        test_list = [1, 2, 3]
        test_int = 42

        # Act
        result_list = analysis_service.safe_json_loads(test_list)
        result_int = analysis_service.safe_json_loads(test_int)

        # Assert
        assert result_list == {}
        assert result_int == {}

    def test_analyze_answer_with_openai_error(
        self,
        analysis_service,
        mock_situation_repo,
        mock_answer_repo,
        sample_situation_data,
        sample_answer_data,
    ):
        """Test answer analysis when OpenAI analysis fails."""
        # Arrange
        answer_in = AnswerCreate(situation_id=1, answer_text="Test answer")

        mock_situation_repo.get.return_value = sample_situation_data
        mock_answer_repo.create_answer.return_value = (sample_answer_data, None)

        with patch(
            "app.services.openai_service.OpenAIService.analyze_eq"
        ) as mock_analyze_eq:
            mock_analyze_eq.side_effect = Exception("OpenAI API Error")

            # Act & Assert
            with pytest.raises(Exception):
                analysis_service.analyze_answer(answer_in)

    def test_get_answers_by_situation_empty_result(
        self, analysis_service, mock_answer_repo
    ):
        """Test answers retrieval when no answers exist."""
        # Arrange
        mock_answer_repo.get_by_situation.return_value = []

        # Act
        result = analysis_service.get_answers_by_situation(situation_id=1)

        # Assert
        assert result == []
