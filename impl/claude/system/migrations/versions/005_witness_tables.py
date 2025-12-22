"""Add Witness Crown Jewel tables.

Revision ID: 005
Revises: 004
Create Date: 2025-12-22

Tables for the Witness (8th Crown Jewel):
- witness_trust: Per-user trust level with decay
- witness_thoughts: Thought stream for recency queries
- witness_actions: Action history with rollback info
- witness_escalations: Trust escalation audit trail

AGENTESE: self.witness.*
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def is_postgres() -> bool:
    """Check if running against PostgreSQL."""
    from alembic import context

    return context.get_context().dialect.name == "postgresql"


def upgrade() -> None:
    # =========================================================================
    # WITNESS CROWN JEWEL (8th Jewel)
    # =========================================================================

    # witness_trust: Per-user trust level with decay
    if is_postgres():
        op.execute("""
            CREATE TABLE IF NOT EXISTS witness_trust (
                id VARCHAR(64) PRIMARY KEY,
                git_email_hash VARCHAR(16) NOT NULL,
                repository_path VARCHAR(512),
                trust_level INTEGER DEFAULT 0 NOT NULL,
                trust_level_raw FLOAT DEFAULT 0.0 NOT NULL,
                last_active TIMESTAMP DEFAULT NOW() NOT NULL,
                observation_count INTEGER DEFAULT 0,
                successful_operations INTEGER DEFAULT 0,
                confirmed_suggestions INTEGER DEFAULT 0,
                total_suggestions INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        """)
    else:
        op.execute("""
            CREATE TABLE IF NOT EXISTS witness_trust (
                id TEXT PRIMARY KEY,
                git_email_hash TEXT NOT NULL,
                repository_path TEXT,
                trust_level INTEGER DEFAULT 0 NOT NULL,
                trust_level_raw REAL DEFAULT 0.0 NOT NULL,
                last_active TEXT NOT NULL,
                observation_count INTEGER DEFAULT 0,
                successful_operations INTEGER DEFAULT 0,
                confirmed_suggestions INTEGER DEFAULT 0,
                total_suggestions INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_witness_trust_email ON witness_trust(git_email_hash)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_witness_trust_level ON witness_trust(trust_level)")

    # witness_thoughts: Thought stream with dual-track storage
    if is_postgres():
        op.execute("""
            CREATE TABLE IF NOT EXISTS witness_thoughts (
                id VARCHAR(64) PRIMARY KEY,
                trust_id VARCHAR(64) REFERENCES witness_trust(id) ON DELETE SET NULL,
                content TEXT NOT NULL,
                source VARCHAR(64) NOT NULL,
                tags JSONB DEFAULT '[]',
                datum_id VARCHAR(64),
                repository_path VARCHAR(512),
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        """)
        # PostgreSQL uses GIN for JSON/JSONB indexes
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_witness_thoughts_recent ON witness_thoughts(created_at)"
        )
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_witness_thoughts_source ON witness_thoughts(source)"
        )
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_witness_thoughts_datum ON witness_thoughts(datum_id)"
        )
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_witness_thoughts_tags ON witness_thoughts USING GIN(tags)"
        )
    else:
        op.execute("""
            CREATE TABLE IF NOT EXISTS witness_thoughts (
                id TEXT PRIMARY KEY,
                trust_id TEXT REFERENCES witness_trust(id) ON DELETE SET NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                tags TEXT DEFAULT '[]',
                datum_id TEXT,
                repository_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_witness_thoughts_recent ON witness_thoughts(created_at)"
        )
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_witness_thoughts_source ON witness_thoughts(source)"
        )
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_witness_thoughts_datum ON witness_thoughts(datum_id)"
        )

    # witness_actions: Action history with rollback info
    if is_postgres():
        op.execute("""
            CREATE TABLE IF NOT EXISTS witness_actions (
                id VARCHAR(64) PRIMARY KEY,
                trust_id VARCHAR(64) REFERENCES witness_trust(id) ON DELETE SET NULL,
                action TEXT NOT NULL,
                target VARCHAR(512),
                success BOOLEAN DEFAULT TRUE NOT NULL,
                message TEXT DEFAULT '' NOT NULL,
                reversible BOOLEAN DEFAULT TRUE NOT NULL,
                inverse_action TEXT,
                git_stash_ref VARCHAR(128),
                checkpoint_path VARCHAR(512),
                repository_path VARCHAR(512),
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        """)
    else:
        op.execute("""
            CREATE TABLE IF NOT EXISTS witness_actions (
                id TEXT PRIMARY KEY,
                trust_id TEXT REFERENCES witness_trust(id) ON DELETE SET NULL,
                action TEXT NOT NULL,
                target TEXT,
                success INTEGER DEFAULT 1 NOT NULL,
                message TEXT DEFAULT '' NOT NULL,
                reversible INTEGER DEFAULT 1 NOT NULL,
                inverse_action TEXT,
                git_stash_ref TEXT,
                checkpoint_path TEXT,
                repository_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_witness_actions_recent ON witness_actions(created_at)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_witness_actions_success ON witness_actions(success)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_witness_actions_reversible ON witness_actions(reversible)"
    )

    # witness_escalations: Trust escalation audit trail
    if is_postgres():
        op.execute("""
            CREATE TABLE IF NOT EXISTS witness_escalations (
                id SERIAL PRIMARY KEY,
                trust_id VARCHAR(64) NOT NULL REFERENCES witness_trust(id) ON DELETE CASCADE,
                from_level INTEGER NOT NULL,
                to_level INTEGER NOT NULL,
                reason TEXT NOT NULL,
                observation_count INTEGER DEFAULT 0,
                successful_operations INTEGER DEFAULT 0,
                confirmed_suggestions INTEGER DEFAULT 0,
                total_suggestions INTEGER DEFAULT 0,
                acceptance_rate FLOAT DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        """)
    else:
        op.execute("""
            CREATE TABLE IF NOT EXISTS witness_escalations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trust_id TEXT NOT NULL REFERENCES witness_trust(id) ON DELETE CASCADE,
                from_level INTEGER NOT NULL,
                to_level INTEGER NOT NULL,
                reason TEXT NOT NULL,
                observation_count INTEGER DEFAULT 0,
                successful_operations INTEGER DEFAULT 0,
                confirmed_suggestions INTEGER DEFAULT 0,
                total_suggestions INTEGER DEFAULT 0,
                acceptance_rate REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_witness_escalations_trust ON witness_escalations(trust_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_witness_escalations_recent ON witness_escalations(created_at)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS witness_escalations")
    op.execute("DROP TABLE IF EXISTS witness_actions")
    op.execute("DROP TABLE IF EXISTS witness_thoughts")
    op.execute("DROP TABLE IF EXISTS witness_trust")
