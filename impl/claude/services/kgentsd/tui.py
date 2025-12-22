"""
Witness TUI: Textual Terminal User Interface for kgentsd.

"The ghost is not a haunting—it's a witnessing that becomes a doing."

This module provides a rich terminal experience for the Witness daemon:
- Real-time thought stream with emoji-prefixed entries
- Status panel showing trust level, watchers, and stats
- Keyboard shortcuts for common actions
- L2 Suggestion prompt for confirmation flow (Phase 4B)

The TUI is the visible presence of the Witness—transforming
invisible infrastructure into tangible experience.

See: plans/kgentsd-presence.md
See: plans/kgentsd-phase4b-prompt.md
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Callable

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, RichLog, Static

from services.witness.polynomial import Thought, TrustLevel
from services.witness.trust.confirmation import ConfirmationResult, PendingSuggestion
from services.witness.trust.escalation import SuggestionStats

from .daemon import DaemonConfig, WitnessDaemon, event_to_thought
from .workflows import WORKFLOW_REGISTRY

# =============================================================================
# Emoji Mapping
# =============================================================================

SOURCE_EMOJI = {
    "git": "📝",
    "filesystem": "📁",
    "tests": "🧪",
    "agentese": "🔮",
    "ci": "🏗️",
    "witness": "💭",
    "manual": "✍️",
    "pattern": "💡",
}

TRUST_COLORS = {
    TrustLevel.READ_ONLY: "yellow",
    TrustLevel.BOUNDED: "cyan",
    TrustLevel.SUGGESTION: "green",
    TrustLevel.AUTONOMOUS: "magenta",
}


# =============================================================================
# Status Panel Widget
# =============================================================================


class StatusPanel(Static):
    """Status panel showing Witness state with trust escalation progress."""

    trust_level: reactive[TrustLevel] = reactive(TrustLevel.READ_ONLY)
    thought_count: reactive[int] = reactive(0)
    error_count: reactive[int] = reactive(0)
    uptime_seconds: reactive[float] = reactive(0.0)

    # Phase 4B: Suggestion metrics for trust escalation
    suggestions_accepted: reactive[int] = reactive(0)
    suggestions_total: reactive[int] = reactive(0)
    reactions_triggered: reactive[int] = reactive(0)

    def __init__(
        self,
        config: DaemonConfig,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        yield Label(id="status-content")

    def watch_trust_level(self, trust: TrustLevel) -> None:
        self._update_content()

    def watch_thought_count(self, count: int) -> None:
        self._update_content()

    def watch_error_count(self, count: int) -> None:
        self._update_content()

    def watch_uptime_seconds(self, uptime: float) -> None:
        self._update_content()

    def watch_suggestions_accepted(self, count: int) -> None:
        self._update_content()

    def watch_suggestions_total(self, count: int) -> None:
        self._update_content()

    def watch_reactions_triggered(self, count: int) -> None:
        self._update_content()

    def _update_content(self) -> None:
        """Update the status panel content."""
        trust = self.trust_level
        color = TRUST_COLORS.get(trust, "white")

        # Format uptime
        uptime = self.uptime_seconds
        if uptime < 60:
            uptime_str = f"{uptime:.0f}s"
        elif uptime < 3600:
            uptime_str = f"{uptime / 60:.0f}m"
        else:
            uptime_str = f"{uptime / 3600:.1f}h"

        # Watcher status
        watchers = " ".join(f"[green]{w}[/green]" for w in self.config.enabled_watchers)

        # Trust escalation progress
        trust_progress = self._render_trust_progress()

        # Build content
        lines = [
            f"Trust: [{color}]{trust.emoji} {trust.description}[/{color}]  {trust_progress}",
            f"Watchers: {watchers}",
            f"Thoughts: {self.thought_count} | Errors: {self.error_count} | Reactions: {self.reactions_triggered}",
            f"Uptime: {uptime_str} | Workflows: {len(WORKFLOW_REGISTRY)}",
        ]

        # Add suggestion metrics if at L2+
        if self.trust_level >= TrustLevel.SUGGESTION and self.suggestions_total > 0:
            acceptance_rate = (
                self.suggestions_accepted / self.suggestions_total
                if self.suggestions_total > 0
                else 0
            )
            lines.append(
                f"Suggestions: {self.suggestions_accepted}/{self.suggestions_total} "
                f"accepted ({acceptance_rate:.0%})"
            )

        label = self.query_one("#status-content", Label)
        label.update("\n".join(lines))

    def _render_trust_progress(self) -> str:
        """Render trust escalation progress bar."""
        trust = self.trust_level

        if trust == TrustLevel.READ_ONLY:
            # L0 → L1: Need 24h + 100 observations
            obs_progress = min(self.thought_count / 100, 1.0)
            hours = self.uptime_seconds / 3600
            time_progress = min(hours / 24, 1.0)
            progress = min(obs_progress, time_progress)
            target = "L1"
        elif trust == TrustLevel.BOUNDED:
            # L1 → L2: Need 100 successful operations
            progress = min(self.reactions_triggered / 100, 1.0)
            target = "L2"
        elif trust == TrustLevel.SUGGESTION:
            # L2 → L3: Need 50 suggestions with >90% acceptance
            if self.suggestions_total >= 50:
                acceptance = (
                    self.suggestions_accepted / self.suggestions_total
                    if self.suggestions_total > 0
                    else 0
                )
                progress = acceptance / 0.9 if acceptance < 0.9 else 1.0
            else:
                progress = self.suggestions_total / 50
            target = "L3"
        else:
            # Already at max
            return "[green]✓ MAX[/green]"

        # Render progress bar
        filled = int(progress * 10)
        bar = "█" * filled + "░" * (10 - filled)
        color = "green" if progress >= 1.0 else "yellow" if progress >= 0.5 else "dim"
        return f"[{color}][{bar}][/{color}] → {target}"


# =============================================================================
# Thought Stream Widget
# =============================================================================


class ThoughtStream(RichLog):
    """Real-time thought stream display."""

    def add_thought(self, thought: Thought) -> None:
        """Add a thought to the stream."""
        timestamp = thought.timestamp.strftime("%H:%M") if thought.timestamp else "??:??"
        emoji = SOURCE_EMOJI.get(thought.source, "💡")

        # Color-code by source
        source_colors = {
            "git": "cyan",
            "tests": "green" if "passed" in thought.content.lower() else "red",
            "filesystem": "blue",
            "agentese": "magenta",
            "ci": "yellow",
            "witness": "white",
            "pattern": "bright_yellow",
        }
        color = source_colors.get(thought.source, "white")

        self.write(f"[dim]{timestamp}[/dim] {emoji} [{color}]{thought.content}[/{color}]")


# =============================================================================
# Suggestion Prompt Widget (Phase 4B)
# =============================================================================


class SuggestionPrompt(Static):
    """
    L2 confirmation prompt with keyboard handling.

    Displays pending suggestions with [Y] [N] [D] [I] options:
    - Y: Accept and execute
    - N: Reject
    - D: Show diff/details
    - I: Ignore (dismiss without recording)

    "The ghost proposes, the human disposes."
    """

    class SuggestionAccepted(Message):
        """Emitted when user accepts a suggestion."""

        def __init__(self, suggestion_id: str) -> None:
            self.suggestion_id = suggestion_id
            super().__init__()

    class SuggestionRejected(Message):
        """Emitted when user rejects a suggestion."""

        def __init__(self, suggestion_id: str, reason: str = "") -> None:
            self.suggestion_id = suggestion_id
            self.reason = reason
            super().__init__()

    class SuggestionIgnored(Message):
        """Emitted when user ignores a suggestion."""

        def __init__(self, suggestion_id: str) -> None:
            self.suggestion_id = suggestion_id
            super().__init__()

    suggestion: reactive[PendingSuggestion | None] = reactive(None)
    is_visible: reactive[bool] = reactive(False)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._show_details = False

    def compose(self) -> ComposeResult:
        yield Label(id="suggestion-content")

    def watch_suggestion(self, suggestion: PendingSuggestion | None) -> None:
        """Update display when suggestion changes."""
        self.is_visible = suggestion is not None
        self._update_content()

    def watch_is_visible(self, is_visible: bool) -> None:
        """Show/hide the widget."""
        self.display = is_visible

    def _update_content(self) -> None:
        """Render the suggestion prompt."""
        if self.suggestion is None:
            return

        s = self.suggestion
        confidence_bar = self._confidence_bar(s.confidence)
        expires = s.time_remaining

        lines = [
            "",
            "[bold yellow]💡 Suggestion[/bold yellow]",
            f"[bold]{s.action}[/bold]",
            f"[dim]{s.rationale}[/dim]",
            "",
            f"Confidence: {confidence_bar} {s.confidence:.0%}",
        ]

        if self._show_details and s.preview:
            lines.extend(
                [
                    "",
                    f"[dim]Description:[/dim] {s.preview.description}",
                    f"[dim]Risk:[/dim] {s.preview.risk_level}",
                    f"[dim]Reversible:[/dim] {'Yes' if s.preview.reversible else 'No'}",
                ]
            )
            if s.preview.affected_files:
                lines.append(f"[dim]Files:[/dim] {', '.join(s.preview.affected_files[:3])}")

        lines.extend(
            [
                "",
                f"[dim]Expires in {str(expires).split('.')[0]}[/dim]",
                "",
                "[green][Y][/green] Accept  [red][N][/red] Reject  [cyan][D][/cyan] Details  [dim][I][/dim] Ignore",
            ]
        )

        label = self.query_one("#suggestion-content", Label)
        label.update("\n".join(lines))

    def _confidence_bar(self, confidence: float) -> str:
        """Render a confidence bar."""
        filled = int(confidence * 10)
        return "[green]" + "█" * filled + "[/green][dim]" + "░" * (10 - filled) + "[/dim]"

    async def on_key(self, event: Any) -> None:
        """Handle keyboard input for suggestion actions."""
        if self.suggestion is None:
            return

        key = event.key.lower() if hasattr(event, "key") else str(event)

        if key == "y":
            self.post_message(self.SuggestionAccepted(self.suggestion.id))
            self.suggestion = None
        elif key == "n":
            self.post_message(self.SuggestionRejected(self.suggestion.id))
            self.suggestion = None
        elif key == "d":
            self._show_details = not self._show_details
            self._update_content()
        elif key == "i":
            self.post_message(self.SuggestionIgnored(self.suggestion.id))
            self.suggestion = None

    def show_suggestion(self, suggestion: PendingSuggestion) -> None:
        """Display a new suggestion."""
        self._show_details = False
        self.suggestion = suggestion

    def hide(self) -> None:
        """Hide the prompt."""
        self.suggestion = None


# =============================================================================
# Main TUI App
# =============================================================================


class WitnessApp(App[None]):
    """The Witness daemon TUI application."""

    TITLE = "🔮 Witness"
    SUB_TITLE = "Listening. Learning. Ready to help."

    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 4;
        grid-rows: auto 1fr auto auto;
    }

    #status-panel {
        height: auto;
        min-height: 5;
        border: solid magenta;
        padding: 0 1;
        margin: 1 1 0 1;
    }

    #thought-stream {
        border: solid cyan;
        margin: 0 1;
    }

    #suggestion-prompt {
        height: auto;
        min-height: 0;
        border: solid yellow;
        padding: 0 1;
        margin: 0 1;
        display: none;
    }

    #suggestion-prompt.visible {
        display: block;
    }

    #help-panel {
        height: 3;
        padding: 0 1;
        margin: 0 1 1 1;
        text-align: center;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "clear", "Clear"),
        Binding("s", "status", "Status"),
        Binding("?", "help", "Help"),
        # Phase 4B: Suggestion bindings (only active when prompt visible)
        Binding("y", "accept_suggestion", "Accept", show=False),
        Binding("n", "reject_suggestion", "Reject", show=False),
        Binding("d", "toggle_details", "Details", show=False),
        Binding("i", "ignore_suggestion", "Ignore", show=False),
    ]

    def __init__(self, config: DaemonConfig, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.daemon: WitnessDaemon | None = None
        self._witness_start_time: datetime = datetime.now()
        self._thought_count = 0
        self._error_count = 0
        self._suggestions_accepted = 0
        self._suggestions_total = 0
        self._reactions_triggered = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield StatusPanel(self.config, id="status-panel")
        yield ThoughtStream(id="thought-stream", highlight=True, markup=True)
        yield SuggestionPrompt(id="suggestion-prompt")
        yield Static(
            "[dim]q[/dim] Quit  [dim]c[/dim] Clear  [dim]s[/dim] Status  [dim]?[/dim] Help",
            id="help-panel",
        )

    async def on_mount(self) -> None:
        """Start the daemon when the app mounts."""
        self._witness_start_time = datetime.now()

        # Add initial awakening thought
        stream = self.query_one("#thought-stream", ThoughtStream)
        stream.write("[bold magenta]🔮 Witness awakened[/bold magenta]")
        stream.write(f"[dim]   Watchers: {', '.join(self.config.enabled_watchers)}[/dim]")
        stream.write("[dim]   L2 suggestions enabled - [Y]/[N]/[D]/[I] to respond[/dim]")
        stream.write("")

        # Start the daemon in background
        self.daemon = WitnessDaemon(self.config)

        # Register suggestion callback for TUI display
        self.daemon.set_suggestion_callback(self._on_suggestion)

        # Override thought sending to update TUI
        original_send = self.daemon._send_thought

        async def tui_send_thought(thought: Any) -> None:
            self._add_thought(thought)
            await original_send(thought)

        self.daemon._send_thought = tui_send_thought  # type: ignore

        # Start daemon in background task
        asyncio.create_task(self._run_daemon())

        # Start uptime updater
        self.set_interval(1.0, self._update_uptime)

        # Start periodic stats sync
        self.set_interval(2.0, self._sync_daemon_stats)

    async def _on_suggestion(self, suggestion: PendingSuggestion) -> None:
        """Handle incoming suggestion from daemon."""
        # Show in thought stream
        stream = self.query_one("#thought-stream", ThoughtStream)
        stream.write("")
        stream.write(f"[bold yellow]💡 New suggestion: {suggestion.action}[/bold yellow]")
        stream.write(f"[dim]   {suggestion.rationale}[/dim]")

        # Show the suggestion prompt
        prompt = self.query_one("#suggestion-prompt", SuggestionPrompt)
        prompt.show_suggestion(suggestion)
        prompt.display = True

    def _sync_daemon_stats(self) -> None:
        """Sync stats from daemon to status panel."""
        if not self.daemon:
            return

        status = self.query_one("#status-panel", StatusPanel)
        status.reactions_triggered = self.daemon.reactions_triggered
        status.suggestions_total = self.daemon.confirmation_manager.total_submitted
        status.suggestions_accepted = self.daemon.confirmation_manager.total_confirmed

    async def _run_daemon(self) -> None:
        """Run the daemon and handle errors."""
        try:
            if self.daemon:
                await self.daemon.start()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            stream = self.query_one("#thought-stream", ThoughtStream)
            stream.write(f"[red]Error: {e}[/red]")

    def _add_thought(self, thought: Thought) -> None:
        """Add a thought to the stream and update counts."""
        stream = self.query_one("#thought-stream", ThoughtStream)
        stream.add_thought(thought)

        self._thought_count += 1
        status = self.query_one("#status-panel", StatusPanel)
        status.thought_count = self._thought_count

    def _update_uptime(self) -> None:
        """Update the uptime display."""
        uptime = (datetime.now() - self._witness_start_time).total_seconds()
        status = self.query_one("#status-panel", StatusPanel)
        status.uptime_seconds = uptime

    def action_clear(self) -> None:
        """Clear the thought stream."""
        stream = self.query_one("#thought-stream", ThoughtStream)
        stream.clear()
        stream.write("[dim]Stream cleared[/dim]")

    def action_status(self) -> None:
        """Show detailed status."""
        stream = self.query_one("#thought-stream", ThoughtStream)
        if self.daemon:
            stream.write("")
            stream.write("[bold]─── Status ───[/bold]")
            stream.write(f"Thoughts sent: {self.daemon.thoughts_sent}")
            stream.write(f"Errors: {self.daemon.errors}")
            for watcher, count in self.daemon.events_by_watcher.items():
                stream.write(f"  {watcher}: {count} events")
            stream.write("")

    def action_help(self) -> None:
        """Show help."""
        stream = self.query_one("#thought-stream", ThoughtStream)
        stream.write("")
        stream.write("[bold]─── Help ───[/bold]")
        stream.write("The Witness observes your development activity:")
        stream.write("  📝 git      - Commits, pushes, checkouts")
        stream.write("  📁 files    - File changes")
        stream.write("  🧪 tests    - Test results")
        stream.write("  🔮 agentese - Cross-jewel events")
        stream.write("  🏗️ ci       - CI/CD status")
        stream.write("")
        stream.write("Trust escalates through observation:")
        stream.write("  L0 → L1: 24h of accurate observations")
        stream.write("  L1 → L2: 100 successful operations")
        stream.write("  L2 → L3: 50 suggestions with >90% acceptance")
        stream.write("")
        stream.write("[bold]Suggestion Controls (when prompt visible):[/bold]")
        stream.write("  [green]Y[/green] Accept  - Approve and execute the suggestion")
        stream.write("  [red]N[/red] Reject  - Decline (recorded for trust metrics)")
        stream.write("  [cyan]D[/cyan] Details - Toggle detailed preview")
        stream.write("  [dim]I[/dim] Ignore  - Dismiss without recording")
        stream.write("")

    # =========================================================================
    # Suggestion Action Handlers (Phase 4B)
    # =========================================================================

    async def action_accept_suggestion(self) -> None:
        """Accept the current suggestion."""
        prompt = self.query_one("#suggestion-prompt", SuggestionPrompt)
        if prompt.suggestion and self.daemon:
            suggestion_id = prompt.suggestion.id
            action_name = prompt.suggestion.action
            stream = self.query_one("#thought-stream", ThoughtStream)

            stream.write("")
            stream.write(f"[yellow]⏳ Executing: {action_name}...[/yellow]")

            # Confirm with daemon's confirmation manager
            result = await self.daemon.confirmation_manager.confirm(
                suggestion_id,
                confirmed_by="tui-user",
            )

            if result.accepted:
                if result.executed:
                    # Phase 4C: Show detailed pipeline results
                    duration = f"{result.duration_ms:.0f}ms" if result.duration_ms else ""
                    stream.write(f"[green]✓ {action_name} completed[/green] [dim]{duration}[/dim]")

                    if result.pipeline_result:
                        # Show step details
                        pr = result.pipeline_result
                        step_count = len(pr.step_results) if hasattr(pr, "step_results") else 0
                        stream.write(f"[dim]   Pipeline: {step_count} steps executed[/dim]")

                        # Show failed step if any
                        if hasattr(pr, "error") and pr.error:
                            stream.write(f"[red]   Error: {pr.error}[/red]")

                        # Show brief step summary
                        if hasattr(pr, "step_results"):
                            for step in pr.step_results[:3]:  # Show first 3 steps
                                status = "[green]✓[/green]" if step.success else "[red]✗[/red]"
                                step_path = step.path.split(".")[-1] if step.path else "?"
                                stream.write(f"[dim]     {status} {step_path}[/dim]")
                            if len(pr.step_results) > 3:
                                stream.write(
                                    f"[dim]     ... and {len(pr.step_results) - 3} more[/dim]"
                                )
                    else:
                        stream.write(f"[dim]   {result.execution_result or 'Success'}[/dim]")

                    self._suggestions_accepted += 1

                    # Phase 4C: Record suggestion confirmation for trust metrics
                    if self.daemon._trust_persistence:
                        await self.daemon._trust_persistence.record_suggestion(confirmed=True)
                else:
                    stream.write("[yellow]⚠ Accepted but not executed[/yellow]")
                    if result.error:
                        stream.write(f"[red]   Error: {result.error}[/red]")
            else:
                stream.write(f"[red]✗ Failed to accept: {result.error}[/red]")

            self._suggestions_total += 1
            prompt.hide()
            self._update_status_metrics()

    async def action_reject_suggestion(self) -> None:
        """Reject the current suggestion."""
        prompt = self.query_one("#suggestion-prompt", SuggestionPrompt)
        if prompt.suggestion and self.daemon:
            suggestion_id = prompt.suggestion.id
            action_name = prompt.suggestion.action
            stream = self.query_one("#thought-stream", ThoughtStream)

            # Reject with daemon's confirmation manager
            result = await self.daemon.confirmation_manager.reject(
                suggestion_id,
                reason="User rejected via TUI",
            )

            stream.write("")
            stream.write(f"[red]✗ Rejected: {action_name}[/red]")

            # Phase 4C: Record suggestion rejection for trust metrics
            if self.daemon._trust_persistence:
                await self.daemon._trust_persistence.record_suggestion(confirmed=False)

            self._suggestions_total += 1
            prompt.hide()
            self._update_status_metrics()

    def action_toggle_details(self) -> None:
        """Toggle suggestion details view."""
        prompt = self.query_one("#suggestion-prompt", SuggestionPrompt)
        if prompt.suggestion:
            prompt._show_details = not prompt._show_details
            prompt._update_content()

    def action_ignore_suggestion(self) -> None:
        """Ignore the current suggestion without recording."""
        prompt = self.query_one("#suggestion-prompt", SuggestionPrompt)
        if prompt.suggestion:
            stream = self.query_one("#thought-stream", ThoughtStream)
            stream.write(f"[dim]   Ignored suggestion: {prompt.suggestion.id}[/dim]")
            prompt.hide()

    def _update_status_metrics(self) -> None:
        """Update status panel with current metrics."""
        status = self.query_one("#status-panel", StatusPanel)
        status.suggestions_accepted = self._suggestions_accepted
        status.suggestions_total = self._suggestions_total

    async def action_quit(self) -> None:
        """Quit the application gracefully."""
        stream = self.query_one("#thought-stream", ThoughtStream)
        stream.write("")
        stream.write("[bold magenta]🌙 Releasing Witness...[/bold magenta]")

        # Stop the daemon
        if self.daemon:
            self.daemon._stop_event.set()
            await asyncio.sleep(0.1)  # Brief pause for cleanup

        self.exit()


# =============================================================================
# Entry Point
# =============================================================================


def run_witness_tui(config: DaemonConfig) -> int:
    """Run the Witness TUI application."""
    app = WitnessApp(config)

    try:
        app.run()
        return 0
    except Exception as e:
        print(f"TUI error: {e}")
        return 1


__all__ = [
    "WitnessApp",
    "StatusPanel",
    "ThoughtStream",
    "SuggestionPrompt",
    "run_witness_tui",
]
