"""
Gate Law: Hard floor enforcement for governance.

A gate law is a non-negotiable constraint. When a dimension falls below
its threshold, the gate zeros out the total score - blocking the action.

Use Cases:
- Ethical floors: No action below ethical threshold
- Safety gates: Must meet minimum safety requirements
- Quality bars: Reject work that doesn't meet standards

Design Philosophy:
    "Some thresholds are not for negotiation."

    A gate law represents a hard floor - a line that cannot be crossed.
    Unlike threshold laws that warn and advise, gate laws block and prevent.
    When you need an action to be impossible below a certain standard,
    use a gate law.
"""

from __future__ import annotations

from dataclasses import dataclass

from .core import GovernanceLaw, LawResult


@dataclass
class GateLaw(GovernanceLaw):
    """
    Gate Law: Hard floor that zeros the total if violated.

    A gate law enforces a non-negotiable minimum. If the specified dimension
    falls below the threshold, the entire score becomes the on_fail value
    (typically 0.0), effectively blocking the action.

    Example:
        >>> ethical_gate = GateLaw("ethical", threshold=0.6, on_fail=0.0)

        >>> # Gate passes - returns average of all scores
        >>> ethical_gate.apply({"ethical": 0.7, "novelty": 0.9})
        0.8

        >>> # Gate fails - returns on_fail value
        >>> ethical_gate.apply({"ethical": 0.5, "novelty": 0.9})
        0.0

        >>> # Direct value check
        >>> result = ethical_gate.check(0.5)
        >>> result.blocked
        True
        >>> result.reason
        'ethical (0.50) below threshold (0.60)'

    Attributes:
        dimension: The dimension this gate monitors.
        threshold: The minimum acceptable value.
        on_fail: The value to return when the gate fails (default: 0.0).

    Use Cases:
        - Ethical floors: No action below ethical threshold
        - Safety gates: Must meet minimum safety requirements
        - Quality bars: Reject work that doesn't meet standards
        - Access control: Deny access below authentication level
    """

    dimension: str
    threshold: float
    on_fail: float = 0.0

    @property
    def name(self) -> str:
        """
        The law name in format 'gate:<dimension>'.

        Example:
            >>> GateLaw("ethical", 0.6).name
            'gate:ethical'
        """
        return f"gate:{self.dimension}"

    def apply(self, scores: dict[str, float]) -> float:
        """
        Apply the gate to a set of dimension scores.

        If the monitored dimension is below the threshold, returns on_fail.
        Otherwise, returns the average of all scores.

        Args:
            scores: Dictionary mapping dimension names to float scores.

        Returns:
            The on_fail value if gate fails, otherwise average of scores.

        Example:
            >>> gate = GateLaw("safety", threshold=0.7, on_fail=0.0)

            >>> # Safety is 0.8 >= 0.7, gate passes
            >>> gate.apply({"safety": 0.8, "speed": 0.9})
            0.85

            >>> # Safety is 0.5 < 0.7, gate fails
            >>> gate.apply({"safety": 0.5, "speed": 0.9})
            0.0

            >>> # Missing dimension treated as 0.0
            >>> gate.apply({"speed": 0.9})
            0.0
        """
        value = scores.get(self.dimension, 0.0)
        if value < self.threshold:
            return self.on_fail
        # Return average of all scores if gate passes
        return sum(scores.values()) / len(scores) if scores else 0.0

    def check(self, value: float) -> LawResult:
        """
        Check a single value against the gate threshold.

        Args:
            value: The value to check.

        Returns:
            LawResult with blocked=True if value is below threshold.

        Example:
            >>> gate = GateLaw("ethical", threshold=0.6)

            >>> result = gate.check(0.7)
            >>> result.passed
            True
            >>> result.score
            0.7

            >>> result = gate.check(0.5)
            >>> result.passed
            False
            >>> result.blocked
            True
            >>> result.reason
            'ethical (0.50) below threshold (0.60)'
        """
        if value < self.threshold:
            return LawResult(
                passed=False,
                score=self.on_fail,
                blocked=True,
                reason=f"{self.dimension} ({value:.2f}) below threshold ({self.threshold:.2f})",
            )
        return LawResult(passed=True, score=value)

    def __repr__(self) -> str:
        return f"GateLaw(dimension={self.dimension!r}, threshold={self.threshold}, on_fail={self.on_fail})"


def gate_law(
    dimension: str,
    threshold: float,
    on_fail: float = 0.0,
) -> GateLaw:
    """
    Factory function for creating gate laws.

    Creates a GateLaw that enforces a hard floor on the specified dimension.
    If the dimension's value falls below the threshold, the total score
    becomes on_fail (blocking the action).

    Args:
        dimension: The dimension to gate on (e.g., "ethical", "safety").
        threshold: The minimum acceptable value (e.g., 0.6 for 60%).
        on_fail: The value to return when gate fails (default: 0.0).

    Returns:
        A configured GateLaw instance.

    Example:
        >>> # Create an ethical floor
        >>> ethical_gate = gate_law("ethical", threshold=0.6)

        >>> # Test against scores
        >>> ethical_gate.apply({"ethical": 0.7, "novelty": 0.9})
        0.8

        >>> ethical_gate.apply({"ethical": 0.5, "novelty": 0.9})
        0.0

        >>> # Create a safety gate with custom on_fail
        >>> safety_gate = gate_law("safety", threshold=0.8, on_fail=-1.0)
        >>> safety_gate.apply({"safety": 0.5})
        -1.0

    Use Cases:
        - gate_law("ethical", 0.6): Ethical floor at 60%
        - gate_law("safety", 0.9): Safety requirement at 90%
        - gate_law("quality", 0.7): Quality bar at 70%
        - gate_law("auth_level", 2.0): Authentication level 2+ required
    """
    return GateLaw(dimension=dimension, threshold=threshold, on_fail=on_fail)


__all__ = [
    "GateLaw",
    "gate_law",
]
