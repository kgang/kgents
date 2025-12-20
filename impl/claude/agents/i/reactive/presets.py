"""
Layout presets for widget composition.

Wave 2.1 Preset Functions
=========================

Presets reduce cognitive load by providing common composition patterns:
- metric_row(*widgets) - horizontal composition with gap=2
- metric_stack(*widgets) - vertical composition with gap=0
- panel(header, body) - header + body layout
- labeled(label, widget) - label glyph + widget
- status_row(phase, activity, health) - standard agent status

Learning from plans/meta.md:
  "Layout presets > manual composition: metric_row(), panel(), status_row() reduce cognitive load"

Quick Start
-----------
    from agents.i.reactive.presets import metric_row, metric_stack, panel, labeled, status_row
    from agents.i.reactive.primitives.bar import BarState, BarWidget
    from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
    from agents.i.reactive.widget import RenderTarget

    # Simple row of metrics
    row = metric_row(
        BarWidget(BarState(value=0.7, label="CPU")),
        BarWidget(BarState(value=0.4, label="MEM")),
    )
    print(row.project(RenderTarget.CLI))
    # Output: CPU: ███████░░░  MEM: ████░░░░░░

    # Labeled widget
    load = labeled("System Load:", BarWidget(BarState(value=0.85)))
    print(load.project(RenderTarget.CLI))
    # Output: System Load: ████████░░

    # Full dashboard
    dashboard = panel(
        GlyphWidget(GlyphState(char="═══ Dashboard ═══")),
        metric_stack(
            status_row("SENSE", "Scanning...", 0.9),
            status_row("ACT", "Idle", 0.5),
        ),
    )

Performance (stress-verified)
-----------------------------
    - 50 BarWidgets in metric_row: passes
    - 50 nested metric_rows: passes
    - 1100 status_row renders: <1s
    - Full dashboard 50x: <2s

See Also
--------
    - composable.py: Low-level >> and // operators
    - HStack, VStack: Composition containers
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from agents.i.reactive.composable import ComposableWidget, HStack, VStack
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

if TYPE_CHECKING:
    pass

# GlyphState.phase uses this literal type
GlyphPhase = Literal["idle", "active", "waiting", "error", "yielding", "thinking", "complete"]


# =============================================================================
# Horizontal Composition
# =============================================================================


def metric_row(*widgets: ComposableWidget, gap: int = 2, separator: str | None = None) -> HStack:
    """
    Compose widgets horizontally with consistent spacing.

    This is the standard pattern for side-by-side metrics:
        metric_row(cpu_bar, mem_bar, disk_bar)

    Args:
        *widgets: Widgets to compose horizontally
        gap: Space between widgets (in characters)
        separator: Optional separator string between widgets

    Returns:
        HStack containing all widgets, or empty HStack if no widgets

    Example:
        >>> cpu = BarWidget(BarState(value=0.75, label="CPU"))
        >>> mem = BarWidget(BarState(value=0.50, label="MEM"))
        >>> row = metric_row(cpu, mem)
        >>> row.project(RenderTarget.CLI)
        'CPU: ███████░░░  MEM: █████░░░░░'
    """
    if not widgets:
        return HStack(children=[], gap=gap)

    result = HStack(children=list(widgets), gap=gap, separator=separator)
    return result


# =============================================================================
# Vertical Composition
# =============================================================================


def metric_stack(*widgets: ComposableWidget, gap: int = 0, separator: str | None = None) -> VStack:
    """
    Compose widgets vertically with consistent spacing.

    This is the standard pattern for stacked metrics:
        metric_stack(header, body, footer)

    Args:
        *widgets: Widgets to compose vertically
        gap: Lines between widgets
        separator: Optional separator line between widgets

    Returns:
        VStack containing all widgets, or empty VStack if no widgets

    Example:
        >>> cpu = BarWidget(BarState(value=0.75, label="CPU"))
        >>> mem = BarWidget(BarState(value=0.50, label="MEM"))
        >>> stack = metric_stack(cpu, mem)
        >>> print(stack.project(RenderTarget.CLI))
        CPU: ███████░░░
        MEM: █████░░░░░
    """
    if not widgets:
        return VStack(children=[], gap=gap)

    result = VStack(children=list(widgets), gap=gap, separator=separator)
    return result


# =============================================================================
# Panel Layout
# =============================================================================


def panel(header: ComposableWidget, body: ComposableWidget, gap: int = 0) -> VStack:
    """
    Create a panel with header and body sections.

    A panel is a vertical composition with optional gap:
        panel(title_glyph, content_widget)

    Args:
        header: Top section widget
        body: Bottom section widget
        gap: Lines between header and body

    Returns:
        VStack with header and body

    Example:
        >>> title = GlyphWidget(GlyphState(char="═══ Status ═══"))
        >>> bars = metric_row(cpu_bar, mem_bar)
        >>> p = panel(title, bars)
    """
    return VStack(children=[header, body], gap=gap)


# =============================================================================
# Labeled Widget
# =============================================================================


def labeled(label: str, widget: ComposableWidget, separator: str = " ") -> HStack:
    """
    Add a label glyph to the left of a widget.

    Creates a horizontal composition with label first:
        labeled("CPU", cpu_bar)  -> "CPU cpu_bar_output"

    Args:
        label: Text label to prepend
        widget: Widget to label
        separator: String between label and widget

    Returns:
        HStack with label glyph and widget

    Example:
        >>> bar = BarWidget(BarState(value=0.75))
        >>> l = labeled("Load:", bar)
        >>> l.project(RenderTarget.CLI)
        'Load: ███████░░░'
    """
    label_glyph = GlyphWidget(GlyphState(char=label))
    return HStack(children=[label_glyph, widget], gap=0, separator=separator)


# =============================================================================
# Status Row
# =============================================================================


def status_row(
    phase: str,
    activity: str,
    health: float,
    *,
    phase_colors: dict[str, str] | None = None,
) -> HStack:
    """
    Create a standard agent status row.

    The status row is a common pattern for agent displays:
        [Phase Glyph] [Activity Text] [Health Bar]

    Args:
        phase: Phase name (e.g., "SENSE", "ACT", "REFLECT")
        activity: Current activity description
        health: Health value 0.0-1.0

    Returns:
        HStack with phase glyph, activity glyph, and health indicator

    Example:
        >>> row = status_row("SENSE", "Analyzing...", 0.85)
        >>> row.project(RenderTarget.CLI)
        '● SENSE Analyzing... ████████░░'
    """
    # Import here to avoid circular dependency
    from agents.i.reactive.primitives.bar import BarState, BarWidget

    # Phase indicator glyph
    phase_char = _phase_to_symbol(phase)
    phase_fg = None
    if phase_colors:
        phase_fg = phase_colors.get(phase)
    glyph_phase = _phase_to_glyph_phase(phase)
    phase_glyph = GlyphWidget(GlyphState(char=phase_char, fg=phase_fg, phase=glyph_phase))

    # Phase name glyph
    phase_name = GlyphWidget(GlyphState(char=phase))

    # Activity glyph
    activity_glyph = GlyphWidget(GlyphState(char=activity))

    # Health bar
    health_bar = BarWidget(BarState(value=max(0.0, min(1.0, health)), width=10, style="solid"))

    return HStack(
        children=[phase_glyph, phase_name, activity_glyph, health_bar],
        gap=1,
    )


def _phase_to_symbol(phase: str) -> str:
    """Map phase name to status symbol."""
    symbols = {
        "SENSE": "◉",
        "ACT": "▶",
        "REFLECT": "◐",
        "PLAN": "○",
        "RESEARCH": "◎",
        "DEVELOP": "◉",
        "STRATEGIZE": "◈",
        "CROSS-SYNERGIZE": "◇",
        "IMPLEMENT": "▶",
        "QA": "◐",
        "TEST": "◑",
        "EDUCATE": "◒",
        "MEASURE": "◓",
    }
    return symbols.get(phase.upper(), "●")


def _phase_to_glyph_phase(phase: str) -> GlyphPhase | None:
    """Map N-Phase names to GlyphState.phase literals."""
    mapping: dict[str, GlyphPhase] = {
        # SENSE phases map to thinking/waiting
        "SENSE": "thinking",
        "PLAN": "thinking",
        "RESEARCH": "waiting",
        "DEVELOP": "active",
        "STRATEGIZE": "thinking",
        "CROSS-SYNERGIZE": "waiting",
        # ACT phases map to active
        "ACT": "active",
        "IMPLEMENT": "active",
        "QA": "active",
        "TEST": "active",
        "EDUCATE": "active",
        # REFLECT phases map to complete/idle
        "REFLECT": "complete",
        "MEASURE": "complete",
    }
    return mapping.get(phase.upper())


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "metric_row",
    "metric_stack",
    "panel",
    "labeled",
    "status_row",
]
