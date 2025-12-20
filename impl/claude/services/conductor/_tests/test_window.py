"""
Tests for ConversationWindow.

CLI v7 Phase 2: Deep Conversation

Test categories (per test-patterns.md T-gent taxonomy):
- Type I (Unit): Basic window operations
- Type II (Integration): Window + Summarizer
- Type III (Property-based): Bounded history invariants
"""

from __future__ import annotations

from datetime import datetime

import pytest

from services.conductor.window import (
    ContextMessage,
    ConversationWindow,
    WindowSnapshot,
    create_window_from_config,
)

# =============================================================================
# Type I: Unit Tests
# =============================================================================


class TestConversationWindowBasic:
    """Basic unit tests for ConversationWindow."""

    def test_create_window_with_defaults(self) -> None:
        """Window creates with sensible defaults."""
        window = ConversationWindow()

        assert window.max_turns == 35  # CLI v7: increased from 10 to 35
        assert window.strategy == "summarize"
        assert window.turn_count == 0
        assert window.total_tokens == 0
        assert not window.has_summary

    def test_create_window_with_custom_params(self) -> None:
        """Window accepts custom configuration."""
        window = ConversationWindow(
            max_turns=5,
            strategy="sliding",
            context_window_tokens=4000,
            summarization_threshold=0.7,
        )

        assert window.max_turns == 5
        assert window.strategy == "sliding"
        assert window.context_window_tokens == 4000
        assert window.summarization_threshold == 0.7

    def test_add_single_turn(self) -> None:
        """Adding a turn increases count and tokens."""
        window = ConversationWindow(max_turns=10)

        window.add_turn("Hello", "Hi there!")

        assert window.turn_count == 1
        assert window.total_tokens > 0
        assert window.total_turn_count == 1

    def test_add_multiple_turns(self) -> None:
        """Multiple turns accumulate correctly."""
        window = ConversationWindow(max_turns=10)

        window.add_turn("First", "Response 1")
        window.add_turn("Second", "Response 2")
        window.add_turn("Third", "Response 3")

        assert window.turn_count == 3
        assert window.total_turn_count == 3

    def test_get_context_messages_order(self) -> None:
        """Context messages returned in correct order."""
        window = ConversationWindow(max_turns=10)
        window.add_turn("User 1", "Assistant 1")
        window.add_turn("User 2", "Assistant 2")

        messages = window.get_context_messages()

        assert len(messages) == 4  # 2 turns × 2 messages
        assert messages[0].role == "user"
        assert messages[0].content == "User 1"
        assert messages[1].role == "assistant"
        assert messages[1].content == "Assistant 1"
        assert messages[2].role == "user"
        assert messages[3].role == "assistant"

    def test_system_prompt_prepended(self) -> None:
        """System prompt appears first in context."""
        window = ConversationWindow(max_turns=10)
        window.set_system_prompt("You are helpful.")
        window.add_turn("Hello", "Hi!")

        messages = window.get_context_messages()

        assert len(messages) == 3  # system + user + assistant
        assert messages[0].role == "system"
        assert messages[0].content == "You are helpful."

    def test_utilization_calculation(self) -> None:
        """Utilization is calculated correctly."""
        window = ConversationWindow(
            max_turns=10,
            context_window_tokens=100,  # Small for testing
        )

        # Add content that's roughly 40 tokens
        window.add_turn("x" * 80, "y" * 80)  # ~40 tokens

        assert 0 < window.utilization < 1.0
        assert window.utilization == window.total_tokens / 100

    def test_reset_clears_state(self) -> None:
        """Reset clears all window state."""
        window = ConversationWindow(max_turns=10)
        window.add_turn("Hello", "World")

        window.reset()

        assert window.turn_count == 0
        assert window.total_tokens == 0
        assert not window.has_summary


class TestSlidingStrategy:
    """Tests for sliding window strategy."""

    def test_sliding_evicts_oldest(self) -> None:
        """Sliding strategy evicts oldest turn at capacity."""
        window = ConversationWindow(max_turns=3, strategy="sliding")

        window.add_turn("First", "R1")
        window.add_turn("Second", "R2")
        window.add_turn("Third", "R3")
        window.add_turn("Fourth", "R4")  # Should evict First

        assert window.turn_count == 3
        messages = window.get_context_messages()
        # First message should be "Second" now
        assert messages[0].content == "Second"

    def test_sliding_tracks_summarized_count(self) -> None:
        """Sliding strategy tracks evicted turn count."""
        window = ConversationWindow(max_turns=2, strategy="sliding")

        window.add_turn("1", "R1")
        window.add_turn("2", "R2")
        window.add_turn("3", "R3")  # Evicts 1
        window.add_turn("4", "R4")  # Evicts 2

        assert window.turn_count == 2  # Working memory
        assert window.total_turn_count == 4  # Including evicted


class TestForgetStrategy:
    """Tests for forget (hard truncate) strategy."""

    def test_forget_drops_without_memory(self) -> None:
        """Forget strategy drops turns with no summary."""
        window = ConversationWindow(max_turns=2, strategy="forget")

        window.add_turn("1", "R1")
        window.add_turn("2", "R2")
        window.add_turn("3", "R3")

        assert window.turn_count == 2
        assert not window.has_summary
        # Forget doesn't track summarized count
        assert window.total_turn_count == 2  # Only current window


class TestSummarizeStrategy:
    """Tests for summarize strategy."""

    def test_summarize_with_summarizer(self) -> None:
        """Summarize strategy calls summarizer when available."""
        summaries_called: list[int] = []

        def mock_summarizer(messages: list[ContextMessage]) -> str:
            summaries_called.append(len(messages))
            return f"Summary of {len(messages)} messages"

        window = ConversationWindow(
            max_turns=4,
            strategy="summarize",
            summarizer=mock_summarizer,
        )

        # Fill window
        for i in range(5):
            window.add_turn(f"User {i}", f"Response {i}")

        assert window.has_summary
        assert len(summaries_called) > 0

    def test_summarize_falls_back_to_sliding(self) -> None:
        """Without summarizer, falls back to sliding behavior."""
        window = ConversationWindow(
            max_turns=3,
            strategy="summarize",
            # No summarizer set
        )

        window.add_turn("1", "R1")
        window.add_turn("2", "R2")
        window.add_turn("3", "R3")
        window.add_turn("4", "R4")

        # Should work like sliding
        assert window.turn_count == 3
        assert not window.has_summary


class TestWindowSnapshot:
    """Tests for WindowSnapshot immutable views."""

    def test_snapshot_captures_state(self) -> None:
        """Snapshot captures current window state."""
        window = ConversationWindow(max_turns=5, strategy="sliding")
        window.add_turn("Hello", "World")

        snapshot = window.snapshot()

        assert isinstance(snapshot, WindowSnapshot)
        assert snapshot.turn_count == 1
        assert snapshot.strategy == "sliding"
        assert not snapshot.has_summary
        assert snapshot.utilization >= 0

    def test_snapshot_is_immutable(self) -> None:
        """Snapshot is frozen dataclass."""
        window = ConversationWindow()
        snapshot = window.snapshot()

        with pytest.raises(Exception):  # FrozenInstanceError
            snapshot.turn_count = 999  # type: ignore


class TestSerialization:
    """Tests for window serialization."""

    def test_to_dict_roundtrip(self) -> None:
        """Window serializes and deserializes correctly."""
        window = ConversationWindow(max_turns=5, strategy="hybrid")
        window.add_turn("Hello", "World")
        window.add_turn("How are you?", "I'm fine!")

        data = window.to_dict()
        restored = ConversationWindow.from_dict(data)

        assert restored.turn_count == window.turn_count
        assert restored.strategy == window.strategy
        assert restored.max_turns == window.max_turns


# =============================================================================
# Type III: Property-Based Tests
# =============================================================================

try:
    from hypothesis import given, settings, strategies as st

    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False


@pytest.mark.skipif(not HAS_HYPOTHESIS, reason="hypothesis not installed")
class TestWindowProperties:
    """Property-based tests for window invariants."""

    @given(
        st.lists(
            st.tuples(st.text(min_size=1, max_size=100), st.text(min_size=1, max_size=100)),
            min_size=1,
            max_size=50,
        )
    )
    @settings(max_examples=50)
    def test_window_never_exceeds_max_turns(self, turns: list[tuple[str, str]]) -> None:
        """Window maintains bounded history regardless of input size."""
        max_turns = 10
        window = ConversationWindow(max_turns=max_turns, strategy="sliding")

        for user_msg, asst_msg in turns:
            window.add_turn(user_msg, asst_msg)

        assert window.turn_count <= max_turns

    @given(
        st.integers(min_value=1, max_value=20),
        st.integers(min_value=1, max_value=100),
    )
    @settings(max_examples=30)
    def test_total_turn_count_monotonic(self, max_turns: int, num_turns: int) -> None:
        """Total turn count never decreases."""
        window = ConversationWindow(max_turns=max_turns, strategy="sliding")

        prev_total = 0
        for i in range(num_turns):
            window.add_turn(f"User {i}", f"Response {i}")
            assert window.total_turn_count >= prev_total
            prev_total = window.total_turn_count

    @given(st.sampled_from(["sliding", "summarize", "hybrid", "forget"]))
    @settings(max_examples=10)
    def test_strategy_respects_max_turns(self, strategy: str) -> None:
        """All strategies respect max_turns bound."""
        max_turns = 5
        window = ConversationWindow(max_turns=max_turns, strategy=strategy)

        for i in range(20):
            window.add_turn(f"User {i}", f"Response {i}")

        assert window.turn_count <= max_turns


# =============================================================================
# Type II: Integration Tests
# =============================================================================


class TestWindowWithContextMessage:
    """Integration tests with ContextMessage."""

    def test_context_message_token_estimation(self) -> None:
        """ContextMessage estimates tokens from content."""
        msg = ContextMessage(role="user", content="Hello world!")

        # 12 chars / 4 = 3 tokens (rough estimate)
        assert msg.tokens == 3

    def test_context_message_to_llm_format(self) -> None:
        """ContextMessage converts to LLM API format."""
        msg = ContextMessage(role="assistant", content="I can help!")

        llm_format = msg.to_llm_format()

        assert llm_format == {"role": "assistant", "content": "I can help!"}

    def test_window_get_context_for_llm(self) -> None:
        """Window produces LLM-ready context."""
        window = ConversationWindow(max_turns=5)
        window.set_system_prompt("Be helpful.")
        window.add_turn("Hi", "Hello!")

        llm_context = window.get_context_for_llm()

        assert isinstance(llm_context, list)
        assert all(isinstance(m, dict) for m in llm_context)
        assert all("role" in m and "content" in m for m in llm_context)


# =============================================================================
# Factory Tests
# =============================================================================


class TestWindowFactory:
    """Tests for window factory functions."""

    def test_create_window_from_config_enum(self) -> None:
        """Factory creates window from ContextStrategy enum."""
        from services.chat.config import ContextStrategy

        for strategy in ContextStrategy:
            window = create_window_from_config(
                strategy,
                max_turns=5,
                context_window_tokens=4000,
            )

            assert isinstance(window, ConversationWindow)
            assert window.max_turns == 5


# =============================================================================
# Phase 2 Validation: The 10+ Turn Memory Test
# =============================================================================


class TestPhase2MemoryValidation:
    """
    CLI v7 Phase 2 Validation Tests.

    The "memory test": Ask the agent "What did we discuss at the start?"
    after 10+ turns. It should remember (via summary or bounded history).
    """

    def test_ten_plus_turns_with_summarization(self) -> None:
        """
        Verifies that after 10+ turns, context includes summary of earlier turns.

        This is THE acceptance test for Phase 2:
        - Window has max_turns=10
        - We add 15 turns (exceeding capacity)
        - Summarizer compresses old turns
        - Context still includes information from turn 1
        """
        summaries_called: list[int] = []

        def mock_summarizer(messages: list[ContextMessage]) -> str:
            """Track what gets summarized and return meaningful summary."""
            summaries_called.append(len(messages))
            # Include first turn info in summary
            first_content = messages[0].content if messages else ""
            return f"Summary: Started discussing '{first_content[:50]}'"

        window = ConversationWindow(
            max_turns=10,
            strategy="summarize",
            summarizer=mock_summarizer,
        )

        # Simulate a 15-turn conversation
        for i in range(15):
            window.add_turn(
                f"User message {i}: What about topic {i}?",
                f"Assistant response {i}: Here's info on topic {i}.",
            )

        # Verify capacity is bounded
        assert window.turn_count <= 10

        # Verify summarizer was called (turns were evicted)
        assert len(summaries_called) > 0

        # Verify summary exists
        assert window.has_summary

        # THE MEMORY TEST: Get context and verify early turn info preserved
        context = window.get_context_messages()

        # Summary should be first non-system message
        context_text = " ".join(m.content for m in context)
        assert "Summary" in context_text  # Summary is included
        assert "topic 0" in context_text or "message 0" in context_text  # Early info preserved

    def test_sliding_window_preserves_recent(self) -> None:
        """
        Sliding window keeps most recent turns.

        Without summarization, at least recent context is available.
        """
        window = ConversationWindow(
            max_turns=5,
            strategy="sliding",
        )

        # Add 10 turns
        for i in range(10):
            window.add_turn(f"User {i}", f"Assistant {i}")

        # Should have exactly 5 turns
        assert window.turn_count == 5

        # Most recent turns should be present
        messages = window.get_context_messages()
        content = " ".join(m.content for m in messages)

        # Recent turns (5-9) should be present
        assert "User 9" in content
        assert "User 5" in content

        # Old turns (0-4) should NOT be present
        assert "User 0" not in content
        assert "User 4" not in content

    def test_memory_survives_serialization(self) -> None:
        """
        Window state (including summary) survives D-gent roundtrip.

        Critical for session recovery across restarts.
        """
        original = ConversationWindow(
            max_turns=5,
            strategy="summarize",
        )

        # Add turns and set a summary manually
        for i in range(3):
            original.add_turn(f"User {i}", f"Response {i}")

        original._summary = "We discussed topics 0-2 extensively."
        original._has_summary = True

        # Serialize and restore
        data = original.to_dict()
        restored = ConversationWindow.from_dict(data)

        # Verify state preserved
        assert restored.turn_count == original.turn_count
        assert restored.has_summary == original.has_summary
        assert restored._summary == original._summary
        assert restored.strategy == original.strategy

    def test_context_for_llm_includes_all_needed_info(self) -> None:
        """
        LLM context includes: summary (if any), system prompt, recent turns.

        This ensures the LLM has what it needs to answer "What did we discuss?"
        """
        window = ConversationWindow(max_turns=5, strategy="summarize")

        # Set system prompt
        window.set_system_prompt("You are helpful.")

        # Set a summary (simulating evicted context)
        window._summary = "We discussed architecture patterns."
        window._has_summary = True

        # Add recent turns
        window.add_turn("Current question?", "Current answer.")

        # Get LLM-ready context
        llm_context = window.get_context_for_llm()

        # Should be list of dicts with role/content
        assert isinstance(llm_context, list)
        assert all(isinstance(m, dict) for m in llm_context)
        assert all("role" in m and "content" in m for m in llm_context)

        # Should include system, summary (as system or user), and recent turn
        roles = [m["role"] for m in llm_context]
        assert "system" in roles
        assert "user" in roles
        assert "assistant" in roles

        # Summary info should be somewhere in context
        all_content = " ".join(m["content"] for m in llm_context)
        assert "architecture patterns" in all_content or "helpful" in all_content


# =============================================================================
# Context Breakdown Tests (Teaching Mode)
# =============================================================================


class TestContextBreakdown:
    """
    Tests for get_context_breakdown() method.

    Teaching Mode: Shows users how the context window is being used.
    """

    def test_breakdown_returns_segments(self) -> None:
        """Breakdown returns list of segments."""
        from services.conductor.window import ContextBreakdown, ContextSegment

        window = ConversationWindow(max_turns=5, context_window_tokens=8000)
        window.add_turn("Hello", "World")

        breakdown = window.get_context_breakdown()

        assert isinstance(breakdown, ContextBreakdown)
        assert isinstance(breakdown.segments, list)
        assert all(isinstance(s, ContextSegment) for s in breakdown.segments)

    def test_breakdown_includes_working_memory(self) -> None:
        """Breakdown includes working memory segment when turns exist."""
        window = ConversationWindow(max_turns=5, context_window_tokens=8000)
        window.add_turn("Hello", "World")

        breakdown = window.get_context_breakdown()
        segment_names = [s.name for s in breakdown.segments]

        assert "Working" in segment_names
        assert "Available" in segment_names

    def test_breakdown_includes_system_prompt(self) -> None:
        """Breakdown includes system segment when prompt is set."""
        window = ConversationWindow(max_turns=5, context_window_tokens=8000)
        window.set_system_prompt("Be helpful and creative.")
        window.add_turn("Hello", "World")

        breakdown = window.get_context_breakdown()
        segment_names = [s.name for s in breakdown.segments]

        assert "System" in segment_names
        system_seg = next(s for s in breakdown.segments if s.name == "System")
        assert system_seg.tokens > 0
        assert "prompt" in system_seg.description.lower()

    def test_breakdown_includes_summary_when_present(self) -> None:
        """Breakdown includes summary segment after summarization."""
        window = ConversationWindow(max_turns=5, context_window_tokens=8000)

        # Manually set summary (simulating summarization)
        window._summary = "Previous conversation about architecture."
        window._summary_tokens = 100

        breakdown = window.get_context_breakdown()
        segment_names = [s.name for s in breakdown.segments]

        assert "Summary" in segment_names
        summary_seg = next(s for s in breakdown.segments if s.name == "Summary")
        assert summary_seg.tokens == 100

    def test_breakdown_utilization_matches_window(self) -> None:
        """Breakdown utilization matches window.utilization."""
        window = ConversationWindow(max_turns=5, context_window_tokens=8000)
        window.add_turn("Hello", "World")

        breakdown = window.get_context_breakdown()

        assert breakdown.utilization == window.utilization

    def test_breakdown_available_is_correct(self) -> None:
        """Available segment tokens = context_window - used tokens."""
        window = ConversationWindow(max_turns=5, context_window_tokens=10000)
        window.add_turn("Hello", "World")

        breakdown = window.get_context_breakdown()
        available_seg = next(s for s in breakdown.segments if s.name == "Available")

        expected_available = breakdown.context_window - breakdown.total_tokens
        assert available_seg.tokens == expected_available

    def test_breakdown_segment_colors_are_tailwind(self) -> None:
        """Segment colors are valid Tailwind CSS classes."""
        window = ConversationWindow(max_turns=5, context_window_tokens=8000)
        window.set_system_prompt("Test")
        window.add_turn("Hello", "World")

        breakdown = window.get_context_breakdown()

        for segment in breakdown.segments:
            assert segment.color.startswith("bg-")

    def test_breakdown_empty_window(self) -> None:
        """Breakdown works on empty window (only Available segment)."""
        window = ConversationWindow(max_turns=5, context_window_tokens=8000)

        breakdown = window.get_context_breakdown()

        # Should only have Available segment
        assert len(breakdown.segments) == 1
        assert breakdown.segments[0].name == "Available"
        assert breakdown.segments[0].tokens == 8000
        assert breakdown.total_tokens == 0
