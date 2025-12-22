"""
Sheaf verification results for K-Block.

Provides detailed information about sheaf condition verification,
including pass/fail status, conflicts, and coverage metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import TokenConflict

# -----------------------------------------------------------------------------
# Sheaf Verification Result
# -----------------------------------------------------------------------------


@dataclass
class SheafVerification:
    """
    Result of sheaf condition verification.

    The sheaf condition requires all pairs of views to agree on
    overlapping tokens. This result captures:
    - Whether the condition passed
    - Which pairs were checked
    - Any conflicts found
    - Coverage metrics

    Example:
        >>> verification = sheaf.verify_sheaf_condition()
        >>> if verification:
        ...     print("All views coherent")
        ... else:
        ...     for conflict in verification.conflicts:
        ...         print(f"Conflict: {conflict}")
    """

    passed: bool
    checked_pairs: int = 0
    conflicts: list[TokenConflict] = field(default_factory=list)
    shared_tokens: int = 0
    total_tokens: int = 0

    @property
    def coverage(self) -> float:
        """
        Percentage of tokens that overlap between views.

        Higher coverage means more tokens are shared across views,
        which increases confidence that views are truly coherent.

        Returns:
            Float between 0.0 and 1.0
        """
        if self.total_tokens == 0:
            return 1.0  # Empty views are trivially coherent
        return self.shared_tokens / self.total_tokens

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize for logging/debugging.

        Returns:
            Dictionary representation of verification result
        """
        return {
            "passed": self.passed,
            "checked_pairs": self.checked_pairs,
            "conflicts": [
                {
                    "token_id": c.token_id,
                    "view1": c.view1.value,
                    "view2": c.view2.value,
                    "kind1": c.kind1,
                    "kind2": c.kind2,
                    "value1": c.value1,
                    "value2": c.value2,
                }
                for c in self.conflicts
            ],
            "shared_tokens": self.shared_tokens,
            "total_tokens": self.total_tokens,
            "coverage": self.coverage,
        }

    def __bool__(self) -> bool:
        """
        Allow using verification result in boolean context.

        Example:
            >>> if sheaf.verify_sheaf_condition():
            ...     # All views coherent
        """
        return self.passed

    def __repr__(self) -> str:
        status = "PASSED" if self.passed else "FAILED"
        return (
            f"SheafVerification({status}, "
            f"pairs={self.checked_pairs}, "
            f"conflicts={len(self.conflicts)}, "
            f"coverage={self.coverage:.1%})"
        )
