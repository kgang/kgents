"""
Town Crown Jewel: Westworld Where Hosts Can Say No.

Tables for Agent Town citizens, conversations, and persistent memory.
Enables citizens to remember across sessions and maintain relationships.

AGENTESE: self.data.table.citizen.*, self.data.table.conversation.*
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


class Citizen(TimestampMixin, Base):
    """
    A citizen (agent) in the Town.

    Citizens have:
    - Personality traits and archetype
    - Persistent memory across sessions
    - Relationships with other citizens
    - Consent flags (can say no)
    """

    __tablename__ = "town_citizens"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(
        String(128), nullable=False, index=True, unique=True
    )
    archetype: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # "dialectic", "empiric", "artistic", etc.
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Personality traits (JSON for flexibility)
    traits: Mapped[dict] = mapped_column(JSON, default=dict)

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_interaction: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)

    # D-gent link for deeper memory
    memory_datum_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="citizen",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_town_citizens_archetype", "archetype"),
        Index("idx_town_citizens_active", "is_active"),
    )


class Conversation(TimestampMixin, CausalMixin, Base):
    """
    A conversation session with a citizen.

    Conversations:
    - Track topic and turn count
    - Link to full turn history
    - Support causality for D-gent access
    """

    __tablename__ = "town_conversations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    citizen_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("town_citizens.id", ondelete="CASCADE"),
        nullable=False,
    )
    topic: Mapped[str | None] = mapped_column(String(256), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    turn_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Head of D-gent causal chain for turn content
    datum_chain_head: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationships
    citizen: Mapped["Citizen"] = relationship("Citizen", back_populates="conversations")
    turns: Mapped[list["ConversationTurn"]] = relationship(
        "ConversationTurn",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationTurn.turn_number",
    )

    __table_args__ = (
        Index("idx_town_conversations_citizen", "citizen_id"),
        Index("idx_town_conversations_active", "is_active"),
        Index("idx_town_conversations_recent", "created_at"),
    )


class ConversationTurn(TimestampMixin, CausalMixin, Base):
    """
    A single turn in a conversation.

    Each turn has:
    - Role (user or citizen)
    - Content (the message)
    - Causal link for D-gent traversal
    """

    __tablename__ = "town_conversation_turns"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("town_conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # "user" | "citizen" | "system"
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Sentiment/emotion analysis (optional)
    sentiment: Mapped[str | None] = mapped_column(String(16), nullable=True)
    emotion: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Relationship
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="turns"
    )

    __table_args__ = (
        Index("idx_town_turns_conversation", "conversation_id", "turn_number"),
    )


class CitizenRelationship(TimestampMixin, Base):
    """
    Relationship between two citizens.

    Tracks:
    - Relationship type (ally, rival, mentor, etc.)
    - Strength/intensity
    - History of interactions
    """

    __tablename__ = "town_citizen_relationships"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    citizen_a_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("town_citizens.id", ondelete="CASCADE"),
        nullable=False,
    )
    citizen_b_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("town_citizens.id", ondelete="CASCADE"),
        nullable=False,
    )
    relationship_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # "ally", "rival", "mentor", "mentee"
    strength: Mapped[float] = mapped_column(Float, default=0.5)  # 0.0 to 1.0
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_relationships_citizens", "citizen_a_id", "citizen_b_id"),
    )
