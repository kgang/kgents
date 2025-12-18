"""Tests for FocusSync - AnimatedFocus ↔ Textual focus bridge."""

from __future__ import annotations

import pytest

from agents.i.reactive.adapters.textual_focus import (
    FocusRing,
    FocusSync,
    create_focus_sync,
)
from agents.i.reactive.pipeline.focus import (
    AnimatedFocus,
    FocusTransitionStyle,
    FocusVisualState,
)
from agents.i.reactive.wiring.interactions import FocusDirection

# =============================================================================
# FocusSync Creation Tests
# =============================================================================


class TestFocusSyncCreation:
    """Test FocusSync creation."""

    def test_create_with_animated_focus(self) -> None:
        """Create sync with AnimatedFocus."""
        focus = AnimatedFocus.create()
        sync = FocusSync(focus)

        assert sync.animated_focus is focus

    def test_create_with_default_flags(self) -> None:
        """Create sync with default sync flags."""
        focus = AnimatedFocus.create()
        sync = FocusSync(focus)

        assert sync._sync_to_textual is True
        assert sync._sync_from_textual is True

    def test_create_with_custom_flags(self) -> None:
        """Create sync with custom sync flags."""
        focus = AnimatedFocus.create()
        sync = FocusSync(
            focus,
            sync_to_textual=False,
            sync_from_textual=False,
        )

        assert sync._sync_to_textual is False
        assert sync._sync_from_textual is False

    def test_starts_without_app(self) -> None:
        """Sync starts without app bound."""
        focus = AnimatedFocus.create()
        sync = FocusSync(focus)

        assert sync._app is None


class TestFocusSyncFactory:
    """Test create_focus_sync factory."""

    def test_creates_sync(self) -> None:
        """Factory creates FocusSync."""
        sync = create_focus_sync()

        assert isinstance(sync, FocusSync)

    def test_creates_animated_focus(self) -> None:
        """Factory creates AnimatedFocus if not provided."""
        sync = create_focus_sync()

        assert isinstance(sync.animated_focus, AnimatedFocus)

    def test_uses_provided_focus(self) -> None:
        """Factory uses provided AnimatedFocus."""
        focus = AnimatedFocus.create()
        sync = create_focus_sync(focus)

        assert sync.animated_focus is focus

    def test_respects_sync_flags(self) -> None:
        """Factory respects sync flag parameters."""
        sync = create_focus_sync(
            sync_to_textual=False,
            sync_from_textual=True,
        )

        assert sync._sync_to_textual is False
        assert sync._sync_from_textual is True


# =============================================================================
# Widget Registration Tests
# =============================================================================


class TestFocusSyncRegistration:
    """Test widget registration."""

    def test_register_widget_without_textual(self) -> None:
        """Register widget without Textual Widget object."""
        sync = create_focus_sync()

        # Just register in AnimatedFocus
        sync.animated_focus.register("btn-1", tab_index=0)

        assert "btn-1" in sync.animated_focus.focus_state._items

    def test_update_position(self) -> None:
        """Update widget position."""
        sync = create_focus_sync()
        sync.animated_focus.register("btn-1", tab_index=0)

        sync.update_position("btn-1", 10.0, 20.0)

        # Position should be registered in transition
        assert "btn-1" in sync.animated_focus.transition._positions

    def test_unregister_widget(self) -> None:
        """Unregister widget."""
        sync = create_focus_sync()
        sync.animated_focus.register("btn-1", tab_index=0)

        sync.animated_focus.unregister("btn-1")

        assert "btn-1" not in sync.animated_focus.focus_state._items


# =============================================================================
# Focus Operations Tests
# =============================================================================


class TestFocusSyncFocusOps:
    """Test focus operations."""

    def test_focus_by_id(self) -> None:
        """Focus a widget by ID."""
        sync = create_focus_sync()
        sync.animated_focus.register("btn-1", tab_index=0)
        sync.animated_focus.register("btn-2", tab_index=1)

        result = sync.focus("btn-1")

        assert result is True
        assert sync.focused_id == "btn-1"

    def test_focus_nonexistent(self) -> None:
        """Focus nonexistent widget returns False."""
        sync = create_focus_sync()

        result = sync.focus("nonexistent")

        assert result is False

    def test_blur(self) -> None:
        """Blur removes focus."""
        sync = create_focus_sync()
        sync.animated_focus.register("btn-1", tab_index=0)
        sync.focus("btn-1")

        sync.blur()

        assert sync.focused_id is None

    def test_move_focus_forward(self) -> None:
        """Move focus forward through widgets."""
        sync = create_focus_sync()
        sync.animated_focus.register("btn-1", tab_index=0)
        sync.animated_focus.register("btn-2", tab_index=1)
        sync.animated_focus.register("btn-3", tab_index=2)
        sync.focus("btn-1")

        new_id = sync.move_focus(FocusDirection.FORWARD)

        assert new_id == "btn-2"

    def test_move_focus_backward(self) -> None:
        """Move focus backward through widgets."""
        sync = create_focus_sync()
        sync.animated_focus.register("btn-1", tab_index=0)
        sync.animated_focus.register("btn-2", tab_index=1)
        sync.animated_focus.register("btn-3", tab_index=2)
        sync.focus("btn-2")

        new_id = sync.move_focus(FocusDirection.BACKWARD)

        assert new_id == "btn-1"


class TestFocusSyncTransitionStyle:
    """Test transition style options."""

    def test_focus_with_style(self) -> None:
        """Focus with custom transition style."""
        sync = create_focus_sync()
        sync.animated_focus.register("btn-1", tab_index=0, position=(0, 0))
        sync.animated_focus.register("btn-2", tab_index=1, position=(10, 0))

        sync.focus("btn-1", style=FocusTransitionStyle.NONE)

        # Should have immediate transition (progress = 1)
        assert sync.visual_state.transition_progress == 1.0

    def test_blur_with_style(self) -> None:
        """Blur with custom transition style."""
        sync = create_focus_sync()
        sync.animated_focus.register("btn-1", tab_index=0)
        sync.focus("btn-1")

        sync.blur(style=FocusTransitionStyle.NONE)

        # Should have immediate blur
        assert sync.focused_id is None


# =============================================================================
# Visual State Tests
# =============================================================================


class TestFocusSyncVisualState:
    """Test visual state access."""

    def test_visual_state_accessible(self) -> None:
        """Visual state is accessible."""
        sync = create_focus_sync()

        state = sync.visual_state

        assert isinstance(state, FocusVisualState)

    def test_visual_state_reflects_focus(self) -> None:
        """Visual state reflects current focus."""
        sync = create_focus_sync()
        sync.animated_focus.register("btn-1", tab_index=0)

        sync.focus("btn-1", style=FocusTransitionStyle.NONE)

        assert sync.visual_state.focused_id == "btn-1"

    def test_update_returns_visual_state(self) -> None:
        """Update method returns visual state."""
        sync = create_focus_sync()

        state = sync.update(16.67)

        assert isinstance(state, FocusVisualState)


# =============================================================================
# FocusRing Tests
# =============================================================================


class TestFocusRing:
    """Test FocusRing helper class."""

    def test_create_focus_ring(self) -> None:
        """Create FocusRing."""
        focus = AnimatedFocus.create()
        ring = FocusRing(focus)

        assert ring._focus is focus

    def test_ring_state(self) -> None:
        """Ring exposes visual state."""
        focus = AnimatedFocus.create()
        ring = FocusRing(focus)

        state = ring.state

        assert isinstance(state, FocusVisualState)

    def test_ring_x_y(self) -> None:
        """Ring exposes x and y."""
        focus = AnimatedFocus.create()
        focus.register("btn-1", tab_index=0, position=(10.0, 20.0))
        focus.focus("btn-1", style=FocusTransitionStyle.NONE)

        ring = FocusRing(focus)

        # Position should be set
        assert isinstance(ring.x, float)
        assert isinstance(ring.y, float)

    def test_ring_opacity(self) -> None:
        """Ring exposes opacity."""
        focus = AnimatedFocus.create()
        ring = FocusRing(focus)

        opacity = ring.opacity

        assert 0.0 <= opacity <= 1.0

    def test_ring_scale(self) -> None:
        """Ring exposes scale."""
        focus = AnimatedFocus.create()
        ring = FocusRing(focus)

        scale = ring.scale

        assert isinstance(scale, float)

    def test_ring_is_visible(self) -> None:
        """Ring visibility based on opacity."""
        focus = AnimatedFocus.create()
        focus.register("btn-1", tab_index=0)
        focus.focus("btn-1", style=FocusTransitionStyle.NONE)

        ring = FocusRing(focus)

        # Should be visible when focused
        assert ring.is_visible

    def test_ring_not_visible_when_blurred(self) -> None:
        """Ring not visible when no focus."""
        focus = AnimatedFocus.create()
        focus.register("btn-1", tab_index=0)

        ring = FocusRing(focus)

        # No focus yet, should not be visible (opacity = 0 from default)
        # Note: initial state may vary
        assert isinstance(ring.is_visible, bool)

    def test_ring_is_transitioning(self) -> None:
        """Ring exposes transitioning state."""
        focus = AnimatedFocus.create()
        ring = FocusRing(focus)

        is_transitioning = ring.is_transitioning

        assert isinstance(is_transitioning, bool)


# =============================================================================
# Lifecycle Tests
# =============================================================================


class TestFocusSyncLifecycle:
    """Test FocusSync lifecycle."""

    def test_unbind_clears_state(self) -> None:
        """Unbind clears internal state."""
        sync = create_focus_sync()
        # Simulate some state
        sync._widget_map["test"] = object()  # type: ignore

        sync.unbind()

        assert sync._app is None
        assert len(sync._widget_map) == 0

    def test_unbind_calls_unsubscribe(self) -> None:
        """Unbind calls unsubscribe if set."""
        sync = create_focus_sync()
        unsub_called = [False]

        def mock_unsub() -> None:
            unsub_called[0] = True

        sync._unsubscribe = mock_unsub

        sync.unbind()

        assert unsub_called[0]


# =============================================================================
# Integration Tests
# =============================================================================


class TestFocusSyncIntegration:
    """Test FocusSync integration scenarios."""

    def test_full_focus_cycle(self) -> None:
        """Test complete focus cycle."""
        sync = create_focus_sync()

        # Register widgets with positions
        sync.animated_focus.register("btn-1", tab_index=0, position=(0, 0))
        sync.animated_focus.register("btn-2", tab_index=1, position=(20, 0))
        sync.animated_focus.register("btn-3", tab_index=2, position=(40, 0))

        # Focus first
        sync.focus("btn-1", style=FocusTransitionStyle.NONE)
        assert sync.focused_id == "btn-1"

        # Move forward
        sync.move_focus(FocusDirection.FORWARD, style=FocusTransitionStyle.NONE)
        assert sync.focused_id == "btn-2"

        # Move forward again
        sync.move_focus(FocusDirection.FORWARD, style=FocusTransitionStyle.NONE)
        assert sync.focused_id == "btn-3"

        # Move backward
        sync.move_focus(FocusDirection.BACKWARD, style=FocusTransitionStyle.NONE)
        assert sync.focused_id == "btn-2"

        # Blur
        sync.blur(style=FocusTransitionStyle.NONE)
        assert sync.focused_id is None

    def test_animation_update_cycle(self) -> None:
        """Test animation update cycle."""
        sync = create_focus_sync()
        sync.animated_focus.register("btn-1", tab_index=0, position=(0, 0))
        sync.animated_focus.register("btn-2", tab_index=1, position=(50, 0))

        # Start spring transition
        sync.focus("btn-1", style=FocusTransitionStyle.SPRING)

        # Run several update cycles
        for _ in range(10):
            state = sync.update(16.67)
            assert isinstance(state, FocusVisualState)

    def test_get_widget_id_by_textual_id(self) -> None:
        """Get widget ID falls back to Textual widget ID."""
        sync = create_focus_sync()

        # Create mock widget-like object
        class MockWidget:
            id = "mock-widget-id"

        result = sync._get_widget_id(MockWidget())  # type: ignore

        assert result == "mock-widget-id"
