"""
Reactive Primitives: The atomic visual units.

Glyph is the atomic unit. Everything composes from glyphs:
- Bar: horizontal/vertical fill (composes glyphs)
- Sparkline: mini timeseries (composes glyphs)
- DensityField: 2D grid with spatial entropy coherence

Wave 1: GlyphWidget (atomic)
Wave 2: BarWidget, SparklineWidget, DensityFieldWidget (composed)
Wave 3: AgentCardWidget, YieldCardWidget (molecules -> organisms)
"""

from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.density_field import (
    DensityFieldState,
    DensityFieldWidget,
    Entity,
    Wind,
)
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
from agents.i.reactive.primitives.hgent_card import (
    DialecticCardState,
    DialecticCardWidget,
    ShadowCardState,
    ShadowCardWidget,
    ShadowItem,
)
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
from agents.i.reactive.primitives.yield_card import YieldCardState, YieldCardWidget

__all__ = [
    # Wave 1: Atomic
    "GlyphWidget",
    "GlyphState",
    # Wave 2: Composed
    "BarWidget",
    "BarState",
    "SparklineWidget",
    "SparklineState",
    "DensityFieldWidget",
    "DensityFieldState",
    "Entity",
    "Wind",
    # Wave 3: Cards (molecules -> organisms)
    "AgentCardWidget",
    "AgentCardState",
    "YieldCardWidget",
    "YieldCardState",
    # H-gent Cards (introspection visualization)
    "ShadowCardWidget",
    "ShadowCardState",
    "ShadowItem",
    "DialecticCardWidget",
    "DialecticCardState",
]
