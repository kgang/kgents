"""
Property-based category law verification.

Philosophy: Laws must hold for ALL agents, not just handpicked examples.

Phase 3/6 of test evolution plan: Hypothesis-powered law verification.
"""

import pytest
from functools import reduce

from bootstrap import ID, compose

# Optional hypothesis import with graceful fallback
try:
    from hypothesis import given, settings, assume
    from testing.strategies import simple_agents, agent_chains

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False

    # Create dummy decorators so module can be imported
    def given(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def settings(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def simple_agents():
        return None

    def agent_chains(*args, **kwargs):
        return None


pytestmark = pytest.mark.skipif(
    not HYPOTHESIS_AVAILABLE,
    reason="hypothesis package required for property-based tests",
)


@pytest.mark.law("identity")
@pytest.mark.property
class TestIdentityLawProperty:
    """Property-based identity law tests.

    Identity law: For all f, Id >> f == f == f >> Id
    """

    @given(agent=simple_agents())
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_left_identity_property(self, agent):
        """For all f: Id >> f == f."""
        composed = compose(ID, agent)

        test_input = 42
        direct = await agent.invoke(test_input)
        via_id = await composed.invoke(test_input)

        assert direct == via_id, f"Left identity failed: {agent.name}"

    @given(agent=simple_agents())
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_right_identity_property(self, agent):
        """For all f: f >> Id == f."""
        composed = compose(agent, ID)

        test_input = 42
        direct = await agent.invoke(test_input)
        via_id = await composed.invoke(test_input)

        assert direct == via_id, f"Right identity failed: {agent.name}"

    @given(agent=simple_agents())
    @settings(max_examples=50)
    @pytest.mark.asyncio
    async def test_identity_both_sides_property(self, agent):
        """For all f: Id >> f >> Id == f."""
        composed = compose(compose(ID, agent), ID)

        test_input = 42
        direct = await agent.invoke(test_input)
        via_ids = await composed.invoke(test_input)

        assert direct == via_ids, f"Both-side identity failed: {agent.name}"


@pytest.mark.law("associativity")
@pytest.mark.property
class TestAssociativityProperty:
    """Property-based associativity tests.

    Associativity law: For all f, g, h: (f >> g) >> h == f >> (g >> h)
    """

    @given(agents=agent_chains(min_length=3, max_length=3))
    @settings(max_examples=50)
    @pytest.mark.asyncio
    async def test_associativity_property(self, agents):
        """For all f, g, h: (f >> g) >> h == f >> (g >> h)."""
        f, g, h = agents

        left = compose(compose(f, g), h)
        right = compose(f, compose(g, h))

        test_input = 0

        left_result = await left.invoke(test_input)
        right_result = await right.invoke(test_input)

        assert left_result == right_result, (
            f"Associativity failed: ({f.name} >> {g.name}) >> {h.name} "
            f"!= {f.name} >> ({g.name} >> {h.name})"
        )

    @given(agents=agent_chains(min_length=2, max_length=8))
    @settings(max_examples=25)
    @pytest.mark.asyncio
    async def test_arbitrary_chain_length(self, agents):
        """Composition works for arbitrary chain lengths."""
        composed = reduce(compose, agents)

        result = await composed.invoke(0)

        # Verify it's an integer (all our test agents are int -> int)
        assert isinstance(result, int), f"Expected int, got {type(result)}"

    @given(agents=agent_chains(min_length=4, max_length=4))
    @settings(max_examples=25)
    @pytest.mark.asyncio
    async def test_four_way_associativity(self, agents):
        """Verify all groupings of 4 agents are equivalent.

        For a, b, c, d: All of these must be equal:
        - ((a >> b) >> c) >> d
        - (a >> (b >> c)) >> d
        - (a >> b) >> (c >> d)
        - a >> ((b >> c) >> d)
        - a >> (b >> (c >> d))
        """
        a, b, c, d = agents
        test_input = 0

        # All possible groupings
        g1 = compose(compose(compose(a, b), c), d)
        g2 = compose(compose(a, compose(b, c)), d)
        g3 = compose(compose(a, b), compose(c, d))
        g4 = compose(a, compose(compose(b, c), d))
        g5 = compose(a, compose(b, compose(c, d)))

        r1 = await g1.invoke(test_input)
        r2 = await g2.invoke(test_input)
        r3 = await g3.invoke(test_input)
        r4 = await g4.invoke(test_input)
        r5 = await g5.invoke(test_input)

        assert r1 == r2 == r3 == r4 == r5, "Four-way associativity failed"


@pytest.mark.law("identity")
@pytest.mark.law("associativity")
@pytest.mark.property
class TestCategoryProperties:
    """Property tests for general category properties."""

    @given(agent=simple_agents())
    @settings(max_examples=50)
    @pytest.mark.asyncio
    async def test_compose_returns_agent(self, agent):
        """Composition produces another agent (closure)."""
        composed = compose(agent, ID)

        # Must have invoke method
        assert hasattr(composed, "invoke")

        # Must be callable
        result = await composed.invoke(0)
        assert result is not None or result == 0  # Allow 0 as valid result

    @given(agents=agent_chains(min_length=2, max_length=2))
    @settings(max_examples=50)
    @pytest.mark.asyncio
    async def test_composition_determinism(self, agents):
        """Same composition always gives same result."""
        f, g = agents

        c1 = compose(f, g)
        c2 = compose(f, g)

        test_input = 42

        r1 = await c1.invoke(test_input)
        r2 = await c2.invoke(test_input)

        assert r1 == r2, f"Non-deterministic composition: {f.name} >> {g.name}"

    @pytest.mark.asyncio
    async def test_identity_is_neutral_element(self):
        """ID is the neutral element of composition."""
        # ID >> ID == ID
        composed = compose(ID, ID)

        result = await composed.invoke(99)
        assert result == 99, "ID >> ID should be identity"


# Run with: pytest impl/claude/bootstrap/_tests/test_laws_property.py -v -m property
