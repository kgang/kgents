"""
Tests for TRACED_OPERAD: Traced Wiring Diagrams with Semantic Preservation.

This module tests:
1. TracedAgent wrapping and behavior
2. traced_seq semantic preservation
3. traced_par semantic preservation
4. Ghost preservation laws
5. Associativity of traced composition
6. Integration with AGENT_OPERAD

Property-based tests verify laws hold for arbitrary inputs.

See: spec/protocols/differance.md
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest
from hypothesis import assume, given, settings, strategies as st

from agents.differance.operad import (
    TRACED_OPERAD,
    TracedAgent,
    TracedOperation,
    create_traced_operad,
    traced_par,
    traced_seq,
)
from agents.differance.trace import Alternative, TraceMonoid, WiringTrace
from agents.operad import AGENT_OPERAD, LawStatus, OperadRegistry
from agents.poly import PolyAgent, from_function

# =============================================================================
# Test Fixtures
# =============================================================================


def make_inc_agent() -> PolyAgent[None, int, int]:
    """Create an increment agent for testing."""
    return from_function("inc", lambda x: x + 1)


def make_double_agent() -> PolyAgent[None, int, int]:
    """Create a doubling agent for testing."""
    return from_function("double", lambda x: x * 2)


def make_square_agent() -> PolyAgent[None, int, int]:
    """Create a squaring agent for testing."""
    return from_function("square", lambda x: x * x)


def make_negate_agent() -> PolyAgent[None, int, int]:
    """Create a negation agent for testing."""
    return from_function("negate", lambda x: -x)


def make_traced_inc() -> TracedAgent[None, int, int]:
    """Create a traced increment agent."""
    return TracedAgent.wrap(make_inc_agent())


def make_traced_double() -> TracedAgent[None, int, int]:
    """Create a traced doubling agent."""
    return TracedAgent.wrap(make_double_agent())


def make_traced_square() -> TracedAgent[None, int, int]:
    """Create a traced squaring agent."""
    return TracedAgent.wrap(make_square_agent())


def make_traced_with_ghosts() -> TracedAgent[None, int, int]:
    """Create a traced agent with some ghost alternatives."""
    agent = make_inc_agent()
    ghost = Alternative(
        operation="sub",
        inputs=("x",),
        reason_rejected="Addition preferred for this use case",
        could_revisit=True,
    )
    trace = WiringTrace.create(
        operation="select",
        inputs=("inc", "sub"),
        output="inc",
        context="Chose increment over subtraction",
        alternatives=(ghost,),
    )
    return TracedAgent(
        agent=agent,
        traces=TraceMonoid.empty().append(trace),
        name=agent.name,
    )


# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def simple_agent_strategy(draw: st.DrawFn) -> PolyAgent[None, int, int]:
    """Generate simple integer → integer agents for testing."""
    name = draw(st.sampled_from(["inc", "double", "square", "negate"]))
    return {
        "inc": make_inc_agent,
        "double": make_double_agent,
        "square": make_square_agent,
        "negate": make_negate_agent,
    }[name]()


@st.composite
def traced_agent_strategy(draw: st.DrawFn) -> TracedAgent[None, int, int]:
    """Generate traced agents for property testing."""
    agent = draw(simple_agent_strategy())

    # Maybe add some ghost alternatives
    num_ghosts = draw(st.integers(min_value=0, max_value=2))
    traces = TraceMonoid.empty()

    for i in range(num_ghosts):
        ghost = Alternative(
            operation=draw(st.sampled_from(["alt_a", "alt_b", "alt_c"])),
            inputs=("x",),
            reason_rejected=draw(st.text(min_size=5, max_size=20)),
            could_revisit=draw(st.booleans()),
        )
        trace = WiringTrace.create(
            operation="select",
            inputs=(agent.name, ghost.operation),
            output=agent.name,
            context=f"Selected {agent.name}",
            alternatives=(ghost,),
        )
        traces = traces.append(trace)

    return TracedAgent(agent=agent, traces=traces, name=agent.name)


# =============================================================================
# TracedAgent Tests
# =============================================================================


class TestTracedAgent:
    """Tests for TracedAgent wrapping and behavior."""

    def test_wrap_creates_traced_agent(self) -> None:
        """TracedAgent.wrap() creates a traced agent from a plain agent."""
        agent = make_inc_agent()
        traced = TracedAgent.wrap(agent)

        assert traced.agent is agent
        assert traced.name == agent.name
        assert len(traced.traces) == 0

    def test_traced_invoke_matches_plain_invoke(self) -> None:
        """TracedAgent.invoke() produces same result as plain agent."""
        agent = make_inc_agent()
        traced = TracedAgent.wrap(agent)

        plain_state = next(iter(agent.positions))
        traced_state = next(iter(traced.positions))

        _, plain_result = agent.invoke(plain_state, 5)
        _, traced_result = traced.invoke(traced_state, 5)

        assert plain_result == traced_result == 6

    def test_traced_transition_matches_plain_transition(self) -> None:
        """TracedAgent.transition() produces same result as plain agent."""
        agent = make_double_agent()
        traced = TracedAgent.wrap(agent)

        plain_state = next(iter(agent.positions))
        traced_state = next(iter(traced.positions))

        _, plain_result = agent.transition(plain_state, 7)
        _, traced_result = traced.transition(traced_state, 7)

        assert plain_result == traced_result == 14

    def test_traced_positions_match_plain_positions(self) -> None:
        """TracedAgent.positions matches underlying agent positions."""
        agent = make_square_agent()
        traced = TracedAgent.wrap(agent)

        assert traced.positions == agent.positions

    def test_traced_directions_match_plain_directions(self) -> None:
        """TracedAgent.directions() matches underlying agent."""
        agent = make_inc_agent()
        traced = TracedAgent.wrap(agent)

        state = next(iter(agent.positions))
        assert traced.directions(state) == agent.directions(state)

    def test_ghosts_returns_all_alternatives(self) -> None:
        """ghosts() returns all alternatives from trace history."""
        traced = make_traced_with_ghosts()
        ghosts = traced.ghosts()

        assert len(ghosts) == 1
        assert ghosts[0].operation == "sub"

    def test_explorable_ghosts_filters_by_could_revisit(self) -> None:
        """explorable_ghosts() filters to revisitable alternatives."""
        agent = make_inc_agent()
        ghost1 = Alternative("a", ("x",), "reason1", could_revisit=True)
        ghost2 = Alternative("b", ("x",), "reason2", could_revisit=False)

        trace = WiringTrace.create(
            operation="select",
            inputs=("inc",),
            output="inc",
            context="test",
            alternatives=(ghost1, ghost2),
        )

        traced = TracedAgent(
            agent=agent,
            traces=TraceMonoid.empty().append(trace),
            name=agent.name,
        )

        explorable = traced.explorable_ghosts()
        assert len(explorable) == 1
        assert ghost1 in explorable
        assert ghost2 not in explorable

    def test_repr_shows_name_and_trace_count(self) -> None:
        """repr() shows agent name and trace count."""
        traced = make_traced_with_ghosts()
        r = repr(traced)

        assert "inc" in r
        assert "traces=1" in r


# =============================================================================
# traced_seq Tests
# =============================================================================


class TestTracedSeq:
    """Tests for traced sequential composition."""

    def test_traced_seq_composes_agents(self) -> None:
        """traced_seq composes two agents sequentially."""
        a = make_traced_inc()
        b = make_traced_double()

        composed = traced_seq(a, b)
        state = next(iter(composed.positions))

        # (5 + 1) * 2 = 12
        _, result = composed.invoke(state, 5)
        assert result == 12

    def test_traced_seq_records_trace(self) -> None:
        """traced_seq records a WiringTrace for the composition."""
        a = make_traced_inc()
        b = make_traced_double()

        composed = traced_seq(a, b)

        assert len(composed.traces) == 1
        trace = composed.traces.traces[0]
        assert trace.operation == "seq"
        assert "inc" in trace.inputs
        assert "double" in trace.inputs

    def test_traced_seq_with_context(self) -> None:
        """traced_seq records custom context."""
        a = make_traced_inc()
        b = make_traced_double()

        composed = traced_seq(a, b, context="Memory cultivation pipeline")

        trace = composed.traces.traces[0]
        assert trace.context == "Memory cultivation pipeline"

    def test_traced_seq_with_alternatives(self) -> None:
        """traced_seq records ghost alternatives."""
        a = make_traced_inc()
        b = make_traced_double()

        ghost = Alternative(
            operation="par",
            inputs=("inc", "double"),
            reason_rejected="Order matters for this transformation",
            could_revisit=True,
        )

        composed = traced_seq(a, b, alternatives=(ghost,))

        trace = composed.traces.traces[0]
        assert len(trace.alternatives) == 1
        assert trace.alternatives[0] == ghost

    def test_traced_seq_preserves_operand_ghosts(self) -> None:
        """traced_seq preserves ghosts from both operands."""
        a = make_traced_with_ghosts()  # Has 1 ghost
        b = make_traced_with_ghosts()  # Has 1 ghost

        composed = traced_seq(a, b)

        # Should have: 1 from a + 1 from b + 0 from composition = 2
        all_ghosts = composed.ghosts()
        assert len(all_ghosts) >= 2

    def test_traced_seq_with_plain_agents(self) -> None:
        """traced_seq works with plain PolyAgents (auto-wraps)."""
        a = make_inc_agent()  # Plain PolyAgent
        b = make_double_agent()  # Plain PolyAgent

        composed = traced_seq(a, b)
        state = next(iter(composed.positions))

        _, result = composed.invoke(state, 5)
        assert result == 12

    def test_traced_seq_semantic_preservation(self) -> None:
        """traced_seq(a, b).agent behaves like seq(a, b)."""
        from agents.poly import sequential

        a = make_inc_agent()
        b = make_double_agent()

        traced = traced_seq(a, b)
        plain = sequential(a, b)

        traced_state = next(iter(traced.positions))
        plain_state = next(iter(plain.positions))

        for x in [0, 1, 5, 10, -3]:
            _, traced_result = traced.invoke(traced_state, x)
            _, plain_result = plain.invoke(plain_state, x)
            assert traced_result == plain_result, f"Mismatch at x={x}"


class TestTracedSeqPropertyBased:
    """Property-based tests for traced_seq laws."""

    @given(simple_agent_strategy(), simple_agent_strategy(), st.integers(-100, 100))
    @settings(max_examples=50)
    def test_semantic_preservation_property(
        self,
        a: PolyAgent[None, int, int],
        b: PolyAgent[None, int, int],
        x: int,
    ) -> None:
        """
        Semantic Preservation Law:
        traced_seq(a, b).agent.invoke(s, x) == seq(a, b).invoke(s, x)
        """
        from agents.poly import sequential

        traced = traced_seq(a, b)
        plain = sequential(a, b)

        traced_state = next(iter(traced.positions))
        plain_state = next(iter(plain.positions))

        _, traced_result = traced.invoke(traced_state, x)
        _, plain_result = plain.invoke(plain_state, x)

        assert traced_result == plain_result

    @given(traced_agent_strategy(), traced_agent_strategy())
    @settings(max_examples=50)
    def test_ghost_preservation_property(
        self,
        a: TracedAgent[None, int, int],
        b: TracedAgent[None, int, int],
    ) -> None:
        """
        Ghost Preservation Law:
        ghosts(traced_seq(a, b)) ⊇ ghosts(a) ∪ ghosts(b)
        """
        composed = traced_seq(a, b)

        a_ghosts = set(a.traces.ghosts())
        b_ghosts = set(b.traces.ghosts())
        composed_ghosts = set(composed.traces.ghosts())

        assert composed_ghosts >= a_ghosts | b_ghosts


# =============================================================================
# traced_par Tests
# =============================================================================


class TestTracedPar:
    """Tests for traced parallel composition."""

    def test_traced_par_composes_agents(self) -> None:
        """traced_par composes two agents in parallel."""
        a = make_traced_inc()
        b = make_traced_double()

        composed = traced_par(a, b)
        state = next(iter(composed.positions))

        # Both receive 5: (5+1, 5*2) = (6, 10)
        _, result = composed.invoke(state, 5)
        assert result == (6, 10)

    def test_traced_par_records_trace(self) -> None:
        """traced_par records a WiringTrace for the composition."""
        a = make_traced_inc()
        b = make_traced_double()

        composed = traced_par(a, b)

        assert len(composed.traces) == 1
        trace = composed.traces.traces[0]
        assert trace.operation == "par"

    def test_traced_par_preserves_operand_ghosts(self) -> None:
        """traced_par preserves ghosts from both operands."""
        a = make_traced_with_ghosts()
        b = make_traced_with_ghosts()

        composed = traced_par(a, b)

        all_ghosts = composed.ghosts()
        assert len(all_ghosts) >= 2

    def test_traced_par_semantic_preservation(self) -> None:
        """traced_par(a, b).agent behaves like par(a, b)."""
        from agents.poly import parallel

        a = make_inc_agent()
        b = make_double_agent()

        traced = traced_par(a, b)
        plain = parallel(a, b)

        traced_state = next(iter(traced.positions))
        plain_state = next(iter(plain.positions))

        for x in [0, 1, 5, 10, -3]:
            _, traced_result = traced.invoke(traced_state, x)
            _, plain_result = plain.invoke(plain_state, x)
            assert traced_result == plain_result, f"Mismatch at x={x}"


class TestTracedParPropertyBased:
    """Property-based tests for traced_par laws."""

    @given(simple_agent_strategy(), simple_agent_strategy(), st.integers(-100, 100))
    @settings(max_examples=50)
    def test_semantic_preservation_property(
        self,
        a: PolyAgent[None, int, int],
        b: PolyAgent[None, int, int],
        x: int,
    ) -> None:
        """
        Semantic Preservation Law:
        traced_par(a, b).agent.invoke(s, x) == par(a, b).invoke(s, x)
        """
        from agents.poly import parallel

        traced = traced_par(a, b)
        plain = parallel(a, b)

        traced_state = next(iter(traced.positions))
        plain_state = next(iter(plain.positions))

        _, traced_result = traced.invoke(traced_state, x)
        _, plain_result = plain.invoke(plain_state, x)

        assert traced_result == plain_result


# =============================================================================
# Associativity Tests
# =============================================================================


class TestTracedAssociativity:
    """Tests for associativity of traced composition."""

    def test_traced_seq_associativity_structure(self) -> None:
        """
        traced_seq(traced_seq(a, b), c) produces equivalent structure to
        traced_seq(a, traced_seq(b, c))
        """
        a = make_traced_inc()
        b = make_traced_double()
        c = make_traced_square()

        left = traced_seq(traced_seq(a, b), c)
        right = traced_seq(a, traced_seq(b, c))

        # Both should have same number of positions
        assert len(left.positions) == len(right.positions)

    def test_traced_seq_associativity_behavior(self) -> None:
        """
        traced_seq(traced_seq(a, b), c).invoke(s, x) ==
        traced_seq(a, traced_seq(b, c)).invoke(s, x)
        """
        a = make_traced_inc()
        b = make_traced_double()
        c = make_traced_square()

        left = traced_seq(traced_seq(a, b), c)
        right = traced_seq(a, traced_seq(b, c))

        left_state = next(iter(left.positions))
        right_state = next(iter(right.positions))

        for x in [0, 1, 5, 10]:
            _, left_result = left.invoke(left_state, x)
            _, right_result = right.invoke(right_state, x)
            assert left_result == right_result, f"Mismatch at x={x}"


class TestTracedAssociativityPropertyBased:
    """Property-based tests for associativity."""

    @given(
        simple_agent_strategy(),
        simple_agent_strategy(),
        simple_agent_strategy(),
        st.integers(-10, 10),
    )
    @settings(max_examples=30)
    def test_associativity_property(
        self,
        a: PolyAgent[None, int, int],
        b: PolyAgent[None, int, int],
        c: PolyAgent[None, int, int],
        x: int,
    ) -> None:
        """
        Associativity Law:
        traced_seq(traced_seq(a, b), c) ≅ traced_seq(a, traced_seq(b, c))
        """
        left = traced_seq(traced_seq(a, b), c)
        right = traced_seq(a, traced_seq(b, c))

        left_state = next(iter(left.positions))
        right_state = next(iter(right.positions))

        _, left_result = left.invoke(left_state, x)
        _, right_result = right.invoke(right_state, x)

        assert left_result == right_result


# =============================================================================
# TRACED_OPERAD Tests
# =============================================================================


class TestTracedOperad:
    """Tests for the TRACED_OPERAD definition."""

    def test_traced_operad_exists(self) -> None:
        """TRACED_OPERAD is defined and has the expected name."""

        assert TRACED_OPERAD is not None
        assert TRACED_OPERAD.name == "TracedOperad"

    def test_traced_operad_has_traced_seq(self) -> None:
        """TRACED_OPERAD has traced_seq operation."""

        op = TRACED_OPERAD.get("traced_seq")
        assert op is not None
        assert op.arity == 2

    def test_traced_operad_has_traced_par(self) -> None:
        """TRACED_OPERAD has traced_par operation."""

        op = TRACED_OPERAD.get("traced_par")
        assert op is not None
        assert op.arity == 2

    def test_traced_operad_inherits_agent_operad_operations(self) -> None:
        """TRACED_OPERAD inherits all AGENT_OPERAD operations."""

        # Should have seq, par, branch, fix, trace from AGENT_OPERAD
        assert TRACED_OPERAD.get("seq") is not None
        assert TRACED_OPERAD.get("par") is not None
        assert TRACED_OPERAD.get("branch") is not None
        assert TRACED_OPERAD.get("fix") is not None
        assert TRACED_OPERAD.get("trace") is not None

    def test_traced_operad_registered_in_registry(self) -> None:
        """TRACED_OPERAD is registered in OperadRegistry."""
        registered = OperadRegistry.get("TracedOperad")
        assert registered is not None
        assert registered.name == "TracedOperad"

    def test_traced_operad_has_laws(self) -> None:
        """TRACED_OPERAD has laws for verification."""

        law_names = [law.name for law in TRACED_OPERAD.laws]

        # Should have traced-specific laws
        assert "semantic_preservation_seq" in law_names
        assert "ghost_preservation_seq" in law_names
        assert "traced_seq_associativity" in law_names

        # Should inherit AGENT_OPERAD laws
        assert "seq_associativity" in law_names
        assert "par_associativity" in law_names

    def test_traced_operad_compose_via_operad(self) -> None:
        """Can use TRACED_OPERAD.compose() to perform traced composition."""

        a = make_inc_agent()
        b = make_double_agent()

        # Wrap as TracedAgents
        ta = TracedAgent.wrap(a)
        tb = TracedAgent.wrap(b)

        composed = TRACED_OPERAD.compose("traced_seq", ta, tb)
        assert isinstance(composed, TracedAgent)

        state = next(iter(composed.positions))
        _, result = composed.invoke(state, 5)
        assert result == 12


# =============================================================================
# Law Verification Tests
# =============================================================================


class TestLawVerification:
    """Tests for operad law verification functions."""

    def test_verify_semantic_preservation_seq(self) -> None:
        """Semantic preservation law passes for traced_seq."""

        a = make_inc_agent()
        b = make_double_agent()

        result = TRACED_OPERAD.verify_law("semantic_preservation_seq", a, b, 5)

        assert result.passed
        assert result.status in (LawStatus.PASSED, LawStatus.STRUCTURAL)

    def test_verify_ghost_preservation_seq(self) -> None:
        """Ghost preservation law passes for traced_seq."""

        a = make_traced_with_ghosts()
        b = make_traced_with_ghosts()

        result = TRACED_OPERAD.verify_law("ghost_preservation_seq", a, b)

        assert result.passed

    def test_verify_traced_associativity(self) -> None:
        """Associativity law passes for traced_seq."""

        a = make_traced_inc()
        b = make_traced_double()
        c = make_traced_square()

        result = TRACED_OPERAD.verify_law("traced_seq_associativity", a, b, c)

        assert result.passed


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests with other systems."""

    def test_traced_composition_chain(self) -> None:
        """Can chain multiple traced compositions with trace accumulation."""
        a = make_traced_inc()
        b = make_traced_double()
        c = make_traced_square()

        # Build: ((a >> b) >> c)
        step1 = traced_seq(a, b, context="Step 1: inc then double")
        step2 = traced_seq(step1, c, context="Step 2: add squaring")

        # Should have accumulated traces
        assert len(step2.traces) == 2

        # Should preserve semantic behavior
        state = next(iter(step2.positions))
        _, result = step2.invoke(state, 3)
        # ((3 + 1) * 2) ^ 2 = 8^2 = 64
        assert result == 64

    def test_traced_composition_with_ghosts_at_each_step(self) -> None:
        """Ghosts from each step are preserved."""
        a = make_traced_inc()
        b = make_traced_double()
        c = make_traced_square()

        ghost1 = Alternative("alt1", ("x",), "Alternative for step 1", True)
        ghost2 = Alternative("alt2", ("x",), "Alternative for step 2", True)

        step1 = traced_seq(a, b, alternatives=(ghost1,))
        step2 = traced_seq(step1, c, alternatives=(ghost2,))

        all_ghosts = step2.ghosts()
        assert len(all_ghosts) == 2
        assert ghost1 in all_ghosts
        assert ghost2 in all_ghosts

    def test_mixed_traced_and_plain_agents(self) -> None:
        """Can mix traced and plain agents in compositions."""
        traced = make_traced_with_ghosts()
        plain = make_double_agent()

        # Compose traced with plain
        composed = traced_seq(traced, plain)

        # Should work and preserve ghosts from traced
        assert len(composed.ghosts()) >= 1

        state = next(iter(composed.positions))
        _, result = composed.invoke(state, 5)
        assert result == 12  # (5 + 1) * 2
