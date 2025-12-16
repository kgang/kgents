"""
GraphWidget: Charts and graphs.

Supports multiple chart types:
- LINE: Line chart
- BAR: Bar chart
- PIE: Pie chart
- SCATTER: Scatter plot
- AREA: Area chart (line with fill)
- RADAR: Radar/spider chart

For web, uses Chart.js. For CLI, uses ASCII art.

Example:
    widget = GraphWidget(GraphWidgetState(
        graph_type=GraphType.LINE,
        labels=("Jan", "Feb", "Mar"),
        datasets=(
            GraphDataset(label="Sales", data=(100, 150, 200)),
        ),
        title="Monthly Sales"
    ))
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget


class GraphType(Enum):
    """Chart/graph types."""

    LINE = auto()
    BAR = auto()
    PIE = auto()
    SCATTER = auto()
    AREA = auto()
    RADAR = auto()


@dataclass(frozen=True)
class GraphDataset:
    """
    Single dataset in a graph.

    Attributes:
        label: Dataset label for legend
        data: Data points
        color: Optional color override
        fill: Whether to fill area under line
    """

    label: str
    data: tuple[float, ...]
    color: str | None = None
    fill: bool = False


@dataclass(frozen=True)
class GraphWidgetState:
    """
    Immutable graph widget state.

    Attributes:
        graph_type: Type of chart
        labels: X-axis labels (for non-pie charts)
        datasets: Data series
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        show_legend: Show legend
        stacked: Stack bars/areas
        cli_width: Width in chars for CLI rendering
        cli_height: Height in chars for CLI rendering
    """

    graph_type: GraphType
    labels: tuple[str, ...] = ()
    datasets: tuple[GraphDataset, ...] = ()
    title: str | None = None
    x_label: str | None = None
    y_label: str | None = None
    show_legend: bool = True
    stacked: bool = False
    cli_width: int = 60
    cli_height: int = 10


class GraphWidget(KgentsWidget[GraphWidgetState]):
    """
    Chart/graph widget.

    Projections:
        - CLI: ASCII art chart (basic)
        - TUI: Rich chart (basic) or plotext if available
        - MARIMO: Chart.js configuration for mo.ui
        - JSON: State dict for API responses
    """

    def __init__(self, state: GraphWidgetState | None = None) -> None:
        self.state = Signal.of(state or GraphWidgetState(graph_type=GraphType.LINE))

    def project(self, target: RenderTarget) -> Any:
        """Project graph to target surface."""
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
        """CLI projection: ASCII chart."""
        s = self.state.value

        if not s.datasets:
            return "(no data)"

        # Title
        lines = []
        if s.title:
            lines.append(s.title.center(s.cli_width))
            lines.append("")

        if s.graph_type == GraphType.PIE:
            return self._pie_to_cli()

        # Get all data points for scaling
        all_data: list[float] = []
        for ds in s.datasets:
            all_data.extend(ds.data)

        if not all_data:
            return "(no data)"

        min_val = min(all_data)
        max_val = max(all_data)
        range_val = max_val - min_val or 1

        # Draw ASCII bar chart (simplified)
        for ds in s.datasets:
            if s.show_legend:
                lines.append(f"  {ds.label}:")
            for i, val in enumerate(ds.data):
                label = s.labels[i] if i < len(s.labels) else str(i)
                normalized = (val - min_val) / range_val
                bar_width = int(normalized * (s.cli_width - 15))
                bar = "█" * bar_width
                lines.append(f"  {label:>8} │{bar} {val:.1f}")
            lines.append("")

        return "\n".join(lines)

    def _pie_to_cli(self) -> str:
        """Render pie chart as ASCII percentages."""
        s = self.state.value
        lines = []

        if s.title:
            lines.append(s.title)
            lines.append("")

        if not s.datasets or not s.datasets[0].data:
            return "(no data)"

        data = s.datasets[0].data
        total = sum(data)
        if total == 0:
            return "(no data)"

        for i, val in enumerate(data):
            label = s.labels[i] if i < len(s.labels) else str(i)
            pct = (val / total) * 100
            bar_width = int(pct / 2)  # Scale to ~50 chars
            bar = "█" * bar_width
            lines.append(f"  {label:>12} │{bar} {pct:.1f}%")

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich or plotext."""
        try:
            # Try plotext first for better charts
            import plotext as plt

            s = self.state.value

            plt.clear_figure()
            if s.title:
                plt.title(s.title)

            for ds in s.datasets:
                x = list(range(len(ds.data)))
                y = list(ds.data)

                if s.graph_type == GraphType.BAR:
                    plt.bar(x, y, label=ds.label)
                elif s.graph_type == GraphType.SCATTER:
                    plt.scatter(x, y, label=ds.label)
                else:  # LINE, AREA
                    plt.plot(x, y, label=ds.label)

            if s.labels:
                plt.xticks(list(range(len(s.labels))), list(s.labels))

            if s.x_label:
                plt.xlabel(s.x_label)
            if s.y_label:
                plt.ylabel(s.y_label)

            plt.plotsize(s.cli_width, s.cli_height)
            return plt.build()

        except ImportError:
            # Fall back to CLI rendering
            from rich.text import Text

            return Text(self._to_cli())

    def _to_marimo(self) -> str:
        """MARIMO projection: Chart.js configuration."""
        s = self.state.value

        # Build Chart.js compatible JSON
        chart_type = {
            GraphType.LINE: "line",
            GraphType.BAR: "bar",
            GraphType.PIE: "pie",
            GraphType.SCATTER: "scatter",
            GraphType.AREA: "line",
            GraphType.RADAR: "radar",
        }.get(s.graph_type, "line")

        datasets_json = []
        default_colors = [
            "#3b82f6",
            "#ef4444",
            "#22c55e",
            "#f59e0b",
            "#8b5cf6",
            "#ec4899",
            "#06b6d4",
            "#f97316",
        ]

        for i, ds in enumerate(s.datasets):
            color = ds.color or default_colors[i % len(default_colors)]
            dataset = {
                "label": ds.label,
                "data": list(ds.data),
                "backgroundColor": color,
                "borderColor": color,
                "fill": ds.fill or s.graph_type == GraphType.AREA,
            }
            datasets_json.append(dataset)

        config = {
            "type": chart_type,
            "data": {
                "labels": list(s.labels),
                "datasets": datasets_json,
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"display": s.show_legend},
                    "title": {
                        "display": bool(s.title),
                        "text": s.title or "",
                    },
                },
                "scales": {
                    "x": {
                        "title": {"display": bool(s.x_label), "text": s.x_label or ""}
                    },
                    "y": {
                        "title": {"display": bool(s.y_label), "text": s.y_label or ""}
                    },
                }
                if chart_type not in ("pie", "radar")
                else {},
            },
        }

        import json

        config_json = json.dumps(config)

        return f"""
        <div class="kgents-graph" data-chart-config='{config_json}'>
            <canvas id="kgents-chart-{id(self)}"></canvas>
        </div>
        <script>
            (function() {{
                const ctx = document.getElementById('kgents-chart-{id(self)}');
                new Chart(ctx, {config_json});
            }})();
        </script>
        """

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: state dict for API responses."""
        s = self.state.value
        return {
            "type": "graph",
            "graphType": s.graph_type.name.lower(),
            "labels": list(s.labels),
            "datasets": [
                {
                    "label": ds.label,
                    "data": list(ds.data),
                    "color": ds.color,
                    "fill": ds.fill,
                }
                for ds in s.datasets
            ],
            "title": s.title,
            "xLabel": s.x_label,
            "yLabel": s.y_label,
            "showLegend": s.show_legend,
            "stacked": s.stacked,
        }


__all__ = ["GraphWidget", "GraphWidgetState", "GraphType", "GraphDataset"]
