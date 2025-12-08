"""
C-gents: Monads - Compositional effect handling.

Monads solve: "How do I compose agents that produce wrapped results?"

This module provides the formal Monad interface and MonadicAgent wrapper.
The actual Maybe and Either implementations are in functor.py.

Why Monads matter:
    Without monads:
        result1 = agent1.invoke(input)
        if result1.is_error: return result1
        result2 = agent2.invoke(result1.value)
        if result2.is_error: return result2
        ...

    With monads:
        agent1.bind(agent2).bind(agent3).invoke(input)
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Callable, Awaitable

from bootstrap.types import Agent
from .functor import Maybe, Just, Nothing, Either, Right, Left

A = TypeVar("A")
B = TypeVar("B")
M = TypeVar("M")


class Monad(ABC, Generic[A]):
    """
    Formal Monad interface.

    A Monad is a type constructor M with two operations:
        unit (return): A → M[A]
        bind (>>=): M[A] → (A → M[B]) → M[B]

    Laws (must hold for valid monads):
        1. Left identity:  unit(a).bind(f) ≡ f(a)
        2. Right identity: m.bind(unit) ≡ m
        3. Associativity:  m.bind(f).bind(g) ≡ m.bind(λa. f(a).bind(g))
    """

    @classmethod
    @abstractmethod
    def unit(cls, value: A) -> "Monad[A]":
        """Wrap a value in the monadic context."""
        pass

    @abstractmethod
    def bind(self, f: Callable[[A], "Monad[B]"]) -> "Monad[B]":
        """Sequence computation: unwrap, apply f, rewrap."""
        pass


# --- Monad instances for Maybe and Either ---
# Maybe and Either from functor.py already have flat_map which IS bind.
# We provide aliases for clarity:

def pure_maybe(value: A) -> Maybe[A]:
    """unit/return for Maybe monad."""
    return Just(value)


def pure_either(value: A) -> Either[None, A]:
    """unit/return for Either monad (with no error)."""
    return Right(value)


def fail_either(error: str) -> Either[str, None]:
    """Create a failed Either."""
    return Left(error)


# --- Monadic Agent Composition ---

class MonadicAgent(Generic[M, A, B], Agent[M, M]):
    """
    Wraps an Agent to work monadically.

    Enables: agent1.bind(agent2).bind(agent3)

    The wrapped agent operates on the value inside the monad,
    and the result is automatically rewrapped.
    """

    def __init__(
        self,
        inner: Agent[A, B],
        unwrap: Callable[[M], A],
        wrap: Callable[[B], M],
        is_failed: Callable[[M], bool],
    ):
        """
        Create a monadic wrapper.

        Args:
            inner: The agent to wrap
            unwrap: Extract value from monad (e.g., just.value)
            wrap: Put value into monad (e.g., Just)
            is_failed: Check if monad is in failure state
        """
        self._inner = inner
        self._unwrap = unwrap
        self._wrap = wrap
        self._is_failed = is_failed
        self._name = f"Monadic({inner.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: M) -> M:
        """Run agent if not failed, otherwise propagate failure."""
        if self._is_failed(input):
            return input
        value = self._unwrap(input)
        result = await self._inner.invoke(value)
        return self._wrap(result)


# --- Do-notation simulation ---
# Python doesn't have do-notation, but we can simulate with async/await

async def do_maybe(
    *steps: Callable[[A], Awaitable[Maybe[B]]]
) -> Callable[[Maybe[A]], Awaitable[Maybe[B]]]:
    """
    Simulate do-notation for Maybe.

    Usage:
        result = await do_maybe(
            step1,  # A → Awaitable[Maybe[B]]
            step2,  # B → Awaitable[Maybe[C]]
            step3,  # C → Awaitable[Maybe[D]]
        )(initial_maybe)
    """
    async def run(m: Maybe[A]) -> Maybe[B]:
        current = m
        for step in steps:
            if current.is_nothing():
                return Nothing  # type: ignore
            current = await step(current.value)  # type: ignore
        return current  # type: ignore
    return run


# --- Convenience: bind chains ---

class MaybeChain(Generic[A]):
    """
    Builder for Maybe monad chains.

    Usage:
        result = await (
            MaybeChain(Just(input))
            .then(agent1)
            .then(agent2)
            .then(agent3)
            .run()
        )
    """

    def __init__(self, initial: Maybe[A]):
        self._initial = initial
        self._agents: list[Agent] = []

    def then(self, agent: Agent[A, B]) -> "MaybeChain[B]":
        """Add an agent to the chain."""
        self._agents.append(agent)
        return self  # type: ignore

    async def run(self) -> Maybe:
        """Execute the chain."""
        current = self._initial
        for agent in self._agents:
            if current.is_nothing():
                return Nothing
            current = Just(await agent.invoke(current.value))  # type: ignore
        return current


class EitherChain(Generic[A]):
    """
    Builder for Either monad chains.

    Usage:
        result = await (
            EitherChain(Right(input))
            .then(agent1)
            .then(agent2)
            .run()
        )

        if result.is_left():
            print(f"Failed: {result.error}")
    """

    def __init__(self, initial: Either):
        self._initial = initial
        self._agents: list[Agent] = []

    def then(self, agent: Agent[A, B]) -> "EitherChain[B]":
        """Add an agent to the chain."""
        self._agents.append(agent)
        return self  # type: ignore

    async def run(self) -> Either:
        """Execute the chain."""
        current = self._initial
        for agent in self._agents:
            if current.is_left():
                return current
            current = Right(await agent.invoke(current.value))  # type: ignore
        return current


# --- Monad transformers (composition of monads) ---
# For composing Maybe[Either[A]] or Either[Maybe[A]]

class MaybeEither(Generic[A]):
    """
    Composed monad: Maybe[Either[E, A]]

    Short-circuits on Nothing OR Left.
    """

    def __init__(self, value: Maybe[Either]):
        self._value = value

    @classmethod
    def pure(cls, a: A) -> "MaybeEither[A]":
        return cls(Just(Right(a)))

    @classmethod
    def fail_nothing(cls) -> "MaybeEither":
        return cls(Nothing)  # type: ignore

    @classmethod
    def fail_left(cls, error) -> "MaybeEither":
        return cls(Just(Left(error)))

    def bind(self, f: Callable[[A], "MaybeEither[B]"]) -> "MaybeEither[B]":
        if self._value.is_nothing():
            return MaybeEither(Nothing)  # type: ignore
        inner = self._value.value  # type: ignore
        if inner.is_left():
            return MaybeEither(Just(inner))
        return f(inner.value)

    def run(self) -> Maybe[Either]:
        return self._value


# Re-export from functor for convenience
__all__ = [
    # Monad interface
    "Monad",
    # Maybe monad
    "Maybe",
    "Just",
    "Nothing",
    "pure_maybe",
    # Either monad
    "Either",
    "Right",
    "Left",
    "pure_either",
    "fail_either",
    # Monadic agents
    "MonadicAgent",
    "MaybeChain",
    "EitherChain",
    # Transformers
    "MaybeEither",
]
