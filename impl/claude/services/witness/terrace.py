"""
Terrace: Curated Knowledge Layer with Versioning.

A Terrace is a curated piece of knowledge that:
- Is immutable once created
- Has versions that supersede previous ones
- Maintains full history for evolution tracking
- Serves as the source of truth for patterns and learnings

Philosophy:
    "Knowledge crystallizes over time. A Terrace captures what we've
    learned, versioned for evolution. Like geological terraces, each
    layer builds on the last."

    The name evokes:
    - Rice terraces: Carefully cultivated, layered knowledge
    - Geological strata: History preserved in layers
    - Garden terraces: Curated, intentional arrangement

Laws:
- Law 1 (Immutability): Terraces are frozen after creation
- Law 2 (Supersession): New versions explicitly supersede old
- Law 3 (History Preserved): All versions are kept for reference
- Law 4 (Topic Uniqueness): One current version per topic

See: spec/protocols/warp-primitives.md
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

TerraceId = NewType("TerraceId", str)


def generate_terrace_id() -> TerraceId:
    """Generate a unique Terrace ID."""
    return TerraceId(f"terrace-{uuid4().hex[:12]}")


# =============================================================================
# Terrace Status
# =============================================================================


class TerraceStatus(Enum):
    """Status of a Terrace."""

    CURRENT = auto()  # The current version for its topic
    SUPERSEDED = auto()  # Replaced by a newer version
    DEPRECATED = auto()  # Marked as no longer recommended
    ARCHIVED = auto()  # Kept for historical reference only


# =============================================================================
# Terrace: The Core Primitive
# =============================================================================


@dataclass(frozen=True)
class Terrace:
    """
    Curated knowledge with versioning.

    Laws:
    - Law 1 (Immutability): Frozen after creation
    - Law 2 (Supersession): supersedes field links to previous version
    - Law 3 (History Preserved): All versions kept
    - Law 4 (Topic Uniqueness): One CURRENT per topic

    A Terrace represents crystallized knowledge about a topic.
    When knowledge evolves, a new Terrace is created that supersedes
    the old one, preserving the history of understanding.

    Example:
        >>> v1 = Terrace.create(
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
    id: TerraceId = field(default_factory=generate_terrace_id)

    # Content
    topic: str = ""  # e.g., "AGENTESE registration", "Testing patterns"
    content: str = ""  # The curated knowledge

    # Versioning (Law 2)
    version: int = 1
    supersedes: TerraceId | None = None  # ID of version this replaces

    # Status
    status: TerraceStatus = TerraceStatus.CURRENT

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
    ) -> Terrace:
        """
        Create a new Terrace (version 1).

        Law 1: The Terrace is immutable from creation.
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
    ) -> Terrace:
        """
        Create a new version that supersedes this one.

        Law 2: New versions explicitly supersede old.
        Law 3: Old version is preserved (this returns a NEW Terrace).

        Args:
            content: Updated content
            reason: Why this evolution occurred
            tags: New tags (or inherit from previous)
            confidence: New confidence (or inherit)

        Returns:
            New Terrace with incremented version
        """
        return Terrace(
            topic=self.topic,
            content=content,
            version=self.version + 1,
            supersedes=self.id,
            status=TerraceStatus.CURRENT,
            evolution_reason=reason,
            tags=tags if tags is not None else self.tags,
            source=self.source,
            confidence=confidence if confidence is not None else self.confidence,
            metadata={**self.metadata, "evolved_from": str(self.id)},
        )

    def deprecate(self, reason: str = "") -> Terrace:
        """
        Mark this Terrace as deprecated.

        Creates a new Terrace with DEPRECATED status.
        """
        return Terrace(
            id=self.id,
            topic=self.topic,
            content=self.content,
            version=self.version,
            supersedes=self.supersedes,
            status=TerraceStatus.DEPRECATED,
            created_at=self.created_at,
            evolution_reason=reason or "Deprecated",
            tags=self.tags,
            source=self.source,
            confidence=self.confidence,
            metadata={**self.metadata, "deprecated_at": datetime.now().isoformat()},
        )

    def archive(self) -> Terrace:
        """Mark this Terrace as archived."""
        return Terrace(
            id=self.id,
            topic=self.topic,
            content=self.content,
            version=self.version,
            supersedes=self.supersedes,
            status=TerraceStatus.ARCHIVED,
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
        return self.status == TerraceStatus.CURRENT

    @property
    def is_superseded(self) -> bool:
        """Check if this has been superseded."""
        return self.status == TerraceStatus.SUPERSEDED

    @property
    def is_deprecated(self) -> bool:
        """Check if this is deprecated."""
        return self.status == TerraceStatus.DEPRECATED

    @property
    def has_supersedes(self) -> bool:
        """Check if this supersedes another version."""
        return self.supersedes is not None

    @property
    def age_days(self) -> float:
        """Get the age of this Terrace in days."""
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
    def from_dict(cls, data: dict[str, Any]) -> Terrace:
        """Create from dictionary."""
        return cls(
            id=TerraceId(data["id"]),
            topic=data.get("topic", ""),
            content=data.get("content", ""),
            version=data.get("version", 1),
            supersedes=TerraceId(data["supersedes"]) if data.get("supersedes") else None,
            status=TerraceStatus[data.get("status", "CURRENT")],
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
            f"Terrace(id={str(self.id)[:16]}..., "
            f"topic='{topic}', "
            f"v{self.version}, "
            f"status={self.status.name})"
        )


# =============================================================================
# TerraceStore: Persistent Storage
# =============================================================================


@dataclass
class TerraceStore:
    """
    Persistent storage for Terraces.

    Enforces Law 4: One current version per topic.

    Provides:
    - Topic-based retrieval (current version)
    - Full history per topic
    - Search by tags
    - Version traversal
    """

    _terraces: dict[TerraceId, Terrace] = field(default_factory=dict)
    _topic_index: dict[str, list[TerraceId]] = field(default_factory=dict)

    # =========================================================================
    # Add/Update
    # =========================================================================

    def add(self, terrace: Terrace) -> None:
        """
        Add a Terrace to the store.

        Law 4: Marks previous version as SUPERSEDED if exists.
        """
        # If this supersedes another, mark that one as superseded
        if terrace.supersedes and terrace.supersedes in self._terraces:
            old = self._terraces[terrace.supersedes]
            superseded = Terrace(
                id=old.id,
                topic=old.topic,
                content=old.content,
                version=old.version,
                supersedes=old.supersedes,
                status=TerraceStatus.SUPERSEDED,
                created_at=old.created_at,
                evolution_reason=old.evolution_reason,
                tags=old.tags,
                source=old.source,
                confidence=old.confidence,
                metadata={**old.metadata, "superseded_by": str(terrace.id)},
            )
            self._terraces[old.id] = superseded

        # Add to main storage
        self._terraces[terrace.id] = terrace

        # Update topic index
        if terrace.topic not in self._topic_index:
            self._topic_index[terrace.topic] = []
        if terrace.id not in self._topic_index[terrace.topic]:
            self._topic_index[terrace.topic].append(terrace.id)

    def update(self, terrace: Terrace) -> None:
        """Update an existing Terrace (for status changes)."""
        self._terraces[terrace.id] = terrace

    # =========================================================================
    # Retrieval
    # =========================================================================

    def get(self, terrace_id: TerraceId) -> Terrace | None:
        """Get a Terrace by ID."""
        return self._terraces.get(terrace_id)

    def current(self, topic: str) -> Terrace | None:
        """
        Get the current (latest) version for a topic.

        Law 4: Returns the one CURRENT version.
        """
        if topic not in self._topic_index:
            return None

        for tid in reversed(self._topic_index[topic]):
            terrace = self._terraces.get(tid)
            if terrace and terrace.is_current:
                return terrace

        return None

    def history(self, topic: str) -> list[Terrace]:
        """
        Get version history for a topic.

        Law 3: All versions are preserved.

        Returns versions ordered from oldest to newest.
        """
        if topic not in self._topic_index:
            return []

        terraces = []
        for tid in self._topic_index[topic]:
            terrace = self._terraces.get(tid)
            if terrace:
                terraces.append(terrace)

        return sorted(terraces, key=lambda t: t.version)

    def latest(self, topic: str) -> Terrace | None:
        """Get the latest version for a topic (regardless of status)."""
        history = self.history(topic)
        return history[-1] if history else None

    # =========================================================================
    # Search
    # =========================================================================

    def by_tag(self, tag: str) -> list[Terrace]:
        """Get all CURRENT Terraces with a specific tag."""
        return [t for t in self._terraces.values() if t.is_current and tag in t.tags]

    def by_source(self, source: str) -> list[Terrace]:
        """Get all CURRENT Terraces from a specific source."""
        return [t for t in self._terraces.values() if t.is_current and t.source == source]

    def search(self, query: str) -> list[Terrace]:
        """
        Search CURRENT Terraces by topic or content.

        Case-insensitive substring match.
        """
        query_lower = query.lower()
        return [
            t
            for t in self._terraces.values()
            if t.is_current and (query_lower in t.topic.lower() or query_lower in t.content.lower())
        ]

    # =========================================================================
    # Listing
    # =========================================================================

    def all_current(self) -> list[Terrace]:
        """Get all CURRENT Terraces."""
        return [t for t in self._terraces.values() if t.is_current]

    def all_topics(self) -> list[str]:
        """Get all topics."""
        return list(self._topic_index.keys())

    def deprecated(self) -> list[Terrace]:
        """Get all deprecated Terraces."""
        return [t for t in self._terraces.values() if t.is_deprecated]

    def recent(self, limit: int = 10) -> list[Terrace]:
        """Get most recently created Terraces."""
        sorted_terraces = sorted(
            self._terraces.values(),
            key=lambda t: t.created_at,
            reverse=True,
        )
        return sorted_terraces[:limit]

    # =========================================================================
    # Version Traversal
    # =========================================================================

    def predecessor(self, terrace: Terrace) -> Terrace | None:
        """Get the version this Terrace supersedes."""
        if terrace.supersedes:
            return self._terraces.get(terrace.supersedes)
        return None

    def successor(self, terrace: Terrace) -> Terrace | None:
        """Get the version that superseded this one (if any)."""
        for t in self._terraces.values():
            if t.supersedes == terrace.id:
                return t
        return None

    def full_chain(self, topic: str) -> list[Terrace]:
        """Get the full version chain for a topic, ordered by version."""
        return self.history(topic)

    # =========================================================================
    # Statistics
    # =========================================================================

    def stats(self) -> dict[str, int]:
        """Get store statistics."""
        current = sum(1 for t in self._terraces.values() if t.is_current)
        superseded = sum(1 for t in self._terraces.values() if t.is_superseded)
        deprecated = sum(1 for t in self._terraces.values() if t.is_deprecated)

        return {
            "total": len(self._terraces),
            "topics": len(self._topic_index),
            "current": current,
            "superseded": superseded,
            "deprecated": deprecated,
        }

    def __len__(self) -> int:
        return len(self._terraces)


# =============================================================================
# Global Store
# =============================================================================

_global_terrace_store: TerraceStore | None = None


def get_terrace_store() -> TerraceStore:
    """Get the global terrace store."""
    global _global_terrace_store
    if _global_terrace_store is None:
        _global_terrace_store = TerraceStore()
    return _global_terrace_store


def set_terrace_store(store: TerraceStore) -> None:
    """Set the global terrace store."""
    global _global_terrace_store
    _global_terrace_store = store


def reset_terrace_store() -> None:
    """Reset the global terrace store (for testing)."""
    global _global_terrace_store
    _global_terrace_store = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases
    "TerraceId",
    "generate_terrace_id",
    # Status
    "TerraceStatus",
    # Core
    "Terrace",
    # Store
    "TerraceStore",
    "get_terrace_store",
    "set_terrace_store",
    "reset_terrace_store",
]
