"""
Budget Probes: Resource budget tracking for harnesses.

Philosophy:
    "Know when to stop before you run out."

This module implements budget checks for:
- VoidHarness (token budget)
- ExplorationHarness (action budget)
- General resource tracking

Budget probes help prevent runaway execution and enable adaptive stopping.

See: protocols/ashc/harness.py (VoidHarness)
"""

from __future__ import annotations

import time
from typing import Any

from .types import ProbeResult, ProbeStatus, ProbeType


class BudgetProbe:
    """
    Check resource budgets for harnesses and execution contexts.

    Usage:
        >>> probe = BudgetProbe()
        >>> result = await probe.check_harness(void_harness)
        >>> if result.passed:
        ...     print(f"Budget remaining: {result.details}")
    """

    async def check_harness(self, harness: Any) -> ProbeResult:
        """
        Check budget for a harness instance.

        Args:
            harness: Harness instance (VoidHarness, ExplorationHarness, etc.)

        Returns:
            ProbeResult with budget information
        """
        start_ms = time.perf_counter() * 1000

        try:
            harness_name = getattr(harness, "name", type(harness).__name__)

            # Check if harness has budget tracking
            if hasattr(harness, "budget_remaining"):
                remaining = harness.budget_remaining
                total = getattr(harness, "budget_total", None)

                if total is not None:
                    percentage = (remaining / total) * 100 if total > 0 else 0
                    details = f"{remaining}/{total} remaining ({percentage:.1f}%)"
                else:
                    details = f"{remaining} remaining"

                # Consider failed if budget is exhausted
                passed = remaining > 0

                duration_ms = (time.perf_counter() * 1000) - start_ms
                return ProbeResult(
                    name=f"budget:{harness_name}",
                    probe_type=ProbeType.BUDGET,
                    status=ProbeStatus.PASSED if passed else ProbeStatus.FAILED,
                    details=details,
                    duration_ms=duration_ms,
                )

            elif hasattr(harness, "get_budget"):
                # Alternative API
                budget_info = harness.get_budget()
                remaining = budget_info.get("remaining", 0)
                total = budget_info.get("total", 0)

                percentage = (remaining / total) * 100 if total > 0 else 0
                details = f"{remaining}/{total} remaining ({percentage:.1f}%)"
                passed = remaining > 0

                duration_ms = (time.perf_counter() * 1000) - start_ms
                return ProbeResult(
                    name=f"budget:{harness_name}",
                    probe_type=ProbeType.BUDGET,
                    status=ProbeStatus.PASSED if passed else ProbeStatus.FAILED,
                    details=details,
                    duration_ms=duration_ms,
                )

            else:
                # No budget tracking
                duration_ms = (time.perf_counter() * 1000) - start_ms
                return ProbeResult(
                    name=f"budget:{harness_name}",
                    probe_type=ProbeType.BUDGET,
                    status=ProbeStatus.SKIPPED,
                    details="No budget tracking available",
                    duration_ms=duration_ms,
                )

        except Exception as e:
            duration_ms = (time.perf_counter() * 1000) - start_ms
            return ProbeResult(
                name=f"budget:error",
                probe_type=ProbeType.BUDGET,
                status=ProbeStatus.ERROR,
                details=f"Error checking budget: {e}",
                duration_ms=duration_ms,
            )

    async def check_token_budget(
        self,
        used: int,
        total: int,
        threshold: float = 0.1,
    ) -> ProbeResult:
        """
        Check token budget against threshold.

        Args:
            used: Tokens used so far
            total: Total token budget
            threshold: Fail if remaining < threshold * total

        Returns:
            ProbeResult indicating budget status
        """
        start_ms = time.perf_counter() * 1000

        remaining = total - used
        percentage = (remaining / total) * 100 if total > 0 else 0
        threshold_percentage = threshold * 100

        passed = remaining >= (threshold * total)

        details = f"{remaining}/{total} tokens remaining ({percentage:.1f}%)"
        if not passed:
            details += f" - below {threshold_percentage:.1f}% threshold"

        duration_ms = (time.perf_counter() * 1000) - start_ms

        return ProbeResult(
            name="budget:tokens",
            probe_type=ProbeType.BUDGET,
            status=ProbeStatus.PASSED if passed else ProbeStatus.FAILED,
            details=details,
            duration_ms=duration_ms,
        )


__all__ = ["BudgetProbe"]
