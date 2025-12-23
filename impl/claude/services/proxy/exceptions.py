"""
Proxy Handle Exceptions: Error types for proxy lifecycle.

AD-015: These exceptions enable explicit error handling for proxy state.

Philosophy:
    "Hidden computation is hostile to agents because they cannot reason
    about what they cannot see."

These exceptions make proxy state issues VISIBLE and ACTIONABLE.

AGENTESE: services.proxy.exceptions
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import SourceType


class ProxyHandleError(Exception):
    """Base exception for proxy handle errors."""

    pass


class NoProxyHandleError(ProxyHandleError):
    """
    Raised when a proxy handle doesn't exist for a source type.

    AD-015: This replaces the ad-hoc NoPreComputedDataError from spec ledger.

    The correct response to this error is to:
    1. Surface it to the user/agent (not hide it)
    2. Offer explicit computation via store.compute()
    3. Let the user/agent decide when to compute

    Example API response:
        {
            "success": false,
            "needs_computation": true,
            "source_type": "spec_corpus",
            "compute_endpoint": "/api/proxy/compute/spec_corpus",
            "message": "No proxy handle exists. Run computation to generate.",
            "hint": "AD-015: Analysis is explicit. Run compute to generate."
        }
    """

    def __init__(self, source_type: "SourceType", message: str | None = None):
        self.source_type = source_type
        self.message = message or (
            f"No proxy handle for '{source_type.value}'. Use store.compute() to generate."
        )
        super().__init__(self.message)


class ComputationError(ProxyHandleError):
    """
    Raised when proxy handle computation fails.

    Contains the original exception for debugging.
    """

    def __init__(
        self,
        source_type: "SourceType",
        original: Exception,
        message: str | None = None,
    ):
        self.source_type = source_type
        self.original = original
        self.message = message or (f"Computation failed for '{source_type.value}': {original}")
        super().__init__(self.message)


class ComputationInProgressError(ProxyHandleError):
    """
    Raised when attempting to delete/invalidate a handle during computation.

    This is a transient state - retry after computation completes.
    """

    def __init__(self, source_type: "SourceType"):
        self.source_type = source_type
        self.message = (
            f"Computation in progress for '{source_type.value}'. "
            f"Wait for completion or use force=True."
        )
        super().__init__(self.message)


class StaleHandleError(ProxyHandleError):
    """
    Raised when a handle is stale and strict freshness is required.

    This is optional - most code should check is_fresh() instead.
    Use when you need to enforce fresh data (e.g., for critical decisions).
    """

    def __init__(self, source_type: "SourceType", age_seconds: float):
        self.source_type = source_type
        self.age_seconds = age_seconds
        self.message = (
            f"Proxy handle for '{source_type.value}' is stale "
            f"(age: {age_seconds:.1f}s). Refresh required."
        )
        super().__init__(self.message)


# =============================================================================
# Backward Compatibility Alias
# =============================================================================

# Alias for migration from spec ledger
# TODO: Remove after migration complete
NoPreComputedDataError = NoProxyHandleError


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Base
    "ProxyHandleError",
    # Specific errors
    "NoProxyHandleError",
    "ComputationError",
    "ComputationInProgressError",
    "StaleHandleError",
    # Alias (deprecated)
    "NoPreComputedDataError",
]
