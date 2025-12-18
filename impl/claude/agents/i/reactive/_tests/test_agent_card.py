"""Tests for AgentCardWidget - full agent representation card."""

from __future__ import annotations

from typing import Any

import pytest

from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.widget import RenderTarget


class TestAgentCardState:
    """Tests for AgentCardState immutable state."""

    def test_default_state(self) -> None:
        """Default AgentCardState has expected values."""
        state = AgentCardState()
        assert state.agent_id == "agent"
        assert state.name == "Agent"
        assert state.phase == "idle"
        assert state.activity == ()
        assert state.capability == 1.0
        assert state.entropy == 0.0
        assert state.style == "full"
        assert state.breathing is True

    def test_state_is_frozen(self) -> None:
        """AgentCardState is immutable (frozen dataclass)."""
        state = AgentCardState(name="Test")
        with pytest.raises(Exception):
            state.name = "Modified"  # type: ignore[misc]

    def test_state_with_all_fields(self) -> None:
        """AgentCardState can be created with all fields."""
        state = AgentCardState(
            agent_id="kgent-1",
            name="Kent's Assistant",
            phase="active",
            activity=(0.2, 0.5, 0.8),
            capability=0.9,
            entropy=0.3,
            seed=42,
            t=1000.0,
            style="compact",
            breathing=False,
        )
        assert state.agent_id == "kgent-1"
        assert state.name == "Kent's Assistant"
        assert state.phase == "active"
        assert state.activity == (0.2, 0.5, 0.8)
        assert state.capability == 0.9
        assert state.style == "compact"


class TestAgentCardWidget:
    """Tests for AgentCardWidget reactive widget."""

    def test_create_with_default_state(self) -> None:
        """AgentCardWidget can be created with default state."""
        widget = AgentCardWidget()
        assert widget.state.value == AgentCardState()

    def test_create_with_initial_state(self) -> None:
        """AgentCardWidget can be created with initial state."""
        state = AgentCardState(name="Test Agent", phase="active")
        widget = AgentCardWidget(state)
        assert widget.state.value.name == "Test Agent"
        assert widget.state.value.phase == "active"

    def test_has_composed_slots(self) -> None:
        """AgentCardWidget has phase_glyph, activity, and capability slots."""
        widget = AgentCardWidget()
        assert "phase_glyph" in widget.slots
        assert "activity" in widget.slots
        assert "capability" in widget.slots

    def test_with_phase_returns_new_widget(self) -> None:
        """with_phase() returns new widget, doesn't mutate original."""
        original = AgentCardWidget(AgentCardState(phase="idle"))
        updated = original.with_phase("active")

        assert original.state.value.phase == "idle"
        assert updated.state.value.phase == "active"

    def test_with_activity_returns_new_widget(self) -> None:
        """with_activity() returns new widget with updated history."""
        original = AgentCardWidget(AgentCardState(activity=()))
        updated = original.with_activity([0.1, 0.5, 0.9])

        assert original.state.value.activity == ()
        assert updated.state.value.activity == (0.1, 0.5, 0.9)

    def test_with_activity_clamps_values(self) -> None:
        """with_activity() clamps values to 0.0-1.0 range."""
        widget = AgentCardWidget()
        updated = widget.with_activity([-0.5, 1.5, 0.5])

        assert updated.state.value.activity == (0.0, 1.0, 0.5)

    def test_push_activity_appends_value(self) -> None:
        """push_activity() appends new value to history."""
        original = AgentCardWidget(AgentCardState(activity=(0.1, 0.2)))
        updated = original.push_activity(0.9)

        assert updated.state.value.activity == (0.1, 0.2, 0.9)

    def test_push_activity_limits_history(self) -> None:
        """push_activity() keeps only last 20 values."""
        initial_activity = tuple(i / 25.0 for i in range(25))
        original = AgentCardWidget(AgentCardState(activity=initial_activity[:20]))
        updated = original.push_activity(0.99)

        assert len(updated.state.value.activity) == 20
        assert updated.state.value.activity[-1] == 0.99

    def test_with_capability_returns_new_widget(self) -> None:
        """with_capability() returns new widget."""
        original = AgentCardWidget(AgentCardState(capability=1.0))
        updated = original.with_capability(0.5)

        assert original.state.value.capability == 1.0
        assert updated.state.value.capability == 0.5

    def test_with_capability_clamps(self) -> None:
        """with_capability() clamps to 0.0-1.0 range."""
        widget = AgentCardWidget()
        assert widget.with_capability(-0.5).state.value.capability == 0.0
        assert widget.with_capability(1.5).state.value.capability == 1.0

    def test_with_time_returns_new_widget(self) -> None:
        """with_time() returns new widget."""
        original = AgentCardWidget(AgentCardState(t=0.0))
        updated = original.with_time(1000.0)

        assert original.state.value.t == 0.0
        assert updated.state.value.t == 1000.0

    def test_with_entropy_returns_new_widget(self) -> None:
        """with_entropy() returns new widget."""
        original = AgentCardWidget(AgentCardState(entropy=0.0))
        updated = original.with_entropy(0.5)

        assert original.state.value.entropy == 0.0
        assert updated.state.value.entropy == 0.5


class TestAgentCardProjectCLI:
    """Tests for CLI projection."""

    def test_project_cli_returns_string(self) -> None:
        """CLI projection returns string."""
        widget = AgentCardWidget()
        result = widget.project(RenderTarget.CLI)
        assert isinstance(result, str)

    def test_project_cli_includes_name(self) -> None:
        """CLI projection includes agent name."""
        widget = AgentCardWidget(AgentCardState(name="TestBot"))
        result = widget.project(RenderTarget.CLI)
        assert "TestBot" in result

    def test_project_cli_includes_phase_glyph(self) -> None:
        """CLI projection includes phase glyph."""
        widget = AgentCardWidget(AgentCardState(phase="active"))
        result = widget.project(RenderTarget.CLI)
        # Active phase uses ◉
        assert "◉" in result

    def test_project_cli_full_style_multiline(self) -> None:
        """Full style CLI projection is multi-line."""
        widget = AgentCardWidget(
            AgentCardState(
                name="Test",
                activity=(0.5, 0.5, 0.5),
                capability=0.5,
                style="full",
            )
        )
        result = widget.project(RenderTarget.CLI)
        assert "\n" in result

    def test_project_cli_minimal_style_single_line(self) -> None:
        """Minimal style CLI projection is single line."""
        widget = AgentCardWidget(AgentCardState(style="minimal"))
        result = widget.project(RenderTarget.CLI)
        assert "\n" not in result

    def test_project_cli_compact_style(self) -> None:
        """Compact style includes activity inline."""
        widget = AgentCardWidget(
            AgentCardState(
                activity=(0.5,),
                style="compact",
            )
        )
        result = widget.project(RenderTarget.CLI)
        # Single line with activity
        assert "\n" not in result


class TestAgentCardProjectJSON:
    """Tests for JSON projection."""

    def test_project_json_returns_dict(self) -> None:
        """JSON projection returns dict."""
        widget = AgentCardWidget()
        result = widget.project(RenderTarget.JSON)
        assert isinstance(result, dict)

    def test_project_json_type_field(self) -> None:
        """JSON projection has type field."""
        widget = AgentCardWidget()
        result = widget.project(RenderTarget.JSON)
        assert result["type"] == "agent_card"

    def test_project_json_basic_fields(self) -> None:
        """JSON projection includes all basic fields."""
        widget = AgentCardWidget(
            AgentCardState(
                agent_id="kgent-1",
                name="Test Agent",
                phase="active",
                capability=0.75,
            )
        )
        result = widget.project(RenderTarget.JSON)

        assert result["agent_id"] == "kgent-1"
        assert result["name"] == "Test Agent"
        assert result["phase"] == "active"
        assert result["capability"] == 0.75

    def test_project_json_includes_children(self) -> None:
        """JSON projection includes child widget projections."""
        widget = AgentCardWidget()
        result = widget.project(RenderTarget.JSON)

        assert "children" in result
        assert "phase_glyph" in result["children"]
        assert "activity" in result["children"]
        assert "capability" in result["children"]

    def test_project_json_distortion_on_high_entropy(self) -> None:
        """JSON projection includes distortion when entropy > 0.1."""
        widget = AgentCardWidget(AgentCardState(entropy=0.5))
        result = widget.project(RenderTarget.JSON)
        assert "distortion" in result


class TestAgentCardProjectMarimo:
    """Tests for marimo/HTML projection."""

    def test_project_marimo_returns_string(self) -> None:
        """Marimo projection returns HTML string."""
        widget = AgentCardWidget()
        result = widget.project(RenderTarget.MARIMO)
        assert isinstance(result, str)

    def test_project_marimo_is_html(self) -> None:
        """Marimo projection is HTML structure."""
        widget = AgentCardWidget()
        result = widget.project(RenderTarget.MARIMO)
        assert "<div" in result
        assert "kgents-agent-card" in result

    def test_project_marimo_includes_agent_id(self) -> None:
        """Marimo projection includes agent ID as data attribute."""
        widget = AgentCardWidget(AgentCardState(agent_id="test-agent"))
        result = widget.project(RenderTarget.MARIMO)
        assert 'data-agent-id="test-agent"' in result

    def test_project_marimo_includes_name(self) -> None:
        """Marimo projection includes agent name."""
        widget = AgentCardWidget(AgentCardState(name="TestBot"))
        result = widget.project(RenderTarget.MARIMO)
        assert "TestBot" in result


class TestAgentCardProjectTUI:
    """Tests for TUI/Textual projection."""

    def test_project_tui_returns_panel_or_fallback(self) -> None:
        """TUI projection returns Rich Panel (when available)."""
        widget = AgentCardWidget()
        result = widget.project(RenderTarget.TUI)

        try:
            from rich.panel import Panel

            assert isinstance(result, Panel)
        except ImportError:
            # Fallback to string if rich not available
            assert isinstance(result, str)


class TestAgentCardComposition:
    """Tests verifying proper composition from Wave 1-2 primitives."""

    def test_slots_are_correct_types(self) -> None:
        """Verify slots contain correct widget types."""
        from agents.i.reactive.primitives.bar import BarWidget
        from agents.i.reactive.primitives.glyph import GlyphWidget
        from agents.i.reactive.primitives.sparkline import SparklineWidget

        widget = AgentCardWidget()
        # Force rebuild
        widget.project(RenderTarget.CLI)

        assert isinstance(widget.slots["phase_glyph"], GlyphWidget)
        assert isinstance(widget.slots["activity"], SparklineWidget)
        assert isinstance(widget.slots["capability"], BarWidget)

    def test_entropy_flows_to_children(self) -> None:
        """Entropy value propagates to child widgets."""
        widget = AgentCardWidget(AgentCardState(entropy=0.5))
        # Force rebuild
        widget.project(RenderTarget.CLI)

        glyph_state = widget.slots["phase_glyph"].state.value  # type: ignore[attr-defined]
        activity_state = widget.slots["activity"].state.value  # type: ignore[attr-defined]
        capability_state = widget.slots["capability"].state.value  # type: ignore[attr-defined]

        assert glyph_state.entropy == 0.5
        assert activity_state.entropy == 0.5
        assert capability_state.entropy == 0.5

    def test_time_flows_to_children(self) -> None:
        """Time value propagates to child widgets."""
        widget = AgentCardWidget(AgentCardState(t=1000.0))
        # Force rebuild
        widget.project(RenderTarget.CLI)

        glyph_state = widget.slots["phase_glyph"].state.value  # type: ignore[attr-defined]
        activity_state = widget.slots["activity"].state.value  # type: ignore[attr-defined]
        capability_state = widget.slots["capability"].state.value  # type: ignore[attr-defined]

        assert glyph_state.t == 1000.0
        assert activity_state.t == 1000.0
        assert capability_state.t == 1000.0


class TestAgentCardDeterminism:
    """Tests for deterministic rendering."""

    def test_same_state_same_output(self) -> None:
        """Same state always produces same output."""
        state = AgentCardState(
            agent_id="test",
            name="Test Agent",
            phase="active",
            activity=(0.1, 0.5, 0.9),
            capability=0.75,
            entropy=0.3,
            seed=42,
            t=1000.0,
        )

        widget1 = AgentCardWidget(state)
        widget2 = AgentCardWidget(state)

        assert widget1.project(RenderTarget.CLI) == widget2.project(RenderTarget.CLI)
        assert widget1.project(RenderTarget.JSON) == widget2.project(RenderTarget.JSON)
        assert widget1.project(RenderTarget.MARIMO) == widget2.project(RenderTarget.MARIMO)


class TestAgentCardProjectionIntegration:
    """Tests for Projection Component Library integration."""

    def test_to_envelope_returns_widget_envelope(self) -> None:
        """to_envelope returns WidgetEnvelope."""
        from protocols.projection.schema import WidgetEnvelope

        widget = AgentCardWidget()
        envelope = widget.to_envelope()
        assert isinstance(envelope, WidgetEnvelope)

    def test_to_envelope_contains_json_data(self) -> None:
        """to_envelope contains projected JSON data."""
        widget = AgentCardWidget(AgentCardState(name="Test"))
        envelope = widget.to_envelope(RenderTarget.JSON)

        assert isinstance(envelope.data, dict)
        assert envelope.data["name"] == "Test"
        assert envelope.data["type"] == "agent_card"

    def test_to_envelope_default_meta_is_done(self) -> None:
        """to_envelope default meta status is DONE."""
        from protocols.projection.schema import WidgetStatus

        widget = AgentCardWidget()
        envelope = widget.to_envelope()

        assert envelope.meta.status == WidgetStatus.DONE

    def test_to_envelope_custom_meta(self) -> None:
        """to_envelope accepts custom meta."""
        from protocols.projection.schema import WidgetMeta, WidgetStatus

        widget = AgentCardWidget()
        custom_meta = WidgetMeta(status=WidgetStatus.STREAMING)
        envelope = widget.to_envelope(meta=custom_meta)

        assert envelope.meta.status == WidgetStatus.STREAMING

    def test_to_envelope_source_path(self) -> None:
        """to_envelope includes source path."""
        widget = AgentCardWidget()
        envelope = widget.to_envelope(source_path="world.agents.manifest")

        assert envelope.source_path == "world.agents.manifest"

    def test_to_json_envelope_returns_dict_envelope(self) -> None:
        """to_json_envelope returns envelope with dict data."""
        widget = AgentCardWidget()
        envelope = widget.to_json_envelope()

        assert isinstance(envelope.data, dict)
        assert envelope.data["type"] == "agent_card"

    def test_widget_type_returns_snake_case(self) -> None:
        """widget_type returns snake_case class name without Widget suffix."""
        widget = AgentCardWidget()
        assert widget.widget_type() == "agent_card"

    def test_envelope_to_dict_is_json_serializable(self) -> None:
        """WidgetEnvelope.to_dict() produces JSON-serializable output."""
        import json

        widget = AgentCardWidget(AgentCardState(name="Test", capability=0.8))
        envelope = widget.to_envelope(source_path="test.path")

        # Should not raise
        result = json.dumps(envelope.to_dict())
        parsed = json.loads(result)

        assert parsed["data"]["name"] == "Test"
        assert parsed["meta"]["status"] == "done"
        assert parsed["sourcePath"] == "test.path"

    def test_envelope_cli_projection(self) -> None:
        """to_envelope works with CLI target."""
        widget = AgentCardWidget(AgentCardState(name="CLI Test"))
        envelope = widget.to_envelope(RenderTarget.CLI)

        assert isinstance(envelope.data, str)
        assert "CLI Test" in envelope.data

    def test_ui_hint_returns_card(self) -> None:
        """AgentCardWidget ui_hint returns 'card'."""
        widget = AgentCardWidget()
        assert widget.ui_hint() == "card"

    def test_base_widget_ui_hint_returns_none(self) -> None:
        """Base widget ui_hint returns None by default."""
        from agents.i.reactive.primitives.glyph import GlyphWidget

        widget = GlyphWidget()
        assert widget.ui_hint() is None


class TestErrorBoundary:
    """Tests for to_envelope() error boundary behavior."""

    def test_error_boundary_catches_exceptions(self) -> None:
        """to_envelope() catches projection exceptions and returns error envelope."""
        from protocols.projection.schema import WidgetStatus

        class FailingWidget(AgentCardWidget):
            def project(self, target: RenderTarget) -> Any:
                raise ValueError("Intentional test failure")

        widget = FailingWidget()
        envelope = widget.to_envelope()

        # Should not raise, returns error envelope
        assert envelope.meta.status == WidgetStatus.ERROR
        assert envelope.meta.has_error
        assert envelope.data is None

    def test_error_boundary_captures_exception_type(self) -> None:
        """Error boundary captures exception type as error code."""

        class FailingWidget(AgentCardWidget):
            def project(self, target: RenderTarget) -> Any:
                raise TypeError("Type mismatch")

        widget = FailingWidget()
        envelope = widget.to_envelope()

        assert envelope.meta.error is not None
        assert envelope.meta.error.code == "TypeError"
        assert "Type mismatch" in envelope.meta.error.message

    def test_error_boundary_captures_custom_exceptions(self) -> None:
        """Error boundary handles custom exception classes."""

        class CustomProjectionError(Exception):
            pass

        class FailingWidget(AgentCardWidget):
            def project(self, target: RenderTarget) -> Any:
                raise CustomProjectionError("Custom failure")

        widget = FailingWidget()
        envelope = widget.to_envelope()

        assert envelope.meta.error is not None
        assert envelope.meta.error.code == "CustomProjectionError"
        assert envelope.meta.error.category == "unknown"

    def test_error_boundary_preserves_source_path(self) -> None:
        """Error envelope preserves source_path on failure."""

        class FailingWidget(AgentCardWidget):
            def project(self, target: RenderTarget) -> Any:
                raise RuntimeError("Boom")

        widget = FailingWidget()
        envelope = widget.to_envelope(source_path="test.widget.manifest")

        assert envelope.source_path == "test.widget.manifest"
        assert envelope.meta.has_error

    def test_success_path_still_works(self) -> None:
        """Normal widgets still work after error boundary added."""
        from protocols.projection.schema import WidgetStatus

        widget = AgentCardWidget(AgentCardState(name="Normal"))
        envelope = widget.to_envelope()

        assert envelope.meta.status == WidgetStatus.DONE
        assert not envelope.meta.has_error
        assert envelope.data is not None
        assert envelope.data["name"] == "Normal"


class TestStreamingEnvelope:
    """Tests for to_streaming_envelope() support."""

    @pytest.mark.asyncio
    async def test_streaming_envelope_yields_multiple(self) -> None:
        """to_streaming_envelope yields at least streaming + final envelope."""
        from protocols.projection.schema import WidgetStatus

        widget = AgentCardWidget(AgentCardState(name="Streaming Test"))
        envelopes = []

        async for envelope in widget.to_streaming_envelope():
            envelopes.append(envelope)

        assert len(envelopes) == 2
        # First is STREAMING
        assert envelopes[0].meta.status == WidgetStatus.STREAMING
        # Last is DONE (or ERROR)
        assert envelopes[-1].meta.status in (WidgetStatus.DONE, WidgetStatus.ERROR)

    @pytest.mark.asyncio
    async def test_streaming_envelope_has_stream_meta(self) -> None:
        """Streaming envelope includes StreamMeta with progress info."""
        widget = AgentCardWidget()

        async for envelope in widget.to_streaming_envelope():
            if envelope.meta.stream is not None:
                assert envelope.meta.stream.started_at is not None
                break

    @pytest.mark.asyncio
    async def test_streaming_envelope_final_has_data(self) -> None:
        """Final streaming envelope contains projected data."""
        widget = AgentCardWidget(AgentCardState(name="Final Data"))

        final_envelope = None
        async for envelope in widget.to_streaming_envelope():
            final_envelope = envelope

        assert final_envelope is not None
        assert final_envelope.data is not None
        assert final_envelope.data["name"] == "Final Data"

    @pytest.mark.asyncio
    async def test_streaming_envelope_respects_source_path(self) -> None:
        """to_streaming_envelope preserves source_path."""
        widget = AgentCardWidget()

        async for envelope in widget.to_streaming_envelope(source_path="test.stream"):
            assert envelope.source_path == "test.stream"

    @pytest.mark.asyncio
    async def test_streaming_envelope_with_total_expected(self) -> None:
        """to_streaming_envelope uses provided total_expected."""
        widget = AgentCardWidget()

        async for envelope in widget.to_streaming_envelope(total_expected=10):
            if envelope.meta.stream is not None:
                assert envelope.meta.stream.total_expected == 10
                break
