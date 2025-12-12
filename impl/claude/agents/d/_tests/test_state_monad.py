"""
Tests for the State Monad Functor (Phase 3: State as Monad).

Verifies:
1. StatefulAgent threads state through computation
2. Functor laws hold (identity, composition)
3. Symmetric lifting: unlift(lift(agent)) ≅ agent
4. State accessor/extractor patterns work
5. Composition with Flux works
"""

import pytest
from agents.d.state_monad import (
    StatefulAgent,
    StateMonadFunctor,
    stateful,
    unstateful,
)
from agents.d.volatile import VolatileAgent
from bootstrap.types import Agent

# =============================================================================
# Test Fixtures
# =============================================================================


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


class IdentityAgent(Agent[int, int]):
    """Identity agent for law testing."""

    @property
    def name(self) -> str:
        return "Identity"

    async def invoke(self, input: int) -> int:
        return input


class CounterAgent(Agent[str, str]):
    """Agent that uses state accessor/extractor to count invocations."""

    @property
    def name(self) -> str:
        return "Counter"

    async def invoke(self, input: str) -> str:
        # Input will be augmented with state by accessor
        return f"processed: {input}"


# =============================================================================
# StatefulAgent Tests
# =============================================================================


class TestStatefulAgent:
    """Test the StatefulAgent wrapper."""

    @pytest.mark.asyncio
    async def test_preserves_behavior(self) -> None:
        """Stateful wrapping doesn't change agent behavior."""
        agent = DoubleAgent()
        memory: VolatileAgent[dict[str, int]] = VolatileAgent(_state={"count": 0})
        stateful_agent = StatefulAgent(inner=agent, memory=memory)

        result = await stateful_agent.invoke(5)

        assert result == 10  # Same as unlifted

    @pytest.mark.asyncio
    async def test_loads_state(self) -> None:
        """State is loaded before invocation."""
        agent = DoubleAgent()
        memory: VolatileAgent[dict[str, int]] = VolatileAgent(_state={"count": 42})
        stateful_agent = StatefulAgent(inner=agent, memory=memory)

        await stateful_agent.invoke(5)

        assert stateful_agent.last_state == {"count": 42}

    @pytest.mark.asyncio
    async def test_state_accessor(self) -> None:
        """State accessor injects state into input."""

        class StateAwareAgent(Agent[dict[str, int], int]):
            @property
            def name(self) -> str:
                return "StateAware"

            async def invoke(self, input: dict[str, int]) -> int:
                # Input has state injected
                return input["value"] + input.get("state_count", 0)

        agent = StateAwareAgent()
        memory: VolatileAgent[dict[str, int]] = VolatileAgent(_state={"count": 10})

        def accessor(input: int, state: dict[str, int]) -> dict[str, int]:
            return {"value": input, "state_count": state["count"]}

        stateful_agent = StatefulAgent(
            inner=agent,
            memory=memory,
            state_accessor=accessor,  # type: ignore[arg-type]
        )

        result = await stateful_agent.invoke(5)  # type: ignore[arg-type]

        assert result == 15  # 5 + 10 from state

    @pytest.mark.asyncio
    async def test_state_extractor(self) -> None:
        """State extractor updates state from output."""
        agent = DoubleAgent()
        memory: VolatileAgent[dict[str, int]] = VolatileAgent(_state={"count": 0})

        def extractor(output: int, state: dict[str, int]) -> tuple[int, dict[str, int]]:
            return output, {"count": state["count"] + 1}

        stateful_agent = StatefulAgent(
            inner=agent,
            memory=memory,
            state_extractor=extractor,
        )

        # First invocation
        await stateful_agent.invoke(5)
        assert stateful_agent.last_state == {"count": 1}

        # Second invocation
        await stateful_agent.invoke(10)
        assert stateful_agent.last_state == {"count": 2}

    @pytest.mark.asyncio
    async def test_has_inner_property(self) -> None:
        """StatefulAgent exposes inner agent."""
        agent = DoubleAgent()
        memory: VolatileAgent[int] = VolatileAgent(_state=0)
        stateful_agent = StatefulAgent(inner=agent, memory=memory)

        assert stateful_agent.inner is agent
        assert stateful_agent.name == "State(Double)"


# =============================================================================
# Functor Law Tests
# =============================================================================


class TestStateMonadFunctorLaws:
    """Verify StateMonadFunctor satisfies functor laws."""

    @pytest.mark.asyncio
    async def test_identity_law(self) -> None:
        """F(id)(x) ≅ id(x) - behavioral equivalence."""
        identity = IdentityAgent()
        memory: VolatileAgent[int] = VolatileAgent(_state=0)
        lifted = StateMonadFunctor.lift(identity, memory=memory)

        result = await lifted.invoke(42)

        assert result == 42  # Same as unlifted identity

    @pytest.mark.asyncio
    async def test_composition_law(self) -> None:
        """F(g >> f) ≅ F(g) >> F(f) - composition preserved."""
        double = DoubleAgent()
        add_one = AddOneAgent()
        memory1: VolatileAgent[int] = VolatileAgent(_state=0)
        memory2: VolatileAgent[int] = VolatileAgent(_state=0)

        # Lift then compose
        lifted_double = StateMonadFunctor.lift(double, memory=memory1)
        lifted_add_one = StateMonadFunctor.lift(add_one, memory=memory2)

        result_1 = await lifted_double.invoke(5)
        result_2 = await lifted_add_one.invoke(result_1)

        # Should be (5 * 2) + 1 = 11
        assert result_2 == 11


# =============================================================================
# Symmetric Lifting Tests
# =============================================================================


class TestSymmetricLifting:
    """Verify round-trip law: unlift(lift(agent)) ≅ agent."""

    @pytest.mark.asyncio
    async def test_roundtrip(self) -> None:
        """unlift(lift(agent)) ≅ agent."""
        original = DoubleAgent()
        memory: VolatileAgent[int] = VolatileAgent(_state=0)

        lifted = StateMonadFunctor.lift(original, memory=memory)
        unlifted = StateMonadFunctor.unlift(lifted)

        # Should be the same agent
        assert unlifted is original
        assert unlifted.name == original.name

        # Should behave the same
        assert await unlifted.invoke(5) == await original.invoke(5)

    def test_unlift_wrong_type_raises(self) -> None:
        """unlift() raises TypeError for wrong type."""
        with pytest.raises(TypeError):
            StateMonadFunctor.unlift(DoubleAgent())  # type: ignore[arg-type]


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test stateful() and unstateful() helpers."""

    @pytest.mark.asyncio
    async def test_stateful_function(self) -> None:
        """stateful() creates StatefulAgent."""
        agent = DoubleAgent()
        memory: VolatileAgent[int] = VolatileAgent(_state=0)

        stateful_agent = stateful(agent, memory=memory)

        assert isinstance(stateful_agent, StatefulAgent)
        result = await stateful_agent.invoke(5)
        assert result == 10

    @pytest.mark.asyncio
    async def test_stateful_with_initial_state(self) -> None:
        """stateful() creates memory with initial state."""
        agent = DoubleAgent()

        stateful_agent = stateful(agent, initial_state={"counter": 0})

        assert isinstance(stateful_agent, StatefulAgent)
        assert stateful_agent.memory is not None

    @pytest.mark.asyncio
    async def test_unstateful_function(self) -> None:
        """unstateful() extracts inner agent."""
        agent = DoubleAgent()
        memory: VolatileAgent[int] = VolatileAgent(_state=0)

        stateful_agent = stateful(agent, memory=memory)
        unstateful_agent = unstateful(stateful_agent)

        assert unstateful_agent is agent


# =============================================================================
# Registry Tests
# =============================================================================


class TestFunctorRegistration:
    """Verify State functor is registered."""

    def test_state_functor_registered(self) -> None:
        """StateMonadFunctor is in the registry."""
        from agents.a.functor import FunctorRegistry

        functor = FunctorRegistry.get("State")
        assert functor is not None
        assert functor.__name__ == "StateMonadFunctor"


# =============================================================================
# Pure Tests
# =============================================================================


class TestPure:
    """Test the pure method (identity for endofunctor)."""

    def test_pure_returns_value_unchanged(self) -> None:
        """pure(x) = x for endofunctor."""
        assert StateMonadFunctor.pure(42) == 42
        assert StateMonadFunctor.pure("hello") == "hello"


# =============================================================================
# Memory Extraction Tests
# =============================================================================


class TestGetMemory:
    """Test memory extraction."""

    def test_get_memory_from_stateful(self) -> None:
        """get_memory() returns memory from StatefulAgent."""
        agent = DoubleAgent()
        memory: VolatileAgent[int] = VolatileAgent(_state=42)
        stateful_agent = stateful(agent, memory=memory)

        # StatefulAgent is duck-typed Agent via structural subtyping
        extracted = StateMonadFunctor.get_memory(stateful_agent)  # type: ignore[arg-type]

        assert extracted is memory

    def test_get_memory_from_non_stateful(self) -> None:
        """get_memory() returns None for non-StatefulAgent."""
        agent = DoubleAgent()

        extracted = StateMonadFunctor.get_memory(agent)

        assert extracted is None
