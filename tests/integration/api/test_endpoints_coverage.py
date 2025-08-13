"""Integration tests to boost API endpoint coverage"""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_get_current_user():
    """Mock get_current_user dependency"""
    return {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "picture": "test.jpg",
    }


class TestTopicsEndpoints:
    """Test topics endpoints to increase coverage"""

    @patch("app.api.v1.endpoints.topics.TopicService")
    def test_get_topics_success(self, mock_topic_service, client):
        """Test GET /api/v1/topics"""
        mock_service = Mock()
        mock_topic_service.return_value = mock_service
        mock_service.get_all_topics.return_value = [
            {"id": 1, "name": "Topic 1"},
            {"id": 2, "name": "Topic 2"},
        ]

        response = client.get("/api/v1/topics")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Topic 1"

    @patch("app.api.v1.endpoints.topics.TopicService")
    def test_get_topics_empty(self, mock_topic_service, client):
        """Test GET /api/v1/topics with no topics"""
        mock_service = Mock()
        mock_topic_service.return_value = mock_service
        mock_service.get_all_topics.return_value = []

        response = client.get("/api/v1/topics")

        assert response.status_code == 200
        assert response.json() == []

    @patch("app.api.v1.endpoints.topics.TopicService")
    def test_get_topic_by_id_success(self, mock_topic_service, client):
        """Test GET /api/v1/topics/{topic_id}"""
        mock_service = Mock()
        mock_topic_service.return_value = mock_service
        mock_service.get_topic_by_id.return_value = {"id": 1, "name": "Topic 1"}

        response = client.get("/api/v1/topics/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Topic 1"

    @patch("app.api.v1.endpoints.topics.TopicService")
    def test_get_topic_by_id_not_found(self, mock_topic_service, client):
        """Test GET /api/v1/topics/{topic_id} when topic not found"""
        mock_service = Mock()
        mock_topic_service.return_value = mock_service
        mock_service.get_topic_by_id.return_value = None

        response = client.get("/api/v1/topics/999")

        assert response.status_code == 404

    @patch("app.api.v1.endpoints.topics.get_current_user")
    @patch("app.api.v1.endpoints.topics.TopicService")
    def test_create_topic_success(
        self, mock_topic_service, mock_get_current_user, client
    ):
        """Test POST /api/v1/topics"""
        mock_get_current_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_service = Mock()
        mock_topic_service.return_value = mock_service
        mock_service.create_topic.return_value = {"id": 1, "name": "New Topic"}

        response = client.post("/api/v1/topics", json={"name": "New Topic"})

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Topic"

    @patch("app.api.v1.endpoints.topics.get_current_user")
    @patch("app.api.v1.endpoints.topics.TopicService")
    def test_update_topic_success(
        self, mock_topic_service, mock_get_current_user, client
    ):
        """Test PUT /api/v1/topics/{topic_id}"""
        mock_get_current_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_service = Mock()
        mock_topic_service.return_value = mock_service
        mock_service.update_topic.return_value = {"id": 1, "name": "Updated Topic"}

        response = client.put("/api/v1/topics/1", json={"name": "Updated Topic"})

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Topic"

    @patch("app.api.v1.endpoints.topics.get_current_user")
    @patch("app.api.v1.endpoints.topics.TopicService")
    def test_delete_topic_success(
        self, mock_topic_service, mock_get_current_user, client
    ):
        """Test DELETE /api/v1/topics/{topic_id}"""
        mock_get_current_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_service = Mock()
        mock_topic_service.return_value = mock_service
        mock_service.delete_topic.return_value = True

        response = client.delete("/api/v1/topics/1")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Topic deleted successfully"


class TestSituationsEndpoints:
    """Test situations endpoints to increase coverage"""

    @patch("app.api.v1.endpoints.situations.SituationService")
    def test_get_situations_by_topic_success(self, mock_situation_service, client):
        """Test GET /api/v1/situations/topic/{topic_id}"""
        mock_service = Mock()
        mock_situation_service.return_value = mock_service
        mock_service.get_situations_by_topic.return_value = [
            {"id": 1, "title": "Situation 1", "topic_id": 1},
            {"id": 2, "title": "Situation 2", "topic_id": 1},
        ]

        response = client.get("/api/v1/situations/topic/1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Situation 1"

    @patch("app.api.v1.endpoints.situations.SituationService")
    def test_get_situation_by_id_success(self, mock_situation_service, client):
        """Test GET /api/v1/situations/{situation_id}"""
        mock_service = Mock()
        mock_situation_service.return_value = mock_service
        mock_service.get_situation_by_id.return_value = {
            "id": 1,
            "title": "Test Situation",
            "content": "Test content",
        }

        response = client.get("/api/v1/situations/1")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Situation"

    @patch("app.api.v1.endpoints.situations.get_current_user")
    @patch("app.api.v1.endpoints.situations.SituationService")
    def test_create_situation_success(
        self, mock_situation_service, mock_get_current_user, client
    ):
        """Test POST /api/v1/situations"""
        mock_get_current_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_service = Mock()
        mock_situation_service.return_value = mock_service
        mock_service.create_situation.return_value = {
            "id": 1,
            "title": "New Situation",
            "content": "New content",
        }

        response = client.post(
            "/api/v1/situations",
            json={"title": "New Situation", "content": "New content", "topic_id": 1},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Situation"

    @patch("app.api.v1.endpoints.situations.SituationService")
    def test_get_contributed_situations_success(self, mock_situation_service, client):
        """Test GET /api/v1/situations/contributed"""
        mock_service = Mock()
        mock_situation_service.return_value = mock_service
        mock_service.get_contributed_situations.return_value = [
            {"id": 1, "title": "Contributed 1", "is_contributed": True}
        ]

        response = client.get("/api/v1/situations/contributed")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["is_contributed"] is True

    @patch("app.api.v1.endpoints.situations.get_current_user_optional")
    @patch("app.api.v1.endpoints.situations.SituationService")
    def test_get_situations_feed_success(
        self, mock_situation_service, mock_get_current_user_optional, client
    ):
        """Test GET /api/v1/situations/feed"""
        mock_get_current_user_optional.return_value = {"id": 1}
        mock_service = Mock()
        mock_situation_service.return_value = mock_service
        mock_service.get_situations_feed_paginated.return_value = [
            {"id": 1, "title": "Feed Item 1"}
        ]

        response = client.get("/api/v1/situations/feed")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    @patch("app.api.v1.endpoints.situations.get_current_user")
    @patch("app.api.v1.endpoints.situations.SituationService")
    def test_update_situation_success(
        self, mock_situation_service, mock_get_current_user, client
    ):
        """Test PUT /api/v1/situations/{situation_id}"""
        mock_get_current_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_service = Mock()
        mock_situation_service.return_value = mock_service
        mock_service.update_situation.return_value = {
            "id": 1,
            "title": "Updated Situation",
        }

        response = client.put(
            "/api/v1/situations/1", json={"title": "Updated Situation"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Situation"

    @patch("app.api.v1.endpoints.situations.get_current_user")
    @patch("app.api.v1.endpoints.situations.SituationService")
    def test_delete_situation_success(
        self, mock_situation_service, mock_get_current_user, client
    ):
        """Test DELETE /api/v1/situations/{situation_id}"""
        mock_get_current_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_service = Mock()
        mock_situation_service.return_value = mock_service
        mock_service.delete_situation.return_value = True

        response = client.delete("/api/v1/situations/1")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Situation deleted successfully"


class TestCommentsEndpoints:
    """Test comments endpoints to increase coverage"""

    @patch("app.api.v1.endpoints.comments.CommentService")
    def test_get_comments_by_situation_success(self, mock_comment_service, client):
        """Test GET /api/v1/comments/situation/{situation_id}"""
        mock_service = Mock()
        mock_comment_service.return_value = mock_service
        mock_service.get_comments_by_situation.return_value = [
            {"id": 1, "content": "Comment 1", "situation_id": 1},
            {"id": 2, "content": "Comment 2", "situation_id": 1},
        ]

        response = client.get("/api/v1/comments/situation/1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["content"] == "Comment 1"

    @patch("app.api.v1.endpoints.comments.get_current_user")
    @patch("app.api.v1.endpoints.comments.CommentService")
    def test_create_comment_success(
        self, mock_comment_service, mock_get_current_user, client
    ):
        """Test POST /api/v1/comments"""
        mock_get_current_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_service = Mock()
        mock_comment_service.return_value = mock_service
        mock_service.create_comment.return_value = {
            "id": 1,
            "content": "New comment",
            "situation_id": 1,
        }

        response = client.post(
            "/api/v1/comments", json={"content": "New comment", "situation_id": 1}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "New comment"

    @patch("app.api.v1.endpoints.comments.get_current_user")
    @patch("app.api.v1.endpoints.comments.CommentService")
    def test_update_comment_success(
        self, mock_comment_service, mock_get_current_user, client
    ):
        """Test PUT /api/v1/comments/{comment_id}"""
        mock_get_current_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_service = Mock()
        mock_comment_service.return_value = mock_service
        mock_service.update_comment.return_value = {
            "id": 1,
            "content": "Updated comment",
        }

        response = client.put("/api/v1/comments/1", json={"content": "Updated comment"})

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated comment"

    @patch("app.api.v1.endpoints.comments.get_current_user")
    @patch("app.api.v1.endpoints.comments.CommentService")
    def test_delete_comment_success(
        self, mock_comment_service, mock_get_current_user, client
    ):
        """Test DELETE /api/v1/comments/{comment_id}"""
        mock_get_current_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_service = Mock()
        mock_comment_service.return_value = mock_service
        mock_service.delete_comment.return_value = True

        response = client.delete("/api/v1/comments/1")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Comment deleted successfully"


class TestAnalysisEndpoints:
    """Test analysis endpoints to increase coverage"""

    @patch("app.api.v1.endpoints.analysis.AnalysisService")
    def test_analyze_answer_success(self, mock_analysis_service, client):
        """Test POST /api/v1/analysis/answer"""
        mock_service = Mock()
        mock_analysis_service.return_value = mock_service
        mock_service.analyze_answer.return_value = {
            "scores": {"empathy": 8, "self_awareness": 7},
            "reasoning": {
                "empathy": "Good understanding",
                "self_awareness": "Decent insight",
            },
        }

        response = client.post(
            "/api/v1/analysis/answer",
            json={
                "situation_id": 1,
                "answer_text": "I would try to understand their perspective",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "scores" in data
        assert "reasoning" in data

    @patch("app.api.v1.endpoints.analysis.SentimentService")
    def test_analyze_sentiment_success(self, mock_sentiment_service, client):
        """Test POST /api/v1/analysis/sentiment"""
        mock_service = Mock()
        mock_sentiment_service.return_value = mock_service
        mock_service.analyze_sentiment.return_value = {
            "sentiment": "positive",
            "confidence": 0.85,
            "emotions": {"joy": 0.7, "trust": 0.6},
        }

        response = client.post(
            "/api/v1/analysis/sentiment", json={"content": "This is a great day!"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "positive"
        assert data["confidence"] == 0.85


class TestUsersEndpoints:
    """Test users endpoints to increase coverage"""

    @patch("app.api.v1.endpoints.users.UserService")
    def test_search_users_success(self, mock_user_service, client):
        """Test GET /api/v1/users/search"""
        mock_service = Mock()
        mock_user_service.return_value = mock_service
        mock_service.search_users.return_value = [
            {"id": 1, "name": "Test User", "email": "test@example.com"}
        ]

        response = client.get("/api/v1/users/search?q=test")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test User"

    @patch("app.api.v1.endpoints.users.UserService")
    def test_get_user_profile_success(self, mock_user_service, client):
        """Test GET /api/v1/users/{user_id}"""
        mock_service = Mock()
        mock_user_service.return_value = mock_service
        mock_service.get_user_profile.return_value = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
            "bio": "Test bio",
        }

        response = client.get("/api/v1/users/1")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test User"

    @patch("app.api.v1.endpoints.users.get_current_user")
    @patch("app.api.v1.endpoints.users.UserService")
    def test_update_user_profile_success(
        self, mock_user_service, mock_get_current_user, client
    ):
        """Test PUT /api/v1/users/{user_id}"""
        mock_get_current_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_service = Mock()
        mock_user_service.return_value = mock_service
        mock_service.update_user_profile.return_value = {
            "id": 1,
            "name": "Updated User",
            "bio": "Updated bio",
        }

        response = client.put(
            "/api/v1/users/1", json={"name": "Updated User", "bio": "Updated bio"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated User"


class TestAuthEndpoints:
    """Test auth endpoints to increase coverage"""

    @patch("app.api.v1.endpoints.auth.AuthService")
    def test_login_google_redirect(self, mock_auth_service, client):
        """Test GET /api/v1/auth/login/google"""
        mock_service = Mock()
        mock_auth_service.return_value = mock_service
        # Mock the redirect response
        from fastapi.responses import RedirectResponse

        mock_service.login_google.return_value = RedirectResponse(
            "https://accounts.google.com/oauth"
        )

        response = client.get("/api/v1/auth/login/google", follow_redirects=False)

        # Should be a redirect
        assert response.status_code in [307, 302, 200]  # Accept various redirect codes

    @patch("app.api.v1.endpoints.auth.AuthService")
    def test_auth_callback_success(self, mock_auth_service, client):
        """Test GET /api/v1/auth/callback"""
        mock_service = Mock()
        mock_auth_service.return_value = mock_service
        mock_service.auth_callback.return_value = {
            "access_token": "test_token",
            "user": {"id": 1, "email": "test@example.com"},
        }

        response = client.get("/api/v1/auth/callback?code=test_code")

        # This might redirect or return JSON depending on implementation
        assert response.status_code in [200, 302, 307]
