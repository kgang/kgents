"""
Tests for budget probes.
"""

import pytest

from services.probe.budget import BudgetProbe
from services.probe.types import ProbeStatus, ProbeType


class MockHarnessWithBudget:
    """Mock harness with budget tracking."""

    def __init__(self, remaining: int, total: int):
        self.name = "mock_harness"
        self.budget_remaining = remaining
        self.budget_total = total


class MockHarnessWithGetBudget:
    """Mock harness with get_budget method."""

    def __init__(self, remaining: int, total: int):
        self.name = "mock_harness_v2"
        self._remaining = remaining
        self._total = total

    def get_budget(self):
        return {"remaining": self._remaining, "total": self._total}


class MockHarnessNoBudget:
    """Mock harness without budget tracking."""

    name = "no_budget"


@pytest.mark.asyncio
async def test_budget_probe_with_remaining():
    """Test budget probe with budget remaining."""
    harness = MockHarnessWithBudget(remaining=500, total=1000)
    probe = BudgetProbe()

    result = await probe.check_harness(harness)

    assert result.passed
    assert result.status == ProbeStatus.PASSED
    assert result.probe_type == ProbeType.BUDGET
    assert "500/1000" in result.details
    assert "50.0%" in result.details


@pytest.mark.asyncio
async def test_budget_probe_exhausted():
    """Test budget probe with exhausted budget."""
    harness = MockHarnessWithBudget(remaining=0, total=1000)
    probe = BudgetProbe()

    result = await probe.check_harness(harness)

    assert result.failed
    assert result.status == ProbeStatus.FAILED
    assert result.probe_type == ProbeType.BUDGET
    assert "0/1000" in result.details


@pytest.mark.asyncio
async def test_budget_probe_get_budget_api():
    """Test budget probe with get_budget API."""
    harness = MockHarnessWithGetBudget(remaining=750, total=1000)
    probe = BudgetProbe()

    result = await probe.check_harness(harness)

    assert result.passed
    assert result.status == ProbeStatus.PASSED
    assert "750/1000" in result.details
    assert "75.0%" in result.details


@pytest.mark.asyncio
async def test_budget_probe_no_tracking():
    """Test budget probe with harness that has no budget tracking."""
    harness = MockHarnessNoBudget()
    probe = BudgetProbe()

    result = await probe.check_harness(harness)

    assert result.status == ProbeStatus.SKIPPED
    assert "No budget tracking" in result.details


@pytest.mark.asyncio
async def test_token_budget_check():
    """Test token budget check."""
    probe = BudgetProbe()

    # Test with budget remaining
    result = await probe.check_token_budget(used=500, total=1000, threshold=0.1)

    assert result.passed
    assert result.status == ProbeStatus.PASSED
    assert "500/1000" in result.details

    # Test below threshold
    result = await probe.check_token_budget(used=950, total=1000, threshold=0.1)

    assert result.failed
    assert result.status == ProbeStatus.FAILED
    assert "below 10.0% threshold" in result.details


@pytest.mark.asyncio
async def test_token_budget_custom_threshold():
    """Test token budget with custom threshold."""
    probe = BudgetProbe()

    # 200 remaining out of 1000 is 20%
    # With threshold of 0.3 (30%), should fail
    result = await probe.check_token_budget(used=800, total=1000, threshold=0.3)

    assert result.failed
    assert "below 30.0% threshold" in result.details
