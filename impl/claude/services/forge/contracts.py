"""
Forge AGENTESE Contract Definitions.

Defines request and response types for Forge @node contracts.
These enable BE/FE contract synchronization via AGENTESE discovery.

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest, workshop.list, artisan.list)
- Contract() for mutation aspects (workshop.create, contribute, exhibition.create)

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
class ForgeManifestResponse:
    """Forge health status manifest response."""

    total_workshops: int
    active_workshops: int
    total_artisans: int
    total_contributions: int
    total_exhibitions: int
    open_exhibitions: int
    storage_backend: str


# === Workshop Types ===


@dataclass(frozen=True)
class WorkshopSummary:
    """Summary of a workshop."""

    id: str
    name: str
    description: str | None
    theme: str | None
    is_active: bool
    artisan_count: int
    contribution_count: int
    started_at: str | None
    created_at: str


@dataclass(frozen=True)
class WorkshopListResponse:
    """Response for workshop list aspect."""

    count: int
    workshops: list[WorkshopSummary]


@dataclass(frozen=True)
class WorkshopGetRequest:
    """Request for workshop details."""

    workshop_id: str


@dataclass(frozen=True)
class WorkshopGetResponse:
    """Response for workshop details."""

    workshop: WorkshopSummary


@dataclass(frozen=True)
class WorkshopCreateRequest:
    """Request to create a workshop."""

    name: str
    description: str | None = None
    theme: str | None = None
    config: dict[str, Any] | None = None


@dataclass(frozen=True)
class WorkshopCreateResponse:
    """Response after creating a workshop."""

    workshop: WorkshopSummary


@dataclass(frozen=True)
class WorkshopEndRequest:
    """Request to end a workshop."""

    workshop_id: str


@dataclass(frozen=True)
class WorkshopEndResponse:
    """Response after ending a workshop."""

    success: bool
    workshop_id: str


# === Artisan Types ===


@dataclass(frozen=True)
class ArtisanSummary:
    """Summary of an artisan."""

    id: str
    workshop_id: str
    name: str
    specialty: str
    style: str | None
    is_active: bool
    contribution_count: int
    created_at: str


@dataclass(frozen=True)
class ArtisanListRequest:
    """Request for artisan list."""

    workshop_id: str
    specialty: str | None = None
    active_only: bool = True


@dataclass(frozen=True)
class ArtisanListResponse:
    """Response for artisan list."""

    count: int
    artisans: list[ArtisanSummary]


@dataclass(frozen=True)
class ArtisanJoinRequest:
    """Request to join a workshop."""

    workshop_id: str
    name: str
    specialty: str
    style: str | None = None
    agent_id: str | None = None


@dataclass(frozen=True)
class ArtisanJoinResponse:
    """Response after joining a workshop."""

    artisan: ArtisanSummary


# === Contribution Types ===


@dataclass(frozen=True)
class ContributionSummary:
    """Summary of a contribution."""

    id: str
    artisan_id: str
    artisan_name: str
    contribution_type: str
    content_type: str
    content: str  # Truncated in API
    prompt: str | None
    inspiration: str | None
    created_at: str


@dataclass(frozen=True)
class ContributeRequest:
    """Request to submit a contribution."""

    artisan_id: str
    content: str
    content_type: str = "text"
    contribution_type: str = "draft"
    prompt: str | None = None
    inspiration: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class ContributeResponse:
    """Response after contributing."""

    contribution: ContributionSummary


@dataclass(frozen=True)
class ContributionListRequest:
    """Request for contribution list."""

    artisan_id: str | None = None
    workshop_id: str | None = None
    contribution_type: str | None = None
    limit: int = 50


@dataclass(frozen=True)
class ContributionListResponse:
    """Response for contribution list."""

    count: int
    contributions: list[ContributionSummary]


# === Exhibition Types ===


@dataclass(frozen=True)
class ExhibitionSummary:
    """Summary of an exhibition."""

    id: str
    workshop_id: str
    name: str
    description: str | None
    curator_notes: str | None
    is_open: bool
    view_count: int
    item_count: int
    opened_at: str | None
    created_at: str


@dataclass(frozen=True)
class ExhibitionCreateRequest:
    """Request to create an exhibition."""

    workshop_id: str
    name: str
    description: str | None = None
    curator_notes: str | None = None


@dataclass(frozen=True)
class ExhibitionCreateResponse:
    """Response after creating an exhibition."""

    exhibition: ExhibitionSummary


@dataclass(frozen=True)
class ExhibitionOpenRequest:
    """Request to open an exhibition."""

    exhibition_id: str


@dataclass(frozen=True)
class ExhibitionOpenResponse:
    """Response after opening an exhibition."""

    success: bool
    exhibition_id: str


@dataclass(frozen=True)
class ExhibitionViewRequest:
    """Request to view an exhibition."""

    exhibition_id: str


@dataclass(frozen=True)
class ExhibitionViewResponse:
    """Response after viewing an exhibition."""

    exhibition: ExhibitionSummary


# === Gallery Types ===


@dataclass(frozen=True)
class GalleryItemSummary:
    """Summary of a gallery item."""

    id: str
    exhibition_id: str
    artifact_type: str
    artifact_content: str  # Truncated in API
    title: str | None
    description: str | None
    display_order: int
    artisan_ids: list[str]


@dataclass(frozen=True)
class GalleryListRequest:
    """Request for gallery list."""

    exhibition_id: str


@dataclass(frozen=True)
class GalleryListResponse:
    """Response for gallery list."""

    count: int
    items: list[GalleryItemSummary]


@dataclass(frozen=True)
class GalleryAddRequest:
    """Request to add item to gallery."""

    exhibition_id: str
    artifact_content: str
    artifact_type: str = "text"
    title: str | None = None
    description: str | None = None
    artisan_ids: list[str] | None = None


@dataclass(frozen=True)
class GalleryAddResponse:
    """Response after adding to gallery."""

    item: GalleryItemSummary


# === Token Types ===


@dataclass(frozen=True)
class TokenManifestResponse:
    """Token balance manifest."""

    user_id: str
    balance: int
    earning_rate: float | None
    spending_history: list[dict[str, Any]] | None = None


# === Bid Types ===


@dataclass(frozen=True)
class BidSubmitRequest:
    """Request to submit a bid."""

    session_id: str
    bid_type: str
    content: str


@dataclass(frozen=True)
class BidSubmitResponse:
    """Response after submitting a bid."""

    success: bool
    bid_id: str | None
    new_balance: str
    error: str | None = None
    reason: str | None = None


# === Festival Types ===


@dataclass(frozen=True)
class FestivalSummary:
    """Summary of a festival."""

    id: str
    title: str
    theme: str
    description: str | None
    status: str
    season: str
    entry_count: int
    started_at: str | None
    ends_at: str | None


@dataclass(frozen=True)
class FestivalListResponse:
    """Response for festival list."""

    count: int
    festivals: list[FestivalSummary]


@dataclass(frozen=True)
class FestivalCreateRequest:
    """Request to create a festival."""

    title: str
    theme: str
    description: str | None = None
    duration_hours: int = 72
    voting_hours: int = 24


@dataclass(frozen=True)
class FestivalCreateResponse:
    """Response after creating a festival."""

    festival: FestivalSummary


@dataclass(frozen=True)
class FestivalEnterRequest:
    """Request to enter a festival."""

    festival_id: str
    artisan: str
    prompt: str
    content: str
    piece_id: str | None = None


@dataclass(frozen=True)
class FestivalEntrySummary:
    """Summary of a festival entry."""

    id: str
    festival_id: str
    artisan: str
    prompt: str
    content: str
    piece_id: str | None
    submitted_at: str


@dataclass(frozen=True)
class FestivalEnterResponse:
    """Response after entering a festival."""

    entry: FestivalEntrySummary


# === Commission Types (Phase 2.5: Commission Workflow) ===


@dataclass(frozen=True)
class ArtisanOutputSummary:
    """Summary of an artisan's output."""

    artisan: str
    status: str
    output: dict[str, Any] | None
    annotation: str | None
    started_at: str | None
    completed_at: str | None
    error: str | None = None


@dataclass(frozen=True)
class CommissionSummary:
    """Summary of a commission."""

    id: str
    intent: str
    name: str | None
    status: str
    created_at: str
    updated_at: str
    soul_approved: bool
    soul_annotation: str | None
    artisan_outputs: dict[str, ArtisanOutputSummary]
    artifact_path: str | None
    artifact_summary: str | None
    paused: bool


@dataclass(frozen=True)
class CommissionCreateRequest:
    """Request to create a commission."""

    intent: str
    name: str | None = None


@dataclass(frozen=True)
class CommissionCreateResponse:
    """Response after creating a commission."""

    commission: CommissionSummary


@dataclass(frozen=True)
class CommissionGetRequest:
    """Request for commission details."""

    commission_id: str


@dataclass(frozen=True)
class CommissionGetResponse:
    """Response for commission details."""

    commission: CommissionSummary


@dataclass(frozen=True)
class CommissionListResponse:
    """Response for commission list."""

    count: int
    commissions: list[CommissionSummary]


@dataclass(frozen=True)
class CommissionStartRequest:
    """Request to start commission review."""

    commission_id: str


@dataclass(frozen=True)
class CommissionStartResponse:
    """Response after starting commission."""

    commission: CommissionSummary


@dataclass(frozen=True)
class CommissionAdvanceRequest:
    """Request to advance commission to next stage."""

    commission_id: str


@dataclass(frozen=True)
class CommissionAdvanceResponse:
    """Response after advancing commission."""

    commission: CommissionSummary


@dataclass(frozen=True)
class CommissionPauseRequest:
    """Request to pause a commission."""

    commission_id: str


@dataclass(frozen=True)
class CommissionPauseResponse:
    """Response after pausing commission."""

    commission: CommissionSummary


@dataclass(frozen=True)
class CommissionResumeRequest:
    """Request to resume a commission."""

    commission_id: str


@dataclass(frozen=True)
class CommissionResumeResponse:
    """Response after resuming commission."""

    commission: CommissionSummary


@dataclass(frozen=True)
class CommissionCancelRequest:
    """Request to cancel a commission."""

    commission_id: str
    reason: str | None = None


@dataclass(frozen=True)
class CommissionCancelResponse:
    """Response after canceling commission."""

    success: bool
    commission_id: str


# === Spectator Types (Phase 2: FishbowlCanvas) ===


@dataclass(frozen=True)
class SpectatorJoinRequest:
    """Request to join a session as a spectator."""

    session_id: str
    citizen_id: str | None = None
    display_name: str | None = None


@dataclass(frozen=True)
class SpectatorJoinResponse:
    """Response after joining as a spectator."""

    spectator_id: str
    token_balance: int
    session_id: str
    success: bool


@dataclass(frozen=True)
class SpectatorCursor:
    """Spectator cursor position for overlay."""

    id: str
    position_x: float
    position_y: float
    citizen_id: str | None = None
    eigenvector: list[float] | None = None
    last_update: str = ""


@dataclass(frozen=True)
class SpectatorCursorUpdateRequest:
    """Request to update spectator cursor position."""

    session_id: str
    spectator_id: str
    position_x: float
    position_y: float


@dataclass(frozen=True)
class SpectatorCursorUpdateResponse:
    """Response after updating cursor position."""

    success: bool


@dataclass(frozen=True)
class BidQueueResponse:
    """Response for current bid queue."""

    session_id: str
    bids: list[dict[str, Any]]
    spectator_count: int
    is_live: bool


@dataclass(frozen=True)
class SessionStreamEvent:
    """SSE event for session streaming."""

    event_type: str
    session_id: str
    timestamp: str
    data: dict[str, Any] = field(default_factory=dict)


# === Artisan Design Types (Phase 3: Architect & Smith) ===


@dataclass(frozen=True)
class AgentDesignOperation:
    """Operation in an agent design."""

    name: str
    input: str
    output: str
    description: str = ""


@dataclass(frozen=True)
class AgentDesignResponse:
    """Architect's categorical design output."""

    name: str
    description: str
    states: list[str]
    initial_state: str
    transitions: dict[str, list[str]]
    operations: list[AgentDesignOperation]
    laws: list[str]
    rationale: str


@dataclass(frozen=True)
class SmithOutputResponse:
    """Smith's code generation output."""

    path: str
    files: list[str]
    file_count: int
    summary: str


# === Soul Types (K-gent Governance) ===


@dataclass(frozen=True)
class SoulManifestResponse:
    """K-gent soul state manifest response."""

    mode: str
    eigenvectors: dict[str, float]
    session_interactions: int
    session_tokens: int
    has_llm: bool


@dataclass(frozen=True)
class SoulVibeResponse:
    """K-gent personality eigenvector response."""

    dimensions: dict[str, float]
    context: str


# === Exports ===

__all__ = [
    # Manifest
    "ForgeManifestResponse",
    # Workshop
    "WorkshopSummary",
    "WorkshopListResponse",
    "WorkshopGetRequest",
    "WorkshopGetResponse",
    "WorkshopCreateRequest",
    "WorkshopCreateResponse",
    "WorkshopEndRequest",
    "WorkshopEndResponse",
    # Artisan
    "ArtisanSummary",
    "ArtisanListRequest",
    "ArtisanListResponse",
    "ArtisanJoinRequest",
    "ArtisanJoinResponse",
    # Contribution
    "ContributionSummary",
    "ContributeRequest",
    "ContributeResponse",
    "ContributionListRequest",
    "ContributionListResponse",
    # Exhibition
    "ExhibitionSummary",
    "ExhibitionCreateRequest",
    "ExhibitionCreateResponse",
    "ExhibitionOpenRequest",
    "ExhibitionOpenResponse",
    "ExhibitionViewRequest",
    "ExhibitionViewResponse",
    # Gallery
    "GalleryItemSummary",
    "GalleryListRequest",
    "GalleryListResponse",
    "GalleryAddRequest",
    "GalleryAddResponse",
    # Token
    "TokenManifestResponse",
    # Bid
    "BidSubmitRequest",
    "BidSubmitResponse",
    # Festival
    "FestivalSummary",
    "FestivalListResponse",
    "FestivalCreateRequest",
    "FestivalCreateResponse",
    "FestivalEnterRequest",
    "FestivalEntrySummary",
    "FestivalEnterResponse",
    # Spectator (Phase 2: FishbowlCanvas)
    "SpectatorJoinRequest",
    "SpectatorJoinResponse",
    "SpectatorCursor",
    "SpectatorCursorUpdateRequest",
    "SpectatorCursorUpdateResponse",
    "BidQueueResponse",
    "SessionStreamEvent",
    # Soul (K-gent Governance)
    "SoulManifestResponse",
    "SoulVibeResponse",
    # Commission (Phase 2.5: Commission Workflow)
    "ArtisanOutputSummary",
    "CommissionSummary",
    "CommissionCreateRequest",
    "CommissionCreateResponse",
    "CommissionGetRequest",
    "CommissionGetResponse",
    "CommissionListResponse",
    "CommissionStartRequest",
    "CommissionStartResponse",
    "CommissionAdvanceRequest",
    "CommissionAdvanceResponse",
    "CommissionPauseRequest",
    "CommissionPauseResponse",
    "CommissionResumeRequest",
    "CommissionResumeResponse",
    "CommissionCancelRequest",
    "CommissionCancelResponse",
    # Artisan Design (Phase 3: Architect & Smith)
    "AgentDesignOperation",
    "AgentDesignResponse",
    "SmithOutputResponse",
]
