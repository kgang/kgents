"""
Periodic source (timer-based).

NOTE: This is for when you ACTUALLY need a timer.
It's not the default pattern — event-driven is the default.

Use periodic sources for:
- Heartbeats / keep-alive signals
- Scheduled polling of external systems
- Time-based batching windows
- Animation / UI refresh loops
"""

import asyncio
import time
from typing import AsyncIterator, TypeVar

T = TypeVar("T")


async def periodic(interval: float) -> AsyncIterator[float]:
    """
    Emit timestamps at regular intervals.

    USE SPARINGLY. This is timer-driven (polling).
    Prefer event-driven sources when possible.

    Args:
        interval: Seconds between emissions

    Yields:
        Unix timestamps at each interval

    Example:
        >>> async for ts in periodic(1.0):
        ...     print(f"Tick at {ts}")
        ...     if should_stop():
        ...         break
    """
    while True:
        yield time.time()
        await asyncio.sleep(interval)


async def countdown(count: int, interval: float = 1.0) -> AsyncIterator[int]:
    """
    Emit countdown from count to 0.

    Finite source for bounded flux.

    Args:
        count: Starting count (inclusive)
        interval: Seconds between emissions

    Yields:
        Integers from count down to 0

    Example:
        >>> async for n in countdown(5):
        ...     print(f"{n}...")
        5...
        4...
        3...
        2...
        1...
        0...
    """
    for n in range(count, -1, -1):
        yield n
        if n > 0:
            await asyncio.sleep(interval)


async def tick(
    interval: float,
    count: int | None = None,
) -> AsyncIterator[int]:
    """
    Emit sequential tick numbers at regular intervals.

    Similar to periodic() but emits tick count instead of timestamp.
    Optionally limited to a specific number of ticks.

    Args:
        interval: Seconds between ticks
        count: Maximum number of ticks (None = infinite)

    Yields:
        Sequential integers starting from 0

    Example:
        >>> async for n in tick(0.5, count=3):
        ...     print(f"Tick {n}")
        Tick 0
        Tick 1
        Tick 2
    """
    n = 0
    while count is None or n < count:
        yield n
        n += 1
        if count is None or n < count:
            await asyncio.sleep(interval)


async def delayed(value: T, delay: float) -> AsyncIterator[T]:
    """
    Emit a single value after a delay.

    Args:
        value: Value to emit
        delay: Seconds to wait before emitting

    Yields:
        The value after the delay

    Example:
        >>> async for v in delayed("ready", 2.0):
        ...     print(v)  # Prints "ready" after 2 seconds
    """
    await asyncio.sleep(delay)
    yield value


async def timeout_source(duration: float) -> AsyncIterator[None]:
    """
    Create a source that emits nothing for a duration, then completes.

    Useful for creating timeout behaviors in pipelines.

    Args:
        duration: Seconds to wait before completing

    Yields:
        Nothing - just waits then completes

    Example:
        >>> # Use with merged() for timeout patterns
        >>> async for item in merged(data_source(), timeout_source(5.0)):
        ...     if item is not None:
        ...         process(item)
        ...     # If we get here with None, we timed out
    """
    await asyncio.sleep(duration)
    return
    yield  # Make this a generator (never reached)
