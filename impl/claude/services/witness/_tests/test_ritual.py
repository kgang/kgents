"""
Tests for Playbook.

Verifies laws:
- Law 1 (Grant Required): Every Playbook has exactly one Grant
- Law 2 (Scope Required): Every Playbook has exactly one Scope
- Law 3 (Guard Transparency): Guards emit Marks on evaluation
- Law 4 (Phase Ordering): Phase transitions follow directed cycle

See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from services.witness.grant import Grant, GrantStatus, ReviewGate
from services.witness.mark import Mark, NPhase
from services.witness.playbook import (
    GuardFailed,
    GuardResult,
    InvalidPhaseTransition,
    MissingGrant,
    MissingScope,
    Playbook,
    PlaybookError,
    PlaybookNotActive,
    PlaybookPhase,
    PlaybookStatus,
    PlaybookStore,
    SentinelGuard,
    get_playbook_store,
    reset_playbook_store,
)
from services.witness.scope import Budget, Scope

# =============================================================================
# Fixtures
# =============================================================================


def make_grant(permissions: frozenset[str] | None = None) -> Grant:
    """Create a granted Grant for testing."""
    return Grant.propose(
        permissions=permissions or frozenset({"file_read", "file_write"}),
    ).grant("kent")


def make_scope(budget: Budget | None = None) -> Scope:
    """Create a valid Scope for testing."""
    return Scope.create(
        description="Test offering",
        scoped_handles=("time.*", "self.*"),
        budget=budget or Budget.standard(),
    )


# =============================================================================
# Law 1: Grant Required Tests
# =============================================================================


class TestLaw1GrantRequired:
    """Law 1: Every Playbook has exactly one Grant."""

    def test_ritual_requires_grant(self) -> None:
        """Playbook.create requires a Grant."""
        offering = make_scope()

        # Without granted Grant
        proposed_grant = Grant.propose(
            permissions=frozenset({"file_read"}),
        )

        with pytest.raises(MissingGrant) as exc_info:
            Playbook.create(
                name="Test",
                grant=proposed_grant,
                scope=offering,
            )

        assert "must be granted" in str(exc_info.value)

    def test_ritual_with_granted_grant_succeeds(self) -> None:
        """Playbook.create succeeds with granted Grant."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(
            name="Test Playbook",
            grant=covenant,
            scope=offering,
        )

        assert ritual.grant_id == covenant.id
        assert ritual.grant == covenant

    def test_ritual_begin_checks_grant(self) -> None:
        """Playbook.begin checks Grant is still active."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(
            name="Test",
            grant=covenant,
            scope=offering,
        )

        # Revoke the Grant
        revoked = covenant.revoke("kent", reason="Test")
        ritual._grant = revoked

        with pytest.raises(MissingGrant) as exc_info:
            ritual.begin()

        assert "not active" in str(exc_info.value)


# =============================================================================
# Law 2: Scope Required Tests
# =============================================================================


class TestLaw2ScopeRequired:
    """Law 2: Every Playbook has exactly one Scope."""

    def test_ritual_requires_scope(self) -> None:
        """Playbook.create requires a valid Scope."""
        covenant = make_grant()

        # Expired offering
        past = datetime.now() - timedelta(hours=1)
        expired_scope = Scope(
            description="Expired",
            scoped_handles=("time.*",),
            expires_at=past,
        )

        with pytest.raises(MissingScope) as exc_info:
            Playbook.create(
                name="Test",
                grant=covenant,
                scope=expired_scope,
            )

        assert "valid" in str(exc_info.value)

    def test_ritual_with_valid_scope_succeeds(self) -> None:
        """Playbook.create succeeds with valid Scope."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(
            name="Test",
            grant=covenant,
            scope=offering,
        )

        assert ritual.scope_id == offering.id
        assert ritual.scope == offering

    def test_ritual_begin_checks_scope(self) -> None:
        """Playbook.begin checks Scope is still valid."""
        covenant = make_grant()
        # Create offering with exhausted budget
        exhausted_scope = Scope.create(
            description="Exhausted",
            scoped_handles=("time.*",),
            budget=Budget(tokens=0),  # Exhausted
        )

        # Use valid offering to create, then swap
        valid_scope = make_scope()
        ritual = Playbook.create(
            name="Test",
            grant=covenant,
            scope=valid_scope,
        )

        # Swap to exhausted offering
        ritual._scope = exhausted_scope

        with pytest.raises(MissingScope):
            ritual.begin()


# =============================================================================
# Law 3: Guard Transparency Tests
# =============================================================================


class TestLaw3GuardTransparency:
    """Law 3: Guards emit Marks on evaluation."""

    def test_guard_evaluation_recorded(self) -> None:
        """Guard evaluations are recorded."""
        covenant = make_grant()
        offering = make_scope()

        guard = SentinelGuard(
            id="budget-guard",
            name="Budget Check",
            check_type="budget",
        )

        ritual = Playbook.create(
            name="Test",
            grant=covenant,
            scope=offering,
            phases=[
                PlaybookPhase(
                    name="Sense",
                    n_phase=NPhase.SENSE,
                    exit_guards=(guard,),
                ),
                PlaybookPhase(
                    name="Act",
                    n_phase=NPhase.ACT,
                ),
                PlaybookPhase(
                    name="Reflect",
                    n_phase=NPhase.REFLECT,
                ),
            ],
        )

        ritual.begin()

        # Transition triggers exit guard evaluation
        ritual.advance_phase(NPhase.ACT)

        # Guard evaluation should be recorded
        assert len(ritual.guard_evaluations) >= 1
        assert ritual.guard_evaluations[0].guard.id == "budget-guard"

    def test_guard_failure_prevents_transition(self) -> None:
        """Failed guard prevents phase transition."""
        covenant = make_grant()
        # Create exhausted offering
        exhausted_scope = Scope.create(
            description="Test",
            scoped_handles=("time.*",),
            budget=Budget(tokens=0),
        )

        # Need valid offering to create ritual
        valid_scope = make_scope()
        guard = SentinelGuard(
            id="budget-guard",
            name="Budget Check",
            check_type="budget",
        )

        ritual = Playbook.create(
            name="Test",
            grant=covenant,
            scope=valid_scope,
            phases=[
                PlaybookPhase(
                    name="Sense",
                    n_phase=NPhase.SENSE,
                    exit_guards=(guard,),
                ),
                PlaybookPhase(name="Act", n_phase=NPhase.ACT),
                PlaybookPhase(name="Reflect", n_phase=NPhase.REFLECT),
            ],
        )

        ritual.begin()

        # Swap to exhausted offering
        ritual._scope = exhausted_scope

        # Transition should fail on exit guard
        with pytest.raises(GuardFailed) as exc_info:
            ritual.advance_phase(NPhase.ACT)

        assert exc_info.value.evaluation.result == GuardResult.FAIL

    def test_time_guard_works(self) -> None:
        """Time guard checks elapsed time."""
        covenant = make_grant()
        offering = make_scope()

        time_guard = SentinelGuard(
            id="time-guard",
            name="Time Limit",
            check_type="time",
            condition="0.001",  # 0.001 seconds - will fail immediately
        )

        ritual = Playbook.create(
            name="Test",
            grant=covenant,
            scope=offering,
            phases=[
                PlaybookPhase(
                    name="Sense",
                    n_phase=NPhase.SENSE,
                    exit_guards=(time_guard,),
                ),
                PlaybookPhase(name="Act", n_phase=NPhase.ACT),
                PlaybookPhase(name="Reflect", n_phase=NPhase.REFLECT),
            ],
        )

        ritual.begin()

        # Even tiny delay exceeds 0.001s
        import time

        time.sleep(0.01)

        with pytest.raises(GuardFailed) as exc_info:
            ritual.advance_phase(NPhase.ACT)

        assert "Time limit" in str(exc_info.value)


# =============================================================================
# Law 4: Phase Ordering Tests
# =============================================================================


class TestLaw4PhaseOrdering:
    """Law 4: Phase transitions follow directed cycle."""

    def test_valid_transitions(self) -> None:
        """Valid phase transitions succeed."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(
            name="Test",
            grant=covenant,
            scope=offering,
        )

        ritual.begin()
        assert ritual.current_phase == NPhase.SENSE

        # SENSE → ACT
        assert ritual.can_transition(NPhase.ACT)
        assert ritual.advance_phase(NPhase.ACT)
        assert ritual.current_phase == NPhase.ACT

        # ACT → REFLECT
        assert ritual.can_transition(NPhase.REFLECT)
        assert ritual.advance_phase(NPhase.REFLECT)
        assert ritual.current_phase == NPhase.REFLECT

        # REFLECT → SENSE (cycle back)
        assert ritual.can_transition(NPhase.SENSE)
        assert ritual.advance_phase(NPhase.SENSE)
        assert ritual.current_phase == NPhase.SENSE

    def test_invalid_transitions_blocked(self) -> None:
        """Invalid phase transitions are blocked."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(
            name="Test",
            grant=covenant,
            scope=offering,
        )

        ritual.begin()
        assert ritual.current_phase == NPhase.SENSE

        # SENSE → REFLECT (invalid, must go through ACT)
        assert not ritual.can_transition(NPhase.REFLECT)
        assert not ritual.advance_phase(NPhase.REFLECT)
        assert ritual.current_phase == NPhase.SENSE  # Unchanged

    def test_same_phase_transition_allowed(self) -> None:
        """Same phase transition is a no-op."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(
            name="Test",
            grant=covenant,
            scope=offering,
        )

        ritual.begin()

        # SENSE → SENSE
        assert ritual.can_transition(NPhase.SENSE)
        assert ritual.advance_phase(NPhase.SENSE)
        assert ritual.current_phase == NPhase.SENSE

    def test_phase_history_tracked(self) -> None:
        """Phase transitions are recorded in history."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(
            name="Test",
            grant=covenant,
            scope=offering,
        )

        ritual.begin()
        ritual.advance_phase(NPhase.ACT)
        ritual.advance_phase(NPhase.REFLECT)

        assert len(ritual.phase_history) == 3
        assert ritual.phase_history[0][0] == NPhase.SENSE
        assert ritual.phase_history[1][0] == NPhase.ACT
        assert ritual.phase_history[2][0] == NPhase.REFLECT


# =============================================================================
# Lifecycle Tests
# =============================================================================


class TestPlaybookLifecycle:
    """Tests for Playbook lifecycle management."""

    def test_lifecycle_pending_to_active(self) -> None:
        """PENDING → ACTIVE transition."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)
        assert ritual.status == PlaybookStatus.PENDING

        ritual.begin()
        assert ritual.status == PlaybookStatus.ACTIVE
        assert ritual.started_at is not None

    def test_lifecycle_active_to_complete(self) -> None:
        """ACTIVE → COMPLETE transition."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)
        ritual.begin()
        ritual.complete()

        assert ritual.status == PlaybookStatus.COMPLETE
        assert ritual.ended_at is not None

    def test_lifecycle_active_to_failed(self) -> None:
        """ACTIVE → FAILED transition."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)
        ritual.begin()
        ritual.fail("Something went wrong")

        assert ritual.status == PlaybookStatus.FAILED
        assert ritual.metadata["failure_reason"] == "Something went wrong"

    def test_lifecycle_cancel(self) -> None:
        """Playbook can be cancelled."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)
        ritual.begin()
        ritual.cancel("User requested")

        assert ritual.status == PlaybookStatus.CANCELLED

    def test_lifecycle_pause_resume(self) -> None:
        """Playbook can be paused and resumed."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)
        ritual.begin()

        ritual.pause()
        assert ritual.status == PlaybookStatus.PAUSED

        ritual.resume()
        assert ritual.status == PlaybookStatus.ACTIVE


# =============================================================================
# Trace Recording Tests
# =============================================================================


class TestTraceRecording:
    """Tests for Mark recording."""

    def test_record_mark(self) -> None:
        """Traces can be recorded."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)
        ritual.begin()

        trace = Mark.from_thought("Test thought", "git")
        ritual.record_mark(trace)

        assert ritual.mark_count == 1
        assert trace.id in ritual.mark_ids

    def test_duplicate_trace_ignored(self) -> None:
        """Recording same trace twice is idempotent."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)
        ritual.begin()

        trace = Mark.from_thought("Test", "git")
        ritual.record_mark(trace)
        ritual.record_mark(trace)  # Duplicate

        assert ritual.mark_count == 1


# =============================================================================
# PlaybookStore Tests
# =============================================================================


class TestPlaybookStore:
    """Tests for PlaybookStore."""

    def setup_method(self) -> None:
        """Reset store before each test."""
        reset_playbook_store()

    def test_add_and_get(self) -> None:
        """Basic add and get operations."""
        store = get_playbook_store()
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)
        store.add(ritual)

        retrieved = store.get(ritual.id)
        assert retrieved is not None
        assert retrieved.id == ritual.id

    def test_active_filter(self) -> None:
        """active() returns only active Playbooks."""
        store = PlaybookStore()
        covenant = make_grant()
        offering = make_scope()

        active = Playbook.create(name="Active", grant=covenant, scope=offering)
        active.begin()

        pending = Playbook.create(name="Pending", grant=covenant, scope=offering)

        complete = Playbook.create(name="Complete", grant=covenant, scope=offering)
        complete.begin()
        complete.complete()

        store.add(active)
        store.add(pending)
        store.add(complete)

        active_list = store.active()
        assert len(active_list) == 1
        assert active_list[0].id == active.id


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Tests for to_dict/from_dict roundtrip."""

    def test_sentinel_guard_roundtrip(self) -> None:
        """SentinelGuard serializes correctly."""
        original = SentinelGuard(
            id="test-guard",
            name="Test Guard",
            description="A test guard",
            check_type="budget",
            condition="tokens > 0",
        )

        data = original.to_dict()
        restored = SentinelGuard.from_dict(data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.check_type == original.check_type

    def test_ritual_phase_roundtrip(self) -> None:
        """PlaybookPhase serializes correctly."""
        original = PlaybookPhase(
            name="Act",
            n_phase=NPhase.ACT,
            allowed_actions=("file_write", "git_commit"),
            timeout_seconds=300.0,
        )

        data = original.to_dict()
        restored = PlaybookPhase.from_dict(data)

        assert restored.name == original.name
        assert restored.n_phase == original.n_phase
        assert restored.allowed_actions == original.allowed_actions

    def test_ritual_roundtrip(self) -> None:
        """Playbook serializes correctly (without Grant/Scope)."""
        covenant = make_grant()
        offering = make_scope()

        original = Playbook.create(
            name="Test Playbook",
            grant=covenant,
            scope=offering,
            description="A test ritual",
        )
        original.begin()
        original.advance_phase(NPhase.ACT)

        data = original.to_dict()
        restored = Playbook.from_dict(data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.current_phase == NPhase.ACT
        assert restored.status == PlaybookStatus.ACTIVE
        assert len(restored.phase_history) == 2


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge cases for robustness."""

    def test_cannot_begin_twice(self) -> None:
        """Cannot begin an already active Playbook."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)
        ritual.begin()

        with pytest.raises(PlaybookError):
            ritual.begin()

    def test_cannot_complete_pending(self) -> None:
        """Cannot complete a pending Playbook."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)

        with pytest.raises(PlaybookNotActive):
            ritual.complete()

    def test_cannot_advance_phase_when_pending(self) -> None:
        """Cannot advance phase when not active."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)

        with pytest.raises(PlaybookNotActive):
            ritual.advance_phase(NPhase.ACT)

    def test_duration_calculation(self) -> None:
        """Duration is calculated correctly."""
        covenant = make_grant()
        offering = make_scope()

        ritual = Playbook.create(name="Test", grant=covenant, scope=offering)
        assert ritual.duration_seconds is None  # Not started

        ritual.begin()
        import time

        time.sleep(0.1)

        duration = ritual.duration_seconds
        assert duration is not None
        assert duration >= 0.1

        ritual.complete()
        final_duration = ritual.duration_seconds
        assert final_duration is not None
        assert final_duration >= 0.1
