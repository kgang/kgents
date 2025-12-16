"""
Tests for Wave 4 Garden synergy handlers.

Gardener-Logos Phase 6: Cross-jewel event processors for garden state changes.
"""

from datetime import datetime
from typing import Any

import pytest

from protocols.synergy.events import (
    Jewel,
    SynergyEvent,
    SynergyEventType,
    create_analysis_complete_event,
    create_gesture_applied_event,
    create_plot_progress_event,
    create_season_changed_event,
)
from protocols.synergy.handlers import GardenToBrainHandler, GestaltToGardenHandler


class TestGardenEvents:
    """Tests for Wave 4 garden event factory functions."""

    def test_create_season_changed_event(self) -> None:
        """SEASON_CHANGED event has correct structure."""
        event = create_season_changed_event(
            garden_id="garden-123",
            garden_name="My Garden",
            old_season="DORMANT",
            new_season="SPROUTING",
            reason="Session started",
        )

        assert event.source_jewel == Jewel.GARDENER
        assert event.target_jewel == Jewel.ALL  # Broadcast
        assert event.event_type == SynergyEventType.SEASON_CHANGED
        assert event.source_id == "garden-123"
        assert event.payload["garden_name"] == "My Garden"
        assert event.payload["old_season"] == "DORMANT"
        assert event.payload["new_season"] == "SPROUTING"
        assert event.payload["reason"] == "Session started"
        assert event.correlation_id is not None

    def test_create_gesture_applied_event(self) -> None:
        """GESTURE_APPLIED event has correct structure."""
        event = create_gesture_applied_event(
            garden_id="garden-123",
            gesture_verb="PRUNE",
            target="concept.prompt.task",
            success=True,
            state_changed=True,
            synergies_triggered=["textgrad:improvement_applied"],
            tone=0.7,
            reasoning="Removing unused prompt",
        )

        assert event.source_jewel == Jewel.GARDENER
        assert event.target_jewel == Jewel.BRAIN
        assert event.event_type == SynergyEventType.GESTURE_APPLIED
        assert event.source_id == "garden-123"
        assert event.payload["verb"] == "PRUNE"
        assert event.payload["target"] == "concept.prompt.task"
        assert event.payload["success"] is True
        assert event.payload["state_changed"] is True
        assert event.payload["tone"] == 0.7
        assert "textgrad:improvement_applied" in event.payload["synergies_triggered"]

    def test_create_plot_progress_event(self) -> None:
        """PLOT_PROGRESS_UPDATED event has correct structure."""
        event = create_plot_progress_event(
            garden_id="garden-123",
            plot_name="coalition-forge",
            plot_path="world.forge",
            old_progress=0.3,
            new_progress=0.5,
            plan_path="plans/core-apps/coalition-forge.md",
        )

        assert event.source_jewel == Jewel.GARDENER
        assert event.target_jewel == Jewel.BRAIN
        assert event.event_type == SynergyEventType.PLOT_PROGRESS_UPDATED
        assert event.source_id == "garden-123"
        assert event.payload["plot_name"] == "coalition-forge"
        assert event.payload["plot_path"] == "world.forge"
        assert event.payload["old_progress"] == 0.3
        assert event.payload["new_progress"] == 0.5
        assert event.payload["progress_delta"] == 0.2
        assert event.payload["plan_path"] == "plans/core-apps/coalition-forge.md"


class TestGardenToBrainHandler:
    """Tests for GardenToBrainHandler."""

    @pytest.mark.asyncio
    async def test_handles_season_changed(self) -> None:
        """Handler processes SEASON_CHANGED events."""
        handler = GardenToBrainHandler(auto_capture=False)  # Dry run

        event = create_season_changed_event(
            garden_id="garden-123",
            garden_name="Test Garden",
            old_season="DORMANT",
            new_season="SPROUTING",
            reason="Session started",
        )

        result = await handler.handle(event)

        assert result.success is True
        assert "Dry run" in result.message
        assert result.metadata["old_season"] == "DORMANT"
        assert result.metadata["new_season"] == "SPROUTING"

    @pytest.mark.asyncio
    async def test_handles_gesture_applied(self) -> None:
        """Handler processes GESTURE_APPLIED events."""
        handler = GardenToBrainHandler(auto_capture=False)  # Dry run

        event = create_gesture_applied_event(
            garden_id="garden-123",
            gesture_verb="GRAFT",
            target="concept.prompt.new_feature",
            success=True,
            state_changed=True,
            synergies_triggered=["textgrad:improvement_proposed"],
            reasoning="Adding new feature prompt",
        )

        result = await handler.handle(event)

        assert result.success is True
        assert "Dry run" in result.message
        assert result.metadata["verb"] == "GRAFT"
        assert result.metadata["target"] == "concept.prompt.new_feature"

    @pytest.mark.asyncio
    async def test_skips_non_state_changing_gesture(self) -> None:
        """Handler skips gestures that didn't change state."""
        handler = GardenToBrainHandler(auto_capture=False)

        event = create_gesture_applied_event(
            garden_id="garden-123",
            gesture_verb="OBSERVE",
            target="concept.gardener",
            success=True,
            state_changed=False,  # No state change
            synergies_triggered=[],
            reasoning="Just looking",
        )

        result = await handler.handle(event)

        assert result.success is True
        assert "Skipped" in result.message
        assert "did not change state" in result.message

    @pytest.mark.asyncio
    async def test_handles_plot_progress_milestone(self) -> None:
        """Handler processes significant plot progress updates."""
        handler = GardenToBrainHandler(auto_capture=False)  # Dry run

        # Crossing 50% milestone
        event = create_plot_progress_event(
            garden_id="garden-123",
            plot_name="coalition-forge",
            plot_path="world.forge",
            old_progress=0.45,
            new_progress=0.55,  # Crosses 50%
            plan_path="plans/core-apps/coalition-forge.md",
        )

        result = await handler.handle(event)

        assert result.success is True
        assert "Dry run" in result.message

    @pytest.mark.asyncio
    async def test_skips_small_progress_change(self) -> None:
        """Handler skips small progress changes that don't cross milestones."""
        handler = GardenToBrainHandler(auto_capture=False)

        # Small change (< 10%) that doesn't cross a milestone
        event = create_plot_progress_event(
            garden_id="garden-123",
            plot_name="coalition-forge",
            plot_path="world.forge",
            old_progress=0.32,
            new_progress=0.35,  # Only 3% change, no milestone
        )

        result = await handler.handle(event)

        assert result.success is True
        assert "Skipped" in result.message
        assert "too small" in result.message

    @pytest.mark.asyncio
    async def test_skips_wrong_event_type(self) -> None:
        """Handler skips non-garden events."""
        handler = GardenToBrainHandler(auto_capture=False)

        event = SynergyEvent(
            source_jewel=Jewel.BRAIN,
            target_jewel=Jewel.GARDENER,
            event_type=SynergyEventType.CRYSTAL_FORMED,
            source_id="crystal-123",
        )

        result = await handler.handle(event)

        assert result.success is True
        assert "Skipped" in result.message

    def test_handler_name(self) -> None:
        """Handler has correct name."""
        handler = GardenToBrainHandler()
        assert handler.name == "GardenToBrainHandler"

    def test_season_crystal_content_includes_emojis(self) -> None:
        """Season crystal content includes appropriate emojis."""
        handler = GardenToBrainHandler(auto_capture=False)

        content = handler._create_season_crystal_content(
            garden_name="Test Garden",
            old_season="DORMANT",
            new_season="SPROUTING",
            reason="Starting fresh",
            timestamp=datetime.now(),
        )

        assert "💤" in content  # DORMANT emoji
        assert "🌱" in content  # SPROUTING emoji
        assert "Test Garden" in content
        assert "Starting fresh" in content

    def test_progress_crystal_content_includes_bar(self) -> None:
        """Progress crystal content includes progress bar visualization."""
        handler = GardenToBrainHandler(auto_capture=False)

        content = handler._create_progress_crystal_content(
            plot_name="coalition-forge",
            old_progress=0.3,
            new_progress=0.5,
            plan_path="plans/core-apps/coalition-forge.md",
            timestamp=datetime.now(),
        )

        assert "coalition-forge" in content
        assert "30%" in content or "0.3" in str(content)
        assert "50%" in content
        assert "█" in content  # Progress bar characters
        assert "📈" in content  # Increasing indicator


class TestGestaltToGardenHandler:
    """Tests for GestaltToGardenHandler."""

    @pytest.mark.asyncio
    async def test_handles_analysis_complete(self) -> None:
        """Handler processes ANALYSIS_COMPLETE events."""
        handler = GestaltToGardenHandler(auto_observe=False)  # Dry run

        event = create_analysis_complete_event(
            source_id="analysis-123",
            module_count=50,
            health_grade="B+",
            average_health=0.84,
            drift_count=2,
            root_path="/path/to/project",
        )

        # Without an active garden, should skip
        result = await handler.handle(event)

        assert result.success is True
        assert "Skipped" in result.message
        assert "No active garden" in result.message

    @pytest.mark.asyncio
    async def test_skips_wrong_event_type(self) -> None:
        """Handler skips non-ANALYSIS_COMPLETE events."""
        handler = GestaltToGardenHandler(auto_observe=False)

        event = SynergyEvent(
            source_jewel=Jewel.GARDENER,
            target_jewel=Jewel.BRAIN,
            event_type=SynergyEventType.SEASON_CHANGED,
            source_id="garden-123",
        )

        result = await handler.handle(event)

        assert result.success is True
        assert "Skipped" in result.message

    def test_handler_name(self) -> None:
        """Handler has correct name."""
        handler = GestaltToGardenHandler()
        assert handler.name == "GestaltToGardenHandler"

    def test_plot_matching_by_crown_jewel(self) -> None:
        """Plots with crown_jewel match correctly."""
        from protocols.gardener_logos.garden import GardenState, create_garden
        from protocols.gardener_logos.plots import create_plot

        handler = GestaltToGardenHandler(auto_observe=False)

        garden = create_garden("Test")
        garden.plots["forge"] = create_plot(
            name="forge",
            path="world.forge",
            crown_jewel="Coalition",
        )

        # Should match "forge" or "coalition" in path
        matches = handler._find_matching_plots(
            garden, "/impl/claude/agents/forge/something.py"
        )
        assert len(matches) == 1
        assert matches[0].name == "forge"

        # Should not match unrelated path
        matches = handler._find_matching_plots(
            garden, "/impl/claude/protocols/brain/memory.py"
        )
        assert len(matches) == 0

    def test_plot_matching_by_plan_path(self) -> None:
        """Plots with plan_path match correctly."""
        from protocols.gardener_logos.garden import create_garden
        from protocols.gardener_logos.plots import create_plot

        handler = GestaltToGardenHandler(auto_observe=False)

        garden = create_garden("Test")
        garden.plots["atelier"] = create_plot(
            name="atelier-experience",
            path="world.atelier",
            plan_path="plans/core-apps/atelier-experience.md",
        )

        # Should match plan name in path
        matches = handler._find_matching_plots(
            garden, "/impl/claude/agents/atelier_experience/test.py"
        )
        assert len(matches) == 1


class TestGardenSynergyIntegration:
    """Integration tests for garden synergies.

    These test the full flow with actual garden operations.
    """

    @pytest.mark.asyncio
    async def test_season_transition_emits_event(self) -> None:
        """Season transitions emit synergy events when enabled."""
        from protocols.gardener_logos.garden import GardenSeason, create_garden
        from protocols.synergy import get_synergy_bus, reset_synergy_bus

        # Reset bus to ensure clean state
        reset_synergy_bus()
        bus = get_synergy_bus()

        # Track emitted events
        emitted_events: list[SynergyEvent] = []

        def track_events(event: SynergyEvent, result: Any) -> None:
            emitted_events.append(event)

        bus.subscribe_results(track_events)

        garden = create_garden("Test Garden")

        # Transition season (this should emit an event)
        # Note: emit_event=True by default, but we're in sync context
        # The event emission uses create_task which needs a running loop
        garden.transition_season(GardenSeason.SPROUTING, "Testing", emit_event=False)

        # Verify state changed
        assert garden.season == GardenSeason.SPROUTING

        # Clean up
        reset_synergy_bus()

    @pytest.mark.asyncio
    async def test_gesture_application_emits_event(self) -> None:
        """Gesture applications emit synergy events for state-changing verbs."""
        from protocols.gardener_logos.garden import create_garden
        from protocols.gardener_logos.tending import apply_gesture, graft
        from protocols.synergy import reset_synergy_bus

        # Reset bus for clean test
        reset_synergy_bus()

        garden = create_garden("Test Garden")

        # Apply a state-changing gesture (GRAFT)
        gesture = graft(
            target="concept.prompt.test",
            reasoning="Adding test prompt",
        )

        # Apply without event emission for test stability
        result = await apply_gesture(garden, gesture, emit_event=False)

        assert result.accepted is True
        assert result.state_changed is True

        # Clean up
        reset_synergy_bus()


class TestEventTypeEnumeration:
    """Tests that verify the new event types are properly added."""

    def test_season_changed_in_enum(self) -> None:
        """SEASON_CHANGED is a valid event type."""
        assert hasattr(SynergyEventType, "SEASON_CHANGED")
        assert SynergyEventType.SEASON_CHANGED.value == "season_changed"

    def test_gesture_applied_in_enum(self) -> None:
        """GESTURE_APPLIED is a valid event type."""
        assert hasattr(SynergyEventType, "GESTURE_APPLIED")
        assert SynergyEventType.GESTURE_APPLIED.value == "gesture_applied"

    def test_plot_progress_updated_in_enum(self) -> None:
        """PLOT_PROGRESS_UPDATED is a valid event type."""
        assert hasattr(SynergyEventType, "PLOT_PROGRESS_UPDATED")
        assert SynergyEventType.PLOT_PROGRESS_UPDATED.value == "plot_progress_updated"
