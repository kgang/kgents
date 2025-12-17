"""Tests for FluxPipeline (Living Pipelines)."""

import asyncio
from typing import Any, AsyncIterator

import pytest
from agents.flux import Flux, FluxPipeline, pipeline
from agents.flux.errors import FluxPipelineError
from agents.poly.types import Agent


# Test fixtures
class DoubleAgent(Agent[int, int]):
    @property
    def name(self) -> str:
        return "Double"

    async def invoke(self, input: int) -> int:
        return input * 2


class AddOneAgent(Agent[int, int]):
    @property
    def name(self) -> str:
        return "AddOne"

    async def invoke(self, input: int) -> int:
        return input + 1


class SquareAgent(Agent[int, int]):
    @property
    def name(self) -> str:
        return "Square"

    async def invoke(self, input: int) -> int:
        return input * input


class ToStringAgent(Agent[int, str]):
    @property
    def name(self) -> str:
        return "ToString"

    async def invoke(self, input: int) -> str:
        return str(input)


async def async_range(n: int) -> AsyncIterator[int]:
    for i in range(n):
        yield i


async def async_list(items: list[Any]) -> AsyncIterator[Any]:
    for item in items:
        yield item


class TestPipeOperator:
    """Test | operator for creating pipelines."""

    def test_pipe_creates_pipeline(self):
        flux_a = Flux.lift(DoubleAgent())
        flux_b = Flux.lift(AddOneAgent())

        result = flux_a | flux_b

        assert isinstance(result, FluxPipeline)

    def test_pipe_preserves_order(self):
        flux_a = Flux.lift(DoubleAgent())
        flux_b = Flux.lift(AddOneAgent())

        pipeline = flux_a | flux_b

        assert len(pipeline) == 2
        assert pipeline[0] is flux_a
        assert pipeline[1] is flux_b

    def test_pipe_chain(self):
        flux_a = Flux.lift(DoubleAgent())
        flux_b = Flux.lift(AddOneAgent())
        flux_c = Flux.lift(SquareAgent())

        pipeline = flux_a | flux_b | flux_c

        assert len(pipeline) == 3


class TestPipelineFunction:
    """Test pipeline() function."""

    def test_pipeline_single_stage(self):
        flux = Flux.lift(DoubleAgent())
        p = pipeline(flux)

        assert len(p) == 1

    def test_pipeline_multiple_stages(self):
        p = pipeline(
            Flux.lift(DoubleAgent()),
            Flux.lift(AddOneAgent()),
            Flux.lift(SquareAgent()),
        )

        assert len(p) == 3


class TestPipelineExecution:
    """Test pipeline execution (THE LIVING PIPELINE TEST)."""

    @pytest.mark.asyncio
    async def test_pipeline_processes_stream(self):
        """Output of each stage flows to input of next."""
        flux_a = Flux.lift(DoubleAgent())
        flux_b = Flux.lift(AddOneAgent())

        p = flux_a | flux_b

        # Input: 1, 2, 3
        # After double: 2, 4, 6
        # After add one: 3, 5, 7
        results = []
        async for result in p.start(async_list([1, 2, 3])):
            results.append(result)

        assert results == [3, 5, 7]

    @pytest.mark.asyncio
    async def test_three_stage_pipeline(self):
        flux_a = Flux.lift(DoubleAgent())  # x * 2
        flux_b = Flux.lift(AddOneAgent())  # x + 1
        flux_c = Flux.lift(SquareAgent())  # x^2

        p = flux_a | flux_b | flux_c

        # Input: 2
        # After double: 4
        # After add one: 5
        # After square: 25
        results = []
        async for result in p.start(async_list([2])):
            results.append(result)

        assert results == [25]

    @pytest.mark.asyncio
    async def test_pipeline_with_type_change(self):
        flux_a = Flux.lift(DoubleAgent())  # int -> int
        flux_b = Flux.lift(ToStringAgent())  # int -> str

        p = flux_a | flux_b

        results = []
        async for result in p.start(async_list([1, 2, 3])):
            results.append(result)

        assert results == ["2", "4", "6"]
        assert all(isinstance(r, str) for r in results)

    @pytest.mark.asyncio
    async def test_pipeline_empty_stream(self):
        p = pipeline(Flux.lift(DoubleAgent()), Flux.lift(AddOneAgent()))

        results = []
        async for result in p.start(async_list([])):
            results.append(result)

        assert results == []


class TestPipelineName:
    """Test pipeline name generation."""

    def test_pipeline_name(self):
        p = pipeline(Flux.lift(DoubleAgent()), Flux.lift(AddOneAgent()))

        assert "Double" in p.name
        assert "AddOne" in p.name
        assert "Pipeline" in p.name


class TestPipelineProperties:
    """Test pipeline properties."""

    def test_first_stage(self):
        flux_a = Flux.lift(DoubleAgent())
        flux_b = Flux.lift(AddOneAgent())
        p = flux_a | flux_b

        assert p.first is flux_a

    def test_last_stage(self):
        flux_a = Flux.lift(DoubleAgent())
        flux_b = Flux.lift(AddOneAgent())
        p = flux_a | flux_b

        assert p.last is flux_b

    def test_len(self):
        p = pipeline(
            Flux.lift(DoubleAgent()),
            Flux.lift(AddOneAgent()),
            Flux.lift(SquareAgent()),
        )

        assert len(p) == 3

    def test_iter(self):
        stages = [
            Flux.lift(DoubleAgent()),
            Flux.lift(AddOneAgent()),
        ]
        p = pipeline(*stages)

        iterated = list(p)

        assert len(iterated) == 2
        assert iterated[0] is stages[0]
        assert iterated[1] is stages[1]

    def test_getitem(self):
        flux_a = Flux.lift(DoubleAgent())
        flux_b = Flux.lift(AddOneAgent())
        p = flux_a | flux_b

        assert p[0] is flux_a
        assert p[1] is flux_b


class TestPipelineValidation:
    """Test pipeline validation."""

    def test_empty_pipeline_raises(self):
        with pytest.raises(FluxPipelineError):
            FluxPipeline([])


class TestPipelineStop:
    """Test pipeline stop functionality."""

    @pytest.mark.asyncio
    async def test_stop_all_stages(self):
        flux_a = Flux.lift(DoubleAgent())
        flux_b = Flux.lift(AddOneAgent())
        p = flux_a | flux_b

        await p.stop()

        # Both stages should be stopped or dormant
        from agents.flux import FluxState

        assert flux_a.state in (FluxState.STOPPED, FluxState.DORMANT)
        assert flux_b.state in (FluxState.STOPPED, FluxState.DORMANT)


class TestPipelineCombination:
    """Test combining pipelines."""

    def test_pipeline_or_flux(self):
        flux_a = Flux.lift(DoubleAgent())
        flux_b = Flux.lift(AddOneAgent())
        flux_c = Flux.lift(SquareAgent())

        p1 = flux_a | flux_b
        p2 = p1 | flux_c

        assert len(p2) == 3

    def test_pipeline_or_pipeline(self):
        flux_a = Flux.lift(DoubleAgent())
        flux_b = Flux.lift(AddOneAgent())
        flux_c = Flux.lift(SquareAgent())
        flux_d = Flux.lift(ToStringAgent())

        p1 = flux_a | flux_b
        p2 = flux_c | flux_d
        combined = p1 | p2

        assert len(combined) == 4


class TestPipelineRepr:
    """Test pipeline string representation."""

    def test_repr(self):
        p = pipeline(Flux.lift(DoubleAgent()), Flux.lift(AddOneAgent()))

        repr_str = repr(p)

        assert "FluxPipeline" in repr_str
        assert "stages=2" in repr_str
