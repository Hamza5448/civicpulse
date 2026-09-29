"""create complaints table

Revision ID: 0001_create_complaints
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_create_complaints"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Base definition for creation/drop
category_enum = postgresql.ENUM(
    "water",
    "electricity",
    "sanitation",
    "roads",
    "streetlights",
    "other",
    name="category_enum",
)
priority_enum = postgresql.ENUM("high", "normal", "low", name="priority_enum")
status_enum = postgresql.ENUM("open", "in_progress", "resolved", "rejected", name="complaint_status_enum")

# Column references with create_type=False to prevent double-execution
category_col_type = postgresql.ENUM(
    "water",
    "electricity",
    "sanitation",
    "roads",
    "streetlights",
    "other",
    name="category_enum",
    create_type=False,
)
priority_col_type = postgresql.ENUM("high", "normal", "low", name="priority_enum", create_type=False)
status_col_type = postgresql.ENUM(
    "open", "in_progress", "resolved", "rejected", name="complaint_status_enum", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        category_enum.create(bind, checkfirst=True)
        priority_enum.create(bind, checkfirst=True)
        status_enum.create(bind, checkfirst=True)

    op.create_table(
        "complaints",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("location", sa.String(length=200), nullable=False),
        sa.Column("reporter_contact", sa.String(length=255), nullable=True),
        sa.Column("category", category_col_type, nullable=False),
        sa.Column("priority", priority_col_type, nullable=False),
        sa.Column("status", status_col_type, nullable=False, server_default="open"),
        sa.Column("ai_summary", sa.String(length=140), nullable=True),
        sa.Column("triaged_by", sa.String(length=32), nullable=True),
        sa.Column("triage_latency_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "length(text) >= 10 AND length(text) <= 2000", name="ck_complaints_text_length"
        ),
        sa.CheckConstraint(
            "length(location) >= 3 AND length(location) <= 200",
            name="ck_complaints_location_length",
        ),
        sa.CheckConstraint(
            "triage_latency_ms IS NULL OR triage_latency_ms >= 0",
            name="ck_complaints_latency_nonnegative",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_complaints_status_priority", "complaints", ["status", "priority"])
    op.create_index("ix_complaints_created_at", "complaints", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_complaints_created_at", table_name="complaints")
    op.drop_index("ix_complaints_status_priority", table_name="complaints")
    op.drop_table("complaints")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        status_enum.drop(bind, checkfirst=True)
        priority_enum.drop(bind, checkfirst=True)
        category_enum.drop(bind, checkfirst=True)