"""
Pilots: Pre-configured widget demonstrations with override hooks.

A Pilot is a complete demonstration scenario for a widget:
- Pre-configured state showcasing the widget's capabilities
- Override hooks for developer customization
- Multiple variations (normal, error, edge cases)

Each pilot answers: "What does this widget look like in practice?"

The pilot system is designed for:
1. Gallery browsing (see all widgets at once)
2. Focused iteration (zoom in on one widget)
3. Edge case exploration (entropy, errors, refusals)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, TypeVar

from agents.i.reactive.widget import KgentsWidget, RenderTarget

T = TypeVar("T")


class PilotCategory(Enum):
    """Categories for organizing pilots in the gallery."""

    PRIMITIVES = auto()  # Glyph, Bar, Sparkline
    CARDS = auto()  # AgentCard, YieldCard, CitizenCard
    CHROME = auto()  # ErrorPanel, RefusalPanel, CachedBadge
    STREAMING = auto()  # StreamState, Backpressure, Progress
    COMPOSITION = auto()  # HStack, VStack, CompositeWidget
    ADAPTERS = auto()  # Textual, Marimo adapters
    SPECIALIZED = auto()  # DensityField, DialecticCard, ShadowCard
    # Gallery V2 categories (AD-009 Vertical Slice)
    POLYNOMIAL = auto()  # State machine visualizations
    OPERAD = auto()  # Composition grammar with laws
    CROWN_JEWELS = auto()  # Full vertical slice mini-demos
    LAYOUT = auto()  # Design Language System components
    INTERACTIVE = auto()  # Flagship interactive pilots


@dataclass
class Pilot:
    """
    A pre-configured widget demonstration.

    Attributes:
        name: Unique identifier (e.g., "glyph_active", "agent_card_error")
        category: Gallery category for organization
        description: One-line description of what this pilot shows
        widget_factory: Callable that creates the widget with optional overrides
        variations: Alternative states to cycle through (for interactive mode)
        tags: Searchable tags (e.g., ["error", "streaming", "entropy"])
    """

    name: str
    category: PilotCategory
    description: str
    widget_factory: Callable[[dict[str, Any]], KgentsWidget[Any]]
    variations: list[dict[str, Any]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def create_widget(self, overrides: dict[str, Any] | None = None) -> KgentsWidget[Any]:
        """Create the widget with optional overrides."""
        return self.widget_factory(overrides or {})

    def render(self, target: RenderTarget, overrides: dict[str, Any] | None = None) -> Any:
        """Create and immediately render the widget."""
        widget = self.create_widget(overrides)
        return widget.project(target)


# Global pilot registry
PILOT_REGISTRY: dict[str, Pilot] = {}


def register_pilot(pilot: Pilot) -> Pilot:
    """Register a pilot in the global registry."""
    PILOT_REGISTRY[pilot.name] = pilot
    return pilot


def _get_time(overrides: dict[str, Any]) -> float:
    """Get time from overrides or current time."""
    if "time_ms" in overrides and overrides["time_ms"] is not None:
        return overrides["time_ms"]
    return time.time() * 1000


def _get_entropy(overrides: dict[str, Any], default: float = 0.0) -> float:
    """Get entropy from overrides or default."""
    if "entropy" in overrides and overrides["entropy"] is not None:
        return max(0.0, min(1.0, overrides["entropy"]))
    return default


def _get_seed(overrides: dict[str, Any], default: int = 42) -> int:
    """Get seed from overrides or default."""
    if "seed" in overrides and overrides["seed"] is not None:
        return overrides["seed"]
    return default


# =============================================================================
# PRIMITIVES: Glyph, Bar, Sparkline
# =============================================================================


def _create_glyph_idle(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

    return GlyphWidget(
        GlyphState(
            phase="idle",
            entropy=_get_entropy(overrides),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
        )
    )


register_pilot(
    Pilot(
        name="glyph_idle",
        category=PilotCategory.PRIMITIVES,
        description="Glyph in idle phase - the atomic visual unit at rest",
        widget_factory=_create_glyph_idle,
        tags=["glyph", "idle", "atomic"],
    )
)


def _create_glyph_active(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

    return GlyphWidget(
        GlyphState(
            phase="active",
            entropy=_get_entropy(overrides, 0.1),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
            animate="breathe",
        )
    )


register_pilot(
    Pilot(
        name="glyph_active",
        category=PilotCategory.PRIMITIVES,
        description="Glyph in active phase - breathing animation",
        widget_factory=_create_glyph_active,
        tags=["glyph", "active", "animation"],
    )
)


def _create_glyph_error(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

    return GlyphWidget(
        GlyphState(
            phase="error",
            entropy=_get_entropy(overrides, 0.6),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
            fg="#dc3545",
        )
    )


register_pilot(
    Pilot(
        name="glyph_error",
        category=PilotCategory.PRIMITIVES,
        description="Glyph in error phase - high entropy, red color",
        widget_factory=_create_glyph_error,
        tags=["glyph", "error", "entropy"],
    )
)


def _create_glyph_entropy_sweep(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create a glyph at the specified entropy level."""
    from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

    return GlyphWidget(
        GlyphState(
            char="*",
            phase="active",
            entropy=_get_entropy(overrides, 0.5),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
        )
    )


register_pilot(
    Pilot(
        name="glyph_entropy_sweep",
        category=PilotCategory.PRIMITIVES,
        description="Glyph with customizable entropy (use --entropy to explore)",
        widget_factory=_create_glyph_entropy_sweep,
        variations=[
            {"entropy": 0.0},
            {"entropy": 0.2},
            {"entropy": 0.4},
            {"entropy": 0.6},
            {"entropy": 0.8},
            {"entropy": 1.0},
        ],
        tags=["glyph", "entropy", "sweep", "interactive"],
    )
)


def _create_bar_solid(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.bar import BarState, BarWidget

    return BarWidget(
        BarState(
            value=overrides.get("value", 0.75),
            width=overrides.get("width", 20),
            style="solid",
            label="Capacity",
            entropy=_get_entropy(overrides),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
        )
    )


register_pilot(
    Pilot(
        name="bar_solid",
        category=PilotCategory.PRIMITIVES,
        description="Solid bar at 75% - classic progress indicator",
        widget_factory=_create_bar_solid,
        tags=["bar", "solid", "progress"],
    )
)


def _create_bar_gradient(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.bar import BarState, BarWidget

    return BarWidget(
        BarState(
            value=overrides.get("value", 0.9),
            width=overrides.get("width", 20),
            style="gradient",
            label="Health",
            entropy=_get_entropy(overrides),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
        )
    )


register_pilot(
    Pilot(
        name="bar_gradient",
        category=PilotCategory.PRIMITIVES,
        description="Gradient bar at 90% - health/resource indicator",
        widget_factory=_create_bar_gradient,
        tags=["bar", "gradient", "health"],
    )
)


def _create_bar_value_sweep(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.bar import BarState, BarWidget

    return BarWidget(
        BarState(
            value=overrides.get("value", 0.5),
            width=20,
            style="solid",
            label="Level",
            entropy=_get_entropy(overrides),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
        )
    )


register_pilot(
    Pilot(
        name="bar_value_sweep",
        category=PilotCategory.PRIMITIVES,
        description="Bar with customizable value (use --value to explore)",
        widget_factory=_create_bar_value_sweep,
        variations=[
            {"value": 0.0},
            {"value": 0.25},
            {"value": 0.5},
            {"value": 0.75},
            {"value": 1.0},
        ],
        tags=["bar", "sweep", "interactive"],
    )
)


def _create_sparkline_rising(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget

    values = tuple(i / 20 for i in range(20))
    return SparklineWidget(
        SparklineState(
            values=values,
            label="Rising",
            max_length=20,
            entropy=_get_entropy(overrides),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
        )
    )


register_pilot(
    Pilot(
        name="sparkline_rising",
        category=PilotCategory.PRIMITIVES,
        description="Rising sparkline - linear growth pattern",
        widget_factory=_create_sparkline_rising,
        tags=["sparkline", "trend", "rising"],
    )
)


def _create_sparkline_volatile(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget

    values = (0.8, 0.3, 0.9, 0.2, 0.7, 0.4, 0.8, 0.1, 0.9, 0.5, 0.6, 0.3, 0.8, 0.4, 0.7)
    return SparklineWidget(
        SparklineState(
            values=values,
            label="Volatile",
            max_length=20,
            entropy=_get_entropy(overrides, 0.2),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
        )
    )


register_pilot(
    Pilot(
        name="sparkline_volatile",
        category=PilotCategory.PRIMITIVES,
        description="Volatile sparkline - erratic pattern with entropy",
        widget_factory=_create_sparkline_volatile,
        tags=["sparkline", "volatile", "entropy"],
    )
)


# =============================================================================
# CARDS: AgentCard, YieldCard, CitizenCard
# =============================================================================


def _create_agent_card_active(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget

    return AgentCardWidget(
        AgentCardState(
            agent_id="pilot-agent-1",
            name=overrides.get("name", "Active Agent"),
            phase=overrides.get("phase", "active"),
            activity=(0.3, 0.5, 0.7, 0.8, 0.6, 0.9, 0.7, 0.8),
            capability=overrides.get("capability", 0.85),
            entropy=_get_entropy(overrides, 0.05),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
            style=overrides.get("style", "full"),
            breathing=overrides.get("breathing", True),
        )
    )


register_pilot(
    Pilot(
        name="agent_card_active",
        category=PilotCategory.CARDS,
        description="Active agent card - full style with breathing animation",
        widget_factory=_create_agent_card_active,
        tags=["card", "agent", "active", "breathing"],
    )
)


def _create_agent_card_error(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget

    return AgentCardWidget(
        AgentCardState(
            agent_id="pilot-agent-error",
            name="Failing Agent",
            phase="error",
            activity=(0.9, 0.1, 0.8, 0.05, 0.7, 0.02, 0.5, 0.01),
            capability=0.2,
            entropy=_get_entropy(overrides, 0.6),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
            style="full",
            breathing=False,
        )
    )


register_pilot(
    Pilot(
        name="agent_card_error",
        category=PilotCategory.CARDS,
        description="Agent in error state - high entropy, declining activity",
        widget_factory=_create_agent_card_error,
        tags=["card", "agent", "error", "entropy"],
    )
)


def _create_agent_card_compact(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget

    return AgentCardWidget(
        AgentCardState(
            agent_id="pilot-compact",
            name="Compact View",
            phase="waiting",
            activity=(0.4, 0.5, 0.4, 0.5, 0.4),
            capability=0.7,
            entropy=_get_entropy(overrides),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
            style="compact",
            breathing=False,
        )
    )


register_pilot(
    Pilot(
        name="agent_card_compact",
        category=PilotCategory.CARDS,
        description="Compact agent card - minimal footprint",
        widget_factory=_create_agent_card_compact,
        tags=["card", "agent", "compact"],
    )
)


def _create_agent_card_minimal(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget

    return AgentCardWidget(
        AgentCardState(
            agent_id="pilot-minimal",
            name="Minimal Agent",
            phase="idle",
            activity=(),
            capability=1.0,
            entropy=_get_entropy(overrides),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
            style="minimal",
        )
    )


register_pilot(
    Pilot(
        name="agent_card_minimal",
        category=PilotCategory.CARDS,
        description="Minimal agent card - just glyph and name",
        widget_factory=_create_agent_card_minimal,
        tags=["card", "agent", "minimal"],
    )
)


def _create_yield_card(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.yield_card import YieldCardState, YieldCardWidget

    return YieldCardWidget(
        YieldCardState(
            yield_id="pilot-yield-1",
            content=overrides.get("content", "This is a yielded result from an agent operation."),
            source_agent="source-agent",
            yield_type="action",
            importance=overrides.get("importance", 0.8),
            entropy=_get_entropy(overrides, 0.05),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
        )
    )


register_pilot(
    Pilot(
        name="yield_card",
        category=PilotCategory.CARDS,
        description="Yield card - agent output with confidence",
        widget_factory=_create_yield_card,
        tags=["card", "yield", "output"],
    )
)


# =============================================================================
# CHROME: ErrorPanel, RefusalPanel, CachedBadge
# =============================================================================


def _create_error_panel_network(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create an error panel (not a KgentsWidget, but renders similarly)."""
    from protocols.projection.chrome import ErrorPanel
    from protocols.projection.schema import ErrorInfo

    error = ErrorInfo(
        category="network",
        code="ECONNREFUSED",
        message="Connection refused to backend service",
        retry_after_seconds=30,
        fallback_action="Check if the server is running",
        trace_id="trace-abc123",
    )
    return _ChromeWrapper("error_panel", ErrorPanel(error))


def _create_error_panel_timeout(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from protocols.projection.chrome import ErrorPanel
    from protocols.projection.schema import ErrorInfo

    error = ErrorInfo(
        category="timeout",
        code="ETIMEDOUT",
        message="Request timed out after 30s",
        retry_after_seconds=5,
    )
    return _ChromeWrapper("error_panel_timeout", ErrorPanel(error))


def _create_refusal_panel(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from protocols.projection.chrome import RefusalPanel
    from protocols.projection.schema import RefusalInfo

    refusal = RefusalInfo(
        reason="This action requires explicit consent due to its irreversible nature.",
        consent_required="destructive_write",
        appeal_to="self.soul.appeal",
        override_cost=50.0,
    )
    return _ChromeWrapper("refusal_panel", RefusalPanel(refusal))


def _create_cached_badge(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from protocols.projection.chrome import CachedBadge

    # 15 minutes = 900 seconds
    return _ChromeWrapper(
        "cached_badge", CachedBadge(age_seconds=900, show_age=True, deterministic=True)
    )


class _ChromeWrapper(KgentsWidget[None]):
    """Wrapper to make chrome components behave like KgentsWidgets for the gallery."""

    def __init__(self, name: str, component: Any) -> None:
        self._name = name
        self._component = component

    def project(self, target: RenderTarget) -> Any:
        # Chrome components extend KgentsWidget, so use project() directly
        return self._component.project(target)


register_pilot(
    Pilot(
        name="error_panel_network",
        category=PilotCategory.CHROME,
        description="Network error panel - connection refused with retry",
        widget_factory=_create_error_panel_network,
        tags=["chrome", "error", "network"],
    )
)

register_pilot(
    Pilot(
        name="error_panel_timeout",
        category=PilotCategory.CHROME,
        description="Timeout error panel - request timeout",
        widget_factory=_create_error_panel_timeout,
        tags=["chrome", "error", "timeout"],
    )
)

register_pilot(
    Pilot(
        name="refusal_panel",
        category=PilotCategory.CHROME,
        description="Refusal panel - consent required for destructive action",
        widget_factory=_create_refusal_panel,
        tags=["chrome", "refusal", "consent"],
    )
)

register_pilot(
    Pilot(
        name="cached_badge",
        category=PilotCategory.CHROME,
        description="Cached badge - stale data indicator",
        widget_factory=_create_cached_badge,
        tags=["chrome", "cache", "stale"],
    )
)


# =============================================================================
# STREAMING: Progress, StreamState
# =============================================================================


def _create_progress_determinate(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from protocols.projection.widgets import ProgressWidget, ProgressWidgetState

    progress = overrides.get("value", 0.65)

    return ProgressWidget(
        ProgressWidgetState(
            value=progress,
            label="Downloading",
            show_percentage=True,
        )
    )


def _create_progress_indeterminate(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from protocols.projection.widgets import (
        ProgressVariant,
        ProgressWidget,
        ProgressWidgetState,
    )

    return ProgressWidget(
        ProgressWidgetState(
            value=-1,  # Indeterminate
            variant=ProgressVariant.INDETERMINATE,
            label="Processing",
            show_percentage=False,
        )
    )


class _WidgetStateWrapper(KgentsWidget[None]):
    """Wrapper for widget states that aren't full KgentsWidgets."""

    def __init__(self, name: str, state: Any) -> None:
        self._name = name
        self._state = state

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return self._render_cli()
            case RenderTarget.JSON:
                return (
                    self._state.__dict__ if hasattr(self._state, "__dict__") else str(self._state)
                )
            case _:
                return str(self._state)

    def _render_cli(self) -> str:
        state = self._state
        if hasattr(state, "progress"):
            if state.progress < 0:
                return f"[{state.label}] ... (indeterminate)"
            pct = int(state.progress * 100)
            bar_filled = int(state.progress * 20)
            bar = "#" * bar_filled + "-" * (20 - bar_filled)
            return f"[{state.label}] [{bar}] {pct}%"
        return str(state)


register_pilot(
    Pilot(
        name="progress_determinate",
        category=PilotCategory.STREAMING,
        description="Determinate progress bar - 65% complete with ETA",
        widget_factory=_create_progress_determinate,
        variations=[
            {"progress": 0.0},
            {"progress": 0.25},
            {"progress": 0.5},
            {"progress": 0.75},
            {"progress": 1.0},
        ],
        tags=["streaming", "progress", "determinate"],
    )
)

register_pilot(
    Pilot(
        name="progress_indeterminate",
        category=PilotCategory.STREAMING,
        description="Indeterminate progress - unknown total",
        widget_factory=_create_progress_indeterminate,
        tags=["streaming", "progress", "indeterminate"],
    )
)


# =============================================================================
# SPECIALIZED: DensityField, DialecticCard, ShadowCard
# =============================================================================


def _create_density_field(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.density_field import (
        DensityFieldState,
        DensityFieldWidget,
        Entity,
        Wind,
    )

    # Entities use integer x, y coordinates
    entities = tuple(
        Entity(
            id=f"entity-{i}",
            x=5 + i * 6,
            y=3 + (i % 3) * 3,
            char=["K", "A", "M", "E"][i % 4],
            phase="active",
            heat=0.5,
        )
        for i in range(5)
    )

    return DensityFieldWidget(
        DensityFieldState(
            entities=entities,
            wind=Wind(dx=0.1, dy=0.05, strength=0.3),
            base_entropy=_get_entropy(overrides, 0.1),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
            width=40,
            height=12,
        )
    )


register_pilot(
    Pilot(
        name="density_field",
        category=PilotCategory.SPECIALIZED,
        description="Density field - 2D spatial visualization with entities",
        widget_factory=_create_density_field,
        tags=["specialized", "density", "spatial", "entities"],
    )
)


def _create_shadow_card(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.hgent_card import (
        ShadowCardState,
        ShadowCardWidget,
        ShadowItem,
    )

    # ShadowItem uses content, exclusion_reason, difficulty
    items = [
        ShadowItem(
            content="capacity for harm",
            exclusion_reason="helpful identity",
            difficulty="high",
        ),
        ShadowItem(
            content="tendency to guess",
            exclusion_reason="accuracy identity",
            difficulty="medium",
        ),
        ShadowItem(
            content="impatience with confusion",
            exclusion_reason="patience identity",
            difficulty="low",
        ),
    ]

    return ShadowCardWidget(
        ShadowCardState(
            title="K-gent Shadow Analysis",
            shadow_inventory=tuple(items),
            balance=0.4,
            entropy=_get_entropy(overrides),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
        )
    )


register_pilot(
    Pilot(
        name="shadow_card",
        category=PilotCategory.SPECIALIZED,
        description="Shadow card - H-gent introspection visualization",
        widget_factory=_create_shadow_card,
        tags=["specialized", "shadow", "introspection", "hgent"],
    )
)


def _create_dialectic_card(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.primitives.hgent_card import (
        DialecticCardState,
        DialecticCardWidget,
    )

    # DialecticCardState uses thesis, antithesis, synthesis, productive_tension, sublation_notes
    productive_tension = overrides.get("productive_tension", False)

    return DialecticCardWidget(
        DialecticCardState(
            thesis="The agent should maximize user productivity.",
            antithesis="The agent should prioritize user wellbeing over productivity.",
            synthesis=None
            if productive_tension
            else "Balance productivity with sustainable work patterns.",
            productive_tension=productive_tension,
            sublation_notes="Speed when exploring, thorough when shipping."
            if not productive_tension
            else "",
            entropy=_get_entropy(overrides),
            seed=_get_seed(overrides),
            t=_get_time(overrides),
        )
    )


register_pilot(
    Pilot(
        name="dialectic_card",
        category=PilotCategory.SPECIALIZED,
        description="Dialectic card - thesis/antithesis/synthesis reasoning",
        widget_factory=_create_dialectic_card,
        tags=["specialized", "dialectic", "reasoning", "hgent"],
    )
)


# =============================================================================
# COMPOSITION: HStack, VStack
# =============================================================================


def _create_hstack_glyphs(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.composable import HStack
    from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

    phases = ["idle", "active", "waiting", "error", "complete"]
    glyphs = [
        GlyphWidget(
            GlyphState(
                phase=phase,
                entropy=_get_entropy(overrides),
                seed=_get_seed(overrides) + i,
                t=_get_time(overrides),
            )
        )
        for i, phase in enumerate(phases)
    ]

    return HStack(glyphs)


register_pilot(
    Pilot(
        name="hstack_glyphs",
        category=PilotCategory.COMPOSITION,
        description="HStack of glyphs - all phases side by side",
        widget_factory=_create_hstack_glyphs,
        tags=["composition", "hstack", "glyph", "phases"],
    )
)


def _create_vstack_bars(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    from agents.i.reactive.composable import VStack
    from agents.i.reactive.primitives.bar import BarState, BarWidget

    levels = [0.2, 0.5, 0.8, 1.0]
    labels = ["Low", "Medium", "High", "Full"]

    bars = [
        BarWidget(
            BarState(
                value=level,
                width=15,
                style="solid",
                label=label,
                entropy=_get_entropy(overrides),
                seed=_get_seed(overrides) + i,
                t=_get_time(overrides),
            )
        )
        for i, (level, label) in enumerate(zip(levels, labels))
    ]

    return VStack(bars)


register_pilot(
    Pilot(
        name="vstack_bars",
        category=PilotCategory.COMPOSITION,
        description="VStack of bars - stacked progress indicators",
        widget_factory=_create_vstack_bars,
        tags=["composition", "vstack", "bar", "stacked"],
    )
)


# =============================================================================
# Helpers
# =============================================================================


def get_pilots_by_category(category: PilotCategory) -> list[Pilot]:
    """Get all pilots in a category."""
    return [p for p in PILOT_REGISTRY.values() if p.category == category]


def get_pilots_by_tag(tag: str) -> list[Pilot]:
    """Get all pilots with a specific tag."""
    return [p for p in PILOT_REGISTRY.values() if tag in p.tags]


def list_all_pilots() -> list[str]:
    """List all registered pilot names."""
    return list(PILOT_REGISTRY.keys())


# =============================================================================
# POLYNOMIAL: State Machine Visualizations (Gallery V2)
# =============================================================================


def _create_gallery_polynomial(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create a gallery polynomial visualization widget."""
    from agents.gallery import gallery_visualization

    viz = gallery_visualization()
    return _PolynomialVizWidget("gallery_polynomial", viz)


class _PolynomialVizWidget(KgentsWidget[None]):
    """Widget wrapper for polynomial visualizations."""

    def __init__(self, name: str, viz: dict[str, Any]) -> None:
        self._name = name
        self._viz = viz

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return self._render_cli()
            case RenderTarget.JSON:
                return self._viz
            case _:
                return self._render_html()

    def _render_cli(self) -> str:
        lines = [
            f"[Polynomial] {self._viz['name']}",
            f"Positions: {len(self._viz['positions'])}",
            f"Edges: {len(self._viz['edges'])}",
            f"Current: {self._viz['current']}",
            "",
        ]
        for pos in self._viz["positions"]:
            marker = ">" if pos["is_current"] else " "
            lines.append(f"{marker} {pos['id']}: {pos['description']}")
        return "\n".join(lines)

    def _render_html(self) -> str:
        positions = "".join(
            f'<div class="poly-pos {"active" if p["is_current"] else ""}">{p["id"]}</div>'
            for p in self._viz["positions"]
        )
        return f"""
        <div class="polynomial-viz">
            <h3>{self._viz["name"]}</h3>
            <div class="positions">{positions}</div>
        </div>
        """


register_pilot(
    Pilot(
        name="gallery_polynomial",
        category=PilotCategory.POLYNOMIAL,
        description="GalleryPolynomial - state machine for gallery navigation",
        widget_factory=_create_gallery_polynomial,
        tags=["polynomial", "state-machine", "gallery", "categorical"],
    )
)


def _create_citizen_polynomial(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create a citizen polynomial visualization widget."""
    viz = {
        "id": "citizen",
        "name": "CitizenPolynomial",
        "positions": [
            {
                "id": "IDLE",
                "label": "Idle",
                "description": "At rest",
                "is_current": True,
                "is_terminal": False,
                "color": "#64748b",
            },
            {
                "id": "SOCIALIZING",
                "label": "Socializing",
                "description": "Interacting",
                "is_current": False,
                "is_terminal": False,
                "color": "#3b82f6",
            },
            {
                "id": "WORKING",
                "label": "Working",
                "description": "Task focus",
                "is_current": False,
                "is_terminal": False,
                "color": "#f59e0b",
            },
            {
                "id": "REFLECTING",
                "label": "Reflecting",
                "description": "Self-analysis",
                "is_current": False,
                "is_terminal": False,
                "color": "#8b5cf6",
            },
            {
                "id": "RESTING",
                "label": "Resting",
                "description": "Recovery",
                "is_current": False,
                "is_terminal": False,
                "color": "#22c55e",
            },
        ],
        "edges": [
            {
                "source": "IDLE",
                "target": "SOCIALIZING",
                "label": "greet",
                "is_valid": True,
            },
            {"source": "IDLE", "target": "WORKING", "label": "task", "is_valid": True},
            {
                "source": "SOCIALIZING",
                "target": "WORKING",
                "label": "focus",
                "is_valid": True,
            },
            {
                "source": "WORKING",
                "target": "REFLECTING",
                "label": "complete",
                "is_valid": True,
            },
            {
                "source": "REFLECTING",
                "target": "RESTING",
                "label": "tired",
                "is_valid": True,
            },
            {
                "source": "RESTING",
                "target": "IDLE",
                "label": "refresh",
                "is_valid": True,
            },
        ],
        "current": "IDLE",
        "valid_directions": ["greet", "task"],
        "history": [],
        "metadata": {"spec": "spec/town/citizen-polynomial.md"},
    }
    return _PolynomialVizWidget("citizen_polynomial", viz)


register_pilot(
    Pilot(
        name="citizen_polynomial",
        category=PilotCategory.POLYNOMIAL,
        description="CitizenPolynomial - Agent Town citizen life cycle",
        widget_factory=_create_citizen_polynomial,
        tags=["polynomial", "state-machine", "town", "citizen"],
    )
)


# =============================================================================
# OPERAD: Composition Grammar Visualizations (Gallery V2)
# =============================================================================


def _create_gallery_operad(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create a gallery operad visualization widget."""
    from agents.gallery.operad import gallery_operad_visualization

    viz = gallery_operad_visualization()
    return _OperadVizWidget("gallery_operad", viz)


class _OperadVizWidget(KgentsWidget[None]):
    """Widget wrapper for operad visualizations."""

    def __init__(self, name: str, viz: dict[str, Any]) -> None:
        self._name = name
        self._viz = viz

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return self._render_cli()
            case RenderTarget.JSON:
                return self._viz
            case _:
                return self._render_html()

    def _render_cli(self) -> str:
        lines = [
            f"[Operad] {self._viz['name']}",
            f"Operations: {len(self._viz['operations'])}",
            f"Laws: {len(self._viz['laws'])}",
            "",
        ]
        for op in self._viz["operations"][:4]:  # Show first 4
            lines.append(f"  {op['name']}: {op['signature']}")
        if len(self._viz["operations"]) > 4:
            lines.append(f"  ... and {len(self._viz['operations']) - 4} more")
        lines.append("")
        lines.append("Laws:")
        for law in self._viz["laws"]:
            lines.append(f"  {law['name']}: {law['equation']}")
        return "\n".join(lines)

    def _render_html(self) -> str:
        ops = "".join(
            f'<div class="op">{op["name"]} ({op["arity"]})</div>' for op in self._viz["operations"]
        )
        laws = "".join(f'<div class="law">{law["equation"]}</div>' for law in self._viz["laws"])
        return f"""
        <div class="operad-viz">
            <h3>{self._viz["name"]}</h3>
            <div class="operations">{ops}</div>
            <div class="laws">{laws}</div>
        </div>
        """


register_pilot(
    Pilot(
        name="gallery_operad",
        category=PilotCategory.OPERAD,
        description="GALLERY_OPERAD - composition grammar for gallery operations",
        widget_factory=_create_gallery_operad,
        tags=["operad", "composition", "gallery", "categorical"],
    )
)


def _create_town_operad(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create a town operad visualization widget."""
    viz = {
        "name": "TOWN_OPERAD",
        "description": "Grammar of citizen interactions in Agent Town",
        "operations": [
            {
                "name": "greet",
                "arity": 2,
                "signature": "Citizen × Citizen → Relationship",
                "description": "Initiate relationship",
            },
            {
                "name": "gossip",
                "arity": 2,
                "signature": "Citizen × Citizen → Information",
                "description": "Share information",
            },
            {
                "name": "trade",
                "arity": 2,
                "signature": "Citizen × Citizen → Exchange",
                "description": "Exchange resources",
            },
            {
                "name": "solo",
                "arity": 1,
                "signature": "Citizen → Reflection",
                "description": "Solo activity",
            },
            {
                "name": "dispute",
                "arity": 2,
                "signature": "Citizen × Citizen → Conflict",
                "description": "Resolve tension",
            },
            {
                "name": "celebrate",
                "arity": 3,
                "signature": "Citizen × Citizen × Citizen → Event",
                "description": "Group celebration",
            },
            {
                "name": "mourn",
                "arity": 2,
                "signature": "Citizen × Citizen → Grief",
                "description": "Shared loss",
            },
            {
                "name": "teach",
                "arity": 2,
                "signature": "Citizen × Citizen → Knowledge",
                "description": "Transfer skill",
            },
        ],
        "laws": [
            {
                "name": "locality",
                "equation": "greet(a,b) affects only neighbors of a,b",
                "description": "Operations are local",
            },
            {
                "name": "rest_inviolability",
                "equation": "RESTING only accepts wake",
                "description": "Rest cannot be interrupted",
            },
            {
                "name": "coherence",
                "equation": "ops preserve sheaf gluing",
                "description": "Operations maintain coherence",
            },
        ],
    }
    return _OperadVizWidget("town_operad", viz)


register_pilot(
    Pilot(
        name="town_operad",
        category=PilotCategory.OPERAD,
        description="TOWN_OPERAD - grammar of Agent Town citizen interactions",
        widget_factory=_create_town_operad,
        tags=["operad", "composition", "town", "citizens"],
    )
)


# =============================================================================
# CROWN_JEWELS: Vertical Slice Mini-Demos (Gallery V2)
# =============================================================================


def _create_town_mini(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create an Agent Town mini-demo widget with rich citizen visualization."""
    # Citizen data: (char, phase, name, archetype)
    citizens = [
        ("K", "active", "Socrates", "Scholar"),
        ("H", "working", "Hypatia", "Builder"),
        ("M", "reflecting", "Marcus", "Watcher"),
        ("A", "idle", "Ada", "Builder"),
        ("L", "resting", "Leonardo", "Healer"),
    ]

    return _TownMiniWidget(
        "town_mini",
        citizens,
        {
            "crown_jewel": "Agent Town",
            "polynomial": "CITIZEN_POLYNOMIAL",
            "operad": "TOWN_OPERAD",
            "route": "/town",
            "path": "world.town.manifest",
        },
    )


# Phase colors for town mini visualization
PHASE_COLORS = {
    "idle": "#64748b",  # slate
    "active": "#22c55e",  # green
    "socializing": "#ec4899",  # pink
    "working": "#f59e0b",  # amber
    "reflecting": "#8b5cf6",  # purple
    "resting": "#3b82f6",  # blue
}

PHASE_GLYPHS = {
    "idle": "○",
    "active": "◉",
    "socializing": "◎",
    "working": "◆",
    "reflecting": "◇",
    "resting": "◐",
}


class _TownMiniWidget(KgentsWidget[None]):
    """Rich mini-demo widget for Agent Town with interactive citizen grid."""

    def __init__(
        self,
        name: str,
        citizens: list[tuple[str, str, str, str]],
        metadata: dict[str, Any],
    ) -> None:
        self._name = name
        self._citizens = citizens
        self._metadata = metadata

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return self._render_cli()
            case RenderTarget.JSON:
                return self._render_json()
            case RenderTarget.MARIMO | RenderTarget.TUI:
                return self._render_html()
            case _:
                return self._render_html()

    def _render_cli(self) -> str:
        lines = [
            f"[Crown Jewel] {self._metadata['crown_jewel']}",
            f"Path: {self._metadata['path']}",
            "",
        ]
        for char, phase, name, archetype in self._citizens:
            glyph = PHASE_GLYPHS.get(phase, "?")
            lines.append(f"  {glyph} {name:<12} [{phase.upper()}] - {archetype}")
        lines.append("")
        lines.append(f"→ Visit {self._metadata['route']} for full experience")
        return "\n".join(lines)

    def _render_json(self) -> dict[str, Any]:
        return {
            "metadata": self._metadata,
            "citizens": [
                {
                    "char": char,
                    "phase": phase,
                    "name": name,
                    "archetype": archetype,
                    "color": PHASE_COLORS.get(phase, "#64748b"),
                }
                for char, phase, name, archetype in self._citizens
            ],
        }

    def _render_html(self) -> str:
        # Build citizen cards grid
        cards = []
        for char, phase, name, archetype in self._citizens:
            color = PHASE_COLORS.get(phase, "#64748b")
            glyph = PHASE_GLYPHS.get(phase, "?")
            card = f"""
            <div class="citizen-mini-card" style="
                background: linear-gradient(135deg, {color}15, {color}05);
                border: 1px solid {color}40;
                border-radius: 8px;
                padding: 12px;
                min-width: 120px;
                transition: all 0.2s ease;
            ">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <span style="
                        font-size: 20px;
                        color: {color};
                        text-shadow: 0 0 8px {color}60;
                    ">{glyph}</span>
                    <span style="
                        font-weight: 600;
                        color: #e2e8f0;
                        font-size: 14px;
                    ">{name}</span>
                </div>
                <div style="
                    font-size: 11px;
                    color: {color};
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 2px;
                ">{phase}</div>
                <div style="
                    font-size: 10px;
                    color: #94a3b8;
                ">{archetype}</div>
            </div>
            """
            cards.append(card)

        cards_html = "".join(cards)

        return f"""
        <div class="town-mini-demo" style="
            background: #0f172a;
            border-radius: 12px;
            padding: 16px;
            font-family: system-ui, -apple-system, sans-serif;
        ">
            <div style="
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 12px;
                padding-bottom: 8px;
                border-bottom: 1px solid #1e293b;
            ">
                <div>
                    <h4 style="
                        color: #f8fafc;
                        font-size: 16px;
                        font-weight: 600;
                        margin: 0 0 4px 0;
                    ">♦ {self._metadata["crown_jewel"]}</h4>
                    <div style="
                        font-size: 11px;
                        color: #64748b;
                        font-family: monospace;
                    ">{self._metadata["path"]}</div>
                </div>
                <a href="{self._metadata["route"]}" style="
                    background: #3b82f6;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    text-decoration: none;
                    font-weight: 500;
                ">Open Full App →</a>
            </div>

            <div style="
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                margin-bottom: 12px;
            ">
                {cards_html}
            </div>

            <div style="
                display: flex;
                gap: 16px;
                font-size: 10px;
                color: #64748b;
                padding-top: 8px;
                border-top: 1px solid #1e293b;
            ">
                <span>◉ Polynomial: <span style="color: #14b8a6">{self._metadata["polynomial"]}</span></span>
                <span>⊛ Operad: <span style="color: #a855f7">{self._metadata["operad"]}</span></span>
            </div>
        </div>
        """


class _CrownJewelMiniWidget(KgentsWidget[None]):
    """Wrapper for Crown Jewel mini-demos."""

    def __init__(self, name: str, inner: KgentsWidget[Any], metadata: dict[str, Any]) -> None:
        self._name = name
        self._inner = inner
        self._metadata = metadata

    def project(self, target: RenderTarget) -> Any:
        inner_content = self._inner.project(target)
        match target:
            case RenderTarget.CLI:
                return (
                    f"[Crown Jewel] {self._metadata['crown_jewel']}\n"
                    f"Polynomial: {self._metadata['polynomial']}\n"
                    f"Operad: {self._metadata['operad']}\n"
                    f"Path: {self._metadata['path']}\n\n"
                    f"{inner_content}"
                )
            case RenderTarget.JSON:
                return {
                    "metadata": self._metadata,
                    "content": inner_content
                    if isinstance(inner_content, dict)
                    else str(inner_content),
                }
            case _:
                return f"""
                <div class="crown-jewel-mini">
                    <h4>{self._metadata["crown_jewel"]}</h4>
                    <div class="meta">Path: {self._metadata["path"]}</div>
                    <div class="content">{inner_content}</div>
                </div>
                """


register_pilot(
    Pilot(
        name="town_mini",
        category=PilotCategory.CROWN_JEWELS,
        description="Agent Town - citizen grid mini-demo",
        widget_factory=_create_town_mini,
        tags=["crown-jewel", "town", "citizens", "mini-demo"],
    )
)


# =============================================================================
# LAYOUT: Design Language System Components (Gallery V2)
# =============================================================================


def _create_elastic_split_demo(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create an elastic split layout demo widget."""
    return _LayoutDemoWidget(
        "elastic_split",
        {
            "component": "ElasticSplit",
            "description": "Density-adaptive split layout",
            "modes": ["compact", "comfortable", "spacious"],
            "laws": ["min_collapse", "max_expand", "ratio_preserve"],
        },
    )


class _LayoutDemoWidget(KgentsWidget[None]):
    """Widget wrapper for layout component demos."""

    def __init__(self, name: str, info: dict[str, Any]) -> None:
        self._name = name
        self._info = info

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return (
                    f"[Layout] {self._info['component']}\n"
                    f"{self._info['description']}\n"
                    f"Modes: {', '.join(self._info['modes'])}\n"
                    f"Laws: {', '.join(self._info['laws'])}"
                )
            case RenderTarget.JSON:
                return self._info
            case _:
                return f"""
                <div class="layout-demo">
                    <h4>{self._info["component"]}</h4>
                    <p>{self._info["description"]}</p>
                </div>
                """


register_pilot(
    Pilot(
        name="elastic_split",
        category=PilotCategory.LAYOUT,
        description="ElasticSplit - density-adaptive layout primitive",
        widget_factory=_create_elastic_split_demo,
        tags=["layout", "elastic", "density", "design-system"],
    )
)


def _create_bottom_drawer_demo(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create a bottom drawer layout demo widget."""
    return _LayoutDemoWidget(
        "bottom_drawer",
        {
            "component": "BottomDrawer",
            "description": "Mobile-friendly drawer from bottom edge",
            "modes": ["collapsed", "peek", "expanded"],
            "laws": ["content_preserve", "touch_target_min"],
        },
    )


register_pilot(
    Pilot(
        name="bottom_drawer",
        category=PilotCategory.LAYOUT,
        description="BottomDrawer - mobile-first drawer component",
        widget_factory=_create_bottom_drawer_demo,
        tags=["layout", "drawer", "mobile", "design-system"],
    )
)


# =============================================================================
# INTERACTIVE: Flagship Interactive Pilots (Gallery V2)
# =============================================================================

# Preset polynomial definitions for the playground
POLYNOMIAL_PRESETS = {
    "traffic_light": {
        "name": "Traffic Light",
        "description": "Classic state machine with timed transitions",
        "positions": [
            {
                "id": "RED",
                "label": "Red",
                "description": "Stop",
                "color": "#dc2626",
                "is_current": True,
            },
            {
                "id": "YELLOW",
                "label": "Yellow",
                "description": "Caution",
                "color": "#f59e0b",
                "is_current": False,
            },
            {
                "id": "GREEN",
                "label": "Green",
                "description": "Go",
                "color": "#22c55e",
                "is_current": False,
            },
        ],
        "edges": [
            {"source": "RED", "target": "GREEN", "label": "tick", "is_valid": True},
            {"source": "GREEN", "target": "YELLOW", "label": "tick", "is_valid": True},
            {"source": "YELLOW", "target": "RED", "label": "tick", "is_valid": True},
        ],
        "valid_inputs": ["tick", "reset"],
        "teaching": "PolyAgent[S, A, B] captures mode-dependent behavior",
    },
    "vending_machine": {
        "name": "Vending Machine",
        "description": "State machine with value-dependent transitions",
        "positions": [
            {
                "id": "IDLE",
                "label": "Idle",
                "description": "Waiting for coins",
                "color": "#64748b",
                "is_current": True,
            },
            {
                "id": "COIN_25",
                "label": "25¢",
                "description": "One quarter",
                "color": "#3b82f6",
                "is_current": False,
            },
            {
                "id": "COIN_50",
                "label": "50¢",
                "description": "Two quarters",
                "color": "#8b5cf6",
                "is_current": False,
            },
            {
                "id": "DISPENSING",
                "label": "Dispensing",
                "description": "Product coming",
                "color": "#22c55e",
                "is_current": False,
            },
        ],
        "edges": [
            {
                "source": "IDLE",
                "target": "COIN_25",
                "label": "insert_coin",
                "is_valid": True,
            },
            {
                "source": "COIN_25",
                "target": "COIN_50",
                "label": "insert_coin",
                "is_valid": True,
            },
            {
                "source": "COIN_50",
                "target": "DISPENSING",
                "label": "select",
                "is_valid": True,
            },
            {
                "source": "DISPENSING",
                "target": "IDLE",
                "label": "complete",
                "is_valid": True,
            },
            {
                "source": "COIN_25",
                "target": "IDLE",
                "label": "refund",
                "is_valid": True,
            },
            {
                "source": "COIN_50",
                "target": "IDLE",
                "label": "refund",
                "is_valid": True,
            },
        ],
        "valid_inputs": ["insert_coin", "select", "refund"],
        "teaching": "Directions encode what inputs are valid at each state",
    },
    "citizen": {
        "name": "Citizen",
        "description": "Agent Town citizen life cycle with Right to Rest",
        "positions": [
            {
                "id": "IDLE",
                "label": "Idle",
                "description": "Ready",
                "color": "#64748b",
                "is_current": True,
            },
            {
                "id": "SOCIALIZING",
                "label": "Socializing",
                "description": "With others",
                "color": "#ec4899",
                "is_current": False,
            },
            {
                "id": "WORKING",
                "label": "Working",
                "description": "Task focus",
                "color": "#f59e0b",
                "is_current": False,
            },
            {
                "id": "REFLECTING",
                "label": "Reflecting",
                "description": "Self-analysis",
                "color": "#8b5cf6",
                "is_current": False,
            },
            {
                "id": "RESTING",
                "label": "Resting",
                "description": "Right to Rest",
                "color": "#22c55e",
                "is_current": False,
            },
        ],
        "edges": [
            {
                "source": "IDLE",
                "target": "SOCIALIZING",
                "label": "greet",
                "is_valid": True,
            },
            {"source": "IDLE", "target": "WORKING", "label": "task", "is_valid": True},
            {
                "source": "SOCIALIZING",
                "target": "WORKING",
                "label": "focus",
                "is_valid": True,
            },
            {
                "source": "SOCIALIZING",
                "target": "IDLE",
                "label": "farewell",
                "is_valid": True,
            },
            {
                "source": "WORKING",
                "target": "REFLECTING",
                "label": "complete",
                "is_valid": True,
            },
            {
                "source": "REFLECTING",
                "target": "RESTING",
                "label": "tired",
                "is_valid": True,
            },
            {
                "source": "REFLECTING",
                "target": "IDLE",
                "label": "energized",
                "is_valid": True,
            },
            {"source": "RESTING", "target": "IDLE", "label": "wake", "is_valid": True},
        ],
        "valid_inputs": ["greet", "task", "wake"],
        "right_to_rest": True,
        "teaching": "RESTING only accepts 'wake' - the Right to Rest enforced by directions",
    },
}


class _PolynomialPlaygroundWidget(KgentsWidget[None]):
    """
    Interactive polynomial playground widget.

    Features:
    - Preset selector (traffic_light, vending_machine, citizen)
    - Visual state diagram
    - Input buttons based on current state
    - Transition trace history
    - Teaching callouts

    Teaching goal: Make PolyAgent[S, A, B] tangible.
    """

    def __init__(
        self,
        preset: str,
        current_state: str | None = None,
        trace: list[str] | None = None,
    ) -> None:
        self._preset = preset
        self._config = POLYNOMIAL_PRESETS.get(preset, POLYNOMIAL_PRESETS["traffic_light"])
        self._current_state = current_state or self._config["positions"][0]["id"]
        self._trace = trace or []

        # Update is_current in positions
        for pos in self._config["positions"]:
            pos["is_current"] = pos["id"] == self._current_state

        # Compute valid inputs for current state
        self._valid_inputs = self._get_valid_inputs()

    def _get_valid_inputs(self) -> list[str]:
        """Get valid inputs for current state based on edges."""
        inputs = []
        for edge in self._config["edges"]:
            if edge["source"] == self._current_state:
                inputs.append(edge["label"])
        return list(set(inputs))

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return self._render_cli()
            case RenderTarget.JSON:
                return self._render_json()
            case _:
                return self._render_html()

    def _render_cli(self) -> str:
        lines = [
            f"[Polynomial Playground] {self._config['name']}",
            f"Description: {self._config['description']}",
            "",
            "States:",
        ]
        for pos in self._config["positions"]:
            marker = ">" if pos["is_current"] else " "
            lines.append(f"  {marker} {pos['id']}: {pos['description']}")

        lines.extend(
            [
                "",
                f"Current: {self._current_state}",
                f"Valid inputs: {', '.join(self._valid_inputs)}",
                "",
                f"Trace: {' → '.join(self._trace) if self._trace else '(none)'}",
                "",
                f"Teaching: {self._config['teaching']}",
            ]
        )
        return "\n".join(lines)

    def _render_json(self) -> dict[str, Any]:
        return {
            "type": "polynomial_playground",
            "preset": self._preset,
            "name": self._config["name"],
            "description": self._config["description"],
            "positions": self._config["positions"],
            "edges": self._config["edges"],
            "current_state": self._current_state,
            "valid_inputs": self._valid_inputs,
            "trace": self._trace,
            "teaching": self._config["teaching"],
            "right_to_rest": self._config.get("right_to_rest", False),
            "interactive": True,
            "api": {
                "transition": f"/api/gallery/polynomial/transition?preset={self._preset}&state={{state}}&input={{input}}",
                "reset": f"/api/gallery/polynomial/reset?preset={self._preset}",
            },
        }

    def _render_html(self) -> str:
        # Build state nodes
        state_nodes = []
        for i, pos in enumerate(self._config["positions"]):
            is_current = pos["is_current"]
            color = pos["color"]
            glow = f"box-shadow: 0 0 20px {color}60;" if is_current else ""
            border = (
                f"border: 2px solid {color};" if is_current else f"border: 1px solid {color}40;"
            )

            state_nodes.append(f"""
                <div class="poly-state" style="
                    background: linear-gradient(135deg, {color}20, {color}10);
                    {border}
                    border-radius: 12px;
                    padding: 12px 16px;
                    text-align: center;
                    min-width: 80px;
                    transition: all 0.3s ease;
                    {glow}
                " data-state="{pos["id"]}">
                    <div style="font-weight: 600; color: {color}; margin-bottom: 4px;">
                        {pos["label"]}
                    </div>
                    <div style="font-size: 10px; color: #94a3b8;">
                        {pos["description"]}
                    </div>
                </div>
            """)

        states_html = "".join(state_nodes)

        # Build input buttons
        input_buttons = []
        for inp in self._valid_inputs:
            input_buttons.append(f"""
                <button class="poly-input-btn" style="
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 13px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                " data-input="{inp}">
                    {inp}
                </button>
            """)
        inputs_html = (
            "".join(input_buttons)
            if input_buttons
            else "<span style='color: #64748b;'>No valid inputs</span>"
        )

        # Build trace
        trace_html = (
            " → ".join(self._trace)
            if self._trace
            else "<em style='color: #64748b;'>Click an input to begin</em>"
        )

        return f"""
        <div class="polynomial-playground" style="
            background: #0f172a;
            border-radius: 16px;
            padding: 20px;
            font-family: system-ui, -apple-system, sans-serif;
        ">
            {" <!-- Header --> "}
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <div>
                    <h3 style="color: #f8fafc; margin: 0 0 4px 0; font-size: 18px;">
                        {self._config["name"]}
                    </h3>
                    <p style="color: #64748b; margin: 0; font-size: 13px;">
                        {self._config["description"]}
                    </p>
                </div>
                <select class="preset-selector" style="
                    background: #1e293b;
                    color: #e2e8f0;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                ">
                    <option value="traffic_light" {"selected" if self._preset == "traffic_light" else ""}>Traffic Light</option>
                    <option value="vending_machine" {"selected" if self._preset == "vending_machine" else ""}>Vending Machine</option>
                    <option value="citizen" {"selected" if self._preset == "citizen" else ""}>Citizen</option>
                </select>
            </div>

            {" <!-- State Diagram --> "}
            <div style="
                display: flex;
                gap: 16px;
                flex-wrap: wrap;
                justify-content: center;
                padding: 24px;
                background: #1e293b;
                border-radius: 12px;
                margin-bottom: 16px;
            ">
                {states_html}
            </div>

            {" <!-- Input Controls --> "}
            <div style="
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 16px;
            ">
                <span style="color: #94a3b8; font-size: 13px; min-width: 80px;">Inputs:</span>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    {inputs_html}
                </div>
            </div>

            {" <!-- Trace --> "}
            <div style="
                background: #1e293b;
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 16px;
            ">
                <span style="color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    Trace
                </span>
                <div style="color: #e2e8f0; font-family: monospace; font-size: 13px; margin-top: 4px;">
                    {trace_html}
                </div>
            </div>

            {" <!-- Teaching Callout --> "}
            <div style="
                background: linear-gradient(135deg, #3b82f620, #8b5cf620);
                border-left: 3px solid #8b5cf6;
                border-radius: 0 8px 8px 0;
                padding: 12px 16px;
            ">
                <span style="color: #a78bfa; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    Teaching
                </span>
                <p style="color: #e2e8f0; margin: 4px 0 0 0; font-size: 13px;">
                    {self._config["teaching"]}
                </p>
            </div>
        </div>
        """


def _create_polynomial_playground(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create polynomial playground widget."""
    preset = overrides.get("preset", "traffic_light")
    current_state = overrides.get("state")
    trace = overrides.get("trace", [])
    return _PolynomialPlaygroundWidget(preset, current_state, trace)


register_pilot(
    Pilot(
        name="polynomial_playground",
        category=PilotCategory.INTERACTIVE,
        description="Build and run state machines interactively - learn PolyAgent[S,A,B]",
        widget_factory=_create_polynomial_playground,
        variations=[
            {"preset": "traffic_light"},
            {"preset": "vending_machine"},
            {"preset": "citizen"},
        ],
        tags=["polynomial", "interactive", "state-machine", "flagship", "teaching"],
    )
)


# Operad definitions for wiring diagram
OPERAD_DEFINITIONS = {
    "TOWN_OPERAD": {
        "name": "TOWN_OPERAD",
        "description": "Grammar of citizen interactions in Agent Town",
        "operations": [
            {
                "id": "greet",
                "name": "greet",
                "arity": 2,
                "signature": "Citizen × Citizen → Relationship",
                "color": "#22c55e",
            },
            {
                "id": "gossip",
                "name": "gossip",
                "arity": 2,
                "signature": "Citizen × Citizen → Information",
                "color": "#3b82f6",
            },
            {
                "id": "trade",
                "name": "trade",
                "arity": 2,
                "signature": "Citizen × Citizen → Exchange",
                "color": "#f59e0b",
            },
            {
                "id": "solo",
                "name": "solo",
                "arity": 1,
                "signature": "Citizen → Reflection",
                "color": "#8b5cf6",
            },
            {
                "id": "celebrate",
                "name": "celebrate",
                "arity": 3,
                "signature": "Cit × Cit × Cit → Event",
                "color": "#ec4899",
            },
        ],
        "laws": [
            {
                "id": "identity",
                "name": "Identity",
                "equation": "γ(f; id, ..., id) = f",
                "verified": True,
            },
            {
                "id": "associativity",
                "name": "Associativity",
                "equation": "γ(γ(f;g);h) = γ(f;γ(g;h))",
                "verified": True,
            },
            {
                "id": "locality",
                "name": "Locality",
                "equation": "ops affect only participants",
                "verified": True,
            },
        ],
        "teaching": "Operads define the grammar of composition - which operations can combine and how",
    },
    "FLOW_OPERAD": {
        "name": "FLOW_OPERAD",
        "description": "Research and collaboration flow composition",
        "operations": [
            {
                "id": "query",
                "name": "query",
                "arity": 1,
                "signature": "Question → SearchResults",
                "color": "#22c55e",
            },
            {
                "id": "synthesize",
                "name": "synthesize",
                "arity": 2,
                "signature": "Results × Results → Summary",
                "color": "#3b82f6",
            },
            {
                "id": "critique",
                "name": "critique",
                "arity": 1,
                "signature": "Summary → Refinement",
                "color": "#f59e0b",
            },
            {
                "id": "commit",
                "name": "commit",
                "arity": 1,
                "signature": "Refinement → Knowledge",
                "color": "#8b5cf6",
            },
        ],
        "laws": [
            {
                "id": "identity",
                "name": "Identity",
                "equation": "γ(f; id) = f",
                "verified": True,
            },
            {
                "id": "associativity",
                "name": "Associativity",
                "equation": "γ(γ(f;g);h) = γ(f;γ(g;h))",
                "verified": True,
            },
        ],
        "teaching": "FLOW_OPERAD governs research collaboration - ensuring coherent knowledge synthesis",
    },
}


class _OperadWiringWidget(KgentsWidget[None]):
    """
    Interactive operad wiring diagram widget.

    Features:
    - Operation palette with arities
    - Visual composition canvas
    - Law verification indicators
    - Composition output display

    Teaching goal: Make operad composition visual and verifiable.
    """

    def __init__(self, operad: str, composition: list[dict[str, Any]] | None = None) -> None:
        self._operad_name = operad
        self._config = OPERAD_DEFINITIONS.get(operad, OPERAD_DEFINITIONS["TOWN_OPERAD"])
        self._composition = composition or []

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return self._render_cli()
            case RenderTarget.JSON:
                return self._render_json()
            case _:
                return self._render_html()

    def _render_cli(self) -> str:
        lines = [
            f"[Operad Wiring] {self._config['name']}",
            f"Description: {self._config['description']}",
            "",
            "Operations:",
        ]
        for op in self._config["operations"]:
            lines.append(f"  {op['name']} ({op['arity']}): {op['signature']}")

        lines.extend(["", "Laws:"])
        for law in self._config["laws"]:
            status = "✓" if law["verified"] else "✗"
            lines.append(f"  {status} {law['name']}: {law['equation']}")

        lines.extend(
            [
                "",
                f"Teaching: {self._config['teaching']}",
            ]
        )
        return "\n".join(lines)

    def _render_json(self) -> dict[str, Any]:
        return {
            "type": "operad_wiring",
            "operad": self._operad_name,
            "name": self._config["name"],
            "description": self._config["description"],
            "operations": self._config["operations"],
            "laws": self._config["laws"],
            "composition": self._composition,
            "teaching": self._config["teaching"],
            "interactive": True,
            "api": {
                "compose": f"/api/gallery/operad/compose?operad={self._operad_name}",
                "verify": f"/api/gallery/operad/verify?operad={self._operad_name}",
            },
        }

    def _render_html(self) -> str:
        # Build operation palette
        ops_html = []
        for op in self._config["operations"]:
            color = op["color"]
            ops_html.append(f"""
                <div class="operad-op" draggable="true" style="
                    background: linear-gradient(135deg, {color}20, {color}10);
                    border: 1px solid {color}40;
                    border-radius: 8px;
                    padding: 10px 14px;
                    cursor: grab;
                    transition: all 0.2s ease;
                " data-op="{op["id"]}">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="
                            background: {color};
                            color: white;
                            font-size: 10px;
                            padding: 2px 6px;
                            border-radius: 4px;
                            font-weight: 600;
                        ">{op["arity"]}</span>
                        <span style="font-weight: 600; color: {color};">{op["name"]}</span>
                    </div>
                    <div style="font-size: 10px; color: #64748b; margin-top: 4px;">
                        {op["signature"]}
                    </div>
                </div>
            """)
        operations_html = "".join(ops_html)

        # Build law indicators
        laws_html = []
        for law in self._config["laws"]:
            color = "#22c55e" if law["verified"] else "#dc2626"
            icon = "✓" if law["verified"] else "✗"
            laws_html.append(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 6px 12px;
                    background: {color}15;
                    border-radius: 6px;
                ">
                    <span style="color: {color}; font-weight: 600;">{icon}</span>
                    <span style="color: #e2e8f0; font-size: 12px;">{law["name"]}</span>
                </div>
            """)
        laws_indicators = "".join(laws_html)

        return f"""
        <div class="operad-wiring" style="
            background: #0f172a;
            border-radius: 16px;
            padding: 20px;
            font-family: system-ui, -apple-system, sans-serif;
        ">
            {" <!-- Header --> "}
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <div>
                    <h3 style="color: #f8fafc; margin: 0 0 4px 0; font-size: 18px;">
                        {self._config["name"]}
                    </h3>
                    <p style="color: #64748b; margin: 0; font-size: 13px;">
                        {self._config["description"]}
                    </p>
                </div>
                <div style="display: flex; gap: 8px;">
                    {laws_indicators}
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 200px 1fr; gap: 16px;">
                {" <!-- Operation Palette --> "}
                <div style="
                    background: #1e293b;
                    border-radius: 12px;
                    padding: 16px;
                ">
                    <div style="color: #94a3b8; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">
                        Operations
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        {operations_html}
                    </div>
                </div>

                {" <!-- Composition Canvas --> "}
                <div style="
                    background: #1e293b;
                    border-radius: 12px;
                    padding: 16px;
                    min-height: 200px;
                    display: flex;
                    flex-direction: column;
                ">
                    <div style="color: #94a3b8; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">
                        Composition Canvas
                    </div>
                    <div style="
                        flex: 1;
                        border: 2px dashed #334155;
                        border-radius: 8px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #64748b;
                        font-size: 13px;
                    ">
                        Drag operations here to compose
                    </div>
                </div>
            </div>

            {" <!-- Teaching Callout --> "}
            <div style="
                background: linear-gradient(135deg, #f59e0b20, #ec489820);
                border-left: 3px solid #f59e0b;
                border-radius: 0 8px 8px 0;
                padding: 12px 16px;
                margin-top: 16px;
            ">
                <span style="color: #fbbf24; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    Teaching
                </span>
                <p style="color: #e2e8f0; margin: 4px 0 0 0; font-size: 13px;">
                    {self._config["teaching"]}
                </p>
            </div>
        </div>
        """


def _create_operad_wiring(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create operad wiring diagram widget."""
    operad = overrides.get("operad", "TOWN_OPERAD")
    composition = overrides.get("composition", [])
    return _OperadWiringWidget(operad, composition)


register_pilot(
    Pilot(
        name="operad_wiring_diagram",
        category=PilotCategory.INTERACTIVE,
        description="Wire operations together and verify composition laws",
        widget_factory=_create_operad_wiring,
        variations=[
            {"operad": "TOWN_OPERAD"},
            {"operad": "FLOW_OPERAD"},
        ],
        tags=["operad", "interactive", "composition", "flagship", "teaching"],
    )
)


class _TownLiveWidget(KgentsWidget[None]):
    """
    Live Agent Town streaming widget.

    Features:
    - Real-time citizen updates via SSE
    - Mini-mesa visualization
    - Phase indicator
    - Event feed
    - Playback controls

    Teaching goal: Polynomial agents in motion - watch state machines interact.
    """

    def __init__(
        self,
        town_id: str = "demo",
        citizens: list[dict[str, Any]] | None = None,
        events: list[dict[str, Any]] | None = None,
        day: int = 1,
        phase: str = "MORNING",
    ) -> None:
        self._town_id = town_id
        self._citizens = citizens or [
            {
                "id": "socrates",
                "name": "Socrates",
                "char": "K",
                "phase": "active",
                "x": 2,
                "y": 2,
                "archetype": "Scholar",
            },
            {
                "id": "hypatia",
                "name": "Hypatia",
                "char": "H",
                "phase": "working",
                "x": 5,
                "y": 3,
                "archetype": "Builder",
            },
            {
                "id": "marcus",
                "name": "Marcus",
                "char": "M",
                "phase": "idle",
                "x": 3,
                "y": 5,
                "archetype": "Watcher",
            },
            {
                "id": "ada",
                "name": "Ada",
                "char": "A",
                "phase": "reflecting",
                "x": 6,
                "y": 4,
                "archetype": "Builder",
            },
            {
                "id": "leonardo",
                "name": "Leonardo",
                "char": "L",
                "phase": "resting",
                "x": 4,
                "y": 6,
                "archetype": "Healer",
            },
        ]
        self._events = events or [
            {"tick": 42, "operation": "greet", "message": "Socrates greeted Marcus"},
            {"tick": 41, "operation": "work", "message": "Hypatia started building"},
            {
                "tick": 40,
                "operation": "rest",
                "message": "Leonardo began rest (Right to Rest)",
            },
        ]
        self._day = day
        self._phase = phase

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return self._render_cli()
            case RenderTarget.JSON:
                return self._render_json()
            case _:
                return self._render_html()

    def _render_cli(self) -> str:
        lines = [
            f"[Town Live] {self._town_id}",
            f"Day {self._day} | Phase: {self._phase} | Citizens: {len(self._citizens)}",
            "",
            "Citizens:",
        ]
        for c in self._citizens:
            lines.append(f"  {c['char']} {c['name']:<12} [{c['phase'].upper()}] {c['archetype']}")

        lines.extend(["", "Recent Events:"])
        for e in self._events[:5]:
            lines.append(f"  [{e['tick']}] {e['message']}")

        lines.extend(
            [
                "",
                "Teaching: Watch polynomial agents interact in real-time",
            ]
        )
        return "\n".join(lines)

    def _render_json(self) -> dict[str, Any]:
        return {
            "type": "town_live",
            "town_id": self._town_id,
            "day": self._day,
            "phase": self._phase,
            "citizens": self._citizens,
            "events": self._events,
            "interactive": True,
            "streaming": True,
            "sse_endpoint": f"/api/town/{self._town_id}/stream",
            "teaching": "Polynomial agents in motion - watch state machines interact",
        }

    def _render_html(self) -> str:
        # Phase colors
        phase_colors = {
            "MORNING": "#f59e0b",
            "AFTERNOON": "#f97316",
            "EVENING": "#8b5cf6",
            "NIGHT": "#3b82f6",
        }
        phase_color = phase_colors.get(self._phase, "#64748b")

        # Citizen phase colors
        citizen_colors = {
            "idle": "#64748b",
            "active": "#22c55e",
            "socializing": "#ec4899",
            "working": "#f59e0b",
            "reflecting": "#8b5cf6",
            "resting": "#3b82f6",
        }

        # Build citizen mini-cards
        citizen_cards = []
        for c in self._citizens:
            color = citizen_colors.get(c["phase"], "#64748b")
            citizen_cards.append(f"""
                <div class="citizen-mini" style="
                    background: linear-gradient(135deg, {color}15, {color}05);
                    border: 1px solid {color}40;
                    border-radius: 8px;
                    padding: 8px 12px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    min-width: 120px;
                ">
                    <span style="
                        font-size: 18px;
                        color: {color};
                        text-shadow: 0 0 8px {color}60;
                    ">{c["char"]}</span>
                    <div>
                        <div style="font-weight: 600; color: #e2e8f0; font-size: 12px;">{c["name"]}</div>
                        <div style="font-size: 10px; color: {color}; text-transform: uppercase;">{c["phase"]}</div>
                    </div>
                </div>
            """)
        citizens_html = "".join(citizen_cards)

        # Build event feed
        event_items = []
        for e in self._events[:5]:
            event_items.append(f"""
                <div style="font-size: 12px; color: #94a3b8; padding: 4px 0;">
                    <span style="color: #64748b; font-family: monospace;">[{e["tick"]}]</span>
                    <span style="color: #e2e8f0;">{e["message"]}</span>
                </div>
            """)
        events_html = "".join(event_items)

        return f"""
        <div class="town-live" style="
            background: #0f172a;
            border-radius: 16px;
            padding: 20px;
            font-family: system-ui, -apple-system, sans-serif;
        ">
            {" <!-- Header --> "}
            <div style="
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid #1e293b;
            ">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <h3 style="color: #f8fafc; margin: 0; font-size: 18px;">
                        Town: {self._town_id}
                    </h3>
                    <span style="color: #64748b; font-size: 13px;">Day {self._day}</span>
                    <span style="
                        background: {phase_color}20;
                        color: {phase_color};
                        padding: 4px 10px;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: 600;
                    ">{self._phase}</span>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button style="
                        background: #22c55e;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 8px 16px;
                        font-size: 13px;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    ">
                        ▶ Play
                    </button>
                    <select style="
                        background: #1e293b;
                        color: #e2e8f0;
                        border: 1px solid #334155;
                        border-radius: 6px;
                        padding: 6px 12px;
                        font-size: 13px;
                    ">
                        <option>1x</option>
                        <option>2x</option>
                        <option>4x</option>
                    </select>
                </div>
            </div>

            {" <!-- Citizens Grid --> "}
            <div style="
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                margin-bottom: 16px;
            ">
                {citizens_html}
            </div>

            {" <!-- Event Feed --> "}
            <div style="
                background: #1e293b;
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 16px;
            ">
                <div style="color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                    Event Feed
                </div>
                {events_html}
            </div>

            {" <!-- Teaching Callout --> "}
            <div style="
                background: linear-gradient(135deg, #22c55e20, #3b82f620);
                border-left: 3px solid #22c55e;
                border-radius: 0 8px 8px 0;
                padding: 12px 16px;
            ">
                <span style="color: #4ade80; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">
                    Teaching
                </span>
                <p style="color: #e2e8f0; margin: 4px 0 0 0; font-size: 13px;">
                    Polynomial agents in motion - watch state machines interact in real-time
                </p>
            </div>

            {" <!-- SSE Indicator --> "}
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                margin-top: 12px;
                padding-top: 12px;
                border-top: 1px solid #1e293b;
            ">
                <div style="
                    width: 8px;
                    height: 8px;
                    background: #22c55e;
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                "></div>
                <span style="color: #64748b; font-size: 11px;">
                    Streaming from /api/town/{self._town_id}/stream
                </span>
            </div>
        </div>
        <style>
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
        </style>
        """


def _create_town_live(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    """Create town live streaming widget."""
    town_id = overrides.get("town_id", "demo")
    return _TownLiveWidget(town_id=town_id)


register_pilot(
    Pilot(
        name="town_live",
        category=PilotCategory.INTERACTIVE,
        description="Watch Agent Town citizens in real-time streaming simulation",
        widget_factory=_create_town_live,
        tags=["streaming", "town", "citizens", "flagship", "teaching", "sse"],
    )
)
