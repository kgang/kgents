"""
Witness Handler: CLI for everyday mark-making.

"Every action leaves a mark. The mark IS the witness."

This is the UX layer for the Witness Crown Jewel. It provides:
- `kg witness mark "action"` - Create a mark (the core habit)
- `kg witness show` - View recent marks
- `kg witness session` - View current session's marks

The km alias is recommended for daily use:
- `km "Did a thing"` - Quick mark (2 keystrokes)
- `km "Chose X" -w "Because Y"` - With reasoning
- `km "Used pattern" -p composable` - With principles

See: spec/protocols/witness-supersession.md
See: plans/witness-fusion-ux-design.md
"""

from __future__ import annotations

import sys
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# =============================================================================
# Rich Console Helpers
# =============================================================================


def _get_console() -> Any:
    """Get Rich console for pretty output."""
    try:
        from rich.console import Console

        return Console()
    except ImportError:
        return None


def _print_mark(mark: dict[str, Any], verbose: bool = False) -> None:
    """Print a single mark."""
    console = _get_console()

    # Extract fields
    timestamp = mark.get("timestamp", "")
    action = mark.get("action", mark.get("response", {}).get("content", ""))
    reasoning = mark.get("reasoning", "")
    principles = mark.get("principles", mark.get("tags", []))
    mark_id = mark.get("id", mark.get("mark_id", ""))[:12]

    # Format timestamp
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        ts_str = dt.strftime("%H:%M")
    except (ValueError, AttributeError):
        ts_str = "??:??"

    if console:
        # Rich output
        principle_str = " ".join(f"[dim][{p}][/dim]" for p in principles) if principles else ""
        line = f"  [dim]{ts_str}[/dim]  {action}"
        if principle_str:
            line += f" {principle_str}"
        console.print(line)

        if verbose and reasoning:
            console.print(f"         [dim]-> {reasoning}[/dim]")
    else:
        # Plain text
        line = f"  {ts_str}  {action}"
        if principles:
            line += f" [{', '.join(principles)}]"
        print(line)
        if verbose and reasoning:
            print(f"         -> {reasoning}")


def _print_marks(
    marks: list[dict[str, Any]], title: str = "Recent Marks", verbose: bool = False
) -> None:
    """Print a list of marks."""
    console = _get_console()

    if not marks:
        if console:
            console.print("[dim]No marks found.[/dim]")
        else:
            print("No marks found.")
        return

    if console:
        console.print(f"\n[bold]{title}[/bold]")
        console.print("[dim]" + "─" * 40 + "[/dim]")
    else:
        print(f"\n{title}")
        print("─" * 40)

    for mark in marks:
        _print_mark(mark, verbose=verbose)

    if console:
        console.print()
    else:
        print()


# =============================================================================
# Mark Operations (D-gent Backed Persistence)
# =============================================================================


async def _create_mark_async(
    action: str,
    reasoning: str | None = None,
    principles: list[str] | None = None,
    author: str = "kent",
) -> dict[str, Any]:
    """Create and store a mark using D-gent backed persistence."""
    from services.providers import get_witness_persistence

    persistence = await get_witness_persistence()
    result = await persistence.save_mark(
        action=action,
        reasoning=reasoning,
        principles=principles or [],
        author=author,
    )

    return {
        "mark_id": result.mark_id,
        "action": result.action,
        "reasoning": result.reasoning,
        "principles": result.principles,
        "timestamp": result.timestamp.isoformat(),
        "author": result.author,
    }


async def _get_recent_marks_async(limit: int = 20) -> list[dict[str, Any]]:
    """Get recent marks from D-gent backed storage."""
    from services.providers import get_witness_persistence

    persistence = await get_witness_persistence()
    marks = await persistence.get_marks(limit=limit)

    return [
        {
            "id": m.mark_id,
            "action": m.action,
            "reasoning": m.reasoning or "",
            "principles": m.principles,
            "timestamp": m.timestamp.isoformat(),
            "author": m.author,
        }
        for m in marks
    ]


def _create_mark(
    action: str,
    reasoning: str | None = None,
    principles: list[str] | None = None,
    author: str = "kent",
) -> dict[str, Any]:
    """Sync wrapper for mark creation."""
    import asyncio

    return asyncio.run(_create_mark_async(action, reasoning, principles, author))


def _get_recent_marks(limit: int = 20) -> list[dict[str, Any]]:
    """Sync wrapper for getting recent marks."""
    import asyncio

    return asyncio.run(_get_recent_marks_async(limit))


# =============================================================================
# Subcommand Handlers
# =============================================================================


def cmd_mark(args: list[str]) -> int:
    """
    Create a mark.

    Usage:
        kg witness mark "Did a thing"
        kg witness mark "Chose X" -w "Because Y"
        kg witness mark "Pattern" -p composable,generative
    """
    if not args:
        print('Usage: kg witness mark "action" [-w reason] [-p principles]')
        return 1

    # Parse arguments
    action = None
    reasoning = None
    principles: list[str] = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-w", "--why", "--reasoning") and i + 1 < len(args):
            reasoning = args[i + 1]
            i += 2
        elif arg in ("-p", "--principles") and i + 1 < len(args):
            principles = [p.strip() for p in args[i + 1].split(",")]
            i += 2
        elif not arg.startswith("-") and action is None:
            action = arg
            i += 1
        else:
            i += 1

    if not action:
        print("Error: Action text required")
        return 1

    try:
        result = _create_mark(action, reasoning, principles)

        console = _get_console()
        if console:
            mark_id = result["mark_id"][:8]
            console.print(f"[green]\u2713[/green] {mark_id}")
            if reasoning:
                console.print(f"  [dim]\u21b3 {reasoning}[/dim]")
            if principles:
                principle_str = " ".join(f"[{p}]" for p in principles)
                console.print(f"  [dim]{principle_str}[/dim]")
        else:
            print(f"\u2713 {result['mark_id'][:8]}")
            if reasoning:
                print(f"  -> {reasoning}")

        return 0
    except Exception as e:
        print(f"Error creating mark: {e}")
        return 1


def cmd_show(args: list[str]) -> int:
    """
    Show recent marks.

    Usage:
        kg witness show
        kg witness show --limit 50
        kg witness show -v  # verbose with reasoning
    """
    limit = 20
    verbose = False

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--limit", "-l") and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg in ("--verbose", "-v"):
            verbose = True
            i += 1
        else:
            i += 1

    try:
        marks = _get_recent_marks(limit)
        _print_marks(marks, title=f"Recent Marks ({len(marks)})", verbose=verbose)
        return 0
    except Exception as e:
        print(f"Error fetching marks: {e}")
        return 1


def cmd_session(args: list[str]) -> int:
    """
    Show marks from current session.

    Usage:
        kg witness session
    """
    # For now, show recent marks (session filtering TBD)
    return cmd_show(args)


# =============================================================================
# Main Entry Point
# =============================================================================


def cmd_witness(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Witness Crown Jewel: Mark-making CLI.

    "Every action leaves a mark. The mark IS the witness."
    """
    if not args or "--help" in args or "-h" in args:
        _print_help()
        return 0

    subcommand = args[0].lower()
    sub_args = args[1:]

    handlers = {
        "mark": cmd_mark,
        "m": cmd_mark,  # alias
        "show": cmd_show,
        "recent": cmd_show,  # alias
        "list": cmd_show,  # alias
        "session": cmd_session,
    }

    handler = handlers.get(subcommand)
    if handler:
        return handler(sub_args)

    # If first arg doesn't look like a subcommand, treat as mark action
    if not subcommand.startswith("-"):
        return cmd_mark(args)

    print(f"Unknown subcommand: {subcommand}")
    _print_help()
    return 1


def _print_help() -> None:
    """Print witness command help."""
    help_text = """
kg witness - Everyday Mark-Making

"Every action leaves a mark. The mark IS the witness."

COMMANDS:
  kg witness mark "action"     Create a mark
  kg witness show              Show recent marks
  kg witness session           Show this session's marks

MARK OPTIONS:
  -w, --why "reason"          Add reasoning
  -p, --principles a,b        Add principles

SHOW OPTIONS:
  -l, --limit N               Number of marks (default: 20)
  -v, --verbose               Show reasoning

QUICK ALIAS (recommended):
  km "action"                  = kg witness mark "action"
  km "X" -w "Y"                = kg witness mark "X" -w "Y"

EXAMPLES:
  kg witness mark "Refactored DI container"
  kg witness mark "Chose PostgreSQL" -w "Scaling needs"
  kg witness mark "Used Crown Jewel pattern" -p composable,generative
  kg witness show --limit 10

PHILOSOPHY:
  Marks are the atomic unit of witness.
  An action without a mark is a reflex.
  An action with a mark is agency.

See: spec/protocols/witness-supersession.md
"""
    print(help_text.strip())


__all__ = ["cmd_witness"]
