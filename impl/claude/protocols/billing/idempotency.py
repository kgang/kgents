"""
Redis-backed Idempotency Store for webhook event deduplication.

Provides atomic check-and-set for webhook event IDs with TTL expiration.
Falls back to in-memory store when Redis is unavailable.

Usage:
    store = await get_idempotency_store()
    if await store.check_and_set(event_id):
        # Process event (first time)
    else:
        # Skip duplicate

Environment:
    REDIS_URL: Redis connection URL (default: redis://triad-redis.kgents-triad.svc.cluster.local:6379)
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class IdempotencyStoreBase(ABC):
    """Abstract base for idempotency stores."""

    @abstractmethod
    async def check_and_set(self, event_id: str) -> bool:
        """
        Check if event is new and mark as processed atomically.

        Returns:
            True if event is new (should be processed)
            False if event is duplicate (should be skipped)
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close any connections."""
        ...


@dataclass
class InMemoryIdempotencyStore(IdempotencyStoreBase):
    """
    In-memory idempotency store for development and fallback.

    Note: Not suitable for horizontal scaling - each instance has its own store.
    """

    _processed: dict[str, datetime] = field(default_factory=dict, init=False)
    max_age_seconds: int = 86400  # 24 hours

    async def check_and_set(self, event_id: str) -> bool:
        """Check and set with cleanup of expired entries."""
        self._cleanup()
        if event_id in self._processed:
            return False
        self._processed[event_id] = datetime.now(UTC)
        return True

    async def close(self) -> None:
        """No-op for in-memory store."""
        pass

    def _cleanup(self) -> None:
        """Remove expired entries."""
        now = datetime.now(UTC)
        expired = [
            eid
            for eid, ts in self._processed.items()
            if (now - ts).total_seconds() > self.max_age_seconds
        ]
        for eid in expired:
            del self._processed[eid]


@dataclass
class RedisIdempotencyStore(IdempotencyStoreBase):
    """
    Redis-backed idempotency store with TTL expiration.

    Uses Redis SET NX EX for atomic check-and-set with automatic expiration.
    Suitable for horizontally scaled deployments.
    """

    redis_url: str = "redis://triad-redis.kgents-triad.svc.cluster.local:6379"
    ttl: int = 86400  # 24 hours
    prefix: str = "idempotency:"
    _client: Any = field(default=None, init=False, repr=False)
    _connected: bool = field(default=False, init=False)

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            import redis.asyncio as aioredis
        except ImportError:
            raise ImportError(
                "redis package required for RedisIdempotencyStore. "
                "Install with: pip install redis"
            )

        self._client = aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        # Verify connection
        await self._client.ping()
        self._connected = True
        logger.info(f"Connected to Redis at {self.redis_url}")

    async def check_and_set(self, event_id: str) -> bool:
        """
        Atomically check if event is new and mark as processed.

        Uses SET key "1" NX EX ttl:
        - NX: Only set if key does not exist
        - EX: Set expiration in seconds

        Returns True if key was set (event is new), False if key existed (duplicate).
        """
        if not self._connected:
            raise RuntimeError(
                "RedisIdempotencyStore not connected. Call connect() first."
            )

        key = f"{self.prefix}{event_id}"
        # SET NX returns True if key was set (new), None if key existed (duplicate)
        result = await self._client.set(key, "1", nx=True, ex=self.ttl)
        return result is not None

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client is not None:
            await self._client.close()
            self._connected = False
            logger.info("Redis connection closed")


# Module-level singleton for shared store
_store: Optional[IdempotencyStoreBase] = None


async def get_idempotency_store() -> IdempotencyStoreBase:
    """
    Get idempotency store with graceful fallback.

    Priority:
    1. Redis if REDIS_URL is set and reachable
    2. In-memory fallback

    The store is cached as a singleton for connection reuse.
    """
    global _store

    if _store is not None:
        return _store

    redis_url = os.environ.get(
        "REDIS_URL",
        "redis://triad-redis.kgents-triad.svc.cluster.local:6379",
    )

    # Try Redis first
    if redis_url:
        try:
            store = RedisIdempotencyStore(redis_url=redis_url)
            await store.connect()
            _store = store
            return _store
        except ImportError:
            logger.warning("redis package not installed, falling back to in-memory")
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}), falling back to in-memory")

    # Fallback to in-memory
    logger.info("Using in-memory idempotency store")
    _store = InMemoryIdempotencyStore()
    return _store


async def reset_store() -> None:
    """Reset the singleton store (for testing)."""
    global _store
    if _store is not None:
        await _store.close()
        _store = None
