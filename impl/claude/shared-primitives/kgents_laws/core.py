"""
kgents-laws/core: Core Types for Law Verification

This module provides the fundamental types used across all law verifications:
- LawStatus: Enumeration of verification outcomes
- LawVerification: Result of verifying a single law

These types are designed for composition - multiple LawVerification results
can be combined into reports and analyzed programmatically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from typing import Any

# -----------------------------------------------------------------------------
# Law Status
# -----------------------------------------------------------------------------


class LawStatus(Enum):
    """
    Status of a law verification.

    Each status represents a distinct verification outcome:

    - PASSED: Law verified behaviorally with test inputs
    - FAILED: Law violation detected with concrete counterexample
    - SKIPPED: Law not tested (missing dependencies, etc.)
    - STRUCTURAL: Law verified by type structure only (no runtime tests)

    Example:
        >>> result = verify_identity(agent, test_inputs)
        >>> match result.status:
        ...     case LawStatus.PASSED:
        ...         print("Identity law holds!")
        ...     case LawStatus.FAILED:
        ...         print(f"Violation: {result.message}")
        ...     case LawStatus.SKIPPED:
        ...         print(f"Skipped: {result.message}")
        ...     case LawStatus.STRUCTURAL:
        ...         print("Verified by structure only")
    """

    PASSED = auto()  # Law verified with test cases
    FAILED = auto()  # Law violation detected
    SKIPPED = auto()  # Law not tested
    STRUCTURAL = auto()  # Verified by structure only (no runtime)


# -----------------------------------------------------------------------------
# Law Verification
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class LawVerification:
    """
    Result of verifying a single categorical law.

    LawVerification captures everything needed to understand
    a verification outcome:

    - What was verified (law_name)
    - Whether it passed (status)
    - What the two sides computed (left_result, right_result)
    - Human-readable explanation (message)

    Properties:
        passed: True if status is PASSED or STRUCTURAL

    Example:
        >>> result = verify_associativity(f, g, h, test_inputs)
        >>> if result.passed:
        ...     print(f"Associativity holds: {result.message}")
        ... else:
        ...     print(f"VIOLATION: {result.message}")
        ...     print(f"  Left:  {result.left_result}")
        ...     print(f"  Right: {result.right_result}")

    Notes:
        - This is a frozen dataclass for immutability
        - Use left_result/right_result for debugging failures
        - message always contains actionable information
    """

    law_name: str
    status: LawStatus
    left_result: Any = None
    right_result: Any = None
    message: str = ""
    test_input: Any = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def passed(self) -> bool:
        """
        True if the law was verified successfully.

        Both PASSED and STRUCTURAL count as passing:
        - PASSED: Verified with concrete test inputs
        - STRUCTURAL: Verified by type structure alone
        """
        return self.status in (LawStatus.PASSED, LawStatus.STRUCTURAL)

    @property
    def failed(self) -> bool:
        """True if verification found a law violation."""
        return self.status == LawStatus.FAILED

    @property
    def skipped(self) -> bool:
        """True if verification was skipped."""
        return self.status == LawStatus.SKIPPED

    def __bool__(self) -> bool:
        """
        Allow using LawVerification in boolean context.

        >>> if verify_identity(agent, inputs):
        ...     print("Identity holds!")
        """
        return self.passed

    def __repr__(self) -> str:
        status_str = self.status.name
        if self.passed:
            return f"LawVerification({self.law_name!r}, {status_str})"
        else:
            return (
                f"LawVerification({self.law_name!r}, {status_str}, "
                f"left={self.left_result!r}, right={self.right_result!r})"
            )

    def __str__(self) -> str:
        """Human-readable string representation."""
        status_emoji = {
            LawStatus.PASSED: "[PASS]",
            LawStatus.FAILED: "[FAIL]",
            LawStatus.SKIPPED: "[SKIP]",
            LawStatus.STRUCTURAL: "[STRUCT]",
        }
        emoji = status_emoji.get(self.status, "[????]")
        return f"{emoji} {self.law_name}: {self.message}"


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------


__all__ = [
    "LawStatus",
    "LawVerification",
]
