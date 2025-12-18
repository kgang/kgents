"""
Tests for GardenState and GardenSeason.

Validates:
- Season properties (plasticity, entropy multiplier)
- Garden state serialization
- Season transitions
- Gesture accumulation
"""

from datetime import datetime, timedelta

import pytest

from ..garden import GardenMetrics, GardenSeason, GardenState, create_garden
from ..tending import TendingGesture, TendingVerb


class TestGardenSeason:
    """Tests for GardenSeason enum."""

    def test_season_has_emoji(self):
        """Each season has an emoji."""
        for season in GardenSeason:
            assert season.emoji is not None
            assert len(season.emoji) > 0

    def test_season_plasticity_range(self):
        """Plasticity should be between 0 and 1."""
        for season in GardenSeason:
            assert 0.0 <= season.plasticity <= 1.0

    def test_sprouting_is_most_plastic(self):
        """SPROUTING season should have highest plasticity."""
        assert GardenSeason.SPROUTING.plasticity == max(s.plasticity for s in GardenSeason)

    def test_dormant_is_least_plastic(self):
        """DORMANT season should have lowest plasticity."""
        assert GardenSeason.DORMANT.plasticity == min(s.plasticity for s in GardenSeason)

    def test_entropy_multiplier_range(self):
        """Entropy multiplier should be positive."""
        for season in GardenSeason:
            assert season.entropy_multiplier > 0


class TestGardenMetrics:
    """Tests for GardenMetrics."""

    def test_default_health_score(self):
        """Default metrics with budget should have partial health from entropy."""
        metrics = GardenMetrics()
        # Default budget of 1.0 - 0.0 spent = 1.0 * 0.25 = 0.25
        assert metrics.health_score == 0.25

    def test_health_score_components(self):
        """Health score should increase with activity."""
        metrics = GardenMetrics(
            active_plots=3,
            recent_gestures=5,
            entropy_budget=1.0,
            entropy_spent=0.0,
            session_cycles=10,
        )
        # Each factor contributes 0.25 max
        assert metrics.health_score > 0.5

    def test_health_score_capped(self):
        """Health score should not exceed 1.0."""
        metrics = GardenMetrics(
            total_prompts=100,
            active_plots=10,
            recent_gestures=20,
            session_cycles=100,
            entropy_budget=10.0,
            entropy_spent=0.0,
        )
        assert metrics.health_score <= 1.0


class TestGardenState:
    """Tests for GardenState."""

    def test_create_garden(self):
        """create_garden should return valid state."""
        garden = create_garden(name="Test Garden")
        assert garden.name == "Test Garden"
        assert garden.garden_id is not None
        assert garden.season == GardenSeason.DORMANT

    def test_create_garden_with_season(self):
        """create_garden should accept initial season."""
        garden = create_garden(name="Test", season=GardenSeason.SPROUTING)
        assert garden.season == GardenSeason.SPROUTING

    def test_garden_serialization_roundtrip(self):
        """Garden should survive dict roundtrip."""
        garden = create_garden(name="Roundtrip Test")
        garden.prompt_count = 42
        garden.memory_crystals = ["crystal-1", "crystal-2"]

        data = garden.to_dict()
        restored = GardenState.from_dict(data)

        assert restored.name == garden.name
        assert restored.garden_id == garden.garden_id
        assert restored.season == garden.season
        assert restored.prompt_count == 42
        assert restored.memory_crystals == ["crystal-1", "crystal-2"]

    def test_season_transition(self):
        """transition_season should update season and record gesture."""
        garden = create_garden()
        assert garden.season == GardenSeason.DORMANT

        garden.transition_season(GardenSeason.SPROUTING, "Time to grow")

        assert garden.season == GardenSeason.SPROUTING
        assert len(garden.recent_gestures) == 1
        assert garden.recent_gestures[0].verb == TendingVerb.ROTATE

    def test_add_gesture(self):
        """add_gesture should accumulate and update metrics."""
        garden = create_garden()
        initial_spent = garden.metrics.entropy_spent

        gesture = TendingGesture(
            verb=TendingVerb.OBSERVE,
            target="test.target",
            tone=0.5,
            reasoning="Testing",
            entropy_cost=0.1,
        )
        garden.add_gesture(gesture)

        assert len(garden.recent_gestures) == 1
        assert garden.metrics.entropy_spent == initial_spent + 0.1

    def test_gesture_limit(self):
        """Garden should keep only last 50 gestures."""
        garden = create_garden()

        for i in range(60):
            gesture = TendingGesture(
                verb=TendingVerb.WAIT,
                target="",
                tone=0.0,
                reasoning=f"Gesture {i}",
                entropy_cost=0.0,
            )
            garden.add_gesture(gesture)

        assert len(garden.recent_gestures) == 50
        # Last gesture should be most recent
        assert "Gesture 59" in garden.recent_gestures[-1].reasoning


class TestGardenSeasonInteraction:
    """Test interactions between season and garden state."""

    def test_season_affects_operations(self):
        """Different seasons should have different entropy costs."""
        dormant_cost = GardenSeason.DORMANT.entropy_multiplier
        sprouting_cost = GardenSeason.SPROUTING.entropy_multiplier
        composting_cost = GardenSeason.COMPOSTING.entropy_multiplier

        # COMPOSTING is hardest (breaking down patterns is work)
        assert composting_cost > sprouting_cost
        assert composting_cost > dormant_cost

        # DORMANT is cheapest (observing costs little)
        assert dormant_cost < sprouting_cost

    def test_garden_tracks_time_in_season(self):
        """Garden should track when season started."""
        garden = create_garden()
        initial_time = garden.season_since

        # Transition
        garden.transition_season(GardenSeason.BLOOMING)

        assert garden.season_since > initial_time
