"""Tests for agents.a.quick - One-liner agent creation."""

import pytest

from agents.a.quick import FunctionAgent, agent, pipeline
from agents.poly.types import Agent


class TestAgentDecorator:
    """Tests for @agent decorator."""

    @pytest.mark.asyncio
    async def test_basic_decorator(self) -> None:
        """@agent creates a FunctionAgent from async function."""

        @agent
        async def double(x: int) -> int:
            return x * 2

        assert isinstance(double, FunctionAgent)
        assert double.name == "double"
        result = await double.invoke(5)
        assert result == 10

    @pytest.mark.asyncio
    async def test_decorator_with_name(self) -> None:
        """@agent(name='...') allows custom naming."""

        @agent(name="my-doubler")
        async def double(x: int) -> int:
            return x * 2

        assert double.name == "my-doubler"

    @pytest.mark.asyncio
    async def test_composition(self) -> None:
        """FunctionAgents compose with >>."""

        @agent
        async def double(x: int) -> int:
            return x * 2

        @agent
        async def add_one(x: int) -> int:
            return x + 1

        composed = double >> add_one
        result = await composed.invoke(5)
        assert result == 11  # (5 * 2) + 1

    @pytest.mark.asyncio
    async def test_associativity(self) -> None:
        """Composition is associative."""

        @agent
        async def f(x: int) -> int:
            return x + 1

        @agent
        async def g(x: int) -> int:
            return x * 2

        @agent
        async def h(x: int) -> int:
            return x - 3

        left = (f >> g) >> h
        right = f >> (g >> h)

        assert await left.invoke(5) == await right.invoke(5)

    def test_repr(self) -> None:
        """FunctionAgent has useful repr."""

        @agent
        async def my_agent(x: int) -> int:
            return x

        assert "my_agent" in repr(my_agent)


class TestPipeline:
    """Tests for pipeline() helper."""

    @pytest.mark.asyncio
    async def test_basic_pipeline(self) -> None:
        """pipeline() composes multiple agents."""

        @agent
        async def double(x: int) -> int:
            return x * 2

        @agent
        async def add_one(x: int) -> int:
            return x + 1

        @agent
        async def stringify(x: int) -> str:
            return f"Result: {x}"

        pipe = pipeline(double, add_one, stringify)
        result = await pipe.invoke(5)
        assert result == "Result: 11"

    def test_requires_at_least_two(self) -> None:
        """pipeline() raises ValueError for < 2 agents."""

        @agent
        async def single(x: int) -> int:
            return x

        with pytest.raises(ValueError, match="at least 2 agents"):
            pipeline(single)

    @pytest.mark.asyncio
    async def test_equivalent_to_manual_composition(self) -> None:
        """pipeline(a, b, c) == a >> b >> c."""

        @agent
        async def a(x: int) -> int:
            return x + 1

        @agent
        async def b(x: int) -> int:
            return x * 2

        @agent
        async def c(x: int) -> int:
            return x - 3

        via_pipeline = pipeline(a, b, c)
        via_operators = a >> b >> c

        # Same behavior
        assert await via_pipeline.invoke(5) == await via_operators.invoke(5)


class TestFunctionAgent:
    """Tests for FunctionAgent class."""

    @pytest.mark.asyncio
    async def test_is_agent(self) -> None:
        """FunctionAgent is a proper Agent."""

        @agent
        async def my_agent(x: int) -> int:
            return x * 2

        assert isinstance(my_agent, Agent)

    @pytest.mark.asyncio
    async def test_preserves_docstring(self) -> None:
        """FunctionAgent preserves the wrapped function's docstring."""

        @agent
        async def documented(x: int) -> int:
            """Doubles the input."""
            return x * 2

        assert "Doubles the input" in (documented.__doc__ or "")
