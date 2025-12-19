"""
Stigmergy Store - High-frequency pheromone coordination.

For fast agent-to-agent signaling that doesn't need persistence.
K8s Pheromone CRDs are for durable, slow-changing signals.
Redis/NATS is for ephemeral, fast coordination.

AGENTESE: void.stigmergy.*

K8-Terrarium v2.0 Architecture:
- K8s Pheromone CRDs: Durable signals with half-life decay (Passive Stigmergy)
- StigmergyStore: Ephemeral signals with TTL (high-frequency coordination)

When to use each:
- Pheromone CRD: Cross-session signals, important alerts, narrative threads
- StigmergyStore: Real-time coordination, attention signals, ephemeral state

Design Principles:
- Graceful Degradation: Falls back to in-memory if Redis unavailable
- No Write Storms: Uses Redis TTL, not update loops
- Tasteful: Only for high-frequency signals, not persistent state
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Try to import redis - optional dependency
try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


# =============================================================================
# Ephemeral Pheromone - Fast, non-persistent signals
# =============================================================================


@dataclass
class EphemeralPheromone:
    """A fast, non-persistent pheromone signal.

    Unlike K8s Pheromone CRDs, these don't persist beyond their TTL.
    Used for high-frequency agent-to-agent coordination.
    """

    type: str
    source: str
    target: str | None
    intensity: float
    payload: dict[str, Any]
    emitted_at: datetime
    ttl_seconds: int = 60  # Auto-expire after 60 seconds

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "type": self.type,
            "source": self.source,
            "target": self.target,
            "intensity": self.intensity,
            "payload": self.payload,
            "emitted_at": self.emitted_at.isoformat(),
            "ttl_seconds": self.ttl_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EphemeralPheromone":
        """Create from dictionary."""
        return cls(
            type=data["type"],
            source=data["source"],
            target=data.get("target"),
            intensity=data.get("intensity", 1.0),
            payload=data.get("payload", {}),
            emitted_at=datetime.fromisoformat(data["emitted_at"]),
            ttl_seconds=data.get("ttl_seconds", 60),
        )


# =============================================================================
# Stigmergy Store - High-frequency pheromone coordination
# =============================================================================


class StigmergyStore:
    """
    Fast pheromone store using Redis.

    For high-frequency coordination (many signals/second).
    Falls back gracefully if Redis unavailable.

    Usage:
        store = StigmergyStore()
        connected = await store.connect()

        # Emit a pheromone
        p = EphemeralPheromone(
            type='ATTENTION',
            source='agent-a',
            target='agent-b',
            intensity=0.8,
            payload={'message': 'look here'},
            emitted_at=datetime.utcnow(),
        )
        key = await store.emit(p)

        # Sense pheromones
        sensed = await store.sense(type_filter='ATTENTION')

        await store.close()
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self._redis_url = redis_url
        self._client: Any = None  # redis.Redis | None
        self._fallback_store: dict[str, EphemeralPheromone] = {}
        self._connected = False

    async def connect(self) -> bool:
        """Connect to Redis, return False if unavailable.

        Graceful Degradation: Falls back to in-memory store.
        """
        if not REDIS_AVAILABLE:
            logger.warning("redis.asyncio not available, using in-memory fallback")
            return False

        try:
            self._client = redis.from_url(self._redis_url)
            await self._client.ping()
            self._connected = True
            logger.info(f"Connected to Redis at {self._redis_url}")
            return True
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}. Using fallback.")
            self._client = None
            self._connected = False
            return False

    @property
    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self._connected and self._client is not None

    async def emit(self, pheromone: EphemeralPheromone) -> str:
        """Emit a pheromone signal.

        Returns the key under which it was stored.
        """
        key = (
            f"stigmergy:{pheromone.type}:{pheromone.source}:{pheromone.emitted_at.timestamp():.6f}"
        )
        value = json.dumps(pheromone.to_dict())

        if self._client:
            # Use Redis SETEX for atomic set-with-TTL
            await self._client.setex(key, pheromone.ttl_seconds, value)
        else:
            # Fallback to in-memory (for testing/local dev)
            self._fallback_store[key] = pheromone
            # Note: In-memory doesn't have automatic TTL cleanup
            # Call cleanup() periodically in fallback mode

        logger.debug(f"Emitted ephemeral pheromone: {key} (TTL={pheromone.ttl_seconds}s)")
        return key

    async def sense(
        self,
        type_filter: str | None = None,
        target_filter: str | None = None,
        source_filter: str | None = None,
    ) -> list[EphemeralPheromone]:
        """Sense active pheromones matching filters.

        Args:
            type_filter: Only return pheromones of this type
            target_filter: Only return pheromones targeting this agent
            source_filter: Only return pheromones from this agent

        Returns:
            List of matching pheromones, sorted by intensity descending
        """
        results: list[EphemeralPheromone] = []

        if self._client:
            # Use Redis KEYS and GET (for small deployments)
            # For production: use SCAN for large key spaces
            pattern = f"stigmergy:{type_filter or '*'}:*"
            keys = await self._client.keys(pattern)

            for key in keys:
                value = await self._client.get(key)
                if value:
                    try:
                        data = json.loads(value)
                        pheromone = EphemeralPheromone.from_dict(data)

                        # Apply filters
                        if target_filter and pheromone.target != target_filter:
                            # But include broadcast pheromones (target=None)
                            if pheromone.target is not None:
                                continue
                        if source_filter and pheromone.source != source_filter:
                            continue

                        results.append(pheromone)
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Invalid pheromone data at {key}: {e}")
        else:
            # Fallback: in-memory store
            now = datetime.now(timezone.utc)
            for key, pheromone in list(self._fallback_store.items()):
                # Check TTL in fallback mode
                age = (now - pheromone.emitted_at).total_seconds()
                if age >= pheromone.ttl_seconds:
                    del self._fallback_store[key]
                    continue

                # Apply filters
                if type_filter and pheromone.type != type_filter:
                    continue
                if target_filter and pheromone.target != target_filter:
                    if pheromone.target is not None:
                        continue
                if source_filter and pheromone.source != source_filter:
                    continue

                results.append(pheromone)

        # Sort by intensity descending
        return sorted(results, key=lambda p: p.intensity, reverse=True)

    async def delete(self, key: str) -> bool:
        """Delete a specific pheromone by key."""
        if self._client:
            result = await self._client.delete(key)
            return bool(result > 0)
        else:
            if key in self._fallback_store:
                del self._fallback_store[key]
                return True
            return False

    async def cleanup(self) -> int:
        """Clean up expired pheromones from fallback store.

        Only needed in fallback mode (Redis handles TTL automatically).
        Returns number of pheromones cleaned up.
        """
        if self._client:
            # Redis handles TTL automatically
            return 0

        now = datetime.now(timezone.utc)
        to_delete = []
        for key, pheromone in self._fallback_store.items():
            age = (now - pheromone.emitted_at).total_seconds()
            if age >= pheromone.ttl_seconds:
                to_delete.append(key)

        for key in to_delete:
            del self._fallback_store[key]

        return len(to_delete)

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            self._connected = False


# =============================================================================
# Factory and Global Instance
# =============================================================================

_store: StigmergyStore | None = None


def get_stigmergy_store(redis_url: str = "redis://localhost:6379") -> StigmergyStore:
    """Get or create the global stigmergy store."""
    global _store
    if _store is None:
        _store = StigmergyStore(redis_url=redis_url)
    return _store


async def create_stigmergy_store(
    redis_url: str = "redis://localhost:6379",
) -> StigmergyStore:
    """Create and connect a stigmergy store."""
    store = StigmergyStore(redis_url=redis_url)
    await store.connect()
    return store


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "EphemeralPheromone",
    "StigmergyStore",
    "get_stigmergy_store",
    "create_stigmergy_store",
    "REDIS_AVAILABLE",
]
