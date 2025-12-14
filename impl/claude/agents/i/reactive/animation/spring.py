"""
Spring Dynamics: Physics-based spring animation.

Springs provide organic, physics-based motion that feels natural.
Unlike tweens with fixed duration, springs settle based on physics.

The spring equation: F = -kx - cv
- k: stiffness (spring constant)
- c: damping coefficient
- x: displacement from target
- v: velocity

Key insight: Springs feel alive because they respond to interruption
naturally. Changing the target mid-motion creates smooth redirection.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Generic, TypeVar

from agents.i.reactive.animation.tween import TransitionStatus
from agents.i.reactive.signal import Signal

if TYPE_CHECKING:
    pass

T = TypeVar("T")


@dataclass(frozen=True)
class SpringConfig:
    """
    Configuration for spring physics.

    Common presets:
    - Gentle: stiffness=120, damping=14 (slow, smooth)
    - Wobbly: stiffness=180, damping=12 (bouncy)
    - Stiff: stiffness=300, damping=20 (snappy)
    - Slow: stiffness=120, damping=30 (overdamped)
    """

    # Spring stiffness (higher = faster oscillation)
    stiffness: float = 170.0

    # Damping coefficient (higher = less bouncy)
    damping: float = 26.0

    # Mass of the simulated object
    mass: float = 1.0

    # Velocity threshold for "at rest" (in units/ms)
    rest_velocity: float = 0.001

    # Displacement threshold for "at rest"
    rest_displacement: float = 0.001

    # Whether to clamp output to [start, target] range
    clamp: bool = False

    @classmethod
    def gentle(cls) -> SpringConfig:
        """Gentle spring preset."""
        return cls(stiffness=120.0, damping=14.0)

    @classmethod
    def wobbly(cls) -> SpringConfig:
        """Wobbly spring preset."""
        return cls(stiffness=180.0, damping=12.0)

    @classmethod
    def stiff(cls) -> SpringConfig:
        """Stiff spring preset."""
        return cls(stiffness=300.0, damping=20.0)

    @classmethod
    def slow(cls) -> SpringConfig:
        """Slow, overdamped spring preset."""
        return cls(stiffness=120.0, damping=30.0)

    @classmethod
    def bouncy(cls) -> SpringConfig:
        """Very bouncy spring preset."""
        return cls(stiffness=200.0, damping=8.0)


@dataclass(frozen=True)
class SpringState:
    """Immutable state of a spring animation."""

    # Current position value
    value: float

    # Target value
    target: float

    # Current velocity
    velocity: float

    # Animation status
    status: TransitionStatus = TransitionStatus.PENDING

    # Elapsed time
    elapsed_ms: float = 0.0

    # Whether spring is at rest
    at_rest: bool = False


@dataclass
class Spring:
    """
    Physics-based spring animation.

    Springs simulate real spring physics for organic motion.
    Unlike tweens, springs have no fixed duration - they settle
    based on physics parameters.

    Example:
        spring = Spring.create(
            initial=0.0,
            target=100.0,
            config=SpringConfig.wobbly(),
        )
        spring.start()

        # On each frame:
        spring.update(delta_ms=16.67)
        print(spring.value)  # Current position

        # Change target mid-animation (smooth transition):
        spring.set_target(50.0)

    Key feature: Interruptibility
        Unlike tweens, changing the target of a running spring
        creates a smooth, natural transition because velocity
        is preserved.
    """

    config: SpringConfig
    state: Signal[SpringState]
    _on_complete: Callable[[Spring], None] | None = field(default=None)

    @classmethod
    def create(
        cls,
        initial: float,
        target: float,
        config: SpringConfig | None = None,
        on_complete: Callable[[Spring], None] | None = None,
    ) -> Spring:
        """
        Create a new Spring animation.

        Args:
            initial: Starting value
            target: Target value to spring towards
            config: Spring physics configuration
            on_complete: Callback when spring settles

        Returns:
            Configured Spring instance
        """
        cfg = config or SpringConfig()

        initial_state = SpringState(
            value=initial,
            target=target,
            velocity=0.0,
            status=TransitionStatus.PENDING,
            elapsed_ms=0.0,
            at_rest=initial == target,
        )

        return cls(
            config=cfg,
            state=Signal.of(initial_state),
            _on_complete=on_complete,
        )

    def start(self) -> SpringState:
        """Start the spring animation."""
        current = self.state.value
        if current.status == TransitionStatus.PENDING:
            # Check if already at target
            at_rest = (
                abs(current.value - current.target) < self.config.rest_displacement
            )
            new_state = SpringState(
                value=current.value,
                target=current.target,
                velocity=0.0,
                status=TransitionStatus.COMPLETE
                if at_rest
                else TransitionStatus.RUNNING,
                elapsed_ms=0.0,
                at_rest=at_rest,
            )
            self.state.set(new_state)
            return new_state
        return current

    def update(self, delta_ms: float) -> SpringState:
        """
        Update the spring physics by delta time.

        Uses semi-implicit Euler integration for stability.

        Args:
            delta_ms: Time elapsed since last update

        Returns:
            New spring state
        """
        current = self.state.value

        if current.status != TransitionStatus.RUNNING:
            return current

        # Convert to seconds for physics
        dt = delta_ms / 1000.0

        # Spring physics
        displacement = current.value - current.target
        spring_force = -self.config.stiffness * displacement
        damping_force = -self.config.damping * current.velocity
        acceleration = (spring_force + damping_force) / self.config.mass

        # Semi-implicit Euler integration
        new_velocity = current.velocity + acceleration * dt
        new_value = current.value + new_velocity * dt

        # Clamping (optional)
        if self.config.clamp:
            min_val = min(current.value, current.target)
            max_val = max(current.value, current.target)
            new_value = max(min_val, min(max_val, new_value))

        # Check if at rest
        is_at_rest = (
            abs(new_velocity) < self.config.rest_velocity
            and abs(new_value - current.target) < self.config.rest_displacement
        )

        if is_at_rest:
            # Snap to target
            new_state = SpringState(
                value=current.target,
                target=current.target,
                velocity=0.0,
                status=TransitionStatus.COMPLETE,
                elapsed_ms=current.elapsed_ms + delta_ms,
                at_rest=True,
            )
            self.state.set(new_state)
            if self._on_complete:
                self._on_complete(self)
            return new_state

        new_state = SpringState(
            value=new_value,
            target=current.target,
            velocity=new_velocity,
            status=TransitionStatus.RUNNING,
            elapsed_ms=current.elapsed_ms + delta_ms,
            at_rest=False,
        )
        self.state.set(new_state)
        return new_state

    def set_target(self, target: float) -> SpringState:
        """
        Set a new target value.

        This is the key feature of springs: changing target mid-animation
        creates smooth, natural motion because velocity is preserved.

        Args:
            target: New target value

        Returns:
            Updated spring state
        """
        current = self.state.value

        # Check if already at new target
        at_rest = (
            abs(current.value - target) < self.config.rest_displacement
            and abs(current.velocity) < self.config.rest_velocity
        )

        new_state = SpringState(
            value=current.value,
            target=target,
            velocity=current.velocity,  # Preserve velocity!
            status=TransitionStatus.COMPLETE if at_rest else TransitionStatus.RUNNING,
            elapsed_ms=current.elapsed_ms,
            at_rest=at_rest,
        )
        self.state.set(new_state)
        return new_state

    def set_value(self, value: float, velocity: float = 0.0) -> SpringState:
        """
        Set value directly (e.g., from user drag).

        Args:
            value: New current value
            velocity: Optional initial velocity

        Returns:
            Updated spring state
        """
        current = self.state.value
        new_state = SpringState(
            value=value,
            target=current.target,
            velocity=velocity,
            status=TransitionStatus.RUNNING,
            elapsed_ms=current.elapsed_ms,
            at_rest=False,
        )
        self.state.set(new_state)
        return new_state

    def pause(self) -> SpringState:
        """Pause the spring animation."""
        current = self.state.value
        if current.status == TransitionStatus.RUNNING:
            new_state = SpringState(
                value=current.value,
                target=current.target,
                velocity=current.velocity,
                status=TransitionStatus.PAUSED,
                elapsed_ms=current.elapsed_ms,
                at_rest=current.at_rest,
            )
            self.state.set(new_state)
            return new_state
        return current

    def resume(self) -> SpringState:
        """Resume the spring animation."""
        current = self.state.value
        if current.status == TransitionStatus.PAUSED:
            new_state = SpringState(
                value=current.value,
                target=current.target,
                velocity=current.velocity,
                status=TransitionStatus.RUNNING,
                elapsed_ms=current.elapsed_ms,
                at_rest=current.at_rest,
            )
            self.state.set(new_state)
            return new_state
        return current

    def reset(self, value: float | None = None) -> SpringState:
        """
        Reset the spring to initial state.

        Args:
            value: Optional new initial value

        Returns:
            Reset spring state
        """
        current = self.state.value
        new_value = value if value is not None else current.value
        new_state = SpringState(
            value=new_value,
            target=current.target,
            velocity=0.0,
            status=TransitionStatus.PENDING,
            elapsed_ms=0.0,
            at_rest=new_value == current.target,
        )
        self.state.set(new_state)
        return new_state

    @property
    def is_complete(self) -> bool:
        """Check if spring has settled."""
        return self.state.value.status == TransitionStatus.COMPLETE

    @property
    def is_running(self) -> bool:
        """Check if spring is currently animating."""
        return self.state.value.status == TransitionStatus.RUNNING

    @property
    def value(self) -> float:
        """Get current value."""
        return self.state.value.value

    @property
    def velocity(self) -> float:
        """Get current velocity."""
        return self.state.value.velocity

    @property
    def target(self) -> float:
        """Get current target."""
        return self.state.value.target


def spring(
    initial: float,
    target: float,
    stiffness: float = 170.0,
    damping: float = 26.0,
) -> Spring:
    """
    Convenience function to create a Spring.

    Args:
        initial: Starting value
        target: Target value
        stiffness: Spring stiffness
        damping: Damping coefficient

    Returns:
        Configured Spring
    """
    return Spring.create(
        initial=initial,
        target=target,
        config=SpringConfig(stiffness=stiffness, damping=damping),
    )


@dataclass
class SpringVec2:
    """
    2D spring for position animations.

    Animates both X and Y with the same spring physics.
    """

    x: Spring
    y: Spring

    @classmethod
    def create(
        cls,
        initial: tuple[float, float],
        target: tuple[float, float],
        config: SpringConfig | None = None,
    ) -> SpringVec2:
        """Create a 2D spring."""
        cfg = config or SpringConfig()
        return cls(
            x=Spring.create(initial[0], target[0], cfg),
            y=Spring.create(initial[1], target[1], cfg),
        )

    def start(self) -> None:
        """Start both springs."""
        self.x.start()
        self.y.start()

    def update(self, delta_ms: float) -> tuple[float, float]:
        """Update both springs."""
        self.x.update(delta_ms)
        self.y.update(delta_ms)
        return self.value

    def set_target(self, target: tuple[float, float]) -> None:
        """Set target for both springs."""
        self.x.set_target(target[0])
        self.y.set_target(target[1])

    @property
    def value(self) -> tuple[float, float]:
        """Get current (x, y) position."""
        return (self.x.value, self.y.value)

    @property
    def is_complete(self) -> bool:
        """Check if both springs have settled."""
        return self.x.is_complete and self.y.is_complete
