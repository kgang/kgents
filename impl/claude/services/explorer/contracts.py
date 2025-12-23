"""
Explorer AGENTESE Contract Definitions.

> *"The file is a lie. There is only the graph."*

Defines request and response types for Explorer @node contracts.
These mirror the frontend TypeScript types in web/src/brain/types.ts.

Contract Protocol:
- Response() for perception aspects (list, search, manifest)
- Contract() for mutation aspects (none currently)

Types here are used by:
1. @node(contracts={...}) in node.py
2. /discover?include_schemas=true endpoint
3. web/scripts/sync-types.ts for FE type generation

See: impl/claude/web/src/brain/types.ts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal

# =============================================================================
# Entity Types
# =============================================================================


class EntityType(str, Enum):
    """The six data construct types in kgents."""

    MARK = "mark"
    CRYSTAL = "crystal"
    TRAIL = "trail"
    EVIDENCE = "evidence"
    TEACHING = "teaching"
    LEMMA = "lemma"


class EvidenceSubtype(str, Enum):
    """Evidence subtypes for discriminated rendering."""

    TRACE_WITNESS = "trace_witness"
    VERIFICATION_GRAPH = "verification_graph"
    CATEGORICAL_VIOLATION = "categorical_violation"


class VerificationStatus(str, Enum):
    """Status of verification evidence."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"
    NEEDS_REVIEW = "needs_review"


class TeachingSeverity(str, Enum):
    """Severity level of teaching insights."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class EvidenceStrength(str, Enum):
    """Evidence strength for trails."""

    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    DEFINITIVE = "definitive"


class Author(str, Enum):
    """Mark author."""

    KENT = "kent"
    CLAUDE = "claude"
    SYSTEM = "system"


class ProofChecker(str, Enum):
    """ASHC proof checkers."""

    DAFNY = "dafny"
    LEAN4 = "lean4"
    VERUS = "verus"


# =============================================================================
# Metadata Types (discriminated union via 'type' field)
# =============================================================================


@dataclass(frozen=True)
class MarkMetadata:
    """Mark-specific metadata."""

    type: Literal["mark"] = "mark"
    action: str = ""
    reasoning: str | None = None
    principles: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    author: str = "kent"
    session_id: str | None = None
    parent_mark_id: str | None = None


@dataclass(frozen=True)
class CrystalMetadata:
    """Crystal-specific metadata."""

    type: Literal["crystal"] = "crystal"
    content_hash: str = ""
    tags: list[str] = field(default_factory=list)
    access_count: int = 0
    last_accessed: str | None = None
    source_type: str | None = None
    source_ref: str | None = None
    datum_id: str | None = None


@dataclass(frozen=True)
class TrailMetadata:
    """Trail-specific metadata."""

    type: Literal["trail"] = "trail"
    name: str = ""
    step_count: int = 0
    topics: list[str] = field(default_factory=list)
    evidence_strength: str = "weak"
    forked_from_id: str | None = None
    is_active: bool = True


@dataclass(frozen=True)
class EvidenceMetadata:
    """Evidence-specific metadata (covers all three subtypes)."""

    type: Literal["evidence"] = "evidence"
    subtype: str = "trace_witness"
    agent_path: str | None = None
    status: str = "pending"
    violation_type: str | None = None
    is_resolved: bool | None = None


@dataclass(frozen=True)
class TeachingMetadata:
    """Teaching-specific metadata."""

    type: Literal["teaching"] = "teaching"
    insight: str = ""
    severity: str = "info"
    source_module: str = ""
    source_symbol: str = ""
    is_alive: bool = True
    died_at: str | None = None
    successor_module: str | None = None
    extinction_id: str | None = None


@dataclass(frozen=True)
class LemmaMetadata:
    """Lemma-specific metadata."""

    type: Literal["lemma"] = "lemma"
    statement: str = ""
    checker: str = "lean4"
    usage_count: int = 0
    obligation_id: str = ""
    dependencies: list[str] = field(default_factory=list)


# Union type for polymorphic metadata
EventMetadata = (
    MarkMetadata
    | CrystalMetadata
    | TrailMetadata
    | EvidenceMetadata
    | TeachingMetadata
    | LemmaMetadata
)


# =============================================================================
# Unified Event
# =============================================================================


@dataclass
class UnifiedEvent:
    """
    A unified event in the Brain stream.

    All entity types are normalized to this shape for display.
    Type-specific fields are stored in `metadata`.
    """

    id: str
    type: EntityType
    title: str
    summary: str
    timestamp: str  # ISO 8601
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "id": self.id,
            "type": self.type.value if isinstance(self.type, EntityType) else self.type,
            "title": self.title,
            "summary": self.summary,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


# =============================================================================
# Filter & Request Types
# =============================================================================


@dataclass
class StreamFilters:
    """Filter state for the Brain stream."""

    types: list[EntityType] = field(default_factory=list)
    author: str | None = None
    date_start: datetime | None = None
    date_end: datetime | None = None
    tags: list[str] = field(default_factory=list)
    search_query: str | None = None


@dataclass
class ListEventsRequest:
    """Request for listing events."""

    filters: StreamFilters | None = None
    limit: int = 50
    offset: int = 0


@dataclass
class ListEventsResponse:
    """Response from listing events."""

    events: list[UnifiedEvent]
    total: int
    has_more: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "events": [e.to_dict() for e in self.events],
            "total": self.total,
            "hasMore": self.has_more,
        }


@dataclass
class SearchEventsRequest:
    """Request for searching events."""

    query: str
    types: list[EntityType] | None = None
    limit: int = 20


@dataclass
class SearchResult:
    """A single search result with score."""

    event: UnifiedEvent
    score: float


@dataclass
class SearchEventsResponse:
    """Response from searching events."""

    results: list[SearchResult]
    total: int
    facets: dict[str, int]  # EntityType -> count

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "results": [{**r.event.to_dict(), "score": r.score} for r in self.results],
            "total": self.total,
            "facets": self.facets,
        }


# =============================================================================
# Manifest Response
# =============================================================================


@dataclass
class ExplorerManifestResponse:
    """Explorer health status manifest."""

    total_events: int
    counts_by_type: dict[str, int]
    storage_backend: str
    connected_services: list[str]
    stream_connected: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "totalEvents": self.total_events,
            "countsByType": self.counts_by_type,
            "storageBackend": self.storage_backend,
            "connectedServices": self.connected_services,
            "streamConnected": self.stream_connected,
        }
