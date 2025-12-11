"""
RelationalLattice: State as a lattice of relationships.

The Relational Lattice extends GraphAgent with full lattice theory:
- Meet (∧): Greatest lower bound - what concepts have in common
- Join (∨): Least upper bound - smallest concept containing both
- Order (≤): Entailment - does A imply B?

Philosophy: "Understanding is not possession—it is relationship."

Part of the Noosphere Layer (D-gent Phase 4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Set, Tuple, TypeVar

from .errors import (
    NodeNotFoundError,
)
from .graph import Edge, EdgeKind, GraphAgent, Subgraph

N = TypeVar("N")  # Node type


class LatticeRelation(Enum):
    """Comparison results for lattice order."""

    BELOW = "below"  # a ≤ b: a is below b
    ABOVE = "above"  # b ≤ a: b is below a
    EQUAL = "equal"  # a = b: same node
    INCOMPARABLE = "incomparable"  # Neither above nor below


@dataclass
class LatticeNode(Generic[N]):
    """
    A node in the relational lattice with order information.

    Extends GraphNode with lattice-specific metadata:
    - depth: Distance from top element
    - is_atom: True if minimal non-bottom element
    - is_coatom: True if maximal non-top element
    """

    id: str
    state: N
    metadata: Dict[str, Any] = field(default_factory=dict)
    depth: int = 0
    is_atom: bool = False
    is_coatom: bool = False

    # Lineage tracking
    created_at: datetime = field(default_factory=datetime.now)
    derived_from: Optional[str] = None  # Parent node ID


@dataclass
class MeetJoinResult:
    """Result of a meet or join operation."""

    node_id: Optional[str]
    operation: str  # "meet" or "join"
    inputs: Tuple[str, str]
    found: bool
    explanation: str = ""


@dataclass
class EntailmentProof:
    """Proof of entailment between two nodes."""

    premise: str  # Node A
    conclusion: str  # Node B
    holds: bool
    path: List[str]  # Path from A to B if entailment holds
    explanation: str = ""


@dataclass
class LatticeStats:
    """Statistics about the lattice structure."""

    total_nodes: int
    total_edges: int
    depth: int  # Maximum depth from top
    num_atoms: int
    num_coatoms: int
    num_components: int  # Connected components
    is_bounded: bool  # Has top and bottom elements


class RelationalLattice(Generic[N]):
    """
    Lattice-structured relational memory.

    The Relational Lattice provides:
    - Meet (∧): Find what two concepts have in common
    - Join (∨): Find smallest concept containing both
    - Entailment (≤): Check if one concept implies another
    - Lineage: Track provenance of derived artifacts
    - Traversal: Explore concept relationships

    Philosophy: "Understanding is not possession—it is relationship."

    Example:
        >>> lattice = RelationalLattice()
        >>>
        >>> # Add concepts
        >>> await lattice.add("animal", {"name": "Animal"})
        >>> await lattice.add("mammal", {"name": "Mammal"})
        >>> await lattice.add("dog", {"name": "Dog"})
        >>>
        >>> # Establish relationships
        >>> await lattice.relate("mammal", "animal", EdgeKind.IS_A)
        >>> await lattice.relate("dog", "mammal", EdgeKind.IS_A)
        >>>
        >>> # Lattice operations
        >>> common = await lattice.meet("dog", "cat")  # Find common ancestor
        >>> container = await lattice.join("dog", "bird")  # Find common container
        >>> is_animal = await lattice.entails("dog", "animal")  # True
    """

    def __init__(
        self,
        persistence_path: Optional[str] = None,
        top_id: str = "__TOP__",
        bottom_id: str = "__BOTTOM__",
    ):
        """
        Initialize relational lattice.

        Args:
            persistence_path: Optional path for persistent storage
            top_id: ID for top element (⊤)
            bottom_id: ID for bottom element (⊥)
        """
        from pathlib import Path

        self._graph: GraphAgent[N] = GraphAgent(
            persistence_path=Path(persistence_path) if persistence_path else None,
        )

        self.top_id = top_id
        self.bottom_id = bottom_id

        # Depth cache for efficient operations
        self._depth_cache: Dict[str, int] = {}

    # === Node Operations ===

    async def add(
        self,
        node_id: str,
        state: N,
        metadata: Optional[Dict[str, Any]] = None,
        derived_from: Optional[str] = None,
    ) -> LatticeNode[N]:
        """
        Add a node to the lattice.

        Args:
            node_id: Unique identifier
            state: Node state/value
            metadata: Optional metadata
            derived_from: ID of parent node (for provenance)

        Returns:
            LatticeNode with depth and lineage information
        """
        full_metadata = {
            **(metadata or {}),
            "created_at": datetime.now().isoformat(),
            "derived_from": derived_from,
        }

        await self._graph.add_node(node_id, state, full_metadata)

        # Add derivation edge if specified
        if derived_from and await self._graph.node_exists(derived_from):
            await self._graph.add_edge(node_id, EdgeKind.DERIVES_FROM, derived_from)

        # Compute depth
        depth = await self._compute_depth(node_id)
        self._depth_cache[node_id] = depth

        return LatticeNode(
            id=node_id,
            state=state,
            metadata=full_metadata,
            depth=depth,
            derived_from=derived_from,
        )

    async def get(self, node_id: str) -> Optional[LatticeNode[N]]:
        """Get node by ID with lattice information."""
        node = await self._graph.get_node(node_id)
        if node is None:
            return None

        depth = self._depth_cache.get(node_id)
        if depth is None:
            depth = await self._compute_depth(node_id)
            self._depth_cache[node_id] = depth

        return LatticeNode(
            id=node.id,
            state=node.state,
            metadata=node.metadata,
            depth=depth,
            derived_from=node.metadata.get("derived_from"),
        )

    async def delete(self, node_id: str) -> bool:
        """Delete node from lattice."""
        self._depth_cache.pop(node_id, None)
        return await self._graph.delete_node(node_id)

    async def exists(self, node_id: str) -> bool:
        """Check if node exists."""
        return await self._graph.node_exists(node_id)

    async def list_nodes(self) -> List[str]:
        """List all node IDs."""
        return await self._graph.list_nodes()

    # === Relationship Operations ===

    async def relate(
        self,
        source: str,
        target: str,
        kind: EdgeKind = EdgeKind.IS_A,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Establish a relationship between nodes.

        For lattice operations, IS_A and DERIVES_FROM edges define order.
        """
        await self._graph.add_edge(source, kind, target, metadata)
        # Invalidate depth cache for affected nodes
        self._depth_cache.pop(source, None)

    async def unrelate(
        self,
        source: str,
        target: str,
        kind: EdgeKind,
    ) -> bool:
        """Remove a relationship. Returns True if it existed."""
        result = await self._graph.remove_edge(source, kind, target)
        if result:
            self._depth_cache.pop(source, None)
        return result

    async def relationships(
        self,
        node_id: str,
        direction: str = "out",
        kind: Optional[EdgeKind] = None,
    ) -> List[Edge[N]]:
        """Get relationships for a node."""
        return await self._graph.get_edges(node_id, direction, kind)

    # === Lattice Operations ===

    async def meet(self, a: str, b: str) -> MeetJoinResult:
        """
        Find greatest lower bound (∧).

        "What do a and b have in common?"

        Returns the most specific node that is an ancestor of both.
        """
        if not await self.exists(a):
            raise NodeNotFoundError(f"Node not found: {a}")
        if not await self.exists(b):
            raise NodeNotFoundError(f"Node not found: {b}")

        if a == b:
            return MeetJoinResult(
                node_id=a,
                operation="meet",
                inputs=(a, b),
                found=True,
                explanation=f"Same node: {a}",
            )

        # Find common ancestors
        result = await self._graph.meet(a, b)

        if result:
            return MeetJoinResult(
                node_id=result,
                operation="meet",
                inputs=(a, b),
                found=True,
                explanation=f"Greatest common ancestor of {a} and {b}",
            )

        return MeetJoinResult(
            node_id=None,
            operation="meet",
            inputs=(a, b),
            found=False,
            explanation=f"No common ancestor for {a} and {b}",
        )

    async def join(self, a: str, b: str) -> MeetJoinResult:
        """
        Find least upper bound (∨).

        "What is the smallest concept containing both a and b?"

        Returns the most general node that is a descendant of both.
        """
        if not await self.exists(a):
            raise NodeNotFoundError(f"Node not found: {a}")
        if not await self.exists(b):
            raise NodeNotFoundError(f"Node not found: {b}")

        if a == b:
            return MeetJoinResult(
                node_id=a,
                operation="join",
                inputs=(a, b),
                found=True,
                explanation=f"Same node: {a}",
            )

        result = await self._graph.join(a, b)

        if result:
            return MeetJoinResult(
                node_id=result,
                operation="join",
                inputs=(a, b),
                found=True,
                explanation=f"Least common descendant of {a} and {b}",
            )

        return MeetJoinResult(
            node_id=None,
            operation="join",
            inputs=(a, b),
            found=False,
            explanation=f"No common descendant for {a} and {b}",
        )

    async def entails(self, a: str, b: str) -> EntailmentProof:
        """
        Check if b entails a (a ≤ b).

        "Is a implied by b?"

        Returns proof with path if entailment holds.
        """
        if not await self.exists(a):
            raise NodeNotFoundError(f"Node not found: {a}")
        if not await self.exists(b):
            raise NodeNotFoundError(f"Node not found: {b}")

        if a == b:
            return EntailmentProof(
                premise=a,
                conclusion=b,
                holds=True,
                path=[a],
                explanation="Reflexivity: every node entails itself",
            )

        # Check if a can be reached from b via ordering edges
        holds = await self._graph.entails(a, b)

        if holds:
            # Find path for proof
            path_result = await self._graph.derivation_path(a, b)
            path = path_result if path_result else [a, b]

            return EntailmentProof(
                premise=a,
                conclusion=b,
                holds=True,
                path=path,
                explanation=f"{b} entails {a} via path: {' → '.join(path)}",
            )

        return EntailmentProof(
            premise=a,
            conclusion=b,
            holds=False,
            path=[],
            explanation=f"{b} does not entail {a}: no path found",
        )

    async def compare(self, a: str, b: str) -> LatticeRelation:
        """
        Compare two nodes in the lattice order.

        Returns:
        - BELOW: a ≤ b (b entails a)
        - ABOVE: b ≤ a (a entails b)
        - EQUAL: a = b
        - INCOMPARABLE: neither
        """
        if a == b:
            return LatticeRelation.EQUAL

        result = await self._graph.compare(a, b)

        if result == "a ≤ b":
            return LatticeRelation.BELOW
        elif result == "b ≤ a":
            return LatticeRelation.ABOVE
        elif result == "a = b":
            return LatticeRelation.EQUAL
        else:
            return LatticeRelation.INCOMPARABLE

    # === Provenance Operations ===

    async def lineage(self, node_id: str, max_depth: int = 10) -> List[str]:
        """
        Get ancestry chain (provenance).

        Every artifact knows its origins—essential for ethical memory.
        """
        return await self._graph.lineage(node_id, max_depth)

    async def descendants(self, node_id: str, max_depth: int = 10) -> List[str]:
        """Get all derived artifacts."""
        return await self._graph.descendants(node_id, max_depth)

    async def derivation_path(
        self,
        from_node: str,
        to_node: str,
        max_depth: int = 10,
    ) -> Optional[List[str]]:
        """Find derivation path between nodes."""
        return await self._graph.derivation_path(from_node, to_node, max_depth)

    async def root_ancestors(self, node_id: str) -> List[str]:
        """
        Find root ancestors (nodes with no parents).

        These are the original sources in the provenance chain.
        """
        ancestors = await self.lineage(node_id, max_depth=100)
        roots = []

        for ancestor in ancestors:
            edges = await self._graph.get_edges(ancestor, direction="out")
            ordering_edges = [
                e for e in edges if e.kind in (EdgeKind.IS_A, EdgeKind.DERIVES_FROM)
            ]
            if not ordering_edges:
                roots.append(ancestor)

        return roots if roots else ([node_id] if not ancestors else [ancestors[-1]])

    # === Traversal Operations ===

    async def traverse(
        self,
        start: str,
        depth: int = 3,
        filter_kinds: Optional[List[EdgeKind]] = None,
    ) -> Subgraph[N]:
        """Graph traversal from starting node."""
        return await self._graph.traverse(start, depth, filter_kinds)

    async def find_path(
        self,
        source: str,
        target: str,
        max_depth: int = 10,
    ) -> Optional[List[Edge[N]]]:
        """Find shortest path between nodes."""
        return await self._graph.find_path(source, target, max_depth)

    async def connected_components(self) -> List[Set[str]]:
        """Find all connected components."""
        return await self._graph.connected_components()

    # === Special Lattice Nodes ===

    async def atoms(self) -> List[str]:
        """
        Find atoms: minimal non-bottom elements.

        Atoms are nodes that have only the bottom element below them.
        """
        all_nodes = await self.list_nodes()
        atoms = []

        for node_id in all_nodes:
            if node_id in (self.top_id, self.bottom_id):
                continue

            # Check if this node has any children (non-bottom)
            descendants = await self.descendants(node_id, max_depth=1)
            if not descendants or all(d == self.bottom_id for d in descendants):
                atoms.append(node_id)

        return atoms

    async def coatoms(self) -> List[str]:
        """
        Find coatoms: maximal non-top elements.

        Coatoms are nodes that have only the top element above them.
        """
        all_nodes = await self.list_nodes()
        coatoms = []

        for node_id in all_nodes:
            if node_id in (self.top_id, self.bottom_id):
                continue

            # Check if this node has any parents (non-top)
            ancestors = await self.lineage(node_id, max_depth=1)
            if not ancestors or all(a == self.top_id for a in ancestors):
                coatoms.append(node_id)

        return coatoms

    # === Statistics ===

    async def stats(self) -> LatticeStats:
        """Get lattice statistics."""
        all_nodes = await self.list_nodes()
        components = await self.connected_components()

        # Count edges
        total_edges = 0
        for node_id in all_nodes:
            edges = await self._graph.get_edges(node_id, direction="out")
            total_edges += len(edges)

        # Check for top/bottom
        has_top = await self.exists(self.top_id)
        has_bottom = await self.exists(self.bottom_id)

        # Compute max depth
        max_depth = 0
        for node_id in all_nodes:
            depth = self._depth_cache.get(node_id)
            if depth is None:
                depth = await self._compute_depth(node_id)
                self._depth_cache[node_id] = depth
            max_depth = max(max_depth, depth)

        atoms = await self.atoms()
        coatoms = await self.coatoms()

        return LatticeStats(
            total_nodes=len(all_nodes),
            total_edges=total_edges,
            depth=max_depth,
            num_atoms=len(atoms),
            num_coatoms=len(coatoms),
            num_components=len(components),
            is_bounded=has_top and has_bottom,
        )

    # === Internal Methods ===

    async def _compute_depth(self, node_id: str) -> int:
        """Compute depth of a node (distance from roots)."""
        ancestors = await self.lineage(node_id, max_depth=100)
        return len(ancestors)

    # === H-gent Integration ===

    async def record_contradiction(
        self,
        thesis: str,
        antithesis: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a dialectical contradiction."""
        await self.relate(thesis, antithesis, EdgeKind.CONTRADICTS, metadata)
        await self.relate(antithesis, thesis, EdgeKind.CONTRADICTS, metadata)

    async def record_synthesis(
        self,
        synthesis: str,
        thesis: str,
        antithesis: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a dialectical synthesis (sublation)."""
        await self.relate(synthesis, thesis, EdgeKind.SYNTHESIZES, metadata)
        await self.relate(synthesis, antithesis, EdgeKind.SYNTHESIZES, metadata)

    async def find_contradictions(self, node_id: str) -> List[str]:
        """Find all nodes that contradict this one."""
        edges = await self.relationships(
            node_id, direction="both", kind=EdgeKind.CONTRADICTS
        )
        results = set()
        for edge in edges:
            if edge.source == node_id:
                results.add(edge.target)
            else:
                results.add(edge.source)
        return list(results)

    async def find_syntheses(self, node_id: str) -> List[str]:
        """Find all syntheses that incorporate this node."""
        edges = await self.relationships(
            node_id, direction="in", kind=EdgeKind.SYNTHESIZES
        )
        return [edge.source for edge in edges]
