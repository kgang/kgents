"""
marimo Stream Adapter: Async generator to reactive cell.

Bridges projection streaming infrastructure with marimo's reactive model.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, TypeVar

if TYPE_CHECKING:
    import marimo as mo

T = TypeVar("T")


async def stream_to_marimo(
    source: AsyncIterator[T],
    render_fn: Callable[[T], Any] | None = None,
    on_complete: Callable[[], None] | None = None,
    on_error: Callable[[Exception], None] | None = None,
) -> AsyncIterator[Any]:
    """
    Convert async stream to marimo-compatible async generator.

    This generator can be used with marimo's reactive cells to
    display streaming content.

    Args:
        source: Async iterator producing stream chunks.
        render_fn: Optional function to render each chunk.
                   If None, chunks are passed through as-is.
        on_complete: Callback when stream completes.
        on_error: Callback on stream error.

    Yields:
        Rendered chunks (or raw if no render_fn).

    Example:
        ```python
        import marimo as mo

        @mo.cell
        async def streaming_cell():
            async for chunk in stream_to_marimo(my_stream):
                yield mo.md(chunk)
        ```
    """
    import marimo as mo

    try:
        async for item in source:
            if render_fn:
                yield render_fn(item)
            else:
                yield item

        if on_complete:
            on_complete()

    except Exception as e:
        if on_error:
            on_error(e)
        else:
            yield mo.callout(
                mo.md(f"**Stream Error:** {e}"),
                kind="danger",
            )


class MarimoStreamState:
    """
    State container for marimo streaming.

    Tracks chunks, status, and provides marimo-friendly accessors.
    """

    def __init__(self) -> None:
        self._chunks: list[str] = []
        self._complete: bool = False
        self._error: Exception | None = None

    def append(self, chunk: str) -> None:
        """Append a chunk."""
        self._chunks.append(chunk)

    def mark_complete(self) -> None:
        """Mark stream as complete."""
        self._complete = True

    def set_error(self, error: Exception) -> None:
        """Set error state."""
        self._error = error

    @property
    def content(self) -> str:
        """Get accumulated content."""
        return "".join(self._chunks)

    @property
    def is_complete(self) -> bool:
        """Check if complete."""
        return self._complete

    @property
    def has_error(self) -> bool:
        """Check for error."""
        return self._error is not None

    @property
    def error(self) -> Exception | None:
        """Get error if any."""
        return self._error

    @property
    def chunk_count(self) -> int:
        """Get number of chunks received."""
        return len(self._chunks)

    def render(self) -> Any:
        """
        Render current state as marimo component.

        Returns:
            marimo component showing stream state.
        """
        import marimo as mo

        if self._error:
            return mo.callout(
                mo.md(f"**Stream Error:** {self._error}"),
                kind="danger",
            )

        content = self.content
        if not self._complete:
            # Add cursor indicator
            content += " ▋"

        result = mo.md(content)

        if self._complete:
            return mo.vstack(
                [
                    result,
                    mo.md("*Stream complete* ✓"),
                ]
            )

        return result


def create_stream_cell(
    source: AsyncIterator[str],
    variant: str = "text",
) -> Callable[[], Any]:
    """
    Create a marimo cell function for streaming content.

    Args:
        source: Async iterator producing string chunks.
        variant: Rendering variant (text, code, markdown).

    Returns:
        Async cell function for marimo.

    Example:
        ```python
        import marimo as mo

        # Create cell
        stream_cell = create_stream_cell(my_source, variant="markdown")

        # Use in notebook
        @mo.cell
        async def my_stream():
            return await stream_cell()
        ```
    """

    async def cell_fn() -> Any:
        import marimo as mo

        state = MarimoStreamState()

        async for chunk in source:
            state.append(chunk)
            # In real marimo, this would trigger reactive update
            yield state.render()

        state.mark_complete()
        yield state.render()

    return cell_fn
