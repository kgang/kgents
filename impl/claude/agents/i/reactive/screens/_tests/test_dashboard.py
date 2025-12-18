"""Tests for DashboardScreen - main agent monitoring view."""

from __future__ import annotations

import pytest

from agents.i.reactive.primitives.agent_card import AgentCardState
from agents.i.reactive.primitives.yield_card import YieldCardState
from agents.i.reactive.screens.dashboard import DashboardScreen, DashboardScreenState
from agents.i.reactive.widget import RenderTarget


class TestDashboardScreenState:
    """Tests for DashboardScreenState immutable state."""

    def test_default_state(self) -> None:
        """Default DashboardScreenState has expected values."""
        state = DashboardScreenState()
        assert state.agents == ()
        assert state.yields == ()
        assert state.width == 80
        assert state.height == 24
        assert state.cards_per_row == 2
        assert state.max_yields_shown == 5
        assert state.t == 0.0
        assert state.entropy == 0.0
        assert state.show_density_field is True

    def test_state_is_frozen(self) -> None:
        """DashboardScreenState is immutable (frozen dataclass)."""
        state = DashboardScreenState()
        with pytest.raises(Exception):
            state.width = 100  # type: ignore[misc]

    def test_state_with_agents(self) -> None:
        """DashboardScreenState can be created with agents."""
        agents = (
            AgentCardState(agent_id="a1", name="Agent 1"),
            AgentCardState(agent_id="a2", name="Agent 2"),
        )
        state = DashboardScreenState(agents=agents)
        assert len(state.agents) == 2
        assert state.agents[0].agent_id == "a1"

    def test_state_with_yields(self) -> None:
        """DashboardScreenState can be created with yields."""
        yields = (
            YieldCardState(yield_id="y1", content="Test"),
            YieldCardState(yield_id="y2", content="Test 2"),
        )
        state = DashboardScreenState(yields=yields)
        assert len(state.yields) == 2


class TestDashboardScreen:
    """Tests for DashboardScreen reactive widget."""

    def test_create_with_default_state(self) -> None:
        """DashboardScreen can be created with default state."""
        screen = DashboardScreen()
        assert screen.state.value == DashboardScreenState()

    def test_create_with_initial_state(self) -> None:
        """DashboardScreen can be created with initial state."""
        state = DashboardScreenState(width=100, entropy=0.5)
        screen = DashboardScreen(state)
        assert screen.state.value.width == 100
        assert screen.state.value.entropy == 0.5

    def test_with_time_returns_new_screen(self) -> None:
        """with_time() returns new screen, doesn't mutate original."""
        original = DashboardScreen(DashboardScreenState(t=0.0))
        updated = original.with_time(1000.0)

        assert original.state.value.t == 0.0
        assert updated.state.value.t == 1000.0

    def test_with_entropy_returns_new_screen(self) -> None:
        """with_entropy() returns new screen."""
        original = DashboardScreen(DashboardScreenState(entropy=0.0))
        updated = original.with_entropy(0.5)

        assert original.state.value.entropy == 0.0
        assert updated.state.value.entropy == 0.5

    def test_with_entropy_clamps(self) -> None:
        """with_entropy() clamps to 0.0-1.0 range."""
        screen = DashboardScreen()
        assert screen.with_entropy(-0.5).state.value.entropy == 0.0
        assert screen.with_entropy(1.5).state.value.entropy == 1.0

    def test_add_agent(self) -> None:
        """add_agent() adds an agent to the dashboard."""
        screen = DashboardScreen()
        agent = AgentCardState(agent_id="a1", name="Test Agent")
        updated = screen.add_agent(agent)

        assert len(updated.state.value.agents) == 1
        assert updated.state.value.agents[0].agent_id == "a1"

    def test_add_agent_replaces_existing(self) -> None:
        """add_agent() replaces existing agent with same id."""
        agent1 = AgentCardState(agent_id="a1", name="Original")
        screen = DashboardScreen(DashboardScreenState(agents=(agent1,)))

        agent2 = AgentCardState(agent_id="a1", name="Updated")
        updated = screen.add_agent(agent2)

        assert len(updated.state.value.agents) == 1
        assert updated.state.value.agents[0].name == "Updated"

    def test_push_yield(self) -> None:
        """push_yield() adds a yield to the stream."""
        screen = DashboardScreen()
        yield_card = YieldCardState(yield_id="y1", content="Test")
        updated = screen.push_yield(yield_card)

        assert len(updated.state.value.yields) == 1
        assert updated.state.value.yields[0].yield_id == "y1"

    def test_push_yield_prepends(self) -> None:
        """push_yield() prepends new yields to the front."""
        yield1 = YieldCardState(yield_id="y1", content="First")
        screen = DashboardScreen(DashboardScreenState(yields=(yield1,)))

        yield2 = YieldCardState(yield_id="y2", content="Second")
        updated = screen.push_yield(yield2)

        assert updated.state.value.yields[0].yield_id == "y2"
        assert updated.state.value.yields[1].yield_id == "y1"


class TestDashboardScreenSlots:
    """Tests for slot composition."""

    def test_has_agent_slots(self) -> None:
        """Dashboard creates slots for agents."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget

        agents = (
            AgentCardState(agent_id="a1"),
            AgentCardState(agent_id="a2"),
        )
        screen = DashboardScreen(DashboardScreenState(agents=agents))
        screen.project(RenderTarget.CLI)  # Force rebuild

        assert isinstance(screen.slots["agent_0"], AgentCardWidget)
        assert isinstance(screen.slots["agent_1"], AgentCardWidget)

    def test_has_yield_slots(self) -> None:
        """Dashboard creates slots for yields."""
        from agents.i.reactive.primitives.yield_card import YieldCardWidget

        yields = (
            YieldCardState(yield_id="y1"),
            YieldCardState(yield_id="y2"),
        )
        screen = DashboardScreen(DashboardScreenState(yields=yields))
        screen.project(RenderTarget.CLI)  # Force rebuild

        assert isinstance(screen.slots["yield_0"], YieldCardWidget)
        assert isinstance(screen.slots["yield_1"], YieldCardWidget)

    def test_has_density_field_slot(self) -> None:
        """Dashboard creates density field slot when enabled."""
        from agents.i.reactive.primitives.density_field import DensityFieldWidget

        screen = DashboardScreen(DashboardScreenState(show_density_field=True))
        screen.project(RenderTarget.CLI)  # Force rebuild

        assert isinstance(screen.slots["density_field"], DensityFieldWidget)

    def test_no_density_field_when_disabled(self) -> None:
        """Dashboard doesn't create density field when disabled."""
        screen = DashboardScreen(DashboardScreenState(show_density_field=False))
        screen.project(RenderTarget.CLI)  # Force rebuild

        assert "density_field" not in screen.slots


class TestDashboardScreenProjectCLI:
    """Tests for CLI projection."""

    def test_project_cli_returns_string(self) -> None:
        """CLI projection returns string."""
        screen = DashboardScreen()
        result = screen.project(RenderTarget.CLI)
        assert isinstance(result, str)

    def test_project_cli_includes_header(self) -> None:
        """CLI projection includes header."""
        screen = DashboardScreen()
        result = screen.project(RenderTarget.CLI)
        assert "DASHBOARD" in result

    def test_project_cli_empty_state(self) -> None:
        """CLI projection handles empty state gracefully."""
        screen = DashboardScreen()
        result = screen.project(RenderTarget.CLI)
        assert "No agents active" in result or "Waiting for activity" in result

    def test_project_cli_with_agents(self) -> None:
        """CLI projection includes agent names."""
        agents = (AgentCardState(agent_id="a1", name="TestBot"),)
        screen = DashboardScreen(DashboardScreenState(agents=agents))
        result = screen.project(RenderTarget.CLI)
        assert "TestBot" in result

    def test_project_cli_with_yields(self) -> None:
        """CLI projection includes yield content."""
        yields = (YieldCardState(yield_id="y1", content="Test output"),)
        screen = DashboardScreen(DashboardScreenState(yields=yields))
        result = screen.project(RenderTarget.CLI)
        assert "Test output" in result


class TestDashboardScreenProjectJSON:
    """Tests for JSON projection."""

    def test_project_json_returns_dict(self) -> None:
        """JSON projection returns dict."""
        screen = DashboardScreen()
        result = screen.project(RenderTarget.JSON)
        assert isinstance(result, dict)

    def test_project_json_type_field(self) -> None:
        """JSON projection has type field."""
        screen = DashboardScreen()
        result = screen.project(RenderTarget.JSON)
        assert result["type"] == "dashboard_screen"

    def test_project_json_includes_agents(self) -> None:
        """JSON projection includes agent data."""
        agents = (AgentCardState(agent_id="a1"),)
        screen = DashboardScreen(DashboardScreenState(agents=agents))
        result = screen.project(RenderTarget.JSON)

        assert "agents" in result
        assert len(result["agents"]) == 1
        assert result["agents"][0]["agent_id"] == "a1"

    def test_project_json_includes_yields(self) -> None:
        """JSON projection includes yield data."""
        yields = (YieldCardState(yield_id="y1", content="Test"),)
        screen = DashboardScreen(DashboardScreenState(yields=yields))
        result = screen.project(RenderTarget.JSON)

        assert "yields" in result
        assert len(result["yields"]) == 1

    def test_project_json_includes_density_field(self) -> None:
        """JSON projection includes density field when enabled."""
        screen = DashboardScreen(DashboardScreenState(show_density_field=True))
        result = screen.project(RenderTarget.JSON)
        assert "density_field" in result


class TestDashboardScreenProjectMarimo:
    """Tests for marimo/HTML projection."""

    def test_project_marimo_returns_string(self) -> None:
        """Marimo projection returns HTML string."""
        screen = DashboardScreen()
        result = screen.project(RenderTarget.MARIMO)
        assert isinstance(result, str)

    def test_project_marimo_is_html(self) -> None:
        """Marimo projection is HTML structure."""
        screen = DashboardScreen()
        result = screen.project(RenderTarget.MARIMO)
        assert "<div" in result
        assert "kgents-dashboard" in result

    def test_project_marimo_includes_header(self) -> None:
        """Marimo projection includes header."""
        screen = DashboardScreen()
        result = screen.project(RenderTarget.MARIMO)
        assert "DASHBOARD" in result

    def test_project_marimo_empty_state(self) -> None:
        """Marimo projection handles empty state."""
        screen = DashboardScreen()
        result = screen.project(RenderTarget.MARIMO)
        assert "No agents active" in result or "Waiting" in result


class TestDashboardScreenProjectTUI:
    """Tests for TUI/Textual projection."""

    def test_project_tui_returns_something(self) -> None:
        """TUI projection returns Panel or fallback."""
        screen = DashboardScreen()
        result = screen.project(RenderTarget.TUI)

        try:
            from rich.panel import Panel

            assert isinstance(result, Panel)
        except ImportError:
            assert isinstance(result, str)


class TestDashboardScreenComposition:
    """Tests verifying proper composition from Wave 1-3 primitives."""

    def test_composes_agent_cards(self) -> None:
        """Dashboard composes AgentCardWidget instances."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget

        agents = (
            AgentCardState(agent_id="a1"),
            AgentCardState(agent_id="a2"),
        )
        screen = DashboardScreen(DashboardScreenState(agents=agents))
        screen.project(RenderTarget.CLI)

        for i in range(2):
            assert isinstance(screen.slots[f"agent_{i}"], AgentCardWidget)

    def test_composes_yield_cards(self) -> None:
        """Dashboard composes YieldCardWidget instances."""
        from agents.i.reactive.primitives.yield_card import YieldCardWidget

        yields = (YieldCardState(yield_id="y1"),)
        screen = DashboardScreen(DashboardScreenState(yields=yields))
        screen.project(RenderTarget.CLI)

        assert isinstance(screen.slots["yield_0"], YieldCardWidget)

    def test_composes_density_field(self) -> None:
        """Dashboard composes DensityFieldWidget."""
        from agents.i.reactive.primitives.density_field import DensityFieldWidget

        screen = DashboardScreen(DashboardScreenState(show_density_field=True))
        screen.project(RenderTarget.CLI)

        assert isinstance(screen.slots["density_field"], DensityFieldWidget)

    def test_entropy_flows_to_children(self) -> None:
        """Entropy value propagates to child widgets."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget

        agents = (AgentCardState(agent_id="a1"),)
        screen = DashboardScreen(DashboardScreenState(agents=agents, entropy=0.5))
        screen.project(RenderTarget.CLI)

        # Agent card should receive the screen's entropy
        agent_widget = screen.slots["agent_0"]
        assert isinstance(agent_widget, AgentCardWidget)
        assert agent_widget.state.value.entropy == 0.5

    def test_time_flows_to_children(self) -> None:
        """Time value propagates to child widgets."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget

        agents = (AgentCardState(agent_id="a1"),)
        screen = DashboardScreen(DashboardScreenState(agents=agents, t=1000.0))
        screen.project(RenderTarget.CLI)

        agent_widget = screen.slots["agent_0"]
        assert isinstance(agent_widget, AgentCardWidget)
        assert agent_widget.state.value.t == 1000.0


class TestDashboardScreenDeterminism:
    """Tests for deterministic rendering."""

    def test_same_state_same_output(self) -> None:
        """Same state always produces same output."""
        state = DashboardScreenState(
            agents=(AgentCardState(agent_id="a1", name="Test"),),
            yields=(YieldCardState(yield_id="y1", content="Test"),),
            entropy=0.3,
            seed=42,
            t=1000.0,
        )

        screen1 = DashboardScreen(state)
        screen2 = DashboardScreen(state)

        assert screen1.project(RenderTarget.CLI) == screen2.project(RenderTarget.CLI)
        assert screen1.project(RenderTarget.JSON) == screen2.project(RenderTarget.JSON)
        assert screen1.project(RenderTarget.MARIMO) == screen2.project(RenderTarget.MARIMO)
