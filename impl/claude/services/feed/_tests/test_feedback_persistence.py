"""
Tests for Feed Feedback Persistence.

Verifies:
- Recording user interactions
- Retrieving attention scores
- Computing analytics
"""

from __future__ import annotations

import pytest

from models.base import get_session_factory, init_db
from services.feed.feedback import FeedbackAction
from services.feed.persistence import FeedFeedbackPersistence


@pytest.fixture
async def persistence() -> FeedFeedbackPersistence:
    """Create feed feedback persistence with test database."""
    # Initialize test database
    await init_db()

    # Create persistence with session factory
    session_factory = get_session_factory()
    return FeedFeedbackPersistence(session_factory=session_factory)


@pytest.mark.asyncio
async def test_record_view_interaction(persistence: FeedFeedbackPersistence) -> None:
    """Test recording a view interaction."""
    interaction_id = await persistence.record_interaction(
        user_id="test_user",
        kblock_id="kb_001",
        action=FeedbackAction.VIEW,
        dwell_time_ms=5000,
    )

    assert interaction_id is not None

    # Verify stats were updated
    stats = await persistence.get_interaction_stats("test_user", "kb_001")
    assert stats["views"] == 1
    assert stats["engagements"] == 0
    assert stats["dismissals"] == 0


@pytest.mark.asyncio
async def test_record_engage_interaction(persistence: FeedFeedbackPersistence) -> None:
    """Test recording an engagement interaction."""
    interaction_id = await persistence.record_interaction(
        user_id="test_user",
        kblock_id="kb_002",
        action=FeedbackAction.ENGAGE,
        interaction_type="edit",
    )

    assert interaction_id is not None

    # Verify stats were updated
    stats = await persistence.get_interaction_stats("test_user", "kb_002")
    assert stats["views"] == 0
    assert stats["engagements"] == 1
    assert stats["dismissals"] == 0


@pytest.mark.asyncio
async def test_attention_score_computation(persistence: FeedFeedbackPersistence) -> None:
    """Test attention score computation."""
    # Record multiple interactions
    await persistence.record_interaction(
        user_id="test_user",
        kblock_id="kb_003",
        action=FeedbackAction.VIEW,
    )
    await persistence.record_interaction(
        user_id="test_user",
        kblock_id="kb_003",
        action=FeedbackAction.VIEW,
    )
    await persistence.record_interaction(
        user_id="test_user",
        kblock_id="kb_003",
        action=FeedbackAction.ENGAGE,
    )

    # Get attention score
    score = await persistence.get_attention_score("test_user", "kb_003")

    # Score should be positive (views * 0.5 + engagements * 2) / (total + 1)
    assert score > 0.0
    assert score <= 1.0


@pytest.mark.asyncio
async def test_dismiss_lowers_score(persistence: FeedFeedbackPersistence) -> None:
    """Test that dismissals lower attention score."""
    # Record view and engagement
    await persistence.record_interaction(
        user_id="test_user",
        kblock_id="kb_004",
        action=FeedbackAction.VIEW,
    )
    await persistence.record_interaction(
        user_id="test_user",
        kblock_id="kb_004",
        action=FeedbackAction.ENGAGE,
    )

    score_before = await persistence.get_attention_score("test_user", "kb_004")

    # Record dismissal
    await persistence.record_interaction(
        user_id="test_user",
        kblock_id="kb_004",
        action=FeedbackAction.DISMISS,
    )

    score_after = await persistence.get_attention_score("test_user", "kb_004")

    # Score should decrease after dismissal
    assert score_after < score_before


@pytest.mark.asyncio
async def test_analytics(persistence: FeedFeedbackPersistence) -> None:
    """Test analytics endpoint."""
    # Record interactions for multiple K-Blocks
    for i in range(5):
        kblock_id = f"kb_{100 + i}"
        await persistence.record_interaction(
            user_id="test_user",
            kblock_id=kblock_id,
            action=FeedbackAction.VIEW,
        )
        await persistence.record_interaction(
            user_id="test_user",
            kblock_id=kblock_id,
            action=FeedbackAction.ENGAGE,
        )

    # Get analytics
    analytics = await persistence.get_analytics(limit=10, min_interactions=1)

    assert "most_engaged_kblocks" in analytics
    assert "totals" in analytics
    assert "recent_activity" in analytics

    # Should have 5 K-Blocks in most engaged
    assert len(analytics["most_engaged_kblocks"]) >= 5

    # Totals should reflect recorded interactions
    assert analytics["totals"]["views"] >= 5
    assert analytics["totals"]["engagements"] >= 5
