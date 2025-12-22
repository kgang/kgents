"""Add parent_mark_id for causal lineage

Revision ID: 008
Revises: 007
Create Date: 2025-12-22

Phase 2: Lineage Ergonomics
- Add parent_mark_id column for causal relationships
- Create index for tree traversal queries

CLI Commands Enabled:
- km "action" --parent mark-abc (create child marks)
- kg witness tree mark-abc (view causal tree)
- kg witness crystallize --tree mark-abc (tree-aware crystallization)

AGENTESE: world.witness.mark.lineage
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add parent_mark_id column for causal lineage."""
    # Add parent_mark_id column with self-referencing FK
    op.add_column(
        "witness_marks",
        sa.Column(
            "parent_mark_id",
            sa.String(64),
            sa.ForeignKey("witness_marks.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # Index for tree traversal (find children of a mark)
    op.create_index(
        "idx_witness_marks_parent",
        "witness_marks",
        ["parent_mark_id"],
    )


def downgrade() -> None:
    """Remove parent_mark_id column."""
    op.drop_index("idx_witness_marks_parent", table_name="witness_marks")
    op.drop_column("witness_marks", "parent_mark_id")
