"""
Constitution: Composition of governance laws.

A constitution combines multiple laws into a unified governance framework.
It evaluates all laws against a set of scores and produces a combined result.

Design Philosophy:
    "Good governance is not a single rule, but a coherent system."

    A constitution represents the composition of multiple constraints -
    some hard (gates), some soft (thresholds). Together they form a
    coherent governance framework that can be evaluated as a unit.

Example:
    >>> from kgents_governance import Constitution, gate_law, threshold_law
    >>>
    >>> # Define a constitution for an AI system
    >>> ai_constitution = Constitution(
    ...     name="ai-safety",
    ...     laws=[
    ...         gate_law("ethical", threshold=0.6),      # Hard floor
    ...         gate_law("safety", threshold=0.8),       # Hard floor
    ...         threshold_law("drift", threshold=0.4),   # Soft limit
    ...     ],
    ...     amendment_threshold=0.9,  # 90% agreement to amend
    ... )
    >>>
    >>> # Evaluate against scores
    >>> result = ai_constitution.evaluate({
    ...     "ethical": 0.7,
    ...     "safety": 0.85,
    ...     "drift": 0.3,
    ... })
    >>> result.passed
    True
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .core import GovernanceLaw, LawResult
from .gate import GateLaw
from .threshold import ThresholdLaw


@dataclass
class Constitution:
    """
    Constitution: Composition of multiple governance laws.

    A constitution combines gate laws (hard floors) and threshold laws
    (soft limits) into a unified framework. When evaluated:
    - Gate laws are checked first; any failure blocks the action
    - Threshold laws are checked second; violations produce warnings
    - The final result combines all outcomes

    Example:
        >>> constitution = Constitution(
        ...     name="kgents-governance",
        ...     laws=[
        ...         gate_law("ethical", threshold=0.6, on_fail=0.0),
        ...         threshold_law("drift", threshold=0.4, action="warn"),
        ...     ],
        ...     amendment_threshold=0.8,
        ... )

        >>> # All gates pass, no threshold warnings
        >>> result = constitution.evaluate({"ethical": 0.7, "drift": 0.3})
        >>> result.passed
        True
        >>> result.warning is None
        True

        >>> # Gate fails - blocked
        >>> result = constitution.evaluate({"ethical": 0.5, "drift": 0.3})
        >>> result.passed
        False
        >>> result.blocked
        True

        >>> # Gate passes, threshold warns
        >>> result = constitution.evaluate({"ethical": 0.7, "drift": 0.5})
        >>> result.passed
        True
        >>> result.warning
        'drift exceeded threshold (0.50 > 0.40)'

    Attributes:
        name: Human-readable name for this constitution.
        laws: List of governance laws (gates and thresholds).
        amendment_threshold: Agreement level required to amend (0.0-1.0).

    Design Philosophy:
        - Gates come first: Any gate failure immediately blocks
        - Thresholds are advisory: All warnings are collected
        - Composition is transparent: The result explains what happened
    """

    name: str
    laws: list[GovernanceLaw] = field(default_factory=list)
    amendment_threshold: float = 0.8  # Agreement needed to amend

    def evaluate(self, scores: dict[str, float]) -> LawResult:
        """
        Evaluate all laws against the provided scores.

        Gate laws are evaluated first. If any gate fails, the result is
        blocked with the gate's on_fail score. If all gates pass,
        threshold laws are evaluated and their warnings are collected.

        Args:
            scores: Dictionary mapping dimension names to float scores.
                    Typically values are in the range [0.0, 1.0].

        Returns:
            A LawResult combining all law evaluations:
            - passed: True if no gates were violated
            - blocked: True if any gate was violated
            - score: Average of scores (or on_fail if blocked)
            - warning: Combined warnings from threshold laws

        Example:
            >>> constitution = Constitution(
            ...     name="project-governance",
            ...     laws=[
            ...         gate_law("quality", 0.7),
            ...         gate_law("safety", 0.8),
            ...         threshold_law("complexity", 0.5),
            ...         threshold_law("tech_debt", 0.4),
            ...     ],
            ... )

            >>> # All pass, no warnings
            >>> result = constitution.evaluate({
            ...     "quality": 0.8,
            ...     "safety": 0.9,
            ...     "complexity": 0.4,
            ...     "tech_debt": 0.3,
            ... })
            >>> result.passed
            True

            >>> # Gate fails
            >>> result = constitution.evaluate({
            ...     "quality": 0.6,  # Below 0.7
            ...     "safety": 0.9,
            ...     "complexity": 0.4,
            ...     "tech_debt": 0.3,
            ... })
            >>> result.blocked
            True

            >>> # Threshold warnings
            >>> result = constitution.evaluate({
            ...     "quality": 0.8,
            ...     "safety": 0.9,
            ...     "complexity": 0.6,  # Above 0.5
            ...     "tech_debt": 0.5,   # Above 0.4
            ... })
            >>> "complexity" in result.warning
            True
            >>> "tech_debt" in result.warning
            True
        """
        warnings: list[str] = []
        blocked = False
        final_score = sum(scores.values()) / len(scores) if scores else 0.0

        # Evaluate gate laws first - any failure blocks
        for law in self.laws:
            if isinstance(law, GateLaw):
                result = law.apply(scores)
                if result == law.on_fail:
                    blocked = True
                    final_score = result
                    break

        # If not blocked, evaluate threshold laws
        if not blocked:
            for law in self.laws:
                if isinstance(law, ThresholdLaw):
                    result = law.check(scores.get(law.dimension, 0.0))
                    if result.warning:
                        warnings.append(result.warning)

        return LawResult(
            passed=not blocked,
            score=final_score,
            warning="; ".join(warnings) if warnings else None,
            blocked=blocked,
        )

    def can_amend(self, agreement: float) -> bool:
        """
        Check if an amendment is allowed given the agreement level.

        Constitutional amendments require sufficient consensus. This method
        checks if the provided agreement level meets the threshold.

        Args:
            agreement: The level of agreement (0.0 to 1.0).
                       0.0 = no agreement, 1.0 = unanimous.

        Returns:
            True if amendment is allowed, False otherwise.

        Example:
            >>> constitution = Constitution(
            ...     name="team-rules",
            ...     laws=[],
            ...     amendment_threshold=0.8,
            ... )

            >>> constitution.can_amend(0.9)
            True

            >>> constitution.can_amend(0.7)
            False

            >>> constitution.can_amend(0.8)
            True
        """
        return agreement >= self.amendment_threshold

    def add_law(self, law: GovernanceLaw) -> Constitution:
        """
        Add a law to the constitution.

        Returns a new Constitution with the law added (immutable pattern).

        Args:
            law: The governance law to add.

        Returns:
            A new Constitution with the law added.

        Example:
            >>> constitution = Constitution(name="base", laws=[])
            >>> new_constitution = constitution.add_law(
            ...     gate_law("ethical", 0.6)
            ... )
            >>> len(new_constitution.laws)
            1
        """
        return Constitution(
            name=self.name,
            laws=[*self.laws, law],
            amendment_threshold=self.amendment_threshold,
        )

    def gate_laws(self) -> list[GateLaw]:
        """
        Get all gate laws in this constitution.

        Returns:
            List of GateLaw instances.

        Example:
            >>> constitution = Constitution(
            ...     name="mixed",
            ...     laws=[
            ...         gate_law("ethical", 0.6),
            ...         threshold_law("drift", 0.4),
            ...         gate_law("safety", 0.8),
            ...     ],
            ... )
            >>> len(constitution.gate_laws())
            2
        """
        return [law for law in self.laws if isinstance(law, GateLaw)]

    def threshold_laws(self) -> list[ThresholdLaw]:
        """
        Get all threshold laws in this constitution.

        Returns:
            List of ThresholdLaw instances.

        Example:
            >>> constitution = Constitution(
            ...     name="mixed",
            ...     laws=[
            ...         gate_law("ethical", 0.6),
            ...         threshold_law("drift", 0.4),
            ...         threshold_law("latency", 0.2),
            ...     ],
            ... )
            >>> len(constitution.threshold_laws())
            2
        """
        return [law for law in self.laws if isinstance(law, ThresholdLaw)]

    def __repr__(self) -> str:
        gate_count = len(self.gate_laws())
        threshold_count = len(self.threshold_laws())
        return (
            f"Constitution(name={self.name!r}, "
            f"gates={gate_count}, thresholds={threshold_count})"
        )


__all__ = [
    "Constitution",
]
