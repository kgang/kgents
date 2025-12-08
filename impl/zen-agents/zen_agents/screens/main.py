"""
Main Screen - The primary interface for zen-agents.

A contemplative TUI for managing parallel AI sessions,
with integrated LLM analysis via kgents agents.
"""

from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static
from textual.worker import Worker, get_current_worker

from ..models import Session, SessionState, SessionType, session_requires_llm
from ..services import SessionManager, StateRefresher
from ..services.agent_orchestrator import AgentOrchestrator
from ..widgets import SessionList, LogViewer


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

    A contemplative TUI for managing parallel AI sessions,
    with integrated LLM analysis via kgents agents.
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
        height: 50%;
        padding: 1;
    }

    MainScreen .log-container {
        height: 50%;
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
        Binding("l", "capture_log", "Capture Log"),
        Binding("?", "help", "Help"),
    ]

    def __init__(
        self,
        manager: SessionManager,
        refresher: StateRefresher,
        orchestrator: Optional[AgentOrchestrator] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._manager = manager
        self._refresher = refresher
        self._orchestrator = orchestrator or AgentOrchestrator()
        self._manager.add_event_handler(self._on_session_event)
        self._selected_session: Optional[Session] = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal():
            with Vertical(classes="main-content"):
                with Container(classes="session-list-container"):
                    yield SessionList(id="session-list")
                with Container(classes="log-container"):
                    yield LogViewer(id="log-viewer")

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
            # Suspend the TUI, attach to tmux, then resume
            await self._attach_to_session(session.tmux_name)
        else:
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.set_message("No running session selected to attach")

    async def _attach_to_session(self, tmux_name: str) -> None:
        """Suspend TUI and attach to tmux session."""
        import subprocess
        import os

        # Suspend the app to release the terminal
        with self.app.suspend():
            # Run tmux attach in the foreground
            subprocess.run(
                ["tmux", "attach-session", "-t", tmux_name],
                stdin=None,
                stdout=None,
                stderr=None,
            )

        # After detaching from tmux, the TUI resumes automatically
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.set_message(f"Detached from {tmux_name}")

    def action_help(self) -> None:
        """Show help."""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.set_message("n:New j/k:Nav enter:Sel a:Attach l:Log d:Kill r:Revive q:Quit")

    async def action_capture_log(self) -> None:
        """Capture and display the selected session's log."""
        if not self._selected_session:
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.set_message("No session selected")
            return

        if self._selected_session.state != SessionState.RUNNING:
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.set_message("Session is not running")
            return

        await self._capture_session_log(self._selected_session)

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

        elif button_id == "action-attach":
            detail = self.query_one("#session-detail", SessionDetail)
            if detail._session and detail._session.state == SessionState.RUNNING:
                await self._attach_to_session(detail._session.tmux_name)

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
        self._selected_session = event.session
        detail = self.query_one("#session-detail", SessionDetail)
        detail.set_session(event.session)

        # Clear log viewer when selection changes
        log_viewer = self.query_one("#log-viewer", LogViewer)
        log_viewer.clear()

    async def on_session_list_session_action(
        self,
        event: SessionList.SessionAction,
    ) -> None:
        """Handle session action requests."""
        if event.action == "kill":
            await self._manager.kill_session(event.session.id)
        elif event.action == "revive":
            await self._manager.revive_session(event.session.id)

    # -------------------------------------------------------------------------
    # Log Capture and Analysis
    # -------------------------------------------------------------------------

    async def _capture_session_log(self, session: Session) -> None:
        """Capture the session's tmux pane content and display in log viewer."""
        import subprocess

        status_bar = self.query_one("#status-bar", StatusBar)
        log_viewer = self.query_one("#log-viewer", LogViewer)

        try:
            # Capture tmux pane content
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", session.tmux_name, "-p", "-S", "-500"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                content = result.stdout
                log_viewer.update_log(content)
                status_bar.set_message(f"Captured log for {session.name}")
            else:
                log_viewer.show_error(f"Failed to capture: {result.stderr}")
                status_bar.set_message("Failed to capture log")

        except subprocess.TimeoutExpired:
            log_viewer.show_error("Timeout capturing pane")
            status_bar.set_message("Timeout capturing log")
        except Exception as e:
            log_viewer.show_error(str(e))
            status_bar.set_message(f"Error: {e}")

    def on_log_viewer_analyze_requested(
        self,
        event: LogViewer.AnalyzeRequested,
    ) -> None:
        """Handle analysis request from log viewer."""
        log_viewer = self.query_one("#log-viewer", LogViewer)
        status_bar = self.query_one("#status-bar", StatusBar)

        if not log_viewer.log_content:
            status_bar.set_message("No log content to analyze. Press 'l' to capture.")
            return

        if not self._selected_session:
            status_bar.set_message("No session selected")
            return

        # Start analysis in worker thread
        log_viewer.start_analyzing()
        status_bar.set_message("Analyzing log with HypothesisEngine...")

        # Run analysis in background worker
        self.run_worker(
            self._do_analysis(
                log_viewer.log_content,
                self._selected_session.metadata.get("domain", "software engineering"),
            ),
            name="analyze_log",
        )

    async def _do_analysis(self, log_content: str, domain: str) -> None:
        """Perform LLM analysis in background worker."""
        log_viewer = self.query_one("#log-viewer", LogViewer)
        status_bar = self.query_one("#status-bar", StatusBar)

        try:
            # Check if LLM is available
            if not await self._orchestrator.check_available():
                log_viewer.show_error("Claude CLI not available. Install with: npm install -g @anthropic/claude-code")
                status_bar.set_message("Claude CLI not available")
                return

            # Run analysis
            result = await self._orchestrator.analyze_log(
                log_content=log_content,
                domain=domain,
            )

            # Format analysis as markdown
            analysis = "## Hypotheses\n"
            for h in result.hypotheses:
                analysis += f"* {h}\n"

            if result.suggested_tests:
                analysis += "\n## Suggested Tests\n"
                for t in result.suggested_tests:
                    analysis += f"* {t}\n"

            if result.reasoning:
                analysis += f"\n## Reasoning\n{result.reasoning}\n"

            log_viewer.show_analysis(analysis)
            status_bar.set_message(f"Analysis complete: {len(result.hypotheses)} hypotheses")

        except Exception as e:
            log_viewer.show_error(str(e))
            status_bar.set_message(f"Analysis failed: {e}")
