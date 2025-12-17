"""
Gardener CLI Handler: Development Session Management.

concept.gardener enables structured development sessions following
the SENSE → ACT → REFLECT polynomial cycle.

Usage:
    kg gardener                     # Show active session status + garden
    kg gardener session             # Session state machine details
    kg gardener start [NAME]        # Start a new session
    kg gardener advance             # Advance to next phase
    kg gardener cycle               # Start a new cycle (from REFLECT)
    kg gardener manifest            # Show polynomial visualization
    kg gardener intent <description> # Set session intent
    kg gardener sessions            # List recent sessions
    kg gardener chat                # Interactive tending chat (ChatFlow)
    kg gardener plant <idea>        # Plant a new idea in the garden
    kg gardener harvest             # Show ideas ready to harvest (flowers)
    kg gardener water <idea-id>     # Nurture an idea to boost confidence
    kg gardener harvest-to-brain    # Harvest flowers to Brain crystals
    kg gardener surprise            # Serendipity from the void

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
# PersonaGarden for idea lifecycle
from agents.k.garden import (
    EntryType,
    GardenLifecycle,
    PersonaGarden,
    get_garden,
)
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
            "[dim]SENSE → ACT → REFLECT: The rhythm of intentional development.[/]",
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
    "SENSE": {
        "emoji": "👁️",
        "label": "Sensing",
        "color": "cyan",
        "desc": "Gather context",
    },
    "ACT": {
        "emoji": "⚡",
        "label": "Acting",
        "color": "yellow",
        "desc": "Execute intent",
    },
    "REFLECT": {
        "emoji": "💭",
        "label": "Reflecting",
        "color": "purple",
        "desc": "Consolidate learnings",
    },
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


async def _show_garden_compact(stats: Any) -> None:
    """Show compact garden status (used in main status view)."""
    from agents.k.garden import GardenStats

    if not isinstance(stats, GardenStats):
        return

    lifecycle_icons = {
        "seed": "🌱",
        "sapling": "🌿",
        "tree": "🌳",
        "flower": "🌸",
        "compost": "🍂",
    }

    if RICH_AVAILABLE:
        console.print("\n[bold green]Garden[/]")

        # Compact one-line lifecycle counts
        parts = []
        for lc in ["seed", "sapling", "tree", "flower"]:
            count = stats.by_lifecycle.get(lc, 0)
            if count > 0:
                icon = lifecycle_icons.get(lc, " ")
                parts.append(f"{icon}{count}")

        if parts:
            console.print(f"  {' '.join(parts)}")
        else:
            console.print("  [dim]Empty - plant an idea![/]")

        # Show flower alert
        flower_count = stats.by_lifecycle.get("flower", 0)
        if flower_count > 0:
            console.print(f"  [yellow]🌸 {flower_count} ready to harvest![/]")

        console.print(f"  [dim]Season: {stats.current_season.value}[/]")
    else:
        print(f"Garden: {stats.total_entries} entries")


# =============================================================================
# Commands
# =============================================================================


async def _show_status(ctx: "InvocationContext | None") -> int:
    """Show current session status and garden overview."""
    display_path_header(
        path="concept.gardener.session.manifest",
        aspect="manifest",
        effects=["SESSION_DISPLAYED", "GARDEN_OVERVIEW"],
    )

    gctx = await _get_context()

    # Get garden stats for display
    garden = get_garden()
    garden_stats = await garden.stats()

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
            # Still show garden status even without session
            await _show_garden_compact(garden_stats)
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
        console.print("\n[bold]State Machine:[/]")
        console.print(f"  {_render_polynomial(state.phase)}")

        # Current phase details
        phase_cfg = PHASE_CONFIG[state.phase]
        console.print(
            f"\n[bold]Current Phase:[/] [{phase_cfg['color']}]{phase_cfg['emoji']} {phase_cfg['label']}[/]"
        )
        console.print(f"  {phase_cfg['desc']}")

        # Intent
        if state.intent:
            console.print("\n[bold]Intent:[/]")
            console.print(f"  {state.intent.get('description', 'No description')}")
            console.print(
                f"  [dim]Priority: {state.intent.get('priority', 'normal')}[/]"
            )

        # Plan
        if state.plan_path:
            console.print(f"\n[bold]Plan:[/] [lime]{state.plan_path}[/]")

        # Stats
        console.print("\n[bold]Counts:[/]")
        console.print(
            f"  Sense: {state.sense_count} | Act: {state.act_count} | Reflect: {state.reflect_count}"
        )

        # Next action hint
        valid_next = {
            "SENSE": "advance",
            "ACT": "advance or rollback",
            "REFLECT": "cycle",
        }
        console.print(
            f"\n[dim]Next: [cyan]kg gardener {valid_next.get(state.phase, 'advance')}[/][/]"
        )

        # Garden status
        await _show_garden_compact(garden_stats)

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
        console.print("\n[bold green]Advanced![/]")
        console.print(
            f"\nNew phase: [{phase_cfg['color']}]{phase_cfg['emoji']} {phase_cfg['label']}[/]"
        )
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
        console.print(
            f"[bold]Valid transitions:[/] {', '.join(valid.get(current, []))}"
        )

        # History
        console.print("\n[bold]Session History:[/]")
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
# Garden Commands: Idea Lifecycle Management
# =============================================================================


async def _show_garden_status(ctx: "InvocationContext | None") -> int:
    """Show garden lifecycle distribution."""
    display_path_header(
        path="self.garden.manifest",
        aspect="manifest",
        effects=["GARDEN_DISPLAYED"],
    )

    garden = get_garden()
    stats = await garden.stats()

    lifecycle_icons = {
        "seed": "🌱",
        "sapling": "🌿",
        "tree": "🌳",
        "flower": "🌸",
        "compost": "🍂",
    }

    if RICH_AVAILABLE:
        console.print("\n[bold green]Garden Status[/]")
        console.print()

        # Lifecycle distribution
        for lc in ["seed", "sapling", "tree", "flower", "compost"]:
            count = stats.by_lifecycle.get(lc, 0)
            icon = lifecycle_icons.get(lc, " ")
            label = lc.capitalize()
            extra = ""
            if lc == "flower" and count > 0:
                extra = " [yellow](ready to harvest!)[/]"
            console.print(f"  {icon} {label}: {count}{extra}")

        console.print()
        console.print(f"  [dim]Season: {stats.current_season.value.upper()}[/]")
        console.print(f"  [dim]Total entries: {stats.total_entries}[/]")

        if stats.total_entries == 0:
            console.print("\n  [dim]Garden is empty. Plant an idea:[/]")
            console.print('  [cyan]kg gardener plant "your insight here"[/]')
        else:
            # Show recent entries with IDs
            entries = list(garden.entries.values())
            non_compost = [e for e in entries if e.lifecycle != GardenLifecycle.COMPOST]
            by_confidence = sorted(non_compost, key=lambda e: -e.confidence)[:5]

            if by_confidence:
                console.print("\n  [bold]Top ideas (by confidence):[/]")
                for entry in by_confidence:
                    icon = lifecycle_icons.get(entry.lifecycle.value, " ")
                    # Truncate ID for display
                    short_id = entry.id[:16] if len(entry.id) > 16 else entry.id
                    console.print(
                        f"    {icon} [cyan]{entry.content[:40]}[/] "
                        f"[dim]({entry.confidence:.0%})[/]"
                    )
                    console.print(f"       [dim]ID: {short_id}[/]")

            console.print(
                '\n  [dim]Water an idea: kg gardener water <id> "evidence"[/]'
            )
    else:
        _emit("Garden Status:", {}, ctx)
        for lc in ["seed", "sapling", "tree", "flower", "compost"]:
            count = stats.by_lifecycle.get(lc, 0)
            icon = lifecycle_icons.get(lc, " ")
            _emit(f"  {icon} {lc}: {count}", {}, ctx)
        _emit(f"  Season: {stats.current_season.value}", {}, ctx)

    return 0


async def _plant_idea(args: list[str], ctx: "InvocationContext | None") -> int:
    """Plant a new idea in the garden."""
    display_path_header(
        path="self.garden.plant",
        aspect="define",
        effects=["IDEA_PLANTED", "SEED_CREATED"],
    )

    if not args:
        _emit('Error: No idea provided. Usage: kg gardener plant "your idea"', {}, ctx)
        return 1

    idea = " ".join(args).strip()
    if not idea:
        _emit("Error: Idea cannot be empty.", {}, ctx)
        return 1

    garden = get_garden()

    # Plant as an insight with moderate confidence
    entry = await garden.plant(
        content=idea,
        entry_type=EntryType.INSIGHT,
        source="manual",
        confidence=0.4,  # Start as sapling (>= 0.4)
    )

    lifecycle_icons = {
        "seed": "🌱",
        "sapling": "🌿",
        "tree": "🌳",
        "flower": "🌸",
        "compost": "🍂",
    }

    icon = lifecycle_icons.get(entry.lifecycle.value, "🌱")

    if RICH_AVAILABLE:
        console.print(
            Panel(
                f"[bold green]Idea Planted![/]\n\n"
                f"{icon} [cyan]{idea}[/]\n\n"
                f"[dim]Lifecycle: {entry.lifecycle.value.upper()}\n"
                f"Confidence: {entry.confidence:.0%}\n"
                f"ID: {entry.id[:12]}...[/]",
                title="Garden",
                border_style="green",
            )
        )
        console.print("\n[dim]Nurture it with evidence, or wait for it to bloom.[/]")
    else:
        _emit(f"{icon} Planted: {idea}", {"entry_id": entry.id}, ctx)
        _emit(f"  Lifecycle: {entry.lifecycle.value}", {}, ctx)

    return 0


async def _harvest_ideas(ctx: "InvocationContext | None") -> int:
    """Show ideas ready to harvest (FLOWER stage)."""
    display_path_header(
        path="self.garden.harvest",
        aspect="manifest",
        effects=["FLOWERS_DISPLAYED", "HARVEST_READY"],
    )

    garden = get_garden()
    flowers = await garden.flowers()

    if not flowers:
        if RICH_AVAILABLE:
            console.print("\n[dim]No flowers ready for harvest yet.[/]")
            console.print(
                "\n[dim]Ideas need to reach high confidence (90%+) to bloom.[/]"
            )
            console.print(
                "[dim]Nurture them with evidence or wait for time to work.[/]"
            )

            # Show what's closest to blooming
            trees = await garden.trees()
            if trees:
                console.print("\n[bold]Closest to bloom (trees):[/]")
                for tree in sorted(trees, key=lambda t: -t.confidence)[:3]:
                    console.print(f"  🌳 {tree.content[:50]} ({tree.confidence:.0%})")
        else:
            _emit("No flowers ready for harvest.", {}, ctx)
        return 0

    if RICH_AVAILABLE:
        console.print("\n[bold yellow]🌸 Ready to Harvest[/]")
        console.print()

        for flower in flowers:
            console.print(f"  🌸 [cyan]{flower.content}[/]")
            console.print(
                f"     [dim]Confidence: {flower.confidence:.0%} | Age: {flower.age_days:.0f} days[/]"
            )
            if flower.evidence:
                console.print(f"     [dim]Evidence: {len(flower.evidence)} items[/]")
            console.print()

        console.print(f"[dim]{len(flowers)} idea(s) ready for harvest.[/]")
        console.print("[dim]Harvested ideas can become Brain crystals.[/]")
    else:
        _emit(f"Flowers ready to harvest: {len(flowers)}", {}, ctx)
        for flower in flowers:
            _emit(f"  🌸 {flower.content}", {}, ctx)

    return 0


async def _water_idea(args: list[str], ctx: "InvocationContext | None") -> int:
    """Water/nurture a specific idea to boost its confidence."""
    display_path_header(
        path="self.garden.nurture",
        aspect="refine",
        effects=["IDEA_NURTURED", "CONFIDENCE_BOOSTED"],
    )

    if not args:
        if RICH_AVAILABLE:
            console.print("\n[red]Error:[/] No idea ID provided.")
            console.print("\nUsage:")
            console.print("  [cyan]kg gardener water <idea-id> [evidence][/]")
            console.print("\nExamples:")
            console.print('  kg gardener water insight_1 "Validated in production"')
            console.print("  kg gardener water insight_1")
            console.print("\n[dim]Tip: Use 'kg gardener garden' to see idea IDs.[/]")
        else:
            _emit(
                "Error: No idea ID provided. Usage: kg gardener water <idea-id>",
                {},
                ctx,
            )
        return 1

    idea_ref = args[0]
    evidence = " ".join(args[1:]).strip() if len(args) > 1 else "Manual nurturing"

    garden = get_garden()

    # Find the idea by ID or partial ID
    target_entry = None
    for entry_id, entry in garden.entries.items():
        if entry_id == idea_ref or entry_id.startswith(idea_ref):
            target_entry = entry
            break

    if target_entry is None:
        # Try matching by content substring
        for entry in garden.entries.values():
            if idea_ref.lower() in entry.content.lower():
                target_entry = entry
                break

    if target_entry is None:
        if RICH_AVAILABLE:
            console.print(f"\n[red]Error:[/] No idea found matching '{idea_ref}'")
            console.print(
                "\n[dim]Use 'kg gardener garden' to list ideas with their IDs.[/]"
            )
        else:
            _emit(f"Error: No idea found matching '{idea_ref}'", {}, ctx)
        return 1

    if target_entry.lifecycle == GardenLifecycle.COMPOST:
        if RICH_AVAILABLE:
            console.print("\n[yellow]Warning:[/] Cannot water composted ideas.")
            console.print(f"[dim]'{target_entry.content[:40]}...' is in compost.[/]")
        else:
            _emit("Cannot water composted ideas.", {}, ctx)
        return 1

    # Nurture the idea
    old_confidence = target_entry.confidence
    old_lifecycle = target_entry.lifecycle
    updated = await garden.nurture(target_entry.id, evidence)

    if updated is None:
        _emit("Error: Failed to nurture idea.", {}, ctx)
        return 1

    lifecycle_icons = {
        "seed": "🌱",
        "sapling": "🌿",
        "tree": "🌳",
        "flower": "🌸",
        "compost": "🍂",
    }
    icon = lifecycle_icons.get(updated.lifecycle.value, "💧")

    if RICH_AVAILABLE:
        console.print("\n[bold green]💧 Idea Watered![/]")
        console.print()
        console.print(f"  {icon} [cyan]{updated.content}[/]")
        console.print()
        console.print(f'  [dim]Evidence added:[/] "{evidence}"')
        console.print(
            f"  [dim]Confidence:[/] {old_confidence:.0%} → [green]{updated.confidence:.0%}[/]"
        )

        if updated.lifecycle != old_lifecycle:
            old_icon = lifecycle_icons.get(old_lifecycle.value, " ")
            new_icon = lifecycle_icons.get(updated.lifecycle.value, " ")
            console.print(
                f"  [dim]Lifecycle:[/] {old_icon} {old_lifecycle.value} → "
                f"[green]{new_icon} {updated.lifecycle.value}[/]"
            )

        if updated.lifecycle == GardenLifecycle.FLOWER:
            console.print("\n  [yellow]🌸 This idea has bloomed! Ready for harvest.[/]")
    else:
        _emit(f"💧 Watered: {updated.content[:40]}", {}, ctx)
        _emit(f"  Confidence: {old_confidence:.0%} → {updated.confidence:.0%}", {}, ctx)

    return 0


async def _harvest_to_brain(ctx: "InvocationContext | None") -> int:
    """Harvest flower ideas and capture them as Brain crystals."""
    display_path_header(
        path="self.garden.harvest.brain",
        aspect="define",
        effects=["IDEAS_HARVESTED", "CRYSTALS_CREATED", "CROSS_JEWEL_FLOW"],
    )

    garden = get_garden()
    flowers = await garden.flowers()

    if not flowers:
        if RICH_AVAILABLE:
            console.print("\n[dim]No flowers ready for harvest yet.[/]")
            console.print("[dim]Ideas need to reach 90%+ confidence to bloom.[/]")
        else:
            _emit("No flowers ready for harvest.", {}, ctx)
        return 0

    # Get brain crystal
    try:
        from agents.brain import get_brain_crystal

        brain = await get_brain_crystal()
    except ImportError:
        _emit("Error: Brain module not available.", {}, ctx)
        return 1

    harvested = []
    for flower in flowers:
        # Capture to brain with garden metadata
        content = f"[Harvested Idea] {flower.content}"
        metadata = {
            "source": "gardener_harvest",
            "garden_entry_id": flower.id,
            "evidence_count": len(flower.evidence),
            "age_days": flower.age_days,
            "entry_type": flower.entry_type.value,
        }

        crystal_id = await brain.capture(content, metadata=metadata)
        harvested.append((flower, crystal_id))

        # Compost the flower after harvesting (it has been gathered)
        await garden.compost(flower.id)

    if RICH_AVAILABLE:
        console.print("\n[bold green]🌾 Harvest Complete![/]")
        console.print(f"\n  Harvested {len(harvested)} idea(s) to Brain:\n")

        for flower, crystal_id in harvested:
            console.print(f"  🌸 → 💎 [cyan]{flower.content[:50]}[/]")
            console.print(f"       [dim]Crystal ID: {crystal_id[:12]}...[/]")

        console.print("\n  [dim]Harvested ideas have been composted in the garden.[/]")
        console.print("  [dim]Use 'kg brain search' to find them in memory.[/]")
    else:
        _emit(f"Harvested {len(harvested)} ideas to Brain crystals.", {}, ctx)

    return 0


async def _surprise(ctx: "InvocationContext | None") -> int:
    """Serendipity from the void - surface unexpected connections."""
    import random

    display_path_header(
        path="void.garden.sip",
        aspect="sip",
        effects=["SERENDIPITY_INVOKED", "CONNECTION_SURFACED"],
    )

    garden = get_garden()
    stats = await garden.stats()

    if stats.total_entries == 0:
        if RICH_AVAILABLE:
            console.print("\n[dim]The void echoes... the garden is empty.[/]")
            console.print(
                '[dim]Plant some ideas first: [cyan]kg gardener plant "idea"[/][/]'
            )
        else:
            _emit("Garden is empty. Plant ideas first.", {}, ctx)
        return 0

    # Collect all non-composted entries
    entries = [
        e for e in garden.entries.values() if e.lifecycle != GardenLifecycle.COMPOST
    ]

    if not entries:
        _emit("No active entries to surface.", {}, ctx)
        return 0

    # Pick a random entry for serendipity
    surprise = random.choice(entries)

    lifecycle_icons = {
        "seed": "🌱",
        "sapling": "🌿",
        "tree": "🌳",
        "flower": "🌸",
        "compost": "🍂",
    }
    icon = lifecycle_icons.get(surprise.lifecycle.value, "✨")

    # Find potentially related entries (simple word overlap)
    surprise_words = set(surprise.content.lower().split())
    related = []
    for e in entries:
        if e.id == surprise.id:
            continue
        e_words = set(e.content.lower().split())
        overlap = len(surprise_words & e_words)
        if overlap >= 2:
            related.append((e, overlap))
    related.sort(key=lambda x: -x[1])

    if RICH_AVAILABLE:
        console.print("\n[bold magenta]✨ From the Void[/]")
        console.print()
        console.print(f"  {icon} [cyan]{surprise.content}[/]")
        console.print(
            f"     [dim]{surprise.lifecycle.value} | {surprise.confidence:.0%} confidence[/]"
        )

        if related:
            console.print("\n  [dim]Perhaps connected to:[/]")
            for r, overlap in related[:2]:
                r_icon = lifecycle_icons.get(r.lifecycle.value, "·")
                console.print(f"    {r_icon} {r.content[:40]}...")

        # Poetic closing
        void_whispers = [
            "What patterns emerge when you hold these together?",
            "The garden dreams of connections not yet seen.",
            "Cross-pollination awaits the curious mind.",
            "Seeds planted apart may grow toward each other.",
            "The void offers; you decide the meaning.",
        ]
        console.print(f"\n  [italic dim]{random.choice(void_whispers)}[/]")
    else:
        _emit(f"✨ Surprise: {surprise.content}", {}, ctx)
        if related:
            _emit(f"  Related: {related[0][0].content[:40]}...", {}, ctx)

    return 0


# =============================================================================
# Chat Mode: Interactive Tending (Phase 3)
# =============================================================================


# Tending gesture patterns for natural language parsing
GESTURE_PATTERNS = {
    "observe": ["observe", "look", "check", "show", "view", "see", "scan", "inspect"],
    "prune": ["prune", "remove", "delete", "cut", "trim", "clear", "clean"],
    "graft": ["graft", "merge", "combine", "join", "connect", "link", "integrate"],
    "water": ["water", "nurture", "nourish", "support", "help", "feed", "grow"],
    "rotate": ["rotate", "shift", "move", "reorder", "change", "swap", "switch"],
    "wait": ["wait", "pause", "hold", "delay", "rest", "sleep", "idle"],
}


def _parse_gesture(text: str) -> tuple[str, str]:
    """
    Parse natural language into tending gesture and target.

    Returns:
        Tuple of (gesture_verb, target) or ("observe", "garden") as default
    """
    text_lower = text.lower().strip()

    for gesture, keywords in GESTURE_PATTERNS.items():
        for keyword in keywords:
            if keyword in text_lower:
                # Extract target (everything after the keyword)
                parts = text_lower.split(keyword, 1)
                target = parts[1].strip() if len(parts) > 1 else "garden"
                # Clean up target
                target = target.strip(" .,!?")
                if not target:
                    target = "garden"
                return gesture.upper(), target

    # Default: treat as observe intent
    return "OBSERVE", text_lower or "garden"


async def _chat_mode(args: list[str], ctx: "InvocationContext | None") -> int:
    """
    Interactive tending chat mode using ChatFlow.

    Maps natural language to tending gestures (OBSERVE, PRUNE, GRAFT, WATER, ROTATE, WAIT).

    AGENTESE: self.jewel.gardener.flow.chat.*

    Args:
        args: Additional arguments (single intent or empty for interactive)
        ctx: Invocation context

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    display_path_header(
        path="self.jewel.gardener.flow.chat.tend",
        aspect="define",
        effects=["FLOW_STARTED", "TURN_COMPLETED", "GESTURE_APPLIED"],
    )

    gctx = await _get_context()

    # Get current session state for context
    session_info = ""
    if gctx.active_session:
        state = gctx.active_session.state
        session_info = f"  Session: {state.name} | Phase: {state.phase}"

    # If args provided, do single gesture (non-interactive)
    if args:
        intent = " ".join(args).strip()
        if not intent:
            _emit("Error: intent cannot be empty", {"error": "empty_intent"}, ctx)
            return 1

        gesture, target = _parse_gesture(intent)
        _print_gesture_response(gesture, target, session_info)
        return 0

    # Interactive chat mode
    print()
    if RICH_AVAILABLE:
        console.print(
            Panel(
                "[bold green]Gardener Chat[/] - Conversational Tending\n\n"
                f"{session_info}\n\n"
                "[dim]Speak naturally to tend your garden. I'll interpret your intent.[/]\n"
                "[dim]Type 'quit' to exit, 'status' to see session state.[/]",
                border_style="green",
            )
        )
    else:
        print("🌱 Gardener Chat - Conversational Tending")
        print("━" * 50)
        if session_info:
            print(session_info)
        print("  Speak naturally to tend your garden.")
        print("  Type 'quit' to exit, 'status' for session state.")
        print("━" * 50)
    print()

    # Track conversation
    turn_number = 0

    while True:
        try:
            # Prompt with turn indicator
            prompt = f"[{turn_number}] 🌱 : " if turn_number > 0 else "🌱 : "
            user_input = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Garden gently closes...")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("\n👋 Garden gently closes...")
            break

        if user_input.lower() == "status":
            await _show_status(ctx)
            continue

        if user_input.lower() in ("manifest", "poly", "polynomial"):
            await _show_manifest(ctx)
            continue

        if user_input.lower() == "advance":
            await _advance_session(ctx)
            continue

        # Parse intent to gesture
        gesture, target = _parse_gesture(user_input)

        # Print response
        _print_gesture_response(gesture, target, session_info)

        turn_number += 1
        print()

    return 0


def _print_gesture_response(gesture: str, target: str, session_info: str) -> None:
    """Print a tending response based on parsed gesture."""
    gesture_emojis = {
        "OBSERVE": "👁️",
        "PRUNE": "✂️",
        "GRAFT": "🔗",
        "WATER": "💧",
        "ROTATE": "🔄",
        "WAIT": "⏸️",
    }

    gesture_actions = {
        "OBSERVE": "Observing",
        "PRUNE": "Pruning",
        "GRAFT": "Grafting",
        "WATER": "Watering",
        "ROTATE": "Rotating",
        "WAIT": "Waiting for",
    }

    emoji = gesture_emojis.get(gesture, "🌿")
    action = gesture_actions.get(gesture, "Tending")

    if RICH_AVAILABLE:
        console.print(f"\n  {emoji} [bold]{action}[/]: [cyan]{target}[/]")
        console.print(f"  [dim]Gesture: {gesture} | Target: {target}[/]")
        # Add contextual suggestions
        if gesture == "OBSERVE":
            console.print(
                "  [dim]💡 Try: 'prune stale plans' or 'water blocked tasks'[/]"
            )
        elif gesture == "WATER":
            console.print(
                "  [dim]💡 Progress nurtured. Run 'kg gardener manifest' to see state.[/]"
            )
    else:
        print(f"\n  {emoji} {action}: {target}")
        print(f"     Gesture: {gesture} | Target: {target}")


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

        case "chat":
            return _run_async(_chat_mode(args_list[1:], ctx))

        # Garden commands (idea lifecycle)
        case "garden":
            return _run_async(_show_garden_status(ctx))

        case "plant":
            return _run_async(_plant_idea(args_list[1:], ctx))

        case "harvest":
            return _run_async(_harvest_ideas(ctx))

        case "harvest-to-brain" | "reap":
            return _run_async(_harvest_to_brain(ctx))

        case "water" | "nurture":
            return _run_async(_water_idea(args_list[1:], ctx))

        case "surprise" | "serendipity" | "void":
            return _run_async(_surprise(ctx))

        case "help":
            _print_help()
            return 0

        case _:
            _emit(f"Unknown command: {subcommand}", {"error": subcommand}, ctx)
            _emit("Use 'kg gardener --help' for available commands.", {}, ctx)
            return 1
