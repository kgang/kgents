"""
Tests for AgentTraceWidget - Agent observability visualization.
"""

from __future__ import annotations

import json

import pytest

from agents.i.reactive.adapters.marimo_trace import (
    AgentTraceState,
    AgentTraceWidget,
    SpanData,
    create_trace_widget,
)
from agents.i.reactive.widget import RenderTarget

# ============================================================
# SpanData Tests
# ============================================================


class TestSpanData:
    """Test SpanData dataclass."""

    def test_span_defaults(self):
        """SpanData has sensible defaults."""
        span = SpanData(span_id="test", name="test_span")

        assert span.span_id == "test"
        assert span.name == "test_span"
        assert span.kind == "internal"
        assert span.parent_id is None
        assert span.status == "unset"

    def test_span_with_attributes(self):
        """SpanData can hold attributes."""
        span = SpanData(
            span_id="llm-1",
            name="llm.generate",
            kind="llm_call",
            attributes={"tokens": 150, "model": "claude-3"},
        )

        assert span.attributes["tokens"] == 150
        assert span.attributes["model"] == "claude-3"

    def test_span_timing(self):
        """SpanData holds timing information."""
        span = SpanData(
            span_id="timed",
            name="timed_span",
            start_time_ms=100.0,
            end_time_ms=500.0,
        )

        assert span.start_time_ms == 100.0
        assert span.end_time_ms == 500.0
        # Duration
        duration = span.end_time_ms - span.start_time_ms
        assert duration == 400.0


# ============================================================
# AgentTraceState Tests
# ============================================================


class TestAgentTraceState:
    """Test AgentTraceState dataclass."""

    def test_state_defaults(self):
        """AgentTraceState has sensible defaults."""
        state = AgentTraceState()

        assert state.trace_id == ""
        assert state.spans == ()
        assert state.view == "timeline"
        assert state.total_latency_ms == 0.0

    def test_state_with_spans(self):
        """AgentTraceState can hold spans."""
        spans = (
            SpanData(span_id="1", name="span1"),
            SpanData(span_id="2", name="span2"),
        )
        state = AgentTraceState(
            trace_id="trace-1",
            spans=spans,
        )

        assert len(state.spans) == 2
        assert state.spans[0].name == "span1"


# ============================================================
# AgentTraceWidget Creation Tests
# ============================================================


class TestTraceWidgetCreation:
    """Test widget creation."""

    def test_create_empty_widget(self):
        """Empty widget can be created."""
        widget = AgentTraceWidget()

        assert widget.state.value.trace_id == ""
        assert len(widget.state.value.spans) == 0

    def test_create_with_state(self):
        """Widget can be created with initial state."""
        widget = AgentTraceWidget(
            AgentTraceState(
                trace_id="test-trace",
                root_agent="test-agent",
            )
        )

        assert widget.state.value.trace_id == "test-trace"
        assert widget.state.value.root_agent == "test-agent"

    def test_factory_function(self):
        """create_trace_widget factory works."""
        widget = create_trace_widget(
            trace_id="factory-trace",
            root_agent="factory-agent",
        )

        assert widget.state.value.trace_id == "factory-trace"
        assert widget.state.value.root_agent == "factory-agent"

    def test_factory_with_spans(self):
        """Factory calculates totals from spans."""
        spans = [
            SpanData(
                span_id="1",
                name="root",
                start_time_ms=0,
                end_time_ms=1000,
            ),
            SpanData(
                span_id="2",
                name="child",
                parent_id="1",
                start_time_ms=100,
                end_time_ms=500,
                attributes={"tokens": 100},
            ),
        ]
        widget = create_trace_widget(
            trace_id="calc-trace",
            root_agent="calc-agent",
            spans=spans,
        )

        state = widget.state.value
        assert state.total_latency_ms == 1000.0
        assert state.total_tokens == 100


# ============================================================
# Immutable Update Tests
# ============================================================


class TestImmutableUpdates:
    """Test immutable update methods."""

    def test_with_spans(self):
        """with_spans returns new widget."""
        widget = AgentTraceWidget(AgentTraceState(trace_id="orig"))
        new_spans = (SpanData(span_id="new", name="new_span"),)

        new_widget = widget.with_spans(new_spans)

        # Original unchanged
        assert len(widget.state.value.spans) == 0
        # New has spans
        assert len(new_widget.state.value.spans) == 1
        # Preserves other state
        assert new_widget.state.value.trace_id == "orig"

    def test_with_view(self):
        """with_view returns new widget with different view."""
        widget = AgentTraceWidget(AgentTraceState(view="timeline"))

        tree_widget = widget.with_view("tree")
        metrics_widget = widget.with_view("metrics")

        assert widget.state.value.view == "timeline"
        assert tree_widget.state.value.view == "tree"
        assert metrics_widget.state.value.view == "metrics"

    def test_add_span(self):
        """add_span appends and recalculates."""
        widget = AgentTraceWidget(AgentTraceState(trace_id="add-test"))

        span1 = SpanData(
            span_id="1",
            name="first",
            start_time_ms=0,
            end_time_ms=500,
        )
        widget2 = widget.add_span(span1)

        span2 = SpanData(
            span_id="2",
            name="second",
            start_time_ms=500,
            end_time_ms=1000,
            attributes={"tokens": 50},
        )
        widget3 = widget2.add_span(span2)

        assert len(widget.state.value.spans) == 0
        assert len(widget2.state.value.spans) == 1
        assert len(widget3.state.value.spans) == 2
        assert widget3.state.value.total_latency_ms == 1000.0
        assert widget3.state.value.total_tokens == 50


# ============================================================
# Projection Tests
# ============================================================


class TestProjections:
    """Test rendering to different targets."""

    def _sample_widget(self) -> AgentTraceWidget:
        """Create sample widget for testing."""
        return create_trace_widget(
            trace_id="proj-test",
            root_agent="proj-agent",
            spans=[
                SpanData(
                    span_id="1",
                    name="agent.run",
                    kind="agent",
                    start_time_ms=0,
                    end_time_ms=1000,
                    status="ok",
                ),
                SpanData(
                    span_id="2",
                    name="llm.call",
                    kind="llm_call",
                    parent_id="1",
                    start_time_ms=100,
                    end_time_ms=600,
                    status="ok",
                    attributes={"tokens": 100},
                ),
            ],
        )

    def test_cli_projection(self):
        """CLI projection produces text."""
        widget = self._sample_widget()
        output = widget.project(RenderTarget.CLI)

        assert isinstance(output, str)
        assert "proj-test" in output
        assert "agent.run" in output
        assert "llm.call" in output

    def test_cli_empty(self):
        """CLI handles empty traces."""
        widget = AgentTraceWidget(AgentTraceState(trace_id="empty"))
        output = widget.project(RenderTarget.CLI)

        assert "empty" in output
        assert "no spans" in output

    def test_marimo_projection(self):
        """MARIMO projection produces HTML."""
        widget = self._sample_widget()
        output = widget.project(RenderTarget.MARIMO)

        assert isinstance(output, str)
        assert "kgents-trace" in output
        assert "proj-test" in output
        assert "<svg" in output  # Timeline SVG

    def test_json_projection(self):
        """JSON projection produces dict."""
        widget = self._sample_widget()
        output = widget.project(RenderTarget.JSON)

        assert isinstance(output, dict)
        assert output["type"] == "agent_trace"
        assert output["trace_id"] == "proj-test"
        assert output["span_count"] == 2
        assert len(output["spans"]) == 2

    def test_json_span_structure(self):
        """JSON spans have correct structure."""
        widget = self._sample_widget()
        output = widget.project(RenderTarget.JSON)

        span = output["spans"][0]
        assert "span_id" in span
        assert "name" in span
        assert "kind" in span
        assert "duration_ms" in span
        assert span["duration_ms"] == 1000.0


# ============================================================
# Edge Cases
# ============================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_duration_span(self):
        """Handles zero-duration spans."""
        widget = create_trace_widget(
            trace_id="zero-dur",
            spans=[
                SpanData(
                    span_id="instant",
                    name="instant_span",
                    start_time_ms=100,
                    end_time_ms=100,  # Same time
                ),
            ],
        )

        # Should not error
        output = widget.project(RenderTarget.CLI)
        assert "instant_span" in output

    def test_error_status_span(self):
        """Error spans render correctly."""
        widget = create_trace_widget(
            trace_id="error-test",
            spans=[
                SpanData(
                    span_id="err",
                    name="error_span",
                    status="error",
                    start_time_ms=0,
                    end_time_ms=100,
                ),
            ],
        )

        cli_output = widget.project(RenderTarget.CLI)
        assert "✗" in cli_output  # Error indicator

        html_output = widget.project(RenderTarget.MARIMO)
        assert "#ef4444" in html_output  # Error color

    def test_deeply_nested_spans(self):
        """Handles nested span hierarchy."""
        widget = create_trace_widget(
            trace_id="nested",
            spans=[
                SpanData(span_id="1", name="root", start_time_ms=0, end_time_ms=1000),
                SpanData(
                    span_id="2",
                    name="child",
                    parent_id="1",
                    start_time_ms=100,
                    end_time_ms=900,
                ),
                SpanData(
                    span_id="3",
                    name="grandchild",
                    parent_id="2",
                    start_time_ms=200,
                    end_time_ms=800,
                ),
            ],
        )

        output = widget.project(RenderTarget.CLI)
        assert "root" in output
        assert "child" in output
        assert "grandchild" in output

    def test_many_spans(self):
        """Handles many spans."""
        spans = [
            SpanData(
                span_id=str(i),
                name=f"span_{i}",
                start_time_ms=i * 10.0,
                end_time_ms=(i + 1) * 10.0,
            )
            for i in range(50)
        ]
        widget = create_trace_widget(trace_id="many", spans=spans)

        output = widget.project(RenderTarget.JSON)
        assert output["span_count"] == 50


# ============================================================
# Integration with MarimoAdapter
# ============================================================


class TestMarimoIntegration:
    """Test integration with MarimoAdapter."""

    def test_adapter_wraps_trace(self):
        """MarimoAdapter can wrap AgentTraceWidget."""
        from agents.i.reactive.adapters import MarimoAdapter, is_anywidget_available

        widget = create_trace_widget(
            trace_id="adapter-test",
            root_agent="adapter-agent",
        )

        adapter = MarimoAdapter(widget)
        assert adapter.kgents_widget is widget

    @pytest.mark.skipif(
        not __import__(
            "agents.i.reactive.adapters", fromlist=["is_anywidget_available"]
        ).is_anywidget_available(),
        reason="anywidget not installed",
    )
    def test_adapter_syncs_trace_state(self):
        """Adapter syncs trace state to JSON."""
        from agents.i.reactive.adapters import MarimoAdapter

        widget = create_trace_widget(
            trace_id="sync-test",
            root_agent="sync-agent",
        )
        adapter = MarimoAdapter(widget)

        state = json.loads(adapter._state_json)
        assert state["type"] == "agent_trace"
        assert state["trace_id"] == "sync-test"
