"""
Tween: Property animation primitive.

A Tween animates a value from start to end over a duration with easing.
This is the fundamental building block for all property animations.

Features:
- Generic over value type (numbers, colors, positions)
- Configurable easing
- Interruptible (can be stopped/reversed mid-animation)
- State machine (pending, running, complete)
- Deterministic (given time, output is predictable)

Key insight: A Tween is a pure function: (start, end, duration, easing, t) -> value
The Tween class wraps this in a stateful animation lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from agents.i.reactive.animation.easing import (
    Easing,
    EasingCurve,
    EasingFn,
    ease_out,
    get_easing_fn,
)
from agents.i.reactive.signal import Signal

if TYPE_CHECKING:
    pass

T = TypeVar("T")


class TransitionStatus(Enum):
    """Animation lifecycle states."""

    PENDING = auto()  # Not started
    RUNNING = auto()  # Currently animating
    PAUSED = auto()  # Paused mid-animation
    COMPLETE = auto()  # Finished (reached end)
    CANCELLED = auto()  # Stopped before completion


@dataclass(frozen=True)
class TweenConfig:
    """Configuration for a Tween animation."""

    # Duration in milliseconds
    duration_ms: float = 300.0

    # Easing function or curve
    easing: Easing | EasingCurve = Easing.EASE_OUT

    # Delay before starting (milliseconds)
    delay_ms: float = 0.0

    # Loop count (0 = no loop, -1 = infinite)
    loops: int = 0

    # Alternate direction on loop (yoyo)
    yoyo: bool = False


@dataclass(frozen=True)
class TweenState(Generic[T]):
    """Immutable state of a Tween animation."""

    # Current animated value
    value: T

    # Start value
    start: T

    # End value
    end: T

    # Animation status
    status: TransitionStatus = TransitionStatus.PENDING

    # Progress [0, 1]
    progress: float = 0.0

    # Elapsed time in milliseconds
    elapsed_ms: float = 0.0

    # Current loop iteration
    loop: int = 0

    # Whether currently moving forward (for yoyo)
    forward: bool = True


# Type alias for interpolation functions
Interpolator = Callable[[T, T, float], T]


def lerp_number(a: float, b: float, t: float) -> float:
    """Linear interpolation for numbers."""
    return a + (b - a) * t


def lerp_int(a: int, b: int, t: float) -> int:
    """Linear interpolation for integers (rounded)."""
    return round(a + (b - a) * t)


def lerp_tuple(a: tuple[float, ...], b: tuple[float, ...], t: float) -> tuple[float, ...]:
    """Linear interpolation for tuples of numbers."""
    return tuple(lerp_number(av, bv, t) for av, bv in zip(a, b))


def lerp_color_rgb(
    a: tuple[int, int, int], b: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    """Linear interpolation for RGB colors."""
    return (
        round(lerp_number(a[0], b[0], t)),
        round(lerp_number(a[1], b[1], t)),
        round(lerp_number(a[2], b[2], t)),
    )


@dataclass
class Tween(Generic[T]):
    """
    Property animation primitive.

    Animates a value from start to end over duration with easing.

    Example:
        # Create a tween from 0 to 100 over 500ms
        tween = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=500, easing=Easing.EASE_OUT),
        )

        # Update on each frame
        tween.update(delta_ms=16.67)
        print(tween.state.value.value)  # Current interpolated value

        # Check completion
        if tween.is_complete:
            print("Animation finished!")

    Lifecycle:
        PENDING ─► RUNNING ─► COMPLETE
                     │
                     ▼
                   PAUSED
                     │
                     ▼
                  CANCELLED
    """

    config: TweenConfig
    state: Signal[TweenState[T]]
    _interpolator: Interpolator[T]
    _easing_fn: EasingFn = field(default=ease_out)
    _on_complete: Callable[[Tween[T]], None] | None = field(default=None)

    @classmethod
    def create(
        cls,
        start: T,
        end: T,
        config: TweenConfig | None = None,
        interpolator: Interpolator[T] | None = None,
        on_complete: Callable[[Tween[T]], None] | None = None,
    ) -> Tween[T]:
        """
        Create a new Tween animation.

        Args:
            start: Starting value
            end: Ending value
            config: Animation configuration
            interpolator: Custom interpolation function
            on_complete: Callback when animation completes

        Returns:
            Configured Tween instance
        """
        cfg = config or TweenConfig()

        # Determine interpolator
        if interpolator is not None:
            interp = interpolator
        elif isinstance(start, float):
            interp = lerp_number  # type: ignore[assignment]
        elif isinstance(start, int):
            interp = lerp_int  # type: ignore[assignment]
        elif isinstance(start, tuple):
            interp = lerp_tuple  # type: ignore[assignment]
        else:
            # Default: just snap at end
            def snap_interp(a: T, b: T, t: float) -> T:
                return b if t >= 1.0 else a

            interp = snap_interp

        # Determine easing function
        if isinstance(cfg.easing, EasingCurve):
            easing_fn: Callable[[float], float] = cfg.easing.apply
        else:
            easing_fn = get_easing_fn(cfg.easing)

        initial_state = TweenState(
            value=start,
            start=start,
            end=end,
            status=TransitionStatus.PENDING,
            progress=0.0,
            elapsed_ms=0.0,
            loop=0,
            forward=True,
        )

        return cls(
            config=cfg,
            state=Signal.of(initial_state),
            _interpolator=interp,
            _easing_fn=easing_fn,
            _on_complete=on_complete,
        )

    def start(self) -> TweenState[T]:
        """Start the animation."""
        current = self.state.value
        if current.status == TransitionStatus.PENDING:
            new_state = TweenState(
                value=current.start,
                start=current.start,
                end=current.end,
                status=TransitionStatus.RUNNING,
                progress=0.0,
                elapsed_ms=0.0,
                loop=0,
                forward=True,
            )
            self.state.set(new_state)
            return new_state
        return current

    def update(self, delta_ms: float) -> TweenState[T]:
        """
        Update the animation by delta time.

        Args:
            delta_ms: Time elapsed since last update

        Returns:
            New animation state
        """
        current = self.state.value

        # Only update if running
        if current.status != TransitionStatus.RUNNING:
            return current

        # Calculate new elapsed time
        new_elapsed = current.elapsed_ms + delta_ms

        # Handle delay
        if new_elapsed < self.config.delay_ms:
            new_state = TweenState(
                value=current.start,
                start=current.start,
                end=current.end,
                status=TransitionStatus.RUNNING,
                progress=0.0,
                elapsed_ms=new_elapsed,
                loop=current.loop,
                forward=current.forward,
            )
            self.state.set(new_state)
            return new_state

        # Calculate progress (accounting for delay)
        active_elapsed = new_elapsed - self.config.delay_ms
        raw_progress = (
            active_elapsed / self.config.duration_ms if self.config.duration_ms > 0 else 1.0
        )

        # Handle looping
        loop = current.loop
        forward = current.forward
        progress = raw_progress

        if progress >= 1.0:
            if self.config.loops == 0:
                # No looping - complete
                progress = 1.0
            elif self.config.loops == -1 or loop < self.config.loops:
                # Loop
                loop += 1
                progress = progress % 1.0
                if self.config.yoyo:
                    forward = not forward
                # Reset elapsed for new loop
                active_elapsed = progress * self.config.duration_ms
                new_elapsed = active_elapsed + self.config.delay_ms

        # Apply easing
        eased_progress = self._easing_fn(progress)

        # Handle yoyo direction
        if not forward:
            eased_progress = 1.0 - eased_progress

        # Interpolate value
        start = current.start
        end = current.end
        value = self._interpolator(start, end, eased_progress)

        # Determine status
        status = TransitionStatus.RUNNING
        if progress >= 1.0 and (
            self.config.loops == 0 or (self.config.loops > 0 and loop >= self.config.loops)
        ):
            status = TransitionStatus.COMPLETE
            value = end if forward else start

        new_state = TweenState(
            value=value,
            start=start,
            end=end,
            status=status,
            progress=min(progress, 1.0),
            elapsed_ms=new_elapsed,
            loop=loop,
            forward=forward,
        )
        self.state.set(new_state)

        # Fire completion callback
        if status == TransitionStatus.COMPLETE and self._on_complete:
            self._on_complete(self)

        return new_state

    def pause(self) -> TweenState[T]:
        """Pause the animation."""
        current = self.state.value
        if current.status == TransitionStatus.RUNNING:
            new_state = TweenState(
                value=current.value,
                start=current.start,
                end=current.end,
                status=TransitionStatus.PAUSED,
                progress=current.progress,
                elapsed_ms=current.elapsed_ms,
                loop=current.loop,
                forward=current.forward,
            )
            self.state.set(new_state)
            return new_state
        return current

    def resume(self) -> TweenState[T]:
        """Resume a paused animation."""
        current = self.state.value
        if current.status == TransitionStatus.PAUSED:
            new_state = TweenState(
                value=current.value,
                start=current.start,
                end=current.end,
                status=TransitionStatus.RUNNING,
                progress=current.progress,
                elapsed_ms=current.elapsed_ms,
                loop=current.loop,
                forward=current.forward,
            )
            self.state.set(new_state)
            return new_state
        return current

    def cancel(self) -> TweenState[T]:
        """Cancel the animation."""
        current = self.state.value
        new_state = TweenState(
            value=current.value,
            start=current.start,
            end=current.end,
            status=TransitionStatus.CANCELLED,
            progress=current.progress,
            elapsed_ms=current.elapsed_ms,
            loop=current.loop,
            forward=current.forward,
        )
        self.state.set(new_state)
        return new_state

    def reverse(self) -> TweenState[T]:
        """Reverse the animation direction."""
        current = self.state.value
        new_state = TweenState(
            value=current.value,
            start=current.end,
            end=current.start,
            status=current.status,
            progress=1.0 - current.progress if current.status == TransitionStatus.RUNNING else 0.0,
            elapsed_ms=0.0 if current.status != TransitionStatus.RUNNING else current.elapsed_ms,
            loop=current.loop,
            forward=not current.forward,
        )
        self.state.set(new_state)
        return new_state

    def reset(self) -> TweenState[T]:
        """Reset animation to initial state."""
        current = self.state.value
        new_state = TweenState(
            value=current.start,
            start=current.start,
            end=current.end,
            status=TransitionStatus.PENDING,
            progress=0.0,
            elapsed_ms=0.0,
            loop=0,
            forward=True,
        )
        self.state.set(new_state)
        return new_state

    def seek(self, progress: float) -> TweenState[T]:
        """
        Seek to a specific progress point.

        Args:
            progress: Target progress [0, 1]

        Returns:
            New state at that progress
        """
        current = self.state.value
        progress = max(0.0, min(1.0, progress))
        eased = self._easing_fn(progress)
        value = self._interpolator(current.start, current.end, eased)

        new_state = TweenState(
            value=value,
            start=current.start,
            end=current.end,
            status=current.status,
            progress=progress,
            elapsed_ms=self.config.delay_ms + progress * self.config.duration_ms,
            loop=current.loop,
            forward=current.forward,
        )
        self.state.set(new_state)
        return new_state

    @property
    def is_complete(self) -> bool:
        """Check if animation has completed."""
        return self.state.value.status == TransitionStatus.COMPLETE

    @property
    def is_running(self) -> bool:
        """Check if animation is currently running."""
        return self.state.value.status == TransitionStatus.RUNNING

    @property
    def value(self) -> T:
        """Get current animated value."""
        return self.state.value.value

    @property
    def progress(self) -> float:
        """Get current progress [0, 1]."""
        return self.state.value.progress


def tween(
    start: T,
    end: T,
    duration_ms: float = 300.0,
    easing: Easing = Easing.EASE_OUT,
    delay_ms: float = 0.0,
) -> Tween[T]:
    """
    Convenience function to create a tween.

    Args:
        start: Starting value
        end: Ending value
        duration_ms: Animation duration
        easing: Easing type
        delay_ms: Delay before starting

    Returns:
        Configured Tween
    """
    return Tween.create(
        start=start,
        end=end,
        config=TweenConfig(
            duration_ms=duration_ms,
            easing=easing,
            delay_ms=delay_ms,
        ),
    )
