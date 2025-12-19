"""
Lifecycle-Aware Ghost Cache: TTL and Human Labels for Cache Entries.

The meta principle: "human readable with safeguards by default construction."

Every cache entry must have:
1. A human_label explaining what it is
2. A TTL defining when it expires
3. Metadata for debugging and audit

This module extends GlassCacheManager with lifecycle awareness,
integrating with the memory substrate's LifecyclePolicy.

Key Types:
- LifecycleCacheEntry: Cache entry with lifecycle metadata
- LifecycleAwareCache: Cache manager with TTL and expiration
- ExpirationEvent: Record of an expiration
- LifecycleStats: Cache health statistics

The categorical insight: cache entries are morphisms from Time to Value,
with TTL defining the codomain's extent.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generic, TypeVar

from .cache import GLASS_CACHE_DIR, GlassCacheManager

T = TypeVar("T")


# =============================================================================
# Lifecycle Cache Entry
# =============================================================================


@dataclass
class LifecycleCacheEntry(Generic[T]):
    """
    Cache entry with lifecycle metadata.

    Every entry must have a human_label (no anonymous debris).
    """

    key: str
    data: T
    human_label: str  # REQUIRED: explains what this is
    ttl: timedelta = field(default_factory=lambda: timedelta(hours=24))
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    agentese_path: str | None = None  # Optional AGENTESE path that created this
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.human_label:
            raise ValueError("human_label is required (no anonymous debris)")

    @property
    def expires_at(self) -> datetime:
        """When this entry expires."""
        return self.created_at + self.ttl

    @property
    def age(self) -> timedelta:
        """How old this entry is."""
        return datetime.now() - self.created_at

    @property
    def time_until_expiration(self) -> timedelta:
        """Time remaining until expiration."""
        return self.expires_at - datetime.now()

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return datetime.now() > self.expires_at

    def access(self) -> None:
        """Record an access."""
        self.last_accessed = datetime.now()
        self.access_count += 1

    def refresh(self, new_ttl: timedelta | None = None) -> None:
        """
        Refresh the entry's TTL.

        Args:
            new_ttl: New TTL (uses original if not provided)
        """
        self.created_at = datetime.now()
        if new_ttl:
            self.ttl = new_ttl

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "data": self.data,
            "human_label": self.human_label,
            "ttl_seconds": self.ttl.total_seconds(),
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "agentese_path": self.agentese_path,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LifecycleCacheEntry[Any]":
        """Create from dictionary."""
        return cls(
            key=data["key"],
            data=data["data"],
            human_label=data["human_label"],
            ttl=timedelta(seconds=data.get("ttl_seconds", 86400)),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            access_count=data.get("access_count", 0),
            agentese_path=data.get("agentese_path"),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Expiration Event
# =============================================================================


@dataclass
class ExpirationEvent:
    """Record of a cache expiration."""

    key: str
    human_label: str
    expired_at: datetime
    age_when_expired: timedelta
    access_count: int
    reason: str  # "ttl", "manual", "evicted"


# =============================================================================
# Lifecycle Stats
# =============================================================================


@dataclass
class LifecycleStats:
    """Statistics about cache lifecycle."""

    total_entries: int
    expired_count: int
    active_count: int
    avg_age_seconds: float
    avg_ttl_seconds: float
    avg_access_count: float
    oldest_entry_age_seconds: float
    entries_by_label: dict[str, int]


# =============================================================================
# Lifecycle-Aware Cache
# =============================================================================


class LifecycleAwareCache:
    """
    Cache manager with lifecycle awareness.

    Extends GlassCacheManager with:
    - TTL tracking and expiration
    - Human labels (required)
    - Access tracking
    - Automatic cleanup

    The meta principle: no anonymous debris. Every cache entry
    must explain what it is and when it should expire.

    Example:
        cache = LifecycleAwareCache()

        # Write with lifecycle
        cache.write(
            key="cortex_status",
            data={"health": "OK"},
            human_label="Cortex health status snapshot",
            ttl=timedelta(hours=1),
        )

        # Read with lifecycle info
        entry = cache.read("cortex_status")
        if entry and not entry.is_expired():
            print(f"Status: {entry.data}")
            print(f"Expires in: {entry.time_until_expiration}")

        # Cleanup expired
        expired = cache.cleanup_expired()
    """

    def __init__(
        self,
        cache_dir: Path | None = None,
        default_ttl: timedelta | None = None,
    ) -> None:
        """
        Initialize lifecycle-aware cache.

        Args:
            cache_dir: Cache directory (default ~/.kgents/ghost/)
            default_ttl: Default TTL for entries (default 24 hours)
        """
        self._base = GlassCacheManager(cache_dir)
        self._default_ttl = default_ttl or timedelta(hours=24)
        self._expiration_events: list[ExpirationEvent] = []
        self._entries: dict[str, LifecycleCacheEntry[Any]] = {}
        self._load_existing()

    def _load_existing(self) -> None:
        """Load existing entries from disk."""
        self._base.ensure_structure()
        for key in self._base.get_all_keys():
            try:
                raw, _ = self._base.read(key)
                if raw and isinstance(raw, dict) and "human_label" in raw:
                    # This is a lifecycle entry
                    entry = LifecycleCacheEntry.from_dict(raw)
                    self._entries[key] = entry
            except (json.JSONDecodeError, KeyError, TypeError):
                # Not a lifecycle entry or corrupted
                pass

    def write(
        self,
        key: str,
        data: Any,
        human_label: str,
        ttl: timedelta | None = None,
        agentese_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> LifecycleCacheEntry[Any]:
        """
        Write data with lifecycle metadata.

        Args:
            key: Cache key
            data: Data to cache
            human_label: REQUIRED - explains what this is
            ttl: Time to live (default 24 hours)
            agentese_path: Optional AGENTESE path
            metadata: Optional additional metadata

        Returns:
            The created LifecycleCacheEntry

        Raises:
            ValueError: If human_label is empty
        """
        if not human_label:
            raise ValueError("human_label is required (no anonymous debris)")

        entry: LifecycleCacheEntry[Any] = LifecycleCacheEntry(
            key=key,
            data=data,
            human_label=human_label,
            ttl=ttl or self._default_ttl,
            agentese_path=agentese_path,
            metadata=metadata or {},
        )

        # Store in memory
        self._entries[key] = entry

        # Persist to disk
        self._base.write(
            key=key,
            data=entry.to_dict(),
            agentese_path=agentese_path,
            metadata={"lifecycle": True, "human_label": human_label},
        )

        return entry

    def read(self, key: str) -> LifecycleCacheEntry[Any] | None:
        """
        Read entry with lifecycle metadata.

        Args:
            key: Cache key

        Returns:
            LifecycleCacheEntry or None if not found
        """
        entry = self._entries.get(key)
        if entry:
            entry.access()
            return entry
        return None

    def read_if_valid(self, key: str) -> LifecycleCacheEntry[Any] | None:
        """
        Read entry only if not expired.

        Args:
            key: Cache key

        Returns:
            LifecycleCacheEntry if valid, None if expired or not found
        """
        entry = self.read(key)
        if entry and not entry.is_expired():
            return entry
        return None

    def refresh(self, key: str, new_ttl: timedelta | None = None) -> bool:
        """
        Refresh an entry's TTL.

        Args:
            key: Cache key
            new_ttl: New TTL (uses original if not provided)

        Returns:
            True if entry was refreshed, False if not found
        """
        entry = self._entries.get(key)
        if entry:
            entry.refresh(new_ttl)
            # Persist update
            self._base.write(
                key=key,
                data=entry.to_dict(),
                agentese_path=entry.agentese_path,
            )
            return True
        return False

    def delete(self, key: str, reason: str = "manual") -> ExpirationEvent | None:
        """
        Delete an entry.

        Args:
            key: Cache key
            reason: Why deleted

        Returns:
            ExpirationEvent if deleted, None if not found
        """
        entry = self._entries.get(key)
        if entry:
            event = ExpirationEvent(
                key=key,
                human_label=entry.human_label,
                expired_at=datetime.now(),
                age_when_expired=entry.age,
                access_count=entry.access_count,
                reason=reason,
            )
            self._expiration_events.append(event)
            del self._entries[key]
            self._base.delete(key)
            return event
        return None

    def cleanup_expired(self) -> list[ExpirationEvent]:
        """
        Remove all expired entries.

        Returns:
            List of expiration events for removed entries
        """
        events: list[ExpirationEvent] = []
        expired_keys = [key for key, entry in self._entries.items() if entry.is_expired()]

        for key in expired_keys:
            event = self.delete(key, reason="ttl")
            if event:
                events.append(event)

        return events

    def get_expired(self) -> list[LifecycleCacheEntry[Any]]:
        """Get all expired entries without removing them."""
        return [e for e in self._entries.values() if e.is_expired()]

    def get_active(self) -> list[LifecycleCacheEntry[Any]]:
        """Get all non-expired entries."""
        return [e for e in self._entries.values() if not e.is_expired()]

    def get_expiring_soon(
        self, threshold: timedelta | None = None
    ) -> list[LifecycleCacheEntry[Any]]:
        """
        Get entries expiring soon.

        Args:
            threshold: Time until expiration to consider "soon" (default 1 hour)

        Returns:
            Entries expiring within threshold
        """
        threshold = threshold or timedelta(hours=1)
        return [
            e
            for e in self._entries.values()
            if not e.is_expired() and e.time_until_expiration < threshold
        ]

    def stats(self) -> LifecycleStats:
        """Get cache lifecycle statistics."""
        entries = list(self._entries.values())
        expired = [e for e in entries if e.is_expired()]
        active = [e for e in entries if not e.is_expired()]

        # Compute label distribution
        labels: dict[str, int] = {}
        for e in entries:
            labels[e.human_label] = labels.get(e.human_label, 0) + 1

        ages = [e.age.total_seconds() for e in entries]
        ttls = [e.ttl.total_seconds() for e in entries]
        accesses = [e.access_count for e in entries]

        return LifecycleStats(
            total_entries=len(entries),
            expired_count=len(expired),
            active_count=len(active),
            avg_age_seconds=sum(ages) / len(ages) if ages else 0.0,
            avg_ttl_seconds=sum(ttls) / len(ttls) if ttls else 0.0,
            avg_access_count=sum(accesses) / len(accesses) if accesses else 0.0,
            oldest_entry_age_seconds=max(ages) if ages else 0.0,
            entries_by_label=labels,
        )

    def all_keys(self) -> list[str]:
        """Get all cache keys."""
        return list(self._entries.keys())

    def clear(self) -> int:
        """
        Clear all entries.

        Returns:
            Number of entries cleared
        """
        count = len(self._entries)
        for key in list(self._entries.keys()):
            self.delete(key, reason="cleared")
        return count


# =============================================================================
# Integration with Memory Substrate
# =============================================================================


def create_from_allocation(
    allocation: Any,  # Allocation from substrate
    cache: LifecycleAwareCache,
) -> LifecycleCacheEntry[Any]:
    """
    Create a cache entry from a memory allocation.

    Args:
        allocation: Allocation from SharedSubstrate
        cache: The cache to write to

    Returns:
        Created cache entry
    """
    return cache.write(
        key=f"allocation:{allocation.agent_id}",
        data={
            "agent_id": str(allocation.agent_id),
            "namespace": allocation.namespace,
            "pattern_count": allocation.pattern_count,
            "access_count": allocation.access_count,
            "created_at": allocation.created_at.isoformat(),
        },
        human_label=allocation.lifecycle.human_label,
        ttl=allocation.lifecycle.ttl,
        metadata={"allocation": True},
    )


def sync_allocation_to_cache(
    allocation: Any,  # Allocation from substrate
    cache: LifecycleAwareCache,
) -> bool:
    """
    Sync allocation state to cache.

    Args:
        allocation: Allocation to sync
        cache: Target cache

    Returns:
        True if synced, False if allocation doesn't exist
    """
    key = f"allocation:{allocation.agent_id}"
    entry = cache.read(key)

    if entry:
        # Update existing
        entry.data = {
            "agent_id": str(allocation.agent_id),
            "namespace": allocation.namespace,
            "pattern_count": allocation.pattern_count,
            "access_count": allocation.access_count,
            "created_at": allocation.created_at.isoformat(),
        }
        cache.write(
            key=key,
            data=entry.data,
            human_label=entry.human_label,
            ttl=entry.ttl,
        )
        return True
    else:
        # Create new
        create_from_allocation(allocation, cache)
        return True


# =============================================================================
# Factory Functions
# =============================================================================


def get_lifecycle_cache(cache_dir: Path | None = None) -> LifecycleAwareCache:
    """
    Get a LifecycleAwareCache instance.

    Args:
        cache_dir: Custom cache directory

    Returns:
        Configured LifecycleAwareCache
    """
    return LifecycleAwareCache(cache_dir=cache_dir)


def create_entry(
    key: str,
    data: Any,
    human_label: str,
    ttl_hours: int = 24,
) -> LifecycleCacheEntry[Any]:
    """
    Create a cache entry (without persisting).

    Args:
        key: Cache key
        data: Data to cache
        human_label: What this is
        ttl_hours: TTL in hours

    Returns:
        LifecycleCacheEntry (not yet persisted)
    """
    return LifecycleCacheEntry(
        key=key,
        data=data,
        human_label=human_label,
        ttl=timedelta(hours=ttl_hours),
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core types
    "LifecycleCacheEntry",
    "ExpirationEvent",
    "LifecycleStats",
    # Cache
    "LifecycleAwareCache",
    # Integration
    "create_from_allocation",
    "sync_allocation_to_cache",
    # Factory functions
    "get_lifecycle_cache",
    "create_entry",
]
