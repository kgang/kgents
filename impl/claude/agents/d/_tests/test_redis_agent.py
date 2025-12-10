"""
Tests for RedisAgent (Redis and Valkey backends).

Note: Tests are skipped if redis package not installed or server not available.
Uses fakeredis for unit tests when available.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List

import pytest

# Check if dependencies are available
try:
    from ..redis_agent import (
        RedisAgent,
        create_redis_agent,
        create_valkey_agent,
    )
    from ..errors import (
        StateNotFoundError,
        StorageError,
    )

    REDIS_DEPS = True
except ImportError:
    REDIS_DEPS = False

# Check if fakeredis is available for offline testing
try:
    import fakeredis.aioredis

    FAKEREDIS_AVAILABLE = True
except ImportError:
    FAKEREDIS_AVAILABLE = False


pytestmark = pytest.mark.skipif(not REDIS_DEPS, reason="redis package not installed")


# Test fixtures


@dataclass
class SimpleState:
    value: int
    name: str


@dataclass
class NestedState:
    simple: SimpleState
    tags: List[str]


class Priority(Enum):
    LOW = "low"
    HIGH = "high"


@dataclass
class EnumState:
    priority: Priority
    count: int


class FakeRedisAgent(RedisAgent):
    """RedisAgent using fakeredis for testing without a real server."""

    async def connect(self) -> None:
        if not FAKEREDIS_AVAILABLE:
            raise ImportError("fakeredis not available")

        self._client = fakeredis.aioredis.FakeRedis(
            encoding="utf-8",
            decode_responses=True,
        )
        self._connected = True


@pytest.fixture
async def fake_redis_agent():
    """Create a fake Redis agent for testing."""
    if not FAKEREDIS_AVAILABLE:
        pytest.skip("fakeredis not installed")

    agent = FakeRedisAgent(
        redis_url="redis://fake",
        key="test:state",
        schema=SimpleState,
        max_history=10,
    )
    await agent.connect()
    yield agent
    await agent.close()


# Basic Operations


@pytest.mark.skipif(not FAKEREDIS_AVAILABLE, reason="fakeredis not installed")
class TestRedisBasicOperations:
    """Tests for basic CRUD operations with Redis."""

    @pytest.mark.asyncio
    async def test_save_and_load(self, fake_redis_agent):
        """State round-trips correctly."""
        state = SimpleState(value=42, name="test")
        await fake_redis_agent.save(state)

        loaded = await fake_redis_agent.load()
        assert loaded.value == 42
        assert loaded.name == "test"

    @pytest.mark.asyncio
    async def test_load_without_state_raises(self, fake_redis_agent):
        """Loading non-existent state raises StateNotFoundError."""
        with pytest.raises(StateNotFoundError):
            await fake_redis_agent.load()

    @pytest.mark.asyncio
    async def test_multiple_saves(self, fake_redis_agent):
        """Multiple saves update state, load returns latest."""
        await fake_redis_agent.save(SimpleState(value=1, name="v1"))
        await fake_redis_agent.save(SimpleState(value=2, name="v2"))
        await fake_redis_agent.save(SimpleState(value=3, name="v3"))

        loaded = await fake_redis_agent.load()
        assert loaded.value == 3
        assert loaded.name == "v3"

    @pytest.mark.asyncio
    async def test_exists(self, fake_redis_agent):
        """exists() correctly detects state presence."""
        assert not await fake_redis_agent.exists()

        await fake_redis_agent.save(SimpleState(value=1, name="test"))
        assert await fake_redis_agent.exists()

    @pytest.mark.asyncio
    async def test_delete(self, fake_redis_agent):
        """delete() removes state and history."""
        await fake_redis_agent.save(SimpleState(value=1, name="test"))
        assert await fake_redis_agent.exists()

        result = await fake_redis_agent.delete()
        assert result is True
        assert not await fake_redis_agent.exists()

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, fake_redis_agent):
        """delete() returns False for non-existent key."""
        result = await fake_redis_agent.delete()
        assert result is False


@pytest.mark.skipif(not FAKEREDIS_AVAILABLE, reason="fakeredis not installed")
class TestRedisHistory:
    """Tests for history functionality."""

    @pytest.mark.asyncio
    async def test_history_returns_previous_states(self, fake_redis_agent):
        """History contains previous states, not current."""
        await fake_redis_agent.save(SimpleState(value=1, name="first"))
        await fake_redis_agent.save(SimpleState(value=2, name="second"))
        await fake_redis_agent.save(SimpleState(value=3, name="third"))

        history = await fake_redis_agent.history()
        assert len(history) == 2
        assert history[0].value == 2  # Most recent before current
        assert history[1].value == 1  # Oldest

    @pytest.mark.asyncio
    async def test_history_with_limit(self, fake_redis_agent):
        """History respects limit parameter."""
        for i in range(5):
            await fake_redis_agent.save(SimpleState(value=i, name=f"v{i}"))

        history = await fake_redis_agent.history(limit=2)
        assert len(history) == 2
        assert history[0].value == 3
        assert history[1].value == 2

    @pytest.mark.asyncio
    async def test_history_empty_initially(self, fake_redis_agent):
        """Empty history for new agent."""
        history = await fake_redis_agent.history()
        assert history == []


@pytest.mark.skipif(not FAKEREDIS_AVAILABLE, reason="fakeredis not installed")
class TestRedisComplexTypes:
    """Tests for nested dataclasses and enums."""

    @pytest.mark.asyncio
    async def test_nested_dataclass(self):
        """Nested dataclasses serialize and deserialize correctly."""
        agent = FakeRedisAgent(
            redis_url="redis://fake",
            key="test:nested",
            schema=NestedState,
        )
        await agent.connect()

        state = NestedState(
            simple=SimpleState(value=1, name="inner"), tags=["a", "b", "c"]
        )
        await agent.save(state)

        loaded = await agent.load()
        assert loaded.simple.value == 1
        assert loaded.simple.name == "inner"
        assert loaded.tags == ["a", "b", "c"]

        await agent.close()

    @pytest.mark.asyncio
    async def test_enum_serialization(self):
        """Enums serialize to values and deserialize back."""
        agent = FakeRedisAgent(
            redis_url="redis://fake",
            key="test:enum",
            schema=EnumState,
        )
        await agent.connect()

        state = EnumState(priority=Priority.HIGH, count=5)
        await agent.save(state)

        loaded = await agent.load()
        assert loaded.priority == Priority.HIGH
        assert loaded.count == 5

        await agent.close()


@pytest.mark.skipif(not FAKEREDIS_AVAILABLE, reason="fakeredis not installed")
class TestRedisTTL:
    """Tests for TTL functionality."""

    @pytest.mark.asyncio
    async def test_ttl_agent_creation(self):
        """TTL agent can be created and configured."""
        agent = FakeRedisAgent(
            redis_url="redis://fake",
            key="test:ttl",
            schema=SimpleState,
            ttl=3600,
        )
        assert agent.ttl == 3600

    @pytest.mark.asyncio
    async def test_refresh_ttl(self):
        """refresh_ttl() extends expiry."""
        agent = FakeRedisAgent(
            redis_url="redis://fake",
            key="test:refresh",
            schema=SimpleState,
            ttl=3600,
        )
        await agent.connect()

        await agent.save(SimpleState(value=1, name="test"))
        result = await agent.refresh_ttl()
        assert result is True

        await agent.close()

    @pytest.mark.asyncio
    async def test_refresh_ttl_no_ttl_configured(self):
        """refresh_ttl() returns False if no TTL configured."""
        agent = FakeRedisAgent(
            redis_url="redis://fake",
            key="test:no_ttl",
            schema=SimpleState,
            ttl=None,
        )
        await agent.connect()

        await agent.save(SimpleState(value=1, name="test"))
        result = await agent.refresh_ttl()
        assert result is False

        await agent.close()

    @pytest.mark.asyncio
    async def test_refresh_ttl_nonexistent_key(self):
        """refresh_ttl() raises for non-existent key."""
        agent = FakeRedisAgent(
            redis_url="redis://fake",
            key="test:missing",
            schema=SimpleState,
            ttl=3600,
        )
        await agent.connect()

        with pytest.raises(StateNotFoundError):
            await agent.refresh_ttl()

        await agent.close()


@pytest.mark.skipif(not FAKEREDIS_AVAILABLE, reason="fakeredis not installed")
class TestRedisMultipleKeys:
    """Tests for multiple keys."""

    @pytest.mark.asyncio
    async def test_different_keys_isolated(self):
        """Different keys maintain separate state."""
        agent1 = FakeRedisAgent(
            redis_url="redis://fake",
            key="test:key1",
            schema=SimpleState,
        )
        agent2 = FakeRedisAgent(
            redis_url="redis://fake",
            key="test:key2",
            schema=SimpleState,
        )

        # Use same fakeredis instance
        await agent1.connect()
        agent2._client = agent1._client
        agent2._connected = True

        await agent1.save(SimpleState(value=1, name="one"))
        await agent2.save(SimpleState(value=2, name="two"))

        loaded1 = await agent1.load()
        loaded2 = await agent2.load()

        assert loaded1.value == 1
        assert loaded2.value == 2

        await agent1.close()


@pytest.mark.skipif(not FAKEREDIS_AVAILABLE, reason="fakeredis not installed")
class TestRedisErrors:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_not_connected_error(self):
        """Operations fail if not connected."""
        agent = FakeRedisAgent(
            redis_url="redis://fake",
            key="test:unconnected",
            schema=SimpleState,
        )

        with pytest.raises(StorageError, match="Not connected"):
            await agent.load()


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_redis_agent(self):
        """create_redis_agent() creates correct agent."""
        agent = create_redis_agent(
            redis_url="redis://localhost:6379",
            key="test:key",
            schema=SimpleState,
            ttl=3600,
        )
        assert agent.redis_url == "redis://localhost:6379"
        assert agent.key == "test:key"
        assert agent.ttl == 3600

    def test_create_valkey_agent(self):
        """create_valkey_agent() creates correct agent (alias for redis)."""
        agent = create_valkey_agent(
            valkey_url="redis://localhost:6379",
            key="test:key",
            schema=SimpleState,
        )
        assert agent.redis_url == "redis://localhost:6379"

    def test_history_key_format(self):
        """History key is correctly formatted."""
        agent = create_redis_agent(
            redis_url="redis://localhost",
            key="session:user123",
            schema=SimpleState,
        )
        assert agent._history_key == "session:user123:history"


class TestRedisAgentSerialization:
    """Tests for serialization/deserialization logic."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(not FAKEREDIS_AVAILABLE, reason="fakeredis not installed")
    async def test_primitive_dict(self):
        """Agent works with dict type."""
        agent = FakeRedisAgent(
            redis_url="redis://fake",
            key="test:dict",
            schema=dict,
        )
        await agent.connect()

        await agent.save({"count": 42, "name": "test"})
        loaded = await agent.load()
        assert loaded["count"] == 42
        assert loaded["name"] == "test"

        await agent.close()

    @pytest.mark.asyncio
    @pytest.mark.skipif(not FAKEREDIS_AVAILABLE, reason="fakeredis not installed")
    async def test_primitive_list(self):
        """Agent works with list type."""
        agent = FakeRedisAgent(
            redis_url="redis://fake",
            key="test:list",
            schema=list,
        )
        await agent.connect()

        await agent.save([1, 2, 3, "four"])
        loaded = await agent.load()
        assert loaded == [1, 2, 3, "four"]

        await agent.close()


# Integration tests (require real Redis server)


@pytest.mark.skip(reason="Requires live Redis server")
class TestRedisLiveServer:
    """Integration tests with real Redis server."""

    @pytest.fixture
    async def live_agent(self):
        """Create agent connected to real Redis."""
        agent = create_redis_agent(
            redis_url="redis://localhost:6379",
            key="test:live:state",
            schema=SimpleState,
        )
        await agent.connect()
        yield agent
        await agent.delete()
        await agent.close()

    @pytest.mark.asyncio
    async def test_real_save_load(self, live_agent):
        """State persists in real Redis."""
        await live_agent.save(SimpleState(value=42, name="live"))
        loaded = await live_agent.load()
        assert loaded.value == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
