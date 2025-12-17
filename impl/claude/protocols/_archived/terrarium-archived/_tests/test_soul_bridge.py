"""
Tests for SoulBridge: Terrarium integration for K-gent.

K-gent Phase 2: These tests verify the bridge between WebSocket
and KgentFlux, enabling K-gent as an ambient presence in web apps.
"""

import asyncio
import uuid
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from agents.k.events import (
    SoulEvent,
    SoulEventType,
    dialogue_turn_event,
    intercept_request_event,
    mode_change_event,
    ping_event,
)
from agents.k.flux import KgentFlux, KgentFluxConfig
from protocols.terrarium.gateway import Terrarium
from protocols.terrarium.mirror import HolographicBuffer
from protocols.terrarium.soul import (
    MessageType,
    SoulBridge,
    SoulBridgeConfig,
    ambient_source,
    create_soul_bridge,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def flux() -> KgentFlux:
    """Create a KgentFlux for testing."""
    config = KgentFluxConfig(
        pulse_enabled=False,
        agent_id="test-kgent",
    )
    return KgentFlux(config=config)


@pytest.fixture
def gateway() -> Terrarium:
    """Create a Terrarium gateway for testing."""
    return Terrarium()


@pytest.fixture
def bridge(flux: KgentFlux, gateway: Terrarium) -> SoulBridge:
    """Create a SoulBridge for testing."""
    return SoulBridge(
        flux=flux,
        gateway=gateway,
        config=SoulBridgeConfig(agent_id="test-kgent"),
    )


# =============================================================================
# Initialization Tests
# =============================================================================


class TestSoulBridgeInit:
    """Test SoulBridge initialization."""

    def test_create_bridge(self, flux: KgentFlux, gateway: Terrarium) -> None:
        """Should create bridge with flux and gateway."""
        bridge = SoulBridge(
            flux=flux,
            gateway=gateway,
        )

        assert bridge.flux is flux
        assert bridge.gateway is gateway

    def test_registers_with_gateway(self, bridge: SoulBridge) -> None:
        """Bridge should register with gateway."""
        assert "test-kgent" in bridge.gateway.registered_agents

    def test_creates_mirror(self, bridge: SoulBridge) -> None:
        """Bridge should create mirror."""
        assert bridge.mirror is not None
        assert isinstance(bridge.mirror, HolographicBuffer)

    def test_attaches_mirror_to_flux(self, bridge: SoulBridge) -> None:
        """Bridge should attach mirror to flux."""
        assert bridge.flux.mirror is not None

    def test_factory_function(self) -> None:
        """Should create bridge via factory."""
        bridge = create_soul_bridge(agent_id="factory-kgent")

        assert bridge.config.agent_id == "factory-kgent"
        assert bridge.flux is not None
        assert bridge.gateway is not None


class TestSoulBridgeConfig:
    """Test SoulBridgeConfig."""

    def test_default_config(self) -> None:
        """Should have sensible defaults."""
        config = SoulBridgeConfig()

        assert config.agent_id == "kgent"
        assert config.max_message_length == 10000
        assert config.default_mode == "reflect"
        assert config.processing_timeout == 60.0
        assert config.enable_broadcast is True

    def test_custom_config(self) -> None:
        """Should accept custom values."""
        config = SoulBridgeConfig(
            agent_id="custom-kgent",
            max_message_length=5000,
            default_mode="challenge",
        )

        assert config.agent_id == "custom-kgent"
        assert config.max_message_length == 5000
        assert config.default_mode == "challenge"


# =============================================================================
# Message Type Tests
# =============================================================================


class TestMessageType:
    """Test MessageType enum."""

    def test_dialogue_types(self) -> None:
        """Should have dialogue types."""
        assert MessageType.DIALOGUE.value == "dialogue"
        assert MessageType.DIALOGUE_START.value == "dialogue_start"
        assert MessageType.DIALOGUE_END.value == "dialogue_end"

    def test_system_types(self) -> None:
        """Should have system types."""
        assert MessageType.PING.value == "ping"
        assert MessageType.SNAPSHOT.value == "snapshot"

    def test_mode_type(self) -> None:
        """Should have mode change type."""
        assert MessageType.MODE_CHANGE.value == "mode_change"

    def test_intercept_type(self) -> None:
        """Should have intercept type."""
        assert MessageType.INTERCEPT.value == "intercept"


# =============================================================================
# Message Conversion Tests
# =============================================================================


class TestMessageToEvent:
    """Test WebSocket message to SoulEvent conversion."""

    def test_convert_dialogue_message(self, bridge: SoulBridge) -> None:
        """Should convert dialogue message."""
        message = {
            "type": "dialogue",
            "message": "What should I focus on?",
            "mode": "reflect",
        }

        event = bridge._message_to_event(message)

        assert event is not None
        assert event.event_type == SoulEventType.DIALOGUE_TURN
        assert event.payload["message"] == "What should I focus on?"
        assert event.payload["mode"] == "reflect"
        assert event.payload["is_request"] is True

    def test_convert_dialogue_turn_message(self, bridge: SoulBridge) -> None:
        """Should convert dialogue_turn message (alias)."""
        message = {
            "type": "dialogue_turn",
            "message": "Hello",
        }

        event = bridge._message_to_event(message)

        assert event is not None
        assert event.event_type == SoulEventType.DIALOGUE_TURN

    def test_convert_mode_change_message(self, bridge: SoulBridge) -> None:
        """Should convert mode change message."""
        message = {
            "type": "mode_change",
            "from_mode": "reflect",
            "to_mode": "challenge",
        }

        event = bridge._message_to_event(message)

        assert event is not None
        assert event.event_type == SoulEventType.MODE_CHANGE
        assert event.payload["from_mode"] == "reflect"
        assert event.payload["to_mode"] == "challenge"

    def test_convert_intercept_message(self, bridge: SoulBridge) -> None:
        """Should convert intercept message."""
        message = {
            "type": "intercept",
            "token_id": "token-123",
            "prompt": "Delete files?",
            "severity": "critical",
            "options": ["yes", "no"],
        }

        event = bridge._message_to_event(message)

        assert event is not None
        assert event.event_type == SoulEventType.INTERCEPT_REQUEST
        assert event.payload["token_id"] == "token-123"
        assert event.payload["prompt"] == "Delete files?"

    def test_convert_ping_message(self, bridge: SoulBridge) -> None:
        """Should convert ping message."""
        message = {"type": "ping"}

        event = bridge._message_to_event(message)

        assert event is not None
        assert event.event_type == SoulEventType.PING

    def test_convert_snapshot_message(self, bridge: SoulBridge) -> None:
        """Should convert snapshot message."""
        message = {"type": "snapshot"}

        event = bridge._message_to_event(message)

        assert event is not None
        assert event.event_type == SoulEventType.STATE_SNAPSHOT

    def test_unknown_message_returns_none(self, bridge: SoulBridge) -> None:
        """Should return None for unknown message types."""
        message = {"type": "unknown_type"}

        event = bridge._message_to_event(message)

        assert event is None

    def test_truncate_long_message(self, bridge: SoulBridge) -> None:
        """Should truncate messages exceeding max length."""
        bridge.config.max_message_length = 10
        message = {
            "type": "dialogue",
            "message": "This is a very long message that exceeds the limit",
        }

        event = bridge._message_to_event(message)

        assert event is not None
        assert len(event.payload["message"]) == 10

    def test_default_mode_applied(self, bridge: SoulBridge) -> None:
        """Should apply default mode when not specified."""
        bridge.config.default_mode = "advise"
        message = {
            "type": "dialogue",
            "message": "Help me",
        }

        event = bridge._message_to_event(message)

        assert event is not None
        assert event.payload["mode"] == "advise"

    def test_correlation_id_generated(self, bridge: SoulBridge) -> None:
        """Should generate correlation ID if not provided."""
        message = {
            "type": "dialogue",
            "message": "Test",
        }

        event = bridge._message_to_event(message)

        assert event is not None
        assert event.correlation_id is not None
        assert event.correlation_id.startswith("ws-")

    def test_correlation_id_preserved(self, bridge: SoulBridge) -> None:
        """Should preserve provided correlation ID."""
        message = {
            "type": "dialogue",
            "message": "Test",
            "correlation_id": "my-correlation-id",
        }

        event = bridge._message_to_event(message)

        assert event is not None
        assert event.correlation_id == "my-correlation-id"


# =============================================================================
# WebSocket Message Handling Tests
# =============================================================================


class TestHandleWebSocketMessage:
    """Test handle_websocket_message method."""

    @pytest.mark.asyncio
    async def test_handle_dialogue_message(self, bridge: SoulBridge) -> None:
        """Should handle dialogue message."""
        # Mock the mirror to capture reflections
        mock_reflect = AsyncMock()
        bridge._mirror = MagicMock()
        bridge._mirror.reflect = mock_reflect

        message = {
            "type": "dialogue",
            "message": "Hello K-gent",
        }

        await bridge.handle_websocket_message(message)

        # Should have reflected the result
        assert mock_reflect.called

    @pytest.mark.asyncio
    async def test_handle_invalid_message(self, bridge: SoulBridge) -> None:
        """Should handle invalid message gracefully."""
        mock_reflect = AsyncMock()
        bridge._mirror = MagicMock()
        bridge._mirror.reflect = mock_reflect

        message = {"type": "invalid_type"}

        await bridge.handle_websocket_message(message)

        # Should have reflected an error
        assert mock_reflect.called
        call_args = mock_reflect.call_args[0][0]
        assert call_args["type"] == "error"


# =============================================================================
# Dialogue Convenience Tests
# =============================================================================


class TestBridgeDialogue:
    """Test direct dialogue method."""

    @pytest.mark.asyncio
    async def test_dialogue_returns_dict(self, bridge: SoulBridge) -> None:
        """dialogue() should return dict response."""
        result = await bridge.dialogue("What should I focus on?")

        assert isinstance(result, dict)
        assert "type" in result
        assert result["type"] == "dialogue_turn"

    @pytest.mark.asyncio
    async def test_dialogue_with_mode(self, bridge: SoulBridge) -> None:
        """dialogue() should accept mode parameter."""
        result = await bridge.dialogue(
            "Challenge my assumptions",
            mode="challenge",
        )

        assert isinstance(result, dict)
        assert "payload" in result


# =============================================================================
# Streaming Tests
# =============================================================================


class TestBridgeStreaming:
    """Test streaming functionality."""

    def test_is_streaming_initially_false(self, bridge: SoulBridge) -> None:
        """Should not be streaming initially."""
        assert not bridge.is_streaming

    @pytest.mark.asyncio
    async def test_start_streaming(self, bridge: SoulBridge) -> None:
        """Should start streaming."""
        task = bridge.start_streaming()

        try:
            assert task is not None
            await asyncio.sleep(0.1)
            # Note: Won't be streaming without flux running
        finally:
            await bridge.stop_streaming()

    @pytest.mark.asyncio
    async def test_stop_streaming(self, bridge: SoulBridge) -> None:
        """Should stop streaming."""
        task = bridge.start_streaming()
        await asyncio.sleep(0.1)
        await bridge.stop_streaming()

        assert not bridge.is_streaming


# =============================================================================
# Lifecycle Tests
# =============================================================================


class TestBridgeLifecycle:
    """Test bridge lifecycle management."""

    @pytest.mark.asyncio
    async def test_stop_cleans_up(self, bridge: SoulBridge) -> None:
        """stop() should cleanup resources."""
        await bridge.stop()

        # Should unregister from gateway
        assert "test-kgent" not in bridge.gateway.registered_agents


# =============================================================================
# Ambient Source Tests
# =============================================================================


class TestAmbientSource:
    """Test ambient event source."""

    def test_ambient_source_is_async_generator_function(self) -> None:
        """ambient_source should be an async generator function."""
        import inspect

        assert inspect.isasyncgenfunction(ambient_source)

    @pytest.mark.asyncio
    async def test_ambient_source_is_async_generator(self) -> None:
        """Calling ambient_source should return an async generator."""
        import inspect

        async_gen = ambient_source()
        assert inspect.isasyncgen(async_gen)
        # Clean up
        await async_gen.aclose()


# =============================================================================
# Integration Tests
# =============================================================================


class TestBridgeIntegration:
    """Integration tests for SoulBridge."""

    @pytest.mark.asyncio
    async def test_full_dialogue_roundtrip(self, bridge: SoulBridge) -> None:
        """Test full dialogue roundtrip."""
        # Send message and get response
        result = await bridge.dialogue("What is your aesthetic?")

        # Should have response
        assert "payload" in result
        payload = result.get("payload", {})

        # Response should not be a request
        assert payload.get("is_request") is False

    @pytest.mark.asyncio
    async def test_mode_change_roundtrip(self, bridge: SoulBridge) -> None:
        """Test mode change roundtrip."""
        # Send mode change via websocket message format
        message = {
            "type": "mode_change",
            "to_mode": "challenge",
        }

        mock_reflect = AsyncMock()
        bridge._mirror = MagicMock()
        bridge._mirror.reflect = mock_reflect

        await bridge.handle_websocket_message(message)

        # Should have response
        assert mock_reflect.called

    @pytest.mark.asyncio
    async def test_snapshot_roundtrip(self, bridge: SoulBridge) -> None:
        """Test snapshot request roundtrip."""
        message = {"type": "snapshot"}

        mock_reflect = AsyncMock()
        bridge._mirror = MagicMock()
        bridge._mirror.reflect = mock_reflect

        await bridge.handle_websocket_message(message)

        # Should have reflected state
        assert mock_reflect.called
        call_args = mock_reflect.call_args[0][0]
        assert call_args["type"] == "state_snapshot"
        assert "soul_state" in call_args
