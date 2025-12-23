"""
Explorer Crown Jewel: Unified Data Explorer for Brain Page.

> *"The file is a lie. There is only the graph."*

The Explorer aggregates ALL kgents data constructs into a unified stream:
- Marks (witnessed behavior)
- Crystals (crystallized knowledge)
- Trails (exploration journeys)
- Evidence (verification graphs, trace witnesses, categorical violations)
- Teachings (ancestral wisdom from deleted code)
- Lemmas (ASHC verified proofs)

Architecture:
- 6 Adapters convert DB models → UnifiedEvent
- UnifiedQueryService orchestrates parallel queries
- SSE stream aggregates real-time events

AGENTESE Paths (via @node("self.explorer")):
- self.explorer.manifest   - Explorer health status
- self.explorer.list       - Paginated unified event list
- self.explorer.search     - Semantic search across all types
- self.explorer.detail     - Get specific entity by type+id
- self.explorer.surface    - Serendipity (random entity)

The Metaphysical Fullstack Pattern (AD-009):
- ExplorerNode wraps UnifiedQueryService as AGENTESE node
- Universal gateway auto-exposes all aspects
- No explicit routes needed (except SSE stream)

See: docs/skills/metaphysical-fullstack.md
"""

from .adapters import (
    CrystalAdapter,
    EntityAdapter,
    EvidenceAdapter,
    LemmaAdapter,
    MarkAdapter,
    TeachingAdapter,
    TrailAdapter,
)
from .contracts import (
    EntityType,
    EvidenceMetadata,
    EvidenceSubtype,
    ListEventsRequest,
    ListEventsResponse,
    SearchEventsRequest,
    SearchEventsResponse,
    StreamFilters,
    UnifiedEvent,
)

# Import node to trigger @node registration (must be after service import)
from .node import ExplorerNode
from .service import UnifiedQueryService

__all__ = [
    # Contracts (types)
    "EntityType",
    "UnifiedEvent",
    "StreamFilters",
    "ListEventsRequest",
    "ListEventsResponse",
    "SearchEventsRequest",
    "SearchEventsResponse",
    "EvidenceSubtype",
    "EvidenceMetadata",
    # Adapters
    "EntityAdapter",
    "MarkAdapter",
    "CrystalAdapter",
    "TrailAdapter",
    "EvidenceAdapter",
    "TeachingAdapter",
    "LemmaAdapter",
    # Service
    "UnifiedQueryService",
    # Node
    "ExplorerNode",
]
