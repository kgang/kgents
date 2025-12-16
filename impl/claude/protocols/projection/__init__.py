"""
Projection Component Library: Unified widget rendering across surfaces.

This module provides the shared vocabulary and infrastructure for rendering
AGENTESE responses consistently across CLI (Textual TUI), Web (React), and
marimo surfaces.

Architecture:
    AGENTESE Response → WidgetEnvelope[T] → Surface-specific projection

The key types are:
    - WidgetEnvelope: Wraps data with metadata (status, cache, errors)
    - WidgetMeta: Status chrome (loading, error, refusal, cache badge)
    - Widget states: Text, Select, Table, Graph, Stream, etc.

Usage:
    from protocols.projection import WidgetEnvelope, WidgetMeta, WidgetStatus

    # Wrap data with metadata
    envelope = WidgetEnvelope(
        data={"name": "Alice", "score": 42},
        meta=WidgetMeta.done(),
        source_path="world.town.manifest",
    )

    # Check status
    if envelope.meta.show_cached_badge:
        print("[CACHED]")

See: spec/protocols/projection.md
"""

# Chrome components
from protocols.projection.chrome import (
    CachedBadge,
    ErrorPanel,
    RefusalPanel,
)
from protocols.projection.schema import (
    CacheMeta,
    ErrorCategory,
    ErrorInfo,
    RefusalInfo,
    StreamMeta,
    UIHint,
    WidgetEnvelope,
    WidgetMeta,
    WidgetStatus,
)

# Streaming infrastructure
from protocols.projection.streaming import (
    AGGRESSIVE_RETRY,
    CONSERVATIVE_RETRY,
    NO_RETRY,
    BackpressurePolicy,
    BufferManager,
    DropPolicy,
    RetryPolicy,
    StreamContext,
    StreamState,
    format_drop_event,
    format_refusal_event,
    stream_with_envelope,
    with_heartbeat,
)

# Widget states
from protocols.projection.widgets import (
    ConfirmWidgetState,
    GraphWidgetState,
    ProgressWidgetState,
    SelectWidgetState,
    StreamWidgetState,
    TableWidgetState,
    TextWidgetState,
)

__all__ = [
    # Status
    "WidgetStatus",
    # Metadata types
    "CacheMeta",
    "ErrorInfo",
    "ErrorCategory",
    "RefusalInfo",
    "StreamMeta",
    "UIHint",
    "WidgetMeta",
    # Envelope
    "WidgetEnvelope",
    # Widget states
    "TextWidgetState",
    "SelectWidgetState",
    "ConfirmWidgetState",
    "ProgressWidgetState",
    "TableWidgetState",
    "GraphWidgetState",
    "StreamWidgetState",
    # Chrome
    "ErrorPanel",
    "RefusalPanel",
    "CachedBadge",
    # Streaming
    "StreamState",
    "StreamContext",
    "BackpressurePolicy",
    "DropPolicy",
    "BufferManager",
    "RetryPolicy",
    "AGGRESSIVE_RETRY",
    "CONSERVATIVE_RETRY",
    "NO_RETRY",
    "stream_with_envelope",
    "format_drop_event",
    "format_refusal_event",
    "with_heartbeat",
]
