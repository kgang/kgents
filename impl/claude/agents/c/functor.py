"""
C-gents: Functors - Structure-preserving transformations.

Functors lift agents to work in different contexts (Maybe, Either, List).
They preserve composition: F(g . f) = F(g) . F(f)

Why: Compose agents that may fail, return errors, or produce collections
without explicit null-checking or error handling at each step.

Functor Laws:
1. Identity: F(id_A) = id_F(A)
2. Composition: F(g ∘ f) = F(g) ∘ F(f)
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Generic, Optional, TypeVar

from bootstrap.types import Agent

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
T = TypeVar("T")

logger = logging.getLogger(__name__)


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
        return self  # Nothing is a singleton, safe cast

    def flat_map(self, f: Callable[[Any], Maybe[B]]) -> Maybe[B]:
        return self  # Nothing is a singleton, safe cast

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
        return self  # Right is covariant, safe cast

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
        return self  # Left is covariant in error type, safe cast

    def flat_map(self, f: Callable[[Any], Either[E, B]]) -> Either[E, B]:
        return self  # Left is covariant in error type, safe cast

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


# --- Fix Pattern: Retry with Exponential Backoff ---


class FixAgent(Agent[A, B]):
    """
    Fix-pattern retry wrapper for transient failures.

    Applies exponential backoff: base_delay * (2 ** attempt)
    Logs all retry attempts as data (conflicts are data principle).

    Example:
        reliable_agent = fix(flaky_agent, max_attempts=3, base_delay=1.0)
    """

    def __init__(
        self,
        inner: Agent[A, B],
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        is_transient: Callable[[Exception], bool] | None = None,
    ):
        """
        Args:
            inner: The agent to wrap with retry logic
            max_attempts: Maximum retry attempts (default: 3)
            base_delay: Base delay in seconds (default: 1.0)
            max_delay: Maximum delay cap in seconds (default: 60.0)
            is_transient: Predicate to identify transient errors (default: all exceptions)
        """
        self._inner = inner
        self._max_attempts = max_attempts
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._is_transient = is_transient or (lambda _: True)
        self._name = f"Fix({inner.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> B:
        last_error: Exception | None = None

        for attempt in range(self._max_attempts):
            try:
                result = await self._inner.invoke(input)
                if attempt > 0:
                    logger.info(
                        f"{self.name}: succeeded on attempt {attempt + 1}/{self._max_attempts}"
                    )
                return result
            except Exception as e:
                last_error = e

                # If non-transient or last attempt, propagate immediately
                if not self._is_transient(e) or attempt == self._max_attempts - 1:
                    logger.warning(
                        f"{self.name}: failed on attempt {attempt + 1}/{self._max_attempts} "
                        f"(error: {type(e).__name__}: {e})"
                    )
                    raise

                # Calculate backoff delay
                delay = min(self._base_delay * (2**attempt), self._max_delay)
                logger.info(
                    f"{self.name}: transient failure on attempt {attempt + 1}/{self._max_attempts}, "
                    f"retrying in {delay:.2f}s (error: {type(e).__name__}: {e})"
                )
                await asyncio.sleep(delay)

        # Should never reach here due to raise in loop, but satisfy type checker
        assert last_error is not None
        raise last_error


# --- Convenience functions ---


def maybe(agent: Agent[A, B]) -> MaybeAgent[A, B]:
    """Lift an agent to handle Maybe values."""
    return MaybeAgent(agent)


def either(agent: Agent[A, B]) -> EitherAgent[Any, A, B]:
    """Lift an agent to handle Either values."""
    return EitherAgent(agent)


def fix(
    agent: Agent[A, B],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    is_transient: Callable[[Exception], bool] | None = None,
) -> FixAgent[A, B]:
    """
    Wrap an agent with Fix-pattern retry logic and exponential backoff.

    Args:
        agent: The agent to make resilient to transient failures
        max_attempts: Maximum retry attempts (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 1.0)
        max_delay: Maximum delay cap in seconds (default: 60.0)
        is_transient: Predicate to identify transient errors (default: retry all)

    Returns:
        FixAgent that retries on transient failures with exponential backoff
    """
    return FixAgent(agent, max_attempts, base_delay, max_delay, is_transient)


# --- List Functor: Process Collections ---


class ListAgent(Agent[list[A], list[B]]):
    """
    Lifts an Agent[A, B] to work with lists.

    Applies the inner agent to each element in the list independently.
    Preserves order of results.

    Example:
        double: Agent[int, int] = ...
        list_double = ListAgent(double)
        await list_double.invoke([1, 2, 3])  # Returns [2, 4, 6]
    """

    def __init__(self, inner: Agent[A, B], parallel: bool = True):
        """
        Args:
            inner: The agent to apply to each element
            parallel: If True, process elements concurrently (default: True)
        """
        self._inner = inner
        self._parallel = parallel
        self._name = f"List({inner.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: list[A]) -> list[B]:
        if not input:
            return []

        if self._parallel:
            # Process all elements concurrently
            tasks = [self._inner.invoke(item) for item in input]
            return await asyncio.gather(*tasks)
        else:
            # Process elements sequentially
            results = []
            for item in input:
                result = await self._inner.invoke(item)
                results.append(result)
            return results


# --- Async Functor: Non-blocking Execution ---


class AsyncAgent(Agent[A, asyncio.Future[B]]):
    """
    Lifts an Agent[A, B] to return a Future[B] immediately.

    The agent starts executing in the background and returns a Future
    that can be awaited later. Enables fire-and-forget or delayed retrieval.

    Example:
        slow_agent: Agent[A, B] = ...
        async_agent = AsyncAgent(slow_agent)
        future = await async_agent.invoke(input)  # Returns immediately
        # ... do other work ...
        result = await future  # Wait for completion
    """

    def __init__(self, inner: Agent[A, B]):
        self._inner = inner
        self._name = f"Async({inner.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> asyncio.Future[B]:
        # Create a task that runs the inner agent
        task = asyncio.create_task(self._inner.invoke(input))
        return task  # type: ignore


# --- Logged Functor: Add Observability ---


@dataclass
class LogEntry:
    """Single log entry for an agent invocation."""

    timestamp: datetime
    agent_name: str
    input_repr: str
    output_repr: str
    duration_ms: float
    error: Optional[str] = None


class LoggedAgent(Agent[A, B]):
    """
    Lifts an Agent[A, B] to log all invocations.

    Records timestamp, input, output, duration, and any errors.
    Useful for debugging, auditing, and performance monitoring.

    Example:
        agent: Agent[A, B] = ...
        logged = LoggedAgent(agent)
        result = await logged.invoke(input)
        # Check logged.history for execution log
    """

    def __init__(
        self,
        inner: Agent[A, B],
        log_level: int = logging.INFO,
        max_repr_length: int = 200,
    ):
        """
        Args:
            inner: The agent to wrap with logging
            log_level: Logging level (default: INFO)
            max_repr_length: Maximum length for input/output repr (default: 200)
        """
        self._inner = inner
        self._log_level = log_level
        self._max_repr_length = max_repr_length
        self._name = f"Logged({inner.name})"
        self.history: list[LogEntry] = []

    @property
    def name(self) -> str:
        return self._name

    def _truncate_repr(self, obj: Any) -> str:
        """Truncate object representation to max length."""
        repr_str = repr(obj)
        if len(repr_str) <= self._max_repr_length:
            return repr_str
        return repr_str[: self._max_repr_length - 3] + "..."

    async def invoke(self, input: A) -> B:
        start_time = datetime.now()
        input_repr = self._truncate_repr(input)
        error_msg: Optional[str] = None

        try:
            logger.log(
                self._log_level,
                f"{self.name}: invoking with input: {input_repr}",
            )

            result = await self._inner.invoke(input)

            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            output_repr = self._truncate_repr(result)

            logger.log(
                self._log_level,
                f"{self.name}: completed in {duration_ms:.2f}ms, output: {output_repr}",
            )

            # Record to history
            self.history.append(
                LogEntry(
                    timestamp=start_time,
                    agent_name=self._inner.name,
                    input_repr=input_repr,
                    output_repr=output_repr,
                    duration_ms=duration_ms,
                )
            )

            return result

        except Exception as e:
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            error_msg = f"{type(e).__name__}: {e}"

            logger.log(
                logging.ERROR,
                f"{self.name}: failed after {duration_ms:.2f}ms with error: {error_msg}",
            )

            # Record failure to history
            self.history.append(
                LogEntry(
                    timestamp=start_time,
                    agent_name=self._inner.name,
                    input_repr=input_repr,
                    output_repr="<error>",
                    duration_ms=duration_ms,
                    error=error_msg,
                )
            )

            raise


# --- Functor Law Validation ---


async def check_identity_law(
    functor_lift: Callable[[Agent[A, B]], Agent[Any, Any]],
    identity_agent: Agent[A, A],
    test_input: Any,
) -> bool:
    """
    Verify the identity functor law: F(id_A) behaves like id_F(A).

    Args:
        functor_lift: Function that lifts an agent (e.g., maybe, either, list)
        identity_agent: An identity agent for type A
        test_input: Test input in the functor's context

    Returns:
        True if identity law holds, False otherwise
    """
    try:
        lifted = functor_lift(identity_agent)
        result = await lifted.invoke(test_input)

        # For most functors, F(id)(x) should equal x
        # (equality check depends on functor type)
        return result == test_input
    except Exception as e:
        logger.warning(f"Identity law check failed with error: {e}")
        return False


async def check_composition_law(
    functor_lift: Callable[[Agent[Any, Any]], Agent[Any, Any]],
    f: Agent[A, B],
    g: Agent[B, C],
    test_input: Any,
) -> bool:
    """
    Verify composition functor law: F(g ∘ f) = F(g) ∘ F(f).

    Args:
        functor_lift: Function that lifts an agent
        f: First agent A → B
        g: Second agent B → C
        test_input: Test input in the functor's context

    Returns:
        True if composition law holds, False otherwise
    """
    try:
        # Left side: F(g ∘ f)
        composed = f >> g
        lifted_composed = functor_lift(composed)
        result_left = await lifted_composed.invoke(test_input)

        # Right side: F(g) ∘ F(f)
        lifted_f = functor_lift(f)
        lifted_g = functor_lift(g)
        lifted_composition = lifted_f >> lifted_g
        result_right = await lifted_composition.invoke(test_input)

        # Results should be equal
        return result_left == result_right
    except Exception as e:
        logger.warning(f"Composition law check failed with error: {e}")
        return False


# --- Convenience functions for new functors ---


def list_agent(agent: Agent[A, B], parallel: bool = True) -> ListAgent[A, B]:
    """Lift an agent to process lists of values."""
    return ListAgent(agent, parallel=parallel)


def async_agent(agent: Agent[A, B]) -> AsyncAgent[A, B]:
    """Lift an agent to return futures for non-blocking execution."""
    return AsyncAgent(agent)


def logged(
    agent: Agent[A, B],
    log_level: int = logging.INFO,
    max_repr_length: int = 200,
) -> LoggedAgent[A, B]:
    """Lift an agent to log all invocations."""
    return LoggedAgent(agent, log_level=log_level, max_repr_length=max_repr_length)


# Promise functor moved to j_integration.py (C×J integration)
