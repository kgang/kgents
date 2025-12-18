"""
Tests for FeverStream and FeverEvent.

Tests cover:
- Oblique strategy selection
- Deterministic selection with seed
- Dream fallback to oblique
- FeverEvent population
"""

from __future__ import annotations

import pytest

from protocols.agentese.metabolism import FeverEvent, FeverStream


class TestObliqueStrategies:
    """Test oblique strategy generation."""

    def test_oblique_returns_string(self) -> None:
        """oblique() returns a strategy string."""
        stream = FeverStream()

        strategy = stream.oblique()

        assert isinstance(strategy, str)
        assert len(strategy) > 0

    def test_oblique_is_deterministic(self) -> None:
        """Same seed produces same strategy."""
        stream = FeverStream()

        s1 = stream.oblique(0.5)
        s2 = stream.oblique(0.5)

        assert s1 == s2

    def test_oblique_varies_with_seed(self) -> None:
        """Different seeds produce different strategies."""
        stream = FeverStream()

        s1 = stream.oblique(0.1)
        s2 = stream.oblique(0.9)

        assert s1 != s2

    def test_oblique_without_seed_is_random(self) -> None:
        """Without seed, strategies vary (statistically)."""
        stream = FeverStream()

        strategies = [stream.oblique() for _ in range(20)]
        unique = set(strategies)

        # Should get at least 2 different strategies in 20 tries
        assert len(unique) >= 2

    def test_oblique_handles_edge_seeds(self) -> None:
        """Edge seeds (0.0, 1.0) don't crash."""
        stream = FeverStream()

        s0 = stream.oblique(0.0)
        s1 = stream.oblique(1.0)
        s_almost_1 = stream.oblique(0.9999)

        assert isinstance(s0, str)
        assert isinstance(s1, str)
        assert isinstance(s_almost_1, str)


class TestFeverDream:
    """Test fever dream generation."""

    @pytest.mark.asyncio
    async def test_dream_falls_back_to_oblique(self) -> None:
        """Without LLM client, dream() returns oblique strategy."""
        stream = FeverStream()

        result = await stream.dream({}, llm_client=None)

        assert isinstance(result, str)
        assert result in stream._oblique_strategies

    @pytest.mark.asyncio
    async def test_dream_with_context(self) -> None:
        """Dream accepts context dict."""
        stream = FeverStream()

        result = await stream.dream(
            {"task": "fix bug", "file": "main.py"},
            llm_client=None,
        )

        assert isinstance(result, str)


class TestFeverEvent:
    """Test FeverEvent dataclass."""

    def test_fever_event_creation(self) -> None:
        """FeverEvent can be created with required fields."""
        event = FeverEvent(
            intensity=0.5,
            timestamp=12345.0,
            trigger="pressure_overflow",
            seed=0.42,
        )

        assert event.intensity == 0.5
        assert event.timestamp == 12345.0
        assert event.trigger == "pressure_overflow"
        assert event.seed == 0.42
        assert event.oblique_strategy == ""  # Default

    def test_fever_event_with_strategy(self) -> None:
        """FeverEvent can be created with oblique strategy."""
        event = FeverEvent(
            intensity=0.5,
            timestamp=12345.0,
            trigger="manual",
            seed=0.42,
            oblique_strategy="Honor thy error as a hidden intention.",
        )

        assert event.oblique_strategy == "Honor thy error as a hidden intention."


class TestFeverStreamPopulation:
    """Test FeverStream.populate_event()."""

    def test_populate_event_adds_strategy(self) -> None:
        """populate_event adds oblique strategy to event."""
        stream = FeverStream()
        event = FeverEvent(
            intensity=0.5,
            timestamp=12345.0,
            trigger="pressure_overflow",
            seed=0.42,
        )

        stream.populate_event(event)

        assert event.oblique_strategy != ""

    def test_populate_event_uses_seed(self) -> None:
        """populate_event uses event's seed for deterministic selection."""
        stream = FeverStream()
        event1 = FeverEvent(intensity=0.5, timestamp=12345.0, trigger="test", seed=0.42)
        event2 = FeverEvent(intensity=0.5, timestamp=12345.0, trigger="test", seed=0.42)

        stream.populate_event(event1)
        stream.populate_event(event2)

        assert event1.oblique_strategy == event2.oblique_strategy

    def test_populate_event_returns_event(self) -> None:
        """populate_event returns the event for chaining."""
        stream = FeverStream()
        event = FeverEvent(intensity=0.5, timestamp=12345.0, trigger="test", seed=0.42)

        returned = stream.populate_event(event)

        assert returned is event
