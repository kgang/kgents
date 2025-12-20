"""
Tool Trust Gate: Witness Integration for Trust-Gated Tool Execution.

The Trust Gate enforces trust requirements before tool execution:
- L0 (READ_ONLY): Read-only tools (read, glob, grep)
- L1 (BOUNDED): Bounded writes (.kgents/ only)
- L2 (SUGGESTION): Write tools with confirmation
- L3 (AUTONOMOUS): System tools (bash, web)

Integration with Witness:
- Gets current trust level from WitnessPersistence
- Records gate decisions in audit trail
- Emits events for UI feedback

Pattern (from crown-jewel-patterns.md):
- Pattern 4: Signal Aggregation (multiple checks combine)
- Pattern 6: Async-Safe Event Emission

See: spec/services/tooling.md §5
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from services.witness import TrustLevel, WitnessPersistence

logger = logging.getLogger(__name__)


# =============================================================================
# Trust Constants
# =============================================================================

# Default trust requirements by tool path
TOOL_TRUST_REQUIREMENTS: dict[str, int] = {
    # File tools
    "file.read": 0,  # L0 - Read-only
    "file.write": 2,  # L2 - Requires confirmation
    "file.edit": 2,  # L2 - Requires confirmation
    "file.glob": 0,  # L0 - Read-only
    "file.notebook": 2,  # L2 - Requires confirmation
    # Search tools
    "search.grep": 0,  # L0 - Read-only
    "search.lsp": 0,  # L0 - Read-only
    # System tools
    "system.bash": 3,  # L3 - Autonomous only
    "system.kill": 2,  # L2 - Requires confirmation
    # Web tools
    "web.fetch": 1,  # L1 - Bounded
    "web.search": 1,  # L1 - Bounded
    # Task tools (self.tools.*)
    "task.list": 0,  # L0 - Read-only
    "task.create": 1,  # L1 - Bounded
    "task.update": 1,  # L1 - Bounded
    # Mode tools
    "mode.plan": 0,  # L0 - Read-only (just enters plan mode)
    "mode.execute": 2,  # L2 - Requires confirmation
    "mode.clarify": 0,  # L0 - Just asks questions
}


# =============================================================================
# Gate Result
# =============================================================================


class GateDecision(Enum):
    """Result of a trust gate check."""

    ALLOWED = auto()  # Proceed with invocation
    DENIED = auto()  # Trust level insufficient
    REQUIRES_CONFIRMATION = auto()  # L2: needs human confirmation
    RATE_LIMITED = auto()  # Too many requests


@dataclass(frozen=True)
class GateResult:
    """
    Result of a trust gate check.

    Contains the decision and metadata about why.
    """

    decision: GateDecision
    tool_path: str
    required_trust: int
    current_trust: int
    message: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def allowed(self) -> bool:
        """Whether invocation is allowed."""
        return self.decision == GateDecision.ALLOWED

    @property
    def requires_confirmation(self) -> bool:
        """Whether human confirmation is required."""
        return self.decision == GateDecision.REQUIRES_CONFIRMATION


# =============================================================================
# Exceptions
# =============================================================================


class TrustViolation(Exception):
    """Trust level insufficient for tool invocation."""

    def __init__(self, message: str, result: GateResult | None = None) -> None:
        super().__init__(message)
        self.result = result


# =============================================================================
# Trust Gate
# =============================================================================


class ToolTrustGate:
    """
    Trust gate for tool invocations.

    Integrates with Witness persistence to:
    - Check current trust level
    - Record gate decisions
    - Emit events for UI

    Example:
        gate = ToolTrustGate(witness_persistence)
        result = await gate.check("file.write", observer)

        if not result.allowed:
            raise TrustViolation(result.message, result)

        if result.requires_confirmation:
            # Await human confirmation
            confirmed = await gate.request_confirmation(...)
    """

    def __init__(
        self,
        witness: "WitnessPersistence | None" = None,
        trust_requirements: dict[str, int] | None = None,
    ) -> None:
        """
        Initialize trust gate.

        Args:
            witness: Optional WitnessPersistence for trust lookup
            trust_requirements: Override default requirements
        """
        self._witness = witness
        self._requirements = trust_requirements or TOOL_TRUST_REQUIREMENTS

    async def check(
        self,
        tool_path: str,
        observer: Any = None,
        git_email: str | None = None,
    ) -> GateResult:
        """
        Check if tool invocation is allowed.

        Args:
            tool_path: Tool path (e.g., "file.write")
            observer: Optional Umwelt for trust context
            git_email: Git email for trust lookup (alternative to observer)

        Returns:
            GateResult with decision and metadata
        """
        # Get required trust level
        required = self._requirements.get(tool_path, 3)  # Default: L3

        # Get current trust level
        current = await self._get_trust_level(observer, git_email)

        # Determine decision
        if current >= required:
            decision = GateDecision.ALLOWED
            message = f"Trust level {current} sufficient for {tool_path}"
        elif current == 2 and required == 2:
            # L2 can proceed with confirmation
            decision = GateDecision.REQUIRES_CONFIRMATION
            message = f"Tool {tool_path} requires confirmation at L2"
        else:
            decision = GateDecision.DENIED
            message = f"Trust level {current} insufficient for {tool_path} (requires {required})"

        result = GateResult(
            decision=decision,
            tool_path=tool_path,
            required_trust=required,
            current_trust=current,
            message=message,
        )

        # Log gate decision
        logger.debug(f"Trust gate: {tool_path} -> {decision.name} (L{current}/L{required})")

        return result

    async def check_or_raise(
        self,
        tool_path: str,
        observer: Any = None,
        git_email: str | None = None,
    ) -> GateResult:
        """
        Check trust and raise if denied.

        Args:
            tool_path: Tool path
            observer: Optional Umwelt
            git_email: Git email

        Returns:
            GateResult (only if allowed or requires_confirmation)

        Raises:
            TrustViolation: If denied
        """
        result = await self.check(tool_path, observer, git_email)

        if result.decision == GateDecision.DENIED:
            raise TrustViolation(result.message, result)

        return result

    async def _get_trust_level(
        self,
        observer: Any,
        git_email: str | None,
    ) -> int:
        """
        Get current trust level.

        Priority:
        1. Observer's trust if available
        2. Witness lookup by git_email
        3. Default to L0 (READ_ONLY)
        """
        # Try to get from observer
        if observer is not None:
            # Observer may have trust_level attribute
            trust = getattr(observer, "trust_level", None)
            if trust is not None:
                return int(trust) if isinstance(trust, int) else trust.value

        # Try witness lookup
        if self._witness is not None and git_email:
            try:
                result = await self._witness.get_trust_level(git_email)
                return result.trust_level.value
            except Exception as e:
                logger.warning(f"Failed to get trust level: {e}")

        # Default to L0
        return 0

    def get_required_trust(self, tool_path: str) -> int:
        """Get required trust level for a tool path."""
        return self._requirements.get(tool_path, 3)

    def set_requirement(self, tool_path: str, trust_level: int) -> None:
        """Override trust requirement for a tool (for testing)."""
        self._requirements[tool_path] = trust_level


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "GateDecision",
    "GateResult",
    "TrustViolation",
    "ToolTrustGate",
    "TOOL_TRUST_REQUIREMENTS",
]
