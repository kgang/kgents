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
        console.print(
            f"  [dim]Inspired by:[/dim] {', '.join(piece.provenance.inspirations)}"
        )

    console.print(
        f"\n  [dim]Created:[/dim] {piece.created_at.strftime('%Y-%m-%d %H:%M')}"
    )
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
    type=click.Choice(["duet", "ensemble", "refinement", "chain"]),
    default="duet",
    help="Collaboration mode",
)
@click.option("--request", "-r", required=True, help="What to create together")
@click.option("--patron", "-p", default="wanderer", help="Your name for provenance")
def collaborate(
    artisan_names: tuple[str], mode: str, request: str, patron: str
) -> None:
    """Commission a collaboration between artisans

    Examples:
        kg atelier collaborate calligrapher cartographer -r "a map of longing"
        kg atelier collaborate --mode=ensemble calligrapher archivist -r "memories of summer"
        kg atelier collaborate --mode=refinement calligrapher calligrapher -r "a perfect haiku"
    """
    from agents.atelier.artisan import AtelierEventType, Piece
    from agents.atelier.workshop import get_workshop

    if len(artisan_names) < 1:
        console.print("[red]At least one artisan required[/red]")
        return

    workshop = get_workshop()

    async def do_collaborate() -> None:
        piece: Piece | None = None
        spinner = Spinner("dots", text=f"beginning {mode}...")

        with Live(spinner, console=console, refresh_per_second=10) as live:
            async for event in workshop.flux.collaborate(
                list(artisan_names), request, mode, patron
            ):
                if event.event_type == AtelierEventType.CONTEMPLATING:
                    live.update(
                        Spinner("dots", text=event.message or "contemplating...")
                    )
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
        console.print(
            ARTISAN_NOT_FOUND_MESSAGE.format(name=artisan_name, artisans=artisan_list)
        )
        return

    workshop = get_workshop()

    async def do_queue() -> None:
        commission = await workshop.queue_commission(artisan_name, request, patron)
        console.print(
            f"[green]✓[/green] Queued commission [bold]{commission.id}[/bold]"
        )
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
                    console.print(
                        f"[green]✓[/green] Created piece [bold]{piece.id}[/bold]"
                    )
                    count += 1
                elif event.event_type == AtelierEventType.ERROR:
                    console.print(f"[red]✗[/red] {event.message}")

            console.print(f"\n[dim]Processed {count} commissions[/dim]")
        else:
            async for event in queue.process_one():
                if event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                    console.print(
                        f"[green]✓[/green] Created piece [bold]{piece.id}[/bold]"
                    )
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
            console.print(
                f"[green]✓[/green] Added {len(added)} sample pieces to your gallery"
            )
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
    from agents.atelier.gallery.store import get_gallery
    from agents.atelier.workshop.commission import get_queue

    gallery = get_gallery()
    queue = get_queue()

    async def show_status() -> None:
        total_pieces = await gallery.count()
        pending_items = await queue.pending()

        console.print("\n[bold]✧ workshop status ✧[/bold]\n")

        table = Table(show_header=False, border_style="dim", box=None)
        table.add_column("Label", style="dim")
        table.add_column("Value")

        table.add_row("Gallery pieces", str(total_pieces))
        table.add_row("Pending queue", str(len(pending_items)))
        table.add_row("Available artisans", str(len(ARTISAN_REGISTRY)))

        console.print(table)

        if len(ARTISAN_REGISTRY) > 0:
            console.print("\n[dim]Artisans:[/dim]")
            for name in ARTISAN_REGISTRY.keys():
                console.print(f"  • {name}")

        console.print()

    run_async(show_status())


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
