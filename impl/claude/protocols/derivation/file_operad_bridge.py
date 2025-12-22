"""
Phase 6: File Operad → Derivation Bridge (Confidence Gating).

Not all agents should have the same privileges. Derivation confidence is
the natural trust measure for gating file operations.

The thresholds are calibrated to tier ceilings:
- read: 0.3 (anyone can read)
- annotate: 0.4 (low bar for notes)
- write: 0.5 (needs some trust)
- delete: 0.7 (only trusted agents)
- execute: 0.8 (only highly trusted)
- promote: 0.85 (JEWEL tier minimum)

Law 6.4 (Monotonic Trust):
    If threshold(O₁) < threshold(O₂), then allowed(A, O₂) → allowed(A, O₁)
    If an agent can delete, it can also read.

See: spec/protocols/derivation-framework.md §6.4
See: spec/protocols/file-operad.md

Teaching:
    gotcha: Unknown agents (no derivation) get 0.0 confidence and are denied
            all operations except reads (if threshold lowered).
            (Evidence: test_file_operad_bridge.py::test_unknown_agent_denied)

    gotcha: The gating is synchronous and cheap. Don't add async overhead.
            (Evidence: test_file_operad_bridge.py::test_gate_performance)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable, Literal

if TYPE_CHECKING:
    from .registry import DerivationRegistry


# =============================================================================
# Operation Types
# =============================================================================


OperationType = Literal[
    "read",
    "annotate",
    "write",
    "delete",
    "execute",
    "promote",
    "sandbox",
    "link",
]


# =============================================================================
# Thresholds Configuration
# =============================================================================


@dataclass(frozen=True)
class OperationThresholds:
    """
    Confidence thresholds for file operations.

    These are calibrated to derivation tier ceilings:
    - BOOTSTRAP (1.0): Can do everything
    - JEWEL (0.85): Can promote
    - APP (0.75): Can execute, delete
    - Low trust (<0.5): Read/annotate only

    Teaching:
        gotcha: Thresholds form a monotonic ordering. An agent that can
                delete can also write, annotate, and read.
    """

    read: float = 0.3
    annotate: float = 0.4
    write: float = 0.5
    link: float = 0.5  # Same as write
    delete: float = 0.7
    execute: float = 0.8
    sandbox: float = 0.6  # Lower than execute (sandboxed is safer)
    promote: float = 0.85

    def threshold_for(self, operation: str) -> float:
        """Get threshold for an operation, defaulting to 0.5."""
        return getattr(self, operation, 0.5)

    def operations_allowed_at(self, confidence: float) -> list[str]:
        """Get all operations allowed at a given confidence level."""
        allowed = []
        for op in ["read", "annotate", "write", "link", "sandbox", "delete", "execute", "promote"]:
            if confidence >= self.threshold_for(op):
                allowed.append(op)
        return allowed

    def highest_allowed_operation(self, confidence: float) -> str | None:
        """Get the highest-privilege operation allowed at confidence level."""
        # Order from highest to lowest privilege
        for op in ["promote", "execute", "delete", "sandbox", "write", "link", "annotate", "read"]:
            if confidence >= self.threshold_for(op):
                return op
        return None


# Default thresholds (can be customized per deployment)
DEFAULT_THRESHOLDS = OperationThresholds()


# =============================================================================
# Gate Result
# =============================================================================


@dataclass(frozen=True)
class ConfidenceGateResult:
    """
    Result of checking an operation against agent confidence.

    Contains all context needed for logging, auditing, and user feedback.
    """

    allowed: bool
    operation: str
    agent_name: str
    agent_confidence: float
    threshold: float
    reason: str
    tier: str = ""  # Agent's derivation tier
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def allowed_result(
        cls,
        operation: str,
        agent_name: str,
        confidence: float,
        threshold: float,
        tier: str = "",
    ) -> "ConfidenceGateResult":
        """Create an allowed result."""
        return cls(
            allowed=True,
            operation=operation,
            agent_name=agent_name,
            agent_confidence=confidence,
            threshold=threshold,
            reason=f"Confidence {confidence:.2f} >= threshold {threshold:.2f}",
            tier=tier,
        )

    @classmethod
    def denied_result(
        cls,
        operation: str,
        agent_name: str,
        confidence: float,
        threshold: float,
        reason: str | None = None,
        tier: str = "",
    ) -> "ConfidenceGateResult":
        """Create a denied result."""
        return cls(
            allowed=False,
            operation=operation,
            agent_name=agent_name,
            agent_confidence=confidence,
            threshold=threshold,
            reason=reason or f"Confidence {confidence:.2f} < threshold {threshold:.2f}",
            tier=tier,
        )

    @classmethod
    def check(
        cls,
        operation: str,
        agent_name: str,
        registry: "DerivationRegistry",
        thresholds: OperationThresholds = DEFAULT_THRESHOLDS,
    ) -> "ConfidenceGateResult":
        """
        Check if agent can perform operation.

        Law 6.4: Confidence gates operations.

        Args:
            operation: The operation to check
            agent_name: The agent requesting the operation
            registry: The derivation registry
            thresholds: Operation thresholds to use

        Returns:
            ConfidenceGateResult with allowed/denied status
        """
        threshold = thresholds.threshold_for(operation)

        if not registry.exists(agent_name):
            return cls.denied_result(
                operation=operation,
                agent_name=agent_name,
                confidence=0.0,
                threshold=threshold,
                reason=f"Unknown agent '{agent_name}' has no derivation",
            )

        derivation = registry.get(agent_name)
        if derivation is None:
            return cls.denied_result(
                operation=operation,
                agent_name=agent_name,
                confidence=0.0,
                threshold=threshold,
                reason=f"Agent '{agent_name}' derivation is None",
            )

        confidence = derivation.total_confidence
        tier = derivation.tier.value

        if confidence >= threshold:
            return cls.allowed_result(
                operation=operation,
                agent_name=agent_name,
                confidence=confidence,
                threshold=threshold,
                tier=tier,
            )
        else:
            return cls.denied_result(
                operation=operation,
                agent_name=agent_name,
                confidence=confidence,
                threshold=threshold,
                tier=tier,
            )


# =============================================================================
# File Operation Request/Result (for integration)
# =============================================================================


@dataclass
class FileOperationRequest:
    """
    A request to perform a file operation.

    This is the input type for the confidence gate.
    """

    operation: str
    path: str
    requester: str  # Agent name
    content: str | None = None  # For write operations
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FileOperationResult:
    """
    Result of a file operation attempt.

    Includes gate result and operation outcome.
    """

    success: bool
    gate_result: ConfidenceGateResult
    output: str | None = None
    error: str | None = None

    @classmethod
    def denied(cls, gate_result: ConfidenceGateResult) -> "FileOperationResult":
        """Create a denied result."""
        return cls(
            success=False,
            gate_result=gate_result,
            error=gate_result.reason,
        )

    @classmethod
    def succeeded(
        cls,
        gate_result: ConfidenceGateResult,
        output: str | None = None,
    ) -> "FileOperationResult":
        """Create a success result."""
        return cls(
            success=True,
            gate_result=gate_result,
            output=output,
        )


# =============================================================================
# Main Gate Function
# =============================================================================


def check_operation_confidence(
    operation: str,
    agent_name: str,
    registry: "DerivationRegistry",
    thresholds: OperationThresholds = DEFAULT_THRESHOLDS,
) -> ConfidenceGateResult:
    """
    Check if an agent can perform a file operation.

    This is the main entry point for confidence gating.

    Args:
        operation: Operation type (read, write, delete, etc.)
        agent_name: The requesting agent
        registry: The derivation registry
        thresholds: Optional custom thresholds

    Returns:
        ConfidenceGateResult with allowed/denied status
    """
    return ConfidenceGateResult.check(operation, agent_name, registry, thresholds)


def gate_file_operation(
    request: FileOperationRequest,
    registry: "DerivationRegistry",
    thresholds: OperationThresholds = DEFAULT_THRESHOLDS,
) -> ConfidenceGateResult:
    """
    Gate a file operation request.

    Convenience wrapper that extracts fields from request.
    """
    return check_operation_confidence(
        operation=request.operation,
        agent_name=request.requester,
        registry=registry,
        thresholds=thresholds,
    )


async def gate_and_execute(
    request: FileOperationRequest,
    registry: "DerivationRegistry",
    executor: Callable[[FileOperationRequest], Any],
    thresholds: OperationThresholds = DEFAULT_THRESHOLDS,
) -> FileOperationResult:
    """
    Gate a file operation and execute if allowed.

    Args:
        request: The operation request
        registry: The derivation registry
        executor: Async function to execute the operation
        thresholds: Optional custom thresholds

    Returns:
        FileOperationResult with gate and execution outcome

    Usage:
        result = await gate_and_execute(
            request=FileOperationRequest(operation="write", path="/foo", requester="Brain"),
            registry=get_registry(),
            executor=file_operad.write,
        )
    """
    gate_result = gate_file_operation(request, registry, thresholds)

    if not gate_result.allowed:
        return FileOperationResult.denied(gate_result)

    try:
        output = await executor(request)
        return FileOperationResult.succeeded(gate_result, str(output) if output else None)
    except Exception as e:
        return FileOperationResult(
            success=False,
            gate_result=gate_result,
            error=str(e),
        )


# =============================================================================
# Bulk Operations
# =============================================================================


def check_multiple_operations(
    operations: list[tuple[str, str]],  # (operation, agent_name)
    registry: "DerivationRegistry",
    thresholds: OperationThresholds = DEFAULT_THRESHOLDS,
) -> list[ConfidenceGateResult]:
    """
    Check multiple operations efficiently.

    Caches derivation lookups for repeated agents.

    Args:
        operations: List of (operation, agent_name) tuples
        registry: The derivation registry
        thresholds: Optional custom thresholds

    Returns:
        List of ConfidenceGateResults (same order as input)
    """
    # Cache derivations by agent
    derivation_cache: dict[str, tuple[float, str]] = {}

    results = []
    for operation, agent_name in operations:
        threshold = thresholds.threshold_for(operation)

        if agent_name not in derivation_cache:
            if not registry.exists(agent_name):
                derivation_cache[agent_name] = (0.0, "")
            else:
                derivation = registry.get(agent_name)
                if derivation:
                    derivation_cache[agent_name] = (
                        derivation.total_confidence,
                        derivation.tier.value,
                    )
                else:
                    derivation_cache[agent_name] = (0.0, "")

        confidence, tier = derivation_cache[agent_name]

        if confidence >= threshold:
            results.append(ConfidenceGateResult.allowed_result(
                operation, agent_name, confidence, threshold, tier
            ))
        else:
            results.append(ConfidenceGateResult.denied_result(
                operation, agent_name, confidence, threshold, tier=tier
            ))

    return results


def get_agent_capabilities(
    agent_name: str,
    registry: "DerivationRegistry",
    thresholds: OperationThresholds = DEFAULT_THRESHOLDS,
) -> dict[str, bool]:
    """
    Get all operations an agent can perform.

    Returns dict mapping operation → allowed.

    Useful for UI to show/hide actions.
    """
    if not registry.exists(agent_name):
        return {op: False for op in ["read", "annotate", "write", "link", "sandbox", "delete", "execute", "promote"]}

    derivation = registry.get(agent_name)
    if derivation is None:
        return {op: False for op in ["read", "annotate", "write", "link", "sandbox", "delete", "execute", "promote"]}

    confidence = derivation.total_confidence

    return {
        op: confidence >= thresholds.threshold_for(op)
        for op in ["read", "annotate", "write", "link", "sandbox", "delete", "execute", "promote"]
    }


__all__ = [
    # Types
    "OperationType",
    "OperationThresholds",
    "DEFAULT_THRESHOLDS",
    "ConfidenceGateResult",
    "FileOperationRequest",
    "FileOperationResult",
    # Main functions
    "check_operation_confidence",
    "gate_file_operation",
    "gate_and_execute",
    # Bulk operations
    "check_multiple_operations",
    "get_agent_capabilities",
]
