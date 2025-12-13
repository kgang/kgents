"""
Tests for OTEL Bridge - TraceMonoid to OpenTelemetry Span conversion.

These tests verify:
- Conversion of events to SpanData
- Parent-child relationship mapping from DependencyGraph
- Batch export functionality
- Trace comparison utilities
"""

from __future__ import annotations

import pytest

from ..event import Event
from ..otel_bridge import (
    SpanData,
    TraceExportBatch,
    compare_traces,
    events_to_spans,
)
from ..trace_monoid import TraceMonoid

# === Fixtures ===


@pytest.fixture
def simple_monoid() -> TraceMonoid[dict[str, str]]:
    """Create a simple monoid with a few events."""
    monoid: TraceMonoid[dict[str, str]] = TraceMonoid()

    e1 = Event.create(
        content={"type": "call", "function": "main"},
        source="thread-1",
        event_id="e1",
        timestamp=1.0,
    )
    e2 = Event.create(
        content={"type": "call", "function": "helper"},
        source="thread-1",
        event_id="e2",
        timestamp=2.0,
    )

    monoid.append_mut(e1)
    monoid.append_mut(e2, depends_on={"e1"})

    return monoid


@pytest.fixture
def concurrent_monoid() -> TraceMonoid[dict[str, str]]:
    """Create a monoid with concurrent events."""
    monoid: TraceMonoid[dict[str, str]] = TraceMonoid()

    e1 = Event.create(
        content={"type": "call", "function": "task_a"},
        source="thread-1",
        event_id="e1",
        timestamp=1.0,
    )
    e2 = Event.create(
        content={"type": "call", "function": "task_b"},
        source="thread-2",
        event_id="e2",
        timestamp=1.5,
    )
    e3 = Event.create(
        content={"type": "call", "function": "join"},
        source="thread-1",
        event_id="e3",
        timestamp=2.0,
    )

    monoid.append_mut(e1)
    monoid.append_mut(e2)  # No dependency - concurrent with e1
    monoid.append_mut(e3, depends_on={"e1", "e2"})  # Depends on both

    return monoid


# === Test SpanData ===


class TestSpanData:
    """Tests for SpanData dataclass."""

    def test_span_data_creation(self) -> None:
        """SpanData can be created with required fields."""
        span = SpanData(
            name="test",
            trace_id="abc123",
            span_id="def456",
            parent_span_id=None,
            start_time_ns=1000000000,
            end_time_ns=2000000000,
        )

        assert span.name == "test"
        assert span.trace_id == "abc123"
        assert span.parent_span_id is None

    def test_span_data_duration(self) -> None:
        """SpanData computes duration correctly."""
        span = SpanData(
            name="test",
            trace_id="abc123",
            span_id="def456",
            parent_span_id=None,
            start_time_ns=1000000000,
            end_time_ns=1500000000,
        )

        assert span.duration_ns == 500000000  # 500ms in ns

    def test_span_data_duration_none_end(self) -> None:
        """SpanData duration is None if end_time is None."""
        span = SpanData(
            name="test",
            trace_id="abc123",
            span_id="def456",
            parent_span_id=None,
            start_time_ns=1000000000,
            end_time_ns=None,
        )

        assert span.duration_ns is None


# === Test events_to_spans ===


class TestEventsToSpans:
    """Tests for events_to_spans conversion."""

    def test_empty_monoid(self) -> None:
        """Empty monoid returns empty list."""
        monoid: TraceMonoid[dict[str, str]] = TraceMonoid()
        spans = events_to_spans(monoid)
        assert spans == []

    def test_single_event(self) -> None:
        """Single event becomes single span."""
        monoid: TraceMonoid[dict[str, str]] = TraceMonoid()
        e1 = Event.create(
            content={"type": "call", "function": "main"},
            source="thread-1",
            event_id="e1",
        )
        monoid.append_mut(e1)

        spans = events_to_spans(monoid)

        assert len(spans) == 1
        assert spans[0].name == "main"
        assert spans[0].parent_span_id is None  # Root span

    def test_parent_child_relationship(
        self,
        simple_monoid: TraceMonoid[dict[str, str]],
    ) -> None:
        """Child event has parent span ID from dependency."""
        spans = events_to_spans(simple_monoid)

        assert len(spans) == 2

        # Find spans by name
        main_span = next(s for s in spans if s.name == "main")
        helper_span = next(s for s in spans if s.name == "helper")

        # main is root
        assert main_span.parent_span_id is None

        # helper has main as parent
        assert helper_span.parent_span_id == main_span.span_id

    def test_concurrent_events(
        self,
        concurrent_monoid: TraceMonoid[dict[str, str]],
    ) -> None:
        """Concurrent events both become root spans."""
        spans = events_to_spans(concurrent_monoid)

        assert len(spans) == 3

        task_a = next(s for s in spans if s.name == "task_a")
        task_b = next(s for s in spans if s.name == "task_b")
        join = next(s for s in spans if s.name == "join")

        # Both task_a and task_b are roots
        assert task_a.parent_span_id is None
        assert task_b.parent_span_id is None

        # join has one of them as parent (first dependency)
        assert join.parent_span_id is not None

    def test_custom_trace_id(self, simple_monoid: TraceMonoid[dict[str, str]]) -> None:
        """Custom trace ID is used."""
        spans = events_to_spans(simple_monoid, trace_id="custom-trace-id")

        for span in spans:
            assert span.trace_id == "custom-trace-id"

    def test_attributes_include_weave_info(
        self,
        simple_monoid: TraceMonoid[dict[str, str]],
    ) -> None:
        """Span attributes include weave event info."""
        spans = events_to_spans(simple_monoid)

        for span in spans:
            assert "weave.event_id" in span.attributes
            assert "weave.source" in span.attributes

    def test_exception_event_has_error_status(self) -> None:
        """Exception events get ERROR status."""
        monoid: TraceMonoid[dict[str, str]] = TraceMonoid()
        e1 = Event.create(
            content={"type": "exception", "function": "failing"},
            source="thread-1",
            event_id="e1",
        )
        monoid.append_mut(e1)

        spans = events_to_spans(monoid)

        assert len(spans) == 1
        assert spans[0].status == "ERROR"


# === Test TraceExportBatch ===


class TestTraceExportBatch:
    """Tests for TraceExportBatch."""

    def test_add_trace(self) -> None:
        """Can add traces to batch."""
        batch = TraceExportBatch()
        monoid: TraceMonoid[dict[str, str]] = TraceMonoid()

        batch.add("test-trace", monoid)

        assert len(batch.traces) == 1
        assert batch.traces[0][0] == "test-trace"

    def test_to_span_data(self, simple_monoid: TraceMonoid[dict[str, str]]) -> None:
        """Can convert batch to SpanData dict."""
        batch = TraceExportBatch()
        batch.add("trace-1", simple_monoid)

        span_data = batch.to_span_data()

        assert "trace-1" in span_data
        assert len(span_data["trace-1"]) == 2


# === Test compare_traces ===


class TestCompareTraces:
    """Tests for trace comparison."""

    def test_compare_identical_traces(
        self,
        simple_monoid: TraceMonoid[dict[str, str]],
    ) -> None:
        """Comparing identical traces shows no differences."""
        result = compare_traces(simple_monoid, simple_monoid)

        assert result["added_functions"] == []
        assert result["removed_functions"] == []
        assert result["event_count_delta"] == 0

    def test_compare_added_function(self) -> None:
        """Comparison detects added functions."""
        before: TraceMonoid[dict[str, str]] = TraceMonoid()
        after: TraceMonoid[dict[str, str]] = TraceMonoid()

        e1 = Event.create(
            content={"function": "main"},
            source="t1",
            event_id="e1",
        )
        e2 = Event.create(
            content={"function": "new_func"},
            source="t1",
            event_id="e2",
        )

        before.append_mut(e1)
        after.append_mut(e1)
        after.append_mut(e2)

        result = compare_traces(before, after)

        assert "new_func" in result["added_functions"]
        assert result["event_count_delta"] == 1

    def test_compare_removed_function(self) -> None:
        """Comparison detects removed functions."""
        before: TraceMonoid[dict[str, str]] = TraceMonoid()
        after: TraceMonoid[dict[str, str]] = TraceMonoid()

        e1 = Event.create(
            content={"function": "main"},
            source="t1",
            event_id="e1",
        )
        e2 = Event.create(
            content={"function": "old_func"},
            source="t1",
            event_id="e2",
        )

        before.append_mut(e1)
        before.append_mut(e2)
        after.append_mut(e1)

        result = compare_traces(before, after)

        assert "old_func" in result["removed_functions"]
        assert result["event_count_delta"] == -1
