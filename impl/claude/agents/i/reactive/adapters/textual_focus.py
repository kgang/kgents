"""
FocusSync: Wire AnimatedFocus to Textual focus system.

Bidirectional sync between kgents AnimatedFocus and Textual's focus:
- AnimatedFocus changes → Textual.focus() called
- Textual Focus events → AnimatedFocus updated

Usage:
    from agents.i.reactive.adapters import FocusSync
    from agents.i.reactive.pipeline.focus import AnimatedFocus

    # Create animated focus
    focus = AnimatedFocus.create()

    # Create sync
    sync = FocusSync(focus)

    # In your App
    class MyApp(App):
        def on_mount(self):
            sync.bind(self)

        def on_focus(self, event):
            sync.on_focus(event)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from agents.i.reactive.pipeline.focus import (
    AnimatedFocus,
    FocusTransitionStyle,
    FocusVisualState,
)
from agents.i.reactive.wiring.interactions import FocusDirection

if TYPE_CHECKING:
    from textual.app import App
    from textual.events import Blur, Focus
    from textual.widget import Widget


class FocusSync:
    """
    Syncs AnimatedFocus with Textual focus system.

    Provides bidirectional binding:
    - When AnimatedFocus.focus() is called, the corresponding Textual widget gets focus
    - When Textual focus changes, AnimatedFocus is updated

    Also provides access to AnimatedFocus visual state for custom focus rendering
    (ring position, opacity, scale for spring animations).

    Example:
        focus = AnimatedFocus.create()

        # Register widgets with positions
        focus.register("btn-1", tab_index=0, position=(0, 0))
        focus.register("btn-2", tab_index=1, position=(10, 0))

        sync = FocusSync(focus)

        class MyApp(App):
            def on_mount(self):
                sync.bind(self)

            def on_key(self, event):
                if event.key == "tab":
                    sync.move_focus(FocusDirection.FORWARD)
    """

    def __init__(
        self,
        animated_focus: AnimatedFocus,
        *,
        sync_to_textual: bool = True,
        sync_from_textual: bool = True,
    ) -> None:
        """
        Create FocusSync.

        Args:
            animated_focus: AnimatedFocus instance to sync
            sync_to_textual: Whether to update Textual focus when AnimatedFocus changes
            sync_from_textual: Whether to update AnimatedFocus when Textual focus changes
        """
        self._focus = animated_focus
        self._app: App | None = None
        self._widget_map: dict[str, Widget] = {}
        self._sync_to_textual = sync_to_textual
        self._sync_from_textual = sync_from_textual
        self._unsubscribe: Callable[[], None] | None = None
        self._updating = False  # Prevent recursive updates

    @property
    def animated_focus(self) -> AnimatedFocus:
        """Get the AnimatedFocus instance."""
        return self._focus

    @property
    def visual_state(self) -> FocusVisualState:
        """Get current visual state for rendering."""
        return self._focus.visual_state

    @property
    def focused_id(self) -> str | None:
        """Get currently focused element ID."""
        return self._focus.focused_id

    def bind(self, app: App) -> Callable[[], None]:
        """
        Bind to a Textual App.

        Args:
            app: Textual App to bind to

        Returns:
            Unsubscribe function
        """
        self._app = app

        # Subscribe to AnimatedFocus changes
        if self._sync_to_textual:
            self._unsubscribe = self._focus.transition.signal.subscribe(
                self._on_animated_focus_change
            )

        return lambda: self.unbind()

    def unbind(self) -> None:
        """Unbind from app."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None
        self._app = None
        self._widget_map.clear()

    def register_widget(
        self,
        widget_id: str,
        widget: Widget,
        tab_index: int = 0,
        position: tuple[float, float] | None = None,
    ) -> None:
        """
        Register a Textual widget for focus sync.

        Args:
            widget_id: Unique identifier (used in AnimatedFocus)
            widget: Textual Widget instance
            tab_index: Position in tab order
            position: Screen position for slide/spring animations
        """
        self._widget_map[widget_id] = widget
        self._focus.register(
            widget_id,
            tab_index=tab_index,
            focusable=widget.can_focus,
            position=position,
        )

    def unregister_widget(self, widget_id: str) -> None:
        """Remove a widget from focus sync."""
        if widget_id in self._widget_map:
            del self._widget_map[widget_id]
        self._focus.unregister(widget_id)

    def update_position(self, widget_id: str, x: float, y: float) -> None:
        """Update a widget's position for animations."""
        self._focus.update_position(widget_id, x, y)

    def focus(
        self,
        widget_id: str,
        style: FocusTransitionStyle | None = None,
    ) -> bool:
        """
        Focus a widget by ID.

        Args:
            widget_id: Widget to focus
            style: Optional transition style override

        Returns:
            True if focus changed
        """
        return self._focus.focus(widget_id, style)

    def blur(self, style: FocusTransitionStyle | None = None) -> None:
        """Remove focus with optional transition style."""
        self._focus.blur(style)

    def move_focus(
        self,
        direction: FocusDirection,
        style: FocusTransitionStyle | None = None,
    ) -> str | None:
        """
        Move focus in direction.

        Args:
            direction: FORWARD or BACKWARD
            style: Optional transition style

        Returns:
            New focused element ID, or None
        """
        return self._focus.move(direction, style)

    def on_focus(self, event: Focus) -> None:
        """
        Handle Textual Focus event.

        Call this from your App's on_focus method to sync
        Textual focus → AnimatedFocus.

        Args:
            event: Textual Focus event
        """
        if not self._sync_from_textual or self._updating:
            return

        # Find widget ID from the focused widget
        widget = event.widget
        widget_id = self._get_widget_id(widget)

        if widget_id:
            self._updating = True
            try:
                self._focus.focus(widget_id)
            finally:
                self._updating = False

    def on_blur(self, event: Blur) -> None:
        """
        Handle Textual Blur event.

        Call this from your App's on_blur method.

        Args:
            event: Textual Blur event
        """
        if not self._sync_from_textual or self._updating:
            return

        # Only blur if no new focus is pending
        # (Textual fires blur before focus)
        pass  # AnimatedFocus handles this via focus() calls

    def _on_animated_focus_change(self, state: FocusVisualState) -> None:
        """Handle AnimatedFocus visual state changes."""
        if not self._sync_to_textual or self._updating or not self._app:
            return

        focused_id = state.focused_id
        if focused_id and focused_id in self._widget_map:
            widget = self._widget_map[focused_id]
            self._updating = True
            try:
                widget.focus()
            finally:
                self._updating = False

    def _get_widget_id(self, widget: Widget) -> str | None:
        """Get widget ID from a Textual Widget."""
        # Check our map (reverse lookup)
        for wid, w in self._widget_map.items():
            if w is widget:
                return wid

        # Try widget's id attribute
        if widget.id:
            return widget.id

        return None

    def update(self, delta_ms: float) -> FocusVisualState:
        """
        Update focus animations.

        Call this on each frame for smooth transitions.

        Args:
            delta_ms: Time since last update

        Returns:
            Current visual state
        """
        return self._focus.update(delta_ms)


class FocusRing:
    """
    Visual focus ring using AnimatedFocus spring values.

    Provides coordinates and opacity for rendering a custom focus indicator
    that smoothly animates between focused elements.

    Example:
        ring = FocusRing(sync.animated_focus)

        def render(self):
            state = ring.state
            if state.ring_opacity > 0.1:
                # Draw ring at (state.ring_x, state.ring_y)
                # with opacity state.ring_opacity
                # and scale state.ring_scale
                pass
    """

    def __init__(self, animated_focus: AnimatedFocus) -> None:
        self._focus = animated_focus

    @property
    def state(self) -> FocusVisualState:
        """Get current visual state."""
        return self._focus.visual_state

    @property
    def x(self) -> float:
        """Ring X position."""
        return self._focus.visual_state.ring_x

    @property
    def y(self) -> float:
        """Ring Y position."""
        return self._focus.visual_state.ring_y

    @property
    def opacity(self) -> float:
        """Ring opacity (0-1)."""
        return self._focus.visual_state.ring_opacity

    @property
    def scale(self) -> float:
        """Ring scale (for pulse effect)."""
        return self._focus.visual_state.ring_scale

    @property
    def is_visible(self) -> bool:
        """Whether ring should be visible."""
        return self._focus.visual_state.ring_opacity > 0.1

    @property
    def is_transitioning(self) -> bool:
        """Whether ring is animating."""
        return self._focus.is_transitioning


def create_focus_sync(
    animated_focus: AnimatedFocus | None = None,
    *,
    sync_to_textual: bool = True,
    sync_from_textual: bool = True,
) -> FocusSync:
    """
    Create a FocusSync instance.

    Args:
        animated_focus: AnimatedFocus to use (creates new if None)
        sync_to_textual: Sync kgents → Textual focus
        sync_from_textual: Sync Textual → kgents focus

    Returns:
        Configured FocusSync
    """
    if animated_focus is None:
        animated_focus = AnimatedFocus.create()

    return FocusSync(
        animated_focus,
        sync_to_textual=sync_to_textual,
        sync_from_textual=sync_from_textual,
    )
