"""SessionList widget for displaying sessions with selection."""

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static

from ...types import Session, SessionState, SessionType
from ..events import SessionSelected


class SessionListItem(Static):
    """A single session row in the list."""

    DEFAULT_CSS = """
    SessionListItem {
        width: 100%;
        height: 1;
        padding: 0 1;
    }

    SessionListItem.selected {
        background: $surface-lighten-1;
    }

    SessionListItem.grabbed {
        background: $primary-darken-3;
    }

    SessionListItem.running {
        color: $success;
    }

    SessionListItem.completed {
        color: $text-muted;
    }

    SessionListItem.paused {
        color: $text;
    }

    SessionListItem.failed, SessionListItem.unknown {
        color: $text-disabled;
    }
    """

    def __init__(self, session: Session, selected: bool = False, grabbed: bool = False) -> None:
        super().__init__()
        self.session = session
        if selected:
            self.add_class("selected")
        if grabbed:
            self.add_class("grabbed")
        self.add_class(session.state.value)

    def render(self) -> str:
        s = self.session
        # Glyph based on state
        glyphs = {
            SessionState.CREATING: "...",
            SessionState.RUNNING: ">>>",
            SessionState.PAUSED: "||",
            SessionState.COMPLETED: "ok",
            SessionState.FAILED: "xx",
            SessionState.UNKNOWN: "??",
        }
        glyph = glyphs.get(s.state, "?")

        # Type prefix for non-Claude sessions
        type_prefixes = {
            SessionType.SHELL: "sh:",
            SessionType.CODEX: "cx:",
            SessionType.GEMINI: "gm:",
            SessionType.CUSTOM: "c:",
        }
        prefix = type_prefixes.get(s.config.session_type, "")
        name = f"{prefix}{s.config.name}" if prefix else s.config.name

        return f"{glyph}  {name:<32}"


class SessionList(Static, can_focus=False):
    """List of all sessions with keyboard navigation.

    Non-focusable - navigation handled by MainScreen keybindings.
    """

    sessions: reactive[list[Session]] = reactive(list, recompose=True)
    selected_index: reactive[int] = reactive(0)
    grab_mode: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    SessionList {
        width: 100%;
        height: 100%;
        border: none;
        padding: 0;
    }

    SessionList .empty-message {
        content-align: center middle;
        color: $text-disabled;
        height: 100%;
    }

    SessionList .title {
        height: 1;
        color: $text-disabled;
        text-align: left;
        padding: 0 1;
        margin-bottom: 1;
    }

    SessionList .title.grab-mode {
        color: $primary;
    }
    """

    def compose(self) -> ComposeResult:
        if not self.sessions:
            yield Static("\n\n\n\n      ...\n\n    empty\n\n    n  new session", classes="empty-message")
            return

        title_classes = "title grab-mode" if self.grab_mode else "title"
        title_text = "= reorder" if self.grab_mode else "sessions"
        yield Static(title_text, classes=title_classes)
        for i, session in enumerate(self.sessions):
            is_selected = i == self.selected_index
            is_grabbed = is_selected and self.grab_mode
            yield SessionListItem(session, selected=is_selected, grabbed=is_grabbed)

    def watch_selected_index(self, index: int) -> None:
        """Emit selection event when index changes."""
        if self.sessions and 0 <= index < len(self.sessions):
            self.post_message(SessionSelected(self.sessions[index]))

    def move_down(self) -> None:
        """Move selection down, or move session down if in grab mode."""
        if not self.sessions:
            return
        if self.grab_mode:
            self._move_session_down()
        else:
            self.selected_index = (self.selected_index + 1) % len(self.sessions)
        self.refresh(recompose=True)

    def move_up(self) -> None:
        """Move selection up, or move session up if in grab mode."""
        if not self.sessions:
            return
        if self.grab_mode:
            self._move_session_up()
        else:
            self.selected_index = (self.selected_index - 1) % len(self.sessions)
        self.refresh(recompose=True)

    def _move_session_down(self) -> None:
        """Move selected session down in the list."""
        if self.selected_index >= len(self.sessions) - 1:
            return
        sessions = list(self.sessions)
        i = self.selected_index
        sessions[i], sessions[i + 1] = sessions[i + 1], sessions[i]
        self.sessions = sessions
        self.selected_index = i + 1

    def _move_session_up(self) -> None:
        """Move selected session up in the list."""
        if self.selected_index <= 0:
            return
        sessions = list(self.sessions)
        i = self.selected_index
        sessions[i], sessions[i - 1] = sessions[i - 1], sessions[i]
        self.sessions = sessions
        self.selected_index = i - 1

    def toggle_grab_mode(self) -> bool:
        """Toggle grab mode for reordering. Returns new grab state."""
        self.grab_mode = not self.grab_mode
        self.refresh(recompose=True)
        return self.grab_mode

    def exit_grab_mode(self) -> None:
        """Exit grab mode without toggling."""
        if self.grab_mode:
            self.grab_mode = False
            self.refresh(recompose=True)

    def get_selected(self) -> Session | None:
        """Get the currently selected session."""
        if self.sessions and 0 <= self.selected_index < len(self.sessions):
            return self.sessions[self.selected_index]
        return None

    def get_session_order(self) -> list[str]:
        """Get session IDs in current display order."""
        return [s.id for s in self.sessions]

    def update_sessions(self, sessions: list[Session]) -> None:
        """Update the session list."""
        self.sessions = sessions
        if self.selected_index >= len(sessions):
            self.selected_index = max(0, len(sessions) - 1)
        self.refresh(recompose=True)
