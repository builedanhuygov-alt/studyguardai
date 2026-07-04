"""initial samples schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-04
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "samples",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ts", sa.String, nullable=False, index=True),
        sa.Column("frame_index", sa.Integer, nullable=False),
        sa.Column("present", sa.Integer, nullable=False),
        sa.Column("posture", sa.Float, nullable=False),
        sa.Column("focus", sa.Float, nullable=False),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("distractions", sa.Integer, nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("samples")
