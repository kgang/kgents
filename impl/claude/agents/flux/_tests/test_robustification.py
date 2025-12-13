"""
Tests for Synapse robustification features.

Test Categories:
1. RetryConfig and exponential backoff
2. DeadLetterQueue operations
3. CircuitBreaker state machine
4. RobustSynapseProcessor integration
5. SynapseMetrics observability
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import pytest
from agents.flux.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitOpenError,
    CircuitState,
    create_qdrant_breaker,
)
from agents.flux.dlq import (
    DeadLetterEvent,
    DeadLetterQueue,
    DLQReason,
    get_dlq,
    reset_dlq,
)
from agents.flux.synapse import (
    ChangeEvent,
    ChangeOperation,
    RetryConfig,
    RobustSynapseProcessor,
    SynapseConfig,
    SynapseMetrics,
    create_robust_synapse,
)

# ===========================================================================
# Test Fixtures
# ===========================================================================


@dataclass
class FailingVectorStore:
    """Vector store that fails on demand."""

    failure_count: int = 0
    failures_remaining: int = 0
    calls: list[str] = field(default_factory=list)

    async def upsert(
        self,
        collection: str,
        id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        self.calls.append(f"upsert:{collection}:{id}")
        if self.failures_remaining > 0:
            self.failures_remaining -= 1
            self.failure_count += 1
            raise ConnectionError("Simulated Qdrant failure")

    async def delete(self, collection: str, id: str) -> None:
        self.calls.append(f"delete:{collection}:{id}")
        if self.failures_remaining > 0:
            self.failures_remaining -= 1
            self.failure_count += 1
            raise ConnectionError("Simulated Qdrant failure")


@dataclass
class MockEmbeddingProvider:
    """Mock embedding provider."""

    dimension: int = 128

    async def embed(self, text: str) -> list[float]:
        return [0.1] * self.dimension


# ===========================================================================
# RetryConfig Tests
# ===========================================================================


class TestRetryConfig:
    """Tests for RetryConfig and exponential backoff."""

    def test_retry_config_defaults(self) -> None:
        """RetryConfig has sensible defaults."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.initial_delay_ms == 100
        assert config.max_delay_ms == 10000
        assert config.exponential_base == 2.0

    def test_delay_for_attempt_exponential(self) -> None:
        """Delay increases exponentially with attempts."""
        config = RetryConfig(
            initial_delay_ms=100,
            exponential_base=2.0,
            max_delay_ms=10000,
        )

        # Attempt 0: 100ms
        assert config.delay_for_attempt(0) == 0.1

        # Attempt 1: 200ms
        assert config.delay_for_attempt(1) == 0.2

        # Attempt 2: 400ms
        assert config.delay_for_attempt(2) == 0.4

        # Attempt 3: 800ms
        assert config.delay_for_attempt(3) == 0.8

    def test_delay_caps_at_max(self) -> None:
        """Delay never exceeds max_delay_ms."""
        config = RetryConfig(
            initial_delay_ms=1000,
            exponential_base=10.0,
            max_delay_ms=5000,
        )

        # Would be 10000ms but capped at 5000ms
        assert config.delay_for_attempt(1) == 5.0

        # High attempt would be huge but capped
        assert config.delay_for_attempt(10) == 5.0

    def test_delay_returns_seconds(self) -> None:
        """delay_for_attempt returns seconds, not milliseconds."""
        config = RetryConfig(initial_delay_ms=1000)

        assert config.delay_for_attempt(0) == 1.0  # 1 second


# ===========================================================================
# DeadLetterQueue Tests
# ===========================================================================


class TestDeadLetterQueue:
    """Tests for DeadLetterQueue."""

    @pytest.fixture(autouse=True)
    def reset_global_dlq(self) -> None:
        """Reset global DLQ before each test."""
        reset_dlq()

    def test_dlq_creation(self) -> None:
        """DLQ can be created."""
        dlq = DeadLetterQueue()
        assert dlq.size == 0
        assert dlq.is_empty

    def test_dlq_enqueue_sync(self) -> None:
        """Events can be enqueued synchronously."""
        dlq = DeadLetterQueue()
        event = DeadLetterEvent(
            original_event_table="memories",
            original_event_operation="INSERT",
            original_event_row_id="mem-1",
            original_event_data={"content": "test"},
            original_event_sequence_id=1,
            target="qdrant",
            error="Connection refused",
            reason=DLQReason.MAX_RETRIES_EXCEEDED,
            failed_at=datetime.now(timezone.utc),
            retry_count=3,
        )

        dlq.enqueue_sync(event)

        assert dlq.size == 1
        assert not dlq.is_empty

    @pytest.mark.asyncio
    async def test_dlq_enqueue_async(self) -> None:
        """Events can be enqueued asynchronously."""
        dlq = DeadLetterQueue()
        event = DeadLetterEvent(
            original_event_table="memories",
            original_event_operation="INSERT",
            original_event_row_id="mem-1",
            original_event_data={},
            original_event_sequence_id=1,
            target="qdrant",
            error="Error",
            reason=DLQReason.MAX_RETRIES_EXCEEDED,
            failed_at=datetime.now(timezone.utc),
            retry_count=3,
        )

        await dlq.enqueue(event)

        assert dlq.size == 1

    def test_dlq_drain(self) -> None:
        """drain() returns all events and clears queue."""
        dlq = DeadLetterQueue()

        for i in range(3):
            event = DeadLetterEvent(
                original_event_table="t",
                original_event_operation="INSERT",
                original_event_row_id=str(i),
                original_event_data={},
                original_event_sequence_id=i,
                target="qdrant",
                error="Error",
                reason=DLQReason.MAX_RETRIES_EXCEEDED,
                failed_at=datetime.now(timezone.utc),
                retry_count=3,
            )
            dlq.enqueue_sync(event)

        events = dlq.drain()

        assert len(events) == 3
        assert dlq.size == 0

    def test_dlq_max_size_evicts_oldest(self) -> None:
        """DLQ evicts oldest when at capacity."""
        dlq = DeadLetterQueue(max_size=2)

        for i in range(3):
            event = DeadLetterEvent(
                original_event_table="t",
                original_event_operation="INSERT",
                original_event_row_id=str(i),
                original_event_data={},
                original_event_sequence_id=i,
                target="qdrant",
                error="Error",
                reason=DLQReason.MAX_RETRIES_EXCEEDED,
                failed_at=datetime.now(timezone.utc),
                retry_count=3,
            )
            dlq.enqueue_sync(event)

        assert dlq.size == 2
        assert dlq.total_evicted == 1

        # First event should be evicted
        events = dlq.drain()
        assert events[0].original_event_row_id == "1"
        assert events[1].original_event_row_id == "2"

    def test_dlq_peek(self) -> None:
        """peek() returns events without removing."""
        dlq = DeadLetterQueue()

        for i in range(5):
            event = DeadLetterEvent(
                original_event_table="t",
                original_event_operation="INSERT",
                original_event_row_id=str(i),
                original_event_data={},
                original_event_sequence_id=i,
                target="qdrant",
                error="Error",
                reason=DLQReason.MAX_RETRIES_EXCEEDED,
                failed_at=datetime.now(timezone.utc),
                retry_count=3,
            )
            dlq.enqueue_sync(event)

        peeked = dlq.peek(3)

        assert len(peeked) == 3
        assert dlq.size == 5  # Not removed

    def test_dlq_peek_by_table(self) -> None:
        """peek_by_table filters by table name."""
        dlq = DeadLetterQueue()

        for table in ["users", "memories", "users"]:
            event = DeadLetterEvent(
                original_event_table=table,
                original_event_operation="INSERT",
                original_event_row_id="1",
                original_event_data={},
                original_event_sequence_id=1,
                target="qdrant",
                error="Error",
                reason=DLQReason.MAX_RETRIES_EXCEEDED,
                failed_at=datetime.now(timezone.utc),
                retry_count=3,
            )
            dlq.enqueue_sync(event)

        users = dlq.peek_by_table("users")
        assert len(users) == 2

    def test_dlq_stats(self) -> None:
        """stats() returns useful information."""
        dlq = DeadLetterQueue()

        for i, reason in enumerate(
            [DLQReason.MAX_RETRIES_EXCEEDED, DLQReason.CIRCUIT_OPEN]
        ):
            event = DeadLetterEvent(
                original_event_table="t",
                original_event_operation="INSERT",
                original_event_row_id=str(i),
                original_event_data={},
                original_event_sequence_id=i,
                target="qdrant",
                error="Error",
                reason=reason,
                failed_at=datetime.now(timezone.utc),
                retry_count=3,
            )
            dlq.enqueue_sync(event)

        stats = dlq.stats()

        assert stats["size"] == 2
        assert stats["by_reason"]["max_retries_exceeded"] == 1
        assert stats["by_reason"]["circuit_open"] == 1

    def test_dead_letter_event_from_change_event(self) -> None:
        """DeadLetterEvent.from_event creates from ChangeEvent."""
        change_event = ChangeEvent.insert(
            table="memories",
            row_id="mem-1",
            data={"content": "test"},
            sequence_id=42,
        )

        dle = DeadLetterEvent.from_event(
            event=change_event,
            target="qdrant",
            error="Connection refused",
            reason=DLQReason.MAX_RETRIES_EXCEEDED,
            retry_count=3,
        )

        assert dle.original_event_table == "memories"
        assert dle.original_event_operation == "INSERT"
        assert dle.original_event_row_id == "mem-1"
        assert dle.original_event_sequence_id == 42

    def test_dead_letter_event_to_dict(self) -> None:
        """DeadLetterEvent serializes to dict."""
        dle = DeadLetterEvent(
            original_event_table="t",
            original_event_operation="INSERT",
            original_event_row_id="1",
            original_event_data={"key": "value"},
            original_event_sequence_id=1,
            target="qdrant",
            error="Error",
            reason=DLQReason.MAX_RETRIES_EXCEEDED,
            failed_at=datetime.now(timezone.utc),
            retry_count=3,
        )

        d = dle.to_dict()

        assert d["table"] == "t"
        assert d["reason"] == "max_retries_exceeded"

    def test_global_dlq(self) -> None:
        """get_dlq returns singleton."""
        dlq1 = get_dlq()
        dlq2 = get_dlq()

        assert dlq1 is dlq2


# ===========================================================================
# CircuitBreaker Tests
# ===========================================================================


class TestCircuitBreaker:
    """Tests for CircuitBreaker."""

    def test_circuit_starts_closed(self) -> None:
        """Circuit starts in CLOSED state."""
        breaker = CircuitBreaker("test")

        assert breaker.state == CircuitState.CLOSED
        assert breaker.is_closed

    def test_circuit_opens_after_threshold(self) -> None:
        """Circuit opens after failure_threshold failures."""
        breaker = CircuitBreaker(
            "test",
            config=CircuitBreakerConfig(failure_threshold=3),
        )

        # Record failures
        for _ in range(3):
            breaker._on_failure()

        assert breaker.state == CircuitState.OPEN
        assert breaker.is_open

    def test_circuit_half_opens_after_timeout(self) -> None:
        """Circuit transitions to HALF_OPEN after recovery timeout."""
        breaker = CircuitBreaker(
            "test",
            config=CircuitBreakerConfig(
                failure_threshold=1,
                recovery_timeout=0.1,  # 100ms
            ),
        )

        # Open the circuit
        breaker._on_failure()
        assert breaker.is_open

        # Wait for recovery timeout
        time.sleep(0.15)

        # Check transition (happens on next call attempt)
        breaker._check_state_transition()

        assert breaker.state == CircuitState.HALF_OPEN

    def test_circuit_closes_on_success(self) -> None:
        """Successful call in HALF_OPEN closes circuit."""
        breaker = CircuitBreaker(
            "test",
            config=CircuitBreakerConfig(
                failure_threshold=1,
                recovery_timeout=0.01,
                success_threshold=1,
            ),
        )

        # Open then half-open
        breaker._on_failure()
        time.sleep(0.02)
        breaker._check_state_transition()
        assert breaker.is_half_open

        # Success should close
        breaker._on_success()
        assert breaker.is_closed

    def test_circuit_reopens_on_half_open_failure(self) -> None:
        """Failure in HALF_OPEN reopens circuit."""
        breaker = CircuitBreaker(
            "test",
            config=CircuitBreakerConfig(
                failure_threshold=1,
                recovery_timeout=0.01,
            ),
        )

        # Open then half-open
        breaker._on_failure()
        time.sleep(0.02)
        breaker._check_state_transition()
        assert breaker.is_half_open

        # Another failure should reopen
        breaker._on_failure()
        assert breaker.is_open

    @pytest.mark.asyncio
    async def test_circuit_call_rejects_when_open(self) -> None:
        """call() raises CircuitOpenError when open."""
        breaker = CircuitBreaker(
            "test",
            config=CircuitBreakerConfig(
                failure_threshold=1,
                recovery_timeout=10.0,  # Long timeout
            ),
        )

        # Open the circuit
        breaker.force_open()

        async def dummy() -> str:
            return "ok"

        with pytest.raises(CircuitOpenError) as exc_info:
            await breaker.call(dummy)

        assert "open" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_circuit_call_succeeds_when_closed(self) -> None:
        """call() succeeds when circuit is closed."""
        breaker = CircuitBreaker("test")

        async def return_value() -> str:
            return "success"

        result = await breaker.call(return_value)

        assert result == "success"

    @pytest.mark.asyncio
    async def test_circuit_call_records_failure(self) -> None:
        """call() records failures for circuit logic."""
        breaker = CircuitBreaker(
            "test",
            config=CircuitBreakerConfig(failure_threshold=2),
        )

        async def always_fails() -> None:
            raise ValueError("boom")

        # First failure
        with pytest.raises(ValueError):
            await breaker.call(always_fails)
        assert breaker._failure_count == 1

        # Second failure - should open
        with pytest.raises(ValueError):
            await breaker.call(always_fails)
        assert breaker.is_open

    def test_circuit_stats(self) -> None:
        """stats() returns useful information."""
        breaker = CircuitBreaker(
            "test-breaker",
            config=CircuitBreakerConfig(failure_threshold=5),
        )

        for _ in range(3):
            breaker._on_failure()

        stats = breaker.stats()

        assert stats["name"] == "test-breaker"
        assert stats["state"] == "closed"
        assert stats["failure_count"] == 3

    def test_circuit_force_operations(self) -> None:
        """force_open and force_close work."""
        breaker = CircuitBreaker("test")

        breaker.force_open()
        assert breaker.is_open

        breaker.force_close()
        assert breaker.is_closed

    def test_create_qdrant_breaker_factory(self) -> None:
        """create_qdrant_breaker creates configured breaker."""
        breaker = create_qdrant_breaker(
            failure_threshold=10,
            recovery_timeout=60.0,
        )

        assert breaker.name == "qdrant"
        assert breaker.config.failure_threshold == 10


# ===========================================================================
# SynapseMetrics Tests
# ===========================================================================


class TestSynapseMetrics:
    """Tests for SynapseMetrics observability."""

    def test_metrics_creation(self) -> None:
        """Metrics can be created."""
        metrics = SynapseMetrics()

        assert metrics.events_processed == 0
        assert metrics.events_failed == 0

    def test_metrics_record_success(self) -> None:
        """record_success updates counters."""
        metrics = SynapseMetrics()

        metrics.record_success(lag_ms=50.0)

        assert metrics.events_processed == 1
        assert metrics.avg_sync_lag_ms == 50.0
        assert metrics.last_successful_sync is not None

    def test_metrics_record_failure(self) -> None:
        """record_failure updates counters."""
        metrics = SynapseMetrics()

        metrics.record_failure()

        assert metrics.events_failed == 1
        assert metrics.last_failed_sync is not None

    def test_metrics_record_retry(self) -> None:
        """record_retry updates counter."""
        metrics = SynapseMetrics()

        metrics.record_retry()
        metrics.record_retry()

        assert metrics.events_retried == 2

    def test_metrics_avg_lag_rolling(self) -> None:
        """avg_sync_lag_ms uses rolling average."""
        metrics = SynapseMetrics()

        metrics.record_success(100.0)
        metrics.record_success(200.0)
        metrics.record_success(300.0)

        assert metrics.avg_sync_lag_ms == 200.0

    def test_metrics_max_lag(self) -> None:
        """max_sync_lag_ms tracks maximum."""
        metrics = SynapseMetrics()

        metrics.record_success(100.0)
        metrics.record_success(500.0)
        metrics.record_success(200.0)

        assert metrics.max_sync_lag_ms == 500.0

    def test_metrics_to_prometheus(self) -> None:
        """to_prometheus exports Prometheus format."""
        metrics = SynapseMetrics()
        metrics.record_success(100.0)
        metrics.record_failure()

        prom = metrics.to_prometheus()

        assert "synapse_events_processed_total 1" in prom
        assert "synapse_events_failed_total 1" in prom
        assert "synapse_sync_lag_ms" in prom

    def test_metrics_to_dict(self) -> None:
        """to_dict exports JSON-compatible dict."""
        metrics = SynapseMetrics()
        metrics.record_success(100.0)

        d = metrics.to_dict()

        assert d["events_processed"] == 1
        assert d["avg_sync_lag_ms"] == 100.0
        assert d["last_successful_sync"] is not None


# ===========================================================================
# RobustSynapseProcessor Tests
# ===========================================================================


class TestRobustSynapseProcessor:
    """Tests for RobustSynapseProcessor integration."""

    @pytest.fixture(autouse=True)
    def reset_global_dlq(self) -> None:
        """Reset global DLQ before each test."""
        reset_dlq()

    @pytest.mark.asyncio
    async def test_robust_processor_succeeds(self) -> None:
        """RobustSynapseProcessor processes events successfully."""
        config = SynapseConfig()
        processor = RobustSynapseProcessor(config=config)

        event = ChangeEvent.insert("memories", "1", {"content": "test"})
        results = await processor.invoke(event)

        assert len(results) == 1
        assert results[0].success

    @pytest.mark.asyncio
    async def test_robust_processor_retries_on_failure(self) -> None:
        """RobustSynapseProcessor retries on transient failures."""
        vector_store = FailingVectorStore()
        vector_store.failures_remaining = 2  # Fail twice, then succeed

        config = SynapseConfig(
            retry_config=RetryConfig(
                max_retries=3,
                initial_delay_ms=10,  # Fast for testing
            ),
        )
        processor = RobustSynapseProcessor(
            config=config,
            embedding_provider=MockEmbeddingProvider(),
            vector_store=vector_store,
        )

        event = ChangeEvent.insert("memories", "1", {"content": "test"})
        results = await processor.invoke(event)

        # Should succeed after retries
        assert results[0].success
        assert processor.metrics.events_retried >= 1
        assert vector_store.failure_count == 2

    @pytest.mark.asyncio
    async def test_robust_processor_sends_to_dlq_after_max_retries(self) -> None:
        """RobustSynapseProcessor sends to DLQ after max retries."""
        vector_store = FailingVectorStore()
        vector_store.failures_remaining = 10  # Always fail

        config = SynapseConfig(
            use_dlq=True,
            retry_config=RetryConfig(
                max_retries=2,
                initial_delay_ms=1,
            ),
        )
        processor = RobustSynapseProcessor(
            config=config,
            embedding_provider=MockEmbeddingProvider(),
            vector_store=vector_store,
        )

        event = ChangeEvent.insert("memories", "1", {"content": "test"})
        results = await processor.invoke(event)

        # Should fail after retries
        assert not results[0].success
        assert results[0].error is not None
        assert "Max retries exceeded" in results[0].error

        # Should be in DLQ
        dlq = get_dlq()
        assert dlq.size == 1
        assert processor.metrics.events_in_dlq == 1

    @pytest.mark.asyncio
    async def test_robust_processor_tracks_metrics(self) -> None:
        """RobustSynapseProcessor tracks metrics."""
        config = SynapseConfig()
        metrics = SynapseMetrics()
        processor = RobustSynapseProcessor(config=config, metrics=metrics)

        # Process several events
        for i in range(5):
            event = ChangeEvent.insert("memories", str(i), {"content": f"test {i}"})
            await processor.invoke(event)

        assert metrics.events_processed == 5
        assert metrics.avg_sync_lag_ms > 0

    @pytest.mark.asyncio
    async def test_create_robust_synapse_factory(self) -> None:
        """create_robust_synapse creates FluxAgent."""
        synapse = create_robust_synapse()

        assert synapse.name == "Flux(RobustSynapseProcessor)"

    @pytest.mark.asyncio
    async def test_robust_synapse_processes_stream(self) -> None:
        """Robust Synapse processes event stream."""
        synapse = create_robust_synapse()

        async def event_source():
            yield ChangeEvent.insert("users", "1", {"content": "Hello"})
            yield ChangeEvent.update("users", "1", {"content": "Updated"})

        results_list = []
        async for results in synapse.start(event_source()):
            results_list.append(results)

        assert len(results_list) == 2


# ===========================================================================
# Exponential Backoff Timing Tests
# ===========================================================================


class TestExponentialBackoffTiming:
    """Tests verifying actual exponential backoff behavior."""

    @pytest.mark.asyncio
    async def test_actual_delay_increases_exponentially(self) -> None:
        """Delays between retries increase exponentially."""
        vector_store = FailingVectorStore()
        vector_store.failures_remaining = 3

        config = SynapseConfig(
            retry_config=RetryConfig(
                max_retries=3,
                initial_delay_ms=50,
                exponential_base=2.0,
            ),
        )
        processor = RobustSynapseProcessor(
            config=config,
            embedding_provider=MockEmbeddingProvider(),
            vector_store=vector_store,
        )

        event = ChangeEvent.insert("memories", "1", {"content": "test"})

        start = time.time()
        await processor.invoke(event)
        elapsed = time.time() - start

        # Should have delays: 50ms + 100ms + 200ms = 350ms minimum
        # Allow some tolerance for execution time
        assert elapsed >= 0.3  # At least 300ms of delay


# ===========================================================================
# Circuit Breaker Integration Tests
# ===========================================================================


class TestCircuitBreakerIntegration:
    """Tests for circuit breaker integrated with RobustSynapseProcessor."""

    @pytest.fixture(autouse=True)
    def reset_global_dlq(self) -> None:
        """Reset global DLQ before each test."""
        reset_dlq()

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_repeated_failures(self) -> None:
        """Circuit opens when Qdrant fails repeatedly."""
        from agents.flux.circuit_breaker import CircuitBreakerConfig

        vector_store = FailingVectorStore()
        vector_store.failures_remaining = 100  # Always fail

        config = SynapseConfig(
            use_circuit_breaker=True,
            use_dlq=True,
            retry_config=RetryConfig(
                max_retries=1,
                initial_delay_ms=1,
            ),
        )
        processor = RobustSynapseProcessor(
            config=config,
            embedding_provider=MockEmbeddingProvider(),
            vector_store=vector_store,
        )

        # Override circuit breaker with lower threshold for test
        processor._circuit_breaker.config = CircuitBreakerConfig(failure_threshold=3)

        # Process multiple events to trigger circuit opening
        for i in range(10):
            event = ChangeEvent.insert("memories", str(i), {"content": "test"})
            await processor.invoke(event)

        # Circuit should be open (after 3 failures with threshold of 3)
        assert processor._circuit_breaker is not None
        assert processor._circuit_breaker.is_open
