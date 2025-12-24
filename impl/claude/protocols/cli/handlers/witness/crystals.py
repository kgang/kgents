"""
Crystal operations: crystallization and crystal management.

Provides:
- cmd_crystallize: Crystallize marks into insight
- cmd_crystals: List recent crystals
- cmd_crystal: Show crystal details
- cmd_expand: Show crystal sources
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from .base import _get_console, _run_async_factory


# =============================================================================
# Crystal Operations
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
    from services.witness.mark import Mark, MarkId, NPhase, Response, Stimulus
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


# =============================================================================
# Command Handlers
# =============================================================================


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


# =============================================================================
# Async Command Handlers (for use within async context)
# =============================================================================


async def cmd_crystallize_async(args: list[str]) -> int:
    """
    Async version of cmd_crystallize for use within async context.

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
        result = await _crystallize_async(level, session_id, tree_root_id)

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


async def cmd_crystals_async(args: list[str]) -> int:
    """
    Async version of cmd_crystals for use within async context.

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
        crystals = await _get_crystals_async(limit, level)

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


async def cmd_crystal_async(args: list[str]) -> int:
    """
    Async version of cmd_crystal for use within async context.

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
        crystal = await _get_crystal_async(crystal_id)

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


async def cmd_expand_async(args: list[str]) -> int:
    """
    Async version of cmd_expand for use within async context.

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
        result = await _expand_crystal_async(crystal_id)

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


__all__ = [
    "cmd_crystallize",
    "cmd_crystals",
    "cmd_crystal",
    "cmd_expand",
    # Async versions
    "cmd_crystallize_async",
    "cmd_crystals_async",
    "cmd_crystal_async",
    "cmd_expand_async",
]
