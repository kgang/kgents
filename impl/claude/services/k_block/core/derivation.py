"""
Derivation DAG for K-Block lineage tracking.

Tracks the derivation relationships between K-Blocks, forming a directed
acyclic graph from L1 (axioms) -> L7 (representations).

Philosophy:
    "The proof IS the decision. The derivation IS the lineage."

Each K-Block can derive from one or more parent K-Blocks. The DAG ensures:
1. No cycles (derivation flows forward through layers)
2. Layer monotonicity (children must be in higher or equal layers)
3. Lineage traceability (can reconstruct full derivation chain)

See: spec/protocols/zero-seed1/layers.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .kblock import KBlockId


@dataclass
class DerivationNode:
    """Node in the derivation DAG."""

    kblock_id: str
    layer: int
    kind: str
    parent_ids: list[str] = field(default_factory=list)  # Nodes this derives from
    child_ids: list[str] = field(default_factory=list)  # Nodes that derive from this

    def __repr__(self) -> str:
        return (
            f"DerivationNode(id={self.kblock_id!r}, layer={self.layer}, "
            f"kind={self.kind!r}, parents={len(self.parent_ids)}, "
            f"children={len(self.child_ids)})"
        )


class DerivationDAG:
    """
    Tracks the derivation relationships between K-Blocks.

    The DAG flows from L1 (axioms) -> L7 (representations).
    Each edge represents a "derives_from" relationship.

    Properties:
    - Acyclic: No node can be its own ancestor
    - Monotonic: Children must be in >= parent layer
    - Traceable: Can reconstruct full lineage to axioms
    """

    def __init__(self) -> None:
        self._nodes: dict[str, DerivationNode] = {}

    def add_node(
        self, kblock_id: str, layer: int, kind: str, parent_ids: list[str] | None = None
    ) -> DerivationNode:
        """
        Add a node to the DAG.

        Args:
            kblock_id: K-Block identifier
            layer: Zero Seed layer (1-7)
            kind: Node kind (axiom, value, goal, spec, action, reflection, representation)
            parent_ids: IDs of parent K-Blocks this derives from

        Returns:
            Created DerivationNode

        Raises:
            ValueError: If parent layers violate monotonicity
        """
        parent_ids = parent_ids or []

        # Validate layer monotonicity
        for parent_id in parent_ids:
            if parent_id in self._nodes:
                parent_layer = self._nodes[parent_id].layer
                if layer < parent_layer:
                    raise ValueError(
                        f"Layer monotonicity violation: child layer {layer} "
                        f"< parent layer {parent_layer} (parent: {parent_id})"
                    )

        node = DerivationNode(
            kblock_id=kblock_id,
            layer=layer,
            kind=kind,
            parent_ids=parent_ids,
            child_ids=[],
        )
        self._nodes[kblock_id] = node

        # Update parent nodes to include this as child
        for parent_id in node.parent_ids:
            if parent_id in self._nodes:
                self._nodes[parent_id].child_ids.append(kblock_id)

        return node

    def get_node(self, kblock_id: str) -> DerivationNode | None:
        """Get node by K-Block ID."""
        return self._nodes.get(kblock_id)

    def get_lineage(self, kblock_id: str) -> list[str]:
        """
        Get all ancestors of a K-Block (derivation chain to axioms).

        Args:
            kblock_id: K-Block ID to trace

        Returns:
            List of ancestor K-Block IDs (topologically sorted)
        """
        result = []
        visited = set()
        stack = [kblock_id]

        while stack:
            current = stack.pop()
            if current in visited or current not in self._nodes:
                continue
            visited.add(current)
            node = self._nodes[current]
            for parent_id in node.parent_ids:
                result.append(parent_id)
                stack.append(parent_id)

        return result

    def get_descendants(self, kblock_id: str) -> list[str]:
        """
        Get all descendants of a K-Block.

        Args:
            kblock_id: K-Block ID to trace forward

        Returns:
            List of descendant K-Block IDs
        """
        result = []
        visited = set()
        stack = [kblock_id]

        while stack:
            current = stack.pop()
            if current in visited or current not in self._nodes:
                continue
            visited.add(current)
            node = self._nodes[current]
            for child_id in node.child_ids:
                result.append(child_id)
                stack.append(child_id)

        return result

    def get_layer_nodes(self, layer: int) -> list[DerivationNode]:
        """
        Get all nodes in a specific layer.

        Args:
            layer: Layer number (1-7)

        Returns:
            List of nodes in that layer
        """
        return [node for node in self._nodes.values() if node.layer == layer]

    def validate_acyclic(self, kblock_id: str) -> bool:
        """
        Verify that a node has no cycles in its ancestry.

        Args:
            kblock_id: K-Block ID to check

        Returns:
            True if acyclic, False if cycle detected
        """
        visited = set()
        rec_stack = set()

        def visit(node_id: str) -> bool:
            if node_id in rec_stack:
                return False  # Cycle detected
            if node_id in visited:
                return True

            visited.add(node_id)
            rec_stack.add(node_id)

            if node_id in self._nodes:
                for parent_id in self._nodes[node_id].parent_ids:
                    if not visit(parent_id):
                        return False

            rec_stack.remove(node_id)
            return True

        return visit(kblock_id)

    def is_grounded(self, kblock_id: str) -> bool:
        """
        Check if a K-Block's lineage terminates at L1 axioms.

        Args:
            kblock_id: K-Block ID to check

        Returns:
            True if lineage reaches L1 axioms, False otherwise
        """
        if kblock_id not in self._nodes:
            return False

        # Traverse to leaves (nodes with no parents)
        leaves = set()
        visited = set()
        stack = [kblock_id]

        while stack:
            current = stack.pop()
            if current in visited or current not in self._nodes:
                continue
            visited.add(current)
            node = self._nodes[current]

            if not node.parent_ids:
                # Leaf node
                leaves.add(current)
            else:
                stack.extend(node.parent_ids)

        # All leaves must be L1 axioms
        return all(self._nodes[leaf_id].layer == 1 for leaf_id in leaves if leaf_id in self._nodes)

    def to_dict(self) -> dict[str, Any]:
        """Serialize DAG to dict."""
        return {
            "nodes": {
                node_id: {
                    "layer": node.layer,
                    "kind": node.kind,
                    "parent_ids": node.parent_ids,
                    "child_ids": node.child_ids,
                }
                for node_id, node in self._nodes.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DerivationDAG":
        """Deserialize DAG from dict."""
        dag = cls()
        nodes_data = data.get("nodes", {})

        # First pass: create all nodes without children (children are derived)
        for node_id, node_data in nodes_data.items():
            dag._nodes[node_id] = DerivationNode(
                kblock_id=node_id,
                layer=node_data["layer"],
                kind=node_data["kind"],
                parent_ids=node_data["parent_ids"],
                child_ids=node_data["child_ids"],
            )

        return dag

    def __len__(self) -> int:
        """Return number of nodes in DAG."""
        return len(self._nodes)

    def __repr__(self) -> str:
        layer_counts: dict[int, int] = {}
        for node in self._nodes.values():
            layer_counts[node.layer] = layer_counts.get(node.layer, 0) + 1

        return (
            f"DerivationDAG(nodes={len(self._nodes)}, layers={dict(sorted(layer_counts.items()))})"
        )


def validate_derivation(
    child_layer: int,
    parent_layers: list[int],
) -> tuple[bool, str | None]:
    """
    Validate that a derivation is valid.

    Rules:
    - Parents must be at a lower layer than child
    - L1 (axioms) cannot have parents

    Args:
        child_layer: The layer of the child node (1-7)
        parent_layers: List of parent node layers

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_derivation(3, [1, 2])  # L3 Goal derives from L1 Axiom and L2 Value
        (True, None)

        >>> validate_derivation(1, [2])  # L1 Axiom cannot have parents
        (False, "Axioms (L1) cannot have parent derivations")

        >>> validate_derivation(2, [3])  # L2 Value cannot derive from L3 Goal (upward)
        (False, "Parent layer (3) must be lower than child (2)")
    """
    if child_layer == 1 and parent_layers:
        return False, "Axioms (L1) cannot have parent derivations"

    for parent_layer in parent_layers:
        if parent_layer >= child_layer:
            return False, f"Parent layer ({parent_layer}) must be lower than child ({child_layer})"

    return True, None


__all__ = [
    "DerivationNode",
    "DerivationDAG",
    "validate_derivation",
]
