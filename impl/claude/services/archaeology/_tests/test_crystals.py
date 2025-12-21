"""
Tests for crystals.py - HistoryCrystal generation for Brain.

Tests cover:
- HistoryCrystal generation from trajectories
- Emotional valence calculation
- Lesson extraction
- Brain format conversion
- Report generation
"""

from datetime import datetime, timedelta, timezone

import pytest

from services.archaeology.classifier import FeatureStatus, FeatureTrajectory
from services.archaeology.crystals import (
    HistoryCrystal,
    generate_all_crystals,
    generate_crystal_report,
    generate_history_crystal,
)
from services.archaeology.mining import Commit
from services.archaeology.patterns import FeaturePattern

# Fixtures


def make_commit(
    sha: str = "abc123",
    message: str = "feat: add feature",
    files: tuple[str, ...] = ("src/foo.py",),
    days_ago: int = 0,
    insertions: int = 50,
    deletions: int = 10,
) -> Commit:
    """Create a test commit."""
    return Commit(
        sha=sha,
        message=message,
        author="test@example.com",
        timestamp=datetime.now(timezone.utc) - timedelta(days=days_ago),
        files_changed=files,
        insertions=insertions,
        deletions=deletions,
    )


def make_trajectory(
    name: str,
    status: FeatureStatus,
    commit_count: int = 10,
    has_tests: bool = True,
    test_count: int = 5,
    days_old: int = 30,
) -> FeatureTrajectory:
    """Create a test trajectory."""
    commits = []
    for i in range(commit_count):
        days_ago = days_old - (i * (days_old // max(commit_count, 1)))
        files = [f"impl/foo/file{i}.py"]
        if has_tests and i < test_count:
            files.append(f"impl/foo/test_file{i}.py")

        commits.append(
            make_commit(
                sha=f"commit{i}",
                message=f"feat({name.lower()}): commit {i}",
                files=tuple(files),
                days_ago=max(0, days_ago),
                insertions=50 + i * 10,
                deletions=10 + i * 2,
            )
        )

    pattern = FeaturePattern(
        name=name,
        impl_patterns=("impl/foo/",),
        spec_patterns=("spec/foo/",),
        test_patterns=("test_",),
    )

    return FeatureTrajectory(
        name=name,
        pattern=pattern,
        commits=tuple(commits),
        status=status,
        has_tests=has_tests,
        test_count=test_count,
    )


# HistoryCrystal tests


class TestHistoryCrystal:
    """Tests for HistoryCrystal dataclass."""

    def test_crystal_is_frozen(self):
        """HistoryCrystal should be immutable."""
        crystal = HistoryCrystal(
            feature_name="Test",
            summary="A test feature",
            key_insights=("Insight 1",),
            emotional_valence=0.5,
            lessons=("Lesson 1",),
            related_principles=("Tasteful",),
            status=FeatureStatus.STABLE,
            commit_count=10,
            first_active=None,
            last_active=None,
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            crystal.feature_name = "Changed"  # type: ignore

    def test_to_brain_crystal_format(self):
        """Should format correctly for Brain storage."""
        crystal = HistoryCrystal(
            feature_name="AGENTESE",
            summary="The universal protocol for agent interaction.",
            key_insights=("Observer-dependent projection", "Five contexts only"),
            emotional_valence=0.9,
            lessons=("Constraint enables creativity",),
            related_principles=("Tasteful", "Composable"),
            status=FeatureStatus.THRIVING,
            commit_count=100,
            first_active=datetime(2025, 1, 1, tzinfo=timezone.utc),
            last_active=datetime(2025, 12, 20, tzinfo=timezone.utc),
        )

        brain_data = crystal.to_brain_crystal()

        assert "content" in brain_data
        assert "AGENTESE" in brain_data["content"]
        assert "Observer-dependent projection" in brain_data["content"]
        assert "Constraint enables creativity" in brain_data["content"]

        assert "tags" in brain_data
        assert "archaeology" in brain_data["tags"]
        assert "agentese" in brain_data["tags"]
        assert "thriving" in brain_data["tags"]

        assert "metadata" in brain_data
        assert brain_data["metadata"]["type"] == "history_crystal"
        assert brain_data["metadata"]["valence"] == 0.9

    def test_to_brain_crystal_handles_none_dates(self):
        """Should handle None dates gracefully."""
        crystal = HistoryCrystal(
            feature_name="Test",
            summary="Test",
            key_insights=(),
            emotional_valence=0.0,
            lessons=(),
            related_principles=(),
            status=FeatureStatus.ABANDONED,
            commit_count=0,
            first_active=None,
            last_active=None,
        )

        brain_data = crystal.to_brain_crystal()
        assert brain_data["metadata"]["first_active"] is None
        assert brain_data["metadata"]["last_active"] is None


# Generation tests


class TestGenerateHistoryCrystal:
    """Tests for generate_history_crystal."""

    def test_thriving_feature_has_positive_valence(self):
        """Thriving features should have positive emotional valence."""
        trajectory = make_trajectory("Brain", FeatureStatus.THRIVING)
        crystal = generate_history_crystal(trajectory)

        assert crystal.emotional_valence > 0.5
        assert crystal.feature_name == "Brain"
        assert crystal.status == FeatureStatus.THRIVING

    def test_abandoned_feature_has_negative_valence(self):
        """Abandoned features should have negative emotional valence."""
        trajectory = make_trajectory("OldFeature", FeatureStatus.ABANDONED, has_tests=False)
        crystal = generate_history_crystal(trajectory)

        assert crystal.emotional_valence < 0

    def test_crystal_has_insights(self):
        """Generated crystals should have at least one insight."""
        trajectory = make_trajectory("Test", FeatureStatus.STABLE)
        crystal = generate_history_crystal(trajectory)

        assert len(crystal.key_insights) >= 1

    def test_crystal_has_lessons(self):
        """Generated crystals should have at least one lesson."""
        trajectory = make_trajectory("Test", FeatureStatus.THRIVING)
        crystal = generate_history_crystal(trajectory)

        assert len(crystal.lessons) >= 1

    def test_crystal_has_summary(self):
        """Generated crystals should have a non-empty summary."""
        trajectory = make_trajectory("Test", FeatureStatus.STABLE)
        crystal = generate_history_crystal(trajectory)

        assert len(crystal.summary) > 50  # Meaningful summary

    def test_stable_feature_mentions_maturity(self):
        """Stable feature summary should mention maturity."""
        trajectory = make_trajectory("Mature", FeatureStatus.STABLE)
        crystal = generate_history_crystal(trajectory)

        assert "stable" in crystal.summary.lower() or "mature" in crystal.summary.lower()


class TestGenerateAllCrystals:
    """Tests for generate_all_crystals."""

    def test_filters_by_commit_count(self):
        """Should filter out features with too few commits."""
        trajectories = [
            make_trajectory("Big", FeatureStatus.THRIVING, commit_count=20),
            make_trajectory("Small", FeatureStatus.STABLE, commit_count=3),
        ]

        crystals = generate_all_crystals(trajectories, min_commits=5)

        assert len(crystals) == 1
        assert crystals[0].feature_name == "Big"

    def test_generates_for_all_statuses(self):
        """Should generate crystals for all feature statuses."""
        trajectories = [
            make_trajectory("A", FeatureStatus.THRIVING, commit_count=10),
            make_trajectory("B", FeatureStatus.STABLE, commit_count=10),
            make_trajectory("C", FeatureStatus.LANGUISHING, commit_count=10),
            make_trajectory("D", FeatureStatus.ABANDONED, commit_count=10),
        ]

        crystals = generate_all_crystals(trajectories)

        assert len(crystals) == 4

    def test_empty_trajectories_returns_empty(self):
        """Should return empty list for empty input."""
        crystals = generate_all_crystals([])
        assert crystals == []


# Valence tests


class TestValenceCalculation:
    """Tests for emotional valence calculation."""

    def test_thriving_with_tests_is_very_positive(self):
        """Thriving feature with tests should be very positive."""
        trajectory = make_trajectory("Good", FeatureStatus.THRIVING, has_tests=True)
        crystal = generate_history_crystal(trajectory)

        assert crystal.emotional_valence >= 0.8

    def test_languishing_is_slightly_negative(self):
        """Languishing features should be slightly negative."""
        trajectory = make_trajectory("Meh", FeatureStatus.LANGUISHING)
        crystal = generate_history_crystal(trajectory)

        assert -0.5 < crystal.emotional_valence < 0

    def test_over_engineered_is_neutral_to_negative(self):
        """Over-engineered features should be neutral to slightly negative."""
        trajectory = make_trajectory("Complex", FeatureStatus.OVER_ENGINEERED)
        crystal = generate_history_crystal(trajectory)

        assert -0.5 < crystal.emotional_valence < 0.3

    def test_valence_bounded(self):
        """Valence should always be in [-1.0, 1.0]."""
        for status in FeatureStatus:
            trajectory = make_trajectory("Test", status)
            crystal = generate_history_crystal(trajectory)

            assert -1.0 <= crystal.emotional_valence <= 1.0


# Principle identification tests


class TestPrincipleIdentification:
    """Tests for related principle identification."""

    def test_thriving_features_are_tasteful(self):
        """Thriving features should be tagged as Tasteful."""
        trajectory = make_trajectory("Good", FeatureStatus.THRIVING)
        crystal = generate_history_crystal(trajectory)

        assert "Tasteful" in crystal.related_principles

    def test_abandoned_features_are_curated(self):
        """Abandoned features relate to Curated principle."""
        trajectory = make_trajectory("Gone", FeatureStatus.ABANDONED)
        crystal = generate_history_crystal(trajectory)

        assert "Curated" in crystal.related_principles

    def test_high_commit_features_are_composable(self):
        """Features with many commits are likely Composable."""
        trajectory = make_trajectory("Big", FeatureStatus.THRIVING, commit_count=50)
        crystal = generate_history_crystal(trajectory)

        assert "Composable" in crystal.related_principles

    def test_limited_to_three_principles(self):
        """Should limit to at most 3 principles."""
        trajectory = make_trajectory("Test", FeatureStatus.THRIVING, commit_count=50)
        crystal = generate_history_crystal(trajectory)

        assert len(crystal.related_principles) <= 3


# Report tests


class TestGenerateCrystalReport:
    """Tests for generate_crystal_report."""

    def test_report_includes_header(self):
        """Report should have a title."""
        report = generate_crystal_report([])
        assert "# History Crystals Report" in report

    def test_report_includes_count(self):
        """Report should include total crystal count."""
        crystals = [
            generate_history_crystal(make_trajectory("A", FeatureStatus.THRIVING)),
            generate_history_crystal(make_trajectory("B", FeatureStatus.STABLE)),
        ]
        report = generate_crystal_report(crystals)

        assert "Total Crystals: 2" in report

    def test_report_groups_by_status(self):
        """Report should group crystals by status."""
        crystals = [
            generate_history_crystal(make_trajectory("A", FeatureStatus.THRIVING)),
            generate_history_crystal(make_trajectory("B", FeatureStatus.ABANDONED)),
        ]
        report = generate_crystal_report(crystals)

        assert "### THRIVING" in report
        assert "### ABANDONED" in report

    def test_report_includes_emotional_landscape(self):
        """Report should include emotional distribution."""
        crystals = [
            generate_history_crystal(make_trajectory("Happy", FeatureStatus.THRIVING)),
            generate_history_crystal(make_trajectory("Sad", FeatureStatus.ABANDONED)),
        ]
        report = generate_crystal_report(crystals)

        assert "Emotional Landscape" in report
        assert "Joyful" in report
