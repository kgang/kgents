"""
FeedService: Access layer for algorithmic K-Block discovery.

Provides filtered, ranked K-Block streams with pagination.

Philosophy:
    "The algorithm adapts to the user, not the user to the algorithm."
    (Linear Adaptation principle)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from services.k_block.core.kblock import KBlock
from services.k_block.zero_seed_storage import ZeroSeedStorage

from .core import Feed, FeedFilter, FeedRanking, FeedSource, User
from .ranking import rank_kblocks

if TYPE_CHECKING:
    pass


# =============================================================================
# Mock User
# =============================================================================


@dataclass
class MockUser:
    """Mock user for testing."""

    id: str = "guest"
    principles: tuple[str, ...] = ()


# =============================================================================
# FeedService
# =============================================================================


@dataclass
class FeedResult:
    """Result of a feed query."""

    items: list[KBlock]
    total: int
    has_more: bool
    offset: int
    limit: int


class FeedService:
    """
    Service for accessing filtered, ranked K-Block streams.

    Integrates:
    - ZeroSeedStorage for K-Block access
    - FeedRanking for algorithmic scoring
    - Pagination for infinite scroll

    Example:
        service = FeedService(storage)
        result = await service.get_feed(
            feed=Feed(...),
            user=user,
            offset=0,
            limit=20,
        )
    """

    def __init__(self, storage: ZeroSeedStorage):
        """
        Initialize FeedService.

        Args:
            storage: K-Block storage backend
        """
        self._storage = storage

    async def get_feed(
        self,
        feed: Feed,
        user: User,
        offset: int = 0,
        limit: int = 20,
    ) -> FeedResult:
        """
        Get filtered, ranked K-Blocks for a feed.

        Args:
            feed: Feed configuration
            user: User context for ranking
            offset: Pagination offset
            limit: Maximum items to return

        Returns:
            FeedResult with items and pagination info
        """
        # Get all K-Blocks from storage
        all_kblocks = list(self._storage._kblocks.values())

        # Filter by sources and filters
        filtered = [kb for kb in all_kblocks if feed.should_include(kb)]

        # Rank using algorithm
        scored = await rank_kblocks(
            kblocks=filtered,
            user=user,
            attention_weight=feed.ranking.attention_weight,
            principles_weight=feed.ranking.principles_weight,
            recency_weight=feed.ranking.recency_weight,
            coherence_weight=feed.ranking.coherence_weight,
        )

        # Extract just the K-Blocks (scores discarded for now)
        ranked = [kb for kb, _score in scored]

        # Paginate
        total = len(ranked)
        items = ranked[offset : offset + limit]
        has_more = (offset + limit) < total

        return FeedResult(
            items=items,
            total=total,
            has_more=has_more,
            offset=offset,
            limit=limit,
        )

    async def get_cosmos(
        self,
        user: User,
        offset: int = 0,
        limit: int = 20,
        ranking: str = "chronological",
    ) -> FeedResult:
        """
        Get all K-Blocks (cosmos feed).

        Args:
            user: User context
            offset: Pagination offset
            limit: Maximum items
            ranking: Ranking strategy ("chronological", "coherence", "principles")

        Returns:
            FeedResult with all K-Blocks
        """
        # Build feed config for cosmos
        if ranking == "coherence":
            feed_ranking = FeedRanking(
                coherence_weight=1.0,
                recency_weight=0.0,
            )
        elif ranking == "principles":
            feed_ranking = FeedRanking(
                principles_weight=1.0,
                recency_weight=0.3,
            )
        else:  # chronological (default)
            feed_ranking = FeedRanking(
                recency_weight=1.0,
            )

        feed = Feed(
            id="cosmos",
            name="Cosmos",
            description="All K-Blocks",
            sources=(FeedSource(type="all"),),
            ranking=feed_ranking,
        )

        return await self.get_feed(feed, user, offset, limit)

    async def get_coherent(
        self,
        user: User,
        offset: int = 0,
        limit: int = 20,
        max_loss: float = 0.2,
    ) -> FeedResult:
        """
        Get low-loss K-Blocks (coherent feed).

        Args:
            user: User context
            offset: Pagination offset
            limit: Maximum items
            max_loss: Maximum Galois loss threshold

        Returns:
            FeedResult with coherent K-Blocks
        """
        # TODO: Add FeedFilter for loss when Galois loss is computed
        # For now, just return chronological
        feed = Feed(
            id="coherent",
            name="Coherent",
            description=f"K-Blocks with loss < {max_loss}",
            sources=(FeedSource(type="all"),),
            ranking=FeedRanking(
                coherence_weight=1.0,
                recency_weight=0.3,
            ),
        )

        return await self.get_feed(feed, user, offset, limit)


# =============================================================================
# Singleton
# =============================================================================


_feed_service: FeedService | None = None


def get_feed_service(storage: ZeroSeedStorage | None = None) -> FeedService:
    """
    Get or create singleton FeedService.

    Args:
        storage: Optional storage backend (creates default if None)

    Returns:
        FeedService singleton
    """
    global _feed_service

    if _feed_service is None:
        if storage is None:
            storage = ZeroSeedStorage()
        _feed_service = FeedService(storage)

    return _feed_service


__all__ = [
    "FeedService",
    "FeedResult",
    "MockUser",
    "get_feed_service",
]
