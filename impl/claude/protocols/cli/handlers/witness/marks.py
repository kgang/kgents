"""
Mark operations: creating and viewing marks.

Provides:
- cmd_mark: Create a new mark
- cmd_show: Show recent marks with filtering
- cmd_session: Show current session's marks
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from .base import (
    _get_console,
    _parse_timestamp,
    _print_marks,
    _run_async_factory,
)


# =============================================================================
# Mark Operations (D-gent Backed Persistence)
# =============================================================================


async def _create_mark_async(
    action: str,
    reasoning: str | None = None,
    principles: list[str] | None = None,
    tags: list[str] | None = None,
    author: str = "kent",
    parent_mark_id: str | None = None,
) -> dict[str, Any]:
    """Create and store a mark using D-gent backed persistence."""
    from services.providers import get_witness_persistence

    persistence = await get_witness_persistence()
    result = await persistence.save_mark(
        action=action,
        reasoning=reasoning,
        principles=principles or [],
        tags=tags or [],
        author=author,
        parent_mark_id=parent_mark_id,
    )

    return {
        "mark_id": result.mark_id,
        "action": result.action,
        "reasoning": result.reasoning,
        "principles": result.principles,
        "tags": result.tags,
        "timestamp": result.timestamp.isoformat(),
        "author": result.author,
        "parent_mark_id": result.parent_mark_id,
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
            "tags": m.tags,
            "timestamp": m.timestamp.isoformat(),
            "author": m.author,
            "parent_mark_id": m.parent_mark_id,
        }
        for m in marks
    ]


# Create sync wrappers with proper bootstrapping
_create_mark = _run_async_factory(_create_mark_async)
_get_recent_marks = _run_async_factory(_get_recent_marks_async)


# =============================================================================
# Command Handlers
# =============================================================================


def cmd_mark(args: list[str]) -> int:
    """
    Create a mark.

    Usage:
        kg witness mark "Did a thing"
        kg witness mark "Chose X" -w "Because Y"
        kg witness mark "Pattern" -p composable,generative
        kg witness mark "Action" --tag eureka --tag gotcha
        kg witness mark "Action" --json  # Machine-readable output
        kg witness mark "Follow-up" --parent mark-abc123  # Create with parent
    """
    if not args:
        print(
            'Usage: kg witness mark "action" [-w reason] [-p principles] [--tag tag] [--parent mark-id] [--json]'
        )
        return 1

    # Parse arguments
    action = None
    reasoning = None
    principles: list[str] = []
    tags: list[str] = []
    parent_mark_id: str | None = None
    json_output = "--json" in args

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--json":
            i += 1
        elif arg in ("-w", "--why", "--reasoning") and i + 1 < len(args):
            reasoning = args[i + 1]
            i += 2
        elif arg in ("-p", "--principles") and i + 1 < len(args):
            principles = [p.strip() for p in args[i + 1].split(",")]
            i += 2
        elif arg in ("-t", "--tag") and i + 1 < len(args):
            # Support multiple --tag flags
            tags.append(args[i + 1].strip())
            i += 2
        elif arg == "--parent" and i + 1 < len(args):
            parent_mark_id = args[i + 1]
            i += 2
        elif not arg.startswith("-") and action is None:
            action = arg
            i += 1
        else:
            i += 1

    if not action:
        if json_output:
            print(json.dumps({"error": "Action text required"}))
        else:
            print("Error: Action text required")
        return 1

    try:
        result = _create_mark(action, reasoning, principles, tags, parent_mark_id=parent_mark_id)

        if json_output:
            # Machine-readable output for agents
            print(json.dumps(result))
        else:
            # Human-friendly output
            console = _get_console()
            if console:
                mark_id = result["mark_id"][:8]
                console.print(f"[green]\u2713[/green] {mark_id}")
                if parent_mark_id:
                    console.print(f"  [dim]\u2514\u2500 child of {parent_mark_id[:12]}[/dim]")
                if reasoning:
                    console.print(f"  [dim]\u21b3 {reasoning}[/dim]")
                if principles:
                    principle_str = " ".join(f"[{p}]" for p in principles)
                    console.print(f"  [dim]{principle_str}[/dim]")
                if tags:
                    tag_str = " ".join(f"#{t}" for t in tags)
                    console.print(f"  [dim]{tag_str}[/dim]")
            else:
                print(f"\u2713 {result['mark_id'][:8]}")
                if parent_mark_id:
                    print(f"  └─ child of {parent_mark_id[:12]}")
                if reasoning:
                    print(f"  -> {reasoning}")
                if tags:
                    print(f"  #{' #'.join(tags)}")

        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error creating mark: {e}")
        return 1


def cmd_show(args: list[str]) -> int:
    """
    Show recent marks.

    Usage:
        kg witness show
        kg witness show --limit 50
        kg witness show -v  # verbose with reasoning
        kg witness show --json  # machine-readable
        kg witness show --today --json  # today's marks as JSON
        kg witness show --grep "keyword"  # filter by content
        kg witness show --tag composable  # filter by principle
    """
    limit = 20
    verbose = False
    json_output = "--json" in args
    today_only = "--today" in args
    grep_pattern: str | None = None
    tag_filter: str | None = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--json":
            i += 1
        elif arg == "--today":
            i += 1
        elif arg in ("--limit", "-l") and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg in ("--verbose", "-v"):
            verbose = True
            i += 1
        elif arg == "--grep" and i + 1 < len(args):
            grep_pattern = args[i + 1].lower()
            i += 2
        elif arg == "--tag" and i + 1 < len(args):
            tag_filter = args[i + 1].lower()
            i += 2
        elif arg == "--since" and i + 1 < len(args):
            # Parse since as ISO date or relative (e.g., "2h", "1d")
            # For now, just skip - would need more complex parsing
            i += 2
        else:
            i += 1

    try:
        marks = _get_recent_marks(limit * 5 if grep_pattern or tag_filter else limit)

        # Apply --today filter
        if today_only:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            marks = [m for m in marks if _parse_timestamp(m.get("timestamp", "")) >= today_start]

        # Apply --grep filter
        if grep_pattern:
            marks = [
                m
                for m in marks
                if grep_pattern in m.get("action", "").lower()
                or grep_pattern in (m.get("reasoning") or "").lower()
            ]

        # Apply --tag filter
        if tag_filter:
            marks = [m for m in marks if tag_filter in [p.lower() for p in m.get("principles", [])]]

        # Re-apply limit after filtering
        marks = marks[:limit]

        if json_output:
            print(json.dumps(marks))
        else:
            _print_marks(marks, title=f"Recent Marks ({len(marks)})", verbose=verbose)
        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
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


async def cmd_session_async(args: list[str]) -> int:
    """
    Async version of cmd_session for use within async context.

    Usage:
        kg witness session
    """
    # For now, show recent marks (session filtering TBD)
    return await _cmd_show_async(args)


# =============================================================================
# Async versions for daemon mode
# =============================================================================


async def _cmd_mark_async(args: list[str]) -> int:
    """
    Async version of cmd_mark for daemon mode.

    Runs directly on daemon's event loop, avoiding event loop conflicts.
    """
    if not args:
        print(
            'Usage: kg witness mark "action" [-w reason] [-p principles] [--tag tag] [--parent mark-id] [--json]'
        )
        return 1

    # Parse arguments
    action = None
    reasoning = None
    principles: list[str] = []
    tags: list[str] = []
    parent_mark_id: str | None = None
    json_output = "--json" in args

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--json":
            i += 1
        elif arg in ("-w", "--why", "--reasoning") and i + 1 < len(args):
            reasoning = args[i + 1]
            i += 2
        elif arg in ("-p", "--principles") and i + 1 < len(args):
            principles = [p.strip() for p in args[i + 1].split(",")]
            i += 2
        elif arg in ("-t", "--tag") and i + 1 < len(args):
            tags.append(args[i + 1].strip())
            i += 2
        elif arg == "--parent" and i + 1 < len(args):
            parent_mark_id = args[i + 1]
            i += 2
        elif not arg.startswith("-") and action is None:
            action = arg
            i += 1
        else:
            i += 1

    if not action:
        if json_output:
            print(json.dumps({"error": "Action text required"}))
        else:
            print("Error: Action text required")
        return 1

    try:
        result = await _create_mark_async(action, reasoning, principles, tags, parent_mark_id=parent_mark_id)

        if json_output:
            print(json.dumps(result))
        else:
            console = _get_console()
            if console:
                mark_id = result["mark_id"][:8]
                console.print(f"[green]\u2713[/green] {mark_id}")
                if parent_mark_id:
                    console.print(f"  [dim]\u2514\u2500 child of {parent_mark_id[:12]}[/dim]")
                if reasoning:
                    console.print(f"  [dim]\u21b3 {reasoning}[/dim]")
            else:
                print(f"\u2713 {result['mark_id'][:8]}")

        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error creating mark: {e}")
        return 1


async def _cmd_show_async(args: list[str]) -> int:
    """
    Async version of cmd_show for daemon mode.

    Runs directly on daemon's event loop, avoiding event loop conflicts.
    """
    limit = 20
    verbose = False
    json_output = "--json" in args
    today_only = "--today" in args
    grep_pattern: str | None = None
    tag_filter: str | None = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--json":
            i += 1
        elif arg == "--today":
            i += 1
        elif arg in ("--limit", "-l") and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg in ("--verbose", "-v"):
            verbose = True
            i += 1
        elif arg == "--grep" and i + 1 < len(args):
            grep_pattern = args[i + 1].lower()
            i += 2
        elif arg == "--tag" and i + 1 < len(args):
            tag_filter = args[i + 1].lower()
            i += 2
        else:
            i += 1

    try:
        marks = await _get_recent_marks_async(limit * 5 if grep_pattern or tag_filter else limit)

        # Apply --today filter
        if today_only:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            marks = [m for m in marks if _parse_timestamp(m.get("timestamp", "")) >= today_start]

        # Apply --grep filter
        if grep_pattern:
            marks = [
                m
                for m in marks
                if grep_pattern in m.get("action", "").lower()
                or grep_pattern in (m.get("reasoning") or "").lower()
            ]

        # Apply --tag filter
        if tag_filter:
            marks = [m for m in marks if tag_filter in [p.lower() for p in m.get("principles", [])]]

        # Re-apply limit after filtering
        marks = marks[:limit]

        if json_output:
            print(json.dumps(marks))
        else:
            _print_marks(marks, title=f"Recent Marks ({len(marks)})", verbose=verbose)
        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error fetching marks: {e}")
        return 1


__all__ = [
    "cmd_mark",
    "cmd_show",
    "cmd_session",
    "_cmd_mark_async",
    "_cmd_show_async",
    "cmd_session_async",
]
