"""
Tests for ActionGate: Trust-Gated Execution.

Verifies:
- Gate decisions at each trust level
- Capability mapping
- Boundary integration
- Trust level updates
"""

import pytest

from services.witness.polynomial import TrustLevel
from services.witness.trust.gate import (
    ACTION_CAPABILITIES,
    ActionGate,
    GateDecision,
    GateResult,
    get_required_level,
)

# =============================================================================
# get_required_level Tests
# =============================================================================


class TestGetRequiredLevel:
    """Tests for get_required_level function."""

    def test_read_only_actions(self) -> None:
        """L0 actions should require READ_ONLY."""
        assert get_required_level("observe git log") == TrustLevel.READ_ONLY
        assert get_required_level("analyze test results") == TrustLevel.READ_ONLY
        assert get_required_level("read file contents") == TrustLevel.READ_ONLY
        assert get_required_level("query database schema") == TrustLevel.READ_ONLY

    def test_bounded_actions(self) -> None:
        """L1 actions should require BOUNDED."""
        assert get_required_level("cache results in .kgents") == TrustLevel.BOUNDED
        assert get_required_level("write .kgents/config") == TrustLevel.BOUNDED
        assert get_required_level("update config in .kgents") == TrustLevel.BOUNDED

    def test_suggestion_actions(self) -> None:
        """L2 actions should require SUGGESTION."""
        assert get_required_level("suggest refactoring") == TrustLevel.SUGGESTION
        assert get_required_level("propose code change") == TrustLevel.SUGGESTION
        assert get_required_level("draft fix for bug") == TrustLevel.SUGGESTION
        assert get_required_level("recommend improvement") == TrustLevel.SUGGESTION

    def test_autonomous_actions(self) -> None:
        """L3 actions should require AUTONOMOUS."""
        assert get_required_level("commit changes") == TrustLevel.AUTONOMOUS
        assert get_required_level("push to remote") == TrustLevel.AUTONOMOUS
        assert get_required_level("run tests") == TrustLevel.AUTONOMOUS
        assert get_required_level("execute script") == TrustLevel.AUTONOMOUS
        assert get_required_level("apply patch") == TrustLevel.AUTONOMOUS
        assert get_required_level("fix typo in file") == TrustLevel.AUTONOMOUS
        assert get_required_level("refactor module") == TrustLevel.AUTONOMOUS
        assert get_required_level("create pr") == TrustLevel.AUTONOMOUS

    def test_unknown_actions_default_to_autonomous(self) -> None:
        """Unknown actions should require AUTONOMOUS (conservative)."""
        assert get_required_level("unknown_action") == TrustLevel.AUTONOMOUS
        assert get_required_level("xyz123") == TrustLevel.AUTONOMOUS

    def test_case_insensitive(self) -> None:
        """Action matching should be case-insensitive."""
        assert get_required_level("OBSERVE") == TrustLevel.READ_ONLY
        assert get_required_level("Commit") == TrustLevel.AUTONOMOUS
        assert get_required_level("SUGGEST") == TrustLevel.SUGGESTION


# =============================================================================
# ActionGate Tests
# =============================================================================


class TestActionGate:
    """Tests for ActionGate class."""

    def test_l0_can_observe(self) -> None:
        """L0 can observe without restriction."""
        gate = ActionGate(TrustLevel.READ_ONLY)
        result = gate.check("observe git log")

        assert result.decision == GateDecision.ALLOW
        assert result.is_allowed
        assert not result.is_denied

    def test_l0_cannot_commit(self) -> None:
        """L0 cannot commit."""
        gate = ActionGate(TrustLevel.READ_ONLY)
        result = gate.check("commit changes")

        assert result.decision == GateDecision.DENY
        assert result.is_denied
        assert not result.is_allowed
        assert result.required_level == TrustLevel.AUTONOMOUS

    def test_l1_can_write_kgents(self) -> None:
        """L1 can write to .kgents directory."""
        gate = ActionGate(TrustLevel.BOUNDED)
        result = gate.check("write .kgents/cache")

        assert result.decision == GateDecision.ALLOW

    def test_l1_cannot_commit(self) -> None:
        """L1 cannot commit."""
        gate = ActionGate(TrustLevel.BOUNDED)
        result = gate.check("commit changes")

        assert result.decision == GateDecision.DENY

    def test_l2_can_suggest(self) -> None:
        """L2 can make suggestions."""
        gate = ActionGate(TrustLevel.SUGGESTION)
        result = gate.check("suggest refactoring")

        assert result.decision == GateDecision.ALLOW

    def test_l2_requires_confirmation_for_autonomous_actions(self) -> None:
        """L2 requires confirmation for L3 actions."""
        gate = ActionGate(TrustLevel.SUGGESTION)
        result = gate.check("commit changes")

        assert result.decision == GateDecision.CONFIRM
        assert result.requires_confirmation

    def test_l3_can_commit_with_logging(self) -> None:
        """L3 can commit with logging."""
        gate = ActionGate(TrustLevel.AUTONOMOUS)
        result = gate.check("commit changes")

        assert result.decision == GateDecision.LOG
        assert result.is_allowed

    def test_l3_logs_all_actions(self) -> None:
        """L3 logs all L3 actions."""
        gate = ActionGate(TrustLevel.AUTONOMOUS)

        for action in ["commit", "push", "execute", "apply"]:
            result = gate.check(action)
            assert result.decision == GateDecision.LOG

    def test_forbidden_action_denied_at_any_level(self) -> None:
        """Forbidden actions are denied at any trust level."""
        for level in TrustLevel:
            gate = ActionGate(level)
            result = gate.check("git push --force origin main")

            assert result.decision == GateDecision.FORBIDDEN
            assert result.is_denied
            assert result.boundary_violation is not None

    def test_can_perform_capability(self) -> None:
        """can_perform checks capability availability."""
        gate = ActionGate(TrustLevel.SUGGESTION)

        assert gate.can_perform("observe")
        assert gate.can_perform("suggest")
        assert not gate.can_perform("commit")

    def test_update_trust(self) -> None:
        """Trust level can be updated."""
        gate = ActionGate(TrustLevel.READ_ONLY)
        assert gate.check("commit").decision == GateDecision.DENY

        gate.update_trust(TrustLevel.AUTONOMOUS)
        assert gate.check("commit").decision == GateDecision.LOG


class TestGateResult:
    """Tests for GateResult properties."""

    def test_is_allowed(self) -> None:
        """is_allowed is True for ALLOW and LOG."""
        assert GateResult(
            decision=GateDecision.ALLOW,
            action="test",
            trust_level=TrustLevel.READ_ONLY,
            required_level=TrustLevel.READ_ONLY,
        ).is_allowed

        assert GateResult(
            decision=GateDecision.LOG,
            action="test",
            trust_level=TrustLevel.AUTONOMOUS,
            required_level=TrustLevel.AUTONOMOUS,
        ).is_allowed

    def test_requires_confirmation(self) -> None:
        """requires_confirmation is True only for CONFIRM."""
        assert GateResult(
            decision=GateDecision.CONFIRM,
            action="test",
            trust_level=TrustLevel.SUGGESTION,
            required_level=TrustLevel.AUTONOMOUS,
        ).requires_confirmation

        assert not GateResult(
            decision=GateDecision.ALLOW,
            action="test",
            trust_level=TrustLevel.READ_ONLY,
            required_level=TrustLevel.READ_ONLY,
        ).requires_confirmation

    def test_is_denied(self) -> None:
        """is_denied is True for DENY and FORBIDDEN."""
        assert GateResult(
            decision=GateDecision.DENY,
            action="test",
            trust_level=TrustLevel.READ_ONLY,
            required_level=TrustLevel.AUTONOMOUS,
        ).is_denied

        assert GateResult(
            decision=GateDecision.FORBIDDEN,
            action="test",
            trust_level=TrustLevel.AUTONOMOUS,
            required_level=TrustLevel.AUTONOMOUS,
        ).is_denied
