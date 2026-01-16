"""
Start Handler: Your starting point for kgents.

The first command new users should run. A warm invitation into the
world of tasteful, curated, ethical, joy-inducing agents.

Usage:
    kg start              Show welcome panel
    kg start --json       Machine-readable output
    kg start --help       Show this help

Design Philosophy:
    - Invitation, not manual
    - Dense but not overwhelming
    - Point to action, not documentation
    - "Simplistic, brutalistic, dense, intelligent design"

AGENTESE Path: self.start
"""

from __future__ import annotations

import json as json_module
from typing import TYPE_CHECKING, Any

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# =============================================================================
# Welcome Content
# =============================================================================

WELCOME_PANEL = """\
[bold white]kgents[/bold white] [dim]— Tasteful agents for thoughtful work[/dim]

[bold cyan]First time?[/bold cyan]
  [green]kg play[/green]          Learn by doing (5 min)
  [green]kg coffee[/green]        Morning ritual to ground your day

[bold cyan]Working on code?[/bold cyan]
  [green]kg brain[/green]         Memory — capture and recall knowledge
  [green]kg witness[/green]       Mark decisions as they happen
  [green]kg explore[/green]       Navigate your codebase with intention

[bold cyan]Need help?[/bold cyan]
  [green]kg docs[/green]          Living documentation
  [green]kg --help[/green]        All commands

[dim]Philosophy: Curated > Complete. Joy > Mere Function.[/dim]
"""

# Machine-readable version for agents/tooling
WELCOME_DATA: dict[str, Any] = {
    "version": "0.2.0",
    "message": "Welcome to kgents — Tasteful agents for thoughtful work",
    "getting_started": [
        {"command": "kg play", "description": "Interactive tutorials (5 min)"},
        {"command": "kg coffee", "description": "Morning ritual to ground your day"},
    ],
    "core_commands": [
        {"command": "kg brain", "description": "Memory — capture and recall knowledge"},
        {"command": "kg witness", "description": "Mark decisions as they happen"},
        {"command": "kg explore", "description": "Navigate codebase with intention"},
    ],
    "help": [
        {"command": "kg docs", "description": "Living documentation"},
        {"command": "kg --help", "description": "All commands"},
    ],
    "philosophy": "Curated > Complete. Joy > Mere Function.",
}


# =============================================================================
# Handler Implementation
# =============================================================================


def _print_help() -> None:
    """Print help for start command."""
    help_text = """
kg start — Your starting point for kgents

USAGE
  kg start              Show welcome panel
  kg start --json       Machine-readable output for tooling
  kg start --help       Show this help

ABOUT
  This is the first command new users should run. It provides
  a warm invitation and clear next steps without overwhelming
  with the full command list.

PHILOSOPHY
  "Daring, bold, creative, opinionated but not gaudy"

  The start command embodies kgents' commitment to taste:
  - Curated entry points, not exhaustive catalogs
  - Action-oriented, not documentation-oriented
  - Dense information, intelligent design

NEXT STEPS
  kg play      Interactive tutorials — learn by doing
  kg coffee    Morning ritual — start your day grounded
  kg --help    See all commands when you're ready
"""
    print(help_text.strip())


def _render_welcome() -> None:
    """Render the welcome panel using Rich."""
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        panel = Panel(
            WELCOME_PANEL.strip(),
            title="[bold]Welcome[/bold]",
            border_style="blue",
            padding=(1, 2),
        )
        console.print()
        console.print(panel)
        console.print()
    except ImportError:
        # Fallback without Rich
        _render_welcome_plain()


def _render_welcome_plain() -> None:
    """Render welcome without Rich (plain text fallback)."""
    print()
    print("=" * 56)
    print("  WELCOME TO KGENTS")
    print("  Tasteful agents for thoughtful work")
    print("=" * 56)
    print()
    print("First time?")
    print("  kg play          Learn by doing (5 min)")
    print("  kg coffee        Morning ritual to ground your day")
    print()
    print("Working on code?")
    print("  kg brain         Memory - capture and recall knowledge")
    print("  kg witness       Mark decisions as they happen")
    print("  kg explore       Navigate your codebase with intention")
    print()
    print("Need help?")
    print("  kg docs          Living documentation")
    print("  kg --help        All commands")
    print()
    print("Philosophy: Curated > Complete. Joy > Mere Function.")
    print()


def _emit_output(
    human: str | None,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """Emit output via dual-channel if ctx available."""
    if human:
        print(human)

    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(semantic)


@handler(
    "start",
    is_async=False,
    needs_pty=False,
    tier=1,
    description="Your starting point for kgents",
)
def cmd_start(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Welcome to kgents! Here's how to begin.

    The start command is the entry point for new users.
    It provides a warm invitation and clear next steps.

    AGENTESE Path: self.start

    Returns:
        0 on success
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("start", args)
        except ImportError:
            pass

    # Parse flags
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    json_mode = "--json" in args

    # Output
    if json_mode:
        print(json_module.dumps(WELCOME_DATA, indent=2))
    else:
        _render_welcome()

    # Emit semantic for pipelines/agents
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(WELCOME_DATA)

    return 0


__all__ = ["cmd_start"]
