"""
Tests for WebSocketFluxSink (C16).

These tests verify:
- WebSocket sink consumes FluxStream correctly
- JSON frame format is correct
- Backpressure handling works
- Graceful disconnect handling
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

import pytest
from agents.k.flux import FluxEvent, FluxStream
from agents.k.llm import StreamingLLMResponse
from protocols.terrarium.stream import MockWebSocket, WebSocketFluxSink

# =============================================================================
# Test Fixtures
# =============================================================================


async def data_source(values: list[str]) -> AsyncIterator[FluxEvent[str]]:
    """Create a simple data source from a list of strings."""
    for value in values:
        yield FluxEvent.data(value)


async def data_source_with_metadata(
    values: list[str], tokens: int = 100
) -> AsyncIterator[FluxEvent[str]]:
    """Create a data source that ends with a metadata event."""
    for value in values:
        yield FluxEvent.data(value)
    yield FluxEvent.metadata(
        StreamingLLMResponse(
            text="".join(values),
            tokens_used=tokens,
            model="test",
            raw_metadata={},
        )
    )


async def slow_source(
    values: list[str], delay: float = 0.01
) -> AsyncIterator[FluxEvent[str]]:
    """Create a slow data source with delays."""
    for value in values:
        await asyncio.sleep(delay)
        yield FluxEvent.data(value)


# =============================================================================
# WebSocketFluxSink Tests
# =============================================================================


class TestWebSocketFluxSinkBasic:
    """Test basic WebSocketFluxSink functionality."""

    @pytest.mark.asyncio
    async def test_sink_sends_chunk_frames(self) -> None:
        """Sink should send chunk frames for data events."""
        mock_ws = MockWebSocket()
        sink = WebSocketFluxSink(mock_ws)

        stream = FluxStream(data_source(["hello", "world"]))
        await sink.consume(stream)

        # Should have chunk frames + done frame
        assert len(mock_ws.sent_messages) == 3

        assert mock_ws.sent_messages[0] == {"type": "chunk", "data": "hello"}
        assert mock_ws.sent_messages[1] == {"type": "chunk", "data": "world"}
        assert mock_ws.sent_messages[2]["type"] == "done"

    @pytest.mark.asyncio
    async def test_sink_sends_done_frame_with_tokens(self) -> None:
        """Sink should send done frame with token count."""
        mock_ws = MockWebSocket()
        sink = WebSocketFluxSink(mock_ws)

        stream = FluxStream(data_source_with_metadata(["a", "b"], tokens=150))
        tokens = await sink.consume(stream)

        # Returns total tokens
        assert tokens == 150

        # Done frame includes token count
        done_frame = mock_ws.sent_messages[-1]
        assert done_frame == {"type": "done", "tokens": 150}

    @pytest.mark.asyncio
    async def test_sink_tracks_chunks_sent(self) -> None:
        """Sink should track number of chunks sent."""
        mock_ws = MockWebSocket()
        sink = WebSocketFluxSink(mock_ws)

        stream = FluxStream(data_source(["a", "b", "c", "d"]))
        await sink.consume(stream)

        assert sink.chunks_sent == 4

    @pytest.mark.asyncio
    async def test_sink_empty_stream(self) -> None:
        """Sink should handle empty stream."""
        mock_ws = MockWebSocket()
        sink = WebSocketFluxSink(mock_ws)

        stream = FluxStream(data_source([]))
        tokens = await sink.consume(stream)

        assert tokens == 0
        assert len(mock_ws.sent_messages) == 1  # Just done frame
        assert mock_ws.sent_messages[0] == {"type": "done", "tokens": 0}


class TestWebSocketFluxSinkMetadata:
    """Test metadata handling."""

    @pytest.mark.asyncio
    async def test_sink_aggregates_multiple_metadata(self) -> None:
        """Sink should aggregate tokens from multiple metadata events."""

        async def multi_metadata_source() -> AsyncIterator[FluxEvent[str]]:
            yield FluxEvent.data("a")
            yield FluxEvent.metadata(
                StreamingLLMResponse(
                    text="a", tokens_used=10, model="t", raw_metadata={}
                )
            )
            yield FluxEvent.data("b")
            yield FluxEvent.metadata(
                StreamingLLMResponse(
                    text="b", tokens_used=20, model="t", raw_metadata={}
                )
            )

        mock_ws = MockWebSocket()
        sink = WebSocketFluxSink(mock_ws)

        stream = FluxStream(multi_metadata_source())
        tokens = await sink.consume(stream)

        assert tokens == 30  # 10 + 20
        assert sink.total_tokens == 30


class TestWebSocketFluxSinkDisconnect:
    """Test disconnect handling."""

    @pytest.mark.asyncio
    async def test_sink_handles_client_disconnect(self) -> None:
        """Sink should handle client disconnect gracefully."""
        mock_ws = MockWebSocket().simulate_disconnect_after(2)
        sink = WebSocketFluxSink(mock_ws)

        stream = FluxStream(data_source(["a", "b", "c", "d", "e"]))

        # Should raise due to disconnect
        with pytest.raises(ConnectionError):
            await sink.consume(stream)

        # Should be cancelled
        assert sink.is_cancelled

        # Only sent messages before disconnect
        assert len(mock_ws.sent_messages) == 2

    @pytest.mark.asyncio
    async def test_sink_cancel_method(self) -> None:
        """cancel() should stop the sink."""
        mock_ws = MockWebSocket()
        sink = WebSocketFluxSink(mock_ws)

        async def long_source() -> AsyncIterator[FluxEvent[str]]:
            for i in range(100):
                yield FluxEvent.data(str(i))
                await asyncio.sleep(0.01)

        stream = FluxStream(long_source())

        # Start consumption in background
        async def consume_and_cancel() -> None:
            asyncio.get_event_loop().call_later(
                0.05, lambda: asyncio.create_task(sink.cancel())
            )
            try:
                await sink.consume(stream)
            except asyncio.CancelledError:
                pass

        await consume_and_cancel()

        # Should be cancelled
        assert sink.is_cancelled


class TestWebSocketFluxSinkBackpressure:
    """Test backpressure handling."""

    @pytest.mark.asyncio
    async def test_sink_with_slow_client(self) -> None:
        """Sink should handle slow client without overflow."""
        # Very slow client
        mock_ws = MockWebSocket().simulate_slow(0.01)
        sink = WebSocketFluxSink(mock_ws, buffer_size=2)

        stream = FluxStream(data_source(["a", "b", "c", "d"]))
        await sink.consume(stream)

        # All chunks should still be sent
        chunk_frames = [m for m in mock_ws.sent_messages if m.get("type") == "chunk"]
        assert len(chunk_frames) == 4


class TestMockWebSocket:
    """Test MockWebSocket helper."""

    @pytest.mark.asyncio
    async def test_mock_websocket_collects_messages(self) -> None:
        """MockWebSocket should collect sent messages."""
        mock_ws = MockWebSocket()

        await mock_ws.send_json({"type": "test", "data": "hello"})
        await mock_ws.send_text('{"type": "text", "data": "world"}')

        assert len(mock_ws.sent_messages) == 2
        assert mock_ws.sent_messages[0] == {"type": "test", "data": "hello"}
        assert mock_ws.sent_messages[1] == {"type": "text", "data": "world"}

    @pytest.mark.asyncio
    async def test_mock_websocket_simulate_disconnect(self) -> None:
        """MockWebSocket should simulate disconnect after N messages."""
        mock_ws = MockWebSocket().simulate_disconnect_after(3)

        await mock_ws.send_json({"msg": 1})
        await mock_ws.send_json({"msg": 2})

        # 3rd message triggers disconnect (after N=3 messages total)
        with pytest.raises(ConnectionError):
            await mock_ws.send_json({"msg": 3})

    @pytest.mark.asyncio
    async def test_mock_websocket_close(self) -> None:
        """MockWebSocket.close() should mark as closed."""
        mock_ws = MockWebSocket()

        await mock_ws.close()

        with pytest.raises(ConnectionError):
            await mock_ws.send_json({"data": "test"})


# =============================================================================
# CP6 Verification Test
# =============================================================================


class TestCP6WebSocketVerification:
    """CP6 checkpoint verification tests for WebSocket sink."""

    @pytest.mark.asyncio
    async def test_websocket_sink_streams_chunks(self) -> None:
        """
        CP6 Verification: WebSocket sink delivers real-time chunks.

        Tests the exact scenario from the checkpoint:
        - Chunks are sent as they arrive
        - Done frame includes token count
        """
        mock_ws = MockWebSocket()
        sink = WebSocketFluxSink(mock_ws)

        # Simulate LLM stream source
        async def llm_like_source() -> AsyncIterator[FluxEvent[str]]:
            chunks = ["Based ", "on ", "your ", "context, ", "I ", "suggest ", "depth."]
            for chunk in chunks:
                yield FluxEvent.data(chunk)
                await asyncio.sleep(0.001)  # Simulate streaming delay
            yield FluxEvent.metadata(
                StreamingLLMResponse(
                    text="".join(chunks),
                    tokens_used=42,
                    model="test",
                    raw_metadata={},
                )
            )

        stream = FluxStream(llm_like_source())
        await sink.consume(stream)

        messages = mock_ws.sent_messages

        # Should have chunk messages
        assert any(m["type"] == "chunk" for m in messages)

        # Last message should be done with tokens
        assert messages[-1]["type"] == "done"
        assert messages[-1]["tokens"] > 0

        # Verify token count
        assert messages[-1]["tokens"] == 42

    @pytest.mark.asyncio
    async def test_integrated_flux_operators_to_websocket(self) -> None:
        """
        Integration test: FluxStream operators → WebSocket sink.

        Verifies the complete pipeline works end-to-end.
        """
        mock_ws = MockWebSocket()
        sink = WebSocketFluxSink(mock_ws)

        # Create source with operators
        async def raw_source() -> AsyncIterator[FluxEvent[str]]:
            chunks = ["", "Hello", " ", "World", "", "!"]
            for chunk in chunks:
                yield FluxEvent.data(chunk)
            yield FluxEvent.metadata(
                StreamingLLMResponse(
                    text="".join(chunks),
                    tokens_used=100,
                    model="test",
                    raw_metadata={},
                )
            )

        # Apply operators
        stream = (
            FluxStream(raw_source())
            .filter(lambda e: e.is_data and len(e.value.strip()) > 0)
            .map(lambda e: FluxEvent.data(e.value.lower()) if e.is_data else e)
        )

        await sink.consume(stream)

        # Verify filtered and transformed chunks
        chunk_data = [
            m["data"] for m in mock_ws.sent_messages if m.get("type") == "chunk"
        ]
        assert chunk_data == ["hello", "world", "!"]

        # Verify done frame
        assert mock_ws.sent_messages[-1] == {"type": "done", "tokens": 100}
