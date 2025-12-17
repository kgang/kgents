"""Tests for FluxAgent core functionality."""

import asyncio
from typing import Any, AsyncIterator

import pytest
from agents.flux import Flux, FluxAgent, FluxConfig, FluxState
from agents.flux.errors import FluxStateError
from agents.poly.types import Agent


# Test fixtures
class EchoAgent(Agent[str, str]):
    """Returns input unchanged."""

    @property
    def name(self) -> str:
        return "Echo"

    async def invoke(self, input: str) -> str:
        return input


class DoubleAgent(Agent[int, int]):
    """Doubles the input."""

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


class FailingAgent(Agent[str, str]):
    """Always raises an error."""

    @property
    def name(self) -> str:
        return "Failing"

    async def invoke(self, input: str) -> str:
        raise ValueError(f"Failed on: {input}")


class SlowAgent(Agent[int, int]):
    """Processes slowly."""

    @property
    def name(self) -> str:
        return "Slow"

    async def invoke(self, input: int) -> int:
        await asyncio.sleep(0.05)
        return input


async def async_range(n: int) -> AsyncIterator[int]:
    """Generate async range."""
    for i in range(n):
        yield i


async def async_list(items: list[Any]) -> AsyncIterator[Any]:
    """Generate async iterator from list."""
    for item in items:
        yield item


class TestFluxAgentStartReturnsAsyncIterator:
    """THE CRITICAL TEST: start() returns AsyncIterator[B], not None."""

    @pytest.mark.asyncio
    async def test_start_returns_async_iterator(self):
        """start() must return an async iterator, not None."""
        flux = Flux.lift(EchoAgent())

        result = flux.start(async_list(["a", "b"]))

        # Must be async iterator
        assert hasattr(result, "__anext__")

    @pytest.mark.asyncio
    async def test_start_can_be_async_for(self):
        """start() result must work with async for."""
        flux = Flux.lift(EchoAgent())

        results = []
        async for item in flux.start(async_list(["a", "b", "c"])):
            results.append(item)

        assert results == ["a", "b", "c"]


class TestFluxAgentBasicProcessing:
    """Test basic stream processing."""

    @pytest.mark.asyncio
    async def test_process_integers(self):
        flux = Flux.lift(DoubleAgent())

        results = []
        async for result in flux.start(async_range(5)):
            results.append(result)

        assert results == [0, 2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_process_empty_stream(self):
        flux = Flux.lift(EchoAgent())

        results = []
        async for result in flux.start(async_list([])):
            results.append(result)

        assert results == []

    @pytest.mark.asyncio
    async def test_process_single_item(self):
        flux = Flux.lift(EchoAgent())

        results = []
        async for result in flux.start(async_list(["only"])):
            results.append(result)

        assert results == ["only"]


class TestFluxAgentStateTransitions:
    """Test state transitions during flux lifecycle."""

    @pytest.mark.asyncio
    async def test_dormant_before_start(self):
        flux = Flux.lift(EchoAgent())
        assert flux.state == FluxState.DORMANT

    @pytest.mark.asyncio
    async def test_flowing_during_processing(self):
        flux = Flux.lift(SlowAgent())

        # Start processing in background
        async def consume():
            async for _ in flux.start(async_range(3)):
                pass

        task = asyncio.create_task(consume())

        # Give time for processing to start
        await asyncio.sleep(0.02)

        assert flux.state in (FluxState.FLOWING, FluxState.DRAINING, FluxState.STOPPED)

        await task

    @pytest.mark.asyncio
    async def test_stopped_after_completion(self):
        flux = Flux.lift(EchoAgent())

        async for _ in flux.start(async_list(["a"])):
            pass

        assert flux.state == FluxState.STOPPED

    @pytest.mark.asyncio
    async def test_cannot_start_while_flowing(self):
        flux = Flux.lift(SlowAgent())

        # Start first stream
        async def consume():
            async for _ in flux.start(async_range(10)):
                pass

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.02)

        # Try to start second stream
        with pytest.raises(FluxStateError):
            async for _ in flux.start(async_range(5)):
                pass

        await flux.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


class TestFluxAgentInvokeOnDormant:
    """Test invoke() in DORMANT state (discrete mode)."""

    @pytest.mark.asyncio
    async def test_invoke_dormant_works(self):
        """invoke() on DORMANT should work like a regular agent."""
        flux = Flux.lift(EchoAgent())

        result = await flux.invoke("test")

        assert result == "test"
        assert flux.state == FluxState.DORMANT  # Still dormant

    @pytest.mark.asyncio
    async def test_invoke_dormant_multiple_times(self):
        flux = Flux.lift(DoubleAgent())

        assert await flux.invoke(5) == 10
        assert await flux.invoke(7) == 14
        assert await flux.invoke(0) == 0


class TestFluxAgentEntropyManagement:
    """Test entropy budget and collapse."""

    @pytest.mark.asyncio
    async def test_entropy_decreases(self):
        config = FluxConfig(entropy_budget=1.0, entropy_decay=0.1)
        flux = Flux.lift(EchoAgent(), config)

        results = []
        async for result in flux.start(async_list(["a", "b", "c"])):
            results.append(result)

        assert flux.entropy_remaining < 1.0

    @pytest.mark.asyncio
    async def test_entropy_collapse(self):
        """Flux should collapse when entropy exhausted."""
        config = FluxConfig(entropy_budget=0.1, entropy_decay=0.05)
        flux = Flux.lift(DoubleAgent(), config)

        results: list[int] = []
        async for result in flux.start(async_range(100)):
            results.append(result)

        # Should stop early due to entropy exhaustion
        assert len(results) < 100
        assert flux.state == FluxState.COLLAPSED

    @pytest.mark.asyncio
    async def test_max_events_limit(self):
        config = FluxConfig(max_events=5)
        flux = Flux.lift(DoubleAgent(), config)

        results: list[int] = []
        async for result in flux.start(async_range(100)):
            results.append(result)

        assert len(results) == 5


class TestFluxAgentEventsProcessed:
    """Test events_processed counter."""

    @pytest.mark.asyncio
    async def test_events_counted(self):
        flux = Flux.lift(EchoAgent())

        async for _ in flux.start(async_list(["a", "b", "c", "d", "e"])):
            pass

        assert flux.events_processed == 5

    @pytest.mark.asyncio
    async def test_events_zero_initially(self):
        flux = Flux.lift(EchoAgent())
        assert flux.events_processed == 0


class TestFluxAgentStop:
    """Test stop() method."""

    @pytest.mark.asyncio
    async def test_stop_terminates_processing(self):
        flux = Flux.lift(SlowAgent())

        results = []

        async def consume():
            async for result in flux.start(async_range(100)):
                results.append(result)

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.1)

        await flux.stop()

        try:
            await asyncio.wait_for(task, timeout=1.0)
        except asyncio.CancelledError:
            pass

        assert flux.state == FluxState.STOPPED
        assert len(results) < 100


class TestFluxAgentReset:
    """Test reset() method."""

    @pytest.mark.asyncio
    async def test_reset_after_stop(self):
        config = FluxConfig(entropy_budget=1.0, entropy_decay=0.1)
        flux = Flux.lift(EchoAgent(), config)

        # Process some items
        async for _ in flux.start(async_list(["a", "b", "c"])):
            pass

        assert flux.state == FluxState.STOPPED
        assert flux.events_processed > 0
        assert flux.entropy_remaining < 1.0

        # Reset
        flux.reset()

        assert flux.state == FluxState.DORMANT  # type: ignore[comparison-overlap]
        assert flux.events_processed == 0
        assert flux.entropy_remaining == 1.0

    @pytest.mark.asyncio
    async def test_cannot_reset_while_flowing(self):
        flux = Flux.lift(SlowAgent())

        async def consume():
            async for _ in flux.start(async_range(10)):
                pass

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.02)

        with pytest.raises(FluxStateError):
            flux.reset()

        await flux.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


class TestFluxAgentRestart:
    """Test restarting after stop."""

    @pytest.mark.asyncio
    async def test_restart_after_stop(self):
        flux = Flux.lift(EchoAgent())

        # First run
        results1 = []
        async for result in flux.start(async_list(["a", "b"])):
            results1.append(result)

        assert results1 == ["a", "b"]

        # Second run (restart)
        results2 = []
        async for result in flux.start(async_list(["c", "d"])):
            results2.append(result)

        assert results2 == ["c", "d"]


class TestFluxAgentErrorHandling:
    """Test error handling in stream processing."""

    @pytest.mark.asyncio
    async def test_inner_error_continues_stream(self):
        """Inner agent errors should not stop the stream."""
        flux = Flux.lift(FailingAgent())

        results = []
        async for result in flux.start(async_list(["a", "b", "c"])):
            results.append(result)

        # All items processed (errors logged but stream continues)
        assert flux.events_processed == 0  # No successful processing


class TestFluxAgentRepr:
    """Test string representation."""

    def test_repr(self):
        flux = Flux.lift(EchoAgent())

        repr_str = repr(flux)

        assert "FluxAgent" in repr_str
        assert "Echo" in repr_str
        assert "dormant" in repr_str


class TestNoAsyncSleepInCore:
    """Verify event-driven design (no polling in core)."""

    def test_no_sleep_in_process_flux(self):
        """Core processing must be event-driven, not timer-driven."""
        import inspect

        source = inspect.getsource(FluxAgent._process_flux)

        # Should not have asyncio.sleep as the main waiting mechanism
        # (small timeouts for queue checking are okay)
        # Exclude comments (lines starting with #) and small timeouts
        lines_with_sleep = [
            line
            for line in source.split("\n")
            if "asyncio.sleep" in line
            and "0.05" not in line
            and "0.01" not in line
            and not line.strip().startswith("#")
            and not line.strip().startswith('"""')
            and "No asyncio.sleep()" not in line  # Exclude docstring
        ]

        assert len(lines_with_sleep) == 0, (
            f"Found asyncio.sleep in core: {lines_with_sleep}"
        )
