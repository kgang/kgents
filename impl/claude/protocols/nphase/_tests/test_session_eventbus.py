"""
Tests for NPhaseSession Event Bus Integration (Wave 4, Task 4.4).

Verifies:
- NPhaseSession accepts event_bus parameter
- Events are emitted on phase transitions
- Events are emitted on checkpoints
- No events when bus not set

See: plans/nphase-native-integration-wave4-prompt.md
"""

from __future__ import annotations

import asyncio

import pytest
from agents.town.event_bus import EventBus
from protocols.nphase.events import (
    NPhaseEvent,
    NPhaseEventType,
    PhaseCheckpointEvent,
    PhaseTransitionEvent,
)
from protocols.nphase.operad import NPhase
from protocols.nphase.session import NPhaseSession, create_session, reset_session_store

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def event_bus() -> EventBus[NPhaseEvent]:
    """Create an event bus for testing."""
    return EventBus[NPhaseEvent]()


@pytest.fixture
def nphase_session() -> NPhaseSession:
    """Create an N-Phase session for testing."""
    reset_session_store()
    return create_session("Test Session")


# =============================================================================
# Helper to collect events
# =============================================================================


async def collect_events(
    bus: EventBus[NPhaseEvent], timeout: float = 0.1
) -> list[NPhaseEvent]:
    """Collect events from bus for a short period."""
    events: list[NPhaseEvent] = []

    async def collector() -> None:
        async for event in bus.subscribe():
            if event is None:
                break
            events.append(event)

    # Run collector with timeout
    task = asyncio.create_task(collector())
    await asyncio.sleep(timeout)
    bus.close()
    try:
        await asyncio.wait_for(task, timeout=0.1)
    except asyncio.TimeoutError:
        task.cancel()
    return events


# =============================================================================
# Event Bus Integration Tests
# =============================================================================


class TestEventBusBasics:
    """Test basic event bus integration."""

    def test_session_has_event_bus_property(
        self, nphase_session: NPhaseSession
    ) -> None:
        """Session has event_bus property."""
        assert nphase_session.event_bus is None

    def test_set_event_bus(
        self, nphase_session: NPhaseSession, event_bus: EventBus[NPhaseEvent]
    ) -> None:
        """set_event_bus() configures the bus."""
        nphase_session.set_event_bus(event_bus)
        assert nphase_session.event_bus is event_bus

    def test_no_events_without_bus(self, nphase_session: NPhaseSession) -> None:
        """No crash when advancing without event bus."""
        # This should not raise
        nphase_session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        assert nphase_session.current_phase == NPhase.ACT


# =============================================================================
# Phase Transition Event Tests
# =============================================================================


class TestPhaseTransitionEvents:
    """Test that phase transitions emit events."""

    @pytest.mark.asyncio
    async def test_advance_emits_event(
        self, nphase_session: NPhaseSession, event_bus: EventBus[NPhaseEvent]
    ) -> None:
        """advance_phase() emits PhaseTransitionEvent."""
        nphase_session.set_event_bus(event_bus)

        # Advance in the background
        nphase_session.advance_phase(NPhase.ACT, auto_checkpoint=False)

        # Allow event to be published
        events = await collect_events(event_bus)

        # Should have one transition event
        transition_events = [
            e for e in events if e.event_type == NPhaseEventType.PHASE_TRANSITION
        ]
        assert len(transition_events) == 1

        event = transition_events[0]
        assert isinstance(event, PhaseTransitionEvent)
        assert event.from_phase == NPhase.UNDERSTAND
        assert event.to_phase == NPhase.ACT
        assert event.session_id == nphase_session.id

    @pytest.mark.asyncio
    async def test_advance_with_payload_included_in_event(
        self, nphase_session: NPhaseSession, event_bus: EventBus[NPhaseEvent]
    ) -> None:
        """Payload is included in transition event."""
        nphase_session.set_event_bus(event_bus)

        nphase_session.advance_phase(
            NPhase.ACT,
            payload={"reason": "testing"},
            auto_checkpoint=False,
        )

        events = await collect_events(event_bus)
        transition_events = [
            e for e in events if e.event_type == NPhaseEventType.PHASE_TRANSITION
        ]

        assert len(transition_events) == 1
        event = transition_events[0]
        assert isinstance(event, PhaseTransitionEvent)
        assert event.payload == {"reason": "testing"}


# =============================================================================
# Checkpoint Event Tests
# =============================================================================


class TestCheckpointEvents:
    """Test that checkpoints emit events."""

    @pytest.mark.asyncio
    async def test_checkpoint_emits_event(
        self, nphase_session: NPhaseSession, event_bus: EventBus[NPhaseEvent]
    ) -> None:
        """checkpoint() emits PhaseCheckpointEvent."""
        nphase_session.set_event_bus(event_bus)

        cp = nphase_session.checkpoint({"reason": "manual"})

        events = await collect_events(event_bus)
        checkpoint_events = [
            e for e in events if e.event_type == NPhaseEventType.PHASE_CHECKPOINT
        ]
        assert len(checkpoint_events) == 1

        event = checkpoint_events[0]
        assert isinstance(event, PhaseCheckpointEvent)
        assert event.checkpoint_id == cp.id
        assert event.phase == NPhase.UNDERSTAND
        assert event.session_id == nphase_session.id

    @pytest.mark.asyncio
    async def test_auto_checkpoint_emits_event(
        self, nphase_session: NPhaseSession, event_bus: EventBus[NPhaseEvent]
    ) -> None:
        """Auto-checkpoint during advance emits event."""
        nphase_session.set_event_bus(event_bus)

        # Advance with auto_checkpoint=True (default)
        nphase_session.advance_phase(NPhase.ACT)

        events = await collect_events(event_bus)

        # Should have checkpoint event (auto) + transition event
        checkpoint_events = [
            e for e in events if e.event_type == NPhaseEventType.PHASE_CHECKPOINT
        ]
        transition_events = [
            e for e in events if e.event_type == NPhaseEventType.PHASE_TRANSITION
        ]

        assert len(checkpoint_events) == 1
        assert len(transition_events) == 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestEventBusIntegration:
    """Integration tests for event bus with N-Phase session."""

    @pytest.mark.asyncio
    async def test_full_workflow_emits_events(
        self, nphase_session: NPhaseSession, event_bus: EventBus[NPhaseEvent]
    ) -> None:
        """Full workflow emits appropriate events."""
        nphase_session.set_event_bus(event_bus)

        # Run a sequence of operations
        nphase_session.advance_phase(NPhase.ACT)  # checkpoint + transition
        nphase_session.checkpoint()  # manual checkpoint
        nphase_session.advance_phase(NPhase.REFLECT)  # checkpoint + transition

        events = await collect_events(event_bus)

        # Count event types
        by_type: dict[NPhaseEventType, int] = {}
        for e in events:
            by_type[e.event_type] = by_type.get(e.event_type, 0) + 1

        assert by_type.get(NPhaseEventType.PHASE_TRANSITION, 0) == 2
        assert by_type.get(NPhaseEventType.PHASE_CHECKPOINT, 0) >= 2  # Auto + manual
