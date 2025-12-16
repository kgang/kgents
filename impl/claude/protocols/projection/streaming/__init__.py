"""
Streaming Infrastructure: State machine, backpressure, and retry.

Provides unified streaming support across surfaces:
- StreamState: Lifecycle state enum
- StreamContext: Unified stream context with state tracking
- BackpressurePolicy: Buffer management configuration
- RetryPolicy: Exponential backoff retry configuration
- stream_with_envelope: SSE generator with metadata

Usage:
    from protocols.projection.streaming import (
        StreamState,
        StreamContext,
        BackpressurePolicy,
        RetryPolicy,
        stream_with_envelope,
    )

    # Create stream context
    context = StreamContext(
        url="http://api/stream",
        backpressure=BackpressurePolicy(buffer_size=100),
        retry=RetryPolicy(max_retries=3),
    )

    # Use SSE generator
    async for chunk in stream_with_envelope(source_iterator):
        yield chunk
"""

from protocols.projection.streaming.backpressure import (
    BackpressurePolicy,
    BufferManager,
    DropEvent,
    DropPolicy,
)
from protocols.projection.streaming.retry import (
    AGGRESSIVE_RETRY,
    CONSERVATIVE_RETRY,
    NO_RETRY,
    RetryPolicy,
)
from protocols.projection.streaming.sse import (
    format_drop_event,
    format_refusal_event,
    stream_with_envelope,
    with_heartbeat,
)
from protocols.projection.streaming.state import StreamContext, StreamState

__all__ = [
    # State
    "StreamState",
    "StreamContext",
    # Backpressure
    "BackpressurePolicy",
    "BufferManager",
    "DropPolicy",
    "DropEvent",
    # Retry
    "RetryPolicy",
    "AGGRESSIVE_RETRY",
    "CONSERVATIVE_RETRY",
    "NO_RETRY",
    # SSE
    "stream_with_envelope",
    "format_drop_event",
    "format_refusal_event",
    "with_heartbeat",
]
