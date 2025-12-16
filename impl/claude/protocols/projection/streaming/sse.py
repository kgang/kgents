"""
SSE Generator: Server-Sent Events with envelope wrapping.

Wraps async iterators in SSE format with:
- WidgetEnvelope metadata
- Heartbeat events
- Completion and error events
- Drop notifications

Example:
    async def source():
        for i in range(10):
            yield {"value": i}
            await asyncio.sleep(0.1)

    async for chunk in stream_with_envelope(source()):
        # chunk is SSE-formatted string like:
        # event: data
        # data: {"data": {"value": 0}, "meta": {...}}
        yield chunk
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, AsyncIterator, TypeVar

from protocols.projection.schema import WidgetMeta, WidgetStatus
from protocols.projection.streaming.backpressure import DropEvent

T = TypeVar("T")


async def stream_with_envelope(
    source: AsyncIterator[T],
    heartbeat_interval: float = 30.0,
    include_timestamps: bool = True,
) -> AsyncIterator[str]:
    """
    Wrap async iterator in SSE format with envelope metadata.

    Generates SSE-formatted strings with:
    - data events: Actual data with envelope
    - heartbeat events: Keep-alive every N seconds
    - complete event: Stream finished
    - error event: Stream failed

    Args:
        source: Async iterator producing data items
        heartbeat_interval: Seconds between heartbeat events
        include_timestamps: Include timestamps in envelope

    Yields:
        SSE-formatted strings (event: type\\ndata: json\\n\\n)
    """
    started_at = time.time()
    received_count = 0
    last_heartbeat = time.time()

    def make_envelope(data: T, status: WidgetStatus = WidgetStatus.STREAMING) -> str:
        """Create envelope JSON."""
        envelope: dict[str, Any] = {
            "data": data,
            "meta": {
                "status": status.name.lower(),
                "stream": {
                    "received": received_count,
                    "totalExpected": None,
                },
            },
        }
        if include_timestamps:
            envelope["meta"]["stream"]["startedAt"] = started_at
            envelope["meta"]["stream"]["lastChunkAt"] = time.time()
        return json.dumps(envelope)

    try:
        async for item in source:
            received_count += 1

            # Emit data event
            yield f"event: data\ndata: {make_envelope(item)}\n\n"

            # Check for heartbeat
            now = time.time()
            if now - last_heartbeat >= heartbeat_interval:
                yield f"event: heartbeat\ndata: {json.dumps({'received': received_count})}\n\n"
                last_heartbeat = now

        # Stream complete
        complete_stream: dict[str, Any] = {
            "received": received_count,
            "totalExpected": received_count,
        }
        if include_timestamps:
            complete_stream["startedAt"] = started_at
            complete_stream["completedAt"] = time.time()

        complete_envelope: dict[str, Any] = {
            "meta": {
                "status": "done",
                "stream": complete_stream,
            },
        }

        yield f"event: complete\ndata: {json.dumps(complete_envelope)}\n\n"

    except Exception as e:
        # Stream error
        error_envelope = {
            "meta": {
                "status": "error",
                "error": {
                    "category": "unknown",
                    "code": type(e).__name__,
                    "message": str(e),
                    "retryAfterSeconds": 5,
                },
            },
        }
        yield f"event: error\ndata: {json.dumps(error_envelope)}\n\n"


def format_drop_event(drop: DropEvent) -> str:
    """Format DropEvent as SSE string."""
    return f"event: stream.dropped\ndata: {json.dumps(drop.to_dict())}\n\n"


def format_refusal_event(reason: str, consent_required: str | None = None) -> str:
    """Format refusal as SSE string."""
    refusal_envelope = {
        "meta": {
            "status": "refusal",
            "refusal": {
                "reason": reason,
                "consentRequired": consent_required,
            },
        },
    }
    return f"event: refusal\ndata: {json.dumps(refusal_envelope)}\n\n"


async def with_heartbeat(
    source: AsyncIterator[str],
    interval: float = 30.0,
) -> AsyncIterator[str]:
    """
    Add periodic heartbeat events to an SSE stream.

    Args:
        source: SSE stream to wrap
        interval: Seconds between heartbeats

    Yields:
        Original events plus heartbeat events
    """
    last_heartbeat = time.time()

    async for event in source:
        yield event

        now = time.time()
        if now - last_heartbeat >= interval:
            yield f"event: heartbeat\ndata: {json.dumps({'timestamp': now})}\n\n"
            last_heartbeat = now


__all__ = [
    "stream_with_envelope",
    "format_drop_event",
    "format_refusal_event",
    "with_heartbeat",
]
