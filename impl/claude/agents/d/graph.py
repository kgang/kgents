"""
GraphAgent: Graph-based state storage with lattice operations.

Provides foundation for the Relational Lattice concept from noosphere.md.
Supports relationships, provenance tracking, and lattice operations (meet, join).
"""

import json
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, Set, TypeVar

from .errors import (
    NodeNotFoundError,
    StorageError,
)

N = TypeVar("N")  # Node type
E = TypeVar("E")  # Edge data type


class EdgeKind(Enum):
    """Standard relationship types."""

    IS_A = "is_a"  # Inheritance/subsumption
    HAS_A = "has_a"  # Composition
    USES = "uses"  # Dependency
    DERIVES_FROM = "derives_from"  # Provenance
    CONTRADICTS = "contradicts"  # Opposition (H-gent)
    SYNTHESIZES = "synthesizes"  # Sublation (H-gent)
    RELATED_TO = "related_to"  # Generic relationship


@dataclass
class Edge(Generic[N]):
    """A typed relationship between nodes."""

    source: str  # Source node ID
    kind: EdgeKind
    target: str  # Target node ID
    metadata: Dict[str, Any] = field(default_factory=dict)

    def reverse(self) -> "Edge[N]":
        """Create reversed edge."""
        return Edge(
            source=self.target,
            kind=self.kind,
            target=self.source,
            metadata=self.metadata,
        )


@dataclass
class GraphNode(Generic[N]):
    """A node in the graph with state and edges."""

    id: str
    state: N
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Subgraph(Generic[N]):
    """A subgraph returned by traversal."""

    nodes: Set[str]
    edges: List[Edge[N]]

    def __len__(self) -> int:
        return len(self.nodes)


class GraphAgent(Generic[N]):
    """
    Graph-based D-gent for relational state storage.

    Features:
    - Store nodes with typed relationships (edges)
    - Lattice operations: meet (∧), join (∨), entails (≤)
    - Provenance tracking: lineage, descendants
    - Graph traversal with depth limits

    This is the foundation for the Relational Lattice in the Noosphere layer.

    Example:
        >>> agent = GraphAgent()
        >>> await agent.add_node("concept1", {"name": "Testing"})
        >>> await agent.add_node("concept2", {"name": "Unit Testing"})
        >>> await agent.add_edge("concept2", EdgeKind.IS_A, "concept1")
        >>> # concept2 is a kind of concept1
        >>> lineage = await agent.lineage("concept2")
        >>> # Returns: ["concept1"] - the ancestors
    """

    def __init__(
        self,
        persistence_path: Optional[Path] = None,
    ):
        """
        Initialize graph agent.

        Args:
            persistence_path: Optional path for persistent storage
        """
        self.persistence_path = persistence_path

        # In-memory storage
        self._nodes: Dict[str, GraphNode[N]] = {}
        self._out_edges: Dict[str, List[Edge[N]]] = {}  # node_id -> outgoing edges
        self._in_edges: Dict[str, List[Edge[N]]] = {}  # node_id -> incoming edges

        # Load from persistence if exists
        if persistence_path and Path(persistence_path).exists():
            self._load_from_disk()

    # === DataAgent Protocol (Simplified) ===

    async def load(self) -> Dict[str, GraphNode[N]]:
        """Load all nodes."""
        return dict(self._nodes)

    async def save(self, state: N) -> str:
        """
        Save state as new node with auto-generated ID.

        Returns the node ID.
        """
        node_id = f"node_{len(self._nodes)}"
        await self.add_node(node_id, state)
        return node_id

    async def history(self, limit: int | None = None) -> List[N]:
        """Return node states in order of addition (newest first)."""
        states = [n.state for n in self._nodes.values()]
        states.reverse()
        return states[:limit] if limit else states

    # === Node Operations ===

    async def add_node(
        self,
        node_id: str,
        state: N,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a node to the graph.

        Args:
            node_id: Unique identifier
            state: Node state
            metadata: Optional metadata
        """
        node = GraphNode(
            id=node_id,
            state=state,
            metadata=metadata or {},
        )
        self._nodes[node_id] = node

        if node_id not in self._out_edges:
            self._out_edges[node_id] = []
        if node_id not in self._in_edges:
            self._in_edges[node_id] = []

        if self.persistence_path:
            self._save_to_disk()

    async def get_node(self, node_id: str) -> Optional[GraphNode[N]]:
        """Get node by ID."""
        return self._nodes.get(node_id)

    async def delete_node(self, node_id: str) -> bool:
        """
        Delete node and all connected edges.

        Returns True if node existed.
        """
        if node_id not in self._nodes:
            return False

        # Remove all edges connected to this node
        del self._nodes[node_id]

        # Remove outgoing edges
        if node_id in self._out_edges:
            for edge in self._out_edges[node_id]:
                self._in_edges[edge.target] = [
                    e
                    for e in self._in_edges.get(edge.target, [])
                    if e.source != node_id
                ]
            del self._out_edges[node_id]

        # Remove incoming edges
        if node_id in self._in_edges:
            for edge in self._in_edges[node_id]:
                self._out_edges[edge.source] = [
                    e
                    for e in self._out_edges.get(edge.source, [])
                    if e.target != node_id
                ]
            del self._in_edges[node_id]

        if self.persistence_path:
            self._save_to_disk()

        return True

    async def node_exists(self, node_id: str) -> bool:
        """Check if node exists."""
        return node_id in self._nodes

    async def list_nodes(self) -> List[str]:
        """List all node IDs."""
        return list(self._nodes.keys())

    # === Edge Operations ===

    async def add_edge(
        self,
        source: str,
        kind: EdgeKind,
        target: str,
        metadata: Optional[Dict[str, Any]] = None,
        bidirectional: bool = False,
    ) -> None:
        """
        Add an edge between nodes.

        Args:
            source: Source node ID
            kind: Edge type
            target: Target node ID
            metadata: Optional edge metadata
            bidirectional: If True, add reverse edge too
        """
        if source not in self._nodes:
            raise NodeNotFoundError(f"Source node not found: {source}")
        if target not in self._nodes:
            raise NodeNotFoundError(f"Target node not found: {target}")

        edge: Edge[N] = Edge(
            source=source,
            kind=kind,
            target=target,
            metadata=metadata or {},
        )

        self._out_edges[source].append(edge)
        self._in_edges[target].append(edge)

        if bidirectional:
            reverse = edge.reverse()
            self._out_edges[target].append(reverse)
            self._in_edges[source].append(reverse)

        if self.persistence_path:
            self._save_to_disk()

    async def get_edges(
        self,
        node_id: str,
        direction: str = "out",
        kind: Optional[EdgeKind] = None,
    ) -> List[Edge[N]]:
        """
        Get edges connected to a node.

        Args:
            node_id: Node ID
            direction: "out", "in", or "both"
            kind: Optional filter by edge kind

        Returns:
            List of edges
        """
        if node_id not in self._nodes:
            raise NodeNotFoundError(f"Node not found: {node_id}")

        edges: List[Edge[N]] = []

        if direction in ("out", "both"):
            edges.extend(self._out_edges.get(node_id, []))
        if direction in ("in", "both"):
            edges.extend(self._in_edges.get(node_id, []))

        if kind is not None:
            edges = [e for e in edges if e.kind == kind]

        return edges

    async def remove_edge(
        self,
        source: str,
        kind: EdgeKind,
        target: str,
    ) -> bool:
        """
        Remove an edge.

        Returns True if edge existed.
        """
        if source not in self._out_edges:
            return False

        original_len = len(self._out_edges[source])
        self._out_edges[source] = [
            e
            for e in self._out_edges[source]
            if not (e.kind == kind and e.target == target)
        ]

        if source in self._in_edges:
            self._in_edges[target] = [
                e
                for e in self._in_edges.get(target, [])
                if not (e.kind == kind and e.source == source)
            ]

        if self.persistence_path:
            self._save_to_disk()

        return len(self._out_edges[source]) < original_len

    # === Lattice Operations ===

    async def meet(self, a: str, b: str) -> Optional[str]:
        """
        Find greatest common ancestor (∧).

        "What do a and b have in common?"

        Returns the most specific node that is an ancestor of both a and b,
        following IS_A and DERIVES_FROM edges.
        """
        ancestors_a = await self._ancestors(a)
        ancestors_b = await self._ancestors(b)

        # Find common ancestors
        common = ancestors_a & ancestors_b

        if not common:
            return None

        # Find the "greatest" (most specific) common ancestor
        # The one with the longest path from both a and b
        best = None
        best_depth = -1

        for node_id in common:
            depth_a = await self._depth_to(a, node_id)
            depth_b = await self._depth_to(b, node_id)
            min_depth = min(depth_a, depth_b)

            if min_depth > best_depth:
                best_depth = min_depth
                best = node_id

        return best

    async def join(self, a: str, b: str) -> Optional[str]:
        """
        Find least common descendant (∨).

        "What is the smallest state containing both a and b?"

        Returns the most general node that is a descendant of both a and b.
        """
        descendants_a = await self._descendants(a)
        descendants_b = await self._descendants(b)

        # Find common descendants
        common = descendants_a & descendants_b

        if not common:
            return None

        # Find the "least" (most general) common descendant
        # The one with the shortest path from both a and b
        best = None
        best_depth = float("inf")

        for node_id in common:
            depth_a = await self._depth_to(node_id, a)
            depth_b = await self._depth_to(node_id, b)
            max_depth = max(depth_a, depth_b)

            if max_depth < best_depth:
                best_depth = max_depth
                best = node_id

        return best

    async def entails(self, a: str, b: str) -> bool:
        """
        Does b entail a? (a ≤ b)

        "Is a implied by b?"

        Returns True if a can be reached from b by following
        IS_A or DERIVES_FROM edges upward.
        """
        ancestors_a = await self._ancestors(a)
        return b in ancestors_a or a == b

    async def compare(self, a: str, b: str) -> str:
        """
        Compare two nodes in the lattice order.

        Returns:
        - "a ≤ b": a is below b (b entails a)
        - "b ≤ a": b is below a (a entails b)
        - "a = b": same node
        - "incomparable": neither above nor below
        """
        if a == b:
            return "a = b"

        a_below_b = await self.entails(a, b)
        b_below_a = await self.entails(b, a)

        if a_below_b and b_below_a:
            return "a = b"  # Equivalent
        elif a_below_b:
            return "a ≤ b"
        elif b_below_a:
            return "b ≤ a"
        else:
            return "incomparable"

    # === Provenance Operations ===

    async def lineage(self, node_id: str, max_depth: int = 10) -> List[str]:
        """
        Get ancestry chain (provenance).

        Every artifact knows its origins—essential for ethical memory.

        Returns: List of ancestors from immediate parent to root,
                 following IS_A and DERIVES_FROM edges.
        """
        if node_id not in self._nodes:
            raise NodeNotFoundError(f"Node not found: {node_id}")

        ancestors = []
        visited = {node_id}
        queue = deque([(node_id, 0)])

        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue

            for edge in self._out_edges.get(current, []):
                if edge.kind in (EdgeKind.IS_A, EdgeKind.DERIVES_FROM):
                    if edge.target not in visited:
                        visited.add(edge.target)
                        ancestors.append(edge.target)
                        queue.append((edge.target, depth + 1))

        return ancestors

    async def descendants(self, node_id: str, max_depth: int = 10) -> List[str]:
        """
        Get all derived artifacts.

        Returns: List of nodes derived from this node.
        """
        if node_id not in self._nodes:
            raise NodeNotFoundError(f"Node not found: {node_id}")

        desc = []
        visited = {node_id}
        queue = deque([(node_id, 0)])

        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue

            for edge in self._in_edges.get(current, []):
                if edge.kind in (EdgeKind.IS_A, EdgeKind.DERIVES_FROM):
                    if edge.source not in visited:
                        visited.add(edge.source)
                        desc.append(edge.source)
                        queue.append((edge.source, depth + 1))

        return desc

    async def derivation_path(
        self,
        from_node: str,
        to_node: str,
        max_depth: int = 10,
    ) -> Optional[List[str]]:
        """
        Find path from one node to another.

        Returns: Sequence of nodes, or None if no path exists.
        """
        if from_node not in self._nodes:
            raise NodeNotFoundError(f"Node not found: {from_node}")
        if to_node not in self._nodes:
            raise NodeNotFoundError(f"Node not found: {to_node}")

        if from_node == to_node:
            return [from_node]

        # BFS to find shortest path
        visited = {from_node}
        queue = deque([(from_node, [from_node])])

        while queue:
            current, path = queue.popleft()
            if len(path) > max_depth:
                continue

            # Check all edges (both directions for general traversal)
            for edge in self._out_edges.get(current, []):
                if edge.target not in visited:
                    new_path = path + [edge.target]
                    if edge.target == to_node:
                        return new_path
                    visited.add(edge.target)
                    queue.append((edge.target, new_path))

        return None

    # === Traversal Operations ===

    async def traverse(
        self,
        start: str,
        depth: int = 3,
        filter_kinds: Optional[List[EdgeKind]] = None,
    ) -> Subgraph[N]:
        """
        Graph traversal from starting node.

        Returns: Subgraph containing all reachable nodes within depth.
        """
        if start not in self._nodes:
            raise NodeNotFoundError(f"Node not found: {start}")

        nodes = {start}
        edges: List[Edge[N]] = []
        visited = {start}
        queue = deque([(start, 0)])

        while queue:
            current, current_depth = queue.popleft()
            if current_depth >= depth:
                continue

            for edge in self._out_edges.get(current, []):
                if filter_kinds and edge.kind not in filter_kinds:
                    continue

                edges.append(edge)
                if edge.target not in visited:
                    visited.add(edge.target)
                    nodes.add(edge.target)
                    queue.append((edge.target, current_depth + 1))

        return Subgraph(nodes=nodes, edges=edges)

    async def find_path(
        self,
        source: str,
        target: str,
        max_depth: int = 10,
    ) -> Optional[List[Edge[N]]]:
        """
        Find shortest path between two nodes.

        Returns: List of edges forming the path, or None if unreachable.
        """
        if source not in self._nodes:
            raise NodeNotFoundError(f"Node not found: {source}")
        if target not in self._nodes:
            raise NodeNotFoundError(f"Node not found: {target}")

        if source == target:
            return []

        # BFS
        visited = {source}
        queue: deque[tuple[str, List[Edge[N]]]] = deque([(source, [])])

        while queue:
            current, path = queue.popleft()
            if len(path) >= max_depth:
                continue

            for edge in self._out_edges.get(current, []):
                new_path = path + [edge]
                if edge.target == target:
                    return new_path
                if edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, new_path))

        return None

    async def connected_components(self) -> List[Set[str]]:
        """
        Find all connected components in the graph.

        Useful for identifying isolated clusters of knowledge.
        """
        visited: Set[str] = set()
        components: List[Set[str]] = []

        for node_id in self._nodes:
            if node_id not in visited:
                # BFS from this node
                component: Set[str] = set()
                queue = deque([node_id])

                while queue:
                    current = queue.popleft()
                    if current in visited:
                        continue
                    visited.add(current)
                    component.add(current)

                    # Add neighbors (both directions)
                    for edge in self._out_edges.get(current, []):
                        if edge.target not in visited:
                            queue.append(edge.target)
                    for edge in self._in_edges.get(current, []):
                        if edge.source not in visited:
                            queue.append(edge.source)

                if component:
                    components.append(component)

        return components

    # === Internal Methods ===

    async def _ancestors(self, node_id: str) -> Set[str]:
        """Get all ancestors of a node."""
        ancestors: Set[str] = set()
        visited = {node_id}
        queue = deque([node_id])

        while queue:
            current = queue.popleft()
            for edge in self._out_edges.get(current, []):
                if edge.kind in (EdgeKind.IS_A, EdgeKind.DERIVES_FROM):
                    if edge.target not in visited:
                        visited.add(edge.target)
                        ancestors.add(edge.target)
                        queue.append(edge.target)

        return ancestors

    async def _descendants(self, node_id: str) -> Set[str]:
        """Get all descendants of a node."""
        desc: Set[str] = set()
        visited = {node_id}
        queue = deque([node_id])

        while queue:
            current = queue.popleft()
            for edge in self._in_edges.get(current, []):
                if edge.kind in (EdgeKind.IS_A, EdgeKind.DERIVES_FROM):
                    if edge.source not in visited:
                        visited.add(edge.source)
                        desc.add(edge.source)
                        queue.append(edge.source)

        return desc

    async def _depth_to(self, source: str, target: str) -> int:
        """Get depth from source to target (BFS)."""
        if source == target:
            return 0

        visited = {source}
        queue = deque([(source, 0)])

        while queue:
            current, depth = queue.popleft()
            for edge in self._out_edges.get(current, []):
                if edge.target == target:
                    return depth + 1
                if edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, depth + 1))

        return float("inf")  # type: ignore

    def _save_to_disk(self) -> None:
        """Save graph to disk."""
        if self.persistence_path is None:
            return

        path = Path(self.persistence_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Collect all edges
        all_edges = []
        for edges in self._out_edges.values():
            for edge in edges:
                all_edges.append(
                    {
                        "source": edge.source,
                        "kind": edge.kind.value,
                        "target": edge.target,
                        "metadata": edge.metadata,
                    }
                )

        data = {
            "nodes": [
                {"id": n.id, "state": n.state, "metadata": n.metadata}
                for n in self._nodes.values()
            ],
            "edges": all_edges,
        }

        # Atomic write
        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        temp_path.replace(path)

    def _load_from_disk(self) -> None:
        """Load graph from disk."""
        if self.persistence_path is None:
            return

        path = Path(self.persistence_path)
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            # Load nodes
            for node_data in data["nodes"]:
                node = GraphNode(
                    id=node_data["id"],
                    state=node_data["state"],
                    metadata=node_data.get("metadata", {}),
                )
                self._nodes[node.id] = node
                self._out_edges[node.id] = []
                self._in_edges[node.id] = []

            # Load edges
            for edge_data in data["edges"]:
                edge: Edge[N] = Edge(
                    source=edge_data["source"],
                    kind=EdgeKind(edge_data["kind"]),
                    target=edge_data["target"],
                    metadata=edge_data.get("metadata", {}),
                )
                self._out_edges[edge.source].append(edge)
                self._in_edges[edge.target].append(edge)

        except Exception as e:
            raise StorageError(f"Failed to load graph: {e}")
