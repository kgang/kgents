"""
Perturbation handling for FluxAgent.

The Perturbation Principle:
- invoke() on DORMANT = direct invocation
- invoke() on FLOWING = perturbation (injected into stream)

This preserves State Integrity for Symbiont agents. A perturbation
flows through the same processing path as normal events, ensuring
state is loaded/saved correctly with no race conditions.

Teaching:
    gotcha: Perturbation priority ordering is REVERSED for asyncio.PriorityQueue.
            Higher priority values come FIRST (e.g., priority=100 before priority=10).
            This is because PriorityQueue is a min-heap, so we flip comparison.
            (Evidence: test_perturbation.py::TestPerturbationOrdering::test_higher_priority_comes_first)

    gotcha: set_result/set_exception/cancel are IDEMPOTENT. Calling them on
            an already-done Future is safe (no-op). This prevents race conditions
            between flux processing and caller cancellation.
            (Evidence: test_perturbation.py::TestPerturbationResult::test_set_result_idempotent)

    gotcha: create_perturbation() uses priority=100 by default, not 0. This means
            helper-created perturbations are HIGH priority. If you want normal
            priority, explicitly pass priority=0.
            (Evidence: test_perturbation.py::TestCreatePerturbation::test_create_with_data)
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")


@dataclass
class Perturbation:
    """
    A high-priority event injected via invoke() on a FLOWING flux.

    Perturbations are wrapper objects that carry:
    1. The input data to process
    2. A Future to receive the result
    3. Priority for queue ordering
    4. Timestamp for tracking

    The Perturbation Principle:
    - invoke() on DORMANT = direct invocation (returns immediately)
    - invoke() on FLOWING = perturbation (injected into stream, awaits result)

    This preserves State Integrity for Symbiont agents:
    - Perturbation goes through the same processing path as normal events
    - State is loaded/saved correctly
    - No race conditions between stream and invoke
    """

    data: Any
    """The input data (type A)."""

    result_future: asyncio.Future[Any]
    """Future to receive the result (type B)."""

    priority: int = 0
    """
    Higher = processed sooner. Default perturbations have priority 0.
    Normal stream events also have priority 0, but perturbations are
    checked before normal events in the merged source.
    """

    timestamp: float = field(default_factory=time.time)
    """When the perturbation was created. Used for debugging/tracing."""

    def __lt__(self, other: "Perturbation") -> bool:
        """
        For priority queue ordering (higher priority first).

        Note: We reverse comparison because asyncio.PriorityQueue
        is a min-heap, so we want higher priorities to sort first.
        Ties are broken by timestamp (earlier first).
        """
        if self.priority != other.priority:
            return self.priority > other.priority  # Higher priority first
        return self.timestamp < other.timestamp  # Earlier first for ties

    def __le__(self, other: "Perturbation") -> bool:
        return self < other or (
            self.priority == other.priority and self.timestamp == other.timestamp
        )

    def __gt__(self, other: "Perturbation") -> bool:
        return not self <= other

    def __ge__(self, other: "Perturbation") -> bool:
        return not self < other

    def __hash__(self) -> int:
        """Hash based on id for use in sets."""
        return id(self)

    def __eq__(self, other: object) -> bool:
        """Equality based on identity, not values."""
        return self is other

    def set_result(self, result: Any) -> None:
        """
        Set the result for the perturbation.

        Safe to call even if the future is already done.
        """
        if not self.result_future.done():
            self.result_future.set_result(result)

    def set_exception(self, exc: Exception) -> None:
        """
        Set an exception for the perturbation.

        Safe to call even if the future is already done.
        """
        if not self.result_future.done():
            self.result_future.set_exception(exc)

    def cancel(self, msg: str = "Perturbation cancelled") -> None:
        """
        Cancel the perturbation.

        Safe to call even if the future is already done.
        """
        if not self.result_future.done():
            self.result_future.cancel(msg)

    @property
    def is_done(self) -> bool:
        """Check if the perturbation has been processed."""
        return self.result_future.done()


def is_perturbation(event: Any) -> bool:
    """Check if event is a Perturbation wrapper."""
    return isinstance(event, Perturbation)


def unwrap_perturbation(event: Any) -> tuple[Any, asyncio.Future[Any] | None]:
    """
    Unwrap event, returning (data, future_or_none).

    If event is Perturbation: returns (data, result_future)
    If event is normal: returns (event, None)

    This enables uniform processing of both perturbations and normal events.
    """
    if is_perturbation(event):
        return event.data, event.result_future
    return event, None


def create_perturbation(
    data: Any,
    priority: int = 100,
    loop: asyncio.AbstractEventLoop | None = None,
) -> Perturbation:
    """
    Create a new perturbation with a fresh Future.

    Args:
        data: The input data to process
        priority: Priority level (higher = sooner)
        loop: Optional event loop for the Future

    Returns:
        Perturbation wrapper with a new Future
    """
    if loop is None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

    future: asyncio.Future[Any] = loop.create_future()
    return Perturbation(
        data=data,
        result_future=future,
        priority=priority,
    )


async def await_perturbation(
    perturbation: Perturbation,
    timeout: float | None = None,
) -> Any:
    """
    Await a perturbation result with optional timeout.

    Args:
        perturbation: The perturbation to await
        timeout: Optional timeout in seconds

    Returns:
        The result from the perturbation

    Raises:
        asyncio.TimeoutError: If timeout is exceeded
        Any exception set on the perturbation's future
    """
    if timeout is not None:
        return await asyncio.wait_for(perturbation.result_future, timeout=timeout)
    return await perturbation.result_future
