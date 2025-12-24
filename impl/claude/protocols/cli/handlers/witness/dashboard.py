"""
Dashboard operations: visual crystal hierarchy exploration.

Provides:
- cmd_dashboard: Textual TUI crystal navigator
- cmd_graph: Crystal graph as JSON for frontend
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime
from typing import Any

from .base import _bootstrap_and_run, _get_console


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

    from .crystals import _get_crystals_async

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


__all__ = [
    "cmd_dashboard",
    "cmd_graph",
]
