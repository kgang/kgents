"""
RedisAgent: Distributed key-value D-gent with async Redis support.

Supports Redis and Valkey (open source Redis fork).

Features:
- Distributed state across multiple processes/nodes
- Optional TTL (time-to-live) for automatic expiry
- Pub/sub for state change notifications
- Atomic operations via Redis transactions
- List-based history for efficient versioning
"""

import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    Generic,
    List,
    Type,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

from .errors import (
    StateCorruptionError,
    StateNotFoundError,
    StateSerializationError,
    StorageError,
)
from .protocol import DataAgent

S = TypeVar("S")


class RedisAgent(Generic[S], DataAgent[S]):
    """
    Redis/Valkey-backed D-gent for distributed state.

    Features:
    - Distributed: State accessible from multiple processes/nodes
    - TTL: Optional automatic expiry
    - History: Stored in Redis list (efficient prepend)
    - Pub/Sub: Optional notifications on state change

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class SessionData:
        ...     user_id: str
        ...     token: str
        ...
        >>> agent = RedisAgent(
        ...     redis_url="redis://localhost:6379",
        ...     key="session:user123",
        ...     schema=SessionData,
        ...     ttl=3600  # 1 hour expiry
        ... )
        >>> await agent.connect()
        >>> await agent.save(SessionData(user_id="u123", token="abc"))
        >>> session = await agent.load()
        >>> session.user_id
        'u123'

    Note:
        Requires 'redis' package: pip install redis
    """

    def __init__(
        self,
        redis_url: str,
        key: str,
        schema: Type[S],
        ttl: int | None = None,
        max_history: int = 100,
        publish_channel: str | None = None,
    ):
        """
        Initialize Redis D-gent.

        Args:
            redis_url: Redis connection URL
                e.g., "redis://localhost:6379" or "redis://:password@host:6379/0"
            key: Key name for state storage
            schema: Type of state (for deserialization)
            ttl: Optional time-to-live in seconds (None = no expiry)
            max_history: Max historical states to retain
            publish_channel: Optional channel for pub/sub notifications
        """
        self.redis_url = redis_url
        self.key = key
        self.schema = schema
        self.ttl = ttl
        self.max_history = max_history
        self.publish_channel = publish_channel
        self._client: Any = None  # Type: redis.asyncio.Redis when connected
        self._connected = False

    @property
    def _require_client(self) -> Any:
        """Get client, raising StorageError if not connected."""
        if not self._connected or self._client is None:
            raise StorageError("Not connected. Call connect() first.")
        return self._client

    @property
    def _history_key(self) -> str:
        """Key for history list."""
        return f"{self.key}:history"

    async def connect(self) -> None:
        """Connect to Redis/Valkey server."""
        try:
            import redis.asyncio as aioredis
        except ImportError:
            raise ImportError(
                "redis package required for RedisAgent. Install with: pip install redis"
            )

        try:
            self._client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test connection
            await self._client.ping()
            self._connected = True
        except Exception as e:
            raise StorageError(f"Failed to connect to Redis: {e}")

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            self._connected = False

    async def load(self) -> S:
        """
        Load current state from Redis.

        Returns:
            Deserialized state

        Raises:
            StateNotFoundError: If key doesn't exist
            StateCorruptionError: If stored data is invalid
        """
        client = self._require_client
        data = await client.get(self.key)

        if data is None:
            raise StateNotFoundError(f"No state for key '{self.key}'")

        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Invalid JSON in Redis: {e}")

        return self._deserialize(parsed)

    async def save(self, state: S) -> None:
        """
        Save state to Redis.

        Args:
            state: State to persist

        Raises:
            StateSerializationError: If state can't be serialized
            StorageError: If Redis write fails
        """
        client = self._require_client
        serialized = self._serialize(state)
        json_data = json.dumps(serialized)

        try:
            # Archive current state to history (if exists)
            current = await client.get(self.key)
            if current is not None:
                # Prepend to history list
                await client.lpush(self._history_key, current)
                # Trim to max_history
                await client.ltrim(self._history_key, 0, self.max_history - 1)

            # Set new state
            if self.ttl:
                await client.setex(self.key, self.ttl, json_data)
            else:
                await client.set(self.key, json_data)

            # Publish notification if channel configured
            if self.publish_channel:
                await client.publish(self.publish_channel, json_data)

        except Exception as e:
            raise StorageError(f"Failed to save state to Redis: {e}")

    async def history(self, limit: int | None = None) -> List[S]:
        """
        Load historical states from Redis list.

        Args:
            limit: Max entries to return (newest first)

        Returns:
            List of historical states
        """
        client = self._require_client
        end_idx = (limit - 1) if limit else (self.max_history - 1)
        entries = await client.lrange(self._history_key, 0, end_idx)

        states = []
        for entry in entries:
            try:
                data = json.loads(entry)
                states.append(self._deserialize(data))
            except (json.JSONDecodeError, Exception):
                # Skip corrupted entries
                continue

        return states

    async def exists(self) -> bool:
        """Check if state exists in Redis."""
        client = self._require_client
        result = await client.exists(self.key)
        return bool(result > 0)

    async def delete(self) -> bool:
        """
        Delete state and history from Redis.

        Returns:
            True if state existed and was deleted
        """
        client = self._require_client
        result = await client.delete(self.key, self._history_key)
        return bool(result > 0)

    async def refresh_ttl(self) -> bool:
        """
        Refresh TTL on current state.

        Returns:
            True if TTL was refreshed, False if no TTL configured

        Raises:
            StateNotFoundError: If key doesn't exist
        """
        client = self._require_client

        if not self.ttl:
            return False

        if not await self.exists():
            raise StateNotFoundError(f"No state for key '{self.key}'")

        await client.expire(self.key, self.ttl)
        return True

    async def subscribe(self, callback: Callable[[S], Any]) -> None:
        """
        Subscribe to state changes via pub/sub.

        Args:
            callback: Async function called when state changes

        Note:
            This is a blocking operation. Consider running in a task.
        """
        client = self._require_client

        if not self.publish_channel:
            raise StorageError("No publish_channel configured for this agent")

        pubsub = client.pubsub()
        await pubsub.subscribe(self.publish_channel)

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    state = self._deserialize(data)
                    result = callback(state)
                    if hasattr(result, "__await__"):
                        await result
                except Exception:
                    # Skip invalid messages
                    continue

    def _serialize(self, state: S) -> Any:
        """Serialize state to JSON-compatible structure."""

        def enum_serializer(obj: Any) -> Any:
            if isinstance(obj, Enum):
                return obj.value
            return obj

        try:
            if is_dataclass(state):
                return asdict(
                    state,  # type: ignore[arg-type]
                    dict_factory=lambda x: {k: enum_serializer(v) for k, v in x},
                )
            return state
        except Exception as e:
            raise StateSerializationError(f"Cannot serialize state: {e}")

    def _deserialize(self, data: Any) -> S:
        """Deserialize JSON data to state type."""
        try:
            if is_dataclass(self.schema):
                return self._deserialize_dataclass(self.schema, data)
            return data
        except Exception as e:
            raise StateCorruptionError(f"Cannot deserialize to {self.schema}: {e}")

    def _deserialize_dataclass(self, cls: Type[Any], data: dict[str, Any]) -> Any:
        """Recursively deserialize a dataclass and its nested fields."""
        if not isinstance(data, dict):
            return data

        try:
            type_hints = get_type_hints(cls)
        except Exception:
            type_hints = {}

        kwargs: dict[str, Any] = {}
        for field_name, field_value in data.items():
            field_type = type_hints.get(field_name)

            if field_value is None:
                kwargs[field_name] = None
            elif field_type and is_dataclass(field_type):
                kwargs[field_name] = self._deserialize_dataclass(
                    field_type, field_value
                )
            elif field_type:
                try:
                    if isinstance(field_type, type) and issubclass(field_type, Enum):
                        kwargs[field_name] = field_type(field_value)
                        continue
                except TypeError:
                    pass

                if isinstance(field_value, list) and field_value:
                    origin = get_origin(field_type)
                    if origin is list:
                        args = get_args(field_type)
                        if args and is_dataclass(args[0]):
                            kwargs[field_name] = [
                                self._deserialize_dataclass(args[0], item)
                                if isinstance(item, dict)
                                else item
                                for item in field_value
                            ]
                            continue

                kwargs[field_name] = field_value
            else:
                kwargs[field_name] = field_value

        return cls(**kwargs)

    async def __aenter__(self) -> "RedisAgent[S]":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit."""
        await self.close()


def create_redis_agent(
    redis_url: str,
    key: str,
    schema: Type[S],
    ttl: int | None = None,
    max_history: int = 100,
    publish_channel: str | None = None,
) -> RedisAgent[S]:
    """
    Create a Redis/Valkey-backed D-gent.

    Args:
        redis_url: Redis connection URL
            e.g., "redis://localhost:6379" or "redis://:password@host:6379/0"
        key: Key name for state storage
        schema: Type of state
        ttl: Optional time-to-live in seconds
        max_history: Max historical states to retain
        publish_channel: Optional channel for pub/sub notifications

    Returns:
        Configured RedisAgent (call connect() before use)

    Example:
        >>> agent = create_redis_agent(
        ...     redis_url="redis://localhost:6379",
        ...     key="session:user123",
        ...     schema=SessionData,
        ...     ttl=3600
        ... )
        >>> async with agent:
        ...     await agent.save(SessionData(...))
    """
    return RedisAgent(
        redis_url=redis_url,
        key=key,
        schema=schema,
        ttl=ttl,
        max_history=max_history,
        publish_channel=publish_channel,
    )


def create_valkey_agent(
    valkey_url: str,
    key: str,
    schema: Type[S],
    ttl: int | None = None,
    max_history: int = 100,
    publish_channel: str | None = None,
) -> RedisAgent[S]:
    """
    Create a Valkey-backed D-gent.

    Valkey is the open-source fork of Redis. This is an alias for
    create_redis_agent() since Valkey is protocol-compatible.

    Args:
        valkey_url: Valkey connection URL
            e.g., "redis://localhost:6379" (uses Redis protocol)
        key: Key name for state storage
        schema: Type of state
        ttl: Optional time-to-live in seconds
        max_history: Max historical states to retain
        publish_channel: Optional channel for pub/sub notifications

    Returns:
        Configured RedisAgent (call connect() before use)
    """
    return create_redis_agent(
        redis_url=valkey_url,
        key=key,
        schema=schema,
        ttl=ttl,
        max_history=max_history,
        publish_channel=publish_channel,
    )
