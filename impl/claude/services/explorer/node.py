"""
Explorer AGENTESE Node: @node("self.explorer")

Wraps UnifiedQueryService as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- self.explorer.manifest  - Explorer health status (counts by type)
- self.explorer.list      - Paginated unified event list
- self.explorer.search    - Keyword search across all types
- self.explorer.detail    - Get specific entity by type + id
- self.explorer.surface   - Serendipity (random entity from the void)

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed (except SSE stream)
- All transports collapse to logos.invoke(path, observer, ...)

> *"The file is a lie. There is only the graph."*

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
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
    EntityType,
    ExplorerManifestResponse,
    ListEventsRequest,
    ListEventsResponse,
    SearchEventsRequest,
    SearchEventsResponse,
    StreamFilters,
)
from .service import UnifiedQueryService

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)


# =============================================================================
# Response Contracts (for type discovery)
# =============================================================================


@dataclass(frozen=True)
class DetailRequest:
    """Request for getting entity detail."""

    entity_type: str
    entity_id: str


@dataclass(frozen=True)
class SurfaceRequest:
    """Request for serendipity surface."""

    types: list[str] | None = None


# =============================================================================
# Rendering Classes
# =============================================================================


@dataclass(frozen=True)
class ExplorerManifestRendering:
    """Rendering for explorer manifest."""

    manifest: ExplorerManifestResponse

    def to_dict(self) -> dict[str, Any]:
        return self.manifest.to_dict()

    def to_text(self) -> str:
        lines = [
            "Explorer Status",
            "===============",
            f"Total Events: {self.manifest.total_events}",
            f"Storage: {self.manifest.storage_backend}",
            f"Stream Connected: {'Yes' if self.manifest.stream_connected else 'No'}",
            "",
            "Counts by Type:",
        ]
        for entity_type, count in self.manifest.counts_by_type.items():
            lines.append(f"  {entity_type}: {count}")
        return "\n".join(lines)


@dataclass(frozen=True)
class ListEventsRendering:
    """Rendering for list events response."""

    response: ListEventsResponse

    def to_dict(self) -> dict[str, Any]:
        return self.response.to_dict()

    def to_text(self) -> str:
        if not self.response.events:
            return "No events found."
        lines = [f"Events ({len(self.response.events)} of {self.response.total}):", ""]
        for event in self.response.events[:20]:
            type_emoji = {
                "mark": "🔖",
                "crystal": "💎",
                "trail": "🛤️",
                "evidence": "📜",
                "teaching": "📚",
                "lemma": "🧮",
            }.get(event.type.value if isinstance(event.type, EntityType) else event.type, "📌")
            lines.append(
                f"  {type_emoji} [{event.type.value if isinstance(event.type, EntityType) else event.type}] {event.title[:60]}"
            )
        if self.response.has_more:
            lines.append(f"\n  ... and {self.response.total - len(self.response.events)} more")
        return "\n".join(lines)


@dataclass(frozen=True)
class SearchResultsRendering:
    """Rendering for search results."""

    response: SearchEventsResponse
    query: str

    def to_dict(self) -> dict[str, Any]:
        return self.response.to_dict()

    def to_text(self) -> str:
        if not self.response.results:
            return f"No results for: {self.query}"
        lines = [f"Search: '{self.query}' ({self.response.total} results)", ""]
        for result in self.response.results[:10]:
            event = result.event
            lines.append(f"  [{result.score:.1f}] {event.title[:60]}")
        return "\n".join(lines)


# =============================================================================
# ExplorerNode
# =============================================================================


@node(
    "self.explorer",
    description="Unified Data Explorer - spatial cathedral of all kgents data",
    dependencies=("unified_query_service",),
    contracts={
        # Perception aspects (Response only)
        "manifest": Response(ExplorerManifestResponse),
        # Query aspects (Contract with request + response)
        "list": Contract(ListEventsRequest, ListEventsResponse),
        "search": Contract(SearchEventsRequest, SearchEventsResponse),
        "detail": Contract(DetailRequest, dict),
        "surface": Contract(SurfaceRequest, dict),
    },
    examples=[
        ("list", {"limit": 50}, "List recent events"),
        ("search", {"query": "Python", "limit": 10}, "Search for Python"),
        ("detail", {"entity_type": "mark", "entity_id": "abc123"}, "Get mark details"),
        ("surface", {}, "Surface random entity"),
    ],
)
class ExplorerNode(BaseLogosNode):
    """
    AGENTESE node for Explorer Crown Jewel.

    Exposes UnifiedQueryService through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/explorer/list
        {"limit": 50, "filters": {"types": ["mark", "crystal"]}}

        # Via Logos directly
        await logos.invoke("self.explorer.list", observer, limit=50)

        # Via CLI
        kgents brain explore --limit 50

    Teaching:
        gotcha: ExplorerNode REQUIRES unified_query_service dependency. Without it,
                instantiation fails with TypeError—this is intentional for DI.

        gotcha: Types filter accepts strings that map to EntityType enum.
                Use "mark", "crystal", "trail", etc.

        gotcha: Every ExplorerNode invocation emits a Mark (WARP Law 3). Don't add
                manual tracing—the gateway handles it at _invoke_path().
    """

    def __init__(self, unified_query_service: UnifiedQueryService) -> None:
        """
        Initialize ExplorerNode.

        Args:
            unified_query_service: The unified query service (injected by container)

        Raises:
            TypeError: If unified_query_service is not provided
        """
        self._service = unified_query_service

    @property
    def handle(self) -> str:
        return "self.explorer"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        All archetypes have read access to explorer.
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # All users can explore
        base = ("list", "search", "detail", "surface")

        # Developers also get manifest
        if archetype_lower in ("developer", "operator", "admin", "system", "architect"):
            return ("manifest",) + base

        return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest explorer status to observer.

        AGENTESE: self.explorer.manifest
        """
        if self._service is None:
            return BasicRendering(
                summary="Explorer not initialized",
                content="No query service configured",
                metadata={"error": "no_service"},
            )

        result = await self._service.manifest()
        return ExplorerManifestRendering(manifest=result)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to service methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._service is None:
            return {"error": "Explorer service not configured"}

        # Route to appropriate service method
        if aspect == "list":
            # Build filters from kwargs
            filters = None
            if any(k in kwargs for k in ("types", "author", "date_start", "date_end", "tags")):
                type_strings = kwargs.get("types", [])
                types = []
                for t in type_strings:
                    try:
                        types.append(EntityType(t) if isinstance(t, str) else t)
                    except ValueError:
                        pass  # Skip invalid types

                filters = StreamFilters(
                    types=types,
                    author=kwargs.get("author"),
                    date_start=kwargs.get("date_start"),
                    date_end=kwargs.get("date_end"),
                    tags=kwargs.get("tags", []),
                )

            request = ListEventsRequest(
                filters=filters,
                limit=kwargs.get("limit", 50),
                offset=kwargs.get("offset", 0),
            )
            response = await self._service.list_events(request)
            return ListEventsRendering(response=response).to_dict()

        elif aspect == "search":
            query = kwargs.get("query", "")
            if not query:
                return {"error": "query required"}

            type_strings = kwargs.get("types", [])
            search_types: list[EntityType] | None = None
            if type_strings:
                search_types = []
                for t in type_strings:
                    try:
                        search_types.append(EntityType(t) if isinstance(t, str) else t)
                    except ValueError:
                        pass

            search_request = SearchEventsRequest(
                query=query,
                types=search_types,
                limit=kwargs.get("limit", 20),
            )
            search_response = await self._service.search_events(search_request)
            return SearchResultsRendering(response=search_response, query=query).to_dict()

        elif aspect == "detail":
            entity_type_str = kwargs.get("entity_type") or kwargs.get("type")
            entity_id = kwargs.get("entity_id") or kwargs.get("id")

            if not entity_type_str or not entity_id:
                return {"error": "entity_type and entity_id required"}

            try:
                entity_type = EntityType(entity_type_str)
            except ValueError:
                return {"error": f"Invalid entity type: {entity_type_str}"}

            result = await self._service.get_by_id(entity_type, entity_id)
            if result is None:
                return {"error": f"Entity not found: {entity_type_str}/{entity_id}"}
            return result.to_dict()

        elif aspect == "surface":
            type_strings = kwargs.get("types", [])
            types = None
            if type_strings:
                types = []
                for t in type_strings:
                    try:
                        types.append(EntityType(t) if isinstance(t, str) else t)
                    except ValueError:
                        pass

            result = await self._service.surface_random(types)
            if result is None:
                return {"surface": None, "message": "No entities found"}
            return {
                "surface": result.to_dict(),
                "message": "Surfaced from the void",
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ExplorerNode",
    "ExplorerManifestRendering",
    "ListEventsRendering",
    "SearchResultsRendering",
]
