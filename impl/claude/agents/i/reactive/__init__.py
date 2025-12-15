"""
Reactive Substrate v1.0 - Target-agnostic widget infrastructure.

This module provides the unified reactive primitives that enable the same
widget definition to render across CLI, TUI (Textual), marimo, and JSON API.

Architecture:
    project : KgentsWidget[S] → Target → Renderable[Target]

Same widget state, different projections. Zero rewrites.

Quick Start:
    from agents.i.reactive import AgentCardWidget, AgentCardState

    # Define once
    card = AgentCardWidget(AgentCardState(
        name="My Agent",
        phase="active",
        activity=(0.3, 0.5, 0.7, 0.9),
        capability=0.85,
    ))

    # Render anywhere
    print(card.to_cli())      # Terminal
    card.to_tui()             # Textual app
    card.to_marimo()          # Notebook
    card.to_json()            # API response

Key Abstractions:
    - Signal[T]: Observable state primitive
    - Computed[T]: Derived state (auto-updates when dependencies change)
    - Effect: Side effects container
    - KgentsWidget[S]: Base widget class with project() for multiple targets
    - CompositeWidget[S]: Widget that composes child widgets in slots
    - HStack/VStack: Composition containers via >> and // operators

Principles:
    1. Pure Entropy Algebra - No random.random() in render paths
    2. Time Flows Downward - Parent provides t to children
    3. Projections Are Manifest - project() IS logos.invoke("manifest")
    4. Glyph as Atomic Unit - Everything composes from glyphs
    5. Deterministic Joy - Same seed -> same personality, forever
    6. Slots/Fillers Composition - Operad-like widget composition
"""

# Re-export adapters
from agents.i.reactive.adapters import (
    AgentTraceState,
    AgentTraceWidget,
    FlexContainer,
    FocusSync,
    MarimoAdapter,
    NotebookTheme,
    SpanData,
    TextualAdapter,
    ThemeBinding,
    create_flex_container,
    create_focus_sync,
    create_marimo_adapter,
    create_notebook_theme,
    create_textual_adapter,
    create_theme_binding,
    create_trace_widget,
    inject_theme_css,
    is_anywidget_available,
)
from agents.i.reactive.colony_bridge import (
    ActivityBuffer,
    ColonyDashboardBridge,
    create_bridge_and_dashboard,
)
from agents.i.reactive.colony_dashboard import (
    ColonyDashboard,
    ColonyState,
    TownPhase,
)
from agents.i.reactive.composable import (
    ComposableMixin,
    ComposableWidget,
    HStack,
    VStack,
)

# Re-export primitives
from agents.i.reactive.primitives import (
    AgentCardState,
    AgentCardWidget,
    BarState,
    BarWidget,
    DensityFieldState,
    DensityFieldWidget,
    DialecticCardState,
    DialecticCardWidget,
    Entity,
    GlyphState,
    GlyphWidget,
    ShadowCardState,
    ShadowCardWidget,
    ShadowItem,
    SparklineState,
    SparklineWidget,
    Wind,
    YieldCardState,
    YieldCardWidget,
)

# Wave 4: Agent Town Citizen Dashboard
from agents.i.reactive.primitives.citizen_card import (
    NPHASE_LABELS,
    PHASE_GLYPHS,
    CitizenState,
    CitizenWidget,
)
from agents.i.reactive.signal import Computed, Effect, Signal
from agents.i.reactive.widget import CompositeWidget, KgentsWidget, RenderTarget

__version__ = "1.0.0"

__all__ = [
    # Core
    "Signal",
    "Computed",
    "Effect",
    "KgentsWidget",
    "CompositeWidget",
    "RenderTarget",
    # Composition
    "ComposableWidget",
    "ComposableMixin",
    "HStack",
    "VStack",
    # Primitives - Atomic
    "GlyphWidget",
    "GlyphState",
    # Primitives - Composed
    "BarWidget",
    "BarState",
    "SparklineWidget",
    "SparklineState",
    "DensityFieldWidget",
    "DensityFieldState",
    "Entity",
    "Wind",
    # Primitives - Cards
    "AgentCardWidget",
    "AgentCardState",
    "YieldCardWidget",
    "YieldCardState",
    # Primitives - H-gent Cards
    "ShadowCardWidget",
    "ShadowCardState",
    "ShadowItem",
    "DialecticCardWidget",
    "DialecticCardState",
    # Adapters - Textual
    "TextualAdapter",
    "create_textual_adapter",
    "FlexContainer",
    "create_flex_container",
    "ThemeBinding",
    "create_theme_binding",
    "FocusSync",
    "create_focus_sync",
    # Adapters - Marimo
    "MarimoAdapter",
    "create_marimo_adapter",
    "is_anywidget_available",
    "NotebookTheme",
    "create_notebook_theme",
    "inject_theme_css",
    "AgentTraceWidget",
    "AgentTraceState",
    "SpanData",
    "create_trace_widget",
    # Wave 4: Agent Town Citizen Dashboard
    "CitizenWidget",
    "CitizenState",
    "PHASE_GLYPHS",
    "NPHASE_LABELS",
    "ColonyDashboard",
    "ColonyState",
    "TownPhase",
    "ActivityBuffer",
    "ColonyDashboardBridge",
    "create_bridge_and_dashboard",
    # Meta
    "__version__",
]
