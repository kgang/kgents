"""
Tests for Rumination: The Soul's Internal Life.

K-gent Phase 2: These tests verify that the rumination generator
produces ambient events correctly based on soul state.
"""

import asyncio
from datetime import timedelta

import pytest
from agents.k.events import (
    SoulEventType,
    is_ambient_event,
)
from agents.k.rumination import (
    RuminationConfig,
    generate_feeling,
    generate_gratitude,
    generate_observation,
    generate_self_challenge,
    generate_thought,
    quick_rumination,
    ruminate,
)
from agents.k.soul import KgentSoul


class TestRuminationConfig:
    """Test RuminationConfig."""

    def test_default_config(self) -> None:
        """Should create config with defaults."""
        config = RuminationConfig()

        assert config.check_interval == timedelta(seconds=5)
        assert config.thought_probability == 0.3
        assert config.max_ruminations == 100

    def test_custom_config(self) -> None:
        """Should create config with custom values."""
        config = RuminationConfig(
            check_interval=timedelta(seconds=1),
            thought_probability=0.5,
            max_ruminations=50,
        )

        assert config.check_interval == timedelta(seconds=1)
        assert config.thought_probability == 0.5
        assert config.max_ruminations == 50


class TestGenerateThought:
    """Test thought generation."""

    def test_generates_thought_content(self) -> None:
        """Should generate thought with content."""
        soul = KgentSoul()
        eigenvectors = soul.eigenvectors

        content, depth, triggered_by = generate_thought(eigenvectors)

        assert content is not None
        assert len(content) > 0
        assert depth in [1, 3]

    def test_thought_uses_eigenvector_templates(self) -> None:
        """Should use eigenvector-based templates."""
        soul = KgentSoul()
        eigenvectors = soul.eigenvectors

        # Generate many thoughts to check variety
        contents = set()
        for _ in range(20):
            content, _, _ = generate_thought(eigenvectors)
            contents.add(content)

        # Should have variety
        assert len(contents) >= 3


class TestGenerateFeeling:
    """Test feeling generation."""

    def test_generates_feeling_for_low_activity(self) -> None:
        """Should generate contemplative feelings for low activity."""
        soul = KgentSoul()
        eigenvectors = soul.eigenvectors

        valence, intensity, cause = generate_feeling(eigenvectors, 0)

        assert valence in ["contemplative", "serene", "curious"]
        assert intensity == 0.3
        assert cause == "quiet moment"

    def test_generates_feeling_for_high_activity(self) -> None:
        """Should generate energized feelings for high activity."""
        soul = KgentSoul()
        eigenvectors = soul.eigenvectors

        valence, intensity, cause = generate_feeling(eigenvectors, 15)

        assert valence in ["engaged", "focused", "energized"]
        assert intensity >= 0.6
        assert cause == "high activity"


class TestGenerateObservation:
    """Test observation generation."""

    def test_generates_observation(self) -> None:
        """Should generate observation with pattern."""
        pattern, confidence, domain = generate_observation()

        assert pattern is not None
        assert len(pattern) > 0
        assert 0.4 <= confidence <= 0.8
        assert domain == "general"


class TestGenerateSelfChallenge:
    """Test self-challenge generation."""

    def test_generates_self_challenge(self) -> None:
        """Should generate self-challenge with thesis and antithesis."""
        soul = KgentSoul()
        eigenvectors = soul.eigenvectors

        thesis, antithesis, synthesis, eigenvector = generate_self_challenge(
            eigenvectors
        )

        assert thesis is not None
        assert antithesis is not None
        # synthesis may be None (unresolved)
        assert eigenvector in [
            "categorical",
            "aesthetic",
            "principled",
            "playful",
            "heterarchical",
        ]


class TestGenerateGratitude:
    """Test gratitude generation."""

    def test_generates_gratitude(self) -> None:
        """Should generate gratitude expression."""
        for_what, to_whom, depth = generate_gratitude()

        assert for_what is not None
        assert len(for_what) > 0
        # to_whom may be None
        assert depth in [1, 3]


class TestRuminate:
    """Test the rumination async generator."""

    @pytest.mark.asyncio
    async def test_ruminate_yields_events(self) -> None:
        """Should yield ambient events."""
        soul = KgentSoul()
        config = RuminationConfig(
            check_interval=timedelta(milliseconds=10),
            thought_probability=1.0,  # Always generate
        )

        events = []
        async for event in ruminate(soul, config):
            events.append(event)
            if len(events) >= 3:
                break

        assert len(events) == 3
        for event in events:
            assert event.event_type == SoulEventType.THOUGHT

    @pytest.mark.asyncio
    async def test_ruminate_respects_probabilities(self) -> None:
        """Should respect event probabilities."""
        soul = KgentSoul()
        config = RuminationConfig(
            check_interval=timedelta(milliseconds=5),
            thought_probability=0.0,
            feeling_probability=0.0,
            observation_probability=0.0,
            challenge_probability=0.0,
            gratitude_probability=1.0,  # Only gratitude
        )

        events = []
        async for event in ruminate(soul, config):
            events.append(event)
            if len(events) >= 3:
                break

        assert len(events) == 3
        for event in events:
            assert event.event_type == SoulEventType.GRATITUDE

    @pytest.mark.asyncio
    async def test_ruminate_events_are_ambient(self) -> None:
        """All rumination events should be ambient."""
        soul = KgentSoul()
        config = RuminationConfig(
            check_interval=timedelta(milliseconds=5),
            # Mix of all types
            thought_probability=0.25,
            feeling_probability=0.25,
            observation_probability=0.25,
            challenge_probability=0.20,
            gratitude_probability=0.05,
        )

        events = []
        async for event in ruminate(soul, config):
            events.append(event)
            if len(events) >= 10:
                break

        for event in events:
            assert is_ambient_event(event), f"Event {event.event_type} is not ambient"

    @pytest.mark.asyncio
    async def test_ruminate_includes_correlation_ids(self) -> None:
        """Events should include correlation IDs."""
        soul = KgentSoul()
        config = RuminationConfig(
            check_interval=timedelta(milliseconds=5),
            thought_probability=1.0,
        )

        async for event in ruminate(soul, config):
            assert event.correlation_id is not None
            assert "rum-" in event.correlation_id
            break


class TestQuickRumination:
    """Test quick_rumination convenience function."""

    @pytest.mark.asyncio
    async def test_quick_rumination_yields_count(self) -> None:
        """Should yield exactly the requested count."""
        soul = KgentSoul()

        events = []
        async for event in quick_rumination(soul, count=5):
            events.append(event)

        assert len(events) == 5

    @pytest.mark.asyncio
    async def test_quick_rumination_is_fast(self) -> None:
        """Should complete quickly (10ms intervals)."""
        soul = KgentSoul()

        start = asyncio.get_event_loop().time()
        events = []
        async for event in quick_rumination(soul, count=3):
            events.append(event)
        elapsed = asyncio.get_event_loop().time() - start

        # Should complete in under 1 second
        assert elapsed < 1.0
        assert len(events) == 3


class TestRuminationVariety:
    """Test that rumination produces varied output."""

    @pytest.mark.asyncio
    async def test_produces_multiple_event_types(self) -> None:
        """Should produce multiple event types over time."""
        soul = KgentSoul()
        config = RuminationConfig(
            check_interval=timedelta(milliseconds=5),
            thought_probability=0.25,
            feeling_probability=0.25,
            observation_probability=0.25,
            challenge_probability=0.20,
            gratitude_probability=0.05,
        )

        event_types = set()
        async for event in ruminate(soul, config):
            event_types.add(event.event_type)
            if len(event_types) >= 3:
                break

        # Should have at least 3 different types
        assert len(event_types) >= 3


class TestRuminationHardening:
    """Test hardening: edge cases and validation."""

    def test_config_clamps_probabilities_above_one(self) -> None:
        """Should clamp probabilities > 1.0 to 1.0."""
        config = RuminationConfig(
            thought_probability=1.5,
            feeling_probability=2.0,
        )

        assert config.thought_probability == 1.0
        assert config.feeling_probability == 1.0

    def test_config_clamps_probabilities_below_zero(self) -> None:
        """Should clamp probabilities < 0.0 to 0.0."""
        config = RuminationConfig(
            thought_probability=-0.5,
            feeling_probability=-1.0,
        )

        assert config.thought_probability == 0.0
        assert config.feeling_probability == 0.0

    def test_config_clamps_max_ruminations(self) -> None:
        """Should clamp max_ruminations to at least 1."""
        config = RuminationConfig(max_ruminations=0)
        assert config.max_ruminations == 1

        config2 = RuminationConfig(max_ruminations=-5)
        assert config2.max_ruminations == 1

    def test_config_total_probability(self) -> None:
        """Should calculate total probability correctly."""
        config = RuminationConfig(
            thought_probability=0.3,
            feeling_probability=0.2,
            observation_probability=0.15,
            challenge_probability=0.1,
            gratitude_probability=0.05,
        )

        assert config.total_probability == 0.8

    def test_generate_feeling_clamps_intensity(self) -> None:
        """Should clamp intensity to [0, 1]."""
        soul = KgentSoul()
        eigenvectors = soul.eigenvectors

        # High activity count should still clamp intensity
        valence, intensity, cause = generate_feeling(eigenvectors, 1000)
        assert 0.0 <= intensity <= 1.0

    def test_generate_feeling_handles_negative_count(self) -> None:
        """Should handle negative event counts gracefully."""
        soul = KgentSoul()
        eigenvectors = soul.eigenvectors

        # Should not crash, should treat as zero
        valence, intensity, cause = generate_feeling(eigenvectors, -10)
        assert valence in ["contemplative", "serene", "curious"]
        assert intensity == 0.3


class TestSynergyBridge:
    """Test Pulse/Crystal synergy bridge functions."""

    def test_soul_to_pulse_basic(self) -> None:
        """Should convert soul state to pulse format."""
        from agents.k.rumination import soul_to_pulse

        soul = KgentSoul()
        pulse_data = soul_to_pulse(soul, "thinking", "test content")

        assert pulse_data["agent"] == "k-gent"
        assert "timestamp" in pulse_data
        assert 0.0 <= pulse_data["pressure"] <= 1.0
        assert pulse_data["phase"] == "thinking"
        assert len(pulse_data["content_hash"]) == 8
        assert pulse_data["metadata"]["source"] == "rumination"

    def test_soul_to_pulse_handles_errors(self) -> None:
        """Should handle malformed soul gracefully."""
        from agents.k.rumination import soul_to_pulse

        # Create a mock "soul" that raises errors
        class BrokenSoul:
            def manifest(self) -> None:
                raise AttributeError("broken")

        pulse_data = soul_to_pulse(BrokenSoul(), "waiting", "")  # type: ignore

        assert pulse_data["turn_count"] == 0
        assert pulse_data["metadata"]["mode"] == "reflect"

    @pytest.mark.asyncio
    async def test_rumination_to_crystal_task(self) -> None:
        """Should convert rumination events to task format."""
        from agents.k.rumination import rumination_to_crystal_task

        soul = KgentSoul()
        events = []
        async for event in quick_rumination(soul, count=5):
            events.append(event)

        task_data = rumination_to_crystal_task(events, "Test session")

        assert task_data["task_id"].startswith("rum_")
        assert task_data["description"] == "Test session"
        assert task_data["status"] == "completed"
        assert task_data["progress"] == 1.0
        assert task_data["metadata"]["event_count"] == 5
        assert task_data["metadata"]["source"] == "rumination"
