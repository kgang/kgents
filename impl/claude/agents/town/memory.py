"""
Graph Memory for Agent Town Citizens.

Provides k-hop graph memory with decay and reinforcement.
Citizens use this to store and recall memories with relational structure.

Pattern source: agents/d/graph.py (BFS traversal), garden.py (trust decay)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class ConnectionKind(Enum):
    """Types of memory connections."""

    RELATED_TO = auto()  # Generic association
    CAUSED_BY = auto()  # Causal relationship
    ABOUT = auto()  # Subject reference
    FELT_WITH = auto()  # Emotional association
    LEARNED_FROM = auto()  # Knowledge source


@dataclass
class MemoryNode:
    """
    Single memory with decay and connections.

    Memories form a graph where connections indicate relationships.
    Strength decays over time unless reinforced.
    """

    id: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    strength: float = 1.0  # 0.0-1.0, decays over time
    connections: dict[str, float] = field(default_factory=dict)  # node_id -> weight
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Clamp strength to valid range."""
        self.strength = max(0.0, min(1.0, self.strength))


@dataclass
class RecallResult:
    """Result of a memory recall operation."""

    nodes: list[MemoryNode]
    hops_used: int
    total_strength: float


class GraphMemory:
    """
    Graph episodic memory with k-hop retrieval.

    Supports:
    - store(): Add memory with connections to related memories
    - recall(): Retrieve via k-hop graph traversal
    - decay(): Apply time-based decay to all memories
    - reinforce(): Strengthen accessed/emotionally significant memories
    """

    def __init__(
        self,
        decay_rate: float = 0.01,
        prune_threshold: float = 0.1,
        max_k_hops: int = 3,
    ) -> None:
        """
        Initialize graph memory.

        Args:
            decay_rate: How much strength decays per decay() call
            prune_threshold: Memories below this strength are removed
            max_k_hops: Maximum allowed k-hop traversal depth
        """
        self._nodes: dict[str, MemoryNode] = {}
        self._decay_rate = decay_rate
        self._prune_threshold = prune_threshold
        self._max_k_hops = max_k_hops

    @property
    def size(self) -> int:
        """Number of memories stored."""
        return len(self._nodes)

    def store(
        self,
        key: str,
        content: str,
        connections: dict[str, float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryNode:
        """
        Store memory with connections to related memories.

        Args:
            key: Unique identifier for the memory
            content: The memory content
            connections: Dict of related memory_id -> weight (0.0-1.0)
            metadata: Additional metadata

        Returns:
            The created MemoryNode
        """
        # Validate connections reference existing memories
        valid_connections: dict[str, float] = {}
        if connections:
            for conn_id, weight in connections.items():
                if conn_id in self._nodes:
                    valid_connections[conn_id] = max(0.0, min(1.0, weight))

        node = MemoryNode(
            id=key,
            content=content,
            connections=valid_connections,
            metadata=metadata or {},
        )
        self._nodes[key] = node

        # Create bidirectional connections (memories link both ways)
        for conn_id, weight in valid_connections.items():
            if conn_id in self._nodes:
                self._nodes[conn_id].connections[key] = weight

        return node

    def recall(self, query: str, k_hops: int = 2) -> RecallResult:
        """
        Retrieve memories via k-hop graph traversal.

        Starts from the memory matching query (exact match on id),
        then traverses connections up to k_hops deep.

        Args:
            query: Memory ID to start from
            k_hops: How many connection hops to traverse (clamped to max_k_hops)

        Returns:
            RecallResult with found nodes, hops used, and total strength
        """
        k_hops = min(k_hops, self._max_k_hops)

        if query not in self._nodes:
            return RecallResult(nodes=[], hops_used=0, total_strength=0.0)

        # BFS traversal (pattern from agents/d/graph.py:534-568)
        visited: set[str] = {query}
        result_nodes: list[MemoryNode] = [self._nodes[query]]
        queue: deque[tuple[str, int]] = deque([(query, 0)])

        while queue:
            current_id, current_depth = queue.popleft()
            if current_depth >= k_hops:
                continue

            current_node = self._nodes.get(current_id)
            if not current_node:
                continue

            # Sort connections by weight (strongest first) for deterministic traversal
            sorted_connections = sorted(
                current_node.connections.items(), key=lambda x: -x[1]
            )

            for conn_id, _weight in sorted_connections:
                if conn_id not in visited and conn_id in self._nodes:
                    visited.add(conn_id)
                    conn_node = self._nodes[conn_id]
                    result_nodes.append(conn_node)
                    queue.append((conn_id, current_depth + 1))

        total_strength = sum(n.strength for n in result_nodes)

        return RecallResult(
            nodes=result_nodes,
            hops_used=k_hops,
            total_strength=total_strength,
        )

    def recall_by_content(self, substring: str, k_hops: int = 2) -> list[RecallResult]:
        """
        Recall memories by content substring match.

        Searches all memories for content containing substring,
        then does k-hop traversal from each match.

        Args:
            substring: Text to search for in memory content
            k_hops: How many connection hops to traverse

        Returns:
            List of RecallResults, one per matching memory
        """
        results: list[RecallResult] = []
        substring_lower = substring.lower()

        for node_id, node in self._nodes.items():
            if substring_lower in node.content.lower():
                result = self.recall(node_id, k_hops)
                if result.nodes:
                    results.append(result)

        return results

    def decay(self, rate: float | None = None) -> int:
        """
        Apply decay to all memories; prune below threshold.

        Pattern from agents/d/garden.py:662-673.

        Args:
            rate: Decay rate (uses default if None)

        Returns:
            Number of memories pruned
        """
        rate = rate if rate is not None else self._decay_rate
        pruned = 0

        to_remove: list[str] = []
        for node_id, node in self._nodes.items():
            node.strength = max(0.0, node.strength - rate)
            if node.strength < self._prune_threshold:
                to_remove.append(node_id)

        for node_id in to_remove:
            self._remove_node(node_id)
            pruned += 1

        return pruned

    def reinforce(self, key: str, amount: float = 0.1) -> bool:
        """
        Strengthen a memory (accessed or emotionally significant).

        Args:
            key: Memory ID to reinforce
            amount: How much to increase strength

        Returns:
            True if memory was reinforced, False if not found
        """
        if key not in self._nodes:
            return False

        node = self._nodes[key]
        node.strength = min(1.0, node.strength + amount)
        return True

    def get(self, key: str) -> MemoryNode | None:
        """Get a specific memory by ID."""
        return self._nodes.get(key)

    def _remove_node(self, node_id: str) -> None:
        """Remove a node and clean up all connections to it."""
        if node_id not in self._nodes:
            return

        # Remove connections from other nodes
        for other_node in self._nodes.values():
            if node_id in other_node.connections:
                del other_node.connections[node_id]

        del self._nodes[node_id]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for persistence."""
        return {
            "nodes": [
                {
                    "id": n.id,
                    "content": n.content,
                    "timestamp": n.timestamp.isoformat(),
                    "strength": n.strength,
                    "connections": n.connections,
                    "metadata": n.metadata,
                }
                for n in self._nodes.values()
            ],
            "decay_rate": self._decay_rate,
            "prune_threshold": self._prune_threshold,
            "max_k_hops": self._max_k_hops,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphMemory:
        """Deserialize from dictionary."""
        memory = cls(
            decay_rate=data.get("decay_rate", 0.01),
            prune_threshold=data.get("prune_threshold", 0.1),
            max_k_hops=data.get("max_k_hops", 3),
        )

        # First pass: create all nodes without connections
        for node_data in data.get("nodes", []):
            node = MemoryNode(
                id=node_data["id"],
                content=node_data["content"],
                timestamp=datetime.fromisoformat(node_data["timestamp"]),
                strength=node_data["strength"],
                connections={},  # Will add in second pass
                metadata=node_data.get("metadata", {}),
            )
            memory._nodes[node.id] = node

        # Second pass: restore connections (both exist now)
        for node_data in data.get("nodes", []):
            node = memory._nodes[node_data["id"]]
            for conn_id, weight in node_data.get("connections", {}).items():
                if conn_id in memory._nodes:
                    node.connections[conn_id] = weight

        return memory

    def __len__(self) -> int:
        """Return number of memories."""
        return len(self._nodes)

    def __contains__(self, key: str) -> bool:
        """Check if memory exists."""
        return key in self._nodes
