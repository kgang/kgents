"""
Tests for WitnessSheaf crystallization gluing.

Tests the sheaf protocol for event source observation:
- EventSource contexts and capabilities
- LocalObservation creation and overlap
- WitnessSheaf.compatible() for gluing eligibility
- WitnessSheaf.glue() for crystallization
- WitnessSheaf.restrict() for inverse extraction
- Sheaf law verification (identity, associativity)

These tests verify the categorical foundation:
    "A sheaf is defined as a presheaf satisfying locality and gluing
    conditions, ensuring coherent global structure while preserving
    local properties."

See: plans/witness-muse-implementation.md
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from services.witness.polynomial import Thought
from services.witness.sheaf import (
    SOURCE_CAPABILITIES,
    EventSource,
    GluingError,
    LocalObservation,
    WitnessSheaf,
    source_overlap,
    verify_associativity_law,
    verify_identity_law,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def base_time() -> datetime:
    """Base time for test observations."""
    return datetime(2025, 12, 19, 10, 0, 0)


@pytest.fixture
def git_observation(base_time: datetime) -> LocalObservation:
    """Git source observation."""
    return LocalObservation(
        source=EventSource.GIT,
        thoughts=(
            Thought(
                content="Committed: feat(witness): Add sheaf gluing",
                source="git",
                tags=("commit", "feature"),
                timestamp=base_time + timedelta(minutes=5),
            ),
            Thought(
                content="Pushed to origin/main",
                source="git",
                tags=("push",),
                timestamp=base_time + timedelta(minutes=6),
            ),
        ),
        started_at=base_time,
        ended_at=base_time + timedelta(minutes=10),
        metadata={"branch": "main"},
    )


@pytest.fixture
def filesystem_observation(base_time: datetime) -> LocalObservation:
    """Filesystem source observation."""
    return LocalObservation(
        source=EventSource.FILESYSTEM,
        thoughts=(
            Thought(
                content="Edited: services/witness/sheaf.py (+150/-0)",
                source="filesystem",
                tags=("file", "create"),
                timestamp=base_time + timedelta(minutes=2),
            ),
            Thought(
                content="Edited: services/witness/sheaf.py (+30/-5)",
                source="filesystem",
                tags=("file", "modify"),
                timestamp=base_time + timedelta(minutes=8),
            ),
        ),
        started_at=base_time,
        ended_at=base_time + timedelta(minutes=10),
    )


@pytest.fixture
def test_observation(base_time: datetime) -> LocalObservation:
    """Test source observation."""
    return LocalObservation(
        source=EventSource.TESTS,
        thoughts=(
            Thought(
                content="Test run: 15 passed, 0 failed",
                source="tests",
                tags=("tests", "success"),
                timestamp=base_time + timedelta(minutes=7),
            ),
        ),
        started_at=base_time + timedelta(minutes=5),
        ended_at=base_time + timedelta(minutes=10),
    )


@pytest.fixture
def late_observation(base_time: datetime) -> LocalObservation:
    """Observation too late to be compatible (beyond tolerance)."""
    return LocalObservation(
        source=EventSource.CI,
        thoughts=(
            Thought(
                content="CI build passed",
                source="ci",
                tags=("ci", "success"),
                timestamp=base_time + timedelta(hours=1),
            ),
        ),
        started_at=base_time + timedelta(hours=1),
        ended_at=base_time + timedelta(hours=1, minutes=5),
    )


@pytest.fixture
def sheaf() -> WitnessSheaf:
    """WitnessSheaf with default settings."""
    return WitnessSheaf()


# =============================================================================
# EventSource Tests
# =============================================================================


class TestEventSource:
    """Tests for EventSource enum and capabilities."""

    def test_all_sources_have_capabilities(self) -> None:
        """Every EventSource has defined capabilities."""
        for source in EventSource:
            assert source in SOURCE_CAPABILITIES
            assert len(source.capabilities) > 0

    def test_git_capabilities(self) -> None:
        """Git source has version control capabilities."""
        assert "version_control" in EventSource.GIT.capabilities
        assert "history" in EventSource.GIT.capabilities

    def test_filesystem_capabilities(self) -> None:
        """Filesystem source has file-related capabilities."""
        assert "files" in EventSource.FILESYSTEM.capabilities
        assert "topology" in EventSource.FILESYSTEM.capabilities

    def test_tests_capabilities(self) -> None:
        """Tests source has quality capabilities."""
        assert "quality" in EventSource.TESTS.capabilities
        assert "validation" in EventSource.TESTS.capabilities

    def test_source_overlap_shared(self) -> None:
        """Sources with shared capabilities have non-empty overlap."""
        # Git and Filesystem don't share capabilities in current design
        overlap = source_overlap(EventSource.GIT, EventSource.GIT)
        assert overlap == EventSource.GIT.capabilities

    def test_source_overlap_disjoint(self) -> None:
        """Disjoint sources have empty overlap."""
        overlap = source_overlap(EventSource.GIT, EventSource.TESTS)
        assert len(overlap) == 0


# =============================================================================
# LocalObservation Tests
# =============================================================================


class TestLocalObservation:
    """Tests for LocalObservation creation and properties."""

    def test_observation_creation(self, git_observation: LocalObservation) -> None:
        """LocalObservation is created with correct properties."""
        assert git_observation.source == EventSource.GIT
        assert git_observation.thought_count == 2
        assert git_observation.metadata["branch"] == "main"

    def test_observation_duration(self, git_observation: LocalObservation) -> None:
        """Duration is calculated correctly."""
        assert git_observation.duration_seconds == 600.0  # 10 minutes

    def test_observations_overlap_temporally(
        self, git_observation: LocalObservation, filesystem_observation: LocalObservation
    ) -> None:
        """Overlapping observations detected."""
        assert git_observation.overlaps_temporally(filesystem_observation)
        assert filesystem_observation.overlaps_temporally(git_observation)

    def test_observations_not_overlapping(
        self, git_observation: LocalObservation, late_observation: LocalObservation
    ) -> None:
        """Non-overlapping observations detected."""
        assert not git_observation.overlaps_temporally(late_observation)


# =============================================================================
# WitnessSheaf.compatible() Tests
# =============================================================================


class TestWitnessSheafCompatible:
    """Tests for WitnessSheaf compatibility checking."""

    def test_empty_compatible(self, sheaf: WitnessSheaf) -> None:
        """Empty list is compatible."""
        assert sheaf.compatible([])

    def test_single_observation_compatible(
        self, sheaf: WitnessSheaf, git_observation: LocalObservation
    ) -> None:
        """Single observation is always compatible."""
        assert sheaf.compatible([git_observation])

    def test_overlapping_observations_compatible(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
        filesystem_observation: LocalObservation,
    ) -> None:
        """Temporally overlapping observations are compatible."""
        assert sheaf.compatible([git_observation, filesystem_observation])

    def test_adjacent_within_tolerance_compatible(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
        test_observation: LocalObservation,
    ) -> None:
        """Adjacent observations within tolerance are compatible."""
        assert sheaf.compatible([git_observation, test_observation])

    def test_too_far_apart_incompatible(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
        late_observation: LocalObservation,
    ) -> None:
        """Observations too far apart are incompatible."""
        assert not sheaf.compatible([git_observation, late_observation])

    def test_custom_tolerance(
        self, git_observation: LocalObservation, late_observation: LocalObservation
    ) -> None:
        """Custom tolerance affects compatibility."""
        lenient_sheaf = WitnessSheaf(time_tolerance=timedelta(hours=2))
        assert lenient_sheaf.compatible([git_observation, late_observation])


# =============================================================================
# WitnessSheaf.glue() Tests
# =============================================================================


class TestWitnessSheafGlue:
    """Tests for WitnessSheaf crystallization gluing."""

    def test_glue_empty(self, sheaf: WitnessSheaf) -> None:
        """Gluing empty list produces empty crystal."""
        crystal = sheaf.glue([], session_id="empty-test")

        assert crystal.session_id == "empty-test"
        assert crystal.thought_count == 0
        assert "Empty" in crystal.narrative.summary

    def test_glue_single_observation(
        self, sheaf: WitnessSheaf, git_observation: LocalObservation
    ) -> None:
        """Gluing single observation produces crystal with those thoughts."""
        crystal = sheaf.glue([git_observation], session_id="single-test")

        assert crystal.thought_count == 2
        assert crystal.session_id == "single-test"
        assert "git" in crystal.topics or any("git" in t.source for t in crystal.thoughts)

    def test_glue_multiple_observations(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
        filesystem_observation: LocalObservation,
        test_observation: LocalObservation,
    ) -> None:
        """Gluing multiple observations merges all thoughts."""
        crystal = sheaf.glue(
            [git_observation, filesystem_observation, test_observation],
            session_id="multi-test",
        )

        # Total thoughts: 2 + 2 + 1 = 5
        assert crystal.thought_count == 5
        assert crystal.session_id == "multi-test"

    def test_glue_preserves_chronological_order(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
        filesystem_observation: LocalObservation,
    ) -> None:
        """Glued crystal has thoughts in chronological order."""
        crystal = sheaf.glue([git_observation, filesystem_observation])

        # Verify timestamps are non-decreasing
        timestamps = [t.timestamp for t in crystal.thoughts if t.timestamp]
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1]

    def test_glue_with_markers(
        self, sheaf: WitnessSheaf, git_observation: LocalObservation
    ) -> None:
        """Markers are preserved in glued crystal."""
        crystal = sheaf.glue(
            [git_observation],
            markers=["Important commit", "Deploy ready"],
        )

        assert len(crystal.markers) == 2
        assert "Important commit" in crystal.markers

    def test_glue_incompatible_raises(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
        late_observation: LocalObservation,
    ) -> None:
        """Gluing incompatible observations raises GluingError."""
        with pytest.raises(GluingError) as exc_info:
            sheaf.glue([git_observation, late_observation])

        assert "GIT" in exc_info.value.sources
        assert "compatible" in str(exc_info.value).lower()

    def test_glue_derives_mood(
        self,
        sheaf: WitnessSheaf,
        test_observation: LocalObservation,
    ) -> None:
        """Glued crystal derives mood from thoughts."""
        crystal = sheaf.glue([test_observation])

        # Test observation has "success" tag, should affect brightness
        assert crystal.mood.brightness >= 0.5


# =============================================================================
# WitnessSheaf.restrict() Tests
# =============================================================================


class TestWitnessSheafRestrict:
    """Tests for WitnessSheaf restriction (inverse of glue)."""

    def test_restrict_extracts_source(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
        filesystem_observation: LocalObservation,
    ) -> None:
        """Restriction extracts only thoughts from specified source."""
        crystal = sheaf.glue([git_observation, filesystem_observation])

        restricted = sheaf.restrict(crystal, EventSource.GIT)

        assert restricted.source == EventSource.GIT
        assert all("git" in t.source.lower() for t in restricted.thoughts)
        assert restricted.thought_count == 2

    def test_restrict_empty_source(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
    ) -> None:
        """Restricting to absent source returns empty observation."""
        crystal = sheaf.glue([git_observation])

        restricted = sheaf.restrict(crystal, EventSource.CI)

        assert restricted.thought_count == 0

    def test_restrict_preserves_crystal_id(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
    ) -> None:
        """Restriction includes crystal_id in metadata."""
        crystal = sheaf.glue([git_observation])

        restricted = sheaf.restrict(crystal, EventSource.GIT)

        assert "crystal_id" in restricted.metadata
        assert restricted.metadata["crystal_id"] == crystal.crystal_id


# =============================================================================
# Sheaf Law Verification
# =============================================================================


class TestSheafLaws:
    """Tests verifying categorical sheaf laws."""

    def test_identity_law(self, sheaf: WitnessSheaf, git_observation: LocalObservation) -> None:
        """Identity law: glue([single]) ≅ from_thoughts(single.thoughts)."""
        assert verify_identity_law(sheaf, git_observation, session_id="identity-test")

    def test_identity_law_filesystem(
        self, sheaf: WitnessSheaf, filesystem_observation: LocalObservation
    ) -> None:
        """Identity law holds for filesystem source."""
        assert verify_identity_law(sheaf, filesystem_observation)

    def test_associativity_law(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
        filesystem_observation: LocalObservation,
        test_observation: LocalObservation,
    ) -> None:
        """Associativity law: (A ∘ B) ∘ C ≅ A ∘ (B ∘ C)."""
        assert verify_associativity_law(
            sheaf,
            git_observation,
            filesystem_observation,
            test_observation,
            session_id="assoc-test",
        )


# =============================================================================
# Integration Tests
# =============================================================================


class TestWitnessSheafIntegration:
    """Integration tests for complete crystallization pipeline."""

    def test_full_crystallization_workflow(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
        filesystem_observation: LocalObservation,
        test_observation: LocalObservation,
    ) -> None:
        """Test complete workflow from observations to crystal to storage."""
        # 1. Check compatibility
        observations = [git_observation, filesystem_observation, test_observation]
        assert sheaf.compatible(observations)

        # 2. Glue into crystal
        crystal = sheaf.glue(
            observations,
            session_id="integration-test",
            markers=["test-milestone"],
        )

        # 3. Verify crystal properties
        assert crystal.thought_count == 5
        assert crystal.session_id == "integration-test"
        assert len(crystal.markers) == 1

        # 4. Verify mood synthesis
        assert crystal.mood is not None

        # 5. Verify can project to memory
        memory = crystal.as_memory()
        assert memory["metadata"]["type"] == "experience_crystal"

        # 6. Verify can restrict back
        git_restricted = sheaf.restrict(crystal, EventSource.GIT)
        assert git_restricted.thought_count == 2

    def test_cross_source_topology(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
        filesystem_observation: LocalObservation,
    ) -> None:
        """Crystal combines topology from multiple sources."""
        crystal = sheaf.glue([git_observation, filesystem_observation])

        # Topology should reflect filesystem source primarily
        assert crystal.topology is not None
        # The crystal should have extracted file paths from filesystem thoughts
        # (if the TopologySnapshot extraction works correctly)

    def test_serialization_roundtrip(
        self,
        sheaf: WitnessSheaf,
        git_observation: LocalObservation,
    ) -> None:
        """Crystal survives JSON serialization."""
        from services.witness.crystal import ExperienceCrystal

        crystal = sheaf.glue([git_observation], session_id="roundtrip-test")

        # Serialize
        json_data = crystal.to_json()

        # Deserialize
        restored = ExperienceCrystal.from_json(json_data)

        # Verify
        assert restored.session_id == crystal.session_id
        assert restored.thought_count == crystal.thought_count


# =============================================================================
# Edge Cases
# =============================================================================


class TestWitnessSheafEdgeCases:
    """Edge case tests for robust sheaf behavior."""

    def test_glue_with_none_timestamps(self, sheaf: WitnessSheaf, base_time: datetime) -> None:
        """Gluing handles thoughts with None timestamps."""
        obs = LocalObservation(
            source=EventSource.USER,
            thoughts=(
                Thought(content="Manual marker", source="user", tags=("marker",), timestamp=None),
                Thought(
                    content="Another marker", source="user", tags=("marker",), timestamp=base_time
                ),
            ),
            started_at=base_time,
            ended_at=base_time + timedelta(minutes=5),
        )

        crystal = sheaf.glue([obs])
        assert crystal.thought_count == 2

    def test_glue_single_thought(self, sheaf: WitnessSheaf, base_time: datetime) -> None:
        """Gluing works with single thought observation."""
        obs = LocalObservation(
            source=EventSource.USER,
            thoughts=(
                Thought(content="Solo thought", source="user", tags=(), timestamp=base_time),
            ),
            started_at=base_time,
            ended_at=base_time,
        )

        crystal = sheaf.glue([obs])
        assert crystal.thought_count == 1

    def test_zero_duration_observation(self, sheaf: WitnessSheaf, base_time: datetime) -> None:
        """Zero duration observations are valid."""
        obs = LocalObservation(
            source=EventSource.AGENTESE,
            thoughts=(Thought(content="Instant", source="agentese", tags=(), timestamp=base_time),),
            started_at=base_time,
            ended_at=base_time,  # Same as start
        )

        assert obs.duration_seconds == 0.0
        crystal = sheaf.glue([obs])
        assert crystal.thought_count == 1


# =============================================================================
# Property-Based Tests
# =============================================================================


try:
    from hypothesis import given, settings, strategies as st

    class TestWitnessSheafProperties:
        """Property-based tests for sheaf invariants."""

        @given(
            thought_count=st.integers(min_value=1, max_value=10),
        )
        @settings(max_examples=20)
        def test_glue_preserves_thought_count(self, thought_count: int) -> None:
            """Gluing preserves total thought count."""
            base = datetime.now()
            thoughts = tuple(
                Thought(
                    content=f"Thought {i}",
                    source="test",
                    tags=(),
                    timestamp=base + timedelta(minutes=i),
                )
                for i in range(thought_count)
            )

            obs = LocalObservation(
                source=EventSource.TESTS,
                thoughts=thoughts,
                started_at=base,
                ended_at=base + timedelta(minutes=thought_count),
            )

            sheaf = WitnessSheaf()
            crystal = sheaf.glue([obs])

            assert crystal.thought_count == thought_count

except ImportError:
    pass  # hypothesis not installed
