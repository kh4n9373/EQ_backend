from sqlalchemy.orm import Session

from app.models import Situation, Topic, User


def test_database_connection(db_session: Session):
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.commit()

    found_user = db_session.query(User).filter_by(email="test@example.com").first()
    assert found_user is not None
    assert found_user.name == "Test User"


def test_models_creation(db_session: Session):
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None

    topic = Topic(name="Test Topic")
    db_session.add(topic)
    db_session.commit()
    assert topic.id is not None

    situation = Situation(
        context="Test context", question="Test question?", topic_id=topic.id
    )
    db_session.add(situation)
    db_session.commit()
    assert situation.id is not None
