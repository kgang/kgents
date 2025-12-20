"""
Cross-Jewel Invocation: Witness Invoking Other Crown Jewels.

"kgentsd is the only jewel that can invoke all other jewels."

At L3 (AUTONOMOUS), Witness can invoke any AGENTESE path on Kent's behalf.
All invocations are gated through ActionGate and logged.

Key Constraints:
- Only L3 (AUTONOMOUS) can invoke mutation paths
- All invocations pass through ActionGate
- Forbidden actions apply to cross-jewel calls
- Read-only paths available at any level

The Pattern (from kgentsd-cross-jewel.md):
    result = await invoker.invoke("world.gestalt.analyze", observer, file="src/main.py")

See: plans/kgentsd-cross-jewel.md
See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from .polynomial import TrustLevel
from .trust import ActionGate, GateDecision, GateResult

if TYPE_CHECKING:
    from protocols.agentese.logos import Logos
    from protocols.agentese.node import Observer


logger = logging.getLogger(__name__)


# =============================================================================
# Invocation Result
# =============================================================================


@dataclass(frozen=True)
class InvocationResult:
    """Result of a cross-jewel invocation."""

    path: str
    success: bool
    result: Any = None
    error: str | None = None
    gate_decision: GateDecision | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_success(self) -> bool:
        """Check if invocation succeeded."""
        return self.success and self.error is None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": self.path,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "gate_decision": self.gate_decision.name if self.gate_decision else None,
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Path Classification
# =============================================================================

# Paths that are read-only (can be invoked at any trust level)
READ_ONLY_ASPECTS = frozenset(
    {
        "manifest",
        "affordances",
        "witness",
        "observe",
        "query",
        "list",
        "get",
        "surface",
        "status",
        "health",
    }
)

# Paths that are mutations (require L3 AUTONOMOUS)
MUTATION_ASPECTS = frozenset(
    {
        "capture",
        "create",
        "update",
        "delete",
        "apply",
        "fix",
        "refactor",
        "commit",
        "push",
        "execute",
        "run",
        "document",
        "forge",
        "build",
    }
)


def classify_path(path: str) -> tuple[str, str, str]:
    """
    Parse an AGENTESE path into components.

    Args:
        path: Full AGENTESE path (e.g., "world.gestalt.analyze")

    Returns:
        Tuple of (context, holon, aspect)

    Raises:
        ValueError: If path is malformed
    """
    parts = path.split(".")
    if len(parts) < 3:
        raise ValueError(f"Path must have at least 3 parts: {path}")

    context = parts[0]
    holon = ".".join(parts[1:-1])
    aspect = parts[-1]

    return context, holon, aspect


def is_read_only_path(path: str) -> bool:
    """
    Check if a path is read-only.

    Read-only paths can be invoked at any trust level.
    Mutation paths require L3 AUTONOMOUS.

    Args:
        path: Full AGENTESE path

    Returns:
        True if path is read-only
    """
    try:
        _, _, aspect = classify_path(path)
        return aspect.lower() in READ_ONLY_ASPECTS
    except ValueError:
        return False


def is_mutation_path(path: str) -> bool:
    """
    Check if a path is a mutation.

    Mutation paths require L3 AUTONOMOUS to invoke.

    Args:
        path: Full AGENTESE path

    Returns:
        True if path is a mutation
    """
    try:
        _, _, aspect = classify_path(path)
        # Mutations are either in the explicit list or not read-only
        return aspect.lower() in MUTATION_ASPECTS or aspect.lower() not in READ_ONLY_ASPECTS
    except ValueError:
        return True  # Conservative: treat malformed paths as mutations


# =============================================================================
# JewelInvoker Class
# =============================================================================


@dataclass
class JewelInvoker:
    """
    Invokes other Crown Jewels on behalf of Witness.

    Only available at L3 (AUTONOMOUS) for mutations.
    Read-only paths can be invoked at any trust level.

    All invocations are:
    1. Gated through ActionGate
    2. Logged for audit trail
    3. Recorded in thought stream

    Example:
        invoker = JewelInvoker(logos, gate, TrustLevel.AUTONOMOUS)

        # Invoke a read-only path (any level)
        result = await invoker.invoke("world.gestalt.manifest", observer)

        # Invoke a mutation path (L3 only)
        result = await invoker.invoke("self.memory.capture", observer, content="...")

    Attributes:
        logos: The Logos instance for path resolution
        gate: ActionGate for trust-gated execution
        trust_level: Current trust level
        log_invocations: Whether to log all invocations (default: True)
    """

    logos: "Logos"
    gate: ActionGate
    trust_level: TrustLevel
    log_invocations: bool = True
    _invocation_log: list[InvocationResult] = field(default_factory=list)

    async def invoke(
        self,
        path: str,
        observer: "Observer",
        **kwargs: Any,
    ) -> InvocationResult:
        """
        Invoke an AGENTESE path with trust gating.

        Args:
            path: Full AGENTESE path (e.g., "world.gestalt.analyze")
            observer: Observer context for the invocation
            **kwargs: Arguments to pass to the aspect

        Returns:
            InvocationResult with success status and result/error

        Note:
            - Read-only paths can be invoked at any trust level
            - Mutation paths require L3 AUTONOMOUS
            - All invocations are gated through ActionGate
        """
        # Determine if this is a read-only or mutation path
        is_readonly = is_read_only_path(path)

        # Build action description for gate
        action_type = "read" if is_readonly else "invoke"
        action_desc = f"{action_type} {path}"

        # Check gate
        gate_result = self.gate.check(action_desc)

        # Handle gate decisions
        if gate_result.decision == GateDecision.FORBIDDEN:
            result = InvocationResult(
                path=path,
                success=False,
                error=f"Forbidden: {gate_result.reason}",
                gate_decision=gate_result.decision,
            )
            self._log_invocation(result)
            return result

        if gate_result.decision == GateDecision.DENY:
            # For mutations, check if we have L3
            if not is_readonly and self.trust_level < TrustLevel.AUTONOMOUS:
                result = InvocationResult(
                    path=path,
                    success=False,
                    error=f"Mutation requires L3 AUTONOMOUS, current: {self.trust_level.description}",
                    gate_decision=gate_result.decision,
                )
                self._log_invocation(result)
                return result

        if gate_result.decision == GateDecision.CONFIRM:
            # L2 can request confirmation for L3 paths
            # For now, we block - confirmation flow handled by ConfirmationManager
            result = InvocationResult(
                path=path,
                success=False,
                error="Requires confirmation (L2 SUGGESTION mode)",
                gate_decision=gate_result.decision,
            )
            self._log_invocation(result)
            return result

        # Execute the invocation
        try:
            invocation_result = await self.logos.invoke(path, observer, **kwargs)

            result = InvocationResult(
                path=path,
                success=True,
                result=invocation_result,
                gate_decision=gate_result.decision,
            )

        except Exception as e:
            logger.error(f"Invocation failed for {path}: {e}", exc_info=True)
            result = InvocationResult(
                path=path,
                success=False,
                error=str(e),
                gate_decision=gate_result.decision,
            )

        self._log_invocation(result)
        return result

    async def invoke_read(
        self,
        path: str,
        observer: "Observer",
        **kwargs: Any,
    ) -> InvocationResult:
        """
        Invoke a read-only path (any trust level).

        Convenience method for read-only invocations.
        Does not check mutation trust requirements.

        Args:
            path: Full AGENTESE path
            observer: Observer context
            **kwargs: Arguments for the aspect

        Returns:
            InvocationResult
        """
        if not is_read_only_path(path):
            logger.warning(f"invoke_read called on mutation path: {path}")

        return await self.invoke(path, observer, **kwargs)

    async def invoke_mutation(
        self,
        path: str,
        observer: "Observer",
        **kwargs: Any,
    ) -> InvocationResult:
        """
        Invoke a mutation path (requires L3 AUTONOMOUS).

        Convenience method for mutation invocations.
        Explicitly checks L3 requirement.

        Args:
            path: Full AGENTESE path
            observer: Observer context
            **kwargs: Arguments for the aspect

        Returns:
            InvocationResult
        """
        if self.trust_level < TrustLevel.AUTONOMOUS:
            return InvocationResult(
                path=path,
                success=False,
                error=f"Mutation requires L3 AUTONOMOUS, current: {self.trust_level.description}",
                gate_decision=GateDecision.DENY,
            )

        return await self.invoke(path, observer, **kwargs)

    def can_invoke(self, path: str) -> bool:
        """
        Check if a path can be invoked at current trust level.

        Args:
            path: Full AGENTESE path

        Returns:
            True if path can be invoked
        """
        # Read-only paths are always allowed (at any trust level)
        if is_read_only_path(path):
            # Still check for forbidden patterns
            action_desc = f"read {path}"
            gate_result = self.gate.check(action_desc)
            if gate_result.decision == GateDecision.FORBIDDEN:
                return False
            return True

        # For mutations, check gate with invoke action
        action_desc = f"invoke {path}"
        gate_result = self.gate.check(action_desc)

        if gate_result.is_denied:
            return False

        # Mutations require L3
        return self.trust_level >= TrustLevel.AUTONOMOUS

    def get_invocation_log(
        self,
        limit: int = 100,
        success_only: bool = False,
    ) -> list[InvocationResult]:
        """
        Get recent invocation log.

        Args:
            limit: Maximum entries to return
            success_only: Only return successful invocations

        Returns:
            List of InvocationResult entries
        """
        log = self._invocation_log
        if success_only:
            log = [r for r in log if r.success]
        return list(reversed(log[-limit:]))

    def _log_invocation(self, result: InvocationResult) -> None:
        """Log an invocation result."""
        if self.log_invocations:
            self._invocation_log.append(result)
            logger.debug(
                f"Invocation: path={result.path}, "
                f"success={result.success}, "
                f"decision={result.gate_decision}"
            )


# =============================================================================
# Factory Functions
# =============================================================================


def create_invoker(
    logos: "Logos",
    trust_level: TrustLevel,
    boundary_checker: Any | None = None,
    log_invocations: bool = True,
) -> JewelInvoker:
    """
    Create a JewelInvoker with appropriate configuration.

    Args:
        logos: Logos instance for path resolution
        trust_level: Current trust level
        boundary_checker: Optional BoundaryChecker (default: created new)
        log_invocations: Whether to log invocations

    Returns:
        Configured JewelInvoker
    """
    from .trust import BoundaryChecker

    gate = ActionGate(
        trust_level=trust_level,
        boundary_checker=boundary_checker or BoundaryChecker(),
    )

    return JewelInvoker(
        logos=logos,
        gate=gate,
        trust_level=trust_level,
        log_invocations=log_invocations,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "InvocationResult",
    "JewelInvoker",
    "create_invoker",
    "is_read_only_path",
    "is_mutation_path",
    "classify_path",
    "READ_ONLY_ASPECTS",
    "MUTATION_ASPECTS",
]
