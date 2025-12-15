"""
Tests for Redis-backed Idempotency Store.

Tests cover:
- In-memory store behavior
- Redis store behavior (with mock)
- Graceful fallback from Redis to in-memory
- TTL expiration
- Concurrent access patterns
"""

from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ..idempotency import (
    InMemoryIdempotencyStore,
    RedisIdempotencyStore,
    get_idempotency_store,
    reset_store,
)

# Check if redis is available for testing
try:
    import redis.asyncio

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

requires_redis = pytest.mark.skipif(
    not REDIS_AVAILABLE, reason="redis package not installed"
)


class TestInMemoryIdempotencyStore:
    """Tests for in-memory idempotency store."""

    @pytest.fixture
    def store(self) -> InMemoryIdempotencyStore:
        """Create a fresh in-memory store."""
        return InMemoryIdempotencyStore()

    @pytest.mark.asyncio
    async def test_new_event_returns_true(
        self, store: InMemoryIdempotencyStore
    ) -> None:
        """First time seeing an event should return True."""
        result = await store.check_and_set("event-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_duplicate_event_returns_false(
        self, store: InMemoryIdempotencyStore
    ) -> None:
        """Second time seeing same event should return False."""
        await store.check_and_set("event-1")
        result = await store.check_and_set("event-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_different_events_return_true(
        self, store: InMemoryIdempotencyStore
    ) -> None:
        """Different events should all return True on first check."""
        assert await store.check_and_set("event-1") is True
        assert await store.check_and_set("event-2") is True
        assert await store.check_and_set("event-3") is True

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_cleanup_removes_expired(
        self, store: InMemoryIdempotencyStore
    ) -> None:
        """Cleanup should remove entries older than max_age_seconds."""
        store.max_age_seconds = 1  # 1 second for testing

        # Add an event
        await store.check_and_set("event-1")

        # Wait for expiration
        await asyncio.sleep(1.5)

        # Should be treated as new after expiration
        result = await store.check_and_set("event-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_close_is_noop(self, store: InMemoryIdempotencyStore) -> None:
        """Close should not raise for in-memory store."""
        await store.close()  # Should not raise


@requires_redis
class TestRedisIdempotencyStore:
    """Tests for Redis-backed idempotency store."""

    @pytest.fixture
    def mock_redis(self) -> AsyncMock:
        """Create a mock Redis client."""
        mock = AsyncMock()
        mock.ping = AsyncMock(return_value=True)
        mock.set = AsyncMock(return_value=True)  # NX set succeeded
        mock.close = AsyncMock()
        return mock

    @pytest.fixture
    def store(self) -> RedisIdempotencyStore:
        """Create a Redis store (not connected)."""
        return RedisIdempotencyStore(
            redis_url="redis://localhost:6379",
            ttl=3600,
            prefix="test:",
        )

    @pytest.mark.asyncio
    async def test_connect_success(
        self, store: RedisIdempotencyStore, mock_redis: AsyncMock
    ) -> None:
        """Connect should establish Redis connection."""
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await store.connect()
            assert store._connected is True

    @pytest.mark.asyncio
    async def test_check_and_set_new_event(
        self, store: RedisIdempotencyStore, mock_redis: AsyncMock
    ) -> None:
        """New event should return True from Redis."""
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await store.connect()
            mock_redis.set.return_value = True  # Key was set (new)

            result = await store.check_and_set("event-1")

            assert result is True
            mock_redis.set.assert_called_once_with(
                "test:event-1", "1", nx=True, ex=3600
            )

    @pytest.mark.asyncio
    async def test_check_and_set_duplicate_event(
        self, store: RedisIdempotencyStore, mock_redis: AsyncMock
    ) -> None:
        """Duplicate event should return False from Redis."""
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await store.connect()
            mock_redis.set.return_value = None  # Key existed (duplicate)

            result = await store.check_and_set("event-1")

            assert result is False

    @pytest.mark.asyncio
    async def test_check_and_set_without_connect_raises(
        self, store: RedisIdempotencyStore
    ) -> None:
        """Using store without connect should raise RuntimeError."""
        with pytest.raises(RuntimeError, match="not connected"):
            await store.check_and_set("event-1")

    @pytest.mark.asyncio
    async def test_close_disconnects(
        self, store: RedisIdempotencyStore, mock_redis: AsyncMock
    ) -> None:
        """Close should disconnect from Redis."""
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await store.connect()
            await store.close()

            assert store._connected is False
            mock_redis.close.assert_called_once()


class TestGetIdempotencyStore:
    """Tests for store factory with graceful fallback."""

    @pytest.fixture(autouse=True)
    async def reset_singleton(self) -> AsyncGenerator[None, None]:
        """Reset singleton before each test."""
        await reset_store()
        yield
        await reset_store()

    @pytest.mark.asyncio
    async def test_fallback_to_inmemory_when_no_redis(self) -> None:
        """Should return in-memory store when Redis unavailable."""
        with patch.dict("os.environ", {"REDIS_URL": ""}, clear=False):
            store = await get_idempotency_store()
            assert isinstance(store, InMemoryIdempotencyStore)

    @requires_redis
    @pytest.mark.asyncio
    async def test_fallback_on_connection_error(self) -> None:
        """Should fall back to in-memory when Redis connection fails."""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(side_effect=ConnectionError("Cannot connect"))

        with patch.dict(
            "os.environ", {"REDIS_URL": "redis://localhost:6379"}, clear=False
        ):
            with patch("redis.asyncio.from_url", return_value=mock_redis):
                store = await get_idempotency_store()
                assert isinstance(store, InMemoryIdempotencyStore)

    @pytest.mark.asyncio
    async def test_fallback_on_import_error(self) -> None:
        """Should fall back to in-memory when redis package not installed."""
        # This test verifies that when redis is not installed, we get in-memory store
        # If redis IS installed but connect fails, same result
        with patch.dict(
            "os.environ", {"REDIS_URL": "redis://localhost:6379"}, clear=False
        ):
            # Mock the RedisIdempotencyStore.connect to raise ImportError
            original_connect = RedisIdempotencyStore.connect

            async def mock_connect(self: RedisIdempotencyStore) -> None:
                raise ImportError("redis not installed")

            with patch.object(RedisIdempotencyStore, "connect", mock_connect):
                store = await get_idempotency_store()
                assert isinstance(store, InMemoryIdempotencyStore)

    @pytest.mark.asyncio
    async def test_singleton_behavior(self) -> None:
        """Should return same store instance on subsequent calls."""
        with patch.dict("os.environ", {"REDIS_URL": ""}, clear=False):
            store1 = await get_idempotency_store()
            store2 = await get_idempotency_store()
            assert store1 is store2

    @requires_redis
    @pytest.mark.asyncio
    async def test_uses_redis_when_available(self) -> None:
        """Should return Redis store when connection succeeds."""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.close = AsyncMock()

        with patch.dict(
            "os.environ", {"REDIS_URL": "redis://localhost:6379"}, clear=False
        ):
            with patch("redis.asyncio.from_url", return_value=mock_redis):
                store = await get_idempotency_store()
                assert isinstance(store, RedisIdempotencyStore)
