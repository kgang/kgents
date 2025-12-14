"""
THE MESA: Town Overview Interface.

The MESA is not Westworld's control room—it's a seance table.
You cannot see everything. Citizens have the right to remain mysterious.

Features:
- Town map with citizen positions
- Metrics dashboard (tension, cooperation)
- Phase indicator
- Event stream

From Glissant: The right to opacity means the MESA shows
surfaces, not depths. Use LENS for deeper viewing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from agents.town.ui.widgets import (
    citizen_badge,
    metric_bar,
    metrics_table,
    region_panel,
)
from rich.console import Console, Group, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from agents.town.environment import TownEnvironment
    from agents.town.flux import TownFlux


@dataclass
class MesaView:
    """
    Terminal overview of Agent Town.

    The MESA provides a bird's-eye view of the simulation:
    - Region map with citizen positions
    - Aggregate metrics
    - Phase and day indicator
    - Controls hint

    From Glissant: This view respects opacity.
    You see positions, not psyches.
    """

    console: Console | None = None

    def __post_init__(self) -> None:
        if self.console is None:
            self.console = Console()

    def render(
        self,
        environment: "TownEnvironment",
        flux: "TownFlux | None" = None,
    ) -> Panel:
        """Render the MESA view."""
        return Panel(
            Group(
                self._render_header(environment, flux),
                Text(),
                self._render_map(environment),
                Text(),
                self._render_metrics(environment),
                Text(),
                self._render_controls(),
            ),
            title=f"[bold white]AGENT TOWN: {environment.name}[/bold white]",
            border_style="blue",
        )

    def _render_header(
        self,
        environment: "TownEnvironment",
        flux: "TownFlux | None",
    ) -> RenderableType:
        """Render the header with day/phase."""
        if flux:
            status = flux.get_status()
            day = status["day"]
            phase = status["phase"]
            phase_icon = "🌅" if phase == "MORNING" else "🌙"
            return Text(
                f"  Day {day} / {phase} {phase_icon}",
                style="bold cyan",
            )
        return Text("  (No simulation running)", style="dim")

    def _render_map(self, environment: "TownEnvironment") -> RenderableType:
        """Render the region map with citizens."""
        panels: list[RenderableType] = []

        for region_name, region in environment.regions.items():
            citizens_here = environment.get_citizens_in_region(region_name)
            density = environment.density_at(region_name)

            citizen_data = [(c.name, c.phase.name, c.archetype) for c in citizens_here]

            panel = region_panel(
                name=region_name,
                description=region.description,
                citizens=citizen_data,
                density=density,
                connections=region.connections,
            )
            panels.append(panel)

        return Group(*panels)

    def _render_metrics(self, environment: "TownEnvironment") -> RenderableType:
        """Render the metrics bar."""
        tension = environment.tension_index()
        coop = environment.cooperation_level()
        tokens = environment.total_token_spend
        surplus = environment.total_accursed_surplus()

        metrics = {
            "Tension Index": tension,
            "Cooperation": coop,
            "Accursed Surplus": surplus,
        }

        thresholds = {
            "Tension Index": (0.7, "HIGH DRAMA!"),
            "Accursed Surplus": (10.0, "NEEDS EXPENDITURE!"),
        }

        table = metrics_table(metrics, thresholds)

        # Add token count
        token_text = Text(f"\nTokens Spent: {tokens:,}", style="dim")

        return Group(
            Text("METRICS", style="bold magenta"),
            table,
            token_text,
        )

    def _render_controls(self) -> RenderableType:
        """Render the controls hint."""
        return Text(
            "  [S]tep  [L]ens <name>  [M]etrics  [B]udget  [?]Help",
            style="dim",
        )

    def print(
        self,
        environment: "TownEnvironment",
        flux: "TownFlux | None" = None,
    ) -> None:
        """Print the MESA view to console."""
        if self.console is None:
            self.console = Console()
        self.console.print(self.render(environment, flux))


def render_mesa(
    environment: "TownEnvironment",
    flux: "TownFlux | None" = None,
) -> str:
    """Render MESA view as string (for testing)."""
    console = Console(force_terminal=True, width=80)
    view = MesaView(console=console)

    with console.capture() as capture:
        view.print(environment, flux)

    return capture.get()


__all__ = ["MesaView", "render_mesa"]
