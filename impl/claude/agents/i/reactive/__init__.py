"""
Reactive Substrate: Target-agnostic widget infrastructure.

This module provides the unified reactive primitives that enable the same
widget definition to render across CLI, TUI (Textual), marimo, and JSON API.

Key abstractions:
- Signal[T]: Observable state primitive
- Computed[T]: Derived state (auto-updates when dependencies change)
- Effect: Side effects container
- KgentsWidget[S]: Base widget class with project() for multiple targets

Usage:
    from agents.i.reactive import Signal, Computed, Effect
    from agents.i.reactive import KgentsWidget, RenderTarget
    from agents.i.reactive.entropy import entropy_to_distortion
    from agents.i.reactive.joy import generate_personality
    from agents.i.reactive.primitives.glyph import GlyphWidget, GlyphState

The reactive substrate is grounded in six principles from v0-ui research:
1. Pure Entropy Algebra - No random.random() in render paths
2. Time Flows Downward - Parent provides t to children
3. Projections Are Manifest - project() IS logos.invoke("manifest")
4. Glyph as Atomic Unit - Everything composes from glyphs
5. Deterministic Joy - Same seed -> same personality, forever
6. Slots/Fillers Composition - Operad-like widget composition
"""

from agents.i.reactive.signal import Computed, Effect, Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

__all__ = [
    "Signal",
    "Computed",
    "Effect",
    "KgentsWidget",
    "RenderTarget",
]
