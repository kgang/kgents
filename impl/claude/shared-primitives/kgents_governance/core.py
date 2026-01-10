"""
Core types for kgents-governance.

This module provides the foundational types for governance laws:
- LawResult: The outcome of applying a law
- GovernanceLaw: Abstract base class for all laws

These types are the building blocks for constructing governance systems
that enforce hard floors (gates) and soft limits (thresholds).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LawResult:
    """
    Result of applying a governance law.

    A LawResult captures the outcome of checking a value or set of scores
    against a governance law. It distinguishes between:
    - passed: Whether the law's condition was satisfied
    - blocked: Whether the law actively prevents an action (gate laws)
    - warning: Advisory message when soft limits are exceeded

    Example:
        >>> # A passing result
        >>> result = LawResult(passed=True, score=0.85)
        >>> result.passed
        True

        >>> # A blocked result (gate law violation)
        >>> result = LawResult(
        ...     passed=False,
        ...     score=0.0,
        ...     blocked=True,
        ...     reason="ethical (0.45) below threshold (0.60)"
        ... )
        >>> result.blocked
        True

        >>> # A warning result (threshold law exceeded)
        >>> result = LawResult(
        ...     passed=True,
        ...     score=0.55,
        ...     warning="drift exceeded threshold (0.55 > 0.40)"
        ... )
        >>> result.warning
        'drift exceeded threshold (0.55 > 0.40)'

    Attributes:
        passed: Whether the law's condition was satisfied.
        score: The computed score (if applicable).
        warning: Advisory message for soft limit violations.
        blocked: Whether the action is actively blocked.
        reason: Human-readable explanation of the result.
    """

    passed: bool
    score: float | None = None
    warning: str | None = None
    blocked: bool = False
    reason: str = ""

    def __bool__(self) -> bool:
        """Allow using LawResult directly in boolean contexts."""
        return self.passed

    def __repr__(self) -> str:
        parts = [f"passed={self.passed}"]
        if self.score is not None:
            parts.append(f"score={self.score:.2f}")
        if self.blocked:
            parts.append("blocked=True")
        if self.warning:
            parts.append(f"warning={self.warning!r}")
        if self.reason:
            parts.append(f"reason={self.reason!r}")
        return f"LawResult({', '.join(parts)})"


class GovernanceLaw(ABC):
    """
    Abstract base class for governance laws.

    A governance law defines a constraint on a system. Laws come in two
    fundamental flavors:
    - Gate laws: Hard floors that block actions when violated
    - Threshold laws: Soft limits that warn but don't block

    All laws must implement:
    - name: A unique identifier for the law
    - apply: Evaluate the law against a dictionary of dimension scores
    - check: Evaluate the law against a single value

    Example:
        >>> class MinimumScoreLaw(GovernanceLaw):
        ...     def __init__(self, dimension: str, minimum: float):
        ...         self.dimension = dimension
        ...         self.minimum = minimum
        ...
        ...     @property
        ...     def name(self) -> str:
        ...         return f"min:{self.dimension}"
        ...
        ...     def apply(self, scores: dict[str, float]) -> float | LawResult:
        ...         value = scores.get(self.dimension, 0.0)
        ...         if value < self.minimum:
        ...             return 0.0
        ...         return sum(scores.values()) / len(scores)
        ...
        ...     def check(self, value: float) -> LawResult:
        ...         if value < self.minimum:
        ...             return LawResult(passed=False, blocked=True)
        ...         return LawResult(passed=True, score=value)

    Design Philosophy:
        Laws should be:
        - Pure: No side effects, same inputs produce same outputs
        - Composable: Multiple laws can be combined in a Constitution
        - Transparent: Results clearly indicate why they passed or failed
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The unique name of this law.

        Convention:
        - Gate laws: "gate:<dimension>"
        - Threshold laws: "threshold:<dimension>"

        Returns:
            A string identifier for this law.
        """
        ...

    @abstractmethod
    def apply(self, scores: dict[str, float]) -> float | LawResult:
        """
        Apply the law to a set of dimension scores.

        This method evaluates the law against a dictionary mapping
        dimension names to their scores. The law extracts the relevant
        dimension(s) and determines the outcome.

        Args:
            scores: Dictionary mapping dimension names to float scores.
                    Scores are typically in the range [0.0, 1.0].

        Returns:
            Either a float score (for simple pass/fail) or a full
            LawResult with detailed information.

        Example:
            >>> law = GateLaw("ethical", threshold=0.6)
            >>> law.apply({"ethical": 0.7, "novelty": 0.9})
            0.8  # Average of scores (gate passed)
            >>> law.apply({"ethical": 0.5, "novelty": 0.9})
            0.0  # Gate blocked (ethical below threshold)
        """
        ...

    @abstractmethod
    def check(self, value: float) -> LawResult:
        """
        Check a single value against the law.

        This method evaluates just one value, returning a detailed
        LawResult. Useful for checking a specific dimension without
        the full context of other scores.

        Args:
            value: The value to check against the law.

        Returns:
            A LawResult indicating whether the check passed.

        Example:
            >>> law = GateLaw("ethical", threshold=0.6)
            >>> result = law.check(0.7)
            >>> result.passed
            True
            >>> result = law.check(0.5)
            >>> result.blocked
            True
        """
        ...

    def __repr__(self) -> str:
        """Default representation using the law name."""
        return f"{self.__class__.__name__}(name={self.name!r})"


__all__ = [
    "LawResult",
    "GovernanceLaw",
]
