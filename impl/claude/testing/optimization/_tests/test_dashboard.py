"""
Tests for test health dashboard integration.

Verifies:
1. TestHealthMetrics data structure
2. Metrics collection from profiles
3. Demo metrics generation
4. Panel rendering
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from testing.optimization import RefinementTracker, TestTier
from testing.optimization.dashboard import (
    TestHealthMetrics,
    collect_test_health_metrics,
    create_demo_test_metrics,
)


class TestTestHealthMetrics:
    """Tests for TestHealthMetrics data structure."""

    def test_status_healthy(self) -> None:
        """Healthy status when no issues."""
        metrics = TestHealthMetrics(
            total_tests=100,
            pass_rate=1.0,
            recommendation_count=0,
            expensive_test_count=0,
            is_online=True,
        )

        assert metrics.status_text == "HEALTHY"

    def test_status_optimizable(self) -> None:
        """Optimizable status when recommendations exist."""
        metrics = TestHealthMetrics(
            total_tests=100,
            recommendation_count=5,
            is_online=True,
        )

        assert metrics.status_text == "OPTIMIZABLE"

    def test_status_needs_work(self) -> None:
        """Needs work status when many expensive tests."""
        metrics = TestHealthMetrics(
            total_tests=100,
            expensive_test_count=10,
            is_online=True,
        )

        assert metrics.status_text == "NEEDS WORK"

    def test_status_failing(self) -> None:
        """Failing status when pass rate low."""
        metrics = TestHealthMetrics(
            total_tests=100,
            pass_rate=0.90,
            is_online=True,
        )

        assert metrics.status_text == "FAILING"

    def test_status_no_data(self) -> None:
        """No data status when offline."""
        metrics = TestHealthMetrics(is_online=False)

        assert metrics.status_text == "NO DATA"


class TestCollectMetrics:
    """Tests for metrics collection."""

    @pytest.mark.asyncio
    async def test_collect_missing_file(self) -> None:
        """Returns offline metrics when file missing."""
        metrics = await collect_test_health_metrics(Path("/nonexistent/profiles.jsonl"))

        assert not metrics.is_online
        assert metrics.total_tests == 0

    @pytest.mark.asyncio
    async def test_collect_empty_profiles(self) -> None:
        """Returns offline metrics when no profiles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "profiles.jsonl"
            path.touch()  # Empty file

            metrics = await collect_test_health_metrics(path)

            assert not metrics.is_online

    @pytest.mark.asyncio
    async def test_collect_with_profiles(self) -> None:
        """Collects metrics from profile data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "profiles.jsonl"

            # Create tracker and add profiles
            tracker = RefinementTracker(log_path=path)
            tracker.record_profile("test_instant", 0.05)
            tracker.record_profile("test_fast", 0.3)
            tracker.record_profile("test_slow", 10.0)

            # Collect metrics
            metrics = await collect_test_health_metrics(path)

            assert metrics.is_online
            assert metrics.total_tests == 3
            assert metrics.tier_counts["instant"] == 1
            assert metrics.tier_counts["fast"] == 1
            assert metrics.tier_counts["slow"] == 1

    @pytest.mark.asyncio
    async def test_collect_with_expensive(self) -> None:
        """Identifies expensive tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "profiles.jsonl"

            tracker = RefinementTracker(log_path=path)
            tracker.record_profile("test_fast", 0.1)
            tracker.record_profile("test_expensive", 45.0)

            metrics = await collect_test_health_metrics(path)

            assert metrics.expensive_test_count == 1
            assert len(metrics.expensive_tests) == 1
            assert metrics.expensive_tests[0]["test_id"] == "test_expensive"

    @pytest.mark.asyncio
    async def test_collect_generates_recommendations(self) -> None:
        """Generates recommendations for expensive tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "profiles.jsonl"

            tracker = RefinementTracker(log_path=path)
            tracker.record_profile("test_trace_expensive", 45.0)

            metrics = await collect_test_health_metrics(path)

            # Should have recommendations for expensive test
            assert metrics.recommendation_count > 0
            assert len(metrics.top_recommendations) > 0


class TestDemoMetrics:
    """Tests for demo metrics generation."""

    def test_demo_metrics_structure(self) -> None:
        """Demo metrics have expected structure."""
        metrics = create_demo_test_metrics()

        assert metrics.is_online
        assert metrics.total_tests > 0
        assert metrics.pass_rate > 0
        assert len(metrics.tier_counts) == 5
        assert "instant" in metrics.tier_counts
        assert "fast" in metrics.tier_counts

    def test_demo_metrics_tier_distribution(self) -> None:
        """Demo metrics have realistic tier distribution."""
        metrics = create_demo_test_metrics()

        # Most tests should be instant/fast
        total = sum(metrics.tier_counts.values())
        instant_fast = metrics.tier_counts["instant"] + metrics.tier_counts["fast"]

        assert instant_fast / total > 0.8  # >80% should be instant/fast

    def test_demo_metrics_has_recommendations(self) -> None:
        """Demo metrics include sample recommendations."""
        metrics = create_demo_test_metrics()

        assert metrics.recommendation_count > 0
        assert len(metrics.top_recommendations) > 0

    def test_demo_metrics_has_expensive(self) -> None:
        """Demo metrics include expensive tests."""
        metrics = create_demo_test_metrics()

        assert metrics.expensive_test_count > 0
        assert len(metrics.expensive_tests) > 0


class TestMetricsTierPercentages:
    """Tests for tier percentage calculations."""

    @pytest.mark.asyncio
    async def test_tier_percentages(self) -> None:
        """Tier percentages sum to 100."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "profiles.jsonl"

            tracker = RefinementTracker(log_path=path)
            for i in range(10):
                tracker.record_profile(f"test_instant_{i}", 0.05)
            for i in range(5):
                tracker.record_profile(f"test_fast_{i}", 0.3)

            metrics = await collect_test_health_metrics(path)

            total_pct = sum(metrics.tier_percentages.values())
            assert abs(total_pct - 100.0) < 0.1  # Allow small rounding error

    @pytest.mark.asyncio
    async def test_tier_percentages_correct(self) -> None:
        """Tier percentages are correct."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "profiles.jsonl"

            tracker = RefinementTracker(log_path=path)
            # 8 instant, 2 fast = 80% instant, 20% fast
            for i in range(8):
                tracker.record_profile(f"test_instant_{i}", 0.05)
            for i in range(2):
                tracker.record_profile(f"test_fast_{i}", 0.3)

            metrics = await collect_test_health_metrics(path)

            assert abs(metrics.tier_percentages["instant"] - 80.0) < 0.1
            assert abs(metrics.tier_percentages["fast"] - 20.0) < 0.1
