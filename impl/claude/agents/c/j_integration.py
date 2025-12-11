"""
C-gent × J-gent Integration: Promise Functor.

The Promise functor lifts agents to return lazy computations with Ground fallback.
This bridges C-gent's functor system with J-gent's Promise type.

Integration Pattern:
    from agents.c.j_integration import PromiseAgent, promise_agent, resolve_promise
    from agents.j.promise import Promise

    agent: Agent[A, B] = ...
    ground_value: B = ...
    promise_agent = PromiseAgent(agent, ground_value)
    promise = await promise_agent.invoke(input)
    result = await resolve_promise(promise, computation)
"""

from __future__ import annotations

from typing import Awaitable, Callable, Optional, TypeVar, Union

from agents.j.promise import Promise as JPromise
from bootstrap.types import Agent

A = TypeVar("A")
B = TypeVar("B")
T = TypeVar("T")


class PromiseAgent(Agent[A, JPromise[B]]):
    """
    Lifts an Agent[A, B] to return a Promise[B] instead of B directly.

    The computation is deferred until the promise is explicitly resolved.
    If resolution fails, returns the ground value.

    This is a lazy functor - enables:
    - Computation on demand
    - Parallel resolution of independent promises
    - Safe fallback via Ground

    Functor Laws for Promise:
    - Identity: Promise(Id) = PromiseId (returns resolved Promise(x) for any x)
    - Composition: Promise(f >> g) = Promise(f) >> Promise(g)

    Example:
        agent: Agent[A, B] = ...
        ground_value: B = ...
        promise_agent = PromiseAgent(agent, ground_value)
        promise = await promise_agent.invoke(input)
        # ... later ...
        result = await resolve_promise(promise)
    """

    def __init__(
        self, inner: Agent[A, B], ground: B, intent: Optional[str] = None
    ) -> None:
        """
        Args:
            inner: The agent to wrap as a promise
            ground: Fallback value if promise fails
            intent: Description of what the promise delivers (default: agent name)
        """
        self._inner = inner
        self._ground = ground
        self._intent = intent or f"Compute {inner.name}"
        self._name = f"Promise({inner.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> JPromise[B]:
        """Return a promise that will compute the result when resolved."""
        # Return unresolved promise
        return JPromise(
            intent=self._intent,
            ground=self._ground,
            context={"input": input, "agent": self._inner.name},
        )


async def resolve_promise(
    promise: JPromise[T],
    computation: Union[Callable[[], T], Callable[[], Awaitable[T]]],
) -> T:
    """
    Resolve a promise by executing its computation.

    Args:
        promise: The promise to resolve
        computation: The deferred computation to execute (can be sync or async)

    Returns:
        The computed value on success, or ground value on failure
    """
    if promise.is_resolved:
        return promise.value_or_ground()

    try:
        promise.mark_resolving()
        result_or_awaitable = computation()
        # Check if the result is awaitable
        if hasattr(result_or_awaitable, "__await__"):
            result = await result_or_awaitable
        else:
            result = result_or_awaitable
        promise.mark_resolved(result)
        return result
    except Exception as e:
        promise.mark_failed(f"Computation failed: {e}")
        return promise.ground


def promise_agent(
    agent: Agent[A, B],
    ground: B,
    intent: Optional[str] = None,
) -> PromiseAgent[A, B]:
    """Lift an agent to return promises (lazy computation)."""
    return PromiseAgent(agent, ground=ground, intent=intent)
