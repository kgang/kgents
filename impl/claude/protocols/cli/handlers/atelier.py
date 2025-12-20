"""
Atelier CLI Handler: Interface to Tiny Atelier.

Commands:
    kg atelier artisans           - Meet the artisans
    kg atelier commission <name> <request> - Commission a piece
    kg atelier gallery            - View your gallery
    kg atelier view <id>          - View a piece with provenance
    kg atelier collaborate        - Multi-artisan collaboration
    kg atelier queue              - Queue for background processing
    kg atelier pending            - View pending commissions
    kg atelier process            - Process queued commissions
    kg atelier seed               - Seed gallery with sample commissions

Theme: Orisinal.com aesthetic—whimsical, minimal, melancholic but hopeful.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any

import click
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

console = Console()


# =============================================================================
# Friendly Error Messages
# =============================================================================

EMPTY_GALLERY_MESSAGE = """
[dim]Your gallery is empty—but that's the beginning of every beautiful collection.[/dim]

[dim]Try commissioning your first piece:[/dim]
  [bold]kg atelier commission calligrapher "a haiku about beginnings"[/bold]

[dim]Or see all available artisans:[/dim]
  [bold]kg atelier artisans[/bold]
"""

ARTISAN_NOT_FOUND_MESSAGE = """
[red]Unknown artisan: {name}[/red]

[dim]Available artisans:[/dim]
{artisans}

[dim]Example:[/dim]
  [bold]kg atelier commission calligrapher "a haiku about persistence"[/bold]
"""

PIECE_NOT_FOUND_MESSAGE = """
[red]Piece '{piece_id}' not found[/red]

[dim]The gallery holds what remains. Perhaps it was:[/dim]
  • Never created
  • Deleted from the gallery
  • A misremembered ID

[dim]View your gallery:[/dim]
  [bold]kg atelier gallery[/bold]
"""

NO_PENDING_MESSAGE = """
[dim]No pending commissions—the queue rests quietly.[/dim]

[dim]Queue something for later:[/dim]
  [bold]kg atelier queue calligrapher "something for tomorrow"[/bold]
"""

STREAMING_ERROR_MESSAGE = """
[red]✗ {error}[/red]

[dim]The artisan encountered an issue. Suggestions:[/dim]
  • Check your network connection
  • Try again in a moment
  • Queue the commission for later: [bold]kg atelier queue ...[/bold]
"""

CONNECTION_ERROR_MESSAGE = """
[red]✗ Connection error[/red]

[dim]Could not reach the artisans. Check:[/dim]
  • Is the API server running?
  • Network connectivity

[dim]For local dev, start the backend:[/dim]
  [bold]uv run uvicorn protocols.api.app:create_app --factory --reload[/bold]
"""


# =============================================================================
# Helper Functions
# =============================================================================


def run_async(coro: Any) -> Any:
    """Run an async coroutine in a new event loop."""
    return asyncio.run(coro)


def display_piece(piece: Any) -> None:
    """Display a piece summary with nice formatting."""
    from agents.atelier.artisan import Piece

    if isinstance(piece, dict):
        piece = Piece.from_dict(piece)

    content = str(piece.content)
    # Wrap long lines for terminal
    if len(content) > 500:
        content = content[:500] + "\n..."

    console.print(
        Panel(
            content,
            title=f"[bold]{piece.artisan}[/bold]",
            subtitle=f"[dim]{piece.form} • {piece.provenance.interpretation[:50]}...[/dim]"
            if len(piece.provenance.interpretation) > 50
            else f"[dim]{piece.form} • {piece.provenance.interpretation}[/dim]",
            width=min(console.width, 80),
            border_style="dim",
        )
    )


def display_piece_full(piece: Any) -> None:
    """Display a piece with full provenance."""
    from agents.atelier.artisan import Piece

    if isinstance(piece, dict):
        piece = Piece.from_dict(piece)

    console.print(f"\n[bold]✧ {piece.id} ✧[/bold]\n")
    console.print(
        Panel(
            str(piece.content),
            title=f"[bold]{piece.artisan}[/bold]",
            subtitle=f"[dim]{piece.form}[/dim]",
            width=min(console.width, 80),
            border_style="dim",
        )
    )

    console.print("\n[bold]Provenance[/bold]")
    console.print(f"  [dim]Interpretation:[/dim] {piece.provenance.interpretation}")

    if piece.provenance.considerations:
        console.print("  [dim]Considered:[/dim]")
        for c in piece.provenance.considerations:
            console.print(f"    • {c}")

    if piece.provenance.choices:
        console.print("  [dim]Choices:[/dim]")
        for ch in piece.provenance.choices:
            console.print(f"    • {ch.decision}")
            if ch.reason:
                console.print(f"      [dim]{ch.reason}[/dim]")

    if piece.provenance.inspirations:
        console.print(f"  [dim]Inspired by:[/dim] {', '.join(piece.provenance.inspirations)}")

    console.print(f"\n  [dim]Created:[/dim] {piece.created_at.strftime('%Y-%m-%d %H:%M')}")
    console.print()


# =============================================================================
# CLI Commands
# =============================================================================


@click.group()
def atelier() -> None:
    """✧ tiny atelier ✧ — A gentle workshop for making beautiful things"""
    pass


@atelier.command()
def artisans() -> None:
    """Meet the artisans in your workshop"""
    from agents.atelier.artisans import ARTISAN_REGISTRY

    console.print("\n[bold]✧ the artisans ✧[/bold]\n")

    for name, cls in ARTISAN_REGISTRY.items():
        artisan = cls()
        console.print(
            Panel(
                f"[italic]{artisan.specialty}[/italic]",
                title=f"[bold]{artisan.name}[/bold]",
                subtitle=f'[dim]kg atelier commission {name} "..."[/dim]',
                width=min(console.width, 70),
                border_style="dim",
            )
        )
        console.print()


@atelier.command()
@click.argument("artisan_name")
@click.argument("request")
@click.option("--patron", "-p", default="wanderer", help="Your name for provenance")
@click.option("--quiet", "-q", is_flag=True, help="Suppress streaming output")
def commission(artisan_name: str, request: str, patron: str, quiet: bool) -> None:
    """Commission an artisan to create something

    Examples:
        kg atelier commission calligrapher "a haiku about persistence"
        kg atelier commission cartographer "a map of my morning routine"
        kg atelier commission archivist "synthesize my recent thoughts"
    """
    from agents.atelier.artisan import AtelierEventType, Piece
    from agents.atelier.workshop import get_workshop

    workshop = get_workshop()

    async def do_commission() -> None:
        piece: Piece | None = None

        if quiet:
            # Silent mode - just get the piece
            piece = await workshop.commission(artisan_name, request, patron)
            if piece:
                display_piece(piece)
            return

        # Streaming mode with live updates
        spinner = Spinner("dots", text="contemplating...")

        with Live(spinner, console=console, refresh_per_second=10) as live:
            async for event in workshop.flux.commission(artisan_name, request, patron):
                if event.event_type == AtelierEventType.COMMISSION_RECEIVED:
                    live.update(Spinner("dots", text="received commission..."))
                elif event.event_type == AtelierEventType.CONTEMPLATING:
                    live.update(Spinner("dots", text="contemplating..."))
                elif event.event_type == AtelierEventType.WORKING:
                    live.update(Spinner("dots2", text="crafting..."))
                elif event.event_type == AtelierEventType.FRAGMENT:
                    # Show progress
                    length = event.data.get("accumulated_length", 0)
                    live.update(Spinner("dots2", text=f"crafting... ({length} chars)"))
                elif event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                    live.update(Text("✓ complete", style="green"))
                elif event.event_type == AtelierEventType.ERROR:
                    live.update(Text(f"✗ {event.message}", style="red"))
                    return

        if piece:
            console.print()
            display_piece(piece)
            console.print(f"\n[dim]Piece ID: {piece.id}[/dim]")

    run_async(do_commission())


@atelier.command()
@click.option("--artisan", "-a", help="Filter by artisan name")
@click.option("--form", "-f", help="Filter by form (haiku, letter, map, etc.)")
@click.option("--limit", "-n", default=10, help="Number of pieces to show")
def gallery(artisan: str | None, form: str | None, limit: int) -> None:
    """View your gallery of pieces"""
    from agents.atelier.gallery.store import get_gallery

    store = get_gallery()

    async def show_gallery() -> None:
        pieces = await store.list_pieces(artisan=artisan, form=form, limit=limit)

        if not pieces:
            console.print(EMPTY_GALLERY_MESSAGE)
            return

        table = Table(title="✧ your gallery ✧", border_style="dim")
        table.add_column("ID", style="dim", width=8)
        table.add_column("Artisan", width=18)
        table.add_column("Form", width=12)
        table.add_column("Preview", width=35)
        table.add_column("Date", width=10)

        for piece in pieces:
            preview = str(piece.content)[:35]
            if len(str(piece.content)) > 35:
                preview += "..."
            preview = preview.replace("\n", " ")

            table.add_row(
                piece.id,
                piece.artisan,
                piece.form,
                preview,
                piece.created_at.strftime("%b %d"),
            )

        console.print()
        console.print(table)
        console.print()

    run_async(show_gallery())


@atelier.command()
@click.argument("piece_id")
def view(piece_id: str) -> None:
    """View a piece in full with its provenance"""
    from agents.atelier.gallery.store import get_gallery

    store = get_gallery()

    async def show_piece() -> None:
        piece = await store.get(piece_id)
        if not piece:
            console.print(PIECE_NOT_FOUND_MESSAGE.format(piece_id=piece_id))
            return
        display_piece_full(piece)

    run_async(show_piece())


@atelier.command()
@click.argument("piece_id")
def lineage(piece_id: str) -> None:
    """View the creative lineage of a piece"""
    from agents.atelier.gallery.lineage import LineageGraph
    from agents.atelier.gallery.store import get_gallery

    store = get_gallery()

    async def show_lineage() -> None:
        piece = await store.get(piece_id)
        if not piece:
            console.print(PIECE_NOT_FOUND_MESSAGE.format(piece_id=piece_id))
            return

        # Build lineage graph from all pieces
        all_pieces = await store.list_pieces(limit=100)
        graph = LineageGraph.from_pieces(all_pieces)

        ancestors = graph.get_ancestors(piece_id)
        descendants = graph.get_descendants(piece_id)

        console.print(f"\n[bold]✧ Lineage of {piece_id} ✧[/bold]\n")

        if ancestors:
            console.print("[dim]Inspired by:[/dim]")
            for node in ancestors:
                console.print(f"  ← [{node.artisan}] {node.preview}")
        else:
            console.print("[dim]This is a root creation (no inspirations)[/dim]")

        console.print()

        if descendants:
            console.print("[dim]Inspired these:[/dim]")
            for node in descendants:
                console.print(f"  → [{node.artisan}] {node.preview}")
        else:
            console.print("[dim]No pieces yet inspired by this one[/dim]")

        console.print()

    run_async(show_lineage())


@atelier.command()
@click.argument("artisan_names", nargs=-1, required=True)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["duet", "ensemble", "refinement", "chain", "exquisite"]),
    default="duet",
    help="Collaboration mode",
)
@click.option("--request", "-r", required=True, help="What to create together")
@click.option("--patron", "-p", default="wanderer", help="Your name for provenance")
@click.option(
    "--visibility",
    "-v",
    default=0.1,
    type=float,
    help="Visibility ratio for exquisite mode (0.0-1.0, default 0.1 = 10%%)",
)
def collaborate(
    artisan_names: tuple[str], mode: str, request: str, patron: str, visibility: float
) -> None:
    """Commission a collaboration between artisans

    Examples:
        kg atelier collaborate calligrapher cartographer -r "a map of longing"
        kg atelier collaborate --mode=ensemble calligrapher archivist -r "memories of summer"
        kg atelier collaborate --mode=refinement calligrapher calligrapher -r "a perfect haiku"
        kg atelier collaborate --mode=exquisite calligrapher cartographer archivist -r "journey"
    """
    from agents.atelier.artisan import AtelierEventType, Piece
    from agents.atelier.workshop import get_workshop

    if len(artisan_names) < 1:
        console.print("[red]At least one artisan required[/red]")
        return

    workshop = get_workshop()

    # Build context for exquisite mode
    context = {}
    if mode == "exquisite":
        context["visibility_ratio"] = visibility

    async def do_collaborate() -> None:
        piece: Piece | None = None
        spinner = Spinner("dots", text=f"beginning {mode}...")

        with Live(spinner, console=console, refresh_per_second=10) as live:
            async for event in workshop.flux.collaborate(
                list(artisan_names), request, mode, patron, context=context
            ):
                if event.event_type == AtelierEventType.CONTEMPLATING:
                    live.update(Spinner("dots", text=event.message or "contemplating..."))
                elif event.event_type == AtelierEventType.WORKING:
                    live.update(Spinner("dots2", text=event.message or "working..."))
                elif event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                    live.update(Text("✓ complete", style="green"))
                elif event.event_type == AtelierEventType.ERROR:
                    live.update(Text(f"✗ {event.message}", style="red"))
                    return

        if piece:
            console.print()
            display_piece_full(piece)

    run_async(do_collaborate())


@atelier.command()
@click.argument("topic")
@click.option(
    "--artisans",
    "-a",
    multiple=True,
    default=["calligrapher", "cartographer"],
    help="Artisans to participate (default: calligrapher, cartographer)",
)
@click.option(
    "--visibility",
    "-v",
    default=0.1,
    type=float,
    help="How much of previous work each artisan sees (0.0-1.0, default 0.1 = 10%%)",
)
@click.option("--patron", "-p", default="wanderer", help="Your name for provenance")
def exquisite(topic: str, artisans: tuple[str], visibility: float, patron: str) -> None:
    """Create an exquisite corpse collaboration

    The surrealist game where each creator only sees a fragment of
    what came before, leading to surprising continuations.

    Examples:
        kg atelier exquisite "a journey through memory"
        kg atelier exquisite "the future of cities" -a architect -a poet -a cartographer
        kg atelier exquisite "metamorphosis" --visibility 0.2
    """
    from agents.atelier.artisan import AtelierEventType, Piece
    from agents.atelier.workshop import get_workshop

    if len(artisans) < 2:
        console.print("[yellow]Exquisite corpse works best with 2+ artisans[/yellow]")
        console.print("[dim]Using default: calligrapher, cartographer[/dim]")
        artisans = ("calligrapher", "cartographer")

    workshop = get_workshop()
    context = {"visibility_ratio": visibility}

    async def do_exquisite() -> None:
        piece: Piece | None = None

        console.print(
            f"\n[bold]✧ Exquisite Corpse ✧[/bold]\n"
            f"[dim]Topic: {topic}[/dim]\n"
            f"[dim]Artisans: {', '.join(artisans)}[/dim]\n"
            f"[dim]Visibility: {int(visibility * 100)}%[/dim]\n"
        )

        spinner = Spinner("dots", text="The corpse stirs...")

        with Live(spinner, console=console, refresh_per_second=10) as live:
            async for event in workshop.flux.collaborate(
                list(artisans), topic, "exquisite", patron, context=context
            ):
                if event.event_type == AtelierEventType.CONTEMPLATING:
                    live.update(Spinner("dots", text=event.message or "contemplating..."))
                elif event.event_type == AtelierEventType.WORKING:
                    live.update(Spinner("dots2", text=event.message or "crafting..."))
                elif event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                    live.update(Text("✧ The corpse is revealed! ✧", style="bold green"))
                elif event.event_type == AtelierEventType.ERROR:
                    live.update(Text(f"✗ {event.message}", style="red"))
                    return

        if piece:
            console.print()
            display_piece_full(piece)

    run_async(do_exquisite())


@atelier.command()
@click.argument("start_text")
@click.argument("artisan_name")
@click.option("--patron", "-p", default="wanderer", help="Your name for provenance")
def handoff(start_text: str, artisan_name: str, patron: str) -> None:
    """Start something and hand it off to an artisan to continue

    You provide the beginning, the artisan takes it from there.
    This is the creative handoff—start the spark, let them fan the flame.

    Examples:
        kg atelier handoff "The old lighthouse keeper had seen many storms, but this one..." calligrapher
        kg atelier handoff "In the center of the map, where no cartographer dared venture..." cartographer
    """
    from agents.atelier.artisan import AtelierEventType, Piece
    from agents.atelier.artisans import ARTISAN_REGISTRY, get_artisan
    from agents.atelier.workshop import get_workshop

    # Validate artisan
    if not get_artisan(artisan_name):
        artisan_list = "\n".join(f"  • {name}" for name in ARTISAN_REGISTRY.keys())
        console.print(ARTISAN_NOT_FOUND_MESSAGE.format(name=artisan_name, artisans=artisan_list))
        return

    workshop = get_workshop()

    # The handoff request includes the start text as context
    handoff_request = f"Continue and complete this creative fragment in your own style:\n\n---\n{start_text}\n---\n\nBuild upon this beginning, honoring its spirit while adding your unique voice."

    async def do_handoff() -> None:
        piece: Piece | None = None

        console.print(
            f"\n[bold]✧ Creative Handoff ✧[/bold]\n"
            f"[dim]Your beginning:[/dim]\n"
            f"  [italic]{start_text[:80]}{'...' if len(start_text) > 80 else ''}[/italic]\n"
            f"\n[dim]Passing to: {artisan_name}[/dim]\n"
        )

        spinner = Spinner("dots", text=f"{artisan_name} receives the spark...")

        with Live(spinner, console=console, refresh_per_second=10) as live:
            async for event in workshop.flux.commission(artisan_name, handoff_request, patron):
                if event.event_type == AtelierEventType.CONTEMPLATING:
                    live.update(Spinner("dots", text=f"{artisan_name} contemplates..."))
                elif event.event_type == AtelierEventType.WORKING:
                    live.update(Spinner("dots2", text=f"{artisan_name} continues your work..."))
                elif event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                    live.update(Text("✓ Handoff complete", style="green"))
                elif event.event_type == AtelierEventType.ERROR:
                    live.update(Text(f"✗ {event.message}", style="red"))
                    return

        if piece:
            console.print()
            display_piece(piece)
            console.print(f"\n[dim]Piece ID: {piece.id}[/dim]")

    run_async(do_handoff())


@atelier.command()
@click.option("--random", "-r", "use_random", is_flag=True, help="Inject a random constraint")
@click.option("--constraint", "-c", help="Specific constraint to apply")
def constrain(use_random: bool, constraint: str | None) -> None:
    """Inject a creative constraint into your next commission

    Constraints spark creativity by limiting choices.
    Use random for surprise, or specify your own.

    Examples:
        kg atelier constrain --random
        kg atelier constrain -c "must include the color blue"
        kg atelier constrain -c "cannot use the word 'the'"
    """
    import random as rand

    # Built-in creative constraints
    RANDOM_CONSTRAINTS = [
        "Must include exactly three colors",
        "Cannot use any words longer than five letters",
        "Must reference water in some form",
        "Should feel like early morning",
        "Must include a specific number (your choice)",
        "Should have a sense of departure or leaving",
        "Must mention something fragile",
        "Should evoke a particular smell",
        "Must include a question that goes unanswered",
        "Should reference something very old and something very new",
        "Must have a recurring element that appears three times",
        "Should feel like the moment just before something changes",
    ]

    if use_random:
        chosen = rand.choice(RANDOM_CONSTRAINTS)
        console.print("\n[bold]✧ Random Constraint ✧[/bold]\n")
        console.print(f"  [italic]{chosen}[/italic]\n")
        console.print(
            "[dim]Use this constraint in your next commission:[/dim]\n"
            f'  [bold]kg atelier commission calligrapher "{chosen}"[/bold]\n'
        )
    elif constraint:
        console.print("\n[bold]✧ Your Constraint ✧[/bold]\n")
        console.print(f"  [italic]{constraint}[/italic]\n")
        console.print(
            "[dim]Use this constraint in your next commission:[/dim]\n"
            f'  [bold]kg atelier commission calligrapher "{constraint}"[/bold]\n'
        )
    else:
        console.print(
            "[yellow]Specify a constraint with -c or use --random[/yellow]\n"
            "\nExamples:\n"
            "  kg atelier constrain --random\n"
            '  kg atelier constrain -c "must include blue"\n'
        )


@atelier.command()
@click.argument("query")
@click.argument("artisan_name")
@click.option("--limit", "-n", default=3, help="Number of memories to pull (default: 3)")
@click.option("--patron", "-p", default="wanderer", help="Your name for provenance")
def inspire(query: str, artisan_name: str, limit: int, patron: str) -> None:
    """Pull memories from Brain as inspiration for creation

    Search Brain for relevant memories, then pass them to an artisan
    to create something inspired by those memories.

    This is the Brain → Atelier synergy: your captured insights
    become seeds for new creations.

    Examples:
        kg atelier inspire "category theory" calligrapher
        kg atelier inspire "moments of joy" cartographer -n 5
        kg atelier inspire "creative insights" archivist
    """
    from agents.atelier.artisan import AtelierEventType, Piece
    from agents.atelier.artisans import ARTISAN_REGISTRY, get_artisan
    from agents.atelier.workshop import get_workshop
    from agents.brain import get_brain_crystal

    # Validate artisan
    if not get_artisan(artisan_name):
        artisan_list = "\n".join(f"  • {name}" for name in ARTISAN_REGISTRY.keys())
        console.print(ARTISAN_NOT_FOUND_MESSAGE.format(name=artisan_name, artisans=artisan_list))
        return

    async def do_inspire() -> None:
        # Search Brain for relevant memories
        brain = await get_brain_crystal()
        memories = await brain.search(query, limit=limit)

        if not memories:
            console.print(
                f"\n[yellow]No memories found for '{query}'[/yellow]\n"
                "[dim]Capture some thoughts with:[/dim]\n"
                f'  [bold]kg brain capture "{query} - your insight here"[/bold]\n'
            )
            return

        console.print("\n[bold]✧ Drawing Inspiration from Memory ✧[/bold]\n")
        console.print(f"[dim]Found {len(memories)} relevant memories:[/dim]\n")

        # Show the memories being used
        for i, mem in enumerate(memories, 1):
            preview = mem.content[:60].replace("\n", " ")
            console.print(
                f"  {i}. [italic]{preview}{'...' if len(mem.content) > 60 else ''}[/italic]"
            )

        console.print()

        # Build the inspiration prompt
        memory_context = "\n\n".join(
            f"Memory {i + 1}: {mem.content}" for i, mem in enumerate(memories)
        )

        inspiration_request = f"""Create something inspired by these memories:

{memory_context}

---

Let these memories guide your creation. You need not reference them directly—
let them inform the mood, themes, or ideas of what you create."""

        # Commission the artisan
        workshop = get_workshop()
        piece: Piece | None = None
        spinner = Spinner("dots", text=f"{artisan_name} contemplates the memories...")

        with Live(spinner, console=console, refresh_per_second=10) as live:
            async for event in workshop.flux.commission(artisan_name, inspiration_request, patron):
                if event.event_type == AtelierEventType.CONTEMPLATING:
                    live.update(Spinner("dots", text=f"{artisan_name} draws from memory..."))
                elif event.event_type == AtelierEventType.WORKING:
                    live.update(Spinner("dots2", text=f"{artisan_name} transforms memories..."))
                elif event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                    live.update(Text("✓ Memory transformed into art", style="green"))
                elif event.event_type == AtelierEventType.ERROR:
                    live.update(Text(f"✗ {event.message}", style="red"))
                    return

        if piece:
            console.print()
            display_piece(piece)
            console.print(f"\n[dim]Piece ID: {piece.id}[/dim]")
            console.print(f"[dim]Inspired by {len(memories)} memories about '{query}'[/dim]")

    run_async(do_inspire())


@atelier.command("queue")
@click.argument("artisan_name")
@click.argument("request")
@click.option("--patron", "-p", default="wanderer", help="Your name for provenance")
def queue_commission(artisan_name: str, request: str, patron: str) -> None:
    """Queue a commission for later processing

    Example:
        kg atelier queue calligrapher "something for tomorrow"
    """
    from agents.atelier.artisans import ARTISAN_REGISTRY, get_artisan
    from agents.atelier.workshop import get_workshop

    # Validate artisan
    if not get_artisan(artisan_name):
        artisan_list = "\n".join(f"  • {name}" for name in ARTISAN_REGISTRY.keys())
        console.print(ARTISAN_NOT_FOUND_MESSAGE.format(name=artisan_name, artisans=artisan_list))
        return

    workshop = get_workshop()

    async def do_queue() -> None:
        commission = await workshop.queue_commission(artisan_name, request, patron)
        console.print(f"[green]✓[/green] Queued commission [bold]{commission.id}[/bold]")
        console.print(
            "  [dim]Process with 'kg atelier process' or wait for background worker[/dim]"
        )

    run_async(do_queue())


@atelier.command()
def pending() -> None:
    """View pending commissions"""
    from agents.atelier.workshop.commission import get_queue

    queue = get_queue()

    async def show_pending() -> None:
        items = await queue.pending()

        if not items:
            console.print(NO_PENDING_MESSAGE)
            return

        table = Table(title="Pending Commissions", border_style="dim")
        table.add_column("ID", style="dim", width=8)
        table.add_column("Artisan", width=15)
        table.add_column("Request", width=35)
        table.add_column("Queued", width=12)

        for item in items:
            preview = item.commission.request[:30]
            if len(item.commission.request) > 30:
                preview += "..."
            queued = item.queued_at.strftime("%b %d %H:%M")
            table.add_row(
                item.commission.id,
                item.artisan_name,
                preview,
                queued,
            )

        console.print()
        console.print(table)
        console.print()

    run_async(show_pending())


@atelier.command("process")
@click.option("--all", "process_all", is_flag=True, help="Process all pending")
def process_queue(process_all: bool) -> None:
    """Process queued commissions"""
    from agents.atelier.artisan import AtelierEventType, Piece
    from agents.atelier.workshop.commission import get_queue

    queue = get_queue()

    async def do_process() -> None:
        count = 0

        if process_all:
            async for event in queue.process_all():
                if event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                    console.print(f"[green]✓[/green] Created piece [bold]{piece.id}[/bold]")
                    count += 1
                elif event.event_type == AtelierEventType.ERROR:
                    console.print(f"[red]✗[/red] {event.message}")

            console.print(f"\n[dim]Processed {count} commissions[/dim]")
        else:
            async for event in queue.process_one():
                if event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                    console.print(f"[green]✓[/green] Created piece [bold]{piece.id}[/bold]")
                    display_piece(piece)
                elif event.event_type == AtelierEventType.ERROR:
                    console.print(f"[red]✗[/red] {event.message}")
                    return

            # Check if there was nothing to process
            pending = await queue.pending()
            if not pending and count == 0:
                console.print(NO_PENDING_MESSAGE)

    run_async(do_process())


@atelier.command()
@click.argument("query")
@click.option("--limit", "-n", default=10, help="Number of results")
def search(query: str, limit: int) -> None:
    """Search your gallery

    Example:
        kg atelier search "persistence"
    """
    from agents.atelier.gallery.store import get_gallery

    store = get_gallery()

    async def do_search() -> None:
        results = await store.search_content(query, limit=limit)

        if not results:
            console.print(
                f"\n[dim]No pieces found matching '{query}'[/dim]\n"
                "\n[dim]Perhaps try a different search, or view the full gallery:[/dim]"
                "\n  [bold]kg atelier gallery[/bold]\n"
            )
            return

        console.print(f"\n[bold]Found {len(results)} pieces[/bold]\n")
        for piece in results:
            preview = str(piece.content)[:50].replace("\n", " ")
            console.print(f"  [{piece.id}] {piece.artisan}: {preview}...")

        console.print()

    run_async(do_search())


@atelier.command()
@click.option("--force", "-f", is_flag=True, help="Overwrite existing seed pieces")
@click.option("--clear", "-c", is_flag=True, help="Remove seed pieces instead")
def seed(force: bool, clear: bool) -> None:
    """Seed the gallery with sample pieces

    This adds 3 example pieces to demonstrate artisan capabilities:
    - A haiku from the Calligrapher
    - A map from the Cartographer
    - A letter from the Correspondent

    Examples:
        kg atelier seed          # Add sample pieces
        kg atelier seed --force  # Overwrite existing seeds
        kg atelier seed --clear  # Remove seed pieces
    """
    from agents.atelier.gallery.seeds import clear_seeds, seed_gallery
    from agents.atelier.gallery.store import get_gallery

    gallery = get_gallery()

    async def do_seed() -> None:
        if clear:
            removed = await clear_seeds(gallery)
            if removed:
                console.print(
                    f"[green]✓[/green] Removed {len(removed)} seed pieces: {', '.join(removed)}"
                )
            else:
                console.print("[dim]No seed pieces to remove[/dim]")
            return

        added = await seed_gallery(gallery, force=force)
        if added:
            console.print(f"[green]✓[/green] Added {len(added)} sample pieces to your gallery")
            console.print("\n[dim]View them with:[/dim]")
            console.print("  [bold]kg atelier gallery[/bold]")
            for piece_id in added:
                console.print(f"  [bold]kg atelier view {piece_id}[/bold]")
        else:
            console.print(
                "[dim]Gallery already contains seed pieces. Use --force to overwrite.[/dim]"
            )

    run_async(do_seed())


@atelier.command()
def status() -> None:
    """Show workshop status and statistics"""
    from agents.atelier.artisans import ARTISAN_REGISTRY
    from agents.atelier.festival import get_festival_manager
    from agents.atelier.gallery.store import get_gallery
    from agents.atelier.workshop.commission import get_queue

    gallery = get_gallery()
    queue = get_queue()
    festivals = get_festival_manager()

    async def show_status() -> None:
        total_pieces = await gallery.count()
        pending_items = await queue.pending()
        active_festivals = festivals.active()

        console.print("\n[bold]✧ workshop status ✧[/bold]\n")

        table = Table(show_header=False, border_style="dim", box=None)
        table.add_column("Label", style="dim")
        table.add_column("Value")

        table.add_row("Gallery pieces", str(total_pieces))
        table.add_row("Pending queue", str(len(pending_items)))
        table.add_row("Available artisans", str(len(ARTISAN_REGISTRY)))
        table.add_row("Active festivals", str(len(active_festivals)))

        console.print(table)

        if len(ARTISAN_REGISTRY) > 0:
            console.print("\n[dim]Artisans:[/dim]")
            for name in ARTISAN_REGISTRY.keys():
                console.print(f"  • {name}")

        if active_festivals:
            console.print("\n[dim]Active Festivals:[/dim]")
            for fest in active_festivals:
                console.print(f"  • {fest.title}: {fest.theme}")

        console.print()

    run_async(show_status())


# =============================================================================
# Festival Commands
# =============================================================================


@atelier.group()
def festival() -> None:
    """✧ festivals ✧ — Seasonal creative challenges"""
    pass


@festival.command("create")
@click.argument("title")
@click.argument("theme")
@click.option("--duration", "-d", default=72, help="Duration in hours (default: 72)")
@click.option("--constraint", "-c", multiple=True, help="Creative constraints")
def festival_create(title: str, theme: str, duration: int, constraint: tuple[str]) -> None:
    """Create a new festival

    Examples:
        kg atelier festival create "Winter Tales" "longest night"
        kg atelier festival create "Spring Bloom" "renewal" -d 48
        kg atelier festival create "Constraint Jam" "limitation" -c "no adjectives"
    """
    from agents.atelier.festival import get_festival_manager

    manager = get_festival_manager()
    fest = manager.create(
        title=title,
        theme=theme,
        duration_hours=duration,
        constraints=list(constraint) if constraint else None,
    )

    console.print("\n[bold]✧ Festival Created ✧[/bold]\n")
    console.print(f"  [bold]{fest.title}[/bold]")
    console.print(f"  [dim]Theme:[/dim] {fest.theme}")
    console.print(f"  [dim]Season:[/dim] {fest.season.value}")
    console.print(f"  [dim]Duration:[/dim] {duration} hours")
    console.print(f"  [dim]ID:[/dim] {fest.id}")
    if fest.constraints:
        console.print("  [dim]Constraints:[/dim]")
        for c in fest.constraints:
            console.print(f"    • {c}")
    console.print(
        f'\n[dim]Enter with:[/dim] kg atelier festival enter {fest.id} calligrapher "your prompt"\n'
    )


@festival.command("list")
@click.option("--active", "-a", is_flag=True, help="Show only active festivals")
def festival_list(active: bool) -> None:
    """List all festivals"""
    from agents.atelier.festival import FestivalStatus, get_festival_manager

    manager = get_festival_manager()
    status_filter = FestivalStatus.ACTIVE if active else None
    festivals = manager.list_festivals(status=status_filter)

    if not festivals:
        console.print(
            "\n[dim]No festivals yet. Create one with:[/dim]\n"
            '  [bold]kg atelier festival create "Title" "theme"[/bold]\n'
        )
        return

    console.print("\n[bold]✧ Festivals ✧[/bold]\n")

    table = Table(border_style="dim")
    table.add_column("ID", style="dim", width=12)
    table.add_column("Title", width=20)
    table.add_column("Theme", width=25)
    table.add_column("Status", width=10)
    table.add_column("Entries", width=8)

    for fest in festivals:
        status_style = {
            FestivalStatus.ACTIVE: "green",
            FestivalStatus.VOTING: "yellow",
            FestivalStatus.CONCLUDED: "dim",
            FestivalStatus.UPCOMING: "blue",
        }.get(fest.status, "")

        table.add_row(
            fest.id,
            fest.title,
            fest.theme[:25] + "..." if len(fest.theme) > 25 else fest.theme,
            f"[{status_style}]{fest.status.value}[/{status_style}]",
            str(len(fest.entries)),
        )

    console.print(table)
    console.print()


@festival.command("view")
@click.argument("festival_id")
def festival_view(festival_id: str) -> None:
    """View a festival's details and entries"""
    from agents.atelier.festival import get_festival_manager

    manager = get_festival_manager()
    fest = manager.get(festival_id)

    if not fest:
        console.print(f"[red]Festival not found: {festival_id}[/red]")
        return

    console.print(f"\n[bold]✧ {fest.title} ✧[/bold]\n")
    console.print(f"  [dim]Theme:[/dim] {fest.theme}")
    console.print(f"  [dim]Season:[/dim] {fest.season.value}")
    console.print(f"  [dim]Status:[/dim] {fest.status.value}")
    console.print(f"  [dim]Description:[/dim] {fest.description}")

    if fest.constraints:
        console.print("  [dim]Constraints:[/dim]")
        for c in fest.constraints:
            console.print(f"    • {c}")

    if fest.time_remaining:
        hours = fest.time_remaining.total_seconds() / 3600
        console.print(f"  [dim]Time remaining:[/dim] {hours:.1f} hours")

    if fest.entries:
        console.print(f"\n[bold]Entries ({len(fest.entries)}):[/bold]\n")

        table = Table(border_style="dim")
        table.add_column("ID", style="dim", width=12)
        table.add_column("Artisan", width=15)
        table.add_column("Preview", width=35)
        table.add_column("Votes", width=8)

        for entry in fest.get_leaderboard(limit=20):
            preview = entry.content[:35].replace("\n", " ")
            if len(entry.content) > 35:
                preview += "..."
            table.add_row(entry.id, entry.artisan, preview, str(entry.votes))

        console.print(table)

    console.print()


@festival.command("enter")
@click.argument("festival_id")
@click.argument("artisan_name")
@click.argument("prompt")
@click.option("--patron", "-p", default="wanderer", help="Your name for provenance")
def festival_enter(festival_id: str, artisan_name: str, prompt: str, patron: str) -> None:
    """Enter a festival with a creation

    The artisan will create a piece based on your prompt,
    which becomes your festival entry.

    Examples:
        kg atelier festival enter fest-abc123 calligrapher "a haiku about waiting"
        kg atelier festival enter fest-abc123 cartographer "map of longing"
    """
    from agents.atelier.artisan import AtelierEventType, Piece
    from agents.atelier.artisans import ARTISAN_REGISTRY, get_artisan
    from agents.atelier.festival import get_festival_manager
    from agents.atelier.workshop import get_workshop

    # Validate artisan
    if not get_artisan(artisan_name):
        artisan_list = "\n".join(f"  • {name}" for name in ARTISAN_REGISTRY.keys())
        console.print(ARTISAN_NOT_FOUND_MESSAGE.format(name=artisan_name, artisans=artisan_list))
        return

    manager = get_festival_manager()
    fest = manager.get(festival_id)

    if not fest:
        console.print(f"[red]Festival not found: {festival_id}[/red]")
        return

    if not fest.is_accepting_entries:
        console.print(f"[yellow]Festival '{fest.title}' is not accepting entries[/yellow]")
        console.print(f"[dim]Status: {fest.status.value}[/dim]")
        return

    workshop = get_workshop()

    async def do_enter() -> None:
        piece: Piece | None = None

        console.print(
            f"\n[bold]✧ Entering Festival: {fest.title} ✧[/bold]\n"
            f"[dim]Theme: {fest.theme}[/dim]\n"
            f"[dim]Artisan: {artisan_name}[/dim]\n"
        )

        # Add festival theme to prompt
        festival_prompt = f"Festival theme: {fest.theme}\n\nCreate: {prompt}"
        if fest.constraints:
            festival_prompt += f"\n\nConstraints: {', '.join(fest.constraints)}"

        spinner = Spinner("dots", text=f"{artisan_name} contemplates the festival theme...")

        with Live(spinner, console=console, refresh_per_second=10) as live:
            async for event in workshop.flux.commission(artisan_name, festival_prompt, patron):
                if event.event_type == AtelierEventType.CONTEMPLATING:
                    live.update(Spinner("dots", text=f"{artisan_name} contemplates..."))
                elif event.event_type == AtelierEventType.WORKING:
                    live.update(Spinner("dots2", text=f"{artisan_name} creates..."))
                elif event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                    live.update(Text("✓ Entry complete", style="green"))
                elif event.event_type == AtelierEventType.ERROR:
                    live.update(Text(f"✗ {event.message}", style="red"))
                    return

        if piece:
            # Register as festival entry
            entry = manager.enter(
                festival_id,
                artisan_name,
                prompt,
                str(piece.content),
                piece_id=piece.id,
            )

            if entry:
                console.print()
                display_piece(piece)
                console.print("\n[green]✓ Entry submitted![/green]")
                console.print(f"[dim]Entry ID: {entry.id}[/dim]")
                console.print(f"[dim]Piece ID: {piece.id}[/dim]")
            else:
                console.print("[red]Failed to register entry[/red]")

    run_async(do_enter())


@festival.command("vote")
@click.argument("festival_id")
@click.argument("entry_id")
@click.option("--count", "-n", default=1, help="Number of votes (default: 1)")
def festival_vote(festival_id: str, entry_id: str, count: int) -> None:
    """Vote for a festival entry

    Examples:
        kg atelier festival vote fest-abc123 entry-xyz789
        kg atelier festival vote fest-abc123 entry-xyz789 -n 3
    """
    from agents.atelier.festival import get_festival_manager

    manager = get_festival_manager()
    fest = manager.get(festival_id)

    if not fest:
        console.print(f"[red]Festival not found: {festival_id}[/red]")
        return

    success = manager.vote(festival_id, entry_id, count)

    if success:
        entry = fest.get_entry(entry_id)
        if entry:
            console.print(f"[green]✓ Voted for entry by {entry.artisan}[/green]")
            console.print(f"[dim]Total votes: {entry.votes}[/dim]")
    else:
        console.print("[red]Could not record vote[/red]")
        console.print("[dim]Check that the entry exists and festival allows voting[/dim]")


@festival.command("conclude")
@click.argument("festival_id")
def festival_conclude(festival_id: str) -> None:
    """Conclude a festival and show results"""
    from agents.atelier.festival import get_festival_manager

    manager = get_festival_manager()
    summary = manager.conclude(festival_id)

    if not summary:
        console.print(f"[red]Festival not found: {festival_id}[/red]")
        return

    console.print(f"\n[bold]✧ Festival Concluded: {summary['title']} ✧[/bold]\n")
    console.print(f"  [dim]Theme:[/dim] {summary['theme']}")
    console.print(f"  [dim]Total entries:[/dim] {summary['total_entries']}")
    console.print(f"  [dim]Total votes:[/dim] {summary['total_votes']}")
    console.print(
        f"  [dim]Participating artisans:[/dim] {', '.join(summary['participating_artisans'])}"
    )

    if summary["winners"]:
        console.print("\n[bold]🏆 Winners:[/bold]\n")
        for i, winner in enumerate(summary["winners"], 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
            console.print(f"  {medal} {winner['artisan']} ({winner['votes']} votes)")
            preview = winner["content"][:60].replace("\n", " ")
            console.print(f"     [dim]{preview}...[/dim]")

    console.print()


@festival.command("suggest")
def festival_suggest() -> None:
    """Suggest a theme for a new festival based on the current season"""
    from agents.atelier.festival import Season, get_festival_manager

    manager = get_festival_manager()
    season = Season.current()
    theme = manager.suggest_theme(season)

    console.print(f"\n[bold]✧ Theme Suggestion for {season.value.title()} ✧[/bold]\n")
    console.print(f"  [italic]{theme}[/italic]\n")
    console.print(
        f"[dim]Create festival with:[/dim]\n"
        f'  [bold]kg atelier festival create "Festival Name" "{theme}"[/bold]\n'
    )


# =============================================================================
# Spectator Economy Commands
# =============================================================================


@atelier.group()
def tokens() -> None:
    """✧ tokens ✧ — Spectator economy management"""
    pass


@tokens.command("balance")
@click.option("--user", "-u", default="wanderer", help="User ID to check")
def tokens_balance(user: str) -> None:
    """Check your token balance

    Examples:
        kg atelier tokens balance
        kg atelier tokens balance -u alice
    """
    from agents.atelier.economy import create_token_pool

    pool = create_token_pool()
    balance = pool.get_balance(user)

    console.print("\n[bold]✧ Token Balance ✧[/bold]\n")
    console.print(f"  [dim]User:[/dim] {user}")
    console.print(f"  [bold]Balance:[/bold] {balance.whole_tokens} tokens")
    console.print(f"  [dim]Total accrued:[/dim] {balance.total_accrued}")
    console.print(f"  [dim]Total spent:[/dim] {balance.total_spent}")
    if balance.watch_session_start:
        console.print("  [green]Currently watching[/green]")
    console.print()


@tokens.command("costs")
def tokens_costs() -> None:
    """Show bid costs for the spectator economy"""
    from agents.atelier.bidding import BID_COSTS, BidType

    console.print("\n[bold]✧ Bid Costs ✧[/bold]\n")

    table = Table(border_style="dim")
    table.add_column("Bid Type", width=20)
    table.add_column("Cost", width=10)
    table.add_column("Description", width=35)

    descriptions = {
        BidType.INJECT_CONSTRAINT: "Direct creative constraint",
        BidType.REQUEST_DIRECTION: "Suggest a direction",
        BidType.BOOST_BUILDER: "Reinforce current path",
    }

    for bid_type, cost in BID_COSTS.items():
        table.add_row(
            bid_type.name.replace("_", " ").title(),
            f"{cost} tokens",
            descriptions.get(bid_type, ""),
        )

    console.print(table)
    console.print(
        "\n[dim]Accepted bids get 1.5x bonus refund. Ignored bids get full refund.[/dim]\n"
    )


# =============================================================================
# Entry Point (for hollow.py registration)
# =============================================================================


def cmd_atelier(args: list[str]) -> int:
    """Entry point for hollow.py lazy loading."""
    try:
        # Click handles its own argument parsing
        atelier(args, standalone_mode=False)
        return 0
    except click.ClickException as e:
        e.show()
        return 1
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1


__all__ = ["atelier", "cmd_atelier"]
