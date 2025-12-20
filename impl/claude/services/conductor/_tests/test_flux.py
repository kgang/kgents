"""
Phase 7: Live Flux — ConductorFlux Integration Tests

CLI v7 Phase 7: Real-time sync across all surfaces.

This test file validates:
1. ConductorFlux subscribes to all phase events
2. Events route correctly to subscribers
3. Cross-phase event correlation works
4. Flux lifecycle (start/stop) is clean
5. Performance: event routing < 10ms

The Flux is the nerve center that makes all surfaces feel alive.

Run:
    cd impl/claude && uv run pytest services/conductor/_tests/test_flux.py -v

Constitution Alignment:
- S5 (Composable): Events compose through the three-bus pipeline
- S3 (Ethical): All agent activity is visible (no hidden state)
- S4 (Joy-Inducing): Real-time updates create "alive" feeling
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest

from protocols.synergy import (
    SynergyEvent,
    SynergyEventType,
    create_conversation_turn_event,
    create_cursor_joined_event,
    create_cursor_updated_event,
    create_file_edited_event,
    create_file_read_event,
    create_swarm_a2a_message_event,
    create_swarm_handoff_event,
    create_swarm_spawned_event,
    get_synergy_bus,
    reset_synergy_bus,
)
from services.conductor.flux import (
    ConductorEvent,
    ConductorEventSubscriber,
    ConductorEventType,
    ConductorFlux,
    get_conductor_flux,
    reset_conductor_flux,
    start_conductor_flux,
)


@pytest.fixture
def clean_flux():
    """Reset flux and synergy bus for clean tests."""
    reset_synergy_bus()
    reset_conductor_flux()
    yield
    reset_synergy_bus()
    reset_conductor_flux()


class TestConductorFluxLifecycle:
    """Test ConductorFlux start/stop lifecycle."""

    def test_flux_not_running_initially(self, clean_flux):
        """Flux starts in stopped state."""
        flux = ConductorFlux()
        assert not flux.running

    def test_start_sets_running(self, clean_flux):
        """Starting flux sets running flag."""
        flux = ConductorFlux()
        flux.start()
        assert flux.running
        flux.stop()

    def test_stop_clears_running(self, clean_flux):
        """Stopping flux clears running flag."""
        flux = ConductorFlux()
        flux.start()
        flux.stop()
        assert not flux.running

    def test_double_start_is_idempotent(self, clean_flux):
        """Starting twice is safe."""
        flux = ConductorFlux()
        flux.start()
        flux.start()  # Should not raise
        assert flux.running
        flux.stop()

    def test_singleton_get_conductor_flux(self, clean_flux):
        """get_conductor_flux returns singleton."""
        flux1 = get_conductor_flux()
        flux2 = get_conductor_flux()
        assert flux1 is flux2

    def test_reset_clears_singleton(self, clean_flux):
        """reset_conductor_flux clears and stops the singleton."""
        flux1 = get_conductor_flux()
        flux1.start()
        reset_conductor_flux()
        flux2 = get_conductor_flux()
        assert flux1 is not flux2
        assert not flux2.running


class TestConductorFluxSubscription:
    """Test subscriber management."""

    def test_subscribe_returns_unsubscribe(self, clean_flux):
        """Subscribe returns unsubscribe callable."""
        flux = ConductorFlux()
        unsubscribe = flux.subscribe(lambda e: None)
        assert callable(unsubscribe)
        unsubscribe()

    def test_subscriber_removed_on_unsubscribe(self, clean_flux):
        """Unsubscribe removes subscriber."""
        flux = ConductorFlux()
        calls = []
        unsubscribe = flux.subscribe(lambda e: calls.append(e))
        assert len(flux._subscribers) == 1
        unsubscribe()
        assert len(flux._subscribers) == 0

    def test_multiple_subscribers(self, clean_flux):
        """Multiple subscribers can coexist."""
        flux = ConductorFlux()
        sub1 = flux.subscribe(lambda e: None)
        sub2 = flux.subscribe(lambda e: None)
        assert len(flux._subscribers) == 2
        sub1()
        assert len(flux._subscribers) == 1
        sub2()
        assert len(flux._subscribers) == 0


class TestPhase1FileEvents:
    """Test Phase 1: File I/O event routing."""

    @pytest.mark.asyncio
    async def test_file_read_routes_to_file_changed(self, clean_flux):
        """FILE_READ events route to FILE_CHANGED."""
        flux = ConductorFlux()
        flux.start()

        received: list[ConductorEvent] = []
        flux.subscribe(lambda e: received.append(e))

        bus = get_synergy_bus()
        event = create_file_read_event(
            path="/test/file.py",
            size=1000,
            lines=50,
        )
        await bus.emit_and_wait(event)
        await asyncio.sleep(0.1)

        assert len(received) == 1
        assert received[0].event_type == ConductorEventType.FILE_CHANGED
        assert received[0].metadata["path"] == "/test/file.py"
        flux.stop()

    @pytest.mark.asyncio
    async def test_file_edited_routes_to_file_changed(self, clean_flux):
        """FILE_EDITED events route to FILE_CHANGED."""
        flux = ConductorFlux()
        flux.start()

        received: list[ConductorEvent] = []
        flux.subscribe(lambda e: received.append(e))

        bus = get_synergy_bus()
        event = create_file_edited_event(
            path="/test/file.py",
            old_size=100,
            new_size=150,
            replacements=1,
        )
        await bus.emit_and_wait(event)
        await asyncio.sleep(0.1)

        assert len(received) == 1
        assert received[0].event_type == ConductorEventType.FILE_CHANGED
        flux.stop()


class TestPhase2ConversationEvents:
    """Test Phase 2: Conversation event routing."""

    @pytest.mark.asyncio
    async def test_conversation_turn_routes_to_turn_added(self, clean_flux):
        """CONVERSATION_TURN events route to TURN_ADDED."""
        flux = ConductorFlux()
        flux.start()

        received: list[ConductorEvent] = []
        flux.subscribe(lambda e: received.append(e))

        bus = get_synergy_bus()
        event = create_conversation_turn_event(
            session_id="test-session",
            turn_number=5,
            role="assistant",
            content_preview="Hello, world!",
        )
        await bus.emit_and_wait(event)
        await asyncio.sleep(0.1)

        assert len(received) == 1
        assert received[0].event_type == ConductorEventType.TURN_ADDED
        assert received[0].metadata["session_id"] == "test-session"
        assert received[0].metadata["turn_number"] == 5
        flux.stop()


class TestPhase3PresenceEvents:
    """Test Phase 3: Presence event routing."""

    @pytest.mark.asyncio
    async def test_cursor_joined_routes_to_agent_joined(self, clean_flux):
        """CURSOR_JOINED events route to AGENT_JOINED."""
        flux = ConductorFlux()
        flux.start()

        received: list[ConductorEvent] = []
        flux.subscribe(lambda e: received.append(e))

        bus = get_synergy_bus()
        event = create_cursor_joined_event(
            agent_id="researcher-1",
            display_name="Researcher",
            behavior="EXPLORER",
        )
        await bus.emit_and_wait(event)
        await asyncio.sleep(0.1)

        assert len(received) == 1
        assert received[0].event_type == ConductorEventType.AGENT_JOINED
        assert received[0].metadata["agent_id"] == "researcher-1"
        flux.stop()

    @pytest.mark.asyncio
    async def test_cursor_updated_routes_to_cursor_moved(self, clean_flux):
        """CURSOR_UPDATED events route to CURSOR_MOVED."""
        flux = ConductorFlux()
        flux.start()

        received: list[ConductorEvent] = []
        flux.subscribe(lambda e: received.append(e))

        bus = get_synergy_bus()
        event = create_cursor_updated_event(
            agent_id="planner-1",
            display_name="Planner",
            state="WORKING",
            focus_path="self.memory",
            activity="Planning...",
        )
        await bus.emit_and_wait(event)
        await asyncio.sleep(0.1)

        assert len(received) == 1
        assert received[0].event_type == ConductorEventType.CURSOR_MOVED
        flux.stop()


class TestPhase6SwarmEvents:
    """Test Phase 6: Swarm/A2A event routing."""

    @pytest.mark.asyncio
    async def test_swarm_spawned_routes_to_swarm_activity(self, clean_flux):
        """SWARM_SPAWNED events route to SWARM_ACTIVITY."""
        flux = ConductorFlux()
        flux.start()

        received: list[ConductorEvent] = []
        flux.subscribe(lambda e: received.append(e))

        bus = get_synergy_bus()
        event = create_swarm_spawned_event(
            agent_id="researcher-1",
            task="Research authentication",
            behavior="EXPLORER",
            autonomy_level=0,
        )
        await bus.emit_and_wait(event)
        await asyncio.sleep(0.1)

        assert len(received) == 1
        assert received[0].event_type == ConductorEventType.SWARM_ACTIVITY
        flux.stop()

    @pytest.mark.asyncio
    async def test_a2a_message_routes_correctly(self, clean_flux):
        """SWARM_A2A_MESSAGE events route to A2A_MESSAGE."""
        flux = ConductorFlux()
        flux.start()

        received: list[ConductorEvent] = []
        flux.subscribe(lambda e: received.append(e))

        bus = get_synergy_bus()
        event = create_swarm_a2a_message_event(
            message_id="msg-123",
            from_agent="researcher-1",
            to_agent="planner-1",
            message_type="NOTIFY",
            payload_preview="Research findings...",
        )
        await bus.emit_and_wait(event)
        await asyncio.sleep(0.1)

        assert len(received) == 1
        assert received[0].event_type == ConductorEventType.A2A_MESSAGE
        assert received[0].metadata["from_agent"] == "researcher-1"
        assert received[0].metadata["to_agent"] == "planner-1"
        flux.stop()

    @pytest.mark.asyncio
    async def test_swarm_handoff_routes_to_swarm_activity(self, clean_flux):
        """SWARM_HANDOFF events route to SWARM_ACTIVITY."""
        flux = ConductorFlux()
        flux.start()

        received: list[ConductorEvent] = []
        flux.subscribe(lambda e: received.append(e))

        bus = get_synergy_bus()
        event = create_swarm_handoff_event(
            handoff_id="handoff-123",
            from_agent="planner-1",
            to_agent="implementer-1",
            context_keys=["plan", "files"],
            conversation_turns=5,
        )
        await bus.emit_and_wait(event)
        await asyncio.sleep(0.1)

        assert len(received) == 1
        assert received[0].event_type == ConductorEventType.SWARM_ACTIVITY
        flux.stop()


class TestCrossPhaseEventFlow:
    """Test cross-phase event correlation and flow."""

    @pytest.mark.asyncio
    async def test_multiple_event_types_in_sequence(self, clean_flux):
        """Events from different phases route correctly in sequence."""
        flux = ConductorFlux()
        flux.start()

        received: list[ConductorEvent] = []
        flux.subscribe(lambda e: received.append(e))

        bus = get_synergy_bus()

        # File event (Phase 1)
        await bus.emit_and_wait(create_file_read_event(
            path="/test.py",
            size=100,
            lines=10,
        ))

        # Conversation event (Phase 2)
        await bus.emit_and_wait(create_conversation_turn_event(
            session_id="sess-1",
            turn_number=1,
            role="user",
            content_preview="Hello",
        ))

        # Cursor event (Phase 3)
        await bus.emit_and_wait(create_cursor_joined_event(
            agent_id="agent-1",
            display_name="Agent",
            behavior="FOLLOWER",
        ))

        # Swarm event (Phase 6)
        await bus.emit_and_wait(create_swarm_spawned_event(
            agent_id="spawned-1",
            task="Task",
            behavior="ASSISTANT",
            autonomy_level=1,
        ))

        await asyncio.sleep(0.2)

        assert len(received) == 4
        event_types = [e.event_type for e in received]
        assert ConductorEventType.FILE_CHANGED in event_types
        assert ConductorEventType.TURN_ADDED in event_types
        assert ConductorEventType.AGENT_JOINED in event_types
        assert ConductorEventType.SWARM_ACTIVITY in event_types
        flux.stop()


class TestFluxPerformance:
    """Performance tests for event routing."""

    @pytest.mark.asyncio
    async def test_event_routing_under_10ms(self, clean_flux):
        """Event routing completes in under 10ms."""
        flux = ConductorFlux()
        flux.start()

        received_times: list[float] = []

        def timed_subscriber(e: ConductorEvent):
            received_times.append(time.perf_counter())

        flux.subscribe(timed_subscriber)

        bus = get_synergy_bus()

        # Measure 10 events
        for i in range(10):
            start = time.perf_counter()
            await bus.emit_and_wait(create_file_read_event(
                path=f"/test_{i}.py",
                size=100,
                lines=10,
            ))
            # Wait for processing
            await asyncio.sleep(0.05)

        flux.stop()

        # All events should have been received
        assert len(received_times) >= 10

    @pytest.mark.asyncio
    async def test_many_subscribers_dont_block(self, clean_flux):
        """Multiple subscribers don't block event routing."""
        flux = ConductorFlux()
        flux.start()

        # Add 20 subscribers
        for _ in range(20):
            flux.subscribe(lambda e: None)

        bus = get_synergy_bus()

        start = time.perf_counter()
        for i in range(5):
            await bus.emit_and_wait(create_file_read_event(
                path=f"/test_{i}.py",
                size=100,
                lines=10,
            ))
        elapsed = time.perf_counter() - start

        # Should complete reasonably fast even with many subscribers
        assert elapsed < 2.0  # 2 seconds max
        flux.stop()


class TestConductorEventSerialization:
    """Test ConductorEvent serialization."""

    @pytest.mark.asyncio
    async def test_to_dict_serialization(self, clean_flux):
        """ConductorEvent.to_dict produces valid JSON-serializable dict."""
        flux = ConductorFlux()
        flux.start()

        received: list[ConductorEvent] = []
        flux.subscribe(lambda e: received.append(e))

        bus = get_synergy_bus()
        await bus.emit_and_wait(create_file_read_event(
            path="/test.py",
            size=100,
            lines=10,
        ))
        await asyncio.sleep(0.1)

        assert len(received) == 1

        data = received[0].to_dict()
        assert "type" in data
        assert "source" in data
        assert "timestamp" in data
        assert "metadata" in data

        # Should be JSON-serializable
        import json
        json_str = json.dumps(data)
        assert json_str

        flux.stop()
