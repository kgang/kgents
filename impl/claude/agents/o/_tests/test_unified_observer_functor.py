"""
Tests for the Unified Observer Functor (Phase 2: Observer Unification).

Verifies:
1. ObservationSink protocol works with any sink
2. ObservedAgent preserves agent behavior
3. Functor laws hold (identity, composition)
4. Symmetric lifting: unlift(lift(agent)) ≅ agent
5. Sink adapters work correctly
"""

import pytest

from agents.o.observer_functor import (
    ListSink,
    ObservationEvent,
    ObservationSink,
    ObservedAgent,
    UnifiedObserverFunctor,
    observe,
    unobserve,
)
from agents.poly.types import Agent

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


class FailingAgent(Agent[int, int]):
    """Agent that always fails."""

    @property
    def name(self) -> str:
        return "Failing"

    async def invoke(self, input: int) -> int:
        raise ValueError(f"Intentional failure with input {input}")


# =============================================================================
# ObservationSink Protocol Tests
# =============================================================================


class TestObservationSinkProtocol:
    """Test the ObservationSink protocol."""

    def test_list_sink_is_observation_sink(self) -> None:
        """ListSink implements ObservationSink."""
        sink = ListSink()
        assert isinstance(sink, ObservationSink)

    @pytest.mark.asyncio
    async def test_list_sink_records_events(self) -> None:
        """ListSink collects events."""
        sink = ListSink()

        event = ObservationEvent(
            agent_name="Test",
            agent_id="test_123",
            duration_ms=42.0,
            input_data="hello",
            output_data="world",
        )

        await sink.record(event)

        assert len(sink.events) == 1
        assert sink.events[0].agent_name == "Test"
        assert sink.events[0].duration_ms == 42.0

    @pytest.mark.asyncio
    async def test_list_sink_clear(self) -> None:
        """ListSink can be cleared."""
        sink = ListSink()

        await sink.record(ObservationEvent(agent_name="Test", agent_id="t1"))
        await sink.record(ObservationEvent(agent_name="Test", agent_id="t2"))

        assert len(sink.events) == 2
        sink.clear()
        assert len(sink.events) == 0


# =============================================================================
# ObservedAgent Tests
# =============================================================================


class TestObservedAgent:
    """Test the ObservedAgent wrapper."""

    @pytest.mark.asyncio
    async def test_preserves_behavior(self) -> None:
        """Observation doesn't change agent behavior."""
        agent = DoubleAgent()
        sink = ListSink()
        observed = ObservedAgent(inner=agent, sink=sink, non_blocking=False)

        result = await observed.invoke(5)

        assert result == 10  # Same as unobserved

    @pytest.mark.asyncio
    async def test_records_to_sink(self) -> None:
        """Observation records events to sink."""
        agent = DoubleAgent()
        sink = ListSink()
        observed = ObservedAgent(inner=agent, sink=sink, non_blocking=False)

        await observed.invoke(5)

        assert len(sink.events) == 1
        event = sink.events[0]
        assert event.agent_name == "Double"
        assert event.input_data == 5
        assert event.output_data == 10
        assert event.success is True
        assert event.error is None

    @pytest.mark.asyncio
    async def test_records_errors(self) -> None:
        """Observation records failures."""
        agent = FailingAgent()
        sink = ListSink()
        observed = ObservedAgent(inner=agent, sink=sink, non_blocking=False)

        with pytest.raises(ValueError):
            await observed.invoke(42)

        assert len(sink.events) == 1
        event = sink.events[0]
        assert event.success is False
        assert event.error is not None
        assert "Intentional failure" in event.error

    @pytest.mark.asyncio
    async def test_has_inner_property(self) -> None:
        """ObservedAgent exposes inner agent."""
        agent = DoubleAgent()
        sink = ListSink()
        observed = ObservedAgent(inner=agent, sink=sink)

        assert observed.inner is agent
        assert observed.name == "Double"

    @pytest.mark.asyncio
    async def test_duration_is_recorded(self) -> None:
        """Observation captures duration."""
        agent = DoubleAgent()
        sink = ListSink()
        observed = ObservedAgent(inner=agent, sink=sink, non_blocking=False)

        await observed.invoke(5)

        event = sink.events[0]
        assert event.duration_ms >= 0.0  # Should have some duration


# =============================================================================
# Functor Law Tests
# =============================================================================


class TestUnifiedObserverFunctorLaws:
    """Verify UnifiedObserverFunctor satisfies functor laws."""

    @pytest.mark.asyncio
    async def test_identity_law(self) -> None:
        """F(id)(x) ≅ id(x) - behavioral equivalence."""
        identity = IdentityAgent()
        sink = ListSink()
        lifted = UnifiedObserverFunctor.lift(identity, sink=sink, non_blocking=False)

        result = await lifted.invoke(42)

        assert result == 42  # Same as unlifted identity

    @pytest.mark.asyncio
    async def test_composition_law(self) -> None:
        """F(g >> f) ≅ F(g) >> F(f) - composition preserved."""
        double = DoubleAgent()
        add_one = AddOneAgent()
        sink = ListSink()

        # Lift then compose
        lifted_double = UnifiedObserverFunctor.lift(double, sink=sink, non_blocking=False)
        lifted_add_one = UnifiedObserverFunctor.lift(add_one, sink=sink, non_blocking=False)

        result_1 = await lifted_double.invoke(5)
        result_2 = await lifted_add_one.invoke(result_1)

        # Should be (5 * 2) + 1 = 11
        assert result_2 == 11

        # Both invocations were recorded
        assert len(sink.events) == 2


# =============================================================================
# Symmetric Lifting Tests
# =============================================================================


class TestSymmetricLifting:
    """Verify round-trip law: unlift(lift(agent)) ≅ agent."""

    @pytest.mark.asyncio
    async def test_roundtrip(self) -> None:
        """unlift(lift(agent)) ≅ agent."""
        original = DoubleAgent()
        sink = ListSink()

        lifted = UnifiedObserverFunctor.lift(original, sink=sink)
        unlifted = UnifiedObserverFunctor.unlift(lifted)

        # Should be the same agent
        assert unlifted is original
        assert unlifted.name == original.name

        # Should behave the same
        assert await unlifted.invoke(5) == await original.invoke(5)

    def test_unlift_wrong_type_raises(self) -> None:
        """unlift() raises TypeError for wrong type."""
        with pytest.raises(TypeError):
            UnifiedObserverFunctor.unlift(DoubleAgent())  # type: ignore[arg-type]


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test observe() and unobserve() helpers."""

    @pytest.mark.asyncio
    async def test_observe_function(self) -> None:
        """observe() creates ObservedAgent."""
        agent = DoubleAgent()
        sink = ListSink()

        observed = observe(agent, sink=sink, non_blocking=False)

        assert isinstance(observed, ObservedAgent)
        result = await observed.invoke(5)
        assert result == 10
        assert len(sink.events) == 1

    @pytest.mark.asyncio
    async def test_unobserve_function(self) -> None:
        """unobserve() extracts inner agent."""
        agent = DoubleAgent()
        sink = ListSink()

        observed = observe(agent, sink=sink)
        unobserved = unobserve(observed)

        assert unobserved is agent


# =============================================================================
# Registry Tests
# =============================================================================


class TestFunctorRegistration:
    """Verify Observer functor is registered."""

    def test_observer_functor_registered(self) -> None:
        """UnifiedObserverFunctor is in the registry."""
        from agents.a.functor import FunctorRegistry

        functor = FunctorRegistry.get("Observer")
        assert functor is not None
        assert functor.__name__ == "UnifiedObserverFunctor"


# =============================================================================
# Pure Tests
# =============================================================================


class TestPure:
    """Test the pure method (identity for endofunctor)."""

    def test_pure_returns_value_unchanged(self) -> None:
        """pure(x) = x for endofunctor."""
        assert UnifiedObserverFunctor.pure(42) == 42
        assert UnifiedObserverFunctor.pure("hello") == "hello"
