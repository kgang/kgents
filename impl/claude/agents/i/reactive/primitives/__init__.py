"""
Reactive Primitives: The atomic visual units.

Glyph is the atomic unit. Everything composes from glyphs:
- Bar: horizontal/vertical fill (composes glyphs)
- Sparkline: mini timeseries (composes glyphs)
- DensityField: 2D grid with spatial entropy coherence

Wave 1: GlyphWidget (atomic)
Wave 2: BarWidget, SparklineWidget, DensityFieldWidget (composed)
"""

from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.density_field import (
    DensityFieldState,
    DensityFieldWidget,
    Entity,
    Wind,
)
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget

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
]
