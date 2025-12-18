"""
Tests for FluxFunctor UniversalFunctor compliance (Alethic Algebra Phase 3).

Verifies that FluxFunctor satisfies the functor laws:
1. Identity: F(id) = id in F's category
2. Composition: F(g . f) = F(g) . F(f)

Note: FluxFunctor operates on streams (AsyncIterator), so law verification
requires collecting stream outputs. The laws hold element-wise across streams.
"""

from typing import Any, AsyncIterator, TypeVar

import pytest

from agents.a.functor import FunctorRegistry
from agents.flux import Flux, FluxAgent, FluxFunctor
from agents.poly.types import Agent

T = TypeVar("T")


# =============================================================================
# Test Fixtures: Stream Helpers
# =============================================================================


async def from_iterable(items: list[T]) -> AsyncIterator[T]:
    """Create an async iterator from a list."""
    for item in items:
        yield item


async def collect_stream(flux_agent: FluxAgent[T, T], source: list[T]) -> list[T]:
    """Run a flux agent on a source and collect all outputs."""
    results = []
    async for result in flux_agent.start(from_iterable(source)):
        results.append(result)
    return results


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


# =============================================================================
# FluxFunctor Law Tests
# =============================================================================


class TestFluxFunctorLaws:
    """Verify FluxFunctor satisfies functor laws."""

    @pytest.mark.asyncio
    async def test_identity_law_single_element(self) -> None:
        """F(id)(stream) processes identity on each element."""
        lifted = FluxFunctor.lift(IdentityAgent())
        results = await collect_stream(lifted, [42])

        assert results == [42]

    @pytest.mark.asyncio
    async def test_identity_law_multiple_elements(self) -> None:
        """F(id)(stream) preserves all elements."""
        lifted = FluxFunctor.lift(IdentityAgent())
        results = await collect_stream(lifted, [1, 2, 3, 4, 5])

        assert results == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_identity_law_empty_stream(self) -> None:
        """F(id)([]) = []."""
        lifted = FluxFunctor.lift(IdentityAgent())
        results = await collect_stream(lifted, [])

        assert results == []

    @pytest.mark.asyncio
    async def test_composition_law(self) -> None:
        """F(g . f) = F(g) . F(f) element-wise on streams."""
        f = DoubleAgent()
        g = AddOneAgent()

        # Left side: F(g . f)
        composed = f >> g
        lifted_composed = FluxFunctor.lift(composed)
        left_results = await collect_stream(lifted_composed, [1, 2, 3])

        # Right side: F(g) . F(f)
        # Note: We need to use sequential processing here
        # First lift f, then pipe to lifted g
        lifted_f = FluxFunctor.lift(f)
        lifted_g = FluxFunctor.lift(g)

        # For FluxAgents, we can use the pipe operator
        # But for law verification, we test equivalent behavior
        # by composing the inner agents then lifting

        # Alternative: compose lifted agents via >>
        lifted_composition = lifted_f >> lifted_g
        right_results = await collect_stream(lifted_composition, [1, 2, 3])

        # Both should give [1*2+1, 2*2+1, 3*2+1] = [3, 5, 7]
        assert left_results == [3, 5, 7]
        assert right_results == [3, 5, 7]
        assert left_results == right_results

    @pytest.mark.asyncio
    async def test_composition_law_empty(self) -> None:
        """Composition law holds for empty streams."""
        f = DoubleAgent()
        g = AddOneAgent()

        # Left side: F(g . f)
        composed = f >> g
        lifted_composed = FluxFunctor.lift(composed)
        left_results = await collect_stream(lifted_composed, [])

        # Right side: F(g) . F(f)
        lifted_f = FluxFunctor.lift(f)
        lifted_g = FluxFunctor.lift(g)
        lifted_composition = lifted_f >> lifted_g
        right_results = await collect_stream(lifted_composition, [])

        assert left_results == []
        assert right_results == []


# =============================================================================
# FluxFunctor Pure Tests
# =============================================================================


class TestFluxFunctorPure:
    """Test FluxFunctor.pure() - embedding values in stream context."""

    @pytest.mark.asyncio
    async def test_pure_creates_single_element_stream(self) -> None:
        """pure(x) yields exactly one value."""
        stream = FluxFunctor.pure(42)

        results = []
        async for item in stream:
            results.append(item)

        assert results == [42]

    @pytest.mark.asyncio
    async def test_pure_with_different_types(self) -> None:
        """pure() works with various types."""
        # String
        stream_str: AsyncIterator[str] = FluxFunctor.pure("hello")
        results_str = [item async for item in stream_str]
        assert results_str == ["hello"]

        # List
        stream_list: AsyncIterator[list[int]] = FluxFunctor.pure([1, 2, 3])
        results_list = [item async for item in stream_list]
        assert results_list == [[1, 2, 3]]

        # Dict
        stream_dict: AsyncIterator[dict[str, str]] = FluxFunctor.pure({"key": "value"})
        results_dict = [item async for item in stream_dict]
        assert results_dict == [{"key": "value"}]


# =============================================================================
# FluxFunctor Lift Tests
# =============================================================================


class TestFluxFunctorLift:
    """Test FluxFunctor.lift() behavior."""

    def test_lift_returns_flux_agent(self) -> None:
        """lift() returns a FluxAgent."""
        agent = DoubleAgent()
        lifted = FluxFunctor.lift(agent)

        assert isinstance(lifted, FluxAgent)

    def test_lift_same_as_flux_lift(self) -> None:
        """FluxFunctor.lift() delegates to Flux.lift()."""
        agent = DoubleAgent()

        flux_lifted = Flux.lift(agent)
        functor_lifted = FluxFunctor.lift(agent)

        # Both should create FluxAgents wrapping the same inner
        assert isinstance(functor_lifted, FluxAgent)
        assert functor_lifted.inner is agent
        assert type(flux_lifted) is type(functor_lifted)

    @pytest.mark.asyncio
    async def test_lift_preserves_agent_behavior(self) -> None:
        """Lifted agent processes values through inner agent."""
        lifted = FluxFunctor.lift(DoubleAgent())
        results = await collect_stream(lifted, [1, 2, 3])

        assert results == [2, 4, 6]


# =============================================================================
# Registry Tests
# =============================================================================


class TestFluxFunctorRegistration:
    """Verify FluxFunctor is properly registered."""

    def test_flux_functor_registered(self) -> None:
        """FluxFunctor is in the registry."""
        functor = FunctorRegistry.get("Flux")

        assert functor is not None
        assert functor.__name__ == "FluxFunctor"

    def test_flux_functor_in_all_functors(self) -> None:
        """FluxFunctor appears in all_functors()."""
        all_functors = FunctorRegistry.all_functors()

        assert "Flux" in all_functors
        # Use name comparison - identity can fail due to pytest import isolation
        assert all_functors["Flux"].__name__ == FluxFunctor.__name__


# =============================================================================
# Backward Compatibility Tests
# =============================================================================


class TestBackwardCompatibility:
    """Verify existing Flux usage still works."""

    def test_flux_class_still_works(self) -> None:
        """Flux.lift() still works (not affected by FluxFunctor)."""
        agent = DoubleAgent()
        flux_agent = Flux.lift(agent)

        assert isinstance(flux_agent, FluxAgent)
        assert flux_agent.inner is agent

    @pytest.mark.asyncio
    async def test_flux_agent_start_still_works(self) -> None:
        """FluxAgent.start() returns async iterator as expected."""
        flux_agent = Flux.lift(DoubleAgent())

        results = []
        async for result in flux_agent.start(from_iterable([1, 2, 3])):
            results.append(result)

        assert results == [2, 4, 6]
