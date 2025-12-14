"""Tests for DebuggerScreen - agent inspection and debugging view."""

from __future__ import annotations

import pytest
from agents.i.reactive.primitives.agent_card import AgentCardState
from agents.i.reactive.primitives.yield_card import YieldCardState
from agents.i.reactive.screens.debugger import DebuggerScreen, DebuggerScreenState
from agents.i.reactive.widget import RenderTarget


class TestDebuggerScreenState:
    """Tests for DebuggerScreenState immutable state."""

    def test_default_state(self) -> None:
        """Default DebuggerScreenState has expected values."""
        state = DebuggerScreenState()
        assert state.agent is None
        assert state.activity_history == ()
        assert state.yields == ()
        assert state.width == 80
        assert state.height == 30
        assert state.max_activity_points == 50
        assert state.max_yields_shown == 10
        assert state.t == 0.0
        assert state.entropy == 0.0

    def test_state_is_frozen(self) -> None:
        """DebuggerScreenState is immutable (frozen dataclass)."""
        state = DebuggerScreenState()
        with pytest.raises(Exception):
            state.entropy = 0.5  # type: ignore[misc]

    def test_state_with_agent(self) -> None:
        """DebuggerScreenState can be created with agent."""
        agent = AgentCardState(agent_id="a1", name="Test Agent")
        state = DebuggerScreenState(agent=agent)
        assert state.agent is not None
        assert state.agent.agent_id == "a1"

    def test_state_with_activity(self) -> None:
        """DebuggerScreenState can be created with activity history."""
        activity = (0.1, 0.5, 0.9, 0.3)
        state = DebuggerScreenState(activity_history=activity)
        assert len(state.activity_history) == 4

    def test_state_with_yields(self) -> None:
        """DebuggerScreenState can be created with yields."""
        yields = (
            YieldCardState(yield_id="y1", content="Test 1"),
            YieldCardState(yield_id="y2", content="Test 2"),
        )
        state = DebuggerScreenState(yields=yields)
        assert len(state.yields) == 2


class TestDebuggerScreen:
    """Tests for DebuggerScreen reactive widget."""

    def test_create_with_default_state(self) -> None:
        """DebuggerScreen can be created with default state."""
        screen = DebuggerScreen()
        assert screen.state.value == DebuggerScreenState()

    def test_create_with_initial_state(self) -> None:
        """DebuggerScreen can be created with initial state."""
        agent = AgentCardState(agent_id="a1", name="Test")
        state = DebuggerScreenState(agent=agent, entropy=0.5)
        screen = DebuggerScreen(state)
        assert screen.state.value.agent is not None
        assert screen.state.value.entropy == 0.5

    def test_with_agent_returns_new_screen(self) -> None:
        """with_agent() returns new screen, doesn't mutate original."""
        original = DebuggerScreen()
        agent = AgentCardState(agent_id="a1", name="Test")
        updated = original.with_agent(agent)

        assert original.state.value.agent is None
        assert updated.state.value.agent is not None
        assert updated.state.value.agent.agent_id == "a1"

    def test_with_agent_none(self) -> None:
        """with_agent(None) clears the selected agent."""
        agent = AgentCardState(agent_id="a1", name="Test")
        screen = DebuggerScreen(DebuggerScreenState(agent=agent))
        updated = screen.with_agent(None)

        assert updated.state.value.agent is None

    def test_with_activity_returns_new_screen(self) -> None:
        """with_activity() returns new screen."""
        original = DebuggerScreen()
        updated = original.with_activity([0.1, 0.5, 0.9])

        assert original.state.value.activity_history == ()
        assert updated.state.value.activity_history == (0.1, 0.5, 0.9)

    def test_with_activity_clamps_values(self) -> None:
        """with_activity() clamps values to 0.0-1.0."""
        screen = DebuggerScreen()
        updated = screen.with_activity([-0.5, 1.5, 0.5])

        assert updated.state.value.activity_history == (0.0, 1.0, 0.5)

    def test_push_activity(self) -> None:
        """push_activity() appends value to history."""
        screen = DebuggerScreen(DebuggerScreenState(activity_history=(0.1, 0.2)))
        updated = screen.push_activity(0.9)

        assert updated.state.value.activity_history == (0.1, 0.2, 0.9)

    def test_push_activity_limits_history(self) -> None:
        """push_activity() respects max_activity_points."""
        state = DebuggerScreenState(
            activity_history=tuple(i / 100.0 for i in range(50)),
            max_activity_points=50,
        )
        screen = DebuggerScreen(state)
        updated = screen.push_activity(0.99)

        assert len(updated.state.value.activity_history) == 50
        assert updated.state.value.activity_history[-1] == 0.99

    def test_with_yields_returns_new_screen(self) -> None:
        """with_yields() returns new screen."""
        original = DebuggerScreen()
        yields = (YieldCardState(yield_id="y1", content="Test"),)
        updated = original.with_yields(yields)

        assert original.state.value.yields == ()
        assert len(updated.state.value.yields) == 1

    def test_push_yield(self) -> None:
        """push_yield() prepends yield to stream."""
        yield1 = YieldCardState(yield_id="y1", content="First")
        screen = DebuggerScreen(DebuggerScreenState(yields=(yield1,)))

        yield2 = YieldCardState(yield_id="y2", content="Second")
        updated = screen.push_yield(yield2)

        assert updated.state.value.yields[0].yield_id == "y2"
        assert updated.state.value.yields[1].yield_id == "y1"

    def test_with_time_returns_new_screen(self) -> None:
        """with_time() returns new screen."""
        original = DebuggerScreen(DebuggerScreenState(t=0.0))
        updated = original.with_time(1000.0)

        assert original.state.value.t == 0.0
        assert updated.state.value.t == 1000.0

    def test_with_entropy_returns_new_screen(self) -> None:
        """with_entropy() returns new screen."""
        original = DebuggerScreen(DebuggerScreenState(entropy=0.0))
        updated = original.with_entropy(0.5)

        assert original.state.value.entropy == 0.0
        assert updated.state.value.entropy == 0.5

    def test_with_entropy_clamps(self) -> None:
        """with_entropy() clamps to 0.0-1.0 range."""
        screen = DebuggerScreen()
        assert screen.with_entropy(-0.5).state.value.entropy == 0.0
        assert screen.with_entropy(1.5).state.value.entropy == 1.0


class TestDebuggerScreenSlots:
    """Tests for slot composition."""

    def test_has_agent_card_slot_when_agent_selected(self) -> None:
        """Debugger creates agent card slot when agent is selected."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget

        agent = AgentCardState(agent_id="a1", name="Test")
        screen = DebuggerScreen(DebuggerScreenState(agent=agent))
        screen.project(RenderTarget.CLI)

        assert "agent_card" in screen.slots
        assert isinstance(screen.slots["agent_card"], AgentCardWidget)

    def test_no_agent_card_slot_when_no_agent(self) -> None:
        """Debugger doesn't create agent card slot when no agent selected."""
        screen = DebuggerScreen()
        screen.project(RenderTarget.CLI)

        assert "agent_card" not in screen.slots

    def test_has_activity_sparkline_slot(self) -> None:
        """Debugger creates activity sparkline slot."""
        from agents.i.reactive.primitives.sparkline import SparklineWidget

        screen = DebuggerScreen()
        screen.project(RenderTarget.CLI)

        assert "activity_sparkline" in screen.slots
        assert isinstance(screen.slots["activity_sparkline"], SparklineWidget)

    def test_has_yield_slots(self) -> None:
        """Debugger creates slots for yields."""
        from agents.i.reactive.primitives.yield_card import YieldCardWidget

        yields = (
            YieldCardState(yield_id="y1"),
            YieldCardState(yield_id="y2"),
        )
        screen = DebuggerScreen(DebuggerScreenState(yields=yields))
        screen.project(RenderTarget.CLI)

        assert isinstance(screen.slots["yield_0"], YieldCardWidget)
        assert isinstance(screen.slots["yield_1"], YieldCardWidget)

    def test_has_entropy_slider_slot(self) -> None:
        """Debugger creates entropy slider slot."""
        from agents.i.reactive.primitives.bar import BarWidget

        screen = DebuggerScreen()
        screen.project(RenderTarget.CLI)

        assert "entropy_slider" in screen.slots
        assert isinstance(screen.slots["entropy_slider"], BarWidget)


class TestDebuggerScreenProjectCLI:
    """Tests for CLI projection."""

    def test_project_cli_returns_string(self) -> None:
        """CLI projection returns string."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.CLI)
        assert isinstance(result, str)

    def test_project_cli_includes_header(self) -> None:
        """CLI projection includes header."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.CLI)
        assert "DEBUGGER" in result

    def test_project_cli_empty_state(self) -> None:
        """CLI projection handles empty state gracefully."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.CLI)
        assert "No agent selected" in result

    def test_project_cli_with_agent(self) -> None:
        """CLI projection includes agent info when selected."""
        agent = AgentCardState(agent_id="a1", name="TestBot")
        screen = DebuggerScreen(DebuggerScreenState(agent=agent))
        result = screen.project(RenderTarget.CLI)
        assert "TestBot" in result
        assert "AGENT" in result

    def test_project_cli_with_activity(self) -> None:
        """CLI projection includes activity timeline."""
        activity = (0.1, 0.5, 0.9)
        agent = AgentCardState(agent_id="a1")
        screen = DebuggerScreen(
            DebuggerScreenState(agent=agent, activity_history=activity)
        )
        result = screen.project(RenderTarget.CLI)
        assert "ACTIVITY" in result or "TIMELINE" in result
        assert "3 points" in result

    def test_project_cli_with_yields(self) -> None:
        """CLI projection includes yields."""
        agent = AgentCardState(agent_id="a1")
        yields = (YieldCardState(yield_id="y1", content="Test output"),)
        screen = DebuggerScreen(DebuggerScreenState(agent=agent, yields=yields))
        result = screen.project(RenderTarget.CLI)
        assert "Test output" in result

    def test_project_cli_shows_entropy_control(self) -> None:
        """CLI projection shows entropy control."""
        agent = AgentCardState(agent_id="a1")
        screen = DebuggerScreen(DebuggerScreenState(agent=agent, entropy=0.5))
        result = screen.project(RenderTarget.CLI)
        assert "ENTROPY" in result
        assert "50%" in result


class TestDebuggerScreenProjectJSON:
    """Tests for JSON projection."""

    def test_project_json_returns_dict(self) -> None:
        """JSON projection returns dict."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.JSON)
        assert isinstance(result, dict)

    def test_project_json_type_field(self) -> None:
        """JSON projection has type field."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.JSON)
        assert result["type"] == "debugger_screen"

    def test_project_json_has_agent_flag(self) -> None:
        """JSON projection indicates if agent is selected."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.JSON)
        assert result["has_agent"] is False

        agent = AgentCardState(agent_id="a1")
        screen2 = DebuggerScreen(DebuggerScreenState(agent=agent))
        result2 = screen2.project(RenderTarget.JSON)
        assert result2["has_agent"] is True

    def test_project_json_includes_agent_card(self) -> None:
        """JSON projection includes agent card when selected."""
        agent = AgentCardState(agent_id="a1")
        screen = DebuggerScreen(DebuggerScreenState(agent=agent))
        result = screen.project(RenderTarget.JSON)

        assert "agent_card" in result
        assert result["agent_card"]["type"] == "agent_card"

    def test_project_json_includes_activity_sparkline(self) -> None:
        """JSON projection includes activity sparkline."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.JSON)

        assert "activity_sparkline" in result

    def test_project_json_includes_yields(self) -> None:
        """JSON projection includes yields."""
        yields = (YieldCardState(yield_id="y1"),)
        screen = DebuggerScreen(DebuggerScreenState(yields=yields))
        result = screen.project(RenderTarget.JSON)

        assert "yields" in result
        assert len(result["yields"]) == 1

    def test_project_json_includes_entropy_slider(self) -> None:
        """JSON projection includes entropy slider."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.JSON)

        assert "entropy_slider" in result


class TestDebuggerScreenProjectMarimo:
    """Tests for marimo/HTML projection."""

    def test_project_marimo_returns_string(self) -> None:
        """Marimo projection returns HTML string."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.MARIMO)
        assert isinstance(result, str)

    def test_project_marimo_is_html(self) -> None:
        """Marimo projection is HTML structure."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.MARIMO)
        assert "<div" in result
        assert "kgents-debugger" in result

    def test_project_marimo_empty_state(self) -> None:
        """Marimo projection handles empty state."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.MARIMO)
        assert "No agent selected" in result

    def test_project_marimo_with_agent(self) -> None:
        """Marimo projection includes agent section when selected."""
        agent = AgentCardState(agent_id="a1", name="TestBot")
        screen = DebuggerScreen(DebuggerScreenState(agent=agent))
        result = screen.project(RenderTarget.MARIMO)
        assert "TestBot" in result
        assert "kgents-debugger-agent" in result


class TestDebuggerScreenProjectTUI:
    """Tests for TUI/Textual projection."""

    def test_project_tui_returns_something(self) -> None:
        """TUI projection returns Panel or fallback."""
        screen = DebuggerScreen()
        result = screen.project(RenderTarget.TUI)

        try:
            from rich.panel import Panel

            assert isinstance(result, Panel)
        except ImportError:
            assert isinstance(result, str)


class TestDebuggerScreenComposition:
    """Tests verifying proper composition from Wave 1-3 primitives."""

    def test_composes_agent_card(self) -> None:
        """Debugger composes AgentCardWidget when agent selected."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget

        agent = AgentCardState(agent_id="a1")
        screen = DebuggerScreen(DebuggerScreenState(agent=agent))
        screen.project(RenderTarget.CLI)

        assert isinstance(screen.slots["agent_card"], AgentCardWidget)

    def test_composes_sparkline(self) -> None:
        """Debugger composes SparklineWidget for activity."""
        from agents.i.reactive.primitives.sparkline import SparklineWidget

        screen = DebuggerScreen()
        screen.project(RenderTarget.CLI)

        assert isinstance(screen.slots["activity_sparkline"], SparklineWidget)

    def test_composes_yield_cards(self) -> None:
        """Debugger composes YieldCardWidget instances."""
        from agents.i.reactive.primitives.yield_card import YieldCardWidget

        yields = (YieldCardState(yield_id="y1"),)
        screen = DebuggerScreen(DebuggerScreenState(yields=yields))
        screen.project(RenderTarget.CLI)

        assert isinstance(screen.slots["yield_0"], YieldCardWidget)

    def test_composes_bar_for_entropy(self) -> None:
        """Debugger composes BarWidget for entropy slider."""
        from agents.i.reactive.primitives.bar import BarWidget

        screen = DebuggerScreen()
        screen.project(RenderTarget.CLI)

        assert isinstance(screen.slots["entropy_slider"], BarWidget)

    def test_entropy_flows_to_children(self) -> None:
        """Entropy value propagates to child widgets."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget
        from agents.i.reactive.primitives.sparkline import SparklineWidget

        agent = AgentCardState(agent_id="a1")
        screen = DebuggerScreen(DebuggerScreenState(agent=agent, entropy=0.5))
        screen.project(RenderTarget.CLI)

        # Agent card should receive the debugger's entropy
        agent_widget = screen.slots["agent_card"]
        assert isinstance(agent_widget, AgentCardWidget)
        assert agent_widget.state.value.entropy == 0.5

        # Sparkline too
        sparkline_widget = screen.slots["activity_sparkline"]
        assert isinstance(sparkline_widget, SparklineWidget)
        assert sparkline_widget.state.value.entropy == 0.5

    def test_time_flows_to_children(self) -> None:
        """Time value propagates to child widgets."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget

        agent = AgentCardState(agent_id="a1")
        screen = DebuggerScreen(DebuggerScreenState(agent=agent, t=1000.0))
        screen.project(RenderTarget.CLI)

        agent_widget = screen.slots["agent_card"]
        assert isinstance(agent_widget, AgentCardWidget)
        assert agent_widget.state.value.t == 1000.0


class TestDebuggerScreenDeterminism:
    """Tests for deterministic rendering."""

    def test_same_state_same_output(self) -> None:
        """Same state always produces same output."""
        state = DebuggerScreenState(
            agent=AgentCardState(agent_id="a1", name="Test"),
            activity_history=(0.1, 0.5, 0.9),
            yields=(YieldCardState(yield_id="y1", content="Test"),),
            entropy=0.3,
            seed=42,
            t=1000.0,
        )

        screen1 = DebuggerScreen(state)
        screen2 = DebuggerScreen(state)

        assert screen1.project(RenderTarget.CLI) == screen2.project(RenderTarget.CLI)
        assert screen1.project(RenderTarget.JSON) == screen2.project(RenderTarget.JSON)
        assert screen1.project(RenderTarget.MARIMO) == screen2.project(
            RenderTarget.MARIMO
        )


class TestDebuggerScreenEntropyControl:
    """Tests for entropy control functionality."""

    def test_entropy_slider_reflects_value(self) -> None:
        """Entropy slider bar reflects current entropy value."""
        from agents.i.reactive.primitives.bar import BarWidget

        screen = DebuggerScreen(DebuggerScreenState(entropy=0.7))
        screen.project(RenderTarget.CLI)

        slider_widget = screen.slots["entropy_slider"]
        assert isinstance(slider_widget, BarWidget)
        assert slider_widget.state.value.value == 0.7

    def test_entropy_changes_affect_visuals(self) -> None:
        """Changing entropy affects visual output."""
        agent = AgentCardState(agent_id="a1")

        screen_low = DebuggerScreen(DebuggerScreenState(agent=agent, entropy=0.0))
        screen_high = DebuggerScreen(DebuggerScreenState(agent=agent, entropy=0.9))

        result_low = screen_low.project(RenderTarget.JSON)
        result_high = screen_high.project(RenderTarget.JSON)

        # High entropy should show in the output
        assert result_low["entropy"] == 0.0
        assert result_high["entropy"] == 0.9
