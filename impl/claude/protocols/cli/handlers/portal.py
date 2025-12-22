"""
Portal CLI: Navigate Source Files Through Hyperedge Expansion.

"You don't go to the document. The document comes to you."

This handler provides:
- `kg portal <file>` - Show portals for a source file
- `kg portal expand <file> <edge>` - Expand a portal edge
- `kg portal tree <file>` - Show full expansion tree

The key insight: hyperedge resolvers already exist for imports, tests, calls, etc.
This CLI makes them accessible for everyday navigation.

See: spec/protocols/portal-token.md Phase 4
"""

from __future__ import annotations

import asyncio
from pathlib import Path
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


def _print_header(title: str) -> None:
    """Print a header with styling."""
    console = _get_console()
    if console:
        console.print(f"\n[bold]{title}[/bold]")
        console.print("[dim]" + "─" * 50 + "[/dim]")
    else:
        print(f"\n{title}")
        print("─" * 50)


def _print_portal_line(
    edge_type: str,
    count: int,
    expanded: bool = False,
) -> None:
    """Print a single portal line with expand/collapse marker."""
    console = _get_console()
    marker = "▼" if expanded else "▶"
    noun = "file" if count == 1 else "files"

    if console:
        console.print(f"  {marker} [cyan][{edge_type}][/cyan] ──→ {count} {noun}")
    else:
        print(f"  {marker} [{edge_type}] ──→ {count} {noun}")


def _print_destination(path: str, exists: bool, indent: int = 4) -> None:
    """Print a destination path with existence indicator."""
    console = _get_console()
    prefix = " " * indent
    marker = "✓" if exists else "✗"

    if console:
        color = "green" if exists else "red"
        console.print(f"{prefix}[{color}]{marker}[/{color}] [dim]{path}[/dim]")
    else:
        print(f"{prefix}{marker} {path}")


# =============================================================================
# Async Bootstrap Helpers
# =============================================================================


async def _bootstrap_and_discover(file_path: Path) -> list[Any]:
    """Bootstrap services and discover portals."""
    from protocols.file_operad.source_portals import discover_portals

    return await discover_portals(file_path)


async def _bootstrap_and_build_tree(
    file_path: Path,
    max_depth: int = 5,
    expand_all: bool = False,
) -> Any:
    """Bootstrap services and build portal tree."""
    from protocols.file_operad.source_portals import build_source_portal_tree

    return await build_source_portal_tree(
        file_path,
        max_depth=max_depth,
        expand_all=expand_all,
    )


def _run_async(coro: Any) -> Any:
    """Run async coroutine synchronously."""
    return asyncio.run(coro)


# =============================================================================
# Subcommand Handlers
# =============================================================================


def cmd_show(args: list[str]) -> int:
    """
    Show portals for a source file.

    Usage:
        kg portal <file>
        kg portal show impl/claude/services/brain/core.py
    """
    if not args:
        print("Usage: kg portal <file>")
        print("       kg portal show <file>")
        return 1

    file_path = Path(args[0])

    # Resolve relative paths
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path

    if not file_path.exists():
        console = _get_console()
        if console:
            console.print(f"[red]Error:[/red] File not found: {file_path}")
        else:
            print(f"Error: File not found: {file_path}")
        return 1

    if not file_path.is_file():
        console = _get_console()
        if console:
            console.print(f"[red]Error:[/red] Not a file: {file_path}")
        else:
            print(f"Error: Not a file: {file_path}")
        return 1

    try:
        links = _run_async(_bootstrap_and_discover(file_path))

        _print_header(f"Portals: {file_path.name}")

        if not links:
            console = _get_console()
            if console:
                console.print("[dim]No portals discovered.[/dim]")
            else:
                print("No portals discovered.")
            return 0

        # Group by edge type
        by_type: dict[str, list[Any]] = {}
        for link in links:
            by_type.setdefault(link.edge_type, []).append(link)

        for edge_type, type_links in sorted(by_type.items()):
            _print_portal_line(edge_type, len(type_links))

        console = _get_console()
        if console:
            console.print()
            console.print("[dim]Tip: Use 'kg portal expand <file> <edge>' to see destinations[/dim]")
        else:
            print()
            print("Tip: Use 'kg portal expand <file> <edge>' to see destinations")

        return 0

    except Exception as e:
        console = _get_console()
        if console:
            console.print(f"[red]Error:[/red] {e}")
        else:
            print(f"Error: {e}")
        return 1


def cmd_expand(args: list[str]) -> int:
    """
    Expand a portal edge to show destinations.

    Usage:
        kg portal expand <file> <edge>
        kg portal expand core.py imports
        kg portal expand core.py tests
    """
    if len(args) < 2:
        print("Usage: kg portal expand <file> <edge>")
        print()
        print("Available edges:")
        print("  imports    - What this file imports")
        print("  tests      - Test files for this module")
        print("  implements - Specs this implements")
        print("  contains   - Submodules/children")
        print("  calls      - Functions called by this module")
        print("  related    - Sibling modules")
        return 1

    file_path = Path(args[0])
    edge_type = args[1]

    # Resolve relative paths
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path

    if not file_path.exists():
        console = _get_console()
        if console:
            console.print(f"[red]Error:[/red] File not found: {file_path}")
        else:
            print(f"Error: File not found: {file_path}")
        return 1

    try:
        links = _run_async(_bootstrap_and_discover(file_path))

        # Filter by edge type
        matching = [l for l in links if l.edge_type == edge_type]

        _print_header(f"[{edge_type}] from {file_path.name}")

        if not matching:
            console = _get_console()
            if console:
                console.print(f"[dim]No {edge_type} portals found.[/dim]")
            else:
                print(f"No {edge_type} portals found.")
            return 0

        _print_portal_line(edge_type, len(matching), expanded=True)

        for link in matching:
            _print_destination(link.path, link.exists())

        return 0

    except Exception as e:
        console = _get_console()
        if console:
            console.print(f"[red]Error:[/red] {e}")
        else:
            print(f"Error: {e}")
        return 1


def cmd_tree(args: list[str]) -> int:
    """
    Show full portal tree for a file.

    Usage:
        kg portal tree <file>
        kg portal tree <file> --depth 5
        kg portal tree <file> --expand-all
    """
    if not args:
        print("Usage: kg portal tree <file> [--depth N] [--expand-all]")
        return 1

    file_path = Path(args[0])
    max_depth = 5
    expand_all = False

    # Parse options
    i = 1
    while i < len(args):
        arg = args[i]
        if arg in ("--depth", "-d") and i + 1 < len(args):
            try:
                max_depth = int(args[i + 1])
            except ValueError:
                print(f"Invalid depth: {args[i + 1]}")
                return 1
            i += 2
        elif arg in ("--expand-all", "-e"):
            expand_all = True
            i += 1
        else:
            i += 1

    # Resolve relative paths
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path

    if not file_path.exists():
        console = _get_console()
        if console:
            console.print(f"[red]Error:[/red] File not found: {file_path}")
        else:
            print(f"Error: File not found: {file_path}")
        return 1

    try:
        tree = _run_async(_bootstrap_and_build_tree(
            file_path,
            max_depth=max_depth,
            expand_all=expand_all,
        ))

        _print_header(f"Portal Tree: {file_path.name}")

        rendered = tree.render(max_depth=max_depth)
        console = _get_console()
        if console:
            console.print(rendered)
        else:
            print(rendered)

        return 0

    except Exception as e:
        console = _get_console()
        if console:
            console.print(f"[red]Error:[/red] {e}")
        else:
            print(f"Error: {e}")
        return 1


def cmd_list_edges(args: list[str]) -> int:
    """
    List available edge types.

    Usage:
        kg portal edges
    """
    _print_header("Available Portal Edge Types")

    edges = [
        ("imports", "What this file imports (Python: ast parsing)"),
        ("tests", "Test files for this module (_tests/test_*.py)"),
        ("implements", "Specs this module implements (docstring refs)"),
        ("contains", "Submodules/children (directory contents)"),
        ("calls", "Functions called by this module (ast parsing)"),
        ("related", "Sibling modules (same directory)"),
        ("parent", "Parent module (directory above)"),
    ]

    console = _get_console()
    for edge_type, description in edges:
        if console:
            console.print(f"  [cyan]{edge_type:12}[/cyan]  {description}")
        else:
            print(f"  {edge_type:12}  {description}")

    if console:
        console.print()
    else:
        print()

    return 0


# =============================================================================
# Main Entry Point
# =============================================================================


def cmd_portal(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Portal navigation for source files.

    "You don't go to the document. The document comes to you."
    """
    if not args or "--help" in args or "-h" in args:
        _print_help()
        return 0

    subcommand = args[0].lower()
    sub_args = args[1:]

    handlers = {
        "show": cmd_show,
        "expand": cmd_expand,
        "tree": cmd_tree,
        "edges": cmd_list_edges,
        "list-edges": cmd_list_edges,
    }

    handler = handlers.get(subcommand)
    if handler:
        return handler(sub_args)

    # If first arg looks like a path, treat as show
    if "/" in subcommand or subcommand.endswith(".py") or Path(subcommand).exists():
        return cmd_show(args)

    console = _get_console()
    if console:
        console.print(f"[red]Unknown subcommand:[/red] {subcommand}")
    else:
        print(f"Unknown subcommand: {subcommand}")
    _print_help()
    return 1


def _print_help() -> None:
    """Print portal command help."""
    help_text = """
kg portal - Navigate Source Files Through Hyperedge Expansion

"You don't go to the document. The document comes to you."

COMMANDS:
  kg portal <file>                    Show portals for file
  kg portal show <file>               Same as above
  kg portal expand <file> <edge>      Expand an edge to see destinations
  kg portal tree <file>               Show full portal tree
  kg portal edges                     List available edge types

OPTIONS:
  --depth, -d N        Max tree depth (default: 3)
  --expand-all, -e     Expand all portals in tree

EDGE TYPES:
  imports      What this file imports
  tests        Test files for this module
  implements   Specs this implements
  contains     Submodules/children
  calls        Functions called
  related      Sibling modules

EXAMPLES:
  kg portal impl/claude/services/brain/core.py
  kg portal expand core.py imports
  kg portal expand core.py tests
  kg portal tree core.py --depth 2
  kg portal tree core.py --expand-all

PHILOSOPHY:
  Navigation is expansion. Expansion is navigation.
  The document IS the exploration.

See: spec/protocols/portal-token.md
"""
    print(help_text.strip())


__all__ = ["cmd_portal"]
