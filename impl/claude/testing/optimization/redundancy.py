"""
Coverage-Based Redundancy Detection (Type IV Judge).

Uses coverage data to identify redundant tests:
1. Run `pytest --cov` and parse coverage.json
2. Build test -> lines_covered mapping
3. Identify tests with high overlap (potential redundancy)
4. Use semantic analysis to confirm redundancy

Philosophy: "If two tests cover the same code paths with the
same inputs, one is redundant. Keep the faster one."

AGENTESE: self.test.redundancy.lens
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TestCoverage:
    """Coverage data for a single test."""

    test_id: str
    files_covered: set[str] = field(default_factory=set)
    lines_covered: dict[str, set[int]] = field(default_factory=dict)  # file -> lines
    branches_covered: dict[str, set[tuple[int, int]]] = field(default_factory=dict)

    @property
    def total_lines(self) -> int:
        """Total lines covered across all files."""
        return sum(len(lines) for lines in self.lines_covered.values())

    def file_line_set(self) -> set[tuple[str, int]]:
        """Get all (file, line) pairs as a set for overlap calculation."""
        result: set[tuple[str, int]] = set()
        for file, lines in self.lines_covered.items():
            for line in lines:
                result.add((file, line))
        return result


@dataclass
class CoverageOverlap:
    """Coverage overlap between two tests."""

    test_a: str
    test_b: str
    overlap_ratio: float  # 0.0 - 1.0 (Jaccard similarity)
    shared_lines: int
    total_lines_a: int
    total_lines_b: int
    shared_files: set[str] = field(default_factory=set)

    @property
    def is_superset(self) -> bool:
        """True if test_a covers everything test_b covers."""
        return self.shared_lines == self.total_lines_b and self.total_lines_a > self.total_lines_b

    @property
    def is_subset(self) -> bool:
        """True if test_b covers everything test_a covers."""
        return self.shared_lines == self.total_lines_a and self.total_lines_b > self.total_lines_a

    @property
    def is_equivalent(self) -> bool:
        """True if both tests cover the exact same lines."""
        return self.total_lines_a == self.total_lines_b == self.shared_lines

    def __str__(self) -> str:
        relation = ""
        if self.is_equivalent:
            relation = " (EQUIVALENT)"
        elif self.is_superset:
            relation = f" ({self.test_a} ⊃ {self.test_b})"
        elif self.is_subset:
            relation = f" ({self.test_b} ⊃ {self.test_a})"

        return (
            f"{self.test_a} ∩ {self.test_b}: "
            f"{self.overlap_ratio:.1%} overlap, "
            f"{self.shared_lines} shared lines{relation}"
        )


@dataclass
class RedundancyReport:
    """Report of detected redundancies."""

    overlaps: list[CoverageOverlap] = field(default_factory=list)
    equivalent_pairs: list[tuple[str, str]] = field(default_factory=list)
    superset_pairs: list[tuple[str, str]] = field(default_factory=list)  # (larger, smaller)
    total_tests: int = 0

    @property
    def redundant_count(self) -> int:
        """Number of potentially redundant tests."""
        return len(self.equivalent_pairs) + len(self.superset_pairs)

    def summary(self) -> dict[str, Any]:
        """Generate summary statistics."""
        return {
            "total_tests": self.total_tests,
            "high_overlap_pairs": len(self.overlaps),
            "equivalent_pairs": len(self.equivalent_pairs),
            "superset_pairs": len(self.superset_pairs),
            "redundant_count": self.redundant_count,
        }


def compute_overlap(cov_a: TestCoverage, cov_b: TestCoverage) -> CoverageOverlap:
    """
    Compute coverage overlap between two tests.

    Uses Jaccard similarity: |A ∩ B| / |A ∪ B|
    """
    lines_a = cov_a.file_line_set()
    lines_b = cov_b.file_line_set()

    intersection = lines_a & lines_b
    union = lines_a | lines_b

    if not union:
        overlap_ratio = 0.0
    else:
        overlap_ratio = len(intersection) / len(union)

    shared_files = cov_a.files_covered & cov_b.files_covered

    return CoverageOverlap(
        test_a=cov_a.test_id,
        test_b=cov_b.test_id,
        overlap_ratio=overlap_ratio,
        shared_lines=len(intersection),
        total_lines_a=len(lines_a),
        total_lines_b=len(lines_b),
        shared_files=shared_files,
    )


def detect_redundancy(
    coverages: list[TestCoverage],
    threshold: float = 0.9,
) -> RedundancyReport:
    """
    Find tests with high coverage overlap.

    Args:
        coverages: Coverage data for each test
        threshold: Minimum overlap ratio to flag (default 0.9 = 90%)

    Returns:
        RedundancyReport with detected overlaps
    """
    report = RedundancyReport(total_tests=len(coverages))

    # Compare all pairs (O(n^2) but tests are typically < 10k)
    for i, cov_a in enumerate(coverages):
        for cov_b in coverages[i + 1 :]:
            overlap = compute_overlap(cov_a, cov_b)

            if overlap.overlap_ratio >= threshold:
                report.overlaps.append(overlap)

                if overlap.is_equivalent:
                    report.equivalent_pairs.append((overlap.test_a, overlap.test_b))
                elif overlap.is_superset:
                    report.superset_pairs.append((overlap.test_a, overlap.test_b))
                elif overlap.is_subset:
                    report.superset_pairs.append((overlap.test_b, overlap.test_a))

    # Sort by overlap ratio (highest first)
    report.overlaps.sort(key=lambda o: o.overlap_ratio, reverse=True)

    return report


# =============================================================================
# Coverage Data Parsing
# =============================================================================


def parse_coverage_json(path: Path) -> dict[str, TestCoverage]:
    """
    Parse coverage.json from pytest-cov.

    Note: This requires running pytest with coverage per-test tracking:
        pytest --cov --cov-context=test

    The coverage.json format varies by tool. This function supports:
    - pytest-cov with context tracking
    - coverage.py JSON format
    """
    if not path.exists():
        return {}

    with path.open() as f:
        data = json.load(f)

    coverages: dict[str, TestCoverage] = {}

    # Handle coverage.py format with contexts
    if "files" in data:
        # Standard coverage.py JSON format
        for file_path, file_data in data["files"].items():
            # Each line may have context info
            contexts = file_data.get("contexts", {})
            for line_str, context_list in contexts.items():
                line = int(line_str)
                for context in context_list:
                    # Context format: "test_module.py::TestClass::test_method"
                    test_id = context
                    if test_id not in coverages:
                        coverages[test_id] = TestCoverage(test_id=test_id)

                    cov = coverages[test_id]
                    cov.files_covered.add(file_path)
                    if file_path not in cov.lines_covered:
                        cov.lines_covered[file_path] = set()
                    cov.lines_covered[file_path].add(line)

    return coverages


def parse_coverage_from_pytest_cov(coverage_dir: Path) -> dict[str, TestCoverage]:
    """
    Parse coverage data from pytest-cov output directory.

    Looks for:
    - .coverage (SQLite database)
    - coverage.json (if --cov-report=json)
    - htmlcov/coverage.json (HTML report data)
    """
    # Try JSON first (easiest to parse)
    json_path = coverage_dir / "coverage.json"
    if json_path.exists():
        return parse_coverage_json(json_path)

    # Try HTML report
    html_json = coverage_dir / "htmlcov" / "coverage.json"
    if html_json.exists():
        return parse_coverage_json(html_json)

    # TODO: Parse .coverage SQLite database if needed

    return {}


# =============================================================================
# Integration with RefinementTracker
# =============================================================================


def add_redundancy_recommendations(
    report: RedundancyReport,
    tracker: Any,  # RefinementTracker (avoid circular import)
) -> list[Any]:  # OptimizationRecommendation
    """
    Convert redundancy report to optimization recommendations.

    Integrates with the RefinementTracker recommendation system.
    """
    from testing.optimization import OptimizationRecommendation

    recommendations: list[OptimizationRecommendation] = []

    # Equivalent tests - suggest removing one
    for test_a, test_b in report.equivalent_pairs:
        # Check which is faster (if profiles available)
        profile_a = tracker.profiles.get(test_a)
        profile_b = tracker.profiles.get(test_b)

        if profile_a and profile_b:
            faster, slower = (
                (test_a, test_b)
                if profile_a.duration_ms <= profile_b.duration_ms
                else (test_b, test_a)
            )
            recommendations.append(
                OptimizationRecommendation(
                    test_id=slower,
                    action="remove_redundant",
                    rationale=f"Equivalent coverage to {faster} (faster test)",
                    estimated_savings_ms=tracker.profiles[slower].duration_ms,
                    implementation=f"# Consider removing {slower}\n# It has identical coverage to {faster}",
                )
            )
        else:
            recommendations.append(
                OptimizationRecommendation(
                    test_id=test_a,
                    action="review_redundant",
                    rationale=f"Equivalent coverage to {test_b}",
                    estimated_savings_ms=0,
                    implementation=f"# Review: {test_a} and {test_b} have identical coverage",
                )
            )

    # Superset tests - the smaller test may be redundant
    for larger, smaller in report.superset_pairs:
        profile = tracker.profiles.get(smaller)
        savings = profile.duration_ms if profile else 0

        recommendations.append(
            OptimizationRecommendation(
                test_id=smaller,
                action="review_subset",
                rationale=f"All lines covered by {larger}",
                estimated_savings_ms=savings,
                implementation=f"# {smaller} may be redundant\n# {larger} covers all its lines plus more",
            )
        )

    return recommendations


__all__ = [
    "TestCoverage",
    "CoverageOverlap",
    "RedundancyReport",
    "compute_overlap",
    "detect_redundancy",
    "parse_coverage_json",
    "parse_coverage_from_pytest_cov",
    "add_redundancy_recommendations",
]
