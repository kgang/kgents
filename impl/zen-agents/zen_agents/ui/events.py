"""Custom Textual messages for zen-agents UI."""

from dataclasses import dataclass
from textual.message import Message

from ..types import Session


class SessionSelected(Message):
    """Posted when a session is selected in the list."""

    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session


@dataclass
class NotificationRequest(Message):
    """Request to show a notification."""

    message: str
    severity: str = "success"  # success, warning, error
    timeout: float = 3.0
