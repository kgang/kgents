"""
Outbox Source: Polls Postgres outbox table for CDC events.

This source implements the polling side of the Transactional Outbox Pattern:
1. Poll outbox table for unprocessed events
2. Yield ChangeEvents to the Synapse
3. Mark events as processed after successful sync

Categorical Role: The OutboxSource is the observable interface that makes
the CDC Functor's state visible to the Synapse.

Note: While this is polling-based (not event-driven), it's necessary because:
- Postgres doesn't push events natively (would need LISTEN/NOTIFY or WAL tailing)
- Outbox polling is simpler and more portable
- The batch-and-mark pattern ensures exactly-once delivery semantics

For truly event-driven CDC, consider:
- LISTEN/NOTIFY with pg_notify()
- Logical replication decoding (WAL tailing)
- Debezium or similar CDC platforms
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, runtime_checkable

from agents.flux.synapse import ChangeEvent, ChangeOperation

from .base import Source

# ===========================================================================
# Database Protocol
# ===========================================================================


@runtime_checkable
class AsyncDatabaseConnection(Protocol):
    """
    Protocol for async database connections.

    Implementations should provide async query execution.
    Compatible with asyncpg, aiopg, psycopg (async mode), etc.
    """

    async def fetch(self, query: str, *args: Any) -> list[dict[str, Any]]:
        """Execute query and return all rows."""
        ...

    async def execute(self, query: str, *args: Any) -> None:
        """Execute query without returning rows."""
        ...


@runtime_checkable
class AsyncConnectionPool(Protocol):
    """
    Protocol for async connection pools.

    Allows acquiring connections from a pool.
    """

    async def acquire(self) -> AsyncDatabaseConnection:
        """Acquire a connection from the pool."""
        ...

    async def release(self, conn: AsyncDatabaseConnection) -> None:
        """Release a connection back to the pool."""
        ...


# ===========================================================================
# Outbox Configuration
# ===========================================================================


@dataclass(frozen=True)
class OutboxConfig:
    """
    Configuration for the OutboxSource.

    Attributes:
        poll_interval_ms: How often to poll for new events (default 100ms)
        batch_size: Maximum events to fetch per poll (default 100)
        mark_processed: Whether to mark events as processed (default True)
        empty_poll_backoff_ms: Backoff time when no events found (default 500ms)
        max_backoff_ms: Maximum backoff time (default 5000ms)
    """

    poll_interval_ms: int = 100
    batch_size: int = 100
    mark_processed: bool = True
    empty_poll_backoff_ms: int = 500
    max_backoff_ms: int = 5000


# ===========================================================================
# Mock Connection for Testing
# ===========================================================================


@dataclass
class MockConnection:
    """
    Mock database connection for testing without a real database.

    Pre-load events to return, or configure to return empty results.
    """

    pending_events: list[dict[str, Any]] = field(default_factory=list)
    processed_ids: list[int] = field(default_factory=list)
    fetch_calls: list[tuple[str, tuple[Any, ...]]] = field(default_factory=list)
    execute_calls: list[tuple[str, tuple[Any, ...]]] = field(default_factory=list)

    async def fetch(self, query: str, *args: Any) -> list[dict[str, Any]]:
        """Return pre-configured events."""
        self.fetch_calls.append((query, args))

        if not self.pending_events:
            return []

        # Return up to batch_size events
        batch_size = args[0] if args else 100
        batch = self.pending_events[:batch_size]
        self.pending_events = self.pending_events[batch_size:]
        return batch

    async def execute(self, query: str, *args: Any) -> None:
        """Record the execute call."""
        self.execute_calls.append((query, args))

        # Track processed IDs
        if "processed" in query.lower() and args:
            self.processed_ids.extend(args)


class MockConnectionPool:
    """Mock connection pool that returns a MockConnection."""

    def __init__(self, connection: MockConnection | None = None) -> None:
        self._connection = connection or MockConnection()

    async def acquire(self) -> MockConnection:
        """Return the mock connection."""
        return self._connection

    async def release(self, conn: AsyncDatabaseConnection | MockConnection) -> None:
        """No-op for mock."""
        pass


# ===========================================================================
# Outbox Source
# ===========================================================================


class OutboxSource(Source[ChangeEvent]):
    """
    Source that polls the Postgres outbox table for CDC events.

    Converts outbox rows into ChangeEvents for the Synapse.

    Usage (with real database):
        >>> pool = await asyncpg.create_pool(dsn)
        >>> source = OutboxSource(pool)
        >>> async for event in source:
        ...     # Process event with Synapse
        ...     await source.acknowledge(event.sequence_id)

    Usage (mock for testing):
        >>> mock_conn = MockConnection(pending_events=[...])
        >>> pool = MockConnectionPool(mock_conn)
        >>> source = OutboxSource(pool)

    Categorical Guarantee:
        Each ChangeEvent maps to exactly one outbox row.
        Acknowledging an event marks it as processed.
        The Synapse should acknowledge after successful sync.
    """

    def __init__(
        self,
        pool: AsyncConnectionPool | MockConnectionPool,
        config: OutboxConfig | None = None,
    ) -> None:
        """
        Initialize the OutboxSource.

        Args:
            pool: Database connection pool
            config: Optional configuration
        """
        self._pool = pool
        self._config = config or OutboxConfig()
        self._current_batch: list[ChangeEvent] = []
        self._batch_index = 0
        self._stopped = False
        self._consecutive_empty = 0
        self._current_backoff = self._config.poll_interval_ms

    async def __anext__(self) -> ChangeEvent:
        """
        Get the next ChangeEvent from the outbox.

        Polls the database in batches for efficiency.
        """
        if self._stopped:
            raise StopAsyncIteration

        # If current batch is exhausted, fetch more
        while self._batch_index >= len(self._current_batch):
            self._current_batch = await self._fetch_batch()
            self._batch_index = 0

            if not self._current_batch:
                # No events - apply backoff
                self._consecutive_empty += 1
                self._current_backoff = min(
                    self._config.empty_poll_backoff_ms * self._consecutive_empty,
                    self._config.max_backoff_ms,
                )
                await asyncio.sleep(self._current_backoff / 1000)
            else:
                # Found events - reset backoff
                self._consecutive_empty = 0
                self._current_backoff = self._config.poll_interval_ms

        # Return next event from batch
        event = self._current_batch[self._batch_index]
        self._batch_index += 1
        return event

    async def _fetch_batch(self) -> list[ChangeEvent]:
        """
        Fetch a batch of unprocessed events from the outbox.

        Returns:
            List of ChangeEvents (may be empty)
        """
        conn = await self._pool.acquire()
        try:
            rows = await conn.fetch(
                """
                SELECT id, event_type, table_name, row_id, payload, created_at
                FROM outbox
                WHERE NOT processed
                ORDER BY id
                LIMIT $1
                """,
                self._config.batch_size,
            )

            return [self._row_to_event(row) for row in rows]
        finally:
            await self._pool.release(conn)

    def _row_to_event(self, row: dict[str, Any]) -> ChangeEvent:
        """
        Convert an outbox row to a ChangeEvent.

        Args:
            row: Database row dict

        Returns:
            ChangeEvent with all fields populated
        """
        operation = ChangeOperation(row["event_type"])

        # Extract timestamp
        created_at = row.get("created_at")
        if created_at is not None:
            # Convert to milliseconds since epoch
            timestamp_ms = int(created_at.timestamp() * 1000)
        else:
            timestamp_ms = int(time.time() * 1000)

        # Payload might be a dict or a JSON string depending on driver
        payload = row["payload"]
        if isinstance(payload, str):
            import json

            payload = json.loads(payload)

        return ChangeEvent(
            table=row["table_name"],
            operation=operation,
            row_id=row["row_id"],
            data=payload,
            timestamp_ms=timestamp_ms,
            sequence_id=row["id"],
        )

    async def acknowledge(self, sequence_id: int | None) -> None:
        """
        Mark an event as processed.

        Should be called after the Synapse successfully syncs an event.
        This completes the exactly-once delivery guarantee.

        Args:
            sequence_id: The outbox row ID to mark as processed
        """
        if sequence_id is None or not self._config.mark_processed:
            return

        conn = await self._pool.acquire()
        try:
            await conn.execute(
                """
                UPDATE outbox
                SET processed = TRUE, processed_at = NOW()
                WHERE id = $1
                """,
                sequence_id,
            )
        finally:
            await self._pool.release(conn)

    async def acknowledge_batch(self, sequence_ids: list[int]) -> None:
        """
        Mark multiple events as processed.

        More efficient than individual acknowledges.

        Args:
            sequence_ids: List of outbox row IDs to mark as processed
        """
        if not sequence_ids or not self._config.mark_processed:
            return

        conn = await self._pool.acquire()
        try:
            await conn.execute(
                """
                UPDATE outbox
                SET processed = TRUE, processed_at = NOW()
                WHERE id = ANY($1)
                """,
                sequence_ids,
            )
        finally:
            await self._pool.release(conn)

    def close(self) -> None:
        """Stop polling the outbox."""
        self._stopped = True

    @property
    def is_stopped(self) -> bool:
        """True if the source has been stopped."""
        return self._stopped


# ===========================================================================
# Convenience Functions
# ===========================================================================


async def poll_outbox_events(
    pool: AsyncConnectionPool | MockConnectionPool,
    config: OutboxConfig | None = None,
    synapse_callback: Any | None = None,
) -> AsyncIterator[ChangeEvent]:
    """
    Convenience function to poll outbox and optionally auto-acknowledge.

    This is a helper for simple use cases. For more control, use
    OutboxSource directly.

    Args:
        pool: Database connection pool
        config: Optional configuration
        synapse_callback: Optional callback that returns True on successful sync

    Yields:
        ChangeEvent objects from the outbox
    """
    source = OutboxSource(pool, config)

    async with source:
        async for event in source:
            yield event

            # Auto-acknowledge if callback confirms success
            if synapse_callback is not None:
                success = await synapse_callback(event)
                if success and event.sequence_id is not None:
                    await source.acknowledge(event.sequence_id)
