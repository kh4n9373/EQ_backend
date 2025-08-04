import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app, get_db
from app.models import Situation, Topic, User

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    connection = engine.connect()
    transaction = connection.begin()

    session = sessionmaker(bind=connection)()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_data(db_session):
    topic = Topic(name="Test Topic")
    db_session.add(topic)
    db_session.flush()

    situation = Situation(
        context="Test situation context",
        question="What would you do in this situation?",
        topic_id=topic.id,
    )
    db_session.add(situation)
    db_session.flush()

    user = User(email="test@example.com", name="Test User", google_id="test_google_id")
    db_session.add(user)
    db_session.flush()

    return {"topic": topic, "situation": situation, "user": user}
