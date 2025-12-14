"""
Replay Integration: Bridge between HotData scenarios and ReplayController.

Converts TurnEvent (rich scenario data) → Turn (replay-compatible) and
provides a ScenarioReplayProvider that drives dashboard updates from
animated playback.

The Turn IS the fundamental unit (holographic principle): a single trace
derives all panels because each TurnEvent carries:
- Path → Traces panel
- EntropyΔ → Metabolism panel
- Garden state → K-gent panel
- Timestamp → Weather trends

Usage:
    from agents.i.data.replay_integration import (
        ScenarioReplayProvider,
        create_replay_from_scenario,
    )

    # Create replay controller from scenario
    controller = create_replay_from_scenario()

    # Or use provider for dashboard integration
    provider = ScenarioReplayProvider()
    await provider.start_replay(speed=2.0)
    async for metrics in provider.metrics_stream():
        dashboard.update(metrics)

Philosophy: "The demo IS the system showing itself."
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, AsyncIterator, Callable

from ..navigation.replay import (
    PlaybackState,
    ReplayController,
    Turn,
    TurnHighlightEvent,
)
from .hot_data import (
    DayScenario,
    TurnEvent,
    create_day_scenario,
    get_scenario_metrics_at_hour,
)

if TYPE_CHECKING:
    from .dashboard_collectors import DashboardMetrics


def turn_event_to_turn(event: TurnEvent, index: int) -> Turn:
    """
    Convert a TurnEvent (scenario data) to a Turn (replay-compatible).

    Args:
        event: The TurnEvent from hot_data scenario
        index: Position in the sequence (for ID generation)

    Returns:
        Turn compatible with ReplayController
    """
    # Determine if this is a "ghost" turn (rejected/pruned)
    is_ghost = event.result in ("REJECT", "PRUNED", "CANCELLED")

    # Map turn types
    turn_type = event.turn_type.upper()
    if turn_type not in ("SPEECH", "ACTION", "THOUGHT", "YIELD", "SILENCE"):
        turn_type = "THOUGHT"  # Default to THOUGHT for unknown types

    # Calculate duration from entropy cost (higher cost = longer action)
    # Base duration 0.1s, +0.5s per 0.05 entropy
    duration = 0.1 + (abs(event.entropy_cost) * 10.0)
    duration = min(2.0, max(0.05, duration))  # Clamp to 0.05-2.0s

    return Turn(
        id=f"turn-{index:04d}",
        turn_type=turn_type,
        content=event.content,
        timestamp=event.timestamp,
        duration=duration,
        agent_id=event.source,
        confidence=1.0 if not is_ghost else 0.3,
        is_ghost=is_ghost,
        parent_id=f"turn-{index - 1:04d}" if index > 0 else None,
        children_ids=[],  # Will be set in post-processing
    )


def scenario_to_turns(scenario: DayScenario) -> list[Turn]:
    """
    Convert a complete DayScenario to a list of Turns.

    Preserves the causal order and links parent→child relationships.

    Args:
        scenario: The DayScenario with TurnEvents

    Returns:
        List of Turns ready for ReplayController
    """
    turns = [turn_event_to_turn(event, i) for i, event in enumerate(scenario.turns)]

    # Link children (reverse of parent relationship)
    for i, turn in enumerate(turns):
        if i < len(turns) - 1:
            turn.children_ids.append(turns[i + 1].id)

    return turns


def create_replay_from_scenario(
    scenario: DayScenario | None = None,
    auto_pause_on_key_moments: bool = True,
) -> ReplayController:
    """
    Create a ReplayController from a scenario.

    Args:
        scenario: The scenario to replay. Defaults to create_day_scenario()
        auto_pause_on_key_moments: Pause on YIELD/ERROR events

    Returns:
        Configured ReplayController ready for playback
    """
    if scenario is None:
        scenario = create_day_scenario()

    turns = scenario_to_turns(scenario)

    return ReplayController(
        turns=turns,
        auto_pause_on_key_moments=auto_pause_on_key_moments,
    )


@dataclass
class ReplayState:
    """Current state of scenario replay."""

    position: int  # Current turn index
    total: int  # Total turns
    speed: float  # Playback speed
    state: PlaybackState  # PLAYING, PAUSED, STOPPED
    current_hour: int  # Simulated hour of day
    is_fever: bool  # Currently in fever state

    @property
    def progress(self) -> float:
        """Progress as 0.0-1.0."""
        return self.position / max(1, self.total)

    @property
    def progress_pct(self) -> int:
        """Progress as percentage."""
        return int(self.progress * 100)


class ScenarioReplayProvider:
    """
    Provides dashboard metrics driven by scenario replay.

    This bridges the gap between the ReplayController (turn-by-turn playback)
    and the MetricsObservable (dashboard update stream).

    Features:
    - Converts replay events to dashboard metrics
    - Interpolates between hours for smooth transitions
    - Emits FeverTriggeredEvent at appropriate times
    - Supports play/pause/speed controls

    Usage:
        provider = ScenarioReplayProvider()
        provider.on_metrics_update = lambda m: dashboard.update(m)
        await provider.start_replay(speed=2.0)
    """

    def __init__(
        self,
        scenario: DayScenario | None = None,
        on_metrics_update: Callable[[DashboardMetrics], None] | None = None,
        on_state_change: Callable[[ReplayState], None] | None = None,
    ) -> None:
        """
        Initialize the replay provider.

        Args:
            scenario: Scenario to replay. Defaults to create_day_scenario()
            on_metrics_update: Callback for metrics updates
            on_state_change: Callback for replay state changes
        """
        self._scenario = scenario or create_day_scenario()
        self._controller = create_replay_from_scenario(
            self._scenario,
            auto_pause_on_key_moments=False,  # We handle this ourselves
        )

        self.on_metrics_update = on_metrics_update
        self.on_state_change = on_state_change

        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._current_hour: int = 0
        self._metrics_cache: dict[int, DashboardMetrics] = {}

    @property
    def state(self) -> ReplayState:
        """Get current replay state."""
        return ReplayState(
            position=self._controller.playhead,
            total=len(self._controller.turns),
            speed=self._controller.speed,
            state=self._controller._state,
            current_hour=self._current_hour,
            is_fever=self._current_hour == 15,  # Fever at 15:00 in scenario
        )

    async def start_replay(self, speed: float = 1.0) -> None:
        """
        Start replaying the scenario.

        Args:
            speed: Playback speed multiplier (0.25 to 4.0)
        """
        if self._running:
            return

        self._running = True
        self._controller.set_speed(speed)

        async def replay_loop() -> None:
            async for event in self._controller.play():
                if not self._running:
                    break

                # Get hour from turn timestamp
                self._current_hour = event.turn.timestamp.hour

                # Get or create metrics for this hour
                metrics = self._get_metrics_for_hour(self._current_hour)

                # Notify callbacks
                if self.on_metrics_update:
                    self.on_metrics_update(metrics)

                if self.on_state_change:
                    self.on_state_change(self.state)

        self._task = asyncio.create_task(replay_loop())

    async def stop(self) -> None:
        """Stop the replay."""
        self._running = False
        self._controller.stop()

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    def pause(self) -> None:
        """Pause playback."""
        self._controller.pause()
        if self.on_state_change:
            self.on_state_change(self.state)

    def resume(self) -> None:
        """Resume playback."""
        self._controller.resume()
        if self.on_state_change:
            self.on_state_change(self.state)

    def toggle_pause(self) -> None:
        """Toggle pause state."""
        self._controller.toggle_pause()
        if self.on_state_change:
            self.on_state_change(self.state)

    def set_speed(self, speed: float) -> None:
        """Set playback speed."""
        self._controller.set_speed(speed)
        if self.on_state_change:
            self.on_state_change(self.state)

    def cycle_speed(self) -> float:
        """Cycle through speed presets. Returns new speed."""
        new_speed = self._controller.cycle_speed()
        if self.on_state_change:
            self.on_state_change(self.state)
        return new_speed

    def seek_to_hour(self, hour: int) -> None:
        """
        Seek to a specific hour in the scenario.

        Args:
            hour: Hour of day (0-23)
        """
        # Find the first turn at or after this hour
        for i, turn in enumerate(self._controller.turns):
            if turn.timestamp.hour >= hour:
                self._controller.seek(i)
                self._current_hour = hour
                break

        # Update metrics
        if self.on_metrics_update:
            metrics = self._get_metrics_for_hour(hour)
            self.on_metrics_update(metrics)

        if self.on_state_change:
            self.on_state_change(self.state)

    def _get_metrics_for_hour(self, hour: int) -> DashboardMetrics:
        """Get cached or create metrics for a given hour."""
        if hour not in self._metrics_cache:
            from .dashboard_collectors import create_scenario_metrics

            self._metrics_cache[hour] = create_scenario_metrics(hour)
        return self._metrics_cache[hour]

    async def metrics_stream(self) -> AsyncIterator[DashboardMetrics]:
        """
        Async iterator that yields metrics as they update during replay.

        Usage:
            async for metrics in provider.metrics_stream():
                dashboard.update(metrics)
        """
        queue: asyncio.Queue[DashboardMetrics] = asyncio.Queue()

        # Store original callback
        original_callback = self.on_metrics_update

        # Replace with queue-based callback
        def queue_callback(metrics: DashboardMetrics) -> None:
            queue.put_nowait(metrics)
            if original_callback:
                original_callback(metrics)

        self.on_metrics_update = queue_callback

        try:
            while self._running:
                try:
                    metrics = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield metrics
                except asyncio.TimeoutError:
                    continue
        finally:
            # Restore original callback
            self.on_metrics_update = original_callback


# =============================================================================
# Replay Controls Widget Data
# =============================================================================


@dataclass
class ReplayControls:
    """Data for replay control widget."""

    is_playing: bool
    is_paused: bool
    speed: float
    progress: float
    current_turn: str
    total_turns: int
    current_hour: int

    @property
    def speed_label(self) -> str:
        """Human-readable speed label."""
        return f"{self.speed}x"

    @property
    def progress_bar(self, width: int = 20) -> str:
        """ASCII progress bar."""
        filled = int(self.progress * width)
        return "█" * filled + "░" * (width - filled)

    @property
    def time_label(self) -> str:
        """Current simulated time."""
        return f"{self.current_hour:02d}:00"


def get_replay_controls(provider: ScenarioReplayProvider) -> ReplayControls:
    """Get current replay control state for UI."""
    state = provider.state
    current_turn = provider._controller.get_current_turn()

    return ReplayControls(
        is_playing=state.state == PlaybackState.PLAYING,
        is_paused=state.state == PlaybackState.PAUSED,
        speed=state.speed,
        progress=state.progress,
        current_turn=current_turn.content[:50] if current_turn else "",
        total_turns=state.total,
        current_hour=state.current_hour,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Conversion functions
    "turn_event_to_turn",
    "scenario_to_turns",
    "create_replay_from_scenario",
    # Provider
    "ScenarioReplayProvider",
    "ReplayState",
    # Controls
    "ReplayControls",
    "get_replay_controls",
]
