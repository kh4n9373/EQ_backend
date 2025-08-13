import types

from fastapi import Depends
from fastapi.testclient import TestClient

from app.api.v1 import deps as deps_module
from app.main_v2 import app


class ObjUser:
    def __init__(self, id: int, email: str, name: str, picture: str | None = None):
        self.id = id
        self.email = email
        self.name = name
        self.picture = picture


def test_get_current_user_me_with_object_returns_attributes(monkeypatch):
    # Override dependency to return an object instead of dict
    monkeypatch.setattr(
        deps_module,
        "get_current_user_dep",
        ObjUser(1, "obj@example.com", "Obj User", "pic"),
    )

    client = TestClient(app)
    res = client.get("/api/v1/users/me")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["id"] == 1
    assert data["email"] == "obj@example.com"
    assert data["name"] == "Obj User"
    assert data["picture"] == "pic"
