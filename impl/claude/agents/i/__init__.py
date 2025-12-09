"""
I-gents: The Living Codex Garden.

Interface agents that render the kgents ecosystem visible. They transform
abstract composition graphs into tangible, navigable, contemplative spaces.

Core concepts:
- Phase: Moon-cycle lifecycle states (dormant, waking, active, waning, empty)
- Glyph: Atomic unit of visualization (phase symbol + identity)
- Scale: Fractal zoom levels (glyph → card → page → garden → library)

Aesthetic:
- Paper-Terminal: Warm cream + warm black, monospace, box-drawing characters
- Contemplative: Breath cycle, margin notes, archival permanence
- Fractal: Same grammar at all scales

Example:
    >>> from agents.i import Phase, Glyph, CardRenderer
    >>>
    >>> glyph = Glyph(agent_id="robin", phase=Phase.ACTIVE)
    >>> print(glyph.render())  # "● robin"
    >>>
    >>> card = CardRenderer(glyph, joy=0.9, ethics=0.8)
    >>> print(card.render())
    # ┌─ robin ────────┐
    # │ ● active       │
    # │ joy: █████████░│
    # │ eth: ████████░░│
    # └────────────────┘
"""

from .types import (
    Phase,
    Glyph,
    Scale,
    MarginNote,
    NoteSource,
    AgentState,
    GardenState,
)
from .renderers import (
    GlyphRenderer,
    CardRenderer,
    PageRenderer,
    GardenRenderer,
    LibraryRenderer,
)
from .export import MarkdownExporter
from .breath import BreathCycle, BreathManager
from .observe import ObserveAction, GardenObserver

__all__ = [
    # Types
    "Phase",
    "Glyph",
    "Scale",
    "MarginNote",
    "NoteSource",
    "AgentState",
    "GardenState",
    # Renderers
    "GlyphRenderer",
    "CardRenderer",
    "PageRenderer",
    "GardenRenderer",
    "LibraryRenderer",
    # Export
    "MarkdownExporter",
    # Aesthetics
    "BreathCycle",
    "BreathManager",
    # W-gent Integration
    "ObserveAction",
    "GardenObserver",
]
