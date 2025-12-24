"""
km: Quick Mark CLI.

"Every action leaves a mark."

This is the maximum-ergonomics interface for everyday marking.
Two keystrokes vs seven: friction matters for frequent actions.

Usage:
    km "Did a thing"                     # Minimal
    km "Chose X" -w "Because Y"          # With reasoning
    km "Pattern" -p composable           # With principles

Equivalent to:
    kg witness mark "..."

Routes through kgentsd daemon for:
- Centralized execution with daemon context
- Trust-gated operations
- Audit logging

See: plans/witness-fusion-ux-design.md
"""

from __future__ import annotations

import os
import sys


def _print_daemon_required_error() -> None:
    """Print a helpful error message when the daemon is not running."""
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console(stderr=True)
        content = (
            "[bold red]kgentsd daemon is not running[/bold red]\n\n"
            "[dim]Start the daemon:[/dim]\n"
            "  [cyan]kgentsd summon[/cyan]\n\n"
            "[dim]Or run km directly (without daemon):[/dim]\n"
            "  [cyan]KGENTS_INSIDE_DAEMON=1 km ...[/cyan]"
        )
        console.print(Panel(content, border_style="red", padding=(1, 2)))
    except ImportError:
        print("kgentsd daemon is not running.", file=sys.stderr)
        print("Start with: kgentsd summon", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    """Quick mark entry point."""
    if argv is None:
        argv = sys.argv[1:]

    # Help
    if not argv:
        print('km - Quick Mark: km "action" [-w why] [-p principles]')
        print()
        print("Examples:")
        print('  km "Refactored DI container"')
        print('  km "Chose PostgreSQL" -w "Scaling needs"')
        print('  km "Used Crown Jewel" -p composable,generative')
        return 0

    # Route through daemon unless already inside daemon
    if not os.environ.get("KGENTS_INSIDE_DAEMON"):
        try:
            from services.kgentsd.socket_client import (
                DaemonConnectionError,
                DaemonTimeoutError,
                is_daemon_available,
                route_command,
            )

            if is_daemon_available():
                try:
                    # Route as "witness mark ..."
                    response = route_command("witness", ["mark"] + list(argv), {})
                    if response.stdout:
                        print(response.stdout, end="")
                    if response.stderr:
                        print(response.stderr, end="", file=sys.stderr)
                    return response.exit_code
                except (DaemonConnectionError, DaemonTimeoutError) as e:
                    print(f"Error connecting to daemon: {e}", file=sys.stderr)
                    return 1
            else:
                # Daemon not running - show helpful message
                _print_daemon_required_error()
                return 1

        except ImportError:
            # Socket client not available - fall through to direct execution
            pass

    # Direct execution (inside daemon or fallback)
    from protocols.cli.handlers.witness_thin import cmd_mark

    return cmd_mark(list(argv))


if __name__ == "__main__":
    sys.exit(main())
