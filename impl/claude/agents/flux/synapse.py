"""
Synapse: CDC Flux agent that maintains derived views.

Categorical Role: Functor from Anchor changes to View updates.

The Synapse maintains the functorial relationship between:
- Postgres (ANCHOR) - The source of truth
- Qdrant (ASSOCIATOR) - Semantic search derived view
- Redis (SPARK) - Cache derived view

Key Properties:
1. Postgres is the sole source of writes
2. Qdrant is mathematically derivative
3. If Qdrant is wiped, it can be fully regenerated from Postgres

Functor Laws:
- Synapse(id_A) = id_{Synapse(A)} -- No change in Postgres → no change in Qdrant
- Synapse(g ∘ f) = Synapse(g) ∘ Synapse(f) -- Sequential changes compose

Implementation Patterns:
1. Outbox Pattern (simpler): Poll outbox table for changes
2. WAL Tailing (advanced): Tail Postgres WAL for real-time changes

This implementation uses the Outbox Pattern for simplicity and portability.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator, Protocol, runtime_checkable

from agents.flux.agent import FluxAgent
from agents.flux.config import FluxConfig
from agents.poly.types import Agent

if TYPE_CHECKING:
    pass


# ===========================================================================
# CDC Event Types
# ===========================================================================


class ChangeOperation(Enum):
    """Database change operations."""

    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


@dataclass(frozen=True)
class ChangeEvent:
    """
    A change in the Anchor (Postgres).

    Represents a single row change from the outbox table or WAL.

    Attributes:
        table: Source table name
        operation: Type of change (INSERT, UPDATE, DELETE)
        row_id: Primary key of the affected row
        data: Row data (payload for INSERT/UPDATE, empty for DELETE)
        timestamp_ms: When the change occurred (unix millis)
        sequence_id: Outbox sequence number for ordering
    """

    table: str
    operation: ChangeOperation
    row_id: str
    data: dict[str, Any]
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    sequence_id: int | None = None

    @classmethod
    def insert(
        cls,
        table: str,
        row_id: str,
        data: dict[str, Any],
        sequence_id: int | None = None,
    ) -> "ChangeEvent":
        """Create an INSERT event."""
        return cls(
            table=table,
            operation=ChangeOperation.INSERT,
            row_id=row_id,
            data=data,
            sequence_id=sequence_id,
        )

    @classmethod
    def update(
        cls,
        table: str,
        row_id: str,
        data: dict[str, Any],
        sequence_id: int | None = None,
    ) -> "ChangeEvent":
        """Create an UPDATE event."""
        return cls(
            table=table,
            operation=ChangeOperation.UPDATE,
            row_id=row_id,
            data=data,
            sequence_id=sequence_id,
        )

    @classmethod
    def delete(cls, table: str, row_id: str, sequence_id: int | None = None) -> "ChangeEvent":
        """Create a DELETE event."""
        return cls(
            table=table,
            operation=ChangeOperation.DELETE,
            row_id=row_id,
            data={},
            sequence_id=sequence_id,
        )


class SyncTarget(Enum):
    """Target systems for sync operations."""

    QDRANT = "qdrant"
    REDIS = "redis"


class SyncOperation(Enum):
    """Types of sync operations."""

    UPSERT = "upsert"
    DELETE = "delete"
    INVALIDATE = "invalidate"


@dataclass(frozen=True)
class SyncResult:
    """
    Result of syncing to a derived view.

    Attributes:
        target: Which system was synced (qdrant, redis)
        operation: What operation was performed
        success: Whether the sync succeeded
        lag_ms: CDC lag (time from change to sync completion)
        source_sequence: Outbox sequence that was synced
        error: Error message if success is False
    """

    target: SyncTarget
    operation: SyncOperation
    success: bool
    lag_ms: float
    source_sequence: int | None = None
    error: str | None = None

    @classmethod
    def success_upsert(
        cls,
        target: SyncTarget,
        lag_ms: float,
        sequence: int | None = None,
    ) -> "SyncResult":
        """Create a successful upsert result."""
        return cls(
            target=target,
            operation=SyncOperation.UPSERT,
            success=True,
            lag_ms=lag_ms,
            source_sequence=sequence,
        )

    @classmethod
    def success_delete(
        cls,
        target: SyncTarget,
        lag_ms: float,
        sequence: int | None = None,
    ) -> "SyncResult":
        """Create a successful delete result."""
        return cls(
            target=target,
            operation=SyncOperation.DELETE,
            success=True,
            lag_ms=lag_ms,
            source_sequence=sequence,
        )

    @classmethod
    def failed(
        cls,
        target: SyncTarget,
        operation: SyncOperation,
        error: str,
        sequence: int | None = None,
    ) -> "SyncResult":
        """Create a failed sync result."""
        return cls(
            target=target,
            operation=operation,
            success=False,
            lag_ms=0.0,
            source_sequence=sequence,
            error=error,
        )


# ===========================================================================
# Provider Protocols
# ===========================================================================


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for computing embeddings."""

    async def embed(self, text: str) -> list[float]:
        """Compute embedding vector for text."""
        ...


@runtime_checkable
class VectorStore(Protocol):
    """Protocol for vector database operations."""

    async def upsert(
        self,
        collection: str,
        id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Upsert a vector with payload."""
        ...

    async def delete(self, collection: str, id: str) -> None:
        """Delete a vector by ID."""
        ...


@runtime_checkable
class CacheStore(Protocol):
    """Protocol for cache operations."""

    async def invalidate(self, key: str) -> None:
        """Invalidate a cache key."""
        ...


# ===========================================================================
# Synapse Configuration
# ===========================================================================


@dataclass(frozen=True)
class RetryConfig:
    """Configuration for retry behavior with exponential backoff."""

    max_retries: int = 3
    initial_delay_ms: int = 100
    max_delay_ms: int = 10000
    exponential_base: float = 2.0

    def delay_for_attempt(self, attempt: int) -> float:
        """Calculate delay in seconds for given attempt (0-indexed)."""
        delay_ms = self.initial_delay_ms * (self.exponential_base**attempt)
        delay_ms = min(delay_ms, self.max_delay_ms)
        return delay_ms / 1000


@dataclass(frozen=True)
class SynapseConfig:
    """
    Configuration for the Synapse CDC agent.

    Attributes:
        collection: Default Qdrant collection name
        text_field: Field in data to embed
        sync_to_qdrant: Whether to sync to Qdrant
        sync_to_redis: Whether to sync to Redis (cache invalidation)
        batch_size: Number of events to process before committing
        retry_failed: Whether to retry failed syncs
        max_retries: Maximum retry attempts for failed syncs
        retry_config: Detailed retry configuration
        use_circuit_breaker: Whether to use circuit breaker for Qdrant
        use_dlq: Whether to send failed events to dead letter queue
    """

    collection: str = "memories"
    text_field: str = "content"
    sync_to_qdrant: bool = True
    sync_to_redis: bool = False
    batch_size: int = 100
    retry_failed: bool = True
    max_retries: int = 3
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    use_circuit_breaker: bool = False
    use_dlq: bool = False


# ===========================================================================
# Synapse Metrics (Observability)
# ===========================================================================


@dataclass
class SynapseMetrics:
    """
    Metrics for monitoring the CDC pipeline.

    Provides visibility into Synapse health and performance.
    """

    events_processed: int = 0
    events_failed: int = 0
    events_retried: int = 0
    events_in_dlq: int = 0
    avg_sync_lag_ms: float = 0.0
    max_sync_lag_ms: float = 0.0
    circuit_state: str = "closed"
    last_successful_sync: datetime | None = None
    last_failed_sync: datetime | None = None
    _lag_samples: list[float] = field(default_factory=list)

    def record_success(self, lag_ms: float) -> None:
        """Record a successful sync."""
        self.events_processed += 1
        self._lag_samples.append(lag_ms)
        if len(self._lag_samples) > 100:
            self._lag_samples.pop(0)
        self.avg_sync_lag_ms = sum(self._lag_samples) / len(self._lag_samples)
        self.max_sync_lag_ms = max(self.max_sync_lag_ms, lag_ms)
        self.last_successful_sync = datetime.now(timezone.utc)

    def record_failure(self) -> None:
        """Record a failed sync."""
        self.events_failed += 1
        self.last_failed_sync = datetime.now(timezone.utc)

    def record_retry(self) -> None:
        """Record a retry attempt."""
        self.events_retried += 1

    def record_dlq(self) -> None:
        """Record event sent to DLQ."""
        self.events_in_dlq += 1

    def set_circuit_state(self, state: str) -> None:
        """Update circuit breaker state."""
        self.circuit_state = state

    def to_prometheus(self) -> str:
        """Export as Prometheus text format."""
        lines = [
            "# HELP synapse_events_processed_total Total CDC events processed",
            "# TYPE synapse_events_processed_total counter",
            f"synapse_events_processed_total {self.events_processed}",
            "",
            "# HELP synapse_events_failed_total Total CDC events that failed",
            "# TYPE synapse_events_failed_total counter",
            f"synapse_events_failed_total {self.events_failed}",
            "",
            "# HELP synapse_events_retried_total Total retry attempts",
            "# TYPE synapse_events_retried_total counter",
            f"synapse_events_retried_total {self.events_retried}",
            "",
            "# HELP synapse_dlq_size Current dead letter queue size",
            "# TYPE synapse_dlq_size gauge",
            f"synapse_dlq_size {self.events_in_dlq}",
            "",
            "# HELP synapse_sync_lag_ms Average CDC sync lag in milliseconds",
            "# TYPE synapse_sync_lag_ms gauge",
            f"synapse_sync_lag_ms {self.avg_sync_lag_ms}",
            "",
            "# HELP synapse_sync_lag_max_ms Maximum CDC sync lag in milliseconds",
            "# TYPE synapse_sync_lag_max_ms gauge",
            f"synapse_sync_lag_max_ms {self.max_sync_lag_ms}",
            "",
            "# HELP synapse_circuit_state Circuit breaker state",
            "# TYPE synapse_circuit_state gauge",
            f'synapse_circuit_state{{state="{self.circuit_state}"}} 1',
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary for API responses."""
        return {
            "events_processed": self.events_processed,
            "events_failed": self.events_failed,
            "events_retried": self.events_retried,
            "events_in_dlq": self.events_in_dlq,
            "avg_sync_lag_ms": self.avg_sync_lag_ms,
            "max_sync_lag_ms": self.max_sync_lag_ms,
            "circuit_state": self.circuit_state,
            "last_successful_sync": (
                self.last_successful_sync.isoformat() if self.last_successful_sync else None
            ),
            "last_failed_sync": (
                self.last_failed_sync.isoformat() if self.last_failed_sync else None
            ),
        }


# ===========================================================================
# Synapse Inner Agent
# ===========================================================================


class SynapseProcessor(Agent[ChangeEvent, list[SyncResult]]):
    """
    Inner agent that processes CDC events.

    This is the discrete agent that gets lifted to Flux.
    Each invocation processes one ChangeEvent and returns SyncResults.
    """

    def __init__(
        self,
        config: SynapseConfig,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None,
        cache_store: CacheStore | None = None,
    ) -> None:
        """
        Initialize the Synapse processor.

        Args:
            config: Synapse configuration
            embedding_provider: Provider for computing embeddings
            vector_store: Vector database client (Qdrant)
            cache_store: Cache client (Redis)
        """
        self._config = config
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._cache_store = cache_store

    @property
    def name(self) -> str:
        return "SynapseProcessor"

    async def invoke(self, event: ChangeEvent) -> list[SyncResult]:
        """
        Process a single CDC event.

        Routes to appropriate handler based on operation type.
        Returns list of SyncResults (one per target system).
        """
        results: list[SyncResult] = []
        start_time = time.time()

        # Process Qdrant sync
        if self._config.sync_to_qdrant:
            qdrant_result = await self._sync_to_qdrant(event, start_time)
            results.append(qdrant_result)

        # Process Redis sync (cache invalidation)
        if self._config.sync_to_redis:
            redis_result = await self._sync_to_redis(event, start_time)
            results.append(redis_result)

        return results

    async def _sync_to_qdrant(self, event: ChangeEvent, start_time: float) -> SyncResult:
        """Sync event to Qdrant vector store."""
        try:
            if event.operation == ChangeOperation.DELETE:
                await self._delete_from_qdrant(event)
                lag_ms = (time.time() - start_time) * 1000
                return SyncResult.success_delete(
                    target=SyncTarget.QDRANT,
                    lag_ms=lag_ms,
                    sequence=event.sequence_id,
                )
            else:
                # INSERT or UPDATE
                await self._upsert_to_qdrant(event)
                lag_ms = (time.time() - start_time) * 1000
                return SyncResult.success_upsert(
                    target=SyncTarget.QDRANT,
                    lag_ms=lag_ms,
                    sequence=event.sequence_id,
                )
        except Exception as e:
            return SyncResult.failed(
                target=SyncTarget.QDRANT,
                operation=(
                    SyncOperation.DELETE
                    if event.operation == ChangeOperation.DELETE
                    else SyncOperation.UPSERT
                ),
                error=str(e),
                sequence=event.sequence_id,
            )

    async def _upsert_to_qdrant(self, event: ChangeEvent) -> None:
        """Upsert vector to Qdrant."""
        if self._embedding_provider is None or self._vector_store is None:
            # Mock mode - just validate the event
            return

        # Extract text to embed
        text = event.data.get(self._config.text_field, "")
        if not text:
            return  # Nothing to embed

        # Compute embedding
        vector = await self._embedding_provider.embed(text)

        # Build payload
        payload = {
            "source": "postgres",
            "table": event.table,
            **event.data,
        }

        # Upsert to vector store
        await self._vector_store.upsert(
            collection=self._config.collection,
            id=event.row_id,
            vector=vector,
            payload=payload,
        )

    async def _delete_from_qdrant(self, event: ChangeEvent) -> None:
        """Delete vector from Qdrant."""
        if self._vector_store is None:
            # Mock mode
            return

        await self._vector_store.delete(
            collection=self._config.collection,
            id=event.row_id,
        )

    async def _sync_to_redis(self, event: ChangeEvent, start_time: float) -> SyncResult:
        """Sync event to Redis (cache invalidation)."""
        try:
            if self._cache_store is not None:
                # Invalidate cache for this row
                cache_key = f"{event.table}:{event.row_id}"
                await self._cache_store.invalidate(cache_key)

            lag_ms = (time.time() - start_time) * 1000
            return SyncResult(
                target=SyncTarget.REDIS,
                operation=SyncOperation.INVALIDATE,
                success=True,
                lag_ms=lag_ms,
                source_sequence=event.sequence_id,
            )
        except Exception as e:
            return SyncResult.failed(
                target=SyncTarget.REDIS,
                operation=SyncOperation.INVALIDATE,
                error=str(e),
                sequence=event.sequence_id,
            )


# ===========================================================================
# Robust Synapse Processor (with retry, circuit breaker, DLQ)
# ===========================================================================


class RobustSynapseProcessor(Agent[ChangeEvent, list[SyncResult]]):
    """
    Enhanced Synapse processor with robustification features.

    Adds:
    - Retry with exponential backoff
    - Circuit breaker for Qdrant
    - Dead letter queue for failed events
    - Observability metrics

    Use this for production deployments where reliability is critical.
    """

    def __init__(
        self,
        config: SynapseConfig,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None,
        cache_store: CacheStore | None = None,
        metrics: SynapseMetrics | None = None,
    ) -> None:
        """
        Initialize the robust Synapse processor.

        Args:
            config: Synapse configuration
            embedding_provider: Provider for computing embeddings
            vector_store: Vector database client (Qdrant)
            cache_store: Cache client (Redis)
            metrics: Optional metrics collector
        """
        self._config = config
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._cache_store = cache_store
        self._metrics = metrics or SynapseMetrics()

        # Initialize circuit breaker if enabled
        self._circuit_breaker: Any = None
        if config.use_circuit_breaker:
            from agents.flux.circuit_breaker import create_qdrant_breaker

            self._circuit_breaker = create_qdrant_breaker()

        # Initialize DLQ if enabled
        self._dlq: Any = None
        if config.use_dlq:
            from agents.flux.dlq import get_dlq

            self._dlq = get_dlq()

    @property
    def name(self) -> str:
        return "RobustSynapseProcessor"

    @property
    def metrics(self) -> SynapseMetrics:
        """Get current metrics."""
        return self._metrics

    async def invoke(self, event: ChangeEvent) -> list[SyncResult]:
        """
        Process a CDC event with retry and circuit breaker.

        Returns list of SyncResults (one per target system).
        """
        results: list[SyncResult] = []
        start_time = time.time()

        # Process Qdrant sync with retry
        if self._config.sync_to_qdrant:
            qdrant_result = await self._sync_to_qdrant_with_retry(event, start_time)
            results.append(qdrant_result)

            # Update metrics
            if qdrant_result.success:
                self._metrics.record_success(qdrant_result.lag_ms)
            else:
                self._metrics.record_failure()

        # Process Redis sync (no retry - cache invalidation is best-effort)
        if self._config.sync_to_redis:
            redis_result = await self._sync_to_redis(event, start_time)
            results.append(redis_result)

        return results

    async def _sync_to_qdrant_with_retry(self, event: ChangeEvent, start_time: float) -> SyncResult:
        """Sync to Qdrant with retry and circuit breaker."""
        retry_config = self._config.retry_config
        last_error: str = ""

        for attempt in range(retry_config.max_retries + 1):
            try:
                # Check circuit breaker
                if self._circuit_breaker and self._circuit_breaker.is_open:
                    from agents.flux.circuit_breaker import CircuitOpenError

                    raise CircuitOpenError(
                        self._circuit_breaker.name,
                        self._circuit_breaker.time_until_retry,
                    )

                # Attempt sync
                result = await self._sync_to_qdrant(event, start_time)

                if result.success:
                    return result

                last_error = result.error or "Unknown error"

                # Record failure in circuit breaker
                if self._circuit_breaker:
                    self._circuit_breaker._on_failure()
                    self._metrics.set_circuit_state(self._circuit_breaker.state.value)

            except Exception as e:
                last_error = str(e)

                # Record failure in circuit breaker
                if self._circuit_breaker:
                    self._circuit_breaker._on_failure()
                    self._metrics.set_circuit_state(self._circuit_breaker.state.value)

            # Check if we should retry
            if attempt < retry_config.max_retries:
                self._metrics.record_retry()
                delay = retry_config.delay_for_attempt(attempt)
                await asyncio.sleep(delay)
            else:
                # Max retries exceeded - send to DLQ
                await self._send_to_dlq(event, last_error)

        # All retries exhausted
        return SyncResult.failed(
            target=SyncTarget.QDRANT,
            operation=(
                SyncOperation.DELETE
                if event.operation == ChangeOperation.DELETE
                else SyncOperation.UPSERT
            ),
            error=f"Max retries exceeded: {last_error}",
            sequence=event.sequence_id,
        )

    async def _sync_to_qdrant(self, event: ChangeEvent, start_time: float) -> SyncResult:
        """Sync event to Qdrant vector store."""
        try:
            if event.operation == ChangeOperation.DELETE:
                await self._delete_from_qdrant(event)
                lag_ms = (time.time() - start_time) * 1000
                return SyncResult.success_delete(
                    target=SyncTarget.QDRANT,
                    lag_ms=lag_ms,
                    sequence=event.sequence_id,
                )
            else:
                await self._upsert_to_qdrant(event)
                lag_ms = (time.time() - start_time) * 1000
                return SyncResult.success_upsert(
                    target=SyncTarget.QDRANT,
                    lag_ms=lag_ms,
                    sequence=event.sequence_id,
                )
        except Exception as e:
            return SyncResult.failed(
                target=SyncTarget.QDRANT,
                operation=(
                    SyncOperation.DELETE
                    if event.operation == ChangeOperation.DELETE
                    else SyncOperation.UPSERT
                ),
                error=str(e),
                sequence=event.sequence_id,
            )

    async def _upsert_to_qdrant(self, event: ChangeEvent) -> None:
        """Upsert vector to Qdrant."""
        if self._embedding_provider is None or self._vector_store is None:
            return

        text = event.data.get(self._config.text_field, "")
        if not text:
            return

        vector = await self._embedding_provider.embed(text)
        payload = {
            "source": "postgres",
            "table": event.table,
            **event.data,
        }

        await self._vector_store.upsert(
            collection=self._config.collection,
            id=event.row_id,
            vector=vector,
            payload=payload,
        )

    async def _delete_from_qdrant(self, event: ChangeEvent) -> None:
        """Delete vector from Qdrant."""
        if self._vector_store is None:
            return

        await self._vector_store.delete(
            collection=self._config.collection,
            id=event.row_id,
        )

    async def _sync_to_redis(self, event: ChangeEvent, start_time: float) -> SyncResult:
        """Sync event to Redis (cache invalidation)."""
        try:
            if self._cache_store is not None:
                cache_key = f"{event.table}:{event.row_id}"
                await self._cache_store.invalidate(cache_key)

            lag_ms = (time.time() - start_time) * 1000
            return SyncResult(
                target=SyncTarget.REDIS,
                operation=SyncOperation.INVALIDATE,
                success=True,
                lag_ms=lag_ms,
                source_sequence=event.sequence_id,
            )
        except Exception as e:
            return SyncResult.failed(
                target=SyncTarget.REDIS,
                operation=SyncOperation.INVALIDATE,
                error=str(e),
                sequence=event.sequence_id,
            )

    async def _send_to_dlq(self, event: ChangeEvent, error: str) -> None:
        """Send failed event to dead letter queue."""
        if self._dlq is None:
            return

        from agents.flux.dlq import DeadLetterEvent, DLQReason

        dle = DeadLetterEvent.from_event(
            event=event,
            target="qdrant",
            error=error,
            reason=DLQReason.MAX_RETRIES_EXCEEDED,
            retry_count=self._config.retry_config.max_retries,
        )

        await self._dlq.enqueue(dle)
        self._metrics.record_dlq()


# ===========================================================================
# Synapse FluxAgent Factory
# ===========================================================================


def create_synapse(
    config: SynapseConfig | None = None,
    embedding_provider: EmbeddingProvider | None = None,
    vector_store: VectorStore | None = None,
    cache_store: CacheStore | None = None,
    flux_config: FluxConfig | None = None,
) -> FluxAgent[ChangeEvent, list[SyncResult]]:
    """
    Create a Synapse FluxAgent.

    The Synapse is a FluxAgent that processes CDC events and maintains
    consistency between Postgres and derived views (Qdrant, Redis).

    Args:
        config: Synapse configuration
        embedding_provider: Provider for computing embeddings
        vector_store: Vector database client (Qdrant)
        cache_store: Cache client (Redis)
        flux_config: Flux configuration (defaults to infinite)

    Returns:
        FluxAgent ready to process ChangeEvent streams

    Example:
        >>> synapse = create_synapse(
        ...     embedding_provider=openai_embedder,
        ...     vector_store=qdrant_client,
        ... )
        >>> async for results in synapse.start(outbox_events):
        ...     for result in results:
        ...         print(f"{result.target}: {result.operation} ({result.lag_ms}ms)")

    Categorical Guarantee:
        Synapse(id_A) = id_{Synapse(A)}  -- No change in Postgres → no change in Qdrant
        Synapse(g ∘ f) = Synapse(g) ∘ Synapse(f)  -- Sequential changes compose
    """
    synapse_config = config or SynapseConfig()
    inner = SynapseProcessor(
        config=synapse_config,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        cache_store=cache_store,
    )

    # Default to infinite flux (CDC runs forever)
    flux_cfg = flux_config or FluxConfig.infinite()

    return FluxAgent(inner=inner, config=flux_cfg)


def create_robust_synapse(
    config: SynapseConfig | None = None,
    embedding_provider: EmbeddingProvider | None = None,
    vector_store: VectorStore | None = None,
    cache_store: CacheStore | None = None,
    flux_config: FluxConfig | None = None,
    metrics: SynapseMetrics | None = None,
) -> FluxAgent[ChangeEvent, list[SyncResult]]:
    """
    Create a robust Synapse FluxAgent with retry, circuit breaker, and DLQ.

    This is the production-grade version of create_synapse with:
    - Retry with exponential backoff
    - Circuit breaker for Qdrant
    - Dead letter queue for permanently failed events
    - Observability metrics

    Args:
        config: Synapse configuration (use_circuit_breaker/use_dlq enable features)
        embedding_provider: Provider for computing embeddings
        vector_store: Vector database client (Qdrant)
        cache_store: Cache client (Redis)
        flux_config: Flux configuration (defaults to infinite)
        metrics: Optional metrics collector (created if not provided)

    Returns:
        FluxAgent with robustification features

    Example:
        >>> config = SynapseConfig(
        ...     use_circuit_breaker=True,
        ...     use_dlq=True,
        ...     retry_config=RetryConfig(max_retries=5),
        ... )
        >>> synapse = create_robust_synapse(
        ...     config=config,
        ...     embedding_provider=openai_embedder,
        ...     vector_store=qdrant_client,
        ... )
        >>> async for results in synapse.start(outbox_events):
        ...     for result in results:
        ...         if not result.success:
        ...             print(f"WARN: {result.error}")
        >>> # Check metrics
        >>> print(synapse._inner.metrics.to_prometheus())
    """
    synapse_config = config or SynapseConfig(use_circuit_breaker=True, use_dlq=True)
    inner = RobustSynapseProcessor(
        config=synapse_config,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        cache_store=cache_store,
        metrics=metrics,
    )

    flux_cfg = flux_config or FluxConfig.infinite()

    return FluxAgent(inner=inner, config=flux_cfg)


# ===========================================================================
# Outbox Source (for convenience)
# ===========================================================================


@dataclass
class OutboxConfig:
    """
    Configuration for polling the outbox table.

    Attributes:
        poll_interval_ms: How often to poll for new events
        batch_size: Maximum events to fetch per poll
        mark_processed: Whether to mark events as processed
    """

    poll_interval_ms: int = 100
    batch_size: int = 100
    mark_processed: bool = True


async def poll_outbox(
    fetch_events: AsyncIterator[list[ChangeEvent]],
) -> AsyncIterator[ChangeEvent]:
    """
    Convert batched outbox fetches into individual ChangeEvents.

    Args:
        fetch_events: Iterator that yields batches of events from outbox

    Yields:
        Individual ChangeEvent objects

    Example:
        >>> async def fetch_from_db():
        ...     while True:
        ...         events = await db.query("SELECT * FROM outbox WHERE ...")
        ...         yield [ChangeEvent(...) for e in events]
        ...         await asyncio.sleep(0.1)
        >>>
        >>> async for event in poll_outbox(fetch_from_db()):
        ...     # Process individual event
        ...     pass
    """
    async for batch in fetch_events:
        for event in batch:
            yield event


# ===========================================================================
# CDC Lag Tracking
# ===========================================================================


@dataclass
class CDCLagTracker:
    """
    Tracks CDC lag for monitoring.

    The coherency_with_truth metric depends on this lag:
    - 0ms lag = perfect coherency
    - 5000ms lag = 0 coherency (threshold)

    Used by ResonanceSignal in the Semantic Metrics.
    """

    _samples: list[float] = field(default_factory=list)
    _max_samples: int = 100

    def record(self, lag_ms: float) -> None:
        """Record a lag sample."""
        self._samples.append(lag_ms)
        if len(self._samples) > self._max_samples:
            self._samples.pop(0)

    @property
    def avg_lag_ms(self) -> float:
        """Average lag in milliseconds."""
        if not self._samples:
            return 0.0
        return sum(self._samples) / len(self._samples)

    @property
    def max_lag_ms(self) -> float:
        """Maximum lag in milliseconds."""
        if not self._samples:
            return 0.0
        return max(self._samples)

    @property
    def coherency(self) -> float:
        """
        Coherency with truth (0-1).

        Degrades linearly as lag increases:
        - 0ms = 1.0 (perfect)
        - 5000ms = 0.0 (threshold)
        """
        threshold_ms = 5000.0
        return max(0.0, 1.0 - (self.avg_lag_ms / threshold_ms))
