"""
WitnessedGraphService: Crown Jewel for unified graph queries.

This service composes all edge sources into a single queryable interface:
    graph = sovereign >> witness >> spec_ledger

Design Principle:
    "Three sources, one graph. Query the unified truth."

Crown Jewel Patterns Applied:
- Pattern 1: Container Owns Workflow (service owns composed graph)
- Pattern 4: Dual-Channel Output (rich edges + stats)
- Pattern 14: Full Stack Agent (service → AGENTESE → CLI)
- Pattern 9: Event-Driven Integration (bus subscription for live updates)

AGENTESE: concept.graph.neighbors, concept.graph.evidence, concept.graph.trace

Loop Closure (2025-12-23):
    K-Block save → Witness mark → Bus event → Graph update → UI refresh
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .composition import ComposedSource
from .types import EdgeKind, HyperEdge

if TYPE_CHECKING:
    from .protocol import EdgeSourceProtocol
    from .sources import SovereignSource, SpecLedgerSource, WitnessSource

logger = logging.getLogger(__name__)


# =============================================================================
# Result Types
# =============================================================================


@dataclass
class NeighborResult:
    """Result of a neighbors query."""

    path: str
    incoming: list[HyperEdge] = field(default_factory=list)
    outgoing: list[HyperEdge] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Total number of connected edges."""
        return len(self.incoming) + len(self.outgoing)

    def by_origin(self) -> dict[str, list[HyperEdge]]:
        """Group all edges by origin."""
        result: dict[str, list[HyperEdge]] = defaultdict(list)
        for edge in self.incoming + self.outgoing:
            result[edge.origin].append(edge)
        return dict(result)

    def by_kind(self) -> dict[EdgeKind, list[HyperEdge]]:
        """Group all edges by kind."""
        result: dict[EdgeKind, list[HyperEdge]] = defaultdict(list)
        for edge in self.incoming + self.outgoing:
            result[edge.kind].append(edge)
        return dict(result)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": self.path,
            "incoming": [e.to_dict() for e in self.incoming],
            "outgoing": [e.to_dict() for e in self.outgoing],
            "total": self.total,
        }


@dataclass
class EvidenceResult:
    """Result of an evidence query for a spec."""

    spec_path: str
    evidence: list[HyperEdge] = field(default_factory=list)

    @property
    def count(self) -> int:
        """Number of evidence edges."""
        return len(self.evidence)

    @property
    def by_kind(self) -> dict[str, int]:
        """Count evidence by kind."""
        result: dict[str, int] = defaultdict(int)
        for edge in self.evidence:
            result[edge.kind.name] += 1
        return dict(result)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "spec_path": self.spec_path,
            "evidence": [e.to_dict() for e in self.evidence],
            "count": self.count,
            "by_kind": self.by_kind,
        }


@dataclass
class TracePath:
    """A path from source to target through the graph."""

    edges: list[HyperEdge] = field(default_factory=list)

    @property
    def length(self) -> int:
        """Number of hops."""
        return len(self.edges)

    @property
    def nodes(self) -> list[str]:
        """All nodes in the path."""
        if not self.edges:
            return []
        result = [self.edges[0].source_path]
        for edge in self.edges:
            result.append(edge.target_path)
        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "edges": [e.to_dict() for e in self.edges],
            "length": self.length,
            "nodes": self.nodes,
        }


# =============================================================================
# WitnessedGraphService
# =============================================================================


class WitnessedGraphService:
    """
    Crown Jewel for unified graph queries.

    Composes multiple edge sources and provides high-level query methods:
    - neighbors: Get all edges connected to a path
    - evidence_for: Get evidence supporting a spec
    - trace_path: Find paths between nodes

    Event-Driven Integration:
        Subscribes to bus events to track when sources change:
        - witness.kblock.saved → Graph may have new edges
        - witness.spec.scanned → Spec ledger updated

    Example:
        >>> service = WitnessedGraphService(sovereign, witness, spec)
        >>> await service.wire_bus()  # Enable live updates
        >>> result = await service.neighbors("spec/agents/d-gent.md")
        >>> print(f"Connected to {result.total} edges")
    """

    def __init__(
        self,
        *sources: "EdgeSourceProtocol",
        sovereign_source: "SovereignSource | None" = None,
        witness_source: "WitnessSource | None" = None,
        spec_source: "SpecLedgerSource | None" = None,
    ) -> None:
        """
        Create the service from edge sources.

        Can be initialized with:
        - Positional sources: WitnessedGraphService(s1, s2, s3)
        - Named sources: WitnessedGraphService(sovereign_source=s1, ...)
        - Mix of both
        """
        all_sources = list(sources)
        if sovereign_source:
            all_sources.append(sovereign_source)
        if witness_source:
            all_sources.append(witness_source)
        if spec_source:
            all_sources.append(spec_source)

        # Compose all sources
        self._graph = ComposedSource(all_sources)

        # Event-driven update tracking (for UI refresh)
        self._last_update_at: datetime = datetime.now(timezone.utc)
        self._update_count: int = 0
        self._bus_unsubs: list[Any] = []

    @property
    def graph(self) -> ComposedSource:
        """The composed graph of all sources."""
        return self._graph

    @property
    def origin(self) -> str:
        """Combined origin of all sources."""
        return self._graph.origin

    async def neighbors(self, path: str) -> NeighborResult:
        """
        Get all edges connected to a path.

        Returns both incoming (edges TO path) and outgoing (edges FROM path).

        Args:
            path: The node path to query

        Returns:
            NeighborResult with incoming and outgoing edges
        """
        result = NeighborResult(path=path)

        # Get outgoing edges (from path)
        async for edge in self._graph.edges_from(path):
            result.outgoing.append(edge)

        # Get incoming edges (to path)
        async for edge in self._graph.edges_to(path):
            result.incoming.append(edge)

        return result

    async def evidence_for(self, spec_path: str) -> EvidenceResult:
        """
        Get all evidence supporting a spec.

        Evidence includes:
        - EVIDENCE edges (explicit evidence marks)
        - IMPLEMENTS edges (code implementations)
        - Test references

        Args:
            spec_path: Path to the spec

        Returns:
            EvidenceResult with all evidence edges
        """
        result = EvidenceResult(spec_path=spec_path)

        # Evidence kinds
        evidence_kinds = {
            EdgeKind.EVIDENCE,
            EdgeKind.IMPLEMENTS,
            EdgeKind.DECISION,
            EdgeKind.EUREKA,
        }

        # Get edges pointing to this spec
        async for edge in self._graph.edges_to(spec_path):
            if edge.kind in evidence_kinds:
                result.evidence.append(edge)

        return result

    async def trace_path(
        self,
        start: str,
        end: str,
        max_depth: int = 5,
    ) -> list[TracePath]:
        """
        Find paths from start to end in the graph.

        Uses BFS to find shortest paths, returns all paths up to max_depth.

        Args:
            start: Starting node path
            end: Ending node path
            max_depth: Maximum path length

        Returns:
            List of TracePath instances (empty if no path found)
        """
        if start == end:
            return [TracePath()]  # Empty path

        # BFS with path tracking
        visited: set[str] = set()
        queue: list[tuple[str, list[HyperEdge]]] = [(start, [])]
        paths: list[TracePath] = []

        while queue:
            current, path = queue.pop(0)

            if len(path) >= max_depth:
                continue

            if current in visited:
                continue
            visited.add(current)

            async for edge in self._graph.edges_from(current):
                new_path = path + [edge]

                if edge.target_path == end:
                    paths.append(TracePath(edges=new_path))
                    continue

                if edge.target_path not in visited:
                    queue.append((edge.target_path, new_path))

        return paths

    async def search(self, query: str, limit: int = 100) -> list[HyperEdge]:
        """
        Search all sources for edges matching query.

        Args:
            query: Search string
            limit: Maximum results

        Returns:
            List of matching HyperEdge instances
        """
        results: list[HyperEdge] = []
        async for edge in self._graph.search(query):
            results.append(edge)
            if len(results) >= limit:
                break
        return results

    async def all_edges(self, limit: int = 10000) -> list[HyperEdge]:
        """
        Get all edges in the graph.

        Args:
            limit: Maximum edges to return

        Returns:
            List of all HyperEdge instances
        """
        results: list[HyperEdge] = []
        async for edge in self._graph.all_edges():
            results.append(edge)
            if len(results) >= limit:
                break
        return results

    async def stats(self) -> dict[str, Any]:
        """
        Get statistics about the graph.

        Returns:
            Dictionary with edge counts by origin and kind
        """
        edges = await self.all_edges()

        by_origin: dict[str, int] = defaultdict(int)
        by_kind: dict[str, int] = defaultdict(int)

        for edge in edges:
            by_origin[edge.origin] += 1
            by_kind[edge.kind.name] += 1

        return {
            "total_edges": len(edges),
            "sources": len(self._graph.sources),
            "origin": self.origin,
            "by_origin": dict(by_origin),
            "by_kind": dict(by_kind),
            "last_update_at": self._last_update_at.isoformat(),
            "update_count": self._update_count,
        }

    # =========================================================================
    # Event-Driven Integration (Bus Subscription)
    # =========================================================================

    async def wire_bus(self) -> None:
        """
        Subscribe to bus events for live graph updates.

        Subscribes to:
        - witness.kblock.saved → New edges from K-Block saves
        - witness.spec.scanned → Spec ledger updates

        This enables the closed loop:
            K-Block save → Witness mark → Bus event → Graph update → UI refresh
        """
        try:
            from services.witness.bus import WitnessTopics, get_synergy_bus

            bus = get_synergy_bus()

            # Subscribe to K-Block saves (creates edges via witness marks)
            unsub1 = bus.subscribe(WitnessTopics.KBLOCK_SAVED, self._on_source_change)
            self._bus_unsubs.append(unsub1)

            # Subscribe to spec scans (updates spec ledger edges)
            unsub2 = bus.subscribe(WitnessTopics.SPEC_SCANNED, self._on_source_change)
            self._bus_unsubs.append(unsub2)

            logger.info("WitnessedGraph wired to bus (KBLOCK_SAVED, SPEC_SCANNED)")

        except ImportError:
            logger.warning("Witness bus not available - graph won't receive live updates")

    async def unwire_bus(self) -> None:
        """Unsubscribe from all bus events."""
        for unsub in self._bus_unsubs:
            unsub()
        self._bus_unsubs.clear()
        logger.info("WitnessedGraph unwired from bus")

    async def _on_source_change(self, topic: str, event: Any) -> None:
        """
        Handle source change events.

        Updates the timestamp and count so frontends know to refresh.
        """
        self._last_update_at = datetime.now(timezone.utc)
        self._update_count += 1

        path = event.get("path", "unknown") if isinstance(event, dict) else "unknown"
        logger.debug(f"Graph source changed: {topic} ({path}), update #{self._update_count}")

    @property
    def last_update_at(self) -> datetime:
        """When the graph was last updated (for UI polling)."""
        return self._last_update_at

    @property
    def update_count(self) -> int:
        """Number of updates since service creation (for cache invalidation)."""
        return self._update_count


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "WitnessedGraphService",
    "NeighborResult",
    "EvidenceResult",
    "TracePath",
]
