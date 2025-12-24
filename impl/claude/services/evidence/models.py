"""
Evidence Mining Models: Frozen dataclasses for git-witness correlation analysis.

This module defines the core data structures for evidence mining - the practice
of correlating witness marks with git history to validate the hypothesis:
    "Systematic decision witnessing improves code quality and reduces rework."

The models follow patterns from archaeology service (mining.py, patterns.py)
and witness service (mark.py) - frozen dataclasses, type hints, comprehensive
docstrings.

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    Evidence mining validates that witness marks correlate with better outcomes.

See: spec/protocols/repo-archaeology.md
See: spec/protocols/witness-primitives.md
See: docs/skills/crown-jewel-patterns.md (Pattern 7: Append-Only History)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Sequence

# =============================================================================
# Correlation Types
# =============================================================================


class CorrelationType(Enum):
    """
    Types of correlations between witness marks and git commits.

    The four correlation types:
    - REFERENCES_COMMIT: Mark explicitly references a commit SHA
    - SAME_TIMESTAMP: Mark and commit within temporal window (±5min)
    - SAME_FILES: Mark mentions files changed in commit
    - DECISION_LED_TO: Decision mark temporally precedes related commits
    """

    REFERENCES_COMMIT = auto()  # Explicit reference in mark metadata
    SAME_TIMESTAMP = auto()  # Temporal proximity
    SAME_FILES = auto()  # File overlap
    DECISION_LED_TO = auto()  # Decision → implementation chain


# =============================================================================
# Commit Patterns
# =============================================================================


@dataclass(frozen=True)
class CommitPattern:
    """
    Temporal, size, and quality patterns extracted from git commits.

    Immutable record of commit characteristics used to identify patterns
    like refactoring waves, feature development cycles, bug fix clusters.
    """

    sha: str
    timestamp: datetime
    author: str
    message: str
    files_changed: int
    insertions: int
    deletions: int
    commit_type: str  # feat, fix, refactor, docs, etc.
    scope: str | None = None  # From conventional commit: feat(brain)
    is_merge: bool = False
    is_revert: bool = False

    @property
    def churn(self) -> int:
        """Total lines changed (insertions + deletions)."""
        return self.insertions + self.deletions

    @property
    def net_change(self) -> int:
        """Net lines added (insertions - deletions)."""
        return self.insertions - self.deletions

    @property
    def is_refactor(self) -> bool:
        """Refactors touch many files with low net change."""
        return self.files_changed > 5 and abs(self.net_change) < 50

    @property
    def is_feature(self) -> bool:
        """Features add more than they remove."""
        return self.insertions > self.deletions * 2 and self.files_changed > 1

    @property
    def is_fix(self) -> bool:
        """Fixes are small, targeted changes."""
        return self.files_changed <= 3 and self.insertions < 50


@dataclass(frozen=True)
class FileChurnMetric:
    """
    File coupling and churn statistics.

    Tracks which files change together (coupling) and how frequently
    files change (churn) - both indicators of potential design issues.
    """

    file_path: str
    total_commits: int
    total_insertions: int
    total_deletions: int
    unique_authors: int
    coupled_files: tuple[str, ...]  # Files that often change together
    coupling_strength: dict[str, float] = field(default_factory=dict)  # file → correlation score

    @property
    def churn(self) -> int:
        """Total lines changed over time."""
        return self.total_insertions + self.total_deletions

    @property
    def churn_per_commit(self) -> float:
        """Average churn per commit - high values indicate instability."""
        return self.churn / self.total_commits if self.total_commits > 0 else 0.0


@dataclass(frozen=True)
class AuthorPattern:
    """
    Author contribution patterns - who works on what.

    Identifies expertise areas, ownership patterns, and collaboration dynamics.
    """

    author: str
    total_commits: int
    total_insertions: int
    total_deletions: int
    primary_scopes: tuple[str, ...]  # Most common scopes (brain, witness, etc.)
    file_paths: tuple[str, ...]  # Most touched files
    commit_types: dict[str, int] = field(default_factory=dict)  # feat: 42, fix: 18, ...
    first_commit: datetime | None = None
    last_commit: datetime | None = None

    @property
    def commits_per_day(self) -> float:
        """Average commits per day over active period."""
        if not self.first_commit or not self.last_commit:
            return 0.0
        delta = (self.last_commit - self.first_commit).days
        return self.total_commits / delta if delta > 0 else float(self.total_commits)


@dataclass(frozen=True)
class BugCorrelation:
    """
    Bug pattern correlation - what causes bugs.

    Correlates bug fixes with commit patterns, file churn, coupling,
    and author patterns to identify bug-prone characteristics.
    """

    bug_fix_sha: str
    bug_fix_timestamp: datetime
    files_fixed: tuple[str, ...]
    likely_introduced_by: str | None = None  # SHA of commit that introduced bug
    time_to_fix: float | None = None  # Days from introduction to fix
    file_churn_at_fix: dict[str, int] = field(default_factory=dict)  # file → churn
    coupling_violations: int = 0  # Number of coupled files also needing fixes


# =============================================================================
# Mark-Commit Links
# =============================================================================


@dataclass(frozen=True)
class MarkCommitLink:
    """
    Correlation between a witness mark and git commit(s).

    This is the key structure for validating the witness hypothesis:
    marks that precede commits should correlate with better outcomes.
    """

    mark_id: str  # Witness mark ID
    mark_timestamp: datetime
    mark_action: str  # The action that was witnessed
    mark_metadata: dict[str, Any] = field(default_factory=dict)
    commit_sha: str | None = None  # Related commit (if found)
    commit_timestamp: datetime | None = None
    correlation_type: CorrelationType | None = None
    correlation_strength: float = 0.0  # 0.0 to 1.0
    evidence: str = ""  # Human-readable explanation of correlation


@dataclass(frozen=True)
class DecisionCommitChain:
    """
    Trace from decision mark → implementation commits.

    Validates the hypothesis: "Decision marks reduce rework and improve quality."
    """

    decision_mark_id: str
    decision_timestamp: datetime
    decision_kent: str  # Kent's position
    decision_claude: str  # Claude's position
    decision_synthesis: str  # Synthesis/resolution
    subsequent_commits: tuple[CommitPattern, ...]  # Commits after decision
    time_to_first_commit: float  # Hours from decision to first commit
    total_commits: int
    total_churn: int
    reverts: int = 0  # Number of commits that were reverted
    rework_ratio: float = 0.0  # Proportion of churn that was rework


@dataclass(frozen=True)
class GotchaVsBugCorrelation:
    """
    Correlation between gotcha annotations and bug fixes.

    Validates: "Capturing gotchas reduces repeat mistakes."
    """

    gotcha_timestamp: datetime
    gotcha_section: str
    gotcha_note: str
    gotcha_file_patterns: tuple[str, ...]  # Files mentioned in gotcha
    related_bugs: tuple[BugCorrelation, ...]  # Bugs in same area
    bugs_before_gotcha: int  # Bugs before annotation
    bugs_after_gotcha: int  # Bugs after annotation
    reduction_ratio: float = 0.0  # (before - after) / before


# =============================================================================
# ROI Metrics
# =============================================================================


@dataclass(frozen=True)
class TimeROI:
    """
    Time saved through witness marks vs. control.

    Measures: Does marking decisions/gotchas save development time?
    """

    feature: str  # Feature being measured (Brain, Witness, etc.)
    with_marks_time: float  # Hours spent with systematic marking
    without_marks_time: float  # Hours spent without (or estimated)
    time_saved: float  # Hours saved
    time_saved_ratio: float  # Proportion of time saved
    sample_size: int  # Number of tasks in sample


@dataclass(frozen=True)
class QualityROI:
    """
    Quality improvement through witness marks.

    Measures: Does marking improve code quality?
    """

    feature: str
    with_marks_bug_rate: float  # Bugs per commit with marks
    without_marks_bug_rate: float  # Bugs per commit without marks
    with_marks_rework_ratio: float  # Rework ratio with marks
    without_marks_rework_ratio: float  # Rework ratio without marks
    quality_improvement: float  # Composite quality score delta
    sample_size: int


@dataclass(frozen=True)
class DecisionROI:
    """
    Decision quality through witness marks.

    Measures: Does recording decisions improve outcomes?
    """

    decision_count: int
    decisions_followed: int  # Decisions that led to implementation
    decisions_revised: int  # Decisions that were changed
    average_time_to_implementation: float  # Hours from decision to code
    rework_after_decision: float  # Rework ratio for decided features
    rework_without_decision: float  # Rework ratio for undecided features
    decision_quality_score: float  # Composite score (0.0 to 1.0)


# =============================================================================
# Evidence Report
# =============================================================================


@dataclass
class EvidenceReport:
    """
    Aggregate evidence report structure.

    Combines all metrics into a single report for a given time period.
    """

    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    repo_path: str = ""
    start_date: datetime | None = None
    end_date: datetime | None = None

    # Commit patterns
    total_commits: int = 0
    commit_patterns: list[CommitPattern] = field(default_factory=list)
    file_churn: list[FileChurnMetric] = field(default_factory=list)
    author_patterns: list[AuthorPattern] = field(default_factory=list)
    bug_correlations: list[BugCorrelation] = field(default_factory=list)

    # Mark-commit correlations
    mark_commit_links: list[MarkCommitLink] = field(default_factory=list)
    decision_chains: list[DecisionCommitChain] = field(default_factory=list)
    gotcha_correlations: list[GotchaVsBugCorrelation] = field(default_factory=list)

    # ROI metrics
    time_roi: list[TimeROI] = field(default_factory=list)
    quality_roi: list[QualityROI] = field(default_factory=list)
    decision_roi: list[DecisionROI] = field(default_factory=list)

    # Summary statistics
    total_marks: int = 0
    marks_with_commits: int = 0
    correlation_rate: float = 0.0  # marks_with_commits / total_marks

    def add_commit_pattern(self, pattern: CommitPattern) -> None:
        """Add a commit pattern to the report."""
        self.commit_patterns.append(pattern)
        self.total_commits += 1

    def add_mark_commit_link(self, link: MarkCommitLink) -> None:
        """Add a mark-commit correlation."""
        self.mark_commit_links.append(link)
        self.total_marks += 1
        if link.commit_sha:
            self.marks_with_commits += 1
        self._update_correlation_rate()

    def _update_correlation_rate(self) -> None:
        """Recalculate correlation rate."""
        if self.total_marks > 0:
            self.correlation_rate = self.marks_with_commits / self.total_marks

    def summary(self) -> dict[str, Any]:
        """
        Generate summary statistics.

        Returns:
            Dictionary of key metrics for quick overview
        """
        return {
            "generated_at": self.generated_at.isoformat(),
            "repo_path": self.repo_path,
            "period": {
                "start": self.start_date.isoformat() if self.start_date else None,
                "end": self.end_date.isoformat() if self.end_date else None,
            },
            "commits": {
                "total": self.total_commits,
                "patterns": len(self.commit_patterns),
            },
            "marks": {
                "total": self.total_marks,
                "with_commits": self.marks_with_commits,
                "correlation_rate": self.correlation_rate,
            },
            "correlations": {
                "mark_commit_links": len(self.mark_commit_links),
                "decision_chains": len(self.decision_chains),
                "gotcha_correlations": len(self.gotcha_correlations),
            },
            "roi": {
                "time_metrics": len(self.time_roi),
                "quality_metrics": len(self.quality_roi),
                "decision_metrics": len(self.decision_roi),
            },
        }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "CorrelationType",
    # Commit patterns
    "CommitPattern",
    "FileChurnMetric",
    "AuthorPattern",
    "BugCorrelation",
    # Mark-commit correlations
    "MarkCommitLink",
    "DecisionCommitChain",
    "GotchaVsBugCorrelation",
    # ROI metrics
    "TimeROI",
    "QualityROI",
    "DecisionROI",
    # Report
    "EvidenceReport",
]
