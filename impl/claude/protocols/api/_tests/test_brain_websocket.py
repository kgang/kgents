"""
Tests for Brain WebSocket real-time communication.

Phase 1 of Crown Jewels completion: Brain WebSocket + Synergy integration.

Tests:
- WebSocket connection/disconnection
- Session management
- Synergy event broadcasting
- Subscription filtering
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Skip all tests if FastAPI not available
pytest.importorskip("fastapi")

from protocols.api.brain_websocket import (
    BrainClientMessageType,
    BrainServerMessageType,
    BrainWebSocketSession,
    broadcast_brain_event,
    create_brain_websocket_router,
    register_session,
    unregister_session,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket."""
    from starlette.websockets import WebSocketState

    ws = MagicMock()
    ws.send_json = AsyncMock()
    ws.receive_json = AsyncMock()
    ws.close = AsyncMock()

    # Simulate WebSocket connected state using actual enum
    ws.client_state = WebSocketState.CONNECTED

    return ws


@pytest.fixture
def session(mock_websocket):
    """Create a test session."""
    return BrainWebSocketSession(
        session_id="test-session-123",
        websocket=mock_websocket,
    )


# =============================================================================
# Session Tests
# =============================================================================


class TestBrainWebSocketSession:
    """Tests for BrainWebSocketSession."""

    @pytest.mark.asyncio
    async def test_send_message(self, session, mock_websocket):
        """Test sending a message to the client."""
        await session.send_message("test_type", {"key": "value"})

        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "test_type"
        assert call_args["data"] == {"key": "value"}
        assert "timestamp" in call_args

    @pytest.mark.asyncio
    async def test_handle_ping_command(self, session, mock_websocket):
        """Test handling ping command."""
        await session.handle_command({"type": "ping"})

        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == BrainServerMessageType.PONG.value
        assert "timestamp" in call_args["data"]

    @pytest.mark.asyncio
    async def test_handle_subscribe_command(self, session, mock_websocket):
        """Test handling subscribe command."""
        # Initial subscription
        initial_events = session.subscribed_events.copy()

        await session.handle_command(
            {
                "type": "subscribe",
                "events": ["custom_event"],
            }
        )

        # Check custom event was added
        assert "custom_event" in session.subscribed_events
        # Original events still present
        for event in initial_events:
            assert event in session.subscribed_events

        # Check status message sent
        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == BrainServerMessageType.STATUS.value
        assert "subscribed" in call_args["data"]

    @pytest.mark.asyncio
    async def test_handle_unsubscribe_command(self, session, mock_websocket):
        """Test handling unsubscribe command."""
        # Ensure we have the event first
        session.subscribed_events.add("crystal_formed")

        await session.handle_command(
            {
                "type": "unsubscribe",
                "events": ["crystal_formed"],
            }
        )

        assert "crystal_formed" not in session.subscribed_events

    @pytest.mark.asyncio
    async def test_handle_unknown_command(self, session, mock_websocket):
        """Test handling unknown command."""
        await session.handle_command({"type": "invalid_command"})

        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == BrainServerMessageType.ERROR.value
        assert "Unknown command" in call_args["data"]["error"]

    def test_should_receive_subscribed_event(self, session):
        """Test subscription filtering."""
        # Default subscription includes crystal_formed
        assert session.should_receive("crystal_formed")
        assert session.should_receive("memory_surfaced")
        assert session.should_receive("vault_imported")

        # Unknown event not subscribed
        assert not session.should_receive("random_event")

    def test_stop_and_stopped(self, session):
        """Test stop signal."""
        assert not session.stopped
        session.stop()
        assert session.stopped


# =============================================================================
# Registry Tests
# =============================================================================


class TestSessionRegistry:
    """Tests for session registry functions."""

    @pytest.mark.asyncio
    async def test_register_and_unregister_session(self, session):
        """Test registering and unregistering sessions."""
        # Register
        await register_session(session)

        # Broadcast should reach this session
        count = await broadcast_brain_event(
            "crystal_formed",
            {"source_id": "test-123"},
        )
        assert count == 1

        # Unregister
        await unregister_session(session)

        # Broadcast should not reach unregistered session
        count = await broadcast_brain_event(
            "crystal_formed",
            {"source_id": "test-456"},
        )
        assert count == 0

    @pytest.mark.asyncio
    async def test_broadcast_filters_by_subscription(self, session, mock_websocket):
        """Test that broadcast respects subscription filtering."""
        # Unsubscribe from crystal_formed
        session.subscribed_events.discard("crystal_formed")

        await register_session(session)

        # Broadcast crystal_formed - should not reach session
        count = await broadcast_brain_event(
            "crystal_formed",
            {"source_id": "test-123"},
        )
        assert count == 0

        # Broadcast memory_surfaced - should reach session
        count = await broadcast_brain_event(
            "memory_surfaced",
            {"source_id": "test-456"},
        )
        assert count == 1

        await unregister_session(session)


# =============================================================================
# Router Tests
# =============================================================================


class TestBrainWebSocketRouter:
    """Tests for the Brain WebSocket router."""

    def test_create_router_returns_router(self):
        """Test that router creation returns a valid router."""
        # Patch synergy subscription to avoid import issues
        with patch("protocols.api.brain_websocket._setup_synergy_subscription"):
            router = create_brain_websocket_router()
            assert router is not None
            assert hasattr(router, "routes")


# =============================================================================
# Integration Tests
# =============================================================================


class TestSynergyIntegration:
    """Tests for synergy bus integration."""

    @pytest.mark.asyncio
    async def test_synergy_event_triggers_broadcast(self, session, mock_websocket):
        """Test that synergy events trigger WebSocket broadcasts."""
        await register_session(session)

        # Simulate a synergy event broadcast
        await broadcast_brain_event(
            BrainServerMessageType.CRYSTAL_FORMED.value,
            {
                "source_id": "synergy-crystal-123",
                "payload": {"content_preview": "test content"},
                "correlation_id": "corr-123",
            },
        )

        # Verify message was sent
        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == BrainServerMessageType.CRYSTAL_FORMED.value
        assert call_args["data"]["source_id"] == "synergy-crystal-123"

        await unregister_session(session)


# =============================================================================
# Message Type Tests
# =============================================================================


class TestMessageTypes:
    """Tests for message type enums."""

    def test_server_message_types(self):
        """Test server message type values."""
        assert BrainServerMessageType.CRYSTAL_FORMED.value == "crystal_formed"
        assert BrainServerMessageType.MEMORY_SURFACED.value == "memory_surfaced"
        assert BrainServerMessageType.VAULT_IMPORTED.value == "vault_imported"
        assert BrainServerMessageType.CONNECTED.value == "connected"
        assert BrainServerMessageType.ERROR.value == "error"
        assert BrainServerMessageType.PONG.value == "pong"

    def test_client_message_types(self):
        """Test client message type values."""
        assert BrainClientMessageType.PING.value == "ping"
        assert BrainClientMessageType.SUBSCRIBE.value == "subscribe"
        assert BrainClientMessageType.UNSUBSCRIBE.value == "unsubscribe"
