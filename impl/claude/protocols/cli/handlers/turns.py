"""
Turns Handler: CLI commands for Turn-gents debugging and visualization.

Part of the Turn-gents Realization: making Turn-gents felt by developers.

Usage:
    kgents turns <agent>              # Show turn history for agent
    kgents turns --all                # Show all turns across all agents
    kgents dag                        # Visualize turn DAG (static)
    kgents dag --interactive          # Visualize turn DAG (interactive TUI)
    kgents fork <turn_id>             # Fork from a specific turn

The Turn-gents Protocol replaces linear context with causal structure:
- Turns are typed events (SPEECH, ACTION, THOUGHT, YIELD, SILENCE)
- CausalCone projects minimal context per agent
- TurnDAGRenderer visualizes the causal DAG

This is Phase 6 of Turn-gents: Debugger Integration.

References:
- Turn-gents Plan: Phase 6 (Debugger Integration)
- weave/turn.py: Turn, TurnType, YieldTurn
- agents/i/screens/turn_dag.py: TurnDAGRenderer
"""

from __future__ import annotations

import json as json_module
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_turns_help() -> None:
    """Print help for turns command."""
    print(__doc__)
    print()
    print("SUBCOMMANDS:")
    print("  (default)         Show turn history for an agent")
    print("  --all             Show all turns across all agents")
    print()
    print("OPTIONS:")
    print("  --last N          Show last N turns (default: 10)")
    print("  --thoughts        Include THOUGHT turns (collapsed by default)")
    print("  --source AGENT    Filter by source agent")
    print(
        "  --type TYPE       Filter by turn type (SPEECH|ACTION|THOUGHT|YIELD|SILENCE)"
    )
    print("  --json            Output as JSON")
    print("  --stats           Show turn statistics only")
    print("  --help, -h        Show this help")


def _print_dag_help() -> None:
    """Print help for dag command."""
    print("kgents dag - Visualize the Turn DAG")
    print()
    print("USAGE:")
    print("  kgents dag [options]")
    print()
    print("OPTIONS:")
    print("  --agent AGENT     Highlight causal cone for agent")
    print("  --interactive, -i Interactive TUI mode")
    print("  --thoughts        Show THOUGHT turns (collapsed by default)")
    print("  --json            Output as JSON")
    print("  --help, -h        Show this help")


def _print_fork_help() -> None:
    """Print help for fork command."""
    print("kgents fork - Fork from a specific turn for debugging")
    print()
    print("USAGE:")
    print("  kgents fork <turn_id> [options]")
    print()
    print("OPTIONS:")
    print("  --name NAME       Name for the forked branch")
    print("  --help, -h        Show this help")


def cmd_turns(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Main entry point for the turns command.

    Shows turn history for an agent or all agents.

    Args:
        args: Command-line arguments
        ctx: Optional InvocationContext for dual-channel output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("turns", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_turns_help()
        return 0

    # Parse flags
    json_mode = "--json" in args
    show_all = "--all" in args
    show_thoughts = "--thoughts" in args
    show_stats = "--stats" in args

    # Parse --last
    last_n = 10
    for i, arg in enumerate(args):
        if arg == "--last" and i + 1 < len(args):
            try:
                last_n = int(args[i + 1])
            except ValueError:
                pass

    # Parse --source
    source_filter: str | None = None
    for i, arg in enumerate(args):
        if arg == "--source" and i + 1 < len(args):
            source_filter = args[i + 1]

    # Parse --type
    type_filter: str | None = None
    for i, arg in enumerate(args):
        if arg == "--type" and i + 1 < len(args):
            type_filter = args[i + 1].upper()

    # Get target agent (first non-flag argument)
    target_agent: str | None = None
    if not show_all:
        skip_next = False
        for arg in args:
            if skip_next:
                skip_next = False
                continue
            if arg in ("--last", "--source", "--type"):
                skip_next = True
                continue
            if arg.startswith("-"):
                continue
            target_agent = arg
            break

    # Execute command
    try:
        return _execute_turns(
            target_agent=target_agent,
            show_all=show_all,
            last_n=last_n,
            show_thoughts=show_thoughts,
            show_stats=show_stats,
            source_filter=source_filter,
            type_filter=type_filter,
            json_mode=json_mode,
            ctx=ctx,
        )
    except ImportError as e:
        _emit_output(
            f"[TURNS] Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1
    except Exception as e:
        _emit_output(
            f"[TURNS] Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _execute_turns(
    target_agent: str | None,
    show_all: bool,
    last_n: int,
    show_thoughts: bool,
    show_stats: bool,
    source_filter: str | None,
    type_filter: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Execute the turns command."""
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text
    from weave import (
        CausalCone,
        CausalConeStats,
        TheWeave,
        Turn,
        TurnType,
        compute_cone_stats,
    )

    # Get the global weave (or create empty one for demo)
    weave = _get_global_weave()

    if len(weave) == 0:
        _emit_output(
            "[TURNS] No turns recorded yet. "
            "Decorate agents with @Capability.TurnBased to start recording turns.",
            {"status": "empty", "message": "No turns recorded"},
            ctx,
        )
        return 0

    # Get turns based on mode
    if show_all or target_agent is None:
        # All turns
        events = weave.linearize()
    else:
        # Agent-specific turns (via CausalCone)
        cone = CausalCone(weave)
        events = cone.project_context(target_agent)

    # Filter to Turn instances
    turns = [e for e in events if isinstance(e, Turn)]

    # Apply type filter
    if type_filter:
        try:
            turn_type = TurnType[type_filter]
            turns = [t for t in turns if t.turn_type == turn_type]
        except KeyError:
            _emit_output(
                f"[TURNS] Unknown turn type: {type_filter}. "
                f"Valid types: SPEECH, ACTION, THOUGHT, YIELD, SILENCE",
                {"error": f"Unknown turn type: {type_filter}"},
                ctx,
            )
            return 1

    # Apply source filter
    if source_filter:
        turns = [t for t in turns if t.source == source_filter]

    # Apply thought collapse
    if not show_thoughts:
        turns = [t for t in turns if t.turn_type != TurnType.THOUGHT]

    # Apply last N limit
    turns = turns[-last_n:]

    # Show stats only mode
    if show_stats:
        return _show_turn_stats(weave, target_agent, json_mode, ctx)

    # Output
    if json_mode:
        turn_data = [
            {
                "id": t.id,
                "source": t.source,
                "turn_type": t.turn_type.name,
                "content": str(t.content)[:100],
                "confidence": t.confidence,
                "entropy_cost": t.entropy_cost,
                "timestamp": t.timestamp,
            }
            for t in turns
        ]
        _emit_output(
            json_module.dumps(turn_data, indent=2),
            {"turns": turn_data},
            ctx,
        )
    else:
        # Rich table output
        console = Console()
        table = Table(title=f"Turn History (last {len(turns)})")

        table.add_column("Type", style="cyan", width=8)
        table.add_column("Source", style="yellow")
        table.add_column("Content", style="white", max_width=50)
        table.add_column("Conf", justify="right")
        table.add_column("ID", style="dim", width=8)

        type_colors = {
            TurnType.SPEECH: "green",
            TurnType.ACTION: "blue",
            TurnType.THOUGHT: "dim",
            TurnType.YIELD: "yellow",
            TurnType.SILENCE: "dim italic",
        }

        for turn in turns:
            color = type_colors.get(turn.turn_type, "white")
            conf_color = (
                "green"
                if turn.confidence > 0.7
                else "yellow"
                if turn.confidence > 0.3
                else "red"
            )

            content_preview = str(turn.content)
            if len(content_preview) > 47:
                content_preview = content_preview[:47] + "..."

            table.add_row(
                Text(turn.turn_type.name, style=color),
                turn.source,
                content_preview,
                Text(f"{turn.confidence:.0%}", style=conf_color),
                turn.id[:8],
            )

        console.print(table)

        # Show compression ratio if agent specified
        if target_agent:
            cone = CausalCone(weave)
            ratio = cone.compression_ratio(target_agent)
            console.print(
                f"\n[dim]Compression ratio for {target_agent}: {ratio:.1%} "
                f"({cone.cone_size(target_agent)}/{len(weave)} events in cone)[/]"
            )

    return 0


def _show_turn_stats(
    weave: Any,
    target_agent: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Show turn statistics."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from weave import CausalCone, Turn, TurnType, compute_cone_stats

    # Count by type
    type_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}

    for event in weave.monoid.events:
        if isinstance(event, Turn):
            type_name = event.turn_type.name
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            source_counts[event.source] = source_counts.get(event.source, 0) + 1

    # Compute cone stats if agent specified
    cone_stats = None
    if target_agent:
        cone = CausalCone(weave)
        cone_stats = compute_cone_stats(cone, target_agent)

    if json_mode:
        stats = {
            "total_turns": len(weave),
            "by_type": type_counts,
            "by_source": source_counts,
        }
        if cone_stats:
            stats["cone_stats"] = {
                "agent_id": cone_stats.agent_id,
                "cone_size": cone_stats.cone_size,
                "compression_ratio": cone_stats.compression_ratio,
            }
        _emit_output(
            json_module.dumps(stats, indent=2),
            stats,
            ctx,
        )
    else:
        console = Console()

        # Type breakdown
        type_table = Table(title="Turns by Type")
        type_table.add_column("Type", style="cyan")
        type_table.add_column("Count", justify="right")

        type_colors = {
            "SPEECH": "green",
            "ACTION": "blue",
            "THOUGHT": "dim",
            "YIELD": "yellow",
            "SILENCE": "dim",
        }

        for type_name, count in sorted(type_counts.items()):
            color = type_colors.get(type_name, "white")
            type_table.add_row(f"[{color}]{type_name}[/]", str(count))

        console.print(type_table)

        # Source breakdown
        source_table = Table(title="\nTurns by Source")
        source_table.add_column("Source", style="yellow")
        source_table.add_column("Count", justify="right")

        for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
            source_table.add_row(source, str(count))

        console.print(source_table)

        # Cone stats
        if cone_stats:
            console.print(
                Panel(
                    f"Agent: {cone_stats.agent_id}\n"
                    f"Cone size: {cone_stats.cone_size} events\n"
                    f"Total weave: {cone_stats.total_weave_size} events\n"
                    f"Compression: {cone_stats.compression_ratio:.1%}",
                    title="Causal Cone Stats",
                )
            )

    return 0


def cmd_dag(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Visualize the Turn DAG.

    Args:
        args: Command-line arguments
        ctx: Optional InvocationContext for dual-channel output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("dag", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_dag_help()
        return 0

    # Parse flags
    json_mode = "--json" in args
    interactive = "--interactive" in args or "-i" in args
    show_thoughts = "--thoughts" in args

    # Parse --agent
    agent_id: str | None = None
    for i, arg in enumerate(args):
        if arg == "--agent" and i + 1 < len(args):
            agent_id = args[i + 1]

    try:
        return _execute_dag(
            agent_id=agent_id,
            interactive=interactive,
            show_thoughts=show_thoughts,
            json_mode=json_mode,
            ctx=ctx,
        )
    except ImportError as e:
        _emit_output(
            f"[DAG] Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1
    except Exception as e:
        _emit_output(
            f"[DAG] Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _execute_dag(
    agent_id: str | None,
    interactive: bool,
    show_thoughts: bool,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Execute the dag command."""
    from agents.i.screens.turn_dag import (
        TurnDAGConfig,
        TurnDAGRenderer,
        render_turn_dag,
    )
    from rich.console import Console
    from weave import TheWeave

    # Get the global weave
    weave = _get_global_weave()

    if len(weave) == 0:
        _emit_output(
            "[DAG] No turns recorded yet.",
            {"status": "empty"},
            ctx,
        )
        return 0

    if interactive:
        # Launch interactive TUI
        return _launch_dag_tui(weave, agent_id, show_thoughts)

    # Static rendering
    config = TurnDAGConfig(show_thoughts=show_thoughts)
    renderer = TurnDAGRenderer(weave=weave, config=config)

    if json_mode:
        # Build JSON representation
        nodes = []
        for event in weave.monoid.events:
            node_data = renderer.get_turn_info(event.id)
            if node_data:
                nodes.append(node_data)

        result = {
            "total_nodes": len(nodes),
            "nodes": nodes,
        }
        if agent_id:
            from weave import CausalCone

            cone = CausalCone(weave)
            result["cone_size"] = cone.cone_size(agent_id)
            result["compression_ratio"] = cone.compression_ratio(agent_id)

        _emit_output(
            json_module.dumps(result, indent=2, default=str),
            result,
            ctx,
        )
    else:
        console = Console()

        # Render DAG
        panel = renderer.render(agent_id=agent_id)
        console.print(panel)

        # Show stats
        stats = renderer.render_stats()
        console.print(stats)

        # Show compression if agent specified
        if agent_id:
            from weave import CausalCone

            cone = CausalCone(weave)
            ratio = cone.compression_ratio(agent_id)
            console.print(
                f"\n[cyan]Cone for {agent_id}:[/] "
                f"{cone.cone_size(agent_id)} events ({ratio:.1%} compression)"
            )

    return 0


def _launch_dag_tui(
    weave: Any,
    agent_id: str | None,
    show_thoughts: bool,
) -> int:
    """Launch interactive TUI for DAG visualization."""
    try:
        from agents.i.screens.turn_dag import TurnDAGConfig, TurnDAGRenderer
        from textual.app import App
        from textual.containers import Container, Horizontal
        from textual.widgets import Footer, Header, Static

    except ImportError:
        print(
            "[DAG] Interactive mode requires textual. Install with: pip install textual"
        )
        return 1

    class TurnDAGApp(App[None]):
        """Interactive Turn DAG viewer."""

        BINDINGS = [
            ("q", "quit", "Quit"),
            ("t", "toggle_thoughts", "Toggle Thoughts"),
            ("r", "refresh", "Refresh"),
        ]

        CSS = """
        Screen {
            layout: vertical;
        }
        #dag-container {
            height: 100%;
            padding: 1;
        }
        """

        def __init__(
            self, weave: Any, agent_id: str | None, show_thoughts: bool
        ) -> None:
            super().__init__()
            self.weave = weave
            self.agent_id = agent_id
            self.show_thoughts = show_thoughts

        def compose(self) -> Any:
            yield Header()
            yield Container(Static(id="dag-view"), id="dag-container")
            yield Footer()

        def on_mount(self) -> None:
            self._render_dag()

        def _render_dag(self) -> None:
            config = TurnDAGConfig(show_thoughts=self.show_thoughts)
            renderer = TurnDAGRenderer(weave=self.weave, config=config)
            panel = renderer.render(agent_id=self.agent_id)

            dag_view = self.query_one("#dag-view", Static)
            dag_view.update(panel)

        def action_toggle_thoughts(self) -> None:
            self.show_thoughts = not self.show_thoughts
            self._render_dag()

        def action_refresh(self) -> None:
            self._render_dag()

    app = TurnDAGApp(weave, agent_id, show_thoughts)
    app.run()
    return 0


def cmd_fork(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Fork from a specific turn for debugging.

    Args:
        args: Command-line arguments
        ctx: Optional InvocationContext for dual-channel output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("fork", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_fork_help()
        return 0

    # Parse --name
    fork_name: str | None = None
    for i, arg in enumerate(args):
        if arg == "--name" and i + 1 < len(args):
            fork_name = args[i + 1]

    # Get turn_id (first non-flag argument)
    turn_id: str | None = None
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg == "--name":
            skip_next = True
            continue
        if arg.startswith("-"):
            continue
        turn_id = arg
        break

    if not turn_id:
        _emit_output(
            "[FORK] No turn ID specified.\n"
            "Usage: kgents fork <turn_id> [--name <name>]",
            {"error": "No turn ID specified"},
            ctx,
        )
        return 1

    try:
        return _execute_fork(turn_id, fork_name, ctx)
    except Exception as e:
        _emit_output(
            f"[FORK] Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _execute_fork(
    turn_id: str,
    fork_name: str | None,
    ctx: "InvocationContext | None",
) -> int:
    """Execute the fork command."""
    from agents.i.screens.turn_dag import TurnDAGRenderer
    from rich.console import Console

    # Get the global weave
    weave = _get_global_weave()

    if len(weave) == 0:
        _emit_output(
            "[FORK] No turns recorded yet.",
            {"status": "empty"},
            ctx,
        )
        return 0

    # Find the turn
    event = weave.get_event(turn_id)
    if event is None:
        # Try partial match
        for e in weave.monoid.events:
            if e.id.startswith(turn_id):
                event = e
                turn_id = e.id
                break

    if event is None:
        _emit_output(
            f"[FORK] Turn not found: {turn_id}",
            {"error": f"Turn not found: {turn_id}"},
            ctx,
        )
        return 1

    # Create forked weave
    renderer = TurnDAGRenderer(weave=weave)
    forked_weave = renderer.fork_from(turn_id, fork_name)

    # Generate fork name if not provided
    if fork_name is None:
        fork_name = f"fork-{turn_id[:8]}-{datetime.now().strftime('%H%M%S')}"

    # Store the forked weave (in a real implementation, this would persist)
    _store_forked_weave(fork_name, forked_weave)

    console = Console()
    console.print(f"[green]Created fork:[/] {fork_name}")
    console.print(f"[dim]  From turn:[/] {turn_id[:16]}...")
    console.print(f"[dim]  Contains:[/] {len(forked_weave)} events")
    console.print()
    console.print("[cyan]To use this fork:[/]")
    console.print(f"  export KGENTS_WEAVE_FORK={fork_name}")

    return 0


# =============================================================================
# Helper Functions
# =============================================================================


def _get_global_weave() -> Any:
    """
    Get the global Weave instance from lifecycle state.

    The Weave is shared across all agents and CLI commands.
    This enables:
    - Turn debugging via `kg turns` and `kg dag`
    - CausalCone context projection
    - Compression metrics for H1 validation

    Returns empty weave if lifecycle not bootstrapped.
    """
    # Primary source: lifecycle state's weave
    try:
        from protocols.cli.hollow import get_lifecycle_state

        state = get_lifecycle_state()
        if state and state.weave is not None:
            return state.weave
    except ImportError:
        pass

    # Fallback: storage provider (if it has weave support)
    try:
        from protocols.cli.hollow import get_storage_provider

        storage = get_storage_provider()
        if storage and hasattr(storage, "get_weave"):
            return storage.get_weave()
    except ImportError:
        pass

    # Last resort: demo weave or empty weave
    from weave import TheWeave

    return _get_demo_weave() or TheWeave()


def _get_demo_weave() -> Any:
    """
    Get a demo weave with sample turns for testing.

    Returns None if no demo data should be shown.
    """
    import os

    # Only create demo weave if explicitly requested
    if os.environ.get("KGENTS_DEMO_TURNS") != "1":
        return None

    from weave import TheWeave, Turn, TurnType

    weave = TheWeave()

    # Create some demo turns
    demo_turns = [
        Turn.create_turn(
            content="Hello, I'm starting a new task",
            source="k-gent",
            turn_type=TurnType.SPEECH,
            confidence=0.95,
        ),
        Turn.create_turn(
            content="Analyzing the request",
            source="k-gent",
            turn_type=TurnType.THOUGHT,
            confidence=0.8,
        ),
        Turn.create_turn(
            content="Reading file: /path/to/code.py",
            source="k-gent",
            turn_type=TurnType.ACTION,
            confidence=0.9,
        ),
        Turn.create_turn(
            content="Here's what I found",
            source="k-gent",
            turn_type=TurnType.SPEECH,
            confidence=0.85,
        ),
    ]

    for turn in demo_turns:
        weave.monoid.append_mut(turn)

    return weave


def _store_forked_weave(name: str, weave: Any) -> None:
    """
    Store a forked weave for later use.

    In a real implementation, this would persist to disk or DB.
    """
    # For now, just store in a global dict (in-memory only)
    global _forked_weaves
    if "_forked_weaves" not in globals():
        _forked_weaves = {}  # type: ignore[name-defined]
    _forked_weaves[name] = weave  # type: ignore[name-defined]


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """
    Emit output via dual-channel if ctx available, else print.
    """
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)


__all__ = [
    "cmd_turns",
    "cmd_dag",
    "cmd_fork",
]
