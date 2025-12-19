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


# === Scenario Types ===
# "Westworld where hosts can say no."


@dataclass(frozen=True)
class ScenarioSummary:
    """Summary of a scenario template for list views."""

    id: str
    name: str
    scenario_type: str
    difficulty: str
    estimated_duration_minutes: int
    citizen_count: int
    tags: list[str]


@dataclass(frozen=True)
class ScenarioListResponse:
    """Response for scenario list aspect."""

    count: int
    scenarios: list[ScenarioSummary]


@dataclass(frozen=True)
class ScenarioDetail:
    """Full scenario template details."""

    id: str
    name: str
    scenario_type: str
    description: str
    difficulty: str
    estimated_duration_minutes: int
    citizen_count: int
    region_count: int
    tags: list[str]


@dataclass(frozen=True)
class ScenarioGetRequest:
    """Request to get a scenario template."""

    scenario_id: str
    detail: bool = False


@dataclass(frozen=True)
class ScenarioGetResponse:
    """Response for scenario get aspect."""

    scenario: ScenarioDetail


@dataclass(frozen=True)
class ScenarioStartRequest:
    """Request to start a scenario session."""

    scenario_id: str


@dataclass(frozen=True)
class SessionProgress:
    """Progress of a scenario session."""

    criterion: str
    met: bool


@dataclass(frozen=True)
class ScenarioSessionDetail:
    """Details of an active scenario session."""

    id: str
    template_id: str
    template_name: str
    phase: str
    is_active: bool
    is_terminal: bool
    citizens: list[str]
    time_elapsed: float
    progress: list[SessionProgress]
    started_at: str | None
    ended_at: str | None


@dataclass(frozen=True)
class ScenarioStartResponse:
    """Response after starting a scenario."""

    session: ScenarioSessionDetail


@dataclass(frozen=True)
class ScenarioTickRequest:
    """Request to advance a scenario session."""

    session_id: str
    elapsed_seconds: float = 1.0


@dataclass(frozen=True)
class ScenarioTickResponse:
    """Response after advancing a scenario."""

    phase: str
    time_elapsed: float
    progress: list[SessionProgress]
    is_complete: bool


@dataclass(frozen=True)
class ScenarioEndRequest:
    """Request to end/abandon a scenario session."""

    session_id: str
    reason: str = ""


@dataclass(frozen=True)
class ScenarioEndResponse:
    """Response after ending a scenario."""

    session: ScenarioSessionDetail


@dataclass(frozen=True)
class ScenarioSessionListResponse:
    """Response for active sessions list."""

    count: int
    sessions: list[ScenarioSessionDetail]


# === Consent Debt Types ===
# "Westworld where hosts can say no"


@dataclass(frozen=True)
class ConsentDebtRequest:
    """Request for consent debt operations."""

    session_id: str
    citizen_name: str
    amount: float = 0.1  # For incur/apologize operations


@dataclass(frozen=True)
class ConsentDebtResponse:
    """Response for consent debt operations."""

    citizen: str
    debt: float
    can_inject_beat: bool
    status: str = "ok"


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
    # Scenario
    "ScenarioSummary",
    "ScenarioListResponse",
    "ScenarioDetail",
    "ScenarioGetRequest",
    "ScenarioGetResponse",
    "ScenarioStartRequest",
    "ScenarioSessionDetail",
    "SessionProgress",
    "ScenarioStartResponse",
    "ScenarioTickRequest",
    "ScenarioTickResponse",
    "ScenarioEndRequest",
    "ScenarioEndResponse",
    "ScenarioSessionListResponse",
    # Consent Debt
    "ConsentDebtRequest",
    "ConsentDebtResponse",
]
