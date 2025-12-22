"""Add parent_index for trail branching

Revision ID: 009
Revises: 008
Create Date: 2025-12-22

Phase 3.1: Branching Trail Creation
- Add parent_index column for step hierarchy
- Enables tree-structured trails where exploration can branch

UI Changes:
- "Branch Here" button in TrailBuilderPanel
- Mini-graph showing branch structure

AGENTESE: self.trail.create (with parent_index)
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add parent_index column for trail branching."""
    # Add parent_index column (nullable - NULL means root step)
    op.add_column(
        "trail_steps",
        sa.Column(
            "parent_index",
            sa.Integer(),
            nullable=True,
        ),
    )

    # Index for tree traversal (find children of a step)
    op.create_index(
        "idx_trail_steps_parent_index",
        "trail_steps",
        ["trail_id", "parent_index"],
    )


def downgrade() -> None:
    """Remove parent_index column."""
    op.drop_index("idx_trail_steps_parent_index", table_name="trail_steps")
    op.drop_column("trail_steps", "parent_index")
