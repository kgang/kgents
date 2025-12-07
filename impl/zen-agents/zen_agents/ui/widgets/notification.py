"""Notification widgets for zen-agents UI."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual.timer import Timer


class ZenNotification(Static):
    """A single notification toast."""

    DEFAULT_CSS = """
    ZenNotification {
        width: auto;
        height: 3;
        padding: 0 2;
        margin-left: 2;
        content-align: center middle;
        text-align: center;
        background: $surface;
        border: round $surface-lighten-1;
        color: $text-muted;
    }
    """

    def __init__(self, message: str, severity: str = "success", timeout: float = 3.0) -> None:
        super().__init__(message)
        self.severity = severity
        self.timeout = timeout
        self._timer: Timer | None = None
        self.add_class(f"-{severity}")

    def on_mount(self) -> None:
        """Start dismiss timer."""
        self._timer = self.set_timer(self.timeout, self._start_dismiss)

    def _start_dismiss(self) -> None:
        """Begin dismiss animation."""
        self.add_class("-dismissing")
        self.set_timer(0.3, self.remove)


class ZenNotificationRack(Container):
    """Container for stacked notifications."""

    DEFAULT_CSS = """
    ZenNotificationRack {
        height: auto;
        width: 100%;
        align-horizontal: left;
    }
    """

    def compose(self) -> ComposeResult:
        return
        yield  # Empty by default

    def show(self, message: str, severity: str = "success", timeout: float = 3.0) -> None:
        """Show a new notification."""
        notification = ZenNotification(message, severity, timeout)
        self.mount(notification)
