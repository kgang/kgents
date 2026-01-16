"""
Entity Adapters: Convert Universe Crystals to UnifiedEvent.

> *"The file is a lie. There is only the graph."*

Each adapter queries the Universe and converts Crystal data to UnifiedEvent:
- MarkAdapter: witness.mark → UnifiedEvent
- CrystalAdapter: brain.crystal → UnifiedEvent
- TrailAdapter: trail.trail → UnifiedEvent
- EvidenceAdapter: (Placeholder - no schema yet)
- TeachingAdapter: (Placeholder - no schema yet)
- LemmaAdapter: (Placeholder - no schema yet)

The Adapter Protocol:
- to_unified_event(crystal) → UnifiedEvent
- list_recent(universe, limit, offset) → list[UnifiedEvent]
- count(universe) → int

Migration from SQLAlchemy to Universe:
- Uses Universe.query() instead of SQLAlchemy session
- Queries by schema name (e.g., "witness.mark")
- Converts Crystal dataclasses to UnifiedEvent
- Preserves public interface for backward compatibility

Teaching:
    gotcha: Universe returns frozen dataclass instances, not SQLAlchemy models
    gotcha: Timestamp fields are stored as ISO 8601 strings in Crystal
    gotcha: Adapters without schemas (Evidence, Teaching, Lemma) return empty lists until schemas are defined
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, TypeVar

from agents.d.universe import Query, Universe, get_universe

from .contracts import (
    CrystalMetadata,
    EntityType,
    EvidenceMetadata,
    LemmaMetadata,
    MarkMetadata,
    StreamFilters,
    TeachingMetadata,
    TrailMetadata,
    UnifiedEvent,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Timestamp Helper
# =============================================================================


def _safe_timestamp(value: Any) -> str:
    """
    Safely convert a timestamp to ISO format string.

    Handles: datetime, string, float (Unix timestamp), None, and other types.
    Always returns ISO 8601 format for frontend compatibility.
    """
    if value is None:
        return datetime.utcnow().isoformat()
    if isinstance(value, (int, float)):
        # Unix timestamp - convert to ISO
        return datetime.fromtimestamp(value).isoformat()
    if isinstance(value, str):
        # Check if it looks like a Unix timestamp (numeric string)
        try:
            ts = float(value)
            if ts > 1000000000:  # Looks like a Unix timestamp (after 2001)
                return datetime.fromtimestamp(ts).isoformat()
        except ValueError:
            pass
        return value  # Already ISO format string
    if hasattr(value, "isoformat"):
        return str(value.isoformat())
    return str(value)


T = TypeVar("T")


# =============================================================================
# Base Adapter Protocol
# =============================================================================


class EntityAdapter(ABC):
    """
    Base adapter protocol for converting Universe Crystals to UnifiedEvent.

    Each adapter must implement:
    - entity_type: The EntityType this adapter handles
    - to_unified_event(): Convert single Crystal to UnifiedEvent
    - list_recent(): Query Universe and convert
    - count(): Get total count for this entity type
    """

    @property
    @abstractmethod
    def entity_type(self) -> EntityType:
        """The entity type this adapter handles."""
        ...

    @abstractmethod
    def to_unified_event(self, crystal: Any) -> UnifiedEvent:
        """Convert a single Crystal to UnifiedEvent."""
        ...

    @abstractmethod
    async def list_recent(
        self,
        universe: Universe,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Query Universe and convert to UnifiedEvents."""
        ...

    @abstractmethod
    async def count(
        self,
        universe: Universe,
        filters: StreamFilters | None = None,
    ) -> int:
        """Get total count for this entity type."""
        ...


# =============================================================================
# Mark Adapter
# =============================================================================


class MarkAdapter(EntityAdapter):
    """Convert witness.mark Crystal to UnifiedEvent."""

    @property
    def entity_type(self) -> EntityType:
        return EntityType.MARK

    def to_unified_event(self, mark: Any) -> UnifiedEvent:
        """Convert WitnessMark Crystal to UnifiedEvent."""
        from agents.d.schemas.witness import WitnessMark

        # Ensure we have a WitnessMark instance
        if not isinstance(mark, WitnessMark):
            raise TypeError(f"Expected WitnessMark, got {type(mark)}")

        # Build metadata
        metadata = MarkMetadata(
            type="mark",
            action=mark.action,
            reasoning=mark.reasoning,
            principles=list(mark.principles) if mark.principles else [],
            tags=list(mark.tags) if mark.tags else [],
            author=mark.author or "kent",
            session_id=mark.context.get("session_id") if mark.context else None,
            parent_mark_id=mark.parent_mark_id,
        )

        # Build title from action (truncate if long)
        title = mark.action[:80] + "..." if len(mark.action) > 80 else mark.action

        # Build summary from reasoning or principles
        if mark.reasoning:
            summary = mark.reasoning[:120] + "..." if len(mark.reasoning) > 120 else mark.reasoning
        elif mark.principles:
            summary = f"Honors: {', '.join(mark.principles[:3])}"
        else:
            summary = f"By {mark.author or 'kent'}"

        # Extract ID from context (Universe stores it there)
        mark_id = mark.context.get("id", "unknown") if mark.context else "unknown"

        # Extract timestamp from context
        timestamp = (
            mark.context.get("created_at", datetime.utcnow().isoformat())
            if mark.context
            else datetime.utcnow().isoformat()
        )

        return UnifiedEvent(
            id=mark_id,
            type=EntityType.MARK,
            title=title,
            summary=summary,
            timestamp=_safe_timestamp(timestamp),
            metadata=metadata.__dict__,
        )

    async def list_recent(
        self,
        universe: Universe,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Query recent marks from Universe and convert."""
        # Query witness.mark schema
        # Note: Universe doesn't support offset yet, so we'll fetch and slice
        query = Query(
            schema="witness.mark",
            limit=limit + offset,  # Fetch enough to account for offset
        )

        crystals = await universe.query(query)

        # Apply offset manually (Universe doesn't support it yet)
        if offset > 0:
            crystals = crystals[offset:]

        # Convert to UnifiedEvents
        events = []
        for crystal in crystals[:limit]:
            try:
                events.append(self.to_unified_event(crystal))
            except Exception as e:
                logger.warning(f"Failed to convert mark crystal: {e}")
                continue

        return events

    async def count(
        self,
        universe: Universe,
        filters: StreamFilters | None = None,
    ) -> int:
        """Get total mark count from Universe."""
        # Query all marks (Universe doesn't have count API yet)
        query = Query(schema="witness.mark", limit=10000)  # High limit to get all
        crystals = await universe.query(query)
        return len(crystals)


# =============================================================================
# Crystal Adapter
# =============================================================================


class CrystalAdapter(EntityAdapter):
    """Convert brain.crystal to UnifiedEvent."""

    @property
    def entity_type(self) -> EntityType:
        return EntityType.CRYSTAL

    def to_unified_event(self, crystal: Any) -> UnifiedEvent:
        """Convert BrainCrystal to UnifiedEvent."""
        from agents.d.schemas.brain import BrainCrystal

        # Ensure we have a BrainCrystal instance
        if not isinstance(crystal, BrainCrystal):
            raise TypeError(f"Expected BrainCrystal, got {type(crystal)}")

        metadata = CrystalMetadata(
            type="crystal",
            content_hash=crystal.content_hash or "",
            tags=list(crystal.tags) if crystal.tags else [],
            access_count=crystal.access_count or 0,
            last_accessed=crystal.last_accessed,
            source_type=crystal.source_type,
            source_ref=crystal.source_ref,
            datum_id=crystal.datum_id,
        )

        # Title is summary (truncated)
        title = crystal.summary[:80] + "..." if len(crystal.summary) > 80 else crystal.summary

        # Summary includes access info and tags
        parts = []
        if crystal.access_count:
            parts.append(f"Accessed {crystal.access_count}x")
        if crystal.tags:
            parts.append(f"Tags: {', '.join(crystal.tags[:3])}")
        summary_text = " | ".join(parts) if parts else "Crystallized knowledge"

        # Extract ID and timestamp from storage (would be added by Universe)
        # For now, use content_hash as ID if not available
        crystal_id = crystal.content_hash[:12]  # Short hash as ID

        return UnifiedEvent(
            id=crystal_id,
            type=EntityType.CRYSTAL,
            title=title,
            summary=summary_text,
            timestamp=crystal.last_accessed or datetime.utcnow().isoformat(),
            metadata=metadata.__dict__,
        )

    async def list_recent(
        self,
        universe: Universe,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Query recent crystals from Universe and convert."""
        query = Query(
            schema="brain.crystal",
            limit=limit + offset,
        )

        crystals = await universe.query(query)

        # Apply offset manually
        if offset > 0:
            crystals = crystals[offset:]

        # Convert to UnifiedEvents
        events = []
        for crystal in crystals[:limit]:
            try:
                events.append(self.to_unified_event(crystal))
            except Exception as e:
                logger.warning(f"Failed to convert brain crystal: {e}")
                continue

        return events

    async def count(
        self,
        universe: Universe,
        filters: StreamFilters | None = None,
    ) -> int:
        """Get total crystal count from Universe."""
        query = Query(schema="brain.crystal", limit=10000)
        crystals = await universe.query(query)
        return len(crystals)


# =============================================================================
# Trail Adapter
# =============================================================================


class TrailAdapter(EntityAdapter):
    """Convert trail.trail to UnifiedEvent."""

    @property
    def entity_type(self) -> EntityType:
        return EntityType.TRAIL

    def to_unified_event(self, trail: Any) -> UnifiedEvent:
        """Convert Trail to UnifiedEvent."""
        from agents.d.schemas.trail import Trail

        # Ensure we have a Trail instance
        if not isinstance(trail, Trail):
            raise TypeError(f"Expected Trail, got {type(trail)}")

        metadata = TrailMetadata(
            type="trail",
            name=trail.name,
            step_count=0,  # Would need to join with trail.step to get this
            topics=[],  # Not in Trail schema yet
            evidence_strength="weak",  # Would need commitments
            forked_from_id=trail.forked_from_id,
            is_active=trail.is_active,
        )

        # Title is trail name
        title = trail.name

        # Summary from description
        summary = (
            trail.description[:120] + "..." if len(trail.description) > 120 else trail.description
        )

        # Extract ID from trail (would be set by Universe)
        trail_id = "trail-" + trail.name[:20]  # Simplified ID

        return UnifiedEvent(
            id=trail_id,
            type=EntityType.TRAIL,
            title=title,
            summary=summary,
            timestamp=datetime.utcnow().isoformat(),  # No timestamp in Trail schema
            metadata=metadata.__dict__,
        )

    async def list_recent(
        self,
        universe: Universe,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Query recent trails from Universe and convert."""
        query = Query(
            schema="trail.trail",
            limit=limit + offset,
        )

        crystals = await universe.query(query)

        # Apply offset manually
        if offset > 0:
            crystals = crystals[offset:]

        # Convert to UnifiedEvents
        events = []
        for crystal in crystals[:limit]:
            try:
                events.append(self.to_unified_event(crystal))
            except Exception as e:
                logger.warning(f"Failed to convert trail crystal: {e}")
                continue

        return events

    async def count(
        self,
        universe: Universe,
        filters: StreamFilters | None = None,
    ) -> int:
        """Get total trail count from Universe."""
        query = Query(schema="trail.trail", limit=10000)
        crystals = await universe.query(query)
        return len(crystals)


# =============================================================================
# Evidence Adapter (Placeholder - No schema yet)
# =============================================================================


class EvidenceAdapter(EntityAdapter):
    """
    Placeholder adapter for Evidence.

    No schema defined yet for verification evidence in the Crystal system.
    Returns empty lists until schema is created.
    """

    @property
    def entity_type(self) -> EntityType:
        return EntityType.EVIDENCE

    def to_unified_event(self, evidence: Any) -> UnifiedEvent:
        """Placeholder - no schema yet."""
        return UnifiedEvent(
            id="evidence-placeholder",
            type=EntityType.EVIDENCE,
            title="Evidence",
            summary="Schema not yet defined",
            timestamp=datetime.utcnow().isoformat(),
            metadata={"type": "evidence", "subtype": "unknown"},
        )

    async def list_recent(
        self,
        universe: Universe,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Return empty list - no schema defined yet."""
        logger.debug("Evidence schema not defined - returning empty list")
        return []

    async def count(
        self,
        universe: Universe,
        filters: StreamFilters | None = None,
    ) -> int:
        """Return 0 - no schema defined yet."""
        return 0


# =============================================================================
# Teaching Adapter (Placeholder - No schema yet)
# =============================================================================


class TeachingAdapter(EntityAdapter):
    """
    Placeholder adapter for Teaching.

    No schema defined yet for teaching crystals in the Crystal system.
    Returns empty lists until schema is created.
    """

    @property
    def entity_type(self) -> EntityType:
        return EntityType.TEACHING

    def to_unified_event(self, teaching: Any) -> UnifiedEvent:
        """Placeholder - no schema yet."""
        return UnifiedEvent(
            id="teaching-placeholder",
            type=EntityType.TEACHING,
            title="Teaching",
            summary="Schema not yet defined",
            timestamp=datetime.utcnow().isoformat(),
            metadata={"type": "teaching"},
        )

    async def list_recent(
        self,
        universe: Universe,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Return empty list - no schema defined yet."""
        logger.debug("Teaching schema not defined - returning empty list")
        return []

    async def count(
        self,
        universe: Universe,
        filters: StreamFilters | None = None,
    ) -> int:
        """Return 0 - no schema defined yet."""
        return 0


# =============================================================================
# Lemma Adapter (Placeholder - No schema yet)
# =============================================================================


class LemmaAdapter(EntityAdapter):
    """
    Placeholder adapter for Lemma.

    No schema defined yet for verified lemmas in the Crystal system.
    Returns empty lists until schema is created.
    """

    @property
    def entity_type(self) -> EntityType:
        return EntityType.LEMMA

    def to_unified_event(self, lemma: Any) -> UnifiedEvent:
        """Placeholder - no schema yet."""
        return UnifiedEvent(
            id="lemma-placeholder",
            type=EntityType.LEMMA,
            title="Lemma",
            summary="Schema not yet defined",
            timestamp=datetime.utcnow().isoformat(),
            metadata={"type": "lemma"},
        )

    async def list_recent(
        self,
        universe: Universe,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Return empty list - no schema defined yet."""
        logger.debug("Lemma schema not defined - returning empty list")
        return []

    async def count(
        self,
        universe: Universe,
        filters: StreamFilters | None = None,
    ) -> int:
        """Return 0 - no schema defined yet."""
        return 0


# =============================================================================
# Adapter Registry
# =============================================================================


def get_adapter(entity_type: EntityType) -> EntityAdapter:
    """Get adapter for entity type."""
    adapters: dict[EntityType, EntityAdapter] = {
        EntityType.MARK: MarkAdapter(),
        EntityType.CRYSTAL: CrystalAdapter(),
        EntityType.TRAIL: TrailAdapter(),
        EntityType.EVIDENCE: EvidenceAdapter(),
        EntityType.TEACHING: TeachingAdapter(),
        EntityType.LEMMA: LemmaAdapter(),
    }
    return adapters[entity_type]


def get_all_adapters() -> list[EntityAdapter]:
    """Get all adapters."""
    return [
        MarkAdapter(),
        CrystalAdapter(),
        TrailAdapter(),
        EvidenceAdapter(),
        TeachingAdapter(),
        LemmaAdapter(),
    ]
