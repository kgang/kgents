"""
Tests for feature classification.

Tests cover:
- Feature status determination
- Velocity and churn calculations
- Report generation
"""

from datetime import datetime, timedelta, timezone

import pytest

from services.archaeology.classifier import (
    FeatureStatus,
    FeatureTrajectory,
    classify_all_features,
    classify_feature,
    generate_report,
)
from services.archaeology.mining import Commit
from services.archaeology.patterns import FeaturePattern


def make_commit(
    message: str = "test",
    days_ago: int = 0,
    files: tuple[str, ...] = ("file.py",),
    insertions: int = 10,
    deletions: int = 5,
) -> Commit:
    """Create a test commit."""
    now = datetime.now(timezone.utc)
    return Commit(
        sha="abc123",
        message=message,
        author="kent@example.com",
        timestamp=now - timedelta(days=days_ago),
        files_changed=files,
        insertions=insertions,
        deletions=deletions,
    )


class TestFeatureStatus:
    """Tests for FeatureStatus enum."""

    def test_all_statuses_have_values(self):
        """All statuses should have string values."""
        assert FeatureStatus.THRIVING.value == "thriving"
        assert FeatureStatus.STABLE.value == "stable"
        assert FeatureStatus.LANGUISHING.value == "languishing"
        assert FeatureStatus.ABANDONED.value == "abandoned"
        assert FeatureStatus.OVER_ENGINEERED.value == "over_engineered"


class TestFeatureTrajectory:
    """Tests for FeatureTrajectory."""

    def test_first_commit(self):
        """Should return earliest commit."""
        pattern = FeaturePattern("Test", ("test/",), ())
        commits = (
            make_commit(days_ago=10),
            make_commit(days_ago=5),
            make_commit(days_ago=1),
        )

        trajectory = FeatureTrajectory(
            name="Test",
            pattern=pattern,
            commits=commits,
            status=FeatureStatus.STABLE,
        )

        assert trajectory.first_commit == commits[0]

    def test_last_commit(self):
        """Should return most recent commit."""
        pattern = FeaturePattern("Test", ("test/",), ())
        commits = (
            make_commit(days_ago=10),
            make_commit(days_ago=5),
            make_commit(days_ago=1),
        )

        trajectory = FeatureTrajectory(
            name="Test",
            pattern=pattern,
            commits=commits,
            status=FeatureStatus.STABLE,
        )

        assert trajectory.last_commit == commits[2]

    def test_velocity_recent_activity(self):
        """Velocity should reflect recent activity."""
        pattern = FeaturePattern("Test", ("test/",), ())

        # All commits are recent
        recent_commits = tuple(make_commit(days_ago=i) for i in range(10))
        trajectory = FeatureTrajectory(
            name="Test",
            pattern=pattern,
            commits=recent_commits,
            status=FeatureStatus.THRIVING,
        )

        # All 10 commits in last 30 days
        assert trajectory.velocity == 1.0

    def test_velocity_old_activity(self):
        """Velocity should be low for old activity."""
        pattern = FeaturePattern("Test", ("test/",), ())

        # All commits are old
        old_commits = tuple(make_commit(days_ago=60 + i) for i in range(10))
        trajectory = FeatureTrajectory(
            name="Test",
            pattern=pattern,
            commits=old_commits,
            status=FeatureStatus.ABANDONED,
        )

        assert trajectory.velocity == 0.0

    def test_churn_average(self):
        """Churn should be average lines per commit."""
        pattern = FeaturePattern("Test", ("test/",), ())
        commits = (
            make_commit(insertions=100, deletions=50),  # 150
            make_commit(insertions=50, deletions=50),  # 100
        )

        trajectory = FeatureTrajectory(
            name="Test",
            pattern=pattern,
            commits=commits,
            status=FeatureStatus.STABLE,
        )

        assert trajectory.churn == 125.0  # (150 + 100) / 2

    def test_to_report_row(self):
        """Should generate valid report row."""
        pattern = FeaturePattern("Test", ("test/",), ())
        commits = (make_commit(days_ago=5),)

        trajectory = FeatureTrajectory(
            name="Test",
            pattern=pattern,
            commits=commits,
            status=FeatureStatus.STABLE,
            has_tests=True,
        )

        row = trajectory.to_report_row()

        assert row["name"] == "Test"
        assert row["status"] == "stable"
        assert row["commits"] == 1
        assert row["has_tests"] is True


class TestClassifyFeature:
    """Tests for feature classification logic."""

    def test_thriving_many_recent_commits_with_tests(self):
        """THRIVING: 5+ commits in 14 days with tests."""
        pattern = FeaturePattern(
            "Brain",
            ("services/brain/",),
            (),
            ("services/brain/_tests/",),
        )

        # 6 recent commits touching brain and tests
        commits = [make_commit(days_ago=i, files=("services/brain/node.py",)) for i in range(6)]
        # Add a test file commit
        commits.append(make_commit(days_ago=2, files=("services/brain/_tests/test_node.py",)))

        trajectory = classify_feature(pattern, commits)

        assert trajectory.status == FeatureStatus.THRIVING
        assert trajectory.has_tests is True

    def test_stable_some_activity_with_tests(self):
        """STABLE: 1-4 commits in 30 days with tests."""
        pattern = FeaturePattern(
            "Brain",
            ("services/brain/",),
            (),
            ("services/brain/_tests/",),
        )

        commits = [
            make_commit(days_ago=20, files=("services/brain/node.py",)),
            make_commit(days_ago=25, files=("services/brain/_tests/test_node.py",)),
        ]

        trajectory = classify_feature(pattern, commits)

        assert trajectory.status == FeatureStatus.STABLE
        assert trajectory.has_tests is True

    def test_abandoned_no_recent_commits(self):
        """ABANDONED: no commits in 60 days."""
        pattern = FeaturePattern("OldFeature", ("old/",), ())

        commits = [
            make_commit(days_ago=90, files=("old/module.py",)),
        ]

        trajectory = classify_feature(pattern, commits)

        assert trajectory.status == FeatureStatus.ABANDONED

    def test_abandoned_no_matching_commits(self):
        """ABANDONED: no commits match pattern."""
        pattern = FeaturePattern("Ghost", ("ghost/",), ())

        commits = [
            make_commit(files=("other/module.py",)),
        ]

        trajectory = classify_feature(pattern, commits)

        assert trajectory.status == FeatureStatus.ABANDONED
        assert trajectory.total_commits == 0

    def test_languishing_tests_but_no_activity(self):
        """LANGUISHING: tests exist but activity dropped."""
        pattern = FeaturePattern(
            "Feature",
            ("feature/",),
            (),
            ("feature/_tests/",),
        )

        # Old commits with tests
        commits = [
            make_commit(days_ago=45, files=("feature/module.py",)),
            make_commit(days_ago=50, files=("feature/_tests/test.py",)),
        ]

        trajectory = classify_feature(pattern, commits)

        assert trajectory.status == FeatureStatus.LANGUISHING

    def test_over_engineered_many_tests_low_activity(self):
        """OVER_ENGINEERED: >50 test files but low recent activity."""
        pattern = FeaturePattern(
            "Evergreen",
            ("evergreen/",),
            (),
            ("evergreen/_tests/",),
        )

        # Generate 60 test file commits (old)
        commits = [
            make_commit(
                days_ago=60 + i,
                files=(f"evergreen/_tests/test_{i}.py",),
            )
            for i in range(60)
        ]

        trajectory = classify_feature(pattern, commits)

        assert trajectory.status == FeatureStatus.OVER_ENGINEERED
        assert trajectory.test_count > 50


class TestClassifyAllFeatures:
    """Tests for bulk classification."""

    def test_classifies_all_patterns(self):
        """Should classify every pattern."""
        patterns = {
            "A": FeaturePattern("A", ("a/",), ()),
            "B": FeaturePattern("B", ("b/",), ()),
        }

        commits = [
            make_commit(files=("a/module.py",)),
            make_commit(files=("b/module.py",)),
        ]

        trajectories = classify_all_features(patterns, commits)

        assert "A" in trajectories
        assert "B" in trajectories
        assert len(trajectories) == 2


class TestGenerateReport:
    """Tests for report generation."""

    def test_report_includes_header(self):
        """Report should include header."""
        trajectories = {
            "Test": FeatureTrajectory(
                name="Test",
                pattern=FeaturePattern("Test", (), ()),
                commits=(),
                status=FeatureStatus.ABANDONED,
            )
        }

        report = generate_report(trajectories)

        assert "# kgents Repository Archaeology Report" in report
        assert "Generated:" in report

    def test_report_includes_summary(self):
        """Report should include status summary."""
        trajectories = {
            "A": FeatureTrajectory(
                name="A",
                pattern=FeaturePattern("A", (), ()),
                commits=(),
                status=FeatureStatus.THRIVING,
            ),
            "B": FeatureTrajectory(
                name="B",
                pattern=FeaturePattern("B", (), ()),
                commits=(),
                status=FeatureStatus.ABANDONED,
            ),
        }

        report = generate_report(trajectories)

        assert "THRIVING: 1" in report
        assert "ABANDONED: 1" in report

    def test_report_includes_table(self):
        """Report should include feature tables."""
        pattern = FeaturePattern("Test", ("test/",), ())
        trajectories = {
            "Test": FeatureTrajectory(
                name="Test",
                pattern=pattern,
                commits=(make_commit(),),
                status=FeatureStatus.STABLE,
            ),
        }

        report = generate_report(trajectories)

        assert "| Feature | Commits | Velocity |" in report
        assert "| Test |" in report
