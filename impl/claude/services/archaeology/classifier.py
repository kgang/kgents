"""
Feature Classifier: Classify features by commit trajectory.

Classifies features as:
- THRIVING: Active development, tests passing, ship-ready
- STABLE: Mature, low activity, solid tests
- LANGUISHING: Started strong, activity dropped off
- ABANDONED: No recent activity, may have broken tests
- OVER_ENGINEERED: Lots of code/tests, low actual usage

See: spec/protocols/repo-archaeology.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Sequence

from .mining import Commit
from .patterns import FeaturePattern


class FeatureStatus(Enum):
    """Status classification for a feature."""

    THRIVING = "thriving"  # Active development, tests passing
    STABLE = "stable"  # Mature, low activity, solid tests
    LANGUISHING = "languishing"  # Started strong, activity dropped
    ABANDONED = "abandoned"  # No recent activity, broken/no tests
    OVER_ENGINEERED = "over_engineered"  # High complexity, low usage


@dataclass
class FeatureTrajectory:
    """
    The lifecycle of a feature from inception to current state.

    Captures the full journey: first commit, all commits, current status,
    and derived metrics like velocity and churn.
    """

    name: str
    pattern: FeaturePattern
    commits: tuple[Commit, ...]
    status: FeatureStatus
    has_tests: bool = False
    test_count: int = 0

    @property
    def first_commit(self) -> Commit | None:
        """The earliest commit touching this feature."""
        if not self.commits:
            return None
        return min(self.commits, key=lambda c: c.timestamp)

    @property
    def last_commit(self) -> Commit | None:
        """The most recent commit touching this feature."""
        if not self.commits:
            return None
        return max(self.commits, key=lambda c: c.timestamp)

    @property
    def total_commits(self) -> int:
        """Total number of commits for this feature."""
        return len(self.commits)

    @property
    def velocity(self) -> float:
        """
        Recent activity relative to total activity.

        Ratio of commits in last 30 days to total commits.
        """
        if not self.commits:
            return 0.0

        now = datetime.now(timezone.utc)
        recent = sum(
            1
            for c in self.commits
            if c.timestamp.replace(tzinfo=timezone.utc) > now - timedelta(days=30)
        )
        return recent / len(self.commits)

    @property
    def churn(self) -> float:
        """
        Average lines changed per commit.

        High churn may indicate instability or major refactoring.
        """
        if not self.commits:
            return 0.0

        total_churn = sum(c.insertions + c.deletions for c in self.commits)
        return total_churn / len(self.commits)

    @property
    def days_since_last_activity(self) -> int:
        """Days since last commit."""
        if not self.commits:
            return 999  # Very stale

        last = self.last_commit
        if last is None:
            return 999

        now = datetime.now(timezone.utc)
        last_ts = last.timestamp.replace(tzinfo=timezone.utc)
        return (now - last_ts).days

    @property
    def age_days(self) -> int:
        """Days since first commit."""
        first = self.first_commit
        if first is None:
            return 0

        now = datetime.now(timezone.utc)
        first_ts = first.timestamp.replace(tzinfo=timezone.utc)
        return (now - first_ts).days

    def to_report_row(self) -> dict[str, str | int | float | bool]:
        """Generate report row for this trajectory."""
        return {
            "name": self.name,
            "status": self.status.value,
            "commits": self.total_commits,
            "velocity": round(self.velocity, 2),
            "churn": round(self.churn, 1),
            "has_tests": self.has_tests,
            "last_active": self.last_commit.timestamp.strftime("%Y-%m-%d")
            if self.last_commit
            else "never",
            "days_stale": self.days_since_last_activity,
        }


def classify_feature(
    pattern: FeaturePattern,
    all_commits: Sequence[Commit],
    now: datetime | None = None,
) -> FeatureTrajectory:
    """
    Classify a feature based on its commit history.

    Args:
        pattern: The feature pattern to classify
        all_commits: All commits in the repository
        now: Current time (for testing)

    Returns:
        FeatureTrajectory with status classification
    """
    now = now or datetime.now(timezone.utc)

    # Filter commits that touch this feature
    feature_commits = [
        c for c in all_commits if any(pattern.matches_file(f) for f in c.files_changed)
    ]

    # Check for test presence
    has_tests = any(
        "test" in f.lower() or "_tests" in f for c in feature_commits for f in c.files_changed
    )

    # Count test files
    test_files = set()
    for c in feature_commits:
        for f in c.files_changed:
            if "test" in f.lower() or "_tests" in f:
                test_files.add(f)
    test_count = len(test_files)

    # Classify status
    status = _determine_status(
        feature_commits,
        has_tests=has_tests,
        test_count=test_count,
        now=now,
    )

    return FeatureTrajectory(
        name=pattern.name,
        pattern=pattern,
        commits=tuple(feature_commits),
        status=status,
        has_tests=has_tests,
        test_count=test_count,
    )


def _determine_status(
    commits: list[Commit],
    has_tests: bool,
    test_count: int,
    now: datetime,
) -> FeatureStatus:
    """
    Determine feature status based on activity patterns.

    Classification heuristics:
    - THRIVING: >=5 commits in 14 days, tests present
    - STABLE: Tests present, 1-4 commits in 30 days
    - LANGUISHING: Tests present but <2 commits in 30 days
    - ABANDONED: No commits in 60 days OR no tests
    - OVER_ENGINEERED: High test count (>50) but low recent activity
    """
    if not commits:
        return FeatureStatus.ABANDONED

    # Make all timestamps timezone-aware
    def to_utc(ts: datetime) -> datetime:
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts.replace(tzinfo=timezone.utc)

    recent_14 = [c for c in commits if to_utc(c.timestamp) > now - timedelta(days=14)]
    recent_30 = [c for c in commits if to_utc(c.timestamp) > now - timedelta(days=30)]
    recent_60 = [c for c in commits if to_utc(c.timestamp) > now - timedelta(days=60)]

    # Over-engineered: many tests but low recent activity
    if test_count > 50 and len(recent_30) < 2:
        return FeatureStatus.OVER_ENGINEERED

    # Abandoned: no activity in 60 days OR no tests
    if len(recent_60) == 0 or (len(commits) > 5 and not has_tests):
        return FeatureStatus.ABANDONED

    # Thriving: active development
    if len(recent_14) >= 5 and has_tests:
        return FeatureStatus.THRIVING

    # Stable: mature with some activity
    if has_tests and len(recent_30) >= 1:
        return FeatureStatus.STABLE

    # Languishing: tests exist but activity dropped
    if has_tests:
        return FeatureStatus.LANGUISHING

    # Default to abandoned if no tests
    return FeatureStatus.ABANDONED


def classify_all_features(
    patterns: dict[str, FeaturePattern],
    all_commits: Sequence[Commit],
) -> dict[str, FeatureTrajectory]:
    """
    Classify all registered features.

    Args:
        patterns: Feature patterns to classify
        all_commits: All commits in repository

    Returns:
        Dict of feature name to trajectory
    """
    return {name: classify_feature(pattern, all_commits) for name, pattern in patterns.items()}


def generate_report(trajectories: dict[str, FeatureTrajectory]) -> str:
    """
    Generate a human-readable report of feature statuses.

    Returns:
        Markdown-formatted report
    """
    lines = [
        "# kgents Repository Archaeology Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Executive Summary",
        "",
    ]

    # Count by status
    by_status: dict[FeatureStatus, list[FeatureTrajectory]] = {}
    for t in trajectories.values():
        by_status.setdefault(t.status, []).append(t)

    for status in FeatureStatus:
        count = len(by_status.get(status, []))
        lines.append(f"- {status.value.upper()}: {count}")

    lines.append("")

    # Detail by status
    for status in [
        FeatureStatus.THRIVING,
        FeatureStatus.STABLE,
        FeatureStatus.LANGUISHING,
        FeatureStatus.OVER_ENGINEERED,
        FeatureStatus.ABANDONED,
    ]:
        features = by_status.get(status, [])
        if not features:
            continue

        lines.append(f"## {status.value.upper()}")
        lines.append("")
        lines.append("| Feature | Commits | Velocity | Last Active |")
        lines.append("|---------|---------|----------|-------------|")

        for t in sorted(features, key=lambda x: x.total_commits, reverse=True):
            row = t.to_report_row()
            lines.append(
                f"| {row['name']} | {row['commits']} | {row['velocity']} | {row['last_active']} |"
            )

        lines.append("")

    return "\n".join(lines)
