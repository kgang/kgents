"""
WebSocketFluxSink: Stream consumer that sends FluxEvents to WebSocket clients.

C16: Terrarium WebSocket Streaming

The sink consumes a FluxStream and sends JSON frames to a WebSocket client:
- {"type": "chunk", "data": "..."} for data events
- {"type": "done", "tokens": N} for stream completion

Features:
- Backpressure handling: pauses source when WebSocket buffer fills
- Graceful disconnect: cancels stream on client disconnect
- Buffer size configurable via KGENT_WS_BUFFER_SIZE env var

Usage:
    async def stream_to_client(websocket: WebSocket, soul: KgentSoul):
        source = LLMStreamSource(client=soul.llm, system="...", user="...")
        sink = WebSocketFluxSink(websocket)
        await sink.consume(FluxStream(source))
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, TypeVar

if TYPE_CHECKING:
    from agents.k.flux import FluxStream

logger = logging.getLogger(__name__)

T = TypeVar("T")


class WebSocketLike(Protocol):
    """Protocol for WebSocket-like objects (compatible with Starlette/FastAPI)."""

    async def send_text(self, data: str) -> None:
        """Send text data to the client."""
        ...

    async def send_json(self, data: dict[str, Any]) -> None:
        """Send JSON data to the client."""
        ...

    async def close(self, code: int = 1000) -> None:
        """Close the connection."""
        ...


# Import DEFAULT_WS_BUFFER_SIZE lazily to avoid circular imports
def _get_default_buffer_size() -> int:
    """Get default buffer size from flux module."""
    try:
        from agents.k.flux import DEFAULT_WS_BUFFER_SIZE

        return DEFAULT_WS_BUFFER_SIZE
    except ImportError:
        return 32


@dataclass
class WebSocketFluxSink:
    """
    Consumes a FluxStream and sends events to a WebSocket client.

    The sink transforms FluxEvents into JSON frames for real-time streaming
    to web clients. It handles backpressure by pausing the source when the
    WebSocket buffer fills up, ensuring we don't overwhelm slow clients.

    Frame Format:
    - Data events: {"type": "chunk", "data": "<text>"}
    - Completion:  {"type": "done", "tokens": <count>}
    - Errors:      {"type": "error", "message": "<error>"}

    Usage:
        sink = WebSocketFluxSink(websocket)
        await sink.consume(stream)  # Blocks until stream exhausts or disconnect

    Backpressure:
        The sink uses an async queue between the source and WebSocket.
        When the queue fills, the source is paused (await blocks).
        This prevents memory exhaustion from slow clients.

    Graceful Shutdown:
        If the client disconnects, the sink cancels the source consumption
        and closes cleanly. No events are lost - they simply stop being sent.
    """

    websocket: WebSocketLike
    buffer_size: int = field(default_factory=_get_default_buffer_size)

    # Internal state
    _cancelled: bool = field(default=False, init=False)
    _total_tokens: int = field(default=0, init=False)
    _chunks_sent: int = field(default=0, init=False)

    @property
    def is_cancelled(self) -> bool:
        """True if the sink was cancelled (client disconnected)."""
        return self._cancelled

    @property
    def total_tokens(self) -> int:
        """Total tokens reported from metadata events."""
        return self._total_tokens

    @property
    def chunks_sent(self) -> int:
        """Number of chunk frames sent."""
        return self._chunks_sent

    async def consume(self, stream: "FluxStream[Any]") -> int:
        """
        Consume a FluxStream and send events to the WebSocket.

        Blocks until:
        - Stream exhausts (sends "done" frame, returns token count)
        - Client disconnects (cancels, returns partial token count)
        - Error occurs (sends "error" frame, raises)

        Args:
            stream: The FluxStream to consume.

        Returns:
            Total tokens used (from metadata events).

        Raises:
            ConnectionError: If WebSocket send fails unrecoverably.
        """
        # Create buffered queue for backpressure
        queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue(
            maxsize=self.buffer_size
        )

        # Producer task: read from stream, push to queue
        producer = asyncio.create_task(
            self._produce(stream, queue), name="ws-sink-producer"
        )

        # Consumer task: read from queue, send to WebSocket
        consumer = asyncio.create_task(self._consume(queue), name="ws-sink-consumer")

        try:
            # Wait for producer to finish (stream exhausted)
            await producer

            # Signal consumer to finish
            await queue.put(None)

            # Wait for consumer to finish
            await consumer

            # Send completion frame
            done_frame = {"type": "done", "tokens": self._total_tokens}
            await self._send_frame(done_frame)

            return self._total_tokens

        except asyncio.CancelledError:
            self._cancelled = True
            producer.cancel()
            consumer.cancel()
            try:
                await producer
            except asyncio.CancelledError:
                pass
            try:
                await consumer
            except asyncio.CancelledError:
                pass
            raise

        except Exception as e:
            self._cancelled = True
            producer.cancel()
            consumer.cancel()

            # Try to send error frame
            try:
                error_frame = {"type": "error", "message": str(e)}
                await self._send_frame(error_frame)
            except Exception:
                pass  # Best effort

            raise

    async def _produce(
        self,
        stream: "FluxStream[Any]",
        queue: asyncio.Queue[dict[str, Any] | None],
    ) -> None:
        """Read from stream and push frames to queue."""
        try:
            async for event in stream:
                if self._cancelled:
                    break

                if event.is_data:
                    # Data event -> chunk frame
                    frame = {"type": "chunk", "data": str(event.value)}
                    await queue.put(frame)

                elif event.is_metadata:
                    # Metadata event -> track tokens
                    if hasattr(event.value, "tokens_used"):
                        self._total_tokens += event.value.tokens_used

        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Error producing from stream: {e}")
            raise

    async def _consume(self, queue: asyncio.Queue[dict[str, Any] | None]) -> None:
        """Read from queue and send to WebSocket."""
        while not self._cancelled:
            frame = await queue.get()

            if frame is None:
                # Sentinel: producer finished
                break

            try:
                await self._send_frame(frame)
                if frame.get("type") == "chunk":
                    self._chunks_sent += 1
            except Exception as e:
                logger.warning(f"WebSocket send failed: {e}")
                self._cancelled = True
                break

    async def _send_frame(self, frame: dict[str, Any]) -> None:
        """Send a JSON frame to the WebSocket."""
        try:
            # Use send_json if available, otherwise serialize manually
            if hasattr(self.websocket, "send_json"):
                await self.websocket.send_json(frame)
            else:
                await self.websocket.send_text(json.dumps(frame))
        except Exception as e:
            # Connection error - mark cancelled and re-raise
            self._cancelled = True
            raise ConnectionError(f"WebSocket send failed: {e}") from e

    async def cancel(self) -> None:
        """Cancel the sink, stopping consumption."""
        self._cancelled = True


# =============================================================================
# Mock WebSocket for Testing
# =============================================================================


@dataclass
class MockWebSocket:
    """
    Mock WebSocket for testing WebSocketFluxSink.

    Collects sent messages for verification.

    Usage:
        mock_ws = MockWebSocket()
        sink = WebSocketFluxSink(mock_ws)
        await sink.consume(stream)

        assert any(m["type"] == "chunk" for m in mock_ws.sent_messages)
        assert mock_ws.sent_messages[-1]["type"] == "done"
    """

    sent_messages: list[dict[str, Any]] = field(default_factory=list)
    _closed: bool = field(default=False, init=False)
    _simulate_slow: float = field(default=0.0, init=False)
    _simulate_disconnect_after: int | None = field(default=None, init=False)

    async def send_text(self, data: str) -> None:
        """Send text data (parses as JSON)."""
        if self._closed:
            raise ConnectionError("WebSocket closed")

        if self._simulate_slow > 0:
            await asyncio.sleep(self._simulate_slow)

        frame = json.loads(data)
        self.sent_messages.append(frame)

        # Simulate disconnect after N messages
        if (
            self._simulate_disconnect_after is not None
            and len(self.sent_messages) >= self._simulate_disconnect_after
        ):
            self._closed = True
            raise ConnectionError("Simulated disconnect")

    async def send_json(self, data: dict[str, Any]) -> None:
        """Send JSON data."""
        if self._closed:
            raise ConnectionError("WebSocket closed")

        if self._simulate_slow > 0:
            await asyncio.sleep(self._simulate_slow)

        self.sent_messages.append(data)

        # Simulate disconnect after N messages
        if (
            self._simulate_disconnect_after is not None
            and len(self.sent_messages) >= self._simulate_disconnect_after
        ):
            self._closed = True
            raise ConnectionError("Simulated disconnect")

    async def close(self, code: int = 1000) -> None:
        """Close the connection."""
        self._closed = True

    def simulate_slow(self, delay: float) -> "MockWebSocket":
        """Configure to simulate slow client."""
        self._simulate_slow = delay
        return self

    def simulate_disconnect_after(self, n: int) -> "MockWebSocket":
        """Configure to simulate disconnect after N messages."""
        self._simulate_disconnect_after = n
        return self


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "WebSocketFluxSink",
    "WebSocketLike",
    "MockWebSocket",
]
