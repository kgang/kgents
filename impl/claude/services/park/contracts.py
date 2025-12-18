"""
Park AGENTESE Contract Definitions.

Defines request and response types for Park @node contracts.
These enable BE/FE contract synchronization via AGENTESE discovery.

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest, host.list, host.get)
- Contract() for mutation aspects (host.create, host.interact)

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
class ParkManifestResponse:
    """Park health status manifest response."""

    total_hosts: int
    active_hosts: int
    total_episodes: int
    active_episodes: int
    total_memories: int
    total_locations: int
    consent_refusal_rate: float
    storage_backend: str


# === Host Types ===


@dataclass(frozen=True)
class HostSummary:
    """Summary of a park host for list views."""

    id: str
    name: str
    character: str
    is_active: bool
    location: str | None
    mood: str | None


@dataclass(frozen=True)
class HostDetail:
    """Full host details."""

    id: str
    name: str
    character: str
    backstory: str | None
    traits: list[str]
    values: list[str]
    boundaries: list[str]
    is_active: bool
    mood: str | None
    energy_level: float
    current_location: str | None
    interaction_count: int
    consent_refusal_count: int


@dataclass(frozen=True)
class HostListResponse:
    """Response for host list aspect."""

    count: int
    hosts: list[HostSummary]


@dataclass(frozen=True)
class HostGetResponse:
    """Response for host get aspect."""

    host: HostDetail


# === Host Mutation Requests ===


@dataclass(frozen=True)
class HostCreateRequest:
    """Request to create a new park host."""

    name: str
    character: str
    backstory: str | None = None
    traits: list[str] | None = None
    values: list[str] | None = None
    boundaries: list[str] | None = None
    location: str | None = None


@dataclass(frozen=True)
class HostCreateResponse:
    """Response after creating a host."""

    host: HostDetail


@dataclass(frozen=True)
class HostUpdateRequest:
    """Request to update host state."""

    host_id: str
    mood: str | None = None
    energy_level: float | None = None
    location: str | None = None


@dataclass(frozen=True)
class HostUpdateResponse:
    """Response after updating a host."""

    host: HostDetail


# === Interaction Types ===


@dataclass(frozen=True)
class InteractionDetail:
    """Details of an interaction with a host."""

    id: str
    host_name: str
    interaction_type: str
    visitor_input: str
    host_response: str | None
    consent_requested: bool
    consent_given: bool | None
    consent_reason: str | None
    host_emotion: str | None
    location: str | None


@dataclass(frozen=True)
class HostInteractRequest:
    """Request to interact with a host."""

    episode_id: str
    host_id: str
    input: str
    type: str = "dialogue"
    location: str | None = None
    check_consent: bool = True


@dataclass(frozen=True)
class HostInteractResponse:
    """Response after interacting with a host."""

    interaction: InteractionDetail


# === Memory Types ===


@dataclass(frozen=True)
class MemorySummary:
    """Summary of a host memory."""

    id: str
    memory_type: str
    summary: str | None
    salience: float
    emotional_valence: float


@dataclass(frozen=True)
class HostWitnessRequest:
    """Request to view host memories."""

    host_id: str
    memory_type: str | None = None
    min_salience: float = 0.0
    limit: int = 20


@dataclass(frozen=True)
class HostWitnessResponse:
    """Response for host memories."""

    count: int
    memories: list[MemorySummary]


# === Episode Types ===


@dataclass(frozen=True)
class EpisodeSummary:
    """Summary of a park episode for list views."""

    id: str
    title: str | None
    status: str
    visitor_name: str | None
    interaction_count: int
    started_at: str


@dataclass(frozen=True)
class EpisodeDetail:
    """Full episode details."""

    id: str
    visitor_id: str
    visitor_name: str | None
    title: str | None
    status: str
    interaction_count: int
    hosts_met: list[str]
    locations_visited: list[str]
    started_at: str
    ended_at: str | None
    duration_seconds: int | None


@dataclass(frozen=True)
class EpisodeListResponse:
    """Response for episode list aspect."""

    count: int
    episodes: list[EpisodeSummary]


@dataclass(frozen=True)
class EpisodeStartRequest:
    """Request to start a park episode."""

    visitor_name: str | None = None
    title: str | None = None


@dataclass(frozen=True)
class EpisodeStartResponse:
    """Response after starting an episode."""

    episode: EpisodeDetail


@dataclass(frozen=True)
class EpisodeEndRequest:
    """Request to end a park episode."""

    episode_id: str
    summary: str | None = None
    status: str = "completed"


@dataclass(frozen=True)
class EpisodeEndResponse:
    """Response after ending an episode."""

    episode: EpisodeDetail


# === Location Types ===


@dataclass(frozen=True)
class LocationSummary:
    """Summary of a park location."""

    id: str
    name: str
    description: str | None
    atmosphere: str | None
    is_open: bool


@dataclass(frozen=True)
class LocationListResponse:
    """Response for location list aspect."""

    count: int
    locations: list[LocationSummary]


@dataclass(frozen=True)
class LocationCreateRequest:
    """Request to create a location."""

    name: str
    description: str | None = None
    atmosphere: str | None = None
    x: float | None = None
    y: float | None = None
    capacity: int | None = None
    connected_to: list[str] | None = None


@dataclass(frozen=True)
class LocationCreateResponse:
    """Response after creating a location."""

    id: str
    name: str
    description: str | None
    atmosphere: str | None
    is_open: bool


# === Exports ===

__all__ = [
    # Manifest
    "ParkManifestResponse",
    # Host
    "HostSummary",
    "HostDetail",
    "HostListResponse",
    "HostGetResponse",
    "HostCreateRequest",
    "HostCreateResponse",
    "HostUpdateRequest",
    "HostUpdateResponse",
    # Interaction
    "InteractionDetail",
    "HostInteractRequest",
    "HostInteractResponse",
    # Memory
    "MemorySummary",
    "HostWitnessRequest",
    "HostWitnessResponse",
    # Episode
    "EpisodeSummary",
    "EpisodeDetail",
    "EpisodeListResponse",
    "EpisodeStartRequest",
    "EpisodeStartResponse",
    "EpisodeEndRequest",
    "EpisodeEndResponse",
    # Location
    "LocationSummary",
    "LocationListResponse",
    "LocationCreateRequest",
    "LocationCreateResponse",
]
