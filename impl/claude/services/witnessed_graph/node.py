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

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import BaseLogosNode, BasicRendering, Observer, Renderable
from protocols.agentese.registry import node

from .types import EdgeKind

if TYPE_CHECKING:
    from protocols.agentese.umwelt import Umwelt  # type: ignore[import-untyped]

    from .service import WitnessedGraphService


# =============================================================================
# Request/Response Models
# =============================================================================


class GraphManifestResponse(BaseModel):
    """Response for graph manifest."""

    total_edges: int = Field(description="Total edges in unified graph")
    sources: int = Field(description="Number of composed sources")
    origin: str = Field(description="Combined origin string")
    by_origin: dict[str, int] = Field(description="Edge count by source")
    by_kind: dict[str, int] = Field(description="Edge count by kind")


class NeighborsRequest(BaseModel):
    """Request for neighbors query."""

    path: str = Field(description="Path to find neighbors for")


class EdgeResponse(BaseModel):
    """A single edge in responses."""

    kind: str = Field(description="Edge type (IMPORTS, EVIDENCE, etc.)")
    source_path: str = Field(description="Origin node path")
    target_path: str = Field(description="Target node path")
    origin: str = Field(description="Source system (sovereign, witness, spec_ledger)")
    context: str | None = Field(None, description="Surrounding context")
    line_number: int | None = Field(None, description="Line number if known")
    confidence: float = Field(1.0, description="Confidence score 0.0-1.0")
    mark_id: str | None = Field(None, description="Witness mark ID if from witness")


class NeighborsResponse(BaseModel):
    """Response for neighbors query."""

    path: str = Field(description="Queried path")
    incoming: list[EdgeResponse] = Field(description="Edges pointing to this path")
    outgoing: list[EdgeResponse] = Field(description="Edges from this path")
    total: int = Field(description="Total connected edges")


class EvidenceRequest(BaseModel):
    """Request for evidence query."""

    spec_path: str = Field(description="Spec path to find evidence for")


class EvidenceResponse(BaseModel):
    """Response for evidence query."""

    spec_path: str = Field(description="Queried spec path")
    evidence: list[EdgeResponse] = Field(description="Evidence edges")
    count: int = Field(description="Total evidence count")
    by_kind: dict[str, int] = Field(description="Count by evidence type")


class TraceRequest(BaseModel):
    """Request for trace query."""

    start: str = Field(description="Starting node path")
    end: str = Field(description="Ending node path")
    max_depth: int = Field(5, description="Maximum path length")


class TracePathResponse(BaseModel):
    """A single path in trace response."""

    edges: list[EdgeResponse] = Field(description="Edges in the path")
    length: int = Field(description="Number of hops")
    nodes: list[str] = Field(description="Node paths in order")


class TraceResponse(BaseModel):
    """Response for trace query."""

    start: str = Field(description="Starting path")
    end: str = Field(description="Ending path")
    paths: list[TracePathResponse] = Field(description="Found paths")
    found: bool = Field(description="Whether any path was found")


class SearchRequest(BaseModel):
    """Request for search query."""

    query: str = Field(description="Search string")
    limit: int = Field(100, description="Maximum results")


class SearchResponse(BaseModel):
    """Response for search query."""

    query: str = Field(description="Search string")
    edges: list[EdgeResponse] = Field(description="Matching edges")
    count: int = Field(description="Number of results")


# =============================================================================
# GraphNode
# =============================================================================


def _edge_to_response(edge: Any) -> EdgeResponse:
    """Convert HyperEdge to EdgeResponse."""
    return EdgeResponse(
        kind=edge.kind.name,
        source_path=edge.source_path,
        target_path=edge.target_path,
        origin=edge.origin,
        context=edge.context,
        line_number=edge.line_number,
        confidence=edge.confidence,
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
            content=response.model_dump_json(indent=2),
            metadata=response.model_dump(),
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
