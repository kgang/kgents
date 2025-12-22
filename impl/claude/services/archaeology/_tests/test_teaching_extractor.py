"""
Tests for CommitTeachingExtractor.

Verifies that commit messages are correctly parsed into TeachingMoments.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from services.archaeology.mining import Commit
from services.archaeology.teaching_extractor import (
    CommitTeaching,
    CommitTeachingExtractor,
    extract_teachings_from_commits,
    generate_teaching_report,
)


def make_commit(
    sha: str = "abc12345",
    message: str = "feat: Add new feature",
    files_changed: tuple[str, ...] = (),
    insertions: int = 10,
    deletions: int = 5,
) -> Commit:
    """Create a test commit."""
    return Commit(
        sha=sha,
        message=message,
        author="test@example.com",
        timestamp=datetime.now(timezone.utc),
        files_changed=files_changed,
        insertions=insertions,
        deletions=deletions,
    )


class TestCommitTeachingExtractor:
    """Test the main extraction class."""

    def test_extracts_from_fix_commit(self) -> None:
        """Fix commits should generate gotcha teachings."""
        commit = make_commit(
            message="fix(brain): Handle empty capture list",
            files_changed=("impl/claude/services/brain/persistence.py",),
            insertions=30,  # Medium churn for warning severity
            deletions=10,
        )
        extractor = CommitTeachingExtractor()
        teachings = extractor.extract_all([commit])

        assert len(teachings) == 1
        assert teachings[0].category == "gotcha"
        assert "brain" in teachings[0].teaching.insight.lower()
        assert teachings[0].teaching.severity == "warning"

    def test_extracts_from_revert_commit(self) -> None:
        """Revert commits should generate warning teachings."""
        commit = make_commit(
            message='Revert "Add complex caching layer"',
            files_changed=("impl/claude/services/cache.py",),
        )
        extractor = CommitTeachingExtractor()
        teachings = extractor.extract_all([commit])

        assert len(teachings) == 1
        assert teachings[0].category == "warning"
        assert teachings[0].teaching.severity == "critical"
        assert "revert" in teachings[0].teaching.insight.lower()

    def test_extracts_from_breaking_commit(self) -> None:
        """BREAKING: commits should generate critical teachings."""
        commit = make_commit(
            message="feat!: BREAKING: Remove deprecated API",
            files_changed=("impl/claude/protocols/api/routes.py",),
        )
        extractor = CommitTeachingExtractor()
        teachings = extractor.extract_all([commit])

        assert len(teachings) == 1
        assert teachings[0].category == "critical"
        assert teachings[0].teaching.severity == "critical"
        assert "breaking" in teachings[0].teaching.insight.lower()

    def test_extracts_from_refactor_with_many_files(self) -> None:
        """Refactors touching many files should generate decision teachings."""
        commit = make_commit(
            message="refactor(arch): Unify storage patterns",
            files_changed=(
                "impl/claude/services/brain/storage.py",
                "impl/claude/services/town/storage.py",
                "impl/claude/services/witness/storage.py",
                "impl/claude/agents/d/storage.py",
            ),
        )
        extractor = CommitTeachingExtractor()
        teachings = extractor.extract_all([commit])

        assert len(teachings) == 1
        assert teachings[0].category == "decision"
        assert "arch" in teachings[0].teaching.insight.lower()

    def test_ignores_small_refactors(self) -> None:
        """Small refactors (< 3 files) should not generate teachings."""
        commit = make_commit(
            message="refactor: Rename variable",
            files_changed=("impl/claude/utils.py",),
        )
        extractor = CommitTeachingExtractor()
        teachings = extractor.extract_all([commit])

        assert len(teachings) == 0

    def test_extracts_from_feat_with_tests(self) -> None:
        """Features with tests should generate pattern teachings."""
        commit = make_commit(
            message="feat(witness): Add mark lineage tracking",
            files_changed=(
                "impl/claude/services/witness/lineage.py",
                "impl/claude/services/witness/_tests/test_lineage.py",
            ),
        )
        extractor = CommitTeachingExtractor()
        teachings = extractor.extract_all([commit])

        assert len(teachings) == 1
        assert teachings[0].category == "pattern"
        assert "witness" in teachings[0].teaching.insight.lower()
        assert "test" in teachings[0].teaching.insight.lower()

    def test_ignores_feat_without_tests(self) -> None:
        """Features without tests should not generate pattern teachings."""
        commit = make_commit(
            message="feat: Add quick hack",
            files_changed=("impl/claude/hack.py",),
        )
        extractor = CommitTeachingExtractor()
        teachings = extractor.extract_all([commit])

        assert len(teachings) == 0

    def test_high_churn_fix_is_critical(self) -> None:
        """Fixes with high churn should be critical severity."""
        commit = make_commit(
            message="fix: Major bug in core system",
            files_changed=(
                "impl/claude/core/a.py",
                "impl/claude/core/b.py",
                "impl/claude/core/c.py",
                "impl/claude/core/d.py",
                "impl/claude/core/e.py",
                "impl/claude/core/f.py",
            ),
            insertions=150,
            deletions=50,
        )
        extractor = CommitTeachingExtractor()
        teachings = extractor.extract_all([commit])

        assert len(teachings) == 1
        assert teachings[0].teaching.severity == "critical"

    def test_low_churn_fix_is_info(self) -> None:
        """Fixes with low churn should be info severity."""
        commit = make_commit(
            message="fix: Typo in error message",
            files_changed=("impl/claude/messages.py",),
            insertions=1,
            deletions=1,
        )
        extractor = CommitTeachingExtractor()
        teachings = extractor.extract_all([commit])

        assert len(teachings) == 1
        assert teachings[0].teaching.severity == "info"


class TestExtractTeachingsFromCommits:
    """Test the convenience function."""

    def test_filters_by_min_churn(self) -> None:
        """Should filter commits below min_churn."""
        commits = [
            make_commit(message="fix: Small fix", insertions=5, deletions=3),
            make_commit(message="fix: Big fix", insertions=50, deletions=30),
        ]
        teachings = extract_teachings_from_commits(commits, min_churn=20)

        assert len(teachings) == 1
        assert teachings[0].commit.churn >= 20

    def test_extracts_multiple_categories(self) -> None:
        """Should extract teachings from multiple categories."""
        commits = [
            make_commit(message="fix: Bug fix"),
            make_commit(message='Revert "Bad idea"'),
            make_commit(
                message="refactor: Big refactor",
                files_changed=("a.py", "b.py", "c.py", "d.py"),
            ),
        ]
        teachings = extract_teachings_from_commits(commits)

        categories = {t.category for t in teachings}
        assert "gotcha" in categories
        assert "warning" in categories
        assert "decision" in categories


class TestGenerateTeachingReport:
    """Test the report generator."""

    def test_report_includes_header(self) -> None:
        """Report should include header."""
        teachings: list[CommitTeaching] = []
        report = generate_teaching_report(teachings)

        assert "Teaching Extraction Report" in report
        assert "Generated:" in report

    def test_report_includes_categories(self) -> None:
        """Report should include category sections."""
        commits = [
            make_commit(message="fix: Bug fix"),
            make_commit(message='Revert "Bad idea"'),
        ]
        teachings = extract_teachings_from_commits(commits)
        report = generate_teaching_report(teachings)

        assert "GOTCHA" in report
        assert "WARNING" in report

    def test_report_includes_feature_info(self) -> None:
        """Report should include feature information."""
        commits = [
            make_commit(
                message="fix(brain): Memory leak",
                files_changed=("impl/claude/services/brain/persistence.py",),
            ),
        ]
        teachings = extract_teachings_from_commits(commits)
        report = generate_teaching_report(teachings)

        assert "Brain" in report

    def test_empty_teachings_produces_report(self) -> None:
        """Empty teachings should still produce a valid report."""
        report = generate_teaching_report([])

        assert "Teaching Extraction Report" in report
        assert "Total teachings: 0" in report


class TestCommitTeaching:
    """Test the CommitTeaching dataclass."""

    def test_has_required_fields(self) -> None:
        """CommitTeaching should have all required fields."""
        commit = make_commit(message="fix: Test")
        extractor = CommitTeachingExtractor()
        teachings = extractor.extract_all([commit])

        assert len(teachings) == 1
        teaching = teachings[0]

        # All fields should be present
        assert teaching.teaching is not None
        assert teaching.commit is not None
        assert teaching.features is not None
        assert teaching.category is not None

    def test_teaching_has_evidence(self) -> None:
        """Teaching moments should have evidence from commit."""
        commit = make_commit(sha="abc12345", message="fix: Test fix")
        extractor = CommitTeachingExtractor()
        teachings = extractor.extract_all([commit])

        assert len(teachings) == 1
        assert teachings[0].teaching.evidence is not None
        assert "abc12345" in teachings[0].teaching.evidence
        assert teachings[0].teaching.commit == "abc12345"
