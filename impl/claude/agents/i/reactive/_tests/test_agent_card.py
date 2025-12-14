"""Tests for AgentCardWidget - full agent representation card."""

from __future__ import annotations

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
        assert widget1.project(RenderTarget.MARIMO) == widget2.project(
            RenderTarget.MARIMO
        )
