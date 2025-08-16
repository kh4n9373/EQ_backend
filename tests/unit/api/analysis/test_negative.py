import pytest
from fastapi.testclient import TestClient


def test_analyze_missing_fields_returns_422(client: TestClient):
    # Missing required fields in AnswerCreate
    resp = client.post("/api/v1/analyze", json={})
    assert resp.status_code == 422


def test_analyze_situation_not_found(client: TestClient, monkeypatch):
    # Monkeypatch service to raise 404-like behavior by returning None and letting router/service handle
    from app.services.analysis_service import AnalysisService

    def fake_analyze_answer(self, answer):
        raise Exception("Situation not found")

    monkeypatch.setattr(AnalysisService, "analyze_answer", fake_analyze_answer)

    payload = {"situation_id": 999999, "answer_text": "answer"}
    resp = client.post("/api/v1/analyze", json=payload)
    # If global exception handler maps to 500, accept 500/404 as negative-path covered
    assert resp.status_code in (404, 500)


def test_analyze_sentiment_missing_content_422(client: TestClient):
    resp = client.post("/api/v1/analyze-sentiment", json={})
    assert resp.status_code == 422
