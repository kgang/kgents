"""
TUI Dashboard - The DVR for agent execution.

A Textual-based TUI that provides:
- Real-time agent monitoring
- Session playback and scrubbing
- Thought stream visualization
- Artifact inspection

Philosophy: "Real-time logs are good, but agents are fast.
By the time you see a mistake, it's gone. The TUI should not
just be a monitor; it should be a DVR."

Layout:
┌─────────────────────────────────────────────────────────────────┐
│ kgents dash                                    [budget: medium] │
├─────────────────┬───────────────────────────────┬───────────────┤
│ AGENTS          │ THOUGHT STREAM                │ ARTIFACTS     │
│                 │                               │               │
│ ● parse [done]  │ [parse] Extracting structure  │ output.json   │
│ ◐ judge [run]   │ [parse] Found 3 functions     │ report.md     │
│ ○ refine [wait] │ [judge] Evaluating principle  │               │
│                 │   1: TASTEFUL ✓               │               │
├─────────────────┴───────────────────────────────┴───────────────┤
│ > _                                              [◀ ▶ scrub]    │
└─────────────────────────────────────────────────────────────────┘

Keybindings:
- ←/→: Rewind/fast-forward through thought stream
- Space: Pause live stream
- Enter: Execute command in context
- s: Take snapshot of current state
- q: Quit
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Callable

from .types import (
    AgentEntry,
    AgentStatus,
    ArtifactEntry,
    DashboardEvent,
    EventType,
    PlaybackState,
    Session,
    SessionState,
    ThoughtEntry,
)
from .event_store import EventStore


# =============================================================================
# Try to import Textual (optional dependency)
# =============================================================================

TEXTUAL_AVAILABLE = False
try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import (
        Static,
        Header,
        Footer,
        Input,
        ListView,
        ListItem,
        Label,
        Log,
        ProgressBar,
    )
    from textual.reactive import reactive
    from textual.binding import Binding
    from textual import events

    TEXTUAL_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# Dashboard Controller (Backend)
# =============================================================================


class DashboardController:
    """
    Backend controller for the dashboard.

    Manages:
    - Session state
    - Event streaming
    - Playback control
    - Store interaction
    """

    def __init__(self, store: EventStore | None = None):
        self.store = store or EventStore()
        self.current_session: Session | None = None
        self.playback: PlaybackState | None = None
        self._callbacks: list[Callable[[DashboardEvent], None]] = []

    def start_session(
        self,
        name: str,
        flow_name: str | None = None,
        flow_path: Path | None = None,
    ) -> Session:
        """Start a new live session."""
        self.current_session = self.store.create_session(
            name=name,
            flow_name=flow_name,
            flow_path=flow_path,
        )
        return self.current_session

    def end_session(self) -> None:
        """End the current session."""
        if self.current_session:
            self.store.end_session(self.current_session.id)
            self.current_session.state = SessionState.ENDED

    def load_session(self, session_id: str) -> Session | None:
        """Load a historical session for replay."""
        session = self.store.get_session(session_id)
        if session:
            self.current_session = session
            self.playback = PlaybackState(session=session)
        return session

    def add_event(
        self,
        event_type: EventType,
        source: str,
        message: str,
        data: dict | None = None,
    ) -> DashboardEvent | None:
        """Add an event to the current session."""
        if not self.current_session:
            return None

        event = self.store.add_event(
            session_id=self.current_session.id,
            event_type=event_type,
            source=source,
            message=message,
            data=data,
        )

        self.current_session.events.append(event)

        # Notify callbacks
        for callback in self._callbacks:
            callback(event)

        return event

    def add_thought(
        self, source: str, content: str, level: str = "info"
    ) -> ThoughtEntry:
        """Add a thought to the stream."""
        thought = ThoughtEntry(
            timestamp=datetime.now(),
            source=source,
            content=content,
            level=level,
        )

        if self.current_session:
            self.current_session.thoughts.append(thought)

            # Also add as event for persistence
            self.add_event(
                EventType.THOUGHT,
                source,
                content,
                {"level": level},
            )

        return thought

    def register_agent(self, agent_id: str, name: str, genus: str) -> AgentEntry:
        """Register an agent for tracking."""
        agent = AgentEntry(id=agent_id, name=name, genus=genus)

        if self.current_session:
            self.current_session.agents[agent_id] = agent
            self.store.register_agent(
                self.current_session.id,
                agent_id,
                name,
                genus,
            )

        return agent

    def update_agent(
        self, agent_id: str, status: AgentStatus, error: str | None = None
    ) -> None:
        """Update agent status."""
        if self.current_session and agent_id in self.current_session.agents:
            agent = self.current_session.agents[agent_id]
            agent.status = status
            agent.error = error

            if status == AgentStatus.RUNNING:
                agent.started_at = datetime.now()
            elif status in (AgentStatus.COMPLETE, AgentStatus.FAILED):
                agent.completed_at = datetime.now()

            self.store.update_agent_status(
                self.current_session.id,
                agent_id,
                status,
                error,
            )

            # Add event
            event_type = {
                AgentStatus.RUNNING: EventType.AGENT_START,
                AgentStatus.COMPLETE: EventType.AGENT_COMPLETE,
                AgentStatus.FAILED: EventType.AGENT_FAIL,
                AgentStatus.SKIPPED: EventType.AGENT_SKIP,
            }.get(status, EventType.THOUGHT)

            self.add_event(event_type, agent_id, f"Agent {agent_id}: {status.value}")

    def register_artifact(
        self,
        name: str,
        artifact_type: str,
        path: Path | None = None,
        content_preview: str = "",
    ) -> ArtifactEntry | None:
        """Register an artifact."""
        if not self.current_session:
            return None

        artifact = self.store.register_artifact(
            self.current_session.id,
            name,
            artifact_type,
            path,
            path.stat().st_size if path and path.exists() else 0,
            content_preview,
        )

        self.current_session.artifacts[artifact.id] = artifact
        return artifact

    def on_event(self, callback: Callable[[DashboardEvent], None]) -> None:
        """Register callback for events."""
        self._callbacks.append(callback)

    # =========================================================================
    # Playback Control
    # =========================================================================

    def seek(self, index: int) -> DashboardEvent | None:
        """Seek to specific event index."""
        if self.playback:
            self.playback.seek(index)
            return self.playback.current_event
        return None

    def step_forward(self) -> DashboardEvent | None:
        """Step forward one event."""
        if self.playback:
            return self.playback.step_forward()
        return None

    def step_backward(self) -> DashboardEvent | None:
        """Step backward one event."""
        if self.playback:
            return self.playback.step_backward()
        return None

    def toggle_pause(self) -> bool:
        """Toggle playback pause."""
        if self.playback:
            self.playback.paused = not self.playback.paused
            return self.playback.paused
        return False


# =============================================================================
# Fallback Console Dashboard (when Textual not available)
# =============================================================================


class ConsoleDashboard:
    """
    Simple console-based dashboard for when Textual is not available.

    Provides basic functionality using standard output.
    """

    def __init__(self, controller: DashboardController):
        self.controller = controller
        self.running = True

    def _clear_screen(self) -> None:
        """Clear the terminal screen."""
        print("\033[2J\033[H", end="")

    def _draw_header(self) -> None:
        """Draw the header."""
        session = self.controller.current_session
        if session:
            mode = "LIVE" if session.state == SessionState.LIVE else "REPLAY"
            print(f"╭─ kgents dash ({mode}) ─ {session.name} ─{'─' * 30}╮")
        else:
            print("╭─ kgents dash ─" + "─" * 50 + "╮")

    def _draw_agents(self) -> None:
        """Draw the agents panel."""
        session = self.controller.current_session
        print("│ AGENTS          │")
        print("│                 │")

        if session:
            for agent in list(session.agents.values())[:10]:
                line = f"│ {agent.render():<15} │"
                print(line)
        else:
            print("│ (no session)    │")

    def _draw_thoughts(self) -> None:
        """Draw the thought stream."""
        session = self.controller.current_session
        print("│ THOUGHT STREAM                               │")
        print("│                                              │")

        if session:
            for thought in session.thoughts[-10:]:
                line = thought.render(show_timestamp=False)[:44]
                print(f"│ {line:<44} │")
        else:
            print("│ (no thoughts)                                │")

    def _draw_footer(self) -> None:
        """Draw the footer."""
        print("├──────────────────────────────────────────────────────────────┤")
        print("│ [q]uit  [←]back  [→]forward  [space]pause  [s]napshot        │")
        print("╰──────────────────────────────────────────────────────────────╯")

    def render(self) -> None:
        """Render the dashboard."""
        self._clear_screen()
        self._draw_header()
        self._draw_agents()
        self._draw_thoughts()
        self._draw_footer()

    async def run(self) -> None:
        """Run the console dashboard."""
        print("Console dashboard mode (Textual not installed)")
        print("Install textual for full TUI: pip install textual")
        print()

        self.render()

        # Simple event loop
        while self.running:
            await asyncio.sleep(1)
            self.render()

    def stop(self) -> None:
        """Stop the dashboard."""
        self.running = False


# =============================================================================
# Textual Dashboard (Full TUI)
# =============================================================================

if TEXTUAL_AVAILABLE:

    class AgentListItem(ListItem):
        """List item for an agent."""

        def __init__(self, agent: AgentEntry):
            super().__init__()
            self.agent = agent

        def compose(self) -> ComposeResult:
            yield Label(self.agent.render())

    class ArtifactListItem(ListItem):
        """List item for an artifact."""

        def __init__(self, artifact: ArtifactEntry):
            super().__init__()
            self.artifact = artifact

        def compose(self) -> ComposeResult:
            yield Label(self.artifact.render())

    class AgentsPanel(Container):
        """Panel showing agent status."""

        DEFAULT_CSS = """
        AgentsPanel {
            width: 20;
            border: solid green;
        }
        AgentsPanel > Label {
            text-style: bold;
        }
        """

        def compose(self) -> ComposeResult:
            yield Label("AGENTS")
            yield ListView(id="agents-list")

    class ThoughtStreamPanel(Container):
        """Panel showing thought stream."""

        DEFAULT_CSS = """
        ThoughtStreamPanel {
            border: solid blue;
        }
        ThoughtStreamPanel > Label {
            text-style: bold;
        }
        """

        def compose(self) -> ComposeResult:
            yield Label("THOUGHT STREAM")
            yield Log(id="thought-log", max_lines=100)

    class ArtifactsPanel(Container):
        """Panel showing artifacts."""

        DEFAULT_CSS = """
        ArtifactsPanel {
            width: 18;
            border: solid yellow;
        }
        ArtifactsPanel > Label {
            text-style: bold;
        }
        """

        def compose(self) -> ComposeResult:
            yield Label("ARTIFACTS")
            yield ListView(id="artifacts-list")

    class ScrubBar(Container):
        """Scrub bar for playback control."""

        DEFAULT_CSS = """
        ScrubBar {
            height: 3;
            border: solid white;
        }
        """

        progress: reactive[float] = reactive(0.0)

        def compose(self) -> ComposeResult:
            yield Horizontal(
                Static("◀", id="scrub-back"),
                ProgressBar(id="scrub-progress", total=100),
                Static("▶", id="scrub-forward"),
            )

        def watch_progress(self, progress: float) -> None:
            """Update progress bar."""
            bar = self.query_one("#scrub-progress", ProgressBar)
            bar.update(progress=int(progress * 100))

    class CommandBar(Container):
        """Command input bar."""

        DEFAULT_CSS = """
        CommandBar {
            height: 3;
            dock: bottom;
        }
        """

        def compose(self) -> ComposeResult:
            yield Input(placeholder="> Enter command...", id="command-input")

    class DashboardApp(App):
        """The main dashboard application."""

        CSS = """
        Screen {
            layout: grid;
            grid-size: 3;
            grid-columns: 20 1fr 18;
        }

        #main-area {
            column-span: 3;
            layout: horizontal;
        }

        #bottom-bar {
            column-span: 3;
            dock: bottom;
            height: 6;
        }
        """

        BINDINGS = [
            Binding("q", "quit", "Quit"),
            Binding("left", "step_back", "Back"),
            Binding("right", "step_forward", "Forward"),
            Binding("space", "toggle_pause", "Pause"),
            Binding("s", "snapshot", "Snapshot"),
        ]

        def __init__(self, controller: DashboardController):
            super().__init__()
            self.controller = controller
            self.controller.on_event(self._on_event)

        def compose(self) -> ComposeResult:
            yield Header()
            with Horizontal(id="main-area"):
                yield AgentsPanel()
                yield ThoughtStreamPanel()
                yield ArtifactsPanel()
            with Vertical(id="bottom-bar"):
                yield ScrubBar()
                yield CommandBar()
            yield Footer()

        def on_mount(self) -> None:
            """Called when app is mounted."""
            self.title = "kgents dash"
            self._refresh_display()

        def _on_event(self, event: DashboardEvent) -> None:
            """Handle incoming event."""
            # Add to thought stream
            log = self.query_one("#thought-log", Log)
            log.write_line(f"[{event.source}] {event.message}")

            # Refresh agent list if needed
            if event.event_type in (
                EventType.AGENT_START,
                EventType.AGENT_COMPLETE,
                EventType.AGENT_FAIL,
            ):
                self._refresh_agents()

            # Refresh artifacts if needed
            if event.event_type in (
                EventType.ARTIFACT_CREATE,
                EventType.ARTIFACT_UPDATE,
            ):
                self._refresh_artifacts()

        def _refresh_display(self) -> None:
            """Refresh all panels."""
            self._refresh_agents()
            self._refresh_artifacts()
            self._refresh_thoughts()

        def _refresh_agents(self) -> None:
            """Refresh agents list."""
            if not self.controller.current_session:
                return

            agents_list = self.query_one("#agents-list", ListView)
            agents_list.clear()

            for agent in self.controller.current_session.agents.values():
                agents_list.append(AgentListItem(agent))

        def _refresh_artifacts(self) -> None:
            """Refresh artifacts list."""
            if not self.controller.current_session:
                return

            artifacts_list = self.query_one("#artifacts-list", ListView)
            artifacts_list.clear()

            for artifact in self.controller.current_session.artifacts.values():
                artifacts_list.append(ArtifactListItem(artifact))

        def _refresh_thoughts(self) -> None:
            """Refresh thought stream."""
            if not self.controller.current_session:
                return

            log = self.query_one("#thought-log", Log)
            log.clear()

            for thought in self.controller.current_session.thoughts:
                log.write_line(thought.render(show_timestamp=True))

        def action_step_back(self) -> None:
            """Step backward in playback."""
            event = self.controller.step_backward()
            if event:
                self._update_scrub_bar()

        def action_step_forward(self) -> None:
            """Step forward in playback."""
            event = self.controller.step_forward()
            if event:
                self._update_scrub_bar()

        def action_toggle_pause(self) -> None:
            """Toggle pause."""
            self.controller.toggle_pause()

        def action_snapshot(self) -> None:
            """Take a snapshot."""
            if self.controller.current_session:
                self.controller.add_event(
                    EventType.SNAPSHOT,
                    "user",
                    "Manual snapshot",
                )

        def _update_scrub_bar(self) -> None:
            """Update scrub bar position."""
            if self.controller.playback:
                scrub = self.query_one(ScrubBar)
                scrub.progress = self.controller.playback.progress

        async def on_input_submitted(self, event: Input.Submitted) -> None:
            """Handle command input."""
            command = event.value
            event.input.value = ""

            if command:
                self.controller.add_event(
                    EventType.USER_COMMAND,
                    "user",
                    command,
                )


# =============================================================================
# Command Entry Point
# =============================================================================


def cmd_dash(args: list[str]) -> int:
    """
    Launch the TUI dashboard.

    Usage:
        kgents dash                          # Launch live dashboard
        kgents dash --flow=<file.yaml>       # Launch with flow visualization
        kgents dash --replay=<session-id>    # Replay historical session
        kgents dash --list                   # List available sessions
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="kgents dash",
        description="TUI Dashboard - The DVR for agent execution",
    )
    parser.add_argument(
        "--flow",
        help="Flowfile to visualize",
    )
    parser.add_argument(
        "--replay",
        help="Session ID to replay",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_sessions",
        help="List available sessions",
    )
    parser.add_argument(
        "--name",
        default="Interactive",
        help="Session name (default: Interactive)",
    )

    parsed = parser.parse_args(args)

    # Initialize controller
    store = EventStore()
    controller = DashboardController(store)

    # Handle --list
    if parsed.list_sessions:
        sessions = store.list_sessions(limit=20)
        if not sessions:
            print("No sessions found.")
            return 0

        print("Available sessions:")
        print()
        for session in sessions:
            state = session.state.value
            duration = (
                f"{session.duration_seconds:.1f}s" if session.ended_at else "ongoing"
            )
            flow = f" ({session.flow_name})" if session.flow_name else ""
            print(f"  {session.id}  [{state}]  {session.name}{flow}  ({duration})")
        print()
        print("Use 'kgents dash --replay=<session-id>' to replay a session.")
        return 0

    # Handle --replay
    if parsed.replay:
        session = controller.load_session(parsed.replay)
        if not session:
            print(f"Session not found: {parsed.replay}")
            return 1
        print(f"Replaying session: {session.name}")
    else:
        # Start new live session
        flow_name = None
        flow_path = None

        if parsed.flow:
            flow_path = Path(parsed.flow)
            if not flow_path.exists():
                print(f"Flow file not found: {parsed.flow}")
                return 1
            flow_name = flow_path.stem

        controller.start_session(
            name=parsed.name,
            flow_name=flow_name,
            flow_path=flow_path,
        )

    # Launch dashboard
    if TEXTUAL_AVAILABLE:
        app = DashboardApp(controller)
        app.run()
    else:
        print("Textual not installed. Using console mode.")
        print("For full TUI experience: pip install textual")
        print()

        console = ConsoleDashboard(controller)
        try:
            asyncio.run(console.run())
        except KeyboardInterrupt:
            console.stop()

    # End session if live
    if (
        controller.current_session
        and controller.current_session.state == SessionState.LIVE
    ):
        controller.end_session()

    return 0


# =============================================================================
# Session Management Commands
# =============================================================================


def cmd_session(args: list[str]) -> int:
    """
    Manage dashboard sessions.

    Usage:
        kgents session list                    # List sessions
        kgents session start --name=<name>     # Start a named session
        kgents session attach <id>             # Attach to a session
        kgents session end <id>                # End a session
        kgents session export <id> --format=flow  # Export as flowfile
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="kgents session",
        description="Manage dashboard sessions",
    )
    subparsers = parser.add_subparsers(dest="action")

    # list
    list_parser = subparsers.add_parser("list", help="List sessions")
    list_parser.add_argument(
        "--state", choices=["live", "ended"], help="Filter by state"
    )
    list_parser.add_argument("--limit", type=int, default=20, help="Max results")

    # start
    start_parser = subparsers.add_parser("start", help="Start a session")
    start_parser.add_argument("--name", required=True, help="Session name")

    # attach
    attach_parser = subparsers.add_parser("attach", help="Attach to a session")
    attach_parser.add_argument("session_id", help="Session ID")

    # end
    end_parser = subparsers.add_parser("end", help="End a session")
    end_parser.add_argument("session_id", help="Session ID")

    # export
    export_parser = subparsers.add_parser("export", help="Export a session")
    export_parser.add_argument("session_id", help="Session ID")
    export_parser.add_argument("--format", choices=["flow", "json"], default="json")

    parsed = parser.parse_args(args)
    store = EventStore()

    if parsed.action == "list":
        state = SessionState(parsed.state) if parsed.state else None
        sessions = store.list_sessions(state=state, limit=parsed.limit)

        if not sessions:
            print("No sessions found.")
            return 0

        for session in sessions:
            print(f"{session.id}  [{session.state.value}]  {session.name}")
        return 0

    elif parsed.action == "start":
        session = store.create_session(name=parsed.name)
        print(f"Started session: {session.id}")
        return 0

    elif parsed.action == "end":
        store.end_session(parsed.session_id)
        print(f"Ended session: {parsed.session_id}")
        return 0

    elif parsed.action == "export":
        session = store.get_session(parsed.session_id)
        if not session:
            print(f"Session not found: {parsed.session_id}")
            return 1

        if parsed.format == "json":
            import json

            print(json.dumps(session.to_dict(), indent=2))
        else:
            # Export as flowfile (simplified)
            print("# Exported from session:", session.id)
            print("version: '1.0'")
            print(f"name: '{session.name}'")
            print("steps:")
            for agent in session.agents.values():
                print(f"  - id: {agent.id}")
                print(f"    genus: {agent.genus}")
        return 0

    else:
        parser.print_help()
        return 0
