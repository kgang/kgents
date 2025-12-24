"""
Unified Query Service: Orchestrates parallel queries across all entity types.

> *"The file is a lie. There is only the graph."*

The UnifiedQueryService:
1. Accepts filter criteria (types, date range, author, tags, search)
2. Queries relevant adapters in parallel
3. Merges and sorts results chronologically
4. Returns unified stream of events

Design Principles:
- Pattern 1: Container Owns Workflow (service owns query orchestration)
- Pattern 6: Async-Safe Event Emission (parallel adapter calls)
- Pattern 15: No Hollow Services (always go through DI)

Migration to Universe:
- Uses Universe instead of SQLAlchemy session
- Adapters query Crystal system via Universe.query()
- Parallel queries still work (Universe is async-safe)

Teaching:
    gotcha: Empty types filter means ALL types, not NO types.
    gotcha: Parallel queries can fail independently. Use gather(return_exceptions=True).
    gotcha: Total count requires summing across all requested types.
"""

from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime
from typing import TYPE_CHECKING

from agents.d.universe import Universe, get_universe

from .adapters import (
    CrystalAdapter,
    EntityAdapter,
    EvidenceAdapter,
    LemmaAdapter,
    MarkAdapter,
    TeachingAdapter,
    TrailAdapter,
    get_adapter,
    get_all_adapters,
)
from .contracts import (
    EntityType,
    ExplorerManifestResponse,
    ListEventsRequest,
    ListEventsResponse,
    SearchEventsRequest,
    SearchEventsResponse,
    SearchResult,
    StreamFilters,
    UnifiedEvent,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class UnifiedQueryService:
    """
    Orchestrates parallel queries across all entity types.

    Usage:
        >>> service = UnifiedQueryService(universe)
        >>> response = await service.list_events(ListEventsRequest(limit=50))
        >>> print(f"Got {len(response.events)} events")

    The service:
    1. Determines which adapters to query based on filters
    2. Runs adapter queries in parallel
    3. Merges results and sorts by timestamp
    4. Returns paginated response
    """

    def __init__(self, universe: Universe | None = None):
        """
        Initialize with Universe instance.

        Args:
            universe: Universe instance for data access. If None, uses singleton.
        """
        self.universe = universe or get_universe()

        # Register schemas with Universe for proper deserialization
        self._register_schemas()

        # Initialize all adapters
        self._adapters: dict[EntityType, EntityAdapter] = {
            EntityType.MARK: MarkAdapter(),
            EntityType.CRYSTAL: CrystalAdapter(),
            EntityType.TRAIL: TrailAdapter(),
            EntityType.EVIDENCE: EvidenceAdapter(),
            EntityType.TEACHING: TeachingAdapter(),
            EntityType.LEMMA: LemmaAdapter(),
        }

    def _register_schemas(self) -> None:
        """Register all Crystal schemas with Universe."""
        from agents.d.schemas.witness import WitnessMark
        from agents.d.schemas.brain import BrainCrystal
        from agents.d.schemas.trail import Trail

        self.universe.register_type("witness.mark", WitnessMark)
        self.universe.register_type("brain.crystal", BrainCrystal)
        self.universe.register_type("trail.trail", Trail)

    def _get_requested_adapters(self, types: list[EntityType] | None) -> list[EntityAdapter]:
        """
        Get adapters for requested types.

        If types is empty or None, returns ALL adapters.
        """
        if not types:
            return list(self._adapters.values())
        return [self._adapters[t] for t in types if t in self._adapters]

    async def list_events(
        self,
        request: ListEventsRequest | None = None,
    ) -> ListEventsResponse:
        """
        List unified events with filtering and pagination.

        Args:
            request: Request with filters, limit, offset.

        Returns:
            Response with events, total count, has_more flag.
        """
        if request is None:
            request = ListEventsRequest()

        filters = request.filters
        limit = request.limit
        offset = request.offset

        # Determine which types to query
        requested_types = filters.types if filters else []
        adapters = self._get_requested_adapters(requested_types if requested_types else None)

        # Request extra to determine has_more
        per_adapter_limit = limit + 1

        # Query adapters in parallel (Universe is async-safe)
        async def query_adapter(adapter: EntityAdapter) -> list[UnifiedEvent]:
            try:
                return await adapter.list_recent(
                    self.universe,
                    limit=per_adapter_limit,
                    offset=0,  # We'll handle offset after merge
                    filters=filters,
                )
            except Exception as e:
                logger.warning(f"Adapter {adapter.entity_type} failed: {e}")
                return []

        results = await asyncio.gather(
            *[query_adapter(adapter) for adapter in adapters],
            return_exceptions=False,
        )

        # Flatten and sort by timestamp descending
        all_events: list[UnifiedEvent] = []
        for event_list in results:
            all_events.extend(event_list)

        all_events.sort(key=lambda e: e.timestamp, reverse=True)

        # Apply offset and limit
        paginated = all_events[offset : offset + limit + 1]

        # Determine has_more
        has_more = len(paginated) > limit
        events = paginated[:limit]

        # Get total count (parallel queries)
        async def count_adapter(adapter: EntityAdapter) -> int:
            try:
                return await adapter.count(self.universe, filters=filters)
            except Exception as e:
                logger.warning(f"Count for {adapter.entity_type} failed: {e}")
                return 0

        counts = await asyncio.gather(
            *[count_adapter(adapter) for adapter in adapters],
            return_exceptions=False,
        )
        total = sum(counts)

        return ListEventsResponse(
            events=events,
            total=total,
            has_more=has_more,
        )

    async def search_events(
        self,
        request: SearchEventsRequest,
    ) -> SearchEventsResponse:
        """
        Search events across all types (basic keyword search).

        For semantic search, use D-gent integration.

        Args:
            request: Request with query string and optional type filter.

        Returns:
            Response with scored results and facets.
        """
        query = request.query.lower()
        requested_types = request.types
        limit = request.limit

        adapters = self._get_requested_adapters(requested_types)

        # Query adapters in parallel
        async def query_adapter(adapter: EntityAdapter) -> list[UnifiedEvent]:
            try:
                # Get more than limit to allow for filtering
                return await adapter.list_recent(self.universe, limit=limit * 3)
            except Exception as e:
                logger.warning(f"Search adapter {adapter.entity_type} failed: {e}")
                return []

        results = await asyncio.gather(
            *[query_adapter(adapter) for adapter in adapters],
            return_exceptions=False,
        )

        # Flatten
        all_events: list[UnifiedEvent] = []
        for event_list in results:
            all_events.extend(event_list)

        # Simple keyword scoring
        scored: list[SearchResult] = []
        for event in all_events:
            score = 0.0
            text = f"{event.title} {event.summary}".lower()

            # Title match is worth more
            if query in event.title.lower():
                score += 2.0
            # Summary match
            if query in event.summary.lower():
                score += 1.0
            # Partial matches
            words = query.split()
            for word in words:
                if word in text:
                    score += 0.5

            if score > 0:
                scored.append(SearchResult(event=event, score=score))

        # Sort by score descending
        scored.sort(key=lambda r: r.score, reverse=True)
        scored = scored[:limit]

        # Build facets (count by type)
        facets: dict[str, int] = {}
        for result in scored:
            type_key = (
                result.event.type.value
                if isinstance(result.event.type, EntityType)
                else result.event.type
            )
            facets[type_key] = facets.get(type_key, 0) + 1

        return SearchEventsResponse(
            results=scored,
            total=len(scored),
            facets=facets,
        )

    async def get_by_id(
        self,
        entity_type: EntityType,
        entity_id: str,
    ) -> UnifiedEvent | None:
        """
        Get a specific entity by type and ID.

        Args:
            entity_type: The type of entity.
            entity_id: The entity ID.

        Returns:
            The UnifiedEvent or None if not found.
        """
        adapter = self._adapters.get(entity_type)
        if not adapter:
            return None

        # Query with ID filter - for now, list and filter
        # TODO: Add get_by_id to adapters for efficiency
        events = await adapter.list_recent(self.universe, limit=1000)
        for event in events:
            if event.id == entity_id:
                return event
        return None

    async def surface_random(
        self,
        types: list[EntityType] | None = None,
    ) -> UnifiedEvent | None:
        """
        Surface a random entity (serendipity).

        The Accursed Share: Entropy, serendipity, gratitude.

        Args:
            types: Optional type filter.

        Returns:
            A random UnifiedEvent or None if empty.
        """
        adapters = self._get_requested_adapters(types)

        # Get counts to weight random selection
        counts: dict[EntityType, int] = {}
        for adapter in adapters:
            try:
                count = await adapter.count(self.universe)
                if count > 0:
                    counts[adapter.entity_type] = count
            except Exception:
                pass

        if not counts:
            return None

        # Weight by count
        total = sum(counts.values())
        r = random.randint(1, total)
        cumulative = 0

        selected_type: EntityType | None = None
        for entity_type, count in counts.items():
            cumulative += count
            if r <= cumulative:
                selected_type = entity_type
                break

        if not selected_type:
            return None

        # Get random offset within type
        adapter = self._adapters[selected_type]
        count = counts[selected_type]
        offset = random.randint(0, max(0, count - 1))

        events = await adapter.list_recent(self.universe, limit=1, offset=offset)
        return events[0] if events else None

    async def manifest(self) -> ExplorerManifestResponse:
        """
        Get explorer health status.

        Returns:
            Manifest with counts and status.
        """

        # Count all entity types in parallel
        async def count_for_type(
            entity_type: EntityType, adapter: EntityAdapter
        ) -> tuple[str, int]:
            try:
                count = await adapter.count(self.universe)
                return (entity_type.value, count)
            except Exception as e:
                logger.warning(f"Count for {entity_type} failed: {e}")
                return (entity_type.value, 0)

        results = await asyncio.gather(
            *[count_for_type(et, adapter) for et, adapter in self._adapters.items()],
            return_exceptions=False,
        )

        # Build counts dict
        counts_by_type: dict[str, int] = dict(results)
        total = sum(counts_by_type.values())

        # Determine connected services based on non-zero counts
        connected = [k for k, v in counts_by_type.items() if v > 0]

        # Get backend info from Universe stats
        stats = await self.universe.stats()

        return ExplorerManifestResponse(
            total_events=total,
            counts_by_type=counts_by_type,
            storage_backend=stats.backend,  # From Universe (postgres/sqlite/memory)
            connected_services=connected,
            stream_connected=True,  # SSE is now implemented
        )
