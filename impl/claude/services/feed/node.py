"""
Feed AGENTESE Node: @node("self.feed")

Wraps feed operations as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- self.feed.manifest       - Feed health status
- self.feed.cosmos         - All K-Blocks (chronological)
- self.feed.coherent       - Low-loss items (< 0.2 loss)
- self.feed.contradictions - Flagged contradiction pairs

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    CoherentRequest,
    CoherentResponse,
    ContradictionPair,
    ContradictionsRequest,
    ContradictionsResponse,
    CosmosRequest,
    CosmosResponse,
    FeedKBlockItem,
    FeedManifestResponse,
)
from .defaults import COHERENT_FEED, COSMOS_FEED

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Rendering ===


@dataclass(frozen=True)
class FeedManifestRendering:
    """Rendering for feed status manifest."""

    total_items: int
    cosmos_count: int
    coherent_count: int
    contradiction_count: int
    avg_loss: float
    storage_backend: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "feed_manifest",
            "total_items": self.total_items,
            "cosmos_count": self.cosmos_count,
            "coherent_count": self.coherent_count,
            "contradiction_count": self.contradiction_count,
            "avg_loss": self.avg_loss,
            "storage_backend": self.storage_backend,
        }

    def to_text(self) -> str:
        lines = [
            "Feed Status",
            "===========",
            f"Total Items: {self.total_items}",
            f"Cosmos (All): {self.cosmos_count}",
            f"Coherent (loss < 0.2): {self.coherent_count}",
            f"Contradictions: {self.contradiction_count}",
            f"Average Loss: {self.avg_loss:.2%}",
            f"Storage Backend: {self.storage_backend}",
        ]
        return "\n".join(lines)




def _apply_ranking(items: list[FeedKBlockItem], ranking: str) -> list[FeedKBlockItem]:
    """Apply ranking algorithm to items."""
    if ranking == "chronological":
        return sorted(items, key=lambda x: x.updated_at, reverse=True)
    elif ranking == "loss-ascending":
        return sorted(items, key=lambda x: x.loss)
    elif ranking == "loss-descending":
        return sorted(items, key=lambda x: x.loss, reverse=True)
    elif ranking == "engagement":
        return sorted(items, key=lambda x: x.edge_count, reverse=True)
    elif ranking == "algorithmic":
        # Use configurable weights from FeedConfig
        from .config import get_feed_config

        config = get_feed_config()

        def score(item: FeedKBlockItem) -> float:
            # Parse timestamp for recency
            created = datetime.fromisoformat(item.created_at.replace('Z', '+00:00'))
            hours_old = (datetime.now(UTC) - created).total_seconds() / 3600
            recency_score = 1.0 / (1.0 + hours_old / 24)  # Decay over days

            # Attention = edge_count normalized
            attention = min(item.edge_count / 10.0, 1.0)

            # Principles = count of aligned principles
            principles_score = len(item.principles) / 7.0

            # Coherence = 1 - loss
            coherence = 1.0 - item.loss

            return (
                attention * config.attention_weight
                + principles_score * config.principles_weight
                + recency_score * config.recency_weight
                + coherence * config.coherence_weight
            )

        return sorted(items, key=score, reverse=True)
    else:
        return items


# === FeedNode ===


@node(
    "self.feed",
    description="Feed Crown Jewel - universal chronological truth stream",
    dependencies=("feed_service",),  # Inject FeedService
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(FeedManifestResponse),
        # Query aspects (Contract with request + response)
        "cosmos": Contract(CosmosRequest, CosmosResponse),
        "coherent": Contract(CoherentRequest, CoherentResponse),
        "contradictions": Contract(ContradictionsRequest, ContradictionsResponse),
    },
    examples=[
        ("manifest", {}, "Show feed health status"),
        ("cosmos", {"offset": 0, "limit": 20, "ranking": "chronological"}, "Get all K-Blocks"),
        ("coherent", {"offset": 0, "limit": 20, "max_loss": 0.2}, "Get low-loss items"),
        ("contradictions", {"offset": 0, "limit": 10}, "Get contradiction pairs"),
    ],
)
class FeedNode(BaseLogosNode):
    """
    AGENTESE node for Feed Crown Jewel.

    The Feed is the primary interface for browsing K-Blocks.
    All items are ranked by algorithmic scoring: attention + principles + recency + coherence.

    Philosophy:
        "The feed is not a view of data. The feed IS the primary interface."

    Teaching:
        gotcha: FeedNode generates mock data for MVP. Replace _generate_mock_kblocks()
                with real K-Block queries when persistence layer is ready.
                (Evidence: This file)

        gotcha: Ranking algorithm matches Feed.tsx client-side scoring. Keep in sync
                or client filtering will differ from backend ranking.
                (Evidence: _apply_ranking() and Feed.tsx:applyRanking())
    """

    def __init__(self, feed_service=None) -> None:
        """
        Initialize FeedNode.

        Args:
            feed_service: Injected FeedService from container
        """
        from .service import get_feed_service

        self._service = feed_service or get_feed_service()

    @property
    def handle(self) -> str:
        return "self.feed"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Phase 8 Observer Consistency:
        - developer/operator: Full access (all feeds)
        - architect/researcher: Read-only access (all feeds)
        - newcomer/casual: Limited to cosmos and coherent
        - guest: Cosmos only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators, admins
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return ("cosmos", "coherent", "contradictions")

        # Architects/researchers: all feeds
        if archetype_lower in ("architect", "artist", "poet", "researcher", "technical"):
            return ("cosmos", "coherent", "contradictions")

        # Newcomers: cosmos + coherent
        if archetype_lower in ("newcomer", "casual", "reviewer"):
            return ("cosmos", "coherent")

        # Guest: cosmos only
        return ("cosmos",)

    async def manifest(
        self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any
    ) -> Renderable:
        """
        Manifest feed status to observer.

        AGENTESE: self.feed.manifest
        """
        # Get all K-Blocks from storage
        all_kblocks = list(self._service._storage._kblocks.values())

        # Count coherent items (loss < 0.2)
        # TODO: Replace with real Galois loss when computed
        coherent_count = len(all_kblocks)  # Temporary: all items assumed coherent

        avg_loss = 0.0  # TODO: Compute average Galois loss

        return FeedManifestRendering(
            total_items=len(all_kblocks),
            cosmos_count=len(all_kblocks),
            coherent_count=coherent_count,
            contradiction_count=0,  # TODO: Implement contradiction detection
            avg_loss=avg_loss,
            storage_backend="ZeroSeedStorage (in-memory)",
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to feed queries.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if aspect == "cosmos":
            # All K-Blocks with optional ranking
            offset = int(kwargs.get("offset", 0))
            limit = int(kwargs.get("limit", 20))
            ranking = kwargs.get("ranking", "chronological")

            # Create mock user for ranking
            from .service import MockUser

            user = MockUser()

            # Get K-Blocks from service
            result = await self._service.get_cosmos(
                user=user,
                offset=offset,
                limit=limit,
                ranking=ranking,
            )

            # Convert K-Blocks to API format
            return {
                "items": [
                    {
                        "id": str(kb.id),
                        "title": getattr(kb, "title", "Untitled"),
                        "content": kb.content,
                        "layer": getattr(kb, "zero_seed_layer", None),
                        "loss": 0.0,  # TODO: Compute Galois loss
                        "author": getattr(kb, "created_by", "unknown"),
                        "createdAt": kb.created_at.isoformat(),
                        "updatedAt": kb.updated_at.isoformat(),
                        "tags": getattr(kb, "tags", []),
                        "principles": [],  # TODO: Extract from proof
                        "edgeCount": 0,  # TODO: Count edges
                        "preview": kb.content[:100],
                    }
                    for kb in result.items
                ],
                "total": result.total,
                "has_more": result.has_more,
                "offset": result.offset,
                "limit": result.limit,
                "ranking": ranking,
            }

        elif aspect == "coherent":
            # Low-loss items (< max_loss threshold)
            offset = int(kwargs.get("offset", 0))
            limit = int(kwargs.get("limit", 20))
            max_loss = float(kwargs.get("max_loss", 0.2))

            # Create mock user for ranking
            from .service import MockUser

            user = MockUser()

            # Get coherent K-Blocks from service
            result = await self._service.get_coherent(
                user=user,
                offset=offset,
                limit=limit,
                max_loss=max_loss,
            )

            # Convert K-Blocks to API format
            return {
                "items": [
                    {
                        "id": str(kb.id),
                        "title": getattr(kb, "title", "Untitled"),
                        "content": kb.content,
                        "layer": getattr(kb, "zero_seed_layer", None),
                        "loss": 0.0,  # TODO: Compute Galois loss
                        "author": getattr(kb, "created_by", "unknown"),
                        "createdAt": kb.created_at.isoformat(),
                        "updatedAt": kb.updated_at.isoformat(),
                        "tags": getattr(kb, "tags", []),
                        "principles": [],  # TODO: Extract from proof
                        "edgeCount": 0,  # TODO: Count edges
                        "preview": kb.content[:100],
                    }
                    for kb in result.items
                ],
                "total": result.total,
                "has_more": result.has_more,
                "offset": result.offset,
                "limit": result.limit,
                "max_loss": max_loss,
            }

        elif aspect == "contradictions":
            # Flagged contradiction pairs
            offset = kwargs.get("offset", 0)
            limit = kwargs.get("limit", 20)

            # TODO: Implement contradiction detection when edge system ready
            # For now, return empty list (honest about missing functionality)
            return {
                "pairs": [],
                "total": 0,
                "has_more": False,
                "offset": offset,
                "limit": limit,
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "FeedNode",
    "FeedManifestRendering",
]
