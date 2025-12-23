"""
Trail Protocol: SQLAlchemy models for Postgres persistence.

Implements the data structures from spec/protocols/trail-protocol.md.

Tables:
- trails: Core trail metadata with fork/merge lineage
- trail_steps: Immutable navigation steps (append-only)
- trail_annotations: Comments on steps
- trail_forks: Fork relationships
- trail_evidence: Evidence linked to trails
- trail_commitments: Claims with commitment levels

Teaching:
    gotcha: Trail steps are IMMUTABLE once persisted.
            Use trail_annotations for comments, not step modifications.

    gotcha: pgvector extension required for embedding column.
            Run: CREATE EXTENSION IF NOT EXISTS vector;

AGENTESE: self.trail.*
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

# pgvector is required for Trail embedding columns
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

VECTOR_1536 = Vector(1536)

if TYPE_CHECKING:
    pass


def generate_trail_id() -> str:
    """Generate a unique trail ID."""
    return f"trail-{uuid.uuid4().hex[:12]}"


def generate_step_id() -> str:
    """Generate a unique step ID."""
    return f"step-{uuid.uuid4().hex[:12]}"


class TrailRow(TimestampMixin, Base):
    """
    First-class knowledge artifact.

    Not ephemeral—persisted to Postgres via D-gent.
    Not solo—supports concurrent co-exploration.
    Not linear—supports fork/merge semantics.

    Laws:
    - Immutability: Steps cannot be modified after persistence
    - Fork Independence: Forks are independent until merged
    - Merge Associativity: merge(merge(A,B),C) = merge(A,merge(B,C))
    - Evidence Monotonicity: Evidence can only grow
    - Commitment Irreversibility: Cannot downgrade commitment level

    AGENTESE: self.trail.manifest
    """

    __tablename__ = "trails"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_trail_id)
    name: Mapped[str] = mapped_column(String(256), nullable=False, default="")

    # Ownership and creation
    created_by_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_by_archetype: Mapped[str] = mapped_column(
        String(64), default="developer", nullable=False
    )

    # Optimistic locking for concurrent access
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Fork/merge lineage
    forked_from_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("trails.id", ondelete="SET NULL"),
        nullable=True,
    )
    merged_into_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("trails.id", ondelete="SET NULL"),
        nullable=True,
    )
    fork_point: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Semantic metadata
    topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    content_hash: Mapped[str] = mapped_column(String(64), default="", nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships - use back_populates without explicit argument
    steps: Mapped[list["TrailStepRow"]] = relationship(
        back_populates="trail",
        cascade="all, delete-orphan",
    )
    annotations: Mapped[list["TrailAnnotationRow"]] = relationship(
        back_populates="trail",
        cascade="all, delete-orphan",
    )
    evidence: Mapped[list["TrailEvidenceRow"]] = relationship(
        back_populates="trail",
        cascade="all, delete-orphan",
    )
    commitments: Mapped[list["TrailCommitmentRow"]] = relationship(
        back_populates="trail",
        cascade="all, delete-orphan",
    )

    # Fork children
    forked_trails: Mapped[list["TrailRow"]] = relationship(
        back_populates="parent_trail",
        foreign_keys=[forked_from_id],
    )
    parent_trail: Mapped["TrailRow | None"] = relationship(
        back_populates="forked_trails",
        foreign_keys=[forked_from_id],
        remote_side=[id],
    )

    @property
    def step_count(self) -> int:
        """Number of steps in this trail."""
        return len(self.steps) if self.steps else 0

    def bump_version(self) -> None:
        """Increment version for optimistic locking."""
        self.version += 1


class TrailStepRow(TimestampMixin, Base):
    """
    Single navigation action in a trail.

    Immutable once recorded. Forms the audit trail.
    Each step records: where we were, what edge we followed, where we went.

    Teaching:
        gotcha: Steps are APPEND-ONLY. Never modify a persisted step.
                Use TrailAnnotation to add comments.
    """

    __tablename__ = "trail_steps"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_step_id)
    trail_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("trails.id", ondelete="CASCADE"),
        nullable=False,
    )
    index: Mapped[int] = mapped_column(Integer, nullable=False)

    # Parent step for branching (NULL = root step, integer = index of parent)
    # Enables tree-structured trails where exploration can branch
    parent_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Who took this step
    explorer_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    explorer_archetype: Mapped[str] = mapped_column(String(64), default="developer", nullable=False)

    # Navigation data
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    edge: Mapped[str | None] = mapped_column(String(256), nullable=True)
    destination_paths: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Semantic enrichment
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Embedding for semantic search
    # Legacy: embedding_json stores JSON-serialized embedding (Text)
    # Native: embedding stores pgvector VECTOR(1536) for native similarity search
    embedding_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Native pgvector embedding column (1536 dimensions for OpenAI text-embedding-3-small)
    # Uses <=> operator for cosine distance in search queries
    # pgvector extension required: CREATE EXTENSION IF NOT EXISTS vector;
    embedding: Mapped[list[float] | None] = mapped_column(
        VECTOR_1536,
        nullable=True,
    )

    # Budget tracking
    budget_consumed: Mapped[dict[str, int]] = mapped_column(JSON, default=dict)
    loop_status: Mapped[str] = mapped_column(String(32), default="OK", nullable=False)

    # Relationship
    trail: Mapped["TrailRow"] = relationship(back_populates="steps")


class TrailAnnotationRow(TimestampMixin, Base):
    """
    Comment or annotation on a trail step.

    Annotations are mutable—they can be added, edited, deleted.
    Steps are immutable; annotations provide the flexibility.
    """

    __tablename__ = "trail_annotations"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: f"ann-{uuid.uuid4().hex[:12]}"
    )
    trail_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("trails.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)

    # Author
    author_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationship
    trail: Mapped["TrailRow"] = relationship(back_populates="annotations")


class TrailForkRow(TimestampMixin, Base):
    """
    Fork point in a trail, enabling divergent exploration.

    Like git branches—multiple explorers can diverge
    and later merge their findings.

    Laws:
    - Fork Independence: Changes to fork don't affect parent
    - Merge preserves both histories
    """

    __tablename__ = "trail_forks"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: f"fork-{uuid.uuid4().hex[:12]}"
    )
    parent_trail_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("trails.id", ondelete="CASCADE"),
        nullable=False,
    )
    child_trail_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("trails.id", ondelete="CASCADE"),
        nullable=False,
    )
    fork_point: Mapped[int] = mapped_column(Integer, nullable=False)

    # Who forked
    forked_by_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Merge state
    merged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    merge_strategy: Mapped[str | None] = mapped_column(String(32), nullable=True)
    merged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class TrailEvidenceRow(TimestampMixin, Base):
    """
    Evidence linked to a trail.

    Evidence is gathered during exploration and used to support commitments.
    Evidence strength: WEAK, MODERATE, STRONG

    Law: Evidence Monotonicity—evidence can only grow.
    """

    __tablename__ = "trail_evidence"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: f"evid-{uuid.uuid4().hex[:12]}"
    )
    trail_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("trails.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Evidence content
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    strength: Mapped[str] = mapped_column(
        String(32), default="moderate", nullable=False
    )  # weak, moderate, strong
    content: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)

    # Source step (optional)
    source_step_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationship
    trail: Mapped["TrailRow"] = relationship(back_populates="evidence")


class TrailCommitmentRow(TimestampMixin, Base):
    """
    A claim committed based on trail evidence.

    Commitment levels: TENTATIVE, MODERATE, STRONG, DEFINITIVE

    Laws:
    - Commitment Irreversibility: Cannot downgrade level
    - Requirements must be met for each level
    """

    __tablename__ = "trail_commitments"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: f"comm-{uuid.uuid4().hex[:12]}"
    )
    trail_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("trails.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Commitment content
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(
        String(32), default="tentative", nullable=False
    )  # tentative, moderate, strong, definitive

    # Evidence supporting this commitment
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Who committed
    committed_by_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationship
    trail: Mapped["TrailRow"] = relationship(back_populates="commitments")


__all__ = [
    "TrailRow",
    "TrailStepRow",
    "TrailAnnotationRow",
    "TrailForkRow",
    "TrailEvidenceRow",
    "TrailCommitmentRow",
    "generate_trail_id",
    "generate_step_id",
]
