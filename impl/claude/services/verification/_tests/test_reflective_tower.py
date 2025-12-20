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
            violations=[{
                "type": "unimplemented_spec_path",
                "description": "Missing implementation",
                "severity": "error",
            }],
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
        await tower.add_artifact(LevelArtifact(
            artifact_id="a1",
            level=TowerLevel.CODE,
            name="Code 1",
            content={},
        ))
        await tower.add_artifact(LevelArtifact(
            artifact_id="a2",
            level=TowerLevel.CODE,
            name="Code 2",
            content={},
        ))
        await tower.add_artifact(LevelArtifact(
            artifact_id="a3",
            level=TowerLevel.SPEC,
            name="Spec 1",
            content={},
        ))

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
