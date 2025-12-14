"""
Animated Focus: Focus management with spring-based transitions.

Builds on Wave 6's FocusState to add smooth animated transitions.

Focus transitions feel natural because they use spring physics:
- Moving focus to a new widget animates smoothly
- Interrupting a transition preserves velocity
- Focus ring pulses subtly to indicate activity

"Focus is attention made visible. Smooth transitions guide the eye."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable

from agents.i.reactive.animation.spring import Spring, SpringConfig, SpringVec2
from agents.i.reactive.animation.tween import TransitionStatus
from agents.i.reactive.signal import Signal
from agents.i.reactive.wiring.interactions import FocusDirection, FocusState

if TYPE_CHECKING:
    from agents.i.reactive.wiring.clock import Clock, ClockState


class FocusTransitionStyle(Enum):
    """Style of focus transition animation."""

    NONE = auto()  # Instant switch
    FADE = auto()  # Fade out/in
    SLIDE = auto()  # Slide to new position
    SPRING = auto()  # Spring-based movement


@dataclass(frozen=True)
class FocusVisualState:
    """
    Visual state for focus rendering.

    Provides interpolated values for smooth transitions.
    """

    # Current focused element ID
    focused_id: str | None = None

    # Previous focused element ID (for transition)
    previous_id: str | None = None

    # Transition progress [0, 1]
    transition_progress: float = 1.0

    # Focus ring opacity [0, 1]
    ring_opacity: float = 1.0

    # Focus ring position (for slide/spring)
    ring_x: float = 0.0
    ring_y: float = 0.0

    # Focus ring scale (for pulse effect)
    ring_scale: float = 1.0

    # Whether transition is active
    transitioning: bool = False


@dataclass
class FocusTransition:
    """
    Manages focus transition animations.

    Wraps FocusState with spring-based transitions.

    Example:
        transition = FocusTransition()
        transition.start("widget-1", "widget-2")  # Animate from 1 to 2

        # On each frame
        transition.update(delta_ms=16.67)
        state = transition.visual_state

        # Use state.ring_x, state.ring_y for position
        # Use state.ring_opacity for fade effect
    """

    _from_id: str | None = None
    _to_id: str | None = None
    _opacity_spring: Spring = field(
        default_factory=lambda: Spring.create(1.0, 1.0, SpringConfig.stiff())
    )
    _position_spring: SpringVec2 = field(
        default_factory=lambda: SpringVec2.create((0, 0), (0, 0), SpringConfig.wobbly())
    )
    _scale_spring: Spring = field(
        default_factory=lambda: Spring.create(1.0, 1.0, SpringConfig.bouncy())
    )
    _visual_state: Signal[FocusVisualState] = field(
        default_factory=lambda: Signal.of(FocusVisualState())
    )
    _positions: dict[str, tuple[float, float]] = field(default_factory=dict)

    @property
    def visual_state(self) -> FocusVisualState:
        """Get current visual state."""
        return self._visual_state.value

    @property
    def signal(self) -> Signal[FocusVisualState]:
        """Signal for visual state changes."""
        return self._visual_state

    def register_position(self, element_id: str, x: float, y: float) -> None:
        """
        Register an element's position for slide/spring transitions.

        Args:
            element_id: Element identifier
            x: X position
            y: Y position
        """
        self._positions[element_id] = (x, y)

    def start(
        self,
        from_id: str | None,
        to_id: str | None,
        style: FocusTransitionStyle = FocusTransitionStyle.SPRING,
    ) -> None:
        """
        Start a focus transition.

        Args:
            from_id: Element losing focus
            to_id: Element gaining focus
            style: Transition style
        """
        self._from_id = from_id
        self._to_id = to_id

        if style == FocusTransitionStyle.NONE:
            # Instant switch
            self._update_visual_state(
                focused_id=to_id,
                previous_id=from_id,
                transition_progress=1.0,
                ring_opacity=1.0 if to_id else 0.0,
            )
            return

        # Start opacity transition
        if to_id:
            self._opacity_spring.set_target(1.0)
        else:
            self._opacity_spring.set_target(0.0)

        if self._opacity_spring.state.value.status == TransitionStatus.PENDING:
            self._opacity_spring.start()

        # Start position transition
        if style in (FocusTransitionStyle.SLIDE, FocusTransitionStyle.SPRING):
            from_pos = (
                self._positions.get(from_id, (0.0, 0.0)) if from_id else (0.0, 0.0)
            )
            to_pos = self._positions.get(to_id, from_pos) if to_id else from_pos

            if from_id:
                self._position_spring.x.set_value(from_pos[0])
                self._position_spring.y.set_value(from_pos[1])

            self._position_spring.set_target(to_pos)

            if self._position_spring.x.state.value.status == TransitionStatus.PENDING:
                self._position_spring.start()

        # Pulse scale on new focus
        if to_id:
            self._scale_spring.set_value(0.9)
            self._scale_spring.set_target(1.0)
            if self._scale_spring.state.value.status == TransitionStatus.PENDING:
                self._scale_spring.start()

        # Initial visual state
        self._update_visual_state(
            focused_id=to_id,
            previous_id=from_id,
            transition_progress=0.0,
            ring_opacity=self._opacity_spring.value,
            ring_x=self._position_spring.value[0],
            ring_y=self._position_spring.value[1],
            ring_scale=self._scale_spring.value,
            transitioning=True,
        )

    def update(self, delta_ms: float) -> FocusVisualState:
        """
        Update transition animations.

        Args:
            delta_ms: Time since last update

        Returns:
            Updated visual state
        """
        # Update springs
        self._opacity_spring.update(delta_ms)
        self._position_spring.update(delta_ms)
        self._scale_spring.update(delta_ms)

        # Check if still transitioning
        transitioning = (
            self._opacity_spring.is_running
            or self._position_spring.x.is_running
            or self._position_spring.y.is_running
            or self._scale_spring.is_running
        )

        # Calculate progress (based on position spring)
        if self._position_spring.x.is_running:
            progress = 1.0 - abs(
                self._position_spring.x.value - self._position_spring.x.target
            ) / max(
                1.0,
                abs(
                    self._positions.get(self._from_id, (0.0, 0.0))[0]
                    - self._positions.get(self._to_id, (0.0, 0.0))[0]
                )
                if self._from_id and self._to_id
                else 1.0,
            )
        else:
            progress = 1.0

        self._update_visual_state(
            focused_id=self._to_id,
            previous_id=self._from_id,
            transition_progress=min(1.0, max(0.0, progress)),
            ring_opacity=self._opacity_spring.value,
            ring_x=self._position_spring.value[0],
            ring_y=self._position_spring.value[1],
            ring_scale=self._scale_spring.value,
            transitioning=transitioning,
        )

        return self._visual_state.value

    def _update_visual_state(
        self,
        focused_id: str | None = None,
        previous_id: str | None = None,
        transition_progress: float = 1.0,
        ring_opacity: float = 1.0,
        ring_x: float = 0.0,
        ring_y: float = 0.0,
        ring_scale: float = 1.0,
        transitioning: bool = False,
    ) -> None:
        """Update the visual state signal."""
        self._visual_state.set(
            FocusVisualState(
                focused_id=focused_id,
                previous_id=previous_id,
                transition_progress=transition_progress,
                ring_opacity=ring_opacity,
                ring_x=ring_x,
                ring_y=ring_y,
                ring_scale=ring_scale,
                transitioning=transitioning,
            )
        )

    @property
    def is_transitioning(self) -> bool:
        """Whether a transition is in progress."""
        return self._visual_state.value.transitioning


@dataclass
class AnimatedFocus:
    """
    Focus manager with animated transitions.

    Combines FocusState for focus logic with FocusTransition
    for smooth visual transitions.

    Example:
        focus = AnimatedFocus.create()

        # Register focusable elements with positions
        focus.register("header", tab_index=0, position=(0, 0))
        focus.register("sidebar", tab_index=1, position=(0, 3))
        focus.register("content", tab_index=2, position=(20, 3))

        # Focus with animation
        focus.focus("sidebar")  # Animates to sidebar

        # Update on each frame
        focus.update(delta_ms=16.67)
        visual = focus.visual_state

        # Render focus ring at visual.ring_x, visual.ring_y
        # with opacity visual.ring_opacity
    """

    focus_state: FocusState = field(default_factory=FocusState)
    transition: FocusTransition = field(default_factory=FocusTransition)
    transition_style: FocusTransitionStyle = FocusTransitionStyle.SPRING
    _clock: Clock | None = None
    _unsubscribe: Callable[[], None] | None = None
    _on_focus_change: Callable[[str | None, str | None], None] | None = None

    @classmethod
    def create(
        cls,
        transition_style: FocusTransitionStyle = FocusTransitionStyle.SPRING,
        clock: Clock | None = None,
        on_focus_change: Callable[[str | None, str | None], None] | None = None,
    ) -> AnimatedFocus:
        """
        Create an AnimatedFocus manager.

        Args:
            transition_style: Default transition style
            clock: Optional clock for automatic updates
            on_focus_change: Callback when focus changes (old_id, new_id)

        Returns:
            Configured AnimatedFocus
        """
        instance = cls(
            focus_state=FocusState(),
            transition=FocusTransition(),
            transition_style=transition_style,
            _on_focus_change=on_focus_change,
        )

        # Connect to clock if provided
        if clock:
            instance.connect_clock(clock)

        return instance

    def register(
        self,
        element_id: str,
        tab_index: int = 0,
        focusable: bool = True,
        group: str = "",
        position: tuple[float, float] | None = None,
    ) -> None:
        """
        Register a focusable element.

        Args:
            element_id: Unique identifier
            tab_index: Position in tab order
            focusable: Whether element can receive focus
            group: Logical grouping
            position: Screen position for slide/spring transitions
        """
        self.focus_state.register(
            element_id, tab_index=tab_index, focusable=focusable, group=group
        )

        if position:
            self.transition.register_position(element_id, position[0], position[1])

    def unregister(self, element_id: str) -> None:
        """Remove a focusable element."""
        self.focus_state.unregister(element_id)

    def update_position(self, element_id: str, x: float, y: float) -> None:
        """Update an element's position for transitions."""
        self.transition.register_position(element_id, x, y)

    def focus(
        self,
        element_id: str,
        style: FocusTransitionStyle | None = None,
    ) -> bool:
        """
        Focus an element with animated transition.

        Args:
            element_id: Element to focus
            style: Override transition style

        Returns:
            True if focus changed
        """
        old_id = self.focus_state.focused_id

        if not self.focus_state.focus(element_id):
            return False

        new_id = self.focus_state.focused_id

        if old_id != new_id:
            self.transition.start(old_id, new_id, style or self.transition_style)
            if self._on_focus_change:
                self._on_focus_change(old_id, new_id)

        return True

    def blur(self, style: FocusTransitionStyle | None = None) -> None:
        """Remove focus with animated transition."""
        old_id = self.focus_state.focused_id
        self.focus_state.blur()
        self.transition.start(old_id, None, style or self.transition_style)
        if self._on_focus_change:
            self._on_focus_change(old_id, None)

    def move(
        self,
        direction: FocusDirection,
        style: FocusTransitionStyle | None = None,
    ) -> str | None:
        """
        Move focus in direction with animated transition.

        Args:
            direction: FORWARD or BACKWARD
            style: Override transition style

        Returns:
            New focused element ID, or None
        """
        old_id = self.focus_state.focused_id
        new_id = self.focus_state.move(direction)

        if old_id != new_id:
            self.transition.start(old_id, new_id, style or self.transition_style)
            if self._on_focus_change:
                self._on_focus_change(old_id, new_id)

        return new_id

    def update(self, delta_ms: float) -> FocusVisualState:
        """
        Update transition animations.

        Args:
            delta_ms: Time since last update

        Returns:
            Current visual state
        """
        return self.transition.update(delta_ms)

    def connect_clock(self, clock: Clock) -> Callable[[], None]:
        """
        Connect to a Clock for automatic updates.

        Args:
            clock: Clock to connect to

        Returns:
            Unsubscribe function
        """
        if self._unsubscribe:
            self._unsubscribe()

        def on_tick(state: ClockState) -> None:
            if state.running:
                self.transition.update(state.delta)

        self._clock = clock
        self._unsubscribe = clock.subscribe(on_tick)
        return self._unsubscribe

    @property
    def focused_id(self) -> str | None:
        """Currently focused element ID."""
        return self.focus_state.focused_id

    @property
    def visual_state(self) -> FocusVisualState:
        """Current visual state for rendering."""
        return self.transition.visual_state

    @property
    def is_transitioning(self) -> bool:
        """Whether a focus transition is in progress."""
        return self.transition.is_transitioning

    def is_focused(self, element_id: str) -> bool:
        """Check if element is focused."""
        return self.focus_state.is_focused(element_id)

    def dispose(self) -> None:
        """Clean up resources."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None


def create_animated_focus(
    transition_style: FocusTransitionStyle = FocusTransitionStyle.SPRING,
    clock: Clock | None = None,
) -> AnimatedFocus:
    """
    Create an AnimatedFocus with common defaults.

    Args:
        transition_style: Style for focus transitions
        clock: Optional clock for automatic updates

    Returns:
        Configured AnimatedFocus
    """
    return AnimatedFocus.create(transition_style=transition_style, clock=clock)
