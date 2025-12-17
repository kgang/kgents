"""
C-gents: Conditional Composition - Branching patterns.

Pattern:
input → [condition?] → [A] if true
                      → [B] if false
"""

import asyncio
from typing import Awaitable, Callable, TypeVar, Union

from agents.poly.types import Agent

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# Type alias for predicates that can be sync or async
Predicate = Union[Callable[[A], bool], Callable[[A], Awaitable[bool]]]


async def _eval_predicate(predicate: Predicate[A], input: A) -> bool:
    """Evaluate a predicate, handling both sync and async cases."""
    result = predicate(input)
    if asyncio.iscoroutine(result):
        awaited: bool = await result
        return awaited
    # result is bool since we checked it's not a coroutine
    assert isinstance(result, bool)
    return result


class BranchAgent(Agent[A, Union[B, C]]):
    """
    Conditional branching based on a predicate.

    If predicate(input) is True, runs if_true agent.
    Otherwise, runs if_false agent.

    Predicate can be sync or async.
    """

    def __init__(
        self,
        predicate: Predicate[A],
        if_true: Agent[A, B],
        if_false: Agent[A, C],
    ):
        self._predicate = predicate
        self._if_true = if_true
        self._if_false = if_false
        self._name = f"Branch({if_true.name} | {if_false.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> Union[B, C]:
        if await _eval_predicate(self._predicate, input):
            return await self._if_true.invoke(input)
        return await self._if_false.invoke(input)


class SwitchAgent(Agent[A, B]):
    """
    Multi-way switch based on a key function.

    Maps input to a key, selects agent based on key.
    Falls back to default if key not found.

    Key function can be sync or async.
    """

    def __init__(
        self,
        key_fn: Union[Callable[[A], str], Callable[[A], Awaitable[str]]],
        cases: dict[str, Agent[A, B]],
        default: Agent[A, B],
    ):
        self._key_fn = key_fn
        self._cases = cases
        self._default = default
        case_names = ", ".join(f"{k}={v.name}" for k, v in cases.items())
        self._name = f"Switch({case_names}, default={default.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> B:
        key_result = self._key_fn(input)
        if asyncio.iscoroutine(key_result):
            key = await key_result
        else:
            key = key_result
        agent = self._cases.get(key, self._default)
        return await agent.invoke(input)


class GuardedAgent(Agent[A, B]):
    """
    Runs agent only if guard passes, otherwise returns default.

    Useful for validation-then-transform patterns.
    Guard can be sync or async.
    """

    def __init__(
        self,
        guard: Predicate[A],
        agent: Agent[A, B],
        on_fail: B,
    ):
        self._guard = guard
        self._agent = agent
        self._on_fail = on_fail
        self._name = f"Guarded({agent.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> B:
        if await _eval_predicate(self._guard, input):
            return await self._agent.invoke(input)
        return self._on_fail


class FilterAgent(Agent[list[A], list[A]]):
    """
    Filters a list of inputs based on a predicate.

    Keeps only elements where predicate returns True.
    Predicate can be sync or async.
    """

    def __init__(self, predicate: Predicate[A], name: str = "Filter"):
        self._predicate = predicate
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: list[A]) -> list[A]:
        results = []
        for x in input:
            if await _eval_predicate(self._predicate, x):
                results.append(x)
        return results


# --- Convenience functions ---


def branch(
    predicate: Predicate[A],
    if_true: Agent[A, B],
    if_false: Agent[A, C],
) -> BranchAgent[A, B, C]:
    """Create a conditional branch."""
    return BranchAgent(predicate, if_true, if_false)


def switch(
    key_fn: Union[Callable[[A], str], Callable[[A], Awaitable[str]]],
    cases: dict[str, Agent[A, B]],
    default: Agent[A, B],
) -> SwitchAgent[A, B]:
    """Create a multi-way switch."""
    return SwitchAgent(key_fn, cases, default)


def guarded(
    guard: Predicate[A],
    agent: Agent[A, B],
    on_fail: B,
) -> GuardedAgent[A, B]:
    """Create a guarded agent."""
    return GuardedAgent(guard, agent, on_fail)


def filter_by(predicate: Predicate[A], name: str = "Filter") -> FilterAgent[A]:
    """Create a filter agent."""
    return FilterAgent(predicate, name)
