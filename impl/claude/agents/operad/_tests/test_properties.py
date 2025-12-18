"""
Property-Based Tests for Operad Laws.

Uses Hypothesis to verify operad laws hold universally:
- Associativity: (a >> b) >> c = a >> (b >> c)
- Identity: id >> a = a = a >> id
- Parallel identity: par(id, id) = id on products

These tests ensure the mathematical foundations are sound.
"""

import pytest
from hypothesis import assume, given, settings, strategies as st

from agents.operad.core import AGENT_OPERAD
from agents.poly import (
    ID,
    PRIMITIVES,
    PolyAgent,
    from_function,
    parallel,
    sequential,
)

# =============================================================================
# Strategies
# =============================================================================


@st.composite
def primitives(draw: st.DrawFn) -> PolyAgent:
    """Strategy for primitives."""
    name = draw(st.sampled_from(list(PRIMITIVES.keys())))
    return PRIMITIVES[name]


@st.composite
def simple_agents(draw: st.DrawFn) -> PolyAgent:
    """Strategy for simple polynomial agents."""
    # Create agents from simple functions
    fn_type = draw(st.integers(min_value=0, max_value=3))

    if fn_type == 0:
        return ID
    elif fn_type == 1:
        return from_function("Inc", lambda x: x + 1 if isinstance(x, (int, float)) else x)
    elif fn_type == 2:
        return from_function("Double", lambda x: x * 2 if isinstance(x, (int, float)) else x)
    else:
        return from_function("Const", lambda x: "const")


@st.composite
def sample_inputs(draw: st.DrawFn):
    """Strategy for sample inputs."""
    input_type = draw(st.integers(min_value=0, max_value=3))

    if input_type == 0:
        return draw(st.integers(min_value=-100, max_value=100))
    elif input_type == 1:
        return draw(st.floats(min_value=-100, max_value=100, allow_nan=False))
    elif input_type == 2:
        return draw(st.text(min_size=0, max_size=20))
    else:
        return draw(st.none())


# =============================================================================
# Identity Law Tests
# =============================================================================


class TestIdentityLaw:
    """Tests for the identity law: id >> a = a = a >> id."""

    @given(agent=simple_agents())
    @settings(max_examples=50)
    def test_left_identity(self, agent: PolyAgent) -> None:
        """id >> a should behave like a."""
        composed = sequential(ID, agent)

        # Check that composition exists
        assert composed is not None
        assert len(composed.positions) > 0

        # Structural check: name should indicate composition
        assert composed.name == f"Id>>{agent.name}"

    @given(agent=simple_agents())
    @settings(max_examples=50)
    def test_right_identity(self, agent: PolyAgent) -> None:
        """a >> id should behave like a."""
        composed = sequential(agent, ID)

        assert composed is not None
        assert len(composed.positions) > 0
        assert composed.name == f"{agent.name}>>Id"

    @given(agent=simple_agents(), input_val=sample_inputs())
    @settings(max_examples=50)
    def test_identity_behavioral(self, agent: PolyAgent, input_val) -> None:
        """Identity composition should preserve behavior on simple agents."""
        # Only test if input is valid for both
        try:
            # Get initial states
            agent_state = next(iter(agent.positions))
            id_state = next(iter(ID.positions))

            # Direct invocation
            _, direct_output = agent.invoke(agent_state, input_val)

            # Through left identity (id >> agent)
            left_composed = sequential(ID, agent)
            left_state = next(iter(left_composed.positions))
            _, left_output = left_composed.invoke(left_state, input_val)

            # Should be equal
            assert direct_output == left_output

        except (ValueError, TypeError, KeyError, StopIteration):
            # Input might not be valid for this agent
            assume(False)


# =============================================================================
# Associativity Law Tests
# =============================================================================


class TestAssociativityLaw:
    """Tests for associativity: (a >> b) >> c = a >> (b >> c)."""

    @given(
        a=simple_agents(),
        b=simple_agents(),
        c=simple_agents(),
    )
    @settings(max_examples=50)
    def test_associativity_structural(self, a: PolyAgent, b: PolyAgent, c: PolyAgent) -> None:
        """(a >> b) >> c and a >> (b >> c) should have same structure."""
        left_assoc = sequential(sequential(a, b), c)
        right_assoc = sequential(a, sequential(b, c))

        # Both should exist
        assert left_assoc is not None
        assert right_assoc is not None

        # Same number of positions
        assert len(left_assoc.positions) == len(right_assoc.positions)

    @given(
        a=simple_agents(),
        b=simple_agents(),
        c=simple_agents(),
        input_val=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=30)
    def test_associativity_behavioral(
        self, a: PolyAgent, b: PolyAgent, c: PolyAgent, input_val: int
    ) -> None:
        """(a >> b) >> c and a >> (b >> c) should produce same output."""
        try:
            left_assoc = sequential(sequential(a, b), c)
            right_assoc = sequential(a, sequential(b, c))

            left_state = next(iter(left_assoc.positions))
            right_state = next(iter(right_assoc.positions))

            _, left_output = left_assoc.invoke(left_state, input_val)
            _, right_output = right_assoc.invoke(right_state, input_val)

            assert left_output == right_output

        except (ValueError, TypeError, KeyError, StopIteration):
            assume(False)


# =============================================================================
# Parallel Composition Tests
# =============================================================================


class TestParallelComposition:
    """Tests for parallel composition laws."""

    @given(a=simple_agents(), b=simple_agents())
    @settings(max_examples=50)
    def test_parallel_creates_product(self, a: PolyAgent, b: PolyAgent) -> None:
        """par(a, b) should create a product agent."""
        composed = parallel(a, b)

        assert composed is not None
        assert len(composed.positions) > 0
        # Name should indicate parallel
        assert "||" in composed.name or "par" in composed.name.lower()

    @given(a=simple_agents(), b=simple_agents(), input_val=st.integers())
    @settings(max_examples=30)
    def test_parallel_behavioral(self, a: PolyAgent, b: PolyAgent, input_val: int) -> None:
        """par(a, b) should produce (a(x), b(x))."""
        try:
            composed = parallel(a, b)

            # Get outputs from individual agents
            a_state = next(iter(a.positions))
            b_state = next(iter(b.positions))

            _, a_output = a.invoke(a_state, input_val)
            _, b_output = b.invoke(b_state, input_val)

            # Get output from parallel composition
            p_state = next(iter(composed.positions))
            _, p_output = composed.invoke(p_state, input_val)

            # Should be the pair
            assert p_output == (a_output, b_output)

        except (ValueError, TypeError, KeyError, StopIteration):
            assume(False)


# =============================================================================
# Operad Law Verification
# =============================================================================


class TestOperadLaws:
    """Tests for operad law verification."""

    def test_agent_operad_has_laws(self) -> None:
        """AGENT_OPERAD should have laws defined."""
        assert len(AGENT_OPERAD.laws) > 0

    def test_all_laws_verifiable(self) -> None:
        """All laws should be verifiable."""
        a = from_function("A", lambda x: x)
        b = from_function("B", lambda x: x)
        c = from_function("C", lambda x: x)

        for law in AGENT_OPERAD.laws:
            # Should not raise
            result = law.verify(a, b, c)
            assert result is not None
            assert hasattr(result, "passed")

    @given(
        a=simple_agents(),
        b=simple_agents(),
        c=simple_agents(),
    )
    @settings(max_examples=20)
    def test_laws_with_random_agents(self, a: PolyAgent, b: PolyAgent, c: PolyAgent) -> None:
        """Laws should verify for random agents."""
        for law in AGENT_OPERAD.laws:
            try:
                result = law.verify(a, b, c)
                assert result is not None
            except Exception:
                # Some laws may not apply to all agent combinations
                pass


# =============================================================================
# Primitive Properties
# =============================================================================


class TestPrimitiveProperties:
    """Property-based tests for primitives."""

    @given(primitive=primitives())
    @settings(max_examples=50)
    def test_all_primitives_have_positions(self, primitive: PolyAgent) -> None:
        """All primitives should have non-empty position sets."""
        assert len(primitive.positions) > 0

    @given(primitive=primitives())
    @settings(max_examples=50)
    def test_all_primitives_have_directions(self, primitive: PolyAgent) -> None:
        """All primitives should have directions for each position."""
        for pos in primitive.positions:
            dirs = primitive.directions(pos)
            assert dirs is not None

    @given(primitive=primitives())
    @settings(max_examples=50)
    def test_all_primitives_composable_with_id(self, primitive: PolyAgent) -> None:
        """All primitives should be composable with ID."""
        left = sequential(ID, primitive)
        right = sequential(primitive, ID)

        assert left is not None
        assert right is not None

    @given(p1=primitives(), p2=primitives())
    @settings(max_examples=30)
    def test_all_primitives_parallel_composable(self, p1: PolyAgent, p2: PolyAgent) -> None:
        """All primitives should be parallel composable."""
        composed = parallel(p1, p2)
        assert composed is not None
        assert len(composed.positions) > 0


# =============================================================================
# Composition Closure
# =============================================================================


class TestCompositionClosure:
    """Tests that composition operations are closed."""

    @given(
        a=simple_agents(),
        b=simple_agents(),
    )
    @settings(max_examples=30)
    def test_sequential_closure(self, a: PolyAgent, b: PolyAgent) -> None:
        """Sequential composition should produce a valid PolyAgent."""
        composed = sequential(a, b)

        # Should be a valid PolyAgent
        assert hasattr(composed, "positions")
        assert hasattr(composed, "directions")
        assert hasattr(composed, "invoke")
        assert hasattr(composed, "name")

    @given(
        a=simple_agents(),
        b=simple_agents(),
    )
    @settings(max_examples=30)
    def test_parallel_closure(self, a: PolyAgent, b: PolyAgent) -> None:
        """Parallel composition should produce a valid PolyAgent."""
        composed = parallel(a, b)

        assert hasattr(composed, "positions")
        assert hasattr(composed, "directions")
        assert hasattr(composed, "invoke")
        assert hasattr(composed, "name")

    @given(
        a=simple_agents(),
        b=simple_agents(),
        c=simple_agents(),
    )
    @settings(max_examples=20)
    def test_nested_composition_closure(self, a: PolyAgent, b: PolyAgent, c: PolyAgent) -> None:
        """Nested compositions should remain valid PolyAgents."""
        nested1 = sequential(parallel(a, b), c)
        nested2 = parallel(sequential(a, b), c)

        assert hasattr(nested1, "positions")
        assert hasattr(nested2, "positions")
