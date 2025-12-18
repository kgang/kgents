"""
Forge Crown Jewel: Creative Workshop Fishbowl.

The Forge is a collaborative creative workshop where spectators can
observe and participate in the creative process.

AGENTESE Paths:
- world.forge.manifest - Show workshop status
- world.forge.workshop.* - Workshop management
- world.forge.artisan.* - Artisan participation
- world.forge.contribute - Submit creative work
- world.forge.exhibition.* - Exhibition curation
- world.forge.gallery.* - Gallery viewing
- world.forge.tokens.* - Spectator economy
- world.forge.bid.* - Constraint injection
- world.forge.festival.* - Seasonal events

Design DNA:
- Fishbowl transparency: Process is visible
- Collaborative: Multiple participants can contribute
- Exhibition-ready: Works can be showcased
- Spectator economy: Watch to earn, bid to influence

Service Architecture:
- ForgeNode: AGENTESE universal gateway
- ForgePersistence: Workshop/exhibition storage
- ForgeEconomyService: Token pool management
- ForgeBiddingService: Constraint injection queue
- ForgeFestivalService: Seasonal creative events

See: docs/skills/metaphysical-fullstack.md
"""

from .bidding_service import (
    ForgeBiddingService,
    BidView,
    QueueStatusView,
    SpectatorStatsView,
    get_bid_cost,
    get_bid_priority,
)
from .economy_service import (
    ForgeEconomyService,
    EconomyStatusView,
    TokenBalanceView,
)
from .festival_service import (
    ForgeFestivalService,
    FestivalEntryView,
    FestivalSummaryView,
    FestivalView,
)
from .node import (
    ArtisanListRendering,
    ArtisanRendering,
    ForgeManifestRendering,
    ForgeNode,
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
    ForgePersistence,
    ForgeStatus,
    ContributionView,
    ExhibitionView,
    GalleryItemView,
    WorkshopView,
)

__all__ = [
    # Persistence
    "ForgePersistence",
    "ForgeStatus",
    "WorkshopView",
    "ArtisanView",
    "ContributionView",
    "ExhibitionView",
    "GalleryItemView",
    # Node
    "ForgeNode",
    "ForgeManifestRendering",
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
    "ForgeEconomyService",
    "TokenBalanceView",
    "EconomyStatusView",
    # Bidding Service
    "ForgeBiddingService",
    "BidView",
    "SpectatorStatsView",
    "QueueStatusView",
    "get_bid_cost",
    "get_bid_priority",
    # Festival Service
    "ForgeFestivalService",
    "FestivalView",
    "FestivalEntryView",
    "FestivalSummaryView",
]
