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

from agents.atelier.artisan import (
    Artisan,
    ArtisanState,
    Choice,
    Commission,
    Piece,
    Provenance,
)
from agents.atelier.workshop import Workshop, WorkshopFlux

__all__ = [
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
]
