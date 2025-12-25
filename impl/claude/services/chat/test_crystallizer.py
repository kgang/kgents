"""
Tests for Chat Crystallizer: Automatic Evidence Capture.

Tests the integration of chat sessions with witness marks and K-Blocks.
"""

import pytest

from services.witness import get_mark_store, reset_mark_store

from .context import LinearityTag
from .crystallizer import (
    CRYSTALLIZATION_TURN_THRESHOLD,
    SIGNIFICANCE_THRESHOLD,
    ChatCrystallizer,
)
from .session import ChatSession, generate_session_id


@pytest.fixture
def mark_store():
    """Provide a fresh mark store for each test."""
    reset_mark_store()
    return get_mark_store()


@pytest.fixture
def crystallizer(mark_store):
    """Provide a crystallizer with test mark store."""
    return ChatCrystallizer(mark_store=mark_store)


@pytest.fixture
def simple_session():
    """Create a simple session with a few turns."""
    session = ChatSession(id=generate_session_id())
    session.add_turn("Hello", "Hi there!")
    session.add_turn("How are you?", "I'm doing well.")
    return session


@pytest.fixture
def significant_session():
    """Create a session that should trigger crystallization."""
    session = ChatSession(id=generate_session_id())

    # Add enough turns to exceed threshold
    for i in range(CRYSTALLIZATION_TURN_THRESHOLD + 2):
        user_msg = f"Question {i}: Can you help me with a detailed implementation?"
        assistant_msg = (
            f"Certainly! Here's a comprehensive response for question {i}. "
            "Let me explain in detail with code examples:\n\n"
            "```python\n"
            "def example_function():\n"
            "    # Implementation details here\n"
            "    pass\n"
            "```\n\n"
            "This demonstrates the pattern we discussed. "
            "Additional context and explanation follows..."
        )
        session.add_turn(user_msg, assistant_msg)

    return session


# =============================================================================
# Significance Computation Tests
# =============================================================================


def test_compute_significance_simple(crystallizer, simple_session):
    """Test significance computation for simple session."""
    score = crystallizer.compute_significance(simple_session)

    # Simple session should have low score
    assert score < SIGNIFICANCE_THRESHOLD
    # Score may be zero for very simple sessions (< threshold turns)


def test_compute_significance_long_conversation(crystallizer, significant_session):
    """Test significance computation for long conversation."""
    score = crystallizer.compute_significance(significant_session)

    # Long session with code should have high score
    assert score >= SIGNIFICANCE_THRESHOLD


def test_significance_turn_count_contribution(crystallizer):
    """Test that turn count contributes to significance."""
    # Create two sessions with different turn counts
    short_session = ChatSession(id=generate_session_id())
    for i in range(5):
        short_session.add_turn(f"Question {i}", f"Answer {i}")

    long_session = ChatSession(id=generate_session_id())
    for i in range(15):
        long_session.add_turn(f"Question {i}", f"Answer {i}")

    short_score = crystallizer.compute_significance(short_session)
    long_score = crystallizer.compute_significance(long_session)

    # Long session should score higher
    assert long_score > short_score


def test_significance_code_block_contribution(crystallizer):
    """Test that code blocks increase significance."""
    # Session without code
    no_code_session = ChatSession(id=generate_session_id())
    for i in range(CRYSTALLIZATION_TURN_THRESHOLD + 1):
        no_code_session.add_turn(f"Question {i}", f"Answer {i} with some text")

    # Session with code blocks
    code_session = ChatSession(id=generate_session_id())
    for i in range(CRYSTALLIZATION_TURN_THRESHOLD + 1):
        code_session.add_turn(
            f"Question {i}",
            f"Answer {i}\n```python\ndef func():\n    pass\n```"
        )

    no_code_score = crystallizer.compute_significance(no_code_session)
    code_score = crystallizer.compute_significance(code_session)

    # Code session should score higher
    assert code_score > no_code_score


# =============================================================================
# Crystallization Decision Tests
# =============================================================================


def test_should_crystallize_below_threshold(crystallizer, simple_session):
    """Test that simple session doesn't trigger crystallization."""
    should, score, reason = crystallizer.should_crystallize(simple_session)

    assert not should
    assert "threshold" in reason.lower()


def test_should_crystallize_significant(crystallizer, significant_session):
    """Test that significant session triggers crystallization."""
    should, score, reason = crystallizer.should_crystallize(significant_session)

    assert should
    assert score >= SIGNIFICANCE_THRESHOLD
    assert "significant" in reason.lower()


def test_minimum_turns_required(crystallizer):
    """Test that minimum turn count is enforced."""
    # Session with high quality but too few turns
    session = ChatSession(id=generate_session_id())
    for i in range(CRYSTALLIZATION_TURN_THRESHOLD - 1):
        # Even with code, should not crystallize due to turn count
        session.add_turn(
            f"Question {i}",
            f"Detailed answer {i}\n```python\ncode here\n```" * 10
        )

    should, score, reason = crystallizer.should_crystallize(session)

    assert not should
    assert "turn threshold" in reason.lower()


# =============================================================================
# Crystallization Process Tests
# =============================================================================


@pytest.mark.asyncio
async def test_maybe_crystallize_insignificant(crystallizer, simple_session):
    """Test that insignificant session is not crystallized."""
    result = await crystallizer.maybe_crystallize(simple_session)

    assert result is None


@pytest.mark.asyncio
async def test_maybe_crystallize_significant(crystallizer, significant_session, mark_store):
    """Test full crystallization of significant session."""
    # Count marks before
    marks_before = len(list(mark_store.all()))

    # Crystallize
    result = await crystallizer.maybe_crystallize(significant_session)

    # Should have result
    assert result is not None
    assert result.k_block_id
    assert result.mark_id
    assert result.evidence_id
    assert result.turn_count == significant_session.turn_count
    assert result.significance_score >= SIGNIFICANCE_THRESHOLD

    # Should have created witness mark
    marks_after = len(list(mark_store.all()))
    assert marks_after == marks_before + 1

    # Verify mark details
    mark = mark_store.get(result.mark_id)
    assert mark is not None
    assert mark.origin == "chat.crystallizer"
    assert "crystallization" in mark.tags
    assert "exploration-proof" in mark.tags
    assert mark.metadata["session_id"] == significant_session.id
    assert mark.metadata["k_block_id"] == result.k_block_id


@pytest.mark.asyncio
async def test_crystallization_creates_kblock(crystallizer, significant_session):
    """Test that crystallization creates a K-Block with conversation."""
    result = await crystallizer.maybe_crystallize(significant_session)

    assert result is not None

    # K-Block should contain conversation turns
    # We can't easily verify K-Block content without cosmos integration,
    # but we can verify the result has the expected structure
    assert result.summary
    assert "exploration" in result.summary.lower()


@pytest.mark.asyncio
async def test_crystallization_creates_evidence(crystallizer, significant_session):
    """Test that crystallization creates evidence record."""
    result = await crystallizer.maybe_crystallize(significant_session)

    assert result is not None
    assert result.evidence_id

    # Evidence ID should be well-formed (starts with "evd-")
    assert result.evidence_id.startswith("evd-")


@pytest.mark.asyncio
async def test_crystallization_proof_structure(crystallizer, significant_session, mark_store):
    """Test that witness mark has proper Toulmin proof structure."""
    result = await crystallizer.maybe_crystallize(significant_session)
    mark = mark_store.get(result.mark_id)

    # Should have proof
    assert mark.proof is not None

    # Proof should be empirical (based on measurements)
    from services.witness import EvidenceTier
    assert mark.proof.tier == EvidenceTier.EMPIRICAL

    # Should reference principles
    assert "evidence-driven" in mark.proof.principles or "exploration" in mark.proof.principles

    # Should have complete Toulmin structure
    assert mark.proof.data
    assert mark.proof.warrant
    assert mark.proof.claim


@pytest.mark.asyncio
async def test_multiple_crystallizations(crystallizer, mark_store):
    """Test that multiple sessions can be crystallized independently."""
    # Create two significant sessions with enough content
    session1 = ChatSession(id=generate_session_id())
    for i in range(CRYSTALLIZATION_TURN_THRESHOLD + 2):
        session1.add_turn(
            f"Question {i}: Detailed query with lots of content",
            f"Answer {i}: " + ("Very detailed response. " * 50) + "\n```code\n```"
        )

    session2 = ChatSession(id=generate_session_id())
    for i in range(CRYSTALLIZATION_TURN_THRESHOLD + 2):
        session2.add_turn(
            f"Question {i}: Another detailed query with lots of content",
            f"Answer {i}: " + ("Very detailed response. " * 50) + "\n```code\n```"
        )

    # Crystallize both
    result1 = await crystallizer.maybe_crystallize(session1)
    result2 = await crystallizer.maybe_crystallize(session2)

    # Both should succeed
    assert result1 is not None
    assert result2 is not None

    # Should have different IDs
    assert result1.k_block_id != result2.k_block_id
    assert result1.mark_id != result2.mark_id
    assert result1.evidence_id != result2.evidence_id

    # Should have two marks
    marks = list(mark_store.all())
    assert len(marks) == 2


# =============================================================================
# Summary Generation Tests
# =============================================================================


def test_generate_summary_from_first_message(crystallizer):
    """Test that summary is generated from first user message."""
    session = ChatSession(id=generate_session_id())
    session.add_turn("This is a test question about implementation", "Response")

    summary = crystallizer._generate_summary(session)

    assert "test question" in summary.lower()
    assert "exploration" in summary.lower()


def test_generate_summary_truncates_long_messages(crystallizer):
    """Test that long first messages are truncated."""
    session = ChatSession(id=generate_session_id())
    long_message = "A" * 200
    session.add_turn(long_message, "Response")

    summary = crystallizer._generate_summary(session)

    # Should be truncated with ellipsis
    assert len(summary) < 200
    assert summary.endswith("...")


def test_generate_summary_empty_session(crystallizer):
    """Test summary generation for empty session."""
    session = ChatSession(id=generate_session_id())

    summary = crystallizer._generate_summary(session)

    # Should still have a summary
    assert summary
    assert session.id in summary
