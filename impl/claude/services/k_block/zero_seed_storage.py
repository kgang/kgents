"""
Zero Seed K-Block Storage: Bridge between Zero Seed API and K-Block storage.

Provides CRUD operations for Zero Seed nodes backed by K-Block storage.

Philosophy:
    "Zero Seed nodes ARE K-Blocks. The derivation IS the lineage."

This module bridges:
- Zero Seed API (ZeroNode models, layer semantics)
- K-Block storage (transactional editing, cosmos persistence)
- Derivation DAG (lineage tracking)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .core.derivation import DerivationDAG
from .core.kblock import KBlockId, generate_kblock_id
from .layers.factories import create_kblock_for_layer

if TYPE_CHECKING:
    from .core.kblock import KBlock

logger = logging.getLogger(__name__)


class ZeroSeedStorage:
    """
    Storage adapter for Zero Seed nodes using K-Blocks.

    Manages:
    1. K-Block creation for Zero Seed nodes
    2. Derivation DAG tracking
    3. CRUD operations with lineage validation
    """

    def __init__(self):
        self._kblocks: dict[str, KBlock] = {}
        self._dag = DerivationDAG()

    def create_node(
        self,
        layer: int,
        title: str,
        content: str,
        lineage: list[str] | None = None,
        confidence: float | None = None,
        tags: list[str] | None = None,
        created_by: str = "system",
    ) -> tuple[KBlock, str]:
        """
        Create a new Zero Seed node as a K-Block.

        Args:
            layer: Zero Seed layer (1-7)
            title: Display title
            content: Markdown content
            lineage: Parent K-Block IDs
            confidence: Confidence score (0-1)
            tags: Tags for categorization
            created_by: Creator identifier

        Returns:
            Tuple of (created K-Block, node_id)

        Raises:
            ValueError: If layer invalid or lineage validation fails
        """
        lineage = lineage or []

        # Generate K-Block ID
        kblock_id = generate_kblock_id()

        # Create K-Block using layer factory
        kblock = create_kblock_for_layer(
            layer=layer,
            kblock_id=kblock_id,
            title=title,
            content=content,
            lineage=lineage,
            confidence=confidence,
            tags=tags,
            created_by=created_by,
        )

        # Store K-Block
        node_id = str(kblock_id)
        self._kblocks[node_id] = kblock

        # Add to derivation DAG
        kind = getattr(kblock, "_kind", "unknown")
        self._dag.add_node(
            kblock_id=node_id,
            layer=layer,
            kind=kind,
            parent_ids=lineage,
        )

        logger.info(
            f"Created Zero Seed node: {node_id} (L{layer}, {kind}, "
            f"lineage={len(lineage)})"
        )

        return kblock, node_id

    def get_node(self, node_id: str) -> KBlock | None:
        """
        Get a Zero Seed node by ID.

        Args:
            node_id: Node ID (K-Block ID)

        Returns:
            K-Block if found, None otherwise
        """
        return self._kblocks.get(node_id)

    def update_node(
        self,
        node_id: str,
        title: str | None = None,
        content: str | None = None,
        confidence: float | None = None,
        tags: list[str] | None = None,
    ) -> KBlock | None:
        """
        Update a Zero Seed node.

        Args:
            node_id: Node ID to update
            title: Updated title
            content: Updated content
            confidence: Updated confidence
            tags: Updated tags

        Returns:
            Updated K-Block if found, None otherwise
        """
        kblock = self._kblocks.get(node_id)
        if not kblock:
            return None

        # Update metadata
        if title is not None:
            kblock._title = title
        if content is not None:
            kblock.set_content(content)
        if confidence is not None:
            kblock._confidence = confidence
        if tags is not None:
            kblock._tags = tags

        logger.info(f"Updated Zero Seed node: {node_id}")
        return kblock

    def delete_node(self, node_id: str) -> bool:
        """
        Delete a Zero Seed node.

        Args:
            node_id: Node ID to delete

        Returns:
            True if deleted, False if not found
        """
        if node_id not in self._kblocks:
            return False

        del self._kblocks[node_id]
        logger.info(f"Deleted Zero Seed node: {node_id}")
        return True

    def get_lineage(self, node_id: str) -> list[str]:
        """
        Get lineage (ancestors) of a node.

        Args:
            node_id: Node ID

        Returns:
            List of ancestor node IDs
        """
        return self._dag.get_lineage(node_id)

    def get_descendants(self, node_id: str) -> list[str]:
        """
        Get descendants of a node.

        Args:
            node_id: Node ID

        Returns:
            List of descendant node IDs
        """
        return self._dag.get_descendants(node_id)

    def get_layer_nodes(self, layer: int) -> list[KBlock]:
        """
        Get all nodes in a specific layer.

        Args:
            layer: Layer number (1-7)

        Returns:
            List of K-Blocks in that layer
        """
        dag_nodes = self._dag.get_layer_nodes(layer)
        return [
            self._kblocks[node.kblock_id]
            for node in dag_nodes
            if node.kblock_id in self._kblocks
        ]

    def is_grounded(self, node_id: str) -> bool:
        """
        Check if a node's lineage terminates at L1 axioms.

        Args:
            node_id: Node ID

        Returns:
            True if grounded in axioms, False otherwise
        """
        return self._dag.is_grounded(node_id)

    @property
    def dag(self) -> DerivationDAG:
        """Get the derivation DAG."""
        return self._dag

    def __len__(self) -> int:
        """Return number of stored nodes."""
        return len(self._kblocks)


# Global storage instance (in production, would use DI)
_storage: ZeroSeedStorage | None = None


def get_zero_seed_storage() -> ZeroSeedStorage:
    """Get global Zero Seed storage instance."""
    global _storage
    if _storage is None:
        _storage = ZeroSeedStorage()
    return _storage


def reset_zero_seed_storage() -> None:
    """Reset global storage (for testing)."""
    global _storage
    _storage = None


__all__ = [
    "ZeroSeedStorage",
    "get_zero_seed_storage",
    "reset_zero_seed_storage",
]
