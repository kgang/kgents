"""
Context window management for chat flows.

Provides strategies for managing finite context windows in chat conversations:
- SlidingContext: Drop oldest messages when full
- SummarizingContext: Compress old messages via LLM

See: spec/f-gents/chat.md
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing import AsyncIterator


@dataclass
class Message:
    """A single message in the conversation."""

    role: str  # "user", "assistant", or "system"
    content: str
    tokens: int = 0

    def __post_init__(self) -> None:
        """Calculate tokens if not provided."""
        if self.tokens == 0:
            self.tokens = count_tokens(self.content)


def count_tokens(text: str) -> int:
    """
    Estimate token count for text.

    This is a simple approximation. For production use, consider using
    tiktoken or the actual model's tokenizer.

    Uses the rough heuristic: 1 token ~= 4 characters
    """
    return len(text) // 4


class SummarizeAgent(Protocol):
    """Protocol for agents that can summarize messages."""

    async def invoke(self, messages: list[Message]) -> str:
        """Summarize a list of messages into compressed text."""
        ...


class SlidingContext:
    """
    Sliding window context manager.

    Drops oldest messages when window size is exceeded.
    Fast and simple, but loses early context.
    """

    def __init__(self, window_size: int):
        """
        Initialize sliding context.

        Args:
            window_size: Maximum tokens to keep in context
        """
        self.window_size = window_size
        self.messages: deque[Message] = deque()
        self.token_count = 0

    def add(self, message: Message) -> None:
        """
        Add a message to context.

        Drops oldest messages if window size is exceeded.

        Args:
            message: Message to add
        """
        self.messages.append(message)
        self.token_count += message.tokens

        # Drop oldest messages until we fit
        while self.token_count > self.window_size and len(self.messages) > 1:
            dropped = self.messages.popleft()
            self.token_count -= dropped.tokens

    def render(self) -> list[Message]:
        """
        Render context as list of messages.

        Returns:
            List of messages in context window
        """
        return list(self.messages)

    def compress(self) -> None:
        """No-op for sliding context (doesn't compress)."""
        pass

    def truncate_oldest(self, count: int = 1) -> None:
        """
        Truncate oldest N messages.

        Args:
            count: Number of messages to drop
        """
        for _ in range(min(count, len(self.messages))):
            if self.messages:
                dropped = self.messages.popleft()
                self.token_count -= dropped.tokens

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        self.token_count = 0


class SummarizingContext:
    """
    Summarizing context manager.

    Compresses old messages when threshold is reached.
    Preserves essence of conversation, costs tokens to summarize.
    """

    def __init__(
        self,
        window_size: int,
        threshold: float = 0.8,
        summarizer: SummarizeAgent | None = None,
    ):
        """
        Initialize summarizing context.

        Args:
            window_size: Maximum tokens to keep in context
            threshold: Trigger summarization at N% of window_size (0.0-1.0)
            summarizer: Agent that can summarize messages
        """
        self.window_size = window_size
        self.threshold = threshold
        self.summarizer = summarizer
        self.summary: str | None = None
        self.recent_messages: list[Message] = []

    def add(self, message: Message) -> None:
        """
        Add a message to context (sync version).

        For async operations (including summarization), use add_async.

        Args:
            message: Message to add
        """
        self.recent_messages.append(message)

    async def add_async(self, message: Message) -> None:
        """
        Add a message to context.

        Triggers compression if threshold is exceeded.

        Args:
            message: Message to add
        """
        self.recent_messages.append(message)
        current_tokens = self._count_tokens()

        if current_tokens > self.window_size * self.threshold:
            await self._compress()

    def _count_tokens(self) -> int:
        """Count total tokens in recent messages and summary."""
        recent_tokens = sum(m.tokens for m in self.recent_messages)
        summary_tokens = count_tokens(self.summary) if self.summary else 0
        return recent_tokens + summary_tokens

    async def _compress(self) -> None:
        """
        Compress old messages via summarization.

        Keeps the most recent 1/3 of messages, summarizes the rest.
        """
        if not self.summarizer:
            # Fallback to truncation if no summarizer
            self.truncate_oldest(len(self.recent_messages) // 2)
            return

        # Keep most recent N messages
        keep_count = max(1, len(self.recent_messages) // 3)
        to_summarize = self.recent_messages[:-keep_count]
        to_keep = self.recent_messages[-keep_count:]

        if not to_summarize:
            return

        # Generate summary
        new_summary = await self.summarizer.invoke(to_summarize)

        # Combine with existing summary
        if self.summary:
            self.summary = f"{self.summary}\n\n{new_summary}"
        else:
            self.summary = new_summary

        self.recent_messages = to_keep

    def render(self) -> list[Message]:
        """
        Render context as list of messages.

        If summary exists, prepends it as a system message.

        Returns:
            List of messages including summary
        """
        messages = []

        if self.summary:
            messages.append(
                Message(
                    role="system",
                    content=f"[Previous conversation summary]\n{self.summary}",
                    tokens=count_tokens(self.summary),
                )
            )

        messages.extend(self.recent_messages)
        return messages

    async def compress(self) -> None:
        """Manually trigger compression."""
        await self._compress()

    def truncate_oldest(self, count: int = 1) -> None:
        """
        Truncate oldest N messages.

        Args:
            count: Number of messages to drop
        """
        to_drop = min(count, len(self.recent_messages))
        self.recent_messages = self.recent_messages[to_drop:]

    def clear(self) -> None:
        """Clear all messages and summary."""
        self.recent_messages.clear()
        self.summary = None


__all__ = [
    "Message",
    "count_tokens",
    "SlidingContext",
    "SummarizingContext",
    "SummarizeAgent",
]
