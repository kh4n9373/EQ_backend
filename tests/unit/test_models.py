from app.models import Answer, Situation, User


def test_user_model():
    user = User(email="test@example.com", name="Test User", google_id="test_google_id")
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.is_active is True


def test_situation_model():
    situation = Situation(context="Test context", question="Test question?", topic_id=1)
    assert situation.context == "Test context"
    assert situation.question == "Test question?"
    assert situation.is_contributed is None


def test_answer_model():
    scores = {"self_awareness": 8, "empathy": 7}
    reasoning = {"self_awareness": "Good awareness", "empathy": "Shows empathy"}

    answer = Answer(
        situation_id=1, answer_text="Test answer", scores=scores, reasoning=reasoning
    )
    assert answer.answer_text == "Test answer"
    assert answer.scores == scores
    assert answer.reasoning == reasoning
