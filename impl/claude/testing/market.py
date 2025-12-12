"""
The Market: Portfolio-Optimized Test Scheduling.

Philosophy: Treat tests as assets in a portfolio. Invest budget where
"volatility" (uncertainty) is highest to maximize information gain.

Research Basis:
- Shannon Information Theory (1948)
- Kelly Criterion (Kelly, "A New Interpretation of Information Rate", 1956)
- Portfolio Theory (Markowitz)

Phase 8.3 - Economics:
- TestAsset: Tests as financial assets
- TestMarket: Kelly-optimal allocation
- Budget tiers for different contexts
"""

import math
from dataclasses import dataclass
from typing import Any, Callable

# =============================================================================
# Core Types
# =============================================================================


@dataclass
class TestCost:
    """Cost of running a test in various dimensions."""

    joules: float  # Compute cost (abstract energy unit)
    time_ms: float  # Expected duration
    tokens: int = 0  # LLM tokens if applicable

    def __add__(self, other: "TestCost") -> "TestCost":
        return TestCost(
            joules=self.joules + other.joules,
            time_ms=self.time_ms + other.time_ms,
            tokens=self.tokens + other.tokens,
        )


@dataclass
class TestAsset:
    """A test treated as a financial asset.

    Higher surprise_if_fail means more valuable information.
    """

    test_id: str
    cost: TestCost

    # Historical statistics
    historical_pass_rate: float = 0.95  # Default: mostly passes
    volatility: float = 0.1  # Standard deviation of outcomes
    last_failure_days: float = 30.0  # Days since last failure

    # Graph metrics (from dependency analysis)
    dependency_centrality: float = 0.5  # How central in import graph
    code_churn: float = 0.1  # How often touched code changes

    @property
    def expected_information_gain(self) -> float:
        """Shannon entropy of outcome distribution.

        Maximum when p=0.5 (most uncertain).
        """
        p = self.historical_pass_rate
        if p <= 0 or p >= 1:
            return 0.0
        return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))

    @property
    def surprise_if_fail(self) -> float:
        """KL divergence if this stable test fails.

        Higher for tests that rarely fail (more surprising).
        """
        p = self.historical_pass_rate
        if p >= 0.99:
            return 100.0  # Very surprising if stable test fails
        if p >= 1.0:
            return 0.0
        # -log2(1-p) = information content of failure event
        return -math.log2(1 - p)

    @property
    def roi(self) -> float:
        """Return on investment: expected info gain per joule."""
        if self.cost.joules <= 0:
            return 0.0
        return self.expected_information_gain / self.cost.joules


# =============================================================================
# Budget Allocation
# =============================================================================


@dataclass
class BudgetTier:
    """Budget configuration for a testing context."""

    name: str
    total_joules: float
    strategy: str  # "kelly", "impact", "full", "adversarial"
    description: str


# Standard budget tiers
BUDGET_TIERS = {
    "dev": BudgetTier(
        name="dev",
        total_joules=1_000,
        strategy="kelly",
        description="Development: Quick feedback, maximize surprise",
    ),
    "pr": BudgetTier(
        name="pr",
        total_joules=5_000,
        strategy="impact",
        description="Pull Request: Focus on changed code impact",
    ),
    "main": BudgetTier(
        name="main",
        total_joules=50_000,
        strategy="kelly",
        description="Main branch: Full Kelly + rebalancing",
    ),
    "release": BudgetTier(
        name="release",
        total_joules=float("inf"),
        strategy="full",
        description="Release: Everything + adversarial testing",
    ),
}


# =============================================================================
# The Market
# =============================================================================


class TestMarket:
    """Portfolio-optimized test scheduler using Kelly Criterion.

    The Market doesn't run tests randomly - it invests in tests
    that maximize expected information gain.
    """

    def __init__(self, budget_tier: str = "dev"):
        """Initialize Test Market.

        Args:
            budget_tier: One of "dev", "pr", "main", "release"
        """
        self.tier = BUDGET_TIERS.get(budget_tier, BUDGET_TIERS["dev"])
        self._assets: dict[str, TestAsset] = {}
        self._allocations: dict[str, float] = {}

    def register_test(self, asset: TestAsset) -> None:
        """Register a test as an asset."""
        self._assets[asset.test_id] = asset

    def update_statistics(
        self,
        test_id: str,
        passed: bool,
        duration_ms: float,
    ) -> None:
        """Update test statistics after a run."""
        if test_id not in self._assets:
            return

        asset = self._assets[test_id]

        # Update pass rate (exponential moving average)
        alpha = 0.1  # Learning rate
        new_outcome = 1.0 if passed else 0.0
        asset.historical_pass_rate = (
            alpha * new_outcome + (1 - alpha) * asset.historical_pass_rate
        )

        # Update last failure
        if not passed:
            asset.last_failure_days = 0.0

        # Update cost estimate
        asset.cost.time_ms = alpha * duration_ms + (1 - alpha) * asset.cost.time_ms

    async def calculate_kelly_allocation(
        self,
        assets: list[TestAsset] | None = None,
        total_budget: float | None = None,
    ) -> dict[str, float]:
        """Calculate optimal budget allocation per test using Kelly Criterion.

        Kelly formula: f* = (p * b - q) / b

        Where:
            f* = fraction of budget to allocate
            p  = probability of finding a bug
            b  = reward if bug found (impact × centrality)
            q  = probability of no bug (1 - p)

        Args:
            assets: Tests to allocate for (defaults to all registered)
            total_budget: Total budget (defaults to tier budget)

        Returns:
            Dictionary mapping test_id to joule allocation
        """
        if assets is None:
            assets = list(self._assets.values())
        if total_budget is None:
            total_budget = self.tier.total_joules

        allocations: dict[str, float] = {}

        for asset in assets:
            # Kelly fraction
            p = 1 - asset.historical_pass_rate  # P(finding bug)
            b = asset.surprise_if_fail * asset.dependency_centrality
            q = asset.historical_pass_rate

            if b > 0:
                kelly_fraction = max(0, (p * b - q) / b)
            else:
                kelly_fraction = 0

            # Constrain to reasonable bounds
            kelly_fraction = min(kelly_fraction, 0.25)  # Never bet >25% on one test

            allocations[asset.test_id] = kelly_fraction

        # Normalize to total budget
        total_fraction = sum(allocations.values())
        if total_fraction > 0:
            for test_id in allocations:
                allocations[test_id] = (
                    allocations[test_id] / total_fraction
                ) * total_budget

        self._allocations = allocations
        return allocations

    async def prioritize_by_surprise(
        self,
        tests: list[Callable[[], Any]] | None = None,
        test_assets: list[TestAsset] | None = None,
        budget: float | None = None,
    ) -> list[str]:
        """Select tests maximizing expected surprise (information gain).

        Args:
            tests: Test functions to select from (deprecated, use test_assets)
            test_assets: Test assets to select from
            budget: Total budget (defaults to tier budget)

        Returns:
            List of test_ids to run, ordered by priority
        """
        if budget is None:
            budget = self.tier.total_joules

        if test_assets is None:
            test_assets = list(self._assets.values())

        allocations = await self.calculate_kelly_allocation(test_assets, budget)

        # Sort by allocation (highest first)
        sorted_tests = sorted(
            test_assets,
            key=lambda a: allocations.get(a.test_id, 0),
            reverse=True,
        )

        # Greedy selection within budget
        selected = []
        remaining = budget

        for asset in sorted_tests:
            if asset.cost.joules <= remaining:
                selected.append(asset.test_id)
                remaining -= asset.cost.joules

        return selected

    async def rebalance_portfolio(
        self,
        new_evidence: list[tuple[str, bool]],
    ) -> dict[str, float]:
        """Rebalance after observing new test results (Bayesian update).

        Args:
            new_evidence: List of (test_id, passed) tuples

        Returns:
            Updated allocations
        """
        updated = self._allocations.copy()

        for test_id, passed in new_evidence:
            if test_id not in updated:
                continue

            asset = self._assets.get(test_id)
            if not asset:
                continue

            if not passed:
                # Failed test: increase its allocation (it's valuable!)
                surprise = asset.surprise_if_fail
                updated[test_id] *= 1 + surprise * 0.1
            else:
                # Passed test: slight decrease
                updated[test_id] *= 0.95

        # Renormalize
        total = sum(updated.values())
        if total > 0:
            budget = self.tier.total_joules
            updated = {k: (v / total) * budget for k, v in updated.items()}

        self._allocations = updated
        return updated


# =============================================================================
# Impact-Based Allocation
# =============================================================================


@dataclass
class ImpactWeight:
    """Weight for impact-based allocation."""

    file_path: str
    lines_changed: int
    risk_score: float  # From static analysis

    @property
    def impact(self) -> float:
        """Total impact score."""
        return self.lines_changed * self.risk_score


class ImpactAllocator:
    """Allocate budget based on code change impact.

    Used for PR context where we want to focus on changed code.
    """

    def __init__(self, budget: float):
        self.budget = budget
        self._impacts: dict[str, float] = {}  # file -> impact score
        self._test_coverage: dict[str, list[str]] = {}  # test_id -> [files]

    def set_file_impact(self, file_path: str, impact: float) -> None:
        """Set impact score for a file."""
        self._impacts[file_path] = impact

    def set_test_coverage(self, test_id: str, files: list[str]) -> None:
        """Set which files a test covers."""
        self._test_coverage[test_id] = files

    async def allocate(self, assets: list[TestAsset]) -> dict[str, float]:
        """Allocate budget based on impact.

        Tests covering higher-impact files get more budget.
        """
        allocations: dict[str, float] = {}

        for asset in assets:
            covered_files = self._test_coverage.get(asset.test_id, [])
            total_impact = sum(self._impacts.get(f, 0.1) for f in covered_files)
            allocations[asset.test_id] = total_impact

        # Normalize to budget
        total = sum(allocations.values())
        if total > 0:
            allocations = {k: (v / total) * self.budget for k, v in allocations.items()}

        return allocations


# =============================================================================
# Budget Manager
# =============================================================================


class BudgetManager:
    """Unified budget manager for different testing contexts.

    Switches between strategies based on context.
    """

    def __init__(self) -> None:
        self._markets: dict[str, TestMarket] = {
            tier: TestMarket(tier) for tier in BUDGET_TIERS
        }
        self._current_tier = "dev"

    def set_tier(self, tier: str) -> None:
        """Set the current budget tier."""
        if tier in BUDGET_TIERS:
            self._current_tier = tier

    @property
    def market(self) -> TestMarket:
        """Get the current market."""
        return self._markets[self._current_tier]

    def register_test(self, asset: TestAsset) -> None:
        """Register test in all markets."""
        for market in self._markets.values():
            market.register_test(asset)

    async def select_tests(
        self,
        available_tests: list[TestAsset],
        changed_files: list[str] | None = None,
    ) -> list[str]:
        """Select tests based on current tier strategy.

        Args:
            available_tests: All available test assets
            changed_files: Files that changed (for impact-based selection)

        Returns:
            List of test_ids to run
        """
        tier = BUDGET_TIERS[self._current_tier]
        market = self.market

        if tier.strategy == "kelly":
            return await market.prioritize_by_surprise(test_assets=available_tests)

        elif tier.strategy == "impact" and changed_files:
            # Impact-based: prioritize tests covering changed files
            allocator = ImpactAllocator(tier.total_joules)
            for f in changed_files:
                allocator.set_file_impact(f, 1.0)

            allocations = await allocator.allocate(available_tests)
            sorted_tests = sorted(
                available_tests,
                key=lambda a: allocations.get(a.test_id, 0),
                reverse=True,
            )
            return [a.test_id for a in sorted_tests]

        elif tier.strategy == "full":
            # Run everything
            return [a.test_id for a in available_tests]

        elif tier.strategy == "adversarial":
            # Run everything + mark for Red Team
            return [a.test_id for a in available_tests]

        return await market.prioritize_by_surprise(test_assets=available_tests)


# =============================================================================
# Report Generation
# =============================================================================


@dataclass
class MarketReport:
    """Report from market allocation."""

    tier: str
    total_budget: float
    tests_selected: int
    tests_skipped: int
    expected_coverage: float
    allocations: dict[str, float]


def format_market_report(report: MarketReport) -> str:
    """Format market report for display."""
    lines = [
        "=" * 60,
        "               MARKET ALLOCATION REPORT                 ",
        "=" * 60,
        f" Tier: {report.tier}",
        f" Budget: {report.total_budget:.0f} J",
        f" Tests Selected: {report.tests_selected}",
        f" Tests Skipped: {report.tests_skipped}",
        f" Expected Coverage: {report.expected_coverage:.1%}",
        "-" * 60,
        " TOP ALLOCATIONS:",
    ]

    # Show top 10 allocations
    sorted_allocs = sorted(
        report.allocations.items(), key=lambda x: x[1], reverse=True
    )[:10]

    for test_id, joules in sorted_allocs:
        pct = joules / report.total_budget * 100 if report.total_budget > 0 else 0
        lines.append(f"   {test_id}: {joules:.1f} J ({pct:.1f}%)")

    lines.append("=" * 60)
    return "\n".join(lines)
