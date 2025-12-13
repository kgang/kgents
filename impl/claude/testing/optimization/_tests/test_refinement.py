"""
Tests for test optimization framework.

Verifies:
1. TestProfile tier assignment
2. RefinementTracker logging and metrics
3. Recommendation generation
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from testing.optimization import (
    OptimizationPhase,
    OptimizationRecommendation,
    Refinement,
    RefinementTracker,
    TestProfile,
    TestTier,
    recommend_optimizations,
)


class TestTestTier:
    """Tests for TestTier enum."""

    def test_tier_values(self) -> None:
        """All tiers have expected values."""
        assert TestTier.INSTANT.value == "instant"
        assert TestTier.FAST.value == "fast"
        assert TestTier.MEDIUM.value == "medium"
        assert TestTier.SLOW.value == "slow"
        assert TestTier.EXPENSIVE.value == "expensive"


class TestTestProfile:
    """Tests for TestProfile dataclass."""

    def test_from_duration_instant(self) -> None:
        """Instant tier for < 100ms."""
        profile = TestProfile.from_duration("test_quick", 0.05)
        assert profile.tier == TestTier.INSTANT
        assert profile.duration_ms == 50.0

    def test_from_duration_fast(self) -> None:
        """Fast tier for 100ms - 1s."""
        profile = TestProfile.from_duration("test_fast", 0.5)
        assert profile.tier == TestTier.FAST

    def test_from_duration_medium(self) -> None:
        """Medium tier for 1s - 5s."""
        profile = TestProfile.from_duration("test_medium", 3.0)
        assert profile.tier == TestTier.MEDIUM

    def test_from_duration_slow(self) -> None:
        """Slow tier for 5s - 30s."""
        profile = TestProfile.from_duration("test_slow", 15.0)
        assert profile.tier == TestTier.SLOW

    def test_from_duration_expensive(self) -> None:
        """Expensive tier for > 30s."""
        profile = TestProfile.from_duration("test_expensive", 45.0)
        assert profile.tier == TestTier.EXPENSIVE


class TestRefinement:
    """Tests for Refinement dataclass."""

    def test_to_dict_and_back(self) -> None:
        """Round-trip serialization."""
        from datetime import datetime, timezone

        original = Refinement(
            timestamp=datetime.now(timezone.utc),
            test_id="test_foo",
            action="mark_slow",
            before_ms=35000,
            after_ms=0,
            rationale="Too expensive for CI",
        )

        data = original.to_dict()
        restored = Refinement.from_dict(data)

        assert restored.test_id == original.test_id
        assert restored.action == original.action
        assert restored.before_ms == original.before_ms
        assert restored.after_ms == original.after_ms
        assert restored.rationale == original.rationale


class TestRefinementTracker:
    """Tests for RefinementTracker."""

    def test_record_profile(self) -> None:
        """Recording a profile assigns tier."""
        tracker = RefinementTracker()

        profile = tracker.record_profile("test_fast", 0.3)

        assert profile.tier == TestTier.FAST
        assert "test_fast" in tracker.profiles

    def test_record_refinement(self) -> None:
        """Recording refinement adds to history."""
        tracker = RefinementTracker()

        refinement = tracker.record_refinement(
            test_id="test_slow",
            action="mark_slow",
            rationale="Exclude from CI",
            before_ms=35000,
            after_ms=0,
        )

        assert len(tracker.refinements) == 1
        assert refinement.action == "mark_slow"

    def test_total_time_saved(self) -> None:
        """Computes total time saved across refinements."""
        tracker = RefinementTracker()

        tracker.record_refinement(
            test_id="test_1",
            action="mark_slow",
            rationale="Slow",
            before_ms=30000,
            after_ms=0,
        )
        tracker.record_refinement(
            test_id="test_2",
            action="add_cache",
            rationale="Cacheable",
            before_ms=5000,
            after_ms=500,
        )

        # 30000 + 4500 = 34500
        assert tracker.total_time_saved_ms() == 34500.0

    def test_expensive_tests_filter(self) -> None:
        """expensive_tests returns only EXPENSIVE tier."""
        tracker = RefinementTracker()

        tracker.record_profile("test_fast", 0.3)
        tracker.record_profile("test_slow", 10.0)
        tracker.record_profile("test_expensive", 45.0)

        expensive = tracker.expensive_tests()

        assert len(expensive) == 1
        assert expensive[0].test_id == "test_expensive"

    def test_slow_tests_filter(self) -> None:
        """slow_tests returns SLOW and EXPENSIVE tiers."""
        tracker = RefinementTracker()

        tracker.record_profile("test_fast", 0.3)
        tracker.record_profile("test_slow", 10.0)
        tracker.record_profile("test_expensive", 45.0)

        slow = tracker.slow_tests()

        assert len(slow) == 2

    def test_summary(self) -> None:
        """summary generates expected structure."""
        tracker = RefinementTracker()

        tracker.record_profile("test_fast", 0.3)
        tracker.record_profile("test_expensive", 45.0)

        summary = tracker.summary()

        assert summary["total_tests"] == 2
        assert "tier_distribution" in summary
        assert summary["tier_distribution"]["expensive"] == 1

    def test_persistence(self) -> None:
        """Refinements persist to JSONL file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "refinements.jsonl"

            # Create tracker and record
            tracker1 = RefinementTracker(log_path=log_path)
            tracker1.record_refinement(
                test_id="test_foo",
                action="mark_slow",
                rationale="Persistent",
            )

            # Create new tracker - should load from file
            tracker2 = RefinementTracker(log_path=log_path)

            assert len(tracker2.refinements) == 1
            assert tracker2.refinements[0].test_id == "test_foo"


class TestRecommendations:
    """Tests for recommendation generation."""

    def test_recommend_mark_slow(self) -> None:
        """Recommends marking expensive tests as slow."""
        tracker = RefinementTracker()
        tracker.record_profile("test_expensive", 45.0)

        recommendations = recommend_optimizations(tracker)

        # Should recommend mark_slow
        actions = [r.action for r in recommendations]
        assert "mark_slow" in actions

    def test_recommend_cache_for_trace(self) -> None:
        """Recommends caching for trace analysis tests."""
        tracker = RefinementTracker()
        tracker.record_profile("test_trace_analysis", 45.0)

        recommendations = recommend_optimizations(tracker)

        # Should recommend caching
        actions = [r.action for r in recommendations]
        assert "cache_static_analysis" in actions

    def test_no_recommendations_for_fast_tests(self) -> None:
        """No recommendations for fast tests."""
        tracker = RefinementTracker()
        tracker.record_profile("test_quick", 0.05)

        recommendations = recommend_optimizations(tracker)

        assert len(recommendations) == 0


class TestOptimizationPhase:
    """Tests for OptimizationPhase enum."""

    def test_all_phases_defined(self) -> None:
        """All expected phases exist."""
        phases = list(OptimizationPhase)

        assert len(phases) == 4
        assert OptimizationPhase.PROFILING in phases
        assert OptimizationPhase.PARTITIONING in phases
        assert OptimizationPhase.CACHING in phases
        assert OptimizationPhase.PARALLELIZING in phases
