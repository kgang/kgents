"""MainScreen: The primary session management interface."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Header, Static

from ...types import Session, SessionState
from ...ground import ZenGround
from ...tmux.capture import TmuxCapture, capture_output
from ..events import SessionSelected, NotificationRequest
from ..widgets.session_list import SessionList
from ..widgets.output_view import OutputView
from .base import ZenScreen


class MainScreen(ZenScreen):
    """Main application screen with session list and output preview.

    Uses kgents agents for all operations:
    - ZenGround: Session state (empirical facts)
    - TmuxCapture: Output capture
    - ZenJudge: Validation pipelines
    - SessionContradict/Sublate: Conflict resolution
    """

    BINDINGS = [
        ("j", "move_down", "Down"),
        ("k", "move_up", "Up"),
        ("down", "move_down", "Down"),
        ("up", "move_up", "Up"),
        Binding("l", "toggle_grab", "Grab", show=False),
        Binding("space", "toggle_grab", "Grab", show=False),
        Binding("escape", "exit_grab", "Exit", show=False),
        ("n", "new_session", "New"),
        ("a", "attach", "Attach"),
        ("p", "pause", "Pause"),
        ("x", "kill", "Kill"),
        ("d", "clean", "Clean"),
        ("v", "revive", "Revive"),
        ("r", "refresh", "Refresh"),
        Binding("s", "toggle_streaming", "Stream", show=False),
        ("?", "show_help", "Help"),
        ("q", "quit", "Quit"),
        Binding("ctrl+q", "quit", "Quit", show=False),
    ]

    streaming: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    MainScreen {
        layout: vertical;
        padding: 1 2;
        layers: base notification;
    }

    MainScreen #content {
        height: 1fr;
    }

    MainScreen #session-list {
        width: 2fr;
        min-width: 30;
        max-width: 30vw;
    }

    MainScreen #output-view {
        width: 3fr;
        border-left: solid $surface-lighten-1;
        padding-left: 2;
    }

    MainScreen .hint {
        dock: bottom;
        height: 1;
        color: $text-disabled;
        text-align: center;
        margin-top: 1;
    }

    MainScreen #notifications {
        dock: bottom;
        layer: notification;
        margin-bottom: 2;
    }
    """

    def __init__(
        self,
        ground: ZenGround,
        capture: TmuxCapture | None = None,
    ) -> None:
        super().__init__()
        self._ground = ground
        self._capture = capture or capture_output

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="content"):
            yield SessionList(id="session-list")
            yield OutputView(id="output-view")
        yield Static("j/k nav  n new  a attach  ? help  q quit", id="hint", classes="hint")
        yield from super().compose()

    async def on_mount(self) -> None:
        """Initialize and start polling."""
        await self._refresh_sessions()
        self._refresh_selected_output()
        self.set_interval(1.0, self._poll_sessions)

    async def _refresh_sessions(self) -> None:
        """Update session list from ground state."""
        state = await self._ground.invoke()
        sessions = list(state.sessions.values())
        session_list = self.query_one("#session-list", SessionList)
        session_list.update_sessions(sessions)

    def _refresh_selected_output(self) -> None:
        """Refresh output for currently selected session."""
        session_list = self.query_one("#session-list", SessionList)
        selected = session_list.get_selected()

        if selected:
            output_view = self.query_one("#output-view", OutputView)
            # Get output from tmux if session is alive
            if selected.is_alive() and selected.tmux:
                # Would use TmuxCapture agent here
                content = "\n".join(selected.output_lines) or "[dim]capturing...[/dim]"
            else:
                content = self._build_dead_session_info(selected)

            glyphs = {
                SessionState.CREATING: "...",
                SessionState.RUNNING: ">>>",
                SessionState.PAUSED: "||",
                SessionState.COMPLETED: "ok",
                SessionState.FAILED: "xx",
                SessionState.UNKNOWN: "??",
            }

            output_view.update_session(
                session_name=selected.config.name,
                output=content,
                glyph=glyphs.get(selected.state, "?"),
                state=selected.state.value,
            )

    def _build_dead_session_info(self, session: Session) -> str:
        """Build info content for inactive session."""
        lines = []
        state_info = {
            SessionState.COMPLETED: ("completed", "Process exited normally"),
            SessionState.FAILED: ("failed", "Process failed"),
            SessionState.PAUSED: ("paused", "Session paused"),
        }
        state_label, state_desc = state_info.get(
            session.state, (session.state.value, "")
        )
        lines.append(f"  session {state_label}")
        if state_desc:
            lines.append(f"  {state_desc}")

        if session.error:
            lines.append(f"  error: {session.error}")

        lines.append("")
        lines.append("  actions")
        lines.append("    v  revive session")
        lines.append("    d  clean up")

        return "\n".join(lines)

    async def _poll_sessions(self) -> None:
        """Periodic refresh of session states."""
        await self._refresh_sessions()
        if self.streaming:
            self._refresh_selected_output()

    # Navigation actions
    def action_move_down(self) -> None:
        self.query_one("#session-list", SessionList).move_down()

    def action_move_up(self) -> None:
        self.query_one("#session-list", SessionList).move_up()

    def action_toggle_grab(self) -> None:
        """Toggle grab mode for reordering."""
        session_list = self.query_one("#session-list", SessionList)
        if session_list.grab_mode:
            session_list.exit_grab_mode()
            self.zen_notify("order saved")
        else:
            session_list.toggle_grab_mode()
            self.zen_notify("grab mode: j/k to reorder, space/esc to exit")

    def action_exit_grab(self) -> None:
        """Exit grab mode."""
        session_list = self.query_one("#session-list", SessionList)
        if session_list.grab_mode:
            session_list.exit_grab_mode()
            self.zen_notify("order saved")

    def action_new_session(self) -> None:
        """Create new session (placeholder)."""
        self.zen_notify("new session: coming soon", "warning")

    def action_attach(self) -> None:
        """Attach to tmux session."""
        session_list = self.query_one("#session-list", SessionList)
        selected = session_list.get_selected()
        if selected and selected.tmux:
            self.app.exit(result=f"attach:{selected.tmux.name}")
        else:
            self.zen_notify("no tmux session to attach", "warning")

    def action_pause(self) -> None:
        """Pause session (placeholder)."""
        self.zen_notify("pause: coming soon", "warning")

    def action_kill(self) -> None:
        """Kill session (placeholder)."""
        self.zen_notify("kill: coming soon", "warning")

    def action_clean(self) -> None:
        """Clean up dead session (placeholder)."""
        self.zen_notify("clean: coming soon", "warning")

    def action_revive(self) -> None:
        """Revive session (placeholder)."""
        self.zen_notify("revive: coming soon", "warning")

    def action_refresh(self) -> None:
        """Manual refresh."""
        self._refresh_selected_output()
        self.zen_notify("refreshed")

    def action_toggle_streaming(self) -> None:
        """Toggle streaming mode."""
        self.streaming = not self.streaming
        mode = "streaming" if self.streaming else "snapshot"
        self.zen_notify(f"output mode: {mode}")
        self._update_hint()

    def action_show_help(self) -> None:
        """Show help screen."""
        from .help import HelpScreen
        self.app.push_screen(HelpScreen())

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def _update_hint(self) -> None:
        """Update hint bar."""
        hint = self.query_one("#hint", Static)
        base = "j/k nav  n new  a attach  ? help  q quit"
        if self.streaming:
            hint.update(f"{base}  [dim]stream[/dim]")
        else:
            hint.update(base)

    def on_session_selected(self, event: SessionSelected) -> None:
        """Handle session selection changes."""
        self._refresh_selected_output()

    def zen_notify(self, message: str, severity: str = "success") -> None:
        """Helper for sending notifications."""
        self.post_message(NotificationRequest(message, severity))
