"""
Tests for Lifecycle-Aware Ghost Cache.

These tests verify:
1. LifecycleCacheEntry with TTL and human labels
2. LifecycleAwareCache operations
3. Expiration and cleanup
4. Statistics tracking
5. Integration with memory substrate
"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from infra.ghost.lifecycle import (
    ExpirationEvent,
    LifecycleAwareCache,
    LifecycleCacheEntry,
    LifecycleStats,
    create_entry,
    get_lifecycle_cache,
)


class TestLifecycleCacheEntry:
    """Tests for LifecycleCacheEntry."""

    def test_entry_requires_human_label(self) -> None:
        """Entry must have human_label (no anonymous debris)."""
        with pytest.raises(ValueError, match="human_label is required"):
            LifecycleCacheEntry(key="test", data={}, human_label="")

    def test_entry_creation(self) -> None:
        """Entry with valid human_label."""
        entry: LifecycleCacheEntry[dict[str, str]] = LifecycleCacheEntry(
            key="status",
            data={"health": "OK"},
            human_label="Cortex health snapshot",
        )

        assert entry.key == "status"
        assert entry.human_label == "Cortex health snapshot"
        assert entry.ttl == timedelta(hours=24)

    def test_entry_custom_ttl(self) -> None:
        """Entry with custom TTL."""
        entry: LifecycleCacheEntry[str] = LifecycleCacheEntry(
            key="temp",
            data="temporary data",
            human_label="Short-lived cache",
            ttl=timedelta(minutes=5),
        )

        assert entry.ttl == timedelta(minutes=5)

    def test_entry_expiration(self) -> None:
        """Entry expiration calculation."""
        entry: LifecycleCacheEntry[str] = LifecycleCacheEntry(
            key="test",
            data="data",
            human_label="test entry",
            ttl=timedelta(hours=1),
        )

        assert not entry.is_expired()
        assert entry.time_until_expiration > timedelta(minutes=59)

        # Manually expire by setting created_at in past
        entry.created_at = datetime.now() - timedelta(hours=2)
        assert entry.is_expired()

    def test_entry_access_tracking(self) -> None:
        """Entry tracks accesses."""
        entry: LifecycleCacheEntry[str] = LifecycleCacheEntry(
            key="test",
            data="data",
            human_label="test entry",
        )

        assert entry.access_count == 0

        entry.access()
        entry.access()

        assert entry.access_count == 2

    def test_entry_refresh(self) -> None:
        """Entry refresh resets TTL."""
        entry: LifecycleCacheEntry[str] = LifecycleCacheEntry(
            key="test",
            data="data",
            human_label="test entry",
            ttl=timedelta(hours=1),
        )

        # Age it
        original_created = entry.created_at
        entry.created_at = datetime.now() - timedelta(minutes=30)

        # Refresh
        entry.refresh()

        assert entry.created_at > original_created - timedelta(minutes=30)

    def test_entry_serialization(self) -> None:
        """Entry can be serialized and deserialized."""
        entry: LifecycleCacheEntry[dict[str, int]] = LifecycleCacheEntry(
            key="test",
            data={"count": 42},
            human_label="test entry",
            ttl=timedelta(hours=2),
        )

        # Serialize
        data = entry.to_dict()
        assert data["key"] == "test"
        assert data["human_label"] == "test entry"

        # Deserialize
        restored = LifecycleCacheEntry.from_dict(data)
        assert restored.key == "test"
        assert restored.data == {"count": 42}


class TestLifecycleAwareCache:
    """Tests for LifecycleAwareCache."""

    @pytest.fixture
    def cache_dir(self) -> Generator[Path, None, None]:
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def cache(self, cache_dir: Path) -> LifecycleAwareCache:
        """Create cache with temp directory."""
        return LifecycleAwareCache(cache_dir=cache_dir)

    def test_write_requires_human_label(self, cache: LifecycleAwareCache) -> None:
        """Write requires human_label."""
        with pytest.raises(ValueError, match="human_label is required"):
            cache.write(key="test", data={}, human_label="")

    def test_write_and_read(self, cache: LifecycleAwareCache) -> None:
        """Write and read entry."""
        cache.write(
            key="status",
            data={"health": "OK"},
            human_label="Health snapshot",
        )

        entry = cache.read("status")

        assert entry is not None
        assert entry.data == {"health": "OK"}
        assert entry.human_label == "Health snapshot"

    def test_read_nonexistent(self, cache: LifecycleAwareCache) -> None:
        """Read nonexistent key returns None."""
        entry = cache.read("nonexistent")
        assert entry is None

    def test_read_if_valid_expired(self, cache: LifecycleAwareCache) -> None:
        """read_if_valid returns None for expired entries."""
        entry = cache.write(
            key="temp",
            data="data",
            human_label="temporary",
            ttl=timedelta(hours=1),
        )

        # Manually expire
        entry.created_at = datetime.now() - timedelta(hours=2)

        result = cache.read_if_valid("temp")
        assert result is None

    def test_refresh(self, cache: LifecycleAwareCache) -> None:
        """Refresh entry TTL."""
        cache.write(
            key="test",
            data="data",
            human_label="test",
            ttl=timedelta(hours=1),
        )

        result = cache.refresh("test")
        assert result is True

        result = cache.refresh("nonexistent")
        assert result is False

    def test_delete(self, cache: LifecycleAwareCache) -> None:
        """Delete entry."""
        cache.write(key="test", data="data", human_label="test")

        event = cache.delete("test")

        assert event is not None
        assert event.key == "test"
        assert event.reason == "manual"

        # Verify deleted
        assert cache.read("test") is None

    def test_cleanup_expired(self, cache: LifecycleAwareCache) -> None:
        """Cleanup expired entries."""
        # Create entries with different TTLs
        entry1 = cache.write(
            key="short",
            data="data1",
            human_label="short-lived",
            ttl=timedelta(hours=1),
        )
        cache.write(
            key="long",
            data="data2",
            human_label="long-lived",
            ttl=timedelta(hours=24),
        )

        # Expire the short one
        entry1.created_at = datetime.now() - timedelta(hours=2)

        events = cache.cleanup_expired()

        assert len(events) == 1
        assert events[0].key == "short"
        assert cache.read("short") is None
        assert cache.read("long") is not None

    def test_get_expired(self, cache: LifecycleAwareCache) -> None:
        """Get expired entries without removing."""
        entry = cache.write(
            key="test",
            data="data",
            human_label="test",
            ttl=timedelta(hours=1),
        )
        entry.created_at = datetime.now() - timedelta(hours=2)

        expired = cache.get_expired()

        assert len(expired) == 1
        assert cache.read("test") is not None  # Still there

    def test_get_expiring_soon(self, cache: LifecycleAwareCache) -> None:
        """Get entries expiring soon."""
        cache.write(
            key="soon",
            data="data1",
            human_label="expiring soon",
            ttl=timedelta(minutes=30),
        )
        cache.write(
            key="later",
            data="data2",
            human_label="expiring later",
            ttl=timedelta(hours=24),
        )

        expiring = cache.get_expiring_soon(threshold=timedelta(hours=1))

        assert len(expiring) == 1
        assert expiring[0].key == "soon"

    def test_stats(self, cache: LifecycleAwareCache) -> None:
        """Cache statistics."""
        cache.write(key="a", data="1", human_label="entry a")
        cache.write(key="b", data="2", human_label="entry b")

        stats = cache.stats()

        assert stats.total_entries == 2
        assert stats.active_count == 2
        assert stats.expired_count == 0
        assert "entry a" in stats.entries_by_label

    def test_all_keys(self, cache: LifecycleAwareCache) -> None:
        """List all cache keys."""
        cache.write(key="a", data="1", human_label="a")
        cache.write(key="b", data="2", human_label="b")

        keys = cache.all_keys()

        assert "a" in keys
        assert "b" in keys

    def test_clear(self, cache: LifecycleAwareCache) -> None:
        """Clear all entries."""
        cache.write(key="a", data="1", human_label="a")
        cache.write(key="b", data="2", human_label="b")

        count = cache.clear()

        assert count == 2
        assert len(cache.all_keys()) == 0


class TestExpirationEvent:
    """Tests for ExpirationEvent."""

    def test_event_creation(self) -> None:
        """ExpirationEvent stores all fields."""
        event = ExpirationEvent(
            key="test",
            human_label="test entry",
            expired_at=datetime.now(),
            age_when_expired=timedelta(hours=25),
            access_count=10,
            reason="ttl",
        )

        assert event.key == "test"
        assert event.reason == "ttl"
        assert event.access_count == 10


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_get_lifecycle_cache(self) -> None:
        """get_lifecycle_cache factory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = get_lifecycle_cache(Path(tmpdir))
            assert isinstance(cache, LifecycleAwareCache)

    def test_create_entry(self) -> None:
        """create_entry factory."""
        entry = create_entry(
            key="test",
            data={"value": 42},
            human_label="test entry",
            ttl_hours=12,
        )

        assert entry.key == "test"
        assert entry.ttl == timedelta(hours=12)
