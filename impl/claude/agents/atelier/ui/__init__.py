"""
Atelier UI: Reactive widgets for the creative workshop.

Widgets follow the KgentsWidget protocol:
1. Signal[S] for state
2. Computed for derived values
3. Effect for side effects
4. project() for target-agnostic rendering

Exports:
- PieceWidget: Display a single piece with provenance
- GalleryWidget: Grid of pieces
- AtelierWidget: Workshop status dashboard
"""

from agents.atelier.ui.widgets import (
    AtelierState,
    AtelierWidget,
    GalleryState,
    GalleryWidget,
    PieceState,
    PieceWidget,
)

__all__ = [
    "AtelierWidget",
    "GalleryWidget",
    "PieceWidget",
    "AtelierState",
    "GalleryState",
    "PieceState",
]
