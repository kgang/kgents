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

    def create_widget(
        self, overrides: dict[str, Any] | None = None
    ) -> KgentsWidget[Any]:
        """Create the widget with optional overrides."""
        return self.widget_factory(overrides or {})

    def render(
        self, target: RenderTarget, overrides: dict[str, Any] | None = None
    ) -> Any:
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
            content=overrides.get(
                "content", "This is a yielded result from an agent operation."
            ),
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
                    self._state.__dict__
                    if hasattr(self._state, "__dict__")
                    else str(self._state)
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
