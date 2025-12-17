"""
Atelier Crown Jewel: Fishbowl Where Spectators Collaborate.

Tables for the Atelier's creative workshops, exhibitions, and galleries.
Punchdrunk-inspired immersive creative collaboration.

AGENTESE: self.data.table.workshop.*, self.data.table.exhibition.*, self.data.table.gallery.*
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Float, Text, DateTime, JSON, ForeignKey, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, CausalMixin

if TYPE_CHECKING:
    from typing import Optional


class Workshop(TimestampMixin, Base):
    """
    A creative workshop in the Atelier.

    Workshops are collaborative spaces where:
    - Artisans (agents) create together
    - Spectators can observe and interact
    - Creative artifacts are produced
    """

    __tablename__ = "atelier_workshops"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    theme: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Configuration
    config: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    artisans: Mapped[list["Artisan"]] = relationship(
        "Artisan",
        back_populates="workshop",
        cascade="all, delete-orphan",
    )
    exhibitions: Mapped[list["Exhibition"]] = relationship(
        "Exhibition",
        back_populates="workshop",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_atelier_workshops_active", "is_active"),
        Index("idx_atelier_workshops_theme", "theme"),
    )


class Artisan(TimestampMixin, Base):
    """
    An artisan (creative agent) in a workshop.

    Artisans:
    - Have creative specialties
    - Collaborate with other artisans
    - Produce artifacts
    """

    __tablename__ = "atelier_artisans"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workshop_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("atelier_workshops.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    specialty: Mapped[str] = mapped_column(String(64), nullable=False)  # "poet", "painter", "composer", "sculptor"
    style: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    contribution_count: Mapped[int] = mapped_column(Integer, default=0)

    # Agent link
    agent_id: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Link to Town citizen or external agent

    # Relationships
    workshop: Mapped["Workshop"] = relationship("Workshop", back_populates="artisans")
    contributions: Mapped[list["ArtifactContribution"]] = relationship(
        "ArtifactContribution",
        back_populates="artisan",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_atelier_artisans_workshop", "workshop_id"),
        Index("idx_atelier_artisans_specialty", "specialty"),
    )


class Exhibition(TimestampMixin, Base):
    """
    An exhibition of creative work.

    Exhibitions:
    - Showcase artifacts from workshops
    - Are curated with a theme
    - Can be viewed by spectators
    """

    __tablename__ = "atelier_exhibitions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workshop_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("atelier_workshops.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    curator_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # State
    is_open: Mapped[bool] = mapped_column(Boolean, default=False)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    workshop: Mapped["Workshop"] = relationship("Workshop", back_populates="exhibitions")
    gallery_items: Mapped[list["GalleryItem"]] = relationship(
        "GalleryItem",
        back_populates="exhibition",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_atelier_exhibitions_workshop", "workshop_id"),
        Index("idx_atelier_exhibitions_open", "is_open"),
    )


class GalleryItem(TimestampMixin, Base):
    """
    An item in a gallery exhibition.

    Gallery items are artifacts that have been:
    - Selected for exhibition
    - Arranged in a specific order
    - Annotated with curatorial context
    """

    __tablename__ = "atelier_gallery_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    exhibition_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("atelier_exhibitions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # The artifact being displayed
    artifact_type: Mapped[str] = mapped_column(String(32), nullable=False)  # "text", "image", "audio", "code"
    artifact_content: Mapped[str] = mapped_column(Text, nullable=False)
    artifact_metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Display settings
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Attribution
    artisan_ids: Mapped[list[str]] = mapped_column(JSON, default=list)  # Multiple artisans can contribute

    # Relationships
    exhibition: Mapped["Exhibition"] = relationship("Exhibition", back_populates="gallery_items")

    __table_args__ = (
        Index("idx_atelier_gallery_exhibition", "exhibition_id"),
        Index("idx_atelier_gallery_order", "exhibition_id", "display_order"),
    )


class ArtifactContribution(TimestampMixin, CausalMixin, Base):
    """
    A contribution by an artisan during a workshop.

    Tracks:
    - What was created
    - When and by whom
    - Context and inspiration
    """

    __tablename__ = "atelier_artifact_contributions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    artisan_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("atelier_artisans.id", ondelete="CASCADE"),
        nullable=False,
    )

    # The contribution
    contribution_type: Mapped[str] = mapped_column(String(32), nullable=False)  # "draft", "revision", "final"
    content_type: Mapped[str] = mapped_column(String(32), nullable=False)  # "text", "image", "audio", "code"
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Context
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    inspiration: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # D-gent link
    datum_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationships
    artisan: Mapped["Artisan"] = relationship("Artisan", back_populates="contributions")

    __table_args__ = (
        Index("idx_atelier_contributions_artisan", "artisan_id"),
        Index("idx_atelier_contributions_type", "contribution_type"),
    )
