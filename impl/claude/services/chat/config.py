"""
Chat Configuration

Dataclasses for chat session configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class ContextStrategy(Enum):
    """Strategy for managing context window overflow."""

    SLIDING = "sliding"  # Drop oldest messages
    SUMMARIZE = "summarize"  # Compress via LLM
    FORGET = "forget"  # Hard truncate, no memory
    HYBRID = "hybrid"  # Sliding + periodic summary


class InterruptionStrategy(Enum):
    """How to handle user interruption during streaming."""

    COMPLETE = "complete"  # Finish current response first
    ABORT = "abort"  # Cancel and process new message
    MERGE = "merge"  # Inject as perturbation


@dataclass
class ChatConfig:
    """
    Chat session configuration.

    This is the high-level configuration for chat sessions.
    Maps to F-gent ChatConfig for underlying flow.
    """

    # Context management
    context_window: int = 8000
    context_strategy: ContextStrategy = ContextStrategy.SUMMARIZE
    summarization_threshold: float = 0.8

    # Turn limits
    turn_timeout: float = 60.0
    max_turns: int | None = None

    # System prompt
    system_prompt: str | None = None
    system_prompt_position: str = "prepend"  # "prepend" or "inject"

    # Dynamic prompt injection
    system_prompt_factory: Callable[..., str] | None = None

    # Interruption handling
    interruption_strategy: InterruptionStrategy = InterruptionStrategy.COMPLETE

    # Persistence
    persist_history: bool = True
    memory_key: str | None = None  # Auto-derived from node path if None

    # Memory injection
    inject_memories: bool = True
    memory_recall_limit: int = 5

    # Entropy budget (conversation budget)
    entropy_budget: float = 1.0
    entropy_decay_per_turn: float = 0.02

    # Model configuration
    model: str | None = None  # If None, uses default from LLM agent
    temperature: float = 0.7
    max_tokens: int = 2048

    # Streaming
    streaming_enabled: bool = True

    def to_fgent_config(self) -> Any:
        """Convert to F-gent ChatConfig."""
        try:
            from agents.f.config import ChatConfig as FgentChatConfig

            return FgentChatConfig(
                context_window=self.context_window,
                context_strategy=self.context_strategy.value,
                summarization_threshold=self.summarization_threshold,
                turn_timeout=self.turn_timeout,
                max_turns=self.max_turns,
                system_prompt=self.system_prompt,
                interruption_strategy=self.interruption_strategy.value,
            )
        except ImportError:
            # F-gent not available, return self
            return self


# Default configurations for different entity types
SOUL_CHAT_CONFIG = ChatConfig(
    context_window=16000,
    context_strategy=ContextStrategy.SUMMARIZE,
    entropy_budget=1.0,
    inject_memories=True,
    memory_recall_limit=5,
)

CITIZEN_CHAT_CONFIG = ChatConfig(
    context_window=8000,
    context_strategy=ContextStrategy.SLIDING,
    entropy_budget=0.5,
    inject_memories=True,
    memory_recall_limit=3,
)

AGENT_CHAT_CONFIG = ChatConfig(
    context_window=4000,
    context_strategy=ContextStrategy.SLIDING,
    entropy_budget=0.3,
    inject_memories=False,
)


__all__ = [
    "ChatConfig",
    "ContextStrategy",
    "InterruptionStrategy",
    "SOUL_CHAT_CONFIG",
    "CITIZEN_CHAT_CONFIG",
    "AGENT_CHAT_CONFIG",
]
