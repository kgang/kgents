"""SessionList widget for displaying sessions with selection."""

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, Input

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
    Supports search/filter mode with / key.
    """

    sessions: reactive[list[Session]] = reactive(list, recompose=True)
    selected_index: reactive[int] = reactive(0)
    grab_mode: reactive[bool] = reactive(False)
    search_mode: reactive[bool] = reactive(False)
    search_query: reactive[str] = reactive("")
    type_filter: reactive[SessionType | None] = reactive(None)

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

    SessionList .title.search-mode {
        color: $warning;
    }

    SessionList .title.filter-mode {
        color: $success;
    }

    SessionList #search-input {
        height: 1;
        border: none;
        background: transparent;
        padding: 0 1;
        margin-bottom: 1;
    }

    SessionList #search-input:focus {
        border: none;
    }
    """

    def compose(self) -> ComposeResult:
        filtered = self._get_filtered_sessions()

        if not self.sessions:
            yield Static("\n\n\n\n      ...\n\n    empty\n\n    n  new session", classes="empty-message")
            return

        # Title with mode indicator
        if self.search_mode:
            title_classes = "title search-mode"
            title_text = "/ search"
        elif self.grab_mode:
            title_classes = "title grab-mode"
            title_text = "= reorder"
        elif self.type_filter:
            title_classes = "title filter-mode"
            title_text = f"[{self.type_filter.value}]"
        elif self.search_query:
            title_classes = "title search-mode"
            title_text = f"/{self.search_query}"
        else:
            title_classes = "title"
            title_text = "sessions"

        yield Static(title_text, classes=title_classes)

        # Search input when in search mode
        if self.search_mode:
            yield Input(placeholder="type to filter...", id="search-input", value=self.search_query)

        # Show filtered sessions
        if not filtered:
            yield Static("  [dim]no matches[/dim]", classes="empty-message")
        else:
            for i, session in enumerate(filtered):
                is_selected = i == self.selected_index
                is_grabbed = is_selected and self.grab_mode
                yield SessionListItem(session, selected=is_selected, grabbed=is_grabbed)

    def _get_filtered_sessions(self) -> list[Session]:
        """Get sessions filtered by current search/type filter."""
        result = self.sessions

        # Type filter
        if self.type_filter:
            result = [s for s in result if s.config.session_type == self.type_filter]

        # Search query filter
        if self.search_query:
            query = self.search_query.lower()
            result = [s for s in result if query in s.config.name.lower()]

        return result

    def watch_selected_index(self, index: int) -> None:
        """Emit selection event when index changes."""
        filtered = self._get_filtered_sessions()
        if filtered and 0 <= index < len(filtered):
            self.post_message(SessionSelected(filtered[index]))

    def move_down(self) -> None:
        """Move selection down, or move session down if in grab mode."""
        filtered = self._get_filtered_sessions()
        if not filtered:
            return
        if self.grab_mode:
            self._move_session_down()
        else:
            self.selected_index = (self.selected_index + 1) % len(filtered)
        self.refresh(recompose=True)

    def move_up(self) -> None:
        """Move selection up, or move session up if in grab mode."""
        filtered = self._get_filtered_sessions()
        if not filtered:
            return
        if self.grab_mode:
            self._move_session_up()
        else:
            self.selected_index = (self.selected_index - 1) % len(filtered)
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

    def enter_search_mode(self) -> None:
        """Enter search/filter mode."""
        self.search_mode = True
        self.refresh(recompose=True)
        # Focus the search input after recompose
        self.call_after_refresh(self._focus_search_input)

    def _focus_search_input(self) -> None:
        """Focus the search input widget."""
        try:
            search_input = self.query_one("#search-input", Input)
            search_input.focus()
        except Exception:
            pass

    def exit_search_mode(self) -> None:
        """Exit search mode, keeping the filter."""
        self.search_mode = False
        self.refresh(recompose=True)

    def clear_search(self) -> None:
        """Clear search query and exit search mode."""
        self.search_mode = False
        self.search_query = ""
        self.selected_index = 0
        self.refresh(recompose=True)

    def set_type_filter(self, session_type: SessionType | None) -> None:
        """Set type filter. None clears the filter."""
        self.type_filter = session_type
        self.selected_index = 0
        self.refresh(recompose=True)

    def cycle_type_filter(self) -> SessionType | None:
        """Cycle through type filters. Returns the new filter."""
        types = [None, SessionType.CLAUDE, SessionType.SHELL, SessionType.CODEX, SessionType.GEMINI, SessionType.CUSTOM]
        current_idx = types.index(self.type_filter) if self.type_filter in types else 0
        next_idx = (current_idx + 1) % len(types)
        self.type_filter = types[next_idx]
        self.selected_index = 0
        self.refresh(recompose=True)
        return self.type_filter

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_query = event.value
            self.selected_index = 0
            self.refresh(recompose=True)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input submission (Enter key)."""
        if event.input.id == "search-input":
            self.exit_search_mode()

    def get_selected(self) -> Session | None:
        """Get the currently selected session."""
        filtered = self._get_filtered_sessions()
        if filtered and 0 <= self.selected_index < len(filtered):
            return filtered[self.selected_index]
        return None

    def get_session_order(self) -> list[str]:
        """Get session IDs in current display order."""
        return [s.id for s in self.sessions]

    def update_sessions(self, sessions: list[Session]) -> None:
        """Update the session list."""
        self.sessions = sessions
        filtered = self._get_filtered_sessions()
        if self.selected_index >= len(filtered):
            self.selected_index = max(0, len(filtered) - 1)
        self.refresh(recompose=True)
