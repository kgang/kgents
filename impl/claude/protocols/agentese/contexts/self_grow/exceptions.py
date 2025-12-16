"""
self.grow Exceptions

Custom exceptions for the autopoietic holon generator.
"""

from __future__ import annotations


class GrowthError(Exception):
    """Base exception for growth operations."""

    pass


class BudgetExhaustedError(GrowthError):
    """Raised when entropy budget is exhausted."""

    def __init__(self, message: str, remaining: float, requested: float):
        super().__init__(message)
        self.remaining = remaining
        self.requested = requested


class AffordanceError(GrowthError):
    """Raised when observer lacks required affordance."""

    def __init__(self, message: str, available: tuple[str, ...] = ()):
        super().__init__(message)
        self.available = available


class ValidationError(GrowthError):
    """Raised when validation fails."""

    def __init__(self, message: str, blockers: list[str] | None = None):
        super().__init__(message)
        self.blockers = blockers or []


class NurseryCapacityError(GrowthError):
    """Raised when nursery is at capacity."""

    def __init__(self, message: str, current: int, max_capacity: int):
        super().__init__(message)
        self.current = current
        self.max_capacity = max_capacity


class RollbackError(GrowthError):
    """Raised when rollback fails."""

    def __init__(self, message: str, token_id: str | None = None):
        super().__init__(message)
        self.token_id = token_id


class CompositionViolationError(GrowthError):
    """Raised when category laws are violated."""

    def __init__(self, message: str, law: str = "unknown"):
        super().__init__(message)
        self.law = law
