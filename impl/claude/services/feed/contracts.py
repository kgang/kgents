"""
Feed AGENTESE Contract Definitions.

Defines request and response types for Feed @node contracts.
These enable BE/FE contract synchronization via AGENTESE discovery.

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest, cosmos, coherent)
- Contract() for mutation aspects (future: mark_seen, dismiss)

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
class FeedManifestResponse:
    """Feed health status manifest response."""

    total_items: int
    cosmos_count: int
    coherent_count: int
    contradiction_count: int
    avg_loss: float
    storage_backend: str


# === K-Block Item ===


@dataclass(frozen=True)
class FeedKBlockItem:
    """Single K-Block item in the feed."""

    id: str
    title: str
    content: str
    layer: int
    loss: float
    author: str
    created_at: str
    updated_at: str
    tags: list[str]
    principles: list[str]
    edge_count: int
    preview: str | None = None


# === Cosmos Response (all K-Blocks) ===


@dataclass(frozen=True)
class CosmosRequest:
    """Request for cosmos feed (all K-Blocks)."""

    offset: int = 0
    limit: int = 20
    ranking: str = (
        "chronological"  # chronological, loss-ascending, loss-descending, engagement, algorithmic
    )


@dataclass(frozen=True)
class CosmosResponse:
    """Response for cosmos feed."""

    items: list[FeedKBlockItem]
    total: int
    has_more: bool
    offset: int
    limit: int
    ranking: str


# === Coherent Response (low-loss items) ===


@dataclass(frozen=True)
class CoherentRequest:
    """Request for coherent feed (low-loss items)."""

    offset: int = 0
    limit: int = 20
    max_loss: float = 0.2


@dataclass(frozen=True)
class CoherentResponse:
    """Response for coherent feed."""

    items: list[FeedKBlockItem]
    total: int
    has_more: bool
    offset: int
    limit: int
    max_loss: float


# === Contradictions Response ===


@dataclass(frozen=True)
class ContradictionPair:
    """Pair of contradicting K-Blocks."""

    id: str
    block_a: FeedKBlockItem
    block_b: FeedKBlockItem
    conflict_type: str  # "principle", "claim", "temporal"
    confidence: float
    discovered_at: str


@dataclass(frozen=True)
class ContradictionsRequest:
    """Request for contradictions feed."""

    offset: int = 0
    limit: int = 20


@dataclass(frozen=True)
class ContradictionsResponse:
    """Response for contradictions feed."""

    pairs: list[ContradictionPair]
    total: int
    has_more: bool
    offset: int
    limit: int


# === Exports ===

__all__ = [
    # Manifest
    "FeedManifestResponse",
    # Items
    "FeedKBlockItem",
    # Cosmos
    "CosmosRequest",
    "CosmosResponse",
    # Coherent
    "CoherentRequest",
    "CoherentResponse",
    # Contradictions
    "ContradictionPair",
    "ContradictionsRequest",
    "ContradictionsResponse",
]
