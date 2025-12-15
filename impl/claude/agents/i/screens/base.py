"""Base screen classes for kgents dashboard with key passthrough.

This module provides the foundation for all dashboard screens, ensuring that
global navigation keys (1-6, tab, q, etc.) always reach the parent DashboardApp
even when focus is on nested widgets.

The key insight: Screen subclasses should NOT stop propagation for navigation keys.
By not calling event.stop() on PASSTHROUGH_KEYS, these events bubble up to the App
layer where they can be handled consistently.
"""

from typing import ClassVar, Generic, TypeVar

from textual.app import ComposeResult
from textual.events import Key
from textual.screen import ModalScreen, Screen

# Type variable for modal screen results
T = TypeVar("T")


class KgentsScreen(Screen[object]):
    """Base screen with key passthrough for global navigation.

    All dashboard screens should inherit from this class to ensure consistent
    keyboard navigation. The PASSTHROUGH_KEYS set defines which keys should
    always bubble up to the parent App for global handling.

    Subclasses can override on_key() for screen-specific behavior, but should
    call super().on_key(event) to preserve passthrough behavior.

    Attributes:
        PASSTHROUGH_KEYS: Keys that always bubble to parent App
        ANCHOR: Visual element name for smooth transitions (set by subclasses)
        ANCHOR_MORPHS_TO: Mapping of screen transitions to anchor targets

    Example:
        class CockpitScreen(KgentsScreen):
            ANCHOR = "agent_status_panel"
            ANCHOR_MORPHS_TO = {"flux": "stream_visualizer"}

            def on_key(self, event: Key) -> None:
                if event.key == "r":
                    self.refresh_data()
                    return
                super().on_key(event)  # Preserve passthrough
    """

    # Keys that should ALWAYS bubble to parent App
    PASSTHROUGH_KEYS: ClassVar[set[str]] = {
        # Screen navigation (number keys)
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        # Screen cycling
        "tab",
        # Special screen shortcuts
        "d",  # Debugger
        "m",  # Memory map
        # Global commands
        "question_mark",  # Help (? key)
        "q",  # Quit
    }

    # Anchor element for gentle eye transitions
    # Subclasses should set this to identify the "visual center" of the screen
    ANCHOR: ClassVar[str] = ""

    # Mapping of screen transitions to their target anchors
    # e.g., {"flux": "stream_panel", "debugger": "trace_view"}
    ANCHOR_MORPHS_TO: ClassVar[dict[str, str]] = {}

    def on_key(self, event: Key) -> None:
        """Handle key events with passthrough for global navigation.

        This method ensures that navigation keys always reach the parent App.
        By NOT calling event.stop() on PASSTHROUGH_KEYS, we allow these events
        to bubble up naturally.

        Args:
            event: The key event to handle
        """
        if event.key in self.PASSTHROUGH_KEYS:
            # Don't stop propagation - let it bubble UP to App
            # This is the critical behavior: we simply return without
            # calling event.stop() or event.prevent_default()
            return

        # For other keys, delegate to parent if it has on_key handler
        # Screen class uses message system, not explicit on_key
        pass

    def get_anchor_for_transition(self, target_screen: str) -> str:
        """Get the visual anchor point for transitioning to another screen.

        This supports smooth visual transitions by identifying which UI element
        should "morph" into the target screen's focal point.

        Args:
            target_screen: Name of the screen being transitioned to

        Returns:
            The anchor element ID, or empty string if no specific anchor
        """
        return self.ANCHOR_MORPHS_TO.get(target_screen, "")

    @classmethod
    def get_anchor(cls) -> str:
        """Get this screen's visual anchor point.

        Returns:
            The anchor element ID for this screen
        """
        return cls.ANCHOR


class KgentsModalScreen(ModalScreen[T], Generic[T]):
    """Base modal screen with escape binding and typed results.

    Modal screens are overlays that capture focus and return a result when
    dismissed. This base class provides:
    - Escape key binding for cancellation
    - Type-safe result handling
    - Auto-dismiss with configurable delay

    Type parameter:
        T: The type of result this modal returns (use None for no result)

    Attributes:
        AUTO_DISMISS_DELAY: Default delay in seconds before auto-dismiss

    Example:
        class ConfirmDialog(KgentsModalScreen[bool]):
            AUTO_DISMISS_DELAY = 0.3

            def compose(self) -> ComposeResult:
                yield Label("Are you sure?")
                yield Button("Yes", id="yes")
                yield Button("No", id="no")

            def on_button_pressed(self, event: Button.Pressed) -> None:
                result = event.button.id == "yes"
                self.dismiss_after(result)
    """

    # Default delay in seconds before auto-dismiss
    # Set to 0.0 to disable auto-dismiss delay
    AUTO_DISMISS_DELAY: ClassVar[float] = 0.0

    BINDINGS = [
        ("escape", "dismiss_modal", "Cancel"),
    ]

    def action_dismiss_modal(self) -> None:
        """Action handler for escape key - dismisses with None result.

        This provides a consistent way to cancel any modal dialog.
        Subclasses can override to customize cancellation behavior.
        """
        self.dismiss(None)

    def dismiss_after(self, result: T, delay: float | None = None) -> None:
        """Auto-dismiss with visual feedback delay.

        This allows the user to see visual feedback (like a button press or
        status update) before the modal disappears. Useful for confirmation
        dialogs and short-lived notifications.

        Args:
            result: The result to return when dismissing
            delay: Delay in seconds before dismiss (uses AUTO_DISMISS_DELAY if None)

        Example:
            def on_button_pressed(self, event: Button.Pressed) -> None:
                # Flash the button before dismissing
                event.button.add_class("pressed")
                self.dismiss_after(True, delay=0.3)
        """
        if delay is None:
            delay = self.AUTO_DISMISS_DELAY

        if delay <= 0:
            # Immediate dismissal
            self.dismiss(result)
        else:
            # Delayed dismissal for visual feedback
            self.set_timer(delay, lambda: self.dismiss(result))

    def dismiss_immediate(self, result: T) -> None:
        """Dismiss immediately without delay.

        Convenience method for cases where you want to be explicit about
        immediate dismissal regardless of AUTO_DISMISS_DELAY setting.

        Args:
            result: The result to return when dismissing
        """
        self.dismiss(result)
