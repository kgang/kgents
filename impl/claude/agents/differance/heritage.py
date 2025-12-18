"""
GhostHeritageDAG: The visual graph of what was chosen and what almost was.

This module implements the heritage DAG — a navigable representation of
trace history that includes both the chosen path and ghost alternatives.

The heritage DAG is the "UI innovation": seeing what almost was alongside what is.

Core Types:
    HeritageNode: A node in the heritage graph (chosen, ghost, or deferred)
    HeritageEdge: An edge linking nodes (produced, ghosted, deferred, concretized)
    GhostHeritageDAG: The full DAG with query methods

Builder Functions:
    build_heritage_dag: Build DAG from TraceMonoid
    build_heritage_dag_from_traces: Convenience wrapper

See: spec/protocols/differance.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Mapping, Sequence

from .trace import Alternative, TraceMonoid, WiringTrace

# =============================================================================
# Type Aliases
# =============================================================================

NodeType = Literal["chosen", "ghost", "deferred", "spec", "impl"]
EdgeType = Literal["produced", "ghosted", "deferred", "concretized"]


# =============================================================================
# HeritageNode
# =============================================================================


@dataclass(frozen=True)
class HeritageNode:
    """
    A node in the ghost heritage graph.

    HeritageNodes represent either:
    - A chosen trace (actual wiring decision that was executed)
    - A ghost (alternative that was considered but not taken)
    - A deferred ghost (explorable alternative for future)

    Attributes:
        id: Unique identifier (trace_id for chosen, generated for ghosts)
        node_type: Classification of this node
        operation: The operation performed or considered
        timestamp: When this decision was made/considered
        depth: Distance from root in the DAG (0 = root)
        output: The result (for chosen nodes only)
        reason: Why this was rejected (for ghost nodes only)
        explorable: Whether this ghost can be explored later
        inputs: Inputs to the operation (for context)

    Example:
        >>> node = HeritageNode(
        ...     id="trace_abc123",
        ...     node_type="chosen",
        ...     operation="seq",
        ...     timestamp=datetime.now(timezone.utc),
        ...     depth=0,
        ...     output="BrainGardener",
        ... )
        >>> node.is_chosen()
        True
    """

    id: str
    node_type: NodeType
    operation: str
    timestamp: datetime
    depth: int
    output: Any | None = None
    reason: str | None = None
    explorable: bool = False
    inputs: tuple[str, ...] = ()

    def is_chosen(self) -> bool:
        """True if this is a chosen (executed) node."""
        return self.node_type == "chosen"

    def is_ghost(self) -> bool:
        """True if this is a ghost (rejected alternative)."""
        return self.node_type in ("ghost", "deferred")

    def can_explore(self) -> bool:
        """True if this ghost can be explored later."""
        return self.explorable and self.node_type in ("ghost", "deferred")


# =============================================================================
# HeritageEdge
# =============================================================================


@dataclass(frozen=True)
class HeritageEdge:
    """
    An edge in the ghost heritage graph.

    Edges represent relationships between nodes:
    - produced: One trace led to another (causal chain)
    - ghosted: A trace had this alternative but rejected it
    - deferred: Same as ghosted but explorable
    - concretized: A ghost that was later executed

    Attributes:
        source: Source node ID
        target: Target node ID
        edge_type: Classification of this edge

    Example:
        >>> edge = HeritageEdge(
        ...     source="trace_abc",
        ...     target="trace_xyz",
        ...     edge_type="produced",
        ... )
        >>> edge.is_causal()
        True
    """

    source: str
    target: str
    edge_type: EdgeType

    def is_causal(self) -> bool:
        """True if this represents a causal relationship."""
        return self.edge_type in ("produced", "concretized")

    def is_ghost_edge(self) -> bool:
        """True if this points to a ghost node."""
        return self.edge_type in ("ghosted", "deferred")


# =============================================================================
# GhostHeritageDAG
# =============================================================================


@dataclass(frozen=True)
class GhostHeritageDAG:
    """
    The full heritage graph including ghosts.

    This is the central data structure for heritage visualization.
    It contains:
    - All nodes (chosen traces and ghost alternatives)
    - All edges (causal links and ghost links)
    - A root node (the starting point for traversal)

    Laws:
    - Every node except root has at least one incoming edge
    - No cycles (it's a DAG)
    - chosen_path forms a single linear chain from root
    - Ghost nodes only appear as targets, never sources

    Example:
        >>> dag = build_heritage_dag(monoid, "output_xyz")
        >>> dag.chosen_path()
        ('trace_1', 'trace_2', 'trace_3')
        >>> dag.ghost_paths()
        (('trace_1', 'trace_1_ghost_0'), ('trace_2', 'trace_2_ghost_0'))
        >>> dag.at_depth(2)
        (HeritageNode(...), HeritageNode(...))
    """

    nodes: Mapping[str, HeritageNode]
    edges: tuple[HeritageEdge, ...]
    root_id: str

    @property
    def node_count(self) -> int:
        """Number of nodes in the DAG."""
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        """Number of edges in the DAG."""
        return len(self.edges)

    @property
    def max_depth(self) -> int:
        """Maximum depth in the DAG."""
        if not self.nodes:
            return 0
        return max(n.depth for n in self.nodes.values())

    def chosen_path(self) -> Sequence[str]:
        """
        Return the sequence of chosen node IDs from root to leaf.

        This is the "golden path" — the actual decisions that were made.

        Returns:
            Tuple of node IDs in order from root to final output
        """
        result: list[str] = []
        current_id: str | None = self.root_id

        while current_id is not None:
            node = self.nodes.get(current_id)
            if node is None or not node.is_chosen():
                break
            result.append(current_id)

            # Find the next chosen node (produced edge)
            next_id: str | None = None
            for edge in self.edges:
                if edge.source == current_id and edge.edge_type == "produced":
                    next_id = edge.target
                    break
            current_id = next_id

        return tuple(result)

    def ghost_paths(self) -> Sequence[Sequence[str]]:
        """
        Return all ghost paths (alternative branches not taken).

        Each ghost path is a tuple (parent_chosen_id, ghost_id),
        representing the branch point and the ghost.

        Returns:
            Tuple of ghost path tuples
        """
        paths: list[tuple[str, str]] = []

        for node_id, node in self.nodes.items():
            if node.is_ghost():
                # Find the parent chosen node
                for edge in self.edges:
                    if edge.target == node_id and edge.is_ghost_edge():
                        paths.append((edge.source, node_id))
                        break

        return tuple(paths)

    def at_depth(self, depth: int) -> Sequence[HeritageNode]:
        """
        Return all nodes at the specified depth.

        Useful for level-by-level visualization or "show me step N".

        Args:
            depth: The depth to query (0 = root)

        Returns:
            All nodes at that depth (both chosen and ghosts)
        """
        return tuple(node for node in self.nodes.values() if node.depth == depth)

    def ghosts_of(self, node_id: str) -> Sequence[HeritageNode]:
        """
        Return all ghost nodes that are alternatives to the given node.

        Args:
            node_id: ID of a chosen node

        Returns:
            Ghost nodes that branch off from this node
        """
        ghost_ids = [
            edge.target for edge in self.edges if edge.source == node_id and edge.is_ghost_edge()
        ]
        return tuple(self.nodes[gid] for gid in ghost_ids if gid in self.nodes)

    def explorable_ghosts(self) -> Sequence[HeritageNode]:
        """Return all ghosts that can be explored."""
        return tuple(node for node in self.nodes.values() if node.can_explore())

    def get_node(self, node_id: str) -> HeritageNode | None:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def parent_of(self, node_id: str) -> HeritageNode | None:
        """Get the parent node (if any)."""
        for edge in self.edges:
            if edge.target == node_id:
                return self.nodes.get(edge.source)
        return None

    def children_of(self, node_id: str) -> Sequence[HeritageNode]:
        """Get all child nodes (both chosen and ghost)."""
        child_ids = [edge.target for edge in self.edges if edge.source == node_id]
        return tuple(self.nodes[cid] for cid in child_ids if cid in self.nodes)

    def verify_integrity(self) -> tuple[bool, str]:
        """
        Verify DAG integrity.

        Checks:
        1. All edge targets exist as nodes
        2. All edge sources exist as nodes
        3. Root node exists (if root_id is set)
        4. No cycles

        Returns:
            Tuple of (is_valid, message)
        """
        # Check empty DAG
        if not self.root_id and not self.nodes:
            return (True, "Empty DAG is valid")

        # Check root exists
        if self.root_id and self.root_id not in self.nodes:
            return (False, f"Root {self.root_id} not in nodes")

        # Check all edge endpoints exist
        for edge in self.edges:
            if edge.source not in self.nodes:
                return (False, f"Edge source {edge.source} not in nodes")
            if edge.target not in self.nodes:
                return (False, f"Edge target {edge.target} not in nodes")

        # Check for cycles (DFS from each node)
        for start_id in self.nodes:
            visited: set[str] = set()
            stack = [start_id]

            while stack:
                current = stack.pop()
                if current in visited:
                    return (False, f"Cycle detected involving {current}")
                visited.add(current)

                # Add children to stack
                for edge in self.edges:
                    if edge.source == current:
                        if edge.target in visited:
                            # Only a cycle if we can get back to start
                            if edge.target == start_id:
                                return (
                                    False,
                                    f"Cycle: {start_id} -> ... -> {current} -> {edge.target}",
                                )
                        else:
                            stack.append(edge.target)

        return (True, "DAG is well-formed")

    def __repr__(self) -> str:
        chosen_count = sum(1 for n in self.nodes.values() if n.is_chosen())
        ghost_count = sum(1 for n in self.nodes.values() if n.is_ghost())
        return (
            f"GhostHeritageDAG(chosen={chosen_count}, ghosts={ghost_count}, depth={self.max_depth})"
        )


# =============================================================================
# Builder Functions
# =============================================================================


def build_heritage_dag(
    monoid: TraceMonoid,
    target_id: str | None = None,
    max_depth: int = 10,
) -> GhostHeritageDAG:
    """
    Build a GhostHeritageDAG from a TraceMonoid.

    This is the primary builder function. It:
    1. Finds the target trace (or uses the most recent)
    2. Walks the causal chain to find the chosen path
    3. Extracts ghost alternatives at each step
    4. Assigns depth via BFS from root

    Args:
        monoid: The TraceMonoid containing trace history
        target_id: Target trace to build DAG for (default: most recent)
        max_depth: Maximum depth to traverse (default: 10)

    Returns:
        GhostHeritageDAG representing the heritage

    Example:
        >>> monoid = TraceMonoid((trace1, trace2, trace3))
        >>> dag = build_heritage_dag(monoid)
        >>> dag.chosen_path()
        ('trace_1', 'trace_2', 'trace_3')
    """
    if not monoid:
        return GhostHeritageDAG(nodes={}, edges=(), root_id="")

    # Find target trace
    if target_id is None:
        # Use most recent trace
        target_trace = monoid.traces[-1] if monoid.traces else None
        if target_trace is None:
            return GhostHeritageDAG(nodes={}, edges=(), root_id="")
        target_id = target_trace.trace_id

    # Get causal chain (oldest -> newest)
    chain = monoid.causal_chain(target_id)
    if not chain:
        return GhostHeritageDAG(nodes={}, edges=(), root_id="")

    # Build nodes and edges
    nodes: dict[str, HeritageNode] = {}
    edges: list[HeritageEdge] = []
    root_id = chain[0].trace_id

    # Build DAG from causal chain
    for depth, trace in enumerate(chain):
        if depth >= max_depth:
            break

        # Add chosen node
        nodes[trace.trace_id] = HeritageNode(
            id=trace.trace_id,
            node_type="chosen",
            operation=trace.operation,
            timestamp=trace.timestamp,
            depth=depth,
            output=trace.output,
            reason=None,
            explorable=False,
            inputs=trace.inputs,
        )

        # Add produced edge (except for root)
        if depth > 0:
            parent_trace = chain[depth - 1]
            edges.append(
                HeritageEdge(
                    source=parent_trace.trace_id,
                    target=trace.trace_id,
                    edge_type="produced",
                )
            )

        # Add ghost nodes from alternatives
        for i, alt in enumerate(trace.alternatives):
            ghost_id = f"{trace.trace_id}_ghost_{i}"

            ghost_type: NodeType = "deferred" if alt.could_revisit else "ghost"
            edge_type: EdgeType = "deferred" if alt.could_revisit else "ghosted"

            nodes[ghost_id] = HeritageNode(
                id=ghost_id,
                node_type=ghost_type,
                operation=alt.operation,
                timestamp=trace.timestamp,
                depth=depth,
                output=None,
                reason=alt.reason_rejected,
                explorable=alt.could_revisit,
                inputs=alt.inputs,
            )

            edges.append(
                HeritageEdge(
                    source=trace.trace_id,
                    target=ghost_id,
                    edge_type=edge_type,
                )
            )

    return GhostHeritageDAG(
        nodes=nodes,
        edges=tuple(edges),
        root_id=root_id,
    )


def build_heritage_dag_from_traces(
    traces: Sequence[WiringTrace],
    target_id: str | None = None,
    max_depth: int = 10,
) -> GhostHeritageDAG:
    """
    Convenience function to build DAG from a sequence of traces.

    Args:
        traces: Sequence of WiringTrace objects
        target_id: Target trace ID (default: most recent)
        max_depth: Maximum depth to traverse

    Returns:
        GhostHeritageDAG
    """
    monoid = TraceMonoid(traces=tuple(traces))
    return build_heritage_dag(monoid, target_id, max_depth)


__all__ = [
    # Type aliases
    "NodeType",
    "EdgeType",
    # Types
    "HeritageNode",
    "HeritageEdge",
    "GhostHeritageDAG",
    # Builders
    "build_heritage_dag",
    "build_heritage_dag_from_traces",
]
