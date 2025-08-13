import os
import time

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.metrics import track_db_query

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=30,
    connect_args=(
        {"check_same_thread": False}
        if "sqlite" in SQLALCHEMY_DATABASE_URL
        else {"connect_timeout": 30, "application_name": "eq_test_backend"}
    ),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.perf_counter()


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    try:
        elapsed = time.perf_counter() - getattr(
            context, "_query_start_time", time.perf_counter()
        )
        track_db_query(elapsed)
    except Exception:
        pass


Base = declarative_base()


def create_indexes():
    """Create database indexes for better query performance."""
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_situations_topic_id 
            ON situations(topic_id);
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_situations_user_id 
            ON situations(user_id);
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_situations_created_at 
            ON situations(created_at DESC);
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_comments_situation_id 
            ON comments(situation_id);
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_comments_user_id 
            ON comments(user_id);
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_reactions_situation_id 
            ON reactions(situation_id);
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_reactions_user_id 
            ON reactions(user_id);
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_reactions_type 
            ON reactions(reaction_type);
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_users_email 
            ON users(email);
        """
            )
        )

        conn.commit()


try:
    create_indexes()
except Exception as e:
    print(f"Warning: Could not create indexes: {e}")
