"""
Pytest plugin for automatic test profiling and optimization.

This plugin:
1. Collects timing data via pytest hooks
2. Updates RefinementTracker with each test's duration
3. Persists profiles to .kgents/ghost/test_profiles.jsonl
4. Emits recommendations after test runs

Philosophy: "Tests are the executable specification.
A slow test suite is a spec that no one reads."

Usage:
    # Enable profiling
    pytest --profile-tests

    # Run with recommendations
    pytest --profile-tests --show-recommendations

AGENTESE: self.test.optimization.witness
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from testing.optimization import (
    OptimizationRecommendation,
    RefinementTracker,
    TestProfile,
    TestTier,
    recommend_optimizations,
)

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser
    from _pytest.reports import TestReport
    from _pytest.terminal import TerminalReporter

# Default paths
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent  # -> kgents root
_GHOST_DIR = _PROJECT_ROOT / ".kgents" / "ghost"
_PROFILES_PATH = _GHOST_DIR / "test_profiles.jsonl"
_REFINEMENTS_PATH = _GHOST_DIR / "test_refinements.jsonl"


class TestOptimizationPlugin:
    """
    Pytest plugin for automatic test profiling.

    Polynomial structure:
        S = {IDLE, PROFILING, ANALYZING, REPORTING}
        E(s) = test events at each state

    The plugin maintains a refinement tracker that records
    test profiles and suggests optimizations.
    """

    def __init__(self, config: Config) -> None:
        """Initialize the plugin with configuration."""
        self.config = config
        self.enabled = config.getoption("--profile-tests", default=False)
        self.show_recommendations = config.getoption("--show-recommendations", default=False)

        # Initialize tracker with persistence path
        profiles_path = _PROFILES_PATH if self.enabled else None
        self.tracker = RefinementTracker(log_path=profiles_path)

        # Session statistics
        self.test_count = 0
        self.total_duration_ms = 0.0
        self.tier_counts: dict[str, int] = {tier.value: 0 for tier in TestTier}

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        """
        Record test timing data.

        Only processes 'call' phase (actual test execution).
        Setup and teardown are recorded separately.
        """
        if not self.enabled:
            return

        if report.when == "call":
            # Record profile
            profile = self.tracker.record_profile(report.nodeid, report.duration)

            # Update statistics
            self.test_count += 1
            self.total_duration_ms += profile.duration_ms
            self.tier_counts[profile.tier.value] += 1

    def pytest_sessionfinish(self, session: Any, exitstatus: int) -> None:
        """
        Generate recommendations and summary at session end.

        Emits optimization suggestions if slow tests detected.
        """
        if not self.enabled:
            return

        # Get terminal reporter for output
        terminalreporter: TerminalReporter | None = self.config.pluginmanager.get_plugin(
            "terminalreporter"
        )

        if terminalreporter is None:
            return

        # Write section header
        terminalreporter.write_sep("=", "Test Optimization Report")

        # Summary statistics
        avg_duration = self.total_duration_ms / max(self.test_count, 1)
        terminalreporter.write_line(f"Total tests profiled: {self.test_count}")
        terminalreporter.write_line(f"Total duration: {self.total_duration_ms / 1000:.2f}s")
        terminalreporter.write_line(f"Average duration: {avg_duration:.2f}ms")

        # Tier distribution
        terminalreporter.write_line("\nTier distribution:")
        for tier in TestTier:
            count = self.tier_counts[tier.value]
            pct = (count / max(self.test_count, 1)) * 100
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            terminalreporter.write_line(f"  {tier.value:10s} {bar} {count:5d} ({pct:5.1f}%)")

        # Recommendations (if enabled and slow tests found)
        if self.show_recommendations:
            recommendations = recommend_optimizations(self.tracker)

            if recommendations:
                terminalreporter.write_line("\nOptimization recommendations:")
                for rec in recommendations[:10]:  # Top 10
                    terminalreporter.write_line(f"  - {rec}")
            else:
                terminalreporter.write_line(
                    "\nNo optimization recommendations (all tests are fast!)"
                )

        # Expensive tests warning
        expensive = self.tracker.expensive_tests()
        if expensive:
            terminalreporter.write_line(f"\n⚠ {len(expensive)} expensive tests (>30s) detected:")
            for profile in expensive[:5]:  # Top 5
                terminalreporter.write_line(
                    f"  - {profile.test_id}: {profile.duration_ms / 1000:.2f}s"
                )
            if len(expensive) > 5:
                terminalreporter.write_line(f"  ... and {len(expensive) - 5} more")


def pytest_addoption(parser: Parser) -> None:
    """Add test optimization command line options."""
    group = parser.getgroup("optimization", "Test optimization options")

    group.addoption(
        "--profile-tests",
        action="store_true",
        default=False,
        help="Enable automatic test profiling",
    )

    group.addoption(
        "--show-recommendations",
        action="store_true",
        default=False,
        help="Show optimization recommendations after test run",
    )

    group.addoption(
        "--profile-output",
        type=str,
        default=None,
        help="Path to output profiles JSONL (default: .kgents/ghost/test_profiles.jsonl)",
    )


def pytest_configure(config: Config) -> None:
    """Register the optimization plugin."""
    # Only register if profiling is enabled (to minimize overhead)
    if config.getoption("--profile-tests", default=False):
        plugin = TestOptimizationPlugin(config)
        config.pluginmanager.register(plugin, "test_optimization")

    # Register markers
    config.addinivalue_line(
        "markers",
        "optimization(action): mark test with optimization metadata",
    )


# =============================================================================
# Standalone Report Generation
# =============================================================================


def generate_report(profiles_path: Path | None = None) -> str:
    """
    Generate optimization report from stored profiles.

    This can be run standalone:
        python -m testing.optimization.pytest_plugin

    Or via CLI:
        kgents test report
    """
    path = profiles_path or _PROFILES_PATH

    if not path.exists():
        return "No profiles found. Run pytest with --profile-tests first."

    tracker = RefinementTracker(log_path=path)
    summary = tracker.summary()

    lines = [
        "=" * 60,
        "TEST OPTIMIZATION REPORT",
        "=" * 60,
        "",
        f"Total tests: {summary['total_tests']}",
        f"Total refinements: {summary['total_refinements']}",
        f"Time saved: {summary['time_saved_ms'] / 1000:.2f}s",
        "",
        "Tier distribution:",
    ]

    for tier, count in summary["tier_distribution"].items():
        time_ms = summary["tier_time_ms"][tier]
        lines.append(f"  {tier:10s}: {count:5d} tests ({time_ms / 1000:.2f}s)")

    if summary["expensive_tests"]:
        lines.append("")
        lines.append("Expensive tests (>30s):")
        for test in summary["expensive_tests"][:10]:
            lines.append(f"  - {test['test_id']}: {test['duration_ms'] / 1000:.2f}s")

    # Recommendations
    recommendations = recommend_optimizations(tracker)
    if recommendations:
        lines.append("")
        lines.append("Recommendations:")
        for rec in recommendations[:10]:
            lines.append(f"  - [{rec.action}] {rec.test_id}")
            lines.append(f"    {rec.rationale}")
            lines.append(f"    Estimated savings: {rec.estimated_savings_ms / 1000:.2f}s")

    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_report())
