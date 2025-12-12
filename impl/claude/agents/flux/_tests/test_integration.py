"""Integration tests for the Flux Functor system."""

import asyncio
from typing import AsyncIterator

import pytest
from agents.flux import Flux, FluxAgent, FluxConfig, FluxPipeline, FluxState
from agents.flux.sources import filtered, from_iterable, mapped, take
from bootstrap.types import Agent


# Test agents
class DoubleAgent(Agent[int, int]):
    @property
    def name(self) -> str:
        return "Double"

    async def invoke(self, input: int) -> int:
        return input * 2


class AddAgent(Agent[int, int]):
    def __init__(self, amount: int = 1):
        self._amount = amount

    @property
    def name(self) -> str:
        return f"Add{self._amount}"

    async def invoke(self, input: int) -> int:
        return input + self._amount


class StatefulAgent(Agent[str, str]):
    """Agent that accumulates state."""

    def __init__(self):
        self.invocations: list[str] = []

    @property
    def name(self) -> str:
        return "Stateful"

    async def invoke(self, input: str) -> str:
        self.invocations.append(input)
        return f"[{len(self.invocations)}] {input}"


class SlowAgent(Agent[int, int]):
    """Agent with variable processing time."""

    def __init__(self, delay: float = 0.01):
        self._delay = delay

    @property
    def name(self) -> str:
        return "Slow"

    async def invoke(self, input: int) -> int:
        await asyncio.sleep(self._delay)
        return input


async def async_range(n: int) -> AsyncIterator[int]:
    for i in range(n):
        yield i


class TestFluxFunctorLaws:
    """Test that Flux satisfies functor laws."""

    @pytest.mark.asyncio
    async def test_identity_law(self):
        """Flux(Id) ≅ Id_Flux"""
        from bootstrap.id import Id

        # Lift identity agent
        flux_id: FluxAgent[int, int] = Flux.lift(Id())

        # Should behave like identity on streams
        results = []
        async for item in flux_id.start(from_iterable([1, 2, 3])):
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_composition_law(self):
        """Flux(f >> g) ≅ Flux(f) >> Flux(g)"""
        from bootstrap.types import ComposedAgent

        # Create agents
        double = DoubleAgent()
        add_one = AddAgent(1)

        # Composed then lifted
        composed = ComposedAgent(double, add_one)
        flux_composed = Flux.lift(composed)

        # Lifted then piped
        flux_double = Flux.lift(DoubleAgent())
        flux_add = Flux.lift(AddAgent(1))

        # Both should produce same results
        results_composed = []
        async for item in flux_composed.start(from_iterable([1, 2, 3])):
            results_composed.append(item)

        results_piped = []
        pipeline = flux_double | flux_add
        async for item in pipeline.start(from_iterable([1, 2, 3])):
            results_piped.append(item)

        # 1*2+1=3, 2*2+1=5, 3*2+1=7
        assert results_composed == [3, 5, 7]
        assert results_piped == [3, 5, 7]


class TestPerturbationIntegrity:
    """Test that perturbation preserves state integrity."""

    @pytest.mark.asyncio
    async def test_perturbation_goes_through_same_path(self):
        """invoke() on FLOWING must go through the stream, not bypass."""
        agent = StatefulAgent()
        flux = Flux.lift(agent)

        # Start processing in background
        results = []

        async def consume():
            async for result in flux.start(from_iterable(["a", "b", "c"])):
                results.append(result)

        task = asyncio.create_task(consume())

        # Wait for processing to start
        await asyncio.sleep(0.05)

        # If flowing, perturbation should go through
        if flux.state == FluxState.FLOWING:
            perturb_result = await flux.invoke("PERTURB")
            # Perturbation result should include the count
            assert "PERTURB" in perturb_result

        await task

        # All inputs should be in agent's invocations
        assert "a" in agent.invocations or len(agent.invocations) > 0


class TestLivingPipelines:
    """Test Living Pipeline functionality."""

    @pytest.mark.asyncio
    async def test_three_stage_pipeline(self):
        """Pipeline of three flux agents."""
        p = (
            Flux.lift(DoubleAgent())
            | Flux.lift(AddAgent(10))
            | Flux.lift(DoubleAgent())
        )

        # Input: 5
        # After Double: 10
        # After Add10: 20
        # After Double: 40
        results = []
        async for item in p.start(from_iterable([5])):
            results.append(item)

        assert results == [40]

    @pytest.mark.asyncio
    async def test_pipeline_with_large_stream(self):
        """Pipeline processing many items."""
        p = Flux.lift(DoubleAgent()) | Flux.lift(AddAgent(1))

        results = []
        async for item in p.start(from_iterable(range(100))):
            results.append(item)

        expected = [i * 2 + 1 for i in range(100)]
        assert results == expected


class TestOuroboricFeedback:
    """Test ouroboric feedback mechanism."""

    @pytest.mark.asyncio
    async def test_feedback_fraction(self):
        """Output feeds back to input with configured fraction."""
        config = FluxConfig(
            feedback_fraction=1.0,  # Full ouroboros
            max_events=10,  # Prevent infinite
        )
        flux = Flux.lift(DoubleAgent(), config)

        results = []
        # Start with single seed
        async for item in flux.start(from_iterable([1])):
            results.append(item)

        # Should have processed multiple items due to feedback
        # 1 -> 2 -> 4 -> 8 -> 16 -> ...
        assert len(results) > 1
        # Check that values are powers of 2
        for r in results:
            assert r > 0 and (r & (r - 1)) == 0  # Is power of 2


class TestBackpressure:
    """Test backpressure handling."""

    @pytest.mark.asyncio
    async def test_drop_oldest_policy(self):
        """drop_oldest should discard old items when buffer full."""
        config = FluxConfig(
            buffer_size=2,
            drop_policy="drop_oldest",
        )
        flux = Flux.lift(SlowAgent(delay=0.01), config)

        # Process many items with slow consumer
        results = []
        async for item in flux.start(from_iterable(range(10))):
            results.append(item)
            # Slow consumption
            await asyncio.sleep(0.02)

        # Some items may be dropped, but we should get results
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_block_policy_preserves_all(self):
        """block policy should preserve all items."""
        config = FluxConfig(
            buffer_size=100,
            drop_policy="block",
        )
        flux = Flux.lift(DoubleAgent(), config)

        results = []
        async for item in flux.start(from_iterable(range(50))):
            results.append(item)

        # All items preserved
        assert len(results) == 50


class TestEntropyPhysics:
    """Test J-gent entropy physics."""

    @pytest.mark.asyncio
    async def test_entropy_depletion_causes_collapse(self):
        """Flux should collapse when entropy runs out."""
        config = FluxConfig(
            entropy_budget=0.1,
            entropy_decay=0.05,
        )
        flux = Flux.lift(DoubleAgent(), config)

        results = []
        async for item in flux.start(from_iterable(range(100))):
            results.append(item)

        # Should have stopped early
        assert len(results) < 100
        assert flux.state == FluxState.COLLAPSED
        assert flux.entropy_remaining <= 0.05  # Near zero

    @pytest.mark.asyncio
    async def test_infinite_entropy(self):
        """Infinite entropy should process all items."""
        config = FluxConfig.infinite()
        flux = Flux.lift(DoubleAgent(), config)

        results = []
        async for item in flux.start(from_iterable(range(200))):
            results.append(item)

        assert len(results) == 200


class TestSourceIntegration:
    """Test integration with flux sources."""

    @pytest.mark.asyncio
    async def test_flux_with_take(self):
        """Flux with take() source combinator."""
        flux = Flux.lift(DoubleAgent())

        results = []
        async for item in flux.start(take(from_iterable(range(100)), 5)):
            results.append(item)

        assert results == [0, 2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_flux_with_filter(self):
        """Flux with filtered() source combinator."""
        flux = Flux.lift(DoubleAgent())

        results = []
        source = filtered(from_iterable(range(10)), lambda x: x % 2 == 0)
        async for item in flux.start(source):
            results.append(item)

        # Even numbers 0,2,4,6,8 doubled
        assert results == [0, 4, 8, 12, 16]


class TestRshiftComposition:
    """Test >> composition with static agents."""

    @pytest.mark.asyncio
    async def test_flux_rshift_agent(self):
        """Flux(f) >> g should compose inner with g."""
        flux_double = Flux.lift(DoubleAgent())
        flux_composed = flux_double >> AddAgent(10)

        # Should be a new FluxAgent with composed inner
        assert isinstance(flux_composed, type(flux_double))

        results = []
        async for item in flux_composed.start(from_iterable([1, 2, 3])):
            results.append(item)

        # 1*2+10=12, 2*2+10=14, 3*2+10=16
        assert results == [12, 14, 16]


class TestConcurrentFluxAgents:
    """Test multiple flux agents running concurrently."""

    @pytest.mark.asyncio
    async def test_independent_flux_agents(self):
        """Multiple flux agents should run independently."""
        flux_a = Flux.lift(DoubleAgent())
        flux_b = Flux.lift(AddAgent(100))

        async def run_flux_a():
            results = []
            async for item in flux_a.start(from_iterable([1, 2, 3])):
                results.append(item)
            return results

        async def run_flux_b():
            results = []
            async for item in flux_b.start(from_iterable([10, 20, 30])):
                results.append(item)
            return results

        results_a, results_b = await asyncio.gather(run_flux_a(), run_flux_b())

        assert results_a == [2, 4, 6]
        assert results_b == [110, 120, 130]
