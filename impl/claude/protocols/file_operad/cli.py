"""
FILE_OPERAD CLI: Portal Navigation Commands

"Navigation is expansion. Expansion is navigation."

This module provides the `kg op` command for navigating operads as documents.

Commands:
  kg op show <path>     - Show an operation with portal links
  kg op expand <path>   - Expand all portals in an operation
  kg op list [operad]   - List operations in an operad
  kg op portals <path>  - List portal links in an operation

The core insight: files don't link to other files—they contain
expandable sections that reveal other files inline.

See: spec/protocols/file-operad.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .ashc_bridge import (
    LawProofCompiler,
    LawVerifier,
    VerificationResult,
)
from .law_parser import (
    LawDefinition,
    LawStatus,
    list_laws_in_operad,
    parse_law_file,
)
from .portal import (
    OPERADS_ROOT,
    PortalOpenSignal,
    PortalRenderer,
    PortalToken,
    PortalTree,
    expand_file,
    parse_wires_to,
    show_portals,
)
from .sandbox import (
    InvalidTransitionError,
    SandboxConfig,
    SandboxId,
    SandboxPhase,
    SandboxPolynomial,
    SandboxRuntime,
    get_sandbox_store,
    reset_sandbox_store,
)
from .trace import (
    enable_persistence,
    get_file_trace_store,
    record_expansion,
    sync_file_trace_store,
)

if TYPE_CHECKING:
    pass


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


def _print_header(text: str) -> None:
    """Print a styled header."""
    console = _get_console()
    if console:
        console.print(f"\n[bold]{text}[/bold]")
        console.print("[dim]" + "\u2500" * 60 + "[/dim]")
    else:
        print(f"\n{text}")
        print("\u2500" * 60)


def _print_portal_link(link: Any, index: int = 0) -> None:
    """Print a single portal link."""
    console = _get_console()
    exists = link.exists()
    status = "[green]\u2713[/green]" if exists else "[dim]\u2717[/dim]"

    if console:
        edge_style = "[cyan]" if exists else "[dim]"
        path_style = "" if exists else "[dim]"
        console.print(
            f"  {status} {edge_style}[{link.edge_type}][/] "
            f"{path_style}{link.path}[/]" + (f" [dim]({link.note})[/dim]" if link.note else "")
        )
    else:
        status_char = "\u2713" if exists else "\u2717"
        note = f" ({link.note})" if link.note else ""
        print(f"  {status_char} [{link.edge_type}] {link.path}{note}")


# =============================================================================
# Path Resolution
# =============================================================================


def resolve_op_path(path_arg: str) -> Path | None:
    """
    Resolve a path argument to a .op file.

    Accepts:
    - Full path: /path/to/file.op
    - Relative path: WITNESS_OPERAD/mark
    - Just operation: mark (searches current context)

    Returns the resolved Path or None if not found.
    """
    # Full path
    full_path = Path(path_arg)
    if full_path.is_absolute():
        if full_path.exists():
            return full_path
        # Try adding .op extension
        with_ext = full_path.with_suffix(".op")
        if with_ext.exists():
            return with_ext
        return None

    # Relative to operads root: OPERAD_NAME/operation
    if "/" in path_arg:
        operad, op = path_arg.split("/", 1)
        op_file = OPERADS_ROOT / operad / f"{op}.op"
        if op_file.exists():
            return op_file
        # Try without .op (in case user included it)
        if op.endswith(".op"):
            op_file = OPERADS_ROOT / operad / op
            if op_file.exists():
                return op_file
        return None

    # Search all operads for this operation name
    for operad_dir in OPERADS_ROOT.iterdir():
        if operad_dir.is_dir() and not operad_dir.name.startswith("_"):
            op_file = operad_dir / f"{path_arg}.op"
            if op_file.exists():
                return op_file

    return None


# =============================================================================
# Subcommand Handlers
# =============================================================================


def cmd_show(args: list[str]) -> int:
    """
    Show an operation file with syntax highlighting.

    Usage:
        kg op show WITNESS_OPERAD/mark
        kg op show mark  (searches all operads)
    """
    if not args:
        print("Usage: kg op show <path>")
        print("Example: kg op show WITNESS_OPERAD/mark")
        return 1

    path = resolve_op_path(args[0])
    if path is None:
        print(f"Error: Operation not found: {args[0]}")
        print(f"\nSearched in: {OPERADS_ROOT}")
        return 1

    console = _get_console()
    content = path.read_text()

    _print_header(f"\U0001f4c4 {path.stem}")

    if console:
        try:
            from rich.markdown import Markdown

            console.print(Markdown(content))
        except ImportError:
            console.print(content)
    else:
        print(content)

    # Show portal links summary
    links = parse_wires_to(content)
    if links:
        _print_header("Portal Links")
        for link in links:
            _print_portal_link(link)
        print()

    return 0


def cmd_expand(args: list[str]) -> int:
    """
    Expand all portal tokens in an operation.

    Usage:
        kg op expand WITNESS_OPERAD/mark
        kg op expand mark --depth 2

    Each expansion is recorded as a FileWiringTrace for ASHC evidence.
    """
    if not args:
        print("Usage: kg op expand <path> [--depth N]")
        return 1

    # Parse args
    path_arg = args[0]
    max_depth = 3

    for i, arg in enumerate(args[1:], 1):
        if arg == "--depth" and i + 1 < len(args):
            try:
                max_depth = int(args[i + 1])
            except (ValueError, IndexError):
                pass

    path = resolve_op_path(path_arg)
    if path is None:
        print(f"Error: Operation not found: {path_arg}")
        return 1

    console = _get_console()
    _print_header(f"\U0001f50d Expanding: {path.stem}")

    # Parse and expand
    content = path.read_text()
    links = parse_wires_to(content)

    if not links:
        if console:
            console.print("[dim]No portal links found in this file.[/dim]")
        else:
            print("No portal links found in this file.")
        return 0

    renderer = PortalRenderer()
    from datetime import datetime

    for i, link in enumerate(links):
        token = PortalToken(link)
        if token.load():
            # Record the expansion as a WiringTrace
            signal = PortalOpenSignal(
                paths_opened=[str(link.file_path)] if link.file_path else [link.path],
                edge_type=link.edge_type,
                parent_path=str(path),
                depth=0,
                timestamp=datetime.now(),
            )
            record_expansion(signal, actor="user")

        if console:
            console.print()
            console.print(renderer.render_cli(token, max_lines=25))
        else:
            print()
            print(renderer.render_cli(token, max_lines=25))

    print()
    return 0


def cmd_list(args: list[str]) -> int:
    """
    List operations in an operad (or all operads).

    Usage:
        kg op list                   - List all operads
        kg op list WITNESS_OPERAD    - List ops in specific operad
    """
    console = _get_console()

    if not args:
        # List all operads
        _print_header("Operads")

        if not OPERADS_ROOT.exists():
            print(f"No operads found at {OPERADS_ROOT}")
            print("Run bootstrap to create initial operads.")
            return 0

        for operad_dir in sorted(OPERADS_ROOT.iterdir()):
            if operad_dir.is_dir() and not operad_dir.name.startswith("_"):
                op_count = len(list(operad_dir.glob("*.op")))
                if console:
                    console.print(
                        f"  [bold]{operad_dir.name}[/bold] [dim]({op_count} operations)[/dim]"
                    )
                else:
                    print(f"  {operad_dir.name} ({op_count} operations)")

        print()
        return 0

    # List operations in specific operad
    operad_name = args[0]
    operad_dir = OPERADS_ROOT / operad_name

    if not operad_dir.exists():
        print(f"Error: Operad not found: {operad_name}")
        print("\nAvailable operads:")
        cmd_list([])
        return 1

    _print_header(f"{operad_name}")

    for op_file in sorted(operad_dir.glob("*.op")):
        # Count portal links
        try:
            links = show_portals(op_file)
            link_info = f" \u2192 {len(links)} portals" if links else ""
        except Exception:
            link_info = ""

        if console:
            console.print(f"  [cyan]{op_file.stem}[/cyan]{link_info}")
        else:
            print(f"  {op_file.stem}{link_info}")

    # Show laws if any
    laws_dir = operad_dir / "_laws"
    if laws_dir.exists():
        laws = list(laws_dir.glob("*.law"))
        if laws:
            print()
            if console:
                console.print(f"  [dim]Laws ({len(laws)}):[/dim]")
            else:
                print(f"  Laws ({len(laws)}):")
            for law in sorted(laws):
                if console:
                    console.print(f"    [dim]{law.stem}[/dim]")
                else:
                    print(f"    {law.stem}")

    print()
    return 0


def cmd_portals(args: list[str]) -> int:
    """
    List portal links in an operation (without expanding).

    Usage:
        kg op portals WITNESS_OPERAD/mark
    """
    if not args:
        print("Usage: kg op portals <path>")
        return 1

    path = resolve_op_path(args[0])
    if path is None:
        print(f"Error: Operation not found: {args[0]}")
        return 1

    links = show_portals(path)

    _print_header(f"Portals in {path.stem}")

    if not links:
        print("  (no portal links)")
        return 0

    for link in links:
        _print_portal_link(link)

    print()
    return 0


def cmd_tree(args: list[str]) -> int:
    """
    Show portal expansion tree for an operation.

    Usage:
        kg op tree WITNESS_OPERAD/mark --depth 2
        kg op tree WITNESS_OPERAD/mark --trail  (also show trail)

    Uses PortalTree.from_file() to build the tree and PortalTree.render() for display.
    Each traversal is recorded as a FileWiringTrace for ASHC evidence.
    "The tree of expansions IS your trail through the knowledge graph."
    """
    if not args:
        print("Usage: kg op tree <path> [--depth N] [--trail]")
        return 1

    path_arg = args[0]
    max_depth = 2
    show_trail = False

    for i, arg in enumerate(args[1:], 1):
        if arg == "--depth" and i + 1 < len(args):
            try:
                max_depth = int(args[i + 1])
            except (ValueError, IndexError):
                pass
        elif arg == "--trail":
            show_trail = True

    path = resolve_op_path(path_arg)
    if path is None:
        print(f"Error: Operation not found: {path_arg}")
        return 1

    console = _get_console()
    _print_header(f"\U0001f333 Portal Tree: {path.stem}")

    # Build tree using PortalTree.from_file()
    tree = PortalTree.from_file(path, max_depth=max_depth, expand_all=True)

    # Record expansions for ASHC evidence
    from datetime import datetime

    def record_tree_expansions(
        node: "PortalNode",
        parent_path: str = "root",
    ) -> None:
        """Recursively record all expanded nodes as traces."""
        from .portal import PortalNode

        for child in node.children:
            if child.edge_type:
                # Get the file path from the token if it exists
                token = tree.tokens.get(child.path)
                if token and token.link.exists():
                    signal = PortalOpenSignal(
                        paths_opened=[str(token.link.file_path)]
                        if token.link.file_path
                        else [child.path],
                        edge_type=child.edge_type,
                        parent_path=parent_path,
                        depth=child.depth,
                        timestamp=datetime.now(),
                    )
                    record_expansion(signal, actor="user")

            # Recurse into expanded children
            if child.expanded:
                record_tree_expansions(child, parent_path=child.path)

    # Import PortalNode for type hint
    from .portal import PortalNode

    record_tree_expansions(tree.root, parent_path=str(path))

    # Render the tree using PortalTree.render()
    rendered = tree.render(max_depth=max_depth)

    if console:
        # Apply some Rich styling to the rendered output
        for line in rendered.split("\n"):
            # Color edge types in brackets
            if "[" in line and "]" in line:
                # Find edge type and color it
                line = line.replace("[", "[cyan][").replace("]", "][/cyan]", 1)
            console.print(line)
    else:
        print(rendered)

    # Optionally show trail
    if show_trail:
        trail = tree.to_trail(name=f"tree:{path.stem}")
        print()
        _print_header("\U0001f4cd Trail")
        print(trail.serialize())

    print()
    return 0


def cmd_trail(args: list[str]) -> int:
    """
    Show the exploration trail (recorded traces).

    Usage:
        kg op trail              Show recent traces (in-memory)
        kg op trail --persist    Load from persistence file
        kg op trail --limit 50   Show more traces
        kg op trail --path X     Filter by path
        kg op trail --save       Save current traces to persistence

    "Every expansion leaves a mark. Every mark is evidence."
    """
    # Parse args
    limit = 20
    path_filter = None
    use_persistence = False
    save_traces = False

    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif args[i] == "--path" and i + 1 < len(args):
            path_filter = args[i + 1]
            i += 2
        elif args[i] in ("--persist", "-p"):
            use_persistence = True
            i += 1
        elif args[i] == "--save":
            save_traces = True
            i += 1
        else:
            i += 1

    console = _get_console()

    # Enable persistence if requested
    if use_persistence:
        store = enable_persistence()
        _print_header("📜 Exploration Trail (persisted)")
    else:
        store = get_file_trace_store()
        _print_header("📜 Exploration Trail")

    # Save if requested
    if save_traces:
        path = sync_file_trace_store()
        if path:
            if console:
                console.print(f"[green]✓[/green] Saved {len(store)} traces to {path}")
            else:
                print(f"✓ Saved {len(store)} traces to {path}")
            print()
        else:
            if console:
                console.print("[yellow]⚠[/yellow] Persistence not enabled. Use --persist first.")
            else:
                print("⚠ Persistence not enabled. Use --persist first.")
        return 0

    if path_filter:
        traces = store.get_path_history(path_filter)
    else:
        traces = store.recent(limit)

    if not traces:
        if console:
            console.print(
                "[dim]No traces recorded yet. Use 'kg op tree' or 'kg op expand' to explore.[/dim]"
            )
            if use_persistence and store.persistence_path:
                console.print(f"[dim]Persistence file: {store.persistence_path}[/dim]")
        else:
            print("No traces recorded yet. Use 'kg op tree' or 'kg op expand' to explore.")
        return 0

    for trace in traces:
        # Format timestamp - include date if persistence mode (cross-session)
        if use_persistence:
            ts = trace.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            ts = trace.timestamp.strftime("%H:%M:%S")

        # Format depth indicator
        depth_indicator = "  " * trace.depth + ("└─ " if trace.depth > 0 else "")

        # Edge type styling
        edge = f"[{trace.edge_type}]" if trace.edge_type else "[root]"

        # Extract just the operation name from path
        path_display = trace.path
        if "/" in trace.path:
            parts = trace.path.split("/")
            path_display = "/".join(parts[-2:]) if len(parts) >= 2 else parts[-1]

        if console:
            actor_style = "[cyan]" if trace.actor == "user" else "[yellow]"
            console.print(
                f"  [dim]{ts}[/dim] {depth_indicator}"
                f"[green]{edge}[/green] {path_display} "
                f"{actor_style}({trace.actor})[/]"
            )
        else:
            print(f"  {ts} {depth_indicator}{edge} {path_display} ({trace.actor})")

    print()
    if console:
        console.print(f"[dim]Total: {len(store)} traces | Showing: {len(traces)}[/dim]")
        if use_persistence and store.persistence_path:
            console.print(f"[dim]Persistence: {store.persistence_path}[/dim]")
    else:
        print(f"Total: {len(store)} traces | Showing: {len(traces)}")

    print()
    return 0


# =============================================================================
# Sandbox Commands (Session 5)
# =============================================================================


def cmd_sandbox(args: list[str]) -> int:
    """
    Create a sandbox from an operation.

    Usage:
        kg op sandbox WITNESS_OPERAD/mark
        kg op sandbox mark --runtime jit-gent
        kg op sandbox mark --timeout 30

    "Sandbox mode treats file execution like a hypothesis—test it in
    isolation before committing to reality."
    """
    if not args:
        print("Usage: kg op sandbox <path> [--runtime native|jit-gent|wasm] [--timeout MINUTES]")
        print("Example: kg op sandbox WITNESS_OPERAD/mark")
        return 1

    # Parse args
    path_arg = args[0]
    runtime = SandboxRuntime.NATIVE
    timeout_minutes = 15

    i = 1
    while i < len(args):
        if args[i] == "--runtime" and i + 1 < len(args):
            try:
                runtime = SandboxRuntime(args[i + 1])
            except ValueError:
                print(f"Invalid runtime: {args[i + 1]}. Use: native, jit-gent, wasm")
                return 1
            i += 2
        elif args[i] == "--timeout" and i + 1 < len(args):
            try:
                timeout_minutes = int(args[i + 1])
            except ValueError:
                print(f"Invalid timeout: {args[i + 1]}")
                return 1
            i += 2
        else:
            i += 1

    path = resolve_op_path(path_arg)
    if path is None:
        print(f"Error: Operation not found: {path_arg}")
        return 1

    console = _get_console()
    content = path.read_text()

    # Create sandbox
    config = SandboxConfig(
        timeout_seconds=timeout_minutes * 60,
        runtime=runtime,
    )

    store = get_sandbox_store()
    sandbox = store.create(str(path), content, config)

    _print_header("\U0001f4e6 Sandbox Created")

    if console:
        console.print(f"  [bold]ID:[/bold] {sandbox.id}")
        console.print(f"  [bold]Source:[/bold] {sandbox.source_path}")
        console.print(f"  [bold]Runtime:[/bold] {sandbox.config.runtime.value}")
        remaining = sandbox.time_remaining
        mins = int(remaining.total_seconds() // 60)
        console.print(f"  [bold]Expires:[/bold] {mins} minutes remaining")
        console.print()
        console.print("[dim]Commands:[/dim]")
        console.print("  kg op sandboxes          List active sandboxes")
        console.print(f"  kg op promote {sandbox.id}  Promote to production")
        console.print(f"  kg op discard {sandbox.id}  Discard sandbox")
        console.print(f"  kg op extend {sandbox.id}   Extend timeout")
    else:
        print(f"  ID: {sandbox.id}")
        print(f"  Source: {sandbox.source_path}")
        print(f"  Runtime: {sandbox.config.runtime.value}")
        remaining = sandbox.time_remaining
        mins = int(remaining.total_seconds() // 60)
        print(f"  Expires: {mins} minutes remaining")
        print()
        print("Commands:")
        print("  kg op sandboxes          List active sandboxes")
        print(f"  kg op promote {sandbox.id}  Promote to production")
        print(f"  kg op discard {sandbox.id}  Discard sandbox")
        print(f"  kg op extend {sandbox.id}   Extend timeout")

    print()
    return 0


def cmd_sandboxes(args: list[str]) -> int:
    """
    List sandboxes.

    Usage:
        kg op sandboxes          List active sandboxes
        kg op sandboxes --all    Include expired/promoted/discarded
    """
    show_all = "--all" in args

    console = _get_console()
    store = get_sandbox_store()

    if show_all:
        sandboxes = store.list_all()
        _print_header("\U0001f4e6 All Sandboxes")
    else:
        sandboxes = store.list_active()
        _print_header("\U0001f4e6 Active Sandboxes")

    if not sandboxes:
        if console:
            console.print("[dim]No sandboxes found.[/dim]")
            console.print("[dim]Create one with: kg op sandbox <path>[/dim]")
        else:
            print("No sandboxes found.")
            print("Create one with: kg op sandbox <path>")
        print()
        return 0

    for sb in sandboxes:
        # Format time remaining
        remaining = sb.time_remaining
        mins = int(remaining.total_seconds() // 60)
        time_str = f"{mins}m remaining" if sb.is_active else "expired"

        # Extract short source path
        source = sb.source_path
        if "/" in source:
            parts = source.split("/")
            source = "/".join(parts[-2:]) if len(parts) >= 2 else parts[-1]

        # Phase indicator
        phase_colors = {
            SandboxPhase.ACTIVE: "green",
            SandboxPhase.PROMOTED: "blue",
            SandboxPhase.DISCARDED: "dim",
            SandboxPhase.EXPIRED: "yellow",
        }
        phase_color = phase_colors.get(sb.phase, "white")

        if console:
            console.print(
                f"  [{phase_color}]{sb.phase.name:10}[/] "
                f"[bold]{sb.id}[/bold]  {source}  "
                f"[dim]{time_str}[/dim]  "
                f"[cyan]{sb.config.runtime.value}[/cyan]"
            )
        else:
            print(f"  {sb.phase.name:10} {sb.id}  {source}  {time_str}  {sb.config.runtime.value}")

    print()
    if console:
        console.print(f"[dim]Total: {len(sandboxes)} sandboxes[/dim]")
    else:
        print(f"Total: {len(sandboxes)} sandboxes")

    print()
    return 0


def cmd_discard(args: list[str]) -> int:
    """
    Discard a sandbox without promotion.

    Usage:
        kg op discard <sandbox_id>
    """
    if not args:
        print("Usage: kg op discard <sandbox_id>")
        print("Example: kg op discard sandbox-abc123")
        return 1

    sandbox_id = SandboxId(args[0])
    console = _get_console()
    store = get_sandbox_store()

    try:
        discarded = store.discard(sandbox_id)

        if console:
            console.print(f"[green]\u2713[/green] Discarded sandbox: {sandbox_id}")
            console.print(f"  [dim]Source: {discarded.source_path}[/dim]")
        else:
            print(f"\u2713 Discarded sandbox: {sandbox_id}")
            print(f"  Source: {discarded.source_path}")

        print()
        return 0

    except KeyError:
        print(f"Error: Sandbox not found: {sandbox_id}")
        return 1
    except InvalidTransitionError as e:
        print(f"Error: {e}")
        return 1


def cmd_extend(args: list[str]) -> int:
    """
    Extend a sandbox's timeout.

    Usage:
        kg op extend <sandbox_id>
        kg op extend <sandbox_id> --minutes 30
    """
    if not args:
        print("Usage: kg op extend <sandbox_id> [--minutes N]")
        print("Example: kg op extend sandbox-abc123 --minutes 30")
        return 1

    sandbox_id = SandboxId(args[0])
    minutes = 15

    i = 1
    while i < len(args):
        if args[i] == "--minutes" and i + 1 < len(args):
            try:
                minutes = int(args[i + 1])
            except ValueError:
                print(f"Invalid minutes: {args[i + 1]}")
                return 1
            i += 2
        else:
            i += 1

    console = _get_console()
    store = get_sandbox_store()

    try:
        extended = store.extend(sandbox_id, minutes)
        remaining = extended.time_remaining
        total_mins = int(remaining.total_seconds() // 60)

        if console:
            console.print(f"[green]\u2713[/green] Extended sandbox: {sandbox_id}")
            console.print(f"  [bold]New timeout:[/bold] {total_mins} minutes remaining")
        else:
            print(f"\u2713 Extended sandbox: {sandbox_id}")
            print(f"  New timeout: {total_mins} minutes remaining")

        print()
        return 0

    except KeyError:
        print(f"Error: Sandbox not found: {sandbox_id}")
        return 1
    except InvalidTransitionError as e:
        print(f"Error: {e}")
        return 1


def cmd_promote(args: list[str]) -> int:
    """
    Promote a sandbox to production.

    Usage:
        kg op promote <sandbox_id>
        kg op promote <sandbox_id> --to WITNESS_OPERAD/mark_v2
        kg op promote <sandbox_id> --preview

    Shows diff preview before promotion.
    """
    if not args:
        print("Usage: kg op promote <sandbox_id> [--to destination] [--preview]")
        print("Example: kg op promote sandbox-abc123")
        return 1

    sandbox_id = SandboxId(args[0])
    destination = None
    preview_only = False

    i = 1
    while i < len(args):
        if args[i] == "--to" and i + 1 < len(args):
            destination = args[i + 1]
            i += 2
        elif args[i] == "--preview":
            preview_only = True
            i += 1
        else:
            i += 1

    console = _get_console()
    store = get_sandbox_store()

    # Get sandbox
    sandbox = store.get(sandbox_id)
    if sandbox is None:
        print(f"Error: Sandbox not found: {sandbox_id}")
        return 1

    if sandbox.phase != SandboxPhase.ACTIVE:
        print(f"Error: Sandbox is not active (phase: {sandbox.phase.name})")
        return 1

    # Show diff preview
    _print_header(f"\U0001f50d Promotion Preview: {sandbox_id}")

    if sandbox.has_modifications:
        diff = sandbox.get_diff()
        if console:
            console.print("[bold]Changes:[/bold]")
            for line in diff.splitlines():
                if line.startswith("+") and not line.startswith("+++"):
                    console.print(f"[green]{line}[/green]")
                elif line.startswith("-") and not line.startswith("---"):
                    console.print(f"[red]{line}[/red]")
                elif line.startswith("@@"):
                    console.print(f"[cyan]{line}[/cyan]")
                else:
                    console.print(line)
        else:
            print("Changes:")
            print(diff)
    else:
        if console:
            console.print("[dim]No modifications made in sandbox.[/dim]")
        else:
            print("No modifications made in sandbox.")

    print()

    if preview_only:
        if console:
            console.print("[dim]Preview only. Use without --preview to promote.[/dim]")
        else:
            print("Preview only. Use without --preview to promote.")
        return 0

    # Determine destination
    dest = destination or sandbox.source_path
    if console:
        console.print(f"[bold]Destination:[/bold] {dest}")
    else:
        print(f"Destination: {dest}")

    # Promote
    try:
        promoted = store.promote(sandbox_id, dest)

        # Write content to destination if it's a file path
        dest_path = Path(dest)
        if dest_path.exists() or dest_path.parent.exists():
            dest_path.write_text(sandbox.content)
            if console:
                console.print(f"[green]\u2713[/green] Wrote content to {dest}")
            else:
                print(f"\u2713 Wrote content to {dest}")

        if console:
            console.print(f"[green]\u2713[/green] Promoted sandbox: {sandbox_id}")
            console.print(f"  [bold]Promoted to:[/bold] {promoted.promoted_to}")
        else:
            print(f"\u2713 Promoted sandbox: {sandbox_id}")
            print(f"  Promoted to: {promoted.promoted_to}")

        print()
        return 0

    except InvalidTransitionError as e:
        print(f"Error: {e}")
        return 1


# =============================================================================
# Law Commands (Session 6a)
# =============================================================================


def cmd_laws(args: list[str]) -> int:
    """
    List laws for an operad.

    Usage:
        kg op laws                    List all operads with law counts
        kg op laws FILE_OPERAD        List laws in FILE_OPERAD
        kg op laws FILE_OPERAD --show Show law details

    "The proof IS the decision. The mark IS the witness."
    """
    console = _get_console()

    if not args:
        # List all operads with law counts
        _print_header("⚖️  Operad Laws")

        if not OPERADS_ROOT.exists():
            print(f"No operads found at {OPERADS_ROOT}")
            return 0

        for operad_dir in sorted(OPERADS_ROOT.iterdir()):
            if operad_dir.is_dir() and not operad_dir.name.startswith("_"):
                laws_dir = operad_dir / "_laws"
                if laws_dir.exists():
                    law_files = list(laws_dir.glob("*.law"))
                    if law_files:
                        # Count verified vs unverified
                        verified = 0
                        failed = 0
                        for law_file in law_files:
                            try:
                                parsed_law = parse_law_file(law_file)
                                if parsed_law.status == LawStatus.VERIFIED:
                                    verified += 1
                                elif parsed_law.status == LawStatus.FAILED:
                                    failed += 1
                            except Exception:
                                pass

                        total = len(law_files)
                        status_str = (
                            f"✅ {verified}" if verified == total else f"✅ {verified}/{total}"
                        )
                        if failed > 0:
                            status_str += f" ❌ {failed}"

                        if console:
                            console.print(
                                f"  [bold]{operad_dir.name}[/bold]  "
                                f"[dim]{total} laws[/dim]  {status_str}"
                            )
                        else:
                            print(f"  {operad_dir.name}  {total} laws  {status_str}")
                else:
                    if console:
                        console.print(f"  [dim]{operad_dir.name}  (no laws)[/dim]")
                    else:
                        print(f"  {operad_dir.name}  (no laws)")

        print()
        return 0

    # Parse args
    operad_name = args[0]
    show_details = "--show" in args or "-s" in args

    operad_dir = OPERADS_ROOT / operad_name
    if not operad_dir.exists():
        print(f"Error: Operad not found: {operad_name}")
        print("\nAvailable operads:")
        cmd_laws([])
        return 1

    laws = list_laws_in_operad(operad_dir)

    if not laws:
        _print_header(f"⚖️  {operad_name} Laws")
        if console:
            console.print("[dim]No laws defined for this operad.[/dim]")
            console.print("[dim]Laws are defined in _laws/*.law files.[/dim]")
        else:
            print("No laws defined for this operad.")
            print("Laws are defined in _laws/*.law files.")
        print()
        return 0

    _print_header(f"⚖️  {operad_name} Laws ({len(laws)})")

    for law in laws:
        # Status indicator
        status_emoji = law.status_emoji

        # Operations list
        ops_str = ", ".join(law.operations) if law.operations else ""

        if show_details:
            # Full details
            if console:
                console.print(f"\n  {status_emoji} [bold]{law.name}[/bold]")
                if law.description:
                    console.print(f'     [dim]"{law.description}"[/dim]')
                console.print(f"     [cyan]Category:[/cyan] {law.category}")
                console.print(f"     [cyan]Equation:[/cyan] {law.equation}")
                if ops_str:
                    console.print(f"     [cyan]Operations:[/cyan] {ops_str}")
                if law.last_verified:
                    console.print(
                        f"     [dim]Last verified: {law.last_verified.strftime('%Y-%m-%d')} "
                        f"by {law.verified_by}[/dim]"
                    )
            else:
                print(f"\n  {status_emoji} {law.name}")
                if law.description:
                    print(f'     "{law.description}"')
                print(f"     Category: {law.category}")
                print(f"     Equation: {law.equation}")
                if ops_str:
                    print(f"     Operations: {ops_str}")
                if law.last_verified:
                    print(
                        f"     Last verified: {law.last_verified.strftime('%Y-%m-%d')} "
                        f"by {law.verified_by}"
                    )
        else:
            # Summary line
            if console:
                console.print(
                    f"  {status_emoji} [bold]{law.name}[/bold]  "
                    f"[dim]{law.category}[/dim]  "
                    f"[cyan]{law.equation}[/cyan]"
                )
            else:
                print(f"  {status_emoji} {law.name}  {law.category}  {law.equation}")

    print()

    # Summary
    verified_count = sum(1 for l in laws if l.status == LawStatus.VERIFIED)
    if console:
        console.print(f"[dim]Verified: {verified_count}/{len(laws)}[/dim]")
    else:
        print(f"Verified: {verified_count}/{len(laws)}")

    print()
    return 0


# =============================================================================
# ASHC Bridge Commands (Session 6b)
# =============================================================================


def cmd_verify(args: list[str]) -> int:
    """
    Verify laws in an operad.

    Usage:
        kg op verify FILE_OPERAD          Verify all laws
        kg op verify FILE_OPERAD/create_read_identity  Verify specific law
        kg op verify --all                Verify all laws in all operads

    "The proof IS the decision. The mark IS the witness."
    """
    console = _get_console()
    verifier = LawVerifier()

    if not args:
        print("Usage: kg op verify <operad> [--all]")
        print("Example: kg op verify FILE_OPERAD")
        print("         kg op verify FILE_OPERAD/create_read_identity")
        print("         kg op verify --all")
        return 1

    verify_all = "--all" in args
    args = [a for a in args if a != "--all"]

    # Collect laws to verify
    laws_to_verify: list[LawDefinition] = []

    if verify_all:
        # Verify all laws in all operads
        _print_header("\u2696\ufe0f  Verifying All Laws")

        if not OPERADS_ROOT.exists():
            print(f"No operads found at {OPERADS_ROOT}")
            return 1

        for operad_dir in sorted(OPERADS_ROOT.iterdir()):
            if operad_dir.is_dir() and not operad_dir.name.startswith("_"):
                laws = list_laws_in_operad(operad_dir)
                for law in laws:
                    laws_to_verify.append(law)

    elif "/" in args[0]:
        # Specific law: OPERAD/law_name
        parts = args[0].split("/", 1)
        operad_name = parts[0]
        law_name = parts[1]

        operad_dir = OPERADS_ROOT / operad_name
        if not operad_dir.exists():
            print(f"Error: Operad not found: {operad_name}")
            return 1

        law_path = operad_dir / "_laws" / f"{law_name}.law"
        if not law_path.exists():
            print(f"Error: Law not found: {args[0]}")
            return 1

        _print_header(f"\u2696\ufe0f  Verifying: {law_name}")
        law = parse_law_file(law_path)
        laws_to_verify.append(law)

    else:
        # Operad name: verify all laws in that operad
        operad_name = args[0]
        operad_dir = OPERADS_ROOT / operad_name

        if not operad_dir.exists():
            print(f"Error: Operad not found: {operad_name}")
            return 1

        _print_header(f"\u2696\ufe0f  Verifying: {operad_name}")
        laws_to_verify = list_laws_in_operad(operad_dir)

    if not laws_to_verify:
        if console:
            console.print("[dim]No laws found to verify.[/dim]")
        else:
            print("No laws found to verify.")
        return 0

    # Run verification
    results = verifier.verify_many(laws_to_verify)

    # Display results
    passed = 0
    failed = 0
    errored = 0
    skipped = 0

    for result in results:
        status_emoji = {
            VerificationResult.PASSED: "\u2705",
            VerificationResult.FAILED: "\u274c",
            VerificationResult.ERROR: "\u26a0\ufe0f ",
            VerificationResult.SKIPPED: "\u23f8",
        }[result.result]

        status_color = {
            VerificationResult.PASSED: "green",
            VerificationResult.FAILED: "red",
            VerificationResult.ERROR: "yellow",
            VerificationResult.SKIPPED: "dim",
        }[result.result]

        # Count results
        if result.result == VerificationResult.PASSED:
            passed += 1
        elif result.result == VerificationResult.FAILED:
            failed += 1
        elif result.result == VerificationResult.ERROR:
            errored += 1
        else:
            skipped += 1

        # Display
        if console:
            console.print(
                f"  {status_emoji} [{status_color}]{result.law.name}[/]  "
                f"[dim]{result.duration_ms:.1f}ms[/dim]"
            )
            if result.error:
                console.print(f"     [red]Error: {result.error}[/red]")
            if result.output and result.result == VerificationResult.PASSED:
                console.print(f"     [dim]{result.output}[/dim]")
        else:
            print(f"  {status_emoji} {result.law.name}  {result.duration_ms:.1f}ms")
            if result.error:
                print(f"     Error: {result.error}")

    # Summary
    print()
    total = len(results)
    if console:
        console.print(
            f"[bold]Results:[/bold] "
            f"[green]{passed} passed[/green], "
            f"[red]{failed} failed[/red], "
            f"[yellow]{errored} errors[/yellow], "
            f"[dim]{skipped} skipped[/dim] "
            f"/ {total} total"
        )
    else:
        print(
            f"Results: {passed} passed, {failed} failed, {errored} errors, {skipped} skipped / {total} total"
        )

    print()
    return 0 if (failed == 0 and errored == 0) else 1


def cmd_prove(args: list[str]) -> int:
    """
    Generate proof obligations from laws.

    Usage:
        kg op prove FILE_OPERAD          Generate obligations for all laws
        kg op prove FILE_OPERAD --unverified  Only unverified/failed laws
        kg op prove FILE_OPERAD/law_name      Specific law

    This compiles LawDefinitions into ProofObligations for the ASHC
    proof search system.

    "The proof IS the decision. The mark IS the witness."
    """
    console = _get_console()
    compiler = LawProofCompiler()

    if not args:
        print("Usage: kg op prove <operad> [--unverified]")
        print("Example: kg op prove FILE_OPERAD")
        print("         kg op prove FILE_OPERAD --unverified")
        print("         kg op prove FILE_OPERAD/create_read_identity")
        return 1

    only_unverified = "--unverified" in args
    args = [a for a in args if a != "--unverified"]

    # Collect laws
    laws: list[LawDefinition] = []

    if "/" in args[0]:
        # Specific law
        parts = args[0].split("/", 1)
        operad_name = parts[0]
        law_name = parts[1]

        operad_dir = OPERADS_ROOT / operad_name
        if not operad_dir.exists():
            print(f"Error: Operad not found: {operad_name}")
            return 1

        law_path = operad_dir / "_laws" / f"{law_name}.law"
        if not law_path.exists():
            print(f"Error: Law not found: {args[0]}")
            return 1

        law = parse_law_file(law_path)
        laws.append(law)
        _print_header(f"\U0001f4dc Proof Obligation: {law_name}")

    else:
        # Operad name
        operad_name = args[0]
        operad_dir = OPERADS_ROOT / operad_name

        if not operad_dir.exists():
            print(f"Error: Operad not found: {operad_name}")
            return 1

        laws = list_laws_in_operad(operad_dir)
        _print_header(f"\U0001f4dc Proof Obligations: {operad_name}")

    if not laws:
        if console:
            console.print("[dim]No laws found.[/dim]")
        else:
            print("No laws found.")
        return 0

    # Compile to proof obligations
    if only_unverified:
        obligations = compiler.compile_unverified(laws)
        if console:
            console.print(f"[dim]Compiling {len(obligations)} unverified/failed laws...[/dim]\n")
        else:
            print(f"Compiling {len(obligations)} unverified/failed laws...\n")
    else:
        obligations = compiler.compile_many(laws)
        if console:
            console.print(f"[dim]Compiling {len(obligations)} laws...[/dim]\n")
        else:
            print(f"Compiling {len(obligations)} laws...\n")

    if not obligations:
        if console:
            console.print(
                "[green]\u2713[/green] All laws are verified. No proof obligations needed."
            )
        else:
            print("\u2713 All laws are verified. No proof obligations needed.")
        return 0

    # Display obligations
    for obl in obligations:
        if console:
            console.print(f"  [bold]\U0001f4cb {obl.law_name}[/bold]")
            console.print(f"     [cyan]Property:[/cyan] {obl.property}")
            console.print(f"     [cyan]Category:[/cyan] {obl.category}")
            if obl.operations:
                console.print(f"     [cyan]Operations:[/cyan] {', '.join(obl.operations)}")
            console.print(f"     [dim]ID: {obl.id}[/dim]")
            if obl.context:
                console.print(f"     [dim]Context: {len(obl.context)} hints[/dim]")
            print()
        else:
            print(f"  \U0001f4cb {obl.law_name}")
            print(f"     Property: {obl.property}")
            print(f"     Category: {obl.category}")
            if obl.operations:
                print(f"     Operations: {', '.join(obl.operations)}")
            print(f"     ID: {obl.id}")
            print()

    # Summary
    if console:
        console.print(f"[bold]Generated:[/bold] {len(obligations)} proof obligation(s)")
        console.print("[dim]These can be fed to the ASHC proof search system.[/dim]")
    else:
        print(f"Generated: {len(obligations)} proof obligation(s)")
        print("These can be fed to the ASHC proof search system.")

    print()
    return 0


def cmd_evidence(args: list[str]) -> int:
    """
    Show ASHC evidence from FILE_OPERAD operations.

    Usage:
        kg op evidence              Show recent trace evidence
        kg op evidence --sandbox    Show sandbox evidence
        kg op evidence --limit 50   Limit to N items

    "Every expansion leaves a mark. Every mark is evidence."
    """
    from .ashc_bridge import (
        FileTraceToEvidenceAdapter,
        SandboxToEvidenceAdapter,
    )

    console = _get_console()

    # Parse args
    show_sandbox = "--sandbox" in args
    limit = 20

    for i, arg in enumerate(args):
        if arg == "--limit" and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass

    _print_header("\U0001f4d1 ASHC Evidence")

    if show_sandbox:
        # Sandbox evidence
        sandbox_adapter = SandboxToEvidenceAdapter()
        sandbox_store = get_sandbox_store()
        sandboxes = sandbox_store.list_all()[:limit]

        if not sandboxes:
            if console:
                console.print("[dim]No sandboxes found.[/dim]")
            else:
                print("No sandboxes found.")
            return 0

        for sb in sandboxes:
            evidence = sandbox_adapter.convert(sb)

            if console:
                success_emoji = "\u2705" if evidence.success else "\u274c"
                console.print(
                    f"  {success_emoji} [bold]{evidence.action}[/bold]  "
                    f"{evidence.target}  "
                    f"[dim]{evidence.timestamp.strftime('%H:%M:%S')}[/dim]"
                )
                if evidence.error:
                    console.print(f"     [red]{evidence.error}[/red]")
            else:
                success_char = "\u2713" if evidence.success else "\u2717"
                print(f"  {success_char} {evidence.action}  {evidence.target}")

    else:
        # Trace evidence
        trace_adapter = FileTraceToEvidenceAdapter()
        trace_store = get_file_trace_store()
        traces = trace_store.recent(limit)

        if not traces:
            if console:
                console.print(
                    "[dim]No traces found. Use 'kg op tree' or 'kg op expand' to explore.[/dim]"
                )
            else:
                print("No traces found. Use 'kg op tree' or 'kg op expand' to explore.")
            return 0

        evidence_list = trace_adapter.convert_many(traces)

        for evidence in evidence_list:
            if console:
                console.print(
                    f"  \U0001f50d [bold]{evidence.action}[/bold]  "
                    f"{evidence.target}  "
                    f"[dim]{evidence.timestamp.strftime('%H:%M:%S')}[/dim]"
                )
                if evidence.context:
                    console.print(f"     [dim]{' | '.join(evidence.context[:3])}[/dim]")
            else:
                print(f"  {evidence.action}  {evidence.target}")

    print()
    if console:
        console.print("[dim]Evidence can be fed to ASHC proof search.[/dim]")
    else:
        print("Evidence can be fed to ASHC proof search.")

    print()
    return 0


# =============================================================================
# WASM Execution Commands (Session 7)
# =============================================================================


def cmd_run(args: list[str]) -> int:
    """
    Execute sandbox content with isolation.

    Usage:
        kg op run <sandbox_id>              Execute existing sandbox
        kg op run <sandbox_id> --runtime wasm  Force WASM runtime
        kg op run --code "print('hello')"  Execute inline code

    "CHAOTIC reality agents MUST run sandboxed before being trusted."
    """
    import asyncio

    from .wasm_executor import IsolationLevel, execute_sandbox

    console = _get_console()

    if not args:
        print("Usage: kg op run <sandbox_id> [--runtime native|jit-gent|wasm]")
        print("       kg op run --code \"print('hello')\" [--runtime wasm]")
        return 1

    # Parse args
    sandbox_id = None
    inline_code = None
    runtime_override = None

    i = 0
    while i < len(args):
        if args[i] == "--code" and i + 1 < len(args):
            inline_code = args[i + 1]
            i += 2
        elif args[i] == "--runtime" and i + 1 < len(args):
            try:
                runtime_override = SandboxRuntime(args[i + 1])
            except ValueError:
                print(f"Invalid runtime: {args[i + 1]}. Use: native, jit-gent, wasm")
                return 1
            i += 2
        elif not sandbox_id and not args[i].startswith("--"):
            sandbox_id = args[i]
            i += 1
        else:
            i += 1

    store = get_sandbox_store()

    # Determine what to execute
    if inline_code:
        # Create temporary sandbox for inline code
        config = SandboxConfig(
            timeout_seconds=30,
            runtime=runtime_override or SandboxRuntime.JIT_GENT,
        )
        sandbox = store.create("inline", inline_code, config)
        _print_header(f"\U0001f680 Executing Inline Code ({sandbox.config.runtime.value})")
    elif sandbox_id:
        # Get existing sandbox
        found_sandbox = store.get(SandboxId(sandbox_id))
        if found_sandbox is None:
            print(f"Error: Sandbox not found: {sandbox_id}")
            return 1
        sandbox = found_sandbox

        # Override runtime if specified
        if runtime_override:
            from dataclasses import replace

            new_config = SandboxConfig(
                timeout_seconds=sandbox.config.timeout_seconds,
                runtime=runtime_override,
                allowed_imports=sandbox.config.allowed_imports,
            )
            sandbox = replace(sandbox, config=new_config)
            store.update(sandbox)

        _print_header(f"\U0001f680 Executing: {sandbox.id} ({sandbox.config.runtime.value})")
    else:
        print("Error: Must provide sandbox_id or --code")
        return 1

    # Execute
    try:
        result = asyncio.run(execute_sandbox(sandbox))

        # Update sandbox with result
        from .sandbox import SandboxEvent, transition_sandbox

        updated = transition_sandbox(sandbox, SandboxEvent.EXECUTE, result=result)
        store.update(updated)

        # Display result
        if result.success:
            if console:
                console.print("[green]\u2713 Execution succeeded[/green]")
            else:
                print("\u2713 Execution succeeded")
        else:
            if console:
                console.print("[red]\u2717 Execution failed[/red]")
            else:
                print("\u2717 Execution failed")

        # Show output
        if result.stdout:
            print()
            if console:
                console.print("[bold]Output:[/bold]")
                console.print(result.stdout)
            else:
                print("Output:")
                print(result.stdout)

        # Show error if any
        if result.error:
            print()
            if console:
                console.print(f"[red]Error: {result.error}[/red]")
            else:
                print(f"Error: {result.error}")

        # Show metrics
        print()
        if console:
            console.print(f"[dim]Execution time: {result.execution_time_ms:.1f}ms[/dim]")
        else:
            print(f"Execution time: {result.execution_time_ms:.1f}ms")

        print()
        return 0 if result.success else 1

    except Exception as e:
        if console:
            console.print(f"[red]Execution error: {type(e).__name__}: {e}[/red]")
        else:
            print(f"Execution error: {type(e).__name__}: {e}")
        return 1


def cmd_analyze(args: list[str]) -> int:
    """
    Analyze code for sandbox safety.

    Usage:
        kg op analyze <sandbox_id>      Analyze sandbox content
        kg op analyze --code "..."      Analyze inline code
        kg op analyze --file <path>     Analyze file content

    Returns safety analysis without executing.
    """
    from .wasm_executor import CodeAnalyzer, ExecutorConfig

    console = _get_console()

    if not args:
        print("Usage: kg op analyze <sandbox_id>")
        print('       kg op analyze --code "import os"')
        print("       kg op analyze --file path/to/file.py")
        return 1

    # Parse args
    code = None
    sandbox_id = None

    i = 0
    while i < len(args):
        if args[i] == "--code" and i + 1 < len(args):
            code = args[i + 1]
            i += 2
        elif args[i] == "--file" and i + 1 < len(args):
            file_path = Path(args[i + 1])
            if not file_path.exists():
                print(f"Error: File not found: {args[i + 1]}")
                return 1
            code = file_path.read_text()
            i += 2
        elif not sandbox_id and not args[i].startswith("--"):
            sandbox_id = args[i]
            i += 1
        else:
            i += 1

    # Get code to analyze
    if sandbox_id:
        store = get_sandbox_store()
        sandbox = store.get(SandboxId(sandbox_id))
        if sandbox is None:
            print(f"Error: Sandbox not found: {sandbox_id}")
            return 1
        code = sandbox.content

    if not code:
        print("Error: No code to analyze")
        return 1

    _print_header("\U0001f50d Code Safety Analysis")

    analyzer = CodeAnalyzer()
    is_safe, warnings = analyzer.analyze(code)

    # Display result
    if is_safe:
        if console:
            console.print("[green]\u2713 Code appears safe for sandbox execution[/green]")
        else:
            print("\u2713 Code appears safe for sandbox execution")
    else:
        if console:
            console.print("[red]\u2717 Code has safety issues[/red]")
        else:
            print("\u2717 Code has safety issues")

    # Show warnings
    if warnings:
        print()
        if console:
            console.print("[bold]Warnings:[/bold]")
            for warning in warnings:
                emoji = "\u26a0\ufe0f " if "Blocked" in warning else "\U0001f4dd"
                console.print(f"  {emoji} {warning}")
        else:
            print("Warnings:")
            for warning in warnings:
                print(f"  - {warning}")

    # Show code preview
    print()
    if console:
        console.print("[dim]Code preview (first 500 chars):[/dim]")
        console.print(f"[dim]{code[:500]}{'...' if len(code) > 500 else ''}[/dim]")
    else:
        print("Code preview (first 500 chars):")
        print(f"{code[:500]}{'...' if len(code) > 500 else ''}")

    print()
    return 0 if is_safe else 1


# =============================================================================
# Main Entry Point
# =============================================================================


def cmd_op(args: list[str]) -> int:
    """
    FILE_OPERAD CLI: Navigate operads as documents.

    "Navigation is expansion. Expansion is navigation."
    """
    if not args or "--help" in args or "-h" in args:
        _print_help()
        return 0

    subcommand = args[0].lower()
    sub_args = args[1:]

    handlers = {
        "show": cmd_show,
        "s": cmd_show,  # alias
        "cat": cmd_show,  # alias
        "expand": cmd_expand,
        "x": cmd_expand,  # alias
        "list": cmd_list,
        "ls": cmd_list,  # alias
        "portals": cmd_portals,
        "p": cmd_portals,  # alias
        "links": cmd_portals,  # alias
        "tree": cmd_tree,
        "t": cmd_tree,  # alias
        "trail": cmd_trail,
        "history": cmd_trail,  # alias
        # Sandbox commands (Session 5)
        "sandbox": cmd_sandbox,
        "sb": cmd_sandbox,  # alias
        "sandboxes": cmd_sandboxes,
        "promote": cmd_promote,
        "discard": cmd_discard,
        "extend": cmd_extend,
        # Law commands (Session 6a)
        "laws": cmd_laws,
        "law": cmd_laws,  # alias
        # ASHC bridge commands (Session 6b)
        "verify": cmd_verify,
        "v": cmd_verify,  # alias
        "prove": cmd_prove,
        "evidence": cmd_evidence,
        # WASM execution commands (Session 7)
        "run": cmd_run,
        "r": cmd_run,  # alias
        "exec": cmd_run,  # alias
        "analyze": cmd_analyze,
        "a": cmd_analyze,  # alias
    }

    handler = handlers.get(subcommand)
    if handler:
        return handler(sub_args)

    # If first arg looks like a path, default to show
    if "/" in subcommand or subcommand.endswith(".op"):
        return cmd_show(args)

    print(f"Unknown subcommand: {subcommand}")
    _print_help()
    return 1


def _print_help() -> None:
    """Print help text."""
    help_text = """
kg op - FILE_OPERAD: Navigate Operads as Documents

"Navigation is expansion. Expansion is navigation."

NAVIGATION COMMANDS:
  kg op show <path>      Show an operation with syntax highlighting
  kg op expand <path>    Expand all portal links inline
  kg op list [operad]    List operads or operations
  kg op portals <path>   List portal links (without expanding)
  kg op tree <path>      Show portal expansion tree
  kg op trail            Show exploration trail (recorded traces)

SANDBOX COMMANDS (Session 5):
  kg op sandbox <path>   Create isolated sandbox from operation
  kg op sandboxes        List active sandboxes
  kg op promote <id>     Promote sandbox to production
  kg op discard <id>     Discard sandbox without promotion
  kg op extend <id>      Extend sandbox timeout

LAW COMMANDS (Session 6a):
  kg op laws             List all operads with law counts
  kg op laws <operad>    List laws in specific operad
  kg op laws <op> --show Show law details (equation, category, verification)

ASHC BRIDGE COMMANDS (Session 6b):
  kg op verify <operad>  Run law verification tests
  kg op verify --all     Verify all laws in all operads
  kg op prove <operad>   Generate proof obligations from laws
  kg op prove <op> --unverified  Only generate for unverified laws
  kg op evidence         Show ASHC evidence from exploration traces
  kg op evidence --sandbox  Show sandbox-derived evidence

WASM EXECUTION COMMANDS (Session 7):
  kg op run <sandbox_id>         Execute sandbox with isolation
  kg op run --code "..."         Execute inline code
  kg op run <id> --runtime wasm  Force WASM runtime
  kg op analyze <sandbox_id>     Analyze code for sandbox safety
  kg op analyze --code "..."     Analyze inline code
  kg op analyze --file <path>    Analyze file content

OPTIONS:
  --depth N              Maximum expansion depth (default: 3)
  --limit N              Number of traces to show (default: 20)
  --path X               Filter traces by path
  --persist, -p          Load/save traces from persistence file
  --save                 Save current traces to persistence
  --runtime X            Sandbox runtime: native, jit-gent, wasm (default: native)
  --timeout N            Sandbox timeout in minutes (default: 15)
  --to <dest>            Promotion destination path
  --preview              Preview diff without promoting
  --show, -s             Show detailed law information
  --all                  Verify all laws in all operads
  --unverified           Only process unverified/failed laws

PATH FORMATS:
  OPERAD_NAME/operation  e.g., WITNESS_OPERAD/mark
  operation              Searches all operads for match
  /full/path/to/file.op  Absolute path

EXAMPLES:
  kg op list                          List all operads
  kg op show WITNESS_OPERAD/mark      Show the mark operation
  kg op tree mark --depth 2           Show portal tree
  kg op trail --persist               Load history from previous sessions

  # Sandbox workflow
  kg op sandbox WITNESS_OPERAD/mark   Create sandbox
  kg op sandboxes                     List active sandboxes
  kg op promote sandbox-abc123        Promote to production
  kg op discard sandbox-abc123        Discard sandbox

  # Law verification (Session 6a)
  kg op laws                          List operads with law counts
  kg op laws FILE_OPERAD              List FILE_OPERAD laws
  kg op laws FILE_OPERAD --show       Show detailed law info

  # ASHC bridge (Session 6b)
  kg op verify FILE_OPERAD            Run verification tests
  kg op prove FILE_OPERAD --unverified  Generate proof obligations
  kg op evidence                      Show exploration evidence

  # WASM execution (Session 7)
  kg op run --code "print('hello')"   Execute inline code
  kg op run sandbox-abc123            Execute existing sandbox
  kg op run sandbox-abc123 --runtime wasm  Force WASM isolation
  kg op analyze --code "import os"    Check code safety

ALIASES:
  show: s, cat
  expand: x
  list: ls
  portals: p, links
  tree: t
  trail: history
  sandbox: sb
  laws: law
  verify: v
  run: r, exec
  analyze: a

PHILOSOPHY:
  "The proof IS the decision. The mark IS the witness."

See: spec/protocols/file-operad.md
"""
    print(help_text.strip())


__all__ = ["cmd_op"]
