from unittest.mock import patch

import pytest


@pytest.mark.integration
def test_create_comment_with_sentiment_ok(client, setup_test_data):
    with patch(
        "app.services.sentiment_service.SentimentService.analyze_sentiment",
        return_value={"s": 1},
    ):
        # We also need an authenticated user
        with patch(
            "app.api.v1.endpoints.comments.get_current_user_dep", return_value={"id": 1}
        ):
            payload = {"content": "hello"}
            # path requires situation_id in URL
            resp = client.post("/api/v1/comments/situations/1/comments", json=payload)
            assert resp.status_code in (200, 201)


@pytest.mark.integration
def test_create_comment_fallback_when_sentiment_fails(client, setup_test_data):
    with patch(
        "app.services.sentiment_service.SentimentService.analyze_sentiment",
        side_effect=RuntimeError("x"),
    ):
        with patch(
            "app.api.v1.endpoints.comments.get_current_user_dep", return_value={"id": 1}
        ):
            payload = {"content": "world"}
            resp = client.post("/api/v1/comments/situations/1/comments", json=payload)
            assert resp.status_code in (200, 201)
