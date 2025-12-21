"""
Tests for Grant.

Verifies laws:
- Law 1 (Required): Sensitive operations require granted Grant
- Law 2 (Revocable): Grants can be revoked at any time
- Law 3 (Gated): Review gates trigger on threshold

See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta

import pytest

from services.witness.grant import (
    GateFallback,
    GateTriggered,
    Grant,
    GrantEnforcer,
    GrantError,
    GrantId,
    GrantNotGranted,
    GrantRevoked,
    GrantStatus,
    GrantStore,
    ReviewGate,
    get_grant_store,
    reset_grant_store,
)

# =============================================================================
# Law 1: Grant Required Tests
# =============================================================================


class TestLaw1GrantRequired:
    """Law 1: Sensitive operations require granted Grant."""

    def test_proposed_covenant_not_active(self) -> None:
        """Proposed Grant is not active."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read"}),
            reason="Test",
        )

        assert covenant.status == GrantStatus.PROPOSED
        assert not covenant.is_active

    def test_granted_covenant_is_active(self) -> None:
        """Granted Grant is active."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read"}),
        ).grant("kent")

        assert covenant.status == GrantStatus.GRANTED
        assert covenant.is_active
        assert covenant.granted_by == "kent"
        assert covenant.granted_at is not None

    def test_check_permission_requires_granted(self) -> None:
        """check_permission raises for non-granted Grant."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read"}),
        )

        with pytest.raises(GrantNotGranted) as exc_info:
            covenant.check_permission("file_read")

        assert "not granted" in str(exc_info.value)

    def test_check_permission_succeeds_when_granted(self) -> None:
        """check_permission succeeds for granted Grant."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read", "file_write"}),
        ).grant("kent")

        # Should not raise
        covenant.check_permission("file_read")
        covenant.check_permission("file_write")

    def test_check_permission_fails_for_missing(self) -> None:
        """check_permission fails for permissions not in Grant."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read"}),
        ).grant("kent")

        with pytest.raises(GrantNotGranted) as exc_info:
            covenant.check_permission("git_push")

        assert "git_push" in str(exc_info.value)

    def test_has_permission_check(self) -> None:
        """has_permission returns correct boolean."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read", "file_write"}),
        ).grant("kent")

        assert covenant.has_permission("file_read")
        assert covenant.has_permission("file_write")
        assert not covenant.has_permission("git_push")


# =============================================================================
# Law 2: Revocable Tests
# =============================================================================


class TestLaw2Revocable:
    """Law 2: Grants can be revoked at any time."""

    def test_covenant_can_be_revoked(self) -> None:
        """Granted Grant can be revoked."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read"}),
        ).grant("kent")

        revoked = covenant.revoke("kent", reason="No longer needed")

        assert revoked.status == GrantStatus.REVOKED
        assert revoked.revoked_by == "kent"
        assert revoked.revoked_at is not None
        assert revoked.revoke_reason == "No longer needed"
        assert not revoked.is_active

    def test_revoked_covenant_check_raises(self) -> None:
        """Revoked Grant raises on permission check."""
        covenant = (
            Grant.propose(
                permissions=frozenset({"file_read"}),
            )
            .grant("kent")
            .revoke("kent")
        )

        with pytest.raises(GrantRevoked) as exc_info:
            covenant.check_permission("file_read")

        assert "revoked" in str(exc_info.value)

    def test_proposed_can_be_revoked(self) -> None:
        """Proposed Grant can also be revoked (cancelled)."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read"}),
        )

        revoked = covenant.revoke("kent", reason="Changed mind")
        assert revoked.status == GrantStatus.REVOKED

    def test_cannot_revoke_already_revoked(self) -> None:
        """Cannot revoke an already revoked Grant."""
        covenant = (
            Grant.propose(
                permissions=frozenset({"file_read"}),
            )
            .grant("kent")
            .revoke("kent")
        )

        with pytest.raises(GrantError) as exc_info:
            covenant.revoke("kent")

        assert "Cannot revoke from REVOKED" in str(exc_info.value)


# =============================================================================
# Law 3: Gated Tests
# =============================================================================


class TestLaw3Gated:
    """Law 3: Review gates trigger on threshold."""

    def test_gate_triggers_at_threshold(self) -> None:
        """Review gate triggers when threshold reached."""
        covenant = Grant.propose(
            permissions=frozenset({"git_push"}),
            review_gates=(ReviewGate("git_push", threshold=3),),
        ).grant("kent")

        enforcer = GrantEnforcer(covenant)

        # First two pushes OK
        enforcer.check("git_push")
        enforcer.check("git_push")

        # Third push triggers gate
        with pytest.raises(GateTriggered) as exc_info:
            enforcer.check("git_push")

        assert exc_info.value.gate.trigger == "git_push"

    def test_gate_threshold_one(self) -> None:
        """Gate with threshold=1 triggers on first use."""
        covenant = Grant.propose(
            permissions=frozenset({"file_delete"}),
            review_gates=(ReviewGate("file_delete", threshold=1),),
        ).grant("kent")

        enforcer = GrantEnforcer(covenant)

        with pytest.raises(GateTriggered):
            enforcer.check("file_delete")

    def test_gate_reset_after_approval(self) -> None:
        """Gate counter resets after approval."""
        covenant = Grant.propose(
            permissions=frozenset({"git_push"}),
            review_gates=(ReviewGate("git_push", threshold=2),),
        ).grant("kent")

        enforcer = GrantEnforcer(covenant)

        # Trigger gate
        enforcer.check("git_push")
        with pytest.raises(GateTriggered):
            enforcer.check("git_push")

        # Approve
        enforcer.approve_gate("git_push")

        # Can push again (counter reset)
        enforcer.check("git_push")  # OK
        with pytest.raises(GateTriggered):
            enforcer.check("git_push")  # Triggers again

    def test_no_gate_for_ungated_operations(self) -> None:
        """Operations without gates don't trigger."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read", "git_push"}),
            review_gates=(ReviewGate("git_push", threshold=1),),
        ).grant("kent")

        enforcer = GrantEnforcer(covenant)

        # file_read has no gate, unlimited uses
        for _ in range(100):
            enforcer.check("file_read")  # Should not raise

    def test_gate_pending_status(self) -> None:
        """is_gate_pending returns correct status."""
        covenant = Grant.propose(
            permissions=frozenset({"git_push"}),
            review_gates=(ReviewGate("git_push", threshold=1),),
        ).grant("kent")

        enforcer = GrantEnforcer(covenant)

        assert not enforcer.is_gate_pending("git_push")

        try:
            enforcer.check("git_push")
        except GateTriggered:
            pass

        assert enforcer.is_gate_pending("git_push")

        enforcer.approve_gate("git_push")
        assert not enforcer.is_gate_pending("git_push")


# =============================================================================
# Status Transition Tests
# =============================================================================


class TestStatusTransitions:
    """Tests for Grant status transitions."""

    def test_propose_to_grant(self) -> None:
        """PROPOSED → GRANTED transition."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read"}),
        )
        assert covenant.status == GrantStatus.PROPOSED

        granted = covenant.grant("kent")
        assert granted.status == GrantStatus.GRANTED

    def test_propose_to_negotiate_to_grant(self) -> None:
        """PROPOSED → NEGOTIATING → GRANTED transition."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read"}),
        )

        negotiating = covenant.negotiate()
        assert negotiating.status == GrantStatus.NEGOTIATING

        granted = negotiating.grant("kent")
        assert granted.status == GrantStatus.GRANTED

    def test_cannot_grant_from_revoked(self) -> None:
        """Cannot grant from REVOKED status."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read"}),
        ).revoke("kent")

        with pytest.raises(GrantError) as exc_info:
            covenant.grant("kent")

        assert "Cannot grant from REVOKED" in str(exc_info.value)

    def test_amend_creates_new_proposed(self) -> None:
        """amend() creates a new PROPOSED Grant."""
        original = Grant.propose(
            permissions=frozenset({"file_read"}),
        ).grant("kent")

        amended = original.amend(
            permissions=frozenset({"file_read", "file_write"}),
        )

        # New Grant
        assert amended.id != original.id
        assert amended.status == GrantStatus.PROPOSED

        # Updated permissions
        assert "file_write" in amended.permissions

        # Tracks amendment
        assert "amends" in amended.metadata


# =============================================================================
# Immutability Tests
# =============================================================================


class TestImmutability:
    """Tests for Grant immutability."""

    def test_covenant_is_frozen(self) -> None:
        """Grant is frozen dataclass."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read"}),
        )

        with pytest.raises(FrozenInstanceError):
            covenant.status = GrantStatus.GRANTED  # type: ignore[misc]

    def test_review_gate_is_frozen(self) -> None:
        """ReviewGate is frozen."""
        gate = ReviewGate("git_push", threshold=3)

        with pytest.raises(FrozenInstanceError):
            gate.threshold = 5  # type: ignore[misc]


# =============================================================================
# Expiry Tests
# =============================================================================


class TestGrantExpiry:
    """Tests for Grant expiry."""

    def test_expired_covenant_not_active(self) -> None:
        """Expired Grant is not active."""
        past = datetime.now() - timedelta(hours=1)
        covenant = Grant(
            permissions=frozenset({"file_read"}),
            status=GrantStatus.GRANTED,
            granted_by="kent",
            granted_at=datetime.now() - timedelta(hours=2),
            expires_at=past,
        )

        assert not covenant.is_active

    def test_expired_check_raises(self) -> None:
        """Expired Grant check raises GrantError."""
        past = datetime.now() - timedelta(hours=1)
        covenant = Grant(
            permissions=frozenset({"file_read"}),
            status=GrantStatus.GRANTED,
            granted_by="kent",
            expires_at=past,
        )

        with pytest.raises(GrantError) as exc_info:
            covenant.check_active()

        assert "expired" in str(exc_info.value)


# =============================================================================
# GrantStore Tests
# =============================================================================


class TestGrantStore:
    """Tests for GrantStore."""

    def setup_method(self) -> None:
        """Reset store before each test."""
        reset_grant_store()

    def test_add_and_get(self) -> None:
        """Basic add and get operations."""
        store = get_grant_store()
        covenant = Grant.propose(permissions=frozenset({"file_read"}))

        store.add(covenant)
        retrieved = store.get(covenant.id)

        assert retrieved is not None
        assert retrieved.id == covenant.id

    def test_active_filter(self) -> None:
        """active() returns only active Grants."""
        store = GrantStore()

        active = Grant.propose(permissions=frozenset({"file_read"})).grant("kent")
        proposed = Grant.propose(permissions=frozenset({"file_write"}))
        revoked = Grant.propose(permissions=frozenset({"git_push"})).grant("kent").revoke("kent")

        store.add(active)
        store.add(proposed)
        store.add(revoked)

        active_list = store.active()
        assert len(active_list) == 1
        assert active_list[0].id == active.id

    def test_pending_filter(self) -> None:
        """pending() returns PROPOSED and NEGOTIATING Grants."""
        store = GrantStore()

        proposed = Grant.propose(permissions=frozenset({"file_read"}))
        negotiating = Grant.propose(permissions=frozenset({"file_write"})).negotiate()
        granted = Grant.propose(permissions=frozenset({"git_push"})).grant("kent")

        store.add(proposed)
        store.add(negotiating)
        store.add(granted)

        pending = store.pending()
        assert len(pending) == 2

    def test_revoked_filter(self) -> None:
        """revoked() returns revoked Grants."""
        store = GrantStore()

        active = Grant.propose(permissions=frozenset({"file_read"})).grant("kent")
        revoked = Grant.propose(permissions=frozenset({"git_push"})).grant("kent").revoke("kent")

        store.add(active)
        store.add(revoked)

        revoked_list = store.revoked()
        assert len(revoked_list) == 1
        assert revoked_list[0].id == revoked.id


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Tests for to_dict/from_dict roundtrip."""

    def test_review_gate_roundtrip(self) -> None:
        """ReviewGate serializes and deserializes correctly."""
        original = ReviewGate(
            trigger="git_push",
            description="Review pushes",
            threshold=5,
            timeout_seconds=600.0,
            fallback=GateFallback.ESCALATE,
        )

        data = original.to_dict()
        restored = ReviewGate.from_dict(data)

        assert restored.trigger == original.trigger
        assert restored.description == original.description
        assert restored.threshold == original.threshold
        assert restored.timeout_seconds == original.timeout_seconds
        assert restored.fallback == original.fallback

    def test_covenant_roundtrip(self) -> None:
        """Grant serializes and deserializes correctly."""
        original = Grant.propose(
            permissions=frozenset({"file_read", "file_write", "git_commit"}),
            review_gates=(
                ReviewGate("git_push", threshold=1),
                ReviewGate("file_delete", threshold=3),
            ),
            reason="Implement feature X",
        ).grant("kent")

        data = original.to_dict()
        restored = Grant.from_dict(data)

        assert restored.id == original.id
        assert restored.permissions == original.permissions
        assert restored.status == original.status
        assert restored.granted_by == original.granted_by
        assert len(restored.review_gates) == 2

    def test_revoked_covenant_roundtrip(self) -> None:
        """Revoked Grant preserves revocation info."""
        original = (
            Grant.propose(
                permissions=frozenset({"file_read"}),
            )
            .grant("kent")
            .revoke("kent", reason="Security concern")
        )

        data = original.to_dict()
        restored = Grant.from_dict(data)

        assert restored.status == GrantStatus.REVOKED
        assert restored.revoked_by == "kent"
        assert restored.revoke_reason == "Security concern"


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge cases for robustness."""

    def test_empty_permissions(self) -> None:
        """Grant with empty permissions grants nothing."""
        covenant = Grant.propose(
            permissions=frozenset(),
        ).grant("kent")

        assert covenant.is_active

        with pytest.raises(GrantNotGranted):
            covenant.check_permission("anything")

    def test_multiple_gates_same_operation(self) -> None:
        """Multiple gates can exist (first wins)."""
        covenant = Grant.propose(
            permissions=frozenset({"git_push"}),
            review_gates=(ReviewGate("git_push", threshold=2),),
        ).grant("kent")

        gate = covenant.get_gate("git_push")
        assert gate is not None
        assert gate.threshold == 2

    def test_enforcer_without_gates(self) -> None:
        """Enforcer works with no gates."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read", "file_write"}),
            review_gates=(),
        ).grant("kent")

        enforcer = GrantEnforcer(covenant)

        # All permitted operations work without limit
        for _ in range(100):
            enforcer.check("file_read")
            enforcer.check("file_write")

    def test_enforcer_permission_check_before_gate(self) -> None:
        """Enforcer checks permission before gate count."""
        covenant = Grant.propose(
            permissions=frozenset({"file_read"}),
            review_gates=(ReviewGate("git_push", threshold=1),),
        ).grant("kent")

        enforcer = GrantEnforcer(covenant)

        # git_push not in permissions
        with pytest.raises(GrantNotGranted):
            enforcer.check("git_push")
