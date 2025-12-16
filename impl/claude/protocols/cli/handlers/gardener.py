"""
Gardener CLI Handler: Development Session Management.

concept.gardener enables structured development sessions following
the SENSE → ACT → REFLECT polynomial cycle.

Usage:
    kg gardener                     # Show active session status
    kg gardener session             # Session state machine details
    kg gardener start [NAME]        # Start a new session
    kg gardener advance             # Advance to next phase
    kg gardener cycle               # Start a new cycle (from REFLECT)
    kg gardener manifest            # Show polynomial visualization
    kg gardener intent <description> # Set session intent
    kg gardener sessions            # List recent sessions

Wave 1: Hero Path Polish
Foundation 3: Visible Polynomial State

AGENTESE: concept.gardener.*

See: plans/core-apps/the-gardener.md
"""

from __future__ import annotations

import asyncio
import threading
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# Rich imports for beautiful output (graceful degradation)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None  # type: ignore[assignment]

# Path display for Foundation 1
from protocols.cli.path_display import (
    apply_path_flags,
    display_path_header,
    parse_path_flags,
)

# =============================================================================
# Context Management (Thread-Safe)
# =============================================================================

_ctx: Any = None
_ctx_lock = threading.Lock()


async def _get_context() -> Any:
    """Get or create GardenerContext (thread-safe)."""
    global _ctx
    if _ctx is None:
        with _ctx_lock:
            if _ctx is None:
                from agents.gardener.handlers import GardenerContext
                from agents.gardener.persistence import create_session_store

                store = create_session_store()
                _ctx = GardenerContext(store=store)
                await _ctx.init()
    return _ctx


def _run_async(coro: Any) -> Any:
    """Run an async coroutine synchronously."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# =============================================================================
# Output Helpers
# =============================================================================


def _emit(message: str, data: dict[str, Any], ctx: "InvocationContext | None") -> None:
    """Emit output to console and optional context."""
    if ctx is not None:
        ctx.output(message, data)
    else:
        print(message)


def _print_help() -> None:
    """Print help for gardener command."""
    print(__doc__)


def _print_banner() -> None:
    """Print the gardener banner."""
    if RICH_AVAILABLE:
        banner = Panel(
            "[bold green]The Gardener[/] - Development Session Manager\n\n"
            '[dim]SENSE → ACT → REFLECT: The rhythm of intentional development.[/]',
            border_style="green",
            padding=(1, 2),
        )
        console.print(banner)
    else:
        print("=" * 60)
        print("  The Gardener - Development Session Manager")
        print("  SENSE → ACT → REFLECT")
        print("=" * 60)


# =============================================================================
# Phase Display
# =============================================================================


PHASE_CONFIG = {
    "SENSE": {"emoji": "👁️", "label": "Sensing", "color": "cyan", "desc": "Gather context"},
    "ACT": {"emoji": "⚡", "label": "Acting", "color": "yellow", "desc": "Execute intent"},
    "REFLECT": {"emoji": "💭", "label": "Reflecting", "color": "purple", "desc": "Consolidate learnings"},
}


def _render_polynomial(phase: str) -> str:
    """Render ASCII polynomial state machine."""
    states = ["SENSE", "ACT", "REFLECT"]
    parts = []

    for i, s in enumerate(states):
        is_current = s == phase
        emoji = PHASE_CONFIG[s]["emoji"]
        label = PHASE_CONFIG[s]["label"]

        if is_current:
            if RICH_AVAILABLE:
                parts.append(f"[bold lime]◀ {emoji} {label} ▶[/]")
            else:
                parts.append(f"◀ {emoji} {label} ▶")
        else:
            if RICH_AVAILABLE:
                parts.append(f"[dim]  {emoji} {label}  [/]")
            else:
                parts.append(f"  {emoji} {label}  ")

        if i < len(states) - 1:
            parts.append(" → ")

    return "".join(parts)


# =============================================================================
# Commands
# =============================================================================


async def _show_status(ctx: "InvocationContext | None") -> int:
    """Show current session status."""
    display_path_header(
        path="concept.gardener.session.manifest",
        aspect="manifest",
        effects=["SESSION_DISPLAYED"],
    )

    gctx = await _get_context()

    if not gctx.active_session:
        if RICH_AVAILABLE:
            console.print(
                Panel(
                    "[dim]No active gardener session.[/]\n\n"
                    "Start one with: [cyan]kg gardener start[/]",
                    title="The Gardener",
                    border_style="dim",
                )
            )
        else:
            _emit("No active session. Start one with: kg gardener start", {}, ctx)
        return 0

    session = gctx.active_session
    state = session.state

    if RICH_AVAILABLE:
        # Header
        console.print(f"\n[bold green]Session:[/] {state.name}")
        console.print(f"[dim]ID: {session.session_id}[/]")

        # Polynomial
        console.print(f"\n[bold]State Machine:[/]")
        console.print(f"  {_render_polynomial(state.phase)}")

        # Current phase details
        phase_cfg = PHASE_CONFIG[state.phase]
        console.print(f"\n[bold]Current Phase:[/] [{phase_cfg['color']}]{phase_cfg['emoji']} {phase_cfg['label']}[/]")
        console.print(f"  {phase_cfg['desc']}")

        # Intent
        if state.intent:
            console.print(f"\n[bold]Intent:[/]")
            console.print(f"  {state.intent.get('description', 'No description')}")
            console.print(f"  [dim]Priority: {state.intent.get('priority', 'normal')}[/]")

        # Plan
        if state.plan_path:
            console.print(f"\n[bold]Plan:[/] [lime]{state.plan_path}[/]")

        # Stats
        console.print(f"\n[bold]Counts:[/]")
        console.print(f"  Sense: {state.sense_count} | Act: {state.act_count} | Reflect: {state.reflect_count}")

        # Next action hint
        valid_next = {
            "SENSE": "advance",
            "ACT": "advance or rollback",
            "REFLECT": "cycle",
        }
        console.print(f"\n[dim]Next: [cyan]kg gardener {valid_next.get(state.phase, 'advance')}[/][/]")

    else:
        _emit(f"Session: {state.name}", {"session_id": session.session_id}, ctx)
        _emit(f"Phase: {state.phase}", {"phase": state.phase}, ctx)
        _emit(_render_polynomial(state.phase), {}, ctx)

    return 0


async def _start_session(args: list[str], ctx: "InvocationContext | None") -> int:
    """Start a new gardener session."""
    from protocols.agentese.node import Observer

    display_path_header(
        path="concept.gardener.session.define",
        aspect="define",
        effects=["SESSION_CREATED", "PHASE_INITIALIZED"],
    )

    name = " ".join(args) if args else None

    gctx = await _get_context()

    from agents.gardener.handlers import handle_session_create

    observer = Observer.guest().to_dict() if hasattr(Observer, "guest") else {}

    kwargs: dict[str, Any] = {}
    if name:
        kwargs["name"] = name

    result = await handle_session_create(gctx, observer, **kwargs)

    if result.get("status") == "error":
        _emit(f"Error: {result.get('message')}", {"error": result.get("message")}, ctx)
        return 1

    session_data = result.get("session", {})

    if RICH_AVAILABLE:
        console.print(
            Panel(
                f"[bold green]Session Started![/]\n\n"
                f"Name: [cyan]{session_data.get('name', 'Unnamed')}[/]\n"
                f"ID: {session_data.get('session_id', 'unknown')[:8]}...\n"
                f"Phase: [yellow]SENSE[/] (Gather context)\n\n"
                f"[dim]The session begins in SENSE phase. Read plans, explore codebase, gather context.[/]",
                title="The Gardener",
                border_style="green",
            )
        )
    else:
        _emit(f"Session started: {session_data.get('name')}", session_data, ctx)

    return 0


async def _advance_session(ctx: "InvocationContext | None") -> int:
    """Advance to the next phase."""
    from protocols.agentese.node import Observer

    display_path_header(
        path="concept.gardener.session.advance",
        aspect="advance",
        effects=["PHASE_TRANSITIONED"],
    )

    gctx = await _get_context()

    if not gctx.active_session:
        _emit("No active session. Start one with: kg gardener start", {}, ctx)
        return 1

    from agents.gardener.handlers import handle_session_advance

    observer = Observer.guest().to_dict() if hasattr(Observer, "guest") else {}

    result = await handle_session_advance(gctx, observer)

    if result.get("status") == "error":
        _emit(f"Error: {result.get('message')}", {"error": result.get("message")}, ctx)
        return 1

    new_phase = gctx.active_session.state.phase
    phase_cfg = PHASE_CONFIG[new_phase]

    if RICH_AVAILABLE:
        console.print(f"\n[bold green]Advanced![/]")
        console.print(f"\nNew phase: [{phase_cfg['color']}]{phase_cfg['emoji']} {phase_cfg['label']}[/]")
        console.print(f"{phase_cfg['desc']}")
        console.print(f"\n{_render_polynomial(new_phase)}")
    else:
        _emit(f"Advanced to: {new_phase}", {"phase": new_phase}, ctx)

    return 0


async def _show_manifest(ctx: "InvocationContext | None") -> int:
    """Show polynomial visualization in detail."""
    display_path_header(
        path="concept.gardener.session.polynomial.manifest",
        aspect="manifest",
        effects=["POLYNOMIAL_DISPLAYED", "STATE_VISIBLE"],
    )

    gctx = await _get_context()

    if not gctx.active_session:
        _emit("No active session.", {}, ctx)
        return 1

    state = gctx.active_session.state

    if RICH_AVAILABLE:
        # Full polynomial diagram
        console.print("\n[bold]Polynomial State Machine:[/]")
        console.print()

        # ASCII diagram
        diagram = """
    ┌─────────┐     advance     ┌─────────┐     advance    ┌───────────┐
    │  SENSE  │────────────────▶│   ACT   │───────────────▶│  REFLECT  │
    │   👁️   │                  │   ⚡    │                 │    💭     │
    └─────────┘                  └─────────┘                 └───────────┘
         ▲                            │                           │
         │                            │ rollback                  │
         │                            ▼                           │
         │                       ┌─────────┐                      │
         └───────────────────────│ SENSE ◀─┼──────────────────────┘
                   cycle         └─────────┘     cycle
        """

        # Highlight current state
        current = state.phase
        for phase in ["SENSE", "ACT", "REFLECT"]:
            if phase == current:
                diagram = diagram.replace(f"│  {phase}  │", f"│▶{phase}◀│")

        console.print(diagram)

        # Valid transitions
        valid = {
            "SENSE": ["ACT"],
            "ACT": ["REFLECT", "SENSE (rollback)"],
            "REFLECT": ["SENSE (cycle)"],
        }

        console.print(f"[bold]Current:[/] {current}")
        console.print(f"[bold]Valid transitions:[/] {', '.join(valid.get(current, []))}")

        # History
        console.print(f"\n[bold]Session History:[/]")
        console.print(f"  SENSE entered: {state.sense_count}x")
        console.print(f"  ACT entered: {state.act_count}x")
        console.print(f"  REFLECT completed: {state.reflect_count}x")

    else:
        _emit(f"Current phase: {state.phase}", {"phase": state.phase}, ctx)
        _emit(_render_polynomial(state.phase), {}, ctx)

    return 0


async def _list_sessions(ctx: "InvocationContext | None") -> int:
    """List recent sessions."""
    display_path_header(
        path="concept.gardener.sessions.manifest",
        aspect="manifest",
        effects=["SESSIONS_LISTED"],
    )

    gctx = await _get_context()
    recent = await gctx.store.list_recent(limit=10)

    if not recent:
        _emit("No sessions found.", {}, ctx)
        return 0

    active_id = gctx.active_session.session_id if gctx.active_session else None

    if RICH_AVAILABLE:
        table = Table(title="Recent Sessions", show_header=True)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Name", style="cyan")
        table.add_column("Phase", style="yellow")
        table.add_column("Active", justify="center")

        for s in recent:
            is_active = s.id == active_id
            active_mark = "[green]★[/]" if is_active else ""
            table.add_row(
                s.id[:8] + "...",
                s.name,
                s.phase,
                active_mark,
            )

        console.print(table)
    else:
        _emit(f"Found {len(recent)} sessions:", {}, ctx)
        for s in recent:
            active_mark = " [ACTIVE]" if s.id == active_id else ""
            _emit(f"  {s.id[:8]}... {s.name} ({s.phase}){active_mark}", {}, ctx)

    return 0


# =============================================================================
# Main Entry Point
# =============================================================================


def cmd_gardener(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    concept.gardener: Development Session Management.

    Manage structured development sessions with the SENSE → ACT → REFLECT cycle.
    """
    # Parse path visibility flags (Wave 0 Foundation 1)
    args_list = list(args)
    args_list, show_paths, trace_mode = parse_path_flags(args_list)
    apply_path_flags(show_paths, trace_mode)

    if "--help" in args_list or "-h" in args_list:
        _print_help()
        return 0

    if not args_list:
        return _run_async(_show_status(ctx))

    subcommand = args_list[0].lower()

    match subcommand:
        case "status" | "session":
            return _run_async(_show_status(ctx))

        case "start" | "create" | "new":
            return _run_async(_start_session(args_list[1:], ctx))

        case "advance" | "next":
            return _run_async(_advance_session(ctx))

        case "cycle":
            # Cycle is just advance from REFLECT
            return _run_async(_advance_session(ctx))

        case "manifest" | "polynomial" | "poly":
            return _run_async(_show_manifest(ctx))

        case "sessions" | "list":
            return _run_async(_list_sessions(ctx))

        case "help":
            _print_help()
            return 0

        case _:
            _emit(f"Unknown command: {subcommand}", {"error": subcommand}, ctx)
            _emit("Use 'kg gardener --help' for available commands.", {}, ctx)
            return 1
