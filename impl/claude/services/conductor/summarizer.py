"""
Summarizer: LLM-powered conversation summarization.

CLI v7 Phase 2: Deep Conversation

The Summarizer compresses conversation history when context grows too large.
It integrates with Morpheus for LLM calls.

Features:
- Configurable summarization prompts
- Token-aware compression (aim for 1/4 to 1/3 of original)
- Preserves key information (entities, decisions, action items)
- Circadian modulation (Pattern #11): more aggressive summarization at night

Usage:
    summarizer = Summarizer(morpheus)
    summary = await summarizer.summarize(messages)
    # Returns compressed summary string

Or with sync wrapper for ConversationWindow:
    window.set_summarizer(summarizer.summarize_sync)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from services.morpheus.persistence import MorpheusPersistence

    from .window import ContextMessage

logger = logging.getLogger(__name__)


# =============================================================================
# Summarization Prompts
# =============================================================================

DEFAULT_SUMMARIZE_PROMPT = """You are summarizing a conversation for context compression.

RULES:
1. Preserve key information: names, decisions, action items, specific facts
2. Use bullet points for clarity
3. Keep the summary under {target_tokens} tokens (about {target_words} words)
4. Focus on what matters for continuing the conversation
5. Omit pleasantries and conversational filler

CONVERSATION TO SUMMARIZE:
{conversation}

Write a concise summary:"""

AGGRESSIVE_SUMMARIZE_PROMPT = """Compress this conversation to essential points only.

Keep: key decisions, names, numbers, action items
Drop: everything else

{conversation}

Summary (max 3 sentences):"""


# =============================================================================
# Summarization Result
# =============================================================================


@dataclass
class SummarizationResult:
    """Result of a summarization operation."""

    summary: str
    original_tokens: int
    summary_tokens: int
    compression_ratio: float
    model_used: str
    latency_ms: float
    success: bool = True
    error: str | None = None

    @property
    def savings(self) -> int:
        """Tokens saved by summarization."""
        return self.original_tokens - self.summary_tokens


# =============================================================================
# Summarizer Service
# =============================================================================


@dataclass
class Summarizer:
    """
    LLM-powered conversation summarizer.

    Integrates with Morpheus for LLM calls. Can be used with
    ConversationWindow via the summarize_sync wrapper.
    """

    morpheus: "MorpheusPersistence | None" = None
    model: str = "claude-3-haiku-20240307"  # Fast, cheap model for summarization
    max_tokens: int = 500
    temperature: float = 0.3  # Low temp for consistent summaries
    target_compression: float = 0.25  # Aim for 25% of original size

    # Circadian modulation (Pattern #11)
    enable_circadian: bool = True
    night_hours: tuple[int, int] = (22, 6)  # 10pm to 6am

    # Prompt templates
    default_prompt: str = DEFAULT_SUMMARIZE_PROMPT
    aggressive_prompt: str = AGGRESSIVE_SUMMARIZE_PROMPT

    # Statistics
    _total_summarizations: int = field(default=0, init=False)
    _total_tokens_saved: int = field(default=0, init=False)

    def _is_night_time(self) -> bool:
        """Check if current time is within night hours."""
        hour = datetime.now().hour
        start, end = self.night_hours
        if start > end:  # Spans midnight
            return hour >= start or hour < end
        return start <= hour < end

    def _get_prompt(self, original_tokens: int) -> str:
        """Get appropriate prompt based on circadian modulation."""
        if self.enable_circadian and self._is_night_time():
            # Night mode: more aggressive compression
            return self.aggressive_prompt

        # Day mode: balanced summarization
        target_tokens = int(original_tokens * self.target_compression)
        target_words = target_tokens  # Rough approximation

        return self.default_prompt.format(
            target_tokens=target_tokens,
            target_words=target_words,
            conversation="{conversation}",
        )

    def _format_messages(self, messages: list["ContextMessage"]) -> str:
        """Format messages for summarization prompt."""
        lines = []
        for msg in messages:
            role = msg.role.upper()
            content = msg.content[:2000]  # Truncate very long messages
            lines.append(f"{role}: {content}")
        return "\n\n".join(lines)

    async def summarize(
        self,
        messages: list["ContextMessage"],
        *,
        force_aggressive: bool = False,
    ) -> SummarizationResult:
        """
        Summarize a list of messages.

        Args:
            messages: Messages to summarize
            force_aggressive: Use aggressive prompt regardless of time

        Returns:
            SummarizationResult with summary and metrics
        """
        if not messages:
            return SummarizationResult(
                summary="",
                original_tokens=0,
                summary_tokens=0,
                compression_ratio=1.0,
                model_used=self.model,
                latency_ms=0,
            )

        # Calculate original tokens
        original_tokens = sum(msg.tokens for msg in messages)

        # Format conversation
        conversation = self._format_messages(messages)

        # Get prompt
        if force_aggressive:
            prompt_template = self.aggressive_prompt
        else:
            prompt_template = self._get_prompt(original_tokens)

        prompt = prompt_template.replace("{conversation}", conversation)

        # Check if morpheus is available
        if self.morpheus is None:
            # Fallback: simple extractive summary
            summary = self._fallback_summarize(messages)
            summary_tokens = len(summary) // 4
            return SummarizationResult(
                summary=summary,
                original_tokens=original_tokens,
                summary_tokens=summary_tokens,
                compression_ratio=summary_tokens / max(original_tokens, 1),
                model_used="fallback",
                latency_ms=0,
            )

        # Call LLM via Morpheus
        try:
            from services.morpheus.types import ChatMessage, ChatRequest

            request = ChatRequest(
                model=self.model,
                messages=[ChatMessage(role="user", content=prompt)],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            start = datetime.now()
            result = await self.morpheus.complete(request, archetype="system")
            latency_ms = (datetime.now() - start).total_seconds() * 1000

            # Extract summary from CompletionResult.response.choices
            summary = ""
            if result.response and result.response.choices:
                summary = result.response.choices[0].message.content or ""

            summary_tokens = len(summary) // 4

            # Update statistics
            self._total_summarizations += 1
            self._total_tokens_saved += original_tokens - summary_tokens

            return SummarizationResult(
                summary=summary.strip(),
                original_tokens=original_tokens,
                summary_tokens=summary_tokens,
                compression_ratio=summary_tokens / max(original_tokens, 1),
                model_used=self.model,
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.warning(f"Summarization failed: {e}")
            # Fallback on error
            summary = self._fallback_summarize(messages)
            summary_tokens = len(summary) // 4
            return SummarizationResult(
                summary=summary,
                original_tokens=original_tokens,
                summary_tokens=summary_tokens,
                compression_ratio=summary_tokens / max(original_tokens, 1),
                model_used="fallback",
                latency_ms=0,
                success=False,
                error=str(e),
            )

    def _fallback_summarize(self, messages: list["ContextMessage"]) -> str:
        """
        Simple extractive fallback when LLM is unavailable.

        Takes first sentence from each message.
        """
        summaries = []
        for msg in messages[-6:]:  # Last 6 messages only
            content = msg.content.strip()
            # Get first sentence
            first_sentence = content.split(".")[0]
            if len(first_sentence) > 100:
                first_sentence = first_sentence[:100] + "..."
            summaries.append(f"- {msg.role}: {first_sentence}")

        return "\n".join(summaries)

    def summarize_sync(self, messages: list["ContextMessage"]) -> str:
        """
        Synchronous wrapper for use with ConversationWindow.

        Note: This blocks the event loop. Use async version when possible.

        Args:
            messages: Messages to summarize

        Returns:
            Summary string
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, can't use run_until_complete
                # Fall back to simple summarization
                return self._fallback_summarize(messages)
            result = loop.run_until_complete(self.summarize(messages))
            return result.summary
        except RuntimeError:
            # No event loop, create one
            result = asyncio.run(self.summarize(messages))
            return result.summary

    def get_statistics(self) -> dict[str, Any]:
        """Get summarization statistics."""
        return {
            "total_summarizations": self._total_summarizations,
            "total_tokens_saved": self._total_tokens_saved,
            "average_savings": (
                self._total_tokens_saved / self._total_summarizations
                if self._total_summarizations > 0
                else 0
            ),
        }


# =============================================================================
# Factory Functions
# =============================================================================


def create_summarizer(
    morpheus: "MorpheusPersistence | None" = None,
    model: str | None = None,
) -> Summarizer:
    """
    Create a Summarizer instance.

    Args:
        morpheus: MorpheusPersistence for LLM calls (optional)
        model: Override default model

    Returns:
        Configured Summarizer
    """
    kwargs: dict[str, Any] = {}
    if morpheus:
        kwargs["morpheus"] = morpheus
    if model:
        kwargs["model"] = model

    return Summarizer(**kwargs)


__all__ = [
    "Summarizer",
    "SummarizationResult",
    "create_summarizer",
    "DEFAULT_SUMMARIZE_PROMPT",
    "AGGRESSIVE_SUMMARIZE_PROMPT",
]
