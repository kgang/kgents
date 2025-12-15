"""
Tests for WorkshopFlux N-Phase Integration (Wave 4, Task 4.1).

Verifies:
- WorkshopFlux accepts optional nphase_session parameter
- Workshop phases map correctly to N-Phase (3-phase cycle)
- Phase transitions sync to N-Phase session
- N-Phase state appears in event metadata
- get_status() includes N-Phase info

See: plans/nphase-native-integration-wave4-prompt.md
"""

from __future__ import annotations

import pytest
from agents.town.workshop import (
    WorkshopEnvironment,
    WorkshopEventType,
    WorkshopFlux,
    WorkshopPhase,
    _get_nphase_for_workshop_phase,
    create_workshop,
)
from protocols.nphase.operad import NPhase
from protocols.nphase.session import NPhaseSession, create_session, reset_session_store

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def workshop() -> WorkshopEnvironment:
    """Create a workshop for testing."""
    return create_workshop()


@pytest.fixture
def nphase_session() -> NPhaseSession:
    """Create an N-Phase session for testing."""
    reset_session_store()
    return create_session("Test Task")


# =============================================================================
# Workshop Phase → N-Phase Mapping Tests
# =============================================================================


class TestPhaseMapping:
    """Test WorkshopPhase → NPhase mapping."""

    def test_exploring_maps_to_understand(self) -> None:
        """EXPLORING maps to UNDERSTAND (gathering context)."""
        result = _get_nphase_for_workshop_phase(WorkshopPhase.EXPLORING)
        assert result == NPhase.UNDERSTAND

    def test_designing_maps_to_understand(self) -> None:
        """DESIGNING maps to UNDERSTAND (still planning)."""
        result = _get_nphase_for_workshop_phase(WorkshopPhase.DESIGNING)
        assert result == NPhase.UNDERSTAND

    def test_prototyping_maps_to_act(self) -> None:
        """PROTOTYPING maps to ACT (doing work)."""
        result = _get_nphase_for_workshop_phase(WorkshopPhase.PROTOTYPING)
        assert result == NPhase.ACT

    def test_refining_maps_to_act(self) -> None:
        """REFINING maps to ACT (still doing work)."""
        result = _get_nphase_for_workshop_phase(WorkshopPhase.REFINING)
        assert result == NPhase.ACT

    def test_integrating_maps_to_reflect(self) -> None:
        """INTEGRATING maps to REFLECT (synthesizing)."""
        result = _get_nphase_for_workshop_phase(WorkshopPhase.INTEGRATING)
        assert result == NPhase.REFLECT

    def test_idle_maps_to_none(self) -> None:
        """IDLE has no N-Phase mapping."""
        result = _get_nphase_for_workshop_phase(WorkshopPhase.IDLE)
        assert result is None

    def test_complete_maps_to_none(self) -> None:
        """COMPLETE has no N-Phase mapping."""
        result = _get_nphase_for_workshop_phase(WorkshopPhase.COMPLETE)
        assert result is None


# =============================================================================
# WorkshopFlux N-Phase Integration Tests
# =============================================================================


class TestWorkshopFluxNPhaseIntegration:
    """Test WorkshopFlux with N-Phase session."""

    def test_flux_accepts_nphase_session(
        self, workshop: WorkshopEnvironment, nphase_session: NPhaseSession
    ) -> None:
        """WorkshopFlux accepts optional nphase_session parameter."""
        flux = WorkshopFlux(workshop, nphase_session=nphase_session)
        assert flux.nphase_session is nphase_session

    def test_flux_without_nphase_session(self, workshop: WorkshopEnvironment) -> None:
        """WorkshopFlux works without N-Phase session."""
        flux = WorkshopFlux(workshop)
        assert flux.nphase_session is None
        assert flux.current_nphase is None

    def test_current_nphase_property(
        self, workshop: WorkshopEnvironment, nphase_session: NPhaseSession
    ) -> None:
        """current_nphase returns session's current phase."""
        flux = WorkshopFlux(workshop, nphase_session=nphase_session)
        assert flux.current_nphase == NPhase.UNDERSTAND  # Initial phase

    @pytest.mark.asyncio
    async def test_start_syncs_nphase(
        self, workshop: WorkshopEnvironment, nphase_session: NPhaseSession
    ) -> None:
        """Starting a task syncs N-Phase with workshop phase."""
        flux = WorkshopFlux(workshop, nphase_session=nphase_session)

        # Start a task (will be routed to Scout → EXPLORING)
        await flux.start("Explore the codebase")

        # Workshop should be in EXPLORING, N-Phase should be UNDERSTAND
        assert flux.current_phase == WorkshopPhase.EXPLORING
        assert nphase_session.current_phase == NPhase.UNDERSTAND

    @pytest.mark.asyncio
    async def test_get_status_includes_nphase(
        self, workshop: WorkshopEnvironment, nphase_session: NPhaseSession
    ) -> None:
        """get_status() includes N-Phase information when session is set."""
        flux = WorkshopFlux(workshop, nphase_session=nphase_session)
        await flux.start("Design a feature")

        status = flux.get_status()

        assert "nphase" in status
        assert status["nphase"]["session_id"] == nphase_session.id
        assert status["nphase"]["current_phase"] == "UNDERSTAND"
        assert status["nphase"]["cycle_count"] == 0

    @pytest.mark.asyncio
    async def test_get_status_no_nphase_without_session(
        self, workshop: WorkshopEnvironment
    ) -> None:
        """get_status() doesn't include N-Phase when no session."""
        flux = WorkshopFlux(workshop)
        await flux.start("Quick task")

        status = flux.get_status()

        assert "nphase" not in status

    @pytest.mark.asyncio
    async def test_event_metadata_includes_nphase(
        self, workshop: WorkshopEnvironment, nphase_session: NPhaseSession
    ) -> None:
        """Workshop events include N-Phase info in metadata."""
        flux = WorkshopFlux(workshop, nphase_session=nphase_session, auto_advance=False)
        await flux.start("Test task")

        # Get an event from step
        events = []
        async for event in flux.step():
            events.append(event)

        # Check that events have nphase metadata
        assert len(events) > 0
        for event in events:
            assert "nphase" in event.metadata
            assert event.metadata["nphase"]["session_id"] == nphase_session.id


# =============================================================================
# N-Phase Transition Tests
# =============================================================================


class TestNPhaseTransitions:
    """Test that workshop phase transitions advance N-Phase correctly."""

    @pytest.mark.asyncio
    async def test_phase_transition_syncs_nphase(
        self, workshop: WorkshopEnvironment, nphase_session: NPhaseSession
    ) -> None:
        """Workshop phase transitions sync to N-Phase when using perturb."""
        flux = WorkshopFlux(
            workshop,
            nphase_session=nphase_session,
            auto_advance=False,  # Manual control for deterministic test
        )

        # "Explore" routes to Scout → EXPLORING (UNDERSTAND)
        await flux.start("Explore the codebase")
        assert flux.current_phase == WorkshopPhase.EXPLORING
        assert nphase_session.current_phase == NPhase.UNDERSTAND

        # EXPLORING → DESIGNING (both UNDERSTAND)
        await flux.perturb("advance")
        # Note: mypy doesn't track that perturb() changes current_phase
        assert flux.current_phase == WorkshopPhase.DESIGNING  # type: ignore[comparison-overlap]
        assert nphase_session.current_phase == NPhase.UNDERSTAND

        # DESIGNING → PROTOTYPING (UNDERSTAND → ACT)
        await flux.perturb("advance")
        # Note: mypy doesn't track that perturb() changes current_phase
        assert flux.current_phase == WorkshopPhase.PROTOTYPING  # type: ignore[comparison-overlap]
        assert nphase_session.current_phase == NPhase.ACT  # type: ignore[comparison-overlap]

        # Verify ledger recorded the transition
        assert len(nphase_session.ledger) > 0

    @pytest.mark.asyncio
    async def test_nphase_advances_on_workshop_phase_change(
        self, workshop: WorkshopEnvironment, nphase_session: NPhaseSession
    ) -> None:
        """N-Phase advances when workshop moves to different mapped phase."""
        flux = WorkshopFlux(workshop, nphase_session=nphase_session, auto_advance=False)

        # Start in EXPLORING (UNDERSTAND)
        await flux.start("Explore and prototype")
        assert nphase_session.current_phase == NPhase.UNDERSTAND

        # Force handoff to Spark (PROTOTYPING → ACT)
        await flux.perturb("handoff", builder="Spark")
        # After handoff to Spark, workshop should be in PROTOTYPING
        # N-Phase should sync to ACT
        # Note: mypy doesn't track that perturb() changes current_phase
        assert flux.current_phase == WorkshopPhase.PROTOTYPING  # type: ignore[comparison-overlap]
        assert nphase_session.current_phase == NPhase.ACT  # type: ignore[comparison-overlap]

    @pytest.mark.asyncio
    async def test_nphase_stays_same_within_mapped_range(
        self, workshop: WorkshopEnvironment, nphase_session: NPhaseSession
    ) -> None:
        """N-Phase doesn't advance when staying within same mapped range."""
        flux = WorkshopFlux(workshop, nphase_session=nphase_session, auto_advance=False)

        # Start in EXPLORING (UNDERSTAND)
        await flux.start("Design something")
        assert nphase_session.current_phase == NPhase.UNDERSTAND
        ledger_len = len(nphase_session.ledger)

        # Handoff to Sage (DESIGNING → still UNDERSTAND)
        await flux.perturb("handoff", builder="Sage")
        assert flux.current_phase == WorkshopPhase.DESIGNING
        # N-Phase should still be UNDERSTAND (no new ledger entry)
        assert nphase_session.current_phase == NPhase.UNDERSTAND
        assert len(nphase_session.ledger) == ledger_len


# =============================================================================
# N-Phase Ledger Tests
# =============================================================================


class TestNPhaseLedger:
    """Test that workshop activities create N-Phase ledger entries."""

    @pytest.mark.asyncio
    async def test_phase_transition_creates_ledger_entry(
        self, workshop: WorkshopEnvironment, nphase_session: NPhaseSession
    ) -> None:
        """Workshop phase transition creates N-Phase ledger entry."""
        flux = WorkshopFlux(workshop, nphase_session=nphase_session, auto_advance=False)

        # Start (creates initial sync if different)
        await flux.start("Start task")
        initial_ledger = len(nphase_session.ledger)

        # Force transition to different N-Phase (UNDERSTAND → ACT)
        await flux.perturb("handoff", builder="Spark")

        # Should have new ledger entry
        assert len(nphase_session.ledger) > initial_ledger
        latest = nphase_session.ledger[-1]
        assert latest.to_phase == NPhase.ACT
        assert "workshop_phase" in latest.payload


# =============================================================================
# Reset Behavior Tests
# =============================================================================


class TestResetBehavior:
    """Test reset behavior with N-Phase session."""

    def test_reset_preserves_nphase_session(
        self, workshop: WorkshopEnvironment, nphase_session: NPhaseSession
    ) -> None:
        """Flux reset preserves N-Phase session (by design)."""
        flux = WorkshopFlux(workshop, nphase_session=nphase_session)

        flux.reset()

        # Session should still be attached
        assert flux.nphase_session is nphase_session

    @pytest.mark.asyncio
    async def test_reset_clears_last_nphase_tracking(
        self, workshop: WorkshopEnvironment, nphase_session: NPhaseSession
    ) -> None:
        """Flux reset clears internal tracking state."""
        flux = WorkshopFlux(workshop, nphase_session=nphase_session)

        await flux.start("Initial task")
        flux.reset()

        # _last_nphase should be cleared (internal state)
        assert flux._last_nphase is None


# =============================================================================
# Integration Test
# =============================================================================


@pytest.mark.asyncio
async def test_full_workflow_with_nphase() -> None:
    """
    Integration test: Run a full workshop workflow with N-Phase tracking.

    Verifies that N-Phase transitions follow the workshop lifecycle.
    """
    reset_session_store()
    workshop = create_workshop()
    session = create_session("Full Integration Test")

    flux = WorkshopFlux(
        workshop,
        nphase_session=session,
        auto_advance=True,
        max_steps_per_phase=2,
    )

    # Start task
    await flux.start("Research, prototype, and integrate")

    # Track N-Phase transitions
    nphase_transitions = []
    last_nphase = session.current_phase

    event_count = 0
    max_events = 30

    async for event in flux.run():
        current = session.current_phase
        if current != last_nphase:
            nphase_transitions.append((last_nphase.name, current.name))
            last_nphase = current
        event_count += 1
        if event_count >= max_events:
            break

    # Should have made progress through N-Phase cycle
    status = flux.get_status()
    assert "nphase" in status

    # Verify session has ledger entries
    assert len(session.ledger) > 0
