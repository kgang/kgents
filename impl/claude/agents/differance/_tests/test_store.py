"""
Tests for DifferanceStore - D-gent trace persistence.

This module tests:
1. Basic CRUD operations (append, get, exists)
2. Causal chain traversal
3. Query filtering
4. TraceMonoid reconstruction
5. Serialization round-trips

See: spec/protocols/differance.md for the formal specification.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from agents.d import MemoryBackend
from agents.differance import DifferanceStore
from agents.differance.trace import Alternative, TraceMonoid, WiringTrace

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def backend() -> MemoryBackend:
    """Create a fresh in-memory backend for each test."""
    return MemoryBackend()


@pytest.fixture
def store(backend: MemoryBackend) -> DifferanceStore:
    """Create a fresh DifferanceStore for each test."""
    return DifferanceStore(backend=backend)


def make_trace(
    operation: str = "seq",
    inputs: tuple[str, ...] = ("A", "B"),
    output: str = "AB",
    context: str = "test context",
    alternatives: tuple[Alternative, ...] = (),
    parent_trace_id: str | None = None,
) -> WiringTrace:
    """Helper to create test traces."""
    return WiringTrace.create(
        operation=operation,
        inputs=inputs,
        output=output,
        context=context,
        alternatives=alternatives,
        parent_trace_id=parent_trace_id,
    )


# =============================================================================
# Basic Operations Tests
# =============================================================================


class TestDifferanceStoreBasicOperations:
    """Tests for basic CRUD operations."""

    @pytest.mark.asyncio
    async def test_append_and_get(self, store: DifferanceStore) -> None:
        """Can append a trace and retrieve it."""
        trace = make_trace()

        trace_id = await store.append(trace)
        assert trace_id == trace.trace_id

        retrieved = await store.get(trace.trace_id)
        assert retrieved is not None
        assert retrieved.trace_id == trace.trace_id
        assert retrieved.operation == trace.operation
        assert retrieved.inputs == trace.inputs
        assert retrieved.output == trace.output
        assert retrieved.context == trace.context

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self, store: DifferanceStore) -> None:
        """get() returns None for nonexistent trace."""
        result = await store.get("nonexistent_id")
        assert result is None

    @pytest.mark.asyncio
    async def test_exists(self, store: DifferanceStore) -> None:
        """exists() correctly reports trace existence."""
        trace = make_trace()

        assert await store.exists(trace.trace_id) is False

        await store.append(trace)

        assert await store.exists(trace.trace_id) is True

    @pytest.mark.asyncio
    async def test_append_is_idempotent(self, store: DifferanceStore) -> None:
        """Appending the same trace twice is idempotent."""
        trace = make_trace()

        id1 = await store.append(trace)
        id2 = await store.append(trace)

        assert id1 == id2

        # Only one trace should exist
        assert await store.count() == 1

    @pytest.mark.asyncio
    async def test_count(self, store: DifferanceStore) -> None:
        """count() returns correct number of traces."""
        assert await store.count() == 0

        t1 = make_trace(output="A")
        t2 = make_trace(output="B")
        t3 = make_trace(output="C")

        await store.append(t1)
        assert await store.count() == 1

        await store.append(t2)
        assert await store.count() == 2

        await store.append(t3)
        assert await store.count() == 3


# =============================================================================
# Causal Chain Tests
# =============================================================================


class TestDifferanceStoreCausalChain:
    """Tests for causal chain traversal."""

    @pytest.mark.asyncio
    async def test_causal_chain_single_trace(self, store: DifferanceStore) -> None:
        """causal_chain for root trace returns single trace."""
        trace = make_trace()
        await store.append(trace)

        chain = await store.causal_chain(trace.trace_id)

        assert len(chain) == 1
        assert chain[0].trace_id == trace.trace_id

    @pytest.mark.asyncio
    async def test_causal_chain_linear(self, store: DifferanceStore) -> None:
        """causal_chain follows parent links correctly."""
        # Create linear chain: t1 → t2 → t3
        t1 = make_trace(output="A")
        await store.append(t1)

        t2 = make_trace(output="B", parent_trace_id=t1.trace_id)
        await store.append(t2)

        t3 = make_trace(output="C", parent_trace_id=t2.trace_id)
        await store.append(t3)

        chain = await store.causal_chain(t3.trace_id)

        assert len(chain) == 3
        assert chain[0].trace_id == t1.trace_id  # Oldest
        assert chain[1].trace_id == t2.trace_id
        assert chain[2].trace_id == t3.trace_id  # Newest

    @pytest.mark.asyncio
    async def test_causal_chain_nonexistent(self, store: DifferanceStore) -> None:
        """causal_chain returns empty for nonexistent trace."""
        chain = await store.causal_chain("nonexistent")
        assert len(chain) == 0

    @pytest.mark.asyncio
    async def test_causal_chain_preserves_order(self, store: DifferanceStore) -> None:
        """causal_chain returns traces in correct order (oldest → newest)."""
        traces: list[WiringTrace] = []
        parent_id: str | None = None

        for i in range(5):
            trace = make_trace(output=f"output_{i}", parent_trace_id=parent_id)
            await store.append(trace)
            traces.append(trace)
            parent_id = trace.trace_id

        # Get chain for the last trace
        chain = await store.causal_chain(traces[-1].trace_id)

        assert len(chain) == 5
        for i, (chain_trace, original_trace) in enumerate(zip(chain, traces)):
            assert chain_trace.trace_id == original_trace.trace_id, f"Mismatch at index {i}"


# =============================================================================
# Serialization Tests
# =============================================================================


class TestDifferanceStoreSerialization:
    """Tests for serialization round-trips."""

    @pytest.mark.asyncio
    async def test_serialization_preserves_timestamp(self, store: DifferanceStore) -> None:
        """Timestamp is preserved through serialization."""
        trace = make_trace()
        await store.append(trace)

        retrieved = await store.get(trace.trace_id)
        assert retrieved is not None

        # Timestamps should be equal (within microsecond precision)
        assert abs((retrieved.timestamp - trace.timestamp).total_seconds()) < 0.001

    @pytest.mark.asyncio
    async def test_serialization_preserves_alternatives(self, store: DifferanceStore) -> None:
        """Alternatives (ghosts) are preserved through serialization."""
        alt1 = Alternative("par", ("A", "B"), "Order matters", could_revisit=True)
        alt2 = Alternative("branch", ("X",), "Too complex", could_revisit=False)

        trace = make_trace(alternatives=(alt1, alt2))
        await store.append(trace)

        retrieved = await store.get(trace.trace_id)
        assert retrieved is not None

        assert len(retrieved.alternatives) == 2

        r_alt1 = retrieved.alternatives[0]
        assert r_alt1.operation == "par"
        assert r_alt1.inputs == ("A", "B")
        assert r_alt1.reason_rejected == "Order matters"
        assert r_alt1.could_revisit is True

        r_alt2 = retrieved.alternatives[1]
        assert r_alt2.operation == "branch"
        assert r_alt2.could_revisit is False

    @pytest.mark.asyncio
    async def test_serialization_preserves_positions(self, store: DifferanceStore) -> None:
        """Polynomial positions are preserved through serialization."""
        trace = WiringTrace.create(
            operation="seq",
            inputs=("A",),
            output="A",
            context="test",
            positions_before={"agent1": frozenset({"IDLE", "READY"})},
            positions_after={"agent1": frozenset({"RUNNING"})},
        )
        await store.append(trace)

        retrieved = await store.get(trace.trace_id)
        assert retrieved is not None

        assert "agent1" in retrieved.positions_before
        assert retrieved.positions_before["agent1"] == frozenset({"IDLE", "READY"})

        assert "agent1" in retrieved.positions_after
        assert retrieved.positions_after["agent1"] == frozenset({"RUNNING"})

    @pytest.mark.asyncio
    async def test_serialization_preserves_parent_id(self, store: DifferanceStore) -> None:
        """Parent trace ID is preserved through serialization."""
        t1 = make_trace(output="A")
        await store.append(t1)

        t2 = make_trace(output="B", parent_trace_id=t1.trace_id)
        await store.append(t2)

        retrieved = await store.get(t2.trace_id)
        assert retrieved is not None
        assert retrieved.parent_trace_id == t1.trace_id


# =============================================================================
# Query Tests
# =============================================================================


class TestDifferanceStoreQuery:
    """Tests for query operations."""

    @pytest.mark.asyncio
    async def test_query_all(self, store: DifferanceStore) -> None:
        """query() with no filters returns all traces."""
        t1 = make_trace(output="A")
        t2 = make_trace(output="B")
        t3 = make_trace(output="C")

        await store.append(t1)
        await store.append(t2)
        await store.append(t3)

        results: list[WiringTrace] = []
        async for trace in store.query():
            results.append(trace)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_query_by_operation(self, store: DifferanceStore) -> None:
        """query() filters by operation."""
        t1 = make_trace(operation="seq", output="A")
        t2 = make_trace(operation="par", output="B")
        t3 = make_trace(operation="seq", output="C")

        await store.append(t1)
        await store.append(t2)
        await store.append(t3)

        results: list[WiringTrace] = []
        async for trace in store.query(operation="seq"):
            results.append(trace)

        assert len(results) == 2
        assert all(t.operation == "seq" for t in results)

    @pytest.mark.asyncio
    async def test_query_limit(self, store: DifferanceStore) -> None:
        """query() respects limit."""
        for i in range(10):
            trace = make_trace(output=f"output_{i}")
            await store.append(trace)

        results: list[WiringTrace] = []
        async for trace in store.query(limit=5):
            results.append(trace)

        assert len(results) == 5


# =============================================================================
# TraceMonoid Reconstruction Tests
# =============================================================================


class TestDifferanceStoreMonoidReconstruction:
    """Tests for TraceMonoid reconstruction from storage."""

    @pytest.mark.asyncio
    async def test_to_monoid_empty(self, store: DifferanceStore) -> None:
        """to_monoid() returns empty monoid for empty store."""
        monoid = await store.to_monoid()
        assert len(monoid) == 0

    @pytest.mark.asyncio
    async def test_to_monoid_with_traces(self, store: DifferanceStore) -> None:
        """to_monoid() reconstructs all traces."""
        t1 = make_trace(output="A")
        t2 = make_trace(output="B")
        t3 = make_trace(output="C")

        await store.append(t1)
        await store.append(t2)
        await store.append(t3)

        monoid = await store.to_monoid()

        assert len(monoid) == 3
        trace_ids = monoid.trace_ids()
        assert t1.trace_id in trace_ids
        assert t2.trace_id in trace_ids
        assert t3.trace_id in trace_ids

    @pytest.mark.asyncio
    async def test_to_monoid_preserves_ghosts(self, store: DifferanceStore) -> None:
        """to_monoid() preserves ghost alternatives."""
        alt = Alternative("par", ("A",), "reason")
        trace = make_trace(alternatives=(alt,))

        await store.append(trace)

        monoid = await store.to_monoid()
        ghosts = monoid.ghosts()

        assert len(ghosts) == 1
        assert ghosts[0].operation == "par"

    @pytest.mark.asyncio
    async def test_to_monoid_sorted_by_timestamp(self, store: DifferanceStore) -> None:
        """to_monoid() sorts traces by timestamp."""
        # Create traces with explicit timestamps to ensure order
        traces_created = []
        for i in range(3):
            trace = make_trace(output=f"output_{i}")
            await store.append(trace)
            traces_created.append(trace)

        monoid = await store.to_monoid()

        # Verify traces are in timestamp order
        timestamps = [t.timestamp for t in monoid.traces]
        assert timestamps == sorted(timestamps)


# =============================================================================
# D-gent Integration Tests
# =============================================================================


class TestDifferanceStoreDgentIntegration:
    """Tests for D-gent backend integration."""

    @pytest.mark.asyncio
    async def test_works_with_memory_backend(self) -> None:
        """Store works with MemoryBackend."""
        backend = MemoryBackend()
        store = DifferanceStore(backend=backend)

        trace = make_trace()
        await store.append(trace)

        retrieved = await store.get(trace.trace_id)
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_default_backend_is_memory(self) -> None:
        """Store defaults to MemoryBackend if none provided."""
        store = DifferanceStore()

        trace = make_trace()
        await store.append(trace)

        retrieved = await store.get(trace.trace_id)
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_datum_metadata_set_correctly(self, backend: MemoryBackend) -> None:
        """Trace metadata is set correctly on Datum."""
        store = DifferanceStore(backend=backend)

        trace = make_trace(operation="branch", output="XYZ")
        await store.append(trace)

        # Access the underlying datum directly
        datum = await backend.get(trace.trace_id)
        assert datum is not None

        assert datum.metadata.get("operation") == "branch"
        assert datum.metadata.get("output") == "XYZ"
        assert datum.metadata.get("type") == "wiring_trace"

    @pytest.mark.asyncio
    async def test_datum_causal_parent_set_correctly(self, backend: MemoryBackend) -> None:
        """Parent trace ID is set as Datum.causal_parent."""
        store = DifferanceStore(backend=backend)

        t1 = make_trace(output="A")
        await store.append(t1)

        t2 = make_trace(output="B", parent_trace_id=t1.trace_id)
        await store.append(t2)

        # Access the underlying datum directly
        datum = await backend.get(t2.trace_id)
        assert datum is not None
        assert datum.causal_parent == t1.trace_id


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestDifferanceStoreEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_inputs(self, store: DifferanceStore) -> None:
        """Traces with empty inputs serialize correctly."""
        trace = make_trace(inputs=())
        await store.append(trace)

        retrieved = await store.get(trace.trace_id)
        assert retrieved is not None
        assert retrieved.inputs == ()

    @pytest.mark.asyncio
    async def test_empty_alternatives(self, store: DifferanceStore) -> None:
        """Traces with no alternatives serialize correctly."""
        trace = make_trace(alternatives=())
        await store.append(trace)

        retrieved = await store.get(trace.trace_id)
        assert retrieved is not None
        assert retrieved.alternatives == ()

    @pytest.mark.asyncio
    async def test_empty_positions(self, store: DifferanceStore) -> None:
        """Traces with empty positions serialize correctly."""
        trace = WiringTrace.create(
            operation="seq",
            inputs=("A",),
            output="A",
            context="test",
            positions_before={},
            positions_after={},
        )
        await store.append(trace)

        retrieved = await store.get(trace.trace_id)
        assert retrieved is not None
        assert retrieved.positions_before == {}
        assert retrieved.positions_after == {}

    @pytest.mark.asyncio
    async def test_special_characters_in_context(self, store: DifferanceStore) -> None:
        """Traces with special characters in context serialize correctly."""
        trace = make_trace(context='Special chars: "quotes", \\backslash, \ttab, \nnewline')
        await store.append(trace)

        retrieved = await store.get(trace.trace_id)
        assert retrieved is not None
        assert "quotes" in retrieved.context
        assert "backslash" in retrieved.context

    @pytest.mark.asyncio
    async def test_unicode_in_context(self, store: DifferanceStore) -> None:
        """Traces with unicode in context serialize correctly."""
        trace = make_trace(context="Unicode: 日本語, emoji: 🎭, symbols: ∀∃∈")
        await store.append(trace)

        retrieved = await store.get(trace.trace_id)
        assert retrieved is not None
        assert "日本語" in retrieved.context
        assert "🎭" in retrieved.context
