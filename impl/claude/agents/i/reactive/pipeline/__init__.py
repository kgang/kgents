"""
Pipeline: Widget Integration Pipeline for reactive rendering.

Wave 9 of the reactive substrate - connecting all pieces into a cohesive system.

This module provides:
- RenderPipeline: Central orchestrator for frame updates
- Layout System: Flex, Grid, and constraint-based sizing
- Theme System: Consistent styling with dark/light modes

"The best pipeline is the one you don't notice. Smooth, invisible, reliable."
"""

from agents.i.reactive.pipeline.focus import (
    AnimatedFocus,
    FocusTransition,
    create_animated_focus,
)
from agents.i.reactive.pipeline.layout import (
    Constraints,
    FlexAlign,
    FlexDirection,
    FlexLayout,
    FlexWrap,
    GridLayout,
    LayoutBox,
    LayoutNode,
    Sizing,
)
from agents.i.reactive.pipeline.render import (
    RenderNode,
    RenderPipeline,
    RenderPriority,
    RenderState,
    create_render_pipeline,
)
from agents.i.reactive.pipeline.theme import (
    ColorToken,
    SpacingToken,
    Theme,
    ThemeMode,
    create_theme,
)

__all__ = [
    # Render
    "RenderNode",
    "RenderPipeline",
    "RenderPriority",
    "RenderState",
    "create_render_pipeline",
    # Layout
    "Constraints",
    "FlexAlign",
    "FlexDirection",
    "FlexLayout",
    "FlexWrap",
    "GridLayout",
    "LayoutBox",
    "LayoutNode",
    "Sizing",
    # Theme
    "ColorToken",
    "SpacingToken",
    "Theme",
    "ThemeMode",
    "create_theme",
    # Focus
    "AnimatedFocus",
    "FocusTransition",
    "create_animated_focus",
]
