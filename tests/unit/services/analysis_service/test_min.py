from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services.analysis_service import AnalysisService


def make_answer_create(situation_id: int, text: str):
    # Minimal shape compatible with pydantic model usage in repo
    return SimpleNamespace(situation_id=situation_id, answer_text=text)


def test_analyze_answer_happy_path(monkeypatch):
    # Mock repos and openai path
    answer_repo = Mock()
    situation_repo = Mock()
    service = AnalysisService(
        answer_repo=answer_repo, situation_repo=situation_repo, sentiment_service=Mock()
    )

    # Situation lookup returns object with context/question
    situation_repo.get.return_value = SimpleNamespace(id=1, context="ctx", question="q")

    # Stub openai analyze_eq
    monkeypatch.setattr(
        service,
        "openai_service",
        SimpleNamespace(analyze_eq=lambda c, q, a: ({"empathy": 7}, {"empathy": "ok"})),
    )

    # Repo create returns answer-like object
    db_answer = SimpleNamespace(
        id=10,
        situation_id=1,
        answer_text="hello",
        scores={"empathy": 7},
        reasoning={"empathy": "ok"},
        created_at=None,
        situation=None,
    )
    # AnalysisService branches to create_answer (not create_answer_with_analysis) when repo is not AnswerRepository instance
    answer_repo.create_answer.return_value = db_answer

    out = service.analyze_answer(make_answer_create(1, "hello"))
    assert out.id == 10
    assert out.scores["empathy"] == 7
    assert out.reasoning["empathy"] == "ok"
    assert out.context == "ctx"
    assert out.question == "q"


def test_analyze_answer_situation_not_found():
    service = AnalysisService(
        answer_repo=Mock(), situation_repo=Mock(), sentiment_service=Mock()
    )
    service.situation_repo.get.return_value = None
    with pytest.raises(Exception):
        service.analyze_answer(make_answer_create(999, "x"))


def test_safe_json_loads_variants():
    service = AnalysisService(
        answer_repo=Mock(), situation_repo=Mock(), sentiment_service=Mock()
    )
    assert service.safe_json_loads({"k": 1}) == {"k": 1}
    assert service.safe_json_loads('{"k":1}') == {"k": 1}
    assert service.safe_json_loads("{bad json") == {}
    assert service.safe_json_loads(123) == {}


def test_get_answers_by_situation_shapes_list():
    answer_repo = Mock()
    service = AnalysisService(
        answer_repo=answer_repo, situation_repo=Mock(), sentiment_service=Mock()
    )
    ans = SimpleNamespace(
        id=1,
        situation_id=2,
        answer_text="a",
        scores={"empathy": 5},
        reasoning={"empathy": "r"},
        created_at=None,
        situation=SimpleNamespace(question="q", context="c"),
    )
    answer_repo.get_by_situation.return_value = [ans]
    out = service.get_answers_by_situation(2)
    assert len(out) == 1
    assert out[0].scores["empathy"] == 5
    assert out[0].question == "q"
