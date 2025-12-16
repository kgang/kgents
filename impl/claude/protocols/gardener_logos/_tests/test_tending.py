"""
Tests for Tending Calculus.

Validates:
- TendingVerb properties
- TendingGesture immutability
- Gesture builders
- Gesture application
"""

import pytest
from datetime import datetime, timedelta

from ..garden import create_garden, GardenSeason
from ..tending import (
    TendingVerb,
    TendingGesture,
    TendingResult,
    apply_gesture,
    observe,
    prune,
    graft,
    water,
    rotate,
    wait,
)


class TestTendingVerb:
    """Tests for TendingVerb enum."""

    def test_verb_has_emoji(self):
        """Each verb has an emoji."""
        for verb in TendingVerb:
            assert verb.emoji is not None
            assert len(verb.emoji) > 0

    def test_verb_has_base_entropy_cost(self):
        """Each verb has a base entropy cost."""
        for verb in TendingVerb:
            assert verb.base_entropy_cost >= 0

    def test_observe_is_cheap(self):
        """OBSERVE should be nearly free."""
        assert TendingVerb.OBSERVE.base_entropy_cost < 0.05

    def test_wait_is_free(self):
        """WAIT should be completely free."""
        assert TendingVerb.WAIT.base_entropy_cost == 0.0

    def test_graft_is_expensive(self):
        """GRAFT should be relatively expensive."""
        assert TendingVerb.GRAFT.base_entropy_cost >= 0.15

    def test_state_affecting_verbs(self):
        """Certain verbs should affect state."""
        assert TendingVerb.PRUNE.affects_state is True
        assert TendingVerb.GRAFT.affects_state is True
        assert TendingVerb.WATER.affects_state is True
        assert TendingVerb.ROTATE.affects_state is True

        # These don't change state
        assert TendingVerb.OBSERVE.affects_state is False
        assert TendingVerb.WAIT.affects_state is False


class TestTendingGesture:
    """Tests for TendingGesture dataclass."""

    def test_gesture_is_frozen(self):
        """Gestures should be immutable."""
        gesture = TendingGesture(
            verb=TendingVerb.OBSERVE,
            target="test",
            tone=0.5,
            reasoning="Testing",
            entropy_cost=0.1,
        )

        # Attempt to modify should raise
        with pytest.raises(Exception):  # FrozenInstanceError
            gesture.tone = 0.9  # type: ignore

    def test_gesture_serialization(self):
        """Gestures should serialize to dict."""
        gesture = TendingGesture(
            verb=TendingVerb.WATER,
            target="concept.prompt.test",
            tone=0.7,
            reasoning="Testing serialization",
            entropy_cost=0.15,
        )

        data = gesture.to_dict()
        assert data["verb"] == "WATER"
        assert data["target"] == "concept.prompt.test"
        assert data["tone"] == 0.7

    def test_gesture_deserialization(self):
        """Gestures should deserialize from dict."""
        data = {
            "verb": "GRAFT",
            "target": "concept.new.thing",
            "tone": 0.8,
            "reasoning": "Adding something new",
            "entropy_cost": 0.2,
            "timestamp": datetime.now().isoformat(),
        }

        gesture = TendingGesture.from_dict(data)
        assert gesture.verb == TendingVerb.GRAFT
        assert gesture.target == "concept.new.thing"
        assert gesture.tone == 0.8

    def test_gesture_is_recent(self):
        """is_recent should detect recent gestures."""
        recent = TendingGesture(
            verb=TendingVerb.OBSERVE,
            target="test",
            tone=0.5,
            reasoning="Recent",
            entropy_cost=0.01,
            timestamp=datetime.now(),
        )

        old = TendingGesture(
            verb=TendingVerb.OBSERVE,
            target="test",
            tone=0.5,
            reasoning="Old",
            entropy_cost=0.01,
            timestamp=datetime.now() - timedelta(hours=48),
        )

        assert recent.is_recent(hours=24) is True
        assert old.is_recent(hours=24) is False

    def test_gesture_display(self):
        """display() should return readable string."""
        gesture = TendingGesture(
            verb=TendingVerb.WATER,
            target="concept.prompt",
            tone=0.5,
            reasoning="Testing",
            entropy_cost=0.1,
        )

        display = gesture.display()
        assert "water" in display.lower()  # Verb name is lowercased
        assert "concept.prompt" in display


class TestGestureBuilders:
    """Tests for gesture builder functions."""

    def test_observe_builder(self):
        """observe() should create OBSERVE gesture."""
        gesture = observe("concept.gardener")
        assert gesture.verb == TendingVerb.OBSERVE
        assert gesture.target == "concept.gardener"

    def test_prune_builder(self):
        """prune() should create PRUNE gesture."""
        gesture = prune("old.pattern", "No longer needed", tone=0.8)
        assert gesture.verb == TendingVerb.PRUNE
        assert gesture.tone == 0.8
        assert "No longer needed" in gesture.reasoning

    def test_graft_builder(self):
        """graft() should create GRAFT gesture."""
        gesture = graft("new.thing", "Adding capability")
        assert gesture.verb == TendingVerb.GRAFT
        assert gesture.target == "new.thing"

    def test_water_builder(self):
        """water() should create WATER gesture."""
        gesture = water("concept.prompt.task", "Make it clearer")
        assert gesture.verb == TendingVerb.WATER
        assert "Make it clearer" in gesture.reasoning

    def test_rotate_builder(self):
        """rotate() should create ROTATE gesture."""
        gesture = rotate("concept.gardener.season")
        assert gesture.verb == TendingVerb.ROTATE

    def test_wait_builder(self):
        """wait() should create WAIT gesture."""
        gesture = wait("Letting things settle")
        assert gesture.verb == TendingVerb.WAIT
        assert gesture.entropy_cost == 0.0
        assert gesture.target == ""


class TestApplyGesture:
    """Tests for apply_gesture function."""

    @pytest.mark.asyncio
    async def test_apply_observe(self):
        """OBSERVE should succeed without changing state."""
        garden = create_garden()
        gesture = observe("concept.gardener")

        result = await apply_gesture(garden, gesture)

        assert result.accepted is True
        assert result.state_changed is False
        assert len(result.reasoning_trace) > 0

    @pytest.mark.asyncio
    async def test_apply_wait(self):
        """WAIT should succeed without state change."""
        garden = create_garden()
        gesture = wait()

        result = await apply_gesture(garden, gesture)

        assert result.accepted is True
        assert result.state_changed is False

    @pytest.mark.asyncio
    async def test_apply_prune(self):
        """PRUNE should be accepted and mark state change."""
        garden = create_garden(season=GardenSeason.HARVEST)
        gesture = prune("old.pattern", "Cleanup")

        result = await apply_gesture(garden, gesture)

        assert result.accepted is True
        assert result.state_changed is True

    @pytest.mark.asyncio
    async def test_apply_water_triggers_synergy(self):
        """WATER on prompt path should trigger TextGRAD synergy."""
        garden = create_garden()
        gesture = water("concept.prompt.test", "Improve clarity")

        result = await apply_gesture(garden, gesture)

        assert result.accepted is True
        assert "textgrad:improvement_proposed" in result.synergies_triggered

    @pytest.mark.asyncio
    async def test_gesture_recorded_in_garden(self):
        """Applied gestures should be recorded in garden momentum."""
        garden = create_garden()
        initial_count = len(garden.recent_gestures)

        gesture = observe("test.path")
        await apply_gesture(garden, gesture)

        assert len(garden.recent_gestures) == initial_count + 1

    @pytest.mark.asyncio
    async def test_gesture_updates_entropy(self):
        """Gestures should update garden's entropy spent."""
        garden = create_garden()
        initial_entropy = garden.metrics.entropy_spent

        gesture = graft("new.thing", "Testing entropy")
        await apply_gesture(garden, gesture)

        assert garden.metrics.entropy_spent > initial_entropy
