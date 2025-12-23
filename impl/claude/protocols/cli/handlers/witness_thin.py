"""
Witness Handler: CLI for everyday mark-making.

"Every action leaves a mark. The mark IS the witness."

PATTERN: Rich CLI UX layer that provides extensive formatting and interaction.
         Unlike simple handlers, this has complex custom logic that can't be
         delegated to AGENTESE router (interactive flows, tree visualization, etc.)

This is the UX layer for the Witness Crown Jewel. It provides:
- `kg witness mark "action"` - Create a mark (the core habit)
- `kg witness show` - View recent marks
- `kg witness session` - View current session's marks

The km alias is recommended for daily use:
- `km "Did a thing"` - Quick mark (2 keystrokes)
- `km "Chose X" -w "Because Y"` - With reasoning
- `km "Used pattern" -p composable` - With principles

Agent-friendly mode:
- `km "action" --json` - Machine-readable output for programmatic use
- `kg witness show --json` - Marks as JSON array
- `kg witness show --today --json` - Filter + JSON for agent queries

See: spec/protocols/witness-supersession.md
See: docs/skills/witness-for-agents.md
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
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


async def _get_mark_tree_async(
    root_mark_id: str,
    max_depth: int = 10,
) -> dict[str, Any]:
    """Get mark tree starting from root."""
    from services.providers import get_witness_persistence

    persistence = await get_witness_persistence()

    # Get the root mark first
    root = await persistence.get_mark(root_mark_id)
    if not root:
        return {"error": f"Mark not found: {root_mark_id}"}

    # Get all marks in tree
    marks = await persistence.get_mark_tree(root_mark_id, max_depth)

    # Build tree structure
    marks_by_id: dict[str, dict[str, Any]] = {}
    for m in marks:
        marks_by_id[m.mark_id] = {
            "id": m.mark_id,
            "action": m.action,
            "reasoning": m.reasoning or "",
            "principles": m.principles,
            "timestamp": m.timestamp.isoformat(),
            "author": m.author,
            "parent_mark_id": m.parent_mark_id,
            "children": [],
        }

    # Wire up children
    for m in marks:
        if m.parent_mark_id and m.parent_mark_id in marks_by_id:
            marks_by_id[m.parent_mark_id]["children"].append(marks_by_id[m.mark_id])

    return {
        "root_mark_id": root_mark_id,
        "total_marks": len(marks),
        "tree": marks_by_id.get(root_mark_id, {}),
        "flat": [
            {
                "id": m.mark_id,
                "action": m.action,
                "reasoning": m.reasoning or "",
                "principles": m.principles,
                "timestamp": m.timestamp.isoformat(),
                "author": m.author,
                "parent_mark_id": m.parent_mark_id,
            }
            for m in marks
        ],
    }


async def _get_mark_ancestry_async(mark_id: str) -> dict[str, Any]:
    """Get ancestry of a mark (parent chain to root)."""
    from services.providers import get_witness_persistence

    persistence = await get_witness_persistence()
    marks = await persistence.get_mark_ancestry(mark_id)

    if not marks:
        return {"error": f"Mark not found: {mark_id}"}

    return {
        "mark_id": mark_id,
        "depth": len(marks) - 1,
        "ancestry": [
            {
                "id": m.mark_id,
                "action": m.action,
                "reasoning": m.reasoning or "",
                "principles": m.principles,
                "timestamp": m.timestamp.isoformat(),
                "author": m.author,
                "parent_mark_id": m.parent_mark_id,
            }
            for m in marks
        ],
    }


async def _bootstrap_and_run(coro_func: Any, *args: Any, **kwargs: Any) -> Any:
    """
    Bootstrap services and run a coroutine in a fresh context.

    This ensures:
    1. Registry is reset to avoid stale connections from different event loops
    2. AGENTESE container cache is cleared to avoid stale singleton references
    3. Services are properly bootstrapped before use
    4. The coroutine runs in a clean async context

    Why this is needed:
    - CLI bootstrap runs in event loop A, creating session factory + engine
    - Handler runs in event loop B via asyncio.run()
    - Without reset, we'd try to use loop A's connections on loop B
    - This causes "Future attached to a different loop" errors
    """
    from protocols.agentese.container import reset_container
    from services.bootstrap import bootstrap_services, reset_registry

    # Reset both registry (disposes engine) and container (clears cached singletons)
    # This ensures fresh initialization on the new event loop
    reset_registry()
    reset_container()

    # Bootstrap fresh on this event loop
    await bootstrap_services()

    # Now run the actual coroutine
    return await coro_func(*args, **kwargs)


def _run_async_factory(coro_func: Any) -> Any:
    """
    Create a sync wrapper that properly bootstraps before running async code.

    Returns a function that, when called with args, will:
    1. Reset the registry
    2. Bootstrap services fresh on the new event loop
    3. Run the coroutine

    This avoids "Future attached to a different loop" and
    "another operation is in progress" errors from stale connections.
    """
    import asyncio
    from functools import wraps

    @wraps(coro_func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(_bootstrap_and_run(coro_func, *args, **kwargs))

    return wrapper


# Create sync wrappers with proper bootstrapping
_create_mark = _run_async_factory(_create_mark_async)
_get_recent_marks = _run_async_factory(_get_recent_marks_async)
_get_mark_tree = _run_async_factory(_get_mark_tree_async)
_get_mark_ancestry = _run_async_factory(_get_mark_ancestry_async)


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


def _parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp string to datetime."""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
    except (ValueError, AttributeError):
        return datetime.min


def cmd_session(args: list[str]) -> int:
    """
    Show marks from current session.

    Usage:
        kg witness session
    """
    # For now, show recent marks (session filtering TBD)
    return cmd_show(args)


# =============================================================================
# Crystal Operations (New)
# =============================================================================


async def _crystallize_async(
    level: str = "session",
    session_id: str | None = None,
    tree_root_id: str | None = None,
) -> dict[str, Any]:
    """Crystallize recent marks into a crystal."""
    from services.providers import get_witness_persistence
    from services.witness.crystal import CrystalLevel
    from services.witness.crystal_store import get_crystal_store
    from services.witness.crystallizer import Crystallizer
    from services.witness.mark import Mark
    from services.witness.persistence import WitnessPersistence

    # Get K-gent Soul for LLM
    try:
        from agents.k.soul import KgentSoul

        soul = KgentSoul()
    except Exception:
        soul = None

    crystallizer = Crystallizer(soul)
    persistence = await get_witness_persistence()

    if tree_root_id:
        # Tree-aware crystallization: crystallize marks in a causal tree
        marks_data = await persistence.get_mark_tree(tree_root_id)

        if not marks_data:
            return {"error": f"Mark tree not found: {tree_root_id}"}

        # Convert to Mark objects
        from services.witness.mark import Mark, MarkId, NPhase, Response, Stimulus

        marks = []
        for m in marks_data:
            # Build response with reasoning in metadata
            response_metadata = {"reasoning": m.reasoning} if m.reasoning else {}
            mark = Mark(
                id=MarkId(m.mark_id),
                timestamp=m.timestamp,
                origin="cli",
                stimulus=Stimulus(kind="action", content=m.action),
                response=Response(kind="mark", content=m.action, metadata=response_metadata),
                tags=tuple(m.principles),
                phase=NPhase.ACT,
            )
            marks.append(mark)

        # Crystallize with tree context (crystallizer handles context internally)
        crystal = await crystallizer.crystallize_marks(
            marks,
            session_id=session_id or "",
        )

        # Store crystal
        store = get_crystal_store()
        store.append(crystal)
        store.sync()

        return {
            "crystal_id": str(crystal.id),
            "level": crystal.level.name,
            "insight": crystal.insight,
            "significance": crystal.significance,
            "principles": list(crystal.principles),
            "source_count": crystal.source_count,
            "confidence": crystal.confidence,
            "crystallized_at": crystal.crystallized_at.isoformat(),
            "tree_root_id": tree_root_id,
        }
    elif level == "session":
        # Get recent marks that haven't been crystallized
        marks_data = await persistence.get_marks(limit=100)

        if not marks_data:
            return {"error": "No marks to crystallize"}

        # Convert to Mark objects
        from services.witness.mark import Mark, MarkId, NPhase, Response, Stimulus

        marks = []
        for m in marks_data:
            # Build response with reasoning in metadata
            response_metadata = {"reasoning": m.reasoning} if m.reasoning else {}
            mark = Mark(
                id=MarkId(m.mark_id),
                timestamp=m.timestamp,
                origin="cli",
                stimulus=Stimulus(kind="action", content=m.action),
                response=Response(kind="mark", content=m.action, metadata=response_metadata),
                tags=tuple(m.principles),
                phase=NPhase.ACT,
            )
            marks.append(mark)

        # Crystallize
        crystal = await crystallizer.crystallize_marks(marks, session_id=session_id or "")

        # Store crystal
        store = get_crystal_store()
        store.append(crystal)
        store.sync()

        return {
            "crystal_id": str(crystal.id),
            "level": crystal.level.name,
            "insight": crystal.insight,
            "significance": crystal.significance,
            "principles": list(crystal.principles),
            "source_count": crystal.source_count,
            "confidence": crystal.confidence,
            "crystallized_at": crystal.crystallized_at.isoformat(),
        }
    else:
        # Higher level crystallization (day, week, epoch)
        return {"error": f"Level '{level}' crystallization not yet implemented"}


async def _get_crystals_async(
    limit: int = 10,
    level: int | None = None,
) -> list[dict[str, Any]]:
    """Get recent crystals from store."""
    from services.witness.crystal import CrystalLevel
    from services.witness.crystal_store import get_crystal_store

    store = get_crystal_store()

    if level is not None:
        crystals = store.recent(limit, CrystalLevel(level))
    else:
        crystals = store.recent(limit)

    return [
        {
            "id": str(c.id),
            "level": c.level.name,
            "insight": c.insight,
            "significance": c.significance,
            "principles": list(c.principles),
            "topics": list(c.topics),
            "source_count": c.source_count,
            "confidence": c.confidence,
            "crystallized_at": c.crystallized_at.isoformat(),
            "duration_minutes": c.duration_minutes,
        }
        for c in crystals
    ]


async def _get_crystal_async(crystal_id: str) -> dict[str, Any] | None:
    """Get a specific crystal by ID."""
    from services.witness.crystal import CrystalId
    from services.witness.crystal_store import get_crystal_store

    store = get_crystal_store()
    crystal = store.get(CrystalId(crystal_id))

    if not crystal:
        return None

    return {
        "id": str(crystal.id),
        "level": crystal.level.name,
        "insight": crystal.insight,
        "significance": crystal.significance,
        "principles": list(crystal.principles),
        "topics": list(crystal.topics),
        "source_marks": [str(m) for m in crystal.source_marks],
        "source_crystals": [str(c) for c in crystal.source_crystals],
        "source_count": crystal.source_count,
        "mood": crystal.mood.to_dict(),
        "compression_ratio": crystal.compression_ratio,
        "confidence": crystal.confidence,
        "token_estimate": crystal.token_estimate,
        "time_range": [
            crystal.time_range[0].isoformat(),
            crystal.time_range[1].isoformat(),
        ]
        if crystal.time_range
        else None,
        "crystallized_at": crystal.crystallized_at.isoformat(),
        "session_id": crystal.session_id,
    }


async def _expand_crystal_async(crystal_id: str) -> dict[str, Any]:
    """Expand a crystal to show its sources."""
    from services.witness.crystal import CrystalId, CrystalLevel
    from services.witness.crystal_store import get_crystal_store

    store = get_crystal_store()
    crystal = store.get(CrystalId(crystal_id))

    if not crystal:
        return {"error": f"Crystal {crystal_id} not found"}

    if crystal.level == CrystalLevel.SESSION:
        # Return mark IDs
        return {
            "crystal_id": str(crystal.id),
            "level": crystal.level.name,
            "source_type": "marks",
            "sources": [str(m) for m in crystal.source_marks],
        }
    else:
        # Return source crystals with their insights
        sources = []
        for source_id in crystal.source_crystals:
            source_crystal = store.get(source_id)
            if source_crystal:
                sources.append(
                    {
                        "id": str(source_crystal.id),
                        "level": source_crystal.level.name,
                        "insight": source_crystal.insight,
                    }
                )
            else:
                sources.append({"id": str(source_id), "error": "not found"})

        return {
            "crystal_id": str(crystal.id),
            "level": crystal.level.name,
            "source_type": "crystals",
            "sources": sources,
        }


# Create sync wrappers
_crystallize = _run_async_factory(_crystallize_async)
_get_crystals = _run_async_factory(_get_crystals_async)
_get_crystal = _run_async_factory(_get_crystal_async)
_expand_crystal = _run_async_factory(_expand_crystal_async)


def cmd_crystallize(args: list[str]) -> int:
    """
    Crystallize marks into a crystal.

    Usage:
        kg witness crystallize              # Crystallize recent marks
        kg witness crystallize --level day  # Crystallize session crystals (TBD)
        kg witness crystallize --tree <id>  # Crystallize tree from root mark
        kg witness crystallize --json       # Output as JSON
    """
    level = "session"
    session_id = None
    tree_root_id = None
    json_output = "--json" in args

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--json":
            i += 1
        elif arg == "--level" and i + 1 < len(args):
            level = args[i + 1].lower()
            i += 2
        elif arg == "--session" and i + 1 < len(args):
            session_id = args[i + 1]
            i += 2
        elif arg == "--tree" and i + 1 < len(args):
            tree_root_id = args[i + 1]
            i += 2
        else:
            i += 1

    console = _get_console()

    try:
        result = _crystallize(level, session_id, tree_root_id)

        if "error" in result:
            if json_output:
                print(json.dumps(result))
            else:
                print(f"Error: {result['error']}")
            return 1

        if json_output:
            print(json.dumps(result))
        else:
            # Pretty print
            if console:
                title = "Tree Crystal Created" if tree_root_id else "Crystal Created"
                console.print(f"\n[bold green]{title}[/bold green]")
                console.print("[dim]" + "─" * 50 + "[/dim]")
                console.print(f"[bold]ID:[/bold] {result['crystal_id'][:12]}...")
                console.print(f"[bold]Level:[/bold] {result['level']}")
                if tree_root_id:
                    console.print(f"[bold]Tree Root:[/bold] {tree_root_id[:12]}...")
                console.print(f"[bold]Sources:[/bold] {result['source_count']} marks")
                console.print(f"[bold]Confidence:[/bold] {result['confidence']:.0%}")
                console.print()
                console.print("[bold]Insight:[/bold]")
                console.print(f"  {result['insight']}")
                if result["significance"]:
                    console.print("\n[bold]Significance:[/bold]")
                    console.print(f"  {result['significance']}")
                if result["principles"]:
                    console.print(f"\n[bold]Principles:[/bold] {', '.join(result['principles'])}")
                console.print()
            else:
                title = "Tree Crystal Created" if tree_root_id else "Crystal Created"
                print(f"\n{title}")
                print("─" * 50)
                print(f"ID: {result['crystal_id'][:12]}...")
                if tree_root_id:
                    print(f"Tree Root: {tree_root_id[:12]}...")
                print(f"Sources: {result['source_count']} marks")
                print(f"Insight: {result['insight']}")
                print()

        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error crystallizing: {e}")
        return 1


def cmd_crystals(args: list[str]) -> int:
    """
    List recent crystals.

    Usage:
        kg witness crystals             # Show recent crystals
        kg witness crystals --level 0   # Show only session crystals
        kg witness crystals --level 1   # Show only day crystals
        kg witness crystals --json      # Output as JSON
    """
    limit = 10
    level = None
    json_output = "--json" in args

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--json":
            i += 1
        elif arg in ("--limit", "-l") and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg == "--level" and i + 1 < len(args):
            try:
                level = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    console = _get_console()

    try:
        crystals = _get_crystals(limit, level)

        if json_output:
            print(json.dumps(crystals))
            return 0

        if not crystals:
            if console:
                console.print(
                    "[dim]No crystals found. Use 'kg witness crystallize' to create one.[/dim]"
                )
            else:
                print("No crystals found. Use 'kg witness crystallize' to create one.")
            return 0

        level_name = f"Level {level}" if level is not None else "All"
        if console:
            console.print(f"\n[bold]Crystals ({level_name})[/bold]")
            console.print("[dim]" + "─" * 60 + "[/dim]")
        else:
            print(f"\nCrystals ({level_name})")
            print("─" * 60)

        for c in crystals:
            try:
                dt = datetime.fromisoformat(c["crystallized_at"])
                ts_str = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, KeyError):
                ts_str = "???"

            insight_short = c["insight"][:60] + "..." if len(c["insight"]) > 60 else c["insight"]

            if console:
                console.print(
                    f"  [dim]{ts_str}[/dim]  "
                    f"[cyan]{c['level']}[/cyan] "
                    f"[dim]({c['source_count']} src)[/dim]  "
                    f"{insight_short}"
                )
                console.print(
                    f"         [dim]id: {c['id'][:12]}... conf: {c['confidence']:.0%}[/dim]"
                )
            else:
                print(f"  {ts_str}  {c['level']} ({c['source_count']} src)  {insight_short}")
                print(f"         id: {c['id'][:12]}...")

        if console:
            console.print()
        else:
            print()

        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error fetching crystals: {e}")
        return 1


def cmd_crystal(args: list[str]) -> int:
    """
    Show details of a specific crystal.

    Usage:
        kg witness crystal <id>
        kg witness crystal <id> --json
    """
    if not args:
        print("Usage: kg witness crystal <id> [--json]")
        return 1

    crystal_id = args[0]
    json_output = "--json" in args
    console = _get_console()

    try:
        crystal = _get_crystal(crystal_id)

        if not crystal:
            if json_output:
                print(json.dumps({"error": f"Crystal {crystal_id} not found"}))
            else:
                print(f"Crystal {crystal_id} not found")
            return 1

        if json_output:
            print(json.dumps(crystal))
            return 0

        # Pretty print
        if console:
            console.print("\n[bold]Crystal Details[/bold]")
            console.print("[dim]" + "─" * 60 + "[/dim]")
            console.print(f"[bold]ID:[/bold] {crystal['id']}")
            console.print(f"[bold]Level:[/bold] {crystal['level']}")
            console.print(f"[bold]Sources:[/bold] {crystal['source_count']}")
            console.print(f"[bold]Confidence:[/bold] {crystal['confidence']:.0%}")
            console.print(f"[bold]Tokens:[/bold] ~{crystal['token_estimate']}")
            console.print(f"[bold]Crystallized:[/bold] {crystal['crystallized_at']}")
            if crystal["time_range"]:
                console.print(
                    f"[bold]Time Range:[/bold] {crystal['time_range'][0]} to {crystal['time_range'][1]}"
                )
            console.print()
            console.print("[bold]Insight:[/bold]")
            console.print(f"  {crystal['insight']}")
            if crystal["significance"]:
                console.print("\n[bold]Significance:[/bold]")
                console.print(f"  {crystal['significance']}")
            if crystal["principles"]:
                console.print(f"\n[bold]Principles:[/bold] {', '.join(crystal['principles'])}")
            if crystal["topics"]:
                console.print(f"[bold]Topics:[/bold] {', '.join(crystal['topics'])}")
            console.print()
            console.print(f"[dim]Mood: {crystal['mood']}[/dim]")
            console.print()
        else:
            print(f"\nCrystal: {crystal['id']}")
            print("─" * 60)
            print(f"Level: {crystal['level']}")
            print(f"Insight: {crystal['insight']}")
            print(f"Significance: {crystal['significance']}")
            print()

        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        return 1


def cmd_expand(args: list[str]) -> int:
    """
    Expand a crystal to show its sources.

    Usage:
        kg witness expand <id>
        kg witness expand <id> --json
    """
    if not args:
        print("Usage: kg witness expand <id> [--json]")
        return 1

    crystal_id = args[0]
    json_output = "--json" in args
    console = _get_console()

    try:
        result = _expand_crystal(crystal_id)

        if "error" in result:
            if json_output:
                print(json.dumps(result))
            else:
                print(f"Error: {result['error']}")
            return 1

        if json_output:
            print(json.dumps(result))
            return 0

        # Pretty print
        if console:
            console.print("\n[bold]Crystal Sources[/bold]")
            console.print("[dim]" + "─" * 50 + "[/dim]")
            console.print(f"[bold]Crystal:[/bold] {result['crystal_id'][:12]}...")
            console.print(f"[bold]Level:[/bold] {result['level']}")
            console.print(f"[bold]Source Type:[/bold] {result['source_type']}")
            console.print()

            if result["source_type"] == "marks":
                console.print(f"[bold]Marks ({len(result['sources'])}):[/bold]")
                for mark_id in result["sources"][:10]:
                    console.print(f"  - {mark_id}")
                if len(result["sources"]) > 10:
                    console.print(f"  ... and {len(result['sources']) - 10} more")
            else:
                console.print(f"[bold]Source Crystals ({len(result['sources'])}):[/bold]")
                for src in result["sources"]:
                    if "error" in src:
                        console.print(f"  - [red]{src['id'][:12]}... (not found)[/red]")
                    else:
                        console.print(f"  - [cyan]{src['id'][:12]}...[/cyan] [{src['level']}]")
                        console.print(f"    {src['insight'][:60]}...")
            console.print()
        else:
            print(f"\nCrystal Sources: {result['crystal_id'][:12]}...")
            print(f"Type: {result['source_type']}")
            for src in result["sources"][:10]:
                print(f"  - {src if isinstance(src, str) else src.get('id', src)}")
            print()

        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        return 1


def cmd_context(args: list[str]) -> int:
    """
    Get budget-aware context from crystals.

    Usage:
        kg witness context                    # Default budget (2000 tokens)
        kg witness context --budget 1000      # Tighter budget
        kg witness context --query "topic"    # Relevance-weighted
        kg witness context --json             # For agents
    """
    budget = 2000
    query: str | None = None
    recency_weight = 0.7
    json_output = "--json" in args

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--json":
            i += 1
        elif arg in ("--budget", "-b") and i + 1 < len(args):
            try:
                budget = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg in ("--query", "-q") and i + 1 < len(args):
            query = args[i + 1]
            i += 2
        elif arg == "--recency-weight" and i + 1 < len(args):
            try:
                recency_weight = float(args[i + 1])
                recency_weight = max(0.0, min(1.0, recency_weight))
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    console = _get_console()

    try:
        from services.witness.context import get_context_sync

        result = get_context_sync(
            budget_tokens=budget,
            recency_weight=recency_weight,
            relevance_query=query,
        )

        if json_output:
            print(json.dumps(result.to_dict()))
            return 0

        if not result.items:
            if console:
                console.print(
                    "[dim]No crystals found. Use 'kg witness crystallize' to create some.[/dim]"
                )
            else:
                print("No crystals found. Use 'kg witness crystallize' to create some.")
            return 0

        # Pretty print
        if console:
            console.print("\n[bold]Context Query[/bold]")
            console.print("[dim]" + "─" * 60 + "[/dim]")
            console.print(
                f"  Budget: {budget} tokens | Used: {result.total_tokens} | Remaining: {result.budget_remaining}"
            )
            if query:
                console.print(f'  Query: "{query}"')
            console.print(f"  Recency weight: {recency_weight:.1f}")
            console.print()
        else:
            print("\nContext Query")
            print("─" * 60)
            print(
                f"  Budget: {budget} tokens | Used: {result.total_tokens} | Remaining: {result.budget_remaining}"
            )
            if query:
                print(f'  Query: "{query}"')
            print()

        for item in result.items:
            crystal = item.crystal
            try:
                dt = crystal.crystallized_at
                if hasattr(dt, "strftime"):
                    ts_str = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    ts_str = str(dt)
            except (ValueError, AttributeError):
                ts_str = "???"

            insight_short = (
                crystal.insight[:55] + "..." if len(crystal.insight) > 55 else crystal.insight
            )

            if console:
                score_str = f"[dim](score: {item.score:.2f})[/dim]"
                console.print(
                    f"  [cyan]{crystal.level.name}[/cyan] "
                    f"[dim]{ts_str}[/dim]  "
                    f"~{item.tokens} tok  "
                    f"{score_str}"
                )
                console.print(f"         {insight_short}")
            else:
                print(
                    f"  {crystal.level.name} {ts_str}  ~{item.tokens} tok  (score: {item.score:.2f})"
                )
                print(f"         {insight_short}")

        if console:
            console.print()
            console.print(
                f"[dim]Cumulative: {result.total_tokens}/{budget} tokens ({len(result.items)} crystals)[/dim]"
            )
            console.print()
        else:
            print()
            print(
                f"Cumulative: {result.total_tokens}/{budget} tokens ({len(result.items)} crystals)"
            )
            print()

        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        return 1


# =============================================================================
# Phase 4: Integration & Streaming Commands
# =============================================================================


def cmd_stream(args: list[str]) -> int:
    """
    Stream crystal events in real-time.

    Usage:
        kg witness stream                    # Stream all crystals
        kg witness stream --level 0          # Only session crystals
        kg witness stream --level 1          # Only day crystals
    """
    import asyncio

    level: int | None = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--level" and i + 1 < len(args):
            try:
                level = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    console = _get_console()

    if console:
        console.print("[bold]Crystal Stream[/bold] (Ctrl+C to stop)")
        console.print("[dim]" + "─" * 40 + "[/dim]")
    else:
        print("Crystal Stream (Ctrl+C to stop)")
        print("─" * 40)

    async def run_stream() -> None:
        from services.witness.stream import stream_crystals_cli

        try:
            async for event in stream_crystals_cli(level=level, include_initial=True):
                if console:
                    console.print(f"  {event}")
                else:
                    print(f"  {event}")
        except asyncio.CancelledError:
            pass

    try:
        asyncio.run(run_stream())
    except KeyboardInterrupt:
        if console:
            console.print("\n[dim]Stream stopped.[/dim]")
        else:
            print("\nStream stopped.")

    return 0


def cmd_propose_now(args: list[str]) -> int:
    """
    Propose updates to NOW.md based on recent crystals.

    Usage:
        kg witness propose-now               # Show proposals
        kg witness propose-now --apply       # Apply proposals (with backup)
        kg witness propose-now --json        # JSON output
    """
    import asyncio

    json_output = "--json" in args
    apply = "--apply" in args
    console = _get_console()

    async def run_propose() -> dict[str, Any]:
        from pathlib import Path

        from services.witness.integration import apply_now_proposal, propose_now_update

        proposals = await propose_now_update()

        if not proposals:
            return {"message": "No proposals generated (no recent crystals)"}

        result = {
            "proposals": [p.to_dict() for p in proposals],
        }

        if apply:
            now_path = Path.cwd() / "NOW.md"
            applied = []
            for p in proposals:
                success = apply_now_proposal(p, now_path)
                applied.append({"section": p.section, "success": success})
            result["applied"] = applied

        return result

    try:
        result = asyncio.run(_bootstrap_and_run(run_propose))

        if json_output:
            print(json.dumps(result))
            return 0

        if "message" in result:
            if console:
                console.print(f"[dim]{result['message']}[/dim]")
            else:
                print(result["message"])
            return 0

        # Pretty print proposals
        import asyncio as aio

        from services.witness.integration import NowMdProposal, propose_now_update

        async def get_proposals_formatted() -> list[str]:
            proposals = await propose_now_update()
            return [p.format_diff() for p in proposals]

        formatted = asyncio.run(_bootstrap_and_run(get_proposals_formatted))

        for diff in formatted:
            if console:
                console.print(diff)
                console.print()
            else:
                print(diff)
                print()

        if "applied" in result:
            if console:
                console.print("[green]✓ Proposals applied[/green]")
            else:
                print("✓ Proposals applied")

        return 0

    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        return 1


def cmd_promote(args: list[str]) -> int:
    """
    Promote a crystal to Brain as a TeachingCrystal.

    Usage:
        kg witness promote <crystal_id>      # Promote specific crystal
        kg witness promote --auto            # Auto-promote top candidates
        kg witness promote --candidates      # List promotion candidates
        kg witness promote --json            # JSON output
    """
    import asyncio

    json_output = "--json" in args
    auto_mode = "--auto" in args
    show_candidates = "--candidates" in args
    console = _get_console()

    # Find crystal_id argument
    crystal_id = None
    for arg in args:
        if not arg.startswith("-"):
            crystal_id = arg
            break

    if show_candidates:
        # List promotion candidates
        from services.witness.integration import identify_promotion_candidates

        candidates = identify_promotion_candidates()

        if json_output:
            print(json.dumps([c.to_dict() for c in candidates[:10]]))
            return 0

        if not candidates:
            if console:
                console.print("[dim]No promotion candidates found.[/dim]")
            else:
                print("No promotion candidates found.")
            return 0

        if console:
            console.print("\n[bold]Promotion Candidates[/bold]")
            console.print("[dim]" + "─" * 60 + "[/dim]")
        else:
            print("\nPromotion Candidates")
            print("─" * 60)

        for i, c in enumerate(candidates[:10], 1):
            insight_short = (
                c.crystal.insight[:50] + "..." if len(c.crystal.insight) > 50 else c.crystal.insight
            )
            if console:
                console.print(f"  {i}. [cyan]{c.crystal.id[:12]}...[/cyan] (score: {c.score:.2f})")
                console.print(f"     {insight_short}")
                console.print(f"     [dim]{', '.join(c.reasons[:2])}[/dim]")
            else:
                print(f"  {i}. {c.crystal.id[:12]}... (score: {c.score:.2f})")
                print(f"     {insight_short}")

        return 0

    if auto_mode:
        # Auto-promote top candidates
        async def run_auto_promote() -> list[dict[str, Any]]:
            from services.witness.integration import auto_promote_crystals

            return await auto_promote_crystals(limit=3)

        try:
            results = asyncio.run(_bootstrap_and_run(run_auto_promote))

            if json_output:
                print(json.dumps(results))
                return 0

            for r in results:
                if r.get("success"):
                    if console:
                        console.print(f"[green]✓[/green] Promoted {r['crystal_id'][:12]}...")
                    else:
                        print(f"✓ Promoted {r['crystal_id'][:12]}...")
                else:
                    if console:
                        console.print(f"[red]✗[/red] Failed: {r.get('error', 'unknown')}")
                    else:
                        print(f"✗ Failed: {r.get('error', 'unknown')}")

            return 0
        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}))
            else:
                print(f"Error: {e}")
            return 1

    if not crystal_id:
        print("Usage: kg witness promote <crystal_id> [--json]")
        print("       kg witness promote --auto")
        print("       kg witness promote --candidates")
        return 1

    # Promote specific crystal
    async def run_promote() -> dict[str, Any]:
        from services.witness.crystal import CrystalId
        from services.witness.integration import promote_to_brain

        return await promote_to_brain(CrystalId(crystal_id))

    try:
        result = asyncio.run(_bootstrap_and_run(run_promote))

        if json_output:
            print(json.dumps(result))
        else:
            if result.get("success"):
                if console:
                    console.print("[green]✓ Crystal promoted to Brain[/green]")
                    console.print(f"  {result.get('message', '')}")
                else:
                    print("✓ Crystal promoted to Brain")
                    print(f"  {result.get('message', '')}")
            else:
                if console:
                    console.print(
                        f"[red]✗ Promotion failed: {result.get('error', 'unknown')}[/red]"
                    )
                else:
                    print(f"✗ Promotion failed: {result.get('error', 'unknown')}")

        return 0 if result.get("success") else 1
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        return 1


def cmd_tree(args: list[str]) -> int:
    """
    Show causal tree of marks.

    Usage:
        kg witness tree <mark_id>            # Show tree descending from mark
        kg witness tree <mark_id> --depth 3  # Limit depth
        kg witness tree <mark_id> --json     # JSON output
        kg witness tree <mark_id> --ancestry # Show ancestors instead
    """
    if not args:
        print("Usage: kg witness tree <mark_id> [--depth N] [--json] [--ancestry]")
        return 1

    mark_id = args[0]
    json_output = "--json" in args
    show_ancestry = "--ancestry" in args
    max_depth = 10

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--depth", "-d") and i + 1 < len(args):
            try:
                max_depth = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    console = _get_console()

    try:
        if show_ancestry:
            result = _get_mark_ancestry(mark_id)
        else:
            result = _get_mark_tree(mark_id, max_depth)

        if "error" in result:
            if json_output:
                print(json.dumps(result))
            else:
                print(f"Error: {result['error']}")
            return 1

        if json_output:
            print(json.dumps(result))
            return 0

        # Pretty print tree
        if show_ancestry:
            # Ancestry view (mark → root)
            if console:
                console.print(f"\n[bold]Ancestry for {mark_id[:12]}...[/bold]")
                console.print(f"[dim]Depth: {result['depth']}[/dim]")
                console.print("[dim]" + "─" * 50 + "[/dim]")
            else:
                print(f"\nAncestry for {mark_id[:12]}...")
                print(f"Depth: {result['depth']}")
                print("─" * 50)

            for i, m in enumerate(result["ancestry"]):
                indent = "  " * i
                action_short = m["action"][:50] + "..." if len(m["action"]) > 50 else m["action"]

                if console:
                    if i == 0:
                        console.print(f"{indent}[cyan]● {m['id'][:12]}...[/cyan]")
                    else:
                        console.print(f"{indent}[dim]└─[/dim] {m['id'][:12]}...")
                    console.print(f"{indent}   {action_short}")
                else:
                    prefix = "●" if i == 0 else "└─"
                    print(f"{indent}{prefix} {m['id'][:12]}...")
                    print(f"{indent}   {action_short}")
        else:
            # Tree view (root → children)
            if console:
                console.print(f"\n[bold]Tree from {mark_id[:12]}...[/bold]")
                console.print(f"[dim]Total marks: {result['total_marks']}[/dim]")
                console.print("[dim]" + "─" * 50 + "[/dim]")
            else:
                print(f"\nTree from {mark_id[:12]}...")
                print(f"Total marks: {result['total_marks']}")
                print("─" * 50)

            def print_node(node: dict[str, Any], prefix: str = "", is_last: bool = True) -> None:
                """Recursively print tree node."""
                connector = "└── " if is_last else "├── "
                action_short = (
                    node["action"][:45] + "..." if len(node["action"]) > 45 else node["action"]
                )

                if console:
                    console.print(
                        f"{prefix}{connector}[cyan]{node['id'][:12]}[/cyan] {action_short}"
                    )
                else:
                    print(f"{prefix}{connector}{node['id'][:12]} {action_short}")

                # Print children
                children = node.get("children", [])
                for i, child in enumerate(children):
                    is_last_child = i == len(children) - 1
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    print_node(child, new_prefix, is_last_child)

            if result.get("tree"):
                print_node(result["tree"], "", True)

        if console:
            console.print()
        else:
            print()

        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        return 1


# =============================================================================
# Phase 5: Crystal Dashboard (Rich TUI)
# =============================================================================


def cmd_dashboard(args: list[str]) -> int:
    """
    Crystal Dashboard - Textual TUI for hierarchy visualization.

    Usage:
        kg witness dashboard             # Launch Textual TUI (default)
        kg witness dashboard --level 0   # Filter to level
        kg witness dashboard --classic   # Use old Rich-based dashboard

    Keyboard (Textual TUI):
        j/k     - Navigate crystals (vim-style)
        ↑/↓     - Navigate crystals (arrows)
        Enter   - Copy insight to clipboard
        0-3     - Filter by level (SESSION/DAY/WEEK/EPOCH)
        a       - Show all levels
        r       - Refresh
        q       - Quit

    See: plans/witness-dashboard-tui.md
    """
    # Check for --classic flag to use old Rich dashboard
    use_classic = "--classic" in args
    args = [a for a in args if a != "--classic"]

    # Parse level filter
    level_filter: int | None = None
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--level" and i + 1 < len(args):
            try:
                level_filter = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    # Use Textual TUI by default
    if not use_classic:
        try:
            from services.witness.tui import run_witness_tui

            return run_witness_tui(initial_level=level_filter)
        except ImportError as e:
            console = _get_console()
            if console:
                console.print(
                    f"[yellow]Textual TUI not available ({e}), falling back to classic.[/yellow]"
                )
            else:
                print(f"Textual TUI not available ({e}), falling back to classic.")
            # Fall through to classic mode

    # Classic Rich-based dashboard (deprecated)
    import asyncio

    console = _get_console()
    if not console:
        print("Dashboard requires Rich library. Install with: pip install rich")
        return 1

    try:
        from rich.layout import Layout
        from rich.live import Live
        from rich.panel import Panel
        from rich.style import Style
        from rich.table import Table
        from rich.text import Text
    except ImportError:
        print("Dashboard requires Rich library. Install with: pip install rich")
        return 1

    auto_refresh = "--refresh" in args

    # Level colors
    LEVEL_COLORS = {
        0: "blue",  # SESSION
        1: "green",  # DAY
        2: "yellow",  # WEEK
        3: "magenta",  # EPOCH
    }
    LEVEL_NAMES = {0: "SESSION", 1: "DAY", 2: "WEEK", 3: "EPOCH"}

    def make_header(level_filter: int | None) -> Panel:
        """Create header panel."""
        title = Text()
        title.append("💎 ", style="bold")
        title.append("Crystal Dashboard", style="bold white")
        if level_filter is not None:
            level_name = LEVEL_NAMES.get(level_filter, "?")
            title.append(f" [{level_name}]", style=LEVEL_COLORS.get(level_filter, "white"))
        title.append("  |  ", style="dim")
        title.append("q", style="bold cyan")
        title.append("uit  ", style="dim")
        title.append("r", style="bold cyan")
        title.append("efresh  ", style="dim")
        title.append("h/l", style="bold cyan")
        title.append(" level  ", style="dim")
        title.append("j/k", style="bold cyan")
        title.append(" navigate", style="dim")
        from rich.box import SIMPLE

        return Panel(title, box=SIMPLE, padding=(0, 1))

    def make_hierarchy_panel(crystals: list[dict[str, Any]], level_filter: int | None) -> Panel:
        """Create hierarchy visualization panel."""
        from rich.box import SIMPLE

        table = Table(show_header=True, header_style="bold", box=SIMPLE, padding=(0, 1))
        table.add_column("Level", width=8)
        table.add_column("Time", width=12)
        table.add_column("Insight", ratio=3)
        table.add_column("Sources", width=8, justify="right")
        table.add_column("Conf", width=6, justify="right")

        if not crystals:
            return Panel(
                "[dim]No crystals yet. Run 'kg witness crystallize' to create some.[/dim]",
                title="[bold]Hierarchy[/bold]",
                border_style="dim",
            )

        for c in crystals[:15]:
            level = c.get("level", "?")
            level_val = {"SESSION": 0, "DAY": 1, "WEEK": 2, "EPOCH": 3}.get(level, -1)
            level_color = LEVEL_COLORS.get(level_val, "white")

            try:
                dt = datetime.fromisoformat(c["crystallized_at"])
                ts_str = dt.strftime("%m-%d %H:%M")
            except (ValueError, KeyError):
                ts_str = "???"

            insight = c.get("insight", "")
            insight_short = insight[:45] + "..." if len(insight) > 45 else insight

            source_count = c.get("source_count", 0)
            confidence = c.get("confidence", 0.0)

            table.add_row(
                Text(level, style=level_color),
                Text(ts_str, style="dim"),
                insight_short,
                str(source_count),
                f"{confidence:.0%}",
            )

        return Panel(table, title="[bold]Crystal Hierarchy[/bold]", border_style="blue")

    def make_stats_panel(crystals: list[dict[str, Any]]) -> Panel:
        """Create statistics panel."""
        # Count by level
        by_level: dict[str, int] = {}
        total_sources = 0
        avg_confidence = 0.0

        for c in crystals:
            level = c.get("level", "?")
            by_level[level] = by_level.get(level, 0) + 1
            total_sources += c.get("source_count", 0)
            avg_confidence += c.get("confidence", 0.0)

        if crystals:
            avg_confidence /= len(crystals)

        stats_text = Text()
        stats_text.append("Total: ", style="dim")
        stats_text.append(str(len(crystals)), style="bold")
        stats_text.append("\n")

        for level_name in ["SESSION", "DAY", "WEEK", "EPOCH"]:
            count = by_level.get(level_name, 0)
            level_val = {"SESSION": 0, "DAY": 1, "WEEK": 2, "EPOCH": 3}.get(level_name, -1)
            color = LEVEL_COLORS.get(level_val, "white")
            stats_text.append(f"{level_name}: ", style=color)
            stats_text.append(f"{count}\n", style="bold")

        stats_text.append("\n")
        stats_text.append("Total sources: ", style="dim")
        stats_text.append(str(total_sources), style="bold")
        stats_text.append("\n")
        stats_text.append("Avg confidence: ", style="dim")
        stats_text.append(f"{avg_confidence:.0%}", style="bold")

        return Panel(stats_text, title="[bold]Stats[/bold]", border_style="green")

    def make_recent_panel(crystals: list[dict[str, Any]]) -> Panel:
        """Create recent crystals panel (session level only)."""
        session_crystals = [c for c in crystals if c.get("level") == "SESSION"][:5]

        if not session_crystals:
            return Panel(
                "[dim]No session crystals[/dim]",
                title="[bold]Recent Sessions[/bold]",
                border_style="dim",
            )

        recent_text = Text()
        for c in session_crystals:
            try:
                dt = datetime.fromisoformat(c["crystallized_at"])
                ts_str = dt.strftime("%H:%M")
            except (ValueError, KeyError):
                ts_str = "??"

            insight = c.get("insight", "")
            insight_short = insight[:35] + "..." if len(insight) > 35 else insight

            recent_text.append(f"• {ts_str} ", style="cyan")
            recent_text.append(f"{insight_short}\n", style="white")

        return Panel(recent_text, title="[bold]Recent Sessions[/bold]", border_style="cyan")

    def make_layout(crystals: list[dict[str, Any]], level_filter: int | None) -> Layout:
        """Create the full dashboard layout."""
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=1),
        )

        layout["main"].split_row(
            Layout(name="hierarchy", ratio=3),
            Layout(name="sidebar", ratio=1),
        )

        layout["sidebar"].split_column(
            Layout(name="stats", ratio=1),
            Layout(name="recent", ratio=1),
        )

        layout["header"].update(make_header(level_filter))
        layout["hierarchy"].update(make_hierarchy_panel(crystals, level_filter))
        layout["stats"].update(make_stats_panel(crystals))
        layout["recent"].update(make_recent_panel(crystals))
        layout["footer"].update(
            Text(
                "Press q to quit | r to refresh | h/l to filter level",
                style="dim",
                justify="center",
            )
        )

        return layout

    def fetch_crystals(level: int | None) -> list[dict[str, Any]]:
        """Fetch crystals synchronously."""

        return asyncio.run(_bootstrap_and_run(lambda: _get_crystals_async(limit=50, level=level)))

    # Initial fetch
    try:
        crystals = fetch_crystals(level_filter)
    except Exception as e:
        console.print(f"[red]Error fetching crystals: {e}[/red]")
        return 1

    # Check if stdin is interactive (TTY)
    is_interactive = sys.stdin.isatty()

    # Simple mode without Live (for now - keyboard input requires more complexity)
    console.clear()
    layout = make_layout(crystals, level_filter)
    console.print(layout)

    if not is_interactive:
        # Non-interactive mode: just display and exit
        console.print(
            "\n[dim]Non-interactive mode: displayed once. Use --refresh for auto-refresh.[/dim]"
        )
        return 0

    console.print("\n[dim]Press Enter to refresh, 'q' to quit, '0-3' to filter level[/dim]")

    # Use Rich's Prompt for more robust input handling
    try:
        from rich.prompt import Prompt

        use_rich_prompt = True
    except ImportError:
        use_rich_prompt = False

    def get_input() -> str:
        """Get input with fallback to plain input if Rich fails."""
        if use_rich_prompt:
            try:
                return Prompt.ask(">", console=console, default="").strip().lower()
            except Exception:
                pass
        # Fallback to plain input
        return input("> ").strip().lower()

    try:
        while True:
            try:
                user_input = get_input()
            except (EOFError, OSError) as e:
                # Handle stdin issues gracefully
                print(f"\n[stdin closed: {e}]")
                break

            if user_input == "q":
                break
            elif user_input == "r" or user_input == "":
                crystals = fetch_crystals(level_filter)
                console.clear()
                layout = make_layout(crystals, level_filter)
                console.print(layout)
                console.print(
                    "\n[dim]Press Enter to refresh, 'q' to quit, '0-3' to filter level[/dim]"
                )
            elif user_input in ("0", "1", "2", "3"):
                level_filter = int(user_input)
                crystals = fetch_crystals(level_filter)
                console.clear()
                layout = make_layout(crystals, level_filter)
                console.print(layout)
                console.print(
                    "\n[dim]Press Enter to refresh, 'q' to quit, '0-3' to filter level[/dim]"
                )
            elif user_input == "a":
                level_filter = None
                crystals = fetch_crystals(level_filter)
                console.clear()
                layout = make_layout(crystals, level_filter)
                console.print(layout)
                console.print(
                    "\n[dim]Press Enter to refresh, 'q' to quit, '0-3' to filter level, 'a' for all[/dim]"
                )

    except KeyboardInterrupt:
        pass
    except Exception as e:
        # Catch any unexpected exceptions with diagnostic info
        print(f"\nDashboard error ({type(e).__name__}): {e}")
        import traceback

        traceback.print_exc()
        return 1

    console.print("\n[dim]Dashboard closed.[/dim]")
    return 0


def cmd_graph(args: list[str]) -> int:
    """
    Output crystal graph as JSON for frontend visualization.

    Usage:
        kg witness graph             # Full hierarchy graph
        kg witness graph --level 0   # Filter by level
        kg witness graph --limit 30  # Limit per level
    """
    import asyncio

    json_output = True  # Always JSON for this command
    level_filter: int | None = None
    limit = 50

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--level" and i + 1 < len(args):
            try:
                level_filter = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg in ("--limit", "-l") and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    async def get_graph() -> dict[str, Any]:
        from services.witness.crystal import CrystalLevel
        from services.witness.crystal_trail import CrystalTrailAdapter, format_graph_response

        adapter = CrystalTrailAdapter()

        level = CrystalLevel(level_filter) if level_filter is not None else None
        graph = adapter.to_graph(level_filter=level, limit=limit)

        return format_graph_response(graph)

    try:
        result = asyncio.run(_bootstrap_and_run(get_graph))
        print(json.dumps(result))
        return 0
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return 1


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
        # Tree commands (lineage)
        "tree": cmd_tree,
        # Crystal commands
        "crystallize": cmd_crystallize,
        "crystals": cmd_crystals,
        "crystal": cmd_crystal,
        "expand": cmd_expand,
        # Context budget commands
        "context": cmd_context,
        "ctx": cmd_context,  # alias
        # Phase 4: Integration & Streaming
        "stream": cmd_stream,
        "propose-now": cmd_propose_now,
        "propose": cmd_propose_now,  # alias
        "promote": cmd_promote,
        # Phase 5: Visual Projection
        "dashboard": cmd_dashboard,
        "dash": cmd_dashboard,  # alias
        "graph": cmd_graph,
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
kg witness - Everyday Mark-Making & Memory Crystallization

"Every action leaves a mark. The mark IS the witness."
"Marks become crystals. Crystals become wisdom."

MARK COMMANDS:
  kg witness mark "action"     Create a mark
  kg witness show              Show recent marks
  kg witness session           Show this session's marks

LINEAGE COMMANDS:
  kg witness tree <id>         Show causal tree (children)
  kg witness tree <id> --ancestry  Show parent chain

CRYSTAL COMMANDS:
  kg witness crystallize       Crystallize marks into insight
  kg witness crystals          List recent crystals
  kg witness crystal <id>      Show crystal details
  kg witness expand <id>       Show crystal sources

CONTEXT COMMANDS:
  kg witness context           Budget-aware crystal context
  kg witness context --budget N  Set token budget (default: 2000)
  kg witness context --query X   Relevance-weighted by query

MARK OPTIONS:
  -w, --why "reason"          Add reasoning
  -p, --principles a,b        Add principles
  -t, --tag <tag>             Add tag (can repeat: --tag a --tag b)
  --parent <mark_id>          Link as child of parent (lineage)
  --json                      Machine-readable JSON output

SHOW OPTIONS:
  -l, --limit N               Number of marks (default: 20)
  -v, --verbose               Show reasoning
  --json                      Output as JSON array
  --today                     Only marks from today
  --grep "pattern"            Filter by content/reasoning
  --tag "principle"           Filter by principle tag

TREE OPTIONS:
  --depth N                   Max depth to traverse (default: 10)
  --ancestry                  Show ancestors instead of children
  --json                      Output as JSON

CRYSTALLIZE OPTIONS:
  --level session|day|week    Target level (default: session)
  --session <id>              Session identifier
  --tree <mark_id>            Crystallize tree from root mark
  --json                      Output as JSON

CRYSTALS OPTIONS:
  --level 0|1|2|3             Filter by level (0=session, 1=day, etc)
  -l, --limit N               Number to show (default: 10)
  --json                      Output as JSON

CONTEXT OPTIONS:
  --budget N                  Token budget (default: 2000)
  --query "topic"             Relevance filter (keyword matching)
  --recency-weight N          Weight for recency vs relevance (0.0-1.0, default: 0.7)
  --json                      Output as JSON (for agents)

INTEGRATION COMMANDS (Phase 4):
  kg witness stream            Stream crystal events in real-time
  kg witness propose-now       Propose NOW.md updates from crystals
  kg witness promote           Promote crystals to Brain teachings

STREAM OPTIONS:
  --level 0|1|2|3             Filter by level

PROPOSE OPTIONS:
  --apply                     Apply proposals with backup
  --json                      Output as JSON

PROMOTE OPTIONS:
  <crystal_id>                Promote specific crystal
  --auto                      Auto-promote top candidates
  --candidates                List promotion candidates
  --json                      Output as JSON

VISUALIZATION COMMANDS (Phase 5):
  kg witness dashboard         Textual TUI crystal navigator (default)
  kg witness graph             Crystal graph as JSON (for frontend)

DASHBOARD OPTIONS:
  --level 0|1|2|3             Filter by level
  --classic                   Use old Rich-based dashboard
  TUI Keys: j/k=navigate, Enter=copy, 0-3=level, a=all, r=refresh, q=quit

GRAPH OPTIONS:
  --level 0|1|2|3             Filter by level
  --limit N                   Max crystals per level (default: 50)

QUICK ALIAS (recommended):
  km "action"                  = kg witness mark "action"
  km "X" -w "Y"                = kg witness mark "X" -w "Y"
  km "X" --tag eureka          = kg witness mark "X" --tag eureka
  km "X" --parent mark-abc     = Link as child of parent

EXAMPLES:
  kg witness mark "Refactored DI container"
  kg witness mark "Chose PostgreSQL" -w "Scaling needs"
  kg witness mark "Insight" --tag eureka --tag pattern  # Multiple tags
  kg witness mark "Fixed issue" --parent mark-abc123    # Create causal link
  kg witness tree mark-abc123          # See tree of related marks
  kg witness crystallize               # LLM-powered insight extraction
  kg witness crystallize --tree mark-abc  # Crystallize entire tree
  kg witness context --budget 1500     # Get crystals within budget
  kg witness context --query "audit"   # Relevance-weighted context

AGENT-FRIENDLY EXAMPLES:
  km "Completed task" --json             # Returns: {"mark_id": "...", ...}
  km "Follow-up" --parent mark-abc --json  # Returns with parent link
  kg witness tree mark-abc --json        # Tree structure as JSON
  kg witness crystallize --json          # Returns: {"crystal_id": "...", ...}
  kg witness crystals --json             # Returns crystal array
  kg witness show --today --json         # Today's marks for context
  kg witness context --budget 1000 --json  # Budget-aware context for agents

PHILOSOPHY:
  Marks are observations. Crystals are insights.
  An action without a mark is a reflex.
  An action with a mark is agency.
  Crystallization reveals patterns.
  Lineage reveals causation.
  Budget forces compression.

See: spec/protocols/witness-crystallization.md
See: docs/skills/witness-for-agents.md
"""
    print(help_text.strip())


__all__ = ["cmd_witness"]
