"""
SoulCache: Redis-backed soul state caching.

Provides fast access to K-gent soul state through the Database Triad's
Redis layer (SPARK). Used for:
- Session state caching
- Eigenvector confidence hot paths
- Active mode state
- Recent interaction metadata

Architecture:
- Redis for hot state (TTL-managed)
- PostgreSQL remains source of truth
- Cache invalidation via CDC

Usage:
    from agents.k.soul_cache import SoulCache, get_soul_cache

    cache = await get_soul_cache()
    await cache.set_session_state(session_id, state)
    state = await cache.get_session_state(session_id)

AGENTESE: self.soul.reflex
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Protocol

logger = logging.getLogger(__name__)


# =============================================================================
# Protocols
# =============================================================================


class CacheClient(Protocol):
    """Protocol for Redis-like cache operations."""

    async def get(self, key: str) -> str | None:
        """Get value by key."""
        ...

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Set key to value with optional TTL in seconds."""
        ...

    async def delete(self, key: str) -> None:
        """Delete a key."""
        ...

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        ...

    async def expire(self, key: str, ttl: int) -> None:
        """Set expiry on a key."""
        ...

    async def ttl(self, key: str) -> int:
        """Get TTL of a key in seconds (-1 if no TTL, -2 if doesn't exist)."""
        ...


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class SoulCacheConfig:
    """Configuration for the soul cache."""

    # Redis settings
    redis_url: str = "redis://localhost:6379"
    key_prefix: str = "kgent:soul:"

    # TTL settings (in seconds)
    session_ttl: int = 3600 * 4  # 4 hours
    eigenvector_ttl: int = 3600  # 1 hour
    mode_ttl: int = 1800  # 30 minutes

    # Connection settings
    max_connections: int = 10
    socket_timeout: float = 5.0

    @classmethod
    def from_env(cls) -> "SoulCacheConfig":
        """Load configuration from environment."""
        return cls(
            redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379"),
            key_prefix=os.environ.get("SOUL_CACHE_PREFIX", "kgent:soul:"),
        )


# =============================================================================
# Cached Types
# =============================================================================


@dataclass
class CachedSessionState:
    """Session state stored in cache."""

    session_id: str
    active_mode: str
    interactions_count: int
    tokens_used_session: int
    created_at: str  # ISO format
    last_interaction: str | None  # ISO format

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str) -> "CachedSessionState":
        """Deserialize from JSON."""
        d = json.loads(data)
        return cls(**d)


@dataclass
class CachedEigenvectors:
    """Eigenvector confidences stored in cache."""

    aesthetic: float
    categorical: float
    collaborative: float
    ethical: float
    joyful: float
    tasteful: float
    cached_at: str  # ISO format

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str) -> "CachedEigenvectors":
        """Deserialize from JSON."""
        d = json.loads(data)
        return cls(**d)


@dataclass
class CachedActiveMode:
    """Active dialogue mode stored in cache."""

    mode: str
    changed_at: str  # ISO format
    reason: str | None

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str) -> "CachedActiveMode":
        """Deserialize from JSON."""
        d = json.loads(data)
        return cls(**d)


# =============================================================================
# Mock Implementation
# =============================================================================


class MockCacheClient:
    """In-memory mock Redis client for testing."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._ttls: dict[str, float] = {}

    async def get(self, key: str) -> str | None:
        # Check TTL expiry
        if key in self._ttls:
            import time

            if time.time() > self._ttls[key]:
                del self._data[key]
                del self._ttls[key]
                return None
        return self._data.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        self._data[key] = value
        if ttl:
            import time

            self._ttls[key] = time.time() + ttl

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)
        self._ttls.pop(key, None)

    async def exists(self, key: str) -> bool:
        if key in self._ttls:
            import time

            if time.time() > self._ttls[key]:
                del self._data[key]
                del self._ttls[key]
                return False
        return key in self._data

    async def expire(self, key: str, ttl: int) -> None:
        if key in self._data:
            import time

            self._ttls[key] = time.time() + ttl

    async def ttl(self, key: str) -> int:
        if key not in self._data:
            return -2
        if key not in self._ttls:
            return -1
        import time

        remaining = int(self._ttls[key] - time.time())
        return max(0, remaining)


# =============================================================================
# Redis Implementation
# =============================================================================


class RedisCacheClient:
    """Real Redis client implementation."""

    def __init__(self, url: str) -> None:
        self._url = url
        self._redis: Any = None

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            import redis.asyncio as redis

            self._redis = await redis.from_url(
                self._url,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test connection
            await self._redis.ping()
            logger.info(f"Connected to Redis at {self._url}")

        except ImportError:
            raise RuntimeError("redis required: pip install redis")

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()

    async def get(self, key: str) -> str | None:
        if self._redis is None:
            await self.connect()
        result = await self._redis.get(key)
        return str(result) if result is not None else None

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        if self._redis is None:
            await self.connect()
        if ttl:
            await self._redis.setex(key, ttl, value)
        else:
            await self._redis.set(key, value)

    async def delete(self, key: str) -> None:
        if self._redis is None:
            await self.connect()
        await self._redis.delete(key)

    async def exists(self, key: str) -> bool:
        if self._redis is None:
            await self.connect()
        result = await self._redis.exists(key)
        return bool(result > 0)

    async def expire(self, key: str, ttl: int) -> None:
        if self._redis is None:
            await self.connect()
        await self._redis.expire(key, ttl)

    async def ttl(self, key: str) -> int:
        if self._redis is None:
            await self.connect()
        result = await self._redis.ttl(key)
        return int(result)


# =============================================================================
# Soul Cache
# =============================================================================


class SoulCache:
    """
    Redis-backed soul state cache.

    Provides fast access to K-gent soul state for:
    - Session state (mode, interaction counts)
    - Eigenvector confidences
    - Active dialogue mode

    Example:
        >>> cache = await SoulCache.create()
        >>> await cache.cache_session(session_id, state)
        >>> state = await cache.get_session(session_id)
    """

    def __init__(
        self,
        config: SoulCacheConfig,
        client: CacheClient,
    ) -> None:
        self._config = config
        self._client = client

    @classmethod
    async def create(
        cls,
        config: SoulCacheConfig | None = None,
    ) -> "SoulCache":
        """Create a SoulCache with appropriate backend."""
        cfg = config or SoulCacheConfig.from_env()

        # Use Protocol type for flexibility
        client: CacheClient
        if cfg.redis_url.startswith("mock://"):
            client = MockCacheClient()
        else:
            redis_client = RedisCacheClient(cfg.redis_url)
            await redis_client.connect()
            client = redis_client

        return cls(config=cfg, client=client)

    def _key(self, *parts: str) -> str:
        """Build a cache key with prefix."""
        return self._config.key_prefix + ":".join(parts)

    # ─────────────────────────────────────────────────────────────────────────
    # Session State
    # ─────────────────────────────────────────────────────────────────────────

    async def cache_session(
        self,
        session_id: str,
        active_mode: str,
        interactions_count: int,
        tokens_used: int,
        created_at: datetime,
        last_interaction: datetime | None = None,
    ) -> None:
        """Cache session state."""
        state = CachedSessionState(
            session_id=session_id,
            active_mode=active_mode,
            interactions_count=interactions_count,
            tokens_used_session=tokens_used,
            created_at=created_at.isoformat(),
            last_interaction=last_interaction.isoformat() if last_interaction else None,
        )

        key = self._key("session", session_id)
        await self._client.set(key, state.to_json(), self._config.session_ttl)
        logger.debug(f"Cached session: {session_id}")

    async def get_session(self, session_id: str) -> CachedSessionState | None:
        """Get cached session state."""
        key = self._key("session", session_id)
        data = await self._client.get(key)

        if data is None:
            return None

        return CachedSessionState.from_json(data)

    async def invalidate_session(self, session_id: str) -> None:
        """Invalidate cached session state."""
        key = self._key("session", session_id)
        await self._client.delete(key)
        logger.debug(f"Invalidated session: {session_id}")

    async def touch_session(self, session_id: str) -> None:
        """Extend session TTL without updating content."""
        key = self._key("session", session_id)
        if await self._client.exists(key):
            await self._client.expire(key, self._config.session_ttl)

    # ─────────────────────────────────────────────────────────────────────────
    # Eigenvectors
    # ─────────────────────────────────────────────────────────────────────────

    async def cache_eigenvectors(
        self,
        soul_id: str,
        aesthetic: float,
        categorical: float,
        collaborative: float,
        ethical: float,
        joyful: float,
        tasteful: float,
    ) -> None:
        """Cache eigenvector confidences."""
        evs = CachedEigenvectors(
            aesthetic=aesthetic,
            categorical=categorical,
            collaborative=collaborative,
            ethical=ethical,
            joyful=joyful,
            tasteful=tasteful,
            cached_at=datetime.now(timezone.utc).isoformat(),
        )

        key = self._key("eigenvectors", soul_id)
        await self._client.set(key, evs.to_json(), self._config.eigenvector_ttl)

    async def get_eigenvectors(self, soul_id: str) -> CachedEigenvectors | None:
        """Get cached eigenvector confidences."""
        key = self._key("eigenvectors", soul_id)
        data = await self._client.get(key)

        if data is None:
            return None

        return CachedEigenvectors.from_json(data)

    async def invalidate_eigenvectors(self, soul_id: str) -> None:
        """Invalidate cached eigenvectors."""
        key = self._key("eigenvectors", soul_id)
        await self._client.delete(key)

    # ─────────────────────────────────────────────────────────────────────────
    # Active Mode
    # ─────────────────────────────────────────────────────────────────────────

    async def cache_mode(
        self,
        session_id: str,
        mode: str,
        reason: str | None = None,
    ) -> None:
        """Cache active dialogue mode."""
        cached = CachedActiveMode(
            mode=mode,
            changed_at=datetime.now(timezone.utc).isoformat(),
            reason=reason,
        )

        key = self._key("mode", session_id)
        await self._client.set(key, cached.to_json(), self._config.mode_ttl)

    async def get_mode(self, session_id: str) -> CachedActiveMode | None:
        """Get cached active mode."""
        key = self._key("mode", session_id)
        data = await self._client.get(key)

        if data is None:
            return None

        return CachedActiveMode.from_json(data)

    async def invalidate_mode(self, session_id: str) -> None:
        """Invalidate cached mode."""
        key = self._key("mode", session_id)
        await self._client.delete(key)

    # ─────────────────────────────────────────────────────────────────────────
    # Bulk Operations
    # ─────────────────────────────────────────────────────────────────────────

    async def invalidate_all_for_soul(self, soul_id: str) -> None:
        """Invalidate all cached data for a soul."""
        await self.invalidate_session(soul_id)
        await self.invalidate_eigenvectors(soul_id)
        await self.invalidate_mode(soul_id)
        logger.debug(f"Invalidated all cache for soul: {soul_id}")

    # ─────────────────────────────────────────────────────────────────────────
    # Health Check
    # ─────────────────────────────────────────────────────────────────────────

    async def ping(self) -> bool:
        """Check if cache is healthy."""
        try:
            test_key = self._key("__health_check__")
            await self._client.set(test_key, "1", ttl=5)
            result = await self._client.get(test_key)
            await self._client.delete(test_key)
            return result == "1"
        except Exception as e:
            logger.warning(f"Cache health check failed: {e}")
            return False


# =============================================================================
# Factory Functions
# =============================================================================


_cache_instance: SoulCache | None = None


async def get_soul_cache(
    config: SoulCacheConfig | None = None,
) -> SoulCache:
    """Get or create the global SoulCache instance."""
    global _cache_instance

    if _cache_instance is None:
        _cache_instance = await SoulCache.create(config)

    return _cache_instance


async def close_soul_cache() -> None:
    """Close the global SoulCache instance."""
    global _cache_instance
    _cache_instance = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "SoulCache",
    "SoulCacheConfig",
    "CachedSessionState",
    "CachedEigenvectors",
    "CachedActiveMode",
    "get_soul_cache",
    "close_soul_cache",
]
