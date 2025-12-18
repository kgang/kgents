"""
Gallery CLI: Production-grade command-line interface.

Usage:
    # Show all widgets
    python -m protocols.projection.gallery --all

    # Specific widget
    python -m protocols.projection.gallery --widget=agent_card_active

    # Category view
    python -m protocols.projection.gallery --category=primitives

    # Different targets
    python -m protocols.projection.gallery --target=tui --widget=glyph_active
    python -m protocols.projection.gallery --target=json --all

    # Developer overrides
    python -m protocols.projection.gallery --entropy=0.8 --seed=42
    python -m protocols.projection.gallery --phase=error --widget=agent_card_active

    # Special modes
    python -m protocols.projection.gallery --benchmark
    python -m protocols.projection.gallery --compare --widget=glyph_active
    python -m protocols.projection.gallery --list
    python -m protocols.projection.gallery --interactive

    # Verbose output
    python -m protocols.projection.gallery -v --widget=bar_solid
"""

from __future__ import annotations

import argparse
import sys
from typing import NoReturn

from agents.i.reactive.widget import RenderTarget
from protocols.projection.gallery.overrides import GalleryOverrides
from protocols.projection.gallery.pilots import PILOT_REGISTRY, PilotCategory
from protocols.projection.gallery.runner import Gallery, run_gallery


def _target_from_str(s: str) -> RenderTarget:
    """Convert string to RenderTarget."""
    mapping = {
        "cli": RenderTarget.CLI,
        "tui": RenderTarget.TUI,
        "marimo": RenderTarget.MARIMO,
        "json": RenderTarget.JSON,
    }
    return mapping.get(s.lower(), RenderTarget.CLI)


def _category_from_str(s: str) -> PilotCategory | None:
    """Convert string to PilotCategory."""
    mapping = {
        "primitives": PilotCategory.PRIMITIVES,
        "cards": PilotCategory.CARDS,
        "chrome": PilotCategory.CHROME,
        "streaming": PilotCategory.STREAMING,
        "composition": PilotCategory.COMPOSITION,
        "adapters": PilotCategory.ADAPTERS,
        "specialized": PilotCategory.SPECIALIZED,
    }
    return mapping.get(s.lower())


def run_interactive(gallery: Gallery) -> NoReturn:
    """
    Run interactive TUI mode with navigation.

    Requires textual to be installed.
    """
    try:
        from textual.app import App, ComposeResult
        from textual.binding import Binding
        from textual.containers import Horizontal, ScrollableContainer, Vertical
        from textual.widgets import Footer, Header, Static, Tree
        from textual.widgets.tree import TreeNode

        from agents.i.reactive.adapters import TextualAdapter
    except ImportError:
        print("Interactive mode requires textual: pip install textual")
        sys.exit(1)

    class GalleryApp(App[None]):
        """Interactive Projection Gallery."""

        TITLE = "Projection Component Gallery"
        SUB_TITLE = "Press ? for help | q to quit"

        CSS = """
        Screen {
            layout: horizontal;
        }

        #sidebar {
            width: 30;
            border: solid $primary;
        }

        #content {
            width: 1fr;
            padding: 1;
        }

        .pilot-view {
            border: round $secondary;
            padding: 1;
            margin-bottom: 1;
        }

        .pilot-title {
            background: $primary;
            color: $text;
            text-style: bold;
            padding: 0 1;
        }

        .pilot-desc {
            color: $text-muted;
            margin-bottom: 1;
        }
        """

        BINDINGS = [
            Binding("q", "quit", "Quit"),
            Binding("?", "help", "Help"),
            Binding("r", "refresh", "Refresh"),
            Binding("a", "show_all", "All"),
            Binding("1", "category_primitives", "Primitives"),
            Binding("2", "category_cards", "Cards"),
            Binding("3", "category_chrome", "Chrome"),
            Binding("4", "category_streaming", "Streaming"),
            Binding("5", "category_composition", "Composition"),
            Binding("6", "category_specialized", "Specialized"),
        ]

        def __init__(self) -> None:
            super().__init__()
            self.gallery = gallery
            self.current_pilot: str | None = None

        def compose(self) -> ComposeResult:
            yield Header()

            with Horizontal():
                # Sidebar with pilot tree
                with ScrollableContainer(id="sidebar"):
                    tree: Tree[str] = Tree("Gallery", id="pilot-tree")
                    tree.root.expand()

                    for category in PilotCategory:
                        pilots = [p for p in PILOT_REGISTRY.values() if p.category == category]
                        if pilots:
                            cat_node = tree.root.add(category.name, expand=True)
                            for pilot in pilots:
                                cat_node.add_leaf(pilot.name, data=pilot.name)

                    yield tree

                # Main content area
                with ScrollableContainer(id="content"):
                    yield Static("Select a pilot from the tree", id="pilot-view")

            yield Footer()

        def on_tree_node_selected(self, event: Tree.NodeSelected[str]) -> None:
            """Handle pilot selection from tree."""
            if event.node.data and event.node.data in PILOT_REGISTRY:
                self.current_pilot = event.node.data
                self._render_pilot(event.node.data)

        def _render_pilot(self, pilot_name: str) -> None:
            """Render selected pilot to content area."""
            pilot = PILOT_REGISTRY[pilot_name]
            result = self.gallery.render(pilot_name, RenderTarget.TUI)

            view = self.query_one("#pilot-view", Static)

            if result.success:
                content = (
                    f"[bold]{pilot_name}[/bold]\n"
                    f"[dim]{pilot.description}[/dim]\n"
                    f"[dim]Tags: {', '.join(pilot.tags)}[/dim]\n"
                    f"[dim]Rendered in {result.render_time_ms:.2f}ms[/dim]\n\n"
                )
                # TUI output might be rich.Text or similar
                if hasattr(result.output, "__rich__"):
                    view.update(f"{content}\n{result.output}")
                else:
                    view.update(f"{content}\n{result.output}")
            else:
                view.update(f"[red]Error: {result.error}[/red]")

        def _show_category(self, category: PilotCategory) -> None:
            """Show all pilots in a category."""
            output = self.gallery.show_category(category, RenderTarget.CLI)
            view = self.query_one("#pilot-view", Static)
            view.update(output)

        def action_show_all(self) -> None:
            output = self.gallery.show_all(RenderTarget.CLI)
            view = self.query_one("#pilot-view", Static)
            view.update(output)

        def action_category_primitives(self) -> None:
            self._show_category(PilotCategory.PRIMITIVES)

        def action_category_cards(self) -> None:
            self._show_category(PilotCategory.CARDS)

        def action_category_chrome(self) -> None:
            self._show_category(PilotCategory.CHROME)

        def action_category_streaming(self) -> None:
            self._show_category(PilotCategory.STREAMING)

        def action_category_composition(self) -> None:
            self._show_category(PilotCategory.COMPOSITION)

        def action_category_specialized(self) -> None:
            self._show_category(PilotCategory.SPECIALIZED)

        def action_refresh(self) -> None:
            if self.current_pilot:
                self._render_pilot(self.current_pilot)
            self.notify("Refreshed")

        def action_help(self) -> None:
            help_text = """
[bold]Projection Component Gallery[/bold]

[yellow]Navigation:[/yellow]
  Tree: Click or use arrows to select pilots
  q: Quit
  r: Refresh current pilot
  a: Show all pilots

[yellow]Category Shortcuts:[/yellow]
  1: Primitives (Glyph, Bar, Sparkline)
  2: Cards (AgentCard, YieldCard)
  3: Chrome (ErrorPanel, RefusalPanel)
  4: Streaming (Progress, StreamState)
  5: Composition (HStack, VStack)
  6: Specialized (DensityField, DialecticCard)

[yellow]Overrides:[/yellow]
  Set via environment variables:
  KGENTS_GALLERY_ENTROPY=0.5
  KGENTS_GALLERY_SEED=42
"""
            view = self.query_one("#pilot-view", Static)
            view.update(help_text)

    app = GalleryApp()
    app.run()
    sys.exit(0)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Projection Component Gallery - Dense pilot experiences for rapid iteration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Browse all widgets
    python -m protocols.projection.gallery --all

    # Focus on one widget
    python -m protocols.projection.gallery -w agent_card_active

    # Filter by category
    python -m protocols.projection.gallery -c primitives

    # Developer overrides
    python -m protocols.projection.gallery -e 0.8 -s 42 -w glyph_entropy_sweep

    # Target comparison
    python -m protocols.projection.gallery --compare -w glyph_active

    # Performance benchmarks
    python -m protocols.projection.gallery --benchmark

    # Interactive TUI mode
    python -m protocols.projection.gallery --interactive

Environment Variables:
    KGENTS_GALLERY_TARGET=cli|tui|marimo|json
    KGENTS_GALLERY_ENTROPY=0.0-1.0
    KGENTS_GALLERY_SEED=int
    KGENTS_GALLERY_VERBOSE=1
        """,
    )

    # Mode flags
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--all", "-a", action="store_true", help="Show all pilots")
    mode_group.add_argument("--list", "-l", action="store_true", help="List available pilots")
    mode_group.add_argument(
        "--benchmark", "-b", action="store_true", help="Run performance benchmarks"
    )
    mode_group.add_argument("--compare", action="store_true", help="Compare across all targets")
    mode_group.add_argument("--interactive", "-i", action="store_true", help="Interactive TUI mode")

    # Selection
    parser.add_argument("--widget", "-w", metavar="NAME", help="Specific pilot/widget to show")
    parser.add_argument(
        "--category",
        "-c",
        choices=[
            "primitives",
            "cards",
            "chrome",
            "streaming",
            "composition",
            "adapters",
            "specialized",
        ],
        help="Filter by category",
    )
    parser.add_argument("--tag", "-T", metavar="TAG", help="Filter by tag")

    # Target
    parser.add_argument(
        "--target",
        "-t",
        choices=["cli", "tui", "marimo", "json"],
        default="cli",
        help="Render target (default: cli)",
    )

    # Overrides
    parser.add_argument(
        "--entropy", "-e", type=float, metavar="F", help="Override entropy (0.0-1.0)"
    )
    parser.add_argument("--seed", "-s", type=int, metavar="N", help="Deterministic seed")
    parser.add_argument("--time", type=float, metavar="MS", help="Fixed time in milliseconds")
    parser.add_argument(
        "--phase",
        choices=[
            "idle",
            "active",
            "waiting",
            "error",
            "yielding",
            "thinking",
            "complete",
        ],
        help="Override phase for phase-aware widgets",
    )
    parser.add_argument(
        "--style", choices=["compact", "full", "minimal"], help="Override card style"
    )
    parser.add_argument("--breathing", action="store_true", help="Enable breathing animation")
    parser.add_argument("--no-breathing", action="store_true", help="Disable breathing animation")

    # Output
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output with debug info"
    )

    args = parser.parse_args()

    # Build overrides from CLI args
    breathing = None
    if args.breathing:
        breathing = True
    elif args.no_breathing:
        breathing = False

    cli_overrides = GalleryOverrides(
        target=_target_from_str(args.target) if args.target else None,
        entropy=args.entropy,
        seed=args.seed,
        time_ms=args.time,
        verbose=args.verbose,
        phase=args.phase,
        style=args.style,
        breathing=breathing,
    )

    gallery = Gallery(cli_overrides)

    # Handle interactive mode first (special case)
    if args.interactive:
        run_interactive(gallery)  # NoReturn

    # Determine target
    target = _target_from_str(args.target)

    # Handle modes
    if args.list:
        print(gallery.list_pilots())
        return

    if args.benchmark:
        if args.widget:
            results = gallery.benchmark([args.widget])
        elif args.category:
            cat = _category_from_str(args.category)
            if cat:
                from protocols.projection.gallery.pilots import get_pilots_by_category

                pilots = [p.name for p in get_pilots_by_category(cat)]
                results = gallery.benchmark(pilots)
            else:
                results = gallery.benchmark()
        else:
            results = gallery.benchmark()
        print(gallery.format_benchmarks(results))
        return

    if args.compare:
        if not args.widget:
            print("--compare requires --widget")
            sys.exit(1)
        print(gallery.compare_targets(args.widget))
        return

    if args.tag:
        pilots = get_pilots_by_tag(args.tag)
        if not pilots:
            print(f"No pilots with tag: {args.tag}")
            sys.exit(1)
        for pilot in pilots:
            print(gallery.show(pilot.name, target))
            print()
        return

    if args.widget:
        print(gallery.show(args.widget, target))
        return

    if args.category:
        cat = _category_from_str(args.category)
        if cat:
            print(gallery.show_category(cat, target))
        else:
            print(f"Unknown category: {args.category}")
        return

    if args.all:
        print(gallery.show_all(target))
        return

    # Default: show help
    parser.print_help()


# Import get_pilots_by_tag for tag filtering
from protocols.projection.gallery.pilots import get_pilots_by_tag

if __name__ == "__main__":
    main()
