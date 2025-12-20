"""
Projection Schema: Core types for unified widget rendering.

This module defines the shared vocabulary for projecting AGENTESE responses
across CLI, Web, and marimo surfaces. The schema captures:

1. Widget lifecycle states (loading, streaming, done, error, refusal)
2. Cache/determinism metadata for v3 AGENTESE hints
3. Error and refusal information with dedicated structures
4. Streaming metadata for progress tracking
5. WidgetEnvelope for wrapping any data with projection metadata

Design Principles:
    - All types are frozen dataclasses (immutable)
    - Status states are explicit enums (no stringly-typed flags)
    - Error vs Refusal are distinct (semantic difference)
    - Cache badge is prominent when data is stale

See: spec/protocols/projection.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Generic, Literal, TypeVar

T = TypeVar("T")


# =============================================================================
# Widget Status
# =============================================================================


class WidgetStatus(Enum):
    """
    Universal widget lifecycle states.

    These states drive rendering decisions across all surfaces:
    - IDLE: Initial state, no data loaded
    - LOADING: Fetching data (show spinner)
    - STREAMING: Receiving incremental data (show progress)
    - DONE: Successfully completed (show content)
    - ERROR: Technical failure (show error panel with retry)
    - REFUSAL: Semantic refusal by agent (show refusal panel)
    - STALE: Cached data that may be outdated (show [CACHED] badge)
    """

    IDLE = auto()
    LOADING = auto()
    STREAMING = auto()
    DONE = auto()
    ERROR = auto()
    REFUSAL = auto()
    STALE = auto()


# =============================================================================
# Cache Metadata
# =============================================================================


@dataclass(frozen=True)
class CacheMeta:
    """
    Cache and determinism metadata from AGENTESE v3 hints.

    Attributes:
        is_cached: Whether this response was served from cache
        cached_at: When the response was cached (ISO timestamp)
        ttl_seconds: Time-to-live for cache entry
        cache_key: Unique key for this cached response
        deterministic: Whether the result is deterministic (same input → same output)
    """

    is_cached: bool = False
    cached_at: datetime | None = None
    ttl_seconds: int | None = None
    cache_key: str | None = None
    deterministic: bool = True

    @property
    def is_stale(self) -> bool:
        """Check if cache is stale based on TTL."""
        if not self.is_cached or self.cached_at is None or self.ttl_seconds is None:
            return False
        # For accurate comparison, use timezone-aware datetimes when available.
        # If cached_at is naive, use naive now() to compare in same "space".
        # If cached_at is aware, use aware now(utc) for correct comparison.
        if self.cached_at.tzinfo is not None:
            now = datetime.now(timezone.utc)
            # Convert to UTC for comparison
            cached_at_utc = self.cached_at.astimezone(timezone.utc)
            elapsed = (now - cached_at_utc).total_seconds()
        else:
            # Both naive - compare directly
            now = datetime.now()
            elapsed = (now - self.cached_at).total_seconds()
        return elapsed > self.ttl_seconds

    @property
    def age_seconds(self) -> float | None:
        """Get cache age in seconds, or None if not cached."""
        if not self.is_cached or self.cached_at is None:
            return None
        # For accurate comparison, use timezone-aware datetimes when available.
        # If cached_at is naive, use naive now() to compare in same "space".
        # If cached_at is aware, use aware now(utc) for correct comparison.
        if self.cached_at.tzinfo is not None:
            now = datetime.now(timezone.utc)
            # Convert to UTC for comparison
            cached_at_utc = self.cached_at.astimezone(timezone.utc)
            return (now - cached_at_utc).total_seconds()
        else:
            # Both naive - compare directly
            now = datetime.now()
            return (now - self.cached_at).total_seconds()


# =============================================================================
# Error Information
# =============================================================================

ErrorCategory = Literal["network", "notFound", "permission", "timeout", "validation", "unknown"]


@dataclass(frozen=True)
class ErrorInfo:
    """
    Structured error information for technical failures.

    This is distinct from RefusalInfo - errors are technical failures,
    refusals are semantic decisions by the agent.

    Attributes:
        category: Type of error for icon/styling selection
        code: Machine-readable error code (e.g., "ECONNREFUSED")
        message: Human-readable error message
        retry_after_seconds: Suggested retry delay (for rate limiting)
        fallback_action: Suggested fallback action (e.g., "use offline mode")
        trace_id: OTEL trace ID for debugging
    """

    category: ErrorCategory
    code: str
    message: str
    retry_after_seconds: int | None = None
    fallback_action: str | None = None
    trace_id: str | None = None

    @property
    def is_retryable(self) -> bool:
        """Whether this error is likely transient and retryable."""
        return self.category in ("network", "timeout")


# =============================================================================
# Refusal Information
# =============================================================================


@dataclass(frozen=True)
class RefusalInfo:
    """
    Information about an agent refusal.

    Refusals are semantic decisions by the agent to not perform an action.
    They are distinct from errors - the system worked correctly, but the
    agent chose not to comply.

    Attributes:
        reason: Human-readable explanation of why the action was refused
        consent_required: What consent is needed to proceed (if any)
        appeal_to: AGENTESE path for appealing the decision (e.g., "self.soul.appeal")
        override_cost: Token/credit cost to override the refusal (if available)
    """

    reason: str
    consent_required: str | None = None
    appeal_to: str | None = None
    override_cost: float | None = None


# =============================================================================
# Stream Metadata
# =============================================================================


@dataclass(frozen=True)
class StreamMeta:
    """
    Metadata for streaming responses.

    Tracks progress of incremental data delivery.

    Attributes:
        total_expected: Expected total items/bytes (None if unknown)
        received: Items/bytes received so far
        started_at: When streaming started
        last_chunk_at: When last chunk was received
    """

    total_expected: int | None = None
    received: int = 0
    started_at: datetime | None = None
    last_chunk_at: datetime | None = None

    @property
    def progress(self) -> float:
        """
        Progress as 0.0-1.0, or -1 if indeterminate.

        Returns -1 when total_expected is unknown, indicating
        that progress bar should show indeterminate state.
        """
        if self.total_expected is None or self.total_expected == 0:
            return -1.0  # Indeterminate
        return min(1.0, self.received / self.total_expected)

    @property
    def is_indeterminate(self) -> bool:
        """Whether progress is indeterminate (unknown total)."""
        return self.total_expected is None

    def with_received(self, received: int) -> StreamMeta:
        """Return new StreamMeta with updated received count."""
        return StreamMeta(
            total_expected=self.total_expected,
            received=received,
            started_at=self.started_at,
            last_chunk_at=datetime.now(timezone.utc),
        )


# =============================================================================
# UI Hints
# =============================================================================

UIHint = Literal["form", "stream", "table", "graph", "card", "text"]


# =============================================================================
# Widget Metadata
# =============================================================================


@dataclass(frozen=True)
class WidgetMeta:
    """
    Universal metadata for all projected widgets.

    Captures status, cache info, errors, refusals, and streaming state.
    This is the "chrome" around widget content.

    Attributes:
        status: Current lifecycle state
        cache: Cache/determinism metadata (if applicable)
        error: Error information (if status == ERROR)
        refusal: Refusal information (if status == REFUSAL)
        stream: Streaming metadata (if status == STREAMING)
        ui_hint: AGENTESE v3 projection hint for widget type selection
    """

    status: WidgetStatus = WidgetStatus.IDLE
    cache: CacheMeta | None = None
    error: ErrorInfo | None = None
    refusal: RefusalInfo | None = None
    stream: StreamMeta | None = None
    ui_hint: UIHint | None = None

    @property
    def is_loading(self) -> bool:
        """Whether widget is in a loading state."""
        return self.status in (WidgetStatus.LOADING, WidgetStatus.STREAMING)

    @property
    def is_cached(self) -> bool:
        """Whether response is from cache."""
        return self.cache is not None and self.cache.is_cached

    @property
    def show_cached_badge(self) -> bool:
        """
        Whether to show prominent [CACHED] badge.

        Shows badge when data is cached AND stale (past TTL).
        Fresh cached data doesn't need a badge.
        """
        if self.cache is None or not self.cache.is_cached:
            return False
        return self.cache.is_stale

    @property
    def has_error(self) -> bool:
        """Whether there's an error to display."""
        return self.status == WidgetStatus.ERROR and self.error is not None

    @property
    def has_refusal(self) -> bool:
        """Whether there's a refusal to display."""
        return self.status == WidgetStatus.REFUSAL and self.refusal is not None

    # Factory methods for common states
    @classmethod
    def idle(cls) -> WidgetMeta:
        """Create idle state."""
        return cls(status=WidgetStatus.IDLE)

    @classmethod
    def loading(cls) -> WidgetMeta:
        """Create loading state."""
        return cls(status=WidgetStatus.LOADING)

    @classmethod
    def streaming(cls, stream: StreamMeta | None = None) -> WidgetMeta:
        """Create streaming state."""
        return cls(status=WidgetStatus.STREAMING, stream=stream)

    @classmethod
    def done(cls, cache: CacheMeta | None = None) -> WidgetMeta:
        """Create done state, optionally with cache info."""
        status = WidgetStatus.STALE if (cache and cache.is_stale) else WidgetStatus.DONE
        return cls(status=status, cache=cache)

    @classmethod
    def with_error(cls, error: ErrorInfo) -> WidgetMeta:
        """Create error state."""
        return cls(status=WidgetStatus.ERROR, error=error)

    @classmethod
    def with_refusal(cls, refusal: RefusalInfo) -> WidgetMeta:
        """Create refusal state."""
        return cls(status=WidgetStatus.REFUSAL, refusal=refusal)


# =============================================================================
# Widget Envelope
# =============================================================================


@dataclass(frozen=True)
class WidgetEnvelope(Generic[T]):
    """
    Universal envelope wrapping any widget data with metadata.

    This is the standard format for all projections. It separates
    the data (T) from the metadata (WidgetMeta), allowing surfaces
    to render appropriate chrome (error panels, cache badges, etc.)
    while the data renderer handles the actual content.

    Attributes:
        data: The actual widget data/content
        meta: Metadata about status, cache, errors, etc.
        source_path: AGENTESE path that produced this (for debugging)
        observer_archetype: Who observed this (for debugging)
    """

    data: T
    meta: WidgetMeta = field(default_factory=WidgetMeta)
    source_path: str | None = None
    observer_archetype: str | None = None

    def with_meta(self, meta: WidgetMeta) -> WidgetEnvelope[T]:
        """Return new envelope with updated meta."""
        return WidgetEnvelope(
            data=self.data,
            meta=meta,
            source_path=self.source_path,
            observer_archetype=self.observer_archetype,
        )

    def with_status(self, status: WidgetStatus) -> WidgetEnvelope[T]:
        """Return new envelope with updated status."""
        new_meta = WidgetMeta(
            status=status,
            cache=self.meta.cache,
            error=self.meta.error,
            refusal=self.meta.refusal,
            stream=self.meta.stream,
            ui_hint=self.meta.ui_hint,
        )
        return self.with_meta(new_meta)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to JSON-serializable dict.

        Used for API responses and TypeScript interop.
        """
        result: dict[str, Any] = {
            "data": self.data,
            "meta": {
                "status": self.meta.status.name.lower(),
                "uiHint": self.meta.ui_hint,
            },
        }

        if self.meta.cache is not None:
            result["meta"]["cache"] = {
                "isCached": self.meta.cache.is_cached,
                "cachedAt": (
                    self.meta.cache.cached_at.isoformat() if self.meta.cache.cached_at else None
                ),
                "ttlSeconds": self.meta.cache.ttl_seconds,
                "cacheKey": self.meta.cache.cache_key,
                "deterministic": self.meta.cache.deterministic,
            }

        if self.meta.error is not None:
            result["meta"]["error"] = {
                "category": self.meta.error.category,
                "code": self.meta.error.code,
                "message": self.meta.error.message,
                "retryAfterSeconds": self.meta.error.retry_after_seconds,
                "fallbackAction": self.meta.error.fallback_action,
                "traceId": self.meta.error.trace_id,
            }

        if self.meta.refusal is not None:
            result["meta"]["refusal"] = {
                "reason": self.meta.refusal.reason,
                "consentRequired": self.meta.refusal.consent_required,
                "appealTo": self.meta.refusal.appeal_to,
                "overrideCost": self.meta.refusal.override_cost,
            }

        if self.meta.stream is not None:
            result["meta"]["stream"] = {
                "totalExpected": self.meta.stream.total_expected,
                "received": self.meta.stream.received,
                "startedAt": (
                    self.meta.stream.started_at.isoformat() if self.meta.stream.started_at else None
                ),
                "lastChunkAt": (
                    self.meta.stream.last_chunk_at.isoformat()
                    if self.meta.stream.last_chunk_at
                    else None
                ),
            }

        if self.source_path is not None:
            result["sourcePath"] = self.source_path

        if self.observer_archetype is not None:
            result["observerArchetype"] = self.observer_archetype

        return result


# =============================================================================
# Exports
# =============================================================================

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
]
