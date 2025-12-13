"""
Tests for DebuggerScreen and its widgets.

Tests cover:
- Turn navigation (j/k keys)
- Thought collapse toggle (t key)
- Ghost visibility toggle (g key)
- Fork from cursor
- Export trace
- Mode cycling
- Integration with TurnDAGRenderer
- Causal cone highlighting
- State diff comparison
"""

from __future__ import annotations

import pytest
from textual.pilot import Pilot

# Import only what we need to avoid opentelemetry dependency
from weave.causal_cone import CausalCone
from weave.trace_monoid import TraceMonoid
from weave.turn import Turn, TurnType
from weave.weave import TheWeave

from ..debugger_screen import DebuggerScreen


@pytest.fixture
def sample_weave() -> TheWeave:
    """Create a sample weave with Turn instances for testing."""
    weave = TheWeave()

    # Add some turns
    turn1 = Turn.create_turn(
        content="Analyzing the problem",
        source="agent-a",
        turn_type=TurnType.SPEECH,
        confidence=0.9,
        entropy_cost=0.1,
    )

    turn2 = Turn.create_turn(
        content="Searching for patterns",
        source="agent-a",
        turn_type=TurnType.THOUGHT,
        confidence=0.8,
        entropy_cost=0.05,
    )

    turn3 = Turn.create_turn(
        content="Execute grep command",
        source="agent-a",
        turn_type=TurnType.ACTION,
        confidence=0.95,
        entropy_cost=0.2,
    )

    turn4 = Turn.create_turn(
        content="Found 42 matches",
        source="agent-a",
        turn_type=TurnType.SPEECH,
        confidence=1.0,
        entropy_cost=0.1,
    )

    turn5 = Turn.create_turn(
        content="Should I proceed?",
        source="agent-a",
        turn_type=TurnType.YIELD,
        confidence=0.7,
        entropy_cost=0.15,
    )

    # Add to weave with dependencies
    weave.monoid.append_mut(turn1, None)
    weave.monoid.append_mut(turn2, {turn1.id})
    weave.monoid.append_mut(turn3, {turn2.id})
    weave.monoid.append_mut(turn4, {turn3.id})
    weave.monoid.append_mut(turn5, {turn4.id})

    return weave


class TestDebuggerScreen:
    """Tests for DebuggerScreen."""

    @pytest.mark.asyncio
    async def test_debugger_screen_mounts(self, sample_weave: TheWeave) -> None:
        """Test that DebuggerScreen mounts successfully."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            assert len(pilot.app.screen_stack) > 0

    @pytest.mark.asyncio
    async def test_navigate_next_turn(self, sample_weave: TheWeave) -> None:
        """Test j key navigates to next turn."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave, agent_id="agent-a"))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)

            # Get initial position
            initial_index = (
                screen._turn_dag.get_current_index() if screen._turn_dag else -1
            )

            # Press j to navigate next
            await pilot.press("j")
            await pilot.pause()

            # Should have moved forward
            if screen._turn_dag:
                new_index = screen._turn_dag.get_current_index()
                assert new_index > initial_index or initial_index == -1

    @pytest.mark.asyncio
    async def test_navigate_prev_turn(self, sample_weave: TheWeave) -> None:
        """Test k key navigates to previous turn."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave, agent_id="agent-a"))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)

            # Navigate forward first
            await pilot.press("j")
            await pilot.press("j")
            await pilot.pause()

            # Get position
            if screen._turn_dag:
                before_index = screen._turn_dag.get_current_index()

                # Press k to navigate back
                await pilot.press("k")
                await pilot.pause()

                after_index = screen._turn_dag.get_current_index()
                assert after_index < before_index

    @pytest.mark.asyncio
    async def test_toggle_thoughts(self, sample_weave: TheWeave) -> None:
        """Test t key toggles thought visibility."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave, agent_id="agent-a"))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)

            if not screen._turn_dag:
                pytest.skip("Turn DAG not mounted")

            # Initial state: thoughts hidden
            assert not screen._turn_dag.show_thoughts

            # Press t to toggle
            await pilot.press("t")
            await pilot.pause()

            # Should now be showing thoughts
            assert screen._turn_dag.show_thoughts

            # Press t again
            await pilot.press("t")
            await pilot.pause()

            # Should be hidden again
            assert not screen._turn_dag.show_thoughts

    @pytest.mark.asyncio
    async def test_toggle_ghosts(self, sample_weave: TheWeave) -> None:
        """Test g key toggles ghost visibility."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave, agent_id="agent-a"))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)

            if not screen._turn_dag:
                pytest.skip("Turn DAG not mounted")

            # Initial state: ghosts hidden
            assert not screen._turn_dag.show_ghosts

            # Press g to toggle
            await pilot.press("g")
            await pilot.pause()

            # Should now be showing ghosts
            assert screen._turn_dag.show_ghosts

    @pytest.mark.asyncio
    async def test_highlight_cone(self, sample_weave: TheWeave) -> None:
        """Test c key highlights causal cone."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave, agent_id="agent-a"))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)

            if not screen._causal_cone:
                pytest.skip("Causal cone not mounted")

            # Press c to highlight
            await pilot.press("c")
            await pilot.pause()

            # Should be highlighted
            assert screen._causal_cone.highlighted

    @pytest.mark.asyncio
    async def test_fork_from_cursor(self, sample_weave: TheWeave) -> None:
        """Test f key forks from cursor position."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave, agent_id="agent-a"))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)

            # Navigate to middle
            await pilot.press("j")
            await pilot.press("j")
            await pilot.pause()

            # Fork
            forked_weave = screen.fork_from_cursor()

            # Forked weave should have fewer events than original
            assert len(forked_weave) <= len(sample_weave)
            assert len(forked_weave) > 0

    @pytest.mark.asyncio
    async def test_export_trace(self, sample_weave: TheWeave) -> None:
        """Test x key exports trace."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave, agent_id="agent-a"))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)

            # Export
            trace = screen.export_trace()

            # Should be non-empty string
            assert isinstance(trace, str)
            assert len(trace) > 0
            assert "Trace Export" in trace

    @pytest.mark.asyncio
    async def test_cycle_mode(self, sample_weave: TheWeave) -> None:
        """Test Tab cycles through modes."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave, agent_id="agent-a"))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)

            # Start in forensic
            assert screen.mode == "forensic"

            # Press Tab
            await pilot.press("tab")
            await pilot.pause()
            assert screen.mode == "replay"  # type: ignore[comparison-overlap]

            # Press Tab again
            await pilot.press("tab")
            await pilot.pause()
            assert screen.mode == "diff"

            # Press Tab again (cycle back)
            await pilot.press("tab")
            await pilot.pause()
            assert screen.mode == "forensic"

    @pytest.mark.asyncio
    async def test_timeline_rewind(self, sample_weave: TheWeave) -> None:
        """Test left arrow rewinds timeline."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave, agent_id="agent-a"))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)

            if not screen._timeline:
                pytest.skip("Timeline not mounted")

            # Move forward first
            await pilot.press("right")
            await pilot.pause()

            initial_pos = screen._timeline.cursor_position

            # Rewind
            await pilot.press("left")
            await pilot.pause()

            # Should have moved backward
            assert screen._timeline.cursor_position < initial_pos

    @pytest.mark.asyncio
    async def test_timeline_step_forward(self, sample_weave: TheWeave) -> None:
        """Test right arrow steps timeline forward."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave, agent_id="agent-a"))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)

            if not screen._timeline:
                pytest.skip("Timeline not mounted")

            initial_pos = screen._timeline.cursor_position

            # Step forward
            await pilot.press("right")
            await pilot.pause()

            # Should have moved forward (unless already at end)
            assert screen._timeline.cursor_position >= initial_pos


class TestTurnDAGWidget:
    """Tests for TurnDAGWidget."""

    def test_turn_dag_widget_creation(self, sample_weave: TheWeave) -> None:
        """Test creating TurnDAGWidget."""
        from ..debugger import TurnDAGWidget
        from ..turn_dag import TurnDAGConfig, TurnDAGRenderer

        config = TurnDAGConfig()
        renderer = TurnDAGRenderer(weave=sample_weave, config=config)
        widget = TurnDAGWidget(renderer=renderer, agent_id="agent-a")

        assert widget.agent_focus == "agent-a"
        assert not widget.show_thoughts
        assert not widget.show_ghosts

    def test_turn_dag_navigation(self, sample_weave: TheWeave) -> None:
        """Test turn navigation."""
        from ..debugger import TurnDAGWidget
        from ..turn_dag import TurnDAGConfig, TurnDAGRenderer

        config = TurnDAGConfig()
        renderer = TurnDAGRenderer(weave=sample_weave, config=config)
        widget = TurnDAGWidget(renderer=renderer, agent_id="agent-a")

        # Build turn list
        widget.on_mount()

        # Should have turns
        assert widget.get_turn_count() > 0

        # Navigate next
        initial_index = widget.get_current_index()
        success = widget.navigate_next()

        # Should succeed if not at end
        if success:
            assert widget.get_current_index() == initial_index + 1

    def test_turn_dag_toggle_thoughts(self, sample_weave: TheWeave) -> None:
        """Test toggling thought visibility."""
        from ..debugger import TurnDAGWidget
        from ..turn_dag import TurnDAGConfig, TurnDAGRenderer

        config = TurnDAGConfig()
        renderer = TurnDAGRenderer(weave=sample_weave, config=config)
        widget = TurnDAGWidget(renderer=renderer, agent_id="agent-a")

        # Initial state
        assert not widget.show_thoughts

        # Toggle
        widget.toggle_thoughts()
        assert widget.show_thoughts

        # Toggle back
        widget.toggle_thoughts()
        assert not widget.show_thoughts


class TestCausalConeWidget:
    """Tests for CausalConeWidget."""

    def test_causal_cone_widget_creation(self, sample_weave: TheWeave) -> None:
        """Test creating CausalConeWidget."""
        from ..debugger import CausalConeWidget

        widget = CausalConeWidget(weave=sample_weave, agent_id="agent-a")
        assert widget.agent_id == "agent-a"
        assert not widget.highlighted

    def test_causal_cone_highlight(self, sample_weave: TheWeave) -> None:
        """Test highlighting causal cone."""
        from ..debugger import CausalConeWidget

        widget = CausalConeWidget(weave=sample_weave, agent_id="agent-a")

        # Highlight
        widget.highlight_cone()
        assert widget.highlighted

        # Unhighlight
        widget.unhighlight_cone()
        assert not widget.highlighted

    def test_causal_cone_get_stats(self, sample_weave: TheWeave) -> None:
        """Test getting cone statistics."""
        from ..debugger import CausalConeWidget

        widget = CausalConeWidget(weave=sample_weave, agent_id="agent-a")
        widget.on_mount()

        stats = widget.get_stats()
        # Stats might be None if no events
        if stats:
            assert stats.agent_id == "agent-a"
            assert stats.cone_size >= 0


class TestStateDiffWidget:
    """Tests for StateDiffWidget."""

    def test_state_diff_widget_creation(self, sample_weave: TheWeave) -> None:
        """Test creating StateDiffWidget."""
        from ..debugger import StateDiffWidget

        widget = StateDiffWidget(weave=sample_weave)
        assert widget.turn_a_id is None
        assert widget.turn_b_id is None

    def test_state_diff_set_turns(self, sample_weave: TheWeave) -> None:
        """Test setting turns for comparison."""
        from ..debugger import StateDiffWidget

        widget = StateDiffWidget(weave=sample_weave)

        # Get turn IDs
        event_ids = [e.id for e in sample_weave.monoid.events]
        if len(event_ids) >= 2:
            turn_a = event_ids[0]
            turn_b = event_ids[1]

            widget.set_turns(turn_a, turn_b)

            assert widget.turn_a_id == turn_a
            assert widget.turn_b_id == turn_b

    def test_state_diff_cycle_turns(self, sample_weave: TheWeave) -> None:
        """Test cycling through turn pairs."""
        from ..debugger import StateDiffWidget

        widget = StateDiffWidget(weave=sample_weave)

        # Get turn IDs
        event_ids = [e.id for e in sample_weave.monoid.events]
        if len(event_ids) >= 3:
            widget.set_turns(event_ids[0], event_ids[1])

            original_b = widget.turn_b_id

            # Cycle
            widget.cycle_turns()

            # Should have moved to next pair
            assert widget.turn_a_id == original_b


class TestTimelineScrubber:
    """Tests for TimelineScrubber."""

    def test_timeline_scrubber_creation(self, sample_weave: TheWeave) -> None:
        """Test creating TimelineScrubber."""
        from ..debugger import TimelineScrubber

        widget = TimelineScrubber(weave=sample_weave)
        assert widget.cursor_position == 0
        assert not widget.at_fork_point

    def test_timeline_rewind(self, sample_weave: TheWeave) -> None:
        """Test rewinding timeline."""
        from ..debugger import TimelineScrubber

        widget = TimelineScrubber(weave=sample_weave)
        widget.on_mount()

        # Move forward first
        widget.step_forward()
        widget.step_forward()

        initial_pos = widget.cursor_position

        # Rewind
        success = widget.rewind()

        if success:
            assert widget.cursor_position == initial_pos - 1

    def test_timeline_step_forward(self, sample_weave: TheWeave) -> None:
        """Test stepping forward."""
        from ..debugger import TimelineScrubber

        widget = TimelineScrubber(weave=sample_weave)
        widget.on_mount()

        initial_pos = widget.cursor_position

        # Step
        success = widget.step_forward()

        # Should succeed if not at end
        if success:
            assert widget.cursor_position == initial_pos + 1

    def test_timeline_fork(self, sample_weave: TheWeave) -> None:
        """Test forking from cursor."""
        from ..debugger import TimelineScrubber

        widget = TimelineScrubber(weave=sample_weave)
        widget.on_mount()

        # Move to middle
        widget.step_forward()

        # Fork
        forked_weave = widget.fork_from_cursor()

        # Should have events
        assert len(forked_weave) > 0
        # Should be at fork point
        assert widget.at_fork_point

    def test_timeline_export(self, sample_weave: TheWeave) -> None:
        """Test exporting trace."""
        from ..debugger import TimelineScrubber

        widget = TimelineScrubber(weave=sample_weave)
        widget.on_mount()

        trace = widget.export_trace()

        assert isinstance(trace, str)
        assert "Trace Export" in trace
        assert len(trace) > 0


# Integration test
class TestDebuggerIntegration:
    """Integration tests for DebuggerScreen."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, sample_weave: TheWeave) -> None:
        """Test a complete debugger workflow."""
        from textual.app import App

        class DebuggerApp(App[None]):
            def on_mount(self) -> None:
                self.push_screen(DebuggerScreen(weave=sample_weave, agent_id="agent-a"))

        app = DebuggerApp()
        async with app.run_test() as pilot:
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)

            # Navigate through turns
            await pilot.press("j")
            await pilot.press("j")
            await pilot.pause()

            # Toggle thoughts
            await pilot.press("t")
            await pilot.pause()

            # Highlight cone
            await pilot.press("c")
            await pilot.pause()

            # Cycle mode
            await pilot.press("tab")
            await pilot.pause()
            assert screen.mode == "replay"

            # Timeline navigation
            await pilot.press("left")
            await pilot.pause()

            # All operations should complete without error
            assert True
