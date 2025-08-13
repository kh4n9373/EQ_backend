from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.deps import get_current_user_dep, get_db
from app.core.config import settings
from app.core.database import Base
from app.core.security import create_access_token
from app.core.security import get_current_user as real_get_current_user
from app.main_v2 import app
from app.models import Answer, Comment, Situation, Topic, User

# Test database setup - use SQLite in-memory for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

# Ensure all services use the testing SessionLocal by monkeypatching SessionLocal symbol imports
import app.core.database as core_db_module
from app.core.database import SessionLocal as RealSessionLocal

core_db_module.SessionLocal = TestingSessionLocal

import app.services.analysis_service as analysis_service_module
import app.services.comment_service as comment_service_module
import app.services.situation_service as situation_service_module
import app.services.topic_service as topic_service_module

# Also patch direct imports in services that may have imported SessionLocal earlier
import app.services.user_service as user_service_module

user_service_module.SessionLocal = TestingSessionLocal
situation_service_module.SessionLocal = TestingSessionLocal
analysis_service_module.SessionLocal = TestingSessionLocal
comment_service_module.SessionLocal = TestingSessionLocal
topic_service_module.SessionLocal = TestingSessionLocal


# Override auth dependency: require Bearer token and resolve user from DB; else 401
def override_get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Return a lightweight current user derived from token for tests
    return {
        "id": 1,
        "email": email,
        "name": "Test User",
        "picture": "https://example.com/pic.jpg",
    }


app.dependency_overrides[get_current_user_dep] = override_get_current_user
# Also override the underlying security function used by Depends
app.dependency_overrides[real_get_current_user] = override_get_current_user

# NOTE: Do not override authentication dependency so unauthorized tests work correctly.


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for testing."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create database session for testing."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def clean_database(db_session):
    """Clean database before each test to ensure isolation."""
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
    yield


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    # ensure uniqueness per test run
    from uuid import uuid4

    unique_suffix = uuid4().hex
    user = User(
        google_id=f"test_google_id_{unique_suffix}",
        email=f"test_{unique_suffix}@example.com",
        name="Test User",
        picture="https://example.com/pic.jpg",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_topic(db_session):
    """Create a sample topic for testing."""
    from uuid import uuid4

    unique_suffix = uuid4().hex
    topic = Topic(name=f"Test Topic {unique_suffix}")
    db_session.add(topic)
    db_session.commit()
    db_session.refresh(topic)
    return topic


@pytest.fixture
def sample_situation(db_session, sample_topic):
    """Create a sample situation for testing."""
    situation = Situation(
        question="What would you do in this situation?",
        context="This is a test situation context.",
        topic_id=sample_topic.id,
    )
    db_session.add(situation)
    db_session.commit()
    db_session.refresh(situation)
    return situation


@pytest.fixture
def auth_headers(sample_user):
    """Create authentication headers for testing."""
    access_token = create_access_token(data={"sub": sample_user.email})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def mock_get_current_user(sample_user):
    """Mock the get_current_user dependency."""
    with patch("app.api.v1.deps.get_current_user_dep") as mock:
        mock.return_value = sample_user
        yield mock
