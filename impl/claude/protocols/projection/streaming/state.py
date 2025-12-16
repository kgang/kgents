"""
StreamState and StreamContext: Unified stream lifecycle management.

State machine:
    IDLE → CONNECTING → STREAMING → DONE
                      ↘ PAUSED ↗
                      ↘ ERROR (retry → CONNECTING)
                      ↘ REFUSED

Each state has specific meaning:
- IDLE: Initial state, no connection
- CONNECTING: Establishing connection
- STREAMING: Actively receiving data
- PAUSED: Temporarily paused by user
- DONE: Stream completed successfully
- ERROR: Technical failure (retryable)
- REFUSED: Agent refused (not retryable)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Generic, TypeVar

from protocols.projection.schema import ErrorInfo, RefusalInfo

T = TypeVar("T")


class StreamState(Enum):
    """Stream lifecycle states."""

    IDLE = auto()
    CONNECTING = auto()
    STREAMING = auto()
    PAUSED = auto()
    DONE = auto()
    ERROR = auto()
    REFUSED = auto()


# Valid state transitions
VALID_TRANSITIONS: dict[StreamState, set[StreamState]] = {
    StreamState.IDLE: {StreamState.CONNECTING},
    StreamState.CONNECTING: {
        StreamState.STREAMING,
        StreamState.ERROR,
        StreamState.REFUSED,
    },
    StreamState.STREAMING: {
        StreamState.PAUSED,
        StreamState.DONE,
        StreamState.ERROR,
        StreamState.REFUSED,
    },
    StreamState.PAUSED: {StreamState.STREAMING, StreamState.DONE},
    StreamState.DONE: {StreamState.IDLE},  # Can restart
    StreamState.ERROR: {StreamState.CONNECTING, StreamState.IDLE},  # Retry or reset
    StreamState.REFUSED: {StreamState.IDLE},  # Can only reset
}


@dataclass
class StreamStats:
    """Statistics for stream monitoring."""

    events_received: int = 0
    events_delivered: int = 0
    events_dropped: int = 0
    bytes_received: int = 0
    drop_reasons: dict[str, int] = field(default_factory=dict)


@dataclass
class StreamContext(Generic[T]):
    """
    Unified stream lifecycle context.

    Tracks state, manages transitions, handles backpressure.

    Attributes:
        state: Current lifecycle state
        url: Stream endpoint URL
        started_at: When streaming started
        last_event_at: When last event was received
        stats: Stream statistics
        error: Current error (if state == ERROR)
        refusal: Current refusal (if state == REFUSED)
        retry_count: Number of retry attempts
        max_retries: Maximum retry attempts
    """

    state: StreamState = StreamState.IDLE
    url: str = ""
    started_at: datetime | None = None
    last_event_at: datetime | None = None
    stats: StreamStats = field(default_factory=StreamStats)
    error: ErrorInfo | None = None
    refusal: RefusalInfo | None = None
    retry_count: int = 0
    max_retries: int = 5

    # Callbacks for state changes
    on_state_change: Callable[[StreamState, StreamState], None] | None = None
    on_event: Callable[[T], None] | None = None
    on_drop: Callable[[T, str], None] | None = None

    def can_transition_to(self, new_state: StreamState) -> bool:
        """Check if transition to new_state is valid."""
        return new_state in VALID_TRANSITIONS.get(self.state, set())

    def transition_to(self, new_state: StreamState) -> bool:
        """
        Attempt to transition to new_state.

        Returns True if transition succeeded, False otherwise.
        Calls on_state_change callback if transition succeeds.
        """
        if not self.can_transition_to(new_state):
            return False

        old_state = self.state
        self.state = new_state

        # Update timestamps
        if new_state == StreamState.STREAMING:
            if self.started_at is None:
                self.started_at = datetime.now()

        if new_state == StreamState.DONE:
            self.started_at = None

        if self.on_state_change:
            self.on_state_change(old_state, new_state)

        return True

    def connect(self) -> bool:
        """Start connection. Returns True if state changed."""
        return self.transition_to(StreamState.CONNECTING)

    def connected(self) -> bool:
        """Mark as connected/streaming. Returns True if state changed."""
        return self.transition_to(StreamState.STREAMING)

    def pause(self) -> bool:
        """Pause streaming. Returns True if state changed."""
        return self.transition_to(StreamState.PAUSED)

    def resume(self) -> bool:
        """Resume from paused. Returns True if state changed."""
        return self.transition_to(StreamState.STREAMING)

    def complete(self) -> bool:
        """Mark stream as complete. Returns True if state changed."""
        return self.transition_to(StreamState.DONE)

    def fail(self, error: ErrorInfo) -> bool:
        """Mark stream as failed. Returns True if state changed."""
        self.error = error
        return self.transition_to(StreamState.ERROR)

    def refuse(self, refusal: RefusalInfo) -> bool:
        """Mark stream as refused. Returns True if state changed."""
        self.refusal = refusal
        return self.transition_to(StreamState.REFUSED)

    def reset(self) -> bool:
        """Reset to idle. Returns True if state changed."""
        self.error = None
        self.refusal = None
        self.retry_count = 0
        self.stats = StreamStats()
        return self.transition_to(StreamState.IDLE)

    def retry(self) -> bool:
        """
        Attempt retry. Returns True if retry is allowed and state changed.

        Increments retry_count and transitions to CONNECTING.
        Returns False if max retries exceeded or not in ERROR state.
        """
        if self.state != StreamState.ERROR:
            return False

        if self.retry_count >= self.max_retries:
            return False

        self.retry_count += 1
        self.error = None
        return self.transition_to(StreamState.CONNECTING)

    def record_event(self, event: T, bytes_size: int = 0) -> None:
        """Record an incoming event."""
        self.stats.events_received += 1
        self.stats.events_delivered += 1
        self.stats.bytes_received += bytes_size
        self.last_event_at = datetime.now()

        if self.on_event:
            self.on_event(event)

    def record_drop(self, event: T, reason: str) -> None:
        """Record a dropped event."""
        self.stats.events_received += 1
        self.stats.events_dropped += 1
        self.stats.drop_reasons[reason] = self.stats.drop_reasons.get(reason, 0) + 1

        if self.on_drop:
            self.on_drop(event, reason)

    @property
    def is_active(self) -> bool:
        """Whether stream is actively receiving data."""
        return self.state == StreamState.STREAMING

    @property
    def is_terminal(self) -> bool:
        """Whether stream is in a terminal state (DONE, ERROR, REFUSED)."""
        return self.state in (StreamState.DONE, StreamState.ERROR, StreamState.REFUSED)

    @property
    def can_retry(self) -> bool:
        """Whether retry is possible."""
        return (
            self.state == StreamState.ERROR
            and self.retry_count < self.max_retries
            and self.error is not None
            and self.error.is_retryable
        )

    @property
    def buffer_fill_ratio(self) -> float:
        """Ratio of events dropped vs delivered (inverse health metric)."""
        total = self.stats.events_delivered + self.stats.events_dropped
        if total == 0:
            return 0.0
        return self.stats.events_dropped / total


__all__ = [
    "StreamState",
    "StreamContext",
    "StreamStats",
    "VALID_TRANSITIONS",
]
