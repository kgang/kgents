"""
Tests for Drift Detection Handler - Sprint 2.

Tests the GestaltToBrainHandler's ability to capture drift events.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from protocols.synergy.events import (
    Jewel,
    SynergyEvent,
    SynergyEventType,
    create_analysis_complete_event,
    create_drift_detected_event,
)
from protocols.synergy.handlers.gestalt_brain import GestaltToBrainHandler

# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateDriftDetectedEvent:
    """Tests for create_drift_detected_event factory."""

    def test_creates_event_with_correct_type(self):
        """Event has DRIFT_DETECTED type."""
        event = create_drift_detected_event(
            source_id="drift-001",
            source_module="agents.m.cartographer",
            target_module="protocols.agentese",
            rule="no_upward_deps",
            severity="error",
            root_path="/path/to/project",
        )
        assert event.event_type == SynergyEventType.DRIFT_DETECTED

    def test_source_and_target_jewels(self):
        """Event routes from Gestalt to Brain."""
        event = create_drift_detected_event(
            source_id="drift-001",
            source_module="foo",
            target_module="bar",
            rule="test",
            severity="warning",
            root_path="/",
        )
        assert event.source_jewel == Jewel.GESTALT
        assert event.target_jewel == Jewel.BRAIN

    def test_payload_contains_all_fields(self):
        """Payload has all required drift fields."""
        event = create_drift_detected_event(
            source_id="drift-001",
            source_module="agents.m.cartographer",
            target_module="protocols.agentese",
            rule="no_upward_deps",
            severity="error",
            root_path="/path/to/project",
            message="Custom message",
        )
        assert event.payload["source_module"] == "agents.m.cartographer"
        assert event.payload["target_module"] == "protocols.agentese"
        assert event.payload["rule"] == "no_upward_deps"
        assert event.payload["severity"] == "error"
        assert event.payload["root_path"] == "/path/to/project"
        assert event.payload["message"] == "Custom message"

    def test_default_message_generated(self):
        """Default message describes the violation."""
        event = create_drift_detected_event(
            source_id="drift-001",
            source_module="foo.bar",
            target_module="baz.qux",
            rule="layer_rule",
            severity="warning",
            root_path="/",
        )
        assert "foo.bar" in event.payload["message"]
        assert "baz.qux" in event.payload["message"]
        assert "layer_rule" in event.payload["message"]


# =============================================================================
# Handler Tests
# =============================================================================


class TestGestaltToBrainHandler:
    """Tests for GestaltToBrainHandler."""

    @pytest.fixture
    def handler(self):
        """Create handler in dry-run mode."""
        return GestaltToBrainHandler(auto_capture=False)

    def test_supports_analysis_complete(self, handler):
        """Handler supports ANALYSIS_COMPLETE event."""
        assert SynergyEventType.ANALYSIS_COMPLETE in handler.SUPPORTED_EVENTS

    def test_supports_drift_detected(self, handler):
        """Handler supports DRIFT_DETECTED event."""
        assert SynergyEventType.DRIFT_DETECTED in handler.SUPPORTED_EVENTS

    @pytest.mark.asyncio
    async def test_skips_unsupported_events(self, handler):
        """Handler skips events it doesn't support."""
        event = SynergyEvent(
            source_jewel=Jewel.BRAIN,
            target_jewel=Jewel.GESTALT,
            event_type=SynergyEventType.CRYSTAL_FORMED,
            source_id="test",
        )

        result = await handler.handle(event)
        # Skip returns success=True with skipped flag in metadata
        assert result.metadata.get("skipped") is True
        assert "not handling" in result.message.lower()


class TestDriftContentCreation:
    """Tests for drift content creation."""

    @pytest.fixture
    def handler(self):
        """Create handler for testing content creation."""
        return GestaltToBrainHandler(auto_capture=False)

    def test_drift_content_includes_modules(self, handler):
        """Drift content includes source and target modules."""
        content = handler._create_drift_content(
            source_module="agents.foo",
            target_module="protocols.bar",
            rule="no_upward_deps",
            severity="error",
            root_path="/project",
            message="Test violation",
            timestamp=datetime.now(),
        )
        assert "agents.foo" in content
        assert "protocols.bar" in content

    def test_drift_content_includes_severity_emoji(self, handler):
        """Drift content has severity emoji."""
        content_error = handler._create_drift_content(
            source_module="foo",
            target_module="bar",
            rule="test",
            severity="error",
            root_path="/",
            message="",
            timestamp=datetime.now(),
        )
        content_warning = handler._create_drift_content(
            source_module="foo",
            target_module="bar",
            rule="test",
            severity="warning",
            root_path="/",
            message="",
            timestamp=datetime.now(),
        )
        assert "🔴" in content_error
        assert "🟡" in content_warning

    def test_drift_content_includes_rule(self, handler):
        """Drift content includes the violated rule."""
        content = handler._create_drift_content(
            source_module="foo",
            target_module="bar",
            rule="no_circular_deps",
            severity="error",
            root_path="/",
            message="",
            timestamp=datetime.now(),
        )
        assert "no_circular_deps" in content


@pytest.mark.asyncio
class TestDriftHandling:
    """Tests for drift event handling."""

    @pytest.fixture
    def handler(self):
        """Create handler in dry-run mode."""
        return GestaltToBrainHandler(auto_capture=False)

    async def test_handles_drift_event_dry_run(self, handler):
        """Handler processes drift event in dry-run mode."""
        event = create_drift_detected_event(
            source_id="drift-001",
            source_module="agents.m.cartographer",
            target_module="protocols.agentese",
            rule="no_upward_deps",
            severity="error",
            root_path="/project",
        )
        result = await handler.handle(event)
        assert result.success is True
        assert "dry run" in result.message.lower()

    async def test_drift_result_metadata(self, handler):
        """Drift result contains expected metadata."""
        event = create_drift_detected_event(
            source_id="drift-001",
            source_module="foo.bar",
            target_module="baz.qux",
            rule="test_rule",
            severity="warning",
            root_path="/test",
        )
        result = await handler.handle(event)
        assert result.metadata["source_module"] == "foo.bar"
        assert result.metadata["target_module"] == "baz.qux"
        assert result.metadata["rule"] == "test_rule"
        assert result.metadata["severity"] == "warning"

    async def test_analysis_complete_still_works(self, handler):
        """Handler still handles ANALYSIS_COMPLETE correctly."""
        event = create_analysis_complete_event(
            source_id="analysis-001",
            module_count=100,
            health_grade="A",
            average_health=0.9,
            drift_count=5,
            root_path="/project",
        )
        result = await handler.handle(event)
        assert result.success is True
        assert result.metadata["module_count"] == 100


# =============================================================================
# Integration Tests
# =============================================================================


class TestDriftEventIntegration:
    """Integration tests for drift events."""

    def test_event_serialization(self):
        """Drift event serializes and deserializes correctly."""
        event = create_drift_detected_event(
            source_id="drift-001",
            source_module="agents.m.cartographer",
            target_module="protocols.agentese",
            rule="no_upward_deps",
            severity="error",
            root_path="/project",
        )
        # Serialize
        data = event.to_dict()
        assert data["event_type"] == "drift_detected"
        assert data["source_jewel"] == "gestalt"
        assert data["target_jewel"] == "brain"

        # Deserialize
        restored = SynergyEvent.from_dict(data)
        assert restored.event_type == SynergyEventType.DRIFT_DETECTED
        assert restored.payload["source_module"] == "agents.m.cartographer"

    def test_multiple_severities(self):
        """Can create events with different severities."""
        for severity in ["error", "warning", "info"]:
            event = create_drift_detected_event(
                source_id=f"drift-{severity}",
                source_module="foo",
                target_module="bar",
                rule="test",
                severity=severity,
                root_path="/",
            )
            assert event.payload["severity"] == severity
