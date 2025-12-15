"""
PhaseGovernor: Controlled playback timing for Agent Town simulations.

Bridges TownFlux event generation to animation frame loop with:
- Configurable phase duration (default 5 seconds per phase)
- Playback speed control (0.5x, 1x, 2x)
- Pause/resume
- Event interpolation within phases

Architecture:
    PhaseGovernor
         │
         ├─► TownFlux.step()     (event generation)
         │
         ├─► FrameScheduler      (timing coordination)
         │
         └─► EventBus            (fan-out to subscribers)

See: plans/purring-squishing-duckling.md Phase 3
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable

if TYPE_CHECKING:
    from agents.town.event_bus import EventBus
    from agents.town.flux import TownEvent, TownFlux


class PlaybackState(Enum):
    """Playback state for the governor."""

    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()


@dataclass
class PhaseTimingConfig:
    """Configuration for phase timing."""

    # Duration of each simulation phase in milliseconds
    phase_duration_ms: int = 5000  # 5 seconds per phase

    # Target events per phase (for interpolation)
    events_per_phase: int = 5

    # Playback speed multiplier (0.5 = half speed, 2.0 = double)
    playback_speed: float = 1.0

    # Minimum delay between events (prevents flood)
    min_event_delay_ms: int = 100

    # Maximum delay between events (prevents long waits)
    max_event_delay_ms: int = 2000

    @property
    def effective_phase_duration_ms(self) -> float:
        """Phase duration adjusted for playback speed."""
        return self.phase_duration_ms / self.playback_speed

    @property
    def event_interval_ms(self) -> float:
        """Target interval between events within a phase."""
        interval = self.effective_phase_duration_ms / max(1, self.events_per_phase)
        return max(self.min_event_delay_ms, min(interval, self.max_event_delay_ms))


@dataclass
class GovernorState:
    """Current state of the PhaseGovernor."""

    playback: PlaybackState = PlaybackState.STOPPED
    current_phase: int = 0
    events_this_phase: int = 0
    total_events: int = 0
    elapsed_ms: float = 0.0
    last_event_time: datetime | None = None


@dataclass
class PhaseGovernor:
    """
    Controls simulation timing with configurable playback speed.

    Wraps TownFlux to provide governed event streaming where
    events are yielded at controlled intervals.

    Example:
        flux = TownFlux(env)
        governor = PhaseGovernor(flux, config=PhaseTimingConfig(phase_duration_ms=5000))

        # Start governed playback
        async for event in governor.run(num_phases=4):
            print(event)  # Events arrive at ~1 per second for 5 events per phase

        # Control playback
        governor.pause()
        governor.set_speed(2.0)  # Double speed
        governor.resume()
    """

    flux: "TownFlux"
    config: PhaseTimingConfig = field(default_factory=PhaseTimingConfig)
    event_bus: "EventBus[TownEvent] | None" = None

    # Runtime state
    _state: GovernorState = field(default_factory=GovernorState)
    _pause_event: asyncio.Event = field(default_factory=asyncio.Event)
    _stop_requested: bool = field(default=False)

    def __post_init__(self) -> None:
        """Initialize pause event as not paused."""
        self._pause_event.set()  # Not paused initially

    # --- Playback Control ---

    async def run(self, num_phases: int = 4) -> AsyncIterator["TownEvent"]:
        """
        Run simulation with governed timing.

        Events are yielded at interpolated intervals within each phase.
        Respects pause/resume and playback speed.

        Args:
            num_phases: Number of phases to run (default 4 = one day)

        Yields:
            TownEvent at governed intervals
        """
        self._state.playback = PlaybackState.PLAYING
        self._stop_requested = False

        try:
            for phase_num in range(num_phases):
                if self._stop_requested:
                    break

                self._state.current_phase = phase_num
                self._state.events_this_phase = 0

                # Collect events from flux for this phase
                phase_events: list[TownEvent] = []
                async for event in self.flux.step():
                    phase_events.append(event)

                # Yield events with timing
                for i, event in enumerate(phase_events):
                    if self._stop_requested:
                        break

                    # Wait for unpause
                    await self._pause_event.wait()

                    # Calculate delay
                    if i > 0:
                        delay_ms = self.config.event_interval_ms
                        await asyncio.sleep(delay_ms / 1000.0)

                    # Yield event
                    self._state.events_this_phase += 1
                    self._state.total_events += 1
                    self._state.last_event_time = datetime.now()

                    yield event

                    # Publish to event bus if wired
                    if self.event_bus is not None:
                        await self.event_bus.publish(event)

                # Delay before next phase
                if phase_num < num_phases - 1 and not self._stop_requested:
                    remaining = self._remaining_phase_time_ms()
                    if remaining > 0:
                        await asyncio.sleep(remaining / 1000.0)

        finally:
            self._state.playback = PlaybackState.STOPPED

    def _remaining_phase_time_ms(self) -> float:
        """Calculate remaining time in current phase."""
        elapsed = self._state.events_this_phase * self.config.event_interval_ms
        return max(0, self.config.effective_phase_duration_ms - elapsed)

    def pause(self) -> None:
        """Pause playback."""
        if self._state.playback == PlaybackState.PLAYING:
            self._state.playback = PlaybackState.PAUSED
            self._pause_event.clear()

    def resume(self) -> None:
        """Resume playback."""
        if self._state.playback == PlaybackState.PAUSED:
            self._state.playback = PlaybackState.PLAYING
            self._pause_event.set()

    def stop(self) -> None:
        """Stop playback (cannot resume, must restart)."""
        self._stop_requested = True
        self._pause_event.set()  # Unblock if paused
        self._state.playback = PlaybackState.STOPPED

    def toggle_pause(self) -> bool:
        """Toggle pause state. Returns True if now paused."""
        if self._state.playback == PlaybackState.PLAYING:
            self.pause()
            return True
        elif self._state.playback == PlaybackState.PAUSED:
            self.resume()
            return False
        return False

    # --- Speed Control ---

    def set_speed(self, speed: float) -> None:
        """
        Set playback speed.

        Args:
            speed: Multiplier (0.5 = half, 1.0 = normal, 2.0 = double)
        """
        self.config.playback_speed = max(0.1, min(speed, 10.0))

    def speed_up(self, factor: float = 1.5) -> float:
        """Increase speed by factor. Returns new speed."""
        self.set_speed(self.config.playback_speed * factor)
        return self.config.playback_speed

    def slow_down(self, factor: float = 1.5) -> float:
        """Decrease speed by factor. Returns new speed."""
        self.set_speed(self.config.playback_speed / factor)
        return self.config.playback_speed

    # --- State Access ---

    @property
    def state(self) -> GovernorState:
        """Get current governor state."""
        return self._state

    @property
    def is_playing(self) -> bool:
        """Whether currently playing (not paused or stopped)."""
        return self._state.playback == PlaybackState.PLAYING

    @property
    def is_paused(self) -> bool:
        """Whether currently paused."""
        return self._state.playback == PlaybackState.PAUSED

    @property
    def is_stopped(self) -> bool:
        """Whether stopped."""
        return self._state.playback == PlaybackState.STOPPED

    @property
    def speed(self) -> float:
        """Current playback speed."""
        return self.config.playback_speed

    # --- Callbacks ---

    def on_phase_complete(self, callback: Callable[[int], None]) -> Callable[[], None]:
        """
        Register callback for phase completion.

        Returns unsubscribe function.
        """
        # TODO: Implement callback registry
        return lambda: None

    def on_event(self, callback: Callable[["TownEvent"], None]) -> Callable[[], None]:
        """
        Register callback for each event.

        Returns unsubscribe function.
        """
        # TODO: Implement callback registry
        return lambda: None


# =============================================================================
# Factory Functions
# =============================================================================


def create_phase_governor(
    flux: "TownFlux",
    phase_duration_ms: int = 5000,
    playback_speed: float = 1.0,
    event_bus: "EventBus[TownEvent] | None" = None,
) -> PhaseGovernor:
    """
    Create PhaseGovernor with common settings.

    Args:
        flux: TownFlux to govern
        phase_duration_ms: Duration per phase in ms
        playback_speed: Initial playback speed
        event_bus: Optional event bus for fan-out

    Returns:
        Configured PhaseGovernor
    """
    config = PhaseTimingConfig(
        phase_duration_ms=phase_duration_ms,
        playback_speed=playback_speed,
    )
    return PhaseGovernor(flux=flux, config=config, event_bus=event_bus)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "PhaseTimingConfig",
    "GovernorState",
    "PlaybackState",
    "PhaseGovernor",
    "create_phase_governor",
]
