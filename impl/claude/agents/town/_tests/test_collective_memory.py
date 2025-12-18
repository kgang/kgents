"""
Tests for TownCollectiveMemory.

Phase 3 of Crown Jewels completion: Cross-citizen memory.

Tests:
- Recording town events
- Retrieving recent events
- Finding events involving specific citizens
- Getting shared context for dialogue
- Persistence with D-gent
"""

from __future__ import annotations

import pytest

from agents.town.persistent_memory import (
    CollectiveEvent,
    TownCollectiveMemory,
    create_collective_memory,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_dgent():
    """Create a mock D-gent that stores data in memory."""
    from unittest.mock import MagicMock

    storage: dict[str, bytes] = {}

    dgent = MagicMock()

    async def mock_get(key: str, namespace: str):
        full_key = f"{namespace}:{key}"
        if full_key in storage:
            datum = MagicMock()
            datum.content = storage[full_key]
            return datum
        if key in storage:
            datum = MagicMock()
            datum.content = storage[key]
            return datum
        return None

    async def mock_upsert(datum):
        # Store the bytes content
        storage[datum.id] = datum.content

    dgent.get = mock_get
    dgent.upsert = mock_upsert

    return dgent


@pytest.fixture
def memory(mock_dgent):
    """Create a TownCollectiveMemory instance."""
    return TownCollectiveMemory("test-town", mock_dgent)


# =============================================================================
# CollectiveEvent Tests
# =============================================================================


class TestCollectiveEvent:
    """Tests for CollectiveEvent dataclass."""

    def test_create_event(self):
        """Test creating an event."""
        event = CollectiveEvent(
            event_id="evt-123",
            event_type="dialogue",
            content="Baker and Merchant discussed trade",
            participants=["baker", "merchant"],
        )
        assert event.event_id == "evt-123"
        assert event.event_type == "dialogue"
        assert "Baker" in event.content
        assert "baker" in event.participants

    def test_event_serialization(self):
        """Test event to_dict and from_dict."""
        event = CollectiveEvent(
            event_id="evt-456",
            event_type="meeting",
            content="Town meeting held",
            participants=["mayor", "baker", "merchant"],
            metadata={"topic": "water"},
        )

        data = event.to_dict()
        restored = CollectiveEvent.from_dict(data)

        assert restored.event_id == event.event_id
        assert restored.event_type == event.event_type
        assert restored.content == event.content
        assert restored.participants == event.participants
        assert restored.metadata == event.metadata


# =============================================================================
# TownCollectiveMemory Tests
# =============================================================================


class TestTownCollectiveMemory:
    """Tests for TownCollectiveMemory class."""

    @pytest.mark.asyncio
    async def test_load_empty_memory(self, memory):
        """Test loading when no prior data exists."""
        await memory.load()
        assert memory._loaded
        assert len(memory._events) == 0

    @pytest.mark.asyncio
    async def test_record_event(self, memory):
        """Test recording a town event."""
        await memory.load()

        event = await memory.record_event(
            event_type="dialogue",
            content="The baker and merchant struck a deal",
            participants=["baker", "merchant"],
            metadata={"trade_value": 100},
        )

        assert event.event_type == "dialogue"
        assert "baker" in event.participants
        assert len(memory._events) == 1

    @pytest.mark.asyncio
    async def test_get_recent_events(self, memory):
        """Test retrieving recent events."""
        await memory.load()

        # Record multiple events
        for i in range(5):
            await memory.record_event(
                event_type="trade" if i % 2 == 0 else "dialogue",
                content=f"Event {i}",
                participants=[f"citizen-{i}"],
            )

        # Get all recent
        recent = await memory.get_recent_events(limit=10)
        assert len(recent) == 5

        # Most recent first
        assert "Event 4" in recent[0].content

    @pytest.mark.asyncio
    async def test_get_recent_events_by_type(self, memory):
        """Test filtering events by type."""
        await memory.load()

        await memory.record_event("trade", "Trade 1", ["baker"])
        await memory.record_event("dialogue", "Dialogue 1", ["poet"])
        await memory.record_event("trade", "Trade 2", ["merchant"])

        trade_events = await memory.get_recent_events(limit=10, event_type="trade")
        assert len(trade_events) == 2
        assert all(e.event_type == "trade" for e in trade_events)

    @pytest.mark.asyncio
    async def test_get_events_involving_citizen(self, memory):
        """Test finding events involving a specific citizen."""
        await memory.load()

        await memory.record_event("trade", "Baker sold bread", ["baker", "merchant"])
        await memory.record_event("dialogue", "Poet recited", ["poet"])
        await memory.record_event("trade", "Baker bought flour", ["baker", "miller"])

        baker_events = await memory.get_events_involving("baker")
        assert len(baker_events) == 2
        assert all("baker" in e.participants for e in baker_events)

        poet_events = await memory.get_events_involving("poet")
        assert len(poet_events) == 1

    @pytest.mark.asyncio
    async def test_get_shared_context(self, memory):
        """Test getting shared context for dialogue."""
        await memory.load()

        await memory.record_event("trade", "Baker-merchant deal", ["baker", "merchant"])
        await memory.record_event("meeting", "Town gathering", ["baker", "poet", "miller"])
        await memory.record_event("dialogue", "Poet and merchant chat", ["poet", "merchant"])

        # Context for baker and merchant
        context = await memory.get_shared_context(["baker", "merchant"], limit=5)
        assert len(context) >= 2

        # Should prioritize events involving these citizens
        assert any("baker" in e.participants or "merchant" in e.participants for e in context)

    @pytest.mark.asyncio
    async def test_max_events_trimming(self, memory):
        """Test that events are trimmed to max_events."""
        memory._max_events = 5
        await memory.load()

        # Record more than max
        for i in range(10):
            await memory.record_event("test", f"Event {i}", [f"citizen-{i}"])

        assert len(memory._events) == 5
        # Most recent should be kept
        assert "Event 9" in memory._events[-1].content
        assert "Event 5" in memory._events[0].content

    @pytest.mark.asyncio
    async def test_summary(self, memory):
        """Test memory summary."""
        await memory.load()

        await memory.record_event("trade", "Trade event", ["baker"])
        await memory.record_event("dialogue", "Dialogue event", ["poet"])

        summary = memory.summary()
        assert summary["town_id"] == "test-town"
        assert summary["event_count"] == 2
        assert "trade" in summary["event_types"]
        assert "dialogue" in summary["event_types"]
        assert summary["loaded"]


# =============================================================================
# Persistence Tests
# =============================================================================


class TestCollectiveMemoryPersistence:
    """Tests for D-gent persistence."""

    @pytest.mark.asyncio
    async def test_events_persist_across_loads(self, mock_dgent):
        """Test that events persist when reloading memory."""
        # Create first instance and record events
        memory1 = TownCollectiveMemory("persist-test", mock_dgent)
        await memory1.load()

        await memory1.record_event("trade", "Original event", ["baker"])

        # Create new instance with same town_id
        memory2 = TownCollectiveMemory("persist-test", mock_dgent)
        await memory2.load()

        # Should have the event
        assert len(memory2._events) == 1
        assert "Original event" in memory2._events[0].content


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    @pytest.mark.asyncio
    async def test_create_collective_memory(self, mock_dgent):
        """Test create_collective_memory factory."""
        memory = await create_collective_memory("factory-test", mock_dgent)

        assert memory._loaded
        assert memory._town_id == "factory-test"
