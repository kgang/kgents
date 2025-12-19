"""
L-gent Lineage Layer - Provenance & Ancestry Tracking

Layer 2: Where did artifacts come from?

The lineage layer maintains a directed acyclic graph (DAG) of relationships between
artifacts, enabling:
- Blame attribution: Which change caused this regression?
- Impact analysis: What breaks if I deprecate this?
- Evolution tracking: How did this artifact improve over time?
- Audit trails: Who created what, when, and why?

Phase 3 implementation uses D-gent GraphAgent for storage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RelationshipType(Enum):
    """Types of relationships in the lineage graph."""

    SUCCESSOR_TO = "successor_to"  # Evolution (same lineage)
    FORKED_FROM = "forked_from"  # Branching (new lineage)
    DEPENDS_ON = "depends_on"  # Runtime dependency
    TESTED_BY = "tested_by"  # Test coverage
    DOCUMENTED_BY = "documented_by"  # Documentation link
    IMPLEMENTS = "implements"  # Contract satisfaction
    COMPOSED_WITH = "composed_with"  # Known composition


@dataclass
class Relationship:
    """A directed edge in the lineage graph."""

    source_id: str  # Origin artifact
    target_id: str  # Destination artifact
    relationship_type: RelationshipType
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "unknown"  # Who/what created this relationship

    # Context
    context: dict[str, Any] = field(default_factory=dict)
    # Examples:
    # - For successor_to: {"change_summary": "Performance optimization"}
    # - For forked_from: {"reason": "Specialized for news domain"}
    # - For depends_on: {"version_constraint": ">=2.0"}

    # Validity
    deprecated: bool = False
    deprecated_at: datetime | None = None
    deprecation_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type.value,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "context": self.context,
            "deprecated": self.deprecated,
            "deprecated_at": self.deprecated_at.isoformat() if self.deprecated_at else None,
            "deprecation_reason": self.deprecation_reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relationship":
        """Create from dictionary."""
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relationship_type=RelationshipType(data["relationship_type"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            created_by=data.get("created_by", "unknown"),
            context=data.get("context", {}),
            deprecated=data.get("deprecated", False),
            deprecated_at=datetime.fromisoformat(data["deprecated_at"])
            if data.get("deprecated_at")
            else None,
            deprecation_reason=data.get("deprecation_reason"),
        )


class LineageError(Exception):
    """Errors related to lineage operations."""

    pass


class LineageGraph:
    """
    Layer 2: Provenance and ancestry tracking.

    Maintains a DAG of relationships between artifacts.
    Phase 3 implementation uses in-memory storage with optional persistence.
    """

    def __init__(self) -> None:
        """Initialize lineage graph."""
        # In-memory storage for Phase 3
        # Future: Integrate with D-gent GraphAgent
        self._edges: list[Relationship] = []
        self._nodes: set[str] = set()  # Track artifact IDs that have edges

    # ─────────────────────────────────────────────────────────────
    # Write Operations
    # ─────────────────────────────────────────────────────────────

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType | str,
        created_by: str = "unknown",
        context: dict[str, Any] | None = None,
    ) -> Relationship:
        """
        Add a new relationship to the lineage graph.

        Validates:
        - No cycles created (DAG property preserved)
        - Relationship type is valid

        Args:
            source_id: Source artifact ID
            target_id: Target artifact ID
            relationship_type: Type of relationship
            created_by: Who/what created this relationship
            context: Optional context dict

        Returns:
            The created Relationship

        Raises:
            LineageError: If relationship would create a cycle
        """
        # Convert string to enum if needed
        if isinstance(relationship_type, str):
            relationship_type = RelationshipType(relationship_type)

        # Check for cycles (would violate DAG)
        if await self._would_create_cycle(source_id, target_id):
            raise LineageError(f"Relationship would create cycle: {source_id} -> {target_id}")

        rel = Relationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            created_by=created_by,
            context=context or {},
        )

        self._edges.append(rel)
        self._nodes.add(source_id)
        self._nodes.add(target_id)

        return rel

    async def deprecate_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType | str,
        reason: str,
    ) -> bool:
        """
        Mark a relationship as deprecated.

        Args:
            source_id: Source artifact ID
            target_id: Target artifact ID
            relationship_type: Type of relationship
            reason: Why it's deprecated

        Returns:
            True if relationship was found and deprecated, False otherwise
        """
        if isinstance(relationship_type, str):
            relationship_type = RelationshipType(relationship_type)

        for edge in self._edges:
            if (
                edge.source_id == source_id
                and edge.target_id == target_id
                and edge.relationship_type == relationship_type
                and not edge.deprecated
            ):
                edge.deprecated = True
                edge.deprecated_at = datetime.now()
                edge.deprecation_reason = reason
                return True

        return False

    # ─────────────────────────────────────────────────────────────
    # Read Operations
    # ─────────────────────────────────────────────────────────────

    async def get_relationships(
        self,
        source_id: str | None = None,
        target_id: str | None = None,
        relationship_type: RelationshipType | str | None = None,
        include_deprecated: bool = False,
    ) -> list[Relationship]:
        """
        Get relationships matching filters.

        Args:
            source_id: Filter by source artifact
            target_id: Filter by target artifact
            relationship_type: Filter by relationship type
            include_deprecated: Include deprecated relationships

        Returns:
            List of matching relationships
        """
        if isinstance(relationship_type, str):
            relationship_type = RelationshipType(relationship_type)

        results = self._edges

        if source_id is not None:
            results = [r for r in results if r.source_id == source_id]

        if target_id is not None:
            results = [r for r in results if r.target_id == target_id]

        if relationship_type is not None:
            results = [r for r in results if r.relationship_type == relationship_type]

        if not include_deprecated:
            results = [r for r in results if not r.deprecated]

        return results

    async def get_ancestors(
        self,
        artifact_id: str,
        relationship_type: RelationshipType | str | None = None,
        max_depth: int | None = None,
    ) -> list[str]:
        """
        Get all ancestors of an artifact (following edges forward).

        For a relationship like "v2.0 SUCCESSOR_TO v1.0", v1.0 is an ancestor of v2.0.
        We follow the edges in the direction they point (source → target).

        Args:
            artifact_id: Artifact to find ancestors for
            relationship_type: Optional filter by relationship type
            max_depth: Maximum depth to traverse (None = unlimited)

        Returns:
            List of ancestor artifact IDs
        """
        if isinstance(relationship_type, str):
            relationship_type = RelationshipType(relationship_type)

        visited = set()
        queue = [(artifact_id, 0)]  # (id, depth)
        visited.add(artifact_id)  # Mark starting node as visited immediately

        while queue:
            current_id, depth = queue.pop(0)

            if max_depth is not None and depth >= max_depth:
                continue

            # Find edges originating FROM current_id (follow edges forward to targets)
            edges = await self.get_relationships(
                source_id=current_id,
                relationship_type=relationship_type,
            )

            for edge in edges:
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, depth + 1))

        # Remove the starting artifact from results
        visited.discard(artifact_id)
        return list(visited)

    async def get_descendants(
        self,
        artifact_id: str,
        relationship_type: RelationshipType | str | None = None,
        max_depth: int | None = None,
    ) -> list[str]:
        """
        Get all descendants of an artifact (following edges backward).

        For a relationship like "v2.0 SUCCESSOR_TO v1.0", v2.0 is a descendant of v1.0.
        We follow edges in the reverse direction (target ← source).

        Args:
            artifact_id: Artifact to find descendants for
            relationship_type: Optional filter by relationship type
            max_depth: Maximum depth to traverse (None = unlimited)

        Returns:
            List of descendant artifact IDs
        """
        if isinstance(relationship_type, str):
            relationship_type = RelationshipType(relationship_type)

        visited = set()
        queue = [(artifact_id, 0)]  # (id, depth)
        visited.add(artifact_id)  # Mark starting node as visited immediately

        while queue:
            current_id, depth = queue.pop(0)

            if max_depth is not None and depth >= max_depth:
                continue

            # Find edges pointing TO current_id (follow edges backward from targets)
            edges = await self.get_relationships(
                target_id=current_id,
                relationship_type=relationship_type,
            )

            for edge in edges:
                if edge.source_id not in visited:
                    visited.add(edge.source_id)
                    queue.append((edge.source_id, depth + 1))

        # Remove the starting artifact from results
        visited.discard(artifact_id)
        return list(visited)

    async def get_path(
        self,
        start_id: str,
        end_id: str,
        relationship_type: RelationshipType | str | None = None,
    ) -> list[str] | None:
        """
        Find a path from start to end artifact (following edges backward).

        For relationships like "v2.0 SUCCESSOR_TO v1.0" and "v3.0 SUCCESSOR_TO v2.0",
        the path from v1.0 to v3.0 is [v1.0, v2.0, v3.0], following the succession chain.
        We traverse edges in reverse (from target to source).

        Args:
            start_id: Starting artifact ID
            end_id: Ending artifact ID
            relationship_type: Optional filter by relationship type

        Returns:
            List of artifact IDs forming the path, or None if no path exists
        """
        if isinstance(relationship_type, str):
            relationship_type = RelationshipType(relationship_type)

        # Special case: path to self
        if start_id == end_id:
            return [start_id]

        # BFS to find shortest path (traversing backward through edges)
        visited = set()
        queue = [(start_id, [start_id])]  # (current_id, path)
        visited.add(start_id)

        while queue:
            current_id, path = queue.pop(0)

            # Find incoming edges (edges pointing TO current_id)
            # We'll follow them backward (from target to source)
            edges = await self.get_relationships(
                target_id=current_id,
                relationship_type=relationship_type,
            )

            for edge in edges:
                if edge.source_id == end_id:
                    # Found the destination!
                    return path + [edge.source_id]

                if edge.source_id not in visited:
                    visited.add(edge.source_id)
                    queue.append((edge.source_id, path + [edge.source_id]))

        return None  # No path found

    async def has_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType | str,
    ) -> bool:
        """
        Check if a specific edge exists.

        Args:
            source_id: Source artifact ID
            target_id: Target artifact ID
            relationship_type: Relationship type

        Returns:
            True if edge exists (and not deprecated)
        """
        edges = await self.get_relationships(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
        )
        return len(edges) > 0

    async def all_nodes(self) -> list[str]:
        """Get all artifact IDs that have relationships."""
        return list(self._nodes)

    # ─────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────

    async def _would_create_cycle(self, source_id: str, target_id: str) -> bool:
        """
        Check if adding an edge source_id → target_id would create a cycle.

        A cycle would be created if there's already a path from target_id to source_id.
        Because then we'd have: source_id → target_id → ... → source_id

        For example:
        - Existing edges: A → B, B → C
        - Trying to add: C → A
        - Path from A to C exists: A → B → C
        - So adding C → A creates cycle: A → B → C → A

        Self-loops (A → A) are also cycles and must be prevented.
        """
        # Self-loop is a cycle
        if source_id == target_id:
            return True

        # Check if there's already a path from target to source
        visited = set()
        queue = [target_id]
        visited.add(target_id)

        while queue:
            current_id = queue.pop(0)

            # Find edges originating FROM current_id
            edges = await self.get_relationships(source_id=current_id)

            for edge in edges:
                if edge.target_id == source_id:
                    # Found a path from target to source!
                    return True

                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append(edge.target_id)

        return False

    # ─────────────────────────────────────────────────────────────
    # Serialization
    # ─────────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Export lineage graph as dictionary."""
        return {
            "edges": [edge.to_dict() for edge in self._edges],
            "nodes": list(self._nodes),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LineageGraph":
        """Import lineage graph from dictionary."""
        graph = cls()
        graph._nodes = set(data.get("nodes", []))
        graph._edges = [Relationship.from_dict(edge) for edge in data.get("edges", [])]
        return graph


# ─────────────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────────────


async def record_evolution(
    graph: LineageGraph,
    parent_id: str,
    child_id: str,
    created_by: str,
    change_summary: str,
) -> Relationship:
    """
    Record an evolution relationship (successor_to).

    Convenience wrapper for common evolution pattern.

    Args:
        graph: LineageGraph instance
        parent_id: Previous version
        child_id: New version
        created_by: Who evolved it
        change_summary: What changed

    Returns:
        Created relationship
    """
    return await graph.add_relationship(
        source_id=child_id,
        target_id=parent_id,
        relationship_type=RelationshipType.SUCCESSOR_TO,
        created_by=created_by,
        context={"change_summary": change_summary},
    )


async def record_fork(
    graph: LineageGraph,
    parent_id: str,
    fork_id: str,
    created_by: str,
    reason: str,
) -> Relationship:
    """
    Record a fork relationship (forked_from).

    Convenience wrapper for common forking pattern.

    Args:
        graph: LineageGraph instance
        parent_id: Original artifact
        fork_id: Forked artifact
        created_by: Who forked it
        reason: Why it was forked

    Returns:
        Created relationship
    """
    return await graph.add_relationship(
        source_id=fork_id,
        target_id=parent_id,
        relationship_type=RelationshipType.FORKED_FROM,
        created_by=created_by,
        context={"reason": reason},
    )


async def record_dependency(
    graph: LineageGraph,
    dependent_id: str,
    dependency_id: str,
    version_constraint: str | None = None,
) -> Relationship:
    """
    Record a dependency relationship (depends_on).

    Args:
        graph: LineageGraph instance
        dependent_id: Artifact that depends
        dependency_id: Artifact that is depended upon
        version_constraint: Optional version constraint (e.g., ">=2.0")

    Returns:
        Created relationship
    """
    context = {}
    if version_constraint:
        context["version_constraint"] = version_constraint

    return await graph.add_relationship(
        source_id=dependent_id,
        target_id=dependency_id,
        relationship_type=RelationshipType.DEPENDS_ON,
        created_by="system",
        context=context,
    )
