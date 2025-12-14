"""
Frame Scheduler: Animation frame coordination.

The FrameScheduler provides RequestAnimationFrame-like callback registration
with configurable FPS and frame skipping under load.

Key features:
- Configurable FPS (30, 60, 120)
- Delta time calculations for smooth interpolation
- Frame skipping when processing takes too long
- Integration with Clock for unified time source

Architecture:
    Clock.tick() ─► FrameScheduler.process_frame() ─┬─► Callback 1
                                                     ├─► Callback 2
                                                     └─► Callback N
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from agents.i.reactive.signal import Signal

if TYPE_CHECKING:
    from agents.i.reactive.wiring.clock import Clock, ClockState


# Type alias for frame callbacks
# (delta_ms: float, frame: int, t: float) -> None
FrameCallback = Callable[[float, int, float], None]


@dataclass(frozen=True)
class FrameSchedulerConfig:
    """Configuration for the FrameScheduler."""

    # Target frames per second
    fps: int = 60

    # Maximum delta time (prevents physics explosions)
    max_delta_ms: float = 100.0

    # Enable frame skipping under load
    skip_frames: bool = True

    # Maximum frames to skip before forcing render
    max_skip: int = 3

    @property
    def frame_duration_ms(self) -> float:
        """Target duration per frame in milliseconds."""
        return 1000.0 / self.fps


@dataclass
class FrameSchedulerState:
    """Current state of the frame scheduler."""

    # Current frame number
    frame: int = 0

    # Time since start in milliseconds
    elapsed_ms: float = 0.0

    # Delta since last processed frame
    delta_ms: float = 0.0

    # Number of frames skipped this tick
    skipped: int = 0

    # Whether scheduler is running
    running: bool = True

    # Accumulated time (for fixed timestep)
    accumulated_ms: float = 0.0


@dataclass
class FrameScheduler:
    """
    Animation frame coordinator.

    Provides RequestAnimationFrame-like API for registering callbacks
    that run on each animation frame.

    Example:
        scheduler = FrameScheduler.create()

        def on_frame(delta_ms: float, frame: int, t: float) -> None:
            print(f"Frame {frame}: {delta_ms:.1f}ms")

        callback_id = scheduler.request_frame(on_frame)

        # On each clock tick:
        scheduler.process_frame(clock_state)

        # Cancel callback:
        scheduler.cancel_frame(callback_id)
    """

    config: FrameSchedulerConfig
    state: Signal[FrameSchedulerState]
    _callbacks: dict[int, FrameCallback] = field(default_factory=dict)
    _next_id: int = field(default=1)
    _clock: Clock | None = field(default=None)
    _unsubscribe: Callable[[], None] | None = field(default=None)

    @classmethod
    def create(
        cls,
        config: FrameSchedulerConfig | None = None,
        clock: Clock | None = None,
    ) -> FrameScheduler:
        """
        Create a new FrameScheduler.

        Args:
            config: Optional configuration
            clock: Optional Clock to subscribe to

        Returns:
            Configured FrameScheduler
        """
        cfg = config or FrameSchedulerConfig()
        scheduler = cls(
            config=cfg,
            state=Signal.of(FrameSchedulerState()),
            _callbacks={},
            _next_id=1,
            _clock=clock,
        )

        # Auto-subscribe to clock if provided
        if clock is not None:
            scheduler._unsubscribe = clock.subscribe(scheduler._on_clock_tick)

        return scheduler

    def request_frame(self, callback: FrameCallback) -> int:
        """
        Request callback on next animation frame.

        Args:
            callback: Function(delta_ms, frame, t) to call

        Returns:
            Callback ID for cancellation
        """
        callback_id = self._next_id
        self._next_id += 1
        self._callbacks[callback_id] = callback
        return callback_id

    def cancel_frame(self, callback_id: int) -> bool:
        """
        Cancel a frame callback.

        Args:
            callback_id: ID returned from request_frame

        Returns:
            True if callback was found and cancelled
        """
        if callback_id in self._callbacks:
            del self._callbacks[callback_id]
            return True
        return False

    def process_frame(
        self,
        clock_state: ClockState | None = None,
        delta_ms: float | None = None,
    ) -> FrameSchedulerState:
        """
        Process one animation frame.

        Either provide a ClockState or raw delta_ms.

        Args:
            clock_state: Current clock state
            delta_ms: Raw delta time in milliseconds

        Returns:
            New scheduler state
        """
        current = self.state.value

        if not current.running:
            return current

        # Get delta from clock state or raw value
        raw_delta = (
            clock_state.delta
            if clock_state
            else (delta_ms or self.config.frame_duration_ms)
        )
        frame_from_clock = clock_state.frame if clock_state else current.frame + 1
        t_from_clock = clock_state.t if clock_state else current.elapsed_ms + raw_delta

        # Clamp delta to prevent physics explosions
        clamped_delta = min(raw_delta, self.config.max_delta_ms)

        # Calculate frames to process
        accumulated = current.accumulated_ms + clamped_delta
        frames_to_process = int(accumulated / self.config.frame_duration_ms)

        # Frame skipping logic
        skipped = 0
        if self.config.skip_frames and frames_to_process > 1:
            skipped = min(frames_to_process - 1, self.config.max_skip)
            frames_to_process = max(1, frames_to_process - skipped)

        # Process callbacks
        callback_delta = clamped_delta
        for _i in range(frames_to_process):
            for callback in list(self._callbacks.values()):
                callback(callback_delta, frame_from_clock, t_from_clock)

        # Update state
        new_state = FrameSchedulerState(
            frame=frame_from_clock,
            elapsed_ms=t_from_clock,
            delta_ms=clamped_delta,
            skipped=skipped,
            running=current.running,
            accumulated_ms=accumulated % self.config.frame_duration_ms,
        )
        self.state.set(new_state)
        return new_state

    def _on_clock_tick(self, clock_state: ClockState) -> None:
        """Internal: Handle clock tick when subscribed."""
        if clock_state.running:
            self.process_frame(clock_state)

    def pause(self) -> None:
        """Pause the scheduler."""
        current = self.state.value
        self.state.set(
            FrameSchedulerState(
                frame=current.frame,
                elapsed_ms=current.elapsed_ms,
                delta_ms=0.0,
                skipped=0,
                running=False,
                accumulated_ms=current.accumulated_ms,
            )
        )

    def resume(self) -> None:
        """Resume the scheduler."""
        current = self.state.value
        self.state.set(
            FrameSchedulerState(
                frame=current.frame,
                elapsed_ms=current.elapsed_ms,
                delta_ms=0.0,
                skipped=0,
                running=True,
                accumulated_ms=current.accumulated_ms,
            )
        )

    def reset(self) -> None:
        """Reset the scheduler to initial state."""
        self._callbacks.clear()
        self.state.set(FrameSchedulerState())

    def dispose(self) -> None:
        """Clean up resources."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None
        self._callbacks.clear()

    @property
    def callback_count(self) -> int:
        """Number of registered callbacks."""
        return len(self._callbacks)


def create_frame_scheduler(
    fps: int = 60,
    clock: Clock | None = None,
) -> FrameScheduler:
    """
    Create a FrameScheduler with common defaults.

    Args:
        fps: Target frame rate
        clock: Optional Clock to subscribe to

    Returns:
        Configured FrameScheduler
    """
    return FrameScheduler.create(
        config=FrameSchedulerConfig(fps=fps),
        clock=clock,
    )
