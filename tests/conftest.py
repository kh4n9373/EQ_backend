import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.deps import get_db
from app.core.database import Base
from app.main import app
from app.seed_data import seed
from tests.fixtures.test_data import (
    sample_analysis_request,
    sample_analysis_response,
    sample_answers,
    sample_comments,
    sample_jwt_payload,
    sample_oauth_data,
    sample_sentiment_request,
    sample_sentiment_response,
    sample_situations,
    sample_topics,
    sample_users,
    unique_answer_data,
    unique_comment_data,
    unique_situation_data,
    unique_topic_data,
    unique_user_data,
)

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://eq_user:eq_pass@localhost:5432/eq_test"
)

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create database tables once for all tests"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create database session for testing"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def setup_test_data(db_session):
    """Setup database with sample data"""
    # seed() manages its own SessionLocal; it does not accept a session parameter
    seed()
    return db_session


@pytest.fixture
def client(db_session):
    """Create test client with database session"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# Mock fixtures
@pytest.fixture
def mock_oauth():
    """Mock OAuth for testing"""
    with patch("app.core.security.oauth") as mock:
        mock.google.parse_id_token.return_value = {
            "sub": "google_123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/pic.jpg",
        }
        yield mock


@pytest.fixture
def mock_openai():
    """Mock OpenAI for testing"""
    with patch("app.services.analysis_service.analyze_eq") as mock:
        mock.return_value = {
            "scores": {
                "self_awareness": 8,
                "self_management": 7,
                "social_awareness": 6,
                "relationship_management": 8,
                "responsible_decision_making": 7,
            },
            "reasoning": {
                "self_awareness": "Good emotional recognition",
                "self_management": "Effective self-control",
                "social_awareness": "Basic empathy shown",
                "relationship_management": "Strong communication skills",
                "responsible_decision_making": "Ethical decision making",
            },
        }
        yield mock


@pytest.fixture
def mock_services():
    """Mock all services for testing"""
    with (
        patch("app.api.v1.endpoints.users.UserService") as mock_user_service,
        patch("app.api.v1.endpoints.topics.TopicService") as mock_topic_service,
        patch(
            "app.api.v1.endpoints.situations.SituationService"
        ) as mock_situation_service,
        patch("app.api.v1.endpoints.comments.CommentService") as mock_comment_service,
        patch("app.api.v1.endpoints.analysis.AnalysisService") as mock_analysis_service,
        patch("app.api.v1.endpoints.auth.AuthService") as mock_auth_service,
    ):

        yield {
            "user_service": mock_user_service,
            "topic_service": mock_topic_service,
            "situation_service": mock_situation_service,
            "comment_service": mock_comment_service,
            "analysis_service": mock_analysis_service,
            "auth_service": mock_auth_service,
        }


@pytest.fixture
def mock_repositories():
    """Mock all repositories for testing"""
    with (
        patch("app.services.user_service.UserRepository") as mock_user_repo,
        patch("app.services.topic_service.TopicRepository") as mock_topic_repo,
        patch(
            "app.services.situation_service.SituationRepository"
        ) as mock_situation_repo,
        patch("app.services.comment_service.CommentRepository") as mock_comment_repo,
        patch("app.services.analysis_service.AnswerRepository") as mock_answer_repo,
    ):

        yield {
            "user_repo": mock_user_repo,
            "topic_repo": mock_topic_repo,
            "situation_repo": mock_situation_repo,
            "comment_repo": mock_comment_repo,
            "answer_repo": mock_answer_repo,
        }


@pytest.fixture
def mock_get_current_user():
    """Mock get_current_user dependency"""
    with patch("app.api.v1.endpoints.users.get_current_user_dep") as mock:
        mock.return_value = {
            "id": 1,
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/pic.jpg",
        }
        yield mock


# Authentication headers
@pytest.fixture
def auth_headers():
    """Authentication headers for testing"""
    return {"Authorization": "Bearer test_token", "Content-Type": "application/json"}


# Sample data fixtures
@pytest.fixture
def test_user(sample_users):
    """Get first sample user"""
    return sample_users[0]


@pytest.fixture
def test_topic(sample_topics):
    """Get first sample topic"""
    return sample_topics[0]


@pytest.fixture
def test_situation(sample_situations):
    """Get first sample situation"""
    return sample_situations[0]


@pytest.fixture
def test_comment(sample_comments):
    """Get first sample comment"""
    return sample_comments[0]


@pytest.fixture
def test_answer(sample_answers):
    """Get first sample answer"""
    return sample_answers[0]


# Test markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location"""
    for item in items:
        # Mark tests based on directory structure
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "end_to_end" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

        # Mark performance tests
        if "performance" in str(item.fspath) or "load" in str(item.fspath):
            item.add_marker(pytest.mark.performance)

        # Mark slow tests
        if any(
            keyword in str(item.fspath) for keyword in ["e2e", "performance", "load"]
        ):
            item.add_marker(pytest.mark.slow)

    # Ensure async tests run even if plugin markers are not recognized
    try:
        import pytest_asyncio  # noqa: F401
    except Exception:
        for item in items:
            if getattr(item.obj, "__code__", None) and asyncio.iscoroutinefunction(
                item.obj
            ):
                item.add_marker(pytest.mark.asyncio)


def pytest_pyfunc_call(pyfuncitem):
    """Run async tests without pytest-asyncio plugin using asyncio.run()."""
    try:
        has_asyncio_plugin = pyfuncitem.config.pluginmanager.hasplugin("asyncio")
    except Exception:
        has_asyncio_plugin = False
    if has_asyncio_plugin:
        return False
    import inspect

    if inspect.iscoroutinefunction(pyfuncitem.obj):
        sig = inspect.signature(pyfuncitem.obj)
        allowed_kwargs = {
            name: pyfuncitem.funcargs[name]
            for name in sig.parameters.keys()
            if name in pyfuncitem.funcargs
        }
        asyncio.run(pyfuncitem.obj(**allowed_kwargs))
        return True
    return False
