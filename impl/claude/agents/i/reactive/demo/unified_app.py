"""
UnifiedApp: Same widgets, any target.

Wave 12 of the reactive substrate: Prove the functor by rendering
identical widget definitions to CLI, TUI, and Notebook targets.

Usage:
    # CLI mode (default)
    python -m agents.i.reactive.demo.unified_app

    # Explicit target
    python -m agents.i.reactive.demo.unified_app --target=cli
    python -m agents.i.reactive.demo.unified_app --target=tui
    python -m agents.i.reactive.demo.unified_app --target=json

    # Notebook mode (use the dedicated notebook file)
    marimo run impl/claude/agents/i/reactive/demo/unified_notebook.py

The key insight: The widget definition IS the UI. The target IS a functor application.

    project : KgentsWidget[S] -> Target -> Renderable[Target]

Same state, different projections. Zero rewrites.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    pass

TargetMode = Literal["cli", "tui", "marimo", "json"]


# =============================================================================
# UnifiedDashboard: The core data structure
# =============================================================================


@dataclass
class UnifiedDashboard:
    """
    A dashboard of widgets that renders to any target.

    This is the proof: define once, render everywhere.

    The UnifiedDashboard holds widget definitions (not renderings).
    Call `render(target)` to project all widgets to that target.

    Example:
        dashboard = create_sample_dashboard()

        # Same dashboard, different targets
        print(dashboard.render_cli())      # ASCII art
        tui_widgets = dashboard.render_tui()  # Textual widgets
        html = dashboard.render_marimo()   # HTML for anywidget
    """

    title: str = "kgents Unified Dashboard"
    agents: list[AgentCardWidget] = field(default_factory=list)
    metrics: list[SparklineWidget] = field(default_factory=list)
    capacities: list[BarWidget] = field(default_factory=list)

    @property
    def all_widgets(self) -> list[KgentsWidget[Any]]:
        """Get all widgets in the dashboard."""
        return [*self.agents, *self.metrics, *self.capacities]

    def render(self, target: RenderTarget) -> list[Any]:
        """
        Render all widgets to a target.

        This is the functor in action: same widget definitions,
        different output types based on target.

        Args:
            target: Which rendering target (CLI, TUI, MARIMO, JSON)

        Returns:
            List of rendered outputs appropriate for the target
        """
        results = []
        for agent in self.agents:
            results.append(agent.project(target))
        for metric in self.metrics:
            results.append(metric.project(target))
        for capacity in self.capacities:
            results.append(capacity.project(target))
        return results

    def render_cli(self) -> str:
        """Render entire dashboard as CLI text."""
        lines = [
            "=" * 60,
            f"  {self.title}",
            "=" * 60,
            "",
        ]

        if self.agents:
            lines.append("AGENTS")
            lines.append("-" * 40)
            for agent in self.agents:
                lines.append(agent.to_cli())
                lines.append("")

        if self.metrics:
            lines.append("METRICS")
            lines.append("-" * 40)
            for metric in self.metrics:
                lines.append(metric.to_cli())
            lines.append("")

        if self.capacities:
            lines.append("CAPACITIES")
            lines.append("-" * 40)
            for capacity in self.capacities:
                lines.append(capacity.to_cli())
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    def render_json(self) -> dict[str, Any]:
        """Render entire dashboard as JSON-serializable dict."""
        return {
            "title": self.title,
            "agents": [agent.to_json() for agent in self.agents],
            "metrics": [metric.to_json() for metric in self.metrics],
            "capacities": [capacity.to_json() for capacity in self.capacities],
        }

    def render_marimo_html(self) -> str:
        """Render dashboard as HTML for marimo."""
        # Use a light theme with good contrast
        html_parts = [
            '<div class="kgents-unified-dashboard" style="font-family: monospace; padding: 16px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; color: #212529;">',
            f'<h2 style="color: #212529; margin-bottom: 16px; border-bottom: 2px solid #dee2e6; padding-bottom: 8px;">{self.title}</h2>',
        ]

        if self.agents:
            html_parts.append(
                '<div class="kgents-agents" style="margin-bottom: 16px;">'
            )
            html_parts.append(
                '<h3 style="color: #0d6efd; margin-bottom: 8px;">Agents</h3>'
            )
            html_parts.append(
                '<div style="display: flex; flex-wrap: wrap; gap: 12px;">'
            )
            for agent in self.agents:
                html_parts.append(agent.to_marimo())
            html_parts.append("</div>")
            html_parts.append("</div>")

        if self.metrics:
            html_parts.append(
                '<div class="kgents-metrics" style="margin-bottom: 16px;">'
            )
            html_parts.append(
                '<h3 style="color: #198754; margin-bottom: 8px;">Metrics</h3>'
            )
            for metric in self.metrics:
                html_parts.append(metric.to_marimo())
            html_parts.append("</div>")

        if self.capacities:
            html_parts.append('<div class="kgents-capacities">')
            html_parts.append(
                '<h3 style="color: #fd7e14; margin-bottom: 8px;">Capacities</h3>'
            )
            for capacity in self.capacities:
                html_parts.append(capacity.to_marimo())
            html_parts.append("</div>")

        html_parts.append("</div>")
        return "\n".join(html_parts)


# =============================================================================
# Sample Dashboard Creation
# =============================================================================


def create_sample_dashboard() -> UnifiedDashboard:
    """
    Create a sample dashboard for demonstration.

    This dashboard shows the range of widgets available:
    - AgentCard: Full agent representation with glyph, sparkline, bar
    - Sparkline: Time-series mini-chart
    - Bar: Capacity/progress indicator
    """
    return UnifiedDashboard(
        title="kgents Unified Demo - Wave 12",
        agents=[
            AgentCardWidget(
                AgentCardState(
                    agent_id="kgent-primary",
                    name="Primary Agent",
                    phase="active",
                    activity=(0.3, 0.5, 0.7, 0.8, 0.6, 0.9, 0.7, 0.8, 0.6, 0.9),
                    capability=0.9,
                    entropy=0.05,
                    breathing=True,
                    style="full",
                )
            ),
            AgentCardWidget(
                AgentCardState(
                    agent_id="kgent-secondary",
                    name="Secondary Agent",
                    phase="waiting",
                    activity=(0.2, 0.3, 0.4, 0.3, 0.2, 0.3, 0.4, 0.3),
                    capability=0.7,
                    entropy=0.02,
                    breathing=False,
                    style="full",
                )
            ),
            AgentCardWidget(
                AgentCardState(
                    agent_id="kgent-monitor",
                    name="Monitor Agent",
                    phase="idle",
                    activity=(0.1, 0.1, 0.1, 0.2, 0.1, 0.1),
                    capability=1.0,
                    entropy=0.0,
                    style="compact",
                )
            ),
        ],
        metrics=[
            SparklineWidget(
                SparklineState(
                    values=tuple(i / 20 for i in range(20)),
                    label="Throughput",
                    max_length=20,
                )
            ),
            SparklineWidget(
                SparklineState(
                    values=(0.8, 0.6, 0.7, 0.5, 0.4, 0.6, 0.7, 0.8, 0.9, 0.7, 0.6, 0.5),
                    label="Latency",
                    max_length=20,
                )
            ),
        ],
        capacities=[
            BarWidget(
                BarState(
                    value=0.75,
                    width=20,
                    style="solid",
                    label="Memory",
                )
            ),
            BarWidget(
                BarState(
                    value=0.45,
                    width=20,
                    style="solid",
                    label="CPU",
                )
            ),
            BarWidget(
                BarState(
                    value=0.92,
                    width=20,
                    style="gradient",
                    label="Disk",
                )
            ),
        ],
    )


# =============================================================================
# CLI Runner
# =============================================================================


def run_cli(dashboard: UnifiedDashboard) -> None:
    """
    Run in CLI mode - plain text output.

    This is the simplest projection: widgets -> ASCII strings.
    """
    print(dashboard.render_cli())


# =============================================================================
# JSON Runner
# =============================================================================


def run_json(dashboard: UnifiedDashboard) -> None:
    """
    Run in JSON mode - serializable output.

    Useful for API responses, logging, or data export.
    """
    output = dashboard.render_json()
    print(json.dumps(output, indent=2))


# =============================================================================
# TUI Runner (Textual)
# =============================================================================


def run_tui(dashboard: UnifiedDashboard) -> None:
    """
    Run in TUI mode - interactive Textual application.

    This demonstrates the full TUI adapter stack:
    - TextualAdapter wraps each KgentsWidget
    - FlexContainer handles layout
    - ThemeBinding manages dark/light modes
    """
    try:
        from agents.i.reactive.adapters import TextualAdapter
        from textual.app import App, ComposeResult
        from textual.binding import Binding
        from textual.containers import Horizontal, Vertical
        from textual.widgets import Footer, Header, Static

    except ImportError as e:
        print(f"TUI mode requires textual: {e}")
        print("Install with: uv pip install textual")
        sys.exit(1)

    class UnifiedTUIApp(App[None]):
        """Wave 12 Unified Demo - TUI Mode."""

        TITLE = dashboard.title
        SUB_TITLE = "One definition, three targets"

        CSS = """
        Screen {
            background: $background;
        }

        #main-container {
            width: 100%;
            height: 100%;
            padding: 1;
        }

        .section-header {
            dock: top;
            height: 1;
            background: $primary;
            color: $text;
            text-align: center;
        }

        .agent-row {
            layout: horizontal;
            height: auto;
            margin-bottom: 1;
        }

        .agent-card {
            width: 28;
            height: auto;
            border: round $primary;
            padding: 1;
            margin-right: 1;
        }

        .metrics-section {
            margin-bottom: 1;
        }

        .metric-widget {
            height: auto;
            margin-bottom: 0;
        }

        .capacity-widget {
            height: 1;
        }
        """

        BINDINGS = [
            Binding("q", "quit", "Quit"),
            Binding("r", "refresh", "Refresh"),
        ]

        def compose(self) -> ComposeResult:
            yield Header()

            with Vertical(id="main-container"):
                # Agents section
                yield Static("AGENTS", classes="section-header")
                with Horizontal(classes="agent-row"):
                    for agent in dashboard.agents:
                        yield TextualAdapter(agent, classes="agent-card")

                # Metrics section
                yield Static("METRICS", classes="section-header")
                with Vertical(classes="metrics-section"):
                    for metric in dashboard.metrics:
                        yield TextualAdapter(metric, classes="metric-widget")

                # Capacities section
                yield Static("CAPACITIES", classes="section-header")
                with Vertical():
                    for capacity in dashboard.capacities:
                        yield TextualAdapter(capacity, classes="capacity-widget")

            yield Footer()

        def action_refresh(self) -> None:
            """Refresh all widgets."""
            self.refresh()
            self.notify("Dashboard refreshed")

    app = UnifiedTUIApp()
    app.run()


# =============================================================================
# Performance Comparison
# =============================================================================


def benchmark_renders(
    dashboard: UnifiedDashboard, iterations: int = 1000
) -> dict[str, float]:
    """
    Benchmark render times across targets.

    Returns dict mapping target name to renders per second.
    """
    import time

    results: dict[str, float] = {}

    # CLI benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        dashboard.render_cli()
    cli_time = time.perf_counter() - start
    results["cli"] = iterations / cli_time

    # JSON benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        dashboard.render_json()
    json_time = time.perf_counter() - start
    results["json"] = iterations / json_time

    # MARIMO benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        dashboard.render_marimo_html()
    marimo_time = time.perf_counter() - start
    results["marimo"] = iterations / marimo_time

    return results


def run_benchmark() -> None:
    """Run and display benchmark results."""
    dashboard = create_sample_dashboard()
    iterations = 1000

    print(f"\nBenchmarking {iterations} iterations per target...")
    results = benchmark_renders(dashboard, iterations)

    print("\n" + "=" * 40)
    print("RENDER PERFORMANCE")
    print("=" * 40)
    for target, rps in sorted(results.items(), key=lambda x: -x[1]):
        print(f"  {target.upper():8} {rps:,.0f} renders/sec")
    print("=" * 40)


# =============================================================================
# Side-by-Side Comparison
# =============================================================================


def capture_comparison() -> dict[str, Any]:
    """
    Generate comparison data for documentation.

    Returns dict with CLI, JSON, and HTML outputs for the same widgets.
    """
    dashboard = create_sample_dashboard()

    return {
        "cli": dashboard.render_cli(),
        "json": dashboard.render_json(),
        "html": dashboard.render_marimo_html(),
    }


# =============================================================================
# Target Auto-Detection (void.entropy.sip exploration)
# =============================================================================


def detect_target() -> TargetMode:
    """
    Auto-detect the appropriate rendering target.

    Detection order:
    1. Check for marimo notebook context
    2. Check for interactive terminal (potential TUI)
    3. Default to CLI

    This is speculative - user can always override with --target.
    """
    import os

    # Check for marimo
    try:
        import marimo

        # If we got here via marimo run, prefer marimo
        if hasattr(marimo, "running_in_notebook"):
            return "marimo"
    except ImportError:
        pass

    # Check for interactive terminal with TUI capability
    if sys.stdout.isatty() and os.environ.get("TERM"):
        # Could run TUI, but default to CLI for simplicity
        # User can explicitly request TUI with --target=tui
        pass

    return "cli"


# =============================================================================
# Entry Point
# =============================================================================


def main() -> None:
    """Main entry point for unified demo."""
    parser = argparse.ArgumentParser(
        description="kgents Unified Demo - Wave 12",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m agents.i.reactive.demo.unified_app              # CLI mode
    python -m agents.i.reactive.demo.unified_app --target=tui  # TUI mode
    python -m agents.i.reactive.demo.unified_app --target=json # JSON output
    python -m agents.i.reactive.demo.unified_app --benchmark   # Performance test

For marimo notebook:
    marimo run impl/claude/agents/i/reactive/demo/unified_notebook.py
        """,
    )
    parser.add_argument(
        "--target",
        "-t",
        choices=["cli", "tui", "json", "auto"],
        default="auto",
        help="Rendering target (default: auto-detect)",
    )
    parser.add_argument(
        "--benchmark",
        "-b",
        action="store_true",
        help="Run performance benchmark",
    )
    parser.add_argument(
        "--compare",
        "-c",
        action="store_true",
        help="Output comparison data (JSON with all targets)",
    )

    args = parser.parse_args()

    # Handle special modes
    if args.benchmark:
        run_benchmark()
        return

    if args.compare:
        comparison = capture_comparison()
        print(json.dumps(comparison, indent=2))
        return

    # Create dashboard
    dashboard = create_sample_dashboard()

    # Determine target
    target = args.target if args.target != "auto" else detect_target()

    # Run appropriate mode
    match target:
        case "cli":
            run_cli(dashboard)
        case "tui":
            run_tui(dashboard)
        case "json":
            run_json(dashboard)
        case "marimo":
            # When run as script with --target=marimo, output HTML
            print(dashboard.render_marimo_html())
        case _:
            run_cli(dashboard)


if __name__ == "__main__":
    main()
