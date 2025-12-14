"""
Trace Handler: Unified static + runtime tracing for Python code.

Part of the kgents trace architecture. Provides call graph analysis,
runtime tracing, and ASCII visualization.

Usage:
    kgents trace <target>              # Static call graph (default)
    kgents trace --runtime <command>   # Runtime trace execution
    kgents trace --help                # Show help

Modes:
    (default)    Static call graph analysis via AST
    --runtime    Trace actual execution via sys.settrace
    --hybrid     Static + runtime correlation (future)

Visualization:
    --tree       Hierarchical tree (default)
    --graph      Node-edge call graph
    --timeline   Temporal execution view
    --flame      Flame graph

Example:
    kgents trace FluxAgent.start
    kgents trace --runtime "soul challenge 'test'"
    kgents trace --flame agents/k
"""

from __future__ import annotations

import asyncio
import json as json_module
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for trace command."""
    print(__doc__)
    print()
    print("MODES:")
    print("  (default)         Static call graph analysis")
    print("  --runtime         Trace actual execution")
    print("  --hybrid          Static + runtime correlation (future)")
    print()
    print("VISUALIZATION:")
    print("  --tree            Hierarchical tree (default)")
    print("  --graph           Node-edge call graph")
    print("  --timeline        Temporal execution view")
    print("  --flame           Flame graph")
    print("  --diff FILE       Compare with saved trace")
    print()
    print("OPTIONS:")
    print("  --depth N         Traversal depth (default: 5)")
    print("  --show-ghosts     Include dynamic/inferred calls")
    print("  --lens AGENT      View from agent's perspective")
    print("  --callees         Trace what target calls (vs who calls it)")
    print("  --export FILE     Save trace (JSON or DOT)")
    print("  --path DIR        Base path for analysis (default: impl/claude)")
    print("  --json            Output as JSON")
    print("  --help, -h        Show this help")


def cmd_trace(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Main entry point for the trace command.

    Args:
        args: Command-line arguments (after the command name)
        ctx: Optional InvocationContext for dual-channel output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("trace", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args
    runtime_mode = "--runtime" in args
    hybrid_mode = "--hybrid" in args
    show_ghosts = "--show-ghosts" in args
    callees_mode = "--callees" in args

    # Parse visualization mode
    viz_mode = "tree"  # default
    if "--graph" in args:
        viz_mode = "graph"
    elif "--timeline" in args:
        viz_mode = "timeline"
    elif "--flame" in args:
        viz_mode = "flame"

    # Parse depth
    depth = 5
    for i, arg in enumerate(args):
        if arg == "--depth" and i + 1 < len(args):
            try:
                depth = int(args[i + 1])
            except ValueError:
                pass

    # Parse lens
    lens: str | None = None
    for i, arg in enumerate(args):
        if arg == "--lens" and i + 1 < len(args):
            lens = args[i + 1]

    # Parse export path
    export_path: str | None = None
    for i, arg in enumerate(args):
        if arg == "--export" and i + 1 < len(args):
            export_path = args[i + 1]

    # Parse diff file
    diff_file: str | None = None
    for i, arg in enumerate(args):
        if arg == "--diff" and i + 1 < len(args):
            diff_file = args[i + 1]

    # Parse base path
    base_path = "impl/claude"
    for i, arg in enumerate(args):
        if arg == "--path" and i + 1 < len(args):
            base_path = args[i + 1]

    # Get target (first non-flag argument)
    target: str | None = None
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg in ("--depth", "--lens", "--export", "--diff", "--path"):
            skip_next = True
            continue
        if arg.startswith("-"):
            continue
        target = arg
        break

    # Run async handler
    return asyncio.run(
        _async_trace(
            target=target,
            runtime_mode=runtime_mode,
            hybrid_mode=hybrid_mode,
            viz_mode=viz_mode,
            depth=depth,
            show_ghosts=show_ghosts,
            callees_mode=callees_mode,
            lens=lens,
            export_path=export_path,
            diff_file=diff_file,
            base_path=base_path,
            json_mode=json_mode,
            ctx=ctx,
        )
    )


async def _async_trace(
    target: str | None,
    runtime_mode: bool,
    hybrid_mode: bool,
    viz_mode: str,
    depth: int,
    show_ghosts: bool,
    callees_mode: bool,
    lens: str | None,
    export_path: str | None,
    diff_file: str | None,
    base_path: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of trace command."""
    try:
        # Lazy imports to keep CLI fast
        from weave.runtime_trace import TraceCollector, TraceFilter
        from weave.static_trace import StaticCallGraph
        from weave.trace_renderer import (
            RenderConfig,
            TraceRenderer,
            render_diff,
            render_graph,
            render_trace,
        )

        if target is None and not runtime_mode:
            _emit_output(
                "[TRACE] Error: No target specified\n"
                "Usage: kgents trace <target> [options]\n"
                "       kgents trace --help",
                {"error": "No target specified"},
                ctx,
            )
            return 1

        # Configure renderer
        config = RenderConfig(
            width=100,
            show_ghosts=show_ghosts,
            truncate_names=50,
        )
        renderer = TraceRenderer(config)

        # Handle diff mode
        if diff_file:
            return await _handle_diff(diff_file, target, json_mode, renderer, ctx)

        # Handle runtime mode
        if runtime_mode:
            return await _handle_runtime(
                target or "",
                viz_mode,
                lens,
                export_path,
                json_mode,
                renderer,
                ctx,
            )

        # Handle static mode (default)
        return await _handle_static(
            target or "",
            viz_mode,
            depth,
            show_ghosts,
            callees_mode,
            export_path,
            base_path,
            json_mode,
            renderer,
            ctx,
        )

    except ImportError as e:
        _emit_output(
            f"[TRACE] X Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[TRACE] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


async def _handle_static(
    target: str,
    viz_mode: str,
    depth: int,
    show_ghosts: bool,
    callees_mode: bool,
    export_path: str | None,
    base_path: str,
    json_mode: bool,
    renderer: Any,
    ctx: "InvocationContext | None",
) -> int:
    """Handle static call graph analysis."""
    from weave.static_trace import StaticCallGraph

    _emit_output(
        f"[TRACE] Analyzing: {target} (depth={depth})",
        {"status": "analyzing", "target": target, "depth": depth},
        ctx,
    )

    # Create and run static analyzer
    graph = StaticCallGraph(base_path)
    graph.analyze("**/*.py")

    _emit_output(
        f"[TRACE] Analyzed {graph.num_files} files, {graph.num_definitions} definitions",
        {
            "files": graph.num_files,
            "definitions": graph.num_definitions,
            "calls": graph.num_calls,
        },
        ctx,
    )

    # Trace callers or callees
    if callees_mode:
        dep_graph = graph.trace_callees(target, depth=depth)
        direction = "callees"
    else:
        dep_graph = graph.trace_callers(target, depth=depth)
        direction = "callers"

    if len(dep_graph) == 0:
        _emit_output(
            f"[TRACE] No {direction} found for: {target}",
            {"status": "empty", "target": target, "direction": direction},
            ctx,
        )
        return 0

    # Get ghost calls if requested
    ghost_nodes: set[str] = set()
    if show_ghosts:
        ghost_calls = graph.get_ghost_calls(target)
        ghost_nodes = {gc.callee for gc in ghost_calls}

    # Render visualization
    layout = "tree" if viz_mode == "tree" else "force"
    output = renderer.render_call_graph(
        dep_graph,
        layout=layout,
        ghost_nodes=ghost_nodes,
    )

    # Build result
    result = {
        "target": target,
        "direction": direction,
        "depth": depth,
        "nodes": len(dep_graph),
        "ghosts": len(ghost_nodes),
        "visualization": output,
    }

    # Export if requested
    if export_path:
        await _export_trace(export_path, result, dep_graph, ctx)

    if json_mode:
        _emit_output(json_module.dumps(result, indent=2), result, ctx)
    else:
        _emit_output(
            f"\n[TRACE] {direction.title()} of {target}:\n",
            {"header": True},
            ctx,
        )
        _emit_output(output, result, ctx)
        _emit_output(
            f"\n[TRACE] {len(dep_graph)} nodes"
            + (f", {len(ghost_nodes)} ghosts" if ghost_nodes else ""),
            {"footer": True},
            ctx,
        )

    return 0


async def _handle_runtime(
    target: str,
    viz_mode: str,
    lens: str | None,
    export_path: str | None,
    json_mode: bool,
    renderer: Any,
    ctx: "InvocationContext | None",
) -> int:
    """Handle runtime tracing."""
    from weave.runtime_trace import TraceCollector, TraceFilter

    _emit_output(
        f"[TRACE] Runtime tracing: {target}",
        {"status": "tracing", "target": target},
        ctx,
    )

    # Create collector with filter
    filter_config = TraceFilter(
        include_patterns=["**/impl/claude/**"],
        exclude_patterns=[
            "**/site-packages/**",
            "**/.venv/**",
            "**/lib/python*/**",
            "**/_tests/**",
        ],
        max_depth=50,
    )

    collector = TraceCollector(filter_config=filter_config, enable_otel=False)

    # Execute the target
    try:
        with collector.trace():
            # If target looks like a command, execute it
            if target.startswith("soul ") or " " in target:
                # Import and execute as CLI command
                parts = target.split()
                cmd = parts[0]
                cmd_args = parts[1:] if len(parts) > 1 else []

                try:
                    from protocols.cli.hollow import resolve_command

                    handler = resolve_command(cmd)
                    if handler:
                        handler(cmd_args)
                    else:
                        _emit_output(
                            f"[TRACE] Unknown command: {cmd}",
                            {"error": f"Unknown command: {cmd}"},
                            ctx,
                        )
                        return 1
                except Exception as e:
                    _emit_output(
                        f"[TRACE] Command error: {e}",
                        {"error": str(e)},
                        ctx,
                    )
            else:
                # Try to import and call as a function
                if "." in target:
                    module_path, func_name = target.rsplit(".", 1)
                    try:
                        import importlib

                        module = importlib.import_module(module_path)
                        func = getattr(module, func_name, None)
                        if callable(func):
                            result = func()
                            if asyncio.iscoroutine(result):
                                await result
                    except Exception as e:
                        _emit_output(
                            f"[TRACE] Import error: {e}",
                            {"error": str(e)},
                            ctx,
                        )

    except Exception as e:
        _emit_output(
            f"[TRACE] Execution error: {e}",
            {"error": str(e)},
            ctx,
        )

    # Get the trace
    monoid = collector.monoid
    event_count = len(monoid)

    if event_count == 0:
        _emit_output(
            "[TRACE] No events captured (check filter settings)",
            {"status": "empty"},
            ctx,
        )
        return 0

    _emit_output(
        f"[TRACE] Captured {event_count} events",
        {"events": event_count},
        ctx,
    )

    # Render based on visualization mode
    if viz_mode == "timeline":
        output = renderer.render_timeline(monoid, lens=lens)
    elif viz_mode == "flame":
        output = renderer.render_flame(monoid)
    elif viz_mode == "tree":
        output = renderer.render_tree_from_monoid(monoid)
    else:
        output = renderer.render_timeline(monoid, lens=lens)

    # Build result
    result = {
        "target": target,
        "events": event_count,
        "visualization": output,
        "thread_summary": collector.get_thread_summary(),
    }

    # Export if requested
    if export_path:
        await _export_runtime_trace(export_path, result, monoid, ctx)

    if json_mode:
        _emit_output(json_module.dumps(result, indent=2), result, ctx)
    else:
        _emit_output(f"\n{output}", result, ctx)

    return 0


async def _handle_diff(
    diff_file: str,
    target: str | None,
    json_mode: bool,
    renderer: Any,
    ctx: "InvocationContext | None",
) -> int:
    """Handle trace diff comparison."""
    from weave.event import Event
    from weave.trace_monoid import TraceMonoid

    _emit_output(
        f"[TRACE] Comparing with: {diff_file}",
        {"status": "diffing", "file": diff_file},
        ctx,
    )

    # Load the saved trace
    try:
        with open(diff_file, "r") as f:
            saved_data = json_module.load(f)
    except FileNotFoundError:
        _emit_output(
            f"[TRACE] File not found: {diff_file}",
            {"error": f"File not found: {diff_file}"},
            ctx,
        )
        return 1
    except json_module.JSONDecodeError as e:
        _emit_output(
            f"[TRACE] Invalid JSON: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1

    # Reconstruct TraceMonoid from saved data
    before: TraceMonoid[dict[str, object]] = TraceMonoid()
    for event_data in saved_data.get("events", []):
        event = Event.create(
            content=event_data.get("content", {}),
            source=event_data.get("source", "unknown"),
            event_id=event_data.get("id"),
        )
        before.append_mut(event)

    # If target specified, note that comparison is not yet supported
    if target:
        _emit_output(
            f"[TRACE] Note: Comparison with '{target}' not yet supported. Showing saved trace only.",
            {"warning": "comparison_not_implemented"},
            ctx,
        )

    # Display the loaded trace
    output = renderer.render_tree_from_monoid(before)

    result = {
        "file": diff_file,
        "events": len(before),
        "visualization": output,
    }

    if json_mode:
        _emit_output(json_module.dumps(result, indent=2), result, ctx)
    else:
        _emit_output(f"\n[TRACE] Loaded trace from {diff_file}:\n", {}, ctx)
        _emit_output(output, result, ctx)

    return 0


async def _export_trace(
    export_path: str,
    result: dict[str, Any],
    dep_graph: Any,
    ctx: "InvocationContext | None",
) -> None:
    """Export static trace to file."""
    path = Path(export_path)

    if path.suffix == ".dot":
        # Export as DOT format for Graphviz
        dot_content = _to_dot(dep_graph, result.get("target", "unknown"))
        path.write_text(dot_content)
    else:
        # Export as JSON
        export_data = {
            "type": "static",
            "target": result.get("target"),
            "direction": result.get("direction"),
            "depth": result.get("depth"),
            "nodes": list(dep_graph.nodes()),
            "edges": [
                {"from": node, "to": list(dep_graph.get_dependencies(node))}
                for node in dep_graph.nodes()
            ],
        }
        path.write_text(json_module.dumps(export_data, indent=2))

    _emit_output(
        f"[TRACE] Exported to: {export_path}",
        {"exported": export_path},
        ctx,
    )


async def _export_runtime_trace(
    export_path: str,
    result: dict[str, Any],
    monoid: Any,
    ctx: "InvocationContext | None",
) -> None:
    """Export runtime trace to file."""
    path = Path(export_path)

    # Export as JSON
    export_data = {
        "type": "runtime",
        "target": result.get("target"),
        "events": [
            {
                "id": event.id,
                "source": event.source,
                "timestamp": event.timestamp,
                "content": event.content,
            }
            for event in monoid.events
        ],
        "thread_summary": result.get("thread_summary"),
    }
    path.write_text(json_module.dumps(export_data, indent=2))

    _emit_output(
        f"[TRACE] Exported to: {export_path}",
        {"exported": export_path},
        ctx,
    )


def _to_dot(dep_graph: Any, target: str) -> str:
    """Convert DependencyGraph to DOT format."""
    lines = [
        "digraph trace {",
        "  rankdir=TB;",
        "  node [shape=box, style=rounded];",
        f'  "{target}" [style="rounded,filled", fillcolor=lightblue];',
    ]

    for node in dep_graph.nodes():
        deps = dep_graph.get_dependencies(node)
        for dep in deps:
            lines.append(f'  "{node}" -> "{dep}";')

    lines.append("}")
    return "\n".join(lines)


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """
    Emit output via dual-channel if ctx available, else print.

    This is the key integration point with the Reflector Protocol:
    - Human output goes to stdout (for humans)
    - Semantic output goes to FD3 (for agents consuming our output)
    """
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
