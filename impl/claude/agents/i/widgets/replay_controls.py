"""
ReplayControlsWidget: Playback controls for scenario replay.

Shows:
- Play/Pause button (space)
- Speed indicator with cycle (s)
- Progress bar with time scrubbing
- Current turn preview

Layout:
┌─────────────────────────────────────────────────────────┐
│ ▶ PLAYING  1.0x │ ████████░░░░░░░░░░░░ 40% │ 15:00    │
│ "FEVER MODE: Forced creative discharge via oblique..."  │
└─────────────────────────────────────────────────────────┘

Keybindings:
- Space: Play/Pause
- s: Cycle speed
- [/]: Seek hour backward/forward
- 0-9: Jump to hour (0=midnight, 9=21:00)

Philosophy: "The demo IS the system showing itself."
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, ProgressBar, Static

if TYPE_CHECKING:
    from ..data.replay_integration import ReplayState, ScenarioReplayProvider


class ReplayControlsWidget(Widget, can_focus=True):
    """
    Playback controls for scenario replay.

    Provides visual feedback and keyboard controls for:
    - Play/Pause toggle
    - Speed cycling
    - Progress scrubbing
    - Hour jumping
    """

    DEFAULT_CSS = """
    ReplayControlsWidget {
        width: 100%;
        height: 3;
        background: #252525;
        border: round #4a4a5c;
        padding: 0 1;
    }

    ReplayControlsWidget:focus {
        border: double #8ac4e8;
    }

    ReplayControlsWidget #controls-row {
        width: 100%;
        height: 1;
    }

    ReplayControlsWidget #play-button {
        width: 10;
        min-width: 10;
        color: #7d9c7a;
    }

    ReplayControlsWidget #play-button.paused {
        color: #e6a352;
    }

    ReplayControlsWidget #speed-label {
        width: 6;
        color: #8ac4e8;
    }

    ReplayControlsWidget #progress-bar {
        width: 1fr;
        color: #6a6560;
    }

    ReplayControlsWidget #time-label {
        width: 7;
        color: #f5f0e6;
        text-align: right;
    }

    ReplayControlsWidget #turn-preview {
        width: 100%;
        height: 1;
        color: #6a6560;
    }
    """

    BINDINGS = [
        Binding("space", "toggle_play", "Play/Pause"),
        Binding("s", "cycle_speed", "Speed"),
        Binding("bracketleft", "seek_back", "Hour Back"),
        Binding("bracketright", "seek_forward", "Hour Forward"),
        Binding("0", "jump_0", "00:00"),
        Binding("1", "jump_1", "03:00"),
        Binding("2", "jump_2", "06:00"),
        Binding("3", "jump_3", "09:00"),
        Binding("4", "jump_4", "12:00"),
        Binding("5", "jump_5", "15:00"),
        Binding("6", "jump_6", "18:00"),
        Binding("7", "jump_7", "21:00"),
    ]

    # Reactive state
    is_playing: reactive[bool] = reactive(False)
    speed: reactive[float] = reactive(1.0)
    progress: reactive[float] = reactive(0.0)
    current_hour: reactive[int] = reactive(0)
    turn_preview: reactive[str] = reactive("")

    def __init__(
        self,
        provider: ScenarioReplayProvider | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._provider = provider
        self._on_state_callbacks: list[Callable[[ReplayState], None]] = []

    def set_provider(self, provider: ScenarioReplayProvider) -> None:
        """Set the replay provider and wire callbacks."""
        self._provider = provider
        provider.on_state_change = self._on_state_change

    def compose(self) -> ComposeResult:
        with Horizontal(id="controls-row"):
            yield Static(self._render_play_button(), id="play-button")
            yield Static(self._render_speed(), id="speed-label")
            yield Static(self._render_progress(), id="progress-bar")
            yield Static(self._render_time(), id="time-label")
        yield Static(self._render_preview(), id="turn-preview")

    def _render_play_button(self) -> str:
        """Render play/pause button."""
        if self.is_playing:
            return "⏸ PLAYING"
        else:
            return "▶ PAUSED"

    def _render_speed(self) -> str:
        """Render speed indicator."""
        return f"{self.speed:.1f}x"

    def _render_progress(self) -> str:
        """Render progress bar."""
        width = 20
        filled = int(self.progress * width)
        bar = "█" * filled + "░" * (width - filled)
        pct = int(self.progress * 100)
        return f"{bar} {pct}%"

    def _render_time(self) -> str:
        """Render current time."""
        return f"{self.current_hour:02d}:00"

    def _render_preview(self) -> str:
        """Render turn preview."""
        if not self.turn_preview:
            return "(no turn)"
        # Truncate to fit
        max_len = 60
        preview = self.turn_preview
        if len(preview) > max_len:
            preview = preview[: max_len - 3] + "..."
        return f'"{preview}"'

    def _on_state_change(self, state: ReplayState) -> None:
        """Handle replay state changes."""
        self.is_playing = state.state.name == "PLAYING"
        self.speed = state.speed
        self.progress = state.progress
        self.current_hour = state.current_hour

        # Get turn preview
        if self._provider:
            turn = self._provider._controller.get_current_turn()
            self.turn_preview = turn.content if turn else ""

        # Update UI
        self._update_display()

        # Notify callbacks
        for cb in self._on_state_callbacks:
            cb(state)

    def _update_display(self) -> None:
        """Update all display elements."""
        if play_btn := self.query_one("#play-button", Static):
            play_btn.update(self._render_play_button())
            play_btn.set_class(not self.is_playing, "paused")

        if speed_lbl := self.query_one("#speed-label", Static):
            speed_lbl.update(self._render_speed())

        if progress_bar := self.query_one("#progress-bar", Static):
            progress_bar.update(self._render_progress())

        if time_lbl := self.query_one("#time-label", Static):
            time_lbl.update(self._render_time())

        if preview := self.query_one("#turn-preview", Static):
            preview.update(self._render_preview())

    def watch_is_playing(self, value: bool) -> None:
        """React to is_playing changes."""
        self._update_display()

    def watch_speed(self, value: float) -> None:
        """React to speed changes."""
        self._update_display()

    def watch_progress(self, value: float) -> None:
        """React to progress changes."""
        self._update_display()

    def watch_current_hour(self, value: int) -> None:
        """React to hour changes."""
        self._update_display()

    # =========================================================================
    # Actions
    # =========================================================================

    def action_toggle_play(self) -> None:
        """Toggle play/pause."""
        if self._provider:
            self._provider.toggle_pause()

    def action_cycle_speed(self) -> None:
        """Cycle through speed presets."""
        if self._provider:
            self._provider.cycle_speed()

    def action_seek_back(self) -> None:
        """Seek one hour back."""
        if self._provider:
            new_hour = max(0, self.current_hour - 1)
            self._provider.seek_to_hour(new_hour)

    def action_seek_forward(self) -> None:
        """Seek one hour forward."""
        if self._provider:
            new_hour = min(23, self.current_hour + 1)
            self._provider.seek_to_hour(new_hour)

    def _jump_to_hour(self, hour: int) -> None:
        """Jump to a specific hour."""
        if self._provider:
            self._provider.seek_to_hour(hour)

    def action_jump_0(self) -> None:
        self._jump_to_hour(0)

    def action_jump_1(self) -> None:
        self._jump_to_hour(3)

    def action_jump_2(self) -> None:
        self._jump_to_hour(6)

    def action_jump_3(self) -> None:
        self._jump_to_hour(9)

    def action_jump_4(self) -> None:
        self._jump_to_hour(12)

    def action_jump_5(self) -> None:
        self._jump_to_hour(15)

    def action_jump_6(self) -> None:
        self._jump_to_hour(18)

    def action_jump_7(self) -> None:
        self._jump_to_hour(21)


# =============================================================================
# Exports
# =============================================================================

__all__ = ["ReplayControlsWidget"]
