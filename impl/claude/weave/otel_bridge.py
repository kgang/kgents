"""
OTEL Bridge: Convert TraceMonoid to OpenTelemetry Spans.

Bridges the mathematical trace foundation (Mazurkiewicz traces) with
standard distributed tracing infrastructure. Enables:

1. Post-hoc export: Analyze a TraceMonoid, then export as OTEL spans
2. Batch processing: Export historical traces to observability backends
3. Trace comparison: Export before/after traces for diffing in Jaeger/Tempo

The key insight is that TraceMonoid's DependencyGraph maps directly to
OTEL's parent-child span relationships:
- Events with no dependencies become root spans
- Events with dependencies become children of their first dependency

Usage:
    from weave.otel_bridge import events_to_spans, export_trace

    # Export a completed trace
    with collector.trace() as monoid:
        my_function()

    # Later, export to OTEL
    export_trace(monoid, service_name="my-service")

    # Or convert and inspect
    span_data = events_to_spans(monoid)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.trace import SpanContext, SpanKind, Status, StatusCode

from .event import Event
from .trace_monoid import TraceMonoid

# === Span Data Structure ===


@dataclass
class SpanData:
    """
    Intermediate representation of a span for conversion.

    Captures the data needed to create an OTEL span without
    actually creating it (useful for inspection/testing).
    """

    name: str
    trace_id: str
    span_id: str
    parent_span_id: str | None
    start_time_ns: int
    end_time_ns: int | None
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "OK"
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def duration_ns(self) -> int | None:
        """Duration in nanoseconds."""
        if self.end_time_ns is None:
            return None
        return self.end_time_ns - self.start_time_ns


# === Conversion Functions ===


def events_to_spans(
    monoid: TraceMonoid[Any],
    trace_id: str | None = None,
) -> list[SpanData]:
    """
    Convert TraceMonoid events to SpanData for inspection or export.

    Uses the DependencyGraph to establish parent-child relationships:
    - Events with no dependencies become root spans
    - Events with dependencies get their first dependency as parent

    Args:
        monoid: TraceMonoid to convert
        trace_id: Optional trace ID (generated if not provided)

    Returns:
        List of SpanData representing the trace
    """
    import uuid

    if not monoid.events:
        return []

    # Generate trace ID if not provided
    trace_id = trace_id or str(uuid.uuid4()).replace("-", "")

    # Build event_id -> span_id mapping
    event_to_span: dict[str, str] = {}
    for event in monoid.events:
        event_to_span[event.id] = str(uuid.uuid4()).replace("-", "")[:16]

    # Get dependency graph
    graph = monoid.braid()

    # Build spans
    spans: list[SpanData] = []

    for event in monoid.events:
        content = event.content

        # Extract span name from content
        name: str
        if isinstance(content, dict):
            name = str(content.get("function", content.get("type", event.id)))
        elif hasattr(content, "function"):
            name = str(getattr(content, "function"))
        elif hasattr(content, "func_name"):
            name = str(getattr(content, "func_name"))
        else:
            name = str(event.id)

        # Find parent span
        parent_span_id: str | None = None
        deps = graph.get_dependencies(event.id)
        if deps:
            # Use first dependency as parent
            parent_id = next(iter(deps))
            parent_span_id = event_to_span.get(parent_id)

        # Build attributes
        attributes: dict[str, Any] = {
            "weave.event_id": event.id,
            "weave.source": event.source,
        }

        if isinstance(content, dict):
            for key in ("file", "line", "depth", "type"):
                if key in content:
                    attributes[f"weave.{key}"] = content[key]
        elif hasattr(content, "__dict__"):
            for key, value in content.__dict__.items():
                if isinstance(value, (str, int, float, bool)):
                    attributes[f"weave.{key}"] = value

        # Determine status
        status = "OK"
        if isinstance(content, dict) and content.get("type") == "exception":
            status = "ERROR"
        elif hasattr(content, "event_type") and getattr(content, "event_type") == "exception":
            status = "ERROR"

        # Convert timestamp to nanoseconds
        start_time_ns = int(event.timestamp * 1e9)

        # End time is estimated (we don't have explicit return times in basic TraceMonoid)
        # For proper end times, use TraceCollector which tracks returns
        end_time_ns = start_time_ns + 1_000_000  # Default 1ms

        spans.append(
            SpanData(
                name=name,
                trace_id=trace_id,
                span_id=event_to_span[event.id],
                parent_span_id=parent_span_id,
                start_time_ns=start_time_ns,
                end_time_ns=end_time_ns,
                attributes=attributes,
                status=status,
            )
        )

    return spans


def export_trace(
    monoid: TraceMonoid[Any],
    service_name: str = "kgents-weave",
    trace_id: str | None = None,
) -> None:
    """
    Export a TraceMonoid directly to the configured OTEL backend.

    This creates actual OTEL spans and exports them through the
    configured trace provider.

    Args:
        monoid: TraceMonoid to export
        service_name: Service name for the spans
        trace_id: Optional trace ID (generated if not provided)
    """
    if not monoid.events:
        return

    tracer = trace.get_tracer(f"{service_name}.export", "0.1.0")

    # Convert to SpanData first
    span_data_list = events_to_spans(monoid, trace_id)

    # Build span_id -> SpanData lookup
    _ = {s.span_id: s for s in span_data_list}  # For future use

    # Find root spans (no parent)
    roots = [s for s in span_data_list if s.parent_span_id is None]

    # Export recursively
    def export_span(data: SpanData, parent_context: Any = None) -> None:
        with tracer.start_as_current_span(
            data.name,
            attributes=data.attributes,
            kind=SpanKind.INTERNAL,
        ) as span:
            if data.status == "ERROR":
                span.set_status(Status(StatusCode.ERROR))
            else:
                span.set_status(Status(StatusCode.OK))

            # Find and export children
            children = [s for s in span_data_list if s.parent_span_id == data.span_id]
            for child in children:
                export_span(child)

    # Export all roots
    for root in roots:
        export_span(root)


# === Batch Export ===


@dataclass
class TraceExportBatch:
    """
    A batch of traces for export.

    Useful for exporting multiple traces at once, e.g., when
    replaying historical data or comparing before/after.
    """

    traces: list[tuple[str, TraceMonoid[Any]]] = field(default_factory=list)

    def add(self, name: str, monoid: TraceMonoid[Any]) -> None:
        """Add a named trace to the batch."""
        self.traces.append((name, monoid))

    def export_all(self, service_name: str = "kgents-weave") -> int:
        """
        Export all traces in the batch.

        Returns:
            Number of traces exported
        """
        count = 0
        for name, monoid in self.traces:
            if monoid.events:
                export_trace(monoid, f"{service_name}.{name}")
                count += 1
        return count

    def to_span_data(self) -> dict[str, list[SpanData]]:
        """
        Convert all traces to SpanData without exporting.

        Returns:
            Dict mapping trace names to SpanData lists
        """
        return {name: events_to_spans(monoid) for name, monoid in self.traces}


# === Comparison Utilities ===


def compare_traces(
    before: TraceMonoid[Any],
    after: TraceMonoid[Any],
) -> dict[str, Any]:
    """
    Compare two traces for behavioral changes.

    Useful for detecting performance regressions or behavioral drift.

    Args:
        before: Baseline trace
        after: New trace to compare

    Returns:
        Comparison summary with differences
    """
    before_spans = events_to_spans(before, "before")
    after_spans = events_to_spans(after, "after")

    # Extract function names
    before_funcs = {s.name for s in before_spans}
    after_funcs = {s.name for s in after_spans}

    # Find differences
    added = after_funcs - before_funcs
    removed = before_funcs - after_funcs
    common = before_funcs & after_funcs

    # Compare depths
    before_depths = {s.name: s.attributes.get("weave.depth", 0) for s in before_spans}
    after_depths = {s.name: s.attributes.get("weave.depth", 0) for s in after_spans}

    depth_changes = {}
    for name in common:
        if before_depths.get(name) != after_depths.get(name):
            depth_changes[name] = {
                "before": before_depths.get(name),
                "after": after_depths.get(name),
            }

    return {
        "added_functions": list(added),
        "removed_functions": list(removed),
        "common_functions": len(common),
        "depth_changes": depth_changes,
        "before_event_count": len(before.events),
        "after_event_count": len(after.events),
        "event_count_delta": len(after.events) - len(before.events),
    }


def export_comparison(
    before: TraceMonoid[Any],
    after: TraceMonoid[Any],
    service_name: str = "kgents-weave",
) -> None:
    """
    Export both traces with distinct trace IDs for side-by-side comparison.

    In Jaeger/Tempo, you can then compare these traces visually.

    Args:
        before: Baseline trace
        after: New trace to compare
        service_name: Service name prefix
    """
    export_trace(before, f"{service_name}.before")
    export_trace(after, f"{service_name}.after")
