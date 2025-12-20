"""
Tests for synergy handlers.

Foundation 4 - Wave 0: Cross-jewel event processors.
"""

import pytest

from protocols.synergy.events import (
    Jewel,
    SynergyEvent,
    SynergyEventType,
    SynergyResult,
    create_analysis_complete_event,
)
from protocols.synergy.handlers import GestaltToBrainHandler
from protocols.synergy.handlers.base import BaseSynergyHandler


class TestBaseSynergyHandler:
    """Tests for BaseSynergyHandler helper methods."""

    def test_success_result(self) -> None:
        """success() creates a success result."""

        class TestHandler(BaseSynergyHandler):
            @property
            def name(self) -> str:
                return "TestHandler"

            async def handle(self, event: SynergyEvent) -> SynergyResult:
                return self.success("OK")

        handler = TestHandler()
        result = handler.success("OK", artifact_id="123")

        assert result.success is True
        assert result.handler_name == "TestHandler"
        assert result.message == "OK"
        assert result.artifact_id == "123"

    def test_failure_result(self) -> None:
        """failure() creates a failure result."""

        class TestHandler(BaseSynergyHandler):
            @property
            def name(self) -> str:
                return "TestHandler"

            async def handle(self, event: SynergyEvent) -> SynergyResult:
                return self.failure("Error")

        handler = TestHandler()
        result = handler.failure("Something went wrong")

        assert result.success is False
        assert result.handler_name == "TestHandler"
        assert result.message == "Something went wrong"

    def test_skip_result(self) -> None:
        """skip() creates a skipped result."""

        class TestHandler(BaseSynergyHandler):
            @property
            def name(self) -> str:
                return "TestHandler"

            async def handle(self, event: SynergyEvent) -> SynergyResult:
                return self.skip("N/A")

        handler = TestHandler()
        result = handler.skip("Not applicable")

        assert result.success is True
        assert "Skipped" in result.message
        assert result.metadata.get("skipped") is True


class TestGestaltToBrainHandler:
    """Tests for GestaltToBrainHandler."""

    @pytest.mark.asyncio
    async def test_handles_analysis_complete(self) -> None:
        """Handler processes ANALYSIS_COMPLETE events."""
        handler = GestaltToBrainHandler(auto_capture=False)  # Dry run

        event = create_analysis_complete_event(
            source_id="analysis-123",
            module_count=50,
            health_grade="B+",
            average_health=0.84,
            drift_count=2,
            root_path="/path/to/project",
        )

        result = await handler.handle(event)

        assert result.success is True
        assert "Dry run" in result.message
        assert result.metadata["module_count"] == 50
        assert result.metadata["health_grade"] == "B+"

    @pytest.mark.asyncio
    async def test_skips_wrong_event_type(self) -> None:
        """Handler skips non-ANALYSIS_COMPLETE events."""
        handler = GestaltToBrainHandler(auto_capture=False)

        event = SynergyEvent(
            source_jewel=Jewel.BRAIN,
            target_jewel=Jewel.GARDENER,
            event_type=SynergyEventType.CRYSTAL_FORMED,
            source_id="crystal-123",
        )

        result = await handler.handle(event)

        assert result.success is True
        assert "Skipped" in result.message

    @pytest.mark.asyncio
    async def test_crystal_content_includes_metrics(self) -> None:
        """Crystal content includes all analysis metrics."""
        handler = GestaltToBrainHandler(auto_capture=False)

        event = create_analysis_complete_event(
            source_id="analysis-123",
            module_count=50,
            health_grade="B+",
            average_health=0.84,
            drift_count=2,
            root_path="/path/to/impl-claude",
        )

        # Access private method for testing content generation
        from datetime import datetime

        content = handler._create_crystal_content(
            module_count=50,
            health_grade="B+",
            average_health=0.84,
            drift_count=2,
            root_path="/path/to/impl-claude",
            timestamp=datetime.now(),
        )

        assert "impl-claude" in content
        assert "50" in content  # module count
        assert "B+" in content
        assert "84%" in content
        assert "2" in content  # drift count

    def test_handler_name(self) -> None:
        """Handler has correct name."""
        handler = GestaltToBrainHandler()
        assert handler.name == "GestaltToBrainHandler"


class TestGestaltToBrainIntegration:
    """Integration tests for Gestalt to Brain synergy.

    These tests verify the actual Brain capture works.
    They're skipped if Brain logos isn't available.
    """

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="Integration test: requires Brain service infrastructure", run=False)
    async def test_actual_capture(self) -> None:
        """Handler actually captures to Brain when enabled."""
        handler = GestaltToBrainHandler(auto_capture=True)

        event = create_analysis_complete_event(
            source_id="test-integration",
            module_count=10,
            health_grade="A",
            average_health=0.95,
            drift_count=0,
            root_path="/test/path",
        )

        result = await handler.handle(event)

        # Should succeed and return a crystal ID
        assert result.success is True
        assert result.artifact_id is not None
        assert "gestalt-" in result.artifact_id
