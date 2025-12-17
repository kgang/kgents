"""
Brain Crown Jewel: Spatial Cathedral of Memory.

Tables for the Brain's crystallized knowledge with queryable metadata.
Hybrid storage: Alembic tables for queryable metadata + D-gent for semantic content.

AGENTESE: self.data.table.crystal.*
"""

from __future__ import annotations

from datetime import datetime
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CausalMixin, TimestampMixin

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
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)

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
        self.last_accessed = datetime.utcnow()


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
