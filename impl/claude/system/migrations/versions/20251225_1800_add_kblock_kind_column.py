"""
Add 'kind' column to kblocks table.

Revision ID: 20251225_1800
Revises: 20251225_1720
Create Date: 2025-12-25 18:00:00.000000

The 'kind' column was missing from the initial migration.
This column distinguishes K-Block types:
- file: Traditional filesystem content
- upload: User-uploaded content (sovereign)
- zero_node: Zero Seed nodes (axioms, values, goals, etc.)
- agent_state: Serialized agent polynomial states
- crystal: Crystallized memories/decisions from Witness
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '20251225_1800'
down_revision = '20251225_1720'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add 'kind' column to kblocks table."""
    # Add the kind column with default value
    op.add_column(
        'kblocks',
        sa.Column('kind', sa.String(length=32), nullable=False, server_default='file')
    )

    # Create index for kind column
    op.create_index('idx_kblocks_unified_kind', 'kblocks', ['kind'])

    # Update existing zero_node rows to have kind='zero_node'
    op.execute(
        """
        UPDATE kblocks
        SET kind = 'zero_node'
        WHERE zero_seed_layer IS NOT NULL
        """
    )


def downgrade() -> None:
    """Remove 'kind' column from kblocks table."""
    op.drop_index('idx_kblocks_unified_kind', 'kblocks')
    op.drop_column('kblocks', 'kind')
