"""
Atelier Crown Jewel: Creative Workshop Fishbowl.

The Atelier is a collaborative creative workshop where spectators can
observe and participate in the creative process.

AGENTESE Paths:
- world.atelier.manifest - Show workshop status
- world.atelier.workshop.* - Workshop management
- world.atelier.artisan.* - Artisan participation
- world.atelier.contribute - Submit creative work
- world.atelier.exhibition.* - Exhibition curation
- world.atelier.gallery.* - Gallery viewing
- world.atelier.tokens.* - Spectator economy
- world.atelier.bid.* - Constraint injection
- world.atelier.festival.* - Seasonal events

Design DNA:
- Fishbowl transparency: Process is visible
- Collaborative: Multiple participants can contribute
- Exhibition-ready: Works can be showcased
- Spectator economy: Watch to earn, bid to influence

Service Architecture:
- AtelierNode: AGENTESE universal gateway
- AtelierPersistence: Workshop/exhibition storage
- AtelierEconomyService: Token pool management
- AtelierBiddingService: Constraint injection queue
- AtelierFestivalService: Seasonal creative events

See: docs/skills/metaphysical-fullstack.md
"""

from .bidding_service import (
    AtelierBiddingService,
    BidView,
    QueueStatusView,
    SpectatorStatsView,
    get_bid_cost,
    get_bid_priority,
)
from .economy_service import (
    AtelierEconomyService,
    EconomyStatusView,
    TokenBalanceView,
)
from .festival_service import (
    AtelierFestivalService,
    FestivalEntryView,
    FestivalSummaryView,
    FestivalView,
)
from .node import (
    ArtisanListRendering,
    ArtisanRendering,
    AtelierManifestRendering,
    AtelierNode,
    ContributionListRendering,
    ContributionRendering,
    ExhibitionRendering,
    GalleryItemRendering,
    GalleryListRendering,
    WorkshopListRendering,
    WorkshopRendering,
)
from .persistence import (
    ArtisanView,
    AtelierPersistence,
    AtelierStatus,
    ContributionView,
    ExhibitionView,
    GalleryItemView,
    WorkshopView,
)

__all__ = [
    # Persistence
    "AtelierPersistence",
    "AtelierStatus",
    "WorkshopView",
    "ArtisanView",
    "ContributionView",
    "ExhibitionView",
    "GalleryItemView",
    # Node
    "AtelierNode",
    "AtelierManifestRendering",
    "WorkshopRendering",
    "WorkshopListRendering",
    "ArtisanRendering",
    "ArtisanListRendering",
    "ContributionRendering",
    "ContributionListRendering",
    "ExhibitionRendering",
    "GalleryItemRendering",
    "GalleryListRendering",
    # Economy Service
    "AtelierEconomyService",
    "TokenBalanceView",
    "EconomyStatusView",
    # Bidding Service
    "AtelierBiddingService",
    "BidView",
    "SpectatorStatsView",
    "QueueStatusView",
    "get_bid_cost",
    "get_bid_priority",
    # Festival Service
    "AtelierFestivalService",
    "FestivalView",
    "FestivalEntryView",
    "FestivalSummaryView",
]
