"""
Tests for Synapse CDC FluxAgent.

The Synapse maintains the functorial relationship between:
- Postgres (ANCHOR) - Source of truth
- Qdrant (ASSOCIATOR) - Semantic search derived view
- Redis (SPARK) - Cache derived view

Test Categories:
1. ChangeEvent construction and helpers
2. SyncResult construction and helpers
3. SynapseProcessor discrete agent
4. Synapse FluxAgent integration
5. CDC lag tracking
6. Functor law verification
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import pytest
from agents.flux.synapse import (
    CDCLagTracker,
    ChangeEvent,
    ChangeOperation,
    SynapseConfig,
    SynapseProcessor,
    SyncOperation,
    SyncResult,
    SyncTarget,
    create_synapse,
    poll_outbox,
)

# ===========================================================================
# Test Fixtures: Mock Providers
# ===========================================================================


@dataclass
class MockEmbeddingProvider:
    """Mock embedding provider for tests."""

    dimension: int = 128
    calls: list[str] = field(default_factory=list)

    async def embed(self, text: str) -> list[float]:
        """Return deterministic mock embedding."""
        self.calls.append(text)
        # Deterministic embedding based on text hash
        seed = hash(text) % 1000
        return [float(seed + i) / 1000 for i in range(self.dimension)]


@dataclass
class MockVectorStore:
    """Mock vector store for tests."""

    upserts: list[tuple[str, str, list[float], dict[str, Any]]] = field(
        default_factory=list
    )
    deletes: list[tuple[str, str]] = field(default_factory=list)

    async def upsert(
        self,
        collection: str,
        id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Record upsert for verification."""
        self.upserts.append((collection, id, vector, payload))

    async def delete(self, collection: str, id: str) -> None:
        """Record delete for verification."""
        self.deletes.append((collection, id))


@dataclass
class MockCacheStore:
    """Mock cache store for tests."""

    invalidations: list[str] = field(default_factory=list)

    async def invalidate(self, key: str) -> None:
        """Record invalidation for verification."""
        self.invalidations.append(key)


# ===========================================================================
# ChangeEvent Tests
# ===========================================================================


class TestChangeEvent:
    """Tests for ChangeEvent dataclass."""

    def test_change_event_creation(self) -> None:
        """ChangeEvent can be created directly."""
        event = ChangeEvent(
            table="users",
            operation=ChangeOperation.INSERT,
            row_id="123",
            data={"name": "Alice"},
        )

        assert event.table == "users"
        assert event.operation == ChangeOperation.INSERT
        assert event.row_id == "123"
        assert event.data == {"name": "Alice"}

    def test_change_event_insert_helper(self) -> None:
        """insert() creates INSERT event."""
        event = ChangeEvent.insert(
            table="users",
            row_id="123",
            data={"name": "Alice"},
            sequence_id=1,
        )

        assert event.operation == ChangeOperation.INSERT
        assert event.sequence_id == 1

    def test_change_event_update_helper(self) -> None:
        """update() creates UPDATE event."""
        event = ChangeEvent.update(
            table="users",
            row_id="123",
            data={"name": "Alice Updated"},
        )

        assert event.operation == ChangeOperation.UPDATE

    def test_change_event_delete_helper(self) -> None:
        """delete() creates DELETE event with empty data."""
        event = ChangeEvent.delete(table="users", row_id="123")

        assert event.operation == ChangeOperation.DELETE
        assert event.data == {}

    def test_change_event_timestamp(self) -> None:
        """ChangeEvent has timestamp."""
        event = ChangeEvent.insert("users", "1", {"x": 1})

        assert event.timestamp_ms > 0

    def test_change_event_is_frozen(self) -> None:
        """ChangeEvent is immutable."""
        event = ChangeEvent.insert("users", "1", {"x": 1})

        with pytest.raises(AttributeError):
            event.table = "other"  # type: ignore


# ===========================================================================
# SyncResult Tests
# ===========================================================================


class TestSyncResult:
    """Tests for SyncResult dataclass."""

    def test_sync_result_success_upsert(self) -> None:
        """success_upsert() creates successful upsert result."""
        result = SyncResult.success_upsert(
            target=SyncTarget.QDRANT,
            lag_ms=10.5,
            sequence=42,
        )

        assert result.target == SyncTarget.QDRANT
        assert result.operation == SyncOperation.UPSERT
        assert result.success is True
        assert result.lag_ms == 10.5
        assert result.source_sequence == 42
        assert result.error is None

    def test_sync_result_success_delete(self) -> None:
        """success_delete() creates successful delete result."""
        result = SyncResult.success_delete(
            target=SyncTarget.QDRANT,
            lag_ms=5.0,
        )

        assert result.operation == SyncOperation.DELETE
        assert result.success is True

    def test_sync_result_failed(self) -> None:
        """failed() creates failed result with error."""
        result = SyncResult.failed(
            target=SyncTarget.QDRANT,
            operation=SyncOperation.UPSERT,
            error="Connection refused",
            sequence=10,
        )

        assert result.success is False
        assert result.error == "Connection refused"
        assert result.lag_ms == 0.0

    def test_sync_result_is_frozen(self) -> None:
        """SyncResult is immutable."""
        result = SyncResult.success_upsert(SyncTarget.QDRANT, 1.0)

        with pytest.raises(AttributeError):
            result.success = False  # type: ignore


# ===========================================================================
# SynapseProcessor Tests
# ===========================================================================


class TestSynapseProcessor:
    """Tests for the discrete SynapseProcessor agent."""

    @pytest.fixture
    def mock_providers(
        self,
    ) -> tuple[MockEmbeddingProvider, MockVectorStore, MockCacheStore]:
        """Create mock providers."""
        return MockEmbeddingProvider(), MockVectorStore(), MockCacheStore()

    @pytest.fixture
    def processor(
        self,
        mock_providers: tuple[MockEmbeddingProvider, MockVectorStore, MockCacheStore],
    ) -> SynapseProcessor:
        """Create processor with mocks."""
        embedder, vector, cache = mock_providers
        return SynapseProcessor(
            config=SynapseConfig(sync_to_qdrant=True, sync_to_redis=True),
            embedding_provider=embedder,
            vector_store=vector,
            cache_store=cache,
        )

    @pytest.mark.asyncio
    async def test_processor_name(self, processor: SynapseProcessor) -> None:
        """Processor has name."""
        assert processor.name == "SynapseProcessor"

    @pytest.mark.asyncio
    async def test_processor_insert_event(
        self,
        processor: SynapseProcessor,
        mock_providers: tuple[MockEmbeddingProvider, MockVectorStore, MockCacheStore],
    ) -> None:
        """INSERT event triggers upsert to Qdrant."""
        embedder, vector, cache = mock_providers
        event = ChangeEvent.insert(
            table="memories",
            row_id="mem-1",
            data={"content": "Hello world"},
        )

        results = await processor.invoke(event)

        # Should have results for both targets
        assert len(results) == 2

        # Check Qdrant result
        qdrant_result = next(r for r in results if r.target == SyncTarget.QDRANT)
        assert qdrant_result.success is True
        assert qdrant_result.operation == SyncOperation.UPSERT

        # Check embedding was computed
        assert "Hello world" in embedder.calls

        # Check vector was stored
        assert len(vector.upserts) == 1
        collection, id_, vec, payload = vector.upserts[0]
        assert collection == "memories"
        assert id_ == "mem-1"
        assert len(vec) == 128  # MockEmbeddingProvider dimension

    @pytest.mark.asyncio
    async def test_processor_update_event(
        self,
        processor: SynapseProcessor,
        mock_providers: tuple[MockEmbeddingProvider, MockVectorStore, MockCacheStore],
    ) -> None:
        """UPDATE event triggers upsert to Qdrant."""
        _, vector, _ = mock_providers
        event = ChangeEvent.update(
            table="memories",
            row_id="mem-1",
            data={"content": "Updated content"},
        )

        results = await processor.invoke(event)

        qdrant_result = next(r for r in results if r.target == SyncTarget.QDRANT)
        assert qdrant_result.success is True
        assert qdrant_result.operation == SyncOperation.UPSERT
        assert len(vector.upserts) == 1

    @pytest.mark.asyncio
    async def test_processor_delete_event(
        self,
        processor: SynapseProcessor,
        mock_providers: tuple[MockEmbeddingProvider, MockVectorStore, MockCacheStore],
    ) -> None:
        """DELETE event triggers delete from Qdrant."""
        _, vector, _ = mock_providers
        event = ChangeEvent.delete(table="memories", row_id="mem-1")

        results = await processor.invoke(event)

        qdrant_result = next(r for r in results if r.target == SyncTarget.QDRANT)
        assert qdrant_result.success is True
        assert qdrant_result.operation == SyncOperation.DELETE
        assert ("memories", "mem-1") in vector.deletes

    @pytest.mark.asyncio
    async def test_processor_redis_invalidation(
        self,
        processor: SynapseProcessor,
        mock_providers: tuple[MockEmbeddingProvider, MockVectorStore, MockCacheStore],
    ) -> None:
        """Events trigger cache invalidation in Redis."""
        _, _, cache = mock_providers
        event = ChangeEvent.insert(
            table="memories",
            row_id="mem-1",
            data={"content": "Hello"},
        )

        results = await processor.invoke(event)

        redis_result = next(r for r in results if r.target == SyncTarget.REDIS)
        assert redis_result.success is True
        assert redis_result.operation == SyncOperation.INVALIDATE
        assert "memories:mem-1" in cache.invalidations

    @pytest.mark.asyncio
    async def test_processor_lag_tracking(
        self,
        processor: SynapseProcessor,
    ) -> None:
        """Results include CDC lag measurement."""
        event = ChangeEvent.insert("memories", "1", {"content": "test"})

        results = await processor.invoke(event)

        for result in results:
            assert result.lag_ms >= 0.0

    @pytest.mark.asyncio
    async def test_processor_mock_mode(self) -> None:
        """Processor works in mock mode (no providers)."""
        processor = SynapseProcessor(config=SynapseConfig())
        event = ChangeEvent.insert("memories", "1", {"content": "test"})

        results = await processor.invoke(event)

        # Should succeed (no-op in mock mode)
        assert len(results) == 1
        assert results[0].success is True

    @pytest.mark.asyncio
    async def test_processor_empty_content_skipped(
        self,
        mock_providers: tuple[MockEmbeddingProvider, MockVectorStore, MockCacheStore],
    ) -> None:
        """Events with empty content are skipped for embedding."""
        embedder, vector, _ = mock_providers
        processor = SynapseProcessor(
            config=SynapseConfig(text_field="content"),
            embedding_provider=embedder,
            vector_store=vector,
        )
        event = ChangeEvent.insert("memories", "1", {"other_field": "value"})

        await processor.invoke(event)

        # No embedding should be computed for missing field
        assert len(embedder.calls) == 0


# ===========================================================================
# Synapse FluxAgent Tests
# ===========================================================================


class TestSynapseFluxAgent:
    """Tests for the Synapse FluxAgent."""

    @pytest.mark.asyncio
    async def test_create_synapse_basic(self) -> None:
        """create_synapse() returns FluxAgent."""
        synapse = create_synapse()

        assert synapse.name == "Flux(SynapseProcessor)"

    @pytest.mark.asyncio
    async def test_synapse_processes_stream(self) -> None:
        """Synapse processes event stream."""
        synapse = create_synapse()

        async def event_source() -> Any:
            yield ChangeEvent.insert("users", "1", {"content": "Hello"})
            yield ChangeEvent.update("users", "1", {"content": "Updated"})
            yield ChangeEvent.delete("users", "1")

        results_list: list[list[SyncResult]] = []
        async for results in synapse.start(event_source()):
            results_list.append(results)

        assert len(results_list) == 3

    @pytest.mark.asyncio
    async def test_synapse_with_providers(self) -> None:
        """Synapse integrates with providers."""
        embedder = MockEmbeddingProvider()
        vector = MockVectorStore()

        synapse = create_synapse(
            embedding_provider=embedder,
            vector_store=vector,
        )

        async def event_source() -> Any:
            yield ChangeEvent.insert("memories", "1", {"content": "Test"})

        async for _ in synapse.start(event_source()):
            pass

        assert len(embedder.calls) == 1
        assert len(vector.upserts) == 1

    @pytest.mark.asyncio
    async def test_synapse_discrete_invoke(self) -> None:
        """Synapse can be invoked discretely when DORMANT."""
        synapse = create_synapse()
        event = ChangeEvent.insert("users", "1", {"content": "test"})

        results = await synapse.invoke(event)

        assert len(results) == 1


# ===========================================================================
# CDC Lag Tracker Tests
# ===========================================================================


class TestCDCLagTracker:
    """Tests for CDCLagTracker."""

    def test_tracker_empty(self) -> None:
        """Empty tracker returns 0."""
        tracker = CDCLagTracker()

        assert tracker.avg_lag_ms == 0.0
        assert tracker.max_lag_ms == 0.0
        assert tracker.coherency == 1.0

    def test_tracker_record_samples(self) -> None:
        """Tracker records and averages samples."""
        tracker = CDCLagTracker()
        tracker.record(100.0)
        tracker.record(200.0)
        tracker.record(300.0)

        assert tracker.avg_lag_ms == 200.0
        assert tracker.max_lag_ms == 300.0

    def test_tracker_coherency_perfect(self) -> None:
        """Zero lag = perfect coherency."""
        tracker = CDCLagTracker()
        tracker.record(0.0)

        assert tracker.coherency == 1.0

    def test_tracker_coherency_degrades(self) -> None:
        """Coherency degrades with lag."""
        tracker = CDCLagTracker()
        tracker.record(2500.0)  # Half of threshold

        assert tracker.coherency == 0.5

    def test_tracker_coherency_threshold(self) -> None:
        """5000ms lag = 0 coherency."""
        tracker = CDCLagTracker()
        tracker.record(5000.0)

        assert tracker.coherency == 0.0

    def test_tracker_coherency_beyond_threshold(self) -> None:
        """Beyond threshold = 0 coherency (not negative)."""
        tracker = CDCLagTracker()
        tracker.record(10000.0)

        assert tracker.coherency == 0.0

    def test_tracker_max_samples(self) -> None:
        """Tracker limits stored samples."""
        tracker = CDCLagTracker()
        tracker._max_samples = 5

        for i in range(10):
            tracker.record(float(i))

        assert len(tracker._samples) == 5
        # Should keep recent samples (5-9)
        assert tracker._samples == [5.0, 6.0, 7.0, 8.0, 9.0]


# ===========================================================================
# Outbox Polling Tests
# ===========================================================================


class TestPollOutbox:
    """Tests for poll_outbox helper."""

    @pytest.mark.asyncio
    async def test_poll_outbox_flattens_batches(self) -> None:
        """poll_outbox flattens batched events."""

        async def batch_source() -> Any:
            yield [
                ChangeEvent.insert("t", "1", {}),
                ChangeEvent.insert("t", "2", {}),
            ]
            yield [
                ChangeEvent.insert("t", "3", {}),
            ]

        events = [e async for e in poll_outbox(batch_source())]

        assert len(events) == 3
        assert [e.row_id for e in events] == ["1", "2", "3"]

    @pytest.mark.asyncio
    async def test_poll_outbox_empty_batch(self) -> None:
        """Empty batches are handled."""

        async def batch_source() -> Any:
            yield []
            yield [ChangeEvent.insert("t", "1", {})]
            yield []

        events = [e async for e in poll_outbox(batch_source())]

        assert len(events) == 1


# ===========================================================================
# Functor Law Tests
# ===========================================================================


class TestFunctorLaws:
    """Tests verifying the Synapse satisfies functor laws."""

    @pytest.mark.asyncio
    async def test_identity_law(self) -> None:
        """
        Synapse(id_A) = id_{Synapse(A)}

        No change in Postgres means no change in Qdrant state.
        For this test, we verify that processing no events
        results in no operations performed.
        """
        vector = MockVectorStore()
        synapse = create_synapse(vector_store=vector)

        async def empty_source() -> Any:
            return
            yield  # Make it a generator

        async for _ in synapse.start(empty_source()):
            pass

        # No operations should have been performed
        assert len(vector.upserts) == 0
        assert len(vector.deletes) == 0

    @pytest.mark.asyncio
    async def test_composition_law(self) -> None:
        """
        Synapse(g ∘ f) = Synapse(g) ∘ Synapse(f)

        Sequential changes compose correctly in the derived view.
        INSERT followed by UPDATE is equivalent to the final state.
        """
        vector = MockVectorStore()
        synapse = create_synapse(
            embedding_provider=MockEmbeddingProvider(),
            vector_store=vector,
        )

        async def sequential_events() -> Any:
            # f: insert with initial content
            yield ChangeEvent.insert("t", "1", {"content": "initial"})
            # g: update to final content
            yield ChangeEvent.update("t", "1", {"content": "final"})

        async for _ in synapse.start(sequential_events()):
            pass

        # Both operations should have been applied
        assert len(vector.upserts) == 2

        # The final state in Qdrant should reflect the composition
        final_upsert = vector.upserts[-1]
        _, id_, _, payload = final_upsert
        assert id_ == "1"
        assert payload["content"] == "final"

    @pytest.mark.asyncio
    async def test_delete_after_insert_removes_state(self) -> None:
        """
        DELETE ∘ INSERT = ∅ (empty state)

        Insert followed by delete should result in deletion.
        """
        vector = MockVectorStore()
        synapse = create_synapse(vector_store=vector)

        async def insert_then_delete() -> Any:
            yield ChangeEvent.insert("t", "1", {"content": "test"})
            yield ChangeEvent.delete("t", "1")

        async for _ in synapse.start(insert_then_delete()):
            pass

        # Should have one delete operation
        assert ("memories", "1") in vector.deletes


# ===========================================================================
# OutboxSource Tests
# ===========================================================================


from datetime import datetime, timezone

from agents.flux.sources.outbox import (
    MockConnection,
    MockConnectionPool,
    OutboxConfig,
    OutboxSource,
)


class TestOutboxSource:
    """Tests for OutboxSource CDC event polling."""

    @pytest.fixture
    def mock_events(self) -> list[dict[str, Any]]:
        """Create mock outbox events."""
        now = datetime.now(timezone.utc)
        return [
            {
                "id": 1,
                "event_type": "INSERT",
                "table_name": "memories",
                "row_id": "mem-1",
                "payload": {"content": "First memory"},
                "created_at": now,
            },
            {
                "id": 2,
                "event_type": "UPDATE",
                "table_name": "memories",
                "row_id": "mem-1",
                "payload": {"content": "Updated memory"},
                "created_at": now,
            },
            {
                "id": 3,
                "event_type": "DELETE",
                "table_name": "memories",
                "row_id": "mem-1",
                "payload": {},
                "created_at": now,
            },
        ]

    @pytest.mark.asyncio
    async def test_outbox_source_yields_events(
        self, mock_events: list[dict[str, Any]]
    ) -> None:
        """OutboxSource yields ChangeEvents from outbox rows."""
        mock_conn = MockConnection(pending_events=mock_events.copy())
        pool = MockConnectionPool(mock_conn)
        source = OutboxSource(pool)

        events: list[ChangeEvent] = []
        count = 0
        async for event in source:
            events.append(event)
            count += 1
            if count >= 3:
                source.close()
                break

        assert len(events) == 3
        assert events[0].operation == ChangeOperation.INSERT
        assert events[1].operation == ChangeOperation.UPDATE
        assert events[2].operation == ChangeOperation.DELETE

    @pytest.mark.asyncio
    async def test_outbox_source_converts_row_correctly(
        self, mock_events: list[dict[str, Any]]
    ) -> None:
        """OutboxSource correctly converts rows to ChangeEvents."""
        mock_conn = MockConnection(pending_events=[mock_events[0]])
        pool = MockConnectionPool(mock_conn)
        source = OutboxSource(pool)

        event = await source.__anext__()
        source.close()

        assert event.table == "memories"
        assert event.row_id == "mem-1"
        assert event.data == {"content": "First memory"}
        assert event.sequence_id == 1

    @pytest.mark.asyncio
    async def test_outbox_source_acknowledge(
        self, mock_events: list[dict[str, Any]]
    ) -> None:
        """acknowledge() marks event as processed."""
        mock_conn = MockConnection(pending_events=[mock_events[0]])
        pool = MockConnectionPool(mock_conn)
        source = OutboxSource(pool)

        event = await source.__anext__()
        await source.acknowledge(event.sequence_id)
        source.close()

        # Check that execute was called with the ID
        assert len(mock_conn.execute_calls) == 1
        assert mock_conn.processed_ids == [1]

    @pytest.mark.asyncio
    async def test_outbox_source_acknowledge_batch(
        self, mock_events: list[dict[str, Any]]
    ) -> None:
        """acknowledge_batch() marks multiple events as processed."""
        mock_conn = MockConnection(pending_events=mock_events.copy())
        pool = MockConnectionPool(mock_conn)
        source = OutboxSource(pool)

        events = []
        count = 0
        async for event in source:
            events.append(event)
            count += 1
            if count >= 3:
                break

        await source.acknowledge_batch([e.sequence_id for e in events if e.sequence_id])
        source.close()

        # Mock stores the batch as a list within the processed_ids
        assert any(
            batch == [1, 2, 3]  # type: ignore[comparison-overlap]
            for batch in mock_conn.processed_ids
            if isinstance(batch, list)
        )

    @pytest.mark.asyncio
    async def test_outbox_source_respects_batch_size(self) -> None:
        """OutboxSource fetches up to batch_size events."""
        many_events = [
            {
                "id": i,
                "event_type": "INSERT",
                "table_name": "t",
                "row_id": str(i),
                "payload": {},
                "created_at": datetime.now(timezone.utc),
            }
            for i in range(10)
        ]
        mock_conn = MockConnection(pending_events=many_events)
        pool = MockConnectionPool(mock_conn)
        config = OutboxConfig(batch_size=3)
        source = OutboxSource(pool, config)

        # Fetch first batch
        events = []
        for _ in range(3):
            events.append(await source.__anext__())
        source.close()

        # Fetch call should have been made with batch_size
        assert mock_conn.fetch_calls[0][1] == (3,)

    @pytest.mark.asyncio
    async def test_outbox_source_close(self) -> None:
        """close() stops the source."""
        mock_conn = MockConnection()
        pool = MockConnectionPool(mock_conn)
        source = OutboxSource(pool)

        source.close()

        assert source.is_stopped

    @pytest.mark.asyncio
    async def test_outbox_source_skip_acknowledge_when_disabled(
        self, mock_events: list[dict[str, Any]]
    ) -> None:
        """acknowledge() is no-op when mark_processed is False."""
        mock_conn = MockConnection(pending_events=[mock_events[0]])
        pool = MockConnectionPool(mock_conn)
        config = OutboxConfig(mark_processed=False)
        source = OutboxSource(pool, config)

        event = await source.__anext__()
        await source.acknowledge(event.sequence_id)
        source.close()

        # No execute call should have been made
        assert len(mock_conn.execute_calls) == 0

    @pytest.mark.asyncio
    async def test_outbox_source_handles_json_payload(self) -> None:
        """OutboxSource handles JSON string payloads."""
        import json

        event_with_json = {
            "id": 1,
            "event_type": "INSERT",
            "table_name": "t",
            "row_id": "1",
            "payload": json.dumps({"key": "value"}),  # JSON string
            "created_at": datetime.now(timezone.utc),
        }
        mock_conn = MockConnection(pending_events=[event_with_json])
        pool = MockConnectionPool(mock_conn)
        source = OutboxSource(pool)

        event = await source.__anext__()
        source.close()

        assert event.data == {"key": "value"}

    @pytest.mark.asyncio
    async def test_outbox_source_context_manager(
        self, mock_events: list[dict[str, Any]]
    ) -> None:
        """OutboxSource works as async context manager."""
        mock_conn = MockConnection(pending_events=[mock_events[0]])
        pool = MockConnectionPool(mock_conn)
        source = OutboxSource(pool)

        async with source as s:
            event = await s.__anext__()
            assert event.table == "memories"

        assert source.is_stopped


class TestOutboxSynapseIntegration:
    """Tests for OutboxSource + Synapse integration."""

    @pytest.mark.asyncio
    async def test_outbox_to_synapse_pipeline(self) -> None:
        """OutboxSource feeds Synapse for end-to-end CDC."""
        now = datetime.now(timezone.utc)
        outbox_events = [
            {
                "id": 1,
                "event_type": "INSERT",
                "table_name": "memories",
                "row_id": "mem-1",
                "payload": {"content": "Test content"},
                "created_at": now,
            },
        ]

        mock_conn = MockConnection(pending_events=outbox_events)
        pool = MockConnectionPool(mock_conn)
        source = OutboxSource(pool)

        embedder = MockEmbeddingProvider()
        vector = MockVectorStore()
        synapse = create_synapse(
            embedding_provider=embedder,
            vector_store=vector,
        )

        # Process through pipeline
        async for event in source:
            results = await synapse.invoke(event)
            assert all(r.success for r in results)
            await source.acknowledge(event.sequence_id)
            source.close()
            break

        # Verify end-to-end flow
        assert len(embedder.calls) == 1
        assert len(vector.upserts) == 1
        assert mock_conn.processed_ids == [1]
