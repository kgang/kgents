"""
Tests for AGENTESE Subscription Manager (v3).

Tests cover:
- Event types and creation
- Subscription lifecycle
- Pattern matching
- Event routing
- Delivery modes
- Buffer management
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import pytest

from ..subscription import (
    AgentesEvent,
    DeliveryMode,
    EventType,
    OrderingMode,
    Subscription,
    SubscriptionConfig,
    SubscriptionManager,
    SubscriptionMetrics,
    _matches_pattern,
    create_subscription_manager,
)


# === Event Tests ===


class TestAgentesEvent:
    """Tests for AgentesEvent dataclass."""

    def test_invoked_event_creation(self) -> None:
        """Test creating an INVOKED event."""
        event = AgentesEvent.invoked(
            path="self.memory.recall",
            aspect="recall",
            data={"query": "test"},
            observer_archetype="developer",
        )

        assert event.path == "self.memory.recall"
        assert event.aspect == "recall"
        assert event.data == {"query": "test"}
        assert event.observer_archetype == "developer"
        assert event.event_type == EventType.INVOKED
        assert event.event_id is not None
        assert isinstance(event.timestamp, datetime)

    def test_changed_event_creation(self) -> None:
        """Test creating a CHANGED event."""
        event = AgentesEvent.changed(
            path="self.memory.state",
            data={"new_value": 42},
        )

        assert event.path == "self.memory.state"
        assert event.event_type == EventType.CHANGED
        assert event.observer_archetype == "system"

    def test_error_event_creation(self) -> None:
        """Test creating an ERROR event."""
        error = ValueError("test error")
        event = AgentesEvent.error(
            path="self.memory.engram",
            error=error,
        )

        assert event.path == "self.memory.engram"
        assert event.event_type == EventType.ERROR
        assert event.data["error"] == "test error"
        assert event.data["type"] == "ValueError"

    def test_refused_event_creation(self) -> None:
        """Test creating a REFUSED event."""
        event = AgentesEvent.refused(
            path="void.entropy.sip",
            reason="Consent not granted",
        )

        assert event.path == "void.entropy.sip"
        assert event.event_type == EventType.REFUSED
        assert event.data["reason"] == "Consent not granted"

    def test_heartbeat_event_creation(self) -> None:
        """Test creating a HEARTBEAT event."""
        event = AgentesEvent.heartbeat()

        assert event.path == "system.heartbeat"
        assert event.event_type == EventType.HEARTBEAT
        assert event.data is None


# === Pattern Matching Tests ===


class TestPatternMatching:
    """Tests for subscription pattern matching."""

    def test_exact_match(self) -> None:
        """Test exact pattern matching."""
        assert _matches_pattern("self.memory", "self.memory") is True
        assert _matches_pattern("self.memory", "self.soul") is False

    def test_wildcard_star(self) -> None:
        """Test single wildcard matching."""
        assert _matches_pattern("self.memory", "*") is True
        assert _matches_pattern("anything", "*") is True

    def test_double_wildcard(self) -> None:
        """Test double wildcard matching."""
        assert _matches_pattern("self.memory.recall", "**") is True
        assert _matches_pattern("a.b.c.d", "**") is True

    def test_suffix_wildcard(self) -> None:
        """Test suffix wildcard matching."""
        assert _matches_pattern("self.memory", "self.*") is True
        assert _matches_pattern("self.soul", "self.*") is True
        assert _matches_pattern("world.house", "self.*") is False

    def test_double_suffix_wildcard(self) -> None:
        """Test double suffix wildcard matching."""
        assert _matches_pattern("self.memory.recall", "self.**") is True
        assert _matches_pattern("self.memory.recall.deep", "self.**") is True
        assert _matches_pattern("world.house", "self.**") is False


# === Subscription Config Tests ===


class TestSubscriptionConfig:
    """Tests for SubscriptionConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = SubscriptionConfig(pattern="self.memory.*")

        assert config.pattern == "self.memory.*"
        assert config.delivery == DeliveryMode.AT_MOST_ONCE
        assert config.ordering == OrderingMode.PER_PATH_FIFO
        assert config.buffer_size == 1000
        assert config.heartbeat_interval == 30.0
        assert config.replay_from is None
        assert config.replay_offset is None
        assert config.aspect_filter is None

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = SubscriptionConfig(
            pattern="world.*",
            delivery=DeliveryMode.AT_LEAST_ONCE,
            ordering=OrderingMode.GLOBAL_CLOCK,
            buffer_size=500,
            heartbeat_interval=10.0,
            aspect_filter="manifest",
        )

        assert config.delivery == DeliveryMode.AT_LEAST_ONCE
        assert config.ordering == OrderingMode.GLOBAL_CLOCK
        assert config.buffer_size == 500
        assert config.heartbeat_interval == 10.0
        assert config.aspect_filter == "manifest"


# === Subscription Tests ===


class TestSubscription:
    """Tests for Subscription class."""

    def test_subscription_creation(self) -> None:
        """Test creating a subscription."""
        config = SubscriptionConfig(pattern="self.memory.*")
        sub = Subscription(id="test-1", config=config)

        assert sub.id == "test-1"
        assert sub.pattern == "self.memory.*"
        assert sub.active is True
        assert sub.pending_count() == 0

    def test_subscription_matches_pattern(self) -> None:
        """Test pattern matching on subscription."""
        config = SubscriptionConfig(pattern="self.memory.*")
        sub = Subscription(id="test-1", config=config)

        assert sub._matches("self.memory.recall") is True
        assert sub._matches("self.memory.engram") is True
        assert sub._matches("self.soul.challenge") is False

    def test_subscription_matches_aspect_filter(self) -> None:
        """Test aspect filter on subscription."""
        config = SubscriptionConfig(
            pattern="self.*",
            aspect_filter="manifest",
        )
        sub = Subscription(id="test-1", config=config)

        assert sub._matches("self.memory", "manifest") is True
        assert sub._matches("self.memory", "recall") is False

    def test_emit_event(self) -> None:
        """Test emitting event to subscription."""
        config = SubscriptionConfig(pattern="self.memory.*")
        sub = Subscription(id="test-1", config=config)

        event = AgentesEvent.invoked(
            path="self.memory.recall",
            aspect="recall",
            data="result",
        )

        assert sub._emit(event) is True
        assert sub.pending_count() == 1

    def test_buffer_full_backpressure(self) -> None:
        """Test buffer full causes backpressure."""
        config = SubscriptionConfig(pattern="self.*", buffer_size=2)
        sub = Subscription(id="test-1", config=config)

        event = AgentesEvent.invoked("self.memory", "recall", "data")

        assert sub._emit(event) is True
        assert sub._emit(event) is True
        assert sub._emit(event) is False  # Buffer full

    @pytest.mark.asyncio
    async def test_close_subscription(self) -> None:
        """Test closing a subscription."""
        config = SubscriptionConfig(pattern="self.*")
        sub = Subscription(id="test-1", config=config)

        await sub.close()
        assert sub.active is False

    @pytest.mark.asyncio
    async def test_async_iteration(self) -> None:
        """Test async iteration over events."""
        config = SubscriptionConfig(pattern="self.*", heartbeat_interval=0.1)
        sub = Subscription(id="test-1", config=config)

        # Emit some events
        for i in range(3):
            event = AgentesEvent.invoked(f"self.test{i}", "manifest", f"data{i}")
            sub._emit(event)

        # Collect events
        events = []

        async def collect():
            count = 0
            async for event in sub:
                events.append(event)
                count += 1
                if count >= 3:
                    await sub.close()
                    break

        await asyncio.wait_for(collect(), timeout=2.0)
        assert len(events) == 3


# === Subscription Manager Tests ===


class TestSubscriptionManager:
    """Tests for SubscriptionManager."""

    @pytest.mark.asyncio
    async def test_subscribe(self) -> None:
        """Test creating a subscription."""
        manager = SubscriptionManager()
        sub = await manager.subscribe("self.memory.*")

        assert sub.pattern == "self.memory.*"
        assert sub.active is True
        assert manager.subscription_count == 1

    @pytest.mark.asyncio
    async def test_unsubscribe(self) -> None:
        """Test removing a subscription."""
        manager = SubscriptionManager()
        sub = await manager.subscribe("self.memory.*")

        result = await manager.unsubscribe(sub.id)
        assert result is True
        assert manager.subscription_count == 0

    @pytest.mark.asyncio
    async def test_unsubscribe_not_found(self) -> None:
        """Test unsubscribe with unknown ID."""
        manager = SubscriptionManager()

        result = await manager.unsubscribe("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_emit_to_subscribers(self) -> None:
        """Test emitting events to matching subscribers."""
        manager = SubscriptionManager()
        sub = await manager.subscribe("self.memory.*")

        delivered = manager.emit_invoked(
            path="self.memory.recall",
            aspect="recall",
            data="result",
        )

        assert delivered == 1
        assert sub.pending_count() == 1

    @pytest.mark.asyncio
    async def test_emit_no_match(self) -> None:
        """Test emitting to non-matching pattern."""
        manager = SubscriptionManager()
        sub = await manager.subscribe("self.memory.*")

        delivered = manager.emit_invoked(
            path="world.house.manifest",
            aspect="manifest",
            data="result",
        )

        assert delivered == 0
        assert sub.pending_count() == 0

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self) -> None:
        """Test emitting to multiple matching subscribers."""
        manager = SubscriptionManager()
        sub1 = await manager.subscribe("self.**")  # Matches any depth under self
        sub2 = await manager.subscribe("self.memory.*")  # Matches one level under self.memory
        sub3 = await manager.subscribe("world.*")

        delivered = manager.emit_invoked(
            path="self.memory.recall",
            aspect="recall",
            data="result",
        )

        assert delivered == 2  # sub1 and sub2 match
        assert sub1.pending_count() == 1
        assert sub2.pending_count() == 1
        assert sub3.pending_count() == 0

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test subscription context manager."""
        manager = SubscriptionManager()

        async with manager.subscription("self.*") as sub:
            assert sub.active is True
            manager.emit_invoked("self.test", "manifest", "data")
            assert sub.pending_count() == 1

        # Subscription should be closed after context
        assert sub.active is False

    @pytest.mark.asyncio
    async def test_list_subscriptions(self) -> None:
        """Test listing all subscriptions."""
        manager = SubscriptionManager()
        await manager.subscribe("self.*")
        await manager.subscribe("world.*")

        subs = manager.list_subscriptions()
        assert len(subs) == 2
        assert all("id" in s and "pattern" in s for s in subs)

    @pytest.mark.asyncio
    async def test_close_manager(self) -> None:
        """Test closing the manager."""
        manager = SubscriptionManager()
        sub1 = await manager.subscribe("self.*")
        sub2 = await manager.subscribe("world.*")

        await manager.close()

        assert sub1.active is False
        assert sub2.active is False
        assert manager.subscription_count == 0

    @pytest.mark.asyncio
    async def test_callbacks(self) -> None:
        """Test subscription callbacks."""
        subscribed: list[str] = []
        unsubscribed: list[str] = []
        events: list[tuple[str, AgentesEvent]] = []

        manager = create_subscription_manager(
            on_subscribe=lambda id, config: subscribed.append(id),
            on_unsubscribe=lambda id: unsubscribed.append(id),
            on_event=lambda id, event: events.append((id, event)),
        )

        sub = await manager.subscribe("self.*")
        assert len(subscribed) == 1

        manager.emit_invoked("self.test", "manifest", "data")
        assert len(events) == 1

        await manager.unsubscribe(sub.id)
        assert len(unsubscribed) == 1


# === Metrics Tests ===


class TestSubscriptionMetrics:
    """Tests for SubscriptionMetrics."""

    def test_record_delivered(self) -> None:
        """Test recording delivered events."""
        metrics = SubscriptionMetrics()
        metrics.record_delivered(5)

        assert metrics.events_delivered == 5

    def test_record_dropped(self) -> None:
        """Test recording dropped events."""
        metrics = SubscriptionMetrics()
        metrics.record_dropped(3)

        assert metrics.events_dropped == 3

    def test_to_dict(self) -> None:
        """Test exporting metrics as dict."""
        metrics = SubscriptionMetrics(
            active_subscriptions=2,
            events_delivered=100,
            events_dropped=5,
        )

        d = metrics.to_dict()
        assert d["active_subscriptions"] == 2
        assert d["events_delivered"] == 100
        assert d["events_dropped"] == 5


# === Integration Tests ===


class TestSubscriptionIntegration:
    """Integration tests for subscription system."""

    @pytest.mark.asyncio
    async def test_full_subscription_flow(self) -> None:
        """Test complete subscription flow."""
        manager = SubscriptionManager()
        received: list[AgentesEvent] = []

        # Create subscription
        sub = await manager.subscribe("self.memory.*")

        # Start consumer
        async def consume():
            async for event in sub:
                received.append(event)
                if len(received) >= 3:
                    await sub.close()
                    break

        consumer_task = asyncio.create_task(consume())

        # Give consumer time to start
        await asyncio.sleep(0.01)

        # Emit events
        for i in range(5):
            manager.emit_invoked(f"self.memory.event{i}", "change", f"data{i}")

        # Wait for consumer
        await asyncio.wait_for(consumer_task, timeout=2.0)

        assert len(received) == 3
        assert all(e.event_type == EventType.INVOKED for e in received)

    @pytest.mark.asyncio
    async def test_aspect_filter_integration(self) -> None:
        """Test subscription with aspect filter."""
        manager = SubscriptionManager()
        received: list[AgentesEvent] = []

        sub = await manager.subscribe("world.*", aspect="manifest")

        # Emit matching event
        manager.emit_invoked("world.house", "manifest", "house-data")
        # Emit non-matching event
        manager.emit_invoked("world.house", "transform", "transform-data")

        # Only manifest event should be received
        assert sub.pending_count() == 1

        await sub.close()
