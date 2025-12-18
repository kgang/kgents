"""
Town AGENTESE Contract Definitions.

Defines request and response types for Town @node contracts.
These enable BE/FE contract synchronization via AGENTESE discovery.

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest, citizen.list, citizen.get)
- Contract() for mutation aspects (citizen.create, citizen.update)

Types here are used by:
1. @node(contracts={...}) in node.py
2. /discover?include_schemas=true endpoint
3. web/scripts/sync-types.ts for FE type generation

See: plans/autopoietic-architecture.md (Phase 7)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# === Manifest Response ===


@dataclass(frozen=True)
class TownManifestResponse:
    """Town health status manifest response."""

    total_citizens: int
    active_citizens: int
    total_conversations: int
    active_conversations: int
    total_relationships: int
    storage_backend: str


# === Citizen Types ===


@dataclass(frozen=True)
class CitizenSummary:
    """Summary of a citizen for list views."""

    id: str
    name: str
    archetype: str
    is_active: bool
    interaction_count: int


@dataclass(frozen=True)
class CitizenDetail:
    """Full citizen details."""

    id: str
    name: str
    archetype: str
    description: str | None
    traits: dict[str, Any]
    is_active: bool
    interaction_count: int
    last_interaction: str | None
    created_at: str


@dataclass(frozen=True)
class CitizenListResponse:
    """Response for citizen list aspect."""

    citizens: list[CitizenSummary]
    total: int


@dataclass(frozen=True)
class CitizenGetResponse:
    """Response for citizen get aspect."""

    citizen: CitizenDetail


# === Citizen Mutation Requests ===


@dataclass(frozen=True)
class CitizenCreateRequest:
    """Request to create a new citizen."""

    name: str
    archetype: str = "default"
    description: str | None = None
    traits: dict[str, Any] | None = None


@dataclass(frozen=True)
class CitizenCreateResponse:
    """Response after creating a citizen."""

    citizen: CitizenDetail


@dataclass(frozen=True)
class CitizenUpdateRequest:
    """Request to update a citizen."""

    citizen_id: str
    description: str | None = None
    traits: dict[str, Any] | None = None
    is_active: bool | None = None


@dataclass(frozen=True)
class CitizenUpdateResponse:
    """Response after updating a citizen."""

    citizen: CitizenDetail


# === Conversation Types ===


@dataclass(frozen=True)
class TurnSummary:
    """Summary of a conversation turn."""

    id: str
    turn_number: int
    role: str
    content: str
    sentiment: str | None
    emotion: str | None
    created_at: str


@dataclass(frozen=True)
class ConversationDetail:
    """Full conversation details."""

    id: str
    citizen_id: str
    citizen_name: str
    topic: str | None
    summary: str | None
    turn_count: int
    is_active: bool
    created_at: str
    turns: list[TurnSummary] = field(default_factory=list)


@dataclass(frozen=True)
class ConverseRequest:
    """Request to start a conversation with a citizen."""

    citizen_id: str | None = None
    name: str | None = None
    topic: str | None = None


@dataclass(frozen=True)
class ConverseResponse:
    """Response after starting a conversation."""

    conversation: ConversationDetail


@dataclass(frozen=True)
class TurnRequest:
    """Request to add a turn to a conversation."""

    conversation_id: str
    content: str
    role: str = "user"
    sentiment: str | None = None
    emotion: str | None = None


@dataclass(frozen=True)
class TurnResponse:
    """Response after adding a turn."""

    turn: TurnSummary


@dataclass(frozen=True)
class HistoryRequest:
    """Request for dialogue history."""

    citizen_id: str | None = None
    name: str | None = None
    limit: int = 50


@dataclass(frozen=True)
class ConversationSummary:
    """Summary of a conversation for history views."""

    id: str
    topic: str | None
    summary: str | None
    turn_count: int
    is_active: bool
    created_at: str


@dataclass(frozen=True)
class HistoryResponse:
    """Response for dialogue history."""

    citizen_id: str
    conversations: list[ConversationSummary]


# === Relationship Types ===


@dataclass(frozen=True)
class RelationshipSummary:
    """Summary of a citizen relationship."""

    id: str
    citizen_a_id: str
    citizen_b_id: str
    relationship_type: str
    strength: float
    interaction_count: int
    notes: str | None


@dataclass(frozen=True)
class RelationshipsRequest:
    """Request for citizen relationships."""

    citizen_id: str | None = None
    name: str | None = None


@dataclass(frozen=True)
class RelationshipsResponse:
    """Response for citizen relationships."""

    citizen_id: str
    count: int
    relationships: list[RelationshipSummary]


# === Exports ===

__all__ = [
    # Manifest
    "TownManifestResponse",
    # Citizen
    "CitizenSummary",
    "CitizenDetail",
    "CitizenListResponse",
    "CitizenGetResponse",
    "CitizenCreateRequest",
    "CitizenCreateResponse",
    "CitizenUpdateRequest",
    "CitizenUpdateResponse",
    # Conversation
    "TurnSummary",
    "ConversationDetail",
    "ConversationSummary",
    "ConverseRequest",
    "ConverseResponse",
    "TurnRequest",
    "TurnResponse",
    "HistoryRequest",
    "HistoryResponse",
    # Relationships
    "RelationshipSummary",
    "RelationshipsRequest",
    "RelationshipsResponse",
]
