"""
Tests for EphemeralAgentCache.

Tests LRU eviction, TTL expiration, and metrics tracking.
"""

from datetime import UTC, datetime, timedelta

import pytest

from services.foundry import CacheEntry, EphemeralAgentCache


class TestCacheBasics:
    """Test basic cache operations."""

    @pytest.fixture
    def cache(self) -> EphemeralAgentCache:
        """Create a fresh cache."""
        return EphemeralAgentCache(max_size=10, ttl_hours=1)

    def test_put_get(self, cache: EphemeralAgentCache) -> None:
        """Basic put and get."""
        entry = CacheEntry(
            key="abc123",
            intent="test intent",
            context={},
            agent_source="def test(): pass",
            target="cli",
            artifact="#!/bin/python\nprint('hello')",
            artifact_type="script",
            reality="deterministic",
            stability_score=1.0,
        )

        cache.put(entry)
        retrieved = cache.get("abc123")

        assert retrieved is not None
        assert retrieved.key == "abc123"
        assert retrieved.intent == "test intent"

    def test_get_nonexistent(self, cache: EphemeralAgentCache) -> None:
        """Get returns None for nonexistent key."""
        result = cache.get("nonexistent")
        assert result is None

    def test_compute_key(self, cache: EphemeralAgentCache) -> None:
        """Key computation is deterministic."""
        key1 = cache.compute_key("parse CSV", {"a": 1})
        key2 = cache.compute_key("parse CSV", {"a": 1})
        key3 = cache.compute_key("parse CSV", {"a": 2})

        assert key1 == key2
        assert key1 != key3

    def test_compute_key_case_insensitive(self, cache: EphemeralAgentCache) -> None:
        """Key computation is case-insensitive for intent."""
        key1 = cache.compute_key("Parse CSV", {})
        key2 = cache.compute_key("parse csv", {})

        assert key1 == key2

    def test_contains(self, cache: EphemeralAgentCache) -> None:
        """Contains check without updating LRU order."""
        entry = CacheEntry(
            key="test",
            intent="test",
            context={},
            agent_source=None,
            target="cli",
            artifact="test",
            artifact_type="script",
            reality="deterministic",
            stability_score=None,
        )

        assert not cache.contains("test")
        cache.put(entry)
        assert cache.contains("test")


class TestCacheLRU:
    """Test LRU eviction behavior."""

    def test_lru_eviction(self) -> None:
        """Oldest entries evicted when at capacity."""
        cache = EphemeralAgentCache(max_size=3, ttl_hours=1)

        # Add 3 entries
        for i in range(3):
            cache.put(
                CacheEntry(
                    key=f"entry{i}",
                    intent=f"intent {i}",
                    context={},
                    agent_source=None,
                    target="cli",
                    artifact="test",
                    artifact_type="script",
                    reality="deterministic",
                    stability_score=None,
                )
            )

        assert cache.size == 3
        assert cache.contains("entry0")

        # Add 4th entry - should evict entry0 (oldest)
        cache.put(
            CacheEntry(
                key="entry3",
                intent="intent 3",
                context={},
                agent_source=None,
                target="cli",
                artifact="test",
                artifact_type="script",
                reality="deterministic",
                stability_score=None,
            )
        )

        assert cache.size == 3
        assert not cache.contains("entry0")  # Evicted
        assert cache.contains("entry1")
        assert cache.contains("entry2")
        assert cache.contains("entry3")

    def test_lru_access_updates_order(self) -> None:
        """Accessing an entry moves it to end (most recent)."""
        cache = EphemeralAgentCache(max_size=3, ttl_hours=1)

        # Add 3 entries
        for i in range(3):
            cache.put(
                CacheEntry(
                    key=f"entry{i}",
                    intent=f"intent {i}",
                    context={},
                    agent_source=None,
                    target="cli",
                    artifact="test",
                    artifact_type="script",
                    reality="deterministic",
                    stability_score=None,
                )
            )

        # Access entry0 - moves it to most recent
        cache.get("entry0")

        # Add 4th entry - should evict entry1 (now oldest)
        cache.put(
            CacheEntry(
                key="entry3",
                intent="intent 3",
                context={},
                agent_source=None,
                target="cli",
                artifact="test",
                artifact_type="script",
                reality="deterministic",
                stability_score=None,
            )
        )

        assert cache.contains("entry0")  # Still here (was accessed)
        assert not cache.contains("entry1")  # Evicted
        assert cache.contains("entry2")
        assert cache.contains("entry3")


class TestCacheMetrics:
    """Test metrics tracking."""

    @pytest.fixture
    def cache(self) -> EphemeralAgentCache:
        """Create a fresh cache."""
        return EphemeralAgentCache(max_size=10, ttl_hours=1)

    def test_record_invocation(self, cache: EphemeralAgentCache) -> None:
        """Record invocation updates metrics."""
        entry = CacheEntry(
            key="test",
            intent="test",
            context={},
            agent_source=None,
            target="cli",
            artifact="test",
            artifact_type="script",
            reality="deterministic",
            stability_score=None,
        )

        cache.put(entry)

        # Record some invocations
        cache.record_invocation("test", success=True)
        cache.record_invocation("test", success=True)
        cache.record_invocation("test", success=False)

        retrieved = cache.get("test")
        assert retrieved is not None
        assert retrieved.invocation_count == 3
        assert retrieved.success_count == 2
        assert retrieved.failure_count == 1
        assert retrieved.success_rate == pytest.approx(2 / 3)

    def test_record_invocation_nonexistent(self, cache: EphemeralAgentCache) -> None:
        """Recording invocation for nonexistent key returns False."""
        result = cache.record_invocation("nonexistent", success=True)
        assert result is False

    def test_stats(self, cache: EphemeralAgentCache) -> None:
        """Stats are tracked correctly."""
        entry = CacheEntry(
            key="test",
            intent="test",
            context={},
            agent_source=None,
            target="cli",
            artifact="test",
            artifact_type="script",
            reality="deterministic",
            stability_score=None,
        )

        cache.put(entry)
        cache.get("test")  # Hit
        cache.get("nonexistent")  # Miss

        stats = cache.stats
        assert stats["total_puts"] == 1
        assert stats["total_gets"] == 2
        assert stats["cache_hits"] == 1
        assert stats["hit_rate"] == 0.5


class TestCacheExpiration:
    """Test TTL expiration."""

    def test_evict_expired(self) -> None:
        """Evict expired entries."""
        cache = EphemeralAgentCache(max_size=10, ttl_hours=1)

        # Add entry with old timestamp
        entry = CacheEntry(
            key="old",
            intent="old intent",
            context={},
            agent_source=None,
            target="cli",
            artifact="test",
            artifact_type="script",
            reality="deterministic",
            stability_score=None,
            created_at=datetime.now(UTC) - timedelta(hours=2),  # 2 hours old
        )
        cache.put(entry)

        # Add fresh entry
        fresh = CacheEntry(
            key="fresh",
            intent="fresh intent",
            context={},
            agent_source=None,
            target="cli",
            artifact="test",
            artifact_type="script",
            reality="deterministic",
            stability_score=None,
        )
        cache.put(fresh)

        assert cache.size == 2

        # Evict expired
        evicted = cache.evict_expired()
        assert evicted == 1
        assert cache.size == 1
        assert not cache.contains("old")
        assert cache.contains("fresh")


class TestCacheOperations:
    """Test cache management operations."""

    @pytest.fixture
    def cache(self) -> EphemeralAgentCache:
        """Create a fresh cache."""
        return EphemeralAgentCache(max_size=10, ttl_hours=1)

    def test_evict_specific(self, cache: EphemeralAgentCache) -> None:
        """Evict a specific entry."""
        entry = CacheEntry(
            key="test",
            intent="test",
            context={},
            agent_source=None,
            target="cli",
            artifact="test",
            artifact_type="script",
            reality="deterministic",
            stability_score=None,
        )
        cache.put(entry)

        assert cache.evict("test")
        assert not cache.contains("test")

    def test_evict_nonexistent(self, cache: EphemeralAgentCache) -> None:
        """Evicting nonexistent entry returns False."""
        assert not cache.evict("nonexistent")

    def test_clear(self, cache: EphemeralAgentCache) -> None:
        """Clear all entries."""
        for i in range(5):
            cache.put(
                CacheEntry(
                    key=f"entry{i}",
                    intent=f"intent {i}",
                    context={},
                    agent_source=None,
                    target="cli",
                    artifact="test",
                    artifact_type="script",
                    reality="deterministic",
                    stability_score=None,
                )
            )

        assert cache.size == 5
        cleared = cache.clear()
        assert cleared == 5
        assert cache.size == 0

    def test_list_entries(self, cache: EphemeralAgentCache) -> None:
        """List entries in most-recent-first order."""
        for i in range(3):
            cache.put(
                CacheEntry(
                    key=f"entry{i}",
                    intent=f"intent {i}",
                    context={},
                    agent_source=None,
                    target="cli",
                    artifact="test",
                    artifact_type="script",
                    reality="deterministic",
                    stability_score=None,
                )
            )

        entries = cache.list_entries()
        assert len(entries) == 3
        # Most recent first
        assert entries[0].key == "entry2"
        assert entries[1].key == "entry1"
        assert entries[2].key == "entry0"
