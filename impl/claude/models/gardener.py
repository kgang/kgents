"""
Gardener Crown Jewel: Cultivation Practice for Ideas.

Tables for the Gardener's idea lifecycle management.
Ideas flow: SEED -> SAPLING -> TREE -> FLOWER -> COMPOST

AGENTESE: self.data.table.idea.*, self.data.table.garden.*
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
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


class IdeaLifecycle(enum.Enum):
    """Lifecycle stages for garden ideas."""

    SEED = "SEED"  # Initial capture, unrefined
    SAPLING = "SAPLING"  # Growing, needs nurturing
    TREE = "TREE"  # Mature, stable
    FLOWER = "FLOWER"  # Producing insights/outputs
    COMPOST = "COMPOST"  # Decomposed, feeds other ideas


class GardenSession(TimestampMixin, Base):
    """
    A gardening session.

    Sessions group related gardening activity:
    - Ideas captured during the session
    - Tending actions performed
    - Lifecycle transitions
    """

    __tablename__ = "garden_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Ideas captured in this session
    ideas: Mapped[list["GardenIdea"]] = relationship(
        "GardenIdea",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    __table_args__ = (Index("idx_garden_sessions_recent", "created_at"),)


class GardenIdea(TimestampMixin, CausalMixin, Base):
    """
    An idea in the garden.

    Ideas have:
    - Content (the actual idea text)
    - Lifecycle stage (SEED -> FLOWER -> COMPOST)
    - Confidence score (0.0 to 1.0)
    - Connections to other ideas
    """

    __tablename__ = "garden_ideas"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    lifecycle: Mapped[str] = mapped_column(
        String(16),
        default=IdeaLifecycle.SEED.value,
        index=True,
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.3)

    # Session tracking
    session_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("garden_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Nurturing tracking
    last_nurtured: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    nurture_count: Mapped[int] = mapped_column(Integer, default=0)

    # Plot assignment (thematic grouping)
    plot_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("garden_plots.id", ondelete="SET NULL"),
        nullable=True,
    )

    # D-gent link for associative connections
    datum_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Tags for categorization
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Relationships
    session: Mapped["GardenSession | None"] = relationship(
        "GardenSession", back_populates="ideas"
    )
    plot: Mapped["GardenPlot | None"] = relationship(
        "GardenPlot", back_populates="ideas"
    )
    outgoing_connections: Mapped[list["IdeaConnection"]] = relationship(
        "IdeaConnection",
        foreign_keys="IdeaConnection.source_id",
        back_populates="source",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_garden_ideas_lifecycle", "lifecycle"),
        Index("idx_garden_ideas_confidence", "confidence"),
        Index("idx_garden_ideas_plot", "plot_id"),
    )

    def nurture(self) -> None:
        """Record a nurturing action."""
        self.nurture_count += 1
        self.last_nurtured = datetime.utcnow()

    def promote(self) -> bool:
        """
        Promote to next lifecycle stage.

        Returns True if promoted, False if already at max.
        """
        stages = list(IdeaLifecycle)
        current_idx = next(
            (i for i, s in enumerate(stages) if s.value == self.lifecycle),
            0,
        )
        if current_idx < len(stages) - 1:
            self.lifecycle = stages[current_idx + 1].value
            return True
        return False


class GardenPlot(TimestampMixin, Base):
    """
    A thematic plot in the garden.

    Plots group related ideas by theme:
    - "project-ideas" - Ideas for new projects
    - "learnings" - Things learned
    - "questions" - Open questions to explore
    """

    __tablename__ = "garden_plots"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(
        String(16), nullable=True
    )  # Hex color for UI

    # Ideas in this plot
    ideas: Mapped[list["GardenIdea"]] = relationship(
        "GardenIdea", back_populates="plot"
    )

    __table_args__ = (Index("idx_garden_plots_name", "name"),)


class IdeaConnection(TimestampMixin, Base):
    """
    Connection between two ideas.

    Connections capture:
    - Relationship type (supports, contradicts, extends, etc.)
    - Strength of connection
    - Optional notes
    """

    __tablename__ = "garden_idea_connections"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("garden_ideas.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("garden_ideas.id", ondelete="CASCADE"),
        nullable=False,
    )
    connection_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # "supports", "contradicts", "extends", "inspired_by"
    strength: Mapped[float] = mapped_column(Float, default=0.5)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    source: Mapped["GardenIdea"] = relationship(
        "GardenIdea",
        foreign_keys=[source_id],
        back_populates="outgoing_connections",
    )

    __table_args__ = (
        Index("idx_garden_connections_source", "source_id"),
        Index("idx_garden_connections_target", "target_id"),
    )
