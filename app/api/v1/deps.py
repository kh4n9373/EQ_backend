import redis
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import get_current_user

_redis_client = None


def _get_redis():
    global _redis_client
    if redis is None:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        _redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        _redis_client.ping()
        return _redis_client
    except Exception:
        return None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_current_user_with_touch(request: Request):
    user = get_current_user(request)
    client = _get_redis()
    if client and user and user.get("id"):
        # TTL key
        user_id = str(user["id"])
        try:
            client.setex(f"active_user:{user_id}", 120, "1")  # 2 minutes TTL
        except Exception:
            pass
    return user


get_current_user_dep = Depends(_get_current_user_with_touch)
