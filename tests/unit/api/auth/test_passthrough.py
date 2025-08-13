from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.v1.endpoints import auth as auth_endpoint
from eq_test_backend.app.main import app


def test_auth_callback_http_exception_passthrough(monkeypatch):
    async def fake_auth_callback(request):
        raise HTTPException(status_code=401, detail="OAuth error")

    monkeypatch.setattr(
        auth_endpoint,
        "auth_service",
        type("S", (), {"auth_callback": fake_auth_callback})(),
    )

    client = TestClient(app)
    res = client.get("/api/v1/auth/callback/google")
    assert res.status_code == 401
    assert res.json()["detail"] == "OAuth error"
