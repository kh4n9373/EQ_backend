from types import SimpleNamespace

import pytest

from app.core.exceptions import NotFoundError
from app.services.analysis_service import AnalysisService


class DummySituationRepo:
    def __init__(self, situation=None):
        self._situation = situation or SimpleNamespace(
            id=1, question="Q?", context="CTX"
        )

    def get(self, db, sid):
        return self._situation if sid == 1 else None


class DummyAnswerRepo:
    def __init__(self, answers=None):
        self._answers = answers or []

    def create_answer(self, db, answer, scores, reasoning):
        obj = SimpleNamespace(
            id=1,
            situation_id=answer.situation_id,
            answer_text=answer.answer_text,
            scores=scores,
            reasoning=reasoning,
            created_at=None,
        )
        return obj, "Q?"

    def get_by_situation(self, db, sid):
        return self._answers


class DummyOpenAI:
    def __init__(self, payload=None):
        self.payload = payload or ({"self_awareness": 7}, {"self_awareness": "ok"})

    def analyze_eq(self, c, q, a):
        return self.payload


class DummySentiment:
    def analyze_sentiment(self, content):
        return {"sentiment": "positive", "score": 0.2}


class AnswerIn:
    def __init__(self, situation_id=1, answer_text="A"):
        self.situation_id = situation_id
        self.answer_text = answer_text


class TextIn:
    def __init__(self, content="vui"):
        self.content = content


def test_safe_json_loads_variants():
    svc = AnalysisService()
    assert svc.safe_json_loads({"a": 1}) == {"a": 1}
    assert svc.safe_json_loads("{" "a" ":1}") == {"a": 1}
    assert svc.safe_json_loads("not json") == {}
    assert svc.safe_json_loads(123) == {}


def test_analyze_answer_ok(monkeypatch):
    svc = AnalysisService(
        answer_repo=DummyAnswerRepo(),
        situation_repo=DummySituationRepo(),
        sentiment_service=DummySentiment(),
    )
    monkeypatch.setattr(svc, "openai_service", DummyOpenAI())

    out = svc.analyze_answer(AnswerIn())
    assert out.scores["self_awareness"] == 7
    assert out.question == "Q?"
    assert out.context == "CTX"


def test_analyze_answer_situation_not_found(monkeypatch):
    svc = AnalysisService(
        answer_repo=DummyAnswerRepo(),
        situation_repo=DummySituationRepo(situation=None),
    )
    with pytest.raises(NotFoundError):
        svc.analyze_answer(AnswerIn(situation_id=999))


def test_get_answers_by_situation_maps_fields(monkeypatch):
    ans = SimpleNamespace(
        id=2,
        situation_id=1,
        answer_text="A",
        scores={"x": 1},
        reasoning={"x": "r"},
        created_at=None,
        situation=SimpleNamespace(question="Q?", context="CTX"),
    )
    svc = AnalysisService(
        answer_repo=DummyAnswerRepo(answers=[ans]),
        situation_repo=DummySituationRepo(),
    )
    out = svc.get_answers_by_situation(1)
    assert len(out) == 1
    assert out[0].question == "Q?" and out[0].context == "CTX"


def test_analyze_sentiment_passthrough():
    svc = AnalysisService(sentiment_service=DummySentiment())
    out = svc.analyze_sentiment(TextIn("vui"))
    assert out["sentiment"] == "positive"
