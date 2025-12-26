"""
Add K-Block tables for Zero Seed persistence.

Revision ID: 20251225_1720
Revises:
Create Date: 2025-12-25 17:20:00.000000

This migration adds tables for K-Block storage:
- kblocks: Main K-Block table with Zero Seed support
- kblock_edges: Normalized edge table for graph queries

K-Blocks represent both regular files and Zero Seed nodes (axioms, values, goals, etc.).
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251225_1720'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create K-Block tables."""
    # Create kblocks table
    op.create_table(
        'kblocks',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('path', sa.String(length=512), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('base_content', sa.Text(), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('isolation', sa.String(length=32), nullable=False),
        sa.Column('zero_seed_layer', sa.Integer(), nullable=True),
        sa.Column('zero_seed_kind', sa.String(length=64), nullable=True),
        sa.Column('lineage', sa.JSON(), nullable=False),
        sa.Column('has_proof', sa.Integer(), nullable=False),
        sa.Column('toulmin_proof', sa.JSON(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('incoming_edges', sa.JSON(), nullable=False),
        sa.Column('outgoing_edges', sa.JSON(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('created_by', sa.String(length=128), nullable=False),
        sa.Column('not_ingested', sa.Integer(), nullable=False),
        sa.Column('analysis_required', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create indexes for kblocks
    op.create_index('idx_kblocks_layer', 'kblocks', ['zero_seed_layer'])
    op.create_index('idx_kblocks_kind', 'kblocks', ['zero_seed_kind'])
    op.create_index('idx_kblocks_path', 'kblocks', ['path'])
    op.create_index('idx_kblocks_created', 'kblocks', ['created_at'])
    op.create_index(op.f('ix_kblocks_content_hash'), 'kblocks', ['content_hash'])

    # Create GIN indexes for JSONB columns (PostgreSQL only)
    # For SQLite, these will be ignored
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_catalog.pg_class c
                WHERE c.relname = 'kblocks'
            ) THEN
                CREATE INDEX IF NOT EXISTS idx_kblocks_tags
                ON kblocks USING GIN (tags);

                CREATE INDEX IF NOT EXISTS idx_kblocks_lineage
                ON kblocks USING GIN (lineage);
            END IF;
        EXCEPTION
            WHEN undefined_object THEN
                -- PostgreSQL not available, skip GIN indexes
                NULL;
        END $$;
        """
    )

    # Create kblock_edges table
    op.create_table(
        'kblock_edges',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('source_id', sa.String(length=64), nullable=False),
        sa.Column('target_id', sa.String(length=64), nullable=False),
        sa.Column('kind', sa.String(length=64), nullable=False),
        sa.Column('label', sa.Text(), nullable=True),
        sa.Column('edge_metadata', sa.JSON(), nullable=False),
        sa.Column('created_by', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create indexes for kblock_edges
    op.create_index('idx_kblock_edges_source', 'kblock_edges', ['source_id'])
    op.create_index('idx_kblock_edges_target', 'kblock_edges', ['target_id'])
    op.create_index('idx_kblock_edges_kind', 'kblock_edges', ['kind'])
    op.create_index('idx_kblock_edges_source_kind', 'kblock_edges', ['source_id', 'kind'])
    op.create_index('idx_kblock_edges_target_kind', 'kblock_edges', ['target_id', 'kind'])


def downgrade() -> None:
    """Drop K-Block tables."""
    op.drop_table('kblock_edges')
    op.drop_table('kblocks')
