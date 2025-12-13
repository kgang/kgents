"""
Dead Letter Queue for CDC events that fail processing.

Events that exceed max retry attempts are sent to the DLQ for:
1. Manual inspection and intervention
2. Later reprocessing after fixes
3. Metrics and alerting

Categorical Role: The DLQ is the terminal object for failed morphisms.
When Synapse(event) fails, the event lands here rather than being lost.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class DLQReason(Enum):
    """Reason for event landing in DLQ."""

    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    CIRCUIT_OPEN = "circuit_open"
    INVALID_PAYLOAD = "invalid_payload"
    EMBEDDING_FAILED = "embedding_failed"
    MANUAL_NACK = "manual_nack"


@dataclass(frozen=True)
class DeadLetterEvent:
    """
    Event that failed all retry attempts.

    Immutable record of what failed and why.
    """

    original_event_table: str
    original_event_operation: str
    original_event_row_id: str
    original_event_data: dict[str, Any]
    original_event_sequence_id: int | None
    target: str
    error: str
    reason: DLQReason
    failed_at: datetime
    retry_count: int

    @classmethod
    def from_event(
        cls,
        event: Any,  # ChangeEvent
        target: str,
        error: str,
        reason: DLQReason,
        retry_count: int,
    ) -> "DeadLetterEvent":
        """Create from a ChangeEvent."""
        return cls(
            original_event_table=event.table,
            original_event_operation=event.operation.value,
            original_event_row_id=event.row_id,
            original_event_data=dict(event.data),
            original_event_sequence_id=event.sequence_id,
            target=target,
            error=error,
            reason=reason,
            failed_at=datetime.now(timezone.utc),
            retry_count=retry_count,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage or API."""
        return {
            "table": self.original_event_table,
            "operation": self.original_event_operation,
            "row_id": self.original_event_row_id,
            "data": self.original_event_data,
            "sequence_id": self.original_event_sequence_id,
            "target": self.target,
            "error": self.error,
            "reason": self.reason.value,
            "failed_at": self.failed_at.isoformat(),
            "retry_count": self.retry_count,
        }


class DeadLetterQueue:
    """
    Stores events that failed processing.

    In-memory queue with configurable max size.
    Can be extended with persistence hooks for production use.

    The DLQ provides:
    1. Bounded storage (evicts oldest when full)
    2. Drain for reprocessing
    3. Persistence hook for external storage
    4. Metrics for monitoring
    """

    def __init__(
        self,
        max_size: int = 1000,
        persist_hook: Callable[[DeadLetterEvent], Any] | None = None,
    ) -> None:
        """
        Initialize the DLQ.

        Args:
            max_size: Maximum events to store (oldest evicted first)
            persist_hook: Optional async function to persist events externally
        """
        self._events: deque[DeadLetterEvent] = deque(maxlen=max_size)
        self._persist_hook = persist_hook
        self._total_enqueued: int = 0
        self._total_evicted: int = 0

    async def enqueue(self, event: DeadLetterEvent) -> None:
        """
        Add failed event to DLQ.

        If queue is full, oldest event is evicted.
        Calls persist hook if configured.
        """
        maxlen = self._events.maxlen or 0
        if len(self._events) >= maxlen > 0:
            self._total_evicted += 1

        self._events.append(event)
        self._total_enqueued += 1

        if self._persist_hook:
            await self._persist_hook(event)

    def enqueue_sync(self, event: DeadLetterEvent) -> None:
        """Synchronous enqueue (skips persist hook)."""
        maxlen = self._events.maxlen or 0
        if len(self._events) >= maxlen > 0:
            self._total_evicted += 1

        self._events.append(event)
        self._total_enqueued += 1

    def drain(self) -> list[DeadLetterEvent]:
        """
        Get all events for reprocessing.

        Clears the queue. Use for manual retry operations.
        """
        events = list(self._events)
        self._events.clear()
        return events

    def peek(self, n: int = 10) -> list[DeadLetterEvent]:
        """
        Peek at the first n events without removing.

        Useful for inspection and debugging.
        """
        return list(self._events)[:n]

    def peek_by_table(self, table: str) -> list[DeadLetterEvent]:
        """Get events for a specific table."""
        return [e for e in self._events if e.original_event_table == table]

    def peek_by_reason(self, reason: DLQReason) -> list[DeadLetterEvent]:
        """Get events with a specific failure reason."""
        return [e for e in self._events if e.reason == reason]

    def remove(self, event: DeadLetterEvent) -> bool:
        """
        Remove a specific event (after manual processing).

        Returns True if found and removed.
        """
        try:
            self._events.remove(event)
            return True
        except ValueError:
            return False

    def clear(self) -> int:
        """Clear all events. Returns count cleared."""
        count = len(self._events)
        self._events.clear()
        return count

    @property
    def size(self) -> int:
        """Current queue size."""
        return len(self._events)

    @property
    def is_empty(self) -> bool:
        """True if queue is empty."""
        return len(self._events) == 0

    @property
    def total_enqueued(self) -> int:
        """Total events ever enqueued."""
        return self._total_enqueued

    @property
    def total_evicted(self) -> int:
        """Total events evicted due to queue full."""
        return self._total_evicted

    def stats(self) -> dict[str, Any]:
        """Get DLQ statistics."""
        by_reason: dict[str, int] = {}
        by_table: dict[str, int] = {}

        for event in self._events:
            reason = event.reason.value
            by_reason[reason] = by_reason.get(reason, 0) + 1

            table = event.original_event_table
            by_table[table] = by_table.get(table, 0) + 1

        return {
            "size": self.size,
            "max_size": self._events.maxlen,
            "total_enqueued": self._total_enqueued,
            "total_evicted": self._total_evicted,
            "by_reason": by_reason,
            "by_table": by_table,
        }


# ===========================================================================
# Singleton instance for global access
# ===========================================================================

_global_dlq: DeadLetterQueue | None = None


def get_dlq(max_size: int = 1000) -> DeadLetterQueue:
    """Get or create the global DLQ instance."""
    global _global_dlq
    if _global_dlq is None:
        _global_dlq = DeadLetterQueue(max_size=max_size)
    return _global_dlq


def reset_dlq() -> None:
    """Reset global DLQ (for testing)."""
    global _global_dlq
    _global_dlq = None
