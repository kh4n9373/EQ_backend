def test_topics_extra_invalid_id(client):
    r = client.get("/api/v1/topics/not-an-int")
    assert r.status_code == 422


def test_topics_update_invalid_payload(client):
    r = client.put("/api/v1/topics/1", json={"name": ""})
    assert r.status_code == 422
