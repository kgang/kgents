"""
Town AGENTESE Node: @node("world.town")

Wraps TownPersistence as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- world.town.manifest       - Town health status
- world.town.citizen.list   - List all citizens
- world.town.citizen.get    - Get citizen by ID or name
- world.town.citizen.create - Create new citizen
- world.town.citizen.update - Update citizen attributes
- world.town.converse       - Start conversation with citizen
- world.town.turn           - Add turn to conversation
- world.town.history        - Get dialogue history
- world.town.relationships  - Get citizen relationships
- world.town.gossip         - Inter-citizen dialogue stream

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    CitizenCreateRequest,
    CitizenCreateResponse,
    CitizenGetResponse,
    CitizenListResponse,
    CitizenUpdateRequest,
    CitizenUpdateResponse,
    ConverseRequest,
    ConverseResponse,
    HistoryRequest,
    HistoryResponse,
    RelationshipsRequest,
    RelationshipsResponse,
    TownManifestResponse,
    TurnRequest,
    TurnResponse,
)
from .persistence import (
    CitizenView,
    ConversationView,
    RelationshipView,
    TownPersistence,
    TownStatus,
    TurnView,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === TownNode Rendering ===


@dataclass(frozen=True)
class TownManifestRendering:
    """Rendering for town status manifest."""

    status: TownStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "town_manifest",
            "total_citizens": self.status.total_citizens,
            "active_citizens": self.status.active_citizens,
            "total_conversations": self.status.total_conversations,
            "active_conversations": self.status.active_conversations,
            "total_relationships": self.status.total_relationships,
            "storage_backend": self.status.storage_backend,
        }

    def to_text(self) -> str:
        lines = [
            "Town Status",
            "===========",
            f"Citizens: {self.status.active_citizens}/{self.status.total_citizens} active",
            f"Conversations: {self.status.active_conversations}/{self.status.total_conversations} active",
            f"Relationships: {self.status.total_relationships}",
            f"Storage: {self.status.storage_backend}",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class CitizenRendering:
    """Rendering for citizen details."""

    citizen: CitizenView

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "citizen",
            "id": self.citizen.id,
            "name": self.citizen.name,
            "archetype": self.citizen.archetype,
            "description": self.citizen.description,
            "traits": self.citizen.traits,
            "is_active": self.citizen.is_active,
            "interaction_count": self.citizen.interaction_count,
            "last_interaction": self.citizen.last_interaction,
            "created_at": self.citizen.created_at,
        }

    def to_text(self) -> str:
        lines = [
            f"Citizen: {self.citizen.name}",
            f"Archetype: {self.citizen.archetype}",
            f"Status: {'active' if self.citizen.is_active else 'inactive'}",
            f"Interactions: {self.citizen.interaction_count}",
        ]
        if self.citizen.description:
            lines.append(f"Description: {self.citizen.description}")
        if self.citizen.traits:
            traits_str = ", ".join(f"{k}={v}" for k, v in self.citizen.traits.items())
            lines.append(f"Traits: {traits_str}")
        return "\n".join(lines)


@dataclass(frozen=True)
class CitizenListRendering:
    """Rendering for citizen list."""

    citizens: list[CitizenView]
    total: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "citizen_list",
            "total": self.total,
            "citizens": [
                {
                    "id": c.id,
                    "name": c.name,
                    "archetype": c.archetype,
                    "is_active": c.is_active,
                    "interaction_count": c.interaction_count,
                }
                for c in self.citizens
            ],
        }

    def to_text(self) -> str:
        if not self.citizens:
            return "No citizens in town"
        lines = [f"Citizens ({self.total}):", ""]
        for c in self.citizens[:20]:  # Limit display
            status = "●" if c.is_active else "○"
            lines.append(
                f"  {status} {c.name} ({c.archetype}) - {c.interaction_count} interactions"
            )
        if self.total > 20:
            lines.append(f"  ... and {self.total - 20} more")
        return "\n".join(lines)


@dataclass(frozen=True)
class ConversationRendering:
    """Rendering for conversation details."""

    conversation: ConversationView

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "conversation",
            "id": self.conversation.id,
            "citizen_id": self.conversation.citizen_id,
            "citizen_name": self.conversation.citizen_name,
            "topic": self.conversation.topic,
            "summary": self.conversation.summary,
            "turn_count": self.conversation.turn_count,
            "is_active": self.conversation.is_active,
            "created_at": self.conversation.created_at,
            "turns": [
                {
                    "id": t.id,
                    "turn_number": t.turn_number,
                    "role": t.role,
                    "content": t.content,
                    "sentiment": t.sentiment,
                    "emotion": t.emotion,
                    "created_at": t.created_at,
                }
                for t in self.conversation.turns
            ],
        }

    def to_text(self) -> str:
        lines = [
            f"Conversation with {self.conversation.citizen_name}",
            f"Topic: {self.conversation.topic or 'General'}",
            f"Status: {'active' if self.conversation.is_active else 'ended'}",
            f"Turns: {self.conversation.turn_count}",
            "",
        ]
        for t in self.conversation.turns[-10:]:  # Last 10 turns
            role_marker = "You" if t.role == "user" else self.conversation.citizen_name
            lines.append(f"[{role_marker}]: {t.content[:200]}")
        return "\n".join(lines)


@dataclass(frozen=True)
class RelationshipListRendering:
    """Rendering for relationship list."""

    relationships: list[RelationshipView]
    citizen_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "relationship_list",
            "citizen_id": self.citizen_id,
            "count": len(self.relationships),
            "relationships": [
                {
                    "id": r.id,
                    "citizen_a_id": r.citizen_a_id,
                    "citizen_b_id": r.citizen_b_id,
                    "type": r.relationship_type,
                    "strength": r.strength,
                    "interaction_count": r.interaction_count,
                    "notes": r.notes,
                }
                for r in self.relationships
            ],
        }

    def to_text(self) -> str:
        if not self.relationships:
            return f"No relationships for citizen {self.citizen_id}"
        lines = [f"Relationships ({len(self.relationships)}):", ""]
        for r in self.relationships:
            other = (
                r.citizen_b_id if r.citizen_a_id == self.citizen_id else r.citizen_a_id
            )
            strength_bar = "█" * int(r.strength * 10)
            lines.append(
                f"  {r.relationship_type}: {other} [{strength_bar}] ({r.interaction_count} interactions)"
            )
        return "\n".join(lines)


# === TownNode ===


@node(
    "world.town",
    description="Agent Town - Westworld simulation with polynomial citizens",
    dependencies=("town_persistence",),
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(TownManifestResponse),
        "citizen.list": Response(CitizenListResponse),
        "citizen.get": Response(CitizenGetResponse),
        "relationships": Contract(RelationshipsRequest, RelationshipsResponse),
        "history": Contract(HistoryRequest, HistoryResponse),
        # Mutation aspects (Contract with request + response)
        "citizen.create": Contract(CitizenCreateRequest, CitizenCreateResponse),
        "citizen.update": Contract(CitizenUpdateRequest, CitizenUpdateResponse),
        "converse": Contract(ConverseRequest, ConverseResponse),
        "turn": Contract(TurnRequest, TurnResponse),
    },
)
class TownNode(BaseLogosNode):
    """
    AGENTESE node for Agent Town Crown Jewel.

    Exposes TownPersistence through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/world/town/citizen/create
        {"name": "Socrates", "archetype": "dialectic"}

        # Via Logos directly
        await logos.invoke("world.town.citizen.create", observer, name="Socrates")

        # Via CLI
        kgents town citizen create Socrates --archetype dialectic
    """

    def __init__(self, town_persistence: TownPersistence) -> None:
        """
        Initialize TownNode.

        TownPersistence is REQUIRED. When Logos tries to instantiate
        without dependencies, it will fail and fall back to the existing
        WorldTownContext resolver. Use ServiceContainer for full DI.

        Args:
            town_persistence: The persistence layer (injected by container)

        Raises:
            TypeError: If town_persistence is not provided (intentional for fallback)
        """
        self._persistence = town_persistence

    @property
    def handle(self) -> str:
        return "world.town"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Core operations (list, get, history) available to all archetypes.
        Mutation operations (create, update, delete) restricted to privileged archetypes.
        """
        # Core operations available to all archetypes
        base = ("citizen.list", "citizen.get", "history", "relationships")

        if archetype in ("developer", "admin", "system"):
            # Full access including mutations and gossip
            return base + (
                "citizen.create",
                "citizen.update",
                "converse",
                "turn",
                "gossip",
                "step",
            )
        elif archetype in ("researcher", "analyst"):
            # Read access with conversation capabilities
            return base + ("converse", "turn")
        else:
            # Standard read-only access
            return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest town status to observer.

        AGENTESE: world.town.manifest
        """
        if self._persistence is None:
            return BasicRendering(
                summary="Town not initialized",
                content="No persistence layer configured",
                metadata={"error": "no_persistence"},
            )

        status = await self._persistence.manifest()
        return TownManifestRendering(status=status)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to persistence methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._persistence is None:
            return {"error": "Town persistence not configured"}

        # === Citizen Operations ===

        if aspect == "citizen.list":
            active_only = kwargs.get("active_only", False)
            archetype_filter = kwargs.get("archetype")
            limit = kwargs.get("limit", 50)

            citizens = await self._persistence.list_citizens(
                active_only=active_only,
                archetype=archetype_filter,
                limit=limit,
            )
            return CitizenListRendering(
                citizens=citizens, total=len(citizens)
            ).to_dict()

        elif aspect == "citizen.get":
            citizen_id = kwargs.get("citizen_id") or kwargs.get("id")
            name = kwargs.get("name")

            if citizen_id:
                citizen = await self._persistence.get_citizen(citizen_id)
            elif name:
                citizen = await self._persistence.get_citizen_by_name(name)
            else:
                return {"error": "citizen_id or name required"}

            if citizen is None:
                return {"error": f"Citizen not found: {citizen_id or name}"}
            return CitizenRendering(citizen=citizen).to_dict()

        elif aspect == "citizen.create":
            name = kwargs.get("name")
            archetype = kwargs.get("archetype", "default")
            description = kwargs.get("description")
            traits = kwargs.get("traits")

            if not name:
                return {"error": "name required"}

            citizen = await self._persistence.create_citizen(
                name=name,
                archetype=archetype,
                description=description,
                traits=traits,
            )
            return CitizenRendering(citizen=citizen).to_dict()

        elif aspect == "citizen.update":
            citizen_id = kwargs.get("citizen_id") or kwargs.get("id")
            if not citizen_id:
                return {"error": "citizen_id required"}

            citizen = await self._persistence.update_citizen(
                citizen_id=citizen_id,
                description=kwargs.get("description"),
                traits=kwargs.get("traits"),
                is_active=kwargs.get("is_active"),
            )
            if citizen is None:
                return {"error": f"Citizen not found: {citizen_id}"}
            return CitizenRendering(citizen=citizen).to_dict()

        # === Conversation Operations ===

        elif aspect == "converse":
            citizen_id = kwargs.get("citizen_id") or kwargs.get("id")
            name = kwargs.get("name")
            topic = kwargs.get("topic")

            # Resolve citizen by ID or name
            if not citizen_id and name:
                citizen = await self._persistence.get_citizen_by_name(name)
                if citizen:
                    citizen_id = citizen.id

            if not citizen_id:
                return {"error": "citizen_id or name required"}

            conversation = await self._persistence.start_conversation(
                citizen_id=citizen_id,
                topic=topic,
            )
            if conversation is None:
                return {"error": f"Citizen not found: {citizen_id}"}
            return ConversationRendering(conversation=conversation).to_dict()

        elif aspect == "turn":
            conversation_id = kwargs.get("conversation_id") or kwargs.get("id")
            role = kwargs.get("role", "user")
            content = kwargs.get("content", "")
            sentiment = kwargs.get("sentiment")
            emotion = kwargs.get("emotion")

            if not conversation_id:
                return {"error": "conversation_id required"}
            if not content:
                return {"error": "content required"}

            turn = await self._persistence.add_turn(
                conversation_id=conversation_id,
                role=role,
                content=content,
                sentiment=sentiment,
                emotion=emotion,
            )
            if turn is None:
                return {"error": f"Conversation not found: {conversation_id}"}
            return {
                "turn": {
                    "id": turn.id,
                    "turn_number": turn.turn_number,
                    "role": turn.role,
                    "content": turn.content,
                    "sentiment": turn.sentiment,
                    "emotion": turn.emotion,
                    "created_at": turn.created_at,
                }
            }

        elif aspect == "history":
            citizen_id = kwargs.get("citizen_id") or kwargs.get("id")
            name = kwargs.get("name")
            limit = kwargs.get("limit", 50)

            # Resolve citizen by ID or name
            if not citizen_id and name:
                citizen = await self._persistence.get_citizen_by_name(name)
                if citizen:
                    citizen_id = citizen.id

            if not citizen_id:
                return {"error": "citizen_id or name required"}

            conversations = await self._persistence.get_dialogue_history(
                citizen_id=citizen_id,
                limit=limit,
            )
            return {
                "citizen_id": citizen_id,
                "conversations": [
                    {
                        "id": c.id,
                        "topic": c.topic,
                        "summary": c.summary,
                        "turn_count": c.turn_count,
                        "is_active": c.is_active,
                        "created_at": c.created_at,
                    }
                    for c in conversations
                ],
            }

        # === Relationship Operations ===

        elif aspect == "relationships":
            citizen_id = kwargs.get("citizen_id") or kwargs.get("id")
            name = kwargs.get("name")

            # Resolve citizen by ID or name
            if not citizen_id and name:
                citizen = await self._persistence.get_citizen_by_name(name)
                if citizen:
                    citizen_id = citizen.id

            if not citizen_id:
                return {"error": "citizen_id or name required"}

            relationships = await self._persistence.get_relationships(citizen_id)
            return RelationshipListRendering(
                relationships=relationships,
                citizen_id=citizen_id,
            ).to_dict()

        # === Simulation Operations ===

        elif aspect == "gossip":
            # Future: Stream inter-citizen dialogue
            return {
                "message": "Gossip stream not yet implemented",
                "hint": "Use SSE endpoint",
            }

        elif aspect == "step":
            # Future: Advance simulation
            return {
                "message": "Simulation step not yet implemented",
                "hint": "Use world.town.step",
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "TownNode",
    "TownManifestRendering",
    "CitizenRendering",
    "CitizenListRendering",
    "ConversationRendering",
    "RelationshipListRendering",
]
