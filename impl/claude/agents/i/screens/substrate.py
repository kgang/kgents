"""
SubstrateScreen - Visualization of SharedSubstrate Memory State.

Shows the M-gent substrate architecture:
- Allocation pressure meters per agent
- Routing gradient heatmap
- Compaction event timeline
- Promotion/demotion status

This screen provides real-time insight into the shared memory substrate,
complementing the Four Pillars view of MemoryMapScreen.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, ProgressBar, Static

from .base import KgentsScreen

if TYPE_CHECKING:
    from agents.m import (
        Allocation,
        CategoricalRouter,
        SharedSubstrate,
    )
    from agents.m.compaction import Compactor


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class AllocationView:
    """View model for allocation display."""

    agent_id: str
    human_label: str
    pattern_count: int
    max_patterns: int
    usage_ratio: float
    at_soft_limit: bool
    last_access: datetime | None = None
    is_dedicated: bool = False


@dataclass
class GradientView:
    """View model for gradient display."""

    concept: str
    agent_id: str
    intensity: float
    trace_count: int


@dataclass
class CompactionEventView:
    """View model for compaction event display."""

    allocation_id: str
    patterns_before: int
    patterns_after: int
    strategy: str
    timestamp: datetime


# =============================================================================
# Widgets
# =============================================================================


class AllocationMeterWidget(Static):
    """Widget showing allocation pressure for a single agent."""

    def __init__(
        self,
        allocation: AllocationView,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._allocation = allocation

    def render(self) -> str:
        """Render the allocation meter."""
        a = self._allocation

        # Status indicator
        if a.is_dedicated:
            status = "[bold magenta]DEDICATED[/]"
        elif a.at_soft_limit:
            status = "[bold yellow]PRESSURE[/]"
        elif a.usage_ratio > 0.5:
            status = "[bold cyan]ACTIVE[/]"
        else:
            status = "[dim]IDLE[/]"

        # Progress bar visualization
        bar_width = 20
        filled = int(a.usage_ratio * bar_width)
        empty = bar_width - filled

        if a.usage_ratio >= 0.8:
            bar_color = "red"
        elif a.usage_ratio >= 0.5:
            bar_color = "yellow"
        else:
            bar_color = "green"

        bar = f"[{bar_color}]{'█' * filled}[/][dim]{'░' * empty}[/]"

        # Last access time
        if a.last_access:
            age_seconds = (datetime.now() - a.last_access).total_seconds()
            if age_seconds < 60:
                age_str = f"{int(age_seconds)}s ago"
            elif age_seconds < 3600:
                age_str = f"{int(age_seconds / 60)}m ago"
            else:
                age_str = f"{int(age_seconds / 3600)}h ago"
        else:
            age_str = "never"

        return (
            f"[bold]{a.agent_id}[/]\n"
            f"  {a.human_label}\n"
            f"  {bar} {a.pattern_count}/{a.max_patterns} ({a.usage_ratio:.0%})\n"
            f"  Status: {status}  Last: {age_str}"
        )


class GradientHeatmapWidget(Static):
    """Widget showing routing gradient heatmap."""

    def __init__(
        self,
        gradients: list[GradientView],
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._gradients = gradients

    def render(self) -> str:
        """Render the gradient heatmap."""
        if not self._gradients:
            return "[dim]No active gradients[/]"

        lines = ["[bold]Routing Gradients[/]\n"]

        # Sort by intensity (descending)
        sorted_gradients = sorted(
            self._gradients, key=lambda g: g.intensity, reverse=True
        )[:10]  # Top 10

        # Find max intensity for normalization
        max_intensity = (
            max(g.intensity for g in sorted_gradients) if sorted_gradients else 1.0
        )

        for g in sorted_gradients:
            # Normalize intensity for color
            normalized = g.intensity / max_intensity

            # Heat color based on intensity
            if normalized >= 0.8:
                color = "red"
            elif normalized >= 0.6:
                color = "orange1"
            elif normalized >= 0.4:
                color = "yellow"
            elif normalized >= 0.2:
                color = "cyan"
            else:
                color = "blue"

            # Heat bar
            heat_width = 10
            heat_filled = int(normalized * heat_width)
            heat_bar = f"[{color}]{'▓' * heat_filled}[/][dim]{'░' * (heat_width - heat_filled)}[/]"

            lines.append(
                f"  {heat_bar} {g.concept[:20]:<20} → {g.agent_id} ({g.trace_count} traces)"
            )

        return "\n".join(lines)


class CompactionTimelineWidget(Static):
    """Widget showing compaction event timeline."""

    def __init__(
        self,
        events: list[CompactionEventView],
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._events = events

    def render(self) -> str:
        """Render the compaction timeline."""
        if not self._events:
            return "[dim]No compaction events[/]"

        lines = ["[bold]Compaction Timeline[/]\n"]

        # Most recent first
        sorted_events = sorted(self._events, key=lambda e: e.timestamp, reverse=True)[
            :5
        ]  # Last 5

        for e in sorted_events:
            # Calculate compression ratio
            if e.patterns_before > 0:
                compression = 1.0 - (e.patterns_after / e.patterns_before)
            else:
                compression = 0.0

            # Time ago
            age = (datetime.now() - e.timestamp).total_seconds()
            if age < 60:
                time_str = f"{int(age)}s ago"
            elif age < 3600:
                time_str = f"{int(age / 60)}m ago"
            else:
                time_str = f"{int(age / 3600)}h ago"

            # Color based on compression
            if compression >= 0.3:
                color = "red"
            elif compression >= 0.1:
                color = "yellow"
            else:
                color = "green"

            lines.append(
                f"  [{color}]●[/] {time_str}: {e.allocation_id}\n"
                f"    {e.patterns_before} → {e.patterns_after} ({compression:.0%} compressed)"
                f" [{e.strategy}]"
            )

        return "\n".join(lines)


class SubstrateSummaryWidget(Static):
    """Widget showing overall substrate summary."""

    def __init__(
        self,
        stats: dict[str, Any],
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._stats = stats

    def render(self) -> str:
        """Render the substrate summary."""
        s = self._stats

        allocation_count = s.get("allocation_count", 0)
        dedicated_count = s.get("dedicated_count", 0)
        total_patterns = s.get("total_patterns", 0)

        return (
            f"[bold]Substrate Summary[/]\n\n"
            f"  Allocations: [cyan]{allocation_count}[/]\n"
            f"  Dedicated:   [magenta]{dedicated_count}[/]\n"
            f"  Patterns:    [yellow]{total_patterns:,}[/]\n"
        )


# =============================================================================
# Screen
# =============================================================================


class SubstrateScreen(KgentsScreen):
    """
    Substrate Dashboard - Visualization of SharedSubstrate state.

    Shows allocation pressure, routing gradients, compaction events,
    and overall substrate health.
    """

    CSS = """
    SubstrateScreen {
        background: #1a1a1a;
    }

    SubstrateScreen #main-container {
        width: 100%;
        height: 100%;
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
        padding: 1;
    }

    SubstrateScreen .panel {
        border: solid #4a4a5c;
        padding: 1;
        background: #252525;
    }

    SubstrateScreen .panel-title {
        text-style: bold;
        color: #e6a352;
        margin-bottom: 1;
    }

    SubstrateScreen .header-bar {
        dock: top;
        height: 3;
        background: #252525;
        border-bottom: solid #4a4a5c;
        padding: 1 2;
        color: #f5f0e6;
    }

    SubstrateScreen #allocation-panel {
        row-span: 2;
    }

    SubstrateScreen .allocation-meter {
        margin-bottom: 1;
        padding: 1;
        border: dashed #4a4a5c;
    }

    SubstrateScreen .hot {
        color: #ff6b6b;
    }

    SubstrateScreen .warm {
        color: #feca57;
    }

    SubstrateScreen .cool {
        color: #54a0ff;
    }

    SubstrateScreen .success {
        color: #1dd1a1;
    }

    SubstrateScreen .warning {
        color: #c97b84;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("c", "compact_all", "Compact All", show=True),
        Binding("p", "show_promotions", "Promotions", show=True),
        Binding("q", "quit", "Quit", show=False),
    ]

    ANCHOR = "allocation-panel"

    # Reactive state
    allocations: reactive[list[AllocationView]] = reactive([])
    gradients: reactive[list[GradientView]] = reactive([])
    compaction_events: reactive[list[CompactionEventView]] = reactive([])
    substrate_stats: reactive[dict[str, Any]] = reactive({})

    def __init__(
        self,
        substrate: "SharedSubstrate[Any] | None" = None,
        router: "CategoricalRouter | None" = None,
        compactor: "Compactor[Any] | None" = None,
        demo_mode: bool = False,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._demo_mode = demo_mode
        self._substrate = substrate
        self._router = router
        self._compactor = compactor

    def compose(self) -> ComposeResult:
        """Compose the substrate dashboard."""
        yield Header()

        with Container(id="main-container"):
            # Left: Allocation pressure meters
            with Vertical(id="allocation-panel", classes="panel"):
                yield Static("[bold]Allocation Pressure[/]", classes="panel-title")
                yield Static(id="allocations-content")

            # Top-right: Gradient heatmap
            with Vertical(id="gradient-panel", classes="panel"):
                yield Static("[bold]Routing Gradients[/]", classes="panel-title")
                yield Static(id="gradients-content")

            # Bottom-right: Summary and timeline
            with Vertical(id="summary-panel", classes="panel"):
                yield Static(id="summary-content")
                yield Static(id="timeline-content")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize data when screen is mounted."""
        if self._demo_mode:
            self._load_demo_data()
        else:
            self._load_live_data()

        # Set up refresh timer
        self.set_interval(2.0, self._refresh_data)

    def _load_demo_data(self) -> None:
        """Load demo data for visualization testing."""
        # Demo allocations
        self.allocations = [
            AllocationView(
                agent_id="kgent:working",
                human_label="K-gent working memory (session)",
                pattern_count=234,
                max_patterns=500,
                usage_ratio=0.47,
                at_soft_limit=False,
                last_access=datetime.now(),
            ),
            AllocationView(
                agent_id="kgent:dialogue",
                human_label="K-gent dialogue history",
                pattern_count=856,
                max_patterns=1000,
                usage_ratio=0.86,
                at_soft_limit=True,
                last_access=datetime.now(),
            ),
            AllocationView(
                agent_id="mgent:cartography",
                human_label="M-gent holographic cartography",
                pattern_count=1245,
                max_patterns=2000,
                usage_ratio=0.62,
                at_soft_limit=False,
            ),
            AllocationView(
                agent_id="dgent:unified",
                human_label="D-gent unified memory (dedicated)",
                pattern_count=3456,
                max_patterns=5000,
                usage_ratio=0.69,
                at_soft_limit=False,
                is_dedicated=True,
            ),
        ]

        # Demo gradients
        self.gradients = [
            GradientView("soul.dialogue.reflect", "kgent", 2.3, 15),
            GradientView("code.python.debugging", "bgent", 1.8, 12),
            GradientView("memory.crystal.retrieve", "mgent", 1.5, 8),
            GradientView("soul.eigenvector.aesthetic", "kgent", 1.2, 5),
            GradientView("data.persistence.save", "dgent", 0.9, 3),
        ]

        # Demo compaction events
        self.compaction_events = [
            CompactionEventView(
                allocation_id="kgent:dream",
                patterns_before=200,
                patterns_after=160,
                strategy="uniform",
                timestamp=datetime.now(),
            ),
            CompactionEventView(
                allocation_id="mgent:working",
                patterns_before=450,
                patterns_after=350,
                strategy="pressure_based",
                timestamp=datetime.now(),
            ),
        ]

        # Demo stats
        self.substrate_stats = {
            "allocation_count": 4,
            "dedicated_count": 1,
            "total_patterns": 5791,
        }

        self._update_display()

    def _load_live_data(self) -> None:
        """Load live data from substrate."""
        if self._substrate is None:
            self._load_demo_data()
            return

        # Load allocations
        allocations = []
        for agent_id, allocation in self._substrate.allocations.items():
            allocations.append(
                AllocationView(
                    agent_id=str(agent_id),
                    human_label=allocation.lifecycle.human_label,
                    pattern_count=allocation.pattern_count,
                    max_patterns=allocation.quota.max_patterns,
                    usage_ratio=allocation.usage_ratio(),
                    at_soft_limit=allocation.is_at_soft_limit(),
                    last_access=allocation.last_accessed,
                )
            )

        # Add dedicated crystals
        for agent_id, dedicated in self._substrate.dedicated_crystals.items():
            # Dedicated crystals don't have quotas, use large max
            allocations.append(
                AllocationView(
                    agent_id=str(agent_id),
                    human_label=f"{agent_id} (dedicated crystal)",
                    pattern_count=len(dedicated.crystal.concepts),
                    max_patterns=10000,  # No real limit
                    usage_ratio=0.0,  # Not applicable
                    at_soft_limit=False,
                    is_dedicated=True,
                )
            )

        self.allocations = allocations
        self.substrate_stats = self._substrate.stats()
        self._update_display()

    def _refresh_data(self) -> None:
        """Refresh data periodically."""
        if self._demo_mode:
            # Demo mode: slightly randomize values
            import random

            for a in self.allocations:
                delta = random.randint(-5, 10)
                a.pattern_count = max(0, min(a.max_patterns, a.pattern_count + delta))
                a.usage_ratio = a.pattern_count / a.max_patterns
                a.at_soft_limit = a.usage_ratio >= 0.8
            self._update_display()
        else:
            self._load_live_data()

    def _update_display(self) -> None:
        """Update the display widgets with current data."""
        # Update allocations
        allocations_content = self.query_one("#allocations-content", Static)
        if self.allocations:
            lines = []
            for a in self.allocations:
                widget = AllocationMeterWidget(a)
                lines.append(widget.render())
            allocations_content.update("\n\n".join(lines))
        else:
            allocations_content.update("[dim]No allocations[/]")

        # Update gradients
        gradients_content = self.query_one("#gradients-content", Static)
        heatmap_widget = GradientHeatmapWidget(self.gradients)
        gradients_content.update(heatmap_widget.render())

        # Update summary
        summary_content = self.query_one("#summary-content", Static)
        summary_widget = SubstrateSummaryWidget(self.substrate_stats)
        summary_content.update(summary_widget.render())

        # Update timeline
        timeline_content = self.query_one("#timeline-content", Static)
        timeline_widget = CompactionTimelineWidget(self.compaction_events)
        timeline_content.update(timeline_widget.render())

    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Manually refresh data."""
        if self._demo_mode:
            self._load_demo_data()
        else:
            self._load_live_data()

    async def action_compact_all(self) -> None:
        """Trigger compaction on all allocations."""
        if self._substrate is None or self._demo_mode:
            self.notify("Compaction not available in demo mode")
            return

        count = 0
        for allocation in self._substrate.allocations.values():
            affected = await self._substrate.compact(allocation)
            if affected > 0:
                count += 1

        self.notify(f"Compacted {count} allocations")
        self._load_live_data()

    def action_show_promotions(self) -> None:
        """Show promotion-eligible allocations."""
        eligible = [
            a for a in self.allocations if a.at_soft_limit and not a.is_dedicated
        ]
        if eligible:
            names = ", ".join(a.agent_id for a in eligible)
            self.notify(f"Promotion candidates: {names}")
        else:
            self.notify("No allocations eligible for promotion")


# =============================================================================
# Factory Functions
# =============================================================================


def create_substrate_screen(
    substrate: "SharedSubstrate[Any] | None" = None,
    router: "CategoricalRouter | None" = None,
    compactor: "Compactor[Any] | None" = None,
    demo_mode: bool = True,
) -> SubstrateScreen:
    """
    Factory function to create SubstrateScreen.

    Args:
        substrate: The shared substrate to visualize
        router: Optional router for gradient data
        compactor: Optional compactor for event timeline
        demo_mode: Use demo data if True

    Returns:
        Configured SubstrateScreen
    """
    return SubstrateScreen(
        substrate=substrate,
        router=router,
        compactor=compactor,
        demo_mode=demo_mode,
    )
