"""
Town Persistence: TableAdapter + D-gent integration for Agent Town Crown Jewel.

Owns domain semantics for Town storage:
- WHEN to persist (citizen creation, conversation turns, relationship updates)
- WHY to persist (queryable metadata + dialogue history + semantic memory)
- HOW to compose (TableAdapter for entities, D-gent for dialogue/memory)

AGENTESE aspects exposed:
- manifest: Show town/citizen status
- witness: View dialogue history
- gossip: Inter-citizen dialogue
- step: Advance simulation

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agents.d import Datum, DgentProtocol, TableAdapter
from models.town import (
    Citizen,
    CitizenRelationship,
    Conversation,
    ConversationTurn,
)

if TYPE_CHECKING:
    pass


@dataclass
class CitizenView:
    """View of a citizen for external consumption."""

    id: str
    name: str
    archetype: str
    description: str | None
    traits: dict[str, Any]
    is_active: bool
    interaction_count: int
    last_interaction: str | None
    created_at: str


@dataclass
class ConversationView:
    """View of a conversation."""

    id: str
    citizen_id: str
    citizen_name: str
    topic: str | None
    summary: str | None
    turn_count: int
    is_active: bool
    created_at: str
    turns: list["TurnView"] = field(default_factory=list)


@dataclass
class TurnView:
    """View of a conversation turn."""

    id: str
    turn_number: int
    role: str  # "user" | "citizen" | "system"
    content: str
    sentiment: str | None
    emotion: str | None
    created_at: str


@dataclass
class RelationshipView:
    """View of a citizen relationship."""

    id: str
    citizen_a_id: str
    citizen_b_id: str
    relationship_type: str
    strength: float
    interaction_count: int
    notes: str | None


@dataclass
class TownStatus:
    """Town health status."""

    total_citizens: int
    active_citizens: int
    total_conversations: int
    active_conversations: int
    total_relationships: int
    storage_backend: str


class TownPersistence:
    """
    Persistence layer for Agent Town Crown Jewel.

    Composes:
    - TableAdapter[Citizen]: Citizen state, traits, activity tracking
    - TableAdapter[Conversation]: Conversation metadata
    - D-gent: Full dialogue history, semantic citizen memory

    Domain Semantics:
    - Citizens have polynomial state (modes, transitions)
    - Conversations are causal chains of turns
    - Relationships emerge from interaction patterns

    Example:
        persistence = TownPersistence(
            citizen_adapter=TableAdapter(Citizen, session_factory),
            conversation_adapter=TableAdapter(Conversation, session_factory),
            dgent=dgent_router,
        )

        citizen = await persistence.create_citizen("Socrates", "dialectic")
        conv = await persistence.start_conversation(citizen.id, "Philosophy")
    """

    def __init__(
        self,
        citizen_adapter: TableAdapter[Citizen],
        conversation_adapter: TableAdapter[Conversation],
        dgent: DgentProtocol,
    ) -> None:
        self.citizens = citizen_adapter
        self.conversations = conversation_adapter
        self.dgent = dgent

    # =========================================================================
    # Citizen Management
    # =========================================================================

    async def create_citizen(
        self,
        name: str,
        archetype: str,
        description: str | None = None,
        traits: dict[str, Any] | None = None,
    ) -> CitizenView:
        """
        Create a new citizen in the town.

        AGENTESE: world.town.citizen.define

        Args:
            name: Citizen name (must be unique)
            archetype: Citizen archetype (dialectic, empiric, artistic, etc.)
            description: Optional description
            traits: Personality traits

        Returns:
            CitizenView of the created citizen
        """
        citizen_id = f"citizen-{uuid.uuid4().hex[:12]}"
        traits = traits or {}

        async with self.citizens.session_factory() as session:
            citizen = Citizen(
                id=citizen_id,
                name=name,
                archetype=archetype,
                description=description,
                traits=traits,
                is_active=True,
                interaction_count=0,
                last_interaction=None,
                memory_datum_id=None,
            )
            session.add(citizen)
            await session.commit()

            return CitizenView(
                id=citizen_id,
                name=name,
                archetype=archetype,
                description=description,
                traits=traits,
                is_active=True,
                interaction_count=0,
                last_interaction=None,
                created_at=citizen.created_at.isoformat() if citizen.created_at else "",
            )

    async def get_citizen(self, citizen_id: str) -> CitizenView | None:
        """Get a citizen by ID."""
        async with self.citizens.session_factory() as session:
            citizen = await session.get(Citizen, citizen_id)
            if citizen is None:
                return None

            return self._citizen_to_view(citizen)

    async def get_citizen_by_name(self, name: str) -> CitizenView | None:
        """Get a citizen by name."""
        async with self.citizens.session_factory() as session:
            stmt = select(Citizen).where(Citizen.name == name)
            result = await session.execute(stmt)
            citizen = result.scalar_one_or_none()
            if citizen is None:
                return None

            return self._citizen_to_view(citizen)

    async def list_citizens(
        self,
        active_only: bool = False,
        archetype: str | None = None,
        limit: int = 50,
    ) -> list[CitizenView]:
        """List citizens with optional filters."""
        async with self.citizens.session_factory() as session:
            stmt = select(Citizen)

            if active_only:
                stmt = stmt.where(Citizen.is_active)
            if archetype:
                stmt = stmt.where(Citizen.archetype == archetype)

            stmt = stmt.order_by(Citizen.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            citizens = result.scalars().all()

            return [self._citizen_to_view(c) for c in citizens]

    async def update_citizen(
        self,
        citizen_id: str,
        description: str | None = None,
        traits: dict[str, Any] | None = None,
        is_active: bool | None = None,
    ) -> CitizenView | None:
        """Update citizen attributes."""
        async with self.citizens.session_factory() as session:
            citizen = await session.get(Citizen, citizen_id)
            if citizen is None:
                return None

            if description is not None:
                citizen.description = description
            if traits is not None:
                citizen.traits = traits
            if is_active is not None:
                citizen.is_active = is_active

            await session.commit()
            return self._citizen_to_view(citizen)

    # =========================================================================
    # Conversation Management
    # =========================================================================

    async def start_conversation(
        self,
        citizen_id: str,
        topic: str | None = None,
    ) -> ConversationView | None:
        """
        Start a new conversation with a citizen.

        AGENTESE: world.town.citizen.<name>.converse

        Args:
            citizen_id: ID of the citizen
            topic: Optional topic/title for the conversation

        Returns:
            ConversationView or None if citizen not found
        """
        async with self.citizens.session_factory() as session:
            citizen = await session.get(Citizen, citizen_id)
            if citizen is None:
                return None

            conv_id = f"conv-{uuid.uuid4().hex[:12]}"

            conversation = Conversation(
                id=conv_id,
                citizen_id=citizen_id,
                topic=topic,
                summary=None,
                turn_count=0,
                is_active=True,
                datum_chain_head=None,
            )
            session.add(conversation)

            # Update citizen interaction tracking
            citizen.interaction_count += 1
            citizen.last_interaction = datetime.now(UTC)

            await session.commit()

            return ConversationView(
                id=conv_id,
                citizen_id=citizen_id,
                citizen_name=citizen.name,
                topic=topic,
                summary=None,
                turn_count=0,
                is_active=True,
                created_at=conversation.created_at.isoformat() if conversation.created_at else "",
                turns=[],
            )

    async def add_turn(
        self,
        conversation_id: str,
        role: str,
        content: str,
        sentiment: str | None = None,
        emotion: str | None = None,
    ) -> TurnView | None:
        """
        Add a turn to a conversation.

        Stores turn in both table (metadata) and D-gent (full content).

        Args:
            conversation_id: ID of the conversation
            role: Role ("user", "citizen", "system")
            content: Turn content
            sentiment: Optional sentiment analysis
            emotion: Optional emotion classification

        Returns:
            TurnView or None if conversation not found
        """
        async with self.citizens.session_factory() as session:
            conversation = await session.get(Conversation, conversation_id)
            if conversation is None:
                return None

            turn_id = f"turn-{uuid.uuid4().hex[:12]}"
            turn_number = conversation.turn_count

            # Create turn in table
            turn = ConversationTurn(
                id=turn_id,
                conversation_id=conversation_id,
                turn_number=turn_number,
                role=role,
                content=content,
                sentiment=sentiment,
                emotion=emotion,
                causal_parent=conversation.datum_chain_head,
            )
            session.add(turn)

            # Store full content in D-gent for semantic search
            datum = Datum(
                id=f"town-{turn_id}",
                content=content.encode("utf-8"),
                created_at=time.time(),
                causal_parent=conversation.datum_chain_head,
                metadata={
                    "type": "conversation_turn",
                    "conversation_id": conversation_id,
                    "role": role,
                    "turn_number": str(turn_number),
                },
            )
            datum_id = await self.dgent.put(datum)

            # Update conversation
            conversation.turn_count += 1
            conversation.datum_chain_head = datum_id

            await session.commit()

            return TurnView(
                id=turn_id,
                turn_number=turn_number,
                role=role,
                content=content,
                sentiment=sentiment,
                emotion=emotion,
                created_at=turn.created_at.isoformat() if turn.created_at else "",
            )

    async def get_conversation(
        self,
        conversation_id: str,
        include_turns: bool = True,
    ) -> ConversationView | None:
        """Get a conversation with optional turns."""
        async with self.citizens.session_factory() as session:
            conversation = await session.get(Conversation, conversation_id)
            if conversation is None:
                return None

            # Get citizen name
            citizen = await session.get(Citizen, conversation.citizen_id)
            citizen_name = citizen.name if citizen else "Unknown"

            turns = []
            if include_turns:
                stmt = (
                    select(ConversationTurn)
                    .where(ConversationTurn.conversation_id == conversation_id)
                    .order_by(ConversationTurn.turn_number)
                )
                result = await session.execute(stmt)
                turn_rows = result.scalars().all()
                turns = [self._turn_to_view(t) for t in turn_rows]

            return ConversationView(
                id=conversation.id,
                citizen_id=conversation.citizen_id,
                citizen_name=citizen_name,
                topic=conversation.topic,
                summary=conversation.summary,
                turn_count=conversation.turn_count,
                is_active=conversation.is_active,
                created_at=conversation.created_at.isoformat() if conversation.created_at else "",
                turns=turns,
            )

    async def end_conversation(
        self,
        conversation_id: str,
        summary: str | None = None,
    ) -> bool:
        """End an active conversation."""
        async with self.citizens.session_factory() as session:
            conversation = await session.get(Conversation, conversation_id)
            if conversation is None:
                return False

            conversation.is_active = False
            if summary:
                conversation.summary = summary

            await session.commit()
            return True

    async def get_dialogue_history(
        self,
        citizen_id: str,
        limit: int = 50,
    ) -> list[ConversationView]:
        """
        Get dialogue history for a citizen.

        AGENTESE: world.town.citizen.<name>.witness

        Returns recent conversations with turn summaries.
        """
        async with self.citizens.session_factory() as session:
            citizen = await session.get(Citizen, citizen_id)
            if citizen is None:
                return []

            stmt = (
                select(Conversation)
                .where(Conversation.citizen_id == citizen_id)
                .order_by(Conversation.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            conversations = result.scalars().all()

            views = []
            for conv in conversations:
                views.append(
                    ConversationView(
                        id=conv.id,
                        citizen_id=conv.citizen_id,
                        citizen_name=citizen.name,
                        topic=conv.topic,
                        summary=conv.summary,
                        turn_count=conv.turn_count,
                        is_active=conv.is_active,
                        created_at=conv.created_at.isoformat() if conv.created_at else "",
                        turns=[],  # Don't load all turns for history
                    )
                )

            return views

    # =========================================================================
    # Relationship Management
    # =========================================================================

    async def create_relationship(
        self,
        citizen_a_id: str,
        citizen_b_id: str,
        relationship_type: str,
        strength: float = 0.5,
        notes: str | None = None,
    ) -> RelationshipView | None:
        """Create a relationship between two citizens."""
        async with self.citizens.session_factory() as session:
            # Verify both citizens exist
            citizen_a = await session.get(Citizen, citizen_a_id)
            citizen_b = await session.get(Citizen, citizen_b_id)
            if citizen_a is None or citizen_b is None:
                return None

            rel_id = f"rel-{uuid.uuid4().hex[:12]}"

            relationship = CitizenRelationship(
                id=rel_id,
                citizen_a_id=citizen_a_id,
                citizen_b_id=citizen_b_id,
                relationship_type=relationship_type,
                strength=strength,
                interaction_count=0,
                notes=notes,
            )
            session.add(relationship)
            await session.commit()

            return RelationshipView(
                id=rel_id,
                citizen_a_id=citizen_a_id,
                citizen_b_id=citizen_b_id,
                relationship_type=relationship_type,
                strength=strength,
                interaction_count=0,
                notes=notes,
            )

    async def get_relationships(
        self,
        citizen_id: str,
    ) -> list[RelationshipView]:
        """Get all relationships for a citizen."""
        async with self.citizens.session_factory() as session:
            stmt = select(CitizenRelationship).where(
                (CitizenRelationship.citizen_a_id == citizen_id)
                | (CitizenRelationship.citizen_b_id == citizen_id)
            )
            result = await session.execute(stmt)
            relationships = result.scalars().all()

            return [
                RelationshipView(
                    id=r.id,
                    citizen_a_id=r.citizen_a_id,
                    citizen_b_id=r.citizen_b_id,
                    relationship_type=r.relationship_type,
                    strength=r.strength,
                    interaction_count=r.interaction_count,
                    notes=r.notes,
                )
                for r in relationships
            ]

    # =========================================================================
    # Town Status
    # =========================================================================

    async def manifest(self) -> TownStatus:
        """
        Get town health status.

        AGENTESE: world.town.manifest
        """
        async with self.citizens.session_factory() as session:
            # Count citizens
            total_citizens_result = await session.execute(select(func.count()).select_from(Citizen))
            total_citizens = total_citizens_result.scalar() or 0

            active_citizens_result = await session.execute(
                select(func.count()).select_from(Citizen).where(Citizen.is_active)
            )
            active_citizens = active_citizens_result.scalar() or 0

            # Count conversations
            total_conv_result = await session.execute(
                select(func.count()).select_from(Conversation)
            )
            total_conversations = total_conv_result.scalar() or 0

            active_conv_result = await session.execute(
                select(func.count()).select_from(Conversation).where(Conversation.is_active)
            )
            active_conversations = active_conv_result.scalar() or 0

            # Count relationships
            rel_result = await session.execute(
                select(func.count()).select_from(CitizenRelationship)
            )
            total_relationships = rel_result.scalar() or 0

        return TownStatus(
            total_citizens=total_citizens,
            active_citizens=active_citizens,
            total_conversations=total_conversations,
            active_conversations=active_conversations,
            total_relationships=total_relationships,
            storage_backend="postgres"
            if "postgres" in str(self.citizens.session_factory).lower()
            else "sqlite",
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _citizen_to_view(self, citizen: Citizen) -> CitizenView:
        """Convert Citizen model to CitizenView."""
        return CitizenView(
            id=citizen.id,
            name=citizen.name,
            archetype=citizen.archetype,
            description=citizen.description,
            traits=citizen.traits or {},
            is_active=citizen.is_active,
            interaction_count=citizen.interaction_count,
            last_interaction=citizen.last_interaction.isoformat()
            if citizen.last_interaction
            else None,
            created_at=citizen.created_at.isoformat() if citizen.created_at else "",
        )

    def _turn_to_view(self, turn: ConversationTurn) -> TurnView:
        """Convert ConversationTurn model to TurnView."""
        return TurnView(
            id=turn.id,
            turn_number=turn.turn_number,
            role=turn.role,
            content=turn.content,
            sentiment=turn.sentiment,
            emotion=turn.emotion,
            created_at=turn.created_at.isoformat() if turn.created_at else "",
        )


__all__ = [
    "TownPersistence",
    "CitizenView",
    "ConversationView",
    "TurnView",
    "RelationshipView",
    "TownStatus",
]
