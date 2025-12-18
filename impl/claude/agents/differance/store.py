"""
DifferanceStore: Append-Only Trace Persistence with D-gent.

This module provides the persistence layer for the Différance Engine,
storing WiringTrace objects via D-gent's backend-agnostic storage.

Key Design Decisions:
    1. Append-only: Never mutate past traces (event sourcing)
    2. Causal linking: Uses datum.causal_parent for trace lineage
    3. D-gent integration: Works with any D-gent backend (Memory → JSONL → SQLite → Postgres)
    4. DataBus optional: Emits events when bus is provided

See: spec/protocols/differance.md
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from typing import TYPE_CHECKING, AsyncIterator, Sequence

from .trace import Alternative, TraceMonoid, WiringTrace

if TYPE_CHECKING:
    from agents.d import DataBus, DgentProtocol, DgentRouter
    from agents.d.datum import Datum

    from .heritage import GhostHeritageDAG


class DifferanceStore:
    """
    Append-only trace persistence with D-gent.

    This store provides the core persistence operations for the Différance Engine:
    - append: Store a new trace (never overwrite)
    - get: Retrieve a trace by ID
    - causal_chain: Get the full lineage of a trace
    - query: Stream traces matching filters
    - to_monoid: Reconstruct a TraceMonoid from stored traces

    The store uses D-gent's DgentProtocol for backend-agnostic persistence,
    meaning it works with MemoryBackend (ephemeral), JSONLBackend (file),
    SQLiteBackend (local DB), or PostgresBackend (production).

    Example:
        >>> from agents.d import MemoryBackend
        >>> store = DifferanceStore(MemoryBackend())
        >>> trace = WiringTrace.create(
        ...     operation="seq",
        ...     inputs=("A", "B"),
        ...     output="AB",
        ...     context="Sequential composition",
        ... )
        >>> await store.append(trace)
        >>> retrieved = await store.get(trace.trace_id)
        >>> assert retrieved == trace
    """

    def __init__(
        self,
        backend: DgentProtocol | None = None,
        bus: DataBus | None = None,
    ) -> None:
        """
        Initialize the DifferanceStore.

        Args:
            backend: D-gent backend for storage. If None, uses MemoryBackend.
            bus: Optional DataBus for event emission on trace operations.
        """
        # Lazy import to avoid circular dependencies
        from agents.d import BusEnabledDgent, MemoryBackend

        self._backend = backend or MemoryBackend()

        # Wrap with bus if provided
        if bus is not None:
            self._dgent: DgentProtocol = BusEnabledDgent(self._backend, bus)
        else:
            self._dgent = self._backend

    async def append(self, trace: WiringTrace) -> str:
        """
        Append a trace to storage (never overwrite).

        This is the primary write operation. Traces are immutable once stored.
        The trace's causal_parent is preserved in the Datum for lineage tracking.

        Args:
            trace: The WiringTrace to store

        Returns:
            The trace_id of the stored trace

        Note:
            If a trace with the same ID already exists, this is a no-op.
            The original trace is preserved (append-only semantics).
        """
        from agents.d import Datum

        # Check if already exists (append-only semantics)
        existing = await self._dgent.get(trace.trace_id)
        if existing is not None:
            return trace.trace_id

        datum = self._serialize(trace)
        return await self._dgent.put(datum)

    async def get(self, trace_id: str) -> WiringTrace | None:
        """
        Retrieve a single trace by ID.

        Args:
            trace_id: The trace ID to retrieve

        Returns:
            The WiringTrace if found, None otherwise
        """
        datum = await self._dgent.get(trace_id)
        if datum is None:
            return None
        return self._deserialize(datum)

    async def exists(self, trace_id: str) -> bool:
        """
        Check if a trace exists.

        Args:
            trace_id: The trace ID to check

        Returns:
            True if the trace exists, False otherwise
        """
        return await self._dgent.exists(trace_id)

    async def causal_chain(self, trace_id: str) -> list[WiringTrace]:
        """
        Get the full lineage of a trace (oldest → newest).

        Follows parent_trace_id links via D-gent's causal_chain method.

        Args:
            trace_id: The trace ID to get ancestry for

        Returns:
            List of traces from oldest ancestor to the given trace.
            Empty list if trace not found.

        Example:
            If trace1 → trace2 → trace3:
            causal_chain("trace3") returns [trace1, trace2, trace3]
        """
        datums = await self._dgent.causal_chain(trace_id)
        return [self._deserialize(d) for d in datums]

    async def query(
        self,
        output_id: str | None = None,
        operation: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> AsyncIterator[WiringTrace]:
        """
        Stream traces matching filters.

        Args:
            output_id: Filter to traces with this output (optional)
            operation: Filter to traces with this operation (optional)
            since: Filter to traces created after this time (optional)
            limit: Maximum number of traces to return

        Yields:
            WiringTrace objects matching the filters
        """
        # Convert datetime to Unix timestamp if provided
        after_timestamp = since.timestamp() if since else None

        # Use output_id as prefix for efficient filtering
        prefix = output_id if output_id else None

        datums = await self._dgent.list(
            prefix=prefix,
            after=after_timestamp,
            limit=limit,
        )

        for datum in datums:
            trace = self._deserialize(datum)

            # Apply additional filters
            if operation is not None and trace.operation != operation:
                continue

            yield trace

    async def to_monoid(self, limit: int = 1000) -> TraceMonoid:
        """
        Reconstruct a TraceMonoid from all stored traces.

        This is useful for in-memory operations on the full trace history.

        Args:
            limit: Maximum number of traces to load

        Returns:
            TraceMonoid containing all stored traces
        """
        traces: list[WiringTrace] = []

        async for trace in self.query(limit=limit):
            traces.append(trace)

        # Sort by timestamp for proper ordering
        traces.sort(key=lambda t: t.timestamp)

        return TraceMonoid(traces=tuple(traces))

    async def count(self) -> int:
        """
        Count total number of traces stored.

        Returns:
            Total count of traces
        """
        return await self._dgent.count()

    async def heritage_dag(
        self,
        root_id: str,
        depth: int = 10,
    ) -> GhostHeritageDAG:
        """
        Build a GhostHeritageDAG for the given root trace.

        This method loads the relevant traces from storage and
        builds the heritage DAG for visualization.

        Args:
            root_id: ID of the target trace
            depth: Maximum depth to traverse (default: 10)

        Returns:
            GhostHeritageDAG for visualization

        Example:
            >>> store = DifferanceStore()
            >>> # ... append some traces ...
            >>> dag = await store.heritage_dag("trace_xyz")
            >>> dag.chosen_path()
            ('trace_abc', 'trace_def', 'trace_xyz')
        """
        from .heritage import GhostHeritageDAG, build_heritage_dag

        # Load the trace and its ancestry
        traces = await self.causal_chain(root_id)

        if not traces:
            return GhostHeritageDAG(nodes={}, edges=(), root_id="")

        # Build monoid from traces
        monoid = TraceMonoid(traces=tuple(traces))

        return build_heritage_dag(monoid, root_id, depth)

    def _serialize(self, trace: WiringTrace) -> Datum:
        """
        Serialize WiringTrace to Datum.

        The trace is stored as JSON bytes with:
        - id: trace.trace_id
        - causal_parent: trace.parent_trace_id
        - metadata: operation, output for quick filtering
        """
        from agents.d import Datum

        # Convert to dict, handling special types
        data = asdict(trace)

        # Convert datetime to ISO string
        data["timestamp"] = trace.timestamp.isoformat()

        # Convert frozensets to lists for JSON serialization
        data["positions_before"] = {k: list(v) for k, v in trace.positions_before.items()}
        data["positions_after"] = {k: list(v) for k, v in trace.positions_after.items()}

        content = json.dumps(data).encode("utf-8")

        return Datum.create(
            content=content,
            id=trace.trace_id,
            causal_parent=trace.parent_trace_id,
            metadata={
                "operation": trace.operation,
                "output": trace.output,
                "type": "wiring_trace",
            },
        )

    def _deserialize(self, datum: Datum) -> WiringTrace:
        """
        Deserialize Datum to WiringTrace.

        Handles the inverse of _serialize, reconstructing
        all special types (datetime, frozenset, etc).
        """
        data = json.loads(datum.content.decode("utf-8"))

        # Parse datetime from ISO string
        timestamp = datetime.fromisoformat(data["timestamp"])

        # Reconstruct frozensets
        positions_before = {k: frozenset(v) for k, v in data.get("positions_before", {}).items()}
        positions_after = {k: frozenset(v) for k, v in data.get("positions_after", {}).items()}

        # Reconstruct alternatives
        alternatives = tuple(
            Alternative(
                operation=alt["operation"],
                inputs=tuple(alt["inputs"]),
                reason_rejected=alt["reason_rejected"],
                could_revisit=alt.get("could_revisit", True),
            )
            for alt in data.get("alternatives", [])
        )

        return WiringTrace(
            trace_id=data["trace_id"],
            timestamp=timestamp,
            operation=data["operation"],
            inputs=tuple(data["inputs"]),
            output=data["output"],
            context=data["context"],
            alternatives=alternatives,
            positions_before=positions_before,
            positions_after=positions_after,
            parent_trace_id=data.get("parent_trace_id"),
        )


__all__ = ["DifferanceStore"]
