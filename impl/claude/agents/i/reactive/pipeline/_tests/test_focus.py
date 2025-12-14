"""Tests for AnimatedFocus."""

import pytest
from agents.i.reactive.pipeline.focus import (
    AnimatedFocus,
    FocusTransition,
    FocusTransitionStyle,
    FocusVisualState,
    create_animated_focus,
)
from agents.i.reactive.wiring.interactions import FocusDirection


class TestFocusVisualState:
    """Tests for FocusVisualState."""

    def test_default_state(self) -> None:
        """FocusVisualState has correct defaults."""
        state = FocusVisualState()

        assert state.focused_id is None
        assert state.previous_id is None
        assert state.transition_progress == 1.0
        assert state.ring_opacity == 1.0
        assert state.transitioning is False


class TestFocusTransition:
    """Tests for FocusTransition."""

    def test_register_position(self) -> None:
        """Can register element positions."""
        transition = FocusTransition()
        transition.register_position("elem-1", 10.0, 20.0)
        transition.register_position("elem-2", 30.0, 40.0)

        assert transition._positions["elem-1"] == (10.0, 20.0)
        assert transition._positions["elem-2"] == (30.0, 40.0)

    def test_instant_transition(self) -> None:
        """NONE style transitions instantly."""
        transition = FocusTransition()
        transition.register_position("a", 0.0, 0.0)
        transition.register_position("b", 50.0, 0.0)

        transition.start("a", "b", FocusTransitionStyle.NONE)

        state = transition.visual_state
        assert state.focused_id == "b"
        assert state.previous_id == "a"
        assert state.transition_progress == 1.0
        assert state.transitioning is False

    def test_spring_transition_starts(self) -> None:
        """SPRING style starts transition."""
        transition = FocusTransition()
        transition.register_position("a", 0.0, 0.0)
        transition.register_position("b", 50.0, 0.0)

        transition.start("a", "b", FocusTransitionStyle.SPRING)

        state = transition.visual_state
        assert state.focused_id == "b"
        assert state.previous_id == "a"
        assert state.transitioning is True

    def test_update_advances_animation(self) -> None:
        """update() advances spring animation."""
        transition = FocusTransition()
        transition.register_position("a", 0.0, 0.0)
        transition.register_position("b", 50.0, 0.0)

        transition.start("a", "b", FocusTransitionStyle.SPRING)
        initial_x = transition.visual_state.ring_x

        # Update several times
        for _ in range(10):
            transition.update(16.67)

        # Position should have changed
        assert transition.visual_state.ring_x != initial_x

    def test_blur_transition(self) -> None:
        """Transition to None (blur) fades out."""
        transition = FocusTransition()
        transition.register_position("a", 0.0, 0.0)

        transition.start("a", None, FocusTransitionStyle.FADE)

        state = transition.visual_state
        assert state.focused_id is None
        assert state.previous_id == "a"


class TestAnimatedFocus:
    """Tests for AnimatedFocus."""

    def test_create(self) -> None:
        """AnimatedFocus can be created."""
        focus = create_animated_focus()

        assert focus.focused_id is None
        assert focus.is_transitioning is False

    def test_register_elements(self) -> None:
        """Can register focusable elements."""
        focus = create_animated_focus()

        focus.register("elem-1", tab_index=0, position=(0, 0))
        focus.register("elem-2", tab_index=1, position=(10, 0))
        focus.register("elem-3", tab_index=2, position=(20, 0))

        assert focus.focus_state.focusable_count() == 3

    def test_focus_element(self) -> None:
        """Can focus an element."""
        focus = create_animated_focus()
        focus.register("elem-1", tab_index=0)
        focus.register("elem-2", tab_index=1)

        result = focus.focus("elem-1")

        assert result is True
        assert focus.focused_id == "elem-1"
        assert focus.is_focused("elem-1") is True

    def test_focus_triggers_transition(self) -> None:
        """Focusing an element triggers transition animation."""
        focus = create_animated_focus(transition_style=FocusTransitionStyle.SPRING)
        focus.register("elem-1", tab_index=0, position=(0, 0))
        focus.register("elem-2", tab_index=1, position=(50, 0))

        focus.focus("elem-1")
        focus.focus("elem-2")

        assert focus.is_transitioning is True
        assert focus.visual_state.focused_id == "elem-2"
        assert focus.visual_state.previous_id == "elem-1"

    def test_blur(self) -> None:
        """blur() removes focus."""
        focus = create_animated_focus()
        focus.register("elem-1", tab_index=0)

        focus.focus("elem-1")
        assert focus.focused_id == "elem-1"

        focus.blur()
        assert focus.focused_id is None

    def test_move_forward(self) -> None:
        """move(FORWARD) advances focus."""
        focus = create_animated_focus()
        focus.register("elem-1", tab_index=0)
        focus.register("elem-2", tab_index=1)
        focus.register("elem-3", tab_index=2)

        focus.focus("elem-1")
        result = focus.move(FocusDirection.FORWARD)

        assert result == "elem-2"
        assert focus.focused_id == "elem-2"

    def test_move_backward(self) -> None:
        """move(BACKWARD) goes to previous."""
        focus = create_animated_focus()
        focus.register("elem-1", tab_index=0)
        focus.register("elem-2", tab_index=1)
        focus.register("elem-3", tab_index=2)

        focus.focus("elem-2")
        result = focus.move(FocusDirection.BACKWARD)

        assert result == "elem-1"
        assert focus.focused_id == "elem-1"

    def test_move_wraps_around(self) -> None:
        """move() wraps at ends."""
        focus = create_animated_focus()
        focus.register("elem-1", tab_index=0)
        focus.register("elem-2", tab_index=1)

        focus.focus("elem-2")
        result = focus.move(FocusDirection.FORWARD)

        assert result == "elem-1"

    def test_update_advances_animation(self) -> None:
        """update() advances transition animation."""
        focus = create_animated_focus(transition_style=FocusTransitionStyle.SPRING)
        focus.register("elem-1", tab_index=0, position=(0, 0))
        focus.register("elem-2", tab_index=1, position=(100, 0))

        focus.focus("elem-1")
        focus.focus("elem-2")

        initial_x = focus.visual_state.ring_x

        # Update to advance animation
        for _ in range(20):
            focus.update(16.67)

        # Animation should have progressed
        assert focus.visual_state.ring_x > initial_x

    def test_update_position(self) -> None:
        """Can update element positions."""
        focus = create_animated_focus()
        focus.register("elem-1", tab_index=0, position=(0, 0))

        focus.update_position("elem-1", 50, 50)

        assert focus.transition._positions["elem-1"] == (50, 50)

    def test_on_focus_change_callback(self) -> None:
        """on_focus_change callback is called."""
        changes: list[tuple[str | None, str | None]] = []

        def on_change(old_id: str | None, new_id: str | None) -> None:
            changes.append((old_id, new_id))

        focus = AnimatedFocus.create(on_focus_change=on_change)
        focus.register("elem-1", tab_index=0)
        focus.register("elem-2", tab_index=1)

        focus.focus("elem-1")
        focus.focus("elem-2")
        focus.blur()

        assert len(changes) == 3
        assert changes[0] == (None, "elem-1")
        assert changes[1] == ("elem-1", "elem-2")
        assert changes[2] == ("elem-2", None)

    def test_unregister(self) -> None:
        """Can unregister elements."""
        focus = create_animated_focus()
        focus.register("elem-1", tab_index=0)
        focus.register("elem-2", tab_index=1)

        focus.unregister("elem-1")

        assert focus.focus_state.focusable_count() == 1

    def test_focus_unfocusable_fails(self) -> None:
        """Can't focus non-focusable elements."""
        focus = create_animated_focus()
        focus.register("elem-1", tab_index=0, focusable=False)

        result = focus.focus("elem-1")

        assert result is False
        assert focus.focused_id is None

    def test_style_override(self) -> None:
        """Can override transition style per focus."""
        focus = create_animated_focus(transition_style=FocusTransitionStyle.SPRING)
        focus.register("elem-1", tab_index=0)
        focus.register("elem-2", tab_index=1)

        focus.focus("elem-1")
        focus.focus("elem-2", style=FocusTransitionStyle.NONE)

        # Instant transition should not be transitioning
        assert focus.is_transitioning is False


class TestAnimatedFocusIntegration:
    """Integration tests for AnimatedFocus with animations."""

    def test_complete_focus_lifecycle(self) -> None:
        """Complete focus lifecycle with animations."""
        focus = create_animated_focus(transition_style=FocusTransitionStyle.SPRING)

        # Register elements in a row
        for i in range(3):
            focus.register(f"elem-{i}", tab_index=i, position=(i * 30, 0))

        # Focus first
        focus.focus("elem-0")
        assert focus.focused_id == "elem-0"

        # Move through all elements
        focus.move(FocusDirection.FORWARD)
        assert focus.focused_id == "elem-1"
        assert focus.is_transitioning is True

        # Run animation - wobbly springs take longer to settle
        # After 200 iterations (3.3 seconds), it should be very close to target
        for _ in range(200):
            focus.update(16.67)
            if not focus.is_transitioning:
                break

        # Verify position is very close to target (even if still technically transitioning)
        assert abs(focus.visual_state.ring_x - 30.0) < 0.1

        # Move to last
        focus.move(FocusDirection.FORWARD)
        assert focus.focused_id == "elem-2"

        # Blur
        focus.blur()
        assert focus.focused_id is None

    def test_interrupt_transition(self) -> None:
        """Interrupting a transition creates smooth redirect."""
        focus = create_animated_focus(transition_style=FocusTransitionStyle.SPRING)
        focus.register("elem-0", tab_index=0, position=(0, 0))
        focus.register("elem-1", tab_index=1, position=(50, 0))
        focus.register("elem-2", tab_index=2, position=(100, 0))

        # Start transition to elem-1
        focus.focus("elem-0")
        focus.focus("elem-1")

        # Advance partway
        for _ in range(5):
            focus.update(16.67)

        # Interrupt with new focus
        focus.focus("elem-2")

        # Should smoothly redirect to new target
        assert focus.focused_id == "elem-2"
        assert focus.visual_state.focused_id == "elem-2"

        # Animation should continue
        assert focus.is_transitioning is True
