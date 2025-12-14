"""
ReplayController - Animated playback of Turn DAG execution.

The ReplayController enables "time travel debugging" by allowing users
to watch agent reasoning unfold like a movie. Features:

- Play/Pause/Stop controls
- Speed adjustment (0.25x to 4x)
- Frame stepping (forward/backward)
- Scrubbing via timeline
- Auto-pause on key events

Usage:
    controller = ReplayController(turns)
    async for event in controller.play():
        highlight_turn(event.turn)
        update_state_diff(event)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, AsyncIterator, Callable

if TYPE_CHECKING:
    pass


class PlaybackState(Enum):
    """State of the replay controller."""

    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()


@dataclass
class Turn:
    """
    A single turn in the agent execution.

    This is a simplified representation; the real Turn would come
    from the weave/turn-gents system.
    """

    id: str
    turn_type: str  # SPEECH, ACTION, THOUGHT, YIELD, SILENCE
    content: str
    timestamp: datetime
    duration: float = 0.1  # Duration in seconds
    agent_id: str = ""
    confidence: float = 1.0
    is_ghost: bool = False  # Pruned/rejected turn
    parent_id: str | None = None
    children_ids: list[str] = field(default_factory=list)


@dataclass
class TurnHighlightEvent:
    """
    Event emitted during replay to signal which turn to highlight.

    Contains the current turn and optional context for visualization.
    """

    turn: Turn
    playhead: int  # 0-based index
    total_turns: int
    elapsed_time: timedelta
    speed: float
    is_key_moment: bool = False  # True for YIELD, errors, etc.


@dataclass
class ReplayStats:
    """Statistics about the replay session."""

    total_turns: int
    current_position: int
    elapsed_time: timedelta
    total_duration: timedelta
    speed: float
    state: PlaybackState


class ReplayController:
    """
    Controls animated playback of Turn DAG.

    Enables watching agent reasoning unfold in time:
    - Stream turns at configurable speed
    - Pause on key moments (YIELD, errors)
    - Step through turns manually
    - Scrub to any position

    The controller emits TurnHighlightEvent objects that the UI
    uses to update visualizations.
    """

    # Speed presets
    SPEED_PRESETS = {
        "0.25x": 0.25,
        "0.5x": 0.5,
        "1x": 1.0,
        "2x": 2.0,
        "4x": 4.0,
    }

    # Turn types that trigger auto-pause
    AUTO_PAUSE_TYPES = {"YIELD", "ERROR", "EXCEPTION"}

    def __init__(
        self,
        turns: list[Turn],
        auto_pause_on_key_moments: bool = True,
        on_key_moment: Callable[[Turn], None] | None = None,
    ) -> None:
        """
        Initialize the ReplayController.

        Args:
            turns: List of turns to replay
            auto_pause_on_key_moments: Pause on YIELD, errors, etc.
            on_key_moment: Optional callback for key moments
        """
        self.turns = turns
        self._playhead = 0
        self._speed = 1.0
        self._state = PlaybackState.STOPPED
        self._auto_pause = auto_pause_on_key_moments
        self._on_key_moment = on_key_moment
        self._start_time: datetime | None = None
        self._pause_event = asyncio.Event()
        self._stop_event = asyncio.Event()

        # Calculate total duration
        self._total_duration = sum(t.duration for t in turns)

    @property
    def playing(self) -> bool:
        """Check if currently playing."""
        return self._state == PlaybackState.PLAYING

    @property
    def paused(self) -> bool:
        """Check if currently paused."""
        return self._state == PlaybackState.PAUSED

    @property
    def stopped(self) -> bool:
        """Check if stopped."""
        return self._state == PlaybackState.STOPPED

    @property
    def playhead(self) -> int:
        """Get current playhead position (0-based index)."""
        return self._playhead

    @property
    def speed(self) -> float:
        """Get current playback speed."""
        return self._speed

    @property
    def progress(self) -> float:
        """Get playback progress as 0.0 to 1.0."""
        if not self.turns:
            return 0.0
        return self._playhead / len(self.turns)

    async def play(self) -> AsyncIterator[TurnHighlightEvent]:
        """
        Start playback from current position.

        Yields TurnHighlightEvent for each turn as it plays.
        Respects speed setting and auto-pause preferences.
        """
        if not self.turns:
            return

        self._state = PlaybackState.PLAYING
        self._start_time = datetime.now()
        self._stop_event.clear()
        self._pause_event.set()  # Not paused

        elapsed = timedelta()

        while self._playhead < len(self.turns) and not self._stop_event.is_set():
            # Wait if paused
            await self._pause_event.wait()

            # Check for stop
            if self._stop_event.is_set():
                break

            turn = self.turns[self._playhead]

            # Check for key moment
            is_key = turn.turn_type in self.AUTO_PAUSE_TYPES

            # Emit highlight event
            event = TurnHighlightEvent(
                turn=turn,
                playhead=self._playhead,
                total_turns=len(self.turns),
                elapsed_time=elapsed,
                speed=self._speed,
                is_key_moment=is_key,
            )
            yield event

            # Callback for key moments
            if is_key and self._on_key_moment:
                self._on_key_moment(turn)

            # Auto-pause on key moments if enabled
            if is_key and self._auto_pause:
                self._state = PlaybackState.PAUSED
                self._pause_event.clear()
                # Wait for resume
                await self._pause_event.wait()
                if self._stop_event.is_set():
                    break
                self._state = PlaybackState.PLAYING

            # Wait for turn duration (adjusted by speed)
            wait_time = turn.duration / self._speed
            await asyncio.sleep(wait_time)

            # Update elapsed time
            elapsed += timedelta(seconds=turn.duration)

            # Advance playhead
            self._playhead += 1

        # Playback complete
        if self._playhead >= len(self.turns):
            self._state = PlaybackState.STOPPED
            self._playhead = len(self.turns) - 1  # Stay on last turn

    def pause(self) -> None:
        """Pause playback."""
        if self._state == PlaybackState.PLAYING:
            self._state = PlaybackState.PAUSED
            self._pause_event.clear()

    def resume(self) -> None:
        """Resume playback from pause."""
        if self._state == PlaybackState.PAUSED:
            self._state = PlaybackState.PLAYING
            self._pause_event.set()

    def toggle_pause(self) -> None:
        """Toggle between playing and paused."""
        if self._state == PlaybackState.PLAYING:
            self.pause()
        elif self._state == PlaybackState.PAUSED:
            self.resume()

    def stop(self) -> None:
        """Stop playback and reset to beginning."""
        self._state = PlaybackState.STOPPED
        self._stop_event.set()
        self._pause_event.set()  # Unblock any waiting
        self._playhead = 0

    def seek(self, position: int) -> Turn | None:
        """
        Seek to a specific position.

        Args:
            position: 0-based turn index

        Returns:
            Turn at that position, or None if invalid
        """
        if not self.turns:
            return None

        self._playhead = max(0, min(position, len(self.turns) - 1))
        return self.turns[self._playhead]

    def seek_relative(self, delta: int) -> Turn | None:
        """
        Seek relative to current position.

        Args:
            delta: Number of turns to move (+/-)

        Returns:
            Turn at new position, or None if invalid
        """
        return self.seek(self._playhead + delta)

    def step_forward(self) -> Turn | None:
        """Step forward one turn."""
        return self.seek_relative(1)

    def step_backward(self) -> Turn | None:
        """Step backward one turn."""
        return self.seek_relative(-1)

    def set_speed(self, speed: float) -> None:
        """
        Set playback speed.

        Args:
            speed: Speed multiplier (0.25 to 4.0)
        """
        self._speed = max(0.25, min(4.0, speed))

    def set_speed_preset(self, preset: str) -> None:
        """
        Set speed using a preset name.

        Args:
            preset: One of "0.25x", "0.5x", "1x", "2x", "4x"
        """
        if preset in self.SPEED_PRESETS:
            self._speed = self.SPEED_PRESETS[preset]

    def cycle_speed(self) -> float:
        """
        Cycle through speed presets.

        Returns:
            New speed value
        """
        speeds = list(self.SPEED_PRESETS.values())
        try:
            idx = speeds.index(self._speed)
            next_idx = (idx + 1) % len(speeds)
            self._speed = speeds[next_idx]
        except ValueError:
            self._speed = 1.0
        return self._speed

    def get_current_turn(self) -> Turn | None:
        """Get the turn at current playhead position."""
        if not self.turns or self._playhead >= len(self.turns):
            return None
        return self.turns[self._playhead]

    def get_stats(self) -> ReplayStats:
        """Get current replay statistics."""
        elapsed = timedelta()
        if self._playhead > 0 and self.turns:
            elapsed = timedelta(
                seconds=sum(t.duration for t in self.turns[: self._playhead])
            )

        return ReplayStats(
            total_turns=len(self.turns),
            current_position=self._playhead,
            elapsed_time=elapsed,
            total_duration=timedelta(seconds=self._total_duration),
            speed=self._speed,
            state=self._state,
        )

    def get_turn_at_time(self, target_time: timedelta) -> int:
        """
        Find the turn index at a given elapsed time.

        Args:
            target_time: Target elapsed time

        Returns:
            Turn index at or before that time
        """
        if not self.turns:
            return 0

        elapsed = timedelta()
        for i, turn in enumerate(self.turns):
            if elapsed + timedelta(seconds=turn.duration) > target_time:
                return i
            elapsed += timedelta(seconds=turn.duration)

        return len(self.turns) - 1

    def seek_to_time(self, target_time: timedelta) -> Turn | None:
        """
        Seek to a specific elapsed time.

        Args:
            target_time: Target elapsed time

        Returns:
            Turn at that time
        """
        idx = self.get_turn_at_time(target_time)
        return self.seek(idx)


def create_demo_turns(count: int = 20) -> list[Turn]:
    """Create demo turns for testing."""
    import random

    turn_types = ["SPEECH", "ACTION", "THOUGHT", "THOUGHT", "SILENCE"]
    now = datetime.now()
    turns = []

    for i in range(count):
        turn_type = random.choice(turn_types)
        if i == count // 2:  # Add a YIELD in the middle
            turn_type = "YIELD"

        turns.append(
            Turn(
                id=f"turn-{i:03d}",
                turn_type=turn_type,
                content=f"Demo turn {i}: {turn_type} content",
                timestamp=now + timedelta(seconds=i * 0.5),
                duration=random.uniform(0.05, 0.2),
                agent_id="demo-agent",
                confidence=random.uniform(0.7, 1.0),
            )
        )

    return turns


__all__ = [
    "ReplayController",
    "Turn",
    "TurnHighlightEvent",
    "ReplayStats",
    "PlaybackState",
    "create_demo_turns",
]
