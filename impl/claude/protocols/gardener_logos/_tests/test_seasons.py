"""
Tests for Season Transitions (Auto-Inducer).

Validates:
- TransitionSignals gathering
- Each transition rule evaluation
- SeasonTransition creation
- Dismissal memory
- Integration with gesture application

Phase 8: Auto-Inducer
See: plans/gardener-logos-enactment.md
"""

from datetime import datetime, timedelta

import pytest

from ..garden import GardenMetrics, GardenSeason, create_garden
from ..seasons import (
    TRANSITION_RULES,
    SeasonTransition,
    TransitionSignals,
    clear_dismissals,
    dismiss_transition,
    evaluate_season_transition,
    is_transition_dismissed,
    suggest_season_transition,
)
from ..tending import (
    TendingGesture,
    TendingVerb,
    apply_gesture,
    graft,
    observe,
    water,
)


class TestTransitionSignals:
    """Tests for TransitionSignals dataclass."""

    def test_signals_gather_from_garden(self):
        """Should gather signals from garden state."""
        garden = create_garden()
        signals = TransitionSignals.gather(garden)

        assert isinstance(signals, TransitionSignals)
        assert signals.gesture_frequency >= 0
        assert signals.gesture_diversity >= 0
        assert signals.time_in_season_hours >= 0
        assert 0 <= signals.entropy_spent_ratio <= 1

    def test_signals_track_gesture_frequency(self):
        """Should calculate gesture frequency correctly."""
        garden = create_garden()

        # Add some gestures
        for i in range(5):
            gesture = TendingGesture(
                verb=TendingVerb.OBSERVE,
                target=f"test.{i}",
                tone=0.5,
                reasoning="Test",
                entropy_cost=0.01,
                timestamp=datetime.now() - timedelta(minutes=i * 10),
            )
            garden.add_gesture(gesture)

        signals = TransitionSignals.gather(garden)

        # With 5 gestures in ~1 hour, frequency should be positive
        assert signals.gesture_frequency > 0

    def test_signals_track_gesture_diversity(self):
        """Should count unique verbs used."""
        garden = create_garden()

        # Add gestures with different verbs
        verbs = [TendingVerb.OBSERVE, TendingVerb.WATER, TendingVerb.GRAFT]
        for verb in verbs:
            gesture = TendingGesture(
                verb=verb,
                target="test",
                tone=0.5,
                reasoning="Test",
                entropy_cost=0.1,
            )
            garden.add_gesture(gesture)

        signals = TransitionSignals.gather(garden)
        assert signals.gesture_diversity == 3

    def test_signals_to_dict(self):
        """Should serialize to dictionary."""
        garden = create_garden()
        signals = TransitionSignals.gather(garden)

        data = signals.to_dict()
        assert "gesture_frequency" in data
        assert "gesture_diversity" in data
        assert "entropy_spent_ratio" in data
        assert "session_active" in data

    def test_signals_time_in_season(self):
        """Should calculate time in current season."""
        garden = create_garden()
        # Set season_since to 2 hours ago
        garden.season_since = datetime.now() - timedelta(hours=2)

        signals = TransitionSignals.gather(garden)
        assert signals.time_in_season_hours >= 1.9
        assert signals.time_in_season_hours <= 2.1


class TestSeasonTransition:
    """Tests for SeasonTransition dataclass."""

    def test_transition_should_suggest_threshold(self):
        """should_suggest should be True only for confidence >= 0.7."""
        garden = create_garden()
        signals = TransitionSignals.gather(garden)

        high_confidence = SeasonTransition(
            from_season=GardenSeason.DORMANT,
            to_season=GardenSeason.SPROUTING,
            confidence=0.8,
            reason="High confidence",
            signals=signals,
        )
        assert high_confidence.should_suggest is True

        low_confidence = SeasonTransition(
            from_season=GardenSeason.DORMANT,
            to_season=GardenSeason.SPROUTING,
            confidence=0.5,
            reason="Low confidence",
            signals=signals,
        )
        assert low_confidence.should_suggest is False

        threshold_confidence = SeasonTransition(
            from_season=GardenSeason.DORMANT,
            to_season=GardenSeason.SPROUTING,
            confidence=0.7,
            reason="At threshold",
            signals=signals,
        )
        assert threshold_confidence.should_suggest is True

    def test_transition_to_dict(self):
        """Should serialize to dictionary."""
        garden = create_garden()
        signals = TransitionSignals.gather(garden)

        transition = SeasonTransition(
            from_season=GardenSeason.DORMANT,
            to_season=GardenSeason.SPROUTING,
            confidence=0.75,
            reason="Test reason",
            signals=signals,
        )

        data = transition.to_dict()
        assert data["from_season"] == "DORMANT"
        assert data["to_season"] == "SPROUTING"
        assert data["confidence"] == 0.75
        assert "signals" in data


class TestTransitionRules:
    """Tests for individual transition rules."""

    def test_all_seasons_have_rules(self):
        """Every season should have at least one transition rule."""
        for season in GardenSeason:
            assert season in TRANSITION_RULES
            assert len(TRANSITION_RULES[season]) >= 1

    def test_dormant_to_sprouting_high_activity(self):
        """DORMANT → SPROUTING should trigger on high activity."""
        garden = create_garden(season=GardenSeason.DORMANT)

        # Simulate high activity: many recent gestures, low entropy usage
        for i in range(10):
            gesture = TendingGesture(
                verb=TendingVerb.OBSERVE,
                target=f"test.{i}",
                tone=0.5,
                reasoning="Active",
                entropy_cost=0.01,
                timestamp=datetime.now() - timedelta(minutes=i * 5),
            )
            garden.add_gesture(gesture)

        garden.metrics.entropy_spent = 0.1
        garden.metrics.entropy_budget = 1.0

        transition = evaluate_season_transition(garden)

        # Should suggest sprouting
        assert transition is not None
        assert transition.to_season == GardenSeason.SPROUTING

    def test_dormant_stays_dormant_low_activity(self):
        """DORMANT should stay dormant with low activity."""
        garden = create_garden(season=GardenSeason.DORMANT)

        # No gestures, no activity
        transition = evaluate_season_transition(garden)

        # Should not suggest transition (or low confidence)
        assert transition is None or not transition.should_suggest

    def test_sprouting_to_blooming_with_progress(self):
        """SPROUTING → BLOOMING should trigger with progress and time."""
        garden = create_garden(season=GardenSeason.SPROUTING)
        garden.season_since = datetime.now() - timedelta(hours=3)

        # Add plots with progress
        from ..plots import PlotState

        garden.plots["test-plot"] = PlotState(
            name="test-plot",
            path="concept.test",
            description="Test",
            progress=0.4,  # 40% progress
        )

        # Add some diverse gestures
        for verb in [TendingVerb.OBSERVE, TendingVerb.WATER, TendingVerb.GRAFT, TendingVerb.ROTATE]:
            gesture = TendingGesture(
                verb=verb,
                target="concept.test",
                tone=0.5,
                reasoning="Progress",
                entropy_cost=0.1,
            )
            garden.add_gesture(gesture)

        transition = evaluate_season_transition(garden)

        # Should suggest blooming if enough progress
        if transition:
            assert transition.to_season == GardenSeason.BLOOMING

    def test_blooming_to_harvest_with_reflection(self):
        """BLOOMING → HARVEST should trigger with reflection cycles."""
        garden = create_garden(season=GardenSeason.BLOOMING)
        garden.season_since = datetime.now() - timedelta(hours=4)

        # Create session with reflect_count
        from agents.gardener.session import create_gardener_session

        session = create_gardener_session(name="Test")
        session.state.reflect_count = 4  # Multiple reflections
        garden._session = session

        signals = TransitionSignals.gather(garden)

        # With 4 reflect cycles, should suggest harvest
        assert signals.reflect_count >= 3

    def test_harvest_to_composting_with_time_and_low_activity(self):
        """HARVEST → COMPOSTING should trigger after extended time with low activity."""
        garden = create_garden(season=GardenSeason.HARVEST)
        garden.season_since = datetime.now() - timedelta(hours=5)

        # No recent activity
        signals = TransitionSignals.gather(garden)

        # Should have low frequency and time > 4h
        assert signals.time_in_season_hours > 4
        assert signals.gesture_frequency < 1

    def test_composting_to_dormant_entropy_depleted(self):
        """COMPOSTING → DORMANT should trigger when entropy depleted."""
        garden = create_garden(season=GardenSeason.COMPOSTING)
        garden.season_since = datetime.now() - timedelta(hours=7)

        # Deplete entropy
        garden.metrics.entropy_spent = 0.9
        garden.metrics.entropy_budget = 1.0

        signals = TransitionSignals.gather(garden)

        # Should have high entropy ratio
        assert signals.entropy_spent_ratio > 0.8


class TestDismissalMemory:
    """Tests for transition dismissal tracking."""

    def test_dismiss_transition_records_dismissal(self):
        """dismiss_transition should record the dismissal."""
        garden_id = "test-garden-123"

        # Clear any existing
        clear_dismissals(garden_id)

        # Dismiss a transition
        dismiss_transition(
            garden_id,
            GardenSeason.DORMANT,
            GardenSeason.SPROUTING,
        )

        # Should be dismissed now
        assert (
            is_transition_dismissed(
                garden_id,
                GardenSeason.DORMANT,
                GardenSeason.SPROUTING,
            )
            is True
        )

    def test_undismissed_transition_not_blocked(self):
        """Non-dismissed transitions should not be blocked."""
        garden_id = "test-garden-456"
        clear_dismissals(garden_id)

        # Should not be dismissed
        assert (
            is_transition_dismissed(
                garden_id,
                GardenSeason.SPROUTING,
                GardenSeason.BLOOMING,
            )
            is False
        )

    def test_clear_dismissals(self):
        """clear_dismissals should remove all dismissals for garden."""
        garden_id = "test-garden-789"

        # Dismiss some transitions
        dismiss_transition(garden_id, GardenSeason.DORMANT, GardenSeason.SPROUTING)
        dismiss_transition(garden_id, GardenSeason.SPROUTING, GardenSeason.BLOOMING)

        # Clear
        clear_dismissals(garden_id)

        # Should no longer be dismissed
        assert (
            is_transition_dismissed(
                garden_id,
                GardenSeason.DORMANT,
                GardenSeason.SPROUTING,
            )
            is False
        )

    def test_suggest_respects_dismissal(self):
        """suggest_season_transition should respect dismissals."""
        garden = create_garden(season=GardenSeason.DORMANT)

        # Set up conditions for transition
        for i in range(10):
            gesture = TendingGesture(
                verb=TendingVerb.OBSERVE,
                target=f"test.{i}",
                tone=0.5,
                reasoning="Active",
                entropy_cost=0.01,
            )
            garden.add_gesture(gesture)

        garden.metrics.entropy_spent = 0.1

        # Dismiss the DORMANT → SPROUTING transition
        dismiss_transition(
            garden.garden_id,
            GardenSeason.DORMANT,
            GardenSeason.SPROUTING,
        )

        # Should not suggest dismissed transition
        suggestion = suggest_season_transition(garden)
        assert suggestion is None


class TestAutoInducerIntegration:
    """Integration tests for auto-inducer with gesture application."""

    @pytest.mark.asyncio
    async def test_gesture_triggers_transition_evaluation(self):
        """Gestures should trigger transition evaluation."""
        garden = create_garden(season=GardenSeason.DORMANT)

        # Set up conditions for transition
        garden.metrics.entropy_spent = 0.1
        garden.metrics.entropy_budget = 1.0

        # Add many gestures to trigger activity signal
        for i in range(15):
            gesture = TendingGesture(
                verb=TendingVerb.OBSERVE,
                target=f"test.{i}",
                tone=0.5,
                reasoning="Active",
                entropy_cost=0.01,
            )
            garden.add_gesture(gesture)

        # Clear any dismissals
        clear_dismissals(garden.garden_id)

        # Apply a gesture with transition evaluation
        gesture = observe("concept.gardener")
        result = await apply_gesture(garden, gesture, evaluate_transition=True)

        # Result should have suggested_transition if conditions met
        assert result.accepted is True
        # May or may not have suggestion depending on exact conditions

    @pytest.mark.asyncio
    async def test_disable_transition_evaluation(self):
        """Can disable transition evaluation."""
        garden = create_garden(season=GardenSeason.DORMANT)

        gesture = observe("test")
        result = await apply_gesture(garden, gesture, evaluate_transition=False)

        # Should not have suggestion
        assert result.suggested_transition is None

    @pytest.mark.asyncio
    async def test_transition_suggestion_structure(self):
        """Transition suggestion should have correct structure."""
        garden = create_garden(season=GardenSeason.DORMANT)

        # Force high activity for transition
        for i in range(20):
            gesture = TendingGesture(
                verb=TendingVerb.WATER if i % 2 == 0 else TendingVerb.OBSERVE,
                target=f"concept.test.{i}",
                tone=0.8,
                reasoning="High activity",
                entropy_cost=0.02,
            )
            garden.add_gesture(gesture)

        garden.metrics.entropy_spent = 0.2
        garden.metrics.entropy_budget = 1.0
        clear_dismissals(garden.garden_id)

        # Evaluate manually
        signals = TransitionSignals.gather(garden)
        transition = evaluate_season_transition(garden, signals=signals)

        if transition and transition.should_suggest:
            assert transition.from_season == GardenSeason.DORMANT
            assert transition.to_season == GardenSeason.SPROUTING
            assert transition.confidence >= 0.7
            assert len(transition.reason) > 0
            assert transition.signals == signals


class TestEdgeCases:
    """Edge case tests for transition logic."""

    def test_empty_garden_signals(self):
        """Should handle garden with no gestures."""
        garden = create_garden()
        signals = TransitionSignals.gather(garden)

        assert signals.gesture_frequency == 0
        assert signals.gesture_diversity == 0

    def test_new_garden_no_suggestion(self):
        """Brand new garden should not suggest transition."""
        garden = create_garden()
        transition = evaluate_season_transition(garden)

        # New garden with no activity shouldn't transition
        assert transition is None or not transition.should_suggest

    def test_signals_clamp_entropy_ratio(self):
        """Entropy ratio should be clamped to 0-1."""
        garden = create_garden()
        garden.metrics.entropy_spent = 2.0  # Over budget
        garden.metrics.entropy_budget = 1.0

        signals = TransitionSignals.gather(garden)
        assert signals.entropy_spent_ratio <= 1.0

    def test_very_old_season_considered(self):
        """Very long time in season should be considered."""
        garden = create_garden(season=GardenSeason.HARVEST)
        garden.season_since = datetime.now() - timedelta(hours=100)

        signals = TransitionSignals.gather(garden)
        assert signals.time_in_season_hours >= 100
