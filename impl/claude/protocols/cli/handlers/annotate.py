"""
Annotate Handler: CLI for spec ↔ impl mapping.

> *"Every spec section should trace to implementation. Every gotcha should be captured."*

This handler provides the CLI interface for the annotation system:
- `kg annotate <spec> --principle <name> --section <section> --note <note>`
- `kg annotate <spec> --impl --section <section> --link <path>`
- `kg annotate <spec> --gotcha --section <section> --note <note>`
- `kg annotate <spec> --taste --section <section> --note <note>`
- `kg annotate <spec> --show`
- `kg annotate <spec> --export [--json]`

Pattern: Rich CLI UX layer following witness_thin.py pattern.
         Provides formatting, validation, and user interaction.

Teaching:
    gotcha: We use asyncio.run() for each command invocation. This creates
            a fresh event loop, so we must bootstrap services each time.

    principle: Composable - CLI handler composes AnnotationStore + graph builder
               to provide rich user experience without duplicating logic.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 2)
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import TYPE_CHECKING, Any

from protocols.cli.handler_meta import handler

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


def _print_annotation(ann: dict[str, Any], verbose: bool = False) -> None:
    """Print a single annotation."""
    console = _get_console()

    # Extract fields
    spec_path = ann.get("spec_path", "")
    section = ann.get("section", "")
    kind = ann.get("kind", "")
    principle = ann.get("principle", "")
    impl_path = ann.get("impl_path", "")
    note = ann.get("note", "")
    ann_id = ann.get("id", "")[:12]
    status = ann.get("status", "active")

    # Format display
    if console:
        # Rich output
        status_color = "green" if status == "active" else "dim"
        line = f"  [{status_color}]{kind}[/{status_color}]  {section}"
        if principle:
            line += f" [dim][{principle}][/dim]"
        if impl_path:
            line += f" [cyan]→ {impl_path}[/cyan]"
        console.print(line)

        if verbose and note:
            console.print(f"         [dim]{note}[/dim]")
        if verbose:
            console.print(f"         [dim]ID: {ann_id}[/dim]")
    else:
        # Plain text
        line = f"  {kind}  {section}"
        if principle:
            line += f" [{principle}]"
        if impl_path:
            line += f" → {impl_path}"
        print(line)
        if verbose and note:
            print(f"         {note}")
        if verbose:
            print(f"         ID: {ann_id}")


def _print_annotations(
    annotations: list[dict[str, Any]],
    title: str = "Annotations",
    verbose: bool = False,
) -> None:
    """Print a list of annotations."""
    console = _get_console()

    if not annotations:
        if console:
            console.print("[dim]No annotations found.[/dim]")
        else:
            print("No annotations found.")
        return

    if console:
        console.print(f"\n[bold]{title}[/bold]")
        console.print("[dim]" + "─" * 60 + "[/dim]")
    else:
        print(f"\n{title}")
        print("─" * 60)

    for ann in annotations:
        _print_annotation(ann, verbose=verbose)

    if console:
        console.print()
    else:
        print()


def _print_graph(graph: dict[str, Any]) -> None:
    """Print implementation graph with coverage metrics."""
    console = _get_console()

    spec_path = graph.get("spec_path", "")
    coverage = graph.get("coverage", 0.0)
    edges = graph.get("edges", [])
    uncovered = graph.get("uncovered_sections", [])

    if console:
        console.print(f"\n[bold]Implementation Graph: {spec_path}[/bold]")
        console.print("[dim]" + "─" * 60 + "[/dim]")
        console.print(f"Coverage: [green]{coverage:.1%}[/green]")
        console.print(f"Edges: {len(edges)}")
        console.print(f"Uncovered sections: {len(uncovered)}")

        if edges:
            console.print("\n[bold]Spec → Impl Links:[/bold]")
            for edge in edges:
                section = edge.get("spec_section", "")
                impl_path = edge.get("impl_path", "")
                verified = edge.get("verified", False)
                status = "[green]✓[/green]" if verified else "[red]✗[/red]"
                console.print(f"  {status} {section} [cyan]→[/cyan] {impl_path}")

        if uncovered:
            console.print("\n[bold]Uncovered Sections:[/bold]")
            for section in uncovered:
                console.print(f"  [dim]• {section}[/dim]")

        console.print()
    else:
        # Plain text
        print(f"\nImplementation Graph: {spec_path}")
        print("─" * 60)
        print(f"Coverage: {coverage:.1%}")
        print(f"Edges: {len(edges)}")
        print(f"Uncovered sections: {len(uncovered)}")

        if edges:
            print("\nSpec → Impl Links:")
            for edge in edges:
                section = edge.get("spec_section", "")
                impl_path = edge.get("impl_path", "")
                verified = edge.get("verified", False)
                status = "✓" if verified else "✗"
                print(f"  {status} {section} → {impl_path}")

        if uncovered:
            print("\nUncovered Sections:")
            for section in uncovered:
                print(f"  • {section}")

        print()


# =============================================================================
# Annotation Operations
# =============================================================================


async def _save_annotation_async(
    spec_path: str,
    section: str,
    kind: str,
    note: str,
    created_by: str = "kent",
    principle: str | None = None,
    impl_path: str | None = None,
    decision_id: str | None = None,
) -> dict[str, Any]:
    """Save a new annotation with witness marking."""
    from services.annotate.store import AnnotationStore
    from services.annotate.types import AnnotationKind
    from services.providers import get_witness_persistence

    store = AnnotationStore()
    witness = await get_witness_persistence()

    # Convert kind string to enum
    kind_enum = AnnotationKind(kind)

    # Save annotation
    annotation = await store.save_annotation(
        spec_path=spec_path,
        section=section,
        kind=kind_enum,
        note=note,
        created_by=created_by,
        witness=witness,
        principle=principle,
        impl_path=impl_path,
        decision_id=decision_id,
    )

    return {
        "id": annotation.id,
        "spec_path": annotation.spec_path,
        "section": annotation.section,
        "kind": annotation.kind.value,
        "principle": annotation.principle,
        "impl_path": annotation.impl_path,
        "decision_id": annotation.decision_id,
        "note": annotation.note,
        "created_by": annotation.created_by,
        "created_at": annotation.created_at.isoformat(),
        "mark_id": annotation.mark_id,
        "status": annotation.status.value,
    }


async def _query_annotations_async(
    spec_path: str | None = None,
    kind: str | None = None,
    principle: str | None = None,
    impl_path: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Query annotations by filters."""
    from services.annotate.store import AnnotationStore
    from services.annotate.types import AnnotationKind, AnnotationStatus

    store = AnnotationStore()

    # Convert string enums
    kind_enum = AnnotationKind(kind) if kind else None
    status_enum = AnnotationStatus(status) if status else None

    # Query
    result = await store.query_annotations(
        spec_path=spec_path,
        kind=kind_enum,
        principle=principle,
        impl_path=impl_path,
        status=status_enum,
    )

    # Convert to dicts
    return [
        {
            "id": ann.id,
            "spec_path": ann.spec_path,
            "section": ann.section,
            "kind": ann.kind.value,
            "principle": ann.principle,
            "impl_path": ann.impl_path,
            "decision_id": ann.decision_id,
            "note": ann.note,
            "created_by": ann.created_by,
            "created_at": ann.created_at.isoformat(),
            "mark_id": ann.mark_id,
            "status": ann.status.value,
        }
        for ann in result.annotations
    ]


async def _build_graph_async(spec_path: str) -> dict[str, Any]:
    """Build implementation graph for a spec."""
    from pathlib import Path

    from services.annotate.graph import build_impl_graph
    from services.annotate.store import AnnotationStore

    store = AnnotationStore()
    graph = await build_impl_graph(spec_path, store, repo_root=Path.cwd())

    return {
        "spec_path": graph.spec_path,
        "coverage": graph.coverage,
        "edges": [
            {
                "spec_section": edge.spec_section,
                "impl_path": edge.impl_path,
                "verified": edge.verified,
                "annotation_id": edge.annotation_id,
            }
            for edge in graph.edges
        ],
        "uncovered_sections": graph.uncovered_sections,
    }


async def _search_annotations_async(
    search_text: str,
    spec_path: str | None = None,
    kind: str | None = None,
) -> list[dict[str, Any]]:
    """Search annotations by substring."""
    from services.annotate.store import AnnotationStore
    from services.annotate.types import AnnotationKind

    store = AnnotationStore()
    kind_enum = AnnotationKind(kind) if kind else None

    annotations = await store.search_annotations(
        search_text=search_text,
        spec_path=spec_path,
        kind=kind_enum,
    )

    return [
        {
            "id": ann.id,
            "spec_path": ann.spec_path,
            "section": ann.section,
            "kind": ann.kind.value,
            "principle": ann.principle,
            "impl_path": ann.impl_path,
            "note": ann.note,
            "created_by": ann.created_by,
            "created_at": ann.created_at.isoformat(),
            "mark_id": ann.mark_id,
            "status": ann.status.value,
        }
        for ann in annotations
    ]


async def _delete_annotation_async(annotation_id: str, archive: bool = True) -> dict[str, Any]:
    """Delete or archive an annotation."""
    from services.annotate.store import AnnotationStore
    from services.annotate.types import AnnotationStatus

    store = AnnotationStore()

    if archive:
        # Soft delete: mark as archived
        result = await store.update_status(annotation_id, AnnotationStatus.ARCHIVED)
        if result:
            return {
                "success": True,
                "action": "archived",
                "annotation_id": annotation_id,
            }
    else:
        # Hard delete: remove from database
        success = await store.delete_annotation(annotation_id)
        if success:
            return {
                "success": True,
                "action": "deleted",
                "annotation_id": annotation_id,
            }

    return {
        "success": False,
        "error": "Annotation not found",
        "annotation_id": annotation_id,
    }


async def _bootstrap_and_run(coro_func: Any, *args: Any, **kwargs: Any) -> Any:
    """
    Bootstrap services and run a coroutine in a fresh context.

    See witness_thin.py for detailed explanation of why this is needed.
    """
    from protocols.agentese.container import reset_container
    from services.bootstrap import bootstrap_services, reset_registry

    reset_registry()
    reset_container()
    await bootstrap_services()
    return await coro_func(*args, **kwargs)


def _run_async_factory(coro_func: Any) -> Any:
    """Create a sync wrapper that properly bootstraps before running async code."""

    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(_bootstrap_and_run(coro_func, *args, **kwargs))

    return sync_wrapper


# =============================================================================
# Command Implementation
# =============================================================================


@handler("annotate", is_async=False, tier=1, description="Spec ↔ impl mapping")
def cmd_annotate(argv: list[str]) -> int:
    """
    Handle kg annotate commands.

    Usage:
        kg annotate <spec> --principle <name> --section <section> --note <note>
        kg annotate <spec> --impl --section <section> --link <path>
        kg annotate <spec> --gotcha --section <section> --note <note>
        kg annotate <spec> --taste --section <section> --note <note>
        kg annotate <spec> --show [--verbose]
        kg annotate <spec> --export [--json]
        kg annotate <spec> --graph

    Examples:
        # Add principle annotation
        kg annotate spec/protocols/witness.md \\
          --principle composable \\
          --section "Mark Structure" \\
          --note "Single output per mark"

        # Add implementation link
        kg annotate spec/protocols/witness.md \\
          --impl \\
          --section "MarkStore" \\
          --link "services/witness/store.py:MarkStore"

        # Add gotcha
        kg annotate spec/protocols/witness.md \\
          --gotcha \\
          --section "Event Emission" \\
          --note "Bus publish is fire-and-forget"

        # View annotations
        kg annotate spec/protocols/witness.md --show

        # Build impl graph
        kg annotate spec/protocols/witness.md --graph
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Annotate specs with principles, impl links, and gotchas",
        add_help=True,
    )

    # Positional: spec path
    parser.add_argument("spec", nargs="?", help="Path to spec file")

    # Annotation types (mutually exclusive)
    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument("--principle", metavar="NAME", help="Add principle annotation")
    type_group.add_argument("--impl", action="store_true", help="Add implementation link")
    type_group.add_argument("--gotcha", action="store_true", help="Add gotcha annotation")
    type_group.add_argument("--taste", action="store_true", help="Add taste annotation")
    type_group.add_argument("--decision", metavar="ID", help="Link to fusion decision")

    # Common fields for adding annotations
    parser.add_argument("--section", metavar="SECTION", help="Spec section/heading")
    parser.add_argument("--note", metavar="NOTE", help="Annotation note")
    parser.add_argument("--link", metavar="PATH", help="Implementation path (for --impl)")

    # Query/display modes
    parser.add_argument("--show", action="store_true", help="Show annotations for spec")
    parser.add_argument("--export", action="store_true", help="Export annotations")
    parser.add_argument("--graph", action="store_true", help="Build implementation graph")
    parser.add_argument("--search", metavar="TEXT", help="Search annotations by substring")
    parser.add_argument("--delete", metavar="ID", help="Delete/archive annotation by ID")

    # Options
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--author", default="kent", help="Annotation author")
    parser.add_argument("--hard-delete", action="store_true", help="Hard delete (vs archive)")
    parser.add_argument("--kind", metavar="KIND", help="Filter by kind (for --search)")

    args = parser.parse_args(argv)

    # Validate spec path required (unless using --search or --delete without spec)
    if not args.spec and not args.search and not args.delete:
        parser.print_help()
        return 1

    # Handle --show mode
    if args.show:
        _run_show = _run_async_factory(_query_annotations_async)
        # Default to showing only active annotations unless specified otherwise
        annotations = _run_show(spec_path=args.spec, status="active")

        if args.json:
            print(json.dumps(annotations, indent=2))
        else:
            _print_annotations(annotations, f"Annotations: {args.spec}", args.verbose)
        return 0

    # Handle --export mode
    if args.export:
        _run_export = _run_async_factory(_query_annotations_async)
        annotations = _run_export(spec_path=args.spec)

        if args.json:
            print(json.dumps(annotations, indent=2))
        else:
            # Export as YAML (future work)
            print(json.dumps(annotations, indent=2))
        return 0

    # Handle --graph mode
    if args.graph:
        _run_graph = _run_async_factory(_build_graph_async)
        graph = _run_graph(args.spec)

        if args.json:
            print(json.dumps(graph, indent=2))
        else:
            _print_graph(graph)
        return 0

    # Handle --search mode
    if args.search:
        _run_search = _run_async_factory(_search_annotations_async)
        results = _run_search(
            search_text=args.search,
            spec_path=args.spec,
            kind=args.kind,
        )

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            _print_annotations(results, f"Search results: '{args.search}'", args.verbose)
        return 0

    # Handle --delete mode
    if args.delete:
        _run_delete = _run_async_factory(_delete_annotation_async)
        result = _run_delete(annotation_id=args.delete, archive=not args.hard_delete)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            console = _get_console()
            if result["success"]:
                action = result["action"]
                if console:
                    console.print(f"[green]✓[/green] Annotation {action}: {args.delete}")
                else:
                    print(f"✓ Annotation {action}: {args.delete}")
            else:
                error = result.get("error", "Unknown error")
                if console:
                    console.print(f"[red]✗[/red] {error}")
                else:
                    print(f"✗ {error}")
                return 1
        return 0

    # Handle annotation creation modes
    if not args.section:
        print("Error: --section required for creating annotations", file=sys.stderr)
        return 1

    if not args.note and not args.link:
        print("Error: --note or --link required for creating annotations", file=sys.stderr)
        return 1

    # Determine annotation kind
    kind = None
    principle = None
    impl_path = None
    decision_id = None
    note = args.note or ""

    if args.principle:
        kind = "principle"
        principle = args.principle
    elif args.impl:
        kind = "impl_link"
        impl_path = args.link
        if not impl_path:
            print("Error: --link required for --impl annotations", file=sys.stderr)
            return 1
    elif args.gotcha:
        kind = "gotcha"
    elif args.taste:
        kind = "taste"
    elif args.decision:
        kind = "decision"
        decision_id = args.decision
    else:
        print(
            "Error: Must specify --principle, --impl, --gotcha, --taste, or --decision",
            file=sys.stderr,
        )
        return 1

    # Save annotation
    _run_save = _run_async_factory(_save_annotation_async)
    annotation = _run_save(
        spec_path=args.spec,
        section=args.section,
        kind=kind,
        note=note,
        created_by=args.author,
        principle=principle,
        impl_path=impl_path,
        decision_id=decision_id,
    )

    if args.json:
        print(json.dumps(annotation, indent=2))
    else:
        console = _get_console()
        if console:
            console.print(
                f"[green]✓[/green] Created {kind} annotation for "
                f"[cyan]{args.spec}[/cyan] / [bold]{args.section}[/bold]"
            )
            console.print(f"  Mark ID: [dim]{annotation['mark_id']}[/dim]")
        else:
            print(f"✓ Created {kind} annotation for {args.spec} / {args.section}")
            print(f"  Mark ID: {annotation['mark_id']}")

    return 0


__all__ = ["cmd_annotate"]
