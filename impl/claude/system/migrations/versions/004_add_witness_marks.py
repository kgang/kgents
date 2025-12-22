"""Add witness_marks table for km command

Revision ID: 004
Revises: 003
Create Date: 2025-12-22

AGENTESE: world.witness.mark
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create witness_marks table for everyday mark-making."""
    op.create_table(
        "witness_marks",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("principles", sa.JSON(), default=list),
        sa.Column("author", sa.String(64), nullable=False, default="kent"),
        sa.Column("session_id", sa.String(64), nullable=True, index=True),
        sa.Column("datum_id", sa.String(64), nullable=True, index=True),
        sa.Column("repository_path", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Indices for common queries
    op.create_index("idx_witness_marks_recent", "witness_marks", ["created_at"])
    op.create_index("idx_witness_marks_author", "witness_marks", ["author"])


def downgrade() -> None:
    """Drop witness_marks table."""
    op.drop_index("idx_witness_marks_author", table_name="witness_marks")
    op.drop_index("idx_witness_marks_recent", table_name="witness_marks")
    op.drop_table("witness_marks")
