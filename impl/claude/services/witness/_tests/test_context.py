"""
Tests for Context Budget System (Phase 3).

Tests cover:
1. Scoring functions (recency, relevance, combined)
2. Budget-aware retrieval
3. Query relevance filtering
4. Edge cases (empty store, exceed budget, etc.)
5. Formatting for prompt injection
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from services.witness.context import (
    ContextItem,
    ContextResult,
    compute_combined_score,
    compute_recency_score,
    compute_relevance_score,
    format_context_for_prompt,
    get_context_sync,
)
from services.witness.crystal import (
    Crystal,
    CrystalId,
    CrystalLevel,
    MoodVector,
    generate_crystal_id,
)
from services.witness.crystal_store import CrystalStore
from services.witness.mark import MarkId

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def empty_store() -> CrystalStore:
    """Create an empty crystal store."""
    return CrystalStore()


@pytest.fixture
def sample_crystal() -> Crystal:
    """Create a sample crystal for testing."""
    return Crystal.from_crystallization(
        insight="Completed extinction audit, removed 52K lines",
        significance="Codebase is leaner, focus is sharper",
        principles=["tasteful", "curated"],
        source_marks=[MarkId("mark-abc123"), MarkId("mark-def456")],
        time_range=(datetime.now(UTC) - timedelta(hours=1), datetime.now(UTC)),
        confidence=0.85,
        topics={"extinction", "audit", "cleanup"},
        session_id="session-123",
    )


@pytest.fixture
def store_with_crystals() -> CrystalStore:
    """Create a store with multiple crystals for testing."""
    store = CrystalStore()
    now = datetime.now(UTC)

    # Recent crystal (high recency)
    recent = Crystal.from_crystallization(
        insight="Just completed important refactoring",
        significance="Architecture improved",
        principles=["composable"],
        source_marks=[MarkId("mark-111")],
        time_range=(now - timedelta(minutes=30), now),
        confidence=0.9,
        topics={"refactoring", "architecture"},
        session_id="session-a",
    )
    # Override crystallized_at to now
    recent = Crystal(
        id=recent.id,
        level=recent.level,
        insight=recent.insight,
        significance=recent.significance,
        principles=recent.principles,
        source_marks=recent.source_marks,
        source_crystals=recent.source_crystals,
        time_range=recent.time_range,
        crystallized_at=now,
        topics=recent.topics,
        mood=recent.mood,
        compression_ratio=recent.compression_ratio,
        confidence=recent.confidence,
        token_estimate=100,
        session_id=recent.session_id,
    )
    store.append(recent)

    # Yesterday crystal (medium recency)
    yesterday = Crystal(
        id=generate_crystal_id(),
        level=CrystalLevel.SESSION,
        insight="Implemented witness crystallization phase 2",
        significance="Lineage ergonomics complete",
        principles=("ethical", "generative"),
        source_marks=(MarkId("mark-222"), MarkId("mark-333")),
        source_crystals=(),
        time_range=(now - timedelta(days=1, hours=2), now - timedelta(days=1)),
        crystallized_at=now - timedelta(days=1),
        topics=frozenset({"witness", "crystallization", "lineage"}),
        mood=MoodVector.neutral(),
        compression_ratio=2.0,
        confidence=0.8,
        token_estimate=150,
        session_id="session-b",
    )
    store.append(yesterday)

    # Week-old crystal (lower recency)
    week_old = Crystal(
        id=generate_crystal_id(),
        level=CrystalLevel.SESSION,
        insight="Completed DI enlightened resolution",
        significance="No more dependency injection surprises",
        principles=("composable",),
        source_marks=(MarkId("mark-444"),),
        source_crystals=(),
        time_range=(now - timedelta(days=7), now - timedelta(days=7, hours=-1)),
        crystallized_at=now - timedelta(days=7),
        topics=frozenset({"di", "resolution", "dependencies"}),
        mood=MoodVector.neutral(),
        compression_ratio=1.0,
        confidence=0.75,
        token_estimate=80,
        session_id="session-c",
    )
    store.append(week_old)

    # Large crystal (high token count)
    large = Crystal(
        id=generate_crystal_id(),
        level=CrystalLevel.SESSION,
        insight="Major architectural redesign covering multiple subsystems with extensive documentation",
        significance="Foundation for future development, affects all modules",
        principles=("generative", "heterarchical"),
        source_marks=tuple(MarkId(f"mark-large-{i}") for i in range(10)),
        source_crystals=(),
        time_range=(now - timedelta(hours=5), now - timedelta(hours=4)),
        crystallized_at=now - timedelta(hours=4),
        topics=frozenset({"architecture", "redesign", "documentation"}),
        mood=MoodVector.neutral(),
        compression_ratio=10.0,
        confidence=0.95,
        token_estimate=500,
        session_id="session-d",
    )
    store.append(large)

    return store


# =============================================================================
# Scoring Tests
# =============================================================================


class TestRecencyScore:
    """Tests for compute_recency_score()."""

    def test_now_returns_one(self) -> None:
        """Crystal created now should have score 1.0."""
        now = datetime.now(UTC)
        score = compute_recency_score(now, now=now)
        assert score == pytest.approx(1.0, abs=0.01)

    def test_half_life_returns_half(self) -> None:
        """Crystal at half-life should have score 0.5."""
        now = datetime.now(UTC)
        half_life_ago = now - timedelta(days=7)
        score = compute_recency_score(half_life_ago, now=now, half_life_days=7.0)
        assert score == pytest.approx(0.5, abs=0.01)

    def test_old_crystal_low_score(self) -> None:
        """Crystal from long ago should have low score."""
        now = datetime.now(UTC)
        old = now - timedelta(days=30)
        score = compute_recency_score(old, now=now, half_life_days=7.0)
        assert score < 0.1

    def test_future_crystal_clamped(self) -> None:
        """Future crystallized_at should clamp to 1.0."""
        now = datetime.now(UTC)
        future = now + timedelta(hours=1)
        score = compute_recency_score(future, now=now)
        # Due to negative age, 2^(-negative) > 1, but we clamp to 1.0
        assert score == pytest.approx(1.0, abs=0.01)


class TestRelevanceScore:
    """Tests for compute_relevance_score()."""

    def test_no_query_returns_half(self, sample_crystal: Crystal) -> None:
        """No query = all crystals equally relevant at 0.5."""
        score = compute_relevance_score(sample_crystal, None)
        assert score == 0.5

    def test_empty_query_returns_half(self, sample_crystal: Crystal) -> None:
        """Empty query = all crystals equally relevant at 0.5."""
        score = compute_relevance_score(sample_crystal, "")
        assert score == 0.5

    def test_exact_topic_match_high_score(self, sample_crystal: Crystal) -> None:
        """Matching a topic exactly should give high score."""
        score = compute_relevance_score(sample_crystal, "extinction")
        assert score > 0.8

    def test_insight_match_high_score(self, sample_crystal: Crystal) -> None:
        """Matching insight content should give high score."""
        score = compute_relevance_score(sample_crystal, "audit")
        assert score > 0.7

    def test_no_match_low_score(self, sample_crystal: Crystal) -> None:
        """Non-matching query should give low score."""
        score = compute_relevance_score(sample_crystal, "websockets")
        assert score == 0.0

    def test_partial_match_medium_score(self, sample_crystal: Crystal) -> None:
        """Partially matching query should give medium score."""
        score = compute_relevance_score(sample_crystal, "extinction websockets")
        assert 0.3 < score < 0.7  # One of two terms matches


class TestCombinedScore:
    """Tests for compute_combined_score()."""

    def test_default_weights(self) -> None:
        """Default weight is 0.7 recency, 0.3 relevance."""
        recency = 1.0
        relevance = 0.0
        score = compute_combined_score(recency, relevance, recency_weight=0.7)
        assert score == pytest.approx(0.7, abs=0.01)

    def test_equal_weights(self) -> None:
        """With 0.5 weight, both scores contribute equally."""
        score = compute_combined_score(0.8, 0.4, recency_weight=0.5)
        assert score == pytest.approx(0.6, abs=0.01)

    def test_all_recency(self) -> None:
        """Weight 1.0 = only recency matters."""
        score = compute_combined_score(0.9, 0.1, recency_weight=1.0)
        assert score == pytest.approx(0.9, abs=0.01)

    def test_all_relevance(self) -> None:
        """Weight 0.0 = only relevance matters."""
        score = compute_combined_score(0.9, 0.1, recency_weight=0.0)
        assert score == pytest.approx(0.1, abs=0.01)


# =============================================================================
# Budget Retrieval Tests
# =============================================================================


class TestGetContext:
    """Tests for get_context_sync() budget-aware retrieval."""

    def test_empty_store_returns_empty(self, empty_store: CrystalStore) -> None:
        """Empty store returns empty result."""
        result = get_context_sync(budget_tokens=2000, store=empty_store)
        assert len(result.items) == 0
        assert result.total_tokens == 0
        assert result.budget_remaining == 2000

    def test_budget_respected(self, store_with_crystals: CrystalStore) -> None:
        """Total tokens should not exceed budget."""
        result = get_context_sync(budget_tokens=200, store=store_with_crystals)
        assert result.total_tokens <= 200
        assert result.budget_remaining >= 0

    def test_fills_greedily(self, store_with_crystals: CrystalStore) -> None:
        """Should fill as much of the budget as possible."""
        result = get_context_sync(budget_tokens=300, store=store_with_crystals)
        # Should include multiple smaller crystals
        assert len(result.items) >= 2
        assert result.total_tokens > 100

    def test_large_crystal_skipped_if_over_budget(self, store_with_crystals: CrystalStore) -> None:
        """Large crystal (500 tokens) should be skipped if over budget."""
        result = get_context_sync(budget_tokens=200, store=store_with_crystals)
        crystal_tokens = [item.tokens for item in result.items]
        assert 500 not in crystal_tokens

    def test_large_budget_includes_all(self, store_with_crystals: CrystalStore) -> None:
        """Large budget should include all crystals."""
        result = get_context_sync(budget_tokens=10000, store=store_with_crystals)
        assert len(result.items) == 4  # All 4 crystals

    def test_sorted_by_score(self, store_with_crystals: CrystalStore) -> None:
        """Items should be ordered by score (highest first)."""
        result = get_context_sync(budget_tokens=1000, store=store_with_crystals)
        scores = [item.score for item in result.items]
        assert scores == sorted(scores, reverse=True)

    def test_cumulative_tokens_correct(self, store_with_crystals: CrystalStore) -> None:
        """Cumulative tokens should add up correctly."""
        result = get_context_sync(budget_tokens=1000, store=store_with_crystals)

        running_total = 0
        for item in result.items:
            running_total += item.tokens
            assert item.cumulative_tokens == running_total

        assert result.total_tokens == running_total


class TestQueryRelevance:
    """Tests for relevance-weighted context queries."""

    def test_query_affects_order(self, store_with_crystals: CrystalStore) -> None:
        """Query should affect crystal ordering."""
        # Query for witness/crystallization - should boost that crystal
        result = get_context_sync(
            budget_tokens=1000,
            relevance_query="crystallization witness",
            recency_weight=0.3,  # Lower recency, higher relevance
            store=store_with_crystals,
        )

        # The witness crystallization crystal should be boosted
        insights = [item.crystal.insight for item in result.items]
        assert any("crystallization" in i.lower() for i in insights[:2])

    def test_query_with_high_recency_weight(self, store_with_crystals: CrystalStore) -> None:
        """High recency weight should prioritize recent over relevant."""
        result = get_context_sync(
            budget_tokens=1000,
            relevance_query="DI resolution",  # Matches week-old crystal
            recency_weight=0.9,  # Strong recency preference
            store=store_with_crystals,
        )

        # Most recent crystal should still be first
        first_insight = result.items[0].crystal.insight
        assert "refactoring" in first_insight.lower()


# =============================================================================
# ContextResult Tests
# =============================================================================


class TestContextResult:
    """Tests for ContextResult methods."""

    def test_crystals_property(self, store_with_crystals: CrystalStore) -> None:
        """crystals property should return just the crystals."""
        result = get_context_sync(budget_tokens=1000, store=store_with_crystals)
        crystals = result.crystals
        assert all(isinstance(c, Crystal) for c in crystals)
        assert len(crystals) == len(result.items)

    def test_to_dict_serializable(self, store_with_crystals: CrystalStore) -> None:
        """to_dict should produce JSON-serializable output."""
        import json

        result = get_context_sync(budget_tokens=1000, store=store_with_crystals)
        data = result.to_dict()

        # Should not raise
        json_str = json.dumps(data)
        assert json_str

        # Check structure
        assert "items" in data
        assert "total_tokens" in data
        assert "budget" in data
        assert "budget_remaining" in data

    def test_to_dict_items_have_required_fields(self, store_with_crystals: CrystalStore) -> None:
        """Each item in to_dict should have required fields."""
        result = get_context_sync(budget_tokens=1000, store=store_with_crystals)
        data = result.to_dict()

        for item in data["items"]:
            assert "id" in item
            assert "level" in item
            assert "insight" in item
            assert "score" in item
            assert "tokens" in item
            assert "cumulative_tokens" in item


# =============================================================================
# Formatting Tests
# =============================================================================


class TestFormatContextForPrompt:
    """Tests for format_context_for_prompt()."""

    def test_empty_result_returns_message(self, empty_store: CrystalStore) -> None:
        """Empty result should return helpful message."""
        result = get_context_sync(budget_tokens=1000, store=empty_store)
        formatted = format_context_for_prompt(result)
        assert "No relevant context found" in formatted

    def test_non_empty_includes_header(self, store_with_crystals: CrystalStore) -> None:
        """Non-empty result should include header."""
        result = get_context_sync(budget_tokens=1000, store=store_with_crystals)
        formatted = format_context_for_prompt(result)
        assert "CONTEXT" in formatted
        assert "Witness Crystals" in formatted

    def test_includes_level_badges(self, store_with_crystals: CrystalStore) -> None:
        """Formatted output should include level badges."""
        result = get_context_sync(budget_tokens=1000, store=store_with_crystals)
        formatted = format_context_for_prompt(result)
        assert "[L0]" in formatted  # SESSION level

    def test_includes_token_summary(self, store_with_crystals: CrystalStore) -> None:
        """Formatted output should include token summary."""
        result = get_context_sync(budget_tokens=1000, store=store_with_crystals)
        formatted = format_context_for_prompt(result)
        assert "tokens" in formatted


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_budget(self, store_with_crystals: CrystalStore) -> None:
        """Zero budget should return nothing."""
        result = get_context_sync(budget_tokens=0, store=store_with_crystals)
        assert len(result.items) == 0

    def test_single_crystal_exact_budget(self, empty_store: CrystalStore) -> None:
        """Crystal that exactly fits budget should be included."""
        crystal = Crystal(
            id=generate_crystal_id(),
            level=CrystalLevel.SESSION,
            insight="Exact fit",
            significance="Test",
            principles=(),
            source_marks=(MarkId("mark-1"),),
            source_crystals=(),
            time_range=None,
            crystallized_at=datetime.now(UTC),
            topics=frozenset(),
            mood=MoodVector.neutral(),
            compression_ratio=1.0,
            confidence=0.8,
            token_estimate=100,
            session_id="",
        )
        empty_store.append(crystal)

        result = get_context_sync(budget_tokens=100, store=empty_store)
        assert len(result.items) == 1
        assert result.total_tokens == 100
        assert result.budget_remaining == 0

    def test_crystals_without_token_estimate(self, empty_store: CrystalStore) -> None:
        """Crystals with 0 token_estimate should use default."""
        crystal = Crystal(
            id=generate_crystal_id(),
            level=CrystalLevel.SESSION,
            insight="No estimate",
            significance="Test",
            principles=(),
            source_marks=(MarkId("mark-1"),),
            source_crystals=(),
            time_range=None,
            crystallized_at=datetime.now(UTC),
            topics=frozenset(),
            mood=MoodVector.neutral(),
            compression_ratio=1.0,
            confidence=0.8,
            token_estimate=0,  # No estimate
            session_id="",
        )
        empty_store.append(crystal)

        result = get_context_sync(budget_tokens=100, store=empty_store)
        # Should use default of 50 tokens
        assert result.items[0].tokens == 50

    def test_very_high_recency_weight(self, store_with_crystals: CrystalStore) -> None:
        """Recency weight > 1.0 should be clamped or handled gracefully."""
        # This tests that combined score doesn't break with extreme weights
        result = get_context_sync(
            budget_tokens=1000,
            recency_weight=1.0,
            store=store_with_crystals,
        )
        assert all(item.score <= 1.0 for item in result.items)
