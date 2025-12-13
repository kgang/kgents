"""
TraceRenderer - ASCII Visualization for Traces.

Part of the kgents trace architecture (Phase 3). Renders DependencyGraphs and
TraceMonoids as ASCII art for terminal display.

Visualization modes:
  - Call Graph: Node-edge diagram using GraphLayout patterns
  - Timeline: Temporal view showing concurrency (threads side-by-side)
  - Flame Graph: Horizontal bars proportional to call depth
  - Diff: Compare two traces showing additions/removals

Ghost calls (dynamic dispatch) are shown with distinct styling to highlight
uncertainty in static analysis.

Usage:
    renderer = TraceRenderer()

    # Render static call graph
    graph = static_call_graph.trace_callers("MyFunc", depth=5)
    print(renderer.render_call_graph(graph))

    # Render runtime trace as timeline
    with collector.trace():
        my_function()
    print(renderer.render_timeline(collector.monoid))

    # Render as flame graph
    print(renderer.render_flame(collector.monoid))

    # Compare traces
    print(renderer.render_diff(before_trace, after_trace))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .dependency import DependencyGraph
from .trace_monoid import TraceMonoid

# Box-drawing characters for ASCII art
CHARS = {
    "h_line": "─",
    "v_line": "│",
    "top_left": "┌",
    "top_right": "┐",
    "bot_left": "└",
    "bot_right": "┘",
    "branch_start": "├",
    "branch_end": "└",
    "cross": "┼",
    "t_right": "├",
    "t_left": "┤",
    "t_down": "┬",
    "t_up": "┴",
    # Node markers
    "solid": "●",
    "ghost": "○",
    "arrow_right": "►",
    "arrow_down": "▼",
    # Diff markers
    "added": "+",
    "removed": "-",
    "unchanged": " ",
    # Flame graph
    "flame_char": "█",
    "flame_ghost": "░",
}


@dataclass
class RenderConfig:
    """Configuration for trace rendering.

    Attributes:
        width: Maximum width of output (characters)
        show_ghosts: Show ghost/dynamic calls
        show_timestamps: Include timestamps in output
        show_files: Include file paths
        truncate_names: Max length for function names (0 = no truncate)
        use_color: Use ANSI color codes
    """

    width: int = 80
    show_ghosts: bool = True
    show_timestamps: bool = False
    show_files: bool = False
    truncate_names: int = 40
    use_color: bool = False


class TraceRenderer:
    """Renders traces as ASCII art.

    Supports multiple visualization modes:
    - Call graph: Node-edge diagram for static analysis
    - Timeline: Concurrent events shown side-by-side
    - Flame graph: Horizontal bars showing call depth
    - Diff: Comparison between two traces

    Example:
        renderer = TraceRenderer()
        output = renderer.render_call_graph(dependency_graph)
        print(output)
    """

    def __init__(self, config: RenderConfig | None = None) -> None:
        """Initialize renderer with configuration.

        Args:
            config: Rendering configuration (uses defaults if None)
        """
        self.config = config or RenderConfig()

    def render_call_graph(
        self,
        graph: DependencyGraph,
        layout: str = "tree",
        root: str | None = None,
        ghost_nodes: set[str] | None = None,
    ) -> str:
        """Render a call graph as ASCII tree or force-directed layout.

        Uses patterns from GraphLayout widget for node-edge rendering.

        Args:
            graph: The DependencyGraph to render
            layout: Layout algorithm ("tree", "force", "semantic")
            root: Root node for tree layout (auto-detected if None)
            ghost_nodes: Set of node IDs to render as ghosts

        Returns:
            ASCII representation of the call graph
        """
        if len(graph) == 0:
            return "Empty graph"

        ghost_nodes = ghost_nodes or set()

        if layout == "tree":
            return self._render_tree_layout(graph, root, ghost_nodes)
        elif layout == "force":
            return self._render_force_layout(graph, ghost_nodes)
        else:  # semantic - fall back to tree for now
            return self._render_tree_layout(graph, root, ghost_nodes)

    def _render_tree_layout(
        self,
        graph: DependencyGraph,
        root: str | None,
        ghost_nodes: set[str],
    ) -> str:
        """Render graph as hierarchical tree."""
        lines: list[str] = []

        # Find root(s) - nodes with no dependencies
        if root:
            roots = [root] if root in graph else []
        else:
            roots = list(graph.get_roots())

        if not roots:
            # If no roots, use all nodes
            roots = list(graph.nodes())

        # Build adjacency list (reverse direction: parent -> children)
        # In DependencyGraph, edges point from dependent to dependency
        # For tree display, we want parent -> children
        children: dict[str, list[str]] = {n: [] for n in graph.nodes()}
        for node in graph.nodes():
            for dep in graph.get_dependencies(node):
                if dep in children:
                    children[dep].append(node)

        # Render each root
        visited: set[str] = set()
        for i, root_node in enumerate(roots):
            is_last_root = i == len(roots) - 1
            self._render_node_tree(
                root_node, children, ghost_nodes, lines, "", is_last_root, visited
            )

        return "\n".join(lines) if lines else "No nodes to display"

    def _render_node_tree(
        self,
        node: str,
        children: dict[str, list[str]],
        ghost_nodes: set[str],
        lines: list[str],
        prefix: str,
        is_last: bool,
        visited: set[str],
    ) -> None:
        """Recursively render a node and its children."""
        if node in visited:
            # Circular reference marker
            connector = CHARS["branch_end"] if is_last else CHARS["branch_start"]
            lines.append(
                f"{prefix}{connector}{CHARS['h_line']}{CHARS['ghost']} {self._truncate(node)} (cycle)"
            )
            return

        visited.add(node)

        # Build the line
        connector = CHARS["branch_end"] if is_last else CHARS["branch_start"]
        is_ghost = node in ghost_nodes
        glyph = CHARS["ghost"] if is_ghost else CHARS["solid"]
        name = self._truncate(node)

        if is_ghost and self.config.show_ghosts:
            line = f"{prefix}{connector}{CHARS['h_line']}{glyph} [ghost] {name}"
        elif is_ghost:
            return  # Skip ghosts if not showing
        else:
            line = f"{prefix}{connector}{CHARS['h_line']}{glyph} {name}"

        lines.append(line)

        # Recurse into children
        child_prefix = prefix + ("  " if is_last else f"{CHARS['v_line']} ")
        node_children = children.get(node, [])

        for i, child in enumerate(node_children):
            self._render_node_tree(
                child,
                children,
                ghost_nodes,
                lines,
                child_prefix,
                i == len(node_children) - 1,
                visited.copy(),
            )

    def _render_force_layout(
        self,
        graph: DependencyGraph,
        ghost_nodes: set[str],
    ) -> str:
        """Render graph using force-directed 2D layout.

        This is a simplified ASCII version - for full 2D rendering,
        use the GraphLayout widget directly.
        """
        lines: list[str] = []
        nodes = list(graph.nodes())

        if not nodes:
            return "Empty graph"

        # Header
        lines.append(f"Call Graph ({len(nodes)} nodes)")
        lines.append(CHARS["h_line"] * min(self.config.width, 60))

        # List nodes with their connections
        for node in nodes:
            is_ghost = node in ghost_nodes
            glyph = CHARS["ghost"] if is_ghost else CHARS["solid"]
            name = self._truncate(node)

            deps = graph.get_dependencies(node)
            if deps:
                dep_str = ", ".join(self._truncate(d, 20) for d in deps)
                line = f"  {glyph} {name} {CHARS['arrow_right']} {dep_str}"
            else:
                line = f"  {glyph} {name}"

            if is_ghost:
                line += " [ghost]"

            lines.append(line)

        return "\n".join(lines)

    def render_timeline(
        self,
        monoid: TraceMonoid[dict[str, Any]],
        lens: str | None = None,
    ) -> str:
        """Render trace as timeline showing concurrency.

        Events from different threads are shown side-by-side.
        Dependencies are shown with vertical lines.

        Args:
            monoid: The TraceMonoid to render
            lens: Agent/source filter (only show events from this source)

        Returns:
            ASCII timeline representation
        """
        if len(monoid) == 0:
            return "Empty trace"

        lines: list[str] = []

        # Group events by source (thread/agent)
        events_by_source: dict[str, list[tuple[str, dict[str, Any], float]]] = {}
        for event in monoid.events:
            if lens and event.source != lens:
                continue
            source = event.source
            if source not in events_by_source:
                events_by_source[source] = []
            events_by_source[source].append((event.id, event.content, event.timestamp))

        if not events_by_source:
            return f"No events matching lens '{lens}'"

        sources = sorted(events_by_source.keys())
        num_sources = len(sources)

        # Calculate column width
        col_width = min(30, (self.config.width - 4) // num_sources)

        # Header
        header_parts = [f"{s[: col_width - 1]:^{col_width}}" for s in sources]
        lines.append(" ".join(header_parts))
        lines.append(CHARS["h_line"] * (col_width * num_sources + num_sources - 1))

        # Merge events by timestamp for interleaved display
        all_events: list[tuple[float, str, str, dict[str, Any]]] = []
        for source, events in events_by_source.items():
            for event_id, content, timestamp in events:
                all_events.append((timestamp, source, event_id, content))

        all_events.sort(key=lambda x: x[0])

        # Render each event row
        for timestamp, source, event_id, content in all_events:
            row_parts: list[str] = []
            source_idx = sources.index(source)

            for i, s in enumerate(sources):
                if i == source_idx:
                    # This source has the event
                    func_name = content.get("function", event_id)
                    event_type = content.get("type", "call")
                    depth = content.get("depth", 0)

                    # Indent by depth
                    indent = "  " * min(depth, 3)
                    truncated = self._truncate(func_name, col_width - len(indent) - 3)

                    if event_type == "exception":
                        cell = f"{indent}!{truncated}"
                    else:
                        cell = f"{indent}{CHARS['solid']}{truncated}"

                    row_parts.append(f"{cell:<{col_width}}")
                else:
                    # Empty column (show continuation line)
                    row_parts.append(f"{CHARS['v_line']:^{col_width}}")

            lines.append(" ".join(row_parts))

        # Footer with stats
        lines.append(CHARS["h_line"] * (col_width * num_sources + num_sources - 1))
        concurrent = self._count_concurrent_pairs(monoid)
        lines.append(f"Total: {len(monoid)} events, {concurrent} concurrent pairs")

        return "\n".join(lines)

    def render_flame(
        self,
        monoid: TraceMonoid[dict[str, Any]],
    ) -> str:
        """Render trace as flame graph.

        Horizontal bars show call depth. Wider bars indicate
        more time or more nested calls.

        Args:
            monoid: The TraceMonoid to render

        Returns:
            ASCII flame graph representation
        """
        if len(monoid) == 0:
            return "Empty trace"

        lines: list[str] = []
        lines.append("Flame Graph")
        lines.append(CHARS["h_line"] * min(self.config.width, 60))

        # Build call stacks from events
        stacks: list[tuple[str, int, bool]] = []  # (function, depth, is_ghost)

        for event in monoid.events:
            content = event.content
            if not isinstance(content, dict):
                continue

            func_name = content.get("function", "unknown")
            depth = content.get("depth", 0)
            event_type = content.get("type", "call")

            if event_type == "call":
                is_ghost = content.get("is_dynamic", False)
                stacks.append((func_name, depth, is_ghost))

        if not stacks:
            return "No call events in trace"

        # Find max depth for scaling
        max_depth = max(d for _, d, _ in stacks) if stacks else 0
        bar_width = self.config.width - 10  # Leave room for depth indicator

        # Group by depth level
        by_depth: dict[int, list[tuple[str, bool]]] = {}
        for func, depth, is_ghost in stacks:
            if depth not in by_depth:
                by_depth[depth] = []
            by_depth[depth].append((func, is_ghost))

        # Render each depth level
        for depth in sorted(by_depth.keys()):
            functions = by_depth[depth]
            num_funcs = len(functions)

            # Bar length proportional to number of functions at this depth
            _ = max(1, min(bar_width, num_funcs * 3))  # Calculated for reference

            # Build the bar
            bar_parts: list[str] = []
            for func, is_ghost in functions[: bar_width // 3]:
                char = CHARS["flame_ghost"] if is_ghost else CHARS["flame_char"]
                bar_parts.append(char * 3)

            bar = "".join(bar_parts)[:bar_width]

            # Depth indicator
            depth_str = f"d{depth}"

            # Most common function at this depth
            func_counts: dict[str, int] = {}
            for func, _ in functions:
                func_counts[func] = func_counts.get(func, 0) + 1
            top_func = max(func_counts.keys(), key=lambda f: func_counts[f])
            top_func_truncated = self._truncate(top_func, 30)

            lines.append(f"{depth_str:>3} {bar} {top_func_truncated}")

        # Legend
        lines.append("")
        lines.append(
            f"Legend: {CHARS['flame_char']}=call  {CHARS['flame_ghost']}=ghost"
        )
        lines.append(f"Max depth: {max_depth}, Total calls: {len(stacks)}")

        return "\n".join(lines)

    def render_diff(
        self,
        before: TraceMonoid[dict[str, Any]],
        after: TraceMonoid[dict[str, Any]],
    ) -> str:
        """Render diff between two traces.

        Shows functions that were added, removed, or unchanged.
        Useful for comparing behavior across code changes.

        Args:
            before: The baseline trace
            after: The new trace

        Returns:
            ASCII diff representation
        """
        lines: list[str] = []
        lines.append("Trace Diff")
        lines.append(CHARS["h_line"] * min(self.config.width, 60))

        # Extract function sets
        before_funcs = self._extract_functions(before)
        after_funcs = self._extract_functions(after)

        # Compute diff
        added = after_funcs - before_funcs
        removed = before_funcs - after_funcs
        unchanged = before_funcs & after_funcs

        # Render removed
        if removed:
            lines.append("")
            lines.append("Removed:")
            for func in sorted(removed):
                lines.append(f"  {CHARS['removed']} {self._truncate(func)}")

        # Render added
        if added:
            lines.append("")
            lines.append("Added:")
            for func in sorted(added):
                lines.append(f"  {CHARS['added']} {self._truncate(func)}")

        # Render unchanged (summarized)
        if unchanged:
            lines.append("")
            lines.append(f"Unchanged: {len(unchanged)} functions")

        # Summary
        lines.append("")
        lines.append(CHARS["h_line"] * min(self.config.width, 60))
        lines.append(f"Before: {len(before)} events, After: {len(after)} events")
        lines.append(
            f"Added: {len(added)}, Removed: {len(removed)}, Unchanged: {len(unchanged)}"
        )

        return "\n".join(lines)

    def render_tree_from_monoid(
        self,
        monoid: TraceMonoid[dict[str, Any]],
        show_ghosts: bool = True,
    ) -> str:
        """Render a TraceMonoid as a call tree.

        Uses BranchTree-style rendering with ghost branches shown
        for potential dynamic dispatch paths.

        Args:
            monoid: The TraceMonoid to render
            show_ghosts: Whether to show ghost branches

        Returns:
            ASCII tree representation
        """
        if len(monoid) == 0:
            return "Empty trace"

        lines: list[str] = []

        # Build tree structure from events
        # Events with dependencies are children of their dependencies
        event_map: dict[str, dict[str, Any]] = {e.id: e.content for e in monoid.events}

        children: dict[str, list[str]] = {}
        roots: list[str] = []
        dep_graph = monoid.braid()

        for event in monoid.events:
            deps = dep_graph.get_dependencies(event.id)
            if deps:
                # Child of first dependency
                parent_id = next(iter(deps))
                if parent_id not in children:
                    children[parent_id] = []
                children[parent_id].append(event.id)
            else:
                roots.append(event.id)

        # Render tree
        for i, root_id in enumerate(roots):
            self._render_event_tree(
                root_id,
                event_map,
                children,
                lines,
                "",
                i == len(roots) - 1,
                show_ghosts,
            )

        return "\n".join(lines) if lines else "No events to display"

    def _render_event_tree(
        self,
        event_id: str,
        event_map: dict[str, dict[str, Any]],
        children: dict[str, list[str]],
        lines: list[str],
        prefix: str,
        is_last: bool,
        show_ghosts: bool,
    ) -> None:
        """Recursively render an event and its children."""
        content = event_map.get(event_id, {})
        func_name = content.get("function", event_id)
        event_type = content.get("type", "call")
        is_ghost = content.get("is_dynamic", False)

        if is_ghost and not show_ghosts:
            return

        connector = CHARS["branch_end"] if is_last else CHARS["branch_start"]
        glyph = CHARS["ghost"] if is_ghost else CHARS["solid"]

        if event_type == "exception":
            line = f"{prefix}{connector}{CHARS['h_line']}! {self._truncate(func_name)}"
        elif is_ghost:
            line = f"{prefix}{connector}{CHARS['h_line']}{glyph} [ghost] {self._truncate(func_name)}"
        else:
            line = f"{prefix}{connector}{CHARS['h_line']}{glyph} {self._truncate(func_name)}"

        lines.append(line)

        # Recurse
        child_prefix = prefix + ("  " if is_last else f"{CHARS['v_line']} ")
        event_children = children.get(event_id, [])

        for i, child_id in enumerate(event_children):
            self._render_event_tree(
                child_id,
                event_map,
                children,
                lines,
                child_prefix,
                i == len(event_children) - 1,
                show_ghosts,
            )

    def _truncate(self, name: str, max_len: int | None = None) -> str:
        """Truncate a name to max length."""
        limit = max_len or self.config.truncate_names
        if limit <= 0:
            return name
        if len(name) <= limit:
            return name
        return name[: limit - 3] + "..."

    def _count_concurrent_pairs(self, monoid: TraceMonoid[dict[str, Any]]) -> int:
        """Count pairs of concurrent events."""
        count = 0
        events = list(monoid.events)
        for i, e1 in enumerate(events):
            for e2 in events[i + 1 :]:
                if e1.source != e2.source:
                    if monoid.are_concurrent(e1.id, e2.id):
                        count += 1
        return count

    def _extract_functions(self, monoid: TraceMonoid[dict[str, Any]]) -> set[str]:
        """Extract unique function names from a trace."""
        funcs: set[str] = set()
        for event in monoid.events:
            content = event.content
            if isinstance(content, dict):
                func = content.get("function")
                if func:
                    funcs.add(func)
        return funcs


# Convenience functions


def render_graph(
    graph: DependencyGraph,
    layout: str = "tree",
    width: int = 80,
) -> str:
    """Render a DependencyGraph as ASCII art.

    Args:
        graph: The graph to render
        layout: Layout algorithm ("tree", "force")
        width: Maximum width

    Returns:
        ASCII representation
    """
    renderer = TraceRenderer(RenderConfig(width=width))
    return renderer.render_call_graph(graph, layout=layout)


def render_trace(
    monoid: TraceMonoid[dict[str, Any]],
    mode: str = "timeline",
    width: int = 80,
) -> str:
    """Render a TraceMonoid as ASCII art.

    Args:
        monoid: The trace to render
        mode: Render mode ("timeline", "flame", "tree")
        width: Maximum width

    Returns:
        ASCII representation
    """
    renderer = TraceRenderer(RenderConfig(width=width))

    if mode == "timeline":
        return renderer.render_timeline(monoid)
    elif mode == "flame":
        return renderer.render_flame(monoid)
    elif mode == "tree":
        return renderer.render_tree_from_monoid(monoid)
    else:
        return renderer.render_timeline(monoid)


def render_diff(
    before: TraceMonoid[dict[str, Any]],
    after: TraceMonoid[dict[str, Any]],
) -> str:
    """Render diff between two traces.

    Args:
        before: Baseline trace
        after: New trace

    Returns:
        ASCII diff representation
    """
    renderer = TraceRenderer()
    return renderer.render_diff(before, after)


__all__ = [
    "TraceRenderer",
    "RenderConfig",
    "render_graph",
    "render_trace",
    "render_diff",
    "CHARS",
]
