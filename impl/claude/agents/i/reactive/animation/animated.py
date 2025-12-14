"""
Animated Widget: Base class for widgets with animation support.

AnimatedWidget extends KgentsWidget with:
- Frame callback subscription
- Animation instance management
- Dirty checking for efficient updates
- Integration with Clock and FrameScheduler

Key insight: Animation is a widget concern, not a rendering concern.
The widget owns its animations; projectors just render current state.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from agents.i.reactive.animation.spring import Spring
from agents.i.reactive.animation.tween import TransitionStatus, Tween
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    from agents.i.reactive.animation.frame import FrameScheduler
    from agents.i.reactive.wiring.clock import Clock

S = TypeVar("S")


@dataclass
class AnimationRegistry:
    """
    Registry for managing active animations on a widget.

    Tracks all running animations and provides batch update/cleanup.
    """

    _tweens: dict[str, Tween[Any]] = field(default_factory=dict)
    _springs: dict[str, Spring] = field(default_factory=dict)

    def register_tween(self, name: str, tween: Tween[Any]) -> None:
        """Register a tween animation."""
        self._tweens[name] = tween

    def register_spring(self, name: str, spring: Spring) -> None:
        """Register a spring animation."""
        self._springs[name] = spring

    def unregister(self, name: str) -> bool:
        """Unregister an animation by name."""
        if name in self._tweens:
            del self._tweens[name]
            return True
        if name in self._springs:
            del self._springs[name]
            return True
        return False

    def update_all(self, delta_ms: float) -> bool:
        """
        Update all animations by delta time.

        Returns:
            True if any animation changed (needs redraw)
        """
        changed = False

        # Update tweens
        for tween in list(self._tweens.values()):
            if tween.is_running:
                tween.update(delta_ms)
                changed = True

        # Update springs
        for spring in list(self._springs.values()):
            if spring.is_running:
                spring.update(delta_ms)
                changed = True

        return changed

    def start_all(self) -> None:
        """Start all pending animations."""
        for tween in self._tweens.values():
            if tween.state.value.status == TransitionStatus.PENDING:
                tween.start()
        for spring in self._springs.values():
            if spring.state.value.status == TransitionStatus.PENDING:
                spring.start()

    def pause_all(self) -> None:
        """Pause all running animations."""
        for tween in self._tweens.values():
            tween.pause()
        for spring in self._springs.values():
            spring.pause()

    def resume_all(self) -> None:
        """Resume all paused animations."""
        for tween in self._tweens.values():
            tween.resume()
        for spring in self._springs.values():
            spring.resume()

    def reset_all(self) -> None:
        """Reset all animations to initial state."""
        for tween in self._tweens.values():
            tween.reset()
        for spring in self._springs.values():
            spring.reset()

    def get_tween(self, name: str) -> Tween[Any] | None:
        """Get a tween by name."""
        return self._tweens.get(name)

    def get_spring(self, name: str) -> Spring | None:
        """Get a spring by name."""
        return self._springs.get(name)

    @property
    def any_running(self) -> bool:
        """Check if any animation is running."""
        return any(t.is_running for t in self._tweens.values()) or any(
            s.is_running for s in self._springs.values()
        )

    @property
    def all_complete(self) -> bool:
        """Check if all animations are complete."""
        tweens_done = all(t.is_complete for t in self._tweens.values())
        springs_done = all(s.is_complete for s in self._springs.values())
        return tweens_done and springs_done

    def clear(self) -> None:
        """Remove all animations."""
        self._tweens.clear()
        self._springs.clear()


class AnimationMixin:
    """
    Mixin for adding animation support to any widget.

    Use this mixin when you want animation capabilities without
    extending AnimatedWidget directly.

    Example:
        class MyWidget(KgentsWidget[MyState], AnimationMixin):
            def __init__(self):
                super().__init__()
                self._init_animation()
                self.animate_property("opacity", 0.0, 1.0, duration_ms=300)
    """

    _animations: AnimationRegistry
    _dirty: bool
    _frame_callback_id: int | None
    _scheduler: FrameScheduler | None

    def _init_animation(self) -> None:
        """Initialize animation support. Call in __init__."""
        self._animations = AnimationRegistry()
        self._dirty = True
        self._frame_callback_id = None
        self._scheduler = None

    def connect_scheduler(self, scheduler: FrameScheduler) -> None:
        """
        Connect to a FrameScheduler for automatic updates.

        Args:
            scheduler: The scheduler to receive frame callbacks from
        """
        self._scheduler = scheduler
        self._frame_callback_id = scheduler.request_frame(self._on_frame)

    def disconnect_scheduler(self) -> None:
        """Disconnect from the frame scheduler."""
        if self._scheduler and self._frame_callback_id is not None:
            self._scheduler.cancel_frame(self._frame_callback_id)
            self._frame_callback_id = None
            self._scheduler = None

    def _on_frame(self, delta_ms: float, frame: int, t: float) -> None:
        """Internal frame callback handler."""
        if self._animations.update_all(delta_ms):
            self._dirty = True
            self._on_animation_frame(delta_ms, frame, t)

    def _on_animation_frame(self, delta_ms: float, frame: int, t: float) -> None:
        """Override to handle animation frame updates."""
        pass

    def animate_value(
        self,
        name: str,
        start: float,
        end: float,
        duration_ms: float = 300.0,
        auto_start: bool = True,
    ) -> Tween[float]:
        """
        Create and register a value animation.

        Args:
            name: Unique name for this animation
            start: Starting value
            end: Ending value
            duration_ms: Animation duration
            auto_start: Whether to start immediately

        Returns:
            The created Tween
        """
        from agents.i.reactive.animation.easing import Easing
        from agents.i.reactive.animation.tween import Tween, TweenConfig

        tween: Tween[float] = Tween.create(
            start=start,
            end=end,
            config=TweenConfig(duration_ms=duration_ms, easing=Easing.EASE_OUT),
        )
        self._animations.register_tween(name, tween)
        if auto_start:
            tween.start()
        return tween

    def spring_to(
        self,
        name: str,
        target: float,
        initial: float | None = None,
    ) -> Spring:
        """
        Create or update a spring animation.

        If a spring with this name exists, updates its target.
        Otherwise, creates a new spring.

        Args:
            name: Unique name for this spring
            target: Target value
            initial: Initial value (only for new springs)

        Returns:
            The Spring instance
        """
        from agents.i.reactive.animation.spring import Spring, SpringConfig

        existing = self._animations.get_spring(name)
        if existing:
            existing.set_target(target)
            return existing

        spring = Spring.create(
            initial=initial if initial is not None else target,
            target=target,
            config=SpringConfig(),
        )
        self._animations.register_spring(name, spring)
        spring.start()
        return spring

    @property
    def is_animating(self) -> bool:
        """Check if any animations are running."""
        return self._animations.any_running

    @property
    def is_dirty(self) -> bool:
        """Check if widget needs redraw."""
        return self._dirty

    def mark_clean(self) -> None:
        """Mark widget as not needing redraw."""
        self._dirty = False

    def mark_dirty(self) -> None:
        """Mark widget as needing redraw."""
        self._dirty = True


class AnimatedWidget(KgentsWidget[S], Generic[S]):
    """
    Base class for widgets with animation support.

    Extends KgentsWidget with:
    - Animation registry for managing tweens/springs
    - Frame callback integration
    - Dirty checking for efficient updates

    Example:
        @dataclass(frozen=True)
        class SliderState:
            value: float = 0.0
            target: float = 0.0

        class SliderWidget(AnimatedWidget[SliderState]):
            def __init__(self, initial: float = 0.0):
                super().__init__(SliderState(value=initial))
                self._value_spring = self.spring_to("value", initial)

            def set_value(self, target: float) -> None:
                self._value_spring.set_target(target)

            def project(self, target: RenderTarget) -> Any:
                value = self._value_spring.value
                match target:
                    case RenderTarget.CLI:
                        filled = int(value / 10)
                        return f"[{'█' * filled}{'░' * (10 - filled)}] {value:.1f}"
                    case RenderTarget.JSON:
                        return {"type": "slider", "value": value}
                    case _:
                        return f"Slider: {value}"
    """

    _animations: AnimationRegistry
    _dirty: bool
    _frame_callback_id: int | None
    _scheduler: FrameScheduler | None

    def __init__(self, initial_state: S) -> None:
        """
        Initialize an animated widget.

        Args:
            initial_state: Initial widget state
        """

        self.state = Signal.of(initial_state)
        self._animations = AnimationRegistry()
        self._dirty = True
        self._frame_callback_id = None
        self._scheduler = None

    def connect_scheduler(self, scheduler: FrameScheduler) -> None:
        """Connect to a FrameScheduler for automatic updates."""
        self._scheduler = scheduler
        self._frame_callback_id = scheduler.request_frame(self._on_frame)

    def disconnect_scheduler(self) -> None:
        """Disconnect from the frame scheduler."""
        if self._scheduler and self._frame_callback_id is not None:
            self._scheduler.cancel_frame(self._frame_callback_id)
            self._frame_callback_id = None
            self._scheduler = None

    def _on_frame(self, delta_ms: float, frame: int, t: float) -> None:
        """Internal frame callback handler."""
        if self._animations.update_all(delta_ms):
            self._dirty = True
            self.on_animation_frame(delta_ms, frame, t)

    def on_animation_frame(self, delta_ms: float, frame: int, t: float) -> None:
        """
        Override to handle animation frame updates.

        Called whenever an animation updates the widget state.

        Args:
            delta_ms: Time since last frame
            frame: Current frame number
            t: Total elapsed time
        """
        pass

    def animate_value(
        self,
        name: str,
        start: float,
        end: float,
        duration_ms: float = 300.0,
        auto_start: bool = True,
    ) -> Tween[float]:
        """Create and register a value animation."""
        from agents.i.reactive.animation.easing import Easing
        from agents.i.reactive.animation.tween import Tween, TweenConfig

        tween: Tween[float] = Tween.create(
            start=start,
            end=end,
            config=TweenConfig(duration_ms=duration_ms, easing=Easing.EASE_OUT),
        )
        self._animations.register_tween(name, tween)
        if auto_start:
            tween.start()
        return tween

    def spring_to(
        self,
        name: str,
        target: float,
        initial: float | None = None,
    ) -> Spring:
        """Create or update a spring animation."""
        from agents.i.reactive.animation.spring import Spring, SpringConfig

        existing = self._animations.get_spring(name)
        if existing:
            existing.set_target(target)
            return existing

        spring = Spring.create(
            initial=initial if initial is not None else target,
            target=target,
            config=SpringConfig(),
        )
        self._animations.register_spring(name, spring)
        spring.start()
        return spring

    @property
    def is_animating(self) -> bool:
        """Check if any animations are running."""
        return self._animations.any_running

    @property
    def is_dirty(self) -> bool:
        """Check if widget needs redraw."""
        return self._dirty

    def mark_clean(self) -> None:
        """Mark widget as not needing redraw."""
        self._dirty = False

    def mark_dirty(self) -> None:
        """Mark widget as needing redraw."""
        self._dirty = True

    @abstractmethod
    def project(self, target: RenderTarget) -> Any:
        """Project this animated widget to a rendering target."""
        ...

    def dispose(self) -> None:
        """Clean up resources."""
        self.disconnect_scheduler()
        self._animations.clear()
