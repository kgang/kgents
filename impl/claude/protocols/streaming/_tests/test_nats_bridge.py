"""Tests for NATS JetStream bridge."""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import uuid4

import pytest
from protocols.streaming.nats_bridge import (
    NATSBridge,
    NATSBridgeConfig,
    NATSConnectionError,
)


class TestNATSBridgeConfig:
    """Tests for NATSBridgeConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = NATSBridgeConfig()

        assert config.servers == ["nats://localhost:4222"]
        assert config.stream_name == "kgent-events"
        assert config.enabled is True
        assert config.consumer_batch_size == 10

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = NATSBridgeConfig(
            servers=["nats://nats1:4222", "nats://nats2:4222"],
            stream_name="custom-stream",
            enabled=False,
        )

        assert len(config.servers) == 2
        assert config.stream_name == "custom-stream"
        assert config.enabled is False


class TestNATSBridgeFallback:
    """Tests for NATS bridge fallback mode (no NATS connection)."""

    @pytest.fixture
    def bridge(self) -> NATSBridge:
        """Create bridge with NATS disabled."""
        config = NATSBridgeConfig(enabled=False)
        return NATSBridge(config)

    @pytest.mark.asyncio
    async def test_connect_disabled(self, bridge: NATSBridge) -> None:
        """Test connecting when disabled uses fallback."""
        await bridge.connect()

        assert not bridge.is_connected

    @pytest.mark.asyncio
    async def test_fallback_publish(self, bridge: NATSBridge) -> None:
        """Test publishing to fallback queue."""
        await bridge.connect()

        session_id = str(uuid4())

        # Publish a chunk
        await bridge.publish_chunk(session_id, "Hello", 0)
        await bridge.publish_chunk(session_id, " World", 1)

        # Verify events in fallback queue
        assert session_id in bridge._fallback_queues
        assert bridge._fallback_queues[session_id].qsize() == 2

    @pytest.mark.asyncio
    async def test_fallback_subscribe(self, bridge: NATSBridge) -> None:
        """Test subscribing from fallback queue."""
        await bridge.connect()

        session_id = str(uuid4())

        # Publish events
        await bridge.publish_chunk(session_id, "Hello", 0)
        await bridge.publish_chunk(session_id, " World", 1)

        # Subscribe and collect events
        events = []
        async for event in bridge.subscribe_session(session_id):
            events.append(event)
            if len(events) >= 2:
                break

        assert len(events) == 2
        assert events[0]["text"] == "Hello"
        assert events[1]["text"] == " World"

    @pytest.mark.asyncio
    async def test_health_check_disabled(self, bridge: NATSBridge) -> None:
        """Test health check when disabled."""
        await bridge.connect()

        health = await bridge.health_check()

        assert health["status"] == "disabled"
        assert health["mode"] == "fallback"

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test async context manager."""
        config = NATSBridgeConfig(enabled=False)

        async with NATSBridge(config) as bridge:
            assert not bridge.is_connected

            session_id = str(uuid4())
            await bridge.publish_chunk(session_id, "Test", 0)

            assert session_id in bridge._fallback_queues


class TestNATSBridgeWithMockNATS:
    """Tests for NATS bridge with mock SoulEvents."""

    @pytest.fixture
    def bridge(self) -> NATSBridge:
        """Create bridge with NATS disabled for testing."""
        config = NATSBridgeConfig(enabled=False)
        return NATSBridge(config)

    @pytest.mark.asyncio
    async def test_publish_soul_event(self, bridge: NATSBridge) -> None:
        """Test publishing a SoulEvent."""
        from agents.k.events import dialogue_turn_event

        await bridge.connect()

        session_id = str(uuid4())
        event = dialogue_turn_event(
            message="Hello, K-gent!",
            mode="reflect",
            is_request=True,
        )

        await bridge.publish_soul_event(session_id, event)

        # Verify event in fallback queue
        assert session_id in bridge._fallback_queues
        assert bridge._fallback_queues[session_id].qsize() == 1

    @pytest.mark.asyncio
    async def test_batch_consume_empty(self, bridge: NATSBridge) -> None:
        """Test batch consume when not connected."""
        await bridge.connect()

        result = await bridge.consume_batch(
            consumer_name="test-consumer",
            subject_filter="kgent.>",
        )

        assert result == []


class TestNATSBridgeQueueManagement:
    """Tests for queue management in fallback mode."""

    @pytest.mark.asyncio
    async def test_fallback_queue_overflow(self) -> None:
        """Test that fallback queue handles overflow gracefully."""
        config = NATSBridgeConfig(enabled=False)
        bridge = NATSBridge(config)
        await bridge.connect()

        session_id = str(uuid4())

        # Fill queue beyond capacity (1000 max)
        for i in range(1010):
            await bridge.publish_chunk(session_id, f"Chunk {i}", i)

        # Should not raise, oldest messages dropped
        assert bridge._fallback_queues[session_id].qsize() <= 1000

    @pytest.mark.asyncio
    async def test_multiple_sessions(self) -> None:
        """Test handling multiple session queues."""
        config = NATSBridgeConfig(enabled=False)
        bridge = NATSBridge(config)
        await bridge.connect()

        session_ids = [str(uuid4()) for _ in range(5)]

        for sid in session_ids:
            await bridge.publish_chunk(sid, f"Hello {sid}", 0)

        assert len(bridge._fallback_queues) == 5
        for sid in session_ids:
            assert bridge._fallback_queues[sid].qsize() == 1
