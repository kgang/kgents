"""Migrate JSON columns to JSONB for GIN indexing

Revision ID: 010
Revises: 009
Create Date: 2025-12-22

JSONB enables:
- GIN indexes for efficient containment queries (@>, <@, ?, ?|, ?&)
- Better query performance for tag filtering
- Proper indexing for witness_marks.tags and witness_marks.principles

Tables affected:
- witness_marks: tags, principles
- witness_thoughts: tags

AGENTESE: time.witness.migrate
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert JSON columns to JSONB and create GIN indexes."""
    # Check if we're on PostgreSQL (JSONB is Postgres-specific)
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        # SQLite doesn't have JSONB, skip migration
        return

    # --- witness_marks table ---

    # Add tags column if it doesn't exist (fixes missing column issue)
    # Then convert to JSONB
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'witness_marks' AND column_name = 'tags'
            ) THEN
                ALTER TABLE witness_marks ADD COLUMN tags JSONB DEFAULT '[]';
            ELSE
                ALTER TABLE witness_marks
                    ALTER COLUMN tags TYPE JSONB USING tags::JSONB;
            END IF;
        END $$;
    """)

    # Convert principles to JSONB
    op.execute("""
        ALTER TABLE witness_marks
            ALTER COLUMN principles TYPE JSONB USING principles::JSONB;
    """)

    # Create GIN indexes for efficient containment queries
    # Drop existing indexes first if they exist (might be wrong type)
    op.execute("DROP INDEX IF EXISTS idx_witness_marks_tags;")
    op.execute("DROP INDEX IF EXISTS idx_witness_marks_principles;")

    op.create_index(
        "idx_witness_marks_tags",
        "witness_marks",
        ["tags"],
        postgresql_using="gin",
    )
    op.create_index(
        "idx_witness_marks_principles",
        "witness_marks",
        ["principles"],
        postgresql_using="gin",
    )

    # --- witness_thoughts table ---

    # Convert tags to JSONB
    op.execute("""
        ALTER TABLE witness_thoughts
            ALTER COLUMN tags TYPE JSONB USING tags::JSONB;
    """)

    # Recreate GIN index
    op.execute("DROP INDEX IF EXISTS idx_witness_thoughts_tags;")
    op.create_index(
        "idx_witness_thoughts_tags",
        "witness_thoughts",
        ["tags"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Convert JSONB columns back to JSON."""
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # Drop GIN indexes (they won't work with JSON)
    op.drop_index("idx_witness_marks_tags", table_name="witness_marks")
    op.drop_index("idx_witness_marks_principles", table_name="witness_marks")
    op.drop_index("idx_witness_thoughts_tags", table_name="witness_thoughts")

    # Convert back to JSON
    op.execute("""
        ALTER TABLE witness_marks
            ALTER COLUMN tags TYPE JSON USING tags::JSON,
            ALTER COLUMN principles TYPE JSON USING principles::JSON;
    """)

    op.execute("""
        ALTER TABLE witness_thoughts
            ALTER COLUMN tags TYPE JSON USING tags::JSON;
    """)
