"""
DebuggerScreen - LOD 2 Forensic View for Turn-gents.

The Debugger provides deep forensic analysis with:
- 3 modes: forensic, replay, diff
- Turn DAG panel (main view)
- Causal cone panel
- State diff panel
- Timeline scrubber at bottom

This is Track C of the Dashboard Overhaul.

Bindings:
    j/k: Navigate turns
    t: Toggle thoughts
    g: Toggle ghosts
    c: Highlight causal cone
    f: Fork from cursor
    x: Export trace
    Tab: Cycle modes
    Esc: Back
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from .debugger import (
    CausalConeWidget,
    StateDiffWidget,
    TimelineScrubber,
    TurnDAGWidget,
)
from .turn_dag import TurnDAGConfig, TurnDAGRenderer

if TYPE_CHECKING:
    from weave import TheWeave


class ModeIndicator(Static):
    """Indicator showing current debugger mode."""

    DEFAULT_CSS = """
    ModeIndicator {
        height: 1;
        width: 100%;
        background: #252525;
        color: #f5f0e6;
        padding: 0 2;
        dock: top;
    }
    """

    mode: reactive[str] = reactive("forensic")

    def render(self) -> str:
        """Render the mode indicator."""
        mode_labels = {
            "forensic": "MODE: FORENSIC (Full Investigation)",
            "replay": "MODE: REPLAY (Time Travel)",
            "diff": "MODE: DIFF (State Comparison)",
        }
        return mode_labels.get(self.mode, f"MODE: {self.mode.upper()}")


class DebuggerScreen(Screen[None]):
    """
    Debugger Screen - LOD 2 Forensic View.

    Provides deep forensic analysis of agent execution:
    - Turn DAG visualization with navigation
    - Causal cone analysis
    - State diff comparison
    - Timeline scrubbing and forking

    Modes:
        forensic: Full DAG + cone + diff (default)
        replay: Time-travel through execution
        diff: Side-by-side state comparison
    """

    CSS = """
    DebuggerScreen {
        background: #1a1a1a;
    }

    DebuggerScreen #main-container {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
        padding: 1;
        height: auto;
    }

    DebuggerScreen #turn-dag-container {
        column-span: 2;
        height: 20;
    }

    DebuggerScreen #cone-container {
        height: 15;
    }

    DebuggerScreen #diff-container {
        height: 15;
    }

    DebuggerScreen #timeline-container {
        dock: bottom;
        height: 7;
    }
    """

    BINDINGS = [
        Binding("j", "navigate_next", "Next Turn", show=True),
        Binding("k", "navigate_prev", "Prev Turn", show=True),
        Binding("t", "toggle_thoughts", "Toggle Thoughts", show=True),
        Binding("g", "toggle_ghosts", "Toggle Ghosts", show=True),
        Binding("c", "highlight_cone", "Highlight Cone", show=True),
        Binding("minus", "back", "Zoom Out", show=True),
        Binding("underscore", "back", "Zoom Out", show=False),
        Binding("x", "export_trace", "Export", show=True),
        Binding("tab", "cycle_mode", "Cycle Mode", show=False),
        Binding("left", "timeline_rewind", "◀ Rewind", show=False),
        Binding("right", "timeline_step", "▶ Step", show=False),
        Binding("escape", "back", "Back", show=True),
        Binding("q", "quit", "Quit", show=False),
    ]

    # Reactive properties
    mode: reactive[Literal["forensic", "replay", "diff"]] = reactive("forensic")

    def __init__(
        self,
        weave: TheWeave,
        agent_id: str | None = None,
        mode: Literal["forensic", "replay", "diff"] = "forensic",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Initialize the DebuggerScreen.

        Args:
            weave: The Weave to debug
            agent_id: Optional agent to focus on
            mode: Initial mode (forensic, replay, diff)
            name: Screen name
            id: Screen ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.weave = weave
        self.agent_id = agent_id
        self.mode = mode

        # Widgets (set in compose)
        self._mode_indicator: ModeIndicator | None = None
        self._turn_dag: TurnDAGWidget | None = None
        self._causal_cone: CausalConeWidget | None = None
        self._state_diff: StateDiffWidget | None = None
        self._timeline: TimelineScrubber | None = None

    def compose(self) -> ComposeResult:
        """Compose the debugger screen."""
        yield Header()

        # Mode indicator
        self._mode_indicator = ModeIndicator()
        self._mode_indicator.mode = self.mode
        yield self._mode_indicator

        # Main container with grid layout
        with Container(id="main-container"):
            # Turn DAG (spans 2 columns)
            with Container(id="turn-dag-container"):
                config = TurnDAGConfig(
                    show_thoughts=False,
                    show_timestamps=True,
                    show_confidence=True,
                    highlight_cone=True,
                )
                renderer = TurnDAGRenderer(weave=self.weave, config=config)
                self._turn_dag = TurnDAGWidget(
                    renderer=renderer,
                    agent_id=self.agent_id,
                )
                yield self._turn_dag

            # Causal Cone
            with Container(id="cone-container"):
                self._causal_cone = CausalConeWidget(
                    weave=self.weave,
                    agent_id=self.agent_id,
                )
                yield self._causal_cone

            # State Diff
            with Container(id="diff-container"):
                self._state_diff = StateDiffWidget(weave=self.weave)
                yield self._state_diff

        # Timeline scrubber at bottom
        with Container(id="timeline-container"):
            self._timeline = TimelineScrubber(weave=self.weave)
            yield self._timeline

        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Sync widgets to initial state
        self._sync_widgets_to_mode()

        # If we have an agent, set up initial state
        if self.agent_id and self._turn_dag:
            # Auto-select first turn for diff
            if self._turn_dag.get_turn_count() >= 2:
                self._update_diff_from_dag()

    def navigate_to_turn(self, turn_id: str) -> None:
        """
        Navigate to a specific turn.

        Args:
            turn_id: Turn ID to navigate to
        """
        if self._timeline:
            # Find the turn in timeline
            event_ids = [e.id for e in self.weave.monoid.events]
            try:
                index = event_ids.index(turn_id)
                self._timeline.jump_to_event(index)
            except ValueError:
                pass

    def toggle_thoughts(self) -> None:
        """Toggle thought visibility."""
        if self._turn_dag:
            self._turn_dag.toggle_thoughts()

    def toggle_ghosts(self) -> None:
        """Toggle ghost branch visibility."""
        if self._turn_dag:
            self._turn_dag.toggle_ghosts()

    def highlight_cone(self) -> None:
        """Highlight the causal cone."""
        if self._causal_cone:
            self._causal_cone.highlight_cone()
            # Auto-unhighlight after 2 seconds
            self.set_timer(2.0, self._unhighlight_cone)

    def fork_from_cursor(self) -> TheWeave:
        """
        Fork a new Weave from cursor position.

        Returns:
            New TheWeave forked from cursor
        """
        if not self._timeline:
            from weave import TheWeave

            return TheWeave()

        new_weave = self._timeline.fork_from_cursor()
        self.notify(f"Forked weave with {len(new_weave)} events")
        return new_weave

    def export_trace(self) -> str:
        """
        Export the trace as text.

        Returns:
            String representation of the trace
        """
        if not self._timeline:
            return "# No timeline available"

        trace = self._timeline.export_trace()
        self.notify("Trace exported (returned as string)")
        return trace

    # ========================================================================
    # Actions (Key Bindings)
    # ========================================================================

    def action_navigate_next(self) -> None:
        """Navigate to next turn (j key)."""
        if self._turn_dag:
            if self._turn_dag.navigate_next():
                self._update_diff_from_dag()
                self._sync_timeline_to_dag()

    def action_navigate_prev(self) -> None:
        """Navigate to previous turn (k key)."""
        if self._turn_dag:
            if self._turn_dag.navigate_prev():
                self._update_diff_from_dag()
                self._sync_timeline_to_dag()

    def action_toggle_thoughts(self) -> None:
        """Toggle thought visibility (t key)."""
        self.toggle_thoughts()

    def action_toggle_ghosts(self) -> None:
        """Toggle ghost visibility (g key)."""
        self.toggle_ghosts()

    def action_highlight_cone(self) -> None:
        """Highlight causal cone (c key)."""
        self.highlight_cone()

    def action_fork_from_cursor(self) -> None:
        """Fork from cursor (f key)."""
        self.fork_from_cursor()

    def action_export_trace(self) -> None:
        """Export trace (x key)."""
        trace = self.export_trace()
        # In a real implementation, we might save to file or copy to clipboard
        # For now, just notify
        self.notify(f"Exported {len(trace)} characters")

    def action_cycle_mode(self) -> None:
        """Cycle through modes (Tab key)."""
        modes: list[Literal["forensic", "replay", "diff"]] = [
            "forensic",
            "replay",
            "diff",
        ]
        current_index = modes.index(self.mode)
        next_index = (current_index + 1) % len(modes)
        self.mode = modes[next_index]

        if self._mode_indicator:
            self._mode_indicator.mode = self.mode

        self._sync_widgets_to_mode()
        self.notify(f"Mode: {self.mode.upper()}")

    def action_timeline_rewind(self) -> None:
        """Rewind timeline (◀ left arrow)."""
        if self._timeline:
            if self._timeline.rewind():
                self._sync_dag_to_timeline()

    def action_timeline_step(self) -> None:
        """Step timeline forward (▶ right arrow)."""
        if self._timeline:
            if self._timeline.step_forward():
                self._sync_dag_to_timeline()

    def action_back(self) -> None:
        """Go back (Escape)."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit application (q)."""
        self.app.exit()

    # ========================================================================
    # Internal Sync Methods
    # ========================================================================

    def _sync_widgets_to_mode(self) -> None:
        """Sync widget visibility based on current mode."""
        if self.mode == "forensic":
            # Show all widgets
            self._show_all_widgets()
        elif self.mode == "replay":
            # Focus on timeline and DAG
            self._show_replay_widgets()
        elif self.mode == "diff":
            # Focus on state diff
            self._show_diff_widgets()

    def _show_all_widgets(self) -> None:
        """Show all widgets (forensic mode)."""
        # All widgets visible by default
        pass

    def _show_replay_widgets(self) -> None:
        """Show replay-focused widgets."""
        # Could hide cone/diff, but for now keep all visible
        pass

    def _show_diff_widgets(self) -> None:
        """Show diff-focused widgets."""
        # Could hide cone, but for now keep all visible
        pass

    def _update_diff_from_dag(self) -> None:
        """Update state diff based on current DAG selection."""
        if not self._turn_dag or not self._state_diff:
            return

        selected = self._turn_dag.get_selected_turn()
        if not selected:
            return

        # Get previous turn for comparison
        current_index = self._turn_dag.get_current_index()
        if current_index > 0:
            all_turns = [e.id for e in self.weave.monoid.events]
            if current_index < len(all_turns):
                prev_turn_id = all_turns[current_index - 1]
                curr_turn_id = all_turns[current_index]
                self._state_diff.set_turns(prev_turn_id, curr_turn_id)

    def _sync_timeline_to_dag(self) -> None:
        """Sync timeline cursor to DAG selection."""
        if not self._turn_dag or not self._timeline:
            return

        selected = self._turn_dag.get_selected_turn()
        if not selected:
            return

        # Find turn index
        event_ids = [e.id for e in self.weave.monoid.events]
        try:
            index = event_ids.index(selected.turn_id)
            self._timeline.jump_to_event(index)
        except ValueError:
            pass

    def _sync_dag_to_timeline(self) -> None:
        """Sync DAG selection to timeline cursor."""
        if not self._turn_dag or not self._timeline:
            return

        cursor_event_id = self._timeline.get_cursor_event_id()
        if cursor_event_id:
            # Find the turn in DAG
            event_ids = [e.id for e in self.weave.monoid.events]
            try:
                index = event_ids.index(cursor_event_id)
                # Navigate DAG to this position
                # Note: This is a simplified sync - real impl would be more sophisticated
                while self._turn_dag.get_current_index() < index:
                    if not self._turn_dag.navigate_next():
                        break
                while self._turn_dag.get_current_index() > index:
                    if not self._turn_dag.navigate_prev():
                        break

                self._update_diff_from_dag()
            except ValueError:
                pass

    def _unhighlight_cone(self) -> None:
        """Unhighlight the causal cone."""
        if self._causal_cone:
            self._causal_cone.unhighlight_cone()


__all__ = ["DebuggerScreen"]
