"""Background task to update metrics periodically (DB totals, active users)."""

import asyncio
import logging
from typing import Optional

import redis
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import engine
from app.core.metrics import set_active_users, update_db_totals
from app.models import Comment, Reaction, Situation, User

logger = logging.getLogger(__name__)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_redis_client: Optional["redis.Redis"] = None


def get_redis_client() -> Optional["redis.Redis"]:
    global _redis_client
    if redis is None:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        _redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        _redis_client.ping()
        return _redis_client
    except Exception as exc:
        logger.warning(f"Redis not available: {exc}")
        _redis_client = None
        return None


async def update_database_metrics():
    """Update database metrics from actual DB counts."""
    try:
        with SessionLocal() as db:
            users_count = db.query(func.count(User.id)).scalar() or 0
            situations_count = db.query(func.count(Situation.id)).scalar() or 0
            reactions_count = db.query(func.count(Reaction.id)).scalar() or 0
            comments_count = db.query(func.count(Comment.id)).scalar() or 0

            update_db_totals(
                users_count, situations_count, reactions_count, comments_count
            )

            logger.info(
                f"Updated DB metrics: users={users_count}, situations={situations_count}, "
                f"reactions={reactions_count}, comments={comments_count}"
            )

    except Exception as e:
        logger.error(f"Error updating database metrics: {e}")


async def update_active_users_from_redis():
    client = get_redis_client()
    if not client:
        return
    try:
        # Count TTL keys
        count = 0
        for _ in client.scan_iter("active_user:*", count=1000):
            count += 1
        set_active_users(int(count))
        logger.info(f"Updated Active Users from Redis (keys): {count}")
    except Exception as exc:  # pragma: no cover
        logger.warning(f"Failed to update active users from Redis: {exc}")


async def start_metrics_updater():
    while True:
        try:
            await update_database_metrics()
            await update_active_users_from_redis()
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Error in metrics updater: {e}")
            await asyncio.sleep(60)
