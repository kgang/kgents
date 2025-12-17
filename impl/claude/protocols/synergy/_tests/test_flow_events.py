"""
Tests for F-gent Flow Synergy events.

Phase 1 Foundation: Cross-jewel communication events for Flow modalities.
"""

import pytest
from protocols.synergy.events import (
    Jewel,
    SynergyEventType,
    create_consensus_reached_event,
    create_contribution_posted_event,
    create_flow_completed_event,
    # Flow event factories
    create_flow_started_event,
    create_hypothesis_created_event,
    create_hypothesis_synthesized_event,
    create_turn_completed_event,
)


class TestFlowEventTypes:
    """Test Flow event type definitions."""

    def test_flow_started_event_type_exists(self) -> None:
        """FLOW_STARTED event type should exist."""
        assert SynergyEventType.FLOW_STARTED.value == "flow_started"

    def test_flow_completed_event_type_exists(self) -> None:
        """FLOW_COMPLETED event type should exist."""
        assert SynergyEventType.FLOW_COMPLETED.value == "flow_completed"

    def test_turn_completed_event_type_exists(self) -> None:
        """TURN_COMPLETED event type should exist."""
        assert SynergyEventType.TURN_COMPLETED.value == "turn_completed"

    def test_hypothesis_created_event_type_exists(self) -> None:
        """HYPOTHESIS_CREATED event type should exist."""
        assert SynergyEventType.HYPOTHESIS_CREATED.value == "hypothesis_created"

    def test_hypothesis_synthesized_event_type_exists(self) -> None:
        """HYPOTHESIS_SYNTHESIZED event type should exist."""
        assert SynergyEventType.HYPOTHESIS_SYNTHESIZED.value == "hypothesis_synthesized"

    def test_consensus_reached_event_type_exists(self) -> None:
        """CONSENSUS_REACHED event type should exist."""
        assert SynergyEventType.CONSENSUS_REACHED.value == "consensus_reached"

    def test_contribution_posted_event_type_exists(self) -> None:
        """CONTRIBUTION_POSTED event type should exist."""
        assert SynergyEventType.CONTRIBUTION_POSTED.value == "contribution_posted"


class TestFlowStartedEvent:
    """Test create_flow_started_event factory."""

    def test_creates_event_with_required_fields(self) -> None:
        """Should create event with required fields."""
        event = create_flow_started_event(
            flow_id="flow-123",
            jewel=Jewel.BRAIN,
            modality="chat",
        )

        assert event.source_jewel == Jewel.BRAIN
        assert event.target_jewel == Jewel.ALL
        assert event.event_type == SynergyEventType.FLOW_STARTED
        assert event.source_id == "flow-123"
        assert event.payload["modality"] == "chat"

    def test_includes_optional_session_id(self) -> None:
        """Should include optional session_id."""
        event = create_flow_started_event(
            flow_id="flow-123",
            jewel=Jewel.GARDENER,
            modality="chat",
            session_id="session-456",
        )

        assert event.payload["session_id"] == "session-456"

    def test_includes_optional_config(self) -> None:
        """Should include optional config."""
        event = create_flow_started_event(
            flow_id="flow-123",
            jewel=Jewel.GESTALT,
            modality="research",
            config={"max_depth": 3},
        )

        assert event.payload["config"]["max_depth"] == 3


class TestFlowCompletedEvent:
    """Test create_flow_completed_event factory."""

    def test_creates_event_with_metrics(self) -> None:
        """Should create event with metrics."""
        event = create_flow_completed_event(
            flow_id="flow-123",
            jewel=Jewel.BRAIN,
            modality="chat",
            duration_seconds=120.5,
            turns=10,
            entropy_spent=0.15,
        )

        assert event.source_jewel == Jewel.BRAIN
        assert event.target_jewel == Jewel.BRAIN
        assert event.event_type == SynergyEventType.FLOW_COMPLETED
        assert event.payload["modality"] == "chat"
        assert event.payload["duration_seconds"] == 120.5
        assert event.payload["turns"] == 10
        assert event.payload["entropy_spent"] == 0.15

    def test_research_modality_metrics(self) -> None:
        """Should include research-specific metrics."""
        event = create_flow_completed_event(
            flow_id="flow-123",
            jewel=Jewel.GESTALT,
            modality="research",
            duration_seconds=300.0,
            hypotheses=5,
        )

        assert event.payload["hypotheses"] == 5

    def test_collaboration_modality_metrics(self) -> None:
        """Should include collaboration-specific metrics."""
        event = create_flow_completed_event(
            flow_id="flow-123",
            jewel=Jewel.COALITION,
            modality="collaboration",
            duration_seconds=600.0,
            contributions=15,
        )

        assert event.payload["contributions"] == 15


class TestTurnCompletedEvent:
    """Test create_turn_completed_event factory."""

    def test_creates_event_with_turn_data(self) -> None:
        """Should create event with turn data."""
        event = create_turn_completed_event(
            turn_id="turn-001",
            flow_id="flow-123",
            jewel=Jewel.BRAIN,
            turn_number=5,
            user_message_preview="What is the architecture?",
            assistant_response_preview="The architecture consists of...",
            tokens_in=50,
            tokens_out=200,
            latency_seconds=2.5,
        )

        assert event.source_jewel == Jewel.BRAIN
        assert event.target_jewel == Jewel.BRAIN
        assert event.event_type == SynergyEventType.TURN_COMPLETED
        assert event.source_id == "turn-001"
        assert event.payload["flow_id"] == "flow-123"
        assert event.payload["turn_number"] == 5
        assert event.payload["tokens_in"] == 50
        assert event.payload["tokens_out"] == 200
        assert event.payload["latency_seconds"] == 2.5

    def test_truncates_long_messages(self) -> None:
        """Should truncate messages to 100 chars."""
        long_message = "x" * 200
        event = create_turn_completed_event(
            turn_id="turn-001",
            flow_id="flow-123",
            jewel=Jewel.BRAIN,
            turn_number=1,
            user_message_preview=long_message,
            assistant_response_preview=long_message,
            tokens_in=100,
            tokens_out=500,
            latency_seconds=1.0,
        )

        assert len(event.payload["user_message_preview"]) == 100
        assert len(event.payload["assistant_response_preview"]) == 100


class TestHypothesisCreatedEvent:
    """Test create_hypothesis_created_event factory."""

    def test_creates_event_with_hypothesis_data(self) -> None:
        """Should create event with hypothesis data."""
        event = create_hypothesis_created_event(
            hypothesis_id="h-001",
            flow_id="flow-123",
            jewel=Jewel.GESTALT,
            hypothesis_content="The complexity comes from tight coupling",
            parent_id=None,
            depth=0,
            promise=0.8,
        )

        assert event.source_jewel == Jewel.GESTALT
        assert event.target_jewel == Jewel.ALL
        assert event.event_type == SynergyEventType.HYPOTHESIS_CREATED
        assert event.source_id == "h-001"
        assert event.payload["flow_id"] == "flow-123"
        assert event.payload["parent_id"] is None
        assert event.payload["depth"] == 0
        assert event.payload["promise"] == 0.8

    def test_includes_parent_id_for_branches(self) -> None:
        """Should include parent_id for branch hypotheses."""
        event = create_hypothesis_created_event(
            hypothesis_id="h-002",
            flow_id="flow-123",
            jewel=Jewel.GESTALT,
            hypothesis_content="Specifically, the data layer",
            parent_id="h-001",
            depth=1,
            promise=0.6,
        )

        assert event.payload["parent_id"] == "h-001"
        assert event.payload["depth"] == 1


class TestHypothesisSynthesizedEvent:
    """Test create_hypothesis_synthesized_event factory."""

    def test_creates_event_with_synthesis_data(self) -> None:
        """Should create event with synthesis data."""
        event = create_hypothesis_synthesized_event(
            synthesis_id="syn-001",
            flow_id="flow-123",
            jewel=Jewel.GESTALT,
            question="Why is this module complex?",
            answer="The module is complex due to tight coupling and unclear boundaries.",
            confidence=0.85,
            hypotheses_explored=5,
            insights_count=3,
        )

        assert event.source_jewel == Jewel.GESTALT
        assert event.target_jewel == Jewel.BRAIN
        assert event.event_type == SynergyEventType.HYPOTHESIS_SYNTHESIZED
        assert event.payload["confidence"] == 0.85
        assert event.payload["hypotheses_explored"] == 5
        assert event.payload["insights_count"] == 3


class TestConsensusReachedEvent:
    """Test create_consensus_reached_event factory."""

    def test_creates_event_with_consensus_data(self) -> None:
        """Should create event with consensus data."""
        event = create_consensus_reached_event(
            decision_id="dec-001",
            flow_id="flow-123",
            jewel=Jewel.COALITION,
            proposal_content="Use strategy A for implementation",
            outcome="approved",
            vote_summary={"approve": 3, "reject": 1, "abstain": 1},
            participants=["agent-1", "agent-2", "agent-3", "agent-4", "agent-5"],
        )

        assert event.source_jewel == Jewel.COALITION
        assert event.target_jewel == Jewel.BRAIN
        assert event.event_type == SynergyEventType.CONSENSUS_REACHED
        assert event.payload["outcome"] == "approved"
        assert event.payload["vote_summary"]["approve"] == 3
        assert len(event.payload["participants"]) == 5


class TestContributionPostedEvent:
    """Test create_contribution_posted_event factory."""

    def test_creates_event_with_contribution_data(self) -> None:
        """Should create event with contribution data."""
        event = create_contribution_posted_event(
            contribution_id="contrib-001",
            flow_id="flow-123",
            jewel=Jewel.COALITION,
            agent_id="agent-1",
            contribution_type="idea",
            content_preview="We should consider using a cache",
            confidence=0.75,
            round_number=2,
        )

        assert event.source_jewel == Jewel.COALITION
        assert event.target_jewel == Jewel.ALL
        assert event.event_type == SynergyEventType.CONTRIBUTION_POSTED
        assert event.payload["agent_id"] == "agent-1"
        assert event.payload["contribution_type"] == "idea"
        assert event.payload["confidence"] == 0.75
        assert event.payload["round_number"] == 2


class TestEventSerialization:
    """Test Flow event serialization."""

    def test_flow_event_round_trip(self) -> None:
        """Flow events should serialize and deserialize correctly."""
        from protocols.synergy.events import SynergyEvent

        original = create_flow_started_event(
            flow_id="flow-123",
            jewel=Jewel.BRAIN,
            modality="chat",
            session_id="session-456",
        )

        data = original.to_dict()
        restored = SynergyEvent.from_dict(data)

        assert restored.source_jewel == original.source_jewel
        assert restored.target_jewel == original.target_jewel
        assert restored.event_type == original.event_type
        assert restored.source_id == original.source_id
        assert restored.payload == original.payload
