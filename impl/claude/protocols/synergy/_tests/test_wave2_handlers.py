"""
Tests for Wave 2 synergy handlers: Coalition integration.

Wave 2 of the Enlightened Crown strategy adds:
- CoalitionToBrainHandler: Captures Coalition task results to Brain
- BrainToCoalitionHandler: Enriches Coalition with Brain context

Note: Atelier handlers removed 2025-12-21.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from protocols.synergy import (
    SynergyEventType,
    create_coalition_formed_event,
    create_task_complete_event,
    get_synergy_bus,
    reset_synergy_bus,
)
from protocols.synergy.handlers import (
    BrainToCoalitionHandler,
    CoalitionToBrainHandler,
)


@pytest.fixture(autouse=True)
def clean_bus():
    """Reset synergy bus before each test."""
    reset_synergy_bus()
    yield
    reset_synergy_bus()


# =============================================================================
# Coalition → Brain Handler Tests
# =============================================================================


class TestCoalitionToBrainHandler:
    """Tests for CoalitionToBrainHandler."""

    def test_handler_name(self):
        """Handler has correct name."""
        handler = CoalitionToBrainHandler(auto_capture=False)
        assert handler.name == "CoalitionToBrainHandler"

    @pytest.mark.asyncio
    async def test_skips_non_task_events(self):
        """Handler skips events that aren't TASK_ASSIGNED."""
        handler = CoalitionToBrainHandler(auto_capture=False)

        event = create_coalition_formed_event(
            coalition_id="coal-123",
            task_template="research",
            archetypes=["Scout", "Sage"],
            eigenvector_compatibility=0.9,
            estimated_credits=50,
        )

        result = await handler.handle(event)
        assert result.success is True
        assert "skipped" in result.message.lower()

    @pytest.mark.asyncio
    async def test_skips_incomplete_tasks(self):
        """Handler skips tasks that aren't marked completed."""
        handler = CoalitionToBrainHandler(auto_capture=False)

        # Create event without completed flag
        event = create_task_complete_event(
            task_id="task-123",
            coalition_id="coal-456",
            task_template="research_report",
            output_format="MARKDOWN",
            output_summary="Research summary",
            credits_spent=50,
            handoffs=3,
            duration_seconds=120.5,
        )
        # Override to mark as incomplete
        event.payload["completed"] = False

        result = await handler.handle(event)
        assert result.success is True
        assert "not yet completed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_dry_run_creates_content(self):
        """Dry run mode creates content without capturing."""
        handler = CoalitionToBrainHandler(auto_capture=False)

        event = create_task_complete_event(
            task_id="task-abc",
            coalition_id="coal-xyz",
            task_template="research_report",
            output_format="MARKDOWN",
            output_summary="Analysis of competitor landscape...",
            credits_spent=75,
            handoffs=4,
            duration_seconds=180.0,
        )

        result = await handler.handle(event)

        assert result.success is True
        assert "dry run" in result.message.lower()
        assert result.metadata["task_template"] == "research_report"
        assert result.metadata["credits_spent"] == 75

    @pytest.mark.asyncio
    async def test_crystal_content_format(self):
        """Crystal content includes all task details."""
        handler = CoalitionToBrainHandler(auto_capture=False)

        content = handler._create_crystal_content(
            task_id="task-123",
            coalition_id="coal-456",
            task_template="competitive_intel",
            output_format="BRIEFING",
            output_summary="Found 5 key competitors with varying strengths...",
            credits_spent=100,
            handoffs=5,
            duration_seconds=300.0,
            timestamp=datetime.now(),
        )

        assert "Coalition Task: competitive_intel" in content
        assert "Credits Spent: 100" in content
        assert "Handoffs: 5" in content
        assert "Duration: 5.0m" in content
        assert "Found 5 key competitors" in content


# =============================================================================
# Brain → Coalition Handler Tests
# =============================================================================


class TestBrainToCoalitionHandler:
    """Tests for BrainToCoalitionHandler."""

    def test_handler_name(self):
        """Handler has correct name."""
        handler = BrainToCoalitionHandler()
        assert handler.name == "BrainToCoalitionHandler"

    @pytest.mark.asyncio
    async def test_skips_non_coalition_events(self):
        """Handler skips events that aren't COALITION_FORMED."""
        handler = BrainToCoalitionHandler()

        event = create_task_complete_event(
            task_id="task-123",
            coalition_id="coal-456",
            task_template="research_report",
            output_format="MARKDOWN",
            output_summary="Test",
            credits_spent=50,
            handoffs=3,
            duration_seconds=120.5,
        )

        result = await handler.handle(event)
        assert result.success is True
        assert "skipped" in result.message.lower()

    @pytest.mark.asyncio
    async def test_skips_empty_task_template(self):
        """Handler skips events without task template."""
        handler = BrainToCoalitionHandler()

        event = create_coalition_formed_event(
            coalition_id="coal-123",
            task_template="",  # Empty
            archetypes=["Scout"],
            eigenvector_compatibility=0.9,
            estimated_credits=50,
        )

        result = await handler.handle(event)
        assert result.success is True
        assert "no task template" in result.message.lower()


# =============================================================================
# Event Factory Tests
# =============================================================================


class TestWave2EventFactories:
    """Tests for Wave 2 event factory functions."""

    def test_coalition_formed_event(self):
        """create_coalition_formed_event creates valid event."""
        event = create_coalition_formed_event(
            coalition_id="coal-123",
            task_template="research_report",
            archetypes=["Scout", "Sage", "Scribe"],
            eigenvector_compatibility=0.87,
            estimated_credits=50,
        )

        assert event.event_type == SynergyEventType.COALITION_FORMED
        assert event.source_id == "coal-123"
        assert event.payload["archetypes"] == ["Scout", "Sage", "Scribe"]
        assert event.payload["eigenvector_compatibility"] == 0.87

    def test_task_complete_event(self):
        """create_task_complete_event creates valid event."""
        event = create_task_complete_event(
            task_id="task-123",
            coalition_id="coal-456",
            task_template="code_review",
            output_format="PR_COMMENTS",
            output_summary="Found 3 issues, 2 suggestions",
            credits_spent=30,
            handoffs=2,
            duration_seconds=90.5,
        )

        assert event.event_type == SynergyEventType.TASK_ASSIGNED
        assert event.source_id == "task-123"
        assert event.payload["completed"] is True
        assert event.payload["credits_spent"] == 30


# =============================================================================
# Bus Registration Tests
# =============================================================================


class TestWave2BusRegistration:
    """Tests for Wave 2 handler registration on the bus."""

    def test_handlers_registered_on_bus_init(self):
        """Wave 2 handlers are registered when bus initializes."""
        bus = get_synergy_bus()

        # Check Coalition handlers registered
        task_handlers = bus._handlers.get(SynergyEventType.TASK_ASSIGNED, [])
        assert len(task_handlers) >= 1
        assert any(h.name == "CoalitionToBrainHandler" for h in task_handlers)

        coalition_handlers = bus._handlers.get(SynergyEventType.COALITION_FORMED, [])
        assert len(coalition_handlers) >= 1
        assert any(h.name == "BrainToCoalitionHandler" for h in coalition_handlers)

    @pytest.mark.asyncio
    async def test_emit_triggers_handler(self):
        """Emitting event triggers the registered handler."""
        bus = get_synergy_bus()
        results: list[Any] = []

        def on_result(event, result):
            results.append(result)

        bus.subscribe_results(on_result)

        event = create_coalition_formed_event(
            coalition_id="coal-test",
            task_template="research",
            archetypes=["Scout"],
            eigenvector_compatibility=0.9,
            estimated_credits=50,
        )

        await bus.emit_and_wait(event)

        # Should have at least one result from BrainToCoalitionHandler
        assert len(results) >= 1
        assert any(r.handler_name == "BrainToCoalitionHandler" for r in results)
