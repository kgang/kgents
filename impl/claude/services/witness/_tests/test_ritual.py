"""
Tests for Ritual.

Verifies laws:
- Law 1 (Covenant Required): Every Ritual has exactly one Covenant
- Law 2 (Offering Required): Every Ritual has exactly one Offering
- Law 3 (Guard Transparency): Guards emit TraceNodes on evaluation
- Law 4 (Phase Ordering): Phase transitions follow directed cycle

See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from services.witness.covenant import Covenant, CovenantStatus, ReviewGate
from services.witness.offering import Budget, Offering
from services.witness.ritual import (
    GuardFailed,
    GuardResult,
    InvalidPhaseTransition,
    MissingCovenant,
    MissingOffering,
    Ritual,
    RitualError,
    RitualNotActive,
    RitualPhase,
    RitualStatus,
    RitualStore,
    SentinelGuard,
    get_ritual_store,
    reset_ritual_store,
)
from services.witness.trace_node import NPhase, TraceNode

# =============================================================================
# Fixtures
# =============================================================================


def make_covenant(permissions: frozenset[str] | None = None) -> Covenant:
    """Create a granted Covenant for testing."""
    return Covenant.propose(
        permissions=permissions or frozenset({"file_read", "file_write"}),
    ).grant("kent")


def make_offering(budget: Budget | None = None) -> Offering:
    """Create a valid Offering for testing."""
    return Offering.create(
        description="Test offering",
        scoped_handles=("time.*", "self.*"),
        budget=budget or Budget.standard(),
    )


# =============================================================================
# Law 1: Covenant Required Tests
# =============================================================================


class TestLaw1CovenantRequired:
    """Law 1: Every Ritual has exactly one Covenant."""

    def test_ritual_requires_covenant(self) -> None:
        """Ritual.create requires a Covenant."""
        offering = make_offering()

        # Without granted Covenant
        proposed_covenant = Covenant.propose(
            permissions=frozenset({"file_read"}),
        )

        with pytest.raises(MissingCovenant) as exc_info:
            Ritual.create(
                name="Test",
                covenant=proposed_covenant,
                offering=offering,
            )

        assert "must be granted" in str(exc_info.value)

    def test_ritual_with_granted_covenant_succeeds(self) -> None:
        """Ritual.create succeeds with granted Covenant."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(
            name="Test Ritual",
            covenant=covenant,
            offering=offering,
        )

        assert ritual.covenant_id == covenant.id
        assert ritual.covenant == covenant

    def test_ritual_begin_checks_covenant(self) -> None:
        """Ritual.begin checks Covenant is still active."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(
            name="Test",
            covenant=covenant,
            offering=offering,
        )

        # Revoke the Covenant
        revoked = covenant.revoke("kent", reason="Test")
        ritual._covenant = revoked

        with pytest.raises(MissingCovenant) as exc_info:
            ritual.begin()

        assert "not active" in str(exc_info.value)


# =============================================================================
# Law 2: Offering Required Tests
# =============================================================================


class TestLaw2OfferingRequired:
    """Law 2: Every Ritual has exactly one Offering."""

    def test_ritual_requires_offering(self) -> None:
        """Ritual.create requires a valid Offering."""
        covenant = make_covenant()

        # Expired offering
        past = datetime.now() - timedelta(hours=1)
        expired_offering = Offering(
            description="Expired",
            scoped_handles=("time.*",),
            expires_at=past,
        )

        with pytest.raises(MissingOffering) as exc_info:
            Ritual.create(
                name="Test",
                covenant=covenant,
                offering=expired_offering,
            )

        assert "valid" in str(exc_info.value)

    def test_ritual_with_valid_offering_succeeds(self) -> None:
        """Ritual.create succeeds with valid Offering."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(
            name="Test",
            covenant=covenant,
            offering=offering,
        )

        assert ritual.offering_id == offering.id
        assert ritual.offering == offering

    def test_ritual_begin_checks_offering(self) -> None:
        """Ritual.begin checks Offering is still valid."""
        covenant = make_covenant()
        # Create offering with exhausted budget
        exhausted_offering = Offering.create(
            description="Exhausted",
            scoped_handles=("time.*",),
            budget=Budget(tokens=0),  # Exhausted
        )

        # Use valid offering to create, then swap
        valid_offering = make_offering()
        ritual = Ritual.create(
            name="Test",
            covenant=covenant,
            offering=valid_offering,
        )

        # Swap to exhausted offering
        ritual._offering = exhausted_offering

        with pytest.raises(MissingOffering):
            ritual.begin()


# =============================================================================
# Law 3: Guard Transparency Tests
# =============================================================================


class TestLaw3GuardTransparency:
    """Law 3: Guards emit TraceNodes on evaluation."""

    def test_guard_evaluation_recorded(self) -> None:
        """Guard evaluations are recorded."""
        covenant = make_covenant()
        offering = make_offering()

        guard = SentinelGuard(
            id="budget-guard",
            name="Budget Check",
            check_type="budget",
        )

        ritual = Ritual.create(
            name="Test",
            covenant=covenant,
            offering=offering,
            phases=[
                RitualPhase(
                    name="Sense",
                    n_phase=NPhase.SENSE,
                    exit_guards=(guard,),
                ),
                RitualPhase(
                    name="Act",
                    n_phase=NPhase.ACT,
                ),
                RitualPhase(
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
        covenant = make_covenant()
        # Create exhausted offering
        exhausted_offering = Offering.create(
            description="Test",
            scoped_handles=("time.*",),
            budget=Budget(tokens=0),
        )

        # Need valid offering to create ritual
        valid_offering = make_offering()
        guard = SentinelGuard(
            id="budget-guard",
            name="Budget Check",
            check_type="budget",
        )

        ritual = Ritual.create(
            name="Test",
            covenant=covenant,
            offering=valid_offering,
            phases=[
                RitualPhase(
                    name="Sense",
                    n_phase=NPhase.SENSE,
                    exit_guards=(guard,),
                ),
                RitualPhase(name="Act", n_phase=NPhase.ACT),
                RitualPhase(name="Reflect", n_phase=NPhase.REFLECT),
            ],
        )

        ritual.begin()

        # Swap to exhausted offering
        ritual._offering = exhausted_offering

        # Transition should fail on exit guard
        with pytest.raises(GuardFailed) as exc_info:
            ritual.advance_phase(NPhase.ACT)

        assert exc_info.value.evaluation.result == GuardResult.FAIL

    def test_time_guard_works(self) -> None:
        """Time guard checks elapsed time."""
        covenant = make_covenant()
        offering = make_offering()

        time_guard = SentinelGuard(
            id="time-guard",
            name="Time Limit",
            check_type="time",
            condition="0.001",  # 0.001 seconds - will fail immediately
        )

        ritual = Ritual.create(
            name="Test",
            covenant=covenant,
            offering=offering,
            phases=[
                RitualPhase(
                    name="Sense",
                    n_phase=NPhase.SENSE,
                    exit_guards=(time_guard,),
                ),
                RitualPhase(name="Act", n_phase=NPhase.ACT),
                RitualPhase(name="Reflect", n_phase=NPhase.REFLECT),
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
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(
            name="Test",
            covenant=covenant,
            offering=offering,
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
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(
            name="Test",
            covenant=covenant,
            offering=offering,
        )

        ritual.begin()
        assert ritual.current_phase == NPhase.SENSE

        # SENSE → REFLECT (invalid, must go through ACT)
        assert not ritual.can_transition(NPhase.REFLECT)
        assert not ritual.advance_phase(NPhase.REFLECT)
        assert ritual.current_phase == NPhase.SENSE  # Unchanged

    def test_same_phase_transition_allowed(self) -> None:
        """Same phase transition is a no-op."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(
            name="Test",
            covenant=covenant,
            offering=offering,
        )

        ritual.begin()

        # SENSE → SENSE
        assert ritual.can_transition(NPhase.SENSE)
        assert ritual.advance_phase(NPhase.SENSE)
        assert ritual.current_phase == NPhase.SENSE

    def test_phase_history_tracked(self) -> None:
        """Phase transitions are recorded in history."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(
            name="Test",
            covenant=covenant,
            offering=offering,
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


class TestRitualLifecycle:
    """Tests for Ritual lifecycle management."""

    def test_lifecycle_pending_to_active(self) -> None:
        """PENDING → ACTIVE transition."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)
        assert ritual.status == RitualStatus.PENDING

        ritual.begin()
        assert ritual.status == RitualStatus.ACTIVE
        assert ritual.started_at is not None

    def test_lifecycle_active_to_complete(self) -> None:
        """ACTIVE → COMPLETE transition."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)
        ritual.begin()
        ritual.complete()

        assert ritual.status == RitualStatus.COMPLETE
        assert ritual.ended_at is not None

    def test_lifecycle_active_to_failed(self) -> None:
        """ACTIVE → FAILED transition."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)
        ritual.begin()
        ritual.fail("Something went wrong")

        assert ritual.status == RitualStatus.FAILED
        assert ritual.metadata["failure_reason"] == "Something went wrong"

    def test_lifecycle_cancel(self) -> None:
        """Ritual can be cancelled."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)
        ritual.begin()
        ritual.cancel("User requested")

        assert ritual.status == RitualStatus.CANCELLED

    def test_lifecycle_pause_resume(self) -> None:
        """Ritual can be paused and resumed."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)
        ritual.begin()

        ritual.pause()
        assert ritual.status == RitualStatus.PAUSED

        ritual.resume()
        assert ritual.status == RitualStatus.ACTIVE


# =============================================================================
# Trace Recording Tests
# =============================================================================


class TestTraceRecording:
    """Tests for TraceNode recording."""

    def test_record_trace(self) -> None:
        """Traces can be recorded."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)
        ritual.begin()

        trace = TraceNode.from_thought("Test thought", "git")
        ritual.record_trace(trace)

        assert ritual.trace_count == 1
        assert trace.id in ritual.trace_node_ids

    def test_duplicate_trace_ignored(self) -> None:
        """Recording same trace twice is idempotent."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)
        ritual.begin()

        trace = TraceNode.from_thought("Test", "git")
        ritual.record_trace(trace)
        ritual.record_trace(trace)  # Duplicate

        assert ritual.trace_count == 1


# =============================================================================
# RitualStore Tests
# =============================================================================


class TestRitualStore:
    """Tests for RitualStore."""

    def setup_method(self) -> None:
        """Reset store before each test."""
        reset_ritual_store()

    def test_add_and_get(self) -> None:
        """Basic add and get operations."""
        store = get_ritual_store()
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)
        store.add(ritual)

        retrieved = store.get(ritual.id)
        assert retrieved is not None
        assert retrieved.id == ritual.id

    def test_active_filter(self) -> None:
        """active() returns only active Rituals."""
        store = RitualStore()
        covenant = make_covenant()
        offering = make_offering()

        active = Ritual.create(name="Active", covenant=covenant, offering=offering)
        active.begin()

        pending = Ritual.create(name="Pending", covenant=covenant, offering=offering)

        complete = Ritual.create(name="Complete", covenant=covenant, offering=offering)
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
        """RitualPhase serializes correctly."""
        original = RitualPhase(
            name="Act",
            n_phase=NPhase.ACT,
            allowed_actions=("file_write", "git_commit"),
            timeout_seconds=300.0,
        )

        data = original.to_dict()
        restored = RitualPhase.from_dict(data)

        assert restored.name == original.name
        assert restored.n_phase == original.n_phase
        assert restored.allowed_actions == original.allowed_actions

    def test_ritual_roundtrip(self) -> None:
        """Ritual serializes correctly (without Covenant/Offering)."""
        covenant = make_covenant()
        offering = make_offering()

        original = Ritual.create(
            name="Test Ritual",
            covenant=covenant,
            offering=offering,
            description="A test ritual",
        )
        original.begin()
        original.advance_phase(NPhase.ACT)

        data = original.to_dict()
        restored = Ritual.from_dict(data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.current_phase == NPhase.ACT
        assert restored.status == RitualStatus.ACTIVE
        assert len(restored.phase_history) == 2


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge cases for robustness."""

    def test_cannot_begin_twice(self) -> None:
        """Cannot begin an already active Ritual."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)
        ritual.begin()

        with pytest.raises(RitualError):
            ritual.begin()

    def test_cannot_complete_pending(self) -> None:
        """Cannot complete a pending Ritual."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)

        with pytest.raises(RitualNotActive):
            ritual.complete()

    def test_cannot_advance_phase_when_pending(self) -> None:
        """Cannot advance phase when not active."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)

        with pytest.raises(RitualNotActive):
            ritual.advance_phase(NPhase.ACT)

    def test_duration_calculation(self) -> None:
        """Duration is calculated correctly."""
        covenant = make_covenant()
        offering = make_offering()

        ritual = Ritual.create(name="Test", covenant=covenant, offering=offering)
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
