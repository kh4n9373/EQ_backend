import json
import types

import pytest

from app.services.openai_service import OpenAIService


class DummyChoice:
    def __init__(self, content: str):
        self.message = types.SimpleNamespace(content=content)


class DummyResponse:
    def __init__(self, content: str):
        self.choices = [DummyChoice(content)]


class DummyClient:
    class chat:
        class completions:
            @staticmethod
            def create(
                model, messages, temperature
            ):  # noqa: D401 (signature must match)
                raise NotImplementedError


def test_analyze_eq_ok(monkeypatch):
    svc = OpenAIService()

    def fake_create(**kwargs):
        payload = {
            "scores": {
                "self_awareness": 7,
                "empathy": 8,
                "self_regulation": 6,
                "communication": 7,
                "decision_making": 7,
            },
            "reasoning": {
                "self_awareness": "ok",
                "empathy": "ok",
                "self_regulation": "ok",
                "communication": "ok",
                "decision_making": "ok",
            },
        }
        return DummyResponse(content=json.dumps(payload))

    # Patch openai.OpenAI().chat.completions.create
    import openai

    original_openai = openai.OpenAI

    class FakeOpenAI:
        def __init__(self, *args, **kwargs):
            pass

        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    return fake_create(**kwargs)

    monkeypatch.setattr(openai, "OpenAI", FakeOpenAI)

    scores, reasoning = svc.analyze_eq("s", "q", "a")
    assert scores["empathy"] == 8
    assert reasoning["communication"] == "ok"

    # restore if needed
    monkeypatch.setattr(openai, "OpenAI", original_openai)


def test_analyze_eq_parse_error(monkeypatch):
    svc = OpenAIService()

    # Return non-JSON content
    def fake_create(**kwargs):
        return DummyResponse(content="not a json result")

    import openai

    class FakeOpenAI:
        def __init__(self, *args, **kwargs):
            pass

        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    return fake_create(**kwargs)

    monkeypatch.setattr(openai, "OpenAI", FakeOpenAI)

    result = svc.analyze_eq("s", "q", "a")
    # On error path current implementation returns a dict with fallback
    assert isinstance(result, dict)
    assert "scores" in result and "reasoning" in result


def test_analyze_eq_client_exception(monkeypatch):
    svc = OpenAIService()

    def fake_create(**kwargs):
        raise RuntimeError("network down")

    import openai

    class FakeOpenAI:
        def __init__(self, *args, **kwargs):
            pass

        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    return fake_create(**kwargs)

    monkeypatch.setattr(openai, "OpenAI", FakeOpenAI)

    result = svc.analyze_eq("s", "q", "a")
    assert isinstance(result, dict)
    assert "error" in result
