from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


class TestMainIntegration:
    """Complete integration tests cho main.py"""

    def test_get_topics(self, client: TestClient):
        response = client.get("/topics")
        assert response.status_code == 200
        topics = response.json()
        assert isinstance(topics, list)
        if topics:
            topic = topics[0]
            assert "id" in topic
            assert "name" in topic

    def test_get_situations_no_topic(self, client: TestClient):
        response = client.get("/situations")
        assert response.status_code == 422

    def test_get_situations_by_topic(self, client: TestClient, sample_data):
        topic = sample_data["topic"]
        response = client.get(f"/situations?topic_id={topic.id}")
        assert response.status_code == 200
        situations = response.json()
        assert isinstance(situations, list)
        if situations:
            situation = situations[0]
            assert "id" in situation
            assert "context" in situation
            assert "question" in situation
            assert "topic_id" in situation

    def test_login_redirect_flow(self, client: TestClient):
        response = client.get("/login/google", follow_redirects=False)
        assert response.status_code in [302, 307]

    def test_unauthenticated_access(self, client: TestClient):
        response = client.get("/users/me")
        assert response.status_code == 401

    def test_logout_flow(self, client: TestClient):
        response = client.post("/logout")
        assert response.status_code == 200

    @patch(
        "app.authorization.oauth.google.authorize_access_token", new_callable=AsyncMock
    )
    def test_oauth_callback_success(
        self, mock_authorize, client: TestClient, db_session
    ):
        mock_token = {
            "userinfo": {
                "sub": "some-google-id",
                "email": "test@google.com",
                "name": "Test Google User",
                "picture": "https://google.com/avatar.jpg",
            },
            "refresh_token": "mock_refresh_token",
        }
        mock_authorize.return_value = mock_token
        response = client.get("/auth/callback", follow_redirects=False)
        assert response.status_code == 307 or response.status_code == 302
        assert response.headers["location"] == "http://localhost:3000/"

    def test_oauth_callback_error(self, client: TestClient):
        response = client.get("/auth/callback")
        assert response.status_code == 401

    # Situation tests
    def test_contribute_situation_flow(self, client: TestClient, sample_data):
        situation_data = {
            "context": "Integration test situation context",
            "question": "What would you do in this integration test situation?",
            "topic_id": sample_data["topic"].id,
        }
        response = client.post("/contribute-situation", json=situation_data)
        assert response.status_code == 401  # Requires authentication

    def test_contribute_situation_invalid_data(self, client: TestClient):
        invalid_data = {"context": "", "question": "", "topic_id": 99999}
        response = client.post("/contribute-situation", json=invalid_data)
        assert response.status_code == 401

    def test_get_contributed_situations(self, client: TestClient):
        response = client.get("/contributed-situations")
        assert response.status_code == 200
        situations = response.json()
        assert isinstance(situations, list)
        if situations:
            situation = situations[0]
            assert "id" in situation
            assert "context" in situation
            assert "question" in situation
            assert "is_contributed" in situation

    def test_analyze_answer_flow(self, client: TestClient, sample_data):
        situation = sample_data["situation"]
        answer_data = {
            "situation_id": situation.id,
            "answer_text": "I would try to understand the situation and respond appropriately with empathy and clear communication.",
        }
        with patch("app.openai_utils.analyze_eq") as mock_analyze:
            mock_analyze.return_value = (
                {"self_awareness": 8, "empathy": 7, "social_skills": 6},
                {
                    "self_awareness": "Good awareness",
                    "empathy": "Shows empathy",
                    "social_skills": "Basic skills",
                },
            )
            response = client.post("/analyze", json=answer_data)
            assert response.status_code == 200
            result = response.json()
            assert "scores" in result
            assert "reasoning" in result
            assert "question" in result
            assert "context" in result

    def test_analyze_invalid_situation_id(self, client: TestClient):
        answer_data = {"situation_id": -1, "answer_text": "Test answer"}
        response = client.post("/analyze", json=answer_data)
        assert response.status_code == 404

    def test_situation_not_found(self, client: TestClient):
        answer_data = {"situation_id": 99999, "answer_text": "Test answer"}
        response = client.post("/analyze", json=answer_data)
        assert response.status_code == 404
        assert "Situation not found" in response.json()["detail"]

    def test_invalid_answer_data(self, client: TestClient):
        """Test handle invalid answer data"""
        invalid_answer = {"situation_id": 1}
        response = client.post("/analyze", json=invalid_answer)
        assert response.status_code == 422

    def test_get_answers_by_situation(self, client: TestClient, sample_data):
        situation = sample_data["situation"]
        response = client.get(f"/answers-by-situation?situation_id={situation.id}")
        assert response.status_code == 200
        answers = response.json()
        assert isinstance(answers, list)
        if answers:
            answer = answers[0]
            assert "id" in answer
            assert "situation_id" in answer
            assert "answer_text" in answer
            assert "scores" in answer
            assert "reasoning" in answer

    def test_get_answers_by_situation_invalid_id(self, client: TestClient):
        response = client.get("/answers-by-situation?situation_id=99999")
        assert response.status_code == 200
        answers = response.json()
        assert isinstance(answers, list)
        assert len(answers) == 0

    def test_get_comments_by_situation(self, client: TestClient, sample_data):
        situation = sample_data["situation"]
        response = client.get(f"/situations/{situation.id}/comments")
        assert response.status_code == 200
        comments = response.json()
        assert isinstance(comments, list)
        if comments:
            comment = comments[0]
            assert "id" in comment
            assert "situation_id" in comment
            assert "content" in comment
            assert "created_at" in comment

    def test_get_comments_by_situation_invalid_id(self, client: TestClient):
        response = client.get("/situations/99999/comments")
        assert response.status_code == 200
        comments = response.json()
        assert isinstance(comments, list)
        assert len(comments) == 0

    def test_create_comment_requires_auth(self, client: TestClient, sample_data):
        situation = sample_data["situation"]
        comment_data = {"content": "This is a test comment for integration testing."}
        response = client.post(
            f"/situations/{situation.id}/comments", json=comment_data
        )
        assert response.status_code == 401

    def test_create_comment_invalid_situation_id(self, client: TestClient):
        """Test create comment với invalid situation_id"""
        comment_data = {"content": "Test comment"}
        response = client.post("/situations/99999/comments", json=comment_data)
        assert response.status_code == 401

    def test_create_comment_with_sentiment_analysis(
        self, client: TestClient, sample_data
    ):
        situation = sample_data["situation"]

        def mock_get_current_user():
            return {
                "id": sample_data["user"].id,
                "email": sample_data["user"].email,
                "name": sample_data["user"].name,
            }

        from app.authorization import get_current_user
        from app.main import app

        app.dependency_overrides[get_current_user] = mock_get_current_user
        try:
            positive_comment = {
                "situation_id": situation.id,
                "content": "Tôi rất vui và hạnh phúc với tình huống này!",
            }
            response = client.post(
                f"/situations/{situation.id}/comments", json=positive_comment
            )
            assert response.status_code == 200
            comment = response.json()
            assert "id" in comment
            assert "content" in comment
            assert comment["content"] == positive_comment["content"]
        finally:
            app.dependency_overrides.clear()

    def test_comment_workflow_complete(self, client: TestClient, sample_data):
        """Test complete comment workflow"""
        situation = sample_data["situation"]

        def mock_get_current_user():
            return {
                "id": sample_data["user"].id,
                "email": sample_data["user"].email,
                "name": sample_data["user"].name,
            }

        from app.authorization import get_current_user
        from app.main import app

        app.dependency_overrides[get_current_user] = mock_get_current_user
        try:
            comment_data = {
                "situation_id": situation.id,
                "content": "Đây là một comment test cho workflow hoàn chỉnh!",
            }
            create_response = client.post(
                f"/situations/{situation.id}/comments", json=comment_data
            )
            assert create_response.status_code == 200
            comment = create_response.json()
            comment_id = comment["id"]

            get_response = client.get(f"/situations/{situation.id}/comments")
            assert get_response.status_code == 200
            comments = get_response.json()
            assert len(comments) > 0
            created_comment = next((c for c in comments if c["id"] == comment_id), None)
            assert created_comment is not None
            assert created_comment["content"] == comment_data["content"]
        finally:
            app.dependency_overrides.clear()

    def test_sentiment_analysis_endpoint(self, client: TestClient):
        positive_text = {"content": "Tôi rất vui và hạnh phúc với cuộc sống hiện tại!"}
        response = client.post("/analyze-sentiment", json=positive_text)
        assert response.status_code == 200
        result = response.json()
        assert "sentiment" in result
        assert "severity" in result
        assert "score" in result
        assert "warning" in result
        assert "suggestions" in result
        assert result["sentiment"] in ["positive", "negative", "neutral"]
        assert result["severity"] in ["low", "medium", "high"]
        assert isinstance(result["suggestions"], list)

    def test_analyze_sentiment_empty_content(self, client: TestClient):
        sentiment_data = {"content": ""}
        response = client.post("/analyze-sentiment", json=sentiment_data)
        assert response.status_code == 200
        result = response.json()
        assert "sentiment" in result

    def test_analyze_sentiment_invalid_data(self, client: TestClient):
        invalid_data = {"text": "This should be content"}
        response = client.post("/analyze-sentiment", json=invalid_data)
        assert response.status_code == 422

    def test_get_reactions_by_situation(self, client: TestClient):
        response = client.get("/situations/1/reactions")
        assert response.status_code == 200
        reactions = response.json()
        assert isinstance(reactions, list)

    def test_create_reaction_requires_auth(self, client: TestClient):
        reaction_data = {"reaction_type": "like"}
        response = client.post("/situations/1/reactions", json=reaction_data)
        assert response.status_code == 401

    def test_delete_reaction_requires_auth(self, client: TestClient):
        response = client.delete("/situations/1/reactions/like")
        assert response.status_code in [401, 404]
