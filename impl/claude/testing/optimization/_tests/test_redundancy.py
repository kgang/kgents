"""
Tests for coverage-based redundancy detection.

Verifies:
1. TestCoverage data structure
2. Overlap computation (Jaccard similarity)
3. Redundancy detection with threshold
4. Integration with RefinementTracker
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from testing.optimization import RefinementTracker
from testing.optimization.redundancy import (
    CoverageOverlap,
    RedundancyReport,
    TestCoverage,
    add_redundancy_recommendations,
    compute_overlap,
    detect_redundancy,
)


class TestTestCoverage:
    """Tests for TestCoverage data structure."""

    def test_total_lines(self) -> None:
        """Computes total lines across files."""
        cov = TestCoverage(
            test_id="test_foo",
            lines_covered={
                "a.py": {1, 2, 3},
                "b.py": {10, 20},
            },
        )

        assert cov.total_lines == 5

    def test_file_line_set(self) -> None:
        """Generates (file, line) pairs."""
        cov = TestCoverage(
            test_id="test_foo",
            lines_covered={
                "a.py": {1, 2},
                "b.py": {10},
            },
        )

        line_set = cov.file_line_set()

        assert ("a.py", 1) in line_set
        assert ("a.py", 2) in line_set
        assert ("b.py", 10) in line_set
        assert len(line_set) == 3

    def test_empty_coverage(self) -> None:
        """Handles empty coverage data."""
        cov = TestCoverage(test_id="test_empty")

        assert cov.total_lines == 0
        assert cov.file_line_set() == set()


class TestComputeOverlap:
    """Tests for overlap computation."""

    def test_identical_coverage(self) -> None:
        """100% overlap for identical coverage."""
        cov_a = TestCoverage(
            test_id="test_a",
            files_covered={"a.py"},
            lines_covered={"a.py": {1, 2, 3}},
        )
        cov_b = TestCoverage(
            test_id="test_b",
            files_covered={"a.py"},
            lines_covered={"a.py": {1, 2, 3}},
        )

        overlap = compute_overlap(cov_a, cov_b)

        assert overlap.overlap_ratio == 1.0
        assert overlap.shared_lines == 3
        assert overlap.is_equivalent

    def test_no_overlap(self) -> None:
        """0% overlap for disjoint coverage."""
        cov_a = TestCoverage(
            test_id="test_a",
            files_covered={"a.py"},
            lines_covered={"a.py": {1, 2, 3}},
        )
        cov_b = TestCoverage(
            test_id="test_b",
            files_covered={"b.py"},
            lines_covered={"b.py": {10, 20, 30}},
        )

        overlap = compute_overlap(cov_a, cov_b)

        assert overlap.overlap_ratio == 0.0
        assert overlap.shared_lines == 0

    def test_partial_overlap(self) -> None:
        """Correct ratio for partial overlap."""
        cov_a = TestCoverage(
            test_id="test_a",
            files_covered={"a.py"},
            lines_covered={"a.py": {1, 2, 3, 4}},  # 4 lines
        )
        cov_b = TestCoverage(
            test_id="test_b",
            files_covered={"a.py"},
            lines_covered={"a.py": {3, 4, 5, 6}},  # 4 lines, 2 shared
        )

        overlap = compute_overlap(cov_a, cov_b)

        # Jaccard: |A ∩ B| / |A ∪ B| = 2 / 6 = 0.333...
        assert abs(overlap.overlap_ratio - (2 / 6)) < 0.001
        assert overlap.shared_lines == 2

    def test_superset_detection(self) -> None:
        """Detects when one test covers a superset."""
        cov_a = TestCoverage(
            test_id="test_a",
            files_covered={"a.py"},
            lines_covered={"a.py": {1, 2, 3, 4, 5}},  # 5 lines
        )
        cov_b = TestCoverage(
            test_id="test_b",
            files_covered={"a.py"},
            lines_covered={"a.py": {2, 3, 4}},  # 3 lines, all in A
        )

        overlap = compute_overlap(cov_a, cov_b)

        assert overlap.is_superset  # A ⊃ B
        assert not overlap.is_subset

    def test_subset_detection(self) -> None:
        """Detects when one test covers a subset."""
        cov_a = TestCoverage(
            test_id="test_a",
            files_covered={"a.py"},
            lines_covered={"a.py": {2, 3}},  # 2 lines
        )
        cov_b = TestCoverage(
            test_id="test_b",
            files_covered={"a.py"},
            lines_covered={"a.py": {1, 2, 3, 4}},  # 4 lines, includes all of A
        )

        overlap = compute_overlap(cov_a, cov_b)

        assert overlap.is_subset  # B ⊃ A
        assert not overlap.is_superset

    def test_shared_files(self) -> None:
        """Tracks shared files correctly."""
        cov_a = TestCoverage(
            test_id="test_a",
            files_covered={"a.py", "b.py"},
            lines_covered={"a.py": {1}, "b.py": {1}},
        )
        cov_b = TestCoverage(
            test_id="test_b",
            files_covered={"b.py", "c.py"},
            lines_covered={"b.py": {1}, "c.py": {1}},
        )

        overlap = compute_overlap(cov_a, cov_b)

        assert overlap.shared_files == {"b.py"}


class TestDetectRedundancy:
    """Tests for redundancy detection."""

    def test_no_redundancy(self) -> None:
        """No overlaps below threshold."""
        coverages = [
            TestCoverage(
                test_id="test_a",
                files_covered={"a.py"},
                lines_covered={"a.py": {1, 2, 3}},
            ),
            TestCoverage(
                test_id="test_b",
                files_covered={"b.py"},
                lines_covered={"b.py": {10, 20, 30}},
            ),
        ]

        report = detect_redundancy(coverages, threshold=0.9)

        assert len(report.overlaps) == 0
        assert len(report.equivalent_pairs) == 0
        assert len(report.superset_pairs) == 0

    def test_equivalent_tests(self) -> None:
        """Detects equivalent tests."""
        coverages = [
            TestCoverage(
                test_id="test_a",
                files_covered={"a.py"},
                lines_covered={"a.py": {1, 2, 3}},
            ),
            TestCoverage(
                test_id="test_b",
                files_covered={"a.py"},
                lines_covered={"a.py": {1, 2, 3}},  # Same coverage
            ),
        ]

        report = detect_redundancy(coverages, threshold=0.9)

        assert len(report.equivalent_pairs) == 1
        assert ("test_a", "test_b") in report.equivalent_pairs

    def test_superset_detection(self) -> None:
        """Detects superset relationships."""
        coverages = [
            TestCoverage(
                test_id="test_large",
                files_covered={"a.py"},
                lines_covered={"a.py": {1, 2, 3, 4, 5}},
            ),
            TestCoverage(
                test_id="test_small",
                files_covered={"a.py"},
                lines_covered={"a.py": {2, 3, 4}},  # Subset
            ),
        ]

        report = detect_redundancy(coverages, threshold=0.5)  # Lower threshold

        assert len(report.superset_pairs) == 1
        # Superset pairs are (larger, smaller)
        assert ("test_large", "test_small") in report.superset_pairs

    def test_threshold_filtering(self) -> None:
        """Only reports overlaps above threshold."""
        coverages = [
            TestCoverage(
                test_id="test_a",
                files_covered={"a.py"},
                lines_covered={"a.py": {1, 2, 3, 4}},
            ),
            TestCoverage(
                test_id="test_b",
                files_covered={"a.py"},
                lines_covered={"a.py": {3, 4, 5, 6}},  # 50% overlap
            ),
        ]

        # High threshold - no results
        report_high = detect_redundancy(coverages, threshold=0.9)
        assert len(report_high.overlaps) == 0

        # Low threshold - should find it
        report_low = detect_redundancy(coverages, threshold=0.3)
        assert len(report_low.overlaps) == 1

    def test_summary(self) -> None:
        """Summary includes correct counts."""
        coverages = [
            TestCoverage(test_id=f"test_{i}", lines_covered={"a.py": {i}})
            for i in range(5)
        ]

        report = detect_redundancy(coverages, threshold=0.9)

        summary = report.summary()
        assert summary["total_tests"] == 5


class TestRedundancyRecommendations:
    """Tests for integrating redundancy with recommendations."""

    def test_equivalent_recommendation(self) -> None:
        """Recommends removing slower equivalent test."""
        tracker = RefinementTracker()
        tracker.record_profile("test_fast", 0.1)  # 100ms
        tracker.record_profile("test_slow", 0.5)  # 500ms

        report = RedundancyReport(
            equivalent_pairs=[("test_fast", "test_slow")],
            total_tests=2,
        )

        recommendations = add_redundancy_recommendations(report, tracker)

        assert len(recommendations) == 1
        rec = recommendations[0]
        assert rec.test_id == "test_slow"  # Slower one flagged
        assert rec.action == "remove_redundant"
        assert rec.estimated_savings_ms == 500.0

    def test_superset_recommendation(self) -> None:
        """Recommends reviewing subset test."""
        tracker = RefinementTracker()
        tracker.record_profile("test_large", 1.0)
        tracker.record_profile("test_small", 0.2)  # 200ms

        report = RedundancyReport(
            superset_pairs=[("test_large", "test_small")],
            total_tests=2,
        )

        recommendations = add_redundancy_recommendations(report, tracker)

        assert len(recommendations) == 1
        rec = recommendations[0]
        assert rec.test_id == "test_small"
        assert rec.action == "review_subset"

    def test_no_profile_recommendation(self) -> None:
        """Creates review recommendation when no profiles."""
        tracker = RefinementTracker()  # No profiles

        report = RedundancyReport(
            equivalent_pairs=[("test_a", "test_b")],
            total_tests=2,
        )

        recommendations = add_redundancy_recommendations(report, tracker)

        assert len(recommendations) == 1
        rec = recommendations[0]
        assert rec.action == "review_redundant"  # Can't determine which is faster
        assert rec.estimated_savings_ms == 0


class TestCoverageOverlapStr:
    """Tests for CoverageOverlap string representation."""

    def test_basic_str(self) -> None:
        """Basic overlap string."""
        overlap = CoverageOverlap(
            test_a="test_a",
            test_b="test_b",
            overlap_ratio=0.75,
            shared_lines=30,
            total_lines_a=40,
            total_lines_b=40,
        )

        s = str(overlap)

        assert "test_a" in s
        assert "test_b" in s
        assert "75" in s  # 75%
        assert "30" in s  # shared lines

    def test_equivalent_str(self) -> None:
        """String shows EQUIVALENT for identical coverage."""
        overlap = CoverageOverlap(
            test_a="test_a",
            test_b="test_b",
            overlap_ratio=1.0,
            shared_lines=30,
            total_lines_a=30,
            total_lines_b=30,
        )

        s = str(overlap)

        assert "EQUIVALENT" in s

    def test_superset_str(self) -> None:
        """String shows superset relation."""
        overlap = CoverageOverlap(
            test_a="test_large",
            test_b="test_small",
            overlap_ratio=0.6,
            shared_lines=20,
            total_lines_a=30,
            total_lines_b=20,
        )

        s = str(overlap)

        assert "⊃" in s  # Superset symbol
