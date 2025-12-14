"""Tests for ForgeScreen - agent creation and editing view."""

from __future__ import annotations

import pytest
from agents.i.reactive.screens.forge import (
    AVAILABLE_PHASES,
    ForgeScreen,
    ForgeScreenState,
)
from agents.i.reactive.widget import RenderTarget


class TestForgeScreenState:
    """Tests for ForgeScreenState immutable state."""

    def test_default_state(self) -> None:
        """Default ForgeScreenState has expected values."""
        state = ForgeScreenState()
        assert state.agent_id == ""
        assert state.name == "New Agent"
        assert state.phase == "idle"
        assert state.capability == 1.0
        assert state.mode == "create"
        assert state.width == 60
        assert state.height == 24
        assert state.t == 0.0
        assert state.entropy == 0.0

    def test_state_is_frozen(self) -> None:
        """ForgeScreenState is immutable (frozen dataclass)."""
        state = ForgeScreenState()
        with pytest.raises(Exception):
            state.name = "Modified"  # type: ignore[misc]

    def test_state_with_all_fields(self) -> None:
        """ForgeScreenState can be created with all fields."""
        state = ForgeScreenState(
            agent_id="test-agent",
            name="Test Agent",
            phase="active",
            capability=0.75,
            mode="edit",
            width=100,
            height=30,
            t=1000.0,
            entropy=0.3,
            seed=42,
        )
        assert state.agent_id == "test-agent"
        assert state.name == "Test Agent"
        assert state.phase == "active"
        assert state.capability == 0.75
        assert state.mode == "edit"


class TestForgeScreen:
    """Tests for ForgeScreen reactive widget."""

    def test_create_with_default_state(self) -> None:
        """ForgeScreen can be created with default state."""
        screen = ForgeScreen()
        assert screen.state.value == ForgeScreenState()

    def test_create_with_initial_state(self) -> None:
        """ForgeScreen can be created with initial state."""
        state = ForgeScreenState(name="Custom Agent", phase="active")
        screen = ForgeScreen(state)
        assert screen.state.value.name == "Custom Agent"
        assert screen.state.value.phase == "active"

    def test_with_name_returns_new_screen(self) -> None:
        """with_name() returns new screen, doesn't mutate original."""
        original = ForgeScreen(ForgeScreenState(name="Original"))
        updated = original.with_name("Updated")

        assert original.state.value.name == "Original"
        assert updated.state.value.name == "Updated"

    def test_with_phase_returns_new_screen(self) -> None:
        """with_phase() returns new screen."""
        original = ForgeScreen(ForgeScreenState(phase="idle"))
        updated = original.with_phase("active")

        assert original.state.value.phase == "idle"
        assert updated.state.value.phase == "active"

    def test_with_capability_returns_new_screen(self) -> None:
        """with_capability() returns new screen."""
        original = ForgeScreen(ForgeScreenState(capability=1.0))
        updated = original.with_capability(0.5)

        assert original.state.value.capability == 1.0
        assert updated.state.value.capability == 0.5

    def test_with_capability_clamps(self) -> None:
        """with_capability() clamps to 0.0-1.0 range."""
        screen = ForgeScreen()
        assert screen.with_capability(-0.5).state.value.capability == 0.0
        assert screen.with_capability(1.5).state.value.capability == 1.0

    def test_with_time_returns_new_screen(self) -> None:
        """with_time() returns new screen."""
        original = ForgeScreen(ForgeScreenState(t=0.0))
        updated = original.with_time(1000.0)

        assert original.state.value.t == 0.0
        assert updated.state.value.t == 1000.0

    def test_with_entropy_returns_new_screen(self) -> None:
        """with_entropy() returns new screen."""
        original = ForgeScreen(ForgeScreenState(entropy=0.0))
        updated = original.with_entropy(0.5)

        assert original.state.value.entropy == 0.0
        assert updated.state.value.entropy == 0.5

    def test_with_entropy_clamps(self) -> None:
        """with_entropy() clamps to 0.0-1.0 range."""
        screen = ForgeScreen()
        assert screen.with_entropy(-0.5).state.value.entropy == 0.0
        assert screen.with_entropy(1.5).state.value.entropy == 1.0

    def test_with_mode_returns_new_screen(self) -> None:
        """with_mode() returns new screen."""
        original = ForgeScreen(ForgeScreenState(mode="create"))
        updated = original.with_mode("edit")

        assert original.state.value.mode == "create"
        assert updated.state.value.mode == "edit"

    def test_get_agent_state(self) -> None:
        """get_agent_state() returns AgentCardState from configuration."""
        screen = ForgeScreen(
            ForgeScreenState(
                agent_id="test-id",
                name="Test Agent",
                phase="active",
                capability=0.8,
            )
        )
        agent = screen.get_agent_state()

        assert agent.agent_id == "test-id"
        assert agent.name == "Test Agent"
        assert agent.phase == "active"
        assert agent.capability == 0.8

    def test_get_agent_state_auto_id(self) -> None:
        """get_agent_state() generates ID when not set."""
        screen = ForgeScreen(ForgeScreenState(agent_id="", seed=42))
        agent = screen.get_agent_state()

        assert "42" in agent.agent_id


class TestForgeScreenSlots:
    """Tests for slot composition."""

    def test_has_preview_card_slot(self) -> None:
        """Forge creates preview card slot."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget

        screen = ForgeScreen()
        screen.project(RenderTarget.CLI)  # Force rebuild

        assert "preview_card" in screen.slots
        assert isinstance(screen.slots["preview_card"], AgentCardWidget)

    def test_has_capability_bar_slot(self) -> None:
        """Forge creates capability bar slot."""
        from agents.i.reactive.primitives.bar import BarWidget

        screen = ForgeScreen()
        screen.project(RenderTarget.CLI)  # Force rebuild

        assert "capability_bar" in screen.slots
        assert isinstance(screen.slots["capability_bar"], BarWidget)

    def test_has_phase_glyph_slots(self) -> None:
        """Forge creates phase glyph slots for all available phases."""
        from agents.i.reactive.primitives.glyph import GlyphWidget

        screen = ForgeScreen()
        screen.project(RenderTarget.CLI)  # Force rebuild

        for phase in AVAILABLE_PHASES:
            assert f"phase_{phase}" in screen.slots
            assert isinstance(screen.slots[f"phase_{phase}"], GlyphWidget)

    def test_selected_phase_has_higher_entropy(self) -> None:
        """Selected phase glyph has higher entropy for visual emphasis."""
        from agents.i.reactive.primitives.glyph import GlyphWidget

        screen = ForgeScreen(ForgeScreenState(phase="active", entropy=0.0))
        screen.project(RenderTarget.CLI)

        selected_widget = screen.slots["phase_active"]
        other_widget = screen.slots["phase_idle"]
        assert isinstance(selected_widget, GlyphWidget)
        assert isinstance(other_widget, GlyphWidget)

        assert selected_widget.state.value.entropy > other_widget.state.value.entropy


class TestForgeScreenProjectCLI:
    """Tests for CLI projection."""

    def test_project_cli_returns_string(self) -> None:
        """CLI projection returns string."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.CLI)
        assert isinstance(result, str)

    def test_project_cli_includes_header(self) -> None:
        """CLI projection includes header with mode."""
        screen = ForgeScreen(ForgeScreenState(mode="create"))
        result = screen.project(RenderTarget.CLI)
        assert "FORGE" in result
        assert "CREATE" in result

    def test_project_cli_includes_name(self) -> None:
        """CLI projection includes agent name."""
        screen = ForgeScreen(ForgeScreenState(name="TestBot"))
        result = screen.project(RenderTarget.CLI)
        assert "TestBot" in result

    def test_project_cli_includes_configuration(self) -> None:
        """CLI projection includes configuration section."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.CLI)
        assert "CONFIGURATION" in result or "Name:" in result

    def test_project_cli_includes_preview(self) -> None:
        """CLI projection includes preview section."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.CLI)
        assert "PREVIEW" in result

    def test_project_cli_shows_capability_percentage(self) -> None:
        """CLI projection shows capability as percentage."""
        screen = ForgeScreen(ForgeScreenState(capability=0.75))
        result = screen.project(RenderTarget.CLI)
        assert "75%" in result


class TestForgeScreenProjectJSON:
    """Tests for JSON projection."""

    def test_project_json_returns_dict(self) -> None:
        """JSON projection returns dict."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.JSON)
        assert isinstance(result, dict)

    def test_project_json_type_field(self) -> None:
        """JSON projection has type field."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.JSON)
        assert result["type"] == "forge_screen"

    def test_project_json_includes_configuration(self) -> None:
        """JSON projection includes configuration."""
        screen = ForgeScreen(
            ForgeScreenState(
                agent_id="test-id",
                name="Test Agent",
                phase="active",
                capability=0.8,
            )
        )
        result = screen.project(RenderTarget.JSON)

        assert "configuration" in result
        config = result["configuration"]
        assert config["agent_id"] == "test-id"
        assert config["name"] == "Test Agent"
        assert config["phase"] == "active"
        assert config["capability"] == 0.8

    def test_project_json_includes_available_phases(self) -> None:
        """JSON projection includes available phases."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.JSON)

        assert "available_phases" in result
        assert set(result["available_phases"]) == set(AVAILABLE_PHASES)

    def test_project_json_includes_preview_card(self) -> None:
        """JSON projection includes preview card."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.JSON)

        assert "preview_card" in result
        assert result["preview_card"]["type"] == "agent_card"

    def test_project_json_includes_capability_bar(self) -> None:
        """JSON projection includes capability bar."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.JSON)

        assert "capability_bar" in result


class TestForgeScreenProjectMarimo:
    """Tests for marimo/HTML projection."""

    def test_project_marimo_returns_string(self) -> None:
        """Marimo projection returns HTML string."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.MARIMO)
        assert isinstance(result, str)

    def test_project_marimo_is_html(self) -> None:
        """Marimo projection is HTML structure."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.MARIMO)
        assert "<div" in result
        assert "kgents-forge" in result

    def test_project_marimo_includes_mode(self) -> None:
        """Marimo projection includes mode in header."""
        screen = ForgeScreen(ForgeScreenState(mode="edit"))
        result = screen.project(RenderTarget.MARIMO)
        assert "EDIT" in result

    def test_project_marimo_includes_phase_selector(self) -> None:
        """Marimo projection includes phase selector."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.MARIMO)
        # Should have phase buttons/options
        for phase in AVAILABLE_PHASES:
            assert phase in result


class TestForgeScreenProjectTUI:
    """Tests for TUI/Textual projection."""

    def test_project_tui_returns_something(self) -> None:
        """TUI projection returns Panel or fallback."""
        screen = ForgeScreen()
        result = screen.project(RenderTarget.TUI)

        try:
            from rich.panel import Panel

            assert isinstance(result, Panel)
        except ImportError:
            assert isinstance(result, str)


class TestForgeScreenComposition:
    """Tests verifying proper composition from Wave 1-3 primitives."""

    def test_composes_agent_card(self) -> None:
        """Forge composes AgentCardWidget for preview."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget

        screen = ForgeScreen()
        screen.project(RenderTarget.CLI)

        assert isinstance(screen.slots["preview_card"], AgentCardWidget)

    def test_composes_bar(self) -> None:
        """Forge composes BarWidget for capability."""
        from agents.i.reactive.primitives.bar import BarWidget

        screen = ForgeScreen()
        screen.project(RenderTarget.CLI)

        assert isinstance(screen.slots["capability_bar"], BarWidget)

    def test_composes_glyphs(self) -> None:
        """Forge composes GlyphWidget for phase selector."""
        from agents.i.reactive.primitives.glyph import GlyphWidget

        screen = ForgeScreen()
        screen.project(RenderTarget.CLI)

        for phase in AVAILABLE_PHASES:
            assert isinstance(screen.slots[f"phase_{phase}"], GlyphWidget)

    def test_entropy_flows_to_preview(self) -> None:
        """Entropy value propagates to preview card."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget

        screen = ForgeScreen(ForgeScreenState(entropy=0.5))
        screen.project(RenderTarget.CLI)

        preview_widget = screen.slots["preview_card"]
        assert isinstance(preview_widget, AgentCardWidget)
        assert preview_widget.state.value.entropy == 0.5

    def test_time_flows_to_children(self) -> None:
        """Time value propagates to child widgets."""
        from agents.i.reactive.primitives.agent_card import AgentCardWidget

        screen = ForgeScreen(ForgeScreenState(t=1000.0))
        screen.project(RenderTarget.CLI)

        preview_widget = screen.slots["preview_card"]
        assert isinstance(preview_widget, AgentCardWidget)
        assert preview_widget.state.value.t == 1000.0


class TestForgeScreenDeterminism:
    """Tests for deterministic rendering."""

    def test_same_state_same_output(self) -> None:
        """Same state always produces same output."""
        state = ForgeScreenState(
            agent_id="test",
            name="Test Agent",
            phase="active",
            capability=0.75,
            entropy=0.3,
            seed=42,
            t=1000.0,
        )

        screen1 = ForgeScreen(state)
        screen2 = ForgeScreen(state)

        assert screen1.project(RenderTarget.CLI) == screen2.project(RenderTarget.CLI)
        assert screen1.project(RenderTarget.JSON) == screen2.project(RenderTarget.JSON)
        assert screen1.project(RenderTarget.MARIMO) == screen2.project(
            RenderTarget.MARIMO
        )


class TestForgeScreenModes:
    """Tests for different forge modes."""

    def test_create_mode_header(self) -> None:
        """Create mode shows appropriate header."""
        screen = ForgeScreen(ForgeScreenState(mode="create"))
        result = screen.project(RenderTarget.CLI)
        assert "CREATE" in result

    def test_edit_mode_header(self) -> None:
        """Edit mode shows appropriate header."""
        screen = ForgeScreen(ForgeScreenState(mode="edit"))
        result = screen.project(RenderTarget.CLI)
        assert "EDIT" in result

    def test_preview_mode_header(self) -> None:
        """Preview mode shows appropriate header."""
        screen = ForgeScreen(ForgeScreenState(mode="preview"))
        result = screen.project(RenderTarget.CLI)
        assert "PREVIEW" in result
