"""
Tests for ContextProjector: Galois Connection for lossy compression.
"""

from __future__ import annotations

import pytest
from agents.d.context_window import ContextWindow, TurnRole
from agents.d.linearity import ResourceClass
from agents.d.projector import (
    AdaptiveThreshold,
    CompressionConfig,
    CompressionResult,
    ContextProjector,
    DefaultSummarizer,
    auto_compress,
    create_projector,
)


class TestDefaultSummarizer:
    """Tests for DefaultSummarizer."""

    @pytest.mark.asyncio
    async def test_short_text_unchanged(self) -> None:
        """Short text passes through unchanged."""
        summarizer = DefaultSummarizer()
        text = "Hello world."

        result = await summarizer.summarize(text, max_tokens=100)
        assert result == text

    @pytest.mark.asyncio
    async def test_long_text_truncated(self) -> None:
        """Long text is truncated."""
        summarizer = DefaultSummarizer()
        text = "a" * 1000  # Long text

        result = await summarizer.summarize(text, max_tokens=10)
        assert len(result) < len(text)
        assert result.endswith("...")

    @pytest.mark.asyncio
    async def test_sentence_preservation(self) -> None:
        """Summarizer tries to preserve complete sentences."""
        summarizer = DefaultSummarizer()
        text = "First sentence. Second sentence. Third sentence."

        # Allow ~20 tokens = ~80 chars
        result = await summarizer.summarize(text, max_tokens=20)

        # Should include some sentences
        assert "sentence" in result


class TestCompressionResult:
    """Tests for CompressionResult."""

    def test_compression_ratio(self) -> None:
        """Compression ratio is calculated correctly."""
        result = CompressionResult(
            window=ContextWindow(),
            original_tokens=1000,
            compressed_tokens=500,
            dropped_count=5,
            summarized_count=2,
            preserved_count=3,
        )

        assert result.compression_ratio == 0.5
        assert result.savings == 0.5

    def test_compression_ratio_zero_original(self) -> None:
        """Handles zero original tokens."""
        result = CompressionResult(
            window=ContextWindow(),
            original_tokens=0,
            compressed_tokens=0,
            dropped_count=0,
            summarized_count=0,
            preserved_count=0,
        )

        assert result.compression_ratio == 1.0


class TestCompressionConfig:
    """Tests for CompressionConfig."""

    def test_defaults(self) -> None:
        """Default config values are sensible."""
        config = CompressionConfig()

        assert config.target_pressure == 0.5
        assert config.min_tokens == 100
        assert config.summary_tokens == 50
        assert config.merge_adjacent is True
        assert config.max_drops_per_pass == 10


class TestContextProjector:
    """Tests for ContextProjector."""

    @pytest.mark.asyncio
    async def test_compress_empty_window(self) -> None:
        """Compressing empty window returns empty window."""
        projector = ContextProjector()
        window = ContextWindow()

        result = await projector.compress(window)

        assert len(result.window) == 0
        assert result.dropped_count == 0

    @pytest.mark.asyncio
    async def test_compress_drops_droppable(self) -> None:
        """Compression drops DROPPABLE turns first."""
        projector = ContextProjector()
        window = ContextWindow(max_tokens=100)

        # Add turns (assistant messages are DROPPABLE by default)
        window.append(TurnRole.USER, "Keep me")  # PRESERVED
        window.append(TurnRole.ASSISTANT, "Drop me " * 20)  # DROPPABLE, long
        window.append(TurnRole.USER, "Keep me too")  # PRESERVED

        # Force compression (set target low)
        result = await projector.compress(window, target_pressure=0.1)

        # User messages (which were PRESERVED) should still be there
        # The result.preserved_count tracks original classification
        assert result.preserved_count == 2

        # The compressed window should have the user messages
        turns = result.window.all_turns()
        user_turns = [t for t in turns if t.role == TurnRole.USER]
        assert len(user_turns) == 2

    @pytest.mark.asyncio
    async def test_compress_preserves_preserved(self) -> None:
        """PRESERVED turns are never dropped."""
        projector = ContextProjector()
        window = ContextWindow(max_tokens=50)

        # Add preserved turns
        window.append(TurnRole.USER, "Critical instruction " * 10)
        window.append(TurnRole.USER, "Another critical one " * 10)

        result = await projector.compress(window, target_pressure=0.1)

        # Both should still be there
        assert result.preserved_count == 2

    @pytest.mark.asyncio
    async def test_compress_updates_metadata(self) -> None:
        """Compression updates window metadata."""
        projector = ContextProjector()
        window = ContextWindow()
        window.append(TurnRole.USER, "Test")

        initial_count = window._meta.compression_count

        result = await projector.compress(window)

        assert result.window._meta.compression_count == initial_count + 1
        assert result.window._meta.last_compression is not None

    @pytest.mark.asyncio
    async def test_compress_with_custom_target(self) -> None:
        """Can specify custom target pressure."""
        projector = ContextProjector()
        window = ContextWindow(max_tokens=1000)

        window.append(TurnRole.ASSISTANT, "a" * 400)  # ~100 tokens
        window.append(TurnRole.ASSISTANT, "b" * 400)  # ~100 tokens

        # Very aggressive compression
        result = await projector.compress(window, target_pressure=0.1)

        # Should have compressed significantly
        assert result.compression_ratio < 1.0

    @pytest.mark.asyncio
    async def test_selective_compress_keeps_roles(self) -> None:
        """selective_compress keeps specified roles."""
        projector = ContextProjector()
        window = ContextWindow()

        window.append(TurnRole.SYSTEM, "System prompt")
        window.append(TurnRole.USER, "User message")
        window.append(TurnRole.ASSISTANT, "Assistant response")
        window.append(TurnRole.TOOL, "Tool output")

        result = await projector.selective_compress(
            window,
            keep_roles={TurnRole.SYSTEM, TurnRole.USER},
            keep_recent=0,  # Don't auto-keep recent
        )

        turns = result.window.all_turns()
        roles = {t.role for t in turns}

        assert TurnRole.SYSTEM in roles
        assert TurnRole.USER in roles

    @pytest.mark.asyncio
    async def test_selective_compress_keeps_recent(self) -> None:
        """selective_compress keeps recent turns."""
        projector = ContextProjector()
        window = ContextWindow()

        for i in range(10):
            window.append(TurnRole.ASSISTANT, f"Message {i}")

        result = await projector.selective_compress(
            window,
            keep_roles=set(),  # Don't auto-keep any roles
            keep_recent=3,
        )

        turns = result.window.all_turns()
        contents = [t.content for t in turns]

        # Should have last 3
        assert "Message 7" in contents
        assert "Message 8" in contents
        assert "Message 9" in contents


class TestAdaptiveThreshold:
    """Tests for AdaptiveThreshold."""

    def test_base_threshold(self) -> None:
        """Base threshold is used by default."""
        threshold = AdaptiveThreshold(base_threshold=0.7)
        assert abs(threshold.effective_threshold - 0.7) < 0.2

    def test_early_task_higher(self) -> None:
        """Early in task, threshold is higher (keep more)."""
        early = AdaptiveThreshold(base_threshold=0.7, task_progress=0.1)
        late = AdaptiveThreshold(base_threshold=0.7, task_progress=0.5)

        assert early.effective_threshold > late.effective_threshold

    def test_late_task_lower(self) -> None:
        """Near completion, threshold is lower (compress more)."""
        middle = AdaptiveThreshold(base_threshold=0.7, task_progress=0.5)
        late = AdaptiveThreshold(base_threshold=0.7, task_progress=0.9)

        assert late.effective_threshold < middle.effective_threshold

    def test_errors_increase_threshold(self) -> None:
        """Errors increase threshold (preserve debug info)."""
        no_errors = AdaptiveThreshold(base_threshold=0.7, error_rate=0.0)
        with_errors = AdaptiveThreshold(base_threshold=0.7, error_rate=0.5)

        assert with_errors.effective_threshold > no_errors.effective_threshold

    def test_loop_decreases_threshold(self) -> None:
        """Loop detection decreases threshold (break pattern)."""
        normal = AdaptiveThreshold(base_threshold=0.7, loop_detected=False)
        looping = AdaptiveThreshold(base_threshold=0.7, loop_detected=True)

        assert looping.effective_threshold < normal.effective_threshold

    def test_threshold_clamped(self) -> None:
        """Threshold is clamped to reasonable range."""
        # Try to push it too high
        high = AdaptiveThreshold(
            base_threshold=0.95,
            task_progress=0.0,
            error_rate=1.0,
        )
        assert high.effective_threshold <= 0.95

        # Try to push it too low
        low = AdaptiveThreshold(
            base_threshold=0.5,
            task_progress=1.0,
            loop_detected=True,
        )
        assert low.effective_threshold >= 0.5

    def test_update_method(self) -> None:
        """Can update threshold parameters."""
        threshold = AdaptiveThreshold()

        threshold.update(task_progress=0.5)
        assert threshold.task_progress == 0.5

        threshold.update(error_rate=0.3)
        assert threshold.error_rate == 0.3

        threshold.update(loop_detected=True)
        assert threshold.loop_detected is True


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_projector(self) -> None:
        """create_projector creates configured projector."""
        projector = create_projector(target_pressure=0.3)

        assert projector.config.target_pressure == 0.3

    @pytest.mark.asyncio
    async def test_auto_compress_when_needed(self) -> None:
        """auto_compress compresses when needed."""
        window = ContextWindow(max_tokens=100)

        # Add lots of content to exceed threshold
        for i in range(20):
            window.append(TurnRole.ASSISTANT, f"Message {i} " * 50)

        assert window.needs_compression

        compressed = await auto_compress(window)

        # Should have compressed
        assert compressed.total_tokens <= window.total_tokens

    @pytest.mark.asyncio
    async def test_auto_compress_skips_when_not_needed(self) -> None:
        """auto_compress returns original when not needed."""
        window = ContextWindow(max_tokens=100000)
        window.append(TurnRole.USER, "Short message")

        assert not window.needs_compression

        result = await auto_compress(window)

        # Should be same window
        assert result is window


class TestGaloisConnectionProperty:
    """
    Tests verifying the Galois Connection property.

    compress ⊣ expand implies:
    compress(expand(c)) <= c

    Since we don't have expand, we verify the weaker property:
    - Compression is monotonic (larger inputs don't produce smaller outputs)
    - Compression respects linearity ordering
    """

    @pytest.mark.asyncio
    async def test_monotonic_preservation(self) -> None:
        """Higher resource classes are preserved over lower."""
        projector = ContextProjector()
        window = ContextWindow(max_tokens=100)

        # Add turns of different classes
        window.append(TurnRole.USER, "Preserved content")  # PRESERVED
        window.append(TurnRole.ASSISTANT, "Therefore important")  # REQUIRED
        window.append(TurnRole.ASSISTANT, "Droppable stuff " * 20)  # DROPPABLE

        result = await projector.compress(window, target_pressure=0.1)

        # PRESERVED should always be there
        assert result.preserved_count >= 1

        # DROPPABLE should be dropped first
        droppable = result.window.droppable_turns()
        preserved = result.window.preserved_turns()

        # If anything was dropped, droppable should be fewer
        if result.dropped_count > 0:
            assert len(droppable) < 1  # We had 1 droppable

    @pytest.mark.asyncio
    async def test_compression_is_lossy(self) -> None:
        """
        Verify compression is lossy - NOT a lens.

        If compress were a lens, compress(expand(compress(s))) = compress(s)
        Since we don't have expand, we verify compress is not identity.
        """
        projector = ContextProjector()
        window = ContextWindow(max_tokens=100)

        # Add lots of droppable content
        for i in range(10):
            window.append(TurnRole.ASSISTANT, f"Droppable message {i} " * 10)

        result = await projector.compress(window, target_pressure=0.1)

        # Should have removed something
        assert result.compression_ratio < 1.0

        # Information is lost - this is expected
        assert result.dropped_count > 0 or result.summarized_count > 0


class TestEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_all_preserved(self) -> None:
        """Window with all PRESERVED turns cannot compress much."""
        projector = ContextProjector()
        window = ContextWindow(max_tokens=100)

        # All user messages (PRESERVED)
        for i in range(5):
            window.append(TurnRole.USER, f"User message {i}")

        result = await projector.compress(window, target_pressure=0.1)

        # Should preserve all
        assert result.preserved_count == 5
        assert result.dropped_count == 0

    @pytest.mark.asyncio
    async def test_all_droppable(self) -> None:
        """Window with all DROPPABLE turns can compress aggressively."""
        projector = ContextProjector()
        window = ContextWindow(max_tokens=100)

        # All assistant messages (DROPPABLE)
        for i in range(10):
            window.append(TurnRole.ASSISTANT, f"Assistant message {i} " * 10)

        result = await projector.compress(window, target_pressure=0.1)

        # Should have dropped most
        assert result.dropped_count > 0

    @pytest.mark.asyncio
    async def test_mixed_compression(self) -> None:
        """Mixed content compresses appropriately."""
        projector = ContextProjector()
        window = ContextWindow(max_tokens=200)

        # Mix of all types
        window.append(TurnRole.SYSTEM, "System prompt")  # REQUIRED
        window.append(TurnRole.USER, "User question")  # PRESERVED
        window.append(TurnRole.ASSISTANT, "Thinking..." * 20)  # DROPPABLE
        window.append(TurnRole.ASSISTANT, "Therefore answer")  # REQUIRED
        window.append(TurnRole.USER, "Follow up")  # PRESERVED

        result = await projector.compress(window, target_pressure=0.3)

        # Preserved should remain
        assert result.preserved_count >= 2
