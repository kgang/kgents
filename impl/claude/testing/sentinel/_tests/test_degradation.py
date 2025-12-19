"""
Integration tests for graceful degradation tiers.

Philosophy: When resources are constrained, degrade gracefully rather than fail.

Tests verify:
1. Tier fallback: full → reduced → minimal → emergency
2. Resource-based tier selection
3. Skipped checks are correctly reported
4. Time budget constraints
"""

from __future__ import annotations

import pytest

from testing.sentinel import (
    DegradationState,
    DegradationTier,
    determine_degradation_tier,
)


@pytest.mark.sentinel
class TestDegradationTierBasic:
    """Basic tests for degradation tier determination."""

    def test_full_tier_when_all_available(self) -> None:
        """Full tier when all resources available."""
        state = determine_degradation_tier(
            network_available=True,
            database_available=True,
            time_budget_seconds=600.0,
        )

        assert state.tier == DegradationTier.FULL
        assert len(state.skipped_checks) == 0
        assert "All resources available" in state.reason

    def test_full_tier_default_args(self) -> None:
        """Full tier with default arguments."""
        state = determine_degradation_tier()

        assert state.tier == DegradationTier.FULL
        assert len(state.skipped_checks) == 0


@pytest.mark.sentinel
class TestNetworkDegradation:
    """Tests for degradation when network is unavailable."""

    def test_reduced_tier_without_network(self) -> None:
        """Reduced tier when network unavailable."""
        state = determine_degradation_tier(
            network_available=False,
            database_available=True,
            time_budget_seconds=600.0,
        )

        assert state.tier == DegradationTier.REDUCED
        assert "contract" in state.skipped_checks
        assert "e2e" in state.skipped_checks

    def test_network_failure_skips_contract_sync(self) -> None:
        """Network failure should skip contract sync check."""
        state = determine_degradation_tier(network_available=False)

        assert "contract" in state.skipped_checks


@pytest.mark.sentinel
class TestDatabaseDegradation:
    """Tests for degradation when database is unavailable."""

    def test_reduced_tier_without_database(self) -> None:
        """Reduced tier when database unavailable."""
        state = determine_degradation_tier(
            network_available=True,
            database_available=False,
            time_budget_seconds=600.0,
        )

        assert state.tier == DegradationTier.REDUCED
        assert "slow_test" in state.skipped_checks

    def test_database_failure_skips_slow_tests(self) -> None:
        """Database failure should skip slow (persistence) tests."""
        state = determine_degradation_tier(database_available=False)

        assert "slow_test" in state.skipped_checks


@pytest.mark.sentinel
class TestTimeBudgetDegradation:
    """Tests for time budget constraints."""

    def test_minimal_tier_under_2_minutes(self) -> None:
        """Minimal tier when time budget < 120s."""
        state = determine_degradation_tier(time_budget_seconds=90.0)

        assert state.tier == DegradationTier.MINIMAL
        assert "test" in state.skipped_checks
        assert "contract" in state.skipped_checks
        assert "90" in state.reason

    def test_emergency_tier_under_30_seconds(self) -> None:
        """Emergency tier when time budget < 30s."""
        state = determine_degradation_tier(time_budget_seconds=20.0)

        assert state.tier == DegradationTier.EMERGENCY
        assert "typecheck" in state.skipped_checks
        assert "test" in state.skipped_checks
        assert "20" in state.reason

    def test_time_budget_takes_precedence(self) -> None:
        """Time budget constraints take precedence over resource availability."""
        # Even with all resources available, tight time forces emergency
        state = determine_degradation_tier(
            network_available=True,
            database_available=True,
            time_budget_seconds=15.0,
        )

        assert state.tier == DegradationTier.EMERGENCY


@pytest.mark.sentinel
class TestTierFallback:
    """Tests for tier fallback sequence: full → reduced → minimal → emergency."""

    @pytest.mark.parametrize(
        "time_budget,expected_tier",
        [
            (600.0, DegradationTier.FULL),
            (120.0, DegradationTier.FULL),
            (119.0, DegradationTier.MINIMAL),
            (30.0, DegradationTier.MINIMAL),
            (29.0, DegradationTier.EMERGENCY),
            (1.0, DegradationTier.EMERGENCY),
        ],
    )
    def test_time_based_tier_fallback(
        self, time_budget: float, expected_tier: DegradationTier
    ) -> None:
        """Tier correctly falls back based on time budget."""
        state = determine_degradation_tier(time_budget_seconds=time_budget)

        assert state.tier == expected_tier

    def test_combined_resource_failures(self) -> None:
        """Combined resource failures accumulate skipped checks."""
        state = determine_degradation_tier(
            network_available=False,
            database_available=False,
            time_budget_seconds=600.0,  # Enough time, but resources missing
        )

        assert state.tier == DegradationTier.REDUCED
        assert "contract" in state.skipped_checks
        assert "e2e" in state.skipped_checks
        assert "slow_test" in state.skipped_checks


@pytest.mark.sentinel
class TestDegradationStateProperties:
    """Tests for DegradationState properties."""

    def test_full_tier_checks_available(self) -> None:
        """Full tier has all checks available."""
        state = DegradationState(
            tier=DegradationTier.FULL,
            reason="test",
            skipped_checks=(),
        )

        checks = state.checks_available
        assert "lint" in checks
        assert "typecheck" in checks
        assert "test" in checks
        assert "contract" in checks
        assert "slow_test" in checks
        assert "e2e" in checks

    def test_reduced_tier_checks_available(self) -> None:
        """Reduced tier has core checks available."""
        state = DegradationState(
            tier=DegradationTier.REDUCED,
            reason="test",
            skipped_checks=("contract", "e2e"),
        )

        checks = state.checks_available
        assert "lint" in checks
        assert "typecheck" in checks
        assert "test" in checks
        assert "contract" not in checks
        assert "e2e" not in checks

    def test_minimal_tier_checks_available(self) -> None:
        """Minimal tier has only static checks available."""
        state = DegradationState(
            tier=DegradationTier.MINIMAL,
            reason="test",
            skipped_checks=("test", "contract", "slow_test", "e2e"),
        )

        checks = state.checks_available
        assert "lint" in checks
        assert "typecheck" in checks
        assert "test" not in checks

    def test_emergency_tier_checks_available(self) -> None:
        """Emergency tier has only lint available."""
        state = DegradationState(
            tier=DegradationTier.EMERGENCY,
            reason="test",
            skipped_checks=("typecheck", "test", "contract", "slow_test", "e2e"),
        )

        checks = state.checks_available
        assert checks == ("lint",)


@pytest.mark.sentinel
class TestDegradationReasonMessages:
    """Tests for human-readable reason messages."""

    def test_full_tier_reason(self) -> None:
        """Full tier reason indicates all resources available."""
        state = determine_degradation_tier()

        assert "available" in state.reason.lower()

    def test_network_failure_reason(self) -> None:
        """Network failure reason is descriptive."""
        state = determine_degradation_tier(network_available=False)

        assert "unavailable" in state.reason.lower() or "contract" in state.reason.lower()

    def test_time_constraint_reason(self) -> None:
        """Time constraint reason includes the budget."""
        state = determine_degradation_tier(time_budget_seconds=45.0)

        assert "45" in state.reason or "time" in state.reason.lower()


@pytest.mark.sentinel
class TestMockedResourceFailures:
    """Integration tests with mocked resource failures."""

    def test_graceful_degradation_sequence(self) -> None:
        """Test the full degradation sequence."""
        # Start with full
        state1 = determine_degradation_tier(
            network_available=True,
            database_available=True,
            time_budget_seconds=600.0,
        )
        assert state1.tier == DegradationTier.FULL

        # Lose network → reduced
        state2 = determine_degradation_tier(
            network_available=False,
            database_available=True,
            time_budget_seconds=600.0,
        )
        assert state2.tier == DegradationTier.REDUCED

        # Also lose database → still reduced but more skipped
        state3 = determine_degradation_tier(
            network_available=False,
            database_available=False,
            time_budget_seconds=600.0,
        )
        assert state3.tier == DegradationTier.REDUCED
        assert len(state3.skipped_checks) > len(state2.skipped_checks)

        # Time crunch → minimal
        state4 = determine_degradation_tier(
            network_available=False,
            database_available=False,
            time_budget_seconds=60.0,
        )
        assert state4.tier == DegradationTier.MINIMAL

        # Severe time crunch → emergency
        state5 = determine_degradation_tier(
            network_available=False,
            database_available=False,
            time_budget_seconds=10.0,
        )
        assert state5.tier == DegradationTier.EMERGENCY

    def test_degradation_never_blocks_lint(self) -> None:
        """Even in emergency, lint should always be available."""
        # Worst case scenario
        state = determine_degradation_tier(
            network_available=False,
            database_available=False,
            time_budget_seconds=1.0,
        )

        assert state.tier == DegradationTier.EMERGENCY
        assert "lint" in state.checks_available


@pytest.mark.sentinel
class TestEdgeCases:
    """Edge case tests for degradation tiers."""

    def test_zero_time_budget(self) -> None:
        """Zero time budget triggers emergency."""
        state = determine_degradation_tier(time_budget_seconds=0.0)

        assert state.tier == DegradationTier.EMERGENCY

    def test_negative_time_budget(self) -> None:
        """Negative time budget triggers emergency."""
        state = determine_degradation_tier(time_budget_seconds=-10.0)

        assert state.tier == DegradationTier.EMERGENCY

    def test_infinite_time_budget(self) -> None:
        """Infinite time budget uses full tier."""
        state = determine_degradation_tier(time_budget_seconds=float("inf"))

        assert state.tier == DegradationTier.FULL

    def test_boundary_at_30_seconds(self) -> None:
        """Test exact boundary at 30 seconds."""
        # At 30s, should be minimal (not emergency)
        state_at = determine_degradation_tier(time_budget_seconds=30.0)
        assert state_at.tier == DegradationTier.MINIMAL

        # Just under 30s, should be emergency
        state_under = determine_degradation_tier(time_budget_seconds=29.9)
        assert state_under.tier == DegradationTier.EMERGENCY

    def test_boundary_at_120_seconds(self) -> None:
        """Test exact boundary at 120 seconds."""
        # At 120s, should be full
        state_at = determine_degradation_tier(time_budget_seconds=120.0)
        assert state_at.tier == DegradationTier.FULL

        # Just under 120s, should be minimal
        state_under = determine_degradation_tier(time_budget_seconds=119.9)
        assert state_under.tier == DegradationTier.MINIMAL
