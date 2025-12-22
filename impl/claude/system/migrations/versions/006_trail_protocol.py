"""Add Trail Protocol tables.

Revision ID: 006
Revises: 005
Create Date: 2025-12-22

Tables for the Trail Protocol (spec/protocols/trail-protocol.md):
- trails: Core trail metadata with fork/merge lineage
- trail_steps: Immutable navigation steps
- trail_annotations: Comments on steps
- trail_forks: Fork relationships
- trail_evidence: Evidence linked to trails
- trail_commitments: Claims with commitment levels

AGENTESE: self.trail.*

Teaching:
    gotcha: Trail steps are IMMUTABLE once persisted.
            Annotations can be added, but steps are append-only.

    gotcha: For pgvector semantic search, embedding is stored as JSON string.
            Real pgvector would use VECTOR(1536) type.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def is_postgres() -> bool:
    """Check if running against PostgreSQL."""
    from alembic import context

    return context.get_context().dialect.name == "postgresql"


def upgrade() -> None:
    # =========================================================================
    # TRAIL PROTOCOL (First-Class Knowledge Artifacts)
    # =========================================================================

    # trails: Core trail metadata with fork/merge lineage
    if is_postgres():
        op.execute("""
            CREATE TABLE IF NOT EXISTS trails (
                id VARCHAR(64) PRIMARY KEY,
                name VARCHAR(256) NOT NULL DEFAULT '',
                created_by_id VARCHAR(64),
                created_by_archetype VARCHAR(64) DEFAULT 'developer' NOT NULL,
                version INTEGER DEFAULT 1 NOT NULL,
                forked_from_id VARCHAR(64) REFERENCES trails(id) ON DELETE SET NULL,
                merged_into_id VARCHAR(64) REFERENCES trails(id) ON DELETE SET NULL,
                fork_point INTEGER,
                topics JSONB DEFAULT '[]',
                content_hash VARCHAR(64) DEFAULT '' NOT NULL,
                is_active BOOLEAN DEFAULT TRUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        """)
        op.execute("CREATE INDEX IF NOT EXISTS idx_trails_created_by ON trails(created_by_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_trails_forked_from ON trails(forked_from_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_trails_active ON trails(is_active)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_trails_topics ON trails USING GIN(topics)")
    else:
        op.execute("""
            CREATE TABLE IF NOT EXISTS trails (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL DEFAULT '',
                created_by_id TEXT,
                created_by_archetype TEXT DEFAULT 'developer' NOT NULL,
                version INTEGER DEFAULT 1 NOT NULL,
                forked_from_id TEXT REFERENCES trails(id) ON DELETE SET NULL,
                merged_into_id TEXT REFERENCES trails(id) ON DELETE SET NULL,
                fork_point INTEGER,
                topics TEXT DEFAULT '[]',
                content_hash TEXT DEFAULT '' NOT NULL,
                is_active INTEGER DEFAULT 1 NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        op.execute("CREATE INDEX IF NOT EXISTS idx_trails_created_by ON trails(created_by_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_trails_forked_from ON trails(forked_from_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_trails_active ON trails(is_active)")

    # trail_steps: Immutable navigation steps
    if is_postgres():
        op.execute("""
            CREATE TABLE IF NOT EXISTS trail_steps (
                id VARCHAR(64) PRIMARY KEY,
                trail_id VARCHAR(64) NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                index INTEGER NOT NULL,
                explorer_id VARCHAR(64),
                explorer_archetype VARCHAR(64) DEFAULT 'developer' NOT NULL,
                source_path TEXT NOT NULL,
                edge VARCHAR(256),
                destination_paths JSONB DEFAULT '[]',
                reasoning TEXT,
                embedding_json TEXT,
                budget_consumed JSONB DEFAULT '{}',
                loop_status VARCHAR(32) DEFAULT 'OK' NOT NULL,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
                UNIQUE(trail_id, index)
            )
        """)
    else:
        op.execute("""
            CREATE TABLE IF NOT EXISTS trail_steps (
                id TEXT PRIMARY KEY,
                trail_id TEXT NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                "index" INTEGER NOT NULL,
                explorer_id TEXT,
                explorer_archetype TEXT DEFAULT 'developer' NOT NULL,
                source_path TEXT NOT NULL,
                edge TEXT,
                destination_paths TEXT DEFAULT '[]',
                reasoning TEXT,
                embedding_json TEXT,
                budget_consumed TEXT DEFAULT '{}',
                loop_status TEXT DEFAULT 'OK' NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(trail_id, "index")
            )
        """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_trail_steps_trail_id ON trail_steps(trail_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_trail_steps_source ON trail_steps(source_path)")

    # trail_annotations: Comments on steps
    if is_postgres():
        op.execute("""
            CREATE TABLE IF NOT EXISTS trail_annotations (
                id VARCHAR(64) PRIMARY KEY,
                trail_id VARCHAR(64) NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                step_index INTEGER NOT NULL,
                author_id VARCHAR(64),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        """)
    else:
        op.execute("""
            CREATE TABLE IF NOT EXISTS trail_annotations (
                id TEXT PRIMARY KEY,
                trail_id TEXT NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                step_index INTEGER NOT NULL,
                author_id TEXT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_trail_annotations_trail ON trail_annotations(trail_id)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_trail_annotations_step ON trail_annotations(trail_id, step_index)"
    )

    # trail_forks: Fork relationships
    if is_postgres():
        op.execute("""
            CREATE TABLE IF NOT EXISTS trail_forks (
                id VARCHAR(64) PRIMARY KEY,
                parent_trail_id VARCHAR(64) NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                child_trail_id VARCHAR(64) NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                fork_point INTEGER NOT NULL,
                forked_by_id VARCHAR(64),
                merged BOOLEAN DEFAULT FALSE NOT NULL,
                merge_strategy VARCHAR(32),
                merged_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        """)
    else:
        op.execute("""
            CREATE TABLE IF NOT EXISTS trail_forks (
                id TEXT PRIMARY KEY,
                parent_trail_id TEXT NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                child_trail_id TEXT NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                fork_point INTEGER NOT NULL,
                forked_by_id TEXT,
                merged INTEGER DEFAULT 0 NOT NULL,
                merge_strategy TEXT,
                merged_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_trail_forks_parent ON trail_forks(parent_trail_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_trail_forks_child ON trail_forks(child_trail_id)")

    # trail_evidence: Evidence linked to trails
    if is_postgres():
        op.execute("""
            CREATE TABLE IF NOT EXISTS trail_evidence (
                id VARCHAR(64) PRIMARY KEY,
                trail_id VARCHAR(64) NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                claim TEXT NOT NULL,
                strength VARCHAR(32) DEFAULT 'moderate' NOT NULL,
                content JSONB DEFAULT '{}',
                source_step_index INTEGER,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        """)
    else:
        op.execute("""
            CREATE TABLE IF NOT EXISTS trail_evidence (
                id TEXT PRIMARY KEY,
                trail_id TEXT NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                claim TEXT NOT NULL,
                strength TEXT DEFAULT 'moderate' NOT NULL,
                content TEXT DEFAULT '{}',
                source_step_index INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_trail_evidence_trail ON trail_evidence(trail_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_trail_evidence_strength ON trail_evidence(strength)")

    # trail_commitments: Claims with commitment levels
    if is_postgres():
        op.execute("""
            CREATE TABLE IF NOT EXISTS trail_commitments (
                id VARCHAR(64) PRIMARY KEY,
                trail_id VARCHAR(64) NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                claim TEXT NOT NULL,
                level VARCHAR(32) DEFAULT 'tentative' NOT NULL,
                evidence_ids JSONB DEFAULT '[]',
                committed_by_id VARCHAR(64),
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        """)
    else:
        op.execute("""
            CREATE TABLE IF NOT EXISTS trail_commitments (
                id TEXT PRIMARY KEY,
                trail_id TEXT NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
                claim TEXT NOT NULL,
                level TEXT DEFAULT 'tentative' NOT NULL,
                evidence_ids TEXT DEFAULT '[]',
                committed_by_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_trail_commitments_trail ON trail_commitments(trail_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_trail_commitments_level ON trail_commitments(level)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS trail_commitments")
    op.execute("DROP TABLE IF EXISTS trail_evidence")
    op.execute("DROP TABLE IF EXISTS trail_forks")
    op.execute("DROP TABLE IF EXISTS trail_annotations")
    op.execute("DROP TABLE IF EXISTS trail_steps")
    op.execute("DROP TABLE IF EXISTS trails")
