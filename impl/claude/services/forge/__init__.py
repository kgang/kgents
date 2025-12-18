"""
Forge Crown Jewel: The Metaphysical Fullstack Developer Workshop.

The Forge is where Kent builds agents using categorical artisans.
Unlike Atelier (spectator fishbowl), the Forge is about commission-driven
creation with seven specialized artisans.

AGENTESE Paths:
- world.forge.manifest - Show forge status
- world.forge.commission.* - Commission workflow (K-gent review)
- world.forge.artisan.* - Artisan interaction
- world.forge.artifact.* - Artifact gallery

Seven Artisans (one per stack layer + cross-cutting):
1. K-gent (Soul): Taste-maker, governance, personality
2. Architect: Categorical design (PolyAgent, Operad, Sheaf)
3. Smith: Implementation (service modules, business logic)
4. Herald: Protocol (AGENTESE nodes, contracts)
5. Projector: Surfaces (CLI, Web, marimo)
6. Sentinel: Security (vulnerabilities, hardening)
7. Witness: Testing (T-gent taxonomy)

Design DNA:
- Commission-driven: Kent initiates, K-gent reviews
- Artisan workflow: Each layer has a specialist
- Cross-jewel integration: Every artifact touches all Crown Jewels
- Differance tracking: Full heritage graph of decisions

See: spec/protocols/metaphysical-forge.md
"""

from .festival_service import (
    FestivalEntryView,
    FestivalSummaryView,
    FestivalView,
    ForgeFestivalService,
)
from .node import (
    ArtisanListRendering,
    ArtisanRendering,
    ContributionListRendering,
    ContributionRendering,
    ExhibitionRendering,
    ForgeManifestRendering,
    ForgeNode,
    GalleryItemRendering,
    GalleryListRendering,
    WorkshopListRendering,
    WorkshopRendering,
)
from .persistence import (
    ArtisanView,
    ContributionView,
    ExhibitionView,
    ForgePersistence,
    ForgeStatus,
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
    # Festival Service (kept for seasonal events)
    "ForgeFestivalService",
    "FestivalView",
    "FestivalEntryView",
    "FestivalSummaryView",
]
