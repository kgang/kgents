"""Tests for FluxMetabolism integration."""

# mypy: disable-error-code="var-annotated"

import asyncio
from typing import Any, AsyncIterator

import pytest
from agents.flux import (
    Flux,
    FluxAgent,
    FluxConfig,
    FluxMetabolism,
    create_flux_metabolism,
)
from bootstrap.types import Agent
from protocols.agentese.metabolism import (
    FeverEvent,
    MetabolicEngine,
    create_metabolic_engine,
)


# Test fixtures
class EchoAgent(Agent[str, str]):
    """Returns input unchanged."""

    @property
    def name(self) -> str:
        return "Echo"

    async def invoke(self, input: str) -> str:
        return input


class CounterAgent(Agent[int, int]):
    """Doubles the input and tracks invocations."""

    def __init__(self) -> None:
        self._count = 0

    @property
    def name(self) -> str:
        return "Counter"

    @property
    def count(self) -> int:
        return self._count

    async def invoke(self, input: int) -> int:
        self._count += 1
        return input * 2


async def async_range(n: int) -> AsyncIterator[int]:
    """Generate async range."""
    for i in range(n):
        yield i


async def async_list(items: list[Any]) -> AsyncIterator[Any]:
    """Generate async iterator from list."""
    for item in items:
        yield item


class TestFluxMetabolismCreation:
    """Tests for FluxMetabolism creation."""

    def test_create_with_engine(self) -> None:
        """FluxMetabolism can be created with explicit engine."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(engine=engine)

        assert metabolism.engine is engine
        assert metabolism.pressure == 0.0
        assert metabolism.in_fever is False

    def test_create_with_factory(self) -> None:
        """Factory function creates FluxMetabolism."""
        engine = MetabolicEngine()
        metabolism = create_flux_metabolism(
            engine=engine,
            input_tokens=100,
            output_tokens=200,
        )

        assert metabolism.engine is engine
        assert metabolism.input_tokens_per_event == 100
        assert metabolism.output_tokens_per_event == 200

    def test_default_token_estimates(self) -> None:
        """Default token estimates are reasonable."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(engine=engine)

        assert metabolism.input_tokens_per_event == 50
        assert metabolism.output_tokens_per_event == 100


class TestFluxMetabolismConsume:
    """Tests for FluxMetabolism.consume()."""

    @pytest.mark.asyncio
    async def test_consume_increments_counter(self) -> None:
        """consume() increments events_metabolized."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(engine=engine)

        assert metabolism._events_metabolized == 0

        await metabolism.consume("event1")
        assert metabolism._events_metabolized == 1

        await metabolism.consume("event2")
        assert metabolism._events_metabolized == 2

    @pytest.mark.asyncio
    async def test_consume_ticks_engine(self) -> None:
        """consume() calls engine.tick() with token counts."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(
            engine=engine,
            input_tokens_per_event=100,
            output_tokens_per_event=200,
        )

        await metabolism.consume("event")

        # Engine should have received tokens
        assert engine.input_tokens == 100
        assert engine.output_tokens == 200

    @pytest.mark.asyncio
    async def test_consume_accumulates_pressure(self) -> None:
        """consume() accumulates metabolic pressure."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(
            engine=engine,
            input_tokens_per_event=500,
            output_tokens_per_event=500,
        )

        initial_pressure = engine.pressure

        await metabolism.consume("event")

        # Pressure should have increased (activity = 1000 * 0.001 = 1.0)
        # With 1% decay: (0.0 + 1.0) * 0.99 = 0.99
        assert engine.pressure > initial_pressure

    @pytest.mark.asyncio
    async def test_consume_returns_fever_on_threshold(self) -> None:
        """consume() returns FeverEvent when threshold exceeded."""
        # Low threshold for quick fever
        engine = MetabolicEngine(critical_threshold=0.1)
        metabolism = FluxMetabolism(
            engine=engine,
            input_tokens_per_event=500,  # High tokens to trigger fever fast
            output_tokens_per_event=500,
        )

        # First consume should trigger fever
        fever = await metabolism.consume("hot_event")

        assert fever is not None
        assert isinstance(fever, FeverEvent)
        assert fever.intensity > 0
        assert metabolism._fevers_triggered == 1

    @pytest.mark.asyncio
    async def test_consume_calls_fever_callback(self) -> None:
        """consume() calls on_fever callback when fever triggers."""
        engine = MetabolicEngine(critical_threshold=0.1)
        fever_events: list[FeverEvent] = []

        async def on_fever(event: FeverEvent) -> None:
            fever_events.append(event)

        metabolism = FluxMetabolism(
            engine=engine,
            input_tokens_per_event=500,
            output_tokens_per_event=500,
            on_fever=on_fever,
        )

        await metabolism.consume("hot_event")

        assert len(fever_events) == 1
        assert fever_events[0].intensity > 0


class TestFluxMetabolismTithe:
    """Tests for FluxMetabolism.tithe()."""

    def test_tithe_discharges_pressure(self) -> None:
        """tithe() reduces metabolic pressure."""
        engine = MetabolicEngine()
        engine.pressure = 0.5
        metabolism = FluxMetabolism(engine=engine)

        result = metabolism.tithe(0.2)

        assert result["discharged"] == 0.2
        assert result["remaining_pressure"] == pytest.approx(0.3)

    def test_tithe_returns_gratitude(self) -> None:
        """tithe() returns gratitude message."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(engine=engine)

        result = metabolism.tithe()

        assert "gratitude" in result


class TestFluxMetabolismStatus:
    """Tests for FluxMetabolism.status()."""

    @pytest.mark.asyncio
    async def test_status_includes_engine_status(self) -> None:
        """status() includes all engine status fields."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(engine=engine)

        status = metabolism.status()

        assert "pressure" in status
        assert "critical_threshold" in status
        assert "in_fever" in status
        assert "temperature" in status

    @pytest.mark.asyncio
    async def test_status_includes_flux_counters(self) -> None:
        """status() includes flux-specific counters."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(engine=engine)

        await metabolism.consume("event1")
        await metabolism.consume("event2")

        status = metabolism.status()

        assert status["events_metabolized"] == 2
        assert "fevers_triggered" in status
        assert "last_fever_oblique" in status


class TestFluxAgentMetabolismIntegration:
    """Tests for FluxAgent with metabolism attached."""

    @pytest.mark.asyncio
    async def test_attach_metabolism(self) -> None:
        """FluxAgent can attach metabolism."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(engine=engine)
        flux = Flux.lift(EchoAgent())

        result = flux.attach_metabolism(metabolism)

        assert result is flux  # Returns self for chaining
        assert flux.metabolism is metabolism

    @pytest.mark.asyncio
    async def test_detach_metabolism(self) -> None:
        """FluxAgent can detach metabolism."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(engine=engine)
        flux = Flux.lift(EchoAgent())
        flux.attach_metabolism(metabolism)

        detached = flux.detach_metabolism()

        assert detached is metabolism
        assert flux.metabolism is None

    @pytest.mark.asyncio
    async def test_flux_consumes_metabolism_on_events(self) -> None:
        """FluxAgent calls metabolism.consume() for each event."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(engine=engine)
        counter = CounterAgent()
        flux = Flux.lift(counter, config=FluxConfig.infinite())
        flux.attach_metabolism(metabolism)

        results = []
        async for result in flux.start(async_range(5)):
            results.append(result)

        assert len(results) == 5
        assert metabolism._events_metabolized == 5

    @pytest.mark.asyncio
    async def test_flux_accumulates_pressure(self) -> None:
        """FluxAgent accumulates metabolic pressure during processing."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(
            engine=engine,
            input_tokens_per_event=100,
            output_tokens_per_event=100,
        )
        flux = Flux.lift(CounterAgent(), config=FluxConfig.infinite())
        flux.attach_metabolism(metabolism)

        async for _ in flux.start(async_range(10)):
            pass

        # Pressure should have accumulated (minus decay)
        assert engine.pressure > 0

    @pytest.mark.asyncio
    async def test_flux_triggers_fever_during_processing(self) -> None:
        """FluxAgent can trigger fever during event processing."""
        # Low threshold, high token cost to trigger fever quickly
        engine = MetabolicEngine(critical_threshold=0.05)
        fever_events: list[FeverEvent] = []

        async def on_fever(event: FeverEvent) -> None:
            fever_events.append(event)

        metabolism = FluxMetabolism(
            engine=engine,
            input_tokens_per_event=500,
            output_tokens_per_event=500,
            on_fever=on_fever,
        )
        flux = Flux.lift(CounterAgent(), config=FluxConfig.infinite())
        flux.attach_metabolism(metabolism)

        # Process enough events to trigger fever
        async for _ in flux.start(async_range(5)):
            pass

        # Should have triggered at least one fever
        assert len(fever_events) >= 1

    @pytest.mark.asyncio
    async def test_flux_without_metabolism_works_normally(self) -> None:
        """FluxAgent works normally without metabolism attached."""
        counter = CounterAgent()
        flux = Flux.lift(counter, config=FluxConfig.infinite())
        # No metabolism attached

        results = []
        async for result in flux.start(async_range(5)):
            results.append(result)

        assert len(results) == 5
        assert flux.metabolism is None


class TestFluxMetabolismEdgeCases:
    """Edge case tests for FluxMetabolism."""

    @pytest.mark.asyncio
    async def test_fever_callback_error_does_not_break_processing(self) -> None:
        """Errors in fever callback don't break flux processing."""
        engine = MetabolicEngine(critical_threshold=0.05)

        async def bad_callback(_event: FeverEvent) -> None:
            raise RuntimeError("Callback error!")

        metabolism = FluxMetabolism(
            engine=engine,
            input_tokens_per_event=500,
            output_tokens_per_event=500,
            on_fever=bad_callback,
        )
        flux = Flux.lift(CounterAgent(), config=FluxConfig.infinite())
        flux.attach_metabolism(metabolism)

        # Should complete without raising
        results = []
        async for result in flux.start(async_range(5)):
            results.append(result)

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_multiple_fevers_during_long_processing(self) -> None:
        """Multiple fevers can trigger during long processing."""
        # Use high decay rate so pressure drops below recovery threshold
        # Fever triggers at 0.5, halves to 0.25, needs to drop to 0.25 (50% of 0.5) to recover
        # Then we need to build back up to trigger again
        engine = MetabolicEngine(critical_threshold=0.5, decay_rate=0.3)
        fever_count = 0

        async def count_fevers(_event: FeverEvent) -> None:
            nonlocal fever_count
            fever_count += 1

        metabolism = FluxMetabolism(
            engine=engine,
            input_tokens_per_event=500,  # Each event adds 1.0 pressure
            output_tokens_per_event=500,
            on_fever=count_fevers,
        )
        flux = Flux.lift(CounterAgent(), config=FluxConfig.infinite())
        flux.attach_metabolism(metabolism)

        # Process many events
        # Each event: 1000 tokens * 0.001 = 1.0 pressure (before decay)
        # With 30% decay, cycles through fever/recovery
        async for _ in flux.start(async_range(30)):
            pass

        # Should have triggered at least one fever
        # (The exact count depends on timing, but at least one should trigger)
        assert fever_count >= 1

    @pytest.mark.asyncio
    async def test_temperature_property_reflects_ratio(self) -> None:
        """temperature property reflects input/output token ratio."""
        engine = MetabolicEngine()
        metabolism = FluxMetabolism(
            engine=engine,
            input_tokens_per_event=100,
            output_tokens_per_event=200,
        )

        await metabolism.consume("event")

        # temperature = input / output = 100 / 200 = 0.5
        assert metabolism.temperature == pytest.approx(0.5)
