"""
C-gents: Monads - Pure compositional effect handling.

Monads solve: "How do I compose functions that produce wrapped results?"

This module provides ONLY the formal Monad interface and core instances.
Agent-specific monadic composition is in monad_agents.py.

Why Monads matter:
    Without monads:
        result1 = f(input)
        if result1.is_error: return result1
        result2 = g(result1.value)
        if result2.is_error: return result2
        ...

    With monads:
        result = bind(bind(f, input), g)
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

from .functor import Either, Just, Left, Maybe, Nothing, Right

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
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


def pure_maybe(value: A) -> Maybe[A]:
    """unit/return for Maybe monad."""
    return Just(value)


def pure_either(value: A) -> Either[None, A]:
    """unit/return for Either monad (with no error)."""
    return Right(value)


def fail_either(error: str) -> Either[str, None]:
    """Create a failed Either."""
    return Left(error)


# --- Monad transformers (composition of monads) ---


class MaybeEither(Generic[A]):
    """
    Composed monad: Maybe[Either[E, A]]

    Short-circuits on Nothing OR Left.
    Useful for computations that can fail in two ways:
        - Absence (Maybe)
        - Explicit error (Either)
    """

    def __init__(self, value: Maybe[Either[Any, A]]):
        self._value = value

    @classmethod
    def pure(cls, a: A) -> "MaybeEither[A]":
        """Lift a pure value into MaybeEither."""
        return cls(Just(Right(a)))

    @classmethod
    def fail_nothing(cls) -> "MaybeEither[Any]":
        """Represent absence."""
        return cls(Nothing)  # Nothing is compatible with Maybe[Either[Any, Any]]

    @classmethod
    def fail_left(cls, error: Any) -> "MaybeEither[Any]":
        """Represent explicit error."""
        return cls(Just(Left(error)))

    def bind(self, f: Callable[[A], "MaybeEither[B]"]) -> "MaybeEither[B]":
        """
        Monadic bind for MaybeEither.

        Short-circuits on Nothing or Left.
        """
        if self._value.is_nothing():
            return MaybeEither(
                Nothing
            )  # Nothing is compatible with Maybe[Either[Any, B]]
        inner = self._value.value  # type: ignore
        if inner.is_left():
            return MaybeEither(Just(inner))
        return f(inner.value)

    def run(self) -> Maybe[Either[Any, A]]:
        """Extract the wrapped value."""
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
    # Transformers
    "MaybeEither",
]
