"""Create self.grow tables for bicameral cortex persistence.

Revision ID: 001
Revises: None
Create Date: 2025-12-16

Tables:
- self_grow_proposals: Holon proposals with semantic search
- self_grow_nursery: Germinating holons in probationary period
- self_grow_rollback_tokens: Promotion rollback insurance
- self_grow_budget: Entropy budget singleton

AGENTESE: self.grow.* persistence layer
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def is_postgres() -> bool:
    """Check if running against PostgreSQL."""
    from alembic import context

    return context.get_context().dialect.name == "postgresql"


def upgrade() -> None:
    # === self_grow_proposals ===
    # Stores HolonProposal specifications for new holons.
    # Left Hemisphere: source of truth
    # Right Hemisphere: semantic search on why_exists
    op.execute("""
        CREATE TABLE IF NOT EXISTS self_grow_proposals (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            context TEXT NOT NULL,
            entity TEXT NOT NULL,
            proposed_by TEXT,
            proposed_at TEXT,
            status TEXT DEFAULT 'draft',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_proposals_context
        ON self_grow_proposals(context)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_proposals_status
        ON self_grow_proposals(status)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_proposals_hash
        ON self_grow_proposals(content_hash)
    """)

    # === self_grow_nursery ===
    # Stores GerminatingHolon entries during probationary period.
    # Tracks usage statistics for promotion/pruning decisions.
    op.execute("""
        CREATE TABLE IF NOT EXISTS self_grow_nursery (
            id TEXT PRIMARY KEY,
            proposal_id TEXT NOT NULL,
            data TEXT NOT NULL,
            handle TEXT NOT NULL,
            usage_count INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            failure_patterns TEXT,
            germinated_by TEXT,
            germinated_at TEXT NOT NULL,
            promoted_at TEXT,
            pruned_at TEXT,
            rollback_token TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (proposal_id) REFERENCES self_grow_proposals(id)
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_nursery_handle
        ON self_grow_nursery(handle)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_nursery_proposal
        ON self_grow_nursery(proposal_id)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_nursery_active
        ON self_grow_nursery(promoted_at, pruned_at)
    """)

    # === self_grow_rollback_tokens ===
    # Stores RollbackToken for promoted holons.
    # Enables 7-day rollback window after promotion.
    op.execute("""
        CREATE TABLE IF NOT EXISTS self_grow_rollback_tokens (
            id TEXT PRIMARY KEY,
            handle TEXT NOT NULL,
            promoted_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            spec_path TEXT,
            impl_path TEXT,
            spec_content TEXT,
            impl_content TEXT,
            created_at TEXT NOT NULL
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_rollback_handle
        ON self_grow_rollback_tokens(handle)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_rollback_expires
        ON self_grow_rollback_tokens(expires_at)
    """)

    # === self_grow_budget ===
    # Singleton table for GrowthBudget state.
    # Tracks entropy budget across sessions.
    op.execute("""
        CREATE TABLE IF NOT EXISTS self_grow_budget (
            id TEXT PRIMARY KEY DEFAULT 'singleton',
            remaining REAL NOT NULL,
            spent_this_run REAL DEFAULT 0,
            spent_by_operation TEXT,
            last_regeneration TEXT,
            config TEXT,
            updated_at TEXT NOT NULL
        )
    """)

    # Insert default budget if not exists (cross-database compatible)
    if is_postgres():
        op.execute("""
            INSERT INTO self_grow_budget (id, remaining, spent_this_run, updated_at)
            VALUES ('singleton', 1.0, 0.0, NOW())
            ON CONFLICT (id) DO NOTHING
        """)
    else:
        op.execute("""
            INSERT OR IGNORE INTO self_grow_budget (id, remaining, spent_this_run, updated_at)
            VALUES ('singleton', 1.0, 0.0, datetime('now'))
        """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS self_grow_budget")
    op.execute("DROP TABLE IF EXISTS self_grow_rollback_tokens")
    op.execute("DROP TABLE IF EXISTS self_grow_nursery")
    op.execute("DROP TABLE IF EXISTS self_grow_proposals")
