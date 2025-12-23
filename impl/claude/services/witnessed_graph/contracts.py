"""
WitnessedGraph AGENTESE Contract Definitions.

Defines request and response types for WitnessedGraph @node contracts.
These enable BE/FE contract synchronization via AGENTESE discovery.

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest)
- Contract() for query aspects (neighbors, evidence, trace, search)

Types here are used by:
1. @node(contracts={...}) in node.py
2. /discover?include_schemas=true endpoint
3. web/scripts/sync-types.ts for FE type generation

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass, field

# =============================================================================
# Edge Response (Shared)
# =============================================================================


@dataclass(frozen=True)
class EdgeResponse:
    """A single edge in responses."""

    kind: str
    source_path: str
    target_path: str
    origin: str
    confidence: float = 1.0
    context: str | None = None
    line_number: int | None = None
    mark_id: str | None = None


# =============================================================================
# Manifest Response
# =============================================================================


@dataclass(frozen=True)
class GraphManifestResponse:
    """Response for graph manifest."""

    total_edges: int
    sources: int
    origin: str
    by_origin: dict[str, int]
    by_kind: dict[str, int]
    # Event-driven update tracking (for UI refresh)
    last_update_at: str  # ISO timestamp
    update_count: int


# =============================================================================
# Neighbors Types
# =============================================================================


@dataclass(frozen=True)
class NeighborsRequest:
    """Request for neighbors query."""

    path: str


@dataclass(frozen=True)
class NeighborsResponse:
    """Response for neighbors query."""

    path: str
    incoming: list[EdgeResponse]
    outgoing: list[EdgeResponse]
    total: int


# =============================================================================
# Evidence Types
# =============================================================================


@dataclass(frozen=True)
class EvidenceRequest:
    """Request for evidence query."""

    spec_path: str


@dataclass(frozen=True)
class EvidenceResponse:
    """Response for evidence query."""

    spec_path: str
    evidence: list[EdgeResponse]
    count: int
    by_kind: dict[str, int]


# =============================================================================
# Trace Types
# =============================================================================


@dataclass(frozen=True)
class TraceRequest:
    """Request for trace query."""

    start: str
    end: str
    max_depth: int = 5


@dataclass(frozen=True)
class TracePathResponse:
    """A single path in trace response."""

    edges: list[EdgeResponse]
    length: int
    nodes: list[str]


@dataclass(frozen=True)
class TraceResponse:
    """Response for trace query."""

    start: str
    end: str
    paths: list[TracePathResponse]
    found: bool


# =============================================================================
# Search Types
# =============================================================================


@dataclass(frozen=True)
class SearchRequest:
    """Request for search query."""

    query: str
    limit: int = 100


@dataclass(frozen=True)
class SearchResponse:
    """Response for search query."""

    query: str
    edges: list[EdgeResponse]
    count: int


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Shared
    "EdgeResponse",
    # Manifest
    "GraphManifestResponse",
    # Neighbors
    "NeighborsRequest",
    "NeighborsResponse",
    # Evidence
    "EvidenceRequest",
    "EvidenceResponse",
    # Trace
    "TraceRequest",
    "TracePathResponse",
    "TraceResponse",
    # Search
    "SearchRequest",
    "SearchResponse",
]
