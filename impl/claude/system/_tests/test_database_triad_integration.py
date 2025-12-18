"""
Integration tests for the Database Triad CDC pipeline.

End-to-end validation of:
- Postgres -> Outbox -> Synapse -> Qdrant flow
- CDC lag tracking
- Qdrant rebuild from Postgres
- Concurrent write consistency
- Partial failure recovery

Test Categories:
1. Basic CDC flow (INSERT, UPDATE, DELETE)
2. Lag tracking accuracy
3. Rebuild capability
4. Concurrent writes
5. Failure scenarios
6. Functor law verification
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import pytest

from agents.flux.semantic_metrics import (
    QdrantPulse,
    ResonanceSignal,
)
from agents.flux.synapse import (
    ChangeEvent,
    ChangeOperation,
    SyncOperation,
    SyncTarget,
)

from .conftest import TriadFixture

# ===========================================================================
# Basic CDC Flow Tests
# ===========================================================================


class TestBasicCDCFlow:
    """End-to-end CDC validation with mock infrastructure."""

    @pytest.mark.asyncio
    async def test_insert_propagates_to_qdrant(self, triad: TriadFixture) -> None:
        """
        INSERT in Postgres -> Outbox -> Synapse -> Qdrant.

        The categorical guarantee: Synapse(insert) = vector_upsert.
        """
        # Insert row in Postgres
        row_id = await triad.postgres.insert(
            "memories",
            {"id": "mem-1", "content": "Hello world"},
        )

        # Process outbox through Synapse
        results = await triad.process_pending_events()

        # Verify sync succeeded
        assert len(results) > 0
        assert all(r.success for r in results)

        # Verify vector exists in Qdrant
        vector = await triad.qdrant.get("memories", row_id)
        assert vector is not None
        assert vector["payload"]["content"] == "Hello world"

    @pytest.mark.asyncio
    async def test_update_updates_vector(self, triad: TriadFixture) -> None:
        """UPDATE in Postgres updates vector in Qdrant."""
        # Insert initial
        row_id = await triad.postgres.insert(
            "memories",
            {"id": "mem-1", "content": "Initial content"},
        )
        await triad.process_pending_events()

        # Update
        await triad.postgres.update(
            "memories",
            row_id,
            {"content": "Updated content"},
        )
        await triad.process_pending_events()

        # Verify update
        vector = await triad.qdrant.get("memories", row_id)
        assert vector is not None
        assert vector["payload"]["content"] == "Updated content"

    @pytest.mark.asyncio
    async def test_delete_removes_vector(self, triad: TriadFixture) -> None:
        """DELETE in Postgres removes vector from Qdrant."""
        # Insert
        row_id = await triad.postgres.insert(
            "memories",
            {"id": "mem-1", "content": "To be deleted"},
        )
        await triad.process_pending_events()

        # Verify exists
        assert await triad.qdrant.get("memories", row_id) is not None

        # Delete
        await triad.postgres.delete("memories", row_id)
        await triad.process_pending_events()

        # Verify removed
        assert await triad.qdrant.get("memories", row_id) is None

    @pytest.mark.asyncio
    async def test_multiple_operations_in_order(self, triad: TriadFixture) -> None:
        """Multiple operations maintain order."""
        # Insert several rows
        ids = []
        for i in range(5):
            row_id = await triad.postgres.insert(
                "memories",
                {"id": f"mem-{i}", "content": f"Memory {i}"},
            )
            ids.append(row_id)

        # Process all
        await triad.process_pending_events()

        # Verify all exist
        count = await triad.qdrant.count("memories")
        assert count == 5

        # Verify order preserved in content
        for i, row_id in enumerate(ids):
            vector = await triad.qdrant.get("memories", row_id)
            assert vector is not None
            assert vector["payload"]["content"] == f"Memory {i}"


# ===========================================================================
# CDC Lag Tracking Tests
# ===========================================================================


class TestCDCLagTracking:
    """Tests for CDC lag tracking accuracy."""

    @pytest.mark.asyncio
    async def test_lag_recorded_on_sync(self, triad: TriadFixture) -> None:
        """Lag is recorded for each successful sync."""
        await triad.postgres.insert("memories", {"content": "Test"})
        await triad.process_pending_events()

        # Lag should be recorded
        assert len(triad.lag_tracker._samples) > 0
        assert triad.lag_tracker.avg_lag_ms >= 0

    @pytest.mark.asyncio
    async def test_lag_tracker_coherency_integration(self, triad: TriadFixture) -> None:
        """
        CDC lag feeds into ResonanceSignal.coherency_with_truth.

        This is the key categorical invariant.
        """
        # Insert several items
        for i in range(5):
            await triad.postgres.insert("memories", {"content": f"Memory {i}"})

        # Process (lag should be very low in mock)
        await triad.process_pending_events()

        # Create Qdrant pulse
        pulse = QdrantPulse(
            vector_count=5,
            avg_search_latency_ms=20.0,
            memory_mb=256.0,
        )

        # Verify coherency uses lag tracker
        signal = ResonanceSignal.from_synapse_lag(triad.lag_tracker, pulse)

        # Low lag should mean high coherency
        assert signal.coherency_with_truth > 0.9

    @pytest.mark.asyncio
    async def test_coherency_degrades_with_simulated_lag(self, triad: TriadFixture) -> None:
        """Coherency degrades when CDC lag is simulated."""
        # Manually record high lag samples
        for _ in range(10):
            triad.lag_tracker.record(3000.0)  # 3 second lag

        pulse = QdrantPulse(
            vector_count=100,
            avg_search_latency_ms=30.0,
            memory_mb=256.0,
        )

        signal = ResonanceSignal.from_synapse_lag(triad.lag_tracker, pulse)

        # High lag = degraded coherency
        # 3000ms / 5000ms threshold = 0.4 coherency
        assert signal.coherency_with_truth == 0.4


# ===========================================================================
# Qdrant Rebuild Tests
# ===========================================================================


class TestQdrantRebuild:
    """Tests for Qdrant rebuild from Postgres."""

    @pytest.mark.asyncio
    async def test_rebuild_from_postgres(self, triad: TriadFixture) -> None:
        """
        Wipe Qdrant, rebuild from Postgres.

        Proof that Postgres is the sole source of truth.
        """
        # Populate data
        for i in range(10):
            await triad.postgres.insert(
                "memories",
                {"id": f"mem-{i}", "content": f"Memory {i}"},
            )
        await triad.process_pending_events()

        # Verify all in Qdrant
        assert await triad.qdrant.count("memories") == 10

        # Wipe Qdrant
        await triad.qdrant.delete_collection("memories")
        assert await triad.qdrant.count("memories") == 0

        # Rebuild from Postgres
        rebuilt = await triad.rebuild_qdrant_from_postgres("memories")

        # Verify all vectors restored
        assert rebuilt == 10
        assert await triad.qdrant.count("memories") == 10

    @pytest.mark.asyncio
    async def test_rebuild_preserves_content(self, triad: TriadFixture) -> None:
        """Rebuild preserves content fidelity."""
        # Insert with specific content
        await triad.postgres.insert(
            "memories",
            {"id": "special", "content": "Important data"},
        )
        await triad.process_pending_events()

        # Wipe and rebuild
        await triad.qdrant.delete_collection("memories")
        await triad.rebuild_qdrant_from_postgres("memories")

        # Verify content preserved
        vector = await triad.qdrant.get("memories", "special")
        assert vector is not None
        assert vector["payload"]["content"] == "Important data"


# ===========================================================================
# Concurrent Write Tests
# ===========================================================================


class TestConcurrentWrites:
    """Tests for concurrent write consistency."""

    @pytest.mark.asyncio
    async def test_concurrent_inserts_maintain_consistency(self, triad: TriadFixture) -> None:
        """
        Concurrent inserts don't cause data loss.

        Tests the outbox's exactly-once guarantee under load.
        """

        async def writer(prefix: str, count: int) -> None:
            for i in range(count):
                await triad.postgres.insert(
                    "memories",
                    {"id": f"{prefix}-{i}", "content": f"Writer {prefix} item {i}"},
                )

        # Concurrent writes from 3 writers
        await asyncio.gather(
            writer("A", 10),
            writer("B", 10),
            writer("C", 10),
        )

        # Process all
        await triad.process_pending_events()

        # Verify all 30 items in Qdrant
        count = await triad.qdrant.count("memories")
        assert count == 30

    @pytest.mark.asyncio
    async def test_mixed_operations_concurrent(self, triad: TriadFixture) -> None:
        """Concurrent mixed operations maintain consistency."""
        # Initial population
        for i in range(5):
            await triad.postgres.insert(
                "memories",
                {"id": f"mem-{i}", "content": f"Initial {i}"},
            )

        await triad.process_pending_events()

        async def updater() -> None:
            for i in range(5):
                await triad.postgres.update(
                    "memories",
                    f"mem-{i}",
                    {"content": f"Updated {i}"},
                )

        async def inserter() -> None:
            for i in range(5, 10):
                await triad.postgres.insert(
                    "memories",
                    {"id": f"mem-{i}", "content": f"New {i}"},
                )

        # Concurrent updates and inserts
        await asyncio.gather(updater(), inserter())
        await triad.process_pending_events()

        # Verify final state
        count = await triad.qdrant.count("memories")
        assert count == 10

        # Verify updates applied
        for i in range(5):
            vector = await triad.qdrant.get("memories", f"mem-{i}")
            assert vector is not None
            assert "Updated" in vector["payload"]["content"]


# ===========================================================================
# Partial Failure Tests
# ===========================================================================


class TestPartialFailureRecovery:
    """Tests for partial failure recovery."""

    @pytest.mark.asyncio
    async def test_unprocessed_events_remain_on_failure(self, triad: TriadFixture) -> None:
        """
        If Synapse fails mid-batch, unprocessed events remain.

        Tests the transactional outbox guarantee.
        """
        # Insert 5 events
        for i in range(5):
            await triad.postgres.insert(
                "memories",
                {"id": f"mem-{i}", "content": f"Item {i}"},
            )

        # Process only 2
        processed = await triad.process_n_events(2)
        assert processed == 2

        # Verify 3 still pending
        pending = triad.count_pending_outbox()
        assert pending == 3

        # Resume processing
        await triad.process_pending_events()

        # All should be in Qdrant now
        assert await triad.qdrant.count("memories") == 5

    @pytest.mark.asyncio
    async def test_idempotent_processing(self, triad: TriadFixture) -> None:
        """Processing same event twice is idempotent."""
        await triad.postgres.insert(
            "memories",
            {"id": "mem-1", "content": "Test"},
        )

        # Process twice
        await triad.process_pending_events()

        # Manually reprocess by creating event
        event = ChangeEvent.insert("memories", "mem-1", {"content": "Test"})
        await triad.synapse_processor.invoke(event)

        # Should still have 1 vector (upsert is idempotent)
        assert await triad.qdrant.count("memories") == 1


# ===========================================================================
# Functor Law Tests
# ===========================================================================


class TestFunctorLaws:
    """Tests verifying the Synapse satisfies functor laws in integration."""

    @pytest.mark.asyncio
    async def test_identity_law_integration(self, triad: TriadFixture) -> None:
        """
        Synapse(id_A) = id_{Synapse(A)}

        No changes in Postgres means no changes in Qdrant.
        """
        # Don't insert anything
        initial_count = await triad.qdrant.count("memories")

        # Process (nothing to process)
        await triad.process_pending_events()

        # Count unchanged
        assert await triad.qdrant.count("memories") == initial_count

    @pytest.mark.asyncio
    async def test_composition_law_integration(self, triad: TriadFixture) -> None:
        """
        Synapse(g . f) = Synapse(g) . Synapse(f)

        Sequential changes compose correctly.
        """
        # f: insert
        await triad.postgres.insert(
            "memories",
            {"id": "mem-1", "content": "initial"},
        )
        await triad.process_pending_events()

        # g: update
        await triad.postgres.update(
            "memories",
            "mem-1",
            {"content": "final"},
        )
        await triad.process_pending_events()

        # Final state is composition
        vector = await triad.qdrant.get("memories", "mem-1")
        assert vector is not None
        assert vector["payload"]["content"] == "final"

    @pytest.mark.asyncio
    async def test_delete_after_insert_is_empty(self, triad: TriadFixture) -> None:
        """
        DELETE . INSERT = empty

        Insert followed by delete should result in no vector.
        """
        row_id = await triad.postgres.insert(
            "memories",
            {"id": "ephemeral", "content": "temporary"},
        )
        await triad.process_pending_events()

        await triad.postgres.delete("memories", row_id)
        await triad.process_pending_events()

        # Should not exist
        assert await triad.qdrant.get("memories", row_id) is None


# ===========================================================================
# Edge Case Tests
# ===========================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_content_handled(self, triad: TriadFixture) -> None:
        """Events with empty content field are handled gracefully."""
        await triad.postgres.insert(
            "memories",
            {"id": "empty", "other_field": "value"},  # No 'content' field
        )
        results = await triad.process_pending_events()

        # Should succeed (no embedding computed)
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_large_content_handled(self, triad: TriadFixture) -> None:
        """Large content is handled correctly."""
        large_content = "x" * 10000  # 10KB of content
        await triad.postgres.insert(
            "memories",
            {"id": "large", "content": large_content},
        )
        await triad.process_pending_events()

        vector = await triad.qdrant.get("memories", "large")
        assert vector is not None
        assert len(vector["payload"]["content"]) == 10000

    @pytest.mark.asyncio
    async def test_unicode_content_preserved(self, triad: TriadFixture) -> None:
        """Unicode content is preserved through the pipeline."""
        unicode_content = "Hello \u4e16\u754c \ud83c\udf0d"  # Hello World in Chinese + globe emoji
        await triad.postgres.insert(
            "memories",
            {"id": "unicode", "content": unicode_content},
        )
        await triad.process_pending_events()

        vector = await triad.qdrant.get("memories", "unicode")
        assert vector is not None
        assert vector["payload"]["content"] == unicode_content

    @pytest.mark.asyncio
    async def test_special_characters_in_id(self, triad: TriadFixture) -> None:
        """Special characters in row ID are handled."""
        special_id = "row:with/special-chars_123"
        await triad.postgres.insert(
            "memories",
            {"id": special_id, "content": "test"},
        )
        await triad.process_pending_events()

        vector = await triad.qdrant.get("memories", special_id)
        assert vector is not None

    @pytest.mark.asyncio
    async def test_null_fields_handled(self, triad: TriadFixture) -> None:
        """Null/None fields don't crash the pipeline."""
        await triad.postgres.insert(
            "memories",
            {"id": "nulls", "content": None, "other": "value"},
        )
        results = await triad.process_pending_events()

        # Should succeed
        assert all(r.success for r in results)
