"""MainScreen: The primary session management interface."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Header, Static

from ...types import Session, SessionState, SessionConfig, SessionType
from ...ground import ZenGround
from ...conflicts import resolve_conflicts, SessionContradictInput
from ...tmux.capture import TmuxCapture, capture_output
from ..events import SessionSelected, NotificationRequest
from ..widgets.session_list import SessionList
from ..widgets.output_view import OutputView
from .base import ZenScreen
from .new_session import NewSessionModal, NewSessionResult
from .conflict import ConflictModal, ConflictModalResult


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
        Binding("escape", "exit_mode", "Exit", show=False),
        ("n", "new_session", "New"),
        ("a", "attach", "Attach"),
        ("p", "pause", "Pause"),
        ("x", "kill", "Kill"),
        ("d", "clean", "Clean"),
        ("v", "revive", "Revive"),
        ("r", "refresh", "Refresh"),
        Binding("s", "toggle_streaming", "Stream", show=False),
        # Search/filter
        Binding("/", "search", "Search", show=False),
        Binding("f", "cycle_filter", "Filter", show=False),
        Binding("1", "filter_claude", "Claude", show=False),
        Binding("2", "filter_shell", "Shell", show=False),
        Binding("3", "filter_codex", "Codex", show=False),
        Binding("4", "filter_gemini", "Gemini", show=False),
        Binding("5", "filter_custom", "Custom", show=False),
        Binding("0", "clear_filter", "All", show=False),
        # Help
        ("?", "show_help", "Help"),
        Binding("f1", "show_help", "Help", show=False),
        Binding("ctrl+p", "command_palette", "Commands", show=False),
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

    MainScreen #status-bar {
        dock: bottom;
        height: 1;
        color: $text-muted;
        padding: 0 2;
    }

    MainScreen #status-bar .stat {
        margin-right: 2;
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
        yield Static("", id="status-bar")
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
        self._update_status_bar(sessions)

    def _refresh_selected_output(self) -> None:
        """Refresh output for currently selected session."""
        session_list = self.query_one("#session-list", SessionList)
        selected = session_list.get_selected()

        if selected:
            # Use async worker to capture output
            self.run_worker(self._capture_and_display(selected), exclusive=False)

    async def _capture_and_display(self, session: Session) -> None:
        """Capture output via TmuxCapture and update display."""
        from ...tmux.capture import CaptureInput

        output_view = self.query_one("#output-view", OutputView)

        if session.is_alive() and session.tmux:
            # Use TmuxCapture agent for live output
            capture_result = await self._capture.invoke(CaptureInput(
                session=session.tmux,
                lines=100,
            ))
            content = "\n".join(capture_result.lines) or "[dim]capturing...[/dim]"

            # Update session output_lines cache
            from dataclasses import replace
            updated = replace(session, output_lines=capture_result.lines)
            self._ground.update_session(updated)
        else:
            content = self._build_dead_session_info(session)

        glyphs = {
            SessionState.CREATING: "...",
            SessionState.RUNNING: ">>>",
            SessionState.PAUSED: "||",
            SessionState.COMPLETED: "ok",
            SessionState.FAILED: "xx",
            SessionState.UNKNOWN: "??",
        }

        output_view.update_session(
            session_name=session.config.name,
            output=content,
            glyph=glyphs.get(session.state, "?"),
            state=session.state.value,
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

    def action_exit_mode(self) -> None:
        """Exit current mode (grab or search)."""
        session_list = self.query_one("#session-list", SessionList)
        if session_list.grab_mode:
            session_list.exit_grab_mode()
            self.zen_notify("order saved")
        elif session_list.search_mode:
            session_list.exit_search_mode()
        elif session_list.search_query or session_list.type_filter:
            session_list.clear_search()
            session_list.set_type_filter(None)
            self.zen_notify("filter cleared")

    def action_new_session(self) -> None:
        """Open new session modal."""
        modal = NewSessionModal(
            ground=self._ground,
            working_dir=Path.cwd(),
        )
        self.app.push_screen(modal, self._on_new_session_result)

    def action_attach(self) -> None:
        """Attach to tmux session."""
        session_list = self.query_one("#session-list", SessionList)
        selected = session_list.get_selected()
        if selected and selected.tmux:
            self.app.exit(result=f"attach:{selected.tmux.name}")
        else:
            self.zen_notify("no tmux session to attach", "warning")

    def action_pause(self) -> None:
        """Pause selected session."""
        session = self._get_selected_session()
        if not session:
            self.zen_notify("no session selected", "warning")
            return
        if session.state != SessionState.RUNNING:
            self.zen_notify("session not running", "warning")
            return
        # Detach from tmux session (pauses it)
        if session.tmux:
            self.run_worker(self._pause_session(session), exclusive=True)
        else:
            self.zen_notify("no tmux session", "warning")

    def action_kill(self) -> None:
        """Kill selected session."""
        session = self._get_selected_session()
        if not session:
            self.zen_notify("no session selected", "warning")
            return
        if not session.is_alive():
            self.zen_notify("session already dead", "warning")
            return
        self.run_worker(self._kill_session(session), exclusive=True)

    def action_clean(self) -> None:
        """Clean up dead session."""
        session = self._get_selected_session()
        if not session:
            self.zen_notify("no session selected", "warning")
            return
        if session.is_alive():
            self.zen_notify("session still alive - kill it first", "warning")
            return
        self.run_worker(self._clean_session(session), exclusive=True)

    def action_revive(self) -> None:
        """Revive a dead/paused session."""
        session = self._get_selected_session()
        if not session:
            self.zen_notify("no session selected", "warning")
            return
        if session.state == SessionState.RUNNING:
            self.zen_notify("session already running", "warning")
            return
        self.run_worker(self._revive_session(session), exclusive=True)

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

    # Search/filter actions
    def action_search(self) -> None:
        """Enter search mode."""
        session_list = self.query_one("#session-list", SessionList)
        session_list.enter_search_mode()
        self._update_hint()

    def action_cycle_filter(self) -> None:
        """Cycle through type filters."""
        session_list = self.query_one("#session-list", SessionList)
        new_filter = session_list.cycle_type_filter()
        if new_filter:
            self.zen_notify(f"filter: {new_filter.value}")
        else:
            self.zen_notify("filter: all")
        self._update_hint()

    def action_filter_claude(self) -> None:
        """Filter to Claude sessions."""
        self._set_type_filter(SessionType.CLAUDE)

    def action_filter_shell(self) -> None:
        """Filter to Shell sessions."""
        self._set_type_filter(SessionType.SHELL)

    def action_filter_codex(self) -> None:
        """Filter to Codex sessions."""
        self._set_type_filter(SessionType.CODEX)

    def action_filter_gemini(self) -> None:
        """Filter to Gemini sessions."""
        self._set_type_filter(SessionType.GEMINI)

    def action_filter_custom(self) -> None:
        """Filter to Custom sessions."""
        self._set_type_filter(SessionType.CUSTOM)

    def action_clear_filter(self) -> None:
        """Clear all filters."""
        session_list = self.query_one("#session-list", SessionList)
        session_list.clear_search()
        session_list.set_type_filter(None)
        self.zen_notify("filter: all")
        self._update_hint()

    def _set_type_filter(self, session_type: SessionType) -> None:
        """Set type filter helper."""
        session_list = self.query_one("#session-list", SessionList)
        session_list.set_type_filter(session_type)
        self.zen_notify(f"filter: {session_type.value}")
        self._update_hint()

    def action_command_palette(self) -> None:
        """Show command palette."""
        from .command_palette import CommandPaletteModal
        self.app.push_screen(CommandPaletteModal(), self._on_command_selected)

    def _on_command_selected(self, command: str | None) -> None:
        """Handle command palette selection."""
        if not command:
            return
        # Map command to action
        action_map = {
            "new": self.action_new_session,
            "attach": self.action_attach,
            "pause": self.action_pause,
            "kill": self.action_kill,
            "clean": self.action_clean,
            "revive": self.action_revive,
            "refresh": self.action_refresh,
            "help": self.action_show_help,
            "quit": self.action_quit,
            "search": self.action_search,
            "filter_claude": self.action_filter_claude,
            "filter_shell": self.action_filter_shell,
            "clear_filter": self.action_clear_filter,
        }
        if command in action_map:
            action_map[command]()

    def action_show_help(self) -> None:
        """Show help screen."""
        from .help import HelpScreen
        self.app.push_screen(HelpScreen())

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def _update_hint(self) -> None:
        """Update hint bar with current mode/filter status."""
        hint = self.query_one("#hint", Static)
        session_list = self.query_one("#session-list", SessionList)

        base = "j/k nav  n new  a attach  ? help  q quit"
        extras = []

        if self.streaming:
            extras.append("[dim]stream[/dim]")
        if session_list.search_mode:
            extras.append("[yellow]/ search[/yellow]")
        elif session_list.search_query:
            extras.append(f"[yellow]/{session_list.search_query}[/yellow]")
        if session_list.type_filter:
            extras.append(f"[green][{session_list.type_filter.value}][/green]")

        if extras:
            hint.update(f"{base}  {'  '.join(extras)}")
        else:
            hint.update(base)

    def _update_status_bar(self, sessions: list[Session]) -> None:
        """Update status bar with session statistics."""
        status_bar = self.query_one("#status-bar", Static)

        # Count by state
        running = sum(1 for s in sessions if s.state == SessionState.RUNNING)
        paused = sum(1 for s in sessions if s.state == SessionState.PAUSED)
        completed = sum(1 for s in sessions if s.state == SessionState.COMPLETED)
        failed = sum(1 for s in sessions if s.state == SessionState.FAILED)

        # Count by type
        type_counts = {}
        for s in sessions:
            t = s.config.session_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        # Build status text
        parts = []
        parts.append(f"[bold]{len(sessions)}[/bold] sessions")

        if running:
            parts.append(f"[green]{running} running[/green]")
        if paused:
            parts.append(f"[yellow]{paused} paused[/yellow]")
        if completed:
            parts.append(f"[dim]{completed} done[/dim]")
        if failed:
            parts.append(f"[red]{failed} failed[/red]")

        status_bar.update("  ".join(parts))

    def on_session_selected(self, event: SessionSelected) -> None:
        """Handle session selection changes."""
        self._refresh_selected_output()

    def zen_notify(self, message: str, severity: str = "success") -> None:
        """Helper for sending notifications."""
        self.post_message(NotificationRequest(message, severity))

    def _get_selected_session(self) -> Session | None:
        """Get currently selected session."""
        session_list = self.query_one("#session-list", SessionList)
        return session_list.get_selected()

    async def _on_new_session_result(self, result: NewSessionResult) -> None:
        """Handle result from NewSessionModal."""
        if not result.created or not result.config:
            return

        # Check for conflicts via pipeline
        ground_state = await self._ground.invoke()
        conflict_result = await resolve_conflicts(
            config=result.config,
            ground_state=ground_state,
            auto_resolve=True,
        )

        if conflict_result.has_conflicts:
            # Show conflict modal
            modal = ConflictModal(conflict_result, result.config)
            self.app.push_screen(modal, self._on_conflict_result)
        else:
            # No conflicts - create session directly
            await self._create_session(result.config)

    async def _on_conflict_result(self, result: ConflictModalResult) -> None:
        """Handle result from ConflictModal."""
        if not result.resolved or not result.final_config:
            self.zen_notify("session creation cancelled", "warning")
            return

        if result.action == "force":
            self.zen_notify("forcing session creation...", "warning")

        await self._create_session(result.final_config)

    async def _create_session(self, config: SessionConfig) -> None:
        """Create a new session via NewSessionPipeline."""
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "pipelines"))
            from pipelines.new_session import NewSessionPipeline

            pipeline = NewSessionPipeline(ground=self._ground)
            result = await pipeline.invoke(config)

            if result.success:
                self.zen_notify(f"created: {config.name}")
                await self._refresh_sessions()
            else:
                self.zen_notify(f"failed: {result.error}", "error")
        except ImportError:
            # Pipeline not available - create placeholder
            self.zen_notify(f"pipeline not available: {config.name}", "warning")
        except Exception as e:
            self.zen_notify(f"error: {e}", "error")

    async def _pause_session(self, session: Session) -> None:
        """Pause a session by sending SIGSTOP or detaching."""
        import asyncio
        from dataclasses import replace

        if session.tmux:
            # Send SIGSTOP to the tmux pane process
            cmd = ["tmux", "send-keys", "-t", session.tmux.pane_id, "C-z"]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await process.wait()

        # Update session state
        updated = replace(session, state=SessionState.PAUSED)
        self._ground.update_session(updated)
        self.zen_notify(f"paused: {session.config.name}")
        await self._refresh_sessions()

    async def _kill_session(self, session: Session) -> None:
        """Kill a session's tmux pane."""
        import asyncio
        from dataclasses import replace
        from datetime import datetime

        if session.tmux:
            cmd = ["tmux", "kill-pane", "-t", session.tmux.pane_id]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await process.wait()

        # Update session state
        updated = replace(
            session,
            state=SessionState.COMPLETED,
            completed_at=datetime.now(),
        )
        self._ground.update_session(updated)
        self.zen_notify(f"killed: {session.config.name}")
        await self._refresh_sessions()

    async def _clean_session(self, session: Session) -> None:
        """Remove a dead session from ground state."""
        # Remove from ground state
        ground_state = await self._ground.invoke()
        if session.id in ground_state.sessions:
            del ground_state.sessions[session.id]
        self.zen_notify(f"cleaned: {session.config.name}")
        await self._refresh_sessions()

    async def _revive_session(self, session: Session) -> None:
        """Revive a paused/dead session by recreating it."""
        # For paused: send SIGCONT
        # For dead: re-run via pipeline
        import asyncio
        from dataclasses import replace

        if session.state == SessionState.PAUSED and session.tmux:
            # Resume with fg or SIGCONT
            cmd = ["tmux", "send-keys", "-t", session.tmux.pane_id, "fg", "Enter"]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await process.wait()

            updated = replace(session, state=SessionState.RUNNING)
            self._ground.update_session(updated)
            self.zen_notify(f"revived: {session.config.name}")
        else:
            # Dead session - recreate via pipeline
            await self._create_session(session.config)

        await self._refresh_sessions()
