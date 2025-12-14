"""
Clock: Central time synchronization for reactive widgets.

The Clock is the heartbeat of the reactive system. It provides:
- Unified time source across all widgets
- Animation frame coordination
- Time-based entropy seeding
- Deterministic replay via recorded time

Key insight: Time flows from ONE source. No scattered time.now() calls.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from agents.i.reactive.signal import Signal

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class ClockState:
    """
    Immutable clock state at a point in time.

    All derived values are deterministic from t and seed.
    """

    # Current time in milliseconds (from epoch or start)
    t: float = 0.0

    # Base seed for entropy (propagates to widgets)
    seed: int = 0

    # Frame number (for animation coordination)
    frame: int = 0

    # Delta since last tick (milliseconds)
    delta: float = 0.0

    # Whether clock is running
    running: bool = True

    # Playback rate (1.0 = normal, 2.0 = double, 0.5 = half)
    rate: float = 1.0

    @property
    def seconds(self) -> float:
        """Time in seconds."""
        return self.t / 1000.0

    def entropy_seed_for(self, widget_id: str) -> int:
        """
        Deterministic seed for a widget based on clock state.

        Same (t, seed, widget_id) -> same result, always.
        """
        return self.seed + hash(widget_id) + self.frame


@dataclass
class ClockConfig:
    """Configuration for the Clock."""

    # Target frame rate (frames per second)
    fps: int = 60

    # Starting seed for entropy
    initial_seed: int = 42

    # Use wall clock time vs simulated time
    use_wall_time: bool = True

    # Auto-start on creation
    auto_start: bool = True


@dataclass
class Clock:
    """
    Central time synchronization for reactive widgets.

    The Clock provides a unified time source that propagates to all widgets.
    This ensures:
    - Consistent animation timing
    - Deterministic entropy seeding
    - Replay capability via recorded time

    Example:
        clock = create_clock()

        # Subscribe to time changes
        clock.state.subscribe(lambda s: print(f"t={s.t}, frame={s.frame}"))

        # Manual tick (for testing)
        clock.tick()

        # Run animation loop
        while True:
            clock.tick()
            time.sleep(1 / 60)

    Architecture:
        Clock.state (Signal[ClockState]) ─┬─► Widget 1 (receives t, seed)
                                          ├─► Widget 2
                                          ├─► Widget 3
                                          └─► ... all widgets
    """

    config: ClockConfig
    state: Signal[ClockState]

    # Internal state
    _start_time: float = field(default=0.0)
    _last_tick: float = field(default=0.0)
    _paused_at: float | None = field(default=None)

    @classmethod
    def create(cls, config: ClockConfig | None = None) -> Clock:
        """Create a new Clock with configuration."""
        cfg = config or ClockConfig()

        initial_state = ClockState(
            t=0.0,
            seed=cfg.initial_seed,
            frame=0,
            delta=0.0,
            running=cfg.auto_start,
            rate=1.0,
        )

        clock = cls(
            config=cfg,
            state=Signal.of(initial_state),
            _start_time=time.time() * 1000 if cfg.use_wall_time else 0.0,
            _last_tick=time.time() * 1000 if cfg.use_wall_time else 0.0,
        )

        return clock

    def tick(self, override_delta: float | None = None) -> ClockState:
        """
        Advance the clock by one frame.

        Args:
            override_delta: Optional delta in ms (for testing/replay)

        Returns:
            New clock state after tick
        """
        current = self.state.value

        if not current.running:
            return current

        now = (
            time.time() * 1000 if self.config.use_wall_time else self._last_tick + 16.67
        )
        delta = (
            override_delta if override_delta is not None else (now - self._last_tick)
        )
        self._last_tick = now

        # Apply playback rate
        delta *= current.rate

        new_state = ClockState(
            t=current.t + delta,
            seed=current.seed,
            frame=current.frame + 1,
            delta=delta,
            running=current.running,
            rate=current.rate,
        )

        self.state.set(new_state)
        return new_state

    def tick_to(self, t: float) -> ClockState:
        """
        Tick to a specific time (for replay/testing).

        Args:
            t: Target time in milliseconds

        Returns:
            New clock state at target time
        """
        current = self.state.value
        delta = t - current.t

        new_state = ClockState(
            t=t,
            seed=current.seed,
            frame=current.frame + 1,
            delta=delta,
            running=current.running,
            rate=current.rate,
        )

        self.state.set(new_state)
        return new_state

    def pause(self) -> ClockState:
        """Pause the clock."""
        current = self.state.value
        if current.running:
            self._paused_at = self._last_tick
            new_state = ClockState(
                t=current.t,
                seed=current.seed,
                frame=current.frame,
                delta=0.0,
                running=False,
                rate=current.rate,
            )
            self.state.set(new_state)
            return new_state
        return current

    def resume(self) -> ClockState:
        """Resume the clock."""
        current = self.state.value
        if not current.running:
            now = time.time() * 1000 if self.config.use_wall_time else self._last_tick
            self._last_tick = now
            self._paused_at = None
            new_state = ClockState(
                t=current.t,
                seed=current.seed,
                frame=current.frame,
                delta=0.0,
                running=True,
                rate=current.rate,
            )
            self.state.set(new_state)
            return new_state
        return current

    def reset(self) -> ClockState:
        """Reset the clock to initial state."""
        now = time.time() * 1000 if self.config.use_wall_time else 0.0
        self._start_time = now
        self._last_tick = now
        self._paused_at = None

        new_state = ClockState(
            t=0.0,
            seed=self.config.initial_seed,
            frame=0,
            delta=0.0,
            running=self.config.auto_start,
            rate=1.0,
        )
        self.state.set(new_state)
        return new_state

    def set_rate(self, rate: float) -> ClockState:
        """
        Set playback rate.

        Args:
            rate: 1.0 = normal, 2.0 = double speed, 0.5 = half speed

        Returns:
            New clock state with rate
        """
        current = self.state.value
        new_state = ClockState(
            t=current.t,
            seed=current.seed,
            frame=current.frame,
            delta=current.delta,
            running=current.running,
            rate=max(0.1, min(10.0, rate)),  # Clamp to reasonable range
        )
        self.state.set(new_state)
        return new_state

    def set_seed(self, seed: int) -> ClockState:
        """
        Set entropy seed.

        Args:
            seed: New base seed for entropy

        Returns:
            New clock state with seed
        """
        current = self.state.value
        new_state = ClockState(
            t=current.t,
            seed=seed,
            frame=current.frame,
            delta=current.delta,
            running=current.running,
            rate=current.rate,
        )
        self.state.set(new_state)
        return new_state

    def snapshot(self) -> ClockState:
        """Get immutable snapshot of current state."""
        return self.state.value

    def subscribe(self, callback: Callable[[ClockState], None]) -> Callable[[], None]:
        """
        Subscribe to clock updates.

        Args:
            callback: Function called on each tick

        Returns:
            Unsubscribe function
        """
        return self.state.subscribe(callback)


def create_clock(
    fps: int = 60,
    seed: int = 42,
    use_wall_time: bool = True,
    auto_start: bool = True,
) -> Clock:
    """
    Create a Clock with common defaults.

    Args:
        fps: Target frame rate
        seed: Initial entropy seed
        use_wall_time: Use real wall clock vs simulated time
        auto_start: Start running immediately

    Returns:
        Configured Clock instance
    """
    return Clock.create(
        ClockConfig(
            fps=fps,
            initial_seed=seed,
            use_wall_time=use_wall_time,
            auto_start=auto_start,
        )
    )


# Global clock singleton (optional use)
_global_clock: Clock | None = None


def get_global_clock() -> Clock:
    """Get or create the global clock singleton."""
    global _global_clock
    if _global_clock is None:
        _global_clock = create_clock()
    return _global_clock


def reset_global_clock() -> Clock:
    """Reset and return the global clock."""
    global _global_clock
    _global_clock = create_clock()
    return _global_clock
