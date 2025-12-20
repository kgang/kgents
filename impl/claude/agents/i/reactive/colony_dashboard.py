"""
ColonyDashboard: Agent Town Colony Visualization.

Wave 4 Component
================

ColonyDashboard composes multiple CitizenWidgets into a unified dashboard
for visualizing an Agent Town colony in real-time.

Architecture:
    ColonyState (frozen dataclass)
        ↓
    ColonyDashboard (KgentsWidget)
        ↓
    Grid of CitizenWidgets (HStack/VStack composition)
        ↓
    Multiple projection targets (CLI/TUI/marimo/JSON)

Quick Start:
    from agents.i.reactive.colony_dashboard import ColonyDashboard, ColonyState
    from agents.i.reactive.primitives.citizen_card import CitizenState
    from agents.town.polynomial import CitizenPhase

    # Create colony state
    citizens = (
        CitizenState(citizen_id="alice", name="Alice", phase=CitizenPhase.WORKING),
        CitizenState(citizen_id="bob", name="Bob", phase=CitizenPhase.IDLE),
    )
    colony = ColonyState(colony_id="town-1", citizens=citizens, day=1)

    # Create dashboard
    dashboard = ColonyDashboard(colony)
    print(dashboard.project(RenderTarget.CLI))

Signal Integration:
    The dashboard integrates with Signal for reactive updates:

    signal = Signal.of(ColonyState(...))
    dashboard = ColonyDashboard()
    dashboard.bind_signal(signal)

    # State updates trigger dashboard rebuild
    signal.set(ColonyState(...))  # Dashboard auto-updates

See Also:
    - primitives/citizen_card.py: CitizenWidget
    - composable.py: HStack/VStack composition
    - town/flux.py: TownFlux event source
    - docs/skills/agent-town-visualization.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from agents.i.reactive.composable import ComposableMixin, HStack, VStack
from agents.i.reactive.primitives.citizen_card import CitizenState, CitizenWidget
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    from agents.town.flux import TownFlux


# =============================================================================
# Colony Phase (Simulation Time)
# =============================================================================


class TownPhase(Enum):
    """Town simulation phases (time of day)."""

    MORNING = auto()
    AFTERNOON = auto()
    EVENING = auto()
    NIGHT = auto()


# =============================================================================
# ColonyState
# =============================================================================


@dataclass(frozen=True)
class ColonyState:
    """
    Immutable state for an Agent Town colony dashboard.

    All dashboard rendering derives deterministically from this state.
    """

    colony_id: str = ""
    citizens: tuple[CitizenState, ...] = ()
    phase: TownPhase = TownPhase.MORNING
    day: int = 1
    total_events: int = 0
    total_tokens: int = 0
    entropy_budget: float = 1.0
    selected_citizen_id: str | None = None
    grid_cols: int = 4  # Citizens per row

    @classmethod
    def from_flux(
        cls,
        flux: TownFlux,
        activity_buffers: dict[str, list[float]] | None = None,
    ) -> ColonyState:
        """
        Extract ColonyState from TownFlux.

        Args:
            flux: The TownFlux to extract state from
            activity_buffers: Optional citizen_id -> activity samples mapping

        Returns:
            Frozen ColonyState with all fields populated
        """
        activity_buffers = activity_buffers or {}

        citizens_state = []
        for citizen in flux.citizens:
            activity = tuple(activity_buffers.get(citizen.id, []))
            state = CitizenState.from_citizen(citizen, activity_samples=activity)
            citizens_state.append(state)

        status = flux.get_status()

        return cls(
            colony_id=f"colony-{id(flux)}",
            citizens=tuple(citizens_state),
            phase=_map_flux_phase(flux.current_phase),
            day=flux.day,
            total_events=status.get("total_events", 0),
            total_tokens=status.get("total_tokens", 0),
            entropy_budget=status.get("accursed_surplus", 0.0),
        )


def _map_flux_phase(flux_phase: Any) -> TownPhase:
    """Map TownFlux.TownPhase to dashboard TownPhase."""
    # TownFlux uses its own TownPhase enum
    phase_name = getattr(flux_phase, "name", "MORNING")
    mapping = {
        "MORNING": TownPhase.MORNING,
        "AFTERNOON": TownPhase.AFTERNOON,
        "EVENING": TownPhase.EVENING,
        "NIGHT": TownPhase.NIGHT,
    }
    return mapping.get(phase_name, TownPhase.MORNING)


# =============================================================================
# ColonyDashboard
# =============================================================================


class ColonyDashboard(ComposableMixin, KgentsWidget[ColonyState]):
    """
    Unified dashboard for Agent Town colony visualization.

    Composes CitizenWidgets into a grid layout with header and footer.
    Supports all rendering targets: CLI, TUI, marimo, JSON.

    Features:
    - Automatic grid layout (configurable columns)
    - Colony-level metrics (phase, day, events, tokens)
    - Citizen selection highlighting
    - Signal binding for reactive updates

    Example:
        # Static dashboard
        colony = ColonyState(citizens=(...), day=1)
        dashboard = ColonyDashboard(colony)
        print(dashboard.project(RenderTarget.CLI))

        # Reactive dashboard
        signal = Signal.of(ColonyState(...))
        dashboard = ColonyDashboard()
        dashboard.bind_signal(signal)
        signal.set(ColonyState(...))  # Dashboard updates
    """

    state: Signal[ColonyState]
    _bound_signal: Signal[ColonyState] | None

    def __init__(self, initial: ColonyState | None = None) -> None:
        state = initial or ColonyState()
        self.state = Signal.of(state)
        self._bound_signal = None

    def bind_signal(self, signal: Signal[ColonyState]) -> None:
        """
        Bind dashboard to a Signal for reactive updates.

        When the bound signal changes, the dashboard state updates automatically.
        """
        self._bound_signal = signal

        def on_change(new_state: ColonyState) -> None:
            self.state.set(new_state)

        signal.subscribe(on_change)

    def with_state(self, new_state: ColonyState) -> ColonyDashboard:
        """Return new dashboard with updated state. Immutable."""
        return ColonyDashboard(new_state)

    def select_citizen(self, citizen_id: str | None) -> ColonyDashboard:
        """Return new dashboard with citizen selected."""
        current = self.state.value
        return ColonyDashboard(
            ColonyState(
                colony_id=current.colony_id,
                citizens=current.citizens,
                phase=current.phase,
                day=current.day,
                total_events=current.total_events,
                total_tokens=current.total_tokens,
                entropy_budget=current.entropy_budget,
                selected_citizen_id=citizen_id,
                grid_cols=current.grid_cols,
            )
        )

    def set_grid_cols(self, cols: int) -> ColonyDashboard:
        """Return new dashboard with different column count."""
        current = self.state.value
        return ColonyDashboard(
            ColonyState(
                colony_id=current.colony_id,
                citizens=current.citizens,
                phase=current.phase,
                day=current.day,
                total_events=current.total_events,
                total_tokens=current.total_tokens,
                entropy_budget=current.entropy_budget,
                selected_citizen_id=current.selected_citizen_id,
                grid_cols=max(1, cols),
            )
        )

    def _build_citizen_grid(self) -> VStack | HStack | None:
        """
        Build citizen widget grid using HStack/VStack composition.

        Returns VStack of HStack rows (or single HStack if one row), or None if no citizens.
        """
        from typing import cast

        state = self.state.value
        citizens = state.citizens
        cols = state.grid_cols

        if not citizens:
            return None

        # Create widgets for each citizen
        widgets = [CitizenWidget(c) for c in citizens]

        # Chunk into rows
        rows: list[HStack] = []
        for i in range(0, len(widgets), cols):
            chunk = widgets[i : i + cols]
            if chunk:
                # Build row via >> composition
                row_widget: HStack | CitizenWidget = chunk[0]
                for w in chunk[1:]:
                    row_widget = row_widget >> w
                rows.append(cast(HStack, row_widget))

        if not rows:
            return None

        # Single row - return as HStack
        if len(rows) == 1:
            return rows[0]

        # Stack rows via // composition
        grid: VStack | HStack = rows[0]
        for row in rows[1:]:
            grid = grid // row

        return cast(VStack, grid)

    def project(self, target: RenderTarget) -> Any:
        """
        Project this colony dashboard to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (ASCII dashboard)
            - TUI: Rich Panel
            - MARIMO: HTML div
            - JSON: dict with colony data
        """
        match target:
            case RenderTarget.CLI:
                return self._to_cli()
            case RenderTarget.TUI:
                return self._to_tui()
            case RenderTarget.MARIMO:
                return self._to_marimo()
            case RenderTarget.JSON:
                return self._to_json()

    def _to_cli(self) -> str:
        """CLI projection: ASCII dashboard with box drawing."""
        state = self.state.value

        # Build output
        lines = []

        # Header box
        width = 65
        lines.append("┌" + "─" * (width - 2) + "┐")
        title = "AGENT TOWN DASHBOARD"
        padding = (width - 2 - len(title)) // 2
        lines.append("│" + " " * padding + title + " " * (width - 2 - padding - len(title)) + "│")
        lines.append("├" + "─" * (width - 2) + "┤")

        # Status line
        status = (
            f"Colony: {state.colony_id[:12]:<12} │ "
            f"Citizens: {len(state.citizens):<2} │ "
            f"Phase: {state.phase.name:<9} │ "
            f"Day: {state.day}"
        )
        lines.append(
            "│ " + status[: width - 4] + " " * (width - 4 - len(status[: width - 4])) + " │"
        )
        lines.append("├" + "─" * (width - 2) + "┤")

        # Citizens grid
        grid = self._build_citizen_grid()
        if grid:
            grid_str = grid.project(RenderTarget.CLI)
            for line in grid_str.split("\n"):
                # Pad or truncate line
                padded = line[: width - 4]
                lines.append("│ " + padded + " " * (width - 4 - len(padded)) + " │")
        else:
            lines.append("│ " + "(no citizens)" + " " * (width - 4 - 13) + " │")

        # Footer
        lines.append("├" + "─" * (width - 2) + "┤")
        footer = (
            f"Entropy: {state.entropy_budget:.2f} │ "
            f"Events: {state.total_events} │ "
            f"Tokens: {state.total_tokens}"
        )
        lines.append(
            "│ " + footer[: width - 4] + " " * (width - 4 - len(footer[: width - 4])) + " │"
        )
        lines.append("└" + "─" * (width - 2) + "┘")

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich Panel with grid."""
        try:
            from rich.columns import Columns
            from rich.console import Group
            from rich.panel import Panel
            from rich.text import Text

            state = self.state.value

            # Build content - list of Rich renderables (Text, Columns, etc.)
            content_parts: list[Any] = []

            # Status
            status = Text()
            status.append("Colony: ", style="dim")
            status.append(f"{state.colony_id[:12]} ", style="bold")
            status.append("│ Citizens: ", style="dim")
            status.append(f"{len(state.citizens)} ", style="cyan")
            status.append("│ Phase: ", style="dim")
            status.append(f"{state.phase.name} ", style="yellow")
            status.append("│ Day: ", style="dim")
            status.append(f"{state.day}", style="bold")
            content_parts.append(status)

            # Citizens grid - build directly with Rich components
            if state.citizens:
                # Project each citizen to TUI (returns Rich Panel)
                citizen_panels = [
                    CitizenWidget(c).project(RenderTarget.TUI) for c in state.citizens
                ]
                # Use Rich Columns for grid layout
                grid_content = Columns(
                    citizen_panels,
                    equal=True,
                    expand=True,
                )
                content_parts.append(grid_content)
            else:
                content_parts.append(Text("(no citizens)", style="dim"))

            # Footer
            footer = Text()
            footer.append("\nEntropy: ", style="dim")
            footer.append(f"{state.entropy_budget:.2f} ", style="green")
            footer.append("│ Events: ", style="dim")
            footer.append(f"{state.total_events} ", style="cyan")
            footer.append("│ Tokens: ", style="dim")
            footer.append(f"{state.total_tokens}", style="yellow")
            content_parts.append(footer)

            return Panel(
                Group(*content_parts),
                title="[bold]AGENT TOWN DASHBOARD[/bold]",
                border_style="blue",
            )
        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML div with styled grid."""
        state = self.state.value

        # Grid
        grid = self._build_citizen_grid()
        grid_html = ""
        if grid:
            grid_html = grid.project(RenderTarget.MARIMO)
        else:
            grid_html = '<div style="color: #6c757d;">(no citizens)</div>'

        html = f"""
        <div class="kgents-colony-dashboard" data-colony-id="{state.colony_id}" style="
            font-family: system-ui, -apple-system, sans-serif;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
            background: #f8f9fa;
        ">
            <div class="header" style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                background: #212529;
                color: #ffffff;
            ">
                <span style="font-weight: bold; font-size: 1.1em;">AGENT TOWN DASHBOARD</span>
                <span style="color: #adb5bd;">
                    {state.phase.name} · Day {state.day}
                </span>
            </div>
            <div class="status-bar" style="
                display: flex;
                gap: 16px;
                padding: 8px 16px;
                background: #e9ecef;
                font-size: 0.875em;
                border-bottom: 1px solid #dee2e6;
            ">
                <span><strong>Colony:</strong> {state.colony_id[:12]}</span>
                <span><strong>Citizens:</strong> {len(state.citizens)}</span>
                <span><strong>Events:</strong> {state.total_events}</span>
            </div>
            <div class="grid-container" style="
                padding: 16px;
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                justify-content: flex-start;
            ">
                {grid_html}
            </div>
            <div class="footer" style="
                display: flex;
                justify-content: space-between;
                padding: 8px 16px;
                background: #e9ecef;
                font-size: 0.875em;
                border-top: 1px solid #dee2e6;
            ">
                <span>Entropy: {state.entropy_budget:.2f}</span>
                <span>Tokens: {state.total_tokens}</span>
            </div>
        </div>
        """
        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: full colony data."""
        state = self.state.value
        return {
            "type": "colony_dashboard",
            "colony_id": state.colony_id,
            "phase": state.phase.name,
            "day": state.day,
            "metrics": {
                "total_events": state.total_events,
                "total_tokens": state.total_tokens,
                "entropy_budget": state.entropy_budget,
            },
            "citizens": [
                {
                    "type": "citizen_card",
                    "citizen_id": c.citizen_id,
                    "name": c.name,
                    "archetype": c.archetype,
                    "phase": c.phase.name,
                    "nphase": c.nphase.name,
                    "mood": c.mood,
                    "region": c.region,
                    "capability": c.capability,
                    "entropy": c.entropy,
                    "activity": list(c.activity),
                    "eigenvectors": {
                        "warmth": c.warmth,
                        "curiosity": c.curiosity,
                        "trust": c.trust,
                    },
                }
                for c in state.citizens
            ],
            "grid_cols": state.grid_cols,
            "selected_citizen_id": state.selected_citizen_id,
        }

    def to_marimo(self, *, use_anywidget: bool = True) -> Any:
        """
        Convert to marimo-compatible widget.

        Args:
            use_anywidget: If True and anywidget available, return MarimoAdapter.
                           Otherwise, return HTML string.
        """
        from agents.i.reactive.adapters.marimo_widget import (
            MarimoAdapter,
            is_anywidget_available,
        )

        if use_anywidget and is_anywidget_available():
            return MarimoAdapter(self)
        return self._to_marimo()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TownPhase",
    "ColonyState",
    "ColonyDashboard",
]
