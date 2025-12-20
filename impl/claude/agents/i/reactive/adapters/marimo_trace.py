"""
AgentTraceWidget: Visualize agent execution traces in notebooks.

Renders OpenTelemetry-compatible spans as interactive visualizations:
- Timeline view (horizontal bars showing duration)
- Tree view (nested call hierarchy)
- Metrics summary (latency, tokens, cost)

This is the "agent observability" bridge - making agent execution
visible and debuggable in computational notebooks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    pass

SpanKind = Literal["internal", "llm_call", "tool_use", "retrieval", "agent", "chain"]


@dataclass(frozen=True)
class SpanData:
    """
    A single span in an agent trace.

    Compatible with OpenTelemetry span structure.
    """

    span_id: str
    name: str
    kind: SpanKind = "internal"
    parent_id: str | None = None
    start_time_ms: float = 0.0
    end_time_ms: float = 0.0
    status: Literal["ok", "error", "unset"] = "unset"
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentTraceState:
    """
    State for visualizing agent execution traces.

    Holds a collection of spans representing an agent's execution.
    """

    trace_id: str = ""
    spans: tuple[SpanData, ...] = ()
    root_agent: str = ""
    total_latency_ms: float = 0.0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    # View mode
    view: Literal["timeline", "tree", "metrics"] = "timeline"
    # Time range for filtering
    start_time_ms: float = 0.0
    end_time_ms: float = 0.0


class AgentTraceWidget(KgentsWidget[AgentTraceState]):
    """
    Visualize agent execution traces in notebooks.

    Renders OpenTelemetry-compatible spans as:
    - Timeline view: Horizontal bars showing duration and overlap
    - Tree view: Nested call hierarchy
    - Metrics summary: Aggregated latency, tokens, cost

    Features:
    - Color-coded span kinds (LLM calls, tool use, retrieval)
    - Error highlighting
    - Interactive view switching (in marimo/Jupyter)
    - Drill-down into nested spans

    Example:
        from agents.i.reactive.adapters.marimo_trace import (
            AgentTraceWidget,
            AgentTraceState,
            SpanData,
        )

        spans = (
            SpanData(
                span_id="1",
                name="agent.run",
                kind="agent",
                start_time_ms=0,
                end_time_ms=1500,
            ),
            SpanData(
                span_id="2",
                name="llm.generate",
                kind="llm_call",
                parent_id="1",
                start_time_ms=100,
                end_time_ms=800,
                attributes={"tokens": 150},
            ),
            SpanData(
                span_id="3",
                name="tool.search",
                kind="tool_use",
                parent_id="1",
                start_time_ms=850,
                end_time_ms=1200,
            ),
        )

        widget = AgentTraceWidget(AgentTraceState(
            trace_id="trace-123",
            spans=spans,
            root_agent="kgent-1",
            total_latency_ms=1500,
        ))

        # In marimo:
        import marimo as mo
        from agents.i.reactive.adapters import MarimoAdapter
        mo.ui.anywidget(MarimoAdapter(widget))
    """

    state: Signal[AgentTraceState]

    def __init__(self, initial: AgentTraceState | None = None) -> None:
        self.state = Signal.of(initial or AgentTraceState())

    def with_spans(self, spans: tuple[SpanData, ...]) -> AgentTraceWidget:
        """Return new widget with updated spans. Immutable."""
        current = self.state.value
        return AgentTraceWidget(
            AgentTraceState(
                trace_id=current.trace_id,
                spans=spans,
                root_agent=current.root_agent,
                total_latency_ms=current.total_latency_ms,
                total_tokens=current.total_tokens,
                total_cost_usd=current.total_cost_usd,
                view=current.view,
                start_time_ms=current.start_time_ms,
                end_time_ms=current.end_time_ms,
            )
        )

    def with_view(self, view: Literal["timeline", "tree", "metrics"]) -> AgentTraceWidget:
        """Return new widget with different view mode. Immutable."""
        current = self.state.value
        return AgentTraceWidget(
            AgentTraceState(
                trace_id=current.trace_id,
                spans=current.spans,
                root_agent=current.root_agent,
                total_latency_ms=current.total_latency_ms,
                total_tokens=current.total_tokens,
                total_cost_usd=current.total_cost_usd,
                view=view,
                start_time_ms=current.start_time_ms,
                end_time_ms=current.end_time_ms,
            )
        )

    def add_span(self, span: SpanData) -> AgentTraceWidget:
        """Add a span to the trace. Immutable."""
        current = self.state.value
        new_spans = (*current.spans, span)

        # Recalculate totals - include all spans, 0 is a valid time
        end_times = [s.end_time_ms for s in new_spans]
        start_times = [s.start_time_ms for s in new_spans]

        if end_times and start_times:
            total_latency = max(end_times) - min(start_times)
            start_time = min(start_times)
            end_time = max(end_times)
        else:
            total_latency = 0
            start_time = 0
            end_time = 0

        total_tokens = sum(
            s.attributes.get("tokens", 0)
            for s in new_spans
            if isinstance(s.attributes.get("tokens"), int)
        )

        return AgentTraceWidget(
            AgentTraceState(
                trace_id=current.trace_id,
                spans=new_spans,
                root_agent=current.root_agent,
                total_latency_ms=total_latency,
                total_tokens=total_tokens,
                total_cost_usd=current.total_cost_usd,
                view=current.view,
                start_time_ms=start_time,
                end_time_ms=end_time,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        """
        Project this trace to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (ASCII timeline)
            - TUI: Rich Panel with trace visualization
            - MARIMO: HTML with SVG timeline
            - JSON: dict with full trace data
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
        """CLI projection: ASCII timeline."""
        state = self.state.value

        if not state.spans:
            return f"Trace {state.trace_id}: (no spans)"

        lines = [f"Trace: {state.trace_id}"]
        lines.append(f"Agent: {state.root_agent}")
        lines.append(f"Total: {state.total_latency_ms:.1f}ms")
        lines.append("-" * 40)

        # Build simple timeline
        if state.total_latency_ms > 0:
            scale = 30 / state.total_latency_ms  # 30 chars wide
        else:
            scale = 1

        for span in state.spans:
            indent = "  " if span.parent_id else ""
            start_pos = int(span.start_time_ms * scale)
            duration = max(1, int((span.end_time_ms - span.start_time_ms) * scale))

            bar = " " * start_pos + "█" * duration
            status_char = "✓" if span.status == "ok" else "✗" if span.status == "error" else "○"
            lines.append(f"{indent}{status_char} {span.name[:15]:<15} |{bar}")

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich Panel."""
        try:
            from rich.panel import Panel
            from rich.text import Text

            state = self.state.value
            content = Text()

            content.append(f"Trace: {state.trace_id}\n", style="bold")
            content.append(f"Agent: {state.root_agent}\n")
            content.append(f"Latency: {state.total_latency_ms:.1f}ms\n")
            content.append(f"Tokens: {state.total_tokens}\n")
            content.append("─" * 30 + "\n")

            for span in state.spans:
                style = (
                    "green" if span.status == "ok" else "red" if span.status == "error" else "dim"
                )
                indent = "  " if span.parent_id else ""
                duration = span.end_time_ms - span.start_time_ms
                content.append(f"{indent}• {span.name} ({duration:.1f}ms)\n", style=style)

            return Panel(content, title="Agent Trace", border_style="blue")

        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML with SVG timeline."""
        state = self.state.value

        html = '<div class="kgents-trace">'

        # Header
        html += '<div class="kgents-trace-header">'
        html += f'<span class="kgents-trace-id">Trace: {state.trace_id}</span>'
        html += f'<span class="kgents-trace-agent">Agent: {state.root_agent}</span>'
        html += "</div>"

        # Metrics
        html += '<div class="kgents-trace-metrics">'
        html += f'<span class="kgents-metric">⏱ {state.total_latency_ms:.1f}ms</span>'
        html += f'<span class="kgents-metric">🔤 {state.total_tokens} tokens</span>'
        if state.total_cost_usd > 0:
            html += f'<span class="kgents-metric">💰 ${state.total_cost_usd:.4f}</span>'
        html += "</div>"

        # Timeline SVG
        if state.spans and state.total_latency_ms > 0:
            html += self._render_timeline_svg(state)

        html += "</div>"
        return html

    def _render_timeline_svg(self, state: AgentTraceState) -> str:
        """Render SVG timeline of spans."""
        width = 400
        row_height = 24
        padding = 4
        label_width = 100

        # Calculate height based on span count
        height = len(state.spans) * row_height + 2 * padding

        svg = f'<svg class="kgents-trace-timeline" viewBox="0 0 {width} {height}" preserveAspectRatio="xMinYMin meet">'

        # Background
        svg += f'<rect width="{width}" height="{height}" fill="var(--kgents-surface, #1a1a2e)" rx="4"/>'

        # Time scale
        scale = (
            (width - label_width - 2 * padding) / state.total_latency_ms
            if state.total_latency_ms > 0
            else 1
        )
        bar_start_x = label_width + padding

        # Color mapping for span kinds
        colors = {
            "agent": "#3b82f6",
            "llm_call": "#8b5cf6",
            "tool_use": "#22c55e",
            "retrieval": "#eab308",
            "chain": "#06b6d4",
            "internal": "#6b7280",
        }

        for i, span in enumerate(state.spans):
            y = padding + i * row_height

            # Span bar
            x = bar_start_x + (span.start_time_ms - state.start_time_ms) * scale
            bar_width = max(4, (span.end_time_ms - span.start_time_ms) * scale)
            color = colors.get(span.kind, "#6b7280")

            # Error spans get red border
            stroke = "#ef4444" if span.status == "error" else "none"

            svg += f'<rect x="{x}" y="{y + 2}" width="{bar_width}" height="{row_height - 4}" '
            svg += f'fill="{color}" rx="2" stroke="{stroke}" stroke-width="1"/>'

            # Label
            svg += f'<text x="{padding}" y="{y + row_height / 2 + 4}" '
            svg += 'fill="var(--kgents-text, #e0e0e0)" font-size="10" font-family="monospace">'
            svg += f"{span.name[:12]}</text>"

        svg += "</svg>"
        return svg

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: full trace data."""
        state = self.state.value

        return {
            "type": "agent_trace",
            "trace_id": state.trace_id,
            "root_agent": state.root_agent,
            "total_latency_ms": state.total_latency_ms,
            "total_tokens": state.total_tokens,
            "total_cost_usd": state.total_cost_usd,
            "view": state.view,
            "span_count": len(state.spans),
            "spans": [
                {
                    "span_id": s.span_id,
                    "name": s.name,
                    "kind": s.kind,
                    "parent_id": s.parent_id,
                    "start_time_ms": s.start_time_ms,
                    "end_time_ms": s.end_time_ms,
                    "duration_ms": s.end_time_ms - s.start_time_ms,
                    "status": s.status,
                    "attributes": s.attributes,
                }
                for s in state.spans
            ],
        }


def create_trace_widget(
    trace_id: str = "",
    root_agent: str = "",
    spans: tuple[SpanData, ...] | list[SpanData] | None = None,
) -> AgentTraceWidget:
    """
    Create an agent trace widget.

    Args:
        trace_id: Trace identifier
        root_agent: Name of root agent
        spans: Collection of spans to visualize

    Returns:
        AgentTraceWidget instance
    """
    span_tuple = tuple(spans) if spans else ()

    # Calculate totals from spans - 0 is a valid time, don't filter it out
    if span_tuple:
        end_times = [s.end_time_ms for s in span_tuple]
        start_times = [s.start_time_ms for s in span_tuple]
        total_latency = max(end_times) - min(start_times) if end_times and start_times else 0
        start_time = min(start_times) if start_times else 0
        end_time = max(end_times) if end_times else 0
        total_tokens = sum(
            s.attributes.get("tokens", 0)
            for s in span_tuple
            if isinstance(s.attributes.get("tokens"), int)
        )
    else:
        total_latency = 0
        start_time = 0
        end_time = 0
        total_tokens = 0

    return AgentTraceWidget(
        AgentTraceState(
            trace_id=trace_id,
            spans=span_tuple,
            root_agent=root_agent,
            total_latency_ms=total_latency,
            total_tokens=total_tokens,
            start_time_ms=start_time,
            end_time_ms=end_time,
        )
    )
