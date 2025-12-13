"""
Test Optimization Framework: Categorical approach to test performance.

This module provides:
1. TestTier functor: Partitions tests by execution cost
2. RefinementTracker: Tracks optimization changes over time
3. CacheStrategy: Memoization patterns for expensive operations

Philosophy (from spec/principles.md):
- Generative: Track refinements, enable regeneration of optimized config
- Composable: Optimizers compose via >> operator
- Transparent: All changes recorded in refinement log

The framework models test optimization as a polynomial functor:

    TestOptimizer: PolyAgent[OptimizationState, TestSuite, OptimizedSuite]

    where OptimizationState = { PROFILING, PARTITIONING, CACHING, PARALLELIZING }
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any


class OptimizationPhase(Enum):
    """Optimization polynomial positions (states)."""

    PROFILING = auto()  # Collecting timing data
    PARTITIONING = auto()  # Tiering tests by cost
    CACHING = auto()  # Adding memoization
    PARALLELIZING = auto()  # Distributing across workers


class TestTier(Enum):
    """Test cost tiers (from CI workflow structure)."""

    INSTANT = "instant"  # < 100ms
    FAST = "fast"  # 100ms - 1s
    MEDIUM = "medium"  # 1s - 5s
    SLOW = "slow"  # 5s - 30s
    EXPENSIVE = "expensive"  # > 30s (should be cached/mocked)


@dataclass
class TestProfile:
    """Profile data for a single test."""

    test_id: str  # pytest nodeid
    duration_ms: float
    tier: TestTier
    root_cause: str | None = None  # Why is it slow?
    optimization: str | None = None  # Applied optimization
    last_profiled: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_duration(cls, test_id: str, duration_s: float) -> TestProfile:
        """Create profile from duration, auto-assigning tier."""
        duration_ms = duration_s * 1000
        if duration_ms < 100:
            tier = TestTier.INSTANT
        elif duration_ms < 1000:
            tier = TestTier.FAST
        elif duration_ms < 5000:
            tier = TestTier.MEDIUM
        elif duration_ms < 30000:
            tier = TestTier.SLOW
        else:
            tier = TestTier.EXPENSIVE
        return cls(test_id=test_id, duration_ms=duration_ms, tier=tier)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSONL storage."""
        return {
            "type": "profile",
            "test_id": self.test_id,
            "duration_ms": self.duration_ms,
            "tier": self.tier.value,
            "root_cause": self.root_cause,
            "optimization": self.optimization,
            "last_profiled": self.last_profiled.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TestProfile:
        """Deserialize from JSONL storage."""
        return cls(
            test_id=data["test_id"],
            duration_ms=data["duration_ms"],
            tier=TestTier(data["tier"]),
            root_cause=data.get("root_cause"),
            optimization=data.get("optimization"),
            last_profiled=datetime.fromisoformat(data["last_profiled"]),
        )


@dataclass
class Refinement:
    """Single optimization refinement (atomic change)."""

    timestamp: datetime
    test_id: str | None  # None = global change
    action: str  # e.g., "mark_slow", "add_cache", "mock_expensive"
    before_ms: float | None
    after_ms: float | None
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSONL."""
        return {
            "ts": self.timestamp.isoformat(),
            "test_id": self.test_id,
            "action": self.action,
            "before_ms": self.before_ms,
            "after_ms": self.after_ms,
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Refinement:
        """Deserialize from JSONL."""
        return cls(
            timestamp=datetime.fromisoformat(data["ts"]),
            test_id=data["test_id"],
            action=data["action"],
            before_ms=data["before_ms"],
            after_ms=data["after_ms"],
            rationale=data["rationale"],
        )


class RefinementTracker:
    """
    Tracks test optimization refinements over time.

    Implements the "track changing refinements" requirement by:
    1. Recording each optimization change
    2. Computing aggregate metrics (total time saved)
    3. Persisting history for regeneration

    AGENTESE: self.test.optimization.witness
    """

    def __init__(self, log_path: Path | None = None) -> None:
        """
        Initialize tracker.

        Args:
            log_path: Path to JSONL refinement log. If None, uses in-memory only.
        """
        self.log_path = log_path
        self.refinements: list[Refinement] = []
        self.profiles: dict[str, TestProfile] = {}

        if log_path and log_path.exists():
            self._load_log()

    def _load_log(self) -> None:
        """Load existing refinements and profiles from JSONL."""
        if not self.log_path:
            return
        with self.log_path.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    # Discriminate by type field
                    if data.get("type") == "profile":
                        profile = TestProfile.from_dict(data)
                        self.profiles[profile.test_id] = profile
                    else:
                        # Legacy format or refinement
                        self.refinements.append(Refinement.from_dict(data))

    def _append_log(self, refinement: Refinement) -> None:
        """Append refinement to JSONL log."""
        if not self.log_path:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a") as f:
            f.write(json.dumps(refinement.to_dict()) + "\n")

    def _append_profile(self, profile: TestProfile) -> None:
        """Append profile to JSONL log."""
        if not self.log_path:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a") as f:
            f.write(json.dumps(profile.to_dict()) + "\n")

    def record_profile(self, test_id: str, duration_s: float) -> TestProfile:
        """Record test profile from timing data."""
        profile = TestProfile.from_duration(test_id, duration_s)
        self.profiles[test_id] = profile
        self._append_profile(profile)
        return profile

    def record_refinement(
        self,
        test_id: str | None,
        action: str,
        rationale: str,
        before_ms: float | None = None,
        after_ms: float | None = None,
    ) -> Refinement:
        """
        Record an optimization refinement.

        Args:
            test_id: Specific test, or None for global change
            action: What was done (e.g., "mark_slow", "add_fixture_cache")
            rationale: Why (categorical reasoning preferred)
            before_ms: Duration before optimization
            after_ms: Duration after optimization
        """
        refinement = Refinement(
            timestamp=datetime.now(timezone.utc),
            test_id=test_id,
            action=action,
            before_ms=before_ms,
            after_ms=after_ms,
            rationale=rationale,
        )
        self.refinements.append(refinement)
        self._append_log(refinement)
        return refinement

    def total_time_saved_ms(self) -> float:
        """Compute total time saved by all refinements."""
        total = 0.0
        for r in self.refinements:
            if r.before_ms is not None and r.after_ms is not None:
                total += r.before_ms - r.after_ms
        return total

    def expensive_tests(self) -> list[TestProfile]:
        """Get tests in EXPENSIVE tier (candidates for optimization)."""
        return [p for p in self.profiles.values() if p.tier == TestTier.EXPENSIVE]

    def slow_tests(self) -> list[TestProfile]:
        """Get tests in SLOW or EXPENSIVE tier."""
        return [
            p
            for p in self.profiles.values()
            if p.tier in (TestTier.SLOW, TestTier.EXPENSIVE)
        ]

    def summary(self) -> dict[str, Any]:
        """Generate optimization summary."""
        tier_counts = {tier.value: 0 for tier in TestTier}
        tier_time = {tier.value: 0.0 for tier in TestTier}

        for profile in self.profiles.values():
            tier_counts[profile.tier.value] += 1
            tier_time[profile.tier.value] += profile.duration_ms

        return {
            "total_tests": len(self.profiles),
            "total_refinements": len(self.refinements),
            "time_saved_ms": self.total_time_saved_ms(),
            "tier_distribution": tier_counts,
            "tier_time_ms": tier_time,
            "expensive_tests": [
                {"test_id": p.test_id, "duration_ms": p.duration_ms}
                for p in self.expensive_tests()
            ],
        }


# =============================================================================
# Optimization Recommendations (from spec/principles.md §7 Generative)
# =============================================================================


@dataclass
class OptimizationRecommendation:
    """A recommended optimization action."""

    test_id: str
    action: str
    rationale: str
    estimated_savings_ms: float
    implementation: str  # Code snippet or description

    def __str__(self) -> str:
        return f"[{self.action}] {self.test_id}: {self.rationale} (saves ~{self.estimated_savings_ms:.0f}ms)"


def recommend_optimizations(
    tracker: RefinementTracker,
) -> list[OptimizationRecommendation]:
    """
    Generate optimization recommendations from profile data.

    Uses categorical reasoning:
    - EXPENSIVE tests: Mock external calls, cache results
    - SLOW tests: Mark @pytest.mark.slow, parallelize
    - Redundant tests: Identify via coverage overlap (Type IV Judge)
    """
    recommendations: list[OptimizationRecommendation] = []

    for profile in tracker.expensive_tests():
        # Recommend marking as slow to exclude from default runs
        recommendations.append(
            OptimizationRecommendation(
                test_id=profile.test_id,
                action="mark_slow",
                rationale="Test exceeds 30s threshold; should not run on every push",
                estimated_savings_ms=profile.duration_ms * 0.9,  # 90% savings
                implementation=f"@pytest.mark.slow\nasync def {profile.test_id.split('::')[-1]}(): ...",
            )
        )

        # If test involves trace analysis, recommend caching
        if "trace" in profile.test_id.lower() or "analysis" in profile.test_id.lower():
            recommendations.append(
                OptimizationRecommendation(
                    test_id=profile.test_id,
                    action="cache_static_analysis",
                    rationale="Static analysis is expensive; cache results across tests",
                    estimated_savings_ms=profile.duration_ms * 0.85,
                    implementation="Use @pytest.fixture(scope='module') for trace analysis results",
                )
            )

    return recommendations


__all__ = [
    # Core types
    "OptimizationPhase",
    "TestTier",
    "TestProfile",
    "Refinement",
    "RefinementTracker",
    "OptimizationRecommendation",
    "recommend_optimizations",
    # Submodules (lazy import to avoid dependencies at import time):
    # - pytest_plugin: Pytest integration for automatic profiling
    # - redundancy: Coverage-based redundancy detection
    # - partition: Categorical test partitioning (operad-based)
    # - flux: Self-improving test suite (FluxAgent integration)
    # - dashboard: Test health dashboard panel
]
