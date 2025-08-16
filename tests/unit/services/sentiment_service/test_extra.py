from app.services.sentiment_service import SentimentService


def test_sentiment_positive_low():
    s = SentimentService()
    r = s.analyze_sentiment("Tôi rất vui và hạnh phúc")
    assert r["sentiment"] == "positive"
    assert r["severity"] == "low"


def test_sentiment_negative_high():
    s = SentimentService()
    text = "tôi buồn, chán, mệt, stress và bực tức rất vl"
    r = s.analyze_sentiment(text)
    assert r["sentiment"] == "negative"
    assert r["severity"] in ("medium", "high")
    assert r["warning"]


def test_sentiment_neutral():
    s = SentimentService()
    r = s.analyze_sentiment("bình thường")
    assert r["sentiment"] == "neutral"
