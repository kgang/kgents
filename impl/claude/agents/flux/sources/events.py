"""
Event-driven sources (NOT timer-driven).

THIS IS THE PATTERN. Event-driven sources respond to actual events,
not arbitrary timer ticks. They represent the preferred way to feed
data into flux pipelines.
"""

from typing import Any, AsyncIterator, Iterable, TypeVar

from .base import SourceProtocol

T = TypeVar("T")


async def from_events(bus: SourceProtocol[T]) -> AsyncIterator[T]:
    """
    Yield events as they occur from an event bus.

    THIS IS THE PATTERN. Event-driven, not timer-driven.

    The event bus can be any object implementing the SourceProtocol,
    which requires a subscribe() method returning an AsyncIterator.

    Args:
        bus: Event source implementing SourceProtocol

    Yields:
        Events as they occur

    Example:
        >>> async for event in from_events(my_bus):
        ...     process(event)
    """
    async for event in bus.subscribe():
        yield event


async def from_stream(stream: AsyncIterator[T]) -> AsyncIterator[T]:
    """
    Pass-through adapter for any async iterator.

    Useful for wrapping existing async iterators to ensure
    compatibility with flux sources.

    Args:
        stream: Any async iterator

    Yields:
        Items from the stream unchanged

    Example:
        >>> async def my_generator():
        ...     yield 1
        ...     yield 2
        ...
        >>> async for item in from_stream(my_generator()):
        ...     print(item)
    """
    async for item in stream:
        yield item


async def from_iterable(items: Iterable[T]) -> AsyncIterator[T]:
    """
    Create an async iterator from a synchronous iterable.

    Useful for testing or for converting lists/tuples/etc to
    flux-compatible sources.

    Args:
        items: Any synchronous iterable (list, tuple, set, etc.)

    Yields:
        Items from the iterable

    Example:
        >>> async for item in from_iterable([1, 2, 3]):
        ...     print(item)
        1
        2
        3
    """
    for item in items:
        yield item


async def from_queue(queue: Any) -> AsyncIterator[Any]:
    """
    Yield items from an asyncio.Queue until a sentinel is received.

    The queue should emit a None sentinel to signal completion.

    Args:
        queue: asyncio.Queue to read from

    Yields:
        Items from the queue until None is received
    """
    while True:
        item = await queue.get()
        if item is None:  # Sentinel
            break
        yield item


async def empty() -> AsyncIterator[Any]:
    """
    Create an empty async iterator.

    Useful as a default or placeholder source that immediately completes.

    Yields:
        Nothing - completes immediately
    """
    return
    yield  # Make this a generator (never reached)


async def single(value: T) -> AsyncIterator[T]:
    """
    Create a source that emits a single value then completes.

    Args:
        value: The single value to emit

    Yields:
        The single value

    Example:
        >>> async for item in single(42):
        ...     print(item)
        42
    """
    yield value


async def repeat(value: T, times: int | None = None) -> AsyncIterator[T]:
    """
    Create a source that emits a value repeatedly.

    Args:
        value: The value to repeat
        times: Number of times to repeat (None = infinite)

    Yields:
        The value, repeated

    Example:
        >>> async for item in repeat("hello", 3):
        ...     print(item)
        hello
        hello
        hello
    """
    if times is None:
        while True:
            yield value
    else:
        for _ in range(times):
            yield value


async def range_source(start: int, stop: int, step: int = 1) -> AsyncIterator[int]:
    """
    Create a source that emits integers in a range.

    Args:
        start: Start value (inclusive)
        stop: Stop value (exclusive)
        step: Step between values

    Yields:
        Integers from start to stop

    Example:
        >>> async for i in range_source(0, 5):
        ...     print(i)
        0
        1
        2
        3
        4
    """
    for i in range(start, stop, step):
        yield i
