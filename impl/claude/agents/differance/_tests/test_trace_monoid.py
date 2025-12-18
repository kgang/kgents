"""
Tests for the Différance Engine core types and monoid laws.

This module uses property-based testing (Hypothesis) to verify:
1. TraceMonoid satisfies monoid laws (identity, associativity)
2. Ghost accumulation preserves alternatives
3. DAG integrity is maintained
4. Serialization round-trips correctly

See: spec/protocols/differance.md for the formal specification.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import FrozenSet

import pytest
from hypothesis import assume, given, settings, strategies as st

from agents.differance.trace import Alternative, TraceMonoid, WiringTrace

# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def alternative_strategy(draw: st.DrawFn) -> Alternative:
    """Generate random Alternative instances."""
    return Alternative(
        operation=draw(st.sampled_from(["seq", "par", "branch", "fix", "trace"])),
        inputs=tuple(draw(st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=3))),
        reason_rejected=draw(st.text(min_size=5, max_size=50)),
        could_revisit=draw(st.booleans()),
    )


@st.composite
def wiring_trace_strategy(draw: st.DrawFn, parent_id: str | None = None) -> WiringTrace:
    """Generate random WiringTrace instances."""
    trace_id = f"trace_{draw(st.text(alphabet='0123456789abcdef', min_size=8, max_size=12))}"

    # Ensure unique trace_id
    assume(trace_id != parent_id)

    return WiringTrace(
        trace_id=trace_id,
        timestamp=datetime.now(timezone.utc),
        operation=draw(st.sampled_from(["seq", "par", "branch", "fix", "trace"])),
        inputs=tuple(draw(st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=3))),
        output=draw(st.text(min_size=1, max_size=20)),
        context=draw(st.text(min_size=5, max_size=100)),
        alternatives=tuple(draw(st.lists(alternative_strategy(), max_size=3))),
        positions_before={
            "state": frozenset(draw(st.lists(st.text(min_size=1, max_size=5), max_size=3)))
        },
        positions_after={
            "state": frozenset(draw(st.lists(st.text(min_size=1, max_size=5), max_size=3)))
        },
        parent_trace_id=parent_id,
    )


@st.composite
def trace_monoid_strategy(draw: st.DrawFn, max_traces: int = 5) -> TraceMonoid:
    """Generate random TraceMonoid instances with valid causal chains."""
    num_traces = draw(st.integers(min_value=0, max_value=max_traces))
    traces: list[WiringTrace] = []

    for i in range(num_traces):
        # Each trace can optionally have a parent from previous traces
        if traces and draw(st.booleans()):
            parent_id = draw(st.sampled_from([t.trace_id for t in traces]))
        else:
            parent_id = None

        trace = draw(wiring_trace_strategy(parent_id=parent_id))
        traces.append(trace)

    return TraceMonoid(traces=tuple(traces))


# =============================================================================
# Alternative Tests
# =============================================================================


class TestAlternative:
    """Tests for the Alternative dataclass."""

    def test_create_valid_alternative(self) -> None:
        """Can create a valid alternative."""
        alt = Alternative(
            operation="par",
            inputs=("Brain", "Gardener"),
            reason_rejected="Order matters for memory cultivation",
            could_revisit=True,
        )

        assert alt.operation == "par"
        assert alt.inputs == ("Brain", "Gardener")
        assert alt.reason_rejected == "Order matters for memory cultivation"
        assert alt.could_revisit is True

    def test_alternative_is_frozen(self) -> None:
        """Alternative is immutable."""
        alt = Alternative(
            operation="par",
            inputs=("A",),
            reason_rejected="test",
            could_revisit=True,
        )

        with pytest.raises(AttributeError):
            alt.operation = "seq"  # type: ignore

    def test_alternative_requires_operation(self) -> None:
        """Alternative must have an operation."""
        with pytest.raises(ValueError, match="must have an operation"):
            Alternative(operation="", inputs=("A",), reason_rejected="test")

    def test_alternative_requires_reason(self) -> None:
        """Alternative must have a reason for rejection."""
        with pytest.raises(ValueError, match="must have a reason"):
            Alternative(operation="par", inputs=("A",), reason_rejected="")

    def test_alternative_default_could_revisit(self) -> None:
        """could_revisit defaults to True."""
        alt = Alternative(operation="par", inputs=("A",), reason_rejected="test")
        assert alt.could_revisit is True

    @given(alternative_strategy())
    def test_alternative_is_hashable(self, alt: Alternative) -> None:
        """Alternatives can be used in sets and as dict keys."""
        s = {alt}
        assert alt in s


# =============================================================================
# WiringTrace Tests
# =============================================================================


class TestWiringTrace:
    """Tests for the WiringTrace dataclass."""

    def test_create_valid_trace(self) -> None:
        """Can create a valid wiring trace."""
        trace = WiringTrace(
            trace_id="dec_abc123",
            timestamp=datetime.now(timezone.utc),
            operation="seq",
            inputs=("Brain", "Gardener"),
            output="BrainGardener",
            context="Memory cultivation requires ordered processing",
            alternatives=(Alternative("par", ("Brain", "Gardener"), "Order matters"),),
            positions_before={"Brain": frozenset({"IDLE"})},
            positions_after={"BrainGardener": frozenset({"READY"})},
            parent_trace_id=None,
        )

        assert trace.trace_id == "dec_abc123"
        assert trace.operation == "seq"
        assert len(trace.alternatives) == 1

    def test_trace_factory_method(self) -> None:
        """WiringTrace.create() generates ID and timestamp."""
        trace = WiringTrace.create(
            operation="seq",
            inputs=("A", "B"),
            output="AB",
            context="Sequential composition",
        )

        assert trace.trace_id.startswith("trace_")
        assert len(trace.trace_id) == len("trace_") + 12
        assert trace.timestamp is not None
        assert trace.operation == "seq"

    def test_trace_is_frozen(self) -> None:
        """WiringTrace is immutable."""
        trace = WiringTrace.create(
            operation="seq",
            inputs=("A",),
            output="A",
            context="test",
        )

        with pytest.raises(AttributeError):
            trace.operation = "par"  # type: ignore

    def test_trace_requires_trace_id(self) -> None:
        """WiringTrace must have a trace_id."""
        with pytest.raises(ValueError, match="must have a trace_id"):
            WiringTrace(
                trace_id="",
                timestamp=datetime.now(timezone.utc),
                operation="seq",
                inputs=(),
                output="X",
                context="test",
            )

    def test_trace_requires_operation(self) -> None:
        """WiringTrace must have an operation."""
        with pytest.raises(ValueError, match="must have an operation"):
            WiringTrace(
                trace_id="t1",
                timestamp=datetime.now(timezone.utc),
                operation="",
                inputs=(),
                output="X",
                context="test",
            )

    def test_trace_requires_output(self) -> None:
        """WiringTrace must have an output."""
        with pytest.raises(ValueError, match="must have an output"):
            WiringTrace(
                trace_id="t1",
                timestamp=datetime.now(timezone.utc),
                operation="seq",
                inputs=(),
                output="",
                context="test",
            )

    def test_trace_ghosts(self) -> None:
        """ghosts() returns all alternatives."""
        alt1 = Alternative("par", ("A",), "reason1")
        alt2 = Alternative("branch", ("B",), "reason2")

        trace = WiringTrace.create(
            operation="seq",
            inputs=("A", "B"),
            output="AB",
            context="test",
            alternatives=(alt1, alt2),
        )

        ghosts = trace.ghosts()
        assert len(ghosts) == 2
        assert alt1 in ghosts
        assert alt2 in ghosts

    def test_trace_explorable_ghosts(self) -> None:
        """explorable_ghosts() filters by could_revisit."""
        alt1 = Alternative("par", ("A",), "reason1", could_revisit=True)
        alt2 = Alternative("branch", ("B",), "reason2", could_revisit=False)

        trace = WiringTrace.create(
            operation="seq",
            inputs=("A", "B"),
            output="AB",
            context="test",
            alternatives=(alt1, alt2),
        )

        explorable = trace.explorable_ghosts()
        assert len(explorable) == 1
        assert alt1 in explorable
        assert alt2 not in explorable

    def test_trace_with_parent(self) -> None:
        """with_parent() creates new trace with parent ID."""
        trace = WiringTrace.create(
            operation="seq",
            inputs=("A",),
            output="A",
            context="test",
        )

        child = trace.with_parent("parent_123")
        assert child.parent_trace_id == "parent_123"
        assert child.trace_id == trace.trace_id
        assert child.operation == trace.operation

    def test_trace_equality(self) -> None:
        """WiringTrace equality works correctly."""
        t1 = WiringTrace.create(
            operation="seq",
            inputs=("A", "B"),
            output="AB",
            context="test",
        )
        # Same trace should be equal to itself
        assert t1 == t1

        # Different traces should not be equal
        t2 = WiringTrace.create(
            operation="seq",
            inputs=("A", "B"),
            output="AB",
            context="test",
        )
        # Different trace_id means not equal
        assert t1 != t2


# =============================================================================
# TraceMonoid Tests - Monoid Laws
# =============================================================================


class TestTraceMonoidLaws:
    """Property-based tests for monoid laws."""

    def test_empty_creates_identity(self) -> None:
        """TraceMonoid.empty() creates the identity element."""
        empty = TraceMonoid.empty()
        assert len(empty.traces) == 0
        assert len(empty.ghosts()) == 0

    @given(trace_monoid_strategy())
    @settings(max_examples=100)
    def test_left_identity(self, m: TraceMonoid) -> None:
        """
        Left identity: ε ⊗ T = T

        Composing empty on the left returns the original.
        """
        result = TraceMonoid.empty().compose(m)
        assert result.traces == m.traces
        assert result == m

    @given(trace_monoid_strategy())
    @settings(max_examples=100)
    def test_right_identity(self, m: TraceMonoid) -> None:
        """
        Right identity: T ⊗ ε = T

        Composing empty on the right returns the original.
        """
        result = m.compose(TraceMonoid.empty())
        assert result.traces == m.traces
        assert result == m

    @given(
        trace_monoid_strategy(max_traces=3),
        trace_monoid_strategy(max_traces=3),
        trace_monoid_strategy(max_traces=3),
    )
    @settings(max_examples=50)
    def test_associativity(self, a: TraceMonoid, b: TraceMonoid, c: TraceMonoid) -> None:
        """
        Associativity: (A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)

        Grouping doesn't matter for composition.
        """
        left = (a.compose(b)).compose(c)
        right = a.compose(b.compose(c))

        assert left.traces == right.traces
        assert left == right

    @given(trace_monoid_strategy(), trace_monoid_strategy())
    @settings(max_examples=100)
    def test_ghost_preservation(self, a: TraceMonoid, b: TraceMonoid) -> None:
        """
        Ghost Preservation: ghosts(a ⊗ b) ⊇ ghosts(a) ∪ ghosts(b)

        Composition never loses ghosts.
        """
        combined = a.compose(b)

        a_ghosts = set(a.ghosts())
        b_ghosts = set(b.ghosts())
        combined_ghosts = set(combined.ghosts())

        # Combined ghosts must include all ghosts from both operands
        assert combined_ghosts >= a_ghosts | b_ghosts


# =============================================================================
# TraceMonoid Tests - Operations
# =============================================================================


class TestTraceMonoidOperations:
    """Tests for TraceMonoid operations."""

    def test_append_single_trace(self) -> None:
        """append() adds a single trace."""
        monoid = TraceMonoid.empty()
        trace = WiringTrace.create(
            operation="seq",
            inputs=("A",),
            output="A",
            context="test",
        )

        result = monoid.append(trace)
        assert len(result.traces) == 1
        assert result.traces[0] == trace

    def test_append_preserves_order(self) -> None:
        """append() maintains trace order."""
        t1 = WiringTrace.create(operation="seq", inputs=("A",), output="A", context="1")
        t2 = WiringTrace.create(operation="par", inputs=("B",), output="B", context="2")
        t3 = WiringTrace.create(operation="fix", inputs=("C",), output="C", context="3")

        monoid = TraceMonoid.empty().append(t1).append(t2).append(t3)

        assert len(monoid.traces) == 3
        assert monoid.traces[0].operation == "seq"
        assert monoid.traces[1].operation == "par"
        assert monoid.traces[2].operation == "fix"

    def test_compose_concatenates_traces(self) -> None:
        """compose() concatenates trace sequences."""
        t1 = WiringTrace.create(operation="seq", inputs=("A",), output="A", context="1")
        t2 = WiringTrace.create(operation="par", inputs=("B",), output="B", context="2")

        m1 = TraceMonoid((t1,))
        m2 = TraceMonoid((t2,))

        result = m1.compose(m2)
        assert len(result.traces) == 2
        assert result.traces[0] == t1
        assert result.traces[1] == t2

    def test_trace_ids_returns_all_ids(self) -> None:
        """trace_ids() returns set of all trace IDs."""
        t1 = WiringTrace.create(operation="seq", inputs=("A",), output="A", context="1")
        t2 = WiringTrace.create(operation="par", inputs=("B",), output="B", context="2")

        monoid = TraceMonoid((t1, t2))
        ids = monoid.trace_ids()

        assert t1.trace_id in ids
        assert t2.trace_id in ids
        assert len(ids) == 2

    def test_get_by_id(self) -> None:
        """get() retrieves trace by ID."""
        t1 = WiringTrace.create(operation="seq", inputs=("A",), output="A", context="1")
        t2 = WiringTrace.create(operation="par", inputs=("B",), output="B", context="2")

        monoid = TraceMonoid((t1, t2))

        assert monoid.get(t1.trace_id) == t1
        assert monoid.get(t2.trace_id) == t2
        assert monoid.get("nonexistent") is None

    def test_root_traces(self) -> None:
        """root_traces() returns traces with no parent."""
        t1 = WiringTrace.create(operation="seq", inputs=("A",), output="A", context="1")
        t2 = WiringTrace.create(
            operation="par",
            inputs=("B",),
            output="B",
            context="2",
            parent_trace_id=t1.trace_id,
        )

        monoid = TraceMonoid((t1, t2))
        roots = monoid.root_traces()

        assert len(roots) == 1
        assert roots[0] == t1

    def test_children_of(self) -> None:
        """children_of() returns traces with given parent."""
        t1 = WiringTrace.create(operation="seq", inputs=("A",), output="A", context="1")
        t2 = WiringTrace.create(
            operation="par",
            inputs=("B",),
            output="B",
            context="2",
            parent_trace_id=t1.trace_id,
        )
        t3 = WiringTrace.create(
            operation="fix",
            inputs=("C",),
            output="C",
            context="3",
            parent_trace_id=t1.trace_id,
        )

        monoid = TraceMonoid((t1, t2, t3))
        children = monoid.children_of(t1.trace_id)

        assert len(children) == 2
        assert t2 in children
        assert t3 in children

    def test_causal_chain(self) -> None:
        """causal_chain() returns ancestry oldest → newest."""
        t1 = WiringTrace.create(operation="seq", inputs=("A",), output="A", context="1")
        t2 = WiringTrace.create(
            operation="par",
            inputs=("B",),
            output="B",
            context="2",
            parent_trace_id=t1.trace_id,
        )
        t3 = WiringTrace.create(
            operation="fix",
            inputs=("C",),
            output="C",
            context="3",
            parent_trace_id=t2.trace_id,
        )

        monoid = TraceMonoid((t1, t2, t3))
        chain = monoid.causal_chain(t3.trace_id)

        assert len(chain) == 3
        assert chain[0] == t1  # Oldest
        assert chain[1] == t2
        assert chain[2] == t3  # Newest (the requested trace)

    def test_causal_chain_for_root(self) -> None:
        """causal_chain() for root returns single trace."""
        t1 = WiringTrace.create(operation="seq", inputs=("A",), output="A", context="1")

        monoid = TraceMonoid((t1,))
        chain = monoid.causal_chain(t1.trace_id)

        assert len(chain) == 1
        assert chain[0] == t1

    def test_causal_chain_not_found(self) -> None:
        """causal_chain() returns empty for nonexistent trace."""
        monoid = TraceMonoid.empty()
        chain = monoid.causal_chain("nonexistent")

        assert len(chain) == 0


# =============================================================================
# TraceMonoid Tests - DAG Integrity
# =============================================================================


class TestTraceMonoidDAGIntegrity:
    """Tests for DAG integrity verification."""

    def test_valid_dag(self) -> None:
        """Well-formed DAG passes verification."""
        t1 = WiringTrace.create(operation="seq", inputs=("A",), output="A", context="1")
        t2 = WiringTrace.create(
            operation="par",
            inputs=("B",),
            output="B",
            context="2",
            parent_trace_id=t1.trace_id,
        )

        monoid = TraceMonoid((t1, t2))
        is_valid, message = monoid.verify_dag_integrity()

        assert is_valid is True
        assert message == "DAG is well-formed"

    def test_orphan_parent_detected(self) -> None:
        """Orphan parent reference is detected."""
        t1 = WiringTrace.create(
            operation="seq",
            inputs=("A",),
            output="A",
            context="1",
            parent_trace_id="nonexistent_parent",
        )

        monoid = TraceMonoid((t1,))
        is_valid, message = monoid.verify_dag_integrity()

        assert is_valid is False
        assert "orphan parent" in message.lower()

    def test_empty_dag_is_valid(self) -> None:
        """Empty monoid has valid DAG."""
        monoid = TraceMonoid.empty()
        is_valid, message = monoid.verify_dag_integrity()

        assert is_valid is True

    @given(trace_monoid_strategy())
    @settings(max_examples=50)
    def test_generated_monoids_have_valid_dag(self, monoid: TraceMonoid) -> None:
        """All generated monoids have valid DAG structure."""
        is_valid, message = monoid.verify_dag_integrity()
        assert is_valid is True, f"DAG integrity failed: {message}"


# =============================================================================
# TraceMonoid Tests - Dunder Methods
# =============================================================================


class TestTraceMonoidDunder:
    """Tests for TraceMonoid special methods."""

    def test_len_empty(self) -> None:
        """len() of empty monoid is 0."""
        assert len(TraceMonoid.empty()) == 0

    def test_len_with_traces(self) -> None:
        """len() returns number of traces."""
        t1 = WiringTrace.create(operation="seq", inputs=("A",), output="A", context="1")
        t2 = WiringTrace.create(operation="par", inputs=("B",), output="B", context="2")

        monoid = TraceMonoid((t1, t2))
        assert len(monoid) == 2

    def test_bool_empty_is_false(self) -> None:
        """Empty monoid is falsy."""
        assert not TraceMonoid.empty()

    def test_bool_with_traces_is_true(self) -> None:
        """Monoid with traces is truthy."""
        t1 = WiringTrace.create(operation="seq", inputs=("A",), output="A", context="1")
        monoid = TraceMonoid((t1,))
        assert monoid

    def test_repr(self) -> None:
        """repr() shows trace and ghost counts."""
        alt = Alternative("par", ("A",), "reason")
        t1 = WiringTrace.create(
            operation="seq",
            inputs=("A",),
            output="A",
            context="1",
            alternatives=(alt,),
        )

        monoid = TraceMonoid((t1,))
        r = repr(monoid)

        assert "traces=1" in r
        assert "ghosts=1" in r
