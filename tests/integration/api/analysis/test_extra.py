def test_analyze_sentiment_missing_field(client, auth_headers):
    # Missing 'content' in body -> 422
    r = client.post("/api/v1/analysis/analyze-sentiment", json={}, headers=auth_headers)
    assert r.status_code == 422


def test_get_answers_by_situation_invalid_id(client, auth_headers):
    r = client.get("/api/v1/analysis/situations/not-int/answers", headers=auth_headers)
    assert r.status_code == 422
