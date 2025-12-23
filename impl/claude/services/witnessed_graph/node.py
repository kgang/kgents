"""
WitnessedGraph AGENTESE Node: @node("concept.graph")

Exposes WitnessedGraphService through the universal AGENTESE protocol.
All transports (HTTP, WebSocket, CLI) collapse to this interface.

Philosophy:
    "Three sources, one graph. Query the unified truth."

AGENTESE Path: concept.graph
    - concept.graph.manifest  → Graph stats and source info
    - concept.graph.neighbors → Edges connected to a path
    - concept.graph.evidence  → Evidence supporting a spec
    - concept.graph.trace     → Path between nodes
    - concept.graph.search    → Search edges by query
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import BaseLogosNode, BasicRendering, Observer, Renderable
from protocols.agentese.registry import node

from .contracts import (
    EdgeResponse,
    EvidenceRequest,
    EvidenceResponse,
    GraphManifestResponse,
    NeighborsRequest,
    NeighborsResponse,
    SearchRequest,
    SearchResponse,
    TracePathResponse,
    TraceRequest,
    TraceResponse,
)

if TYPE_CHECKING:
    from protocols.agentese.umwelt import Umwelt  # type: ignore[import-untyped]

    from .service import WitnessedGraphService


# =============================================================================
# GraphNode
# =============================================================================


def _edge_to_response(edge: Any) -> EdgeResponse:
    """Convert HyperEdge to EdgeResponse dataclass."""
    return EdgeResponse(
        kind=edge.kind.name,
        source_path=edge.source_path,
        target_path=edge.target_path,
        origin=edge.origin,
        confidence=edge.confidence,
        context=edge.context,
        line_number=edge.line_number,
        mark_id=edge.mark_id,
    )


@node(
    "concept.graph",
    description="WitnessedGraph - Unified edge composition from Sovereign, Witness, and SpecLedger",
    dependencies=("witnessed_graph_service",),
    contracts={
        # Perception aspects (Response only)
        "manifest": Response(GraphManifestResponse),
        # Query aspects (Contract with request + response)
        "neighbors": Contract(NeighborsRequest, NeighborsResponse),
        "evidence": Contract(EvidenceRequest, EvidenceResponse),
        "trace": Contract(TraceRequest, TraceResponse),
        "search": Contract(SearchRequest, SearchResponse),
    },
    examples=[
        ("manifest", {}, "Get graph statistics"),
        ("neighbors", {"path": "spec/agents/d-gent.md"}, "Get edges connected to spec"),
        ("evidence", {"spec_path": "spec/protocols/k-block.md"}, "Get evidence for spec"),
        ("trace", {"start": "impl/service.py", "end": "spec/service.md"}, "Find path"),
        ("search", {"query": "witness"}, "Search edges"),
    ],
)
class GraphNode(BaseLogosNode):
    """
    AGENTESE node for WitnessedGraph Crown Jewel (9th Jewel).

    Exposes the unified graph through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/concept/graph/neighbors
        {"path": "spec/agents/d-gent.md"}

        # Via Logos directly
        await logos.invoke("concept.graph.neighbors", observer, path="spec/...")

        # Via CLI
        kg graph neighbors spec/agents/d-gent.md
    """

    def __init__(self, witnessed_graph_service: "WitnessedGraphService") -> None:
        """
        Initialize GraphNode.

        Args:
            witnessed_graph_service: The unified graph service (injected by container)
        """
        self._graph = witnessed_graph_service

    @property
    def handle(self) -> str:
        """Return the AGENTESE handle for this node."""
        return "concept.graph"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        WitnessedGraph is read-only—all archetypes get full query access.
        The graph unifies evidence from multiple sources; querying it
        is always safe (no mutations).
        """
        # All archetypes can query the graph
        return ("manifest", "neighbors", "evidence", "trace", "search")

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to the appropriate method.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if aspect == "manifest":
            return await self.manifest(observer, **kwargs)
        elif aspect == "neighbors":
            path = kwargs.get("path", "")
            return await self.neighbors(path)
        elif aspect == "evidence":
            spec_path = kwargs.get("spec_path", "")
            return await self.evidence(spec_path)
        elif aspect == "trace":
            start = kwargs.get("start", "")
            end = kwargs.get("end", "")
            max_depth = kwargs.get("max_depth", 5)
            return await self.trace(start, end, max_depth)
        elif aspect == "search":
            query = kwargs.get("query", "")
            limit = kwargs.get("limit", 100)
            return await self.search(query, limit)
        else:
            return {"error": f"Unknown aspect: {aspect}"}

    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Get graph statistics and source information.

        Returns:
            BasicRendering with graph stats
        """
        stats = await self._graph.stats()
        response = GraphManifestResponse(
            total_edges=stats["total_edges"],
            sources=stats["sources"],
            origin=stats["origin"],
            by_origin=stats["by_origin"],
            by_kind=stats["by_kind"],
        )
        return BasicRendering(
            summary=f"WitnessedGraph: {stats['total_edges']} edges from {stats['sources']} sources",
            content=json.dumps(asdict(response), indent=2),
            metadata=asdict(response),
        )

    async def neighbors(self, path: str) -> NeighborsResponse:
        """
        Get edges connected to a path.

        Args:
            path: The node path to query

        Returns:
            NeighborsResponse with incoming and outgoing edges
        """
        result = await self._graph.neighbors(path)
        return NeighborsResponse(
            path=result.path,
            incoming=[_edge_to_response(e) for e in result.incoming],
            outgoing=[_edge_to_response(e) for e in result.outgoing],
            total=result.total,
        )

    async def evidence(self, spec_path: str) -> EvidenceResponse:
        """
        Get evidence supporting a spec.

        Args:
            spec_path: Path to the spec

        Returns:
            EvidenceResponse with evidence edges
        """
        result = await self._graph.evidence_for(spec_path)
        return EvidenceResponse(
            spec_path=result.spec_path,
            evidence=[_edge_to_response(e) for e in result.evidence],
            count=result.count,
            by_kind=result.by_kind,
        )

    async def trace(
        self,
        start: str,
        end: str,
        max_depth: int = 5,
    ) -> TraceResponse:
        """
        Find paths between nodes.

        Args:
            start: Starting node path
            end: Ending node path
            max_depth: Maximum path length

        Returns:
            TraceResponse with found paths
        """
        paths = await self._graph.trace_path(start, end, max_depth)
        return TraceResponse(
            start=start,
            end=end,
            paths=[
                TracePathResponse(
                    edges=[_edge_to_response(e) for e in p.edges],
                    length=p.length,
                    nodes=p.nodes,
                )
                for p in paths
            ],
            found=len(paths) > 0,
        )

    async def search(
        self,
        query: str,
        limit: int = 100,
    ) -> SearchResponse:
        """
        Search edges by query.

        Args:
            query: Search string
            limit: Maximum results

        Returns:
            SearchResponse with matching edges
        """
        edges = await self._graph.search(query, limit)
        return SearchResponse(
            query=query,
            edges=[_edge_to_response(e) for e in edges],
            count=len(edges),
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = ["GraphNode"]
