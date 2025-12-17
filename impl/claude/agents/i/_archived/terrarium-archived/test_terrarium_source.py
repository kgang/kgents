"""
Tests for TerrariumWebSocketSource.

Tests the WebSocket data source that bridges Terrarium metrics
to I-gent widgets.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agents.i.data.terrarium_source import (
    AgentMetrics,
    TerrariumWebSocketSource,
)

# Check if websockets is available
try:
    import websockets  # noqa: F401

    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

requires_websockets = pytest.mark.skipif(
    not HAS_WEBSOCKETS,
    reason="websockets package not installed",
)


# =============================================================================
# Tests: AgentMetrics
# =============================================================================


class TestAgentMetrics:
    """Tests for AgentMetrics dataclass."""

    def test_default_values(self) -> None:
        """Test default metric values."""
        metrics = AgentMetrics(agent_id="test-agent")

        assert metrics.agent_id == "test-agent"
        assert metrics.state == "unknown"
        assert metrics.pressure == 0.0
        assert metrics.flow == 0.0
        assert metrics.temperature == 0.0

    def test_activity_property(self) -> None:
        """Test activity is mapped from temperature."""
        metrics = AgentMetrics(agent_id="test", temperature=0.75)

        assert metrics.activity == 0.75

    def test_health_healthy(self) -> None:
        """Test health is healthy when pressure < 50."""
        metrics = AgentMetrics(agent_id="test", pressure=30.0)

        assert metrics.health == "healthy"

    def test_health_degraded(self) -> None:
        """Test health is degraded when pressure 50-80."""
        metrics = AgentMetrics(agent_id="test", pressure=60.0)

        assert metrics.health == "degraded"

    def test_health_critical(self) -> None:
        """Test health is critical when pressure > 80."""
        metrics = AgentMetrics(agent_id="test", pressure=90.0)

        assert metrics.health == "critical"

    def test_health_boundary_50(self) -> None:
        """Test health at pressure = 50 (boundary is >= 50)."""
        metrics = AgentMetrics(agent_id="test", pressure=50.0)

        # 50 is the boundary - it's degraded (>= 50)
        assert metrics.health == "degraded"

    def test_health_just_below_50(self) -> None:
        """Test health just below pressure = 50."""
        metrics = AgentMetrics(agent_id="test", pressure=49.9)

        assert metrics.health == "healthy"

    def test_health_boundary_80(self) -> None:
        """Test health at pressure = 80."""
        metrics = AgentMetrics(agent_id="test", pressure=80.0)

        assert metrics.health == "degraded"

    def test_health_above_80(self) -> None:
        """Test health at pressure = 80.1."""
        metrics = AgentMetrics(agent_id="test", pressure=80.1)

        assert metrics.health == "critical"


# =============================================================================
# Tests: TerrariumWebSocketSource Initialization
# =============================================================================


class TestTerrariumWebSocketSourceInit:
    """Tests for TerrariumWebSocketSource initialization."""

    def test_default_values(self) -> None:
        """Test default configuration."""
        source = TerrariumWebSocketSource()

        assert source.base_url == "ws://localhost:8080"
        assert source.reconnect_delay == 2.0
        assert source.max_reconnect_attempts == 5

    def test_custom_values(self) -> None:
        """Test custom configuration."""
        source = TerrariumWebSocketSource(
            base_url="ws://custom:9000",
            reconnect_delay=5.0,
            max_reconnect_attempts=10,
        )

        assert source.base_url == "ws://custom:9000"
        assert source.reconnect_delay == 5.0
        assert source.max_reconnect_attempts == 10

    def test_callbacks(self) -> None:
        """Test callback registration."""
        on_connected = MagicMock()
        on_disconnected = MagicMock()
        on_error = MagicMock()

        source = TerrariumWebSocketSource(
            on_connected=on_connected,
            on_disconnected=on_disconnected,
            on_error=on_error,
        )

        assert source.on_connected is on_connected
        assert source.on_disconnected is on_disconnected
        assert source.on_error is on_error


# =============================================================================
# Tests: Event Parsing
# =============================================================================


class TestParseEvent:
    """Tests for _parse_event method."""

    def test_parse_metabolism_event(self) -> None:
        """Test parsing metabolism event."""
        source = TerrariumWebSocketSource()
        event = {
            "type": "metabolism",
            "agent_id": "flux-abc",
            "state": "flowing",
            "pressure": 45.0,
            "flow": 12.5,
            "temperature": 0.8,
        }

        metrics = source._parse_event("flux-abc", event)

        assert metrics is not None
        assert metrics.agent_id == "flux-abc"
        assert metrics.state == "flowing"
        assert metrics.pressure == 45.0
        assert metrics.flow == 12.5
        assert metrics.temperature == 0.8

    def test_parse_agent_stopped_event(self) -> None:
        """Test parsing agent_stopped event."""
        source = TerrariumWebSocketSource()
        event = {
            "type": "agent_stopped",
            "agent_id": "flux-abc",
        }

        metrics = source._parse_event("flux-abc", event)

        assert metrics is not None
        assert metrics.agent_id == "flux-abc"
        assert metrics.state == "stopped"
        assert metrics.pressure == 0.0
        assert metrics.flow == 0.0
        assert metrics.temperature == 0.0

    def test_parse_fever_event_with_last_metrics(self) -> None:
        """Test parsing fever event when last metrics exist."""
        source = TerrariumWebSocketSource()

        # Set up last metrics
        source._last_metrics["flux-abc"] = AgentMetrics(
            agent_id="flux-abc",
            state="flowing",
            pressure=30.0,
            flow=10.0,
            temperature=0.5,
        )

        event = {
            "type": "fever",
            "agent_id": "flux-abc",
            "temperature": 0.95,
        }

        metrics = source._parse_event("flux-abc", event)

        assert metrics is not None
        assert metrics.temperature == 0.95
        # Other values preserved from last metrics
        assert metrics.pressure == 30.0
        assert metrics.flow == 10.0

    def test_parse_fever_event_without_last_metrics(self) -> None:
        """Test parsing fever event when no last metrics."""
        source = TerrariumWebSocketSource()
        event = {
            "type": "fever",
            "agent_id": "flux-abc",
            "temperature": 0.95,
        }

        metrics = source._parse_event("flux-abc", event)

        assert metrics is None  # Can't create fever metrics without baseline

    def test_parse_unknown_event_type(self) -> None:
        """Test parsing unknown event type."""
        source = TerrariumWebSocketSource()
        event = {
            "type": "some_other_event",
            "data": "something",
        }

        metrics = source._parse_event("flux-abc", event)

        assert metrics is None

    def test_parse_ping_event(self) -> None:
        """Test parsing ping event (ignored)."""
        source = TerrariumWebSocketSource()
        event = {"type": "ping"}

        metrics = source._parse_event("flux-abc", event)

        assert metrics is None

    def test_parse_metabolism_with_missing_fields(self) -> None:
        """Test parsing metabolism event with missing optional fields."""
        source = TerrariumWebSocketSource()
        event = {
            "type": "metabolism",
            # No other fields
        }

        metrics = source._parse_event("flux-abc", event)

        assert metrics is not None
        assert metrics.agent_id == "flux-abc"
        assert metrics.state == "unknown"
        assert metrics.pressure == 0.0


# =============================================================================
# Tests: Connection State
# =============================================================================


class TestConnectionState:
    """Tests for connection state tracking."""

    def test_is_connected_false_initially(self) -> None:
        """Test is_connected returns False initially."""
        source = TerrariumWebSocketSource()

        assert source.is_connected("flux-abc") is False

    def test_connected_agents_empty_initially(self) -> None:
        """Test connected_agents is empty initially."""
        source = TerrariumWebSocketSource()

        assert source.connected_agents == []

    def test_get_last_metrics_none_initially(self) -> None:
        """Test get_last_metrics returns None initially."""
        source = TerrariumWebSocketSource()

        assert source.get_last_metrics("flux-abc") is None

    def test_get_last_metrics_after_parse(self) -> None:
        """Test get_last_metrics after parsing an event."""
        source = TerrariumWebSocketSource()

        # Manually set last metrics (normally done during observe)
        source._last_metrics["flux-abc"] = AgentMetrics(
            agent_id="flux-abc",
            state="flowing",
            temperature=0.5,
        )

        metrics = source.get_last_metrics("flux-abc")

        assert metrics is not None
        assert metrics.agent_id == "flux-abc"


# =============================================================================
# Tests: Async Operations
# =============================================================================


class TestAsyncOperations:
    """Tests for async operations."""

    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self) -> None:
        """Test disconnect when not connected."""
        source = TerrariumWebSocketSource()

        result = await source.disconnect("flux-abc")

        assert result is False

    @pytest.mark.asyncio
    async def test_disconnect_all_empty(self) -> None:
        """Test disconnect_all when no connections."""
        source = TerrariumWebSocketSource()

        count = await source.disconnect_all()

        assert count == 0


# =============================================================================
# Mock WebSocket for Integration Tests
# =============================================================================


@dataclass
class MockWebSocket:
    """Mock WebSocket for testing."""

    messages: list[str]
    _index: int = 0
    closed: bool = False

    async def close(self) -> None:
        """Close the connection."""
        self.closed = True

    def __aiter__(self) -> "MockWebSocket":
        return self

    async def __anext__(self) -> str:
        if self._index >= len(self.messages) or self.closed:
            raise StopAsyncIteration
        message = self.messages[self._index]
        self._index += 1
        return message


@requires_websockets
class TestObserveIntegration:
    """Integration tests for observe method."""

    @pytest.mark.asyncio
    async def test_observe_yields_metrics(self) -> None:
        """Test observe yields metrics from WebSocket messages."""
        source = TerrariumWebSocketSource()

        messages = [
            json.dumps(
                {
                    "type": "metabolism",
                    "agent_id": "flux-abc",
                    "state": "flowing",
                    "pressure": 25.0,
                    "flow": 10.0,
                    "temperature": 0.5,
                }
            ),
            json.dumps(
                {
                    "type": "metabolism",
                    "agent_id": "flux-abc",
                    "state": "flowing",
                    "pressure": 30.0,
                    "flow": 12.0,
                    "temperature": 0.6,
                }
            ),
        ]

        mock_ws = MockWebSocket(messages=messages)

        # Mock the websockets.connect context manager
        mock_connect = AsyncMock()
        mock_connect.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        with patch("websockets.connect", return_value=mock_connect):
            # Collect metrics
            results = []
            async for metrics in source._connect_and_observe(
                "flux-abc", "ws://test/observe/flux-abc"
            ):
                results.append(metrics)

        assert len(results) == 2
        assert results[0].temperature == 0.5
        assert results[1].temperature == 0.6

    @pytest.mark.asyncio
    async def test_observe_filters_non_metabolism_events(self) -> None:
        """Test observe filters out non-metabolism events."""
        source = TerrariumWebSocketSource()

        messages = [
            json.dumps({"type": "ping"}),
            json.dumps(
                {
                    "type": "metabolism",
                    "agent_id": "flux-abc",
                    "temperature": 0.5,
                }
            ),
            json.dumps({"type": "snapshot", "data": {}}),
        ]

        mock_ws = MockWebSocket(messages=messages)

        mock_connect = AsyncMock()
        mock_connect.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        with patch("websockets.connect", return_value=mock_connect):
            results = []
            async for metrics in source._connect_and_observe("flux-abc", "ws://test"):
                results.append(metrics)

        # Only the metabolism event should produce metrics
        assert len(results) == 1
        assert results[0].temperature == 0.5

    @pytest.mark.asyncio
    async def test_observe_handles_invalid_json(self) -> None:
        """Test observe handles invalid JSON gracefully."""
        source = TerrariumWebSocketSource()

        messages = [
            "not valid json",
            json.dumps(
                {
                    "type": "metabolism",
                    "agent_id": "flux-abc",
                    "temperature": 0.5,
                }
            ),
        ]

        mock_ws = MockWebSocket(messages=messages)

        mock_connect = AsyncMock()
        mock_connect.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        with patch("websockets.connect", return_value=mock_connect):
            results = []
            async for metrics in source._connect_and_observe("flux-abc", "ws://test"):
                results.append(metrics)

        # Should still get the valid message
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_callbacks_called(self) -> None:
        """Test on_connected and on_disconnected callbacks are called."""
        on_connected = MagicMock()
        on_disconnected = MagicMock()

        source = TerrariumWebSocketSource(
            on_connected=on_connected,
            on_disconnected=on_disconnected,
        )

        messages = [
            json.dumps(
                {
                    "type": "metabolism",
                    "agent_id": "flux-abc",
                    "temperature": 0.5,
                }
            ),
        ]

        mock_ws = MockWebSocket(messages=messages)

        mock_connect = AsyncMock()
        mock_connect.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        with patch("websockets.connect", return_value=mock_connect):
            async for _ in source._connect_and_observe("flux-abc", "ws://test"):
                pass

        on_connected.assert_called_once_with("flux-abc")
        on_disconnected.assert_called_once_with("flux-abc")

    @pytest.mark.asyncio
    async def test_last_metrics_updated(self) -> None:
        """Test last_metrics is updated during observation."""
        source = TerrariumWebSocketSource()

        messages = [
            json.dumps(
                {
                    "type": "metabolism",
                    "agent_id": "flux-abc",
                    "temperature": 0.5,
                }
            ),
            json.dumps(
                {
                    "type": "metabolism",
                    "agent_id": "flux-abc",
                    "temperature": 0.8,
                }
            ),
        ]

        mock_ws = MockWebSocket(messages=messages)

        mock_connect = AsyncMock()
        mock_connect.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        with patch("websockets.connect", return_value=mock_connect):
            async for _ in source._connect_and_observe("flux-abc", "ws://test"):
                pass

        # Last metrics should be the final value
        last = source.get_last_metrics("flux-abc")
        assert last is not None
        assert last.temperature == 0.8
