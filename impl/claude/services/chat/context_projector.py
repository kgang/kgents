"""
WorkingContextProjector: Functor from Session -> ContextWindow

The Working Context is a computed projection, not ground truth.
The Session maintains the complete turn history; this functor
renders it to fit the context window.

WorkingContext : Session -> ContextWindow

This functor applies:
1. Context strategy (sliding/summarize)
2. Token budget constraints
3. System prompt injection
4. Memory recall injection
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .config import ChatConfig, ContextStrategy
from .session import Message, Turn

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


@dataclass
class ContextWindow:
    """
    The rendered context window for LLM consumption.

    This is what gets sent to the LLM, including:
    - System prompt
    - Summary of older messages (if applicable)
    - Recent messages
    - Injected memories
    """

    messages: list[Message] = field(default_factory=list)
    total_tokens: int = 0
    summary: str | None = None
    injected_memories: list[str] = field(default_factory=list)

    @property
    def utilization(self) -> float:
        """Context utilization as a ratio."""
        return self.total_tokens / 8000  # Default window

    def render_for_llm(self) -> list[dict[str, str]]:
        """Render messages in LLM format."""
        return [{"role": m.role, "content": m.content} for m in self.messages]


class WorkingContextProjector:
    """
    Projects a session's turn history into a working context window.

    The projection is a functor:
        F: Session -> ContextWindow

    Properties:
    - Preserves message order
    - Respects token budget
    - Applies configured strategy
    - Injects system prompt and memories
    """

    def __init__(
        self,
        config: ChatConfig,
        summarizer: Any | None = None,
    ):
        """
        Initialize the projector.

        Args:
            config: Chat configuration (context window, strategy, etc.)
            summarizer: Optional LLM agent for summarization
        """
        self.config = config
        self.summarizer = summarizer

        # Cached summary of older turns
        self._cached_summary: str | None = None
        self._summarized_through_turn: int = 0

    def project(
        self,
        turns: list[Turn],
        system_prompt: str | None = None,
        injected_memories: list[str] | None = None,
    ) -> ContextWindow:
        """
        Project turn history to context window.

        This is the main entry point (synchronous).

        Args:
            turns: Complete turn history
            system_prompt: System prompt to inject
            injected_memories: Memories to inject

        Returns:
            Rendered ContextWindow
        """
        window = ContextWindow()

        # Add system prompt first
        if system_prompt:
            sys_msg = Message(role="system", content=system_prompt)
            window.messages.append(sys_msg)
            window.total_tokens += sys_msg.tokens

        # Inject memories into system prompt area
        if injected_memories:
            memory_content = "\n\n".join([
                "[Relevant Memory]",
                *injected_memories,
            ])
            mem_msg = Message(role="system", content=memory_content)
            window.messages.append(mem_msg)
            window.total_tokens += mem_msg.tokens
            window.injected_memories = injected_memories

        # Apply strategy to turn history
        match self.config.context_strategy:
            case ContextStrategy.SLIDING:
                self._apply_sliding(window, turns)
            case ContextStrategy.SUMMARIZE:
                self._apply_summarize(window, turns)
            case ContextStrategy.FORGET:
                self._apply_forget(window, turns)
            case ContextStrategy.HYBRID:
                self._apply_hybrid(window, turns)

        return window

    async def project_async(
        self,
        turns: list[Turn],
        system_prompt: str | None = None,
        injected_memories: list[str] | None = None,
    ) -> ContextWindow:
        """
        Project turn history to context window (async version).

        Use this when summarization may be needed.
        """
        window = ContextWindow()

        # Add system prompt
        if system_prompt:
            sys_msg = Message(role="system", content=system_prompt)
            window.messages.append(sys_msg)
            window.total_tokens += sys_msg.tokens

        # Inject memories
        if injected_memories:
            memory_content = "\n\n".join([
                "[Relevant Memory]",
                *injected_memories,
            ])
            mem_msg = Message(role="system", content=memory_content)
            window.messages.append(mem_msg)
            window.total_tokens += mem_msg.tokens
            window.injected_memories = injected_memories

        # Apply strategy (async for summarization)
        match self.config.context_strategy:
            case ContextStrategy.SLIDING:
                self._apply_sliding(window, turns)
            case ContextStrategy.SUMMARIZE:
                await self._apply_summarize_async(window, turns)
            case ContextStrategy.FORGET:
                self._apply_forget(window, turns)
            case ContextStrategy.HYBRID:
                await self._apply_hybrid_async(window, turns)

        return window

    def _apply_sliding(
        self,
        window: ContextWindow,
        turns: list[Turn],
    ) -> None:
        """
        Apply sliding window strategy.

        Simply includes most recent messages that fit in the window.
        """
        budget = self.config.context_window - window.total_tokens
        messages: list[Message] = []

        # Walk backwards through turns, adding until budget exceeded
        for turn in reversed(turns):
            turn_tokens = turn.tokens_in + turn.tokens_out

            if turn_tokens > budget:
                break

            # Add messages (prepend since we're going backwards)
            messages.insert(0, turn.assistant_response)
            messages.insert(0, turn.user_message)
            budget -= turn_tokens

        window.messages.extend(messages)
        window.total_tokens += sum(m.tokens for m in messages)

    def _apply_summarize(
        self,
        window: ContextWindow,
        turns: list[Turn],
    ) -> None:
        """
        Apply summarization strategy (sync version).

        Uses cached summary if available, otherwise falls back to sliding.
        """
        # Check if we need to summarize
        threshold_tokens = int(self.config.context_window * self.config.summarization_threshold)
        all_tokens = sum(t.tokens_in + t.tokens_out for t in turns)

        if all_tokens <= threshold_tokens:
            # No need to summarize, use all messages
            self._apply_sliding(window, turns)
            return

        # Use cached summary if available
        if self._cached_summary:
            summary_msg = Message(
                role="system",
                content=f"[Previous conversation summary]\n{self._cached_summary}",
            )
            window.messages.append(summary_msg)
            window.total_tokens += summary_msg.tokens
            window.summary = self._cached_summary

            # Add recent turns after summary
            recent_turns = turns[self._summarized_through_turn:]
            self._apply_sliding(window, recent_turns)
        else:
            # Fall back to sliding if no summarizer
            self._apply_sliding(window, turns)

    async def _apply_summarize_async(
        self,
        window: ContextWindow,
        turns: list[Turn],
    ) -> None:
        """
        Apply summarization strategy (async version).

        Generates new summary if needed.
        """
        threshold_tokens = int(self.config.context_window * self.config.summarization_threshold)
        all_tokens = sum(t.tokens_in + t.tokens_out for t in turns)

        if all_tokens <= threshold_tokens:
            self._apply_sliding(window, turns)
            return

        # Determine how many turns to summarize
        # Keep the most recent 1/3, summarize the rest
        keep_count = max(1, len(turns) // 3)
        to_summarize = turns[:-keep_count]
        to_keep = turns[-keep_count:]

        # Generate summary if we have a summarizer and need to
        if self.summarizer and len(to_summarize) > self._summarized_through_turn:
            summary = await self._generate_summary(to_summarize)
            self._cached_summary = summary
            self._summarized_through_turn = len(to_summarize)

        # Add summary
        if self._cached_summary:
            summary_msg = Message(
                role="system",
                content=f"[Previous conversation summary]\n{self._cached_summary}",
            )
            window.messages.append(summary_msg)
            window.total_tokens += summary_msg.tokens
            window.summary = self._cached_summary

        # Add recent turns
        for turn in to_keep:
            window.messages.append(turn.user_message)
            window.messages.append(turn.assistant_response)
            window.total_tokens += turn.tokens_in + turn.tokens_out

    def _apply_forget(
        self,
        window: ContextWindow,
        turns: list[Turn],
    ) -> None:
        """
        Apply forget strategy.

        Hard truncation - only keeps messages that fit, no memory.
        """
        self._apply_sliding(window, turns)

    def _apply_hybrid(
        self,
        window: ContextWindow,
        turns: list[Turn],
    ) -> None:
        """
        Apply hybrid strategy (sync version).

        Sliding + periodic summary.
        """
        # Same as summarize in sync mode
        self._apply_summarize(window, turns)

    async def _apply_hybrid_async(
        self,
        window: ContextWindow,
        turns: list[Turn],
    ) -> None:
        """
        Apply hybrid strategy (async version).
        """
        await self._apply_summarize_async(window, turns)

    async def _generate_summary(self, turns: list[Turn]) -> str:
        """
        Generate a summary of turns using the summarizer.

        Args:
            turns: Turns to summarize

        Returns:
            Summary text
        """
        if not self.summarizer:
            return self._generate_simple_summary(turns)

        # Build messages for summarization
        messages = []
        for turn in turns:
            messages.append(turn.user_message)
            messages.append(turn.assistant_response)

        try:
            summary = await self.summarizer.invoke(messages)
            return str(summary)
        except Exception:
            return self._generate_simple_summary(turns)

    def _generate_simple_summary(self, turns: list[Turn]) -> str:
        """Generate a simple summary without LLM."""
        if not turns:
            return ""

        # Extract key points
        topics = set()
        for turn in turns:
            # Simple extraction: first 50 chars of each user message
            content = turn.user_message.content[:50]
            if content:
                topics.add(content.strip())

        summary_parts = [
            f"Previous conversation covered {len(turns)} turns.",
            "Topics discussed: " + ", ".join(list(topics)[:5]) + "...",
        ]
        return "\n".join(summary_parts)

    def reset(self) -> None:
        """Reset the projector state."""
        self._cached_summary = None
        self._summarized_through_turn = 0


__all__ = [
    "ContextWindow",
    "WorkingContextProjector",
]
