"""
Tests for synergy events.

Foundation 4 - Wave 0: Cross-jewel communication events.
"""

from datetime import datetime

import pytest

from protocols.synergy.events import (
    Jewel,
    SynergyEvent,
    SynergyEventType,
    SynergyResult,
    create_analysis_complete_event,
    create_artifact_created_event,
    create_crystal_formed_event,
    create_session_complete_event,
)


class TestSynergyEvent:
    """Tests for SynergyEvent dataclass."""

    def test_create_event(self) -> None:
        """Events can be created with required fields."""
        event = SynergyEvent(
            source_jewel=Jewel.GESTALT,
            target_jewel=Jewel.BRAIN,
            event_type=SynergyEventType.ANALYSIS_COMPLETE,
            source_id="analysis-123",
        )

        assert event.source_jewel == Jewel.GESTALT
        assert event.target_jewel == Jewel.BRAIN
        assert event.event_type == SynergyEventType.ANALYSIS_COMPLETE
        assert event.source_id == "analysis-123"
        assert event.payload == {}
        assert isinstance(event.timestamp, datetime)
        assert isinstance(event.correlation_id, str)

    def test_create_event_with_payload(self) -> None:
        """Events can include a payload."""
        event = SynergyEvent(
            source_jewel=Jewel.GESTALT,
            target_jewel=Jewel.BRAIN,
            event_type=SynergyEventType.ANALYSIS_COMPLETE,
            source_id="analysis-123",
            payload={
                "module_count": 50,
                "health_grade": "B+",
            },
        )

        assert event.payload["module_count"] == 50
        assert event.payload["health_grade"] == "B+"

    def test_to_dict_serialization(self) -> None:
        """Events can be serialized to dict."""
        event = SynergyEvent(
            source_jewel=Jewel.GESTALT,
            target_jewel=Jewel.BRAIN,
            event_type=SynergyEventType.ANALYSIS_COMPLETE,
            source_id="analysis-123",
            payload={"module_count": 50},
        )

        data = event.to_dict()

        assert data["source_jewel"] == "gestalt"
        assert data["target_jewel"] == "brain"
        assert data["event_type"] == "analysis_complete"
        assert data["source_id"] == "analysis-123"
        assert data["payload"]["module_count"] == 50
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["correlation_id"], str)

    def test_from_dict_deserialization(self) -> None:
        """Events can be deserialized from dict."""
        data = {
            "source_jewel": "gestalt",
            "target_jewel": "brain",
            "event_type": "analysis_complete",
            "source_id": "analysis-123",
            "payload": {"module_count": 50},
            "timestamp": "2025-12-16T10:00:00",
            "correlation_id": "corr-456",
        }

        event = SynergyEvent.from_dict(data)

        assert event.source_jewel == Jewel.GESTALT
        assert event.target_jewel == Jewel.BRAIN
        assert event.event_type == SynergyEventType.ANALYSIS_COMPLETE
        assert event.source_id == "analysis-123"
        assert event.payload["module_count"] == 50
        assert event.correlation_id == "corr-456"


class TestSynergyResult:
    """Tests for SynergyResult dataclass."""

    def test_create_success_result(self) -> None:
        """Success results have success=True."""
        result = SynergyResult(
            success=True,
            handler_name="TestHandler",
            message="Handled successfully",
            artifact_id="crystal-123",
        )

        assert result.success is True
        assert result.handler_name == "TestHandler"
        assert result.message == "Handled successfully"
        assert result.artifact_id == "crystal-123"

    def test_create_failure_result(self) -> None:
        """Failure results have success=False."""
        result = SynergyResult(
            success=False,
            handler_name="TestHandler",
            message="Handler failed: network error",
        )

        assert result.success is False
        assert result.artifact_id is None

    def test_to_dict(self) -> None:
        """Results can be serialized."""
        result = SynergyResult(
            success=True,
            handler_name="TestHandler",
            message="OK",
            artifact_id="crystal-123",
            metadata={"key": "value"},
        )

        data = result.to_dict()

        assert data["success"] is True
        assert data["handler_name"] == "TestHandler"
        assert data["artifact_id"] == "crystal-123"
        assert data["metadata"]["key"] == "value"


class TestFactoryFunctions:
    """Tests for event factory functions."""

    def test_create_analysis_complete_event(self) -> None:
        """Factory creates analysis complete event."""
        event = create_analysis_complete_event(
            source_id="analysis-123",
            module_count=50,
            health_grade="B+",
            average_health=0.84,
            drift_count=2,
            root_path="/path/to/project",
        )

        assert event.source_jewel == Jewel.GESTALT
        assert event.target_jewel == Jewel.BRAIN
        assert event.event_type == SynergyEventType.ANALYSIS_COMPLETE
        assert event.payload["module_count"] == 50
        assert event.payload["health_grade"] == "B+"
        assert event.payload["average_health"] == 0.84
        assert event.payload["drift_count"] == 2
        assert event.payload["root_path"] == "/path/to/project"

    def test_create_crystal_formed_event(self) -> None:
        """Factory creates crystal formed event."""
        event = create_crystal_formed_event(
            crystal_id="crystal-123",
            content_preview="Architecture Analysis: impl-claude",
            content_type="text",
        )

        assert event.source_jewel == Jewel.BRAIN
        assert event.target_jewel == Jewel.ALL
        assert event.event_type == SynergyEventType.CRYSTAL_FORMED
        assert event.source_id == "crystal-123"
        assert "Architecture" in event.payload["content_preview"]

    def test_create_session_complete_event(self) -> None:
        """Factory creates session complete event."""
        event = create_session_complete_event(
            session_id="session-123",
            session_name="Feature Implementation",
            artifacts_count=5,
            learnings=["Pattern X works well", "Avoid approach Y"],
        )

        assert event.source_jewel == Jewel.GARDENER
        assert event.target_jewel == Jewel.BRAIN
        assert event.event_type == SynergyEventType.SESSION_COMPLETE
        assert event.payload["session_name"] == "Feature Implementation"
        assert event.payload["artifacts_count"] == 5
        assert len(event.payload["learnings"]) == 2

    def test_create_artifact_created_event(self) -> None:
        """Factory creates artifact created event."""
        event = create_artifact_created_event(
            artifact_id="artifact-123",
            artifact_type="code",
            path="/src/foo.py",
            description="New module implementation",
            session_id="session-456",
        )

        assert event.source_jewel == Jewel.GARDENER
        assert event.target_jewel == Jewel.BRAIN
        assert event.event_type == SynergyEventType.ARTIFACT_CREATED
        assert event.payload["artifact_type"] == "code"
        assert event.payload["path"] == "/src/foo.py"
        assert event.payload["session_id"] == "session-456"


class TestJewelEnum:
    """Tests for Jewel enum."""

    def test_all_jewels_exist(self) -> None:
        """All 7 crown jewels plus ALL are defined."""
        assert Jewel.BRAIN.value == "brain"
        assert Jewel.GESTALT.value == "gestalt"
        assert Jewel.GARDENER.value == "gardener"
        assert Jewel.ATELIER.value == "atelier"
        assert Jewel.COALITION.value == "coalition"
        assert Jewel.PARK.value == "park"
        assert Jewel.DOMAIN.value == "domain"
        assert Jewel.ALL.value == "*"


class TestEventTypes:
    """Tests for SynergyEventType enum."""

    def test_gestalt_events(self) -> None:
        """Gestalt event types exist."""
        assert SynergyEventType.ANALYSIS_COMPLETE.value == "analysis_complete"
        assert SynergyEventType.HEALTH_COMPUTED.value == "health_computed"
        assert SynergyEventType.DRIFT_DETECTED.value == "drift_detected"

    def test_brain_events(self) -> None:
        """Brain event types exist."""
        assert SynergyEventType.CRYSTAL_FORMED.value == "crystal_formed"
        assert SynergyEventType.MEMORY_SURFACED.value == "memory_surfaced"

    def test_gardener_events(self) -> None:
        """Gardener event types exist."""
        assert SynergyEventType.SESSION_STARTED.value == "session_started"
        assert SynergyEventType.SESSION_COMPLETE.value == "session_complete"
        assert SynergyEventType.ARTIFACT_CREATED.value == "artifact_created"
