"""
Tiny Atelier: A gentle workshop for making beautiful things.

Theme: Orisinal.com aesthetic—whimsical, minimal, melancholic but hopeful.

Atelier is a streaming-first implementation demonstrating the full kgents
ecosystem: PolyAgent state machines, Operad composition, EventBus fan-out,
and multi-projection support.

Architecture:
    Commission → EventBus → Artisan → Piece
                    ↓
              Subscribers (CLI, Web, Gallery)

Streaming Philosophy:
    Everything is a stream. The commission doesn't "call" the artisan;
    it emits intent into the flux. The artisan doesn't "return" a piece;
    it yields fragments into the stream.

See: docs/systems-reference.md for infrastructure details.
"""

# Polynomial and Operad (Layers 2 & 3 of Vertical Slice)
from agents.atelier.artisan import (
    Artisan,
    ArtisanState,
    Choice,
    Commission,
    Piece,
    Provenance,
)
from agents.atelier.bidding import (
    BID_COSTS,
    BID_PRIORITIES,
    AtelierBidManager,
    Bid,
    BidOutcome,
    BidQueue,
    BidResult,
    BidType,
    SpectatorStats,
    get_bid_manager,
)
from agents.atelier.economy import (
    AccrualResult,
    AccrualTier,
    AsyncTokenPool,
    InsufficientBalanceError,
    InvalidAmountError,
    InvalidUserError,
    LicenseTierProvider,
    RefundResult,
    SessionError,
    SpendResult,
    TokenPool,
    TokenPoolError,
    UserBalance,
    create_async_token_pool,
    create_token_pool,
    create_token_pool_with_licensing,
)
from agents.atelier.gestalt_integration import (
    CodeIssue,
    GestaltArtifactAnalysis,
    analyze_artifact_code,
    analyze_piece,
    create_health_badge_props,
    emit_artifact_analysis_complete,
)
from agents.atelier.polynomial import (
    ATELIER_POLYNOMIAL,
    WORKSHOP_POLYNOMIAL,
    CloseInput,
    ContributeInput,
    ContributeOutput,
    ExhibitOutput,
    JoinInput,
    JoinOutput,
    OpenExhibitionInput,
    RefineInput,
    StartExhibitionInput,
    ViewInput,
    WorkshopInput,
    WorkshopOutput,
    WorkshopPhase,
    workshop_directions,
    workshop_transition,
)
from agents.atelier.synergy import (
    SynergyAwareWorkshop,
    emit_bid_accepted,
    emit_piece_created,
    wrap_stream_with_synergy,
)
from agents.atelier.workshop import Workshop, WorkshopFlux
from agents.atelier.workshop.operad import (
    ATELIER_OPERAD,
    CompositionLaw,
    create_atelier_operad,
)

__all__ = [
    # Polynomial (Layer 2)
    "ATELIER_POLYNOMIAL",
    "WORKSHOP_POLYNOMIAL",
    "WorkshopPhase",
    "WorkshopInput",
    "WorkshopOutput",
    "JoinInput",
    "JoinOutput",
    "ContributeInput",
    "ContributeOutput",
    "RefineInput",
    "StartExhibitionInput",
    "OpenExhibitionInput",
    "ViewInput",
    "CloseInput",
    "ExhibitOutput",
    "workshop_directions",
    "workshop_transition",
    # Operad (Layer 3)
    "ATELIER_OPERAD",
    "create_atelier_operad",
    "CompositionLaw",
    # Core types
    "Artisan",
    "ArtisanState",
    "Commission",
    "Choice",
    "Piece",
    "Provenance",
    # Workshop
    "Workshop",
    "WorkshopFlux",
    # Bidding (Spike 1B: Spectator Economy)
    "Bid",
    "BidType",
    "BidOutcome",
    "BidResult",
    "BidQueue",
    "SpectatorStats",
    "AtelierBidManager",
    "BID_COSTS",
    "BID_PRIORITIES",
    "get_bid_manager",
    # Economy (Spike 1A: TokenPool)
    "TokenPool",
    "AsyncTokenPool",
    "UserBalance",
    "AccrualTier",
    "AccrualResult",
    "SpendResult",
    "RefundResult",
    "LicenseTierProvider",
    "create_token_pool",
    "create_async_token_pool",
    "create_token_pool_with_licensing",
    # Economy Exceptions
    "TokenPoolError",
    "InvalidUserError",
    "InvalidAmountError",
    "InsufficientBalanceError",
    "SessionError",
    # Synergy (Wave 2: Brain integration)
    "emit_piece_created",
    "emit_bid_accepted",
    "wrap_stream_with_synergy",
    "SynergyAwareWorkshop",
    # Gestalt Integration (Wave 2: Code analysis)
    "CodeIssue",
    "GestaltArtifactAnalysis",
    "analyze_artifact_code",
    "analyze_piece",
    "create_health_badge_props",
    "emit_artifact_analysis_complete",
]
