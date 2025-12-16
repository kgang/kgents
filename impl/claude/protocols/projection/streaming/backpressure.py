"""
Backpressure: Buffer management and drop policies.

Handles backpressure when consumers are slow:
- Bounded buffer with configurable size
- High watermark alerts
- Multiple drop policies (oldest, newest, random)
- Drop visibility via DropEvent

Example:
    policy = BackpressurePolicy(
        buffer_size=100,
        high_watermark=0.8,
        drop_policy=DropPolicy.DROP_OLDEST,
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class DropPolicy(Enum):
    """Policy for dropping events when buffer is full."""

    DROP_OLDEST = auto()  # Drop from head (oldest events)
    DROP_NEWEST = auto()  # Drop incoming (newest events)
    DROP_RANDOM = auto()  # Random sample (preserve distribution)
    BLOCK = auto()  # Block producer (true backpressure)


@dataclass(frozen=True)
class DropEvent:
    """
    Notification that events were dropped.

    Sent to consumers for visibility into backpressure drops.
    """

    count: int
    oldest_timestamp: datetime
    newest_timestamp: datetime
    reason: str  # "buffer_full", "consumer_slow", "rate_limit"
    dropped_sample: tuple[Any, ...] = ()  # First few dropped items

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": "drop_event",
            "count": self.count,
            "oldestTimestamp": self.oldest_timestamp.isoformat(),
            "newestTimestamp": self.newest_timestamp.isoformat(),
            "reason": self.reason,
            "droppedSampleCount": len(self.dropped_sample),
        }


@dataclass
class BackpressurePolicy:
    """
    Configuration for buffer backpressure handling.

    Attributes:
        buffer_size: Maximum buffer size
        high_watermark: Alert threshold (0.0-1.0)
        critical_watermark: Drop threshold (0.0-1.0)
        drop_policy: What to drop when full
        emit_drop_events: Send DropEvent to consumer
        drop_batch_threshold: Emit after N drops
    """

    buffer_size: int = 1000
    high_watermark: float = 0.8  # 80%
    critical_watermark: float = 0.95  # 95%
    drop_policy: DropPolicy = DropPolicy.DROP_OLDEST
    emit_drop_events: bool = True
    drop_batch_threshold: int = 10  # Emit after N drops


@dataclass
class BufferManager(Generic[T]):
    """
    Manages a bounded buffer with backpressure.

    Handles buffering, drops, and notifications according to policy.
    """

    policy: BackpressurePolicy
    buffer: list[tuple[datetime, T]] = field(default_factory=list)

    # Drop tracking
    pending_drop_count: int = 0
    oldest_drop: datetime | None = None
    newest_drop: datetime | None = None
    dropped_samples: list[T] = field(default_factory=list)

    def push(self, item: T) -> DropEvent | None:
        """
        Push item to buffer.

        Returns DropEvent if drops occurred and threshold reached.
        """
        now = datetime.now()
        current_fill = len(self.buffer) / self.policy.buffer_size

        # Check if we need to drop
        if current_fill >= self.policy.critical_watermark:
            return self._handle_drop(item, now)

        # Add to buffer
        self.buffer.append((now, item))
        return self._maybe_emit_drop_event()

    def pop(self) -> T | None:
        """Pop oldest item from buffer, or None if empty."""
        if not self.buffer:
            return None
        _, item = self.buffer.pop(0)
        return item

    def _handle_drop(self, item: T, timestamp: datetime) -> DropEvent | None:
        """Handle dropping an item according to policy."""
        match self.policy.drop_policy:
            case DropPolicy.DROP_OLDEST:
                # Drop oldest from buffer
                if self.buffer:
                    dropped_time, dropped_item = self.buffer.pop(0)
                    self._record_drop(dropped_item, dropped_time)
                # Add new item
                self.buffer.append((timestamp, item))

            case DropPolicy.DROP_NEWEST:
                # Drop the incoming item
                self._record_drop(item, timestamp)

            case DropPolicy.DROP_RANDOM:
                # Drop random item from buffer
                import random

                if self.buffer:
                    idx = random.randint(0, len(self.buffer) - 1)
                    dropped_time, dropped_item = self.buffer.pop(idx)
                    self._record_drop(dropped_item, dropped_time)
                # Add new item
                self.buffer.append((timestamp, item))

            case DropPolicy.BLOCK:
                # Block - don't add, wait for space
                # In async context, this should await
                self._record_drop(item, timestamp)

        return self._maybe_emit_drop_event()

    def _record_drop(self, item: T, timestamp: datetime) -> None:
        """Record a dropped item."""
        self.pending_drop_count += 1

        if self.oldest_drop is None:
            self.oldest_drop = timestamp
        self.newest_drop = timestamp

        # Keep sample of dropped items (first 3)
        if len(self.dropped_samples) < 3:
            self.dropped_samples.append(item)

    def _maybe_emit_drop_event(self) -> DropEvent | None:
        """Emit DropEvent if threshold reached."""
        if not self.policy.emit_drop_events:
            return None

        if self.pending_drop_count < self.policy.drop_batch_threshold:
            return None

        if self.oldest_drop is None or self.newest_drop is None:
            return None

        event = DropEvent(
            count=self.pending_drop_count,
            oldest_timestamp=self.oldest_drop,
            newest_timestamp=self.newest_drop,
            reason="buffer_full",
            dropped_sample=tuple(self.dropped_samples),
        )

        # Reset tracking
        self.pending_drop_count = 0
        self.oldest_drop = None
        self.newest_drop = None
        self.dropped_samples = []

        return event

    @property
    def fill_ratio(self) -> float:
        """Current buffer fill ratio (0.0-1.0)."""
        return len(self.buffer) / self.policy.buffer_size

    @property
    def is_at_high_watermark(self) -> bool:
        """Whether buffer is at high watermark."""
        return self.fill_ratio >= self.policy.high_watermark

    @property
    def is_at_critical(self) -> bool:
        """Whether buffer is at critical level."""
        return self.fill_ratio >= self.policy.critical_watermark

    @property
    def size(self) -> int:
        """Current buffer size."""
        return len(self.buffer)


__all__ = [
    "BackpressurePolicy",
    "DropPolicy",
    "DropEvent",
    "BufferManager",
]
