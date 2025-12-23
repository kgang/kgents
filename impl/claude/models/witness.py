"""
Witness Crown Jewel: The 8th Jewel Tables.

Tables for the Witness daemon's persistent state:
- WitnessTrust: Per-user trust level with decay
- WitnessThought: Thought stream for recency queries
- WitnessAction: Action history with rollback info
- WitnessEscalation: Trust escalation audit trail

The Dual-Track Pattern:
- These tables: Fast queries by recency, user, status
- D-gent datum: Semantic search, associative connections (via datum_id links)

AGENTESE: self.witness.*
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from typing import Optional


def hash_email(email: str) -> str:
    """Hash git email for privacy-preserving trust keys."""
    return hashlib.sha256(email.lower().encode()).hexdigest()[:16]


class WitnessTrust(TimestampMixin, Base):
    """
    Trust level for a git user in a repository.

    Trust is earned through consistent, valuable observations:
    - L0 READ_ONLY: 0 (default)
    - L1 BOUNDED: 1 (can write to .kgents/)
    - L2 SUGGESTION: 2 (can propose changes)
    - L3 AUTONOMOUS: 3 (full developer agency)

    Trust decays over inactivity:
    - 0.1 levels per 24h of inactivity
    - Minimum floor: L1 (never drops below L1 after first achievement)
    """

    __tablename__ = "witness_trust"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # hash_email(git_email)
    git_email_hash: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    repository_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Trust level (0-3)
    trust_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trust_level_raw: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Activity tracking for decay
    last_active: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Escalation metrics (for tracking progress toward next level)
    observation_count: Mapped[int] = mapped_column(Integer, default=0)
    successful_operations: Mapped[int] = mapped_column(Integer, default=0)
    confirmed_suggestions: Mapped[int] = mapped_column(Integer, default=0)
    total_suggestions: Mapped[int] = mapped_column(Integer, default=0)

    # Escalation history
    escalations: Mapped[list["WitnessEscalation"]] = relationship(
        "WitnessEscalation",
        back_populates="trust",
        cascade="all, delete-orphan",
        order_by="WitnessEscalation.created_at.desc()",
    )

    __table_args__ = (  # type: ignore[assignment]
        Index("idx_witness_trust_email", "git_email_hash"),
        Index("idx_witness_trust_level", "trust_level"),
    )

    def touch(self) -> None:
        """Update last_active timestamp."""
        self.last_active = datetime.now(UTC)

    def apply_decay(self) -> "WitnessTrust":
        """
        Apply trust decay based on inactivity.

        Trust decays by 0.1 levels per 24h of inactivity.
        Minimum floor: L1 (never drops below L1 after first achievement).
        """
        # Ensure last_active is timezone-aware for comparison
        last_active = self.last_active
        if last_active.tzinfo is None:
            last_active = last_active.replace(tzinfo=UTC)
        hours_inactive = (datetime.now(UTC) - last_active).total_seconds() / 3600
        decay_steps = int(hours_inactive / 24) * 0.1

        # Apply decay to raw level
        new_raw = max(self.trust_level_raw - decay_steps, 0.0)

        # Floor at L1 if ever achieved
        if self.trust_level >= 1:
            new_raw = max(new_raw, 1.0)

        self.trust_level_raw = new_raw
        self.trust_level = int(new_raw)
        return self


class WitnessThought(TimestampMixin, Base):
    """
    A thought in the thought stream.

    Thoughts are observations crystallized from events.
    Dual-track: SQL for recency queries, D-gent for semantic search.

    The thought stream is both a **semantic corpus** (for pattern detection)
    and a **temporal log** (for recent thoughts display).
    """

    __tablename__ = "witness_thoughts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    trust_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("witness_trust.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)  # git, tests, ci, etc.
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)

    # D-gent link for semantic search
    datum_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Repository context
    repository_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    __table_args__ = (  # type: ignore[assignment]
        Index("idx_witness_thoughts_recent", "created_at"),
        Index("idx_witness_thoughts_source", "source"),
        Index("idx_witness_thoughts_tags", "tags", postgresql_using="gin"),
    )


class WitnessAction(TimestampMixin, Base):
    """
    An action executed by the Witness (L3 only).

    All actions are logged and (ideally) reversible.
    Rollback info is stored for 7 days.
    """

    __tablename__ = "witness_actions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    trust_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("witness_trust.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Action details
    action: Mapped[str] = mapped_column(Text, nullable=False)
    target: Mapped[str | None] = mapped_column(String(512), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    message: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # Rollback info
    reversible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    inverse_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    git_stash_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    checkpoint_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Repository context
    repository_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    __table_args__ = (  # type: ignore[assignment]
        Index("idx_witness_actions_recent", "created_at"),
        Index("idx_witness_actions_success", "success"),
        Index("idx_witness_actions_reversible", "reversible"),
    )


class WitnessEscalation(TimestampMixin, Base):
    """
    Audit trail for trust escalation events.

    Records every trust level change for accountability.
    """

    __tablename__ = "witness_escalations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trust_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("witness_trust.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Escalation details
    from_level: Mapped[int] = mapped_column(Integer, nullable=False)
    to_level: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    # Metrics at time of escalation
    observation_count: Mapped[int] = mapped_column(Integer, default=0)
    successful_operations: Mapped[int] = mapped_column(Integer, default=0)
    confirmed_suggestions: Mapped[int] = mapped_column(Integer, default=0)
    total_suggestions: Mapped[int] = mapped_column(Integer, default=0)
    acceptance_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationship
    trust: Mapped["WitnessTrust"] = relationship("WitnessTrust", back_populates="escalations")

    __table_args__ = (  # type: ignore[assignment]
        Index("idx_witness_escalations_trust", "trust_id"),
        Index("idx_witness_escalations_recent", "created_at"),
    )


class WitnessMark(TimestampMixin, Base):
    """
    A Mark in the Witness ledger.

    Marks are the atomic unit of witnessed behavior:
    - Every action leaves a mark
    - Marks are immutable once created
    - Marks can have reasoning and principles
    - Marks can have tags for categorization and querying

    Used by the `km` CLI command for everyday mark-making.

    Evidence Tag Taxonomy (spec/protocols/living-spec-evidence.md):
    - spec:{path}        — Mark relates to a spec (e.g., spec:principles.md)
    - evidence:impl      — Declares implementation evidence
    - evidence:test      — Declares test evidence
    - evidence:usage     — Declares usage evidence
    - evidence:run       — Records a test run
    - evidence:pass      — Test passed
    - evidence:fail      — Test failed
    - eureka, gotcha, taste, friction, joy, veto — Session tags

    AGENTESE: world.witness.mark / time.witness.mark
    """

    __tablename__ = "witness_marks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # What was done
    action: Mapped[str] = mapped_column(Text, nullable=False)

    # Why (optional but encouraged)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Which principles honored (stored as JSONB array for GIN indexing)
    principles: Mapped[list[str]] = mapped_column(JSONB, default=list)

    # General tags for categorization (stored as JSONB array for GIN indexing)
    # Includes evidence tags (spec:*, evidence:*) and session tags (eureka, gotcha, etc.)
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)

    # Authorship
    author: Mapped[str] = mapped_column(String(64), default="kent", nullable=False)

    # Session context (for grouping marks)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Parent mark for causal lineage (--parent flag)
    parent_mark_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("witness_marks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # D-gent link for semantic search
    datum_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Repository context
    repository_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    __table_args__ = (  # type: ignore[assignment]
        Index("idx_witness_marks_recent", "created_at"),
        Index("idx_witness_marks_author", "author"),
        Index("idx_witness_marks_session", "session_id"),
        Index("idx_witness_marks_tags", "tags", postgresql_using="gin"),
        Index("idx_witness_marks_principles", "principles", postgresql_using="gin"),
    )


__all__ = [
    "WitnessTrust",
    "WitnessThought",
    "WitnessAction",
    "WitnessEscalation",
    "WitnessMark",
    "hash_email",
]
