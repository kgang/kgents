"""
K-Block Models: PostgreSQL persistence for Zero Seed K-Blocks.

This module defines SQLAlchemy models for K-Block storage in PostgreSQL.

UNIFICATION PRINCIPLE (AD-010):
    Everything is an Agent, and every Agent can be represented as a K-Block.

K-Blocks are transactional editing containers that can represent:
- FILE: Traditional filesystem content (specs, implementations)
- UPLOAD: User-uploaded content (sovereign)
- ZERO_NODE: Zero Seed nodes (axioms, values, goals, specs, actions, reflections, representations)
- AGENT_STATE: Serialized agent polynomial states
- CRYSTAL: Crystallized memories/decisions from Witness

The models support:
- Full K-Block metadata (layer, kind, lineage, confidence)
- Edge tracking (incoming/outgoing edges for graph traversal)
- Proof tracking (Toulmin proofs for verified nodes)
- Zero Seed integration (7-layer hierarchy)

AGENTESE: self.data.table.kblock.*
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    pass


class KBlock(TimestampMixin, Base):
    """
    K-Block: Transactional editing container with Zero Seed support.

    UNIFICATION PRINCIPLE (AD-010):
        Everything is an Agent, and every Agent can be represented as a K-Block.

    A K-Block can be:
    1. FILE: Traditional filesystem content (specs, implementations)
    2. UPLOAD: User-uploaded content (sovereign)
    3. ZERO_NODE: Zero Seed node (zero_seed_layer=1-7) - axioms, values, goals, etc.
    4. AGENT_STATE: Serialized agent polynomial states
    5. CRYSTAL: Crystallized memories/decisions from Witness

    The Zero Seed 7-layer hierarchy (for kind="zero_node"):
    - L0: Zero Seed itself (the genesis)
    - L1: Axioms (categorical ground truths)
    - L2: Values (what we care about)
    - L3: Goals (what we aim for)
    - L4: Specs (how we achieve goals)
    - L5: Actions (implementations)
    - L6: Reflections (learnings)
    - L7: Representations (projections)

    Storage pattern:
    - Queryable metadata in this table (fast filtering by layer, kind, tags)
    - Full content in 'content' field (markdown)
    - Edges in JSONB for graph traversal
    """

    __tablename__ = "kblocks"

    # Identity
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    path: Mapped[str] = mapped_column(String(512), nullable=False, index=True)

    # Kind (Unification: Everything is an Agent)
    # Valid values: file, upload, zero_node, agent_state, crystal
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="file", index=True)

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    base_content: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Content at creation (for diffing)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # State
    isolation: Mapped[str] = mapped_column(
        String(32), nullable=False, default="PRISTINE"
    )  # PRISTINE, DIRTY, STALE, CONFLICTING, ENTANGLED

    # Zero Seed Integration (NULL for regular files)
    zero_seed_layer: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True
    )  # 0-7
    zero_seed_kind: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )  # "axiom", "value", "goal", etc.

    # Derivation (lineage tracking)
    lineage: Mapped[list[str]] = mapped_column(
        JSON, default=list
    )  # Parent K-Block IDs

    # Proof tracking
    has_proof: Mapped[bool] = mapped_column(Integer, default=0)  # Boolean as 0/1
    toulmin_proof: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Toulmin proof structure

    # Confidence
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    # Edges (JSON for graph queries - use JSONB in PostgreSQL migrations)
    # Format: [{"id": "edge_id", "source": "kb_1", "target": "kb_2", "kind": "derives_from", "label": "..."}]
    incoming_edges: Mapped[list[dict]] = mapped_column(JSON, default=list)
    outgoing_edges: Mapped[list[dict]] = mapped_column(JSON, default=list)

    # Metadata
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_by: Mapped[str] = mapped_column(String(128), default="system")

    # Sovereignty indicators
    not_ingested: Mapped[bool] = mapped_column(
        Integer, default=0
    )  # Not in cosmos or sovereign store
    analysis_required: Mapped[bool] = mapped_column(
        Integer, default=0
    )  # Needs analysis before editing

    __table_args__ = (
        # Fast queries by unified kind (Unification: Everything is an Agent)
        Index("idx_kblocks_unified_kind", "kind"),
        # Fast queries by layer
        Index("idx_kblocks_layer", "zero_seed_layer"),
        # Fast queries by zero_seed_kind (distinct from unified kind)
        Index("idx_kblocks_kind", "zero_seed_kind"),
        # Fast queries by path (file lookups)
        Index("idx_kblocks_path", "path"),
        # Fast queries by creation time (recent nodes)
        Index("idx_kblocks_created", "created_at"),
        # Note: GIN indexes for tags/lineage are created via Alembic migration
        # for PostgreSQL (requires JSONB type). SQLite uses regular B-tree.
    )

    def __repr__(self) -> str:
        layer_str = f"L{self.zero_seed_layer}" if self.zero_seed_layer is not None else ""
        kind_str = self.kind
        layer_suffix = f", {layer_str}" if layer_str else ""
        return f"<KBlock(id={self.id!r}, kind={kind_str}{layer_suffix}, path={self.path!r})>"


class KBlockEdge(TimestampMixin, Base):
    """
    K-Block Edge: Typed relationships between K-Blocks.

    Edges form the derivation DAG and semantic graph:
    - derives_from: Child node derives from parent
    - refines: Node refines another node
    - contradicts: Node contradicts another node
    - evidence_for: Node provides evidence for another
    - implements: Implementation of a spec

    Edges are stored both:
    1. In the KBlock.incoming_edges and KBlock.outgoing_edges JSONB fields (for fast traversal)
    2. In this normalized table (for complex queries)

    The dual storage enables:
    - Fast graph traversal (JSONB in KBlock)
    - Complex edge queries (this table)
    """

    __tablename__ = "kblock_edges"

    # Identity
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Edge endpoints
    source_id: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # Source K-Block
    target_id: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # Target K-Block

    # Edge type
    kind: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str | None] = mapped_column(Text, nullable=True)  # Human-readable label

    # Edge metadata (renamed to avoid SQLAlchemy reserved name)
    edge_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[str] = mapped_column(String(128), default="system")

    __table_args__ = (
        # Fast queries for all edges from a node
        Index("idx_kblock_edges_source", "source_id"),
        # Fast queries for all edges to a node
        Index("idx_kblock_edges_target", "target_id"),
        # Fast queries by edge type
        Index("idx_kblock_edges_kind", "kind"),
        # Fast queries for specific edge types between nodes
        Index("idx_kblock_edges_source_kind", "source_id", "kind"),
        Index("idx_kblock_edges_target_kind", "target_id", "kind"),
    )

    def __repr__(self) -> str:
        return f"<KBlockEdge(id={self.id!r}, {self.source_id} --{self.kind}--> {self.target_id})>"


__all__ = ["KBlock", "KBlockEdge"]
