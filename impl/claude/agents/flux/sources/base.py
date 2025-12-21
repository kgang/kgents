"""
Base protocols and types for flux sources.

A Source is anything that can produce an asynchronous stream of values.
Sources should be EVENT-DRIVEN whenever possible.

Teaching:
    gotcha: Sources should be EVENT-DRIVEN, not timer-driven. If your __anext__()
            uses asyncio.sleep() in a loop to poll, you're doing it wrong. Await
            the actual event (file watcher, message queue, etc.) instead.
            (Evidence: Structural - module docstring emphasizes event-driven)

    gotcha: close() is NOT async. If your source needs async cleanup, do it in
            __aexit__ (the async context manager exit) instead.
            (Evidence: Structural - close signature is sync)
"""

from typing import AsyncIterator, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


@runtime_checkable
class SourceProtocol(Protocol[T_co]):
    """
    Protocol for objects that can produce async streams.

    Any object implementing subscribe() → AsyncIterator[T] can be
    used as a flux source via from_events().
    """

    def subscribe(self) -> AsyncIterator[T_co]:
        """
        Subscribe to events from this source.

        Returns an async iterator that yields events as they occur.
        The iterator should complete when the source is exhausted
        or when the subscription is cancelled.
        """
        ...


class Source(AsyncIterator[T]):
    """
    Base class for custom flux sources.

    Subclass this to create custom event sources. The key method
    to implement is __anext__(), which should yield events as they
    occur without polling.

    Example:
        class FileWatcher(Source[FileEvent]):
            def __init__(self, path: Path):
                self._path = path
                self._watcher = None

            async def __anext__(self) -> FileEvent:
                if self._watcher is None:
                    self._watcher = await create_watcher(self._path)
                return await self._watcher.next_event()

            def close(self) -> None:
                if self._watcher:
                    self._watcher.close()
    """

    def __aiter__(self) -> AsyncIterator[T]:
        """Return self as the async iterator."""
        return self

    async def __anext__(self) -> T:
        """
        Get the next event from the source.

        Must be overridden by subclasses.

        Returns:
            The next event

        Raises:
            StopAsyncIteration: When the source is exhausted
        """
        raise NotImplementedError("Subclasses must implement __anext__")

    def close(self) -> None:
        """
        Close the source and release any resources.

        Override this if your source holds resources that need cleanup.
        """
        pass

    async def __aenter__(self) -> "Source[T]":
        """Context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Context manager exit - closes the source."""
        self.close()
