"""
Brain Crown Jewel: Spatial Cathedral of Memory.

Tables for the Brain's crystallized knowledge with queryable metadata.
Hybrid storage: Alembic tables for queryable metadata + D-gent for semantic content.

AGENTESE: self.data.table.crystal.*
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
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

from .base import Base, CausalMixin, TimestampMixin

# Use JSONB on PostgreSQL, JSON elsewhere (for GIN indexes)
JSONBCompat = JSON().with_variant(JSONB(), "postgresql")

if TYPE_CHECKING:
    from typing import Optional


class Crystal(TimestampMixin, Base):
    """
    A crystallized piece of knowledge in the Brain.

    Crystals are the atomic units of memory - facts, insights, learnings
    that have been distilled and stored. Each crystal has:
    - Queryable metadata (tags, access patterns, summary)
    - Link to semantic content in D-gent (datum_id)
    - Usage tracking (access_count, last_accessed)

    The dual-track pattern:
    - This table: Fast queries by tag, recency, access frequency
    - D-gent datum: Semantic search, associative connections
    """

    __tablename__ = "brain_crystals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSONBCompat, default=list)

    # Usage tracking for relevance scoring
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Link to D-gent for semantic content
    datum_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Source tracking
    source_type: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # "capture", "import", "generation"
    source_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Relationships
    crystal_tags: Mapped[list["CrystalTag"]] = relationship(
        "CrystalTag",
        back_populates="crystal",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_brain_crystals_tags", "tags", postgresql_using="gin"),
        Index("idx_brain_crystals_recent", "created_at"),
        Index("idx_brain_crystals_accessed", "last_accessed"),
    )

    def touch(self) -> None:
        """Record an access to this crystal."""
        self.access_count += 1
        self.last_accessed = datetime.now(UTC)


class CrystalTag(Base):
    """
    Normalized tag for efficient tag-based queries.

    Enables:
    - Get all crystals with tag X
    - Get all tags for crystal Y
    - Tag frequency analysis
    """

    __tablename__ = "brain_crystal_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crystal_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("brain_crystals.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Relationship back to crystal
    crystal: Mapped["Crystal"] = relationship("Crystal", back_populates="crystal_tags")

    __table_args__ = (Index("idx_crystal_tags_lookup", "tag", "crystal_id"),)


class BrainSettings(TimestampMixin, Base):
    """
    User settings for Brain behavior.

    Singleton per user/tenant. Stores preferences like:
    - Default capture tags
    - Retention policies
    - Display preferences
    """

    __tablename__ = "brain_settings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default="default")
    default_tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    retention_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_crystals: Mapped[int | None] = mapped_column(Integer, nullable=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)


# =============================================================================
# Memory-First Documentation: Teaching Crystals & Extinction
# =============================================================================
#
# "Teaching moments don't die; they become ancestors."
#
# These tables implement the Memory-First Documentation spec:
# - TeachingCrystal: Wisdom persisted beyond code deletion
# - ExtinctionEvent: Mass deletion events with salvaged wisdom
# - ExtinctionTeaching: Links extinction events to preserved teaching
#
# See: spec/protocols/memory-first-docs.md
# =============================================================================


class TeachingCrystal(TimestampMixin, Base):
    """
    A teaching moment crystallized in Brain.

    Persists beyond the death of source code.
    Links to successors when source is deleted.

    Laws (from spec):
    - Persistence Law: Teaching moments extracted from code MUST be crystallized
    - Extinction Law: Teaching from deleted code marked died_at, NOT deleted
    - Successor Chain Law: Successor mappings form a DAG

    AGENTESE: self.memory.crystallize_teaching, void.extinct.wisdom
    """

    __tablename__ = "brain_teaching_crystals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # The teaching
    insight: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # "info" | "warning" | "critical"
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)  # test_file.py::test_name

    # Provenance
    source_module: Mapped[str] = mapped_column(
        String(256), nullable=False, index=True
    )  # "services.town.dialogue_service"
    source_symbol: Mapped[str] = mapped_column(
        String(256), nullable=False
    )  # "DialogueService.process_turn"
    source_commit: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )  # Git SHA where learned

    # Temporal
    born_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    died_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Lineage (Successor Chain)
    successor_module: Mapped[str | None] = mapped_column(
        String(256), nullable=True
    )  # What replaced the source
    successor_symbol: Mapped[str | None] = mapped_column(
        String(256), nullable=True
    )  # Symbol in successor
    applies_to: Mapped[list[str]] = mapped_column(
        JSON, default=list
    )  # AGENTESE paths still relevant

    # Link to full crystal content (optional, for rich teaching)
    crystal_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("brain_crystals.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationship to full crystal
    crystal: Mapped["Crystal | None"] = relationship("Crystal", foreign_keys=[crystal_id])

    # Relationship to extinction events (many-to-many via join table)
    extinction_links: Mapped[list["ExtinctionTeaching"]] = relationship(
        "ExtinctionTeaching",
        back_populates="teaching_crystal",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # Find all alive teaching crystals
        Index("idx_teaching_crystals_alive", "died_at", postgresql_where="died_at IS NULL"),
        # Find teaching by module (for hydration)
        Index("idx_teaching_crystals_module", "source_module"),
        # Find teaching by severity (for prioritization)
        Index("idx_teaching_crystals_severity", "severity"),
    )

    @property
    def is_alive(self) -> bool:
        """Check if this teaching crystal's source code still exists."""
        return self.died_at is None

    @property
    def is_ancestor(self) -> bool:
        """Check if this teaching is ancestral wisdom (from deleted code)."""
        return self.died_at is not None


class ExtinctionEvent(TimestampMixin, Base):
    """
    A mass deletion event with salvaged wisdom.

    Records architectural decisions that removed code
    while preserving the teaching moments learned.

    The soil remembers what the garden forgets.

    AGENTESE: self.memory.prepare_extinction, void.extinct.list
    """

    __tablename__ = "brain_extinction_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # What happened
    reason: Mapped[str] = mapped_column(Text, nullable=False)  # "Crown Jewel Cleanup - AD-009"
    decision_doc: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # "spec/decisions/AD-009.md"
    commit: Mapped[str] = mapped_column(String(64), nullable=False)  # Git SHA of deletion

    # What was deleted
    deleted_paths: Mapped[list[str]] = mapped_column(JSON, default=list)  # ["services/town/", ...]

    # Successor mapping (DAG)
    successor_map: Mapped[dict] = mapped_column(JSON, default=dict)  # {"town": "brain", ...}

    # How many teaching crystals were preserved
    preserved_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship to preserved teaching crystals (many-to-many via join table)
    teaching_links: Mapped[list["ExtinctionTeaching"]] = relationship(
        "ExtinctionTeaching",
        back_populates="extinction_event",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # Find extinctions by date (for archaeology)
        Index("idx_extinction_events_date", "created_at"),
    )


class ExtinctionTeaching(Base):
    """
    Join table linking extinction events to preserved teaching crystals.

    When code is deleted, this tracks which teaching moments were
    salvaged during that extinction event.
    """

    __tablename__ = "brain_extinction_teaching"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    extinction_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("brain_extinction_events.id", ondelete="CASCADE"),
        nullable=False,
    )
    teaching_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("brain_teaching_crystals.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    extinction_event: Mapped["ExtinctionEvent"] = relationship(
        "ExtinctionEvent", back_populates="teaching_links"
    )
    teaching_crystal: Mapped["TeachingCrystal"] = relationship(
        "TeachingCrystal", back_populates="extinction_links"
    )

    __table_args__ = (
        Index("idx_extinction_teaching_lookup", "extinction_id", "teaching_id", unique=True),
    )
