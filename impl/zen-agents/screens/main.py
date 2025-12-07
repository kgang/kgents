"""
Main Screen - The primary interface for zen-agents.

A contemplative TUI for managing parallel AI sessions.
"""

from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

from ..models import Session, SessionState, SessionType
from ..services import SessionManager, StateRefresher
from ..widgets import SessionList


class StatusBar(Static):
    """Status bar showing current state."""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        padding: 0 1;
        background: $surface;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._message = ""

    def set_message(self, message: str) -> None:
        """Set the status message."""
        self._message = message
        self.update(message)


class CreateSessionModal(Container):
    """Modal for creating a new session."""

    DEFAULT_CSS = """
    CreateSessionModal {
        align: center middle;
        width: 60;
        height: auto;
        max-height: 80%;
        padding: 1 2;
        background: $surface;
        border: solid $primary;
    }

    CreateSessionModal Label {
        margin-bottom: 1;
    }

    CreateSessionModal Input {
        margin-bottom: 1;
    }

    CreateSessionModal Select {
        margin-bottom: 1;
    }

    CreateSessionModal .buttons {
        height: 3;
        align: center middle;
    }

    CreateSessionModal Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Create New Session", classes="title")
        yield Label("Name:")
        yield Input(placeholder="session-name", id="session-name")
        yield Label("Type:")
        yield Select(
            [(t.value, t) for t in SessionType],
            id="session-type",
            value=SessionType.CLAUDE,
        )
        yield Label("Working Directory (optional):")
        yield Input(placeholder="/path/to/directory", id="working-dir")
        with Horizontal(classes="buttons"):
            yield Button("Create", variant="primary", id="create-btn")
            yield Button("Cancel", id="cancel-btn")


class SessionDetail(Container):
    """Panel showing details of selected session."""

    DEFAULT_CSS = """
    SessionDetail {
        width: 40;
        height: 100%;
        padding: 1;
        border-left: solid $surface-lighten-1;
    }

    SessionDetail .title {
        text-style: bold;
        margin-bottom: 1;
    }

    SessionDetail .detail-row {
        margin-bottom: 1;
    }

    SessionDetail .label {
        color: $text-muted;
    }

    SessionDetail .value {
        color: $text;
    }

    SessionDetail .actions {
        margin-top: 2;
    }

    SessionDetail Button {
        margin-right: 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._session: Optional[Session] = None

    def compose(self) -> ComposeResult:
        yield Label("Session Details", classes="title")
        yield Label("Select a session to view details", id="no-selection")
        yield Container(id="details", classes="hidden")

    def set_session(self, session: Optional[Session]) -> None:
        """Set the session to display."""
        self._session = session
        self._update_display()

    def _update_display(self) -> None:
        """Update the detail display."""
        no_selection = self.query_one("#no-selection", Label)
        details = self.query_one("#details", Container)

        if not self._session:
            no_selection.remove_class("hidden")
            details.add_class("hidden")
            return

        no_selection.add_class("hidden")
        details.remove_class("hidden")

        # Update details
        session = self._session
        details.remove_children()

        details.mount(Label(f"Name: {session.name}", classes="detail-row"))
        details.mount(Label(f"Type: {session.session_type.value}", classes="detail-row"))
        details.mount(Label(f"State: {session.state.value}", classes="detail-row"))
        details.mount(Label(f"Tmux: {session.tmux_name}", classes="detail-row"))
        details.mount(Label(f"Created: {session.created_at.strftime('%H:%M:%S')}", classes="detail-row"))

        if session.working_dir:
            details.mount(Label(f"Dir: {session.working_dir}", classes="detail-row"))

        if session.exit_code is not None:
            details.mount(Label(f"Exit: {session.exit_code}", classes="detail-row"))

        # Actions
        with Container(classes="actions"):
            if session.state == SessionState.RUNNING:
                details.mount(Button("Kill", variant="error", id="action-kill"))
                details.mount(Button("Attach", variant="primary", id="action-attach"))
            elif session.state in (SessionState.PAUSED, SessionState.KILLED):
                details.mount(Button("Revive", variant="success", id="action-revive"))
            details.mount(Button("Remove", variant="warning", id="action-remove"))


class MainScreen(Screen):
    """
    The main screen of zen-agents.

    A contemplative TUI for managing parallel AI sessions.
    """

    DEFAULT_CSS = """
    MainScreen {
        layout: horizontal;
    }

    MainScreen .main-content {
        width: 1fr;
        height: 100%;
    }

    MainScreen .session-list-container {
        height: 1fr;
        padding: 1;
    }

    MainScreen .hidden {
        display: none;
    }

    MainScreen #modal-overlay {
        align: center middle;
        background: $background 50%;
    }
    """

    BINDINGS = [
        Binding("n", "new_session", "New"),
        Binding("q", "quit", "Quit"),
        Binding("a", "attach", "Attach"),
        Binding("?", "help", "Help"),
    ]

    def __init__(
        self,
        manager: SessionManager,
        refresher: StateRefresher,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._manager = manager
        self._refresher = refresher
        self._manager.add_event_handler(self._on_session_event)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal():
            with Vertical(classes="main-content"):
                with Container(classes="session-list-container"):
                    yield SessionList(id="session-list")

            yield SessionDetail(id="session-detail")

        yield StatusBar(id="status-bar")
        yield Container(id="modal-overlay", classes="hidden")
        yield Footer()

    async def on_mount(self) -> None:
        """Start the state refresher when mounted."""
        await self._refresher.start()
        self._update_session_list()

    async def on_unmount(self) -> None:
        """Stop the state refresher when unmounted."""
        await self._refresher.stop()

    def _update_session_list(self) -> None:
        """Update the session list widget."""
        session_list = self.query_one("#session-list", SessionList)
        session_list.sessions = self._manager.sessions

    async def _on_session_event(self, event) -> None:
        """Handle session events from the manager."""
        self._update_session_list()

        # Update status bar
        status_bar = self.query_one("#status-bar", StatusBar)

        from ..services.session_manager import (
            SessionCreated,
            SessionStateChanged,
            SessionKilled,
        )

        if isinstance(event, SessionCreated):
            status_bar.set_message(f"Created session: {event.session.name}")
        elif isinstance(event, SessionStateChanged):
            status_bar.set_message(
                f"Session state changed: {event.old_state.value} → {event.new_state.value}"
            )
        elif isinstance(event, SessionKilled):
            status_bar.set_message(f"Session killed (exit: {event.exit_code})")

    def action_new_session(self) -> None:
        """Show the new session modal."""
        overlay = self.query_one("#modal-overlay", Container)
        overlay.remove_class("hidden")
        overlay.remove_children()
        overlay.mount(CreateSessionModal())

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    async def action_attach(self) -> None:
        """Attach to selected session's tmux."""
        session_list = self.query_one("#session-list", SessionList)
        session = session_list.selected_session

        if session and session.state == SessionState.RUNNING:
            # Note: Actual attachment would need to be handled by
            # suspending the TUI and running tmux attach
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.set_message(f"Attach: tmux attach-session -t {session.tmux_name}")

    def action_help(self) -> None:
        """Show help."""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.set_message("n:New j/k:Navigate enter:Select d:Kill r:Revive q:Quit")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "cancel-btn":
            overlay = self.query_one("#modal-overlay", Container)
            overlay.add_class("hidden")
            overlay.remove_children()

        elif button_id == "create-btn":
            await self._create_session_from_modal()

        elif button_id == "action-kill":
            detail = self.query_one("#session-detail", SessionDetail)
            if detail._session:
                await self._manager.kill_session(detail._session.id)

        elif button_id == "action-revive":
            detail = self.query_one("#session-detail", SessionDetail)
            if detail._session:
                await self._manager.revive_session(detail._session.id)

        elif button_id == "action-remove":
            detail = self.query_one("#session-detail", SessionDetail)
            if detail._session:
                await self._manager.remove_session(detail._session.id)
                detail.set_session(None)

    async def _create_session_from_modal(self) -> None:
        """Create a session from the modal inputs."""
        overlay = self.query_one("#modal-overlay", Container)
        modal = overlay.query_one(CreateSessionModal)

        name_input = modal.query_one("#session-name", Input)
        type_select = modal.query_one("#session-type", Select)
        dir_input = modal.query_one("#working-dir", Input)

        name = name_input.value.strip()
        session_type = type_select.value
        working_dir = dir_input.value.strip() or None

        if not name:
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.set_message("Error: Name is required")
            return

        try:
            await self._manager.create_session(
                name=name,
                session_type=session_type,
                working_dir=working_dir,
            )

            # Close modal
            overlay.add_class("hidden")
            overlay.remove_children()

        except Exception as e:
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.set_message(f"Error: {e}")

    def on_session_list_session_selected(
        self,
        event: SessionList.SessionSelected,
    ) -> None:
        """Handle session selection."""
        detail = self.query_one("#session-detail", SessionDetail)
        detail.set_session(event.session)

    async def on_session_list_session_action(
        self,
        event: SessionList.SessionAction,
    ) -> None:
        """Handle session action requests."""
        if event.action == "kill":
            await self._manager.kill_session(event.session.id)
        elif event.action == "revive":
            await self._manager.revive_session(event.session.id)
