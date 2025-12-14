"""
Animation Combinators: Sequence and Parallel composition.

Combinators allow composing simple animations into complex ones:
- Sequence: Run animations one after another
- Parallel: Run animations simultaneously

This follows the operad pattern from the reactive substrate:
animations compose like morphisms in a category.

Key insight: Animation combinators are the Kleisli category for
the animation monad. Sequence is >>=, Parallel is applicative <*>.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from agents.i.reactive.animation.tween import TransitionStatus, Tween, TweenState
from agents.i.reactive.signal import Signal

if TYPE_CHECKING:
    pass

T = TypeVar("T")


@dataclass(frozen=True)
class CombinatorState:
    """State of an animation combinator."""

    # Overall status
    status: TransitionStatus = TransitionStatus.PENDING

    # Overall progress [0, 1]
    progress: float = 0.0

    # Elapsed time in milliseconds
    elapsed_ms: float = 0.0

    # Current animation index (for Sequence)
    current_index: int = 0


class AnimationCombinator(ABC):
    """
    Base class for animation combinators.

    Combinators compose multiple animations into a single animation
    with unified lifecycle management.
    """

    @abstractmethod
    def start(self) -> CombinatorState:
        """Start the combined animation."""
        ...

    @abstractmethod
    def update(self, delta_ms: float) -> CombinatorState:
        """Update all animations by delta time."""
        ...

    @abstractmethod
    def pause(self) -> CombinatorState:
        """Pause all animations."""
        ...

    @abstractmethod
    def resume(self) -> CombinatorState:
        """Resume all animations."""
        ...

    @abstractmethod
    def reset(self) -> CombinatorState:
        """Reset all animations to initial state."""
        ...

    @property
    @abstractmethod
    def is_complete(self) -> bool:
        """Check if all animations have completed."""
        ...


@dataclass
class Sequence(AnimationCombinator):
    """
    Run animations in sequence, one after another.

    Each animation starts when the previous one completes.
    Total duration is sum of all animation durations.

    Example:
        seq = Sequence.of([
            tween(0.0, 100.0, duration_ms=300),
            tween(100.0, 50.0, duration_ms=200),
            tween(50.0, 75.0, duration_ms=100),
        ])
        seq.start()

        # On each frame:
        seq.update(delta_ms=16.67)

        # Current animation's value:
        value = seq.current_value()
    """

    _animations: list[Tween[Any]]
    state: Signal[CombinatorState]
    _on_complete: Callable[[Sequence], None] | None = field(default=None)

    @classmethod
    def of(
        cls,
        animations: list[Tween[Any]],
        on_complete: Callable[[Sequence], None] | None = None,
    ) -> Sequence:
        """
        Create a Sequence from a list of animations.

        Args:
            animations: List of Tween animations to run in order
            on_complete: Callback when sequence completes

        Returns:
            Configured Sequence
        """
        return cls(
            _animations=animations,
            state=Signal.of(CombinatorState()),
            _on_complete=on_complete,
        )

    def start(self) -> CombinatorState:
        """Start the sequence (starts first animation)."""
        current = self.state.value
        if current.status == TransitionStatus.PENDING:
            if not self._animations:
                # Empty sequence completes immediately
                new_state = CombinatorState(
                    status=TransitionStatus.COMPLETE,
                    progress=1.0,
                    elapsed_ms=0.0,
                    current_index=0,
                )
                self.state.set(new_state)
                return new_state
            self._animations[0].start()
            new_state = CombinatorState(
                status=TransitionStatus.RUNNING,
                progress=0.0,
                elapsed_ms=0.0,
                current_index=0,
            )
            self.state.set(new_state)
            return new_state
        return current

    def update(self, delta_ms: float) -> CombinatorState:
        """Update the sequence by delta time."""
        current = self.state.value

        if current.status != TransitionStatus.RUNNING:
            return current

        if not self._animations:
            new_state = CombinatorState(
                status=TransitionStatus.COMPLETE,
                progress=1.0,
                elapsed_ms=current.elapsed_ms + delta_ms,
                current_index=0,
            )
            self.state.set(new_state)
            return new_state

        # Update current animation
        idx = current.current_index
        anim = self._animations[idx]
        anim.update(delta_ms)

        # Check if current animation completed
        if anim.is_complete:
            # Move to next animation
            next_idx = idx + 1
            if next_idx < len(self._animations):
                # Start next animation
                self._animations[next_idx].start()
                new_state = CombinatorState(
                    status=TransitionStatus.RUNNING,
                    progress=(next_idx / len(self._animations)),
                    elapsed_ms=current.elapsed_ms + delta_ms,
                    current_index=next_idx,
                )
                self.state.set(new_state)
                return new_state
            else:
                # Sequence complete
                new_state = CombinatorState(
                    status=TransitionStatus.COMPLETE,
                    progress=1.0,
                    elapsed_ms=current.elapsed_ms + delta_ms,
                    current_index=idx,
                )
                self.state.set(new_state)
                if self._on_complete:
                    self._on_complete(self)
                return new_state

        # Calculate overall progress
        anim_progress = anim.progress
        overall = (idx + anim_progress) / len(self._animations)

        new_state = CombinatorState(
            status=TransitionStatus.RUNNING,
            progress=overall,
            elapsed_ms=current.elapsed_ms + delta_ms,
            current_index=idx,
        )
        self.state.set(new_state)
        return new_state

    def pause(self) -> CombinatorState:
        """Pause the sequence."""
        current = self.state.value
        if current.status == TransitionStatus.RUNNING and self._animations:
            self._animations[current.current_index].pause()
            new_state = CombinatorState(
                status=TransitionStatus.PAUSED,
                progress=current.progress,
                elapsed_ms=current.elapsed_ms,
                current_index=current.current_index,
            )
            self.state.set(new_state)
            return new_state
        return current

    def resume(self) -> CombinatorState:
        """Resume the sequence."""
        current = self.state.value
        if current.status == TransitionStatus.PAUSED and self._animations:
            self._animations[current.current_index].resume()
            new_state = CombinatorState(
                status=TransitionStatus.RUNNING,
                progress=current.progress,
                elapsed_ms=current.elapsed_ms,
                current_index=current.current_index,
            )
            self.state.set(new_state)
            return new_state
        return current

    def reset(self) -> CombinatorState:
        """Reset all animations in the sequence."""
        for anim in self._animations:
            anim.reset()
        new_state = CombinatorState()
        self.state.set(new_state)
        return new_state

    @property
    def is_complete(self) -> bool:
        """Check if sequence has completed."""
        return self.state.value.status == TransitionStatus.COMPLETE

    @property
    def current_animation(self) -> Tween[Any] | None:
        """Get the currently active animation."""
        current = self.state.value
        if self._animations and current.current_index < len(self._animations):
            return self._animations[current.current_index]
        return None

    def current_value(self) -> Any | None:
        """Get the current animation's value."""
        anim = self.current_animation
        return anim.value if anim else None

    def __len__(self) -> int:
        return len(self._animations)


@dataclass
class Parallel(AnimationCombinator):
    """
    Run animations in parallel, all at once.

    All animations start and run simultaneously.
    Completes when ALL animations have completed.

    Example:
        par = Parallel.of([
            tween(0.0, 100.0, duration_ms=300),  # x position
            tween(0.0, 50.0, duration_ms=200),   # y position
            tween(1.0, 0.5, duration_ms=400),    # opacity
        ])
        par.start()

        # On each frame:
        par.update(delta_ms=16.67)

        # Get all current values:
        x, y, opacity = par.values()
    """

    _animations: list[Tween[Any]]
    state: Signal[CombinatorState]
    _on_complete: Callable[[Parallel], None] | None = field(default=None)

    @classmethod
    def of(
        cls,
        animations: list[Tween[Any]],
        on_complete: Callable[[Parallel], None] | None = None,
    ) -> Parallel:
        """
        Create a Parallel from a list of animations.

        Args:
            animations: List of Tween animations to run simultaneously
            on_complete: Callback when all complete

        Returns:
            Configured Parallel
        """
        return cls(
            _animations=animations,
            state=Signal.of(CombinatorState()),
            _on_complete=on_complete,
        )

    def start(self) -> CombinatorState:
        """Start all animations simultaneously."""
        current = self.state.value
        if current.status == TransitionStatus.PENDING:
            for anim in self._animations:
                anim.start()
            new_state = CombinatorState(
                status=TransitionStatus.RUNNING,
                progress=0.0,
                elapsed_ms=0.0,
                current_index=0,
            )
            self.state.set(new_state)
            return new_state
        return current

    def update(self, delta_ms: float) -> CombinatorState:
        """Update all animations by delta time."""
        current = self.state.value

        if current.status != TransitionStatus.RUNNING:
            return current

        if not self._animations:
            new_state = CombinatorState(
                status=TransitionStatus.COMPLETE,
                progress=1.0,
                elapsed_ms=current.elapsed_ms + delta_ms,
                current_index=0,
            )
            self.state.set(new_state)
            return new_state

        # Update all animations
        for anim in self._animations:
            if not anim.is_complete:
                anim.update(delta_ms)

        # Calculate overall progress (average)
        total_progress = sum(a.progress for a in self._animations)
        overall = total_progress / len(self._animations)

        # Check if all complete
        all_complete = all(a.is_complete for a in self._animations)

        if all_complete:
            new_state = CombinatorState(
                status=TransitionStatus.COMPLETE,
                progress=1.0,
                elapsed_ms=current.elapsed_ms + delta_ms,
                current_index=0,
            )
            self.state.set(new_state)
            if self._on_complete:
                self._on_complete(self)
            return new_state

        new_state = CombinatorState(
            status=TransitionStatus.RUNNING,
            progress=overall,
            elapsed_ms=current.elapsed_ms + delta_ms,
            current_index=0,
        )
        self.state.set(new_state)
        return new_state

    def pause(self) -> CombinatorState:
        """Pause all animations."""
        current = self.state.value
        if current.status == TransitionStatus.RUNNING:
            for anim in self._animations:
                anim.pause()
            new_state = CombinatorState(
                status=TransitionStatus.PAUSED,
                progress=current.progress,
                elapsed_ms=current.elapsed_ms,
                current_index=0,
            )
            self.state.set(new_state)
            return new_state
        return current

    def resume(self) -> CombinatorState:
        """Resume all animations."""
        current = self.state.value
        if current.status == TransitionStatus.PAUSED:
            for anim in self._animations:
                anim.resume()
            new_state = CombinatorState(
                status=TransitionStatus.RUNNING,
                progress=current.progress,
                elapsed_ms=current.elapsed_ms,
                current_index=0,
            )
            self.state.set(new_state)
            return new_state
        return current

    def reset(self) -> CombinatorState:
        """Reset all animations."""
        for anim in self._animations:
            anim.reset()
        new_state = CombinatorState()
        self.state.set(new_state)
        return new_state

    @property
    def is_complete(self) -> bool:
        """Check if all animations have completed."""
        return self.state.value.status == TransitionStatus.COMPLETE

    def values(self) -> list[Any]:
        """Get current values from all animations."""
        return [a.value for a in self._animations]

    def value_at(self, index: int) -> Any | None:
        """Get value from specific animation."""
        if 0 <= index < len(self._animations):
            return self._animations[index].value
        return None

    def __len__(self) -> int:
        return len(self._animations)


def sequence(*animations: Tween[Any]) -> Sequence:
    """
    Convenience function to create a Sequence.

    Args:
        *animations: Animations to run in sequence

    Returns:
        Configured Sequence
    """
    return Sequence.of(list(animations))


def parallel(*animations: Tween[Any]) -> Parallel:
    """
    Convenience function to create a Parallel.

    Args:
        *animations: Animations to run in parallel

    Returns:
        Configured Parallel
    """
    return Parallel.of(list(animations))
