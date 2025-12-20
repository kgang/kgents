"""
ActionGate: Trust-Gated Execution for Witness Actions.

Every action is gated by trust level:
- ALLOW: Execute immediately (level sufficient)
- DENY: Cannot execute at current level
- CONFIRM: Needs human confirmation (Level 2)
- LOG: Execute with logging (Level 3)

The Pattern (from crown-jewel-patterns.md):
    "Container Owns Workflow" - ActionGate owns action lifecycle.

Example:
    >>> gate = ActionGate(TrustLevel.SUGGESTION)
    >>> result = await gate.check("git commit -m 'fix: typo'")
    >>> print(result.decision)
    GateDecision.CONFIRM

See: plans/kgentsd-trust-system.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from services.witness.polynomial import TrustLevel

from .boundaries import BoundaryChecker

if TYPE_CHECKING:
    pass


# =============================================================================
# Gate Decision
# =============================================================================


class GateDecision(Enum):
    """Decision from the action gate."""

    ALLOW = auto()  # Execute immediately
    DENY = auto()  # Cannot execute at current level
    CONFIRM = auto()  # Needs human confirmation (L2)
    LOG = auto()  # Execute with logging (L3)
    FORBIDDEN = auto()  # Action is forbidden at any level


# =============================================================================
# Gate Result
# =============================================================================


@dataclass
class GateResult:
    """Result of gating an action."""

    decision: GateDecision
    action: str
    trust_level: TrustLevel
    required_level: TrustLevel
    reason: str = ""
    boundary_violation: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_allowed(self) -> bool:
        """Check if action is allowed (ALLOW or LOG)."""
        return self.decision in (GateDecision.ALLOW, GateDecision.LOG)

    @property
    def requires_confirmation(self) -> bool:
        """Check if action requires confirmation."""
        return self.decision == GateDecision.CONFIRM

    @property
    def is_denied(self) -> bool:
        """Check if action is denied."""
        return self.decision in (GateDecision.DENY, GateDecision.FORBIDDEN)


# =============================================================================
# Action Capability Mapping
# =============================================================================

# Map action patterns to required trust levels
ACTION_CAPABILITIES: dict[str, TrustLevel] = {
    # L0: Read-only observation
    "observe": TrustLevel.READ_ONLY,
    "analyze": TrustLevel.READ_ONLY,
    "read": TrustLevel.READ_ONLY,
    "query": TrustLevel.READ_ONLY,
    # L1: Bounded modifications
    "cache": TrustLevel.BOUNDED,
    "write .kgents": TrustLevel.BOUNDED,
    "update config": TrustLevel.BOUNDED,
    # L2: Suggestions
    "suggest": TrustLevel.SUGGESTION,
    "propose": TrustLevel.SUGGESTION,
    "draft": TrustLevel.SUGGESTION,
    "recommend": TrustLevel.SUGGESTION,
    # L3: Autonomous actions
    "commit": TrustLevel.AUTONOMOUS,
    "push": TrustLevel.AUTONOMOUS,
    "run tests": TrustLevel.AUTONOMOUS,
    "execute": TrustLevel.AUTONOMOUS,
    "apply": TrustLevel.AUTONOMOUS,
    "fix": TrustLevel.AUTONOMOUS,
    "refactor": TrustLevel.AUTONOMOUS,
    "create pr": TrustLevel.AUTONOMOUS,
}


def get_required_level(action: str) -> TrustLevel:
    """
    Determine required trust level for an action.

    Uses pattern matching against known capability keywords.
    Defaults to AUTONOMOUS for unknown actions (conservative).
    """
    action_lower = action.lower()

    # Check each capability pattern
    for pattern, level in ACTION_CAPABILITIES.items():
        if pattern in action_lower:
            return level

    # Default: require autonomous for unknown actions
    return TrustLevel.AUTONOMOUS


# =============================================================================
# ActionGate Class
# =============================================================================


class ActionGate:
    """
    Gates actions based on trust level.

    Every action flows through the gate:
    1. Check if action is forbidden (boundary check)
    2. Determine required trust level
    3. Compare to current trust level
    4. Return decision (ALLOW, DENY, CONFIRM, LOG)

    Example:
        gate = ActionGate(TrustLevel.SUGGESTION)

        # L2 can suggest but not execute
        result = gate.check("suggest refactor")
        assert result.decision == GateDecision.ALLOW

        # L2 can propose commits but requires confirmation
        result = gate.check("git commit -m 'fix'")
        assert result.decision == GateDecision.CONFIRM

        # L3 can execute with logging
        gate = ActionGate(TrustLevel.AUTONOMOUS)
        result = gate.check("git commit -m 'fix'")
        assert result.decision == GateDecision.LOG
    """

    def __init__(
        self,
        trust_level: TrustLevel,
        boundary_checker: BoundaryChecker | None = None,
    ) -> None:
        self.trust_level = trust_level
        self.boundary_checker = boundary_checker or BoundaryChecker()

    def check(self, action: str, target: str | None = None) -> GateResult:
        """
        Check if an action is allowed at the current trust level.

        Args:
            action: The action to check (e.g., "git commit -m 'fix'")
            target: Optional target for the action (e.g., file path)

        Returns:
            GateResult with decision and reason
        """
        full_action = f"{action} {target}" if target else action

        # 1. Check forbidden actions first
        violation = self.boundary_checker.check(full_action)
        if violation:
            return GateResult(
                decision=GateDecision.FORBIDDEN,
                action=action,
                trust_level=self.trust_level,
                required_level=TrustLevel.AUTONOMOUS,
                reason=f"Forbidden: {violation.reason}",
                boundary_violation=violation.pattern,
            )

        # 2. Determine required level
        required_level = get_required_level(full_action)

        # 3. Special case: L2 (SUGGESTION) can request confirmation for L3 actions
        #    L2 can't execute directly, but can propose for human approval
        if self.trust_level == TrustLevel.SUGGESTION and required_level == TrustLevel.AUTONOMOUS:
            return GateResult(
                decision=GateDecision.CONFIRM,
                action=action,
                trust_level=self.trust_level,
                required_level=required_level,
                reason="Awaiting human confirmation",
            )

        # 4. Check if current level is sufficient
        if self.trust_level < required_level:
            return GateResult(
                decision=GateDecision.DENY,
                action=action,
                trust_level=self.trust_level,
                required_level=required_level,
                reason=f"Requires {required_level.description}, current: {self.trust_level.description}",
            )

        # 5. Determine decision based on current level

        if self.trust_level == TrustLevel.AUTONOMOUS:
            # L3: Log all actions
            return GateResult(
                decision=GateDecision.LOG,
                action=action,
                trust_level=self.trust_level,
                required_level=required_level,
                reason="Executing with full logging",
            )

        # Default: Allow
        return GateResult(
            decision=GateDecision.ALLOW,
            action=action,
            trust_level=self.trust_level,
            required_level=required_level,
            reason="Allowed at current level",
        )

    def can_perform(self, capability: str) -> bool:
        """
        Quick check if a capability is available at current trust level.

        Args:
            capability: The capability to check (e.g., "commit", "suggest")

        Returns:
            True if capability is available
        """
        required = get_required_level(capability)
        return self.trust_level >= required

    def update_trust(self, new_level: TrustLevel) -> None:
        """Update the trust level."""
        self.trust_level = new_level


__all__ = [
    "ActionGate",
    "GateDecision",
    "GateResult",
    "get_required_level",
    "ACTION_CAPABILITIES",
]
