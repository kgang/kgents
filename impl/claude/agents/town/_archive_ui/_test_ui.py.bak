"""
Tests for Agent Town UI components.

Verifies:
- MESA rendering
- LENS LOD levels
- TRACE span visualization
"""

from __future__ import annotations

import pytest
from agents.town.citizen import Citizen, Eigenvectors
from agents.town.environment import create_mpp_environment
from agents.town.flux import TownFlux
from agents.town.ui.lens import LOD_MODEL_MAP, LensView, render_lens
from agents.town.ui.mesa import MesaView, render_mesa
from agents.town.ui.trace import Span, SpanBuilder, TraceView, render_trace
from agents.town.ui.widgets import (
    citizen_badge,
    eigenvector_table,
    metric_bar,
    region_panel,
    relationship_table,
)


class TestWidgets:
    """Test shared widgets."""

    def test_metric_bar(self) -> None:
        """Metric bar renders."""
        bar = metric_bar("warmth", 0.7, max_value=1.0)
        assert "warmth" in str(bar)

    def test_citizen_badge(self) -> None:
        """Citizen badge renders."""
        badge = citizen_badge("Alice", "IDLE", "Innkeeper")
        text = str(badge)
        assert "Alice" in text

    def test_region_panel(self) -> None:
        """Region panel renders."""
        panel = region_panel(
            name="inn",
            description="A cozy inn",
            citizens=[("Alice", "IDLE", "Innkeeper")],
            density=0.5,
            connections=["square"],
        )
        assert panel is not None

    def test_eigenvector_table(self) -> None:
        """Eigenvector table renders."""
        ev = {"warmth": 0.8, "curiosity": 0.6}
        table = eigenvector_table(ev)
        assert table is not None

    def test_relationship_table(self) -> None:
        """Relationship table renders."""
        rels = {"bob": 0.5, "clara": -0.2}
        table = relationship_table(rels)
        assert table is not None


class TestMesaView:
    """Test MESA view."""

    def test_render_without_flux(self) -> None:
        """Can render without flux."""
        env = create_mpp_environment()
        view = MesaView()

        panel = view.render(env)
        assert panel is not None

    def test_render_with_flux(self) -> None:
        """Can render with flux."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        view = MesaView()

        panel = view.render(env, flux)
        assert panel is not None

    def test_render_mesa_string(self) -> None:
        """render_mesa returns string."""
        env = create_mpp_environment()

        output = render_mesa(env)
        assert isinstance(output, str)
        assert "AGENT TOWN" in output
        assert "smallville-mpp" in output

    def test_mesa_shows_regions(self) -> None:
        """MESA shows region names."""
        env = create_mpp_environment()

        output = render_mesa(env)
        assert "INN" in output.upper()
        assert "SQUARE" in output.upper()

    def test_mesa_shows_citizens(self) -> None:
        """MESA shows citizen names."""
        env = create_mpp_environment()

        output = render_mesa(env)
        assert "Alice" in output

    def test_mesa_shows_metrics(self) -> None:
        """MESA shows metrics."""
        env = create_mpp_environment()

        output = render_mesa(env)
        assert "METRICS" in output.upper() or "Tension" in output


class TestLensView:
    """Test LENS view."""

    def test_lod_model_map(self) -> None:
        """LOD model map is defined."""
        assert LOD_MODEL_MAP[0] == "cache"
        assert LOD_MODEL_MAP[1] == "haiku"
        assert LOD_MODEL_MAP[5] == "opus"

    def test_render_lod_0(self) -> None:
        """Can render LOD 0."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        view = LensView()

        panel = view.render(citizen, lod=0)
        assert panel is not None

    def test_render_lod_5(self) -> None:
        """Can render LOD 5 (abyss)."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        view = LensView()

        panel = view.render(citizen, lod=5)
        assert panel is not None

    def test_render_lens_string(self) -> None:
        """render_lens returns string."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")

        output = render_lens(citizen, lod=1)
        assert isinstance(output, str)
        assert "Alice" in output

    def test_lens_lod_0_minimal(self) -> None:
        """LOD 0 shows minimal info."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")

        output = render_lens(citizen, lod=0)
        assert "Alice" in output
        assert "inn" in output

    def test_lens_lod_1_shows_archetype(self) -> None:
        """LOD 1 shows archetype."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")

        output = render_lens(citizen, lod=1)
        assert "Innkeeper" in output

    def test_lens_lod_3_shows_eigenvectors(self) -> None:
        """LOD 3 shows eigenvectors."""
        citizen = Citizen(
            name="Alice",
            archetype="Innkeeper",
            region="inn",
            eigenvectors=Eigenvectors(warmth=0.8),
        )

        output = render_lens(citizen, lod=3)
        # Should show eigenvector names
        assert "warmth" in output.lower() or "Warmth" in output

    def test_lens_lod_5_shows_abyss(self) -> None:
        """LOD 5 shows opacity/abyss."""
        citizen = Citizen(name="Alice", archetype="Innkeeper", region="inn")

        output = render_lens(citizen, lod=5)
        assert "ABYSS" in output.upper() or "opacity" in output.lower()


class TestSpan:
    """Test Span class."""

    def test_basic_creation(self) -> None:
        """Can create a span."""
        span = Span(name="test", duration_ms=100)
        assert span.name == "test"
        assert span.duration_ms == 100

    def test_total_tokens(self) -> None:
        """Total tokens sums in/out and children."""
        parent = Span(
            name="parent",
            duration_ms=100,
            tokens_in=50,
            tokens_out=30,
        )
        child = Span(
            name="child",
            duration_ms=50,
            tokens_in=20,
            tokens_out=10,
        )
        parent.children.append(child)

        assert parent.total_tokens == 50 + 30 + 20 + 10

    def test_to_dict(self) -> None:
        """Can serialize to dict."""
        span = Span(name="test", duration_ms=100, tokens_in=50)
        d = span.to_dict()

        assert d["name"] == "test"
        assert d["duration_ms"] == 100
        assert d["tokens_in"] == 50


class TestSpanBuilder:
    """Test SpanBuilder."""

    def test_basic_build(self) -> None:
        """Can build a span."""
        builder = SpanBuilder("test")
        span = builder.finish()

        assert span.name == "test"
        assert span.success

    def test_with_attributes(self) -> None:
        """Can set attributes."""
        builder = SpanBuilder("test")
        builder.set_attributes({"key": "value"})
        span = builder.finish()

        assert span.attributes["key"] == "value"

    def test_with_tokens(self) -> None:
        """Can set tokens."""
        builder = SpanBuilder("test")
        builder.set_tokens(100, 50)
        span = builder.finish()

        assert span.tokens_in == 100
        assert span.tokens_out == 50

    def test_with_error(self) -> None:
        """Can mark as error."""
        builder = SpanBuilder("test")
        builder.set_error("Something failed")
        span = builder.finish()

        assert not span.success
        assert span.error == "Something failed"


class TestTraceView:
    """Test TRACE view."""

    def test_render_simple_span(self) -> None:
        """Can render a simple span."""
        span = Span(name="test", duration_ms=100, success=True)
        view = TraceView()

        panel = view.render(span)
        assert panel is not None

    def test_render_nested_spans(self) -> None:
        """Can render nested spans."""
        child = Span(name="child", duration_ms=50)
        parent = Span(name="parent", duration_ms=100, children=[child])
        view = TraceView()

        panel = view.render(parent)
        assert panel is not None

    def test_render_trace_string(self) -> None:
        """render_trace returns string."""
        span = Span(name="test", duration_ms=100, tokens_in=50)

        output = render_trace(span)
        assert isinstance(output, str)
        assert "test" in output

    def test_trace_shows_duration(self) -> None:
        """Trace shows duration."""
        span = Span(name="test", duration_ms=123)

        output = render_trace(span)
        assert "123" in output or "ms" in output

    def test_trace_shows_success(self) -> None:
        """Trace shows success/failure status."""
        success_span = Span(name="test", duration_ms=100, success=True)
        fail_span = Span(name="test", duration_ms=100, success=False)

        success_output = render_trace(success_span)
        fail_output = render_trace(fail_span)

        assert "✓" in success_output or "SUCCESS" in success_output.upper()
        assert (
            "✗" in fail_output
            or "ERROR" in fail_output.upper()
            or "PARTIAL" in fail_output.upper()
        )


class TestUIIntegration:
    """Test UI components together."""

    def test_mesa_and_lens_together(self) -> None:
        """Can render MESA and LENS for same environment."""
        env = create_mpp_environment()
        alice = env.get_citizen_by_name("Alice")
        assert alice is not None

        mesa_output = render_mesa(env)
        lens_output = render_lens(alice, lod=3)

        assert "Alice" in mesa_output
        assert "Alice" in lens_output

    def test_trace_for_operation(self) -> None:
        """Can create trace for a town operation."""
        builder = SpanBuilder("citizen.greet")
        builder.set_attributes({"citizen_a": "Alice", "citizen_b": "Bob"})
        builder.set_tokens(200, 0)
        span = builder.finish()

        output = render_trace(span)
        assert "greet" in output
