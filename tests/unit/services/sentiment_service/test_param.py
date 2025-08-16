import pytest

from app.services.sentiment_service import SentimentService


@pytest.fixture()
def svc():
    return SentimentService()


@pytest.mark.parametrize(
    "text, expected_sentiment",
    [
        ("Hôm nay tôi rất vui và hạnh phúc", "positive"),
        ("Tôi cảm thấy chán và mệt", "negative"),
        ("Hôm nay trời mát", "neutral"),
    ],
)
def test_basic_sentiment_labels(svc, text, expected_sentiment):
    result = svc.analyze_sentiment(text)
    assert result["sentiment"] == expected_sentiment


def test_empty_text_is_neutral_with_zero_score(svc):
    result = svc.analyze_sentiment("")
    assert result["sentiment"] == "neutral"
    assert result["score"] == 0


@pytest.mark.parametrize(
    "text, expected",
    [
        ("vui", ("positive", "low")),  # ~ +1/1 > 0.1
        ("chán", ("negative", "medium")),  # ~ -1/1 < -0.1
        ("vui chán", ("neutral", "low")),  # 0
    ],
)
def test_thresholds_and_severity(svc, text, expected):
    sentiment, severity = expected
    result = svc.analyze_sentiment(text)
    assert result["sentiment"] == sentiment
    assert result["severity"] == severity


def test_high_severity_when_many_negative_keywords(svc):
    text = "Tôi rất chán, mệt, bế tắc và thất vọng, mọi thứ thật tồi tệ"
    result = svc.analyze_sentiment(text)
    assert result["sentiment"] == "negative"
    assert result["severity"] == "high"
    assert result["warning"]  # warning should be present for high severity


def test_analysis_fields_exist(svc):
    text = "Tôi cảm thấy lạc quan và may mắn"
    result = svc.analyze_sentiment(text)
    assert set(result.keys()) >= {
        "sentiment",
        "score",
        "severity",
        "suggestions",
        "analysis",
    }
    assert set(result["analysis"].keys()) == {
        "positive_words",
        "negative_words",
        "total_words",
    }
