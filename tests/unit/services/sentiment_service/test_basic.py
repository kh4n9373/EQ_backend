import pytest

from app.services.sentiment_service import SentimentService


class TestSentimentService:
    @pytest.fixture
    def sentiment_service(self):
        return SentimentService()

    def test_analyze_sentiment_positive(self, sentiment_service):
        """Test sentiment analysis with positive content."""
        # Arrange
        content = "Tôi rất vui và hạnh phúc với cuộc sống hiện tại"

        # Act
        result = sentiment_service.analyze_sentiment(content)

        # Assert
        assert result["sentiment"] == "positive"
        assert result["score"] > 0
        assert result["severity"] == "low"
        assert "suggestions" in result
        assert "analysis" in result

    def test_analyze_sentiment_negative(self, sentiment_service):
        """Test sentiment analysis with negative content."""
        # Arrange
        content = "Tôi rất chán và mệt mỏi với công việc này"

        # Act
        result = sentiment_service.analyze_sentiment(content)

        # Assert
        assert result["sentiment"] == "negative"
        assert result["score"] < 0
        assert "warning" in result
        assert "suggestions" in result

    def test_analyze_sentiment_negative_high_severity(self, sentiment_service):
        """Test sentiment analysis with high severity negative content."""
        # Arrange
        content = "Tôi rất chán mệt stress khó chịu bực tức giận buồn thất vọng"

        # Act
        result = sentiment_service.analyze_sentiment(content)

        # Assert
        assert result["sentiment"] == "negative"
        assert result["severity"] == "high"
        assert "⚠️" in result["warning"]

    def test_analyze_sentiment_neutral(self, sentiment_service):
        """Test sentiment analysis with neutral content."""
        # Arrange
        content = "Hôm nay tôi đi làm và về nhà"

        # Act
        result = sentiment_service.analyze_sentiment(content)

        # Assert
        assert result["sentiment"] == "neutral"
        assert abs(result["score"]) <= 0.1
        assert result["severity"] == "low"

    def test_analyze_sentiment_empty_content(self, sentiment_service):
        """Test sentiment analysis with empty content."""
        # Arrange
        content = ""

        # Act
        result = sentiment_service.analyze_sentiment(content)

        # Assert
        assert result["sentiment"] == "neutral"
        assert result["score"] == 0
        assert result["analysis"]["total_words"] == 0

    def test_analyze_sentiment_mixed_content(self, sentiment_service):
        """Test sentiment analysis with mixed positive and negative content."""
        # Arrange
        content = "Tôi vui vì được nghỉ nhưng buồn vì phải làm bài tập"

        # Act
        result = sentiment_service.analyze_sentiment(content)

        # Assert
        assert "sentiment" in result
        assert "score" in result
        assert "analysis" in result
        assert result["analysis"]["positive_words"] > 0
        assert result["analysis"]["negative_words"] > 0

    def test_sentiment_keywords_detection(self, sentiment_service):
        """Test that sentiment keywords are properly detected."""
        # Arrange
        positive_content = "vui hạnh phúc tốt tuyệt thích yêu"
        negative_content = "chán mệt stress khó chịu bực tức"

        # Act
        positive_result = sentiment_service.analyze_sentiment(positive_content)
        negative_result = sentiment_service.analyze_sentiment(negative_content)

        # Assert
        assert positive_result["sentiment"] == "positive"
        assert negative_result["sentiment"] == "negative"
        assert positive_result["analysis"]["positive_words"] > 0
        assert negative_result["analysis"]["negative_words"] > 0

    def test_sentiment_suggestions_generation(self, sentiment_service):
        """Test that appropriate suggestions are generated."""
        # Arrange
        negative_content = "Tôi rất chán và mệt mỏi"

        # Act
        result = sentiment_service.analyze_sentiment(negative_content)

        # Assert
        assert "suggestions" in result
        assert len(result["suggestions"]) > 0
        assert all(isinstance(suggestion, str) for suggestion in result["suggestions"])

    def test_sentiment_analysis_structure(self, sentiment_service):
        """Test that sentiment analysis returns correct structure."""
        # Arrange
        content = "Test content"

        # Act
        result = sentiment_service.analyze_sentiment(content)

        # Assert
        required_keys = ["sentiment", "score", "severity", "suggestions", "analysis"]
        for key in required_keys:
            assert key in result

        analysis_keys = ["positive_words", "negative_words", "total_words"]
        for key in analysis_keys:
            assert key in result["analysis"]

        assert isinstance(result["score"], (int, float))
        assert result["sentiment"] in ["positive", "negative", "neutral"]
        assert result["severity"] in ["low", "medium", "high"]
