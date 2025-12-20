"""
Tests for ExperienceCrystal and related types.

Tests the core crystallization concepts:
- MoodVector derivation from thoughts
- TopologySnapshot extraction
- Narrative template fallback
- ExperienceCrystal creation and serialization
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from services.witness.crystal import (
    ExperienceCrystal,
    MoodVector,
    Narrative,
    TopologySnapshot,
)
from services.witness.polynomial import Thought

# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def sample_thoughts() -> list[Thought]:
    """Create sample thought stream for testing."""
    base_time = datetime.now()
    return [
        Thought(
            content="Started work on routing refactor",
            source="witness",
            tags=("lifecycle", "start"),
            timestamp=base_time,
        ),
        Thought(
            content="Edited: protocols/cli/hollow.py (+45/-12)",
            source="filesystem",
            tags=("file", "modify"),
            timestamp=base_time + timedelta(minutes=5),
        ),
        Thought(
            content="Test session: 20 passed, 2 failed, 0 skipped",
            source="tests",
            tags=("tests", "session"),
            timestamp=base_time + timedelta(minutes=10),
        ),
        Thought(
            content="Edited: protocols/cli/hollow.py (+8/-3)",
            source="filesystem",
            tags=("file", "modify"),
            timestamp=base_time + timedelta(minutes=15),
        ),
        Thought(
            content="Test session: 22 passed, 0 failed, 0 skipped",
            source="tests",
            tags=("tests", "session", "success"),
            timestamp=base_time + timedelta(minutes=20),
        ),
        Thought(
            content="Committed: feat(cli): Path-first routing",
            source="git",
            tags=("git", "commit"),
            timestamp=base_time + timedelta(minutes=25),
        ),
    ]


@pytest.fixture
def empty_thoughts() -> list[Thought]:
    """Empty thought list."""
    return []


@pytest.fixture
def failure_heavy_thoughts() -> list[Thought]:
    """Thoughts with many failures."""
    base_time = datetime.now()
    return [
        Thought(
            content="Test failed: test_routing",
            source="tests",
            tags=("tests", "failure"),
            timestamp=base_time,
        ),
        Thought(
            content="Error in hollow.py line 42",
            source="filesystem",
            tags=("error",),
            timestamp=base_time + timedelta(minutes=1),
        ),
        Thought(
            content="Test failed: test_dispatch",
            source="tests",
            tags=("tests", "failure"),
            timestamp=base_time + timedelta(minutes=2),
        ),
        Thought(
            content="Still failing",
            source="witness",
            tags=(),
            timestamp=base_time + timedelta(minutes=3),
        ),
    ]


# =============================================================================
# MoodVector Tests
# =============================================================================


class TestMoodVector:
    """Tests for MoodVector affective signature."""

    def test_neutral_mood(self) -> None:
        """Neutral mood has all dimensions at 0.5."""
        mood = MoodVector.neutral()
        assert mood.warmth == 0.5
        assert mood.weight == 0.5
        assert mood.tempo == 0.5
        assert mood.texture == 0.5
        assert mood.brightness == 0.5
        assert mood.saturation == 0.5
        assert mood.complexity == 0.5

    def test_mood_from_empty_thoughts(self) -> None:
        """Empty thoughts produce neutral mood."""
        mood = MoodVector.from_thoughts([])
        assert mood == MoodVector.neutral()

    def test_mood_from_sample_thoughts(self, sample_thoughts: list[Thought]) -> None:
        """Sample thoughts produce reasonable mood."""
        mood = MoodVector.from_thoughts(sample_thoughts)

        # Sample has 2 successes and 2 failures, so brightness should be ~0.5
        # (22 passed, 0 failed has "pass" and "success" in tags, 2 failed has "fail")
        assert 0.4 <= mood.brightness <= 0.6  # Near neutral

        # Should have some warmth (has commit)
        assert mood.warmth > 0.4

        # Should have moderate tempo (6 events)
        assert 0.0 < mood.tempo < 1.0

    def test_mood_from_failure_heavy_thoughts(self, failure_heavy_thoughts: list[Thought]) -> None:
        """Failure-heavy thoughts produce darker mood."""
        mood = MoodVector.from_thoughts(failure_heavy_thoughts)

        # Should have lower brightness (failures)
        assert mood.brightness < 0.5

        # Should have rougher texture
        assert mood.texture > 0.5

    def test_mood_dimension_bounds(self) -> None:
        """All dimensions are clamped to [0, 1]."""
        # Create mood with out-of-bounds values
        mood = MoodVector(
            warmth=-0.5,
            weight=1.5,
            tempo=0.5,
            texture=0.5,
            brightness=0.5,
            saturation=0.5,
            complexity=0.5,
        )

        # Should be clamped
        assert mood.warmth >= 0.0
        assert mood.weight <= 1.0

    def test_mood_similarity_identical(self) -> None:
        """Identical moods have similarity 1.0."""
        mood = MoodVector(
            warmth=0.8,
            weight=0.3,
            tempo=0.6,
            texture=0.2,
            brightness=0.9,
            saturation=0.5,
            complexity=0.4,
        )
        assert mood.similarity(mood) == pytest.approx(1.0, abs=0.001)

    def test_mood_similarity_different(self) -> None:
        """Different moods have lower similarity."""
        mood1 = MoodVector(
            warmth=0.9,
            weight=0.1,
            tempo=0.9,
            texture=0.1,
            brightness=0.9,
            saturation=0.9,
            complexity=0.1,
        )
        mood2 = MoodVector(
            warmth=0.1,
            weight=0.9,
            tempo=0.1,
            texture=0.9,
            brightness=0.1,
            saturation=0.1,
            complexity=0.9,
        )

        similarity = mood1.similarity(mood2)
        assert similarity < 1.0
        assert similarity > -1.0  # Still positive due to all positive values

    def test_mood_to_dict_roundtrip(self) -> None:
        """Mood can be serialized and deserialized."""
        original = MoodVector(
            warmth=0.7,
            weight=0.3,
            tempo=0.8,
            texture=0.2,
            brightness=0.9,
            saturation=0.4,
            complexity=0.6,
        )
        data = original.to_dict()
        restored = MoodVector.from_dict(data)

        assert restored.warmth == original.warmth
        assert restored.brightness == original.brightness

    def test_dominant_quality(self) -> None:
        """Dominant quality is furthest from neutral."""
        mood = MoodVector(
            warmth=0.5,  # neutral
            weight=0.5,  # neutral
            tempo=0.5,  # neutral
            texture=0.5,  # neutral
            brightness=0.95,  # very bright - furthest from 0.5
            saturation=0.5,  # neutral
            complexity=0.5,  # neutral
        )
        assert mood.dominant_quality == "brightness"


# =============================================================================
# TopologySnapshot Tests
# =============================================================================


class TestTopologySnapshot:
    """Tests for TopologySnapshot codebase position."""

    def test_empty_topology(self) -> None:
        """Empty thoughts produce default topology."""
        topo = TopologySnapshot.from_thoughts([])
        assert topo.primary_path == "."
        assert topo.heat == {}

    def test_topology_from_file_events(self, sample_thoughts: list[Thought]) -> None:
        """Topology extracts file paths from thoughts."""
        topo = TopologySnapshot.from_thoughts(sample_thoughts)

        # Should have extracted hollow.py as primary (most active)
        assert "hollow.py" in topo.primary_path or len(topo.heat) > 0

    def test_topology_heat_normalized(self) -> None:
        """Heat map is normalized to [0, 1]."""
        thoughts = [
            Thought(content="Edited: foo.py", source="filesystem", tags=("file",)),
            Thought(content="Edited: foo.py", source="filesystem", tags=("file",)),
            Thought(content="Edited: bar.py", source="filesystem", tags=("file",)),
        ]
        topo = TopologySnapshot.from_thoughts(thoughts)

        if topo.heat:
            # Max should be 1.0 (foo.py edited twice)
            assert max(topo.heat.values()) == pytest.approx(1.0)
            # All values in [0, 1]
            for v in topo.heat.values():
                assert 0.0 <= v <= 1.0

    def test_topology_serialization(self) -> None:
        """Topology can be serialized and deserialized."""
        original = TopologySnapshot(
            primary_path="src/main.py",
            heat={"src/main.py": 1.0, "src/utils.py": 0.5},
            dependencies=frozenset([("src/main.py", "src/utils.py")]),
        )
        data = original.to_dict()
        restored = TopologySnapshot.from_dict(data)

        assert restored.primary_path == original.primary_path
        assert restored.heat == original.heat
        assert restored.dependencies == original.dependencies


# =============================================================================
# Narrative Tests
# =============================================================================


class TestNarrative:
    """Tests for Narrative synthesis."""

    def test_empty_narrative(self) -> None:
        """Empty thoughts produce minimal narrative."""
        narrative = Narrative.template_fallback([])
        assert "Empty session" in narrative.summary

    def test_template_fallback(self, sample_thoughts: list[Thought]) -> None:
        """Template fallback produces reasonable narrative."""
        narrative = Narrative.template_fallback(sample_thoughts)

        assert len(narrative.summary) > 0
        assert "6 observations" in narrative.summary or "observations" in narrative.summary.lower()
        assert len(narrative.themes) <= 3  # Top 3 themes

    def test_narrative_serialization(self) -> None:
        """Narrative can be serialized and deserialized."""
        original = Narrative(
            summary="Great session",
            themes=("routing", "tests"),
            highlights=("Fixed bug", "All tests pass"),
            dramatic_question="Can we ship today?",
        )
        data = original.to_dict()
        restored = Narrative.from_dict(data)

        assert restored.summary == original.summary
        assert restored.themes == original.themes
        assert restored.highlights == original.highlights


# =============================================================================
# ExperienceCrystal Tests
# =============================================================================


class TestExperienceCrystal:
    """Tests for ExperienceCrystal atomic memory unit."""

    def test_crystal_from_empty_thoughts(self) -> None:
        """Empty thoughts produce empty crystal."""
        crystal = ExperienceCrystal.from_thoughts([], session_id="test-session")

        assert crystal.session_id == "test-session"
        assert crystal.thought_count == 0
        assert "Empty" in crystal.narrative.summary

    def test_crystal_from_sample_thoughts(self, sample_thoughts: list[Thought]) -> None:
        """Sample thoughts produce rich crystal."""
        crystal = ExperienceCrystal.from_thoughts(
            sample_thoughts,
            session_id="routing-refactor",
            markers=["Started routing", "Tests fixed"],
        )

        assert crystal.session_id == "routing-refactor"
        assert crystal.thought_count == 6
        assert len(crystal.markers) == 2
        # Sample has mixed success/failure signals, so brightness near neutral
        assert 0.4 <= crystal.mood.brightness <= 0.6
        assert crystal.started_at is not None
        assert crystal.ended_at is not None
        assert crystal.duration_minutes is not None
        assert crystal.duration_minutes > 0

    def test_crystal_topics_extracted(self, sample_thoughts: list[Thought]) -> None:
        """Crystal extracts topics from thoughts."""
        crystal = ExperienceCrystal.from_thoughts(sample_thoughts)

        # Should have sources as topics
        assert (
            "filesystem" in crystal.topics or "git" in crystal.topics or "tests" in crystal.topics
        )

    def test_crystal_serialization_roundtrip(self, sample_thoughts: list[Thought]) -> None:
        """Crystal can be serialized and deserialized."""
        original = ExperienceCrystal.from_thoughts(
            sample_thoughts,
            session_id="test-session",
            markers=["marker1"],
        )

        json_data = original.to_json()
        restored = ExperienceCrystal.from_json(json_data)

        assert restored.crystal_id == original.crystal_id
        assert restored.session_id == original.session_id
        assert restored.thought_count == original.thought_count
        assert restored.mood.brightness == pytest.approx(original.mood.brightness, abs=0.01)

    def test_crystal_as_memory(self, sample_thoughts: list[Thought]) -> None:
        """Crystal projects to D-gent compatible format."""
        crystal = ExperienceCrystal.from_thoughts(sample_thoughts, session_id="test")
        memory = crystal.as_memory()

        assert memory["key"].startswith("witness:crystal:")
        assert "metadata" in memory
        assert memory["metadata"]["type"] == "experience_crystal"
        assert isinstance(memory["metadata"]["topics"], list)

    def test_crystal_id_uniqueness(self) -> None:
        """Each crystal gets a unique ID."""
        crystal1 = ExperienceCrystal.from_thoughts([])
        crystal2 = ExperienceCrystal.from_thoughts([])

        assert crystal1.crystal_id != crystal2.crystal_id

    def test_crystal_complexity_from_mood(self, sample_thoughts: list[Thought]) -> None:
        """Crystal complexity derived from mood complexity."""
        crystal = ExperienceCrystal.from_thoughts(sample_thoughts)

        # Complexity should be between 0 and 1
        assert 0.0 <= crystal.complexity <= 1.0

    def test_crystal_repr(self, sample_thoughts: list[Thought]) -> None:
        """Crystal has informative repr."""
        crystal = ExperienceCrystal.from_thoughts(sample_thoughts)
        repr_str = repr(crystal)

        assert "ExperienceCrystal" in repr_str
        assert "thoughts=6" in repr_str


# =============================================================================
# Integration Tests
# =============================================================================


class TestCrystallizationIntegration:
    """Integration tests for the crystallization pipeline."""

    def test_full_crystallization_pipeline(self, sample_thoughts: list[Thought]) -> None:
        """Test complete crystallization from thoughts to memory."""
        # Create crystal
        crystal = ExperienceCrystal.from_thoughts(
            sample_thoughts,
            session_id="integration-test",
            markers=["milestone"],
        )

        # Verify all components
        assert crystal.thought_count > 0
        assert crystal.mood != MoodVector.neutral()
        assert crystal.narrative.summary != ""
        assert len(crystal.topics) > 0

        # Serialize to memory format
        memory = crystal.as_memory()
        assert memory["metadata"]["session_id"] == "integration-test"

        # Deserialize back
        restored = ExperienceCrystal.from_json(crystal.to_json())
        assert restored.session_id == crystal.session_id
        assert restored.thought_count == crystal.thought_count

    def test_mood_affects_narrative_retrieval(self) -> None:
        """Similar moods should have high similarity for retrieval."""
        # Create two similar sessions
        happy_thoughts = [
            Thought(content="Test passed", source="tests", tags=("success",)),
            Thought(content="All green", source="tests", tags=("success",)),
        ]
        also_happy_thoughts = [
            Thought(content="Tests successful", source="tests", tags=("success",)),
            Thought(content="Build passed", source="ci", tags=("success",)),
        ]

        crystal1 = ExperienceCrystal.from_thoughts(happy_thoughts)
        crystal2 = ExperienceCrystal.from_thoughts(also_happy_thoughts)

        # Moods should be similar
        similarity = crystal1.mood.similarity(crystal2.mood)
        assert similarity > 0.5  # More similar than different


# =============================================================================
# Property-Based Tests (Optional - requires hypothesis)
# =============================================================================


try:
    from hypothesis import given, settings, strategies as st

    class TestMoodVectorProperties:
        """Property-based tests for MoodVector."""

        @given(
            warmth=st.floats(min_value=0.0, max_value=1.0),
            weight=st.floats(min_value=0.0, max_value=1.0),
            tempo=st.floats(min_value=0.0, max_value=1.0),
            texture=st.floats(min_value=0.0, max_value=1.0),
            brightness=st.floats(min_value=0.0, max_value=1.0),
            saturation=st.floats(min_value=0.0, max_value=1.0),
            complexity=st.floats(min_value=0.0, max_value=1.0),
        )
        @settings(max_examples=50)
        def test_mood_self_similarity_is_one(
            self,
            warmth: float,
            weight: float,
            tempo: float,
            texture: float,
            brightness: float,
            saturation: float,
            complexity: float,
        ) -> None:
            """Any mood has similarity 1.0 with itself."""
            mood = MoodVector(
                warmth=warmth,
                weight=weight,
                tempo=tempo,
                texture=texture,
                brightness=brightness,
                saturation=saturation,
                complexity=complexity,
            )
            assert mood.similarity(mood) == pytest.approx(1.0, abs=0.001)

        @given(
            warmth=st.floats(min_value=0.0, max_value=1.0),
            weight=st.floats(min_value=0.0, max_value=1.0),
        )
        @settings(max_examples=20)
        def test_mood_serialization_roundtrip(self, warmth: float, weight: float) -> None:
            """Mood survives serialization roundtrip."""
            original = MoodVector(warmth=warmth, weight=weight)
            restored = MoodVector.from_dict(original.to_dict())
            assert restored.warmth == pytest.approx(original.warmth, abs=0.001)
            assert restored.weight == pytest.approx(original.weight, abs=0.001)

except ImportError:
    pass  # hypothesis not installed, skip property tests
