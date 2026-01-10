"""
Threshold Law: Soft limit enforcement for governance.

A threshold law monitors a dimension and issues warnings when limits
are exceeded, but does not block the action. It's advisory, not mandatory.

Use Cases:
- Drift detection: Alert when quality is degrading
- Performance monitoring: Warn on latency spikes
- Budget tracking: Notify when approaching limits
- Resource usage: Flag when nearing capacity

Design Philosophy:
    "Not every limit needs to be a wall."

    Some constraints should inform rather than prevent. A threshold law
    respects autonomy while ensuring awareness. When you want to highlight
    a concern without blocking progress, use a threshold law.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .core import GovernanceLaw, LawResult


@dataclass
class ThresholdLaw(GovernanceLaw):
    """
    Threshold Law: Soft limit that warns but doesn't block.

    A threshold law issues warnings when a dimension exceeds its threshold,
    but still allows the action to proceed. It's advisory governance -
    raising awareness without preventing progress.

    Example:
        >>> drift_alert = ThresholdLaw("drift", threshold=0.4, action="warn")

        >>> # Value under threshold - no warning
        >>> result = drift_alert.check(0.3)
        >>> result.passed
        True
        >>> result.warning is None
        True

        >>> # Value over threshold - warning issued
        >>> result = drift_alert.check(0.5)
        >>> result.passed
        True  # Still passes - soft limit
        >>> result.warning
        'drift exceeded threshold (0.50 > 0.40)'

    Attributes:
        dimension: The dimension this law monitors.
        threshold: The value above which warnings are issued.
        action: The type of action to take ("warn", "log", "notify").

    Use Cases:
        - Drift detection: Alert when diverging from baseline
        - Performance monitoring: Warn on degradation
        - Budget tracking: Notify when approaching limit
        - Resource usage: Flag when nearing capacity
    """

    dimension: str
    threshold: float
    action: Literal["warn", "log", "notify"] = "warn"

    @property
    def name(self) -> str:
        """
        The law name in format 'threshold:<dimension>'.

        Example:
            >>> ThresholdLaw("drift", 0.4).name
            'threshold:drift'
        """
        return f"threshold:{self.dimension}"

    def apply(self, scores: dict[str, float]) -> LawResult:
        """
        Apply the threshold to a set of dimension scores.

        Extracts the monitored dimension and checks it against the threshold.
        Returns a LawResult with a warning if exceeded.

        Args:
            scores: Dictionary mapping dimension names to float scores.

        Returns:
            LawResult with passed=True and optional warning.

        Example:
            >>> law = ThresholdLaw("latency", threshold=0.5, action="warn")

            >>> # Under threshold - clean pass
            >>> result = law.apply({"latency": 0.3, "errors": 0.1})
            >>> result.passed
            True
            >>> result.warning is None
            True

            >>> # Over threshold - pass with warning
            >>> result = law.apply({"latency": 0.7, "errors": 0.1})
            >>> result.passed
            True
            >>> result.warning
            'latency exceeded threshold (0.70 > 0.50)'
        """
        value = scores.get(self.dimension, 0.0)
        return self.check(value)

    def check(self, value: float) -> LawResult:
        """
        Check a single value against the threshold.

        Args:
            value: The value to check.

        Returns:
            LawResult with passed=True (always) and warning if exceeded.

        Example:
            >>> law = ThresholdLaw("drift", threshold=0.4, action="notify")

            >>> result = law.check(0.3)
            >>> result.passed
            True
            >>> result.warning is None
            True

            >>> result = law.check(0.6)
            >>> result.passed
            True
            >>> result.warning
            'drift exceeded threshold (0.60 > 0.40)'
            >>> result.reason
            'Consider action: notify'
        """
        if value > self.threshold:
            return LawResult(
                passed=True,  # Soft limit - still passes
                score=value,
                warning=f"{self.dimension} exceeded threshold ({value:.2f} > {self.threshold:.2f})",
                reason=f"Consider action: {self.action}",
            )
        return LawResult(passed=True, score=value)

    def __repr__(self) -> str:
        return f"ThresholdLaw(dimension={self.dimension!r}, threshold={self.threshold}, action={self.action!r})"


def threshold_law(
    dimension: str,
    threshold: float,
    action: Literal["warn", "log", "notify"] = "warn",
) -> ThresholdLaw:
    """
    Factory function for creating threshold laws.

    Creates a ThresholdLaw that issues warnings when the specified dimension
    exceeds its threshold. Unlike gate laws, threshold laws don't block -
    they inform and advise.

    Args:
        dimension: The dimension to monitor (e.g., "drift", "latency").
        threshold: The value above which warnings are issued.
        action: The suggested action type ("warn", "log", "notify").

    Returns:
        A configured ThresholdLaw instance.

    Example:
        >>> # Create a drift alert
        >>> drift_alert = threshold_law("drift", threshold=0.4, action="warn")

        >>> # No warning under threshold
        >>> result = drift_alert.check(0.3)
        >>> result.warning is None
        True

        >>> # Warning over threshold
        >>> result = drift_alert.check(0.5)
        >>> result.warning
        'drift exceeded threshold (0.50 > 0.40)'
        >>> result.passed  # Still passes!
        True

        >>> # Create various monitors
        >>> latency_alert = threshold_law("latency", 0.2, action="notify")
        >>> budget_alert = threshold_law("spend_ratio", 0.8, action="log")

    Use Cases:
        - threshold_law("drift", 0.4): Alert on drift > 40%
        - threshold_law("latency_ms", 200.0): Warn on latency > 200ms
        - threshold_law("error_rate", 0.01): Log on error rate > 1%
        - threshold_law("budget_used", 0.8): Notify on budget > 80%
    """
    return ThresholdLaw(dimension=dimension, threshold=threshold, action=action)


__all__ = [
    "ThresholdLaw",
    "threshold_law",
]
