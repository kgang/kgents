"""
Quick Agent Creation: One-Liner Convenience.

Turn any async function into an agent with a single decorator:

    @agent
    async def double(x: int) -> int:
        return x * 2

    result = await double.invoke(5)  # 10

For composition:

    pipe = pipeline(double, add_one, stringify)
    result = await pipe.invoke(5)  # "11"
"""

from __future__ import annotations

from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    TypeVar,
    overload,
)

from agents.poly.types import Agent

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class FunctionAgent(Agent[A, B], Generic[A, B]):
    """
    Agent wrapper for async functions.

    Created by the @agent decorator. Preserves the function's
    signature and docstring while adding agent semantics.
    """

    def __init__(
        self,
        fn: Callable[[A], Awaitable[B]],
        agent_name: str | None = None,
    ) -> None:
        self._fn = fn
        self._name = agent_name or fn.__name__
        # Preserve function metadata (docstring, etc.)
        self.__doc__ = fn.__doc__
        self.__module__ = fn.__module__

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> B:
        return await self._fn(input)

    def __repr__(self) -> str:
        return f"FunctionAgent({self._name})"


@overload
def agent(fn: Callable[[A], Awaitable[B]]) -> FunctionAgent[A, B]: ...


@overload
def agent(
    *, name: str
) -> Callable[[Callable[[A], Awaitable[B]]], FunctionAgent[A, B]]: ...


def agent(
    fn: Callable[[A], Awaitable[B]] | None = None,
    *,
    name: str | None = None,
) -> FunctionAgent[A, B] | Callable[[Callable[[A], Awaitable[B]]], FunctionAgent[A, B]]:
    """
    Decorator to create an agent from an async function.

    Can be used with or without arguments:

        @agent
        async def double(x: int) -> int:
            return x * 2

        @agent(name="my-doubler")
        async def double(x: int) -> int:
            return x * 2

    Args:
        fn: The async function to wrap (when used without parentheses)
        name: Optional custom name for the agent

    Returns:
        A FunctionAgent wrapping the function
    """
    if fn is not None:
        # Called without arguments: @agent
        return FunctionAgent(fn)

    # Called with arguments: @agent(name="...")
    def decorator(f: Callable[[A], Awaitable[B]]) -> FunctionAgent[A, B]:
        return FunctionAgent(f, agent_name=name)

    return decorator


def pipeline(*agents: Agent[Any, Any]) -> Agent[Any, Any]:
    """
    Compose multiple agents into a pipeline.

    Equivalent to: agents[0] >> agents[1] >> ... >> agents[n]

    Example:
        pipe = pipeline(parse_int, double, stringify)
        result = await pipe.invoke("21")  # "42"

    Args:
        *agents: Two or more agents to compose

    Returns:
        A composed agent that runs all agents in sequence

    Raises:
        ValueError: If fewer than 2 agents provided
    """
    if len(agents) < 2:
        raise ValueError("pipeline() requires at least 2 agents")

    result = agents[0]
    for ag in agents[1:]:
        result = result >> ag
    return result


__all__ = [
    "FunctionAgent",
    "agent",
    "pipeline",
]
