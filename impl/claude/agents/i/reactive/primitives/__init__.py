"""
Reactive Primitives: The atomic visual units.

Glyph is the atomic unit. Everything composes from glyphs:
- Bar: horizontal fill (composes glyphs)
- Sparkline: mini timeseries (composes glyphs)
- DensityField: 2D grid (composes glyphs)

This module currently implements Wave 1 (Glyph only).
"""

from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

__all__ = [
    "GlyphWidget",
    "GlyphState",
]
