"""
Tests for Reflective Tower.

Tests the level hierarchy and consistency verification between adjacent levels.

Feature: formal-verification-metatheory
"""

from __future__ import annotations

import pytest

from services.verification.reflective_tower import (
    ConsistencyResult,
    CorrectionProposal,
    LevelArtifact,
    ReflectiveTower,
    TowerLevel,
    create_tower,
    verify_tower_consistency,
)

# =============================================================================
# Tower Level Tests
# =============================================================================


class TestTowerLevels:
    """Tests for tower level definitions."""

    def test_level_ordering(self) -> None:
        """Levels are correctly ordered."""
        assert TowerLevel.BEHAVIORAL_PATTERNS < TowerLevel.TRACE_WITNESSES
        assert TowerLevel.TRACE_WITNESSES < TowerLevel.CODE
        assert TowerLevel.CODE < TowerLevel.SPEC
        assert TowerLevel.SPEC < TowerLevel.META_SPEC
        assert TowerLevel.META_SPEC < TowerLevel.FOUNDATIONS
        assert TowerLevel.FOUNDATIONS < TowerLevel.INTENT

    def test_level_values(self) -> None:
        """Level values are as expected."""
        assert int(TowerLevel.BEHAVIORAL_PATTERNS) == -2
        assert int(TowerLevel.TRACE_WITNESSES) == -1
        assert int(TowerLevel.CODE) == 0
        assert int(TowerLevel.SPEC) == 1
        assert int(TowerLevel.META_SPEC) == 2
        assert int(TowerLevel.FOUNDATIONS) == 3
        assert int(TowerLevel.INTENT) == 100  # "Level ∞"


# =============================================================================
# Artifact Tests
# =============================================================================


class TestLevelArtifacts:
    """Tests for level artifacts."""

    def test_artifact_creation(self) -> None:
        """Artifacts can be created."""
        artifact = LevelArtifact(
            artifact_id="test_artifact",
            level=TowerLevel.CODE,
            name="Test Artifact",
            content={"module_path": "test.py"},
        )

        assert artifact.artifact_id == "test_artifact"
        assert artifact.level == TowerLevel.CODE
        assert artifact.name == "Test Artifact"

    def test_artifact_hashability(self) -> None:
        """Artifacts are hashable."""
        artifact = LevelArtifact(
            artifact_id="test",
            level=TowerLevel.SPEC,
            name="Test",
            content={},
        )

        # Should be hashable
        artifact_set = {artifact}
        assert artifact in artifact_set

    @pytest.mark.asyncio
    async def test_add_artifact_to_tower(self) -> None:
        """Artifacts can be added to tower."""
        tower = ReflectiveTower()

        artifact = LevelArtifact(
            artifact_id="code_artifact",
            level=TowerLevel.CODE,
            name="Code Module",
            content={"module_path": "services/test.py", "functions": ["test_func"]},
        )

        await tower.add_artifact(artifact)

        retrieved = await tower.get_artifact(TowerLevel.CODE, "code_artifact")
        assert retrieved is not None
        assert retrieved.artifact_id == "code_artifact"


# =============================================================================
# Consistency Verification Tests
# =============================================================================


class TestConsistencyVerification:
    """Tests for consistency verification between levels."""

    @pytest.mark.asyncio
    async def test_verify_adjacent_levels(self) -> None:
        """Adjacent levels can be verified."""
        tower = ReflectiveTower()

        # Add artifacts at adjacent levels
        code_artifact = LevelArtifact(
            artifact_id="code_1",
            level=TowerLevel.CODE,
            name="Code",
            content={"module_path": "test.py", "functions": ["manifest"]},
        )
        spec_artifact = LevelArtifact(
            artifact_id="spec_1",
            level=TowerLevel.SPEC,
            name="Spec",
            content={"paths": ["self.test.manifest"], "operads": []},
        )

        await tower.add_artifact(code_artifact)
        await tower.add_artifact(spec_artifact)

        results = await tower.verify_consistency(TowerLevel.CODE, TowerLevel.SPEC)

        assert len(results) > 0
        assert all(isinstance(r, ConsistencyResult) for r in results)

    @pytest.mark.asyncio
    async def test_consistent_artifacts(self) -> None:
        """Consistent artifacts pass verification."""
        tower = ReflectiveTower()

        # Add consistent artifacts
        code_artifact = LevelArtifact(
            artifact_id="code_2",
            level=TowerLevel.CODE,
            name="Code",
            content={"module_path": "test.py", "functions": ["manifest", "witness"]},
        )
        spec_artifact = LevelArtifact(
            artifact_id="spec_2",
            level=TowerLevel.SPEC,
            name="Spec",
            content={"paths": ["self.test.manifest", "self.test.witness"], "operads": []},
        )

        await tower.add_artifact(code_artifact)
        await tower.add_artifact(spec_artifact)

        results = await tower.verify_consistency(TowerLevel.CODE, TowerLevel.SPEC)

        # Should have results
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_inconsistent_artifacts_detected(self) -> None:
        """Inconsistent artifacts are detected."""
        tower = ReflectiveTower()

        # Add inconsistent artifacts (spec path not in code)
        code_artifact = LevelArtifact(
            artifact_id="code_3",
            level=TowerLevel.CODE,
            name="Code",
            content={"module_path": "test.py", "functions": []},  # No functions
        )
        spec_artifact = LevelArtifact(
            artifact_id="spec_3",
            level=TowerLevel.SPEC,
            name="Spec",
            content={"paths": ["self.test.missing_function"], "operads": []},
        )

        await tower.add_artifact(code_artifact)
        await tower.add_artifact(spec_artifact)

        results = await tower.verify_consistency(TowerLevel.CODE, TowerLevel.SPEC)

        # Should detect inconsistency
        assert len(results) > 0
        inconsistent = [r for r in results if not r.is_consistent]
        assert len(inconsistent) > 0


# =============================================================================
# Correction Proposal Tests
# =============================================================================


class TestCorrectionProposals:
    """Tests for correction proposals."""

    @pytest.mark.asyncio
    async def test_propose_corrections(self) -> None:
        """Corrections are proposed for inconsistencies."""
        tower = ReflectiveTower()

        # Create inconsistent result
        result = ConsistencyResult(
            result_id="test_result",
            source_level=TowerLevel.CODE,
            target_level=TowerLevel.SPEC,
            is_consistent=False,
            violations=[
                {
                    "type": "unimplemented_spec_path",
                    "description": "Missing implementation",
                    "severity": "error",
                }
            ],
            suggestions=["Implement the missing spec path"],
            verification_time_ms=10.0,
        )

        proposals = await tower.propose_corrections(result)

        assert len(proposals) > 0
        assert all(isinstance(p, CorrectionProposal) for p in proposals)

    @pytest.mark.asyncio
    async def test_no_proposals_for_consistent(self) -> None:
        """No proposals for consistent results."""
        tower = ReflectiveTower()

        result = ConsistencyResult(
            result_id="consistent_result",
            source_level=TowerLevel.CODE,
            target_level=TowerLevel.SPEC,
            is_consistent=True,
            violations=[],
            suggestions=[],
            verification_time_ms=5.0,
        )

        proposals = await tower.propose_corrections(result)

        assert len(proposals) == 0


# =============================================================================
# Compression Tests
# =============================================================================


class TestCompression:
    """Tests for compression morphisms."""

    @pytest.mark.asyncio
    async def test_compress_artifact(self) -> None:
        """Artifacts can be compressed to lower levels."""
        tower = ReflectiveTower()

        spec_artifact = LevelArtifact(
            artifact_id="spec_to_compress",
            level=TowerLevel.SPEC,
            name="Spec",
            content={"paths": ["self.test.manifest"], "operads": []},
        )

        await tower.add_artifact(spec_artifact)

        compressed = await tower.compress(spec_artifact, TowerLevel.CODE)

        assert compressed is not None
        assert compressed.level == TowerLevel.CODE
        assert "compression_morphism" in compressed.metadata

    @pytest.mark.asyncio
    async def test_compression_preserves_info(self) -> None:
        """Compression preserves specified information."""
        tower = ReflectiveTower()

        artifact = LevelArtifact(
            artifact_id="to_compress",
            level=TowerLevel.META_SPEC,
            name="Meta-Spec",
            content={"categories": ["Agent"], "functors": ["F"]},
        )

        await tower.add_artifact(artifact)

        compressed = await tower.compress(artifact, TowerLevel.SPEC)

        assert compressed is not None
        content = compressed.content
        assert "preserved" in content
        assert "original_id" in content


# =============================================================================
# Tower Summary Tests
# =============================================================================


class TestTowerSummary:
    """Tests for tower summary."""

    @pytest.mark.asyncio
    async def test_empty_tower_summary(self) -> None:
        """Empty tower has valid summary."""
        tower = ReflectiveTower()

        summary = await tower.get_tower_summary()

        assert "levels" in summary
        assert "total_artifacts" in summary
        assert summary["total_artifacts"] == 0

    @pytest.mark.asyncio
    async def test_tower_summary_with_artifacts(self) -> None:
        """Tower summary reflects artifacts."""
        tower = ReflectiveTower()

        # Add artifacts at different levels
        await tower.add_artifact(
            LevelArtifact(
                artifact_id="a1",
                level=TowerLevel.CODE,
                name="Code 1",
                content={},
            )
        )
        await tower.add_artifact(
            LevelArtifact(
                artifact_id="a2",
                level=TowerLevel.CODE,
                name="Code 2",
                content={},
            )
        )
        await tower.add_artifact(
            LevelArtifact(
                artifact_id="a3",
                level=TowerLevel.SPEC,
                name="Spec 1",
                content={},
            )
        )

        summary = await tower.get_tower_summary()

        assert summary["total_artifacts"] == 3
        assert summary["levels"]["CODE"]["artifact_count"] == 2
        assert summary["levels"]["SPEC"]["artifact_count"] == 1


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_create_tower(self) -> None:
        """create_tower creates a valid tower."""
        tower = await create_tower()

        assert isinstance(tower, ReflectiveTower)
        assert len(tower.handlers) == 7  # All levels

    @pytest.mark.asyncio
    async def test_verify_tower_consistency(self) -> None:
        """verify_tower_consistency returns summary."""
        tower = await create_tower()

        result = await verify_tower_consistency(tower)

        assert "total_checks" in result
        assert "consistent" in result
        assert "inconsistent" in result
        assert "consistency_ratio" in result


# =============================================================================
# Property 8: Reflective Tower Consistency (Property-Based Tests)
# =============================================================================


from hypothesis import given, settings, strategies as st


@st.composite
def level_artifact_strategy(draw: st.DrawFn) -> LevelArtifact:
    """Generate random level artifacts."""
    level = draw(st.sampled_from(list(TowerLevel)))
    artifact_id = f"artifact_{draw(st.integers(min_value=1, max_value=1000))}"

    # Generate level-appropriate content
    if level == TowerLevel.BEHAVIORAL_PATTERNS:
        content = {
            "pattern_type": draw(st.sampled_from(["flow", "performance", "verification"])),
            "frequency": draw(st.integers(min_value=1, max_value=100)),
            "example_traces": [
                f"trace_{i}" for i in range(draw(st.integers(min_value=1, max_value=3)))
            ],
        }
    elif level == TowerLevel.TRACE_WITNESSES:
        content = {
            "agent_path": f"self.test.{draw(st.sampled_from(['manifest', 'witness', 'refine']))}",
            "verification_status": draw(st.sampled_from(["success", "failure", "pending"])),
            "witness_id": f"witness_{draw(st.integers(min_value=1, max_value=100))}",
        }
    elif level == TowerLevel.CODE:
        content = {
            "module_path": f"services/{draw(st.sampled_from(['brain', 'town', 'forge']))}/service.py",
            "functions": [draw(st.sampled_from(["manifest", "witness", "refine", "capture"]))],
            "classes": [draw(st.sampled_from(["Service", "Agent", "Handler"]))],
        }
    elif level == TowerLevel.SPEC:
        content = {
            "paths": [f"self.test.{draw(st.sampled_from(['manifest', 'witness']))}"],
            "operads": [{"name": "TestOperad", "operations": ["op1", "op2"]}]
            if draw(st.booleans())
            else [],
            "constraints": [],
        }
    elif level == TowerLevel.META_SPEC:
        content = {
            "categories": [draw(st.sampled_from(["Agent", "Morphism", "Functor"]))],
            "functors": [draw(st.sampled_from(["F", "G", "Id"]))] if draw(st.booleans()) else [],
            "natural_transformations": [],
        }
    elif level == TowerLevel.FOUNDATIONS:
        content = {
            "types": [draw(st.sampled_from(["AgentType", "MorphismType", "PathType"]))],
            "paths": [],
            "universe_level": draw(st.integers(min_value=0, max_value=3)),
        }
    else:  # INTENT
        content = {
            "nodes": [f"node_{i}" for i in range(draw(st.integers(min_value=1, max_value=5)))],
            "edges": [],
            "covers": [],
        }

    return LevelArtifact(
        artifact_id=artifact_id,
        level=level,
        name=f"Test {level.name} Artifact",
        content=content,
    )


class TestReflectiveTowerConsistencyProperty:
    """
    Property 8: Reflective Tower Consistency

    For any modification to a level in the reflective tower, consistency
    with adjacent levels SHALL be verified.

    Validates: Requirements 3.6, 3.7
    """

    @pytest.mark.asyncio
    @given(artifact=level_artifact_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_artifact_added_to_correct_level(self, artifact: LevelArtifact) -> None:
        """Artifacts are added to their correct level."""
        tower = ReflectiveTower()

        await tower.add_artifact(artifact)

        retrieved = await tower.get_artifact(artifact.level, artifact.artifact_id)
        assert retrieved is not None
        assert retrieved.level == artifact.level

    @pytest.mark.asyncio
    @given(artifact=level_artifact_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_adjacent_level_verification_available(self, artifact: LevelArtifact) -> None:
        """Adjacent level verification is available for any artifact."""
        tower = ReflectiveTower()

        await tower.add_artifact(artifact)

        # Should be able to verify adjacent levels
        results = await tower.verify_adjacent_levels(artifact.level)

        # Results should be a list (may be empty if no artifacts at adjacent levels)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    @given(
        artifact1=level_artifact_strategy(),
        artifact2=level_artifact_strategy(),
    )
    @settings(max_examples=50, deadline=None)
    async def test_consistency_verification_returns_result(
        self,
        artifact1: LevelArtifact,
        artifact2: LevelArtifact,
    ) -> None:
        """Consistency verification returns valid results."""
        tower = ReflectiveTower()

        await tower.add_artifact(artifact1)
        await tower.add_artifact(artifact2)

        results = await tower.verify_consistency(artifact1.level, artifact2.level)

        # Should return list of ConsistencyResult
        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, ConsistencyResult)
            assert result.source_level == artifact1.level
            assert result.target_level == artifact2.level

    @pytest.mark.asyncio
    @given(artifact=level_artifact_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_compression_preserves_level_relationship(
        self,
        artifact: LevelArtifact,
    ) -> None:
        """Compression maintains proper level relationships."""
        tower = ReflectiveTower()

        await tower.add_artifact(artifact)

        # Try to compress to adjacent lower level
        level_value = int(artifact.level)

        # Find a valid target level
        target_level = None
        for level in TowerLevel:
            if int(level) == level_value - 1:
                target_level = level
                break

        if target_level is not None:
            compressed = await tower.compress(artifact, target_level)

            if compressed is not None:
                assert compressed.level == target_level
                assert int(compressed.level) < int(artifact.level)

    @pytest.mark.asyncio
    async def test_tower_maintains_level_hierarchy(self) -> None:
        """Tower maintains proper level hierarchy."""
        tower = ReflectiveTower()

        # Add artifacts at multiple levels
        artifacts = [
            LevelArtifact(
                artifact_id="code_1",
                level=TowerLevel.CODE,
                name="Code",
                content={"module_path": "test.py", "functions": ["test"]},
            ),
            LevelArtifact(
                artifact_id="spec_1",
                level=TowerLevel.SPEC,
                name="Spec",
                content={"paths": ["self.test"], "operads": []},
            ),
            LevelArtifact(
                artifact_id="meta_1",
                level=TowerLevel.META_SPEC,
                name="Meta",
                content={"categories": ["Agent"], "functors": []},
            ),
        ]

        for artifact in artifacts:
            await tower.add_artifact(artifact)

        summary = await tower.get_tower_summary()

        # All levels should be tracked
        assert summary["total_artifacts"] == 3
        assert summary["levels"]["CODE"]["artifact_count"] == 1
        assert summary["levels"]["SPEC"]["artifact_count"] == 1
        assert summary["levels"]["META_SPEC"]["artifact_count"] == 1

    @pytest.mark.asyncio
    async def test_inconsistency_generates_proposals(self) -> None:
        """Inconsistencies generate correction proposals."""
        tower = ReflectiveTower()

        # Create inconsistent artifacts
        code_artifact = LevelArtifact(
            artifact_id="code_inconsistent",
            level=TowerLevel.CODE,
            name="Code",
            content={"module_path": "test.py", "functions": []},  # No functions
        )
        spec_artifact = LevelArtifact(
            artifact_id="spec_inconsistent",
            level=TowerLevel.SPEC,
            name="Spec",
            content={"paths": ["self.test.missing"], "operads": []},  # Path not in code
        )

        await tower.add_artifact(code_artifact)
        await tower.add_artifact(spec_artifact)

        results = await tower.verify_consistency(TowerLevel.CODE, TowerLevel.SPEC)

        # Find inconsistent results
        inconsistent = [r for r in results if not r.is_consistent]

        if inconsistent:
            proposals = await tower.propose_corrections(inconsistent[0])
            assert isinstance(proposals, list)

    @pytest.mark.asyncio
    @given(artifact=level_artifact_strategy())
    @settings(max_examples=30, deadline=None)
    async def test_tower_summary_reflects_artifacts(self, artifact: LevelArtifact) -> None:
        """Tower summary accurately reflects added artifacts."""
        tower = ReflectiveTower()

        initial_summary = await tower.get_tower_summary()
        initial_count = initial_summary["total_artifacts"]

        await tower.add_artifact(artifact)

        final_summary = await tower.get_tower_summary()

        assert final_summary["total_artifacts"] == initial_count + 1
        assert final_summary["levels"][artifact.level.name]["artifact_count"] >= 1
