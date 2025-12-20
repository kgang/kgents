"""
ConversationWindow: Bounded history with context strategies.

CLI v7 Phase 2: Deep Conversation

This implements Pattern #8 (Bounded History Trace) from crown-jewel-patterns.md:
- Fixed-size window for context
- Strategies: sliding, summarize, hybrid
- Threshold-based summarization triggers

The window is the "working memory" of a conversation:
- Full history stored in ChatSession._turns (ground truth)
- Window provides the context for LLM calls (working memory)

Usage:
    window = ConversationWindow(max_turns=35, strategy=ContextStrategy.SUMMARIZE)
    window.add_turn("Hello", "Hi there!")
    context = window.get_context_messages()
    # Context has at most 35 recent turns + optional summary
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from services.chat.config import ContextStrategy

logger = logging.getLogger(__name__)


# =============================================================================
# Context Message: The unit of window storage
# =============================================================================


@dataclass
class ContextMessage:
    """
    A message in the conversation window.

    Lighter than chat.session.Message - focused on context, not metrics.
    """

    role: str  # "system", "user", "assistant", "summary"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tokens: int = 0  # Estimated tokens (4 chars ~= 1 token)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.tokens == 0:
            self.tokens = len(self.content) // 4

    def to_dict(self) -> dict[str, Any]:
        """Serialize for LLM context."""
        return {
            "role": self.role,
            "content": self.content,
        }

    def to_llm_format(self) -> dict[str, str]:
        """Format for LLM API (Anthropic/OpenAI compatible)."""
        return {
            "role": self.role,
            "content": self.content,
        }


# =============================================================================
# Window Snapshot: Immutable view of window state
# =============================================================================


@dataclass(frozen=True)
class WindowSnapshot:
    """
    Immutable snapshot of window state.

    Used for:
    - Debugging/observability
    - Testing assertions
    - Persistence checkpoints
    """

    turn_count: int
    total_tokens: int
    summary_tokens: int
    utilization: float  # 0.0 to 1.0
    strategy: str
    has_summary: bool
    oldest_turn_age_seconds: float
    newest_turn_age_seconds: float


@dataclass(frozen=True)
class ContextSegment:
    """
    A segment of the context window for visualization.

    Used by Teaching Mode to show how context is being used.
    """

    name: str  # "System", "Summary", "Working", "Available"
    tokens: int
    color: str  # CSS class or hex color
    description: str


@dataclass(frozen=True)
class ContextBreakdown:
    """
    Full breakdown of context window composition.

    Teaching mode visualization: shows users how context is managed.
    """

    segments: list[ContextSegment]
    total_tokens: int
    context_window: int
    utilization: float  # 0.0 to 1.0
    strategy: str
    has_summary: bool


# =============================================================================
# ConversationWindow: The bounded history implementation
# =============================================================================


class ConversationWindow:
    """
    Bounded conversation history with context strategies.

    Pattern #8: Bounded History Trace
    - Fixed-size window (configurable max_turns)
    - Multiple strategies for overflow handling
    - Summarization threshold for proactive compression

    Strategies:
    - SLIDING: Drop oldest messages (lossy but fast)
    - SUMMARIZE: Compress old messages into summary (requires LLM)
    - HYBRID: Sliding + periodic summarization
    - FORGET: Hard truncate with no memory (for stateless contexts)
    """

    def __init__(
        self,
        max_turns: int = 35,
        strategy: str = "summarize",
        context_window_tokens: int = 8000,
        summarization_threshold: float = 0.8,
        summarizer: Callable[[list[ContextMessage]], str] | None = None,
    ):
        """
        Initialize conversation window.

        Args:
            max_turns: Maximum number of turns to keep in working memory
            strategy: Context strategy ("sliding", "summarize", "hybrid", "forget")
            context_window_tokens: Maximum tokens for context (used for threshold)
            summarization_threshold: Trigger summarization at this utilization (0.0-1.0)
            summarizer: Async function to summarize messages (injected)
        """
        self.max_turns = max_turns
        self.strategy = strategy.lower()
        self.context_window_tokens = context_window_tokens
        self.summarization_threshold = summarization_threshold
        self._summarizer = summarizer

        # Working memory: bounded list of turns
        self._turns: list[tuple[ContextMessage, ContextMessage]] = []

        # Summary: compressed history from evicted turns
        self._summary: str | None = None
        self._summary_tokens: int = 0
        self._summarized_turn_count: int = 0

        # System prompt (optional, prepended to context)
        self._system_prompt: str | None = None

        # Timestamps
        self._created_at = datetime.now()
        self._last_updated = datetime.now()

    # === Properties ===

    @property
    def turn_count(self) -> int:
        """Number of turns in working memory."""
        return len(self._turns)

    @property
    def total_turn_count(self) -> int:
        """Total turns including summarized history."""
        return self._summarized_turn_count + len(self._turns)

    @property
    def has_summary(self) -> bool:
        """Whether a summary exists."""
        return self._summary is not None

    @property
    def total_tokens(self) -> int:
        """Total tokens in working memory (including summary)."""
        turn_tokens = sum(user.tokens + assistant.tokens for user, assistant in self._turns)
        return turn_tokens + self._summary_tokens

    @property
    def utilization(self) -> float:
        """Context utilization as percentage (0.0-1.0)."""
        return min(1.0, self.total_tokens / self.context_window_tokens)

    @property
    def is_at_capacity(self) -> bool:
        """Whether window is at max turns."""
        return len(self._turns) >= self.max_turns

    @property
    def needs_summarization(self) -> bool:
        """Whether summarization should be triggered."""
        return (
            self.strategy in ("summarize", "hybrid")
            and self.utilization >= self.summarization_threshold
            and self._summarizer is not None
        )

    # === Core Operations ===

    def add_turn(
        self,
        user_message: str,
        assistant_response: str,
        *,
        user_metadata: dict[str, Any] | None = None,
        assistant_metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add a conversation turn to the window.

        If at capacity, applies the configured strategy:
        - SLIDING/FORGET: Evicts oldest turn
        - SUMMARIZE/HYBRID: Triggers summarization before eviction

        Args:
            user_message: The user's message content
            assistant_response: The assistant's response content
            user_metadata: Optional metadata for user message
            assistant_metadata: Optional metadata for assistant message
        """
        user_msg = ContextMessage(
            role="user",
            content=user_message,
            metadata=user_metadata or {},
        )
        assistant_msg = ContextMessage(
            role="assistant",
            content=assistant_response,
            metadata=assistant_metadata or {},
        )

        # Check capacity
        if self.is_at_capacity:
            self._handle_overflow()

        # Add turn
        self._turns.append((user_msg, assistant_msg))
        self._last_updated = datetime.now()

        logger.debug(
            f"Window: added turn {self.turn_count}/{self.max_turns}, "
            f"tokens={self.total_tokens}, utilization={self.utilization:.1%}"
        )

    def _handle_overflow(self) -> None:
        """Handle window overflow based on strategy."""
        if self.strategy == "forget":
            # Hard drop, no memory
            self._turns.pop(0)
            return

        if self.strategy == "sliding":
            # Drop oldest, no summarization
            evicted = self._turns.pop(0)
            self._summarized_turn_count += 1
            logger.debug(f"Sliding: evicted turn, total={self.total_turn_count}")
            return

        if self.strategy in ("summarize", "hybrid"):
            # Summarize if we have a summarizer
            if self._summarizer is not None and len(self._turns) >= 2:
                # Summarize oldest half
                half = len(self._turns) // 2
                to_summarize = self._turns[:half]
                self._turns = self._turns[half:]

                # Flatten for summarization
                messages = []
                for user_msg, asst_msg in to_summarize:
                    messages.extend([user_msg, asst_msg])

                try:
                    new_summary = self._summarizer(messages)
                    if self._summary:
                        # Merge with existing summary
                        self._summary = f"{self._summary}\n\n{new_summary}"
                    else:
                        self._summary = new_summary
                    self._summary_tokens = len(self._summary) // 4
                    self._summarized_turn_count += half
                    logger.info(f"Summarized {half} turns, summary={self._summary_tokens} tokens")
                except Exception as e:
                    # Fallback to sliding on summarization failure
                    logger.warning(f"Summarization failed, falling back to sliding: {e}")
                    self._turns.pop(0)
                    self._summarized_turn_count += 1
            else:
                # No summarizer, fall back to sliding
                self._turns.pop(0)
                self._summarized_turn_count += 1

    def set_summarizer(self, summarizer: Callable[[list[ContextMessage]], str]) -> None:
        """
        Inject the summarizer function.

        The summarizer takes a list of messages and returns a summary string.
        This is injected to avoid coupling to a specific LLM client.

        Args:
            summarizer: Function that summarizes messages
        """
        self._summarizer = summarizer

    def set_system_prompt(self, prompt: str | None) -> None:
        """Set the system prompt (prepended to context)."""
        self._system_prompt = prompt

    # === Context Retrieval ===

    def get_context_messages(self) -> list[ContextMessage]:
        """
        Get messages for LLM context.

        Returns messages in order:
        1. System prompt (if set)
        2. Summary (if exists)
        3. Working memory turns (user/assistant pairs)

        Returns:
            List of ContextMessage objects ready for LLM
        """
        messages: list[ContextMessage] = []

        # 1. System prompt
        if self._system_prompt:
            messages.append(ContextMessage(role="system", content=self._system_prompt))

        # 2. Summary as system context
        if self._summary:
            messages.append(
                ContextMessage(
                    role="system",
                    content=f"## Conversation Summary\n\n{self._summary}",
                    metadata={"type": "summary"},
                )
            )

        # 3. Working memory
        for user_msg, assistant_msg in self._turns:
            messages.append(user_msg)
            messages.append(assistant_msg)

        return messages

    def get_context_for_llm(self) -> list[dict[str, str]]:
        """
        Get context in LLM API format.

        Returns:
            List of dicts with 'role' and 'content' keys
        """
        return [msg.to_llm_format() for msg in self.get_context_messages()]

    def get_recent_turns(self, limit: int | None = None) -> list[tuple[str, str]]:
        """
        Get recent turns as (user, assistant) tuples.

        Args:
            limit: Maximum turns to return (None = all)

        Returns:
            List of (user_message, assistant_response) tuples
        """
        turns = self._turns[-limit:] if limit else self._turns
        return [(u.content, a.content) for u, a in turns]

    # === State Management ===

    def snapshot(self) -> WindowSnapshot:
        """
        Create immutable snapshot of window state.

        Returns:
            WindowSnapshot for observability/testing
        """
        oldest_age = 0.0
        newest_age = 0.0
        now = datetime.now()

        if self._turns:
            oldest_age = (now - self._turns[0][0].timestamp).total_seconds()
            newest_age = (now - self._turns[-1][1].timestamp).total_seconds()

        return WindowSnapshot(
            turn_count=self.turn_count,
            total_tokens=self.total_tokens,
            summary_tokens=self._summary_tokens,
            utilization=self.utilization,
            strategy=self.strategy,
            has_summary=self.has_summary,
            oldest_turn_age_seconds=oldest_age,
            newest_turn_age_seconds=newest_age,
        )

    def get_context_breakdown(self) -> ContextBreakdown:
        """
        Get breakdown of context window composition.

        Teaching Mode: Shows users how the context window is being used.
        Returns segments for: System prompt, Summary, Working memory, Available.

        Returns:
            ContextBreakdown with segments and utilization info
        """
        segments: list[ContextSegment] = []

        # 1. System prompt tokens
        system_tokens = 0
        if self._system_prompt:
            system_tokens = len(self._system_prompt) // 4
            segments.append(
                ContextSegment(
                    name="System",
                    tokens=system_tokens,
                    color="bg-violet-500",
                    description="System prompt and personality",
                )
            )

        # 2. Summary tokens (compressed history)
        if self._summary_tokens > 0:
            segments.append(
                ContextSegment(
                    name="Summary",
                    tokens=self._summary_tokens,
                    color="bg-blue-500",
                    description="Compressed conversation history",
                )
            )

        # 3. Working memory (recent turns)
        working_tokens = sum(user.tokens + assistant.tokens for user, assistant in self._turns)
        if working_tokens > 0:
            segments.append(
                ContextSegment(
                    name="Working",
                    tokens=working_tokens,
                    color="bg-cyan-500",
                    description=f"Recent {len(self._turns)} turns (full detail)",
                )
            )

        # 4. Available headroom
        used_tokens = system_tokens + self._summary_tokens + working_tokens
        available_tokens = max(0, self.context_window_tokens - used_tokens)
        segments.append(
            ContextSegment(
                name="Available",
                tokens=available_tokens,
                color="bg-gray-700",
                description="Remaining context space",
            )
        )

        return ContextBreakdown(
            segments=segments,
            total_tokens=used_tokens,
            context_window=self.context_window_tokens,
            utilization=self.utilization,
            strategy=self.strategy,
            has_summary=self.has_summary,
        )

    def reset(self) -> None:
        """Clear the window (fresh start)."""
        self._turns.clear()
        self._summary = None
        self._summary_tokens = 0
        self._summarized_turn_count = 0
        self._last_updated = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize window state.

        Used for persistence/debugging.
        """
        return {
            "max_turns": self.max_turns,
            "strategy": self.strategy,
            "turn_count": self.turn_count,
            "total_turn_count": self.total_turn_count,
            "total_tokens": self.total_tokens,
            "utilization": self.utilization,
            "has_summary": self.has_summary,
            "summary_tokens": self._summary_tokens,
            "turns": [
                {
                    "user": u.to_dict(),
                    "assistant": a.to_dict(),
                }
                for u, a in self._turns
            ],
            "summary": self._summary,
            "created_at": self._created_at.isoformat(),
            "last_updated": self._last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationWindow:
        """
        Deserialize window state.

        Args:
            data: Dictionary from to_dict()

        Returns:
            Reconstructed ConversationWindow
        """
        window = cls(
            max_turns=data.get("max_turns", 35),
            strategy=data.get("strategy", "summarize"),
        )

        # Restore turns
        for turn_data in data.get("turns", []):
            user_data = turn_data["user"]
            asst_data = turn_data["assistant"]
            window._turns.append(
                (
                    ContextMessage(
                        role=user_data["role"],
                        content=user_data["content"],
                    ),
                    ContextMessage(
                        role=asst_data["role"],
                        content=asst_data["content"],
                    ),
                )
            )

        # Restore summary
        window._summary = data.get("summary")
        window._summary_tokens = data.get("summary_tokens", 0)
        window._summarized_turn_count = data.get("total_turn_count", 0) - len(window._turns)

        return window


# =============================================================================
# Factory Functions
# =============================================================================


def create_window_from_config(
    config: "ContextStrategy",
    max_turns: int = 35,
    context_window_tokens: int = 8000,
) -> ConversationWindow:
    """
    Create a ConversationWindow from ChatConfig strategy.

    Args:
        config: ContextStrategy enum from chat config
        max_turns: Maximum turns
        context_window_tokens: Context window size

    Returns:
        Configured ConversationWindow
    """
    # Import here to avoid circular dependency
    from services.chat.config import ContextStrategy

    strategy_map = {
        ContextStrategy.SLIDING: "sliding",
        ContextStrategy.SUMMARIZE: "summarize",
        ContextStrategy.HYBRID: "hybrid",
        ContextStrategy.FORGET: "forget",
    }

    return ConversationWindow(
        max_turns=max_turns,
        strategy=strategy_map.get(config, "summarize"),
        context_window_tokens=context_window_tokens,
    )


__all__ = [
    "ContextMessage",
    "WindowSnapshot",
    "ContextSegment",
    "ContextBreakdown",
    "ConversationWindow",
    "create_window_from_config",
]
