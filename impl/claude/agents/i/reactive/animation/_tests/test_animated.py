"""Tests for AnimatedWidget and AnimationMixin."""

from dataclasses import dataclass
from typing import Any

import pytest
from agents.i.reactive.animation.animated import (
    AnimatedWidget,
    AnimationMixin,
    AnimationRegistry,
)
from agents.i.reactive.animation.frame import FrameScheduler
from agents.i.reactive.animation.spring import Spring, SpringConfig
from agents.i.reactive.animation.tween import (
    TransitionStatus,
    Tween,
    TweenConfig,
    tween,
)
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget


class TestAnimationRegistry:
    """Tests for AnimationRegistry."""

    def test_register_tween(self) -> None:
        """Register a tween animation."""
        registry = AnimationRegistry()
        tw = tween(0.0, 100.0)
        registry.register_tween("opacity", tw)
        assert registry.get_tween("opacity") is tw

    def test_register_spring(self) -> None:
        """Register a spring animation."""
        registry = AnimationRegistry()
        sp = Spring.create(initial=0.0, target=100.0)
        registry.register_spring("position", sp)
        assert registry.get_spring("position") is sp

    def test_unregister_tween(self) -> None:
        """Unregister a tween animation."""
        registry = AnimationRegistry()
        tw = tween(0.0, 100.0)
        registry.register_tween("opacity", tw)
        result = registry.unregister("opacity")
        assert result is True
        assert registry.get_tween("opacity") is None

    def test_unregister_spring(self) -> None:
        """Unregister a spring animation."""
        registry = AnimationRegistry()
        sp = Spring.create(initial=0.0, target=100.0)
        registry.register_spring("position", sp)
        result = registry.unregister("position")
        assert result is True
        assert registry.get_spring("position") is None

    def test_unregister_nonexistent(self) -> None:
        """Unregister returns False for non-existent."""
        registry = AnimationRegistry()
        result = registry.unregister("fake")
        assert result is False

    def test_update_all_updates_tweens(self) -> None:
        """update_all updates running tweens."""
        registry = AnimationRegistry()
        tw = tween(0.0, 100.0, duration_ms=100.0)
        tw.start()
        registry.register_tween("test", tw)

        changed = registry.update_all(50.0)
        assert changed is True
        assert tw.progress > 0

    def test_update_all_updates_springs(self) -> None:
        """update_all updates running springs."""
        registry = AnimationRegistry()
        sp = Spring.create(initial=0.0, target=100.0)
        sp.start()
        registry.register_spring("test", sp)

        changed = registry.update_all(16.67)
        assert changed is True
        assert sp.value > 0

    def test_update_all_returns_false_when_nothing_running(self) -> None:
        """update_all returns False when nothing is running."""
        registry = AnimationRegistry()
        tw = tween(0.0, 100.0)  # Not started
        registry.register_tween("test", tw)

        changed = registry.update_all(16.67)
        assert changed is False

    def test_start_all(self) -> None:
        """start_all starts all pending animations."""
        registry = AnimationRegistry()
        tw = tween(0.0, 100.0)
        sp = Spring.create(initial=0.0, target=100.0)
        registry.register_tween("tween", tw)
        registry.register_spring("spring", sp)

        registry.start_all()

        assert tw.is_running
        assert sp.is_running

    def test_pause_all(self) -> None:
        """pause_all pauses all running animations."""
        registry = AnimationRegistry()
        tw = tween(0.0, 100.0)
        tw.start()
        sp = Spring.create(initial=0.0, target=100.0)
        sp.start()
        registry.register_tween("tween", tw)
        registry.register_spring("spring", sp)

        registry.pause_all()

        assert tw.state.value.status == TransitionStatus.PAUSED
        assert sp.state.value.status == TransitionStatus.PAUSED

    def test_resume_all(self) -> None:
        """resume_all resumes all paused animations."""
        registry = AnimationRegistry()
        tw = tween(0.0, 100.0)
        tw.start()
        tw.pause()
        sp = Spring.create(initial=0.0, target=100.0)
        sp.start()
        sp.pause()
        registry.register_tween("tween", tw)
        registry.register_spring("spring", sp)

        registry.resume_all()

        assert tw.is_running
        assert sp.is_running

    def test_reset_all(self) -> None:
        """reset_all resets all animations."""
        registry = AnimationRegistry()
        tw = tween(0.0, 100.0)
        tw.start()
        tw.update(50.0)
        sp = Spring.create(initial=0.0, target=100.0)
        sp.start()
        sp.update(16.67)
        registry.register_tween("tween", tw)
        registry.register_spring("spring", sp)

        registry.reset_all()

        assert tw.state.value.status == TransitionStatus.PENDING
        assert sp.state.value.status == TransitionStatus.PENDING

    def test_any_running(self) -> None:
        """any_running returns True if any animation is running."""
        registry = AnimationRegistry()
        tw = tween(0.0, 100.0)
        registry.register_tween("test", tw)
        assert registry.any_running is False

        tw.start()
        assert registry.any_running is True

    def test_all_complete(self) -> None:
        """all_complete returns True when all animations complete."""
        registry = AnimationRegistry()
        tw = tween(0.0, 100.0, duration_ms=100.0)
        tw.start()
        registry.register_tween("test", tw)

        assert registry.all_complete is False

        tw.update(100.0)
        assert registry.all_complete is True

    def test_clear(self) -> None:
        """clear removes all animations."""
        registry = AnimationRegistry()
        registry.register_tween("tween", tween(0.0, 100.0))
        registry.register_spring("spring", Spring.create(initial=0.0, target=100.0))

        registry.clear()

        assert registry.get_tween("tween") is None
        assert registry.get_spring("spring") is None


@dataclass(frozen=True)
class TestWidgetState:
    """Simple test widget state."""

    value: float = 0.0


class ConcreteAnimatedWidget(AnimatedWidget[TestWidgetState]):
    """Concrete implementation for testing."""

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return f"Value: {self._animations.get_spring('value')}"
            case RenderTarget.JSON:
                return {"value": self.state.value.value}
            case _:
                return str(self.state.value.value)


class TestAnimatedWidget:
    """Tests for AnimatedWidget."""

    def test_create_widget(self) -> None:
        """Create animated widget."""
        widget = ConcreteAnimatedWidget(TestWidgetState(value=0.0))
        assert widget.state.value.value == 0.0

    def test_animate_value_creates_tween(self) -> None:
        """animate_value creates and registers a tween."""
        widget = ConcreteAnimatedWidget(TestWidgetState())
        tw = widget.animate_value("opacity", 0.0, 1.0, duration_ms=300.0)

        assert tw.is_running
        assert widget._animations.get_tween("opacity") is tw

    def test_spring_to_creates_spring(self) -> None:
        """spring_to creates and registers a spring."""
        widget = ConcreteAnimatedWidget(TestWidgetState())
        sp = widget.spring_to("position", target=100.0, initial=0.0)

        assert sp.is_running
        assert widget._animations.get_spring("position") is sp

    def test_spring_to_updates_existing(self) -> None:
        """spring_to updates target of existing spring."""
        widget = ConcreteAnimatedWidget(TestWidgetState())
        sp1 = widget.spring_to("position", target=100.0, initial=0.0)
        sp2 = widget.spring_to("position", target=50.0)

        assert sp1 is sp2
        assert sp1.target == 50.0

    def test_is_animating_property(self) -> None:
        """is_animating returns True when animations running."""
        widget = ConcreteAnimatedWidget(TestWidgetState())
        assert widget.is_animating is False

        widget.animate_value("test", 0.0, 100.0)
        assert widget.is_animating is True

    def test_dirty_tracking(self) -> None:
        """Dirty tracking works correctly."""
        widget = ConcreteAnimatedWidget(TestWidgetState())
        assert widget.is_dirty is True  # Initially dirty

        widget.mark_clean()
        assert widget.is_dirty is False

        widget.mark_dirty()
        assert widget.is_dirty is True

    def test_connect_scheduler(self) -> None:
        """Connect to frame scheduler."""
        widget = ConcreteAnimatedWidget(TestWidgetState())
        scheduler = FrameScheduler.create()

        widget.connect_scheduler(scheduler)

        assert scheduler.callback_count == 1

    def test_disconnect_scheduler(self) -> None:
        """Disconnect from frame scheduler."""
        widget = ConcreteAnimatedWidget(TestWidgetState())
        scheduler = FrameScheduler.create()
        widget.connect_scheduler(scheduler)

        widget.disconnect_scheduler()

        assert scheduler.callback_count == 0

    def test_scheduler_updates_animations(self) -> None:
        """Scheduler updates trigger animation updates."""
        widget = ConcreteAnimatedWidget(TestWidgetState())
        scheduler = FrameScheduler.create()
        widget.connect_scheduler(scheduler)

        tw = widget.animate_value("test", 0.0, 100.0, duration_ms=100.0)

        scheduler.process_frame(delta_ms=50.0)

        assert tw.progress > 0

    def test_dispose_cleans_up(self) -> None:
        """Dispose cleans up resources."""
        widget = ConcreteAnimatedWidget(TestWidgetState())
        scheduler = FrameScheduler.create()
        widget.connect_scheduler(scheduler)
        widget.animate_value("test", 0.0, 100.0)

        widget.dispose()

        assert scheduler.callback_count == 0
        assert widget._animations.get_tween("test") is None

    def test_project_uses_animation_values(self) -> None:
        """Projection can access animation values."""
        widget = ConcreteAnimatedWidget(TestWidgetState())
        widget.spring_to("value", target=100.0, initial=0.0)

        result = widget.project(RenderTarget.CLI)
        assert "value" in result.lower()


class ConcreteWidgetWithMixin(KgentsWidget[TestWidgetState], AnimationMixin):
    """Widget using AnimationMixin."""

    def __init__(self) -> None:
        self.state = Signal.of(TestWidgetState())
        self._init_animation()

    def project(self, target: RenderTarget) -> Any:
        return str(self.state.value.value)


class TestAnimationMixin:
    """Tests for AnimationMixin."""

    def test_mixin_initialization(self) -> None:
        """Mixin initializes correctly."""
        widget = ConcreteWidgetWithMixin()
        assert hasattr(widget, "_animations")
        assert widget._dirty is True

    def test_mixin_animate_value(self) -> None:
        """Mixin can animate values."""
        widget = ConcreteWidgetWithMixin()
        tw = widget.animate_value("test", 0.0, 100.0)
        assert tw.is_running

    def test_mixin_spring_to(self) -> None:
        """Mixin can create springs."""
        widget = ConcreteWidgetWithMixin()
        sp = widget.spring_to("test", target=100.0, initial=0.0)
        assert sp.is_running

    def test_mixin_connect_scheduler(self) -> None:
        """Mixin can connect to scheduler."""
        widget = ConcreteWidgetWithMixin()
        scheduler = FrameScheduler.create()

        widget.connect_scheduler(scheduler)
        assert scheduler.callback_count == 1

        widget.disconnect_scheduler()
        assert scheduler.callback_count == 0

    def test_mixin_is_animating(self) -> None:
        """Mixin tracks animation state."""
        widget = ConcreteWidgetWithMixin()
        assert widget.is_animating is False

        widget.animate_value("test", 0.0, 100.0)
        assert widget.is_animating is True

    def test_mixin_dirty_tracking(self) -> None:
        """Mixin tracks dirty state."""
        widget = ConcreteWidgetWithMixin()
        widget.mark_clean()
        assert widget.is_dirty is False

        widget.mark_dirty()
        assert widget.is_dirty is True
