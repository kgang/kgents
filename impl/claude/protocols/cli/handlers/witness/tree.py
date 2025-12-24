"""
Tree operations: causal tree visualization and ancestry.

Provides:
- cmd_tree: Show causal tree of marks
"""

from __future__ import annotations

import json
from typing import Any

from .base import _get_console, _run_async_factory


# =============================================================================
# Tree Operations
# =============================================================================


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


# Create sync wrappers
_get_mark_tree = _run_async_factory(_get_mark_tree_async)
_get_mark_ancestry = _run_async_factory(_get_mark_ancestry_async)


# =============================================================================
# Command Handler
# =============================================================================


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
# Async Command Handler
# =============================================================================


async def cmd_tree_async(args: list[str]) -> int:
    """
    Async version of cmd_tree for use within async context.

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
            result = await _get_mark_ancestry_async(mark_id)
        else:
            result = await _get_mark_tree_async(mark_id, max_depth)

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


__all__ = ["cmd_tree", "cmd_tree_async"]
