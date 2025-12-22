"""
Tests for Witness Bridge: CommitTeaching → Mark transformation.

Phase 5 of Git Archaeology Backfill: Witness Integration.

See: services/archaeology/witness_bridge.py
"""

from __future__ import annotations

from datetime import datetime

import pytest

from services.archaeology.mining import Commit
from services.archaeology.teaching_extractor import CommitTeaching
from services.archaeology.witness_bridge import (
    ARCHAEOLOGY_LINEAGE_TAG,
    ARCHAEOLOGY_ORIGIN,
    CrystallizationResult,
    generate_crystallization_report,
    generate_deterministic_mark_id,
    teaching_to_mark,
)
from services.living_docs.types import TeachingMoment
from services.witness.mark import EvidenceTier, Mark

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_commit() -> Commit:
    """Create a sample commit for testing."""
    return Commit(
        sha="abc123def456",
        message="fix(brain): Handle empty capture list",
        author="Kent Gang",
        timestamp=datetime(2025, 1, 15, 10, 30, 0),
        files_changed=("services/brain/core.py", "services/brain/_tests/test_core.py"),
        insertions=50,
        deletions=10,
    )


@pytest.fixture
def sample_teaching(sample_commit: Commit) -> CommitTeaching:
    """Create a sample CommitTeaching for testing."""
    return CommitTeaching(
        teaching=TeachingMoment(
            insight="Bug fixed in brain: Handle empty capture list",
            severity="warning",
            evidence="commit:abc123de",
            commit="abc123de",
        ),
        commit=sample_commit,
        features=("brain", "memory"),
        category="gotcha",
    )


@pytest.fixture
def sample_revert_teaching() -> CommitTeaching:
    """Create a sample revert teaching for testing."""
    commit = Commit(
        sha="def456abc789",
        message='Revert "Add experimental caching"',
        author="Claude",
        timestamp=datetime(2025, 1, 16, 14, 0, 0),
        files_changed=("services/brain/cache.py",),
        insertions=5,
        deletions=100,
    )
    return CommitTeaching(
        teaching=TeachingMoment(
            insight="Approach reverted: Add experimental caching. The implementation did not work as expected.",
            severity="critical",
            evidence="revert:commit:def456ab",
            commit="def456ab",
        ),
        commit=commit,
        features=("brain",),
        category="warning",
    )


# =============================================================================
# Test teaching_to_mark
# =============================================================================


class TestTeachingToMark:
    """Tests for teaching_to_mark transformation."""

    def test_basic_transformation(self, sample_teaching: CommitTeaching) -> None:
        """Test basic CommitTeaching → Mark transformation."""
        mark = teaching_to_mark(sample_teaching)

        assert isinstance(mark, Mark)
        assert mark.origin == ARCHAEOLOGY_ORIGIN
        assert ARCHAEOLOGY_LINEAGE_TAG in mark.tags

    def test_mark_has_genealogical_evidence(self, sample_teaching: CommitTeaching) -> None:
        """Mark should have GENEALOGICAL evidence tier."""
        mark = teaching_to_mark(sample_teaching)

        assert mark.proof is not None
        assert mark.proof.tier == EvidenceTier.GENEALOGICAL

    def test_mark_contains_commit_sha(self, sample_teaching: CommitTeaching) -> None:
        """Mark should contain commit SHA in metadata and proof."""
        mark = teaching_to_mark(sample_teaching)

        assert "commit_sha" in mark.metadata
        assert mark.metadata["commit_sha"] == sample_teaching.commit.sha
        assert sample_teaching.commit.sha[:8] in mark.proof.data

    def test_mark_preserves_insight(self, sample_teaching: CommitTeaching) -> None:
        """Mark should preserve the teaching insight in response."""
        mark = teaching_to_mark(sample_teaching)

        assert mark.response.content == sample_teaching.teaching.insight

    def test_mark_has_category_tag(self, sample_teaching: CommitTeaching) -> None:
        """Mark should have the category as a tag."""
        mark = teaching_to_mark(sample_teaching)

        assert sample_teaching.category in mark.tags

    def test_mark_has_severity_tag(self, sample_teaching: CommitTeaching) -> None:
        """Mark should have severity as a tag."""
        mark = teaching_to_mark(sample_teaching)

        severity_tag = f"severity:{sample_teaching.teaching.severity}"
        assert severity_tag in mark.tags

    def test_mark_preserves_features(self, sample_teaching: CommitTeaching) -> None:
        """Mark should preserve affected features in metadata."""
        mark = teaching_to_mark(sample_teaching)

        assert "features" in mark.metadata
        assert mark.metadata["features"] == list(sample_teaching.features)

    def test_mark_preserves_timestamp(self, sample_teaching: CommitTeaching) -> None:
        """Mark should use commit timestamp."""
        mark = teaching_to_mark(sample_teaching)

        assert mark.timestamp == sample_teaching.commit.timestamp

    def test_mark_phase_is_reflect(self, sample_teaching: CommitTeaching) -> None:
        """Mark should be in REFLECT phase (archaeological analysis)."""
        from services.witness.mark import NPhase

        mark = teaching_to_mark(sample_teaching)

        assert mark.phase == NPhase.REFLECT

    def test_critical_teaching_has_ethical_principle(
        self, sample_revert_teaching: CommitTeaching
    ) -> None:
        """Critical teachings should have 'ethical' principle."""
        mark = teaching_to_mark(sample_revert_teaching)

        assert mark.proof is not None
        assert "ethical" in mark.proof.principles


# =============================================================================
# Test generate_deterministic_mark_id
# =============================================================================


class TestDeterministicMarkId:
    """Tests for deterministic mark ID generation."""

    def test_deterministic_same_input(self, sample_teaching: CommitTeaching) -> None:
        """Same teaching should produce same mark ID."""
        id1 = generate_deterministic_mark_id(sample_teaching)
        id2 = generate_deterministic_mark_id(sample_teaching)

        assert id1 == id2

    def test_different_teachings_different_ids(
        self, sample_teaching: CommitTeaching, sample_revert_teaching: CommitTeaching
    ) -> None:
        """Different teachings should produce different mark IDs."""
        id1 = generate_deterministic_mark_id(sample_teaching)
        id2 = generate_deterministic_mark_id(sample_revert_teaching)

        assert id1 != id2

    def test_id_format(self, sample_teaching: CommitTeaching) -> None:
        """Mark ID should follow arch-{sha[:8]}-{hash[:8]} pattern."""
        mark_id = generate_deterministic_mark_id(sample_teaching)

        assert mark_id.startswith("arch-")
        parts = str(mark_id).split("-")
        assert len(parts) == 3
        assert parts[1] == sample_teaching.commit.sha[:8]

    def test_id_stable_across_time(self, sample_teaching: CommitTeaching) -> None:
        """ID should not change based on current time."""
        import time

        id1 = generate_deterministic_mark_id(sample_teaching)
        time.sleep(0.01)
        id2 = generate_deterministic_mark_id(sample_teaching)

        assert id1 == id2


# =============================================================================
# Test CrystallizationResult
# =============================================================================


class TestCrystallizationResult:
    """Tests for CrystallizationResult dataclass."""

    def test_result_creation(self) -> None:
        """Test basic result creation."""
        result = CrystallizationResult(
            total_teachings=10,
            marks_created=8,
            marks_skipped=2,
            errors=[],
            mark_ids=["arch-abc-123", "arch-def-456"],
        )

        assert result.total_teachings == 10
        assert result.marks_created == 8
        assert result.marks_skipped == 2
        assert len(result.errors) == 0
        assert len(result.mark_ids) == 2

    def test_result_with_errors(self) -> None:
        """Test result with errors."""
        result = CrystallizationResult(
            total_teachings=10,
            marks_created=7,
            marks_skipped=0,
            errors=["Error 1", "Error 2", "Error 3"],
            mark_ids=["arch-abc-123"],
        )

        assert len(result.errors) == 3
        # marks_created + skipped + errors = total_teachings (approximately)


# =============================================================================
# Test generate_crystallization_report
# =============================================================================


class TestCrystallizationReport:
    """Tests for crystallization report generation."""

    def test_report_generation(self) -> None:
        """Test report generation."""
        result = CrystallizationResult(
            total_teachings=10,
            marks_created=8,
            marks_skipped=2,
            errors=[],
            mark_ids=["arch-abc-123", "arch-def-456"],
        )

        report = generate_crystallization_report(result)

        assert "Archaeological Crystallization Report" in report
        assert "10" in report  # total_teachings
        assert "8" in report  # marks_created
        assert "2" in report  # marks_skipped

    def test_report_with_errors(self) -> None:
        """Test report includes errors."""
        result = CrystallizationResult(
            total_teachings=10,
            marks_created=7,
            marks_skipped=0,
            errors=["Failed to process commit abc123"],
            mark_ids=[],
        )

        report = generate_crystallization_report(result)

        assert "Errors:" in report
        assert "abc123" in report

    def test_report_with_many_errors_truncates(self) -> None:
        """Test report truncates when many errors."""
        errors = [f"Error {i}" for i in range(20)]
        result = CrystallizationResult(
            total_teachings=20,
            marks_created=0,
            marks_skipped=0,
            errors=errors,
            mark_ids=[],
        )

        report = generate_crystallization_report(result)

        # Should show first 10 errors, then "... and N more"
        assert "... and" in report or "10" in report


# =============================================================================
# Test Principle Inference
# =============================================================================


class TestPrincipleInference:
    """Tests for principle inference from teachings."""

    def test_gotcha_has_ethical(self, sample_teaching: CommitTeaching) -> None:
        """Gotchas should have 'ethical' principle (learning from mistakes)."""
        mark = teaching_to_mark(sample_teaching)

        assert mark.proof is not None
        assert "ethical" in mark.proof.principles

    def test_pattern_has_composable_and_generative(self) -> None:
        """Patterns should have 'composable' and 'generative' principles."""
        commit = Commit(
            sha="pattern123",
            message="feat(brain): Add crystal composition API with tests",
            author="Kent",
            timestamp=datetime.now(),
            files_changed=("services/brain/crystal.py", "services/brain/_tests/test_crystal.py"),
            insertions=200,
            deletions=20,
        )
        teaching = CommitTeaching(
            teaching=TeachingMoment(
                insight="New pattern (brain): Add crystal composition API - includes test coverage",
                severity="info",
                evidence="feat+test:commit:pattern1",
                commit="pattern1",
            ),
            commit=commit,
            features=("brain",),
            category="pattern",
        )

        mark = teaching_to_mark(teaching)

        assert mark.proof is not None
        assert "composable" in mark.proof.principles
        assert "generative" in mark.proof.principles

    def test_decision_has_tasteful(self) -> None:
        """Decisions should have 'tasteful' principle."""
        commit = Commit(
            sha="refactor123",
            message="refactor(witness): Simplify trust model",
            author="Kent",
            timestamp=datetime.now(),
            files_changed=("a.py", "b.py", "c.py", "d.py"),  # Multi-file = decision
            insertions=100,
            deletions=150,
        )
        teaching = CommitTeaching(
            teaching=TeachingMoment(
                insight="Architectural decision (witness): Simplify trust model",
                severity="info",
                evidence="refactor:commit:refacto",
                commit="refacto",
            ),
            commit=commit,
            features=("witness",),
            category="decision",
        )

        mark = teaching_to_mark(teaching)

        assert mark.proof is not None
        assert "tasteful" in mark.proof.principles


# =============================================================================
# Test Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_features(self) -> None:
        """Test teaching with no features."""
        commit = Commit(
            sha="abc123",
            message="fix: General cleanup",
            author="Kent",
            timestamp=datetime.now(),
            files_changed=(),
            insertions=10,
            deletions=5,
        )
        teaching = CommitTeaching(
            teaching=TeachingMoment(
                insight="General fix",
                severity="info",
                evidence="commit:abc123",
                commit="abc123",
            ),
            commit=commit,
            features=("general",),  # Default when no features matched
            category="gotcha",
        )

        mark = teaching_to_mark(teaching)

        assert mark.metadata["features"] == ["general"]

    def test_long_insight_in_proof(self) -> None:
        """Test teaching with very long insight."""
        long_insight = "A" * 1000
        commit = Commit(
            sha="abc123",
            message="fix: " + "A" * 200,
            author="Kent",
            timestamp=datetime.now(),
            files_changed=("file.py",),
            insertions=10,
            deletions=5,
        )
        teaching = CommitTeaching(
            teaching=TeachingMoment(
                insight=long_insight,
                severity="info",
                evidence="commit:abc123",
                commit="abc123",
            ),
            commit=commit,
            features=("general",),
            category="gotcha",
        )

        mark = teaching_to_mark(teaching)

        # Should not truncate - the insight is preserved
        assert mark.response.content == long_insight
        assert mark.proof.claim == long_insight

    def test_special_characters_in_insight(self) -> None:
        """Test teaching with special characters."""
        special_insight = 'Fix: Handle "quotes" and <angle> brackets & ampersands'
        commit = Commit(
            sha="abc123",
            message=special_insight,
            author="Kent",
            timestamp=datetime.now(),
            files_changed=("file.py",),
            insertions=10,
            deletions=5,
        )
        teaching = CommitTeaching(
            teaching=TeachingMoment(
                insight=special_insight,
                severity="info",
                evidence="commit:abc123",
                commit="abc123",
            ),
            commit=commit,
            features=("general",),
            category="gotcha",
        )

        mark = teaching_to_mark(teaching)

        assert mark.response.content == special_insight
