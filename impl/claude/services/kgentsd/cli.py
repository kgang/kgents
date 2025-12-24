"""
kgentsd: The Witness Daemon CLI.

"The ghost is not a haunting—it's a witnessing that becomes a doing."

Commands:
    kgentsd summon    - Awaken the Witness (foreground with TUI)
    kgentsd release   - Release the Witness gracefully
    kgentsd status    - Show current Witness state
    kgentsd thoughts  - View recent thought stream
    kgentsd ask       - Direct query to the Witness

The Witness daemon differs from `kg witness`:
- `kg witness` is transactional (invoke AGENTESE, get result, exit)
- `kgentsd` is a presence (runs continuously, shows thought stream)

See: plans/kgentsd-presence.md
"""

from __future__ import annotations

import asyncio
import os
import signal
import sys
from pathlib import Path
from typing import Any

from services.witness.polynomial import WITNESS_POLYNOMIAL, TrustLevel, WitnessState

from .daemon import (
    WATCHER_TYPES,
    DaemonConfig,
    check_daemon_status,
    get_daemon_status,
    start_daemon,
    stop_daemon,
)
from .workflows import WORKFLOW_REGISTRY

# =============================================================================
# Version & Help
# =============================================================================

__version__ = "0.2.0"

HELP_TEXT = """\
kgentsd - The Witness Daemon

USAGE:
  kgentsd summon [OPTIONS]    Awaken the Witness (start daemon)
  kgentsd banish [OPTIONS]    Banish the Witness (stop daemon)
  kgentsd release             Release the Witness (alias for banish)
  kgentsd status [--trust]    Show Witness state + trust metrics + pool stats
  kgentsd thoughts [--limit N]  View thought stream
  kgentsd ask "..."           Direct query

SUMMON OPTIONS:
  --watchers TYPES    Comma-separated: git,filesystem,test,agentese,ci
  --all               Enable all watchers
  -b, --background    Run in background (no TUI)
  -f, --foreground    Run in foreground (for debugging)

BANISH OPTIONS:
  --force, -f         Force kill (SIGKILL instead of SIGTERM)

WATCHERS:
  git        Git operations (commits, pushes, checkouts)
  filesystem File changes (create, modify, delete)
  test       pytest results
  agentese   Cross-jewel events
  ci         GitHub Actions (requires --github-owner, --github-repo)

EXAMPLES:
  $ kgentsd summon                          # Start with git watcher (default)
  $ kgentsd summon --watchers git,test      # Git + test watchers
  $ kgentsd summon --all -b                 # All watchers, background
  $ kgentsd summon -f                       # Foreground mode (debug)
  $ kgentsd status                          # Check if running
  $ kgentsd status --json                   # Machine-readable status
  $ kgentsd banish                          # Graceful stop
  $ kgentsd banish --force                  # Force kill
  $ kgentsd thoughts --limit 20             # Recent thoughts
  $ kgentsd ask "what should I work on?"    # Ask the Witness

ARCHITECTURE:
  The daemon provides:
  • Multi-processing for CPU-bound tasks (LLM, crystallization)
  • Multi-threading for I/O-bound tasks (database, file I/O)
  • PTY support for interactive commands (soul reflect, etc.)
  • Trust-gated operations via ActionGate
  • Audit trail for all CLI activity

TRUST LEVELS:
  L0 READ_ONLY   - Observe and project
  L1 BOUNDED     - Write to .kgents/ only
  L2 SUGGESTION  - Propose changes (requires confirmation)
  L3 AUTONOMOUS  - Full developer agency

For more: https://github.com/kgents/kgents
"""

# =============================================================================
# Rich Console Output
# =============================================================================


def _get_console() -> Any:
    """Get Rich console for pretty output."""
    try:
        from rich.console import Console

        return Console()
    except ImportError:
        return None


def _print_awakening(config: DaemonConfig, trust_level: TrustLevel) -> None:
    """Print the awakening message with rich formatting."""
    console = _get_console()

    # Watcher status with checkmarks
    watcher_status = []
    for w in WATCHER_TYPES:
        if w in config.enabled_watchers:
            watcher_status.append(f"{w} ✓")
        else:
            watcher_status.append(f"[dim]{w}[/dim]")

    workflow_count = len(WORKFLOW_REGISTRY)

    if console:
        from rich.panel import Panel
        from rich.text import Text

        # Build awakening message
        lines = [
            "",
            f"   Trust Level: {trust_level.emoji} {trust_level.description}",
            f"   Watchers: {' '.join(watcher_status[:3])}",
            f"   Workflows: {workflow_count} templates ready",
            "",
            "   Listening. Learning. Ready to help.",
            "",
            "   [dim]Press Ctrl+C to release[/dim]",
        ]

        content = Text.from_markup("\n".join(lines))
        panel = Panel(
            content,
            title="[bold magenta]🔮 Witness awakening...[/bold magenta]",
            border_style="magenta",
            padding=(0, 2),
        )
        console.print(panel)
    else:
        # Fallback to plain text
        print("\n🔮 Witness awakening...")
        print(f"   Trust Level: {trust_level.emoji} {trust_level.description}")
        print(f"   Watchers: {', '.join(w for w in config.enabled_watchers)}")
        print(f"   Workflows: {workflow_count} templates ready")
        print()
        print("   Listening. Learning. Ready to help.")
        print()
        print("   Press Ctrl+C to release")
        print()


def _print_thought(thought: Any) -> None:
    """Print a thought with timestamp and emoji."""
    console = _get_console()

    # Source to emoji mapping
    source_emoji = {
        "git": "📝",
        "filesystem": "📁",
        "tests": "🧪",
        "agentese": "🔮",
        "ci": "🏗️",
        "witness": "💭",
        "manual": "✍️",
    }

    emoji = source_emoji.get(thought.source, "💡")
    timestamp = thought.timestamp.strftime("%H:%M") if thought.timestamp else "??:??"

    if console:
        console.print(f"   {timestamp} {emoji} {thought.content}")
    else:
        print(f"   {timestamp} {emoji} {thought.content}")


def _print_status(status: dict[str, Any]) -> None:
    """Print daemon status."""
    console = _get_console()

    running = status.get("running", False)
    pid = status.get("pid")
    watchers = status.get("enabled_watchers", [])
    socket_path = status.get("socket_path", "unknown")
    socket_active = status.get("socket_active", False)

    if console:
        from rich.panel import Panel
        from rich.text import Text

        if running:
            # Socket status
            if socket_active:
                socket_status = "[green]● active[/green]"
            else:
                socket_status = "[yellow]○ inactive[/yellow]"

            lines = [
                f"[green]● Running[/green] (PID: {pid})",
                f"Socket: {socket_path} {socket_status}",
                f"Watchers: {', '.join(watchers)}",
                f"Log: {status.get('log_file', 'unknown')}",
            ]
        else:
            lines = [
                "[yellow]○ Not running[/yellow]",
                "",
                "[dim]Run `kgentsd summon` to awaken the Witness[/dim]",
            ]

        panel = Panel(
            Text.from_markup("\n".join(lines)),
            title="Witness Status",
            border_style="cyan" if running else "yellow",
        )
        console.print(panel)
    else:
        if running:
            socket_indicator = "●" if socket_active else "○"
            print(f"● Running (PID: {pid})")
            print(f"  Socket: {socket_path} ({socket_indicator})")
            print(f"  Watchers: {', '.join(watchers)}")
        else:
            print("○ Not running")
            print("  Run `kgentsd summon` to awaken the Witness")


# =============================================================================
# Command Handlers
# =============================================================================


def cmd_summon(args: list[str]) -> int:
    """
    Summon the Witness daemon (foreground mode with TUI).

    This is the primary kgentsd experience—a continuous presence
    that shows the thought stream in real-time.
    """
    # Parse arguments
    watchers: tuple[str, ...] = ("git",)  # Default
    background = False
    use_all = False

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--watchers" and i + 1 < len(args):
            watchers = tuple(args[i + 1].split(","))
            i += 2
        elif arg.startswith("--watchers="):
            watchers = tuple(arg.split("=", 1)[1].split(","))
            i += 1
        elif arg in ("--background", "-b"):
            background = True
            i += 1
        elif arg in ("--all", "-a"):
            use_all = True
            i += 1
        elif arg in ("--help", "-h"):
            print("kgentsd summon - Awaken the Witness")
            print()
            print("Options:")
            print("  --watchers TYPES  Comma-separated watcher types")
            print("  --all, -a         Enable all watchers")
            print("  --background, -b  Run in background (no TUI)")
            print()
            print("Watcher types:", ", ".join(sorted(WATCHER_TYPES)))
            return 0
        else:
            i += 1

    # --all overrides --watchers
    if use_all:
        watchers = tuple(sorted(WATCHER_TYPES))

    # Validate watchers
    for w in watchers:
        if w not in WATCHER_TYPES:
            print(f"Unknown watcher type: {w}")
            print(f"Valid types: {', '.join(WATCHER_TYPES)}")
            return 1

    # Check if already running
    is_running, existing_pid = check_daemon_status()
    if is_running:
        print(f"Witness already running (PID: {existing_pid})")
        print("Use `kgentsd release` to stop it first, or `kgentsd status` for details")
        return 1

    # Create config
    config = DaemonConfig(
        enabled_watchers=watchers,
        repo_path=Path.cwd(),
    )

    if background:
        # Background mode: use existing daemon spawning
        pid = start_daemon(config)
        print(f"🔮 Witness awakened in background (PID: {pid})")
        print("   Use `kgentsd status` to check, `kgentsd release` to stop")
        return 0

    # Foreground mode: run with TUI
    try:
        return _run_foreground(config)
    except KeyboardInterrupt:
        print("\n🌙 Witness released. Until next time.")
        return 0


def _run_foreground(config: DaemonConfig) -> int:
    """Run the daemon in foreground with TUI thought stream."""
    # Get initial trust level (could query persistence, but default to L0)
    trust_level = TrustLevel.READ_ONLY

    # Print awakening message
    _print_awakening(config, trust_level)

    # Try to use Textual TUI if available
    try:
        from .tui import run_witness_tui

        return run_witness_tui(config)
    except ImportError:
        # Fallback to simple console output
        return _run_simple_foreground(config)


def _run_simple_foreground(config: DaemonConfig) -> int:
    """Fallback foreground mode without Textual."""
    from .daemon import WitnessDaemon, event_to_thought

    daemon = WitnessDaemon(config)

    # Override the thought sending to print to console
    original_send = daemon._send_thought

    async def print_thought(thought: Any) -> None:
        _print_thought(thought)
        await original_send(thought)

    daemon._send_thought = print_thought  # type: ignore

    # Run the daemon
    try:
        asyncio.run(daemon.start())
        return 0
    except KeyboardInterrupt:
        return 0


def cmd_banish(args: list[str]) -> int:
    """
    Banish the Witness daemon (stop).

    Options:
        --force, -f    Force kill (SIGKILL instead of SIGTERM)
    """
    if "--help" in args or "-h" in args:
        print("kgentsd banish - Banish the Witness")
        print()
        print("Gracefully stops the running Witness daemon.")
        print()
        print("Options:")
        print("  --force, -f    Force kill (SIGKILL instead of SIGTERM)")
        return 0

    force = "--force" in args or "-f" in args
    config = DaemonConfig()

    is_running, pid = check_daemon_status(config)
    if not is_running or pid is None:
        console = _get_console()
        if console:
            console.print("[yellow]Witness was not running.[/yellow]")
        else:
            print("Witness was not running.")
        return 0

    import signal

    try:
        if force:
            os.kill(pid, signal.SIGKILL)
            action = "Force killed"
        else:
            os.kill(pid, signal.SIGTERM)
            action = "Sent SIGTERM to"

        # Wait for process to exit
        import time
        from .daemon import is_process_running, remove_pid_file

        for _ in range(50):  # 5 seconds
            if not is_process_running(pid):
                break
            time.sleep(0.1)

        if is_process_running(pid):
            if not force:
                console = _get_console()
                if console:
                    console.print("[yellow]Process didn't exit gracefully, sending SIGKILL...[/yellow]")
                else:
                    print("Process didn't exit gracefully, sending SIGKILL...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)

        # Clean up PID file
        remove_pid_file(config.pid_file)

        console = _get_console()
        if console:
            console.print(f"[green]🌙 Witness banished. {action} PID {pid}.[/green]")
        else:
            print(f"🌙 Witness banished. {action} PID {pid}.")
        return 0

    except OSError as e:
        console = _get_console()
        if console:
            console.print(f"[red]Failed to stop daemon: {e}[/red]")
        else:
            print(f"Failed to stop daemon: {e}")
        return 1


def cmd_release(args: list[str]) -> int:
    """Release the Witness daemon gracefully (alias for banish)."""
    return cmd_banish(args)


def cmd_status(args: list[str]) -> int:
    """Show current Witness daemon status."""
    if "--help" in args or "-h" in args:
        print("kgentsd status - Show Witness state")
        print()
        print("Displays daemon status and trust metrics.")
        print()
        print("Options:")
        print("  --trust  Show detailed trust escalation progress")
        print("  --json   Machine-readable JSON output")
        return 0

    show_trust = "--trust" in args
    json_output = "--json" in args

    # Get daemon status
    status = get_daemon_status()

    # Add socket responsiveness check
    if status["running"]:
        try:
            from .socket_client import is_daemon_available
            status["socket_responsive"] = is_daemon_available()
        except Exception:
            status["socket_responsive"] = status["socket_active"]
    else:
        status["socket_responsive"] = False

    if json_output:
        import json as json_module
        print(json_module.dumps(status, indent=2))
        return 0

    _print_status(status)

    # Phase 4C: Always show trust metrics
    _print_trust_status(show_trust)

    return 0


def _print_trust_status(detailed: bool = False) -> None:
    """Print trust status from persistence."""
    console = _get_console()

    try:
        from services.kgentsd.trust_persistence import TrustPersistence

        persistence = TrustPersistence()
        state = persistence._load_sync()  # Sync load for CLI
        status = persistence.get_status()

        trust_level = status["trust_emoji"] + " " + status["trust_description"]
        obs_count = status["observation_count"]
        ops_count = status["successful_operations"]
        acceptance = status["acceptance_rate"]
        progress = status["escalation_progress"]

        if console:
            from rich.panel import Panel
            from rich.progress import BarColumn, Progress, TextColumn
            from rich.table import Table
            from rich.text import Text

            # Build trust info table
            table = Table.grid(padding=(0, 2))
            table.add_column(style="dim")
            table.add_column()

            table.add_row("Trust Level:", trust_level)
            table.add_row("Observations:", str(obs_count))
            table.add_row("Operations:", str(ops_count))
            table.add_row("Acceptance Rate:", acceptance)

            if status.get("last_active"):
                from datetime import datetime

                try:
                    last = datetime.fromisoformat(status["last_active"])
                    ago = datetime.now() - last
                    if ago.days > 0:
                        last_str = f"{ago.days}d ago"
                    elif ago.seconds > 3600:
                        last_str = f"{ago.seconds // 3600}h ago"
                    else:
                        last_str = f"{ago.seconds // 60}m ago"
                    table.add_row("Last Active:", last_str)
                except Exception:
                    pass

            # Progress toward next level
            next_level = progress.get("next_level")
            if next_level:
                overall = progress.get("overall_progress", 0)
                bar_filled = int(overall * 20)
                bar_empty = 20 - bar_filled
                # Note: parentheses needed for correct string concatenation
                progress_bar = (
                    "[green]" + ("█" * bar_filled) + "[/green][dim]" + ("░" * bar_empty) + "[/dim]"
                )

                table.add_row("", "")  # spacer
                table.add_row("Next Level:", next_level)
                table.add_row("Progress:", progress_bar + f" {overall:.0%}")

                # Detailed progress if requested
                if detailed:
                    if "observations_needed" in progress:
                        table.add_row(
                            "  Observations needed:", str(progress["observations_needed"])
                        )
                    if "hours_remaining" in progress:
                        table.add_row("  Hours remaining:", f"{progress['hours_remaining']:.1f}h")
                    if "operations_needed" in progress:
                        table.add_row("  Operations needed:", str(progress["operations_needed"]))
                    if "suggestions_needed" in progress:
                        table.add_row("  Suggestions needed:", str(progress["suggestions_needed"]))
                    if "acceptance_needed" in progress:
                        table.add_row(
                            "  Acceptance needed:", f"{progress['acceptance_needed']:.0%}"
                        )

            panel = Panel(
                table,
                title="[bold cyan]Trust Metrics[/bold cyan]",
                border_style="cyan",
                padding=(0, 2),
            )
            console.print(panel)

        else:
            # Plain text fallback
            print()
            print("Trust Metrics:")
            print(f"  Trust Level: {trust_level}")
            print(f"  Observations: {obs_count}")
            print(f"  Operations: {ops_count}")
            print(f"  Acceptance: {acceptance}")
            if next_level:
                print(f"  Next Level: {next_level}")
                print(f"  Progress: {progress.get('overall_progress', 0):.0%}")

    except Exception as e:
        if console:
            console.print(f"[dim]Trust metrics unavailable: {e}[/dim]")
        else:
            print(f"Trust metrics unavailable: {e}")


def cmd_thoughts(args: list[str]) -> int:
    """View recent thought stream."""
    limit = 20

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--limit" and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                print(f"Invalid limit: {args[i + 1]}")
                return 1
            i += 2
        elif arg.startswith("--limit="):
            try:
                limit = int(arg.split("=", 1)[1])
            except ValueError:
                print(f"Invalid limit: {arg}")
                return 1
            i += 1
        elif arg in ("--help", "-h"):
            print("kgentsd thoughts - View thought stream")
            print()
            print("Options:")
            print("  --limit N  Number of thoughts to show (default: 20)")
            return 0
        else:
            i += 1

    # Query thoughts via AGENTESE
    try:
        import asyncio

        from protocols.agentese.logos import Logos
        from protocols.agentese.node import Observer

        async def get_thoughts() -> Any:
            logos = Logos()
            observer = Observer.guest()
            result = await logos.invoke("self.witness.thoughts", observer, limit=limit)
            return result

        result = asyncio.run(get_thoughts())

        console = _get_console()
        if console and hasattr(result, "to_text"):
            console.print(result.to_text())
        elif hasattr(result, "thoughts"):
            for t in result.thoughts:
                _print_thought(t)
        else:
            print(result)

        return 0

    except Exception as e:
        print(f"Error fetching thoughts: {e}")
        print("Is the gateway running? Try: uvicorn protocols.api.app:create_app --factory")
        return 1


def cmd_ask(args: list[str]) -> int:
    """Ask the Witness a direct question."""
    if "--help" in args or "-h" in args:
        print("kgentsd ask - Direct query to the Witness")
        print()
        print('Usage: kgentsd ask "your question here"')
        print()
        print("Examples:")
        print('  kgentsd ask "what should I work on?"')
        print('  kgentsd ask "summarize today\'s activity"')
        return 0

    if not args:
        print('Usage: kgentsd ask "your question"')
        return 1

    question = " ".join(args)

    # TODO: Wire to K-gent for personality + Memory + Gestalt for context
    # For now, show a placeholder
    console = _get_console()

    if console:
        from rich.panel import Panel

        console.print(
            Panel(
                "[dim]Coming in Phase 4C: The Conversation[/dim]\n\n"
                f"You asked: {question}\n\n"
                "[dim]This will integrate K-gent (personality), Memory (context),\n"
                "and Gestalt (code awareness) for context-aware responses.[/dim]",
                title="💭 Witness",
                border_style="magenta",
            )
        )
    else:
        print("Coming in Phase 4C: The Conversation")
        print(f"You asked: {question}")

    return 0


# =============================================================================
# Main Entry Point
# =============================================================================


def main(argv: list[str] | None = None) -> int:
    """Main entry point for kgentsd CLI."""
    if argv is None:
        argv = sys.argv[1:]

    args = list(argv)

    # No command given
    if not args:
        print(HELP_TEXT)
        return 0

    command = args[0]
    command_args = args[1:]

    # Route to handlers
    handlers = {
        "summon": cmd_summon,
        "banish": cmd_banish,
        "release": cmd_release,
        "status": cmd_status,
        "thoughts": cmd_thoughts,
        "ask": cmd_ask,
        # Aliases
        "start": cmd_summon,
        "stop": cmd_banish,
    }

    if command in ("--help", "-h"):
        print(HELP_TEXT)
        return 0

    if command == "--version":
        print(f"kgentsd {__version__}")
        return 0

    handler = handlers.get(command)
    if handler is None:
        print(f"Unknown command: {command}")
        print()
        print("Available commands: summon, release, status, thoughts, ask")
        print("Run `kgentsd --help` for more information.")
        return 1

    return handler(command_args)


if __name__ == "__main__":
    sys.exit(main())
