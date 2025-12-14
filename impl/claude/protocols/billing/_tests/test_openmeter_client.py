"""Tests for OpenMeter usage metering client."""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from protocols.billing.openmeter_client import (
    OpenMeterClient,
    OpenMeterConfig,
    UsageEventSchema,
    UsageEventType,
)


class TestUsageEventSchema:
    """Tests for UsageEventSchema."""

    def test_create_event(self) -> None:
        """Test creating a usage event."""
        event = UsageEventSchema.create(
            event_type=UsageEventType.LLM_TOKENS,
            subject="tenant-123",
            data={"tokens_in": 100, "tokens_out": 50},
        )

        assert event.type == "llm.tokens"
        assert event.subject == "tenant-123"
        assert event.source == "kgents-api"
        assert event.data["tokens_in"] == 100

    def test_event_to_dict(self) -> None:
        """Test converting event to dict."""
        event = UsageEventSchema.create(
            event_type=UsageEventType.API_REQUEST,
            subject="tenant-456",
            data={"endpoint": "/v1/soul/dialogue", "method": "POST"},
        )

        d = event.to_dict()

        assert d["type"] == "api.request"
        assert d["subject"] == "tenant-456"
        assert "id" in d
        assert "time" in d


class TestOpenMeterConfig:
    """Tests for OpenMeterConfig."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = OpenMeterConfig()

        assert config.api_key == ""
        assert config.batch_size == 100
        assert not config.is_configured

    def test_configured(self) -> None:
        """Test configured state."""
        config = OpenMeterConfig(api_key="om_test_key")

        assert config.is_configured

    def test_disabled(self) -> None:
        """Test disabled state."""
        config = OpenMeterConfig(api_key="om_test_key", enabled=False)

        assert not config.is_configured


class TestOpenMeterClientLocalMode:
    """Tests for OpenMeter client in local mode (no API key)."""

    @pytest.fixture
    def client(self) -> OpenMeterClient:
        """Create client in local mode."""
        config = OpenMeterConfig()  # No API key
        return OpenMeterClient(config)

    @pytest.mark.asyncio
    async def test_start_stop(self, client: OpenMeterClient) -> None:
        """Test starting and stopping client."""
        await client.start()
        assert client._running

        await client.stop()
        assert not client._running

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test async context manager."""
        config = OpenMeterConfig()

        async with OpenMeterClient(config) as client:
            assert client._running

        assert not client._running

    @pytest.mark.asyncio
    async def test_record_tokens(self, client: OpenMeterClient) -> None:
        """Test recording token usage."""
        await client.start()

        tenant_id = uuid4()
        session_id = uuid4()

        await client.record_tokens(
            tenant_id=tenant_id,
            session_id=session_id,
            tokens_in=100,
            tokens_out=50,
        )

        # Event should be buffered
        assert len(client._buffer) == 1
        assert client._buffer[0].type == "llm.tokens"

        await client.stop()

    @pytest.mark.asyncio
    async def test_record_request(self, client: OpenMeterClient) -> None:
        """Test recording API request."""
        await client.start()

        await client.record_request(
            tenant_id="tenant-123",
            endpoint="/v1/kgent/sessions",
            method="POST",
            status_code=201,
        )

        assert len(client._buffer) == 1
        assert client._buffer[0].type == "api.request"

        await client.stop()

    @pytest.mark.asyncio
    async def test_record_session_create(self, client: OpenMeterClient) -> None:
        """Test recording session creation."""
        await client.start()

        await client.record_session_create(
            tenant_id="tenant-123",
            session_id="session-456",
            agent_type="kgent",
        )

        assert len(client._buffer) == 1
        assert client._buffer[0].type == "session.create"

        await client.stop()

    @pytest.mark.asyncio
    async def test_record_message(self, client: OpenMeterClient) -> None:
        """Test recording a message."""
        await client.start()

        await client.record_message(
            tenant_id="tenant-123",
            session_id="session-456",
            message_length=150,
            role="user",
        )

        assert len(client._buffer) == 1
        assert client._buffer[0].type == "session.message"

        await client.stop()

    @pytest.mark.asyncio
    async def test_record_agentese_invoke(self, client: OpenMeterClient) -> None:
        """Test recording AGENTESE invocation."""
        await client.start()

        await client.record_agentese_invoke(
            tenant_id="tenant-123",
            path="self.soul.reflect",
            aspect="manifest",
            tokens_used=0,
        )

        assert len(client._buffer) == 1
        assert client._buffer[0].type == "agentese.invoke"

        await client.stop()


class TestOpenMeterClientBatching:
    """Tests for batching behavior."""

    @pytest.mark.asyncio
    async def test_auto_flush_on_batch_size(self) -> None:
        """Test that buffer flushes when batch size reached."""
        config = OpenMeterConfig(batch_size=5)
        client = OpenMeterClient(config)
        await client.start()

        tenant_id = "tenant-123"

        # Record 5 events (batch size)
        for i in range(5):
            await client.record_request(
                tenant_id=tenant_id,
                endpoint=f"/endpoint-{i}",
                method="GET",
                status_code=200,
            )

        # Buffer should be empty after auto-flush
        assert len(client._buffer) == 0
        assert client._events_sent == 5

        await client.stop()

    @pytest.mark.asyncio
    async def test_manual_flush(self) -> None:
        """Test manual flush."""
        config = OpenMeterConfig(batch_size=100)
        client = OpenMeterClient(config)
        await client.start()

        await client.record_request(
            tenant_id="tenant-123",
            endpoint="/test",
            method="GET",
            status_code=200,
        )

        assert len(client._buffer) == 1

        await client.flush()

        assert len(client._buffer) == 0
        assert client._events_sent == 1

        await client.stop()

    @pytest.mark.asyncio
    async def test_flush_on_stop(self) -> None:
        """Test that remaining events are flushed on stop."""
        config = OpenMeterConfig(batch_size=100)
        client = OpenMeterClient(config)
        await client.start()

        await client.record_request(
            tenant_id="tenant-123",
            endpoint="/test",
            method="GET",
            status_code=200,
        )

        assert len(client._buffer) == 1

        await client.stop()

        # Events should be flushed on stop
        assert client._events_sent == 1


class TestOpenMeterClientMetrics:
    """Tests for client metrics."""

    @pytest.mark.asyncio
    async def test_get_metrics(self) -> None:
        """Test getting client metrics."""
        config = OpenMeterConfig(batch_size=10)
        client = OpenMeterClient(config)
        await client.start()

        # Record some events
        for _ in range(15):  # Will trigger one flush
            await client.record_request(
                tenant_id="tenant-123",
                endpoint="/test",
                method="GET",
                status_code=200,
            )

        metrics = client.get_metrics()

        assert metrics["events_sent"] == 10  # First batch
        assert metrics["events_buffered"] == 5  # Remaining
        assert metrics["running"] is True

        await client.stop()

    @pytest.mark.asyncio
    async def test_health_check_local_mode(self) -> None:
        """Test health check in local mode."""
        config = OpenMeterConfig()  # No API key
        client = OpenMeterClient(config)
        await client.start()

        health = await client.health_check()

        assert health["status"] == "disabled"
        assert health["mode"] == "local"

        await client.stop()


class TestUsageEventTypes:
    """Tests for usage event type enum."""

    def test_all_event_types(self) -> None:
        """Test all event types have string values."""
        expected_types = [
            "api.request",
            "llm.tokens",
            "session.create",
            "session.message",
            "agentese.invoke",
            "storage.write",
            "storage.read",
        ]

        actual_types = [t.value for t in UsageEventType]

        for expected in expected_types:
            assert expected in actual_types
