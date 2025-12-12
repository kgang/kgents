"""
Tests for SoulFunctor UniversalFunctor compliance (Alethic Algebra Phase 4).

Verifies that SoulFunctor satisfies the functor laws:
1. Identity: F(id) = id in F's category
2. Composition: F(g . f) = F(g) . F(f)

The Soul functor lifts agents to operate with persona/soul awareness.
The Categorical Imperative: agents act through the lens of identity.
"""

import pytest
from agents.a.functor import (
    FunctorRegistry,
    verify_composition_law,
    verify_functor,
    verify_identity_law,
)
from agents.k import KENT_EIGENVECTORS, PersonaSeed, PersonaState
from agents.k.functor import (
    Soul,
    SoulAgent,
    SoulFunctor,
    soul,
    soul_lift,
    soul_with,
    unlift,
    unwrap,
)
from bootstrap.types import Agent

# =============================================================================
# Test Fixtures: Agents
# =============================================================================


class IdentityAgent(Agent[int, int]):
    """Identity agent for law testing."""

    @property
    def name(self) -> str:
        return "Identity"

    async def invoke(self, input: int) -> int:
        return input


class DoubleAgent(Agent[int, int]):
    """Doubles its input."""

    @property
    def name(self) -> str:
        return "Double"

    async def invoke(self, input: int) -> int:
        return input * 2


class AddOneAgent(Agent[int, int]):
    """Adds one to input."""

    @property
    def name(self) -> str:
        return "AddOne"

    async def invoke(self, input: int) -> int:
        return input + 1


class StringifyAgent(Agent[int, str]):
    """Converts int to string."""

    @property
    def name(self) -> str:
        return "Stringify"

    async def invoke(self, input: int) -> str:
        return f"value={input}"


# =============================================================================
# Soul Container Tests
# =============================================================================


class TestSoulContainer:
    """Test the Soul container type."""

    def test_soul_creation(self) -> None:
        """Soul should wrap a value."""
        s = Soul(value=42)
        assert s.value == 42

    def test_soul_with_default_eigenvectors(self) -> None:
        """Soul should have default eigenvectors."""
        s = Soul(value=42)
        assert s.eigenvectors is not None
        assert s.eigenvectors.aesthetic.value < 0.5  # Minimalist

    def test_soul_equality(self) -> None:
        """Soul equality based on value and context."""
        s1 = Soul(value=42)
        s2 = Soul(value=42)
        s3 = Soul(value=43)

        assert s1 == s2
        assert s1 != s3

    def test_soul_map(self) -> None:
        """Soul.map should apply function preserving context."""
        s = Soul(value=5)
        doubled = s.map(lambda x: x * 2)

        assert doubled.value == 10
        assert doubled.eigenvectors == s.eigenvectors

    def test_soul_with_metadata(self) -> None:
        """with_metadata should add metadata preserving context."""
        s = Soul(value=42)
        s2 = s.with_metadata("source", "test")

        assert s2.value == 42
        assert s2.metadata["source"] == "test"
        assert s2.eigenvectors == s.eigenvectors

    def test_soul_context_prompt(self) -> None:
        """context_prompt should return eigenvector context."""
        s = Soul(value=42)
        prompt = s.context_prompt

        assert isinstance(prompt, str)
        assert "Personality Coordinates" in prompt

    def test_soul_repr(self) -> None:
        """Soul repr should be informative."""
        s = Soul(value=42)
        assert "Soul(42)" in repr(s)


# =============================================================================
# SoulFunctor Law Tests
# =============================================================================


class TestSoulFunctorLaws:
    """Verify SoulFunctor satisfies functor laws."""

    @pytest.mark.asyncio
    async def test_identity_law(self) -> None:
        """F(id)(Soul(x)) = Soul(x)."""
        result = await verify_identity_law(SoulFunctor, IdentityAgent(), Soul(42))

        assert result.passed is True
        assert result.left_result == Soul(42)
        assert result.right_result == Soul(42)

    @pytest.mark.asyncio
    async def test_identity_law_preserves_context(self) -> None:
        """F(id) should preserve soul context."""
        lifted = SoulFunctor.lift(IdentityAgent())
        input_soul = Soul(
            value=42, eigenvectors=KENT_EIGENVECTORS, metadata={"test": "value"}
        )

        result = await lifted.invoke(input_soul)

        assert result.value == 42
        assert result.eigenvectors == input_soul.eigenvectors
        assert result.metadata == input_soul.metadata

    @pytest.mark.asyncio
    async def test_composition_law(self) -> None:
        """F(g . f) = F(g) . F(f)."""
        result = await verify_composition_law(
            SoulFunctor,
            DoubleAgent(),
            AddOneAgent(),
            Soul(5),
        )

        assert result.passed is True
        # (5 * 2) + 1 = 11
        assert result.left_result == Soul(11)
        assert result.right_result == Soul(11)

    @pytest.mark.asyncio
    async def test_composition_law_preserves_context(self) -> None:
        """Composition should preserve soul context through pipeline."""
        f = DoubleAgent()
        g = AddOneAgent()

        lifted_f = SoulFunctor.lift(f)
        lifted_g = SoulFunctor.lift(g)
        composed = lifted_f >> lifted_g

        input_soul = Soul(value=5, metadata={"source": "test"})
        result = await composed.invoke(input_soul)

        # Value should be (5 * 2) + 1 = 11
        assert result.value == 11
        # Context should be preserved
        assert result.metadata == {"source": "test"}

    @pytest.mark.asyncio
    async def test_full_verification(self) -> None:
        """Complete functor verification."""
        report = await verify_functor(
            SoulFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            Soul(5),
        )

        assert report.passed is True
        assert report.functor_name == "SoulFunctor"


# =============================================================================
# SoulFunctor Pure Tests
# =============================================================================


class TestSoulFunctorPure:
    """Test SoulFunctor.pure() - embedding values in soul context."""

    def test_pure_wraps_value(self) -> None:
        """pure(x) = Soul(x)."""
        result = SoulFunctor.pure(42)

        assert isinstance(result, Soul)
        assert result.value == 42

    def test_pure_uses_default_eigenvectors(self) -> None:
        """pure() should use KENT_EIGENVECTORS by default."""
        result = SoulFunctor.pure(42)

        assert result.eigenvectors is not None
        assert result.eigenvectors.aesthetic.value < 0.5  # Minimalist

    def test_pure_with_different_types(self) -> None:
        """pure() works with various types."""
        # String
        s_str = SoulFunctor.pure("hello")
        assert s_str.value == "hello"

        # List
        s_list = SoulFunctor.pure([1, 2, 3])
        assert s_list.value == [1, 2, 3]

        # Dict
        s_dict = SoulFunctor.pure({"key": "value"})
        assert s_dict.value == {"key": "value"}


# =============================================================================
# SoulFunctor Lift Tests
# =============================================================================


class TestSoulFunctorLift:
    """Test SoulFunctor.lift() behavior."""

    def test_lift_returns_soul_agent(self) -> None:
        """lift() returns a SoulAgent."""
        agent = DoubleAgent()
        lifted = SoulFunctor.lift(agent)

        assert isinstance(lifted, SoulAgent)

    def test_lift_preserves_inner_agent(self) -> None:
        """lift() should preserve the inner agent."""
        agent = DoubleAgent()
        lifted = SoulFunctor.lift(agent)

        assert lifted.inner is agent

    def test_lift_agent_name(self) -> None:
        """Lifted agent should have descriptive name."""
        agent = DoubleAgent()
        lifted = SoulFunctor.lift(agent)

        assert lifted.name == "Soul(Double)"

    @pytest.mark.asyncio
    async def test_lift_processes_values(self) -> None:
        """Lifted agent should process values through inner agent."""
        lifted = SoulFunctor.lift(DoubleAgent())
        result = await lifted.invoke(Soul(5))

        assert result.value == 10

    @pytest.mark.asyncio
    async def test_lift_with_persona(self) -> None:
        """lift_with_persona should set custom persona."""
        persona = PersonaState(seed=PersonaSeed(name="Test"))
        lifted = SoulFunctor.lift_with_persona(
            DoubleAgent(),
            persona=persona,
        )

        assert lifted._default_persona is persona


# =============================================================================
# Registry Tests
# =============================================================================


class TestSoulFunctorRegistration:
    """Verify SoulFunctor is properly registered."""

    def test_soul_functor_registered(self) -> None:
        """SoulFunctor is in the registry."""
        functor = FunctorRegistry.get("Soul")

        assert functor is not None
        assert functor.__name__ == "SoulFunctor"

    def test_soul_functor_in_all_functors(self) -> None:
        """SoulFunctor appears in all_functors()."""
        all_functors = FunctorRegistry.all_functors()

        assert "Soul" in all_functors
        # Check by name since module paths may differ
        assert all_functors["Soul"].__name__ == "SoulFunctor"


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_soul_function(self) -> None:
        """soul() should be alias for pure()."""
        s = soul(42)
        assert isinstance(s, Soul)
        assert s.value == 42

    def test_soul_lift_function(self) -> None:
        """soul_lift() should be alias for lift()."""
        lifted = soul_lift(DoubleAgent())
        assert isinstance(lifted, SoulAgent)

    def test_soul_with_function(self) -> None:
        """soul_with() should create soul with explicit context."""
        persona = PersonaState(seed=PersonaSeed(name="Custom"))
        s = soul_with(42, persona=persona, source="test")

        assert s.value == 42
        assert s.persona is persona
        assert s.metadata["source"] == "test"

    def test_unlift_function(self) -> None:
        """unlift() should extract inner agent."""
        agent = DoubleAgent()
        lifted = soul_lift(agent)
        unlifted = unlift(lifted)

        assert unlifted is agent

    def test_unwrap_function(self) -> None:
        """unwrap() should extract raw value."""
        s = soul(42)
        value = unwrap(s)

        assert value == 42


# =============================================================================
# SoulAgent Behavior Tests
# =============================================================================


class TestSoulAgentBehavior:
    """Test SoulAgent specific behaviors."""

    @pytest.mark.asyncio
    async def test_soul_agent_context_flow(self) -> None:
        """Soul context should flow through agent invocation."""
        lifted = soul_lift(DoubleAgent())

        # Create soul with custom metadata
        input_soul = soul_with(5, source="user", priority="high")
        result = await lifted.invoke(input_soul)

        # Value transformed
        assert result.value == 10
        # Metadata preserved
        assert result.metadata["source"] == "user"
        assert result.metadata["priority"] == "high"

    @pytest.mark.asyncio
    async def test_soul_agent_chain(self) -> None:
        """Multiple soul agents can be chained."""
        double = soul_lift(DoubleAgent())
        add_one = soul_lift(AddOneAgent())

        chain = double >> add_one
        result = await chain.invoke(soul(5))

        # (5 * 2) + 1 = 11
        assert result.value == 11

    @pytest.mark.asyncio
    async def test_soul_agent_with_type_change(self) -> None:
        """Soul agent should handle type-changing agents."""
        lifted = soul_lift(StringifyAgent())
        result = await lifted.invoke(soul(42))

        assert result.value == "value=42"
        assert isinstance(result, Soul)


# =============================================================================
# Integration Tests
# =============================================================================


class TestSoulFunctorIntegration:
    """Integration tests for SoulFunctor with other functors."""

    @pytest.mark.asyncio
    async def test_soul_with_eigenvector_influence(self) -> None:
        """Soul context should carry eigenvector information."""
        lifted = soul_lift(IdentityAgent())

        # Create soul with specific eigenvectors
        input_soul = Soul(value=42, eigenvectors=KENT_EIGENVECTORS)
        result = await lifted.invoke(input_soul)

        # Eigenvectors should flow through
        assert result.eigenvectors is KENT_EIGENVECTORS
        assert result.eigenvectors.aesthetic.value < 0.5  # Minimalist

    @pytest.mark.asyncio
    async def test_soul_metadata_accumulation(self) -> None:
        """Metadata should be preserved across transformations."""
        lifted = soul_lift(DoubleAgent())

        # Start with metadata
        s1 = soul(5).with_metadata("step", 0)
        s2 = await lifted.invoke(s1)

        # Original metadata preserved
        assert s2.metadata["step"] == 0
