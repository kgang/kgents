"""
Tests for Coalition Bridge: Gardener ↔ Coalition Forge integration.

Wave 2: Extensions - Testing the cross-jewel orchestration.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from protocols.gardener_logos import (
    CoalitionSpawnResult,
    GardenSeason,
    GardenState,
    TendingVerb,
    create_garden,
    graft_coalition,
    record_coalition_completion,
)
from protocols.gardener_logos.coalition_bridge import (
    GardenerCoalitionIntegration,
    _estimate_credits_for_template,
    _suggest_archetypes_for_template,
)


@pytest.fixture
def garden() -> GardenState:
    """Create a test garden."""
    g = create_garden(name="test-garden")
    g.session_id = "session-123"
    return g


class TestGraftCoalition:
    """Tests for graft_coalition gesture builder."""

    def test_creates_graft_gesture(self):
        """Creates a GRAFT gesture for coalition spawning."""
        gesture = graft_coalition(
            task_template="research_report",
            task_description="Research competitors in the market",
            reasoning="Need competitive analysis",
        )

        assert gesture.verb == TendingVerb.GRAFT
        assert gesture.target == "world.coalition.form:research_report"
        # When reasoning is provided, it uses that; otherwise uses description
        assert (
            "competitive analysis" in gesture.reasoning
            or "Research competitors" in gesture.reasoning
        )

    def test_includes_session_id(self):
        """Gesture includes garden session ID."""
        gesture = graft_coalition(
            task_template="code_review",
            task_description="Review PR #123",
            garden_session_id="garden-xyz",
        )

        assert gesture.session_id == "garden-xyz"

    def test_higher_entropy_cost(self):
        """Coalition graft has higher entropy cost than base."""
        gesture = graft_coalition(
            task_template="research_report",
            task_description="Test",
        )

        # Coalition graft should cost more than base graft
        assert gesture.entropy_cost > TendingVerb.GRAFT.base_entropy_cost

    def test_tone_controls_definitiveness(self):
        """Tone parameter controls gesture definitiveness."""
        tentative = graft_coalition(
            task_template="research_report",
            task_description="Maybe research",
            tone=0.3,
        )
        definitive = graft_coalition(
            task_template="research_report",
            task_description="Definitely research",
            tone=0.9,
        )

        assert tentative.tone == 0.3
        assert definitive.tone == 0.9


class TestRecordCoalitionCompletion:
    """Tests for record_coalition_completion."""

    @pytest.mark.asyncio
    async def test_creates_observe_gesture(self, garden: GardenState):
        """Records completion as OBSERVE gesture."""
        initial_gesture_count = len(garden.recent_gestures)

        gesture = await record_coalition_completion(
            garden=garden,
            task_id="task-abc",
            coalition_id="coal-xyz",
            output_summary="Found 5 competitors",
            credits_spent=50,
            handoffs=3,
            success=True,
        )

        assert gesture.verb == TendingVerb.OBSERVE
        assert "coal-xyz" in gesture.target
        assert len(garden.recent_gestures) == initial_gesture_count + 1

    @pytest.mark.asyncio
    async def test_success_affects_tone(self, garden: GardenState):
        """Successful completions have higher tone."""
        success_gesture = await record_coalition_completion(
            garden=garden,
            task_id="task-1",
            coalition_id="coal-1",
            output_summary="Success",
            credits_spent=50,
            success=True,
        )

        failure_gesture = await record_coalition_completion(
            garden=garden,
            task_id="task-2",
            coalition_id="coal-2",
            output_summary="Failed",
            credits_spent=0,
            success=False,
        )

        assert success_gesture.tone > failure_gesture.tone


class TestArchetypeSuggestions:
    """Tests for archetype suggestion logic."""

    def test_research_report_archetypes(self):
        """Research reports get Scout, Sage, Scribe."""
        archetypes = _suggest_archetypes_for_template("research_report")
        assert "Scout" in archetypes
        assert "Sage" in archetypes
        assert "Scribe" in archetypes

    def test_code_review_archetypes(self):
        """Code reviews get Steady, Sync, Scout."""
        archetypes = _suggest_archetypes_for_template("code_review")
        assert "Steady" in archetypes
        assert "Sync" in archetypes

    def test_unknown_template_fallback(self):
        """Unknown templates get sensible fallback."""
        archetypes = _suggest_archetypes_for_template("unknown_task")
        assert len(archetypes) >= 2


class TestCreditEstimation:
    """Tests for credit estimation logic."""

    def test_research_report_credits(self):
        """Research reports cost ~50 credits."""
        credits = _estimate_credits_for_template("research_report")
        assert credits == 50

    def test_competitive_intel_most_expensive(self):
        """Competitive intel is most expensive."""
        intel = _estimate_credits_for_template("competitive_intel")
        review = _estimate_credits_for_template("code_review")
        assert intel > review

    def test_unknown_template_fallback(self):
        """Unknown templates get fallback cost."""
        credits = _estimate_credits_for_template("unknown")
        assert credits > 0


class TestGardenerCoalitionIntegration:
    """Tests for the full integration helper."""

    def test_initialization(self, garden: GardenState):
        """Integration initializes with garden."""
        integration = GardenerCoalitionIntegration(garden)
        assert integration.active_count == 0

    @pytest.mark.asyncio
    async def test_spawn_and_track(self, garden: GardenState):
        """Can spawn and track a coalition."""
        integration = GardenerCoalitionIntegration(garden)

        result = await integration.spawn_and_track(
            task_template="research_report",
            task_description="Analyze market trends",
            reasoning="Quarterly review",
        )

        assert isinstance(result, CoalitionSpawnResult)
        # Note: actual spawning may fail without full infrastructure
        # but the result should always be returned

    @pytest.mark.asyncio
    async def test_record_completion_removes_from_active(self, garden: GardenState):
        """Recording completion removes coalition from active tracking."""
        integration = GardenerCoalitionIntegration(garden)

        # Manually add to active (simulating spawn)
        integration._active_coalitions["test-coal"] = {
            "task_template": "test",
            "spawned_at": datetime.now(),
        }
        assert integration.active_count == 1

        await integration.record_completion(
            coalition_id="test-coal",
            task_id="task-123",
            output_summary="Complete",
            credits_spent=25,
        )

        assert integration.active_count == 0


class TestGestureRecording:
    """Tests for gesture recording in garden."""

    @pytest.mark.asyncio
    async def test_completion_adds_to_momentum(self, garden: GardenState):
        """Coalition completion adds gesture to garden momentum."""
        initial_count = len(garden.recent_gestures)

        await record_coalition_completion(
            garden=garden,
            task_id="task-xyz",
            coalition_id="coal-abc",
            output_summary="Test summary",
            credits_spent=30,
        )

        assert len(garden.recent_gestures) > initial_count

    def test_graft_gesture_target_format(self):
        """Graft gesture target has correct format."""
        gesture = graft_coalition(
            task_template="content_creation",
            task_description="Write blog post",
        )

        assert gesture.target.startswith("world.coalition.form:")
        assert "content_creation" in gesture.target
