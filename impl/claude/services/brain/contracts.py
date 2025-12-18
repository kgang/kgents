"""
Brain AGENTESE Contract Definitions.

Defines request and response types for Brain @node contracts.
These enable BE/FE contract synchronization via AGENTESE discovery.

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest, search, surface)
- Contract() for mutation aspects (capture, delete, heal)

Types here are used by:
1. @node(contracts={...}) in node.py
2. /discover?include_schemas=true endpoint
3. web/scripts/sync-types.ts for FE type generation

See: plans/autopoietic-architecture.md (Phase 7)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# === Manifest Response ===


@dataclass(frozen=True)
class BrainManifestResponse:
    """Brain health status manifest response."""

    total_crystals: int
    vector_count: int
    has_semantic: bool
    coherency_rate: float
    ghosts_healed: int
    storage_path: str
    storage_backend: str


# === Capture Types ===


@dataclass(frozen=True)
class CaptureRequest:
    """Request to capture content to holographic memory."""

    content: str
    tags: list[str] = field(default_factory=list)
    source_type: str = "capture"
    source_ref: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class CaptureResponse:
    """Response after capturing content."""

    crystal_id: str
    content: str
    summary: str
    captured_at: str
    has_embedding: bool
    storage: str
    datum_id: str | None
    tags: list[str]


# === Search Types ===


@dataclass(frozen=True)
class SearchRequest:
    """Request for semantic search."""

    query: str
    limit: int = 10
    tags: list[str] | None = None


@dataclass(frozen=True)
class SearchResultItem:
    """Single search result item."""

    crystal_id: str
    summary: str
    similarity: float
    captured_at: str


@dataclass(frozen=True)
class SearchResponse:
    """Response for semantic search."""

    query: str
    count: int
    results: list[SearchResultItem]


# === Surface Types ===


@dataclass(frozen=True)
class SurfaceRequest:
    """Request for serendipitous surface from the void."""

    context: str | None = None
    entropy: float = 0.7


@dataclass(frozen=True)
class SurfaceItem:
    """Surfaced crystal item."""

    crystal_id: str
    content: str
    summary: str
    similarity: float


@dataclass(frozen=True)
class SurfaceResponse:
    """Response for surface operation."""

    surface: SurfaceItem | None
    entropy: float
    message: str | None = None


# === Get Types ===


@dataclass(frozen=True)
class GetRequest:
    """Request to get specific crystal by ID."""

    crystal_id: str


@dataclass(frozen=True)
class GetResponse:
    """Response for get crystal operation."""

    crystal_id: str
    content: str
    summary: str
    captured_at: str


# === Recent/ByTag Types ===


@dataclass(frozen=True)
class RecentRequest:
    """Request for recent crystals."""

    limit: int = 10


@dataclass(frozen=True)
class ByTagRequest:
    """Request for crystals by tag."""

    tag: str
    limit: int = 10


# === Delete Types ===


@dataclass(frozen=True)
class DeleteRequest:
    """Request to delete a crystal."""

    crystal_id: str


@dataclass(frozen=True)
class DeleteResponse:
    """Response after deleting a crystal."""

    deleted: bool
    crystal_id: str


# === Heal Types ===


@dataclass(frozen=True)
class HealResponse:
    """Response after healing ghost memories."""

    healed: int
    message: str


# === Topology Types ===


@dataclass(frozen=True)
class TopologyNode:
    """A node in the brain topology."""

    id: str
    label: str
    x: float
    y: float
    z: float
    resolution: float
    content: str
    summary: str
    captured_at: str
    tags: list[str]


@dataclass(frozen=True)
class TopologyEdge:
    """An edge between topology nodes."""

    source: str
    target: str
    similarity: float


@dataclass(frozen=True)
class TopologyStats:
    """Statistics for brain topology."""

    concept_count: int
    edge_count: int
    hub_count: int
    gap_count: int
    avg_resolution: float


@dataclass(frozen=True)
class TopologyRequest:
    """Request for brain topology."""

    similarity_threshold: float = 0.3


@dataclass(frozen=True)
class TopologyResponse:
    """Response for brain topology visualization."""

    nodes: list[TopologyNode]
    edges: list[TopologyEdge]
    gaps: list[dict[str, Any]]  # Knowledge gaps
    hub_ids: list[str]
    stats: TopologyStats


# === Exports ===

__all__ = [
    # Manifest
    "BrainManifestResponse",
    # Capture
    "CaptureRequest",
    "CaptureResponse",
    # Search
    "SearchRequest",
    "SearchResultItem",
    "SearchResponse",
    # Surface
    "SurfaceRequest",
    "SurfaceItem",
    "SurfaceResponse",
    # Get
    "GetRequest",
    "GetResponse",
    # Recent/ByTag
    "RecentRequest",
    "ByTagRequest",
    # Delete
    "DeleteRequest",
    "DeleteResponse",
    # Heal
    "HealResponse",
    # Topology
    "TopologyNode",
    "TopologyEdge",
    "TopologyStats",
    "TopologyRequest",
    "TopologyResponse",
]
