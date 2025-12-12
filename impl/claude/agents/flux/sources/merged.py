"""
Stream combinators for flux sources.

These functions transform and combine async iterators,
enabling powerful stream processing patterns.
"""

import asyncio
from typing import Any, AsyncIterator, Awaitable, Callable, TypeVar, cast

T = TypeVar("T")
U = TypeVar("U")


async def merged(*sources: AsyncIterator[T]) -> AsyncIterator[T]:
    """
    Merge multiple sources into a single stream.

    Items are yielded as they arrive from any source.
    Order is not preserved between sources.

    Args:
        *sources: Async iterators to merge

    Yields:
        Items from all sources as they arrive

    Example:
        >>> async for item in merged(source_a, source_b, source_c):
        ...     # Items from any source, interleaved
        ...     process(item)
    """
    if not sources:
        return

    # Create tasks for getting next item from each source
    pending: dict[asyncio.Task[tuple[int, T]], int] = {}
    iterators = list(sources)
    exhausted: set[int] = set()

    async def get_next(index: int, it: AsyncIterator[T]) -> tuple[int, T]:
        """Get next item from iterator, returning (index, item)."""
        return (index, await it.__anext__())

    # Start initial tasks
    for i, it in enumerate(iterators):
        task = asyncio.create_task(get_next(i, it))
        pending[task] = i

    try:
        while pending:
            # Wait for any task to complete
            done, _ = await asyncio.wait(
                pending.keys(),
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in done:
                index = pending.pop(task)

                try:
                    idx, item = task.result()
                    yield item

                    # Start next task for this source
                    if idx not in exhausted:
                        new_task = asyncio.create_task(get_next(idx, iterators[idx]))
                        pending[new_task] = idx

                except StopAsyncIteration:
                    exhausted.add(index)

    finally:
        # Cancel any remaining tasks
        for task in pending:
            task.cancel()


async def filtered(
    source: AsyncIterator[T],
    predicate: Callable[[T], bool] | Callable[[T], Awaitable[bool]],
) -> AsyncIterator[T]:
    """
    Filter items from a source based on a predicate.

    Args:
        source: Source to filter
        predicate: Function returning True for items to keep
                  Can be sync or async

    Yields:
        Items for which predicate returns True

    Example:
        >>> async for n in filtered(numbers(), lambda x: x % 2 == 0):
        ...     print(n)  # Only even numbers
    """
    async for item in source:
        result = predicate(item)
        if asyncio.iscoroutine(result):
            result = await result
        if result:
            yield item


async def mapped(
    source: AsyncIterator[T],
    transform: Callable[[T], U] | Callable[[T], Awaitable[U]],
) -> AsyncIterator[U]:
    """
    Transform items from a source.

    Args:
        source: Source to transform
        transform: Function to apply to each item
                  Can be sync or async

    Yields:
        Transformed items

    Example:
        >>> async for s in mapped(numbers(), str):
        ...     print(s)  # Numbers as strings
    """
    async for item in source:
        result = transform(item)
        if asyncio.iscoroutine(result):
            yield cast(U, await result)
        else:
            yield cast(U, result)


async def batched(
    source: AsyncIterator[T],
    size: int,
    timeout: float | None = None,
) -> AsyncIterator[list[T]]:
    """
    Group items into batches.

    Emits a batch when either:
    - Batch reaches the specified size
    - Timeout elapses (if specified)
    - Source exhausts (emits final partial batch)

    Args:
        source: Source to batch
        size: Maximum batch size
        timeout: Optional timeout in seconds

    Yields:
        Lists of items

    Example:
        >>> async for batch in batched(items(), 10, timeout=1.0):
        ...     process_batch(batch)
    """
    batch: list[T] = []
    source_iter = source.__aiter__()
    source_done = False

    while not source_done:
        try:
            if timeout:
                item = await asyncio.wait_for(
                    source_iter.__anext__(),
                    timeout=timeout,
                )
            else:
                item = await source_iter.__anext__()

            batch.append(item)

            if len(batch) >= size:
                yield batch
                batch = []

        except asyncio.TimeoutError:
            # Timeout: emit current batch even if not full
            if batch:
                yield batch
                batch = []

        except StopAsyncIteration:
            source_done = True

    # Emit final batch
    if batch:
        yield batch


async def debounced(
    source: AsyncIterator[T],
    delay: float,
) -> AsyncIterator[T]:
    """
    Emit item only after delay with no new items.

    Useful for handling rapid bursts of events where you only
    care about the final value after activity settles.

    Args:
        source: Source to debounce
        delay: Seconds to wait for activity to settle

    Yields:
        Items after they've been stable for delay seconds

    Example:
        >>> # Only emit after 0.5s of no new input
        >>> async for value in debounced(keystrokes(), 0.5):
        ...     search(value)
    """
    source_iter = source.__aiter__()
    last_item: T | None = None
    has_item = False
    source_done = False

    while not source_done:
        try:
            item = await asyncio.wait_for(
                source_iter.__anext__(),
                timeout=delay,
            )
            last_item = item
            has_item = True

        except asyncio.TimeoutError:
            # No new item for delay seconds, emit the last one
            if has_item and last_item is not None:
                yield last_item
                has_item = False

        except StopAsyncIteration:
            source_done = True
            # Emit final item if we have one
            if has_item and last_item is not None:
                yield last_item


async def take(source: AsyncIterator[T], count: int) -> AsyncIterator[T]:
    """
    Take at most count items from source.

    Args:
        source: Source to limit
        count: Maximum items to take

    Yields:
        Up to count items from source

    Example:
        >>> async for item in take(infinite_source(), 10):
        ...     process(item)  # Only first 10 items
    """
    taken = 0
    async for item in source:
        if taken >= count:
            break
        yield item
        taken += 1


async def skip(source: AsyncIterator[T], count: int) -> AsyncIterator[T]:
    """
    Skip the first count items from source.

    Args:
        source: Source to skip from
        count: Number of items to skip

    Yields:
        Items after skipping count items

    Example:
        >>> async for item in skip(source(), 5):
        ...     process(item)  # Skips first 5 items
    """
    skipped = 0
    async for item in source:
        if skipped < count:
            skipped += 1
            continue
        yield item


async def take_while(
    source: AsyncIterator[T],
    predicate: Callable[[T], bool],
) -> AsyncIterator[T]:
    """
    Take items while predicate is True.

    Stops at first item where predicate returns False.

    Args:
        source: Source to take from
        predicate: Function returning True for items to keep

    Yields:
        Items until predicate returns False

    Example:
        >>> async for n in take_while(numbers(), lambda x: x < 10):
        ...     print(n)  # Stops when n >= 10
    """
    async for item in source:
        if not predicate(item):
            break
        yield item


async def skip_while(
    source: AsyncIterator[T],
    predicate: Callable[[T], bool],
) -> AsyncIterator[T]:
    """
    Skip items while predicate is True.

    Starts yielding at first item where predicate returns False.

    Args:
        source: Source to skip from
        predicate: Function returning True for items to skip

    Yields:
        Items starting when predicate returns False

    Example:
        >>> async for n in skip_while(numbers(), lambda x: x < 5):
        ...     print(n)  # Starts at first n >= 5
    """
    skipping = True
    async for item in source:
        if skipping:
            if predicate(item):
                continue
            skipping = False
        yield item


async def enumerate_source(
    source: AsyncIterator[T],
    start: int = 0,
) -> AsyncIterator[tuple[int, T]]:
    """
    Add index to each item.

    Args:
        source: Source to enumerate
        start: Starting index

    Yields:
        Tuples of (index, item)

    Example:
        >>> async for i, item in enumerate_source(items()):
        ...     print(f"{i}: {item}")
    """
    index = start
    async for item in source:
        yield (index, item)
        index += 1
