"""
L-gent Graph Search: Relationship-based discovery using LineageGraph and TypeLattice.

This module implements "Brain 3" of L-gent's three-brain architecture:
graph search using relationships and type compatibility to find artifacts.

Phase 7 Implementation:
- GraphBrain: Relationship-aware search engine
- Compatible artifact finding (upstream/downstream composition)
- Path finding for composition planning
- Lineage traversal (ancestors/descendants/dependents)
- Type-based filtering using TypeLattice

Design Philosophy:
- Leverage existing L-gent infrastructure (LineageGraph, TypeLattice)
- Enable composition planning ("how do I get from A to B?")
- Surface hidden dependencies and evolution history
- Composable: Works alongside keyword and semantic search
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .lattice import TypeLattice
from .lineage import LineageGraph, RelationshipType
from .registry import Registry
from .types import CatalogEntry, EntityType


class SearchDirection(Enum):
    """Direction for compatibility search."""

    UPSTREAM = "upstream"  # What can feed into this?
    DOWNSTREAM = "downstream"  # What can receive this output?
    BOTH = "both"  # Both directions


@dataclass
class GraphResult:
    """Result from graph search with relationship context."""

    id: str
    entry: CatalogEntry
    relationship: str  # Type of relationship ("compatible", "successor_to", etc.)
    path_length: int  # Distance from query origin
    path: Optional[list[str]]  # Full path if relevant
    explanation: str  # Why this was found


class GraphBrain:
    """Graph-based search over artifact relationships.

    This is "Brain 3" of the three-brain architecture. It finds artifacts
    based on their relationships to other artifacts, enabling:
    - Composition planning (what connects to what?)
    - Dependency discovery (what depends on this?)
    - Lineage exploration (where did this come from?)
    - Type compatibility matching

    Example:
        brain = GraphBrain(registry, lineage, lattice)
        results = await brain.find_compatible("NewsParser", direction="downstream")
        # Returns: agents that can receive NewsParser's output
    """

    def __init__(self, registry: Registry, lineage: LineageGraph, lattice: TypeLattice):
        """Initialize graph search brain.

        Args:
            registry: Catalog registry
            lineage: Lineage graph for provenance tracking
            lattice: Type lattice for compatibility checking
        """
        self.registry = registry
        self.lineage = lineage
        self.lattice = lattice

    async def find_compatible(
        self,
        artifact_id: str,
        direction: SearchDirection = SearchDirection.DOWNSTREAM,
        limit: int = 10,
    ) -> list[GraphResult]:
        """Find artifacts that can compose with the given one.

        Args:
            artifact_id: ID of artifact to find compatibility for
            direction: Search direction (upstream/downstream/both)
            limit: Maximum number of results

        Returns:
            List of compatible artifacts with composition context
        """
        entry = await self.registry.get(artifact_id)
        if not entry:
            return []

        results: list[GraphResult] = []

        # Downstream: Find agents whose input is compatible with our output
        if direction in (SearchDirection.DOWNSTREAM, SearchDirection.BOTH):
            if entry.output_type:
                downstream = await self._find_downstream_compatible(entry, limit)
                results.extend(downstream)

        # Upstream: Find agents whose output is compatible with our input
        if direction in (SearchDirection.UPSTREAM, SearchDirection.BOTH):
            if entry.input_type:
                upstream = await self._find_upstream_compatible(entry, limit)
                results.extend(upstream)

        # Sort by path length (prefer direct connections)
        results.sort(key=lambda r: r.path_length)
        return results[:limit]

    async def find_path(
        self, source_type: str, target_type: str, max_length: int = 5
    ) -> Optional[list[str]]:
        """Find composition path from source to target type.

        Uses BFS to find the shortest sequence of agents that can transform
        data from source_type to target_type.

        Args:
            source_type: Starting type
            target_type: Target type
            max_length: Maximum path length

        Returns:
            List of artifact IDs forming a valid pipeline, or None if no path exists
        """
        # BFS over type-compatible agents
        queue: list[tuple[str, list[str]]] = [(source_type, [])]
        visited: set[str] = {source_type}

        while queue:
            current_type, path = queue.pop(0)

            if len(path) >= max_length:
                continue

            # Find all agents that accept current_type as input
            all_agents = await self.registry.list()
            candidates = [
                a
                for a in all_agents
                if a.entity_type == EntityType.AGENT and a.input_type == current_type
            ]

            for agent in candidates:
                new_path = path + [agent.id]

                # Check if we've reached target
                if agent.output_type == target_type:
                    return new_path

                # Check if output_type is a subtype of target
                try:
                    result = await self.lattice.is_subtype(
                        agent.output_type, target_type
                    )
                    if result:
                        return new_path
                except Exception:
                    pass

                # Continue search
                if agent.output_type and agent.output_type not in visited:
                    visited.add(agent.output_type)
                    queue.append((agent.output_type, new_path))

        return None

    async def get_dependents(
        self, artifact_id: str, depth: int = 1
    ) -> list[GraphResult]:
        """Find artifacts that depend on the given one.

        Args:
            artifact_id: ID of artifact to find dependents for
            depth: Maximum traversal depth (1 = direct dependents only)

        Returns:
            List of dependent artifacts
        """
        results: list[GraphResult] = []

        # Find relationships where artifact is the target (depended upon)
        relationships = await self.lineage.get_relationships(target_id=artifact_id)
        depends_on_rels = [
            r
            for r in relationships
            if r.relationship_type == RelationshipType.DEPENDS_ON
        ]

        for rel in depends_on_rels:
            entry = await self.registry.get(rel.source_id)
            if entry:
                results.append(
                    GraphResult(
                        id=rel.source_id,
                        entry=entry,
                        relationship="depends_on",
                        path_length=1,
                        path=[artifact_id, rel.source_id],
                        explanation=f"{entry.name} depends on this artifact",
                    )
                )

        # Recursive traversal if depth > 1
        if depth > 1:
            for rel in depends_on_rels:
                sub_dependents = await self.get_dependents(rel.source_id, depth - 1)
                for sub_dep in sub_dependents:
                    # Adjust path and length
                    sub_dep.path_length += 1
                    if sub_dep.path:
                        sub_dep.path = [artifact_id] + sub_dep.path
                    results.append(sub_dep)

        return results

    async def get_ancestors(
        self,
        artifact_id: str,
        depth: int = -1,  # -1 = unlimited
    ) -> list[GraphResult]:
        """Find the lineage ancestry of an artifact.

        Args:
            artifact_id: ID of artifact to find ancestors for
            depth: Maximum traversal depth (-1 = unlimited)

        Returns:
            List of ancestor artifacts
        """
        ancestors_list = await self.lineage.get_ancestors(
            artifact_id,
            relationship_type=RelationshipType.SUCCESSOR_TO,
            max_depth=depth if depth > 0 else None,
        )

        results: list[GraphResult] = []
        for ancestor_id in ancestors_list:
            entry = await self.registry.get(ancestor_id)
            if entry:
                results.append(
                    GraphResult(
                        id=ancestor_id,
                        entry=entry,
                        relationship="ancestor",
                        path_length=1,  # Direct ancestor (distance not returned by API)
                        path=None,  # Could reconstruct path if needed
                        explanation="Ancestor artifact",
                    )
                )

        return results

    async def get_descendants(
        self, artifact_id: str, depth: int = -1
    ) -> list[GraphResult]:
        """Find descendants (artifacts evolved from this one).

        Args:
            artifact_id: ID of artifact to find descendants for
            depth: Maximum traversal depth (-1 = unlimited)

        Returns:
            List of descendant artifacts
        """
        descendants_list = await self.lineage.get_descendants(
            artifact_id,
            relationship_type=RelationshipType.SUCCESSOR_TO,
            max_depth=depth if depth > 0 else None,
        )

        results: list[GraphResult] = []
        for descendant_id in descendants_list:
            entry = await self.registry.get(descendant_id)
            if entry:
                results.append(
                    GraphResult(
                        id=descendant_id,
                        entry=entry,
                        relationship="descendant",
                        path_length=1,  # Direct descendant
                        path=None,
                        explanation="Descendant artifact",
                    )
                )

        return results

    async def find_related(
        self,
        artifact_id: str,
        relationship_type: Optional[RelationshipType] = None,
        limit: int = 10,
    ) -> list[GraphResult]:
        """Find all artifacts related to the given one.

        Args:
            artifact_id: ID of artifact to find relations for
            relationship_type: Optional filter for relationship type
            limit: Maximum number of results

        Returns:
            List of related artifacts
        """
        relationships = await self.lineage.get_relationships(source_id=artifact_id)

        # Filter by type if specified
        if relationship_type:
            relationships = [
                r for r in relationships if r.relationship_type == relationship_type
            ]

        results: list[GraphResult] = []
        for rel in relationships[:limit]:
            entry = await self.registry.get(rel.target_id)
            if entry:
                results.append(
                    GraphResult(
                        id=rel.target_id,
                        entry=entry,
                        relationship=rel.relationship_type.value,
                        path_length=1,
                        path=[artifact_id, rel.target_id],
                        explanation=f"Related via {rel.relationship_type.value}",
                    )
                )

        return results

    # Private methods

    async def _find_downstream_compatible(
        self, entry: CatalogEntry, limit: int
    ) -> list[GraphResult]:
        """Find agents that can receive this artifact's output."""
        if not entry.output_type:
            return []

        results: list[GraphResult] = []
        all_agents = await self.registry.list()

        for candidate in all_agents:
            if candidate.entity_type != EntityType.AGENT or candidate.id == entry.id:
                continue

            if not candidate.input_type:
                continue

            # Check if our output is compatible with their input
            try:
                compatible = await self.lattice.can_compose(entry.id, candidate.id)
                if compatible.compatible:
                    results.append(
                        GraphResult(
                            id=candidate.id,
                            entry=candidate,
                            relationship="downstream_compatible",
                            path_length=1,
                            path=[entry.id, candidate.id],
                            explanation=f"Can compose: {entry.output_type} → {candidate.input_type}",
                        )
                    )
            except Exception:
                # Type not in lattice, fall back to exact match
                if entry.output_type == candidate.input_type:
                    results.append(
                        GraphResult(
                            id=candidate.id,
                            entry=candidate,
                            relationship="downstream_compatible",
                            path_length=1,
                            path=[entry.id, candidate.id],
                            explanation=f"Exact type match: {entry.output_type}",
                        )
                    )

        return results[:limit]

    async def _find_upstream_compatible(
        self, entry: CatalogEntry, limit: int
    ) -> list[GraphResult]:
        """Find agents that can feed into this artifact's input."""
        if not entry.input_type:
            return []

        results: list[GraphResult] = []
        all_agents = await self.registry.list()

        for candidate in all_agents:
            if candidate.entity_type != EntityType.AGENT or candidate.id == entry.id:
                continue

            if not candidate.output_type:
                continue

            # Check if their output is compatible with our input
            try:
                compatible = await self.lattice.can_compose(candidate.id, entry.id)
                if compatible.compatible:
                    results.append(
                        GraphResult(
                            id=candidate.id,
                            entry=candidate,
                            relationship="upstream_compatible",
                            path_length=1,
                            path=[candidate.id, entry.id],
                            explanation=f"Can compose: {candidate.output_type} → {entry.input_type}",
                        )
                    )
            except Exception:
                # Type not in lattice, fall back to exact match
                if candidate.output_type == entry.input_type:
                    results.append(
                        GraphResult(
                            id=candidate.id,
                            entry=candidate,
                            relationship="upstream_compatible",
                            path_length=1,
                            path=[candidate.id, entry.id],
                            explanation=f"Exact type match: {candidate.output_type}",
                        )
                    )

        return results[:limit]


# Convenience function


async def create_graph_brain(
    registry: Registry, lineage: LineageGraph, lattice: TypeLattice
) -> GraphBrain:
    """Create a graph search brain.

    Args:
        registry: Catalog registry
        lineage: Lineage graph
        lattice: Type lattice

    Returns:
        GraphBrain instance
    """
    return GraphBrain(registry, lineage, lattice)
