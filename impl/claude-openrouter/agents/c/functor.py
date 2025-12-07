"""
C-gents: Functors - Structure-preserving transformations.

Functors lift agents to work in different contexts (Maybe, Either, List).
They preserve composition: F(g . f) = F(g) . F(f)

Why: Compose agents that may fail, return errors, or produce collections
without explicit null-checking or error handling at each step.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable, Any

from bootstrap.types import Agent

A = TypeVar("A")
B = TypeVar("B")
T = TypeVar("T")


# --- Maybe: Optional values ---

class Maybe(Generic[T], ABC):
    """
    Optional value container.

    Either Just(value) or Nothing.
    Enables composition of agents that may not produce a result.
    """

    @abstractmethod
    def is_just(self) -> bool:
        pass

    @abstractmethod
    def is_nothing(self) -> bool:
        pass

    @abstractmethod
    def map(self, f: Callable[[T], B]) -> "Maybe[B]":
        """Apply f if Just, propagate Nothing."""
        pass

    @abstractmethod
    def flat_map(self, f: Callable[[T], "Maybe[B]"]) -> "Maybe[B]":
        """Apply f if Just (f returns Maybe), propagate Nothing."""
        pass

    @abstractmethod
    def get_or(self, default: T) -> T:
        """Extract value or return default."""
        pass


@dataclass
class Just(Maybe[T]):
    """Contains a value."""
    value: T

    def is_just(self) -> bool:
        return True

    def is_nothing(self) -> bool:
        return False

    def map(self, f: Callable[[T], B]) -> Maybe[B]:
        return Just(f(self.value))

    def flat_map(self, f: Callable[[T], Maybe[B]]) -> Maybe[B]:
        return f(self.value)

    def get_or(self, default: T) -> T:
        return self.value

    def __repr__(self) -> str:
        return f"Just({self.value!r})"


class _Nothing(Maybe[Any]):
    """Represents absence of value (singleton)."""

    def is_just(self) -> bool:
        return False

    def is_nothing(self) -> bool:
        return True

    def map(self, f: Callable[[Any], B]) -> Maybe[B]:
        return self  # type: ignore

    def flat_map(self, f: Callable[[Any], Maybe[B]]) -> Maybe[B]:
        return self  # type: ignore

    def get_or(self, default: T) -> T:
        return default

    def __repr__(self) -> str:
        return "Nothing"


Nothing: Maybe[Any] = _Nothing()


# --- Either: Success or Error ---

E = TypeVar("E")  # Error type


class Either(Generic[E, T], ABC):
    """
    Either Left(error) or Right(value).

    Convention: Right is success, Left is error.
    Enables composition with error handling.
    """

    @abstractmethod
    def is_right(self) -> bool:
        pass

    @abstractmethod
    def is_left(self) -> bool:
        pass

    @abstractmethod
    def map(self, f: Callable[[T], B]) -> "Either[E, B]":
        """Apply f if Right, propagate Left."""
        pass

    @abstractmethod
    def flat_map(self, f: Callable[[T], "Either[E, B]"]) -> "Either[E, B]":
        """Apply f if Right (f returns Either), propagate Left."""
        pass

    @abstractmethod
    def map_left(self, f: Callable[[E], B]) -> "Either[B, T]":
        """Transform the error if Left."""
        pass


@dataclass
class Right(Either[Any, T]):
    """Success case - contains the value."""
    value: T

    def is_right(self) -> bool:
        return True

    def is_left(self) -> bool:
        return False

    def map(self, f: Callable[[T], B]) -> Either[Any, B]:
        return Right(f(self.value))

    def flat_map(self, f: Callable[[T], Either[Any, B]]) -> Either[Any, B]:
        return f(self.value)

    def map_left(self, f: Callable[[Any], B]) -> Either[B, T]:
        return self  # type: ignore

    def __repr__(self) -> str:
        return f"Right({self.value!r})"


@dataclass
class Left(Either[E, Any]):
    """Error case - contains the error."""
    error: E

    def is_right(self) -> bool:
        return False

    def is_left(self) -> bool:
        return True

    def map(self, f: Callable[[Any], B]) -> Either[E, B]:
        return self  # type: ignore

    def flat_map(self, f: Callable[[Any], Either[E, B]]) -> Either[E, B]:
        return self  # type: ignore

    def map_left(self, f: Callable[[E], B]) -> Either[B, Any]:
        return Left(f(self.error))

    def __repr__(self) -> str:
        return f"Left({self.error!r})"


# --- Lifted Agents ---

class MaybeAgent(Agent[Maybe[A], Maybe[B]]):
    """
    Lifts an Agent[A, B] to work with Maybe values.

    If input is Nothing, short-circuits to Nothing.
    If input is Just(a), applies inner agent to a.
    """

    def __init__(self, inner: Agent[A, B]):
        self._inner = inner
        self._name = f"Maybe({inner.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: Maybe[A]) -> Maybe[B]:
        if input.is_nothing():
            return Nothing
        return Just(await self._inner.invoke(input.value))  # type: ignore


class EitherAgent(Agent[Either[E, A], Either[E, B]]):
    """
    Lifts an Agent[A, B] to work with Either values.

    If input is Left(error), short-circuits with that error.
    If input is Right(a), applies inner agent to a.
    """

    def __init__(self, inner: Agent[A, B]):
        self._inner = inner
        self._name = f"Either({inner.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: Either[E, A]) -> Either[E, B]:
        if input.is_left():
            return input  # type: ignore
        return Right(await self._inner.invoke(input.value))  # type: ignore


# --- Convenience functions ---

def maybe(agent: Agent[A, B]) -> MaybeAgent[A, B]:
    """Lift an agent to handle Maybe values."""
    return MaybeAgent(agent)


def either(agent: Agent[A, B]) -> EitherAgent[Any, A, B]:
    """Lift an agent to handle Either values."""
    return EitherAgent(agent)
