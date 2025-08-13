from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("google_id", sa.String(), unique=True, index=True),
        sa.Column("email", sa.String(), unique=True, index=True),
        sa.Column("name", sa.String()),
        sa.Column("picture", sa.String()),
        sa.Column("bio", sa.String(), nullable=True),
        sa.Column("encrypted_refresh_token", sa.String()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
    )
    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), unique=True, index=True),
    )
    op.create_table(
        "situations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("topics.id")),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("context", sa.String()),
        sa.Column("question", sa.String()),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("is_contributed", sa.Boolean(), server_default=sa.text("false")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
    )
    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("situation_id", sa.Integer(), sa.ForeignKey("situations.id")),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("answer_text", sa.String()),
        sa.Column("scores", sa.JSON()),
        sa.Column("reasoning", sa.JSON()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
    )
    op.create_table(
        "results",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("total_scores", sa.JSON()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
    )
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("situation_id", sa.Integer(), sa.ForeignKey("situations.id")),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("content", sa.String()),
        sa.Column("sentiment_score", sa.Integer(), nullable=True),
        sa.Column("sentiment_label", sa.String(), nullable=True),
        sa.Column("sentiment_analysis", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
    )
    op.create_table(
        "reactions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("situation_id", sa.Integer(), sa.ForeignKey("situations.id")),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("reaction_type", sa.String()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")
        ),
    )


def downgrade():
    op.drop_table("reactions")
    op.drop_table("comments")
    op.drop_table("results")
    op.drop_table("answers")
    op.drop_table("situations")
    op.drop_table("topics")
    op.drop_table("users")


revision: str = "bb9ea76cc252"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
