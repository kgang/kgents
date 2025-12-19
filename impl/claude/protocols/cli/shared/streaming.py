"""
StreamingHandler: Unified streaming infrastructure for CLI commands.

This extracts the streaming patterns from soul.py into a reusable handler.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncIterator

from .context import InvocationContext
from .output import OutputFormatter, format_dialogue_header

if TYPE_CHECKING:
    pass


@dataclass
class StreamResult:
    """Result of a streaming operation."""

    text: str
    tokens_used: int
    chunks_emitted: int
    cancelled: bool = False


class StreamingHandler:
    """
    Unified streaming handler for CLI commands.

    Supports:
    - Flux streaming (dialogue_flux)
    - Generic async iterators
    - Graceful cancellation
    """

    def __init__(self, ctx: InvocationContext):
        self.ctx = ctx
        self.output = OutputFormatter(ctx)

    async def stream_dialogue(
        self,
        soul: Any,
        mode: Any,
        prompt: str,
        budget: Any,
        show_header: bool = True,
    ) -> StreamResult:
        """
        Stream a dialogue response using soul.dialogue_flux().

        Args:
            soul: KgentSoul instance
            mode: DialogueMode
            prompt: User prompt
            budget: BudgetTier
            show_header: Whether to print the mode header

        Returns:
            StreamResult with final text and metadata
        """
        # Print header (unless pipe mode)
        if show_header and not self.ctx.pipe_mode and not self.ctx.json_mode:
            print(format_dialogue_header(mode.value))
            print()

        chunks: list[str] = []
        final_tokens = 0
        final_text = ""
        cancelled = False
        chunk_index = 0

        try:
            async for event in soul.dialogue_flux(prompt, mode=mode, budget=budget):
                if event.is_data:
                    chunk = event.value
                    chunks.append(chunk)
                    self.output.stream_chunk(chunk, chunk_index)
                    chunk_index += 1
                elif event.is_metadata:
                    final_tokens = event.value.tokens_used
                    final_text = event.value.text

        except (KeyboardInterrupt, asyncio.CancelledError):
            cancelled = True
            if not self.ctx.pipe_mode:
                print("\n\n[Interrupted]")

        # Finalize
        response = "".join(chunks) if chunks else final_text

        if self.ctx.pipe_mode:
            self.output.stream_metadata(
                {
                    "tokens_used": final_tokens,
                    "text": response,
                    "total_chunks": chunk_index,
                }
            )
        elif not self.ctx.json_mode:
            print()  # Newline after streaming content
            if final_tokens > 0:
                print(f"\n  [{final_tokens} tokens]")

        return StreamResult(
            text=response,
            tokens_used=final_tokens,
            chunks_emitted=chunk_index,
            cancelled=cancelled,
        )

    async def stream_iterator(
        self,
        iterator: AsyncIterator[str],
        on_metadata: dict[str, Any] | None = None,
    ) -> StreamResult:
        """
        Stream from a generic async iterator.

        Args:
            iterator: Async iterator yielding string chunks
            on_metadata: Optional metadata to emit on completion

        Returns:
            StreamResult with final text
        """
        chunks: list[str] = []
        cancelled = False
        chunk_index = 0

        try:
            async for chunk in iterator:
                chunks.append(chunk)
                self.output.stream_chunk(chunk, chunk_index)
                chunk_index += 1

        except (KeyboardInterrupt, asyncio.CancelledError):
            cancelled = True
            if not self.ctx.pipe_mode:
                print("\n\n[Interrupted]")

        response = "".join(chunks)

        if on_metadata:
            self.output.stream_metadata(on_metadata)

        return StreamResult(
            text=response,
            tokens_used=on_metadata.get("tokens_used", 0) if on_metadata else 0,
            chunks_emitted=chunk_index,
            cancelled=cancelled,
        )


async def invoke_with_retry(
    flux: Any,
    event: Any,
    max_retries: int = 2,
    timeout_seconds: float = 60.0,
) -> Any:
    """
    Invoke flux with timeout and retry logic.

    Args:
        flux: KgentFlux instance
        event: SoulEvent to process
        max_retries: Number of retries on failure
        timeout_seconds: Timeout per attempt

    Returns:
        Result event from flux.invoke()

    Raises:
        Exception: If all retries exhausted
    """
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return await asyncio.wait_for(
                flux.invoke(event),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            last_error = asyncio.TimeoutError(f"LLM response timeout after {timeout_seconds}s")
            if attempt == max_retries:
                raise last_error
            await asyncio.sleep(0.5 * (attempt + 1))
        except asyncio.CancelledError:
            raise
        except Exception as e:
            last_error = e
            if attempt == max_retries:
                raise
            await asyncio.sleep(0.5 * (attempt + 1))

    raise last_error or RuntimeError("Unexpected retry loop exit")
