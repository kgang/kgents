"""
Différance Engine: Core Types for Traced Wiring Diagrams.

This module implements the TraceMonoid — an algebraic structure that records
wiring decisions with ghost alternatives. Every composition decision creates
both a difference (what was chosen) and a deferral (what remains explorable).

Core Types:
    Alternative: A road not taken — the ghost
    WiringTrace: Single recorded wiring decision (ADR-style)
    TraceMonoid: Monoid of wiring traces with ghost accumulation

Laws:
    Identity:      ε ⊗ T = T = T ⊗ ε
    Associativity: (A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)
    Ghost Preservation: ghosts(a ⊗ b) ⊇ ghosts(a) ∪ ghosts(b)

Theory:
    Traced monoidal categories + Derrida's différance.
    See spec/protocols/differance.md for full specification.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, FrozenSet, Mapping, Sequence


@dataclass(frozen=True)
class Alternative:
    """
    A road not taken — the ghost.

    Alternatives record decisions that were considered but rejected. They
    form the "ghost heritage" that can be revisited later if needed.

    Attributes:
        operation: The operation that was considered (e.g., "par" instead of "seq")
        inputs: Agent IDs that would have been wired
        reason_rejected: Human-readable explanation of why this wasn't chosen
        could_revisit: Whether this alternative can be explored later

    Example:
        >>> alt = Alternative(
        ...     operation="par",
        ...     inputs=("Brain", "Gardener"),
        ...     reason_rejected="Order matters for memory cultivation",
        ...     could_revisit=True,
        ... )
    """

    operation: str
    inputs: tuple[str, ...]
    reason_rejected: str
    could_revisit: bool = True

    def __post_init__(self) -> None:
        """Validate alternative on creation."""
        if not self.operation:
            raise ValueError("Alternative must have an operation")
        if not self.reason_rejected:
            raise ValueError("Alternative must have a reason for rejection")


@dataclass(frozen=True)
class WiringTrace:
    """
    Single recorded wiring decision (ADR-style).

    A WiringTrace captures one composition decision in full detail:
    what was done, what alternatives were considered, why this choice
    was made, and how the polynomial state changed.

    Attributes:
        trace_id: Unique identifier for this trace
        timestamp: When this decision was made
        operation: The operation performed (e.g., "seq", "par", "branch")
        inputs: Agent IDs that were wired
        output: Agent ID of the composed result
        context: Human-readable context for why this decision was made
        alternatives: Ghosts — alternatives that were considered but not chosen
        positions_before: Polynomial positions before the operation
        positions_after: Polynomial positions after the operation
        parent_trace_id: ID of the parent trace (for causal chain)

    Laws:
        - trace_id must be unique across the trace history
        - parent_trace_id must refer to an existing trace or be None (root)
        - alternatives preserve rejected paths for potential revisiting

    Example:
        >>> trace = WiringTrace(
        ...     trace_id="dec_abc123",
        ...     timestamp=datetime.now(timezone.utc),
        ...     operation="seq",
        ...     inputs=("Brain", "Gardener"),
        ...     output="BrainGardener",
        ...     context="Memory cultivation requires ordered processing",
        ...     alternatives=(
        ...         Alternative("par", ("Brain", "Gardener"), "Order matters"),
        ...     ),
        ...     positions_before={"Brain": frozenset({"IDLE"})},
        ...     positions_after={"BrainGardener": frozenset({"READY"})},
        ...     parent_trace_id=None,
        ... )
    """

    trace_id: str
    timestamp: datetime
    operation: str
    inputs: tuple[str, ...]
    output: str
    context: str
    alternatives: tuple[Alternative, ...] = field(default_factory=tuple)
    positions_before: Mapping[str, FrozenSet[str]] = field(default_factory=dict)
    positions_after: Mapping[str, FrozenSet[str]] = field(default_factory=dict)
    parent_trace_id: str | None = None

    def __post_init__(self) -> None:
        """Validate trace on creation."""
        if not self.trace_id:
            raise ValueError("WiringTrace must have a trace_id")
        if not self.operation:
            raise ValueError("WiringTrace must have an operation")
        if not self.output:
            raise ValueError("WiringTrace must have an output")

    @classmethod
    def create(
        cls,
        operation: str,
        inputs: tuple[str, ...],
        output: str,
        context: str,
        alternatives: tuple[Alternative, ...] = (),
        positions_before: Mapping[str, FrozenSet[str]] | None = None,
        positions_after: Mapping[str, FrozenSet[str]] | None = None,
        parent_trace_id: str | None = None,
    ) -> WiringTrace:
        """
        Factory method to create a WiringTrace with auto-generated ID and timestamp.

        Example:
            >>> trace = WiringTrace.create(
            ...     operation="seq",
            ...     inputs=("A", "B"),
            ...     output="AB",
            ...     context="Sequential composition",
            ... )
        """
        return cls(
            trace_id=f"trace_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(timezone.utc),
            operation=operation,
            inputs=inputs,
            output=output,
            context=context,
            alternatives=alternatives,
            positions_before=positions_before or {},
            positions_after=positions_after or {},
            parent_trace_id=parent_trace_id,
        )

    def with_parent(self, parent_id: str) -> WiringTrace:
        """Create a new trace with the given parent ID."""
        return WiringTrace(
            trace_id=self.trace_id,
            timestamp=self.timestamp,
            operation=self.operation,
            inputs=self.inputs,
            output=self.output,
            context=self.context,
            alternatives=self.alternatives,
            positions_before=self.positions_before,
            positions_after=self.positions_after,
            parent_trace_id=parent_id,
        )

    def ghosts(self) -> Sequence[Alternative]:
        """Return all alternatives (ghosts) for this trace."""
        return self.alternatives

    def explorable_ghosts(self) -> Sequence[Alternative]:
        """Return only the alternatives that can be revisited."""
        return tuple(alt for alt in self.alternatives if alt.could_revisit)


@dataclass(frozen=True)
class TraceMonoid:
    """
    Monoid of wiring traces with ghost accumulation.

    The TraceMonoid is the central algebraic structure of the Différance Engine.
    It accumulates traces via composition while preserving ghost alternatives
    from both operands.

    Monoid Laws:
        Identity:      ε ⊗ T = T = T ⊗ ε   (empty composed with anything is identity)
        Associativity: (A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)   (grouping doesn't matter)

    Ghost Preservation Law:
        ghosts(a ⊗ b) ⊇ ghosts(a) ∪ ghosts(b)

    Attributes:
        traces: Tuple of WiringTrace objects in chronological order

    Example:
        >>> m1 = TraceMonoid((trace1,))
        >>> m2 = TraceMonoid((trace2,))
        >>> combined = m1.compose(m2)
        >>> assert len(combined.traces) == 2
        >>> assert set(combined.ghosts()) >= set(m1.ghosts()) | set(m2.ghosts())
    """

    traces: tuple[WiringTrace, ...] = field(default_factory=tuple)

    @staticmethod
    def empty() -> TraceMonoid:
        """
        Create the identity element of the monoid.

        The empty monoid satisfies:
            empty().compose(m) == m == m.compose(empty())

        Returns:
            TraceMonoid with no traces
        """
        return TraceMonoid(traces=())

    def append(self, trace: WiringTrace) -> TraceMonoid:
        """
        Append a single trace to the monoid.

        This is a convenience method equivalent to:
            self.compose(TraceMonoid((trace,)))

        Args:
            trace: The trace to append

        Returns:
            New TraceMonoid with the trace appended
        """
        return TraceMonoid(traces=self.traces + (trace,))

    def compose(self, other: TraceMonoid) -> TraceMonoid:
        """
        Compose two monoids (monoid multiplication).

        This operation:
        1. Concatenates the trace sequences
        2. Preserves all ghosts from both operands

        Laws:
            Identity:      ε ⊗ T = T = T ⊗ ε
            Associativity: (A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)

        Args:
            other: TraceMonoid to compose with

        Returns:
            New TraceMonoid with combined traces
        """
        return TraceMonoid(traces=self.traces + other.traces)

    def ghosts(self) -> Sequence[Alternative]:
        """
        Return all ghost alternatives across all traces.

        The ghosts are accumulated from all traces in the monoid.
        This satisfies the Ghost Preservation Law:
            ghosts(a ⊗ b) ⊇ ghosts(a) ∪ ghosts(b)

        Returns:
            Sequence of all Alternative objects from all traces
        """
        result: list[Alternative] = []
        for trace in self.traces:
            result.extend(trace.ghosts())
        return tuple(result)

    def explorable_ghosts(self) -> Sequence[Alternative]:
        """Return only the ghosts that can be revisited."""
        result: list[Alternative] = []
        for trace in self.traces:
            result.extend(trace.explorable_ghosts())
        return tuple(result)

    def trace_ids(self) -> FrozenSet[str]:
        """Return all trace IDs in this monoid."""
        return frozenset(trace.trace_id for trace in self.traces)

    def get(self, trace_id: str) -> WiringTrace | None:
        """Get a specific trace by ID."""
        for trace in self.traces:
            if trace.trace_id == trace_id:
                return trace
        return None

    def root_traces(self) -> Sequence[WiringTrace]:
        """Return traces with no parent (roots of the DAG)."""
        return tuple(t for t in self.traces if t.parent_trace_id is None)

    def children_of(self, trace_id: str) -> Sequence[WiringTrace]:
        """Return traces that have the given trace as parent."""
        return tuple(t for t in self.traces if t.parent_trace_id == trace_id)

    def causal_chain(self, trace_id: str) -> Sequence[WiringTrace]:
        """
        Get the causal chain (ancestry) for a trace.

        Follows parent_trace_id links to build the full lineage
        from the root to the given trace.

        Args:
            trace_id: ID of the trace to get ancestry for

        Returns:
            Sequence of traces from oldest ancestor to the trace,
            or empty if trace not found
        """
        trace = self.get(trace_id)
        if trace is None:
            return ()

        # Build chain by walking up
        chain: list[WiringTrace] = [trace]
        current = trace

        while current.parent_trace_id is not None:
            parent = self.get(current.parent_trace_id)
            if parent is None:
                break  # Orphan reference — shouldn't happen in well-formed monoid
            chain.append(parent)
            current = parent

        # Reverse to get oldest → newest order
        return tuple(reversed(chain))

    def verify_dag_integrity(self) -> tuple[bool, str]:
        """
        Verify that the trace DAG is well-formed.

        Checks:
        1. All parent_trace_ids refer to existing traces or are None
        2. No cycles in the parent chain

        Returns:
            Tuple of (is_valid, message)
        """
        trace_ids = self.trace_ids()

        for trace in self.traces:
            if trace.parent_trace_id is not None:
                if trace.parent_trace_id not in trace_ids:
                    return (
                        False,
                        f"Trace {trace.trace_id} has orphan parent {trace.parent_trace_id}",
                    )

                # Check for cycles
                visited: set[str] = {trace.trace_id}
                current = trace

                while current.parent_trace_id is not None:
                    if current.parent_trace_id in visited:
                        return (
                            False,
                            f"Cycle detected at trace {current.trace_id}",
                        )
                    visited.add(current.parent_trace_id)
                    parent = self.get(current.parent_trace_id)
                    if parent is None:
                        break
                    current = parent

        return (True, "DAG is well-formed")

    def __len__(self) -> int:
        """Return the number of traces in the monoid."""
        return len(self.traces)

    def __bool__(self) -> bool:
        """Return True if the monoid has any traces."""
        return len(self.traces) > 0

    def __repr__(self) -> str:
        ghost_count = len(self.ghosts())
        return f"TraceMonoid(traces={len(self.traces)}, ghosts={ghost_count})"


__all__ = [
    "Alternative",
    "WiringTrace",
    "TraceMonoid",
]
