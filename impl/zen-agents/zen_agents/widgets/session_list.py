"""
Session List Widget - Textual widget for displaying sessions.

A contemplative list of active AI sessions.
"""

from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView, Static

from ..models import Session, SessionState, SessionType


# State indicators with contemplative aesthetic
STATE_ICONS = {
    SessionState.RUNNING: "●",    # Solid circle - active
    SessionState.COMPLETED: "○",  # Empty circle - finished
    SessionState.PAUSED: "◐",     # Half circle - paused
    SessionState.FAILED: "✗",     # X - failed
    SessionState.KILLED: "◌",     # Dotted circle - terminated
}

STATE_COLORS = {
    SessionState.RUNNING: "green",
    SessionState.COMPLETED: "blue",
    SessionState.PAUSED: "yellow",
    SessionState.FAILED: "red",
    SessionState.KILLED: "dim",
}

TYPE_ICONS = {
    # Provider backends
    SessionType.CLAUDE: "🤖",
    SessionType.CODEX: "💻",
    SessionType.GEMINI: "✨",
    SessionType.SHELL: "⌘",
    SessionType.OPENROUTER: "🌐",
    # LLM-backed kgents
    SessionType.ROBIN: "🐦",      # Robin - scientific companion
    SessionType.CREATIVITY: "🎨",  # Creativity coach
    SessionType.HYPOTHESIS: "🔬",  # Hypothesis engine
    SessionType.KGENT: "👤",       # Kent simulacra
}


class SessionItem(Static):
    """A single session in the list."""

    DEFAULT_CSS = """
    SessionItem {
        height: 3;
        padding: 0 1;
        border: solid $surface;
        margin-bottom: 1;
    }

    SessionItem:hover {
        background: $surface;
    }

    SessionItem.--selected {
        border: solid $accent;
        background: $surface;
    }

    SessionItem .session-name {
        text-style: bold;
    }

    SessionItem .session-state-running {
        color: $success;
    }

    SessionItem .session-state-completed {
        color: $primary;
    }

    SessionItem .session-state-paused {
        color: $warning;
    }

    SessionItem .session-state-failed {
        color: $error;
    }

    SessionItem .session-state-killed {
        color: $text-muted;
    }

    SessionItem .session-type {
        color: $text-muted;
    }

    SessionItem .session-time {
        color: $text-muted;
        text-align: right;
    }
    """

    class Selected(Message):
        """Emitted when this item is selected."""
        def __init__(self, session: Session) -> None:
            self.session = session
            super().__init__()

    def __init__(self, session: Session, **kwargs) -> None:
        super().__init__(**kwargs)
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def compose(self) -> ComposeResult:
        """Compose the session item."""
        session = self._session
        state_icon = STATE_ICONS.get(session.state, "?")
        type_icon = TYPE_ICONS.get(session.session_type, "?")
        state_class = f"session-state-{session.state.value}"

        # Format time
        time_str = session.created_at.strftime("%H:%M")

        yield Label(
            f"{state_icon} {session.name}",
            classes=f"session-name {state_class}",
        )
        yield Label(
            f"  {type_icon} {session.session_type.value} │ {time_str}",
            classes="session-type",
        )

    def update_session(self, session: Session) -> None:
        """Update the session data and refresh display."""
        self._session = session
        self.refresh()

    def on_click(self) -> None:
        """Handle click - emit selected message."""
        self.post_message(self.Selected(self._session))


class SessionList(VerticalScroll):
    """
    List of sessions with selection.

    A contemplative view of all active AI sessions.
    """

    DEFAULT_CSS = """
    SessionList {
        height: 100%;
        padding: 1;
    }

    SessionList > .empty-message {
        color: $text-muted;
        text-align: center;
        padding: 2;
    }
    """

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("enter", "select", "Select"),
        Binding("d", "delete", "Kill"),
        Binding("r", "revive", "Revive"),
    ]

    class SessionSelected(Message):
        """Emitted when a session is selected."""
        def __init__(self, session: Session) -> None:
            self.session = session
            super().__init__()

    class SessionAction(Message):
        """Emitted when an action is requested on a session."""
        def __init__(self, session: Session, action: str) -> None:
            self.session = session
            self.action = action
            super().__init__()

    selected_index: reactive[int] = reactive(0)
    sessions: reactive[list[Session]] = reactive([])

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._items: list[SessionItem] = []

    def compose(self) -> ComposeResult:
        """Compose the session list."""
        if not self.sessions:
            yield Label(
                "No sessions. Press 'n' to create one.",
                classes="empty-message",
            )

    def watch_sessions(self, sessions: list[Session]) -> None:
        """React to sessions changes."""
        self._rebuild_list()

    def _rebuild_list(self) -> None:
        """Rebuild the list of session items."""
        # Remove existing items
        for item in self._items:
            item.remove()
        self._items.clear()

        # Clear the container
        self.remove_children()

        if not self.sessions:
            self.mount(Label(
                "No sessions. Press 'n' to create one.",
                classes="empty-message",
            ))
            return

        # Create new items
        for i, session in enumerate(self.sessions):
            item = SessionItem(session)
            if i == self.selected_index:
                item.add_class("--selected")
            self._items.append(item)
            self.mount(item)

    def _update_selection(self) -> None:
        """Update selection highlight."""
        for i, item in enumerate(self._items):
            if i == self.selected_index:
                item.add_class("--selected")
            else:
                item.remove_class("--selected")

    def action_cursor_down(self) -> None:
        """Move selection down."""
        if self._items:
            self.selected_index = min(
                self.selected_index + 1,
                len(self._items) - 1,
            )
            self._update_selection()

    def action_cursor_up(self) -> None:
        """Move selection up."""
        if self._items:
            self.selected_index = max(self.selected_index - 1, 0)
            self._update_selection()

    def action_select(self) -> None:
        """Select the current session."""
        if self._items and 0 <= self.selected_index < len(self._items):
            session = self._items[self.selected_index].session
            self.post_message(self.SessionSelected(session))

    def action_delete(self) -> None:
        """Request to delete the current session."""
        if self._items and 0 <= self.selected_index < len(self._items):
            session = self._items[self.selected_index].session
            self.post_message(self.SessionAction(session, "kill"))

    def action_revive(self) -> None:
        """Request to revive the current session."""
        if self._items and 0 <= self.selected_index < len(self._items):
            session = self._items[self.selected_index].session
            if session.state != SessionState.RUNNING:
                self.post_message(self.SessionAction(session, "revive"))

    def on_session_item_selected(self, event: SessionItem.Selected) -> None:
        """Handle session item selection."""
        # Update selected index
        for i, item in enumerate(self._items):
            if item.session.id == event.session.id:
                self.selected_index = i
                break
        self._update_selection()
        self.post_message(self.SessionSelected(event.session))

    def update_session(self, session: Session) -> None:
        """Update a session in the list."""
        for item in self._items:
            if item.session.id == session.id:
                item.update_session(session)
                break

    @property
    def selected_session(self) -> Optional[Session]:
        """Get the currently selected session."""
        if self._items and 0 <= self.selected_index < len(self._items):
            return self._items[self.selected_index].session
        return None
