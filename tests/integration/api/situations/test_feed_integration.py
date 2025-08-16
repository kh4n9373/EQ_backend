from unittest.mock import patch

import pytest


@pytest.mark.integration
def test_situations_feed_without_user(client, setup_test_data):
    # get_current_user_dep expects a user; simulate None by patching to {} so current_user_id becomes None
    with patch("app.api.v1.endpoints.situations.get_current_user_dep", return_value={}):
        resp = client.get("/api/v1/situations/feed")
    assert resp.status_code == 200
    body = resp.json()
    # Endpoint might return list or object with items; handle both
    if isinstance(body, dict) and "items" in body:
        items = body["items"]
    else:
        items = body
    assert isinstance(items, list)


@pytest.mark.integration
def test_situations_feed_with_user(client, setup_test_data):
    # Patch dependency to simulate authenticated user
    with patch(
        "app.api.v1.endpoints.situations.get_current_user_dep", return_value={"id": 1}
    ):
        resp = client.get("/api/v1/situations/feed")
        assert resp.status_code == 200
        body = resp.json()
        if isinstance(body, dict) and "items" in body:
            items = body["items"]
        else:
            items = body
        assert isinstance(items, list)
