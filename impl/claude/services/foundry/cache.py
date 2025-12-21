"""
EphemeralAgentCache — LRU cache with metrics for JIT agents.

The cache stores ephemeral agents by (intent, context) hash for reuse.
Tracks invocation metrics to support promotion decisions in Phase 5.

Features:
- LRU eviction when capacity exceeded
- TTL expiration for stale entries
- Invocation tracking (count, success/failure)
- Thread-safe operations

See: spec/services/foundry.md
"""

from __future__ import annotations

import hashlib
import json
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any


@dataclass
class CacheEntry:
    """
    Entry in the ephemeral agent cache.

    Tracks both the agent artifact and metrics for promotion evaluation.
    """

    key: str  # SHA256 of normalized (intent, context)
    intent: str
    context: dict[str, Any]
    agent_source: str | None  # Generated Python source (PROBABILISTIC only)
    target: str  # Selected target (local, cli, docker, etc.)
    artifact: str | list[dict[str, Any]]  # The compiled output
    artifact_type: str  # "script" | "dockerfile" | "html" | "manifests"
    reality: str  # DETERMINISTIC | PROBABILISTIC | CHAOTIC
    stability_score: float | None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Metrics for promotion evaluation
    invocation_count: int = 0
    last_invoked: datetime | None = None
    success_count: int = 0
    failure_count: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0-1.0)."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0  # Assume success if never failed
        return self.success_count / total

    @property
    def age(self) -> timedelta:
        """Time since creation."""
        return datetime.now(UTC) - self.created_at

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "key": self.key,
            "intent": self.intent,
            "context": self.context,
            "agent_source": self.agent_source,
            "target": self.target,
            "artifact_type": self.artifact_type,
            "reality": self.reality,
            "stability_score": self.stability_score,
            "created_at": self.created_at.isoformat(),
            "invocation_count": self.invocation_count,
            "last_invoked": self.last_invoked.isoformat() if self.last_invoked else None,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "age_seconds": self.age.total_seconds(),
        }


class EphemeralAgentCache:
    """
    LRU cache with metrics tracking for ephemeral agents.

    Thread-safe implementation using OrderedDict for LRU ordering.

    Usage:
        cache = EphemeralAgentCache(max_size=100, ttl_hours=24)

        # Store an entry
        entry = CacheEntry(key=..., intent=..., ...)
        cache.put(entry)

        # Retrieve
        cached = cache.get(key)

        # Record usage
        cache.record_invocation(key, success=True)
    """

    def __init__(self, max_size: int = 100, ttl_hours: int = 24) -> None:
        """
        Initialize cache.

        Args:
            max_size: Maximum number of entries (oldest evicted when exceeded)
            ttl_hours: Time-to-live in hours (expired entries evicted on access)
        """
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._ttl = timedelta(hours=ttl_hours)
        self._lock = threading.RLock()

        # Statistics
        self._total_puts = 0
        self._total_gets = 0
        self._cache_hits = 0
        self._evictions = 0

    @property
    def size(self) -> int:
        """Current number of entries."""
        with self._lock:
            return len(self._cache)

    @property
    def max_size(self) -> int:
        """Maximum capacity."""
        return self._max_size

    @property
    def stats(self) -> dict[str, Any]:
        """Cache statistics."""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "total_puts": self._total_puts,
                "total_gets": self._total_gets,
                "cache_hits": self._cache_hits,
                "hit_rate": self._cache_hits / max(self._total_gets, 1),
                "evictions": self._evictions,
            }

    def compute_key(self, intent: str, context: dict[str, Any]) -> str:
        """
        Compute SHA256 hash of normalized (intent, context).

        The key is deterministic for the same intent and context.
        """
        # Normalize: lowercase intent, sorted context keys
        normalized = {
            "intent": intent.lower().strip(),
            "context": dict(sorted(context.items())) if context else {},
        }
        serialized = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]

    def get(self, key: str) -> CacheEntry | None:
        """
        Get entry by key, updating LRU order.

        Returns None if not found or expired.
        """
        with self._lock:
            self._total_gets += 1

            if key not in self._cache:
                return None

            entry = self._cache[key]

            # Check TTL
            if entry.age > self._ttl:
                del self._cache[key]
                return None

            # Update LRU order (move to end)
            self._cache.move_to_end(key)
            self._cache_hits += 1
            return entry

    def put(self, entry: CacheEntry) -> None:
        """
        Store entry, evicting oldest if over capacity.

        If key already exists, updates the entry and LRU order.
        """
        with self._lock:
            self._total_puts += 1

            # If key exists, remove it first (will be re-added at end)
            if entry.key in self._cache:
                del self._cache[entry.key]

            # Evict oldest entries if at capacity
            while len(self._cache) >= self._max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._evictions += 1

            # Add new entry at end (most recent)
            self._cache[entry.key] = entry

    def record_invocation(self, key: str, success: bool) -> bool:
        """
        Record an invocation of a cached agent.

        Updates invocation_count, last_invoked, and success/failure counts.
        Returns True if entry exists, False otherwise.
        """
        with self._lock:
            if key not in self._cache:
                return False

            entry = self._cache[key]
            # CacheEntry is a dataclass, so we can modify fields directly
            entry.invocation_count += 1
            entry.last_invoked = datetime.now(UTC)
            if success:
                entry.success_count += 1
            else:
                entry.failure_count += 1

            return True

    def list_entries(self) -> list[CacheEntry]:
        """
        List all cached entries (most recent first).

        Does not evict expired entries - use evict_expired() for that.
        """
        with self._lock:
            # Return in reverse order (most recent first)
            return list(reversed(self._cache.values()))

    def evict_expired(self) -> int:
        """
        Remove entries past TTL.

        Returns count of evicted entries.
        """
        with self._lock:
            now = datetime.now(UTC)
            expired_keys = [
                key
                for key, entry in self._cache.items()
                if (now - entry.created_at) > self._ttl
            ]

            for key in expired_keys:
                del self._cache[key]
                self._evictions += 1

            return len(expired_keys)

    def evict(self, key: str) -> bool:
        """
        Remove a specific entry.

        Returns True if entry existed, False otherwise.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._evictions += 1
                return True
            return False

    def clear(self) -> int:
        """
        Clear all entries.

        Returns count of cleared entries.
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._evictions += count
            return count

    def contains(self, key: str) -> bool:
        """Check if key exists (does not update LRU order)."""
        with self._lock:
            return key in self._cache


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "CacheEntry",
    "EphemeralAgentCache",
]
