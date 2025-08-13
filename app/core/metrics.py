import threading

from fastapi import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# Business metrics
ACTIVE_USERS = Gauge("active_users", "Number of active users")
SITUATIONS_CREATED = Counter("situations_created_total", "Total situations created")
REACTIONS_TOTAL = Counter("reactions_total", "Total reactions")
COMMENTS_CREATED = Counter("comments_created_total", "Total comments created")

# Auth metrics
AUTH_LOGIN_SUCCESS = Counter(
    "auth_login_success_total", "Successful logins", ["provider"]
)
AUTH_LOGIN_FAILURE = Counter("auth_login_failure_total", "Failed logins", ["provider"])
AUTH_LOGOUT = Counter("auth_logout_total", "Total logouts")

# Error/exception metrics
EXCEPTIONS_TOTAL = Counter("exceptions_total", "Unhandled exceptions", ["type"])

# DB metrics
DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds", "Database query duration in seconds"
)

# Database totals
TOTAL_USERS_DB = Gauge("total_users_db", "Total users in database")
TOTAL_SITUATIONS_DB = Gauge("total_situations_db", "Total situations in database")
TOTAL_REACTIONS_DB = Gauge("total_reactions_db", "Total reactions in database")
TOTAL_COMMENTS_DB = Gauge("total_comments_db", "Total comments in database")


def get_metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Active users helpers
_active_users_lock = threading.Lock()
_active_users_count: int = 0


def _set_active_users_internal(count: int) -> None:
    global _active_users_count
    _active_users_count = max(0, int(count))
    ACTIVE_USERS.set(float(_active_users_count))


def increment_active_users() -> None:
    with _active_users_lock:
        _set_active_users_internal(_active_users_count + 1)


def decrement_active_users() -> None:
    with _active_users_lock:
        _set_active_users_internal(_active_users_count - 1)


def set_active_users(count: int) -> None:
    with _active_users_lock:
        _set_active_users_internal(count)


# Business helpers
def increment_situations_created() -> None:
    SITUATIONS_CREATED.inc()


def increment_reactions() -> None:
    REACTIONS_TOTAL.inc()


def increment_comments_created() -> None:
    COMMENTS_CREATED.inc()


# Auth helpers
def mark_login_success(provider: str = "google") -> None:
    AUTH_LOGIN_SUCCESS.labels(provider=provider).inc()


def mark_login_failure(provider: str = "google") -> None:
    AUTH_LOGIN_FAILURE.labels(provider=provider).inc()


def mark_logout() -> None:
    AUTH_LOGOUT.inc()


# Exception helpers
def mark_exception(exc_type: str) -> None:
    EXCEPTIONS_TOTAL.labels(type=exc_type).inc()


# DB helpers
def track_db_query(duration_seconds: float) -> None:
    try:
        DB_QUERY_DURATION.observe(duration_seconds)
    except Exception:
        pass


# Database totals helpers
def update_db_totals(
    users_count: int, situations_count: int, reactions_count: int, comments_count: int
) -> None:
    try:
        TOTAL_USERS_DB.set(users_count)
        TOTAL_SITUATIONS_DB.set(situations_count)
        TOTAL_REACTIONS_DB.set(reactions_count)
        TOTAL_COMMENTS_DB.set(comments_count)
    except Exception:
        pass
