"""
Tests for Summarizer service.

CLI v7 Phase 2: Deep Conversation

Test categories (per test-patterns.md T-gent taxonomy):
- Type I (Unit): Basic summarization operations
- Type II (Integration): Summarizer + Morpheus
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.conductor.summarizer import (
    AGGRESSIVE_SUMMARIZE_PROMPT,
    DEFAULT_SUMMARIZE_PROMPT,
    SummarizationResult,
    Summarizer,
    create_summarizer,
)
from services.conductor.window import ContextMessage

# =============================================================================
# Type I: Unit Tests
# =============================================================================


class TestSummarizerBasic:
    """Basic unit tests for Summarizer."""

    def test_create_summarizer_defaults(self) -> None:
        """Summarizer creates with sensible defaults."""
        summarizer = Summarizer()

        assert summarizer.model == "claude-3-haiku-20240307"
        assert summarizer.max_tokens == 500
        assert summarizer.temperature == 0.3
        assert summarizer.target_compression == 0.25
        assert summarizer.morpheus is None

    def test_create_summarizer_custom_model(self) -> None:
        """Summarizer accepts custom model."""
        summarizer = Summarizer(model="gpt-4o-mini")

        assert summarizer.model == "gpt-4o-mini"

    def test_fallback_summarize_extracts_first_sentences(self) -> None:
        """Fallback summarization extracts first sentences."""
        summarizer = Summarizer()

        messages = [
            ContextMessage(role="user", content="This is a long message. With multiple sentences."),
            ContextMessage(role="assistant", content="This is the response. Also multiple parts."),
        ]

        summary = summarizer._fallback_summarize(messages)

        assert "user:" in summary.lower()
        assert "assistant:" in summary.lower()
        assert "This is a long message" in summary

    def test_fallback_truncates_long_sentences(self) -> None:
        """Fallback truncates very long first sentences."""
        summarizer = Summarizer()

        long_text = "x" * 500  # Very long single sentence
        messages = [ContextMessage(role="user", content=long_text)]

        summary = summarizer._fallback_summarize(messages)

        # Should be truncated
        assert len(summary) < 200

    def test_format_messages_for_prompt(self) -> None:
        """Messages formatted correctly for summarization prompt."""
        summarizer = Summarizer()

        messages = [
            ContextMessage(role="user", content="Hello"),
            ContextMessage(role="assistant", content="Hi there"),
        ]

        formatted = summarizer._format_messages(messages)

        assert "USER: Hello" in formatted
        assert "ASSISTANT: Hi there" in formatted

    def test_format_truncates_very_long_messages(self) -> None:
        """Very long messages are truncated in prompt."""
        summarizer = Summarizer()

        long_content = "x" * 5000
        messages = [ContextMessage(role="user", content=long_content)]

        formatted = summarizer._format_messages(messages)

        # Should be capped at 2000 chars per message
        assert len(formatted) < 2100


class TestCircadianModulation:
    """Tests for circadian modulation (Pattern #11)."""

    def test_night_time_detection(self) -> None:
        """Night time correctly detected."""
        summarizer = Summarizer(
            enable_circadian=True,
            night_hours=(22, 6),  # 10pm to 6am
        )

        # Mock datetime to test different hours
        with patch("services.conductor.summarizer.datetime") as mock_dt:
            # Test midnight (night)
            mock_dt.now.return_value = MagicMock(hour=0)
            assert summarizer._is_night_time()

            # Test noon (day)
            mock_dt.now.return_value = MagicMock(hour=12)
            assert not summarizer._is_night_time()

            # Test 11pm (night)
            mock_dt.now.return_value = MagicMock(hour=23)
            assert summarizer._is_night_time()

    def test_aggressive_prompt_at_night(self) -> None:
        """Uses aggressive prompt during night hours."""
        summarizer = Summarizer(enable_circadian=True)

        with patch("services.conductor.summarizer.datetime") as mock_dt:
            mock_dt.now.return_value = MagicMock(hour=2)  # 2am

            prompt = summarizer._get_prompt(1000)

            assert "max 3 sentences" in prompt.lower() or "essential" in prompt.lower()

    def test_default_prompt_during_day(self) -> None:
        """Uses default prompt during day hours."""
        summarizer = Summarizer(enable_circadian=True)

        with patch("services.conductor.summarizer.datetime") as mock_dt:
            mock_dt.now.return_value = MagicMock(hour=14)  # 2pm

            prompt = summarizer._get_prompt(1000)

            # Default prompt has target_tokens placeholder
            assert "target_tokens" not in prompt or "{target_tokens}" not in prompt


class TestSummarizationResult:
    """Tests for SummarizationResult dataclass."""

    def test_result_success_properties(self) -> None:
        """Result properties for successful summarization."""
        result = SummarizationResult(
            summary="This is a summary.",
            original_tokens=1000,
            summary_tokens=100,
            compression_ratio=0.1,
            model_used="claude-3-haiku",
            latency_ms=150.0,
        )

        assert result.success
        assert result.savings == 900
        assert result.compression_ratio == 0.1

    def test_result_failure_properties(self) -> None:
        """Result properties for failed summarization."""
        result = SummarizationResult(
            summary="Fallback summary",
            original_tokens=500,
            summary_tokens=50,
            compression_ratio=0.1,
            model_used="fallback",
            latency_ms=0,
            success=False,
            error="LLM unavailable",
        )

        assert not result.success
        assert result.error == "LLM unavailable"


class TestSummarizerStatistics:
    """Tests for summarizer statistics tracking."""

    def test_statistics_initially_zero(self) -> None:
        """Statistics start at zero."""
        summarizer = Summarizer()

        stats = summarizer.get_statistics()

        assert stats["total_summarizations"] == 0
        assert stats["total_tokens_saved"] == 0
        assert stats["average_savings"] == 0


# =============================================================================
# Type II: Integration Tests
# =============================================================================


class TestSummarizerWithMorpheus:
    """Integration tests with mocked Morpheus."""

    @pytest.mark.asyncio
    async def test_summarize_with_morpheus(self) -> None:
        """Summarizer calls Morpheus for LLM summarization."""
        # Mock Morpheus with proper CompletionResult structure
        mock_morpheus = AsyncMock()
        mock_result = MagicMock()
        # CompletionResult has .response with .choices
        mock_result.response.choices = [MagicMock()]
        mock_result.response.choices[0].message.content = "This is the summary."
        mock_result.latency_ms = 100.0
        mock_morpheus.complete.return_value = mock_result

        summarizer = Summarizer(morpheus=mock_morpheus)

        messages = [
            ContextMessage(role="user", content="Long message " * 50),
            ContextMessage(role="assistant", content="Long response " * 50),
        ]

        result = await summarizer.summarize(messages)

        assert result.success
        assert result.summary == "This is the summary."
        assert result.model_used == "claude-3-haiku-20240307"
        mock_morpheus.complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_summarize_fallback_on_error(self) -> None:
        """Summarizer falls back on Morpheus error."""
        # Mock Morpheus that raises after request creation
        mock_morpheus = AsyncMock()
        mock_morpheus.complete.side_effect = Exception("API Error")

        summarizer = Summarizer(morpheus=mock_morpheus)

        messages = [
            ContextMessage(role="user", content="Hello world"),
        ]

        result = await summarizer.summarize(messages)

        assert not result.success
        assert result.model_used == "fallback"
        assert "API Error" in str(result.error)  # Error message contains "API Error"

    @pytest.mark.asyncio
    async def test_summarize_empty_messages(self) -> None:
        """Empty message list returns empty result."""
        summarizer = Summarizer()

        result = await summarizer.summarize([])

        assert result.success
        assert result.summary == ""
        assert result.original_tokens == 0

    @pytest.mark.asyncio
    async def test_summarize_without_morpheus(self) -> None:
        """Without Morpheus, uses fallback summarization."""
        summarizer = Summarizer()  # No morpheus

        messages = [
            ContextMessage(role="user", content="Test message content."),
            ContextMessage(role="assistant", content="Test response content."),
        ]

        result = await summarizer.summarize(messages)

        assert result.success
        assert result.model_used == "fallback"
        assert len(result.summary) > 0


class TestSummarizeSync:
    """Tests for synchronous summarization wrapper."""

    def test_summarize_sync_uses_fallback(self) -> None:
        """Sync wrapper uses fallback in running loop context."""
        summarizer = Summarizer()

        messages = [
            ContextMessage(role="user", content="Hello world."),
        ]

        # This should work without async context
        summary = summarizer.summarize_sync(messages)

        assert isinstance(summary, str)
        assert len(summary) > 0


# =============================================================================
# Factory Tests
# =============================================================================


class TestSummarizerFactory:
    """Tests for summarizer factory functions."""

    def test_create_summarizer_without_morpheus(self) -> None:
        """Factory creates summarizer without Morpheus."""
        summarizer = create_summarizer()

        assert isinstance(summarizer, Summarizer)
        assert summarizer.morpheus is None

    def test_create_summarizer_with_morpheus(self) -> None:
        """Factory creates summarizer with Morpheus."""
        mock_morpheus = MagicMock()

        summarizer = create_summarizer(morpheus=mock_morpheus)

        assert summarizer.morpheus is mock_morpheus

    def test_create_summarizer_with_custom_model(self) -> None:
        """Factory accepts custom model."""
        summarizer = create_summarizer(model="gpt-4o")

        assert summarizer.model == "gpt-4o"
