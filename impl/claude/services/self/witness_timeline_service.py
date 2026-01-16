"""
WitnessTimelineService: Aggregated Timeline of All Witness Activity.

This service provides a unified view of all witness activity for the
Self-Reflective OS Reflect Mode:
- Marks (execution artifacts)
- Trace seals (crystal sealing events)
- Crystals (compressed memory)
- Decisions (dialectical fusions)

Philosophy:
    "The timeline is the heartbeat. Every action leaves a mark.
     Every mark joins the stream. Every stream tells a story."

AGENTESE Paths:
- self.witness.timeline    - Get aggregated timeline
- self.witness.search      - Search marks by query
- self.witness.for_file    - Get witnesses for a file
- self.witness.activity    - Development activity summary

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- All transports collapse to logos.invoke(path, observer, ...)

See: plans/self-reflective-os/
See: spec/protocols/witness-primitives.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Timeline Event Types
# =============================================================================


class EventType(str, Enum):
    """Types of events in the witness timeline."""

    MARK = "mark"
    TRACE_SEAL = "trace_seal"
    CRYSTAL = "crystal"
    DECISION = "decision"


class ActorType(str, Enum):
    """Actor types for timeline events."""

    KENT = "kent"
    CLAUDE = "claude"
    SYSTEM = "system"


# =============================================================================
# Data Models
# =============================================================================


@dataclass(frozen=True)
class TimelineEvent:
    """
    Unified timeline event (mark, trace seal, crystal, or decision).

    This is the atomic unit of the aggregated timeline, providing a
    consistent view across all witness activity types.

    Attributes:
        id: Unique event identifier
        event_type: Type of event (mark, trace_seal, crystal, decision)
        timestamp: When the event occurred
        summary: Human-readable summary of the event
        actor: Who/what produced the event (kent, claude, system)
        related_files: Files involved in this event
        tags: Classification tags
        details: Event-type-specific details
    """

    id: str
    event_type: EventType
    timestamp: datetime
    summary: str
    actor: ActorType
    related_files: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "summary": self.summary,
            "actor": self.actor.value,
            "related_files": list(self.related_files),
            "tags": list(self.tags),
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TimelineEvent":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            event_type=EventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            summary=data["summary"],
            actor=ActorType(data["actor"]),
            related_files=tuple(data.get("related_files", [])),
            tags=tuple(data.get("tags", [])),
            details=data.get("details", {}),
        )


@dataclass(frozen=True)
class TimelineFilter:
    """
    Filter parameters for timeline queries.

    All parameters are optional. Multiple parameters combine with AND logic.
    """

    event_types: tuple[EventType, ...] | None = None
    actors: tuple[ActorType, ...] | None = None
    file_path: str | None = None
    tag: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    search_query: str | None = None

    def matches(self, event: TimelineEvent) -> bool:
        """Check if an event matches this filter."""
        # Event type filter
        if self.event_types and event.event_type not in self.event_types:
            return False

        # Actor filter
        if self.actors and event.actor not in self.actors:
            return False

        # File path filter (substring match)
        if self.file_path:
            if not any(self.file_path in f for f in event.related_files):
                return False

        # Tag filter
        if self.tag and self.tag not in event.tags:
            return False

        # Date range filter (handle both offset-naive and offset-aware datetimes)
        if self.date_from:
            event_ts = event.timestamp
            filter_ts = self.date_from
            # Normalize to aware datetimes for comparison
            if event_ts.tzinfo is None:
                event_ts = event_ts.replace(tzinfo=timezone.utc)
            if filter_ts.tzinfo is None:
                filter_ts = filter_ts.replace(tzinfo=timezone.utc)
            if event_ts < filter_ts:
                return False

        if self.date_to:
            event_ts = event.timestamp
            filter_ts = self.date_to
            # Normalize to aware datetimes for comparison
            if event_ts.tzinfo is None:
                event_ts = event_ts.replace(tzinfo=timezone.utc)
            if filter_ts.tzinfo is None:
                filter_ts = filter_ts.replace(tzinfo=timezone.utc)
            if event_ts > filter_ts:
                return False

        # Search query (case-insensitive in summary and tags)
        if self.search_query:
            query_lower = self.search_query.lower()
            if query_lower not in event.summary.lower():
                if not any(query_lower in t.lower() for t in event.tags):
                    return False

        return True


@dataclass(frozen=True)
class DevelopmentActivity:
    """
    Summary of development activity over a period.

    Used by the Reflect Mode to show activity summaries.
    """

    period: str  # 'day', 'week', 'month'
    start_date: datetime
    end_date: datetime
    total_marks: int
    total_crystals: int
    total_decisions: int
    events_by_day: dict[str, int] = field(default_factory=dict)
    events_by_actor: dict[str, int] = field(default_factory=dict)
    events_by_type: dict[str, int] = field(default_factory=dict)
    top_files: tuple[tuple[str, int], ...] = ()
    top_tags: tuple[tuple[str, int], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "period": self.period,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "total_marks": self.total_marks,
            "total_crystals": self.total_crystals,
            "total_decisions": self.total_decisions,
            "events_by_day": self.events_by_day,
            "events_by_actor": self.events_by_actor,
            "events_by_type": self.events_by_type,
            "top_files": list(self.top_files),
            "top_tags": list(self.top_tags),
        }


# =============================================================================
# WitnessTimelineService
# =============================================================================


class WitnessTimelineService:
    """
    Aggregated timeline of all witness activity.

    This service composes from existing witness services to provide
    a unified view of:
    - Marks (from MarkStore/WitnessPersistence)
    - Crystals (from CrystalStore)
    - Decisions (from DecisionStore if available)

    Example:
        service = WitnessTimelineService()

        # Get recent timeline
        events = await service.get_timeline(limit=50)

        # Search marks
        marks = await service.search_marks("refactoring")

        # Get activity summary
        activity = await service.get_development_activity(period="week")
    """

    def __init__(
        self,
        persistence: Any | None = None,  # WitnessPersistence
        mark_store: Any | None = None,  # MarkStore
        crystal_store: Any | None = None,  # CrystalStore
    ) -> None:
        """
        Initialize WitnessTimelineService.

        Args:
            persistence: WitnessPersistence instance (optional)
            mark_store: MarkStore instance (optional)
            crystal_store: CrystalStore instance (optional)
        """
        self._persistence = persistence
        self._mark_store = mark_store
        self._crystal_store = crystal_store

    def _get_persistence(self) -> Any:
        """Lazy-load WitnessPersistence."""
        if self._persistence is None:
            from services.witness.persistence import WitnessPersistence

            self._persistence = WitnessPersistence()
        return self._persistence

    def _get_mark_store(self) -> Any:
        """Lazy-load MarkStore."""
        if self._mark_store is None:
            from services.witness.trace_store import get_mark_store

            self._mark_store = get_mark_store()
        return self._mark_store

    def _get_crystal_store(self) -> Any:
        """Lazy-load CrystalStore."""
        if self._crystal_store is None:
            from services.witness.crystal_store import get_crystal_store

            self._crystal_store = get_crystal_store()
        return self._crystal_store

    # =========================================================================
    # Timeline Operations
    # =========================================================================

    async def get_timeline(
        self,
        filter: TimelineFilter | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[TimelineEvent]:
        """
        Get aggregated timeline of all witness activity.

        Combines marks, crystals, and decisions into a unified timeline,
        sorted by timestamp (newest first).

        Args:
            filter: Optional filter criteria
            limit: Maximum events to return (default 100)
            offset: Number of events to skip (for pagination)

        Returns:
            List of TimelineEvent objects, newest first
        """
        events: list[TimelineEvent] = []

        # Collect marks
        try:
            mark_events = await self._collect_mark_events(limit * 2)
            events.extend(mark_events)
        except Exception as e:
            logger.warning(f"Error collecting marks: {e}")

        # Collect crystals
        try:
            crystal_events = await self._collect_crystal_events(limit * 2)
            events.extend(crystal_events)
        except Exception as e:
            logger.warning(f"Error collecting crystals: {e}")

        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)

        # Apply filter
        if filter:
            events = [e for e in events if filter.matches(e)]

        # Apply pagination
        return events[offset : offset + limit]

    async def _collect_mark_events(self, limit: int) -> list[TimelineEvent]:
        """Collect timeline events from marks."""
        events: list[TimelineEvent] = []

        try:
            mark_store = self._get_mark_store()
            marks = list(mark_store.recent(limit=limit))

            for mark in marks:
                # Determine actor from origin
                actor = self._infer_actor(mark.origin)

                # Extract related files from metadata
                related_files = self._extract_files_from_mark(mark)

                # Create summary
                summary = (
                    mark.response.content[:200]
                    if mark.response.content
                    else f"Mark from {mark.origin}"
                )

                event = TimelineEvent(
                    id=str(mark.id),
                    event_type=EventType.MARK,
                    timestamp=mark.timestamp,
                    summary=summary,
                    actor=actor,
                    related_files=related_files,
                    tags=mark.tags,
                    details={
                        "origin": mark.origin,
                        "domain": mark.domain,
                        "phase": mark.phase.value if mark.phase else None,
                        "stimulus_kind": mark.stimulus.kind,
                        "is_sealed": mark.is_sealed,
                    },
                )
                events.append(event)
        except Exception as e:
            logger.error(f"Error collecting mark events: {e}")

        return events

    async def _collect_crystal_events(self, limit: int) -> list[TimelineEvent]:
        """Collect timeline events from crystals."""
        events: list[TimelineEvent] = []

        try:
            crystal_store = self._get_crystal_store()
            crystals = list(crystal_store.recent(limit=limit))

            for crystal in crystals:
                event = TimelineEvent(
                    id=str(crystal.id),
                    event_type=EventType.CRYSTAL,
                    timestamp=crystal.crystallized_at,
                    summary=crystal.insight[:200]
                    if crystal.insight
                    else f"Crystal at {crystal.level.name}",
                    actor=ActorType.SYSTEM,
                    related_files=(),  # Crystals don't track files directly
                    tags=tuple(crystal.topics) if crystal.topics else (),
                    details={
                        "level": crystal.level.name,
                        "significance": crystal.significance,
                        "principles": list(crystal.principles),
                        "confidence": crystal.confidence,
                        "compression_ratio": crystal.compression_ratio,
                        "source_count": crystal.source_count,
                    },
                )
                events.append(event)
        except Exception as e:
            logger.error(f"Error collecting crystal events: {e}")

        return events

    def _infer_actor(self, origin: str) -> ActorType:
        """Infer actor type from origin."""
        if origin in ("kent", "user", "human"):
            return ActorType.KENT
        elif origin in ("claude", "llm", "ai", "assistant"):
            return ActorType.CLAUDE
        else:
            return ActorType.SYSTEM

    def _extract_files_from_mark(self, mark: Any) -> tuple[str, ...]:
        """Extract related file paths from a mark."""
        files: list[str] = []

        # Check metadata
        if mark.metadata:
            if "file_path" in mark.metadata:
                files.append(mark.metadata["file_path"])
            if "kblock_path" in mark.metadata:
                files.append(mark.metadata["kblock_path"])
            if "path" in mark.metadata:
                files.append(mark.metadata["path"])

        # Check stimulus
        if mark.stimulus and mark.stimulus.metadata:
            if "path" in mark.stimulus.metadata:
                files.append(mark.stimulus.metadata["path"])

        # Check response
        if mark.response and mark.response.metadata:
            if "path" in mark.response.metadata:
                files.append(mark.response.metadata["path"])

        return tuple(set(files))  # Deduplicate

    # =========================================================================
    # Search Operations
    # =========================================================================

    async def search_marks(self, query: str, limit: int = 50) -> list[dict[str, Any]]:
        """
        Search marks by text query.

        Searches in:
        - Mark response content
        - Tags
        - Metadata

        Args:
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of matching marks as dictionaries
        """
        results: list[dict[str, Any]] = []
        query_lower = query.lower()

        try:
            mark_store = self._get_mark_store()

            for mark in mark_store.all():
                # Search in response content
                if mark.response.content and query_lower in mark.response.content.lower():
                    results.append(self._mark_to_dict(mark))
                    continue

                # Search in tags
                if any(query_lower in t.lower() for t in mark.tags):
                    results.append(self._mark_to_dict(mark))
                    continue

                # Search in origin
                if query_lower in mark.origin.lower():
                    results.append(self._mark_to_dict(mark))
                    continue

                if len(results) >= limit:
                    break
        except Exception as e:
            logger.error(f"Error searching marks: {e}")

        return results[:limit]

    def _mark_to_dict(self, mark: Any) -> dict[str, Any]:
        """Convert a mark to a dictionary."""
        return {
            "id": str(mark.id),
            "origin": mark.origin,
            "domain": mark.domain,
            "timestamp": mark.timestamp.isoformat(),
            "stimulus": mark.stimulus.to_dict() if mark.stimulus else None,
            "response": mark.response.to_dict() if mark.response else None,
            "tags": list(mark.tags),
            "phase": mark.phase.value if mark.phase else None,
            "is_sealed": mark.is_sealed,
        }

    async def get_marks_for_file(self, path: str, limit: int = 50) -> list[dict[str, Any]]:
        """
        Get marks related to a specific file.

        Args:
            path: File path to search for
            limit: Maximum results to return

        Returns:
            List of marks related to the file
        """
        results: list[dict[str, Any]] = []

        try:
            mark_store = self._get_mark_store()

            for mark in mark_store.all():
                # Check metadata for file path
                if mark.metadata:
                    for key in ("file_path", "path", "kblock_path"):
                        if key in mark.metadata and path in mark.metadata[key]:
                            results.append(self._mark_to_dict(mark))
                            break

                # Check tags for path reference
                if any(path in t for t in mark.tags):
                    if mark.id not in [r["id"] for r in results]:
                        results.append(self._mark_to_dict(mark))

                if len(results) >= limit:
                    break
        except Exception as e:
            logger.error(f"Error getting marks for file: {e}")

        return results[:limit]

    async def get_crystals_for_file(self, path: str, limit: int = 20) -> list[dict[str, Any]]:
        """
        Get crystals related to a specific file.

        Since crystals don't track files directly, this searches in
        topics and insight text.

        Args:
            path: File path to search for
            limit: Maximum results to return

        Returns:
            List of crystals that mention the file
        """
        results: list[dict[str, Any]] = []

        try:
            crystal_store = self._get_crystal_store()

            for crystal in crystal_store.all():
                # Check if file mentioned in insight
                if path in crystal.insight:
                    results.append(crystal.to_dict())
                    continue

                # Check topics
                if any(path in topic for topic in crystal.topics):
                    results.append(crystal.to_dict())
                    continue

                if len(results) >= limit:
                    break
        except Exception as e:
            logger.error(f"Error getting crystals for file: {e}")

        return results[:limit]

    # =========================================================================
    # Activity Analysis
    # =========================================================================

    async def get_development_activity(
        self,
        period: str = "week",
    ) -> DevelopmentActivity:
        """
        Get summary of development activity over a period.

        Args:
            period: Time period ('day', 'week', 'month')

        Returns:
            DevelopmentActivity with aggregated statistics
        """
        now = datetime.now(timezone.utc)

        # Calculate date range
        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "week":
            start_date = now - timedelta(weeks=1)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(weeks=1)

        # Collect events in range
        filter = TimelineFilter(date_from=start_date, date_to=now)
        events = await self.get_timeline(filter=filter, limit=10000)

        # Count by day
        events_by_day: dict[str, int] = {}
        events_by_actor: dict[str, int] = {}
        events_by_type: dict[str, int] = {}
        file_counts: dict[str, int] = {}
        tag_counts: dict[str, int] = {}

        mark_count = 0
        crystal_count = 0
        decision_count = 0

        for event in events:
            # Count by day
            day_key = event.timestamp.strftime("%Y-%m-%d")
            events_by_day[day_key] = events_by_day.get(day_key, 0) + 1

            # Count by actor
            events_by_actor[event.actor.value] = events_by_actor.get(event.actor.value, 0) + 1

            # Count by type
            events_by_type[event.event_type.value] = (
                events_by_type.get(event.event_type.value, 0) + 1
            )

            # Type-specific counts
            if event.event_type == EventType.MARK:
                mark_count += 1
            elif event.event_type == EventType.CRYSTAL:
                crystal_count += 1
            elif event.event_type == EventType.DECISION:
                decision_count += 1

            # Count files
            for f in event.related_files:
                file_counts[f] = file_counts.get(f, 0) + 1

            # Count tags
            for t in event.tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1

        # Top files and tags
        top_files = tuple(sorted(file_counts.items(), key=lambda x: -x[1])[:10])
        top_tags = tuple(sorted(tag_counts.items(), key=lambda x: -x[1])[:10])

        return DevelopmentActivity(
            period=period,
            start_date=start_date,
            end_date=now,
            total_marks=mark_count,
            total_crystals=crystal_count,
            total_decisions=decision_count,
            events_by_day=events_by_day,
            events_by_actor=events_by_actor,
            events_by_type=events_by_type,
            top_files=top_files,
            top_tags=top_tags,
        )


# =============================================================================
# Factory Functions
# =============================================================================

_global_service: WitnessTimelineService | None = None


def get_witness_timeline_service() -> WitnessTimelineService:
    """Get the global witness timeline service (singleton)."""
    global _global_service
    if _global_service is None:
        _global_service = WitnessTimelineService()
    return _global_service


def create_witness_timeline_service(
    persistence: Any | None = None,
    mark_store: Any | None = None,
    crystal_store: Any | None = None,
) -> WitnessTimelineService:
    """
    Create a new witness timeline service with dependencies.

    Args:
        persistence: WitnessPersistence instance
        mark_store: MarkStore instance
        crystal_store: CrystalStore instance

    Returns:
        New WitnessTimelineService instance
    """
    return WitnessTimelineService(
        persistence=persistence,
        mark_store=mark_store,
        crystal_store=crystal_store,
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Enums
    "EventType",
    "ActorType",
    # Data Models
    "TimelineEvent",
    "TimelineFilter",
    "DevelopmentActivity",
    # Service
    "WitnessTimelineService",
    # Factory
    "get_witness_timeline_service",
    "create_witness_timeline_service",
]
