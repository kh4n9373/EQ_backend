from datetime import datetime

import pytest

from app.models import Answer, Comment, Situation, Topic, User
from app.schemas.analysis import AnswerCreate, SentimentAnalysisRequest
from app.schemas.comments import CommentCreate, CommentUpdate
from app.schemas.situations import SituationCreate, SituationUpdate
from app.schemas.topics import TopicCreate, TopicUpdate
from app.schemas.users import UserCreate, UserUpdate


@pytest.fixture
def sample_users():
    """Sample users for testing"""
    return [
        User(
            id=1,
            google_id="google_123",
            email="user1@example.com",
            name="User One",
            picture="https://example.com/pic1.jpg",
            bio="Test bio 1",
            encrypted_refresh_token=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        User(
            id=2,
            google_id="google_456",
            email="user2@example.com",
            name="User Two",
            picture="https://example.com/pic2.jpg",
            bio="Test bio 2",
            encrypted_refresh_token=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]


@pytest.fixture
def sample_topics():
    """Sample topics for testing"""
    return [
        Topic(id=1, name="Topic One"),
        Topic(id=2, name="Topic Two"),
        Topic(id=3, name="Topic Three"),
    ]


@pytest.fixture
def sample_situations():
    """Sample situations for testing"""
    return [
        Situation(
            id=1,
            topic_id=1,
            user_id=1,
            context="Test context 1",
            question="Test question 1?",
            image_url="https://example.com/img1.jpg",
            is_contributed=False,
            created_at=datetime.now(),
        ),
        Situation(
            id=2,
            topic_id=1,
            user_id=2,
            context="Test context 2",
            question="Test question 2?",
            image_url="https://example.com/img2.jpg",
            is_contributed=True,
            created_at=datetime.now(),
        ),
        Situation(
            id=3,
            topic_id=2,
            user_id=1,
            context="Test context 3",
            question="Test question 3?",
            image_url=None,
            is_contributed=False,
            created_at=datetime.now(),
        ),
    ]


@pytest.fixture
def sample_comments():
    """Sample comments for testing"""
    return [
        Comment(
            id=1,
            situation_id=1,
            user_id=1,
            content="Great comment!",
            sentiment_analysis={"sentiment": "positive", "score": 0.8},
            created_at=datetime.now(),
        ),
        Comment(
            id=2,
            situation_id=1,
            user_id=2,
            content="Interesting perspective",
            sentiment_analysis={"sentiment": "neutral", "score": 0.5},
            created_at=datetime.now(),
        ),
        Comment(
            id=3,
            situation_id=2,
            user_id=1,
            content="I disagree with this",
            sentiment_analysis={"sentiment": "negative", "score": 0.2},
            created_at=datetime.now(),
        ),
    ]


@pytest.fixture
def sample_answers():
    """Sample answers for testing"""
    return [
        Answer(
            id=1,
            situation_id=1,
            answer_text="I would handle this by...",
            scores={
                "self_awareness": 8,
                "self_management": 7,
                "social_awareness": 6,
                "relationship_management": 8,
                "responsible_decision_making": 7,
            },
            reasoning={
                "self_awareness": "I recognize my emotions",
                "self_management": "I control my reactions",
                "social_awareness": "I understand others",
                "relationship_management": "I build connections",
                "responsible_decision_making": "I make ethical choices",
            },
            created_at=datetime.now(),
        ),
        Answer(
            id=2,
            situation_id=2,
            answer_text="In this situation, I would...",
            scores={
                "self_awareness": 6,
                "self_management": 8,
                "social_awareness": 7,
                "relationship_management": 6,
                "responsible_decision_making": 8,
            },
            reasoning={
                "self_awareness": "I am aware of my feelings",
                "self_management": "I stay calm",
                "social_awareness": "I empathize with others",
                "relationship_management": "I communicate effectively",
                "responsible_decision_making": "I consider consequences",
            },
            created_at=datetime.now(),
        ),
    ]


@pytest.fixture
def sample_oauth_data():
    """Sample OAuth data for testing"""
    return {
        "userinfo": {
            "sub": "google_123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/pic.jpg",
        },
        "token": {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
        },
    }


@pytest.fixture
def sample_jwt_payload():
    """Sample JWT payload for testing"""
    return {
        "sub": "test@example.com",
        "exp": datetime.now().timestamp() + 3600,
        "iat": datetime.now().timestamp(),
    }


@pytest.fixture
def sample_analysis_request():
    """Sample analysis request for testing"""
    return AnswerCreate(
        situation_id=1,
        answer_text="I would handle this situation by staying calm and listening to all parties involved.",
    )


@pytest.fixture
def sample_sentiment_request():
    """Sample sentiment analysis request for testing"""
    return SentimentAnalysisRequest(
        content="This is a positive comment about the situation."
    )


@pytest.fixture
def sample_analysis_response():
    """Sample analysis response for testing"""
    return {
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


@pytest.fixture
def sample_sentiment_response():
    """Sample sentiment analysis response for testing"""
    return {
        "sentiment": "positive",
        "score": 0.85,
        "keywords": ["positive", "good", "excellent"],
    }


# Unique test data generators for different tests
@pytest.fixture
def unique_user_data():
    """Generate unique user data for each test"""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return {
        "google_id": f"google_{unique_id}",
        "email": f"user_{unique_id}@example.com",
        "name": f"User {unique_id}",
        "picture": f"https://example.com/pic_{unique_id}.jpg",
        "bio": f"Bio for user {unique_id}",
        "encrypted_refresh_token": None,
    }


@pytest.fixture
def unique_topic_data():
    """Generate unique topic data for each test"""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return {"name": f"Topic {unique_id}"}


@pytest.fixture
def unique_situation_data():
    """Generate unique situation data for each test"""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return {
        "topic_id": 1,
        "user_id": 1,
        "context": f"Context {unique_id}",
        "question": f"Question {unique_id}?",
        "image_url": f"https://example.com/img_{unique_id}.jpg",
        "is_contributed": False,
    }


@pytest.fixture
def unique_comment_data():
    """Generate unique comment data for each test"""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return {"situation_id": 1, "user_id": 1, "content": f"Comment content {unique_id}"}


@pytest.fixture
def unique_answer_data():
    """Generate unique answer data for each test"""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return {
        "situation_id": 1,
        "answer_text": f"Answer text {unique_id}",
        "scores": {
            "self_awareness": 7,
            "self_management": 8,
            "social_awareness": 6,
            "relationship_management": 7,
            "responsible_decision_making": 8,
        },
        "reasoning": {
            "self_awareness": f"Reasoning {unique_id}",
            "self_management": f"Management {unique_id}",
            "social_awareness": f"Social {unique_id}",
            "relationship_management": f"Relationship {unique_id}",
            "responsible_decision_making": f"Decision {unique_id}",
        },
    }
