"""
Park Crown Jewel: Westworld Where Hosts Can Say No.

Tables for the Park's immersive host interactions.
Punchdrunk-inspired where agents have agency and memory.

AGENTESE: self.data.table.host.*, self.data.table.episode.*
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CausalMixin, TimestampMixin

if TYPE_CHECKING:
    from typing import Optional


class Host(TimestampMixin, Base):
    """
    A host (agent) in the Park.

    Hosts are autonomous agents that:
    - Have persistent memory across episodes
    - Can consent to or decline interactions
    - Maintain character consistency
    - Remember past visitors
    """

    __tablename__ = "park_hosts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    character: Mapped[str] = mapped_column(String(64), nullable=False)  # Character archetype
    backstory: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Personality
    traits: Mapped[dict] = mapped_column(JSON, default=dict)
    values: Mapped[list[str]] = mapped_column(JSON, default=list)
    boundaries: Mapped[list[str]] = mapped_column(JSON, default=list)  # Things they won't do

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    mood: Mapped[str | None] = mapped_column(String(32), nullable=True)
    energy_level: Mapped[float] = mapped_column(Float, default=1.0)

    # Location in park
    current_location: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Stats
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)
    consent_refusal_count: Mapped[int] = mapped_column(Integer, default=0)

    # D-gent link for deep memory
    memory_datum_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationships
    memories: Mapped[list["HostMemory"]] = relationship(
        "HostMemory",
        back_populates="host",
        cascade="all, delete-orphan",
    )
    interactions: Mapped[list["Interaction"]] = relationship(
        "Interaction",
        back_populates="host",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_park_hosts_character", "character"),
        Index("idx_park_hosts_active", "is_active"),
        Index("idx_park_hosts_location", "current_location"),
    )


class HostMemory(TimestampMixin, CausalMixin, Base):
    """
    A memory held by a host.

    Memories:
    - Persist across episodes
    - Influence host behavior
    - Can fade over time (salience decay)
    """

    __tablename__ = "park_host_memories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    host_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("park_hosts.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Memory content
    memory_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # "event", "person", "place", "emotion", "insight"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Importance and persistence
    salience: Mapped[float] = mapped_column(Float, default=0.5)  # How important/memorable
    emotional_valence: Mapped[float] = mapped_column(Float, default=0.0)  # -1 to 1
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Source
    episode_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("park_episodes.id", ondelete="SET NULL"),
        nullable=True,
    )
    visitor_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # D-gent link for semantic retrieval
    datum_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Relationship
    host: Mapped["Host"] = relationship("Host", back_populates="memories")

    __table_args__ = (
        Index("idx_park_memories_host", "host_id"),
        Index("idx_park_memories_type", "memory_type"),
        Index("idx_park_memories_salience", "salience"),
    )


class Episode(TimestampMixin, Base):
    """
    An episode (session) in the Park.

    Episodes are bounded periods of activity:
    - Start when a visitor enters
    - End when they leave
    - Contain interactions
    """

    __tablename__ = "park_episodes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    visitor_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    visitor_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Episode metadata
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # State
    status: Mapped[str] = mapped_column(
        String(32), default="active"
    )  # "active", "completed", "abandoned"
    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Stats
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)
    hosts_met: Mapped[list[str]] = mapped_column(JSON, default=list)
    locations_visited: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Interactions in this episode
    interactions: Mapped[list["Interaction"]] = relationship(
        "Interaction",
        back_populates="episode",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_park_episodes_visitor", "visitor_id"),
        Index("idx_park_episodes_status", "status"),
        Index("idx_park_episodes_started", "started_at"),
    )


class Interaction(TimestampMixin, CausalMixin, Base):
    """
    An interaction between a visitor and a host.

    Interactions:
    - Are the atomic unit of Park activity
    - Can be accepted or declined by hosts
    - Create memories for hosts
    """

    __tablename__ = "park_interactions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    episode_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("park_episodes.id", ondelete="CASCADE"),
        nullable=False,
    )
    host_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("park_hosts.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Interaction type
    interaction_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # "dialogue", "action", "observation", "gift"

    # Content
    visitor_input: Mapped[str] = mapped_column(Text, nullable=False)
    host_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Consent
    consent_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_given: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    consent_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Location
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Emotion
    host_emotion: Mapped[str | None] = mapped_column(String(32), nullable=True)
    visitor_sentiment: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Relationships
    episode: Mapped["Episode"] = relationship("Episode", back_populates="interactions")
    host: Mapped["Host"] = relationship("Host", back_populates="interactions")

    __table_args__ = (
        Index("idx_park_interactions_episode", "episode_id"),
        Index("idx_park_interactions_host", "host_id"),
        Index("idx_park_interactions_type", "interaction_type"),
    )


class ParkLocation(TimestampMixin, Base):
    """
    A location in the Park.

    Locations:
    - Are places hosts can be
    - Have atmosphere and purpose
    - Connect to form a map
    """

    __tablename__ = "park_locations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    atmosphere: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Spatial
    x: Mapped[float | None] = mapped_column(Float, nullable=True)
    y: Mapped[float | None] = mapped_column(Float, nullable=True)
    connected_locations: Mapped[list[str]] = mapped_column(JSON, default=list)

    # State
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (Index("idx_park_locations_name", "name"),)
