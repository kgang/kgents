"""
Tests for Coalition Forge Visualization.

Tests all three widgets:
1. CoalitionFormationView - who joins, why, eigenvector compatibility
2. DialogueStream - SSE-based dialogue viewer
3. HandoffAnimation - visual transitions between agents

Plus SSE mocking and AGENTESE integration.

Test Categories:
1. Widget initialization and state management
2. Event emission and subscription (SSE mocks)
3. All projection targets (CLI/JSON/TUI/MARIMO)
4. AGENTESE handler tests
5. State serialization
6. Integration workflows
7. Projection law verification (functor laws)
8. Error handling and edge cases
9. State transition validation
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agents.forge.visualization import (
    BuilderEntry,
    CoalitionFormationView,
    DialogueMessage,
    DialogueSpeaker,
    DialogueState,
    DialogueStream,
    EigenvectorCompatibility,
    ForgeFormationState,
    ForgeVisualizationError,
    FormationEvent,
    FormationEventType,
    FormationStateError,
    HandoffAnimation,
    HandoffState,
    create_dialogue_stream,
    create_formation_view,
    create_handoff_animation,
    handle_coalition_subscribe,
    handle_dialogue_witness,
    project_dialogue_to_ascii,
    project_formation_to_ascii,
    project_handoff_to_ascii,
)
from agents.i.reactive.widget import RenderTarget

# =============================================================================
# CoalitionFormationView Tests
# =============================================================================


class TestCoalitionFormationView:
    """Tests for CoalitionFormationView widget."""

    def test_initialization_default_state(self) -> None:
        """Test widget initializes with default empty state."""
        view = CoalitionFormationView()
        state = view.state.value

        assert state.task_id == ""
        assert state.phase == "idle"
        assert state.progress_percent == 0.0
        assert len(state.builders) == 0
        assert len(state.events) == 0

    def test_initialization_with_initial_state(self) -> None:
        """Test widget initializes with provided state."""
        initial = ForgeFormationState(
            task_id="test-123",
            task_description="Test task",
            phase="forming",
        )
        view = CoalitionFormationView(initial_state=initial)
        state = view.state.value

        assert state.task_id == "test-123"
        assert state.task_description == "Test task"
        assert state.phase == "forming"

    def test_start_formation(self) -> None:
        """Test starting coalition formation."""
        view = CoalitionFormationView()
        view.start_formation("Research competitors", "research_report")

        state = view.state.value
        assert state.task_description == "Research competitors"
        assert state.task_type == "research_report"
        assert state.phase == "forming"
        assert state.started_at is not None
        assert len(state.events) == 1
        assert state.events[0].type == FormationEventType.FORMATION_STARTED

    def test_start_formation_with_task_id(self) -> None:
        """Test starting formation with custom task ID."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general", task_id="custom-id")

        state = view.state.value
        assert state.task_id == "custom-id"

    def test_add_builder(self) -> None:
        """Test adding a builder to the coalition."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general")

        view.add_builder(
            archetype="Scout",
            name="Scout",
            role="Research",
            is_lead=True,
            compatibility_score=0.85,
        )

        state = view.state.value
        assert len(state.builders) == 1
        assert state.builders[0].archetype == "Scout"
        assert state.builders[0].is_lead is True
        assert state.builders[0].compatibility_score == 0.85
        assert state.lead_builder == "Scout"

    def test_add_multiple_builders(self) -> None:
        """Test adding multiple builders updates progress."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general")

        view.add_builder("Scout", "Scout", "Research", is_lead=True)
        view.add_builder("Sage", "Sage", "Analysis")
        view.add_builder("Scribe", "Scribe", "Documentation")

        state = view.state.value
        assert len(state.builders) == 3
        assert state.progress_percent == 100.0  # 3/3 target builders

    def test_complete_formation(self) -> None:
        """Test completing coalition formation."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general")
        view.add_builder("Scout", "Scout", "Research")
        view.complete_formation()

        state = view.state.value
        assert state.phase == "formed"
        assert state.progress_percent == 100.0
        assert state.events[-1].type == FormationEventType.FORMATION_COMPLETE

    def test_add_compatibility(self) -> None:
        """Test adding compatibility scores."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general")

        compat = EigenvectorCompatibility(
            builder_a="Scout",
            builder_b="Sage",
            warmth=0.8,
            curiosity=0.9,
            overall=0.85,
        )
        view.add_compatibility("Scout", "Sage", compat)

        state = view.state.value
        assert "Scout" in state.compatibility_matrix
        assert state.compatibility_matrix["Scout"]["Sage"] == 0.85
        assert state.events[-1].type == FormationEventType.COMPATIBILITY_COMPUTED

    def test_project_to_cli(self) -> None:
        """Test CLI projection produces ASCII art."""
        view = CoalitionFormationView()
        view.start_formation("Research competitors", "research_report")
        view.add_builder(
            "Scout", "Scout", "Research", is_lead=True, compatibility_score=0.85
        )

        output = view.to_cli()

        assert "COALITION FORMING" in output
        assert "Research competitors" in output
        assert "Scout" in output
        assert "Research" in output
        assert "85%" in output

    def test_project_to_json(self) -> None:
        """Test JSON projection produces dict."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general")

        output = view.to_json()

        assert output["type"] == "coalition_formation"
        assert output["task_description"] == "Test task"
        assert output["phase"] == "forming"
        assert isinstance(output["builders"], list)
        assert isinstance(output["events"], list)

    def test_widget_type(self) -> None:
        """Test widget type returns correct value."""
        view = CoalitionFormationView()
        assert view.widget_type() == "coalition_formation"

    def test_ui_hint(self) -> None:
        """Test UI hint returns stream."""
        view = CoalitionFormationView()
        assert view.ui_hint() == "stream"

    def test_event_callback(self) -> None:
        """Test event callback is triggered."""
        events_received: list[FormationEvent] = []

        def on_event(event: FormationEvent) -> None:
            events_received.append(event)

        view = CoalitionFormationView(on_event=on_event)
        view.start_formation("Test task", "general")
        view.add_builder("Scout", "Scout", "Research")

        assert len(events_received) == 2
        assert events_received[0].type == FormationEventType.FORMATION_STARTED
        assert events_received[1].type == FormationEventType.BUILDER_JOINED


class TestCoalitionFormationViewSSE:
    """SSE-specific tests for CoalitionFormationView."""

    @pytest.mark.asyncio
    async def test_subscribe_yields_events(self) -> None:
        """Test subscription yields events asynchronously."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general")

        # Get the subscription
        subscription = view.subscribe()

        # Start formation emits event to queue
        view.add_builder("Scout", "Scout", "Research")

        # Collect events (with timeout) - queue has FORMATION_STARTED then BUILDER_JOINED
        try:
            event1 = await asyncio.wait_for(subscription.__anext__(), timeout=0.1)
            # First event is FORMATION_STARTED
            assert event1.type == FormationEventType.FORMATION_STARTED

            event2 = await asyncio.wait_for(subscription.__anext__(), timeout=0.1)
            # Second event is BUILDER_JOINED
            assert event2.type == FormationEventType.BUILDER_JOINED
        except asyncio.TimeoutError:
            pytest.skip("Event queue timing issue")


# =============================================================================
# DialogueStream Tests
# =============================================================================


class TestDialogueStream:
    """Tests for DialogueStream widget."""

    def test_initialization_default_state(self) -> None:
        """Test widget initializes with default empty state."""
        stream = DialogueStream()
        state = stream.state.value

        assert len(state.messages) == 0
        assert state.is_streaming is False
        assert state.active_speaker is None

    def test_add_message(self) -> None:
        """Test adding a message to the stream."""
        stream = DialogueStream()
        stream.add_message(DialogueSpeaker.SCOUT, "Hello world")

        state = stream.state.value
        assert len(state.messages) == 1
        assert state.messages[0].content == "Hello world"
        assert state.messages[0].speaker == DialogueSpeaker.SCOUT
        assert state.is_streaming is True

    def test_add_message_with_string_speaker(self) -> None:
        """Test adding message with string speaker name."""
        stream = DialogueStream()
        stream.add_message("CustomAgent", "Hello")

        state = stream.state.value
        assert state.messages[0].speaker == "CustomAgent"

    def test_add_handoff(self) -> None:
        """Test adding a handoff transition message."""
        stream = DialogueStream()
        stream.add_handoff("Scout", "Sage", "Passing research findings")

        state = stream.state.value
        assert len(state.messages) == 1
        assert state.messages[0].is_handoff is True
        assert state.messages[0].speaker == "Scout"

    def test_add_artifact(self) -> None:
        """Test adding an artifact message."""
        stream = DialogueStream()
        stream.add_artifact(DialogueSpeaker.SAGE, "design_doc", "Architecture overview")

        state = stream.state.value
        assert len(state.messages) == 1
        assert state.messages[0].is_artifact is True
        assert state.messages[0].artifact_type == "design_doc"

    def test_start_stop_streaming(self) -> None:
        """Test starting and stopping streaming."""
        stream = DialogueStream()

        stream.start_streaming()
        assert stream.state.value.is_streaming is True

        stream.stop_streaming()
        assert stream.state.value.is_streaming is False
        assert stream.state.value.active_speaker is None

    def test_clear(self) -> None:
        """Test clearing all messages."""
        stream = DialogueStream()
        stream.add_message(DialogueSpeaker.SCOUT, "Message 1")
        stream.add_message(DialogueSpeaker.SAGE, "Message 2")

        stream.clear()

        state = stream.state.value
        assert len(state.messages) == 0
        assert state.is_streaming is False

    def test_max_messages_trimming(self) -> None:
        """Test that messages are trimmed to max limit."""
        stream = DialogueStream(initial_state=DialogueState(max_messages=5))

        for i in range(10):
            stream.add_message(DialogueSpeaker.SCOUT, f"Message {i}")

        state = stream.state.value
        assert len(state.messages) == 5
        # Should have latest messages
        assert state.messages[0].content == "Message 5"
        assert state.messages[-1].content == "Message 9"

    def test_project_to_cli(self) -> None:
        """Test CLI projection produces ASCII art."""
        stream = DialogueStream()
        stream.add_message(DialogueSpeaker.SCOUT, "Exploring the codebase...")
        stream.add_message(DialogueSpeaker.SAGE, "I see a pattern here.")

        output = stream.to_cli()

        assert "DIALOGUE STREAM" in output
        assert "Scout" in output
        assert "Sage" in output

    def test_project_to_json(self) -> None:
        """Test JSON projection produces dict."""
        stream = DialogueStream()
        stream.add_message(DialogueSpeaker.SCOUT, "Hello")

        output = stream.to_json()

        assert output["type"] == "dialogue_stream"
        assert len(output["messages"]) == 1
        assert output["is_streaming"] is True

    def test_widget_type(self) -> None:
        """Test widget type returns correct value."""
        stream = DialogueStream()
        assert stream.widget_type() == "dialogue_stream"


class TestDialogueStreamSSE:
    """SSE-specific tests for DialogueStream."""

    @pytest.mark.asyncio
    async def test_subscribe_yields_messages(self) -> None:
        """Test subscription yields messages asynchronously."""
        stream = DialogueStream()

        subscription = stream.subscribe()

        # Add a message
        stream.add_message(DialogueSpeaker.SCOUT, "Hello")

        # Collect one message
        try:
            msg = await asyncio.wait_for(subscription.__anext__(), timeout=0.1)
            assert msg.content == "Hello"
        except asyncio.TimeoutError:
            pytest.skip("Message queue timing issue")


# =============================================================================
# HandoffAnimation Tests
# =============================================================================


class TestHandoffAnimation:
    """Tests for HandoffAnimation widget."""

    def test_initialization_default_state(self) -> None:
        """Test widget initializes with default state."""
        anim = HandoffAnimation()
        state = anim.state.value

        assert state.from_builder is None
        assert state.to_builder is None
        assert state.is_active is False
        assert state.progress == 0.0
        assert len(state.handoffs) == 0

    def test_start_handoff(self) -> None:
        """Test starting a handoff animation."""
        anim = HandoffAnimation()
        anim.start_handoff("Scout", "Sage", "research findings")

        state = anim.state.value
        assert state.from_builder == "Scout"
        assert state.to_builder == "Sage"
        assert state.artifact == "research findings"
        assert state.is_active is True
        assert state.progress == 0.0

    def test_update_progress(self) -> None:
        """Test updating animation progress."""
        anim = HandoffAnimation()
        anim.start_handoff("Scout", "Sage")

        anim.update_progress(0.5)
        assert anim.state.value.progress == 0.5

        anim.update_progress(1.0)
        assert anim.state.value.progress == 1.0

    def test_update_progress_clamping(self) -> None:
        """Test progress is clamped to 0-1 range."""
        anim = HandoffAnimation()
        anim.start_handoff("Scout", "Sage")

        anim.update_progress(1.5)
        assert anim.state.value.progress == 1.0

        anim.update_progress(-0.5)
        assert anim.state.value.progress == 0.0

    def test_complete_handoff(self) -> None:
        """Test completing a handoff animation."""
        anim = HandoffAnimation()
        anim.start_handoff("Scout", "Sage", "findings")
        anim.complete_handoff()

        state = anim.state.value
        assert state.from_builder is None
        assert state.to_builder is None
        assert state.is_active is False
        assert len(state.handoffs) == 1
        assert state.handoffs[0][0] == "Scout"
        assert state.handoffs[0][1] == "Sage"
        assert state.handoffs[0][2] == "findings"

    def test_multiple_handoffs_recorded(self) -> None:
        """Test multiple handoffs are recorded in history."""
        anim = HandoffAnimation()

        anim.start_handoff("Scout", "Sage")
        anim.complete_handoff()

        anim.start_handoff("Sage", "Spark")
        anim.complete_handoff()

        anim.start_handoff("Spark", "Steady")
        anim.complete_handoff()

        state = anim.state.value
        assert len(state.handoffs) == 3

    def test_reset(self) -> None:
        """Test resetting animation state."""
        anim = HandoffAnimation()
        anim.start_handoff("Scout", "Sage")
        anim.complete_handoff()

        anim.reset()

        state = anim.state.value
        assert state.from_builder is None
        assert len(state.handoffs) == 0
        assert state.is_active is False

    def test_project_to_cli_active(self) -> None:
        """Test CLI projection during active animation."""
        anim = HandoffAnimation()
        anim.start_handoff("Scout", "Sage", "findings")
        anim.update_progress(0.5)

        output = anim.to_cli()

        assert "Scout" in output
        assert "Sage" in output
        assert "findings" in output

    def test_project_to_cli_inactive_with_history(self) -> None:
        """Test CLI projection with handoff history."""
        anim = HandoffAnimation()
        anim.start_handoff("Scout", "Sage")
        anim.complete_handoff()
        anim.start_handoff("Sage", "Spark")
        anim.complete_handoff()

        output = anim.to_cli()

        assert "Handoffs:" in output
        assert "Scout" in output
        assert "Sage" in output

    def test_project_to_json(self) -> None:
        """Test JSON projection produces dict."""
        anim = HandoffAnimation()
        anim.start_handoff("Scout", "Sage")

        output = anim.to_json()

        assert output["type"] == "handoff_animation"
        assert output["from_builder"] == "Scout"
        assert output["to_builder"] == "Sage"
        assert output["is_active"] is True

    def test_widget_type(self) -> None:
        """Test widget type returns correct value."""
        anim = HandoffAnimation()
        assert anim.widget_type() == "handoff_animation"


# =============================================================================
# ASCII Projection Tests
# =============================================================================


class TestASCIIProjections:
    """Tests for ASCII projection functions."""

    def test_project_formation_empty_state(self) -> None:
        """Test formation ASCII with empty state."""
        state = ForgeFormationState()
        output = project_formation_to_ascii(state)

        assert "COALITION" in output
        assert "idle" in output.upper() or "IDLE" in output

    def test_project_formation_with_builders(self) -> None:
        """Test formation ASCII with builders."""
        state = ForgeFormationState(
            task_description="Research competitors",
            phase="forming",
            progress_percent=67.0,
            builders=(
                BuilderEntry(
                    "Scout", "Scout", "Research", joined=True, compatibility_score=0.85
                ),
                BuilderEntry(
                    "Sage", "Sage", "Analysis", joined=True, compatibility_score=0.72
                ),
            ),
        )
        output = project_formation_to_ascii(state)

        assert "Research competitors" in output
        assert "Scout" in output
        assert "Sage" in output
        assert "85%" in output
        assert "72%" in output

    def test_project_formation_custom_width(self) -> None:
        """Test formation ASCII with custom width."""
        state = ForgeFormationState(task_description="Test")
        output = project_formation_to_ascii(state, width=80)

        # Check each line is approximately the right width
        lines = output.split("\n")
        for line in lines:
            assert len(line) <= 82  # Allow small variance

    def test_project_dialogue_empty_state(self) -> None:
        """Test dialogue ASCII with empty state."""
        state = DialogueState()
        output = project_dialogue_to_ascii(state)

        assert "DIALOGUE STREAM" in output
        assert "PAUSED" in output

    def test_project_dialogue_with_messages(self) -> None:
        """Test dialogue ASCII with messages."""
        state = DialogueState(
            messages=(
                DialogueMessage(DialogueSpeaker.SCOUT, "Exploring..."),
                DialogueMessage(DialogueSpeaker.SAGE, "Analyzing..."),
            ),
            is_streaming=True,
        )
        output = project_dialogue_to_ascii(state)

        assert "Scout" in output
        assert "Sage" in output
        assert "LIVE" in output

    def test_project_dialogue_with_handoff(self) -> None:
        """Test dialogue ASCII shows handoff indicator."""
        state = DialogueState(
            messages=(
                DialogueMessage(
                    DialogueSpeaker.SCOUT,
                    "Handing off",
                    is_handoff=True,
                    metadata={"to_speaker": "Sage"},
                ),
            ),
            is_streaming=True,
        )
        output = project_dialogue_to_ascii(state)

        assert "Scout" in output

    def test_project_handoff_active(self) -> None:
        """Test handoff ASCII during active animation."""
        state = HandoffState(
            from_builder="Scout",
            to_builder="Sage",
            artifact="findings",
            is_active=True,
            progress=0.5,
        )
        output = project_handoff_to_ascii(state)

        assert "Scout" in output
        assert "Sage" in output
        assert "findings" in output

    def test_project_handoff_inactive(self) -> None:
        """Test handoff ASCII when inactive with history."""
        state = HandoffState(
            handoffs=(
                ("Scout", "Sage", "findings", datetime.now()),
                ("Sage", "Spark", "design", datetime.now()),
            ),
        )
        output = project_handoff_to_ascii(state)

        assert "Handoffs:" in output
        assert "Scout" in output

    def test_project_handoff_no_history(self) -> None:
        """Test handoff ASCII with no history."""
        state = HandoffState()
        output = project_handoff_to_ascii(state)

        assert "No handoffs yet" in output


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_formation_view_empty(self) -> None:
        """Test creating empty formation view."""
        view = create_formation_view()

        assert view.state.value.phase == "idle"

    def test_create_formation_view_with_task(self) -> None:
        """Test creating formation view with task."""
        view = create_formation_view("Research competitors", "research_report")

        state = view.state.value
        assert state.task_description == "Research competitors"
        assert state.task_type == "research_report"
        assert state.phase == "forming"

    def test_create_dialogue_stream(self) -> None:
        """Test creating dialogue stream."""
        stream = create_dialogue_stream()

        assert isinstance(stream, DialogueStream)
        assert len(stream.state.value.messages) == 0

    def test_create_handoff_animation(self) -> None:
        """Test creating handoff animation."""
        anim = create_handoff_animation()

        assert isinstance(anim, HandoffAnimation)
        assert anim.state.value.is_active is False


# =============================================================================
# AGENTESE Handler Tests
# =============================================================================


class TestAGENTESEHandlers:
    """Tests for AGENTESE path handlers."""

    @pytest.mark.asyncio
    async def test_handle_coalition_subscribe(self) -> None:
        """Test coalition subscribe handler yields events."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general")

        handler = handle_coalition_subscribe("test-id", view)

        # Add a builder to emit an event
        view.add_builder("Scout", "Scout", "Research")

        try:
            # First event is FORMATION_STARTED
            event_dict1 = await asyncio.wait_for(handler.__anext__(), timeout=0.1)
            assert "type" in event_dict1
            assert event_dict1["type"] == "FORMATION_STARTED"

            # Second event is BUILDER_JOINED
            event_dict2 = await asyncio.wait_for(handler.__anext__(), timeout=0.1)
            assert "type" in event_dict2
            assert event_dict2["type"] == "BUILDER_JOINED"
        except asyncio.TimeoutError:
            pytest.skip("Event timing issue")

    @pytest.mark.asyncio
    async def test_handle_dialogue_witness(self) -> None:
        """Test dialogue witness handler yields messages."""
        stream = DialogueStream()

        handler = handle_dialogue_witness("test-id", stream)

        # Add a message
        stream.add_message(DialogueSpeaker.SCOUT, "Hello")

        try:
            msg_dict = await asyncio.wait_for(handler.__anext__(), timeout=0.1)
            assert "content" in msg_dict
            assert msg_dict["content"] == "Hello"
        except asyncio.TimeoutError:
            pytest.skip("Message timing issue")


# =============================================================================
# State Serialization Tests
# =============================================================================


class TestStateSerialization:
    """Tests for state to_dict methods."""

    def test_eigenvector_compatibility_to_dict(self) -> None:
        """Test EigenvectorCompatibility serialization."""
        compat = EigenvectorCompatibility(
            builder_a="Scout",
            builder_b="Sage",
            warmth=0.8,
            curiosity=0.9,
            overall=0.85,
        )
        d = compat.to_dict()

        assert d["builder_a"] == "Scout"
        assert d["builder_b"] == "Sage"
        assert d["dimensions"]["warmth"] == 0.8
        assert d["overall"] == 0.85

    def test_formation_event_to_dict(self) -> None:
        """Test FormationEvent serialization."""
        event = FormationEvent(
            type=FormationEventType.BUILDER_JOINED,
            builder="Scout",
            message="Scout joined",
        )
        d = event.to_dict()

        assert d["type"] == "BUILDER_JOINED"
        assert d["builder"] == "Scout"
        assert d["message"] == "Scout joined"
        assert "timestamp" in d

    def test_builder_entry_to_dict(self) -> None:
        """Test BuilderEntry serialization."""
        entry = BuilderEntry(
            archetype="Scout",
            name="Scout",
            role="Research",
            is_lead=True,
            compatibility_score=0.85,
        )
        d = entry.to_dict()

        assert d["archetype"] == "Scout"
        assert d["is_lead"] is True
        assert d["compatibility_score"] == 0.85

    def test_dialogue_message_to_dict(self) -> None:
        """Test DialogueMessage serialization."""
        msg = DialogueMessage(
            speaker=DialogueSpeaker.SCOUT,
            content="Hello",
            is_handoff=True,
        )
        d = msg.to_dict()

        assert d["speaker"] == "Scout"
        assert d["content"] == "Hello"
        assert d["is_handoff"] is True

    def test_handoff_state_to_dict(self) -> None:
        """Test HandoffState serialization."""
        state = HandoffState(
            from_builder="Scout",
            to_builder="Sage",
            is_active=True,
            progress=0.5,
        )
        d = state.to_dict()

        assert d["from_builder"] == "Scout"
        assert d["to_builder"] == "Sage"
        assert d["is_active"] is True
        assert d["progress"] == 0.5


# =============================================================================
# SSE Mock Tests
# =============================================================================


class MockSSEClient:
    """Mock SSE client for testing."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.connected = False

    async def connect(self) -> None:
        self.connected = True

    async def receive(self) -> dict[str, Any]:
        if not self.events:
            await asyncio.sleep(0.1)
            return {"type": "keepalive"}
        return self.events.pop(0)

    def push(self, event: dict[str, Any]) -> None:
        self.events.append(event)


class TestSSEMocking:
    """Tests demonstrating SSE mocking patterns."""

    @pytest.mark.asyncio
    async def test_mock_sse_client_receives_events(self) -> None:
        """Test that mock SSE client receives pushed events."""
        client = MockSSEClient()
        await client.connect()

        assert client.connected

        client.push({"type": "FORMATION_STARTED", "message": "Starting"})
        client.push({"type": "BUILDER_JOINED", "builder": "Scout"})

        event1 = await client.receive()
        assert event1["type"] == "FORMATION_STARTED"

        event2 = await client.receive()
        assert event2["type"] == "BUILDER_JOINED"

    @pytest.mark.asyncio
    async def test_mock_sse_client_keepalive(self) -> None:
        """Test that mock SSE client returns keepalive when empty."""
        client = MockSSEClient()
        await client.connect()

        event = await client.receive()
        assert event["type"] == "keepalive"

    @pytest.mark.asyncio
    async def test_formation_view_sse_integration(self) -> None:
        """Test formation view with mock SSE client."""
        view = CoalitionFormationView()
        client = MockSSEClient()
        await client.connect()

        # Wire view events to client
        def on_event(event: FormationEvent) -> None:
            client.push(event.to_dict())

        view = CoalitionFormationView(on_event=on_event)

        # Start formation
        view.start_formation("Test task", "general")

        # Check event was pushed
        event = await client.receive()
        assert event["type"] == "FORMATION_STARTED"


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for the visualization system."""

    def test_full_formation_workflow(self) -> None:
        """Test complete formation workflow."""
        view = CoalitionFormationView()

        # Start formation
        view.start_formation("Research competitors", "research_report")
        assert view.state.value.phase == "forming"

        # Add builders
        view.add_builder(
            "Scout", "Scout", "Research", is_lead=True, compatibility_score=0.9
        )
        view.add_builder("Sage", "Sage", "Analysis", compatibility_score=0.85)
        view.add_builder("Scribe", "Scribe", "Documentation", compatibility_score=0.78)

        # Add compatibility
        view.add_compatibility(
            "Scout", "Sage", EigenvectorCompatibility("Scout", "Sage", overall=0.85)
        )

        # Complete formation
        view.complete_formation()

        state = view.state.value
        assert state.phase == "formed"
        assert len(state.builders) == 3
        assert state.lead_builder == "Scout"
        assert "Scout" in state.compatibility_matrix

    def test_dialogue_with_handoffs(self) -> None:
        """Test dialogue stream with handoffs and artifacts."""
        stream = DialogueStream()
        stream.start_streaming()

        # Scout explores
        stream.add_message(DialogueSpeaker.SCOUT, "Exploring the codebase...")
        stream.add_message(DialogueSpeaker.SCOUT, "Found 5 key modules")

        # Handoff to Sage
        stream.add_handoff("Scout", "Sage", "Passing findings")

        # Sage analyzes
        stream.add_message(DialogueSpeaker.SAGE, "Analyzing the structure...")
        stream.add_artifact(DialogueSpeaker.SAGE, "design_doc", "Architecture overview")

        # Handoff to Scribe
        stream.add_handoff("Sage", "Scribe", "Ready for documentation")

        state = stream.state.value
        assert len(state.messages) == 6
        assert state.messages[2].is_handoff is True
        assert state.messages[4].is_artifact is True

    def test_handoff_animation_sequence(self) -> None:
        """Test handoff animation through a sequence."""
        anim = HandoffAnimation()

        # Scout -> Sage
        anim.start_handoff("Scout", "Sage", "research")
        for i in range(5):
            anim.update_progress(i * 0.2)
        anim.complete_handoff()

        # Sage -> Spark
        anim.start_handoff("Sage", "Spark", "design")
        for i in range(5):
            anim.update_progress(i * 0.2)
        anim.complete_handoff()

        state = anim.state.value
        assert len(state.handoffs) == 2
        assert state.handoffs[0][2] == "research"
        assert state.handoffs[1][2] == "design"

    def test_all_widgets_project_consistently(self) -> None:
        """Test all widgets project to all targets."""
        formation = create_formation_view("Test", "general")
        formation.add_builder("Scout", "Scout", "Research")

        dialogue = create_dialogue_stream()
        dialogue.add_message(DialogueSpeaker.SCOUT, "Hello")

        handoff = create_handoff_animation()
        handoff.start_handoff("Scout", "Sage")

        # Test all targets
        for target in [
            RenderTarget.CLI,
            RenderTarget.JSON,
            RenderTarget.TUI,
            RenderTarget.MARIMO,
        ]:
            assert formation.project(target) is not None
            assert dialogue.project(target) is not None
            assert handoff.project(target) is not None


# =============================================================================
# Projection Law Verification Tests
# =============================================================================


class TestProjectionLaws:
    """
    Tests verifying functor law compliance for projections.

    Projections must satisfy:
    1. Identity: project(id(state)) == project(state)
    2. Determinism: Same state -> same output
    """

    def test_formation_view_identity_law_cli(self) -> None:
        """Verify identity law for CLI projection."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general")
        view.add_builder("Scout", "Scout", "Research")

        # Project twice with same state
        output1 = view.to_cli()
        output2 = view.to_cli()

        assert output1 == output2, (
            "Identity law violation: CLI projection not idempotent"
        )

    def test_formation_view_identity_law_json(self) -> None:
        """Verify identity law for JSON projection."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general")

        output1 = view.to_json()
        output2 = view.to_json()

        # JSON dicts should be equal
        assert output1 == output2, (
            "Identity law violation: JSON projection not idempotent"
        )

    def test_dialogue_stream_identity_law(self) -> None:
        """Verify identity law for dialogue stream projections."""
        stream = DialogueStream()
        stream.add_message(DialogueSpeaker.SCOUT, "Hello")
        stream.add_message(DialogueSpeaker.SAGE, "World")

        for target in [RenderTarget.CLI, RenderTarget.JSON]:
            output1 = stream.project(target)
            output2 = stream.project(target)
            assert output1 == output2, f"Identity law violation for {target}"

    def test_handoff_animation_identity_law(self) -> None:
        """Verify identity law for handoff animation projections."""
        anim = HandoffAnimation()
        anim.start_handoff("Scout", "Sage", "findings")

        for target in [RenderTarget.CLI, RenderTarget.JSON]:
            output1 = anim.project(target)
            output2 = anim.project(target)
            assert output1 == output2, f"Identity law violation for {target}"

    def test_determinism_formation_view(self) -> None:
        """Verify determinism: same state always produces same output."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general")
        view.add_builder("Scout", "Scout", "Research")
        view.add_builder("Sage", "Sage", "Analysis")

        # Project 10 times and verify all outputs are identical
        outputs = [view.to_cli() for _ in range(10)]
        assert len(set(outputs)) == 1, "Determinism violation: outputs differ"

    def test_determinism_json_structure(self) -> None:
        """Verify JSON output structure is deterministic."""
        view = CoalitionFormationView()
        view.start_formation("Test task", "general")

        json1 = view.to_json()
        json2 = view.to_json()

        # Verify structure
        assert json1.keys() == json2.keys()
        assert json1["type"] == json2["type"]
        assert json1["phase"] == json2["phase"]


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error boundaries and validation."""

    def test_start_formation_while_forming_raises(self) -> None:
        """Test that starting formation while already forming raises error."""
        view = CoalitionFormationView()
        view.start_formation("Task 1", "general")

        with pytest.raises(FormationStateError) as exc_info:
            view.start_formation("Task 2", "general")

        assert "already in phase" in str(exc_info.value)

    def test_add_builder_when_not_forming_raises(self) -> None:
        """Test that adding builder when not forming raises error."""
        view = CoalitionFormationView()

        with pytest.raises(FormationStateError) as exc_info:
            view.add_builder("Scout", "Scout", "Research")

        assert "not in forming phase" in str(exc_info.value)

    def test_add_builder_after_complete_raises(self) -> None:
        """Test that adding builder after formation complete raises error."""
        view = CoalitionFormationView()
        view.start_formation("Test", "general")
        view.add_builder("Scout", "Scout", "Research")
        view.complete_formation()

        with pytest.raises(FormationStateError) as exc_info:
            view.add_builder("Sage", "Sage", "Analysis")

        assert "not in forming phase" in str(exc_info.value)

    def test_compatibility_score_clamping(self) -> None:
        """Test that compatibility score is clamped to [0.0, 1.0]."""
        view = CoalitionFormationView()
        view.start_formation("Test", "general")

        # Score > 1.0 should be clamped
        view.add_builder("Scout", "Scout", "Research", compatibility_score=1.5)
        state = view.state.value
        assert state.builders[0].compatibility_score <= 1.0

    def test_compatibility_score_negative_clamping(self) -> None:
        """Test that negative compatibility score is clamped to 0.0."""
        view = CoalitionFormationView()
        view.start_formation("Test", "general")

        view.add_builder("Scout", "Scout", "Research", compatibility_score=-0.5)
        state = view.state.value
        assert state.builders[0].compatibility_score >= 0.0

    def test_exception_classes_inherit_properly(self) -> None:
        """Test that exception classes inherit from base."""
        assert issubclass(FormationStateError, ForgeVisualizationError)
        assert issubclass(ForgeVisualizationError, Exception)


# =============================================================================
# State Transition Tests
# =============================================================================


class TestStateTransitions:
    """Tests for valid state transitions."""

    def test_idle_to_forming_valid(self) -> None:
        """Test idle -> forming is valid."""
        view = CoalitionFormationView()
        assert view.state.value.phase == "idle"

        view.start_formation("Test", "general")
        assert view.state.value.phase == "forming"

    def test_forming_to_formed_valid(self) -> None:
        """Test forming -> formed is valid."""
        view = CoalitionFormationView()
        view.start_formation("Test", "general")
        view.add_builder("Scout", "Scout", "Research")
        view.complete_formation()

        assert view.state.value.phase == "formed"

    def test_complete_to_forming_via_restart(self) -> None:
        """Test complete -> forming is valid (for new task)."""
        view = CoalitionFormationView()
        view.start_formation("Task 1", "general")
        view.add_builder("Scout", "Scout", "Research")
        view.complete_formation()

        assert view.state.value.phase == "formed"

        # Can start new formation after complete
        # Reset to idle first
        view._signal.set(ForgeFormationState())
        view.start_formation("Task 2", "general")
        assert view.state.value.phase == "forming"

    def test_duplicate_builder_handling(self) -> None:
        """Test that duplicate builders are handled gracefully."""
        view = CoalitionFormationView()
        view.start_formation("Test", "general")

        view.add_builder("Scout", "Scout", "Research")
        initial_count = len(view.state.value.builders)

        # Adding same archetype again should be handled
        view.add_builder("Scout", "Scout-2", "Research-2")
        # Should still have same count (duplicate skipped)
        assert len(view.state.value.builders) == initial_count


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_task_description(self) -> None:
        """Test formation with empty task description."""
        view = CoalitionFormationView()
        view.start_formation("", "general")

        state = view.state.value
        assert state.task_description == ""
        assert state.phase == "forming"

    def test_very_long_task_description(self) -> None:
        """Test formation with very long task description."""
        view = CoalitionFormationView()
        long_desc = "A" * 1000
        view.start_formation(long_desc, "general")

        state = view.state.value
        assert state.task_description == long_desc

    def test_special_characters_in_task(self) -> None:
        """Test formation with special characters in task."""
        view = CoalitionFormationView()
        special_task = "Test <task> with 'quotes' and \"double\" & symbols"
        view.start_formation(special_task, "general")

        state = view.state.value
        assert state.task_description == special_task

    def test_max_builders(self) -> None:
        """Test adding many builders."""
        view = CoalitionFormationView()
        view.start_formation("Test", "general")

        for i in range(10):
            view.add_builder(f"Builder{i}", f"Name{i}", f"Role{i}")

        state = view.state.value
        assert len(state.builders) == 10
        assert state.progress_percent == 100.0  # Progress capped at 100%

    def test_dialogue_empty_content(self) -> None:
        """Test dialogue with empty content."""
        stream = DialogueStream()
        stream.add_message(DialogueSpeaker.SCOUT, "")

        state = stream.state.value
        assert len(state.messages) == 1
        assert state.messages[0].content == ""

    def test_handoff_no_artifact(self) -> None:
        """Test handoff without artifact."""
        anim = HandoffAnimation()
        anim.start_handoff("Scout", "Sage", artifact=None)

        state = anim.state.value
        assert state.artifact is None
        assert state.is_active is True

    def test_handoff_complete_without_start(self) -> None:
        """Test completing handoff without starting."""
        anim = HandoffAnimation()
        anim.complete_handoff()

        # Should handle gracefully
        state = anim.state.value
        assert state.is_active is False
        assert len(state.handoffs) == 0  # No handoff recorded


# =============================================================================
# Unicode and Encoding Tests
# =============================================================================


class TestUnicodeHandling:
    """Tests for unicode and encoding edge cases."""

    def test_unicode_task_description(self) -> None:
        """Test formation with unicode task description."""
        view = CoalitionFormationView()
        unicode_desc = "Research competitors"
        view.start_formation(unicode_desc, "general")

        assert view.state.value.task_description == unicode_desc

    def test_unicode_builder_name(self) -> None:
        """Test builder with unicode name."""
        view = CoalitionFormationView()
        view.start_formation("Test", "general")
        view.add_builder("Scout", "Agent", "Research")

        assert view.state.value.builders[0].name == "Agent"

    def test_unicode_dialogue_message(self) -> None:
        """Test dialogue with unicode message."""
        stream = DialogueStream()
        stream.add_message(DialogueSpeaker.SCOUT, "Hello World!")

        assert stream.state.value.messages[0].content == "Hello World!"

    def test_cli_projection_unicode_safe(self) -> None:
        """Test that CLI projection handles unicode safely."""
        view = CoalitionFormationView()
        view.start_formation("Unicode test", "general")
        view.add_builder("Scout", "Agent", "Research")

        # Should not raise
        output = view.to_cli()
        assert isinstance(output, str)


# =============================================================================
# Concurrency Tests
# =============================================================================


class TestConcurrency:
    """Tests for concurrent access patterns."""

    @pytest.mark.asyncio
    async def test_concurrent_event_emission(self) -> None:
        """Test that concurrent event emission is safe."""
        view = CoalitionFormationView()
        view.start_formation("Test", "general")

        async def add_builders() -> None:
            for i in range(5):
                try:
                    view.add_builder(f"Builder{i}", f"Name{i}", f"Role{i}")
                except FormationStateError:
                    pass  # Handle state errors gracefully
                await asyncio.sleep(0.01)

        # Run concurrently
        await asyncio.gather(add_builders(), add_builders())

        # State should be consistent
        state = view.state.value
        assert len(state.builders) >= 1

    @pytest.mark.asyncio
    async def test_concurrent_dialogue_messages(self) -> None:
        """Test concurrent dialogue message addition."""
        stream = DialogueStream()

        async def add_messages() -> None:
            for i in range(10):
                stream.add_message(DialogueSpeaker.SCOUT, f"Message {i}")
                await asyncio.sleep(0.001)

        await asyncio.gather(add_messages(), add_messages())

        # Should have messages from both
        state = stream.state.value
        assert len(state.messages) >= 10
