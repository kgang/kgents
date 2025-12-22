"""Add pgvector embedding column to trail_steps.

Revision ID: 007
Revises: 006
Create Date: 2025-12-22

Enables native pgvector semantic search for trails:
- Adds VECTOR(1536) column for OpenAI text-embedding-3-small embeddings
- Creates IVFFlat index with cosine distance for approximate nearest neighbor
- Gracefully handles non-Postgres backends (SQLite uses TEXT fallback)

AGENTESE: self.trail.search (semantic)

Teaching:
    gotcha: pgvector extension must exist before VECTOR column can be created.
            The migration enables it with CREATE EXTENSION IF NOT EXISTS.

    gotcha: IVFFlat index requires data before it's effective.
            For small datasets (<10K vectors), exact search may be faster.

    gotcha: Migration 006 used embedding_json (TEXT). This migration adds
            native embedding (VECTOR) alongside it. Old data needs backfill.

See: spec/protocols/trail-protocol.md 4.1 (Dual-Mode Semantic Matching)
See: plans/pgvector-integration.md
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def is_postgres() -> bool:
    """Check if running against PostgreSQL."""
    from alembic import context

    return context.get_context().dialect.name == "postgresql"


def upgrade() -> None:
    """
    Add pgvector embedding column and IVFFlat index.

    For Postgres:
    - Enable pgvector extension
    - Add VECTOR(1536) column to trail_steps
    - Create IVFFlat index with vector_cosine_ops

    For SQLite (fallback):
    - No action (continues using embedding_json TEXT column)
    """
    if not is_postgres():
        # SQLite doesn't support pgvector, skip
        # Semantic search falls back to Python cosine similarity
        return

    # Enable pgvector extension
    # Safe to run multiple times (IF NOT EXISTS)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Add VECTOR(1536) column for native pgvector storage
    # 1536 dimensions = OpenAI text-embedding-3-small
    # Nullable because existing rows won't have embeddings
    op.execute("""
        ALTER TABLE trail_steps
        ADD COLUMN IF NOT EXISTS embedding VECTOR(1536)
    """)

    # Create IVFFlat index for approximate nearest neighbor search
    # - lists=100: 100 Voronoi cells (good for 10K-100K vectors)
    # - vector_cosine_ops: Use cosine distance (<=>)
    #
    # Note: IVFFlat needs training data. For best performance:
    # 1. Insert vectors without index
    # 2. Build index after dataset is populated
    #
    # For now we create it immediately for simplicity.
    # Rebuild with: REINDEX INDEX idx_trail_steps_embedding_vector;
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_trail_steps_embedding_vector
        ON trail_steps
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)


def downgrade() -> None:
    """Remove pgvector embedding column and index."""
    if not is_postgres():
        return

    # Drop index first (depends on column)
    op.execute("DROP INDEX IF EXISTS idx_trail_steps_embedding_vector")

    # Drop column
    op.execute("ALTER TABLE trail_steps DROP COLUMN IF EXISTS embedding")

    # Note: We don't drop the pgvector extension as other tables may use it
