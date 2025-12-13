"""
ErrorOverlay - Display kind error messages with recovery hints.

Philosophy: "Errors are learning moments, not failures."
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from ...theme.dashboard import THEME

if TYPE_CHECKING:
    pass


class ErrorOverlay(ModalScreen[None]):
    """
    Error overlay with kind messaging and recovery hints.

    Shows:
    - What went wrong (friendly description)
    - Why it might have happened
    - What to try next (recovery actions)

    Always closes with Escape or Enter.
    """

    CSS = f"""
    ErrorOverlay {{
        align: center middle;
    }}

    ErrorOverlay #error-container {{
        width: 70;
        height: auto;
        max-height: 80%;
        border: thick {THEME.error};
        background: {THEME.background};
        padding: 2;
    }}

    ErrorOverlay #error-icon {{
        height: 1;
        text-align: center;
        color: {THEME.error};
        text-style: bold;
        margin-bottom: 1;
    }}

    ErrorOverlay #error-title {{
        height: 1;
        text-align: center;
        color: {THEME.text_primary};
        text-style: bold;
        margin-bottom: 2;
    }}

    ErrorOverlay #error-message {{
        height: auto;
        color: {THEME.text_secondary};
        margin-bottom: 2;
    }}

    ErrorOverlay #error-details {{
        height: auto;
        color: {THEME.text_muted};
        border: round {THEME.border};
        padding: 1;
        margin-bottom: 2;
    }}

    ErrorOverlay #recovery-hints {{
        height: auto;
        color: {THEME.info};
        margin-bottom: 1;
    }}

    ErrorOverlay #footer {{
        height: 1;
        text-align: center;
        color: {THEME.text_muted};
        border-top: solid {THEME.border};
        padding-top: 1;
    }}

    ErrorOverlay .hint-item {{
        color: {THEME.success};
    }}
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close", show=True),
        Binding("enter", "dismiss", "Close", show=False),
    ]

    def __init__(
        self,
        title: str = "Something went wrong",
        message: str = "An unexpected error occurred.",
        details: str | None = None,
        recovery_hints: list[str] | None = None,
        name: str | None = None,
    ) -> None:
        """
        Initialize the error overlay.

        Args:
            title: Error title (friendly, non-technical)
            message: What went wrong (user-facing explanation)
            details: Technical details (exception message, stack trace, etc.)
            recovery_hints: List of suggested recovery actions
            name: Widget name
        """
        super().__init__(name=name)
        self.title_text = title
        self.message_text = message
        self.details_text = details
        self.recovery_hints = recovery_hints or []

    def compose(self) -> ComposeResult:
        """Compose the error overlay."""
        with Container(id="error-container"):
            with Vertical():
                # Error icon
                yield Static("⚠", id="error-icon")

                # Title
                yield Static(self.title_text, id="error-title")

                # Message
                yield Static(self.message_text, id="error-message")

                # Technical details (if provided)
                if self.details_text:
                    details_widget = Static(id="error-details")
                    details_widget.update(f"Technical details:\n{self.details_text}")
                    yield details_widget

                # Recovery hints (if provided)
                if self.recovery_hints:
                    hints_widget = Static(id="recovery-hints")
                    hints_text = "What to try:\n"
                    for i, hint in enumerate(self.recovery_hints, 1):
                        hints_text += f"  {i}. {hint}\n"
                    hints_widget.update(hints_text.strip())
                    yield hints_widget

                # Footer
                yield Static("Press [Escape] or [Enter] to close", id="footer")

    async def action_dismiss(self, result: None = None) -> None:
        """Dismiss the overlay."""
        self.dismiss()


def friendly_error_message(exception: Exception) -> tuple[str, str, list[str]]:
    """
    Convert an exception to friendly error messaging.

    Returns:
        (title, message, recovery_hints)
    """
    exception_type = type(exception).__name__

    # Common error patterns with friendly messaging
    if "FileNotFoundError" in exception_type:
        return (
            "File not found",
            "The system couldn't find a file it was looking for.",
            [
                "Check that the file exists",
                "Verify the path is correct",
                "Try refreshing the view (press 'r')",
            ],
        )

    elif "ConnectionError" in exception_type or "Timeout" in exception_type:
        return (
            "Connection issue",
            "Couldn't connect to the required service.",
            [
                "Check your network connection",
                "Verify the service is running",
                "Try again in a moment",
            ],
        )

    elif "PermissionError" in exception_type:
        return (
            "Permission denied",
            "You don't have permission to access this resource.",
            [
                "Check file permissions",
                "Ensure you're running with appropriate privileges",
                "Contact your administrator if needed",
            ],
        )

    elif "ValueError" in exception_type or "TypeError" in exception_type:
        return (
            "Invalid data",
            "The system received data it couldn't understand.",
            [
                "Check your input",
                "Try refreshing the data (press 'r')",
                "Report this if it persists",
            ],
        )

    else:
        # Generic fallback
        return (
            "Unexpected error",
            "Something unexpected happened.",
            [
                "Try refreshing (press 'r')",
                "Check the logs for details",
                "Report this if it persists",
            ],
        )


__all__ = ["ErrorOverlay", "friendly_error_message"]
