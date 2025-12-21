"""
Lesson: Curated Knowledge Layer with Versioning.

A Lesson is a curated piece of knowledge that:
- Is immutable once created
- Has versions that supersede previous ones
- Maintains full history for evolution tracking
- Serves as the source of truth for patterns and learnings

Philosophy:
    "Knowledge crystallizes over time. A Lesson captures what we've
    learned, versioned for evolution. Like lessons learned, each
    builds on the last."

Rename History:
    Lesson → Lesson (spec/protocols/witness-primitives.md)
    "Lessons learned" - clearer than geological metaphor

Laws:
- Law 1 (Immutability): Lessons are frozen after creation
- Law 2 (Supersession): New versions explicitly supersede old
- Law 3 (History Preserved): All versions are kept for reference
- Law 4 (Topic Uniqueness): One current version per topic

See: spec/protocols/witness-primitives.md
See: docs/skills/crown-jewel-patterns.md (Pattern 7: Append-Only History)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, NewType
from uuid import uuid4

# =============================================================================
# Type Aliases
# =============================================================================

LessonId = NewType("LessonId", str)

# Backwards compatibility alias
LessonId = LessonId


def generate_lesson_id() -> LessonId:
    """Generate a unique Lesson ID."""
    return LessonId(f"lesson-{uuid4().hex[:12]}")


# Backwards compatibility alias
generate_lesson_id = generate_lesson_id


# =============================================================================
# Lesson Status
# =============================================================================


class LessonStatus(Enum):
    """Status of a Lesson."""

    CURRENT = auto()  # The current version for its topic
    SUPERSEDED = auto()  # Replaced by a newer version
    DEPRECATED = auto()  # Marked as no longer recommended
    ARCHIVED = auto()  # Kept for historical reference only


# Backwards compatibility alias
LessonStatus = LessonStatus


# =============================================================================
# Lesson: The Core Primitive
# =============================================================================


@dataclass(frozen=True)
class Lesson:
    """
    Curated knowledge with versioning.

    Laws:
    - Law 1 (Immutability): Frozen after creation
    - Law 2 (Supersession): supersedes field links to previous version
    - Law 3 (History Preserved): All versions kept
    - Law 4 (Topic Uniqueness): One CURRENT per topic

    A Lesson represents crystallized knowledge about a topic.
    When knowledge evolves, a new Lesson is created that supersedes
    the old one, preserving the history of understanding.

    Example:
        >>> v1 = Lesson.create(
        ...     topic="AGENTESE registration",
        ...     content="Use @node decorator. Register in gateway.",
        ... )
        >>> v2 = v1.evolve(
        ...     content="Use @node decorator. Ensure import in gateway. Watch for silent skip.",
        ...     reason="Added silent skip warning from debugging session",
        ... )
        >>> v2.version  # 2
        >>> v2.supersedes  # v1.id
    """

    # Identity
    id: LessonId = field(default_factory=generate_lesson_id)

    # Content
    topic: str = ""  # e.g., "AGENTESE registration", "Testing patterns"
    content: str = ""  # The curated knowledge

    # Versioning (Law 2)
    version: int = 1
    supersedes: LessonId | None = None  # ID of version this replaces

    # Status
    status: LessonStatus = LessonStatus.CURRENT

    # Timing
    created_at: datetime = field(default_factory=datetime.now)

    # Evolution tracking
    evolution_reason: str = ""  # Why this version was created

    # Metadata
    tags: tuple[str, ...] = ()
    source: str = ""  # Where this knowledge came from
    confidence: float = 1.0  # How confident we are (0.0-1.0)
    metadata: dict[str, Any] = field(default_factory=dict)

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def create(
        cls,
        topic: str,
        content: str,
        tags: tuple[str, ...] = (),
        source: str = "",
        confidence: float = 1.0,
    ) -> Lesson:
        """
        Create a new Lesson (version 1).

        Law 1: The Lesson is immutable from creation.
        """
        return cls(
            topic=topic,
            content=content,
            version=1,
            tags=tags,
            source=source,
            confidence=confidence,
        )

    # =========================================================================
    # Evolution (Law 2)
    # =========================================================================

    def evolve(
        self,
        content: str,
        reason: str = "",
        tags: tuple[str, ...] | None = None,
        confidence: float | None = None,
    ) -> Lesson:
        """
        Create a new version that supersedes this one.

        Law 2: New versions explicitly supersede old.
        Law 3: Old version is preserved (this returns a NEW Lesson).

        Args:
            content: Updated content
            reason: Why this evolution occurred
            tags: New tags (or inherit from previous)
            confidence: New confidence (or inherit)

        Returns:
            New Lesson with incremented version
        """
        return Lesson(
            topic=self.topic,
            content=content,
            version=self.version + 1,
            supersedes=self.id,
            status=LessonStatus.CURRENT,
            evolution_reason=reason,
            tags=tags if tags is not None else self.tags,
            source=self.source,
            confidence=confidence if confidence is not None else self.confidence,
            metadata={**self.metadata, "evolved_from": str(self.id)},
        )

    def deprecate(self, reason: str = "") -> Lesson:
        """
        Mark this Lesson as deprecated.

        Creates a new Lesson with DEPRECATED status.
        """
        return Lesson(
            id=self.id,
            topic=self.topic,
            content=self.content,
            version=self.version,
            supersedes=self.supersedes,
            status=LessonStatus.DEPRECATED,
            created_at=self.created_at,
            evolution_reason=reason or "Deprecated",
            tags=self.tags,
            source=self.source,
            confidence=self.confidence,
            metadata={**self.metadata, "deprecated_at": datetime.now().isoformat()},
        )

    def archive(self) -> Lesson:
        """Mark this Lesson as archived."""
        return Lesson(
            id=self.id,
            topic=self.topic,
            content=self.content,
            version=self.version,
            supersedes=self.supersedes,
            status=LessonStatus.ARCHIVED,
            created_at=self.created_at,
            evolution_reason=self.evolution_reason,
            tags=self.tags,
            source=self.source,
            confidence=self.confidence,
            metadata={**self.metadata, "archived_at": datetime.now().isoformat()},
        )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_current(self) -> bool:
        """Check if this is the current version."""
        return self.status == LessonStatus.CURRENT

    @property
    def is_superseded(self) -> bool:
        """Check if this has been superseded."""
        return self.status == LessonStatus.SUPERSEDED

    @property
    def is_deprecated(self) -> bool:
        """Check if this is deprecated."""
        return self.status == LessonStatus.DEPRECATED

    @property
    def has_supersedes(self) -> bool:
        """Check if this supersedes another version."""
        return self.supersedes is not None

    @property
    def age_days(self) -> float:
        """Get the age of this Lesson in days."""
        delta = datetime.now() - self.created_at
        return delta.total_seconds() / (24 * 3600)

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "topic": self.topic,
            "content": self.content,
            "version": self.version,
            "supersedes": str(self.supersedes) if self.supersedes else None,
            "status": self.status.name,
            "created_at": self.created_at.isoformat(),
            "evolution_reason": self.evolution_reason,
            "tags": list(self.tags),
            "source": self.source,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Lesson:
        """Create from dictionary."""
        return cls(
            id=LessonId(data["id"]),
            topic=data.get("topic", ""),
            content=data.get("content", ""),
            version=data.get("version", 1),
            supersedes=LessonId(data["supersedes"]) if data.get("supersedes") else None,
            status=LessonStatus[data.get("status", "CURRENT")],
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(),
            evolution_reason=data.get("evolution_reason", ""),
            tags=tuple(data.get("tags", [])),
            source=data.get("source", ""),
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        topic = self.topic[:25] + "..." if len(self.topic) > 25 else self.topic
        return (
            f"Lesson(id={str(self.id)[:16]}..., "
            f"topic='{topic}', "
            f"v{self.version}, "
            f"status={self.status.name})"
        )


# Backwards compatibility alias
Lesson = Lesson


# =============================================================================
# LessonStore: Persistent Storage
# =============================================================================


@dataclass
class LessonStore:
    """
    Persistent storage for Lessons.

    Enforces Law 4: One current version per topic.

    Provides:
    - Topic-based retrieval (current version)
    - Full history per topic
    - Search by tags
    - Version traversal
    """

    _lessons: dict[LessonId, Lesson] = field(default_factory=dict)
    _topic_index: dict[str, list[LessonId]] = field(default_factory=dict)

    # =========================================================================
    # Add/Update
    # =========================================================================

    def add(self, lesson: Lesson) -> None:
        """
        Add a Lesson to the store.

        Law 4: Marks previous version as SUPERSEDED if exists.
        """
        # If this supersedes another, mark that one as superseded
        if lesson.supersedes and lesson.supersedes in self._lessons:
            old = self._lessons[lesson.supersedes]
            superseded = Lesson(
                id=old.id,
                topic=old.topic,
                content=old.content,
                version=old.version,
                supersedes=old.supersedes,
                status=LessonStatus.SUPERSEDED,
                created_at=old.created_at,
                evolution_reason=old.evolution_reason,
                tags=old.tags,
                source=old.source,
                confidence=old.confidence,
                metadata={**old.metadata, "superseded_by": str(lesson.id)},
            )
            self._lessons[old.id] = superseded

        # Add to main storage
        self._lessons[lesson.id] = lesson

        # Update topic index
        if lesson.topic not in self._topic_index:
            self._topic_index[lesson.topic] = []
        if lesson.id not in self._topic_index[lesson.topic]:
            self._topic_index[lesson.topic].append(lesson.id)

    def update(self, lesson: Lesson) -> None:
        """Update an existing Lesson (for status changes)."""
        self._lessons[lesson.id] = lesson

    # =========================================================================
    # Retrieval
    # =========================================================================

    def get(self, lesson_id: LessonId) -> Lesson | None:
        """Get a Lesson by ID."""
        return self._lessons.get(lesson_id)

    def current(self, topic: str) -> Lesson | None:
        """
        Get the current (latest) version for a topic.

        Law 4: Returns the one CURRENT version.
        """
        if topic not in self._topic_index:
            return None

        for lid in reversed(self._topic_index[topic]):
            lesson = self._lessons.get(lid)
            if lesson and lesson.is_current:
                return lesson

        return None

    def history(self, topic: str) -> list[Lesson]:
        """
        Get version history for a topic.

        Law 3: All versions are preserved.

        Returns versions ordered from oldest to newest.
        """
        if topic not in self._topic_index:
            return []

        lessons = []
        for lid in self._topic_index[topic]:
            lesson = self._lessons.get(lid)
            if lesson:
                lessons.append(lesson)

        return sorted(lessons, key=lambda l: l.version)

    def latest(self, topic: str) -> Lesson | None:
        """Get the latest version for a topic (regardless of status)."""
        history = self.history(topic)
        return history[-1] if history else None

    # =========================================================================
    # Search
    # =========================================================================

    def by_tag(self, tag: str) -> list[Lesson]:
        """Get all CURRENT Lessons with a specific tag."""
        return [l for l in self._lessons.values() if l.is_current and tag in l.tags]

    def by_source(self, source: str) -> list[Lesson]:
        """Get all CURRENT Lessons from a specific source."""
        return [l for l in self._lessons.values() if l.is_current and l.source == source]

    def search(self, query: str) -> list[Lesson]:
        """
        Search CURRENT Lessons by topic or content.

        Case-insensitive substring match.
        """
        query_lower = query.lower()
        return [
            l
            for l in self._lessons.values()
            if l.is_current and (query_lower in l.topic.lower() or query_lower in l.content.lower())
        ]

    # =========================================================================
    # Listing
    # =========================================================================

    def all_current(self) -> list[Lesson]:
        """Get all CURRENT Lessons."""
        return [l for l in self._lessons.values() if l.is_current]

    def all_topics(self) -> list[str]:
        """Get all topics."""
        return list(self._topic_index.keys())

    def deprecated(self) -> list[Lesson]:
        """Get all deprecated Lessons."""
        return [l for l in self._lessons.values() if l.is_deprecated]

    def recent(self, limit: int = 10) -> list[Lesson]:
        """Get most recently created Lessons."""
        sorted_lessons = sorted(
            self._lessons.values(),
            key=lambda l: l.created_at,
            reverse=True,
        )
        return sorted_lessons[:limit]

    # =========================================================================
    # Version Traversal
    # =========================================================================

    def predecessor(self, lesson: Lesson) -> Lesson | None:
        """Get the version this Lesson supersedes."""
        if lesson.supersedes:
            return self._lessons.get(lesson.supersedes)
        return None

    def successor(self, lesson: Lesson) -> Lesson | None:
        """Get the version that superseded this one (if any)."""
        for l in self._lessons.values():
            if l.supersedes == lesson.id:
                return l
        return None

    def full_chain(self, topic: str) -> list[Lesson]:
        """Get the full version chain for a topic, ordered by version."""
        return self.history(topic)

    # =========================================================================
    # Statistics
    # =========================================================================

    def stats(self) -> dict[str, int]:
        """Get store statistics."""
        current = sum(1 for l in self._lessons.values() if l.is_current)
        superseded = sum(1 for l in self._lessons.values() if l.is_superseded)
        deprecated = sum(1 for l in self._lessons.values() if l.is_deprecated)

        return {
            "total": len(self._lessons),
            "topics": len(self._topic_index),
            "current": current,
            "superseded": superseded,
            "deprecated": deprecated,
        }

    def __len__(self) -> int:
        return len(self._lessons)


# Backwards compatibility alias
LessonStore = LessonStore


# =============================================================================
# Global Store
# =============================================================================

_global_lesson_store: LessonStore | None = None


def get_lesson_store() -> LessonStore:
    """Get the global lesson store."""
    global _global_lesson_store
    if _global_lesson_store is None:
        _global_lesson_store = LessonStore()
    return _global_lesson_store


# Backwards compatibility alias
get_lesson_store = get_lesson_store


def set_lesson_store(store: LessonStore) -> None:
    """Set the global lesson store."""
    global _global_lesson_store
    _global_lesson_store = store


# Backwards compatibility alias
set_lesson_store = set_lesson_store


def reset_lesson_store() -> None:
    """Reset the global lesson store (for testing)."""
    global _global_lesson_store
    _global_lesson_store = None


# Backwards compatibility alias
reset_lesson_store = reset_lesson_store


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases (new names)
    "LessonId",
    "generate_lesson_id",
    # Backwards compatibility
    "LessonId",
    "generate_lesson_id",
    # Status (new name)
    "LessonStatus",
    # Backwards compatibility
    "LessonStatus",
    # Core (new name)
    "Lesson",
    # Backwards compatibility
    "Lesson",
    # Store (new name)
    "LessonStore",
    "get_lesson_store",
    "set_lesson_store",
    "reset_lesson_store",
    # Backwards compatibility
    "LessonStore",
    "get_lesson_store",
    "set_lesson_store",
    "reset_lesson_store",
]
