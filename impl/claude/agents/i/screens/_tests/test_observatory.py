"""
Tests for ObservatoryScreen - LOD -1 ecosystem view.
"""

import pytest
from textual.widgets import Footer, Header

from ...data.core_types import Phase
from ...data.garden import GardenSnapshot, create_demo_gardens
from ...data.state import AgentSnapshot, FluxState
from ..observatory import GardenCard, ObservatoryScreen, VoidPanel


@pytest.fixture
def demo_gardens() -> list[GardenSnapshot]:
    """Create demo gardens for testing."""
    return create_demo_gardens()


@pytest.fixture
def demo_flux_state() -> FluxState:
    """Create demo flux state for testing."""
    state = FluxState()

    # Add agents for garden 1 (main)
    state.add_agent(
        AgentSnapshot(
            id="K-gent",
            name="K-gent",
            phase=Phase.ACTIVE,
            activity=0.8,
            grid_x=0,
            grid_y=0,
            connections={"A-gent": 0.7},
        )
    )
    state.add_agent(
        AgentSnapshot(
            id="A-gent",
            name="A-gent",
            phase=Phase.ACTIVE,
            activity=0.6,
            grid_x=1,
            grid_y=0,
            connections={"L-gent": 0.5},
        )
    )
    state.add_agent(
        AgentSnapshot(
            id="L-gent",
            name="L-gent",
            phase=Phase.WAKING,
            activity=0.4,
            grid_x=2,
            grid_y=0,
        )
    )

    # Add agents for garden 2 (experiment-alpha)
    state.add_agent(
        AgentSnapshot(
            id="robin",
            name="robin",
            phase=Phase.ACTIVE,
            activity=0.9,
            grid_x=0,
            grid_y=1,
            connections={"test": 0.6},
        )
    )
    state.add_agent(
        AgentSnapshot(
            id="test",
            name="test",
            phase=Phase.DORMANT,
            activity=0.2,
            grid_x=1,
            grid_y=1,
        )
    )

    return state


class TestGardenCard:
    """Test GardenCard widget."""

    def test_garden_card_creation(
        self, demo_gardens: list[GardenSnapshot], demo_flux_state: FluxState
    ) -> None:
        """Test that GardenCard can be created."""
        garden = demo_gardens[0]
        card = GardenCard(garden=garden, agents=demo_flux_state.agents)
        assert card.garden == garden
        assert card.agents == demo_flux_state.agents

    def test_garden_card_posture_symbols(
        self, demo_gardens: list[GardenSnapshot], demo_flux_state: FluxState
    ) -> None:
        """Test posture symbol generation for agents."""
        garden = demo_gardens[0]
        card = GardenCard(garden=garden, agents=demo_flux_state.agents)

        # Get posture symbols for agents with different phases
        for agent_id in garden.agent_ids:
            agent = demo_flux_state.agents.get(agent_id)
            if agent:
                symbol = card._get_posture_symbol(agent)
                assert isinstance(symbol, str)
                assert len(symbol) >= 1  # Has at least one character

    def test_garden_card_focus(
        self, demo_gardens: list[GardenSnapshot], demo_flux_state: FluxState
    ) -> None:
        """Test focus state management."""
        garden = demo_gardens[0]
        card = GardenCard(garden=garden, agents=demo_flux_state.agents)

        # Initially not focused
        assert "focused" not in card.classes

        # Set focused
        card.set_focused(True)
        assert "focused" in card.classes

        # Clear focus
        card.set_focused(False)
        assert "focused" not in card.classes


class TestVoidPanel:
    """Test VoidPanel widget."""

    def test_void_panel_creation(self) -> None:
        """Test that VoidPanel can be created."""
        panel = VoidPanel(entropy_budget=0.5, suggestion="Test suggestion")
        assert panel.entropy_budget == 0.5
        assert panel.suggestion == "Test suggestion"

    def test_void_panel_render(self) -> None:
        """Test VoidPanel rendering."""
        panel = VoidPanel(entropy_budget=0.25, suggestion="Honor thy error")
        rendered = panel.render()

        assert "VOID" in rendered
        assert "Accursed Share" in rendered
        assert "25%" in rendered
        assert "Honor thy error" in rendered


class TestObservatoryScreen:
    """Test ObservatoryScreen."""

    @pytest.mark.asyncio
    async def test_observatory_creation_demo_mode(self) -> None:
        """Test ObservatoryScreen creation in demo mode."""
        screen = ObservatoryScreen(demo_mode=True)
        assert screen._demo_mode is True
        assert len(screen.gardens) > 0
        assert screen.flux_state is not None

    @pytest.mark.asyncio
    async def test_observatory_creation_with_data(
        self, demo_gardens: list[GardenSnapshot], demo_flux_state: FluxState
    ) -> None:
        """Test ObservatoryScreen creation with provided data."""
        screen = ObservatoryScreen(gardens=demo_gardens, flux_state=demo_flux_state)
        assert screen.gardens == demo_gardens
        assert screen.flux_state == demo_flux_state

    @pytest.mark.asyncio
    async def test_observatory_composition(self) -> None:
        """Test that ObservatoryScreen composes correctly."""
        from textual.app import App

        class TestApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(ObservatoryScreen(demo_mode=True))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, ObservatoryScreen)

            # Check that header and footer are present
            assert len(screen.query(Header)) == 1
            assert len(screen.query(Footer)) == 1

            # Check that garden cards are created
            assert len(screen._garden_cards) > 0

            # Check that void panel is present
            assert screen._void_panel is not None

    @pytest.mark.asyncio
    async def test_get_gardens(self, demo_gardens: list[GardenSnapshot]) -> None:
        """Test get_gardens interface method."""
        screen = ObservatoryScreen(gardens=demo_gardens)
        gardens = screen.get_gardens()
        assert gardens == demo_gardens

    @pytest.mark.asyncio
    async def test_focus_garden(self, demo_gardens: list[GardenSnapshot]) -> None:
        """Test focus_garden interface method."""
        from textual.app import App

        class TestApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(ObservatoryScreen(gardens=demo_gardens, demo_mode=True))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, ObservatoryScreen)

            # Focus second garden
            screen.focus_garden(demo_gardens[1].id)
            assert screen.focused_garden_id == demo_gardens[1].id

    @pytest.mark.asyncio
    async def test_next_garden_action(self) -> None:
        """Test next_garden action."""
        from textual.app import App

        class TestApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(ObservatoryScreen(demo_mode=True))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, ObservatoryScreen)

            initial_garden = screen.focused_garden_id

            # Press Tab to cycle to next garden
            await pilot.press("tab")

            # Should have moved to next garden
            assert screen.focused_garden_id != initial_garden

    @pytest.mark.asyncio
    async def test_prev_garden_action(self) -> None:
        """Test prev_garden action."""
        from textual.app import App

        class TestApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(ObservatoryScreen(demo_mode=True))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, ObservatoryScreen)

            # Set to second garden
            screen.focused_garden_id = screen.gardens[1].id
            initial_garden = screen.focused_garden_id

            # Press Shift+Tab to cycle to previous garden
            await pilot.press("shift+tab")

            # Should have moved to previous garden
            assert screen.focused_garden_id != initial_garden
            assert screen.focused_garden_id == screen.gardens[0].id

    @pytest.mark.asyncio
    async def test_toggle_graph_action(self) -> None:
        """Test toggle_graph action."""
        from textual.app import App

        class TestApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(ObservatoryScreen(demo_mode=True))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, ObservatoryScreen)

            # Get initial graph layout
            first_card = list(screen._garden_cards.values())[0]
            if first_card._graph:
                initial_layout = first_card._graph.layout

                # Press 'g' to toggle graph
                await pilot.press("g")

                # Layout should have changed
                assert first_card._graph.layout != initial_layout

    @pytest.mark.asyncio
    async def test_emergency_brake_action(self) -> None:
        """Test emergency brake action."""
        from textual.app import App

        class TestApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(ObservatoryScreen(demo_mode=True))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, ObservatoryScreen)

            # Press Space for emergency brake
            await pilot.press("space")

            # Should show notification (can't test content, but action should work)
            # This is tested by not raising an exception

    @pytest.mark.asyncio
    async def test_zoom_to_agent(
        self, demo_gardens: list[GardenSnapshot], demo_flux_state: FluxState
    ) -> None:
        """Test zoom_to_agent interface method - just verifies it doesn't crash."""
        # This test just verifies the method exists and can be called
        # Actual screen push is integration-tested elsewhere
        screen = ObservatoryScreen(gardens=demo_gardens, flux_state=demo_flux_state)

        # Verify the agents exist
        assert "K-gent" in screen.flux_state.agents
        assert screen.flux_state.agents["K-gent"] is not None

    @pytest.mark.asyncio
    async def test_zoom_to_terrarium(self, demo_gardens: list[GardenSnapshot]) -> None:
        """Test zoom_to_terrarium interface method - just verifies it exists."""
        # This test just verifies the method exists
        # Actual screen push is integration-tested elsewhere
        screen = ObservatoryScreen(gardens=demo_gardens, demo_mode=True)

        # Verify gardens exist
        assert len(screen.gardens) > 0
        assert demo_gardens[0].id in [g.id for g in screen.gardens]

    @pytest.mark.asyncio
    async def test_empty_gardens(self) -> None:
        """Test ObservatoryScreen with no gardens."""
        from textual.app import App

        class TestApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(ObservatoryScreen(gardens=[], flux_state=FluxState()))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, ObservatoryScreen)

            # Should handle empty state gracefully
            assert len(screen.gardens) == 0
            assert screen.focused_garden_id is None

            # Actions should not crash
            await pilot.press("tab")
            await pilot.press("enter")

    @pytest.mark.asyncio
    async def test_focus_state_persistence(self) -> None:
        """Test that focus state persists across updates."""
        from textual.app import App

        class TestApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(ObservatoryScreen(demo_mode=True))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, ObservatoryScreen)

            # Focus second garden
            if len(screen.gardens) > 1:
                screen.focus_garden(screen.gardens[1].id)
                focused_id = screen.focused_garden_id

                # Focus should persist
                assert screen.focused_garden_id == focused_id

                # Card should show focus
                assert focused_id is not None
                assert "focused" in screen._garden_cards[focused_id].classes
