"""
Repository Mining Engine: Generalizable git pattern extraction.

Mine ANY git repository for development patterns - temporal rhythms, file coupling,
author specialization, bug correlations.

Philosophy:
    "The git log is a trace monoid of development choices."
    "Each commit is a mark. Each pattern is evidence."

Usage:
    miner = RepositoryMiner("/path/to/repo")
    patterns = miner.mine_commit_patterns(max_commits=1000)
    churn = miner.mine_file_churn(top_n=20)
    authors = miner.mine_author_patterns()
    bugs = miner.mine_bug_correlations()

See: spec/protocols/living-spec-evidence.md
"""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from services.archaeology.mining import Commit, parse_git_log

# ==============================================================================
# Aggregate Models (simpler than full evidence models)
# ==============================================================================


class CommitPatternSummary:
    """Aggregate temporal/quality summary of commits."""

    def __init__(
        self,
        *,
        total_commits: int,
        date_range: tuple[datetime, datetime] | None,
        avg_commit_size: float,
        median_commit_size: float,
        commit_types: dict[str, int],
        largest_commits: list[str],
        quality_score: float,
        temporal_density: dict[str, int],
        weekend_ratio: float,
    ):
        self.total_commits = total_commits
        self.date_range = date_range
        self.avg_commit_size = avg_commit_size
        self.median_commit_size = median_commit_size
        self.commit_types = commit_types
        self.largest_commits = largest_commits
        self.quality_score = quality_score
        self.temporal_density = temporal_density
        self.weekend_ratio = weekend_ratio


class FileChurnMetric:
    """File-level churn and coupling metric."""

    def __init__(
        self,
        *,
        path: str,
        commit_count: int,
        total_churn: int,
        avg_churn_per_commit: float,
        authors: tuple[str, ...],
        coupled_files: tuple[str, ...],
        coupling_strength: float,
        last_modified: datetime,
    ):
        self.path = path
        self.commit_count = commit_count
        self.total_churn = total_churn
        self.avg_churn_per_commit = avg_churn_per_commit
        self.authors = authors
        self.coupled_files = coupled_files
        self.coupling_strength = coupling_strength
        self.last_modified = last_modified


class AuthorPattern:
    """Author ownership and specialization pattern."""

    def __init__(
        self,
        *,
        author: str,
        total_commits: int,
        owned_files: tuple[str, ...],
        specialization_score: float,
        primary_domains: tuple[str, ...],
        collaboration_partners: dict[str, int],
        avg_commit_size: float,
        commit_type_distribution: dict[str, int],
    ):
        self.author = author
        self.total_commits = total_commits
        self.owned_files = owned_files
        self.specialization_score = specialization_score
        self.primary_domains = primary_domains
        self.collaboration_partners = collaboration_partners
        self.avg_commit_size = avg_commit_size
        self.commit_type_distribution = commit_type_distribution


class BugCorrelation:
    """Bug pattern correlation analysis."""

    def __init__(
        self,
        *,
        total_fixes: int,
        fix_ratio: float,
        bug_prone_files: tuple[str, ...],
        fix_commit_sizes: dict[str, float],
        fix_to_feature_lag: float,
        regression_indicators: list[str],
        quality_trend: str,
    ):
        self.total_fixes = total_fixes
        self.fix_ratio = fix_ratio
        self.bug_prone_files = bug_prone_files
        self.fix_commit_sizes = fix_commit_sizes
        self.fix_to_feature_lag = fix_to_feature_lag
        self.regression_indicators = regression_indicators
        self.quality_trend = quality_trend


# ==============================================================================
# Repository Miner
# ==============================================================================


class RepositoryMiner:
    """
    Mine ANY git repository for patterns. Generalizable.

    Reuses archaeology's git parsing infrastructure but adds generalized
    pattern analysis applicable to any repository.
    """

    def __init__(self, repo_path: Path | str):
        """
        Initialize miner for a git repository.

        Args:
            repo_path: Path to repository root or subdirectory (will search for .git)

        Raises:
            ValueError: If not inside a git repository
        """
        self.repo_path = self._find_git_root(Path(repo_path))

    @staticmethod
    def _find_git_root(path: Path) -> Path:
        """Find git root by walking up from path."""
        current = path.resolve()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        raise ValueError(f"Not inside a git repository: {path}")

    def mine_commit_patterns(
        self,
        max_commits: int | None = None,
        since: str | None = None,
    ) -> CommitPatternSummary:
        """
        Extract temporal, size, and quality patterns from commits.

        Args:
            max_commits: Limit analysis to N most recent commits
            since: ISO date string (e.g., "2025-01-01") to limit date range

        Returns:
            CommitPatternSummary with aggregated metrics
        """
        commits = parse_git_log(repo_path=self.repo_path, max_commits=max_commits)

        if not commits:
            # Empty repository
            return CommitPatternSummary(
                total_commits=0,
                date_range=None,
                avg_commit_size=0.0,
                median_commit_size=0.0,
                commit_types={},
                largest_commits=[],
                quality_score=0.0,
                temporal_density={},
                weekend_ratio=0.0,
            )

        # Filter by date if specified
        if since:
            since_dt = datetime.fromisoformat(since)
            # Make timezone-aware if needed for comparison
            if since_dt.tzinfo is None:
                # Assume UTC if no timezone specified
                from datetime import timezone as tz

                since_dt = since_dt.replace(tzinfo=tz.utc)
            commits = [c for c in commits if c.timestamp >= since_dt]

        if not commits:
            # No commits in date range
            return CommitPatternSummary(
                total_commits=0,
                date_range=None,
                avg_commit_size=0.0,
                median_commit_size=0.0,
                commit_types={},
                largest_commits=[],
                quality_score=0.0,
                temporal_density={},
                weekend_ratio=0.0,
            )

        # Date range
        timestamps = [c.timestamp for c in commits]
        date_range = (min(timestamps), max(timestamps))

        # Commit sizes
        sizes = [c.churn for c in commits]
        avg_size = statistics.mean(sizes)
        median_size = statistics.median(sizes)

        # Commit types
        types: Counter[str] = Counter(c.commit_type for c in commits)

        # Largest commits (top 5)
        sorted_commits = sorted(commits, key=lambda c: c.churn, reverse=True)
        largest = [c.sha for c in sorted_commits[:5]]

        # Quality score (0-1)
        # Based on: message quality, size distribution, type diversity
        quality = self._compute_quality_score(commits)

        # Temporal density (hour of day)
        hours: dict[str, int] = defaultdict(int)
        for c in commits:
            hour = c.timestamp.hour
            hours[str(hour)] = hours.get(str(hour), 0) + 1

        # Weekend ratio
        weekend_commits = sum(1 for c in commits if c.timestamp.weekday() >= 5)
        weekend_ratio = weekend_commits / len(commits)

        return CommitPatternSummary(
            total_commits=len(commits),
            date_range=date_range,
            avg_commit_size=avg_size,
            median_commit_size=median_size,
            commit_types=dict(types),
            largest_commits=largest,
            quality_score=quality,
            temporal_density=dict(hours),
            weekend_ratio=weekend_ratio,
        )

    def mine_file_churn(
        self,
        max_commits: int | None = None,
        top_n: int = 20,
    ) -> list[FileChurnMetric]:
        """
        Analyze file-level churn and coupling patterns.

        Args:
            max_commits: Limit to N most recent commits
            top_n: Return top N files by churn

        Returns:
            List of FileChurnMetric ordered by total churn descending
        """
        commits = parse_git_log(repo_path=self.repo_path, max_commits=max_commits)

        if not commits:
            return []

        # Aggregate per-file metrics
        file_data: dict[str, dict[str, object]] = defaultdict(
            lambda: {
                "commits": 0,
                "churn": 0,
                "authors": set(),
                "last_modified": None,
                "co_changes": Counter(),
            }
        )

        for commit in commits:
            for file_path in commit.files_changed:
                file_data[file_path]["commits"] = int(file_data[file_path]["commits"]) + 1  # type: ignore[arg-type, call-overload]
                file_data[file_path]["churn"] = int(file_data[file_path]["churn"]) + commit.churn  # type: ignore[arg-type, call-overload]
                assert isinstance(file_data[file_path]["authors"], set)
                file_data[file_path]["authors"].add(commit.author)  # type: ignore[union-attr]

                # Track last modified
                last_mod = file_data[file_path]["last_modified"]
                if last_mod is None or commit.timestamp > last_mod:  # type: ignore[operator]
                    file_data[file_path]["last_modified"] = commit.timestamp

                # Track coupling (files changed together)
                for other_file in commit.files_changed:
                    if other_file != file_path:
                        assert isinstance(file_data[file_path]["co_changes"], Counter)
                        file_data[file_path]["co_changes"][other_file] += 1  # type: ignore[index]

        # Convert to FileChurnMetric
        metrics = []
        for path, data in file_data.items():
            commits_count = int(data["commits"])  # type: ignore[arg-type, call-overload]
            total_churn = int(data["churn"])  # type: ignore[arg-type, call-overload]
            avg_churn = total_churn / commits_count if commits_count > 0 else 0.0

            assert isinstance(data["co_changes"], Counter)
            # Top 3 coupled files
            coupled = [f for f, _ in data["co_changes"].most_common(3)]

            # Coupling strength: how often does this file change with others?
            # 0 = always changes alone, 1 = always changes with others
            total_co_changes = sum(data["co_changes"].values())
            coupling_strength = (
                min(total_co_changes / commits_count, 1.0) if commits_count > 0 else 0.0
            )

            assert isinstance(data["authors"], set)
            assert data["last_modified"] is None or isinstance(data["last_modified"], datetime)

            metrics.append(
                FileChurnMetric(
                    path=path,
                    commit_count=commits_count,
                    total_churn=total_churn,
                    avg_churn_per_commit=avg_churn,
                    authors=tuple(sorted(data["authors"])),
                    coupled_files=tuple(coupled),
                    coupling_strength=coupling_strength,
                    last_modified=data["last_modified"] or datetime.min,
                )
            )

        # Sort by total churn descending
        metrics.sort(key=lambda m: m.total_churn, reverse=True)

        return metrics[:top_n]

    def mine_author_patterns(
        self,
        max_commits: int | None = None,
    ) -> list[AuthorPattern]:
        """
        Analyze author ownership and specialization patterns.

        Args:
            max_commits: Limit to N most recent commits

        Returns:
            List of AuthorPattern ordered by commit count descending
        """
        commits = parse_git_log(repo_path=self.repo_path, max_commits=max_commits)

        if not commits:
            return []

        # Aggregate per-author metrics
        author_data: dict[str, dict[str, object]] = defaultdict(
            lambda: {
                "commits": 0,
                "files": Counter(),
                "types": Counter(),
                "sizes": [],
                "collaborators": Counter(),
            }
        )

        for commit in commits:
            author = commit.author
            author_data[author]["commits"] = int(author_data[author]["commits"]) + 1  # type: ignore[arg-type, call-overload]
            assert isinstance(author_data[author]["types"], Counter)
            assert isinstance(author_data[author]["files"], Counter)
            author_data[author]["types"][commit.commit_type] += 1  # type: ignore[index]
            assert isinstance(author_data[author]["sizes"], list)
            author_data[author]["sizes"].append(commit.churn)  # type: ignore[union-attr]

            # Track file ownership
            for file_path in commit.files_changed:
                author_data[author]["files"][file_path] += 1  # type: ignore[index]

            # Track collaborators (other authors in same files)
            for file_path in commit.files_changed:
                for other_commit in commits:
                    if other_commit.author != author and file_path in other_commit.files_changed:
                        assert isinstance(author_data[author]["collaborators"], Counter)
                        author_data[author]["collaborators"][other_commit.author] += 1  # type: ignore[index]

        # Convert to AuthorPattern
        patterns = []
        for author, data in author_data.items():
            assert isinstance(data["files"], Counter)
            # Owned files (files where author has >50% of commits)
            total_file_commits = sum(data["files"].values())
            owned = []
            for file_path, count in data["files"].items():
                # Check if this author has majority commits for this file
                file_total_commits = sum(1 for c in commits if file_path in c.files_changed)
                if count / file_total_commits > 0.5:
                    owned.append(file_path)

            # Specialization score (Gini coefficient of file distribution)
            specialization = _gini_coefficient([c for c in data["files"].values()])

            # Primary domains (top 3 directory prefixes)
            domains: Counter[str] = Counter()
            for file_path in data["files"]:
                if "/" in file_path:
                    domain = file_path.split("/")[0]
                    domains[domain] += data["files"][file_path]
            primary = [d for d, _ in domains.most_common(3)]

            # Top 3 collaborators
            assert isinstance(data["collaborators"], Counter)
            collaborators = dict(data["collaborators"].most_common(3))

            # Average commit size
            assert isinstance(data["sizes"], list)
            avg_size = statistics.mean(data["sizes"]) if data["sizes"] else 0.0

            assert isinstance(data["types"], Counter)
            assert isinstance(data["commits"], int)

            patterns.append(
                AuthorPattern(
                    author=author,
                    total_commits=data["commits"],
                    owned_files=tuple(owned[:10]),  # Top 10 owned files
                    specialization_score=specialization,
                    primary_domains=tuple(primary),
                    collaboration_partners=collaborators,
                    avg_commit_size=avg_size,
                    commit_type_distribution=dict(data["types"]),
                )
            )

        # Sort by commit count descending
        patterns.sort(key=lambda p: p.total_commits, reverse=True)

        return patterns

    def mine_bug_correlations(
        self,
        max_commits: int | None = None,
    ) -> BugCorrelation:
        """
        Analyze bug patterns and fix correlations.

        Args:
            max_commits: Limit to N most recent commits

        Returns:
            BugCorrelation with aggregated bug/fix metrics
        """
        commits = parse_git_log(repo_path=self.repo_path, max_commits=max_commits)

        if not commits:
            return BugCorrelation(
                total_fixes=0,
                fix_ratio=0.0,
                bug_prone_files=(),
                fix_commit_sizes={},
                fix_to_feature_lag=0.0,
                regression_indicators=[],
                quality_trend="stable",
            )

        # Identify fix commits
        fix_commits = [c for c in commits if c.commit_type == "fix"]
        total_fixes = len(fix_commits)
        fix_ratio = total_fixes / len(commits) if commits else 0.0

        # Bug-prone files (files that appear in fix commits most often)
        bug_files: Counter[str] = Counter()
        for commit in fix_commits:
            for file_path in commit.files_changed:
                bug_files[file_path] += 1

        bug_prone = tuple(f for f, _ in bug_files.most_common(10))

        # Fix commit sizes (categorized)
        fix_sizes: dict[str, list[int]] = {"small": [], "medium": [], "large": []}
        for commit in fix_commits:
            if commit.churn < 20:
                fix_sizes["small"].append(commit.churn)
            elif commit.churn < 100:
                fix_sizes["medium"].append(commit.churn)
            else:
                fix_sizes["large"].append(commit.churn)

        avg_fix_sizes = {
            category: statistics.mean(sizes) if sizes else 0.0
            for category, sizes in fix_sizes.items()
        }

        # Fix-to-feature lag (avg commits between feature and first fix in same file)
        # Simplified: average distance between feature and fix commits
        lag = self._compute_feature_fix_lag(commits)

        # Regression indicators (commits with multiple subsequent fixes)
        regressions = self._detect_regressions(commits)

        # Quality trend (improving/stable/degrading)
        trend = self._compute_quality_trend(commits)

        return BugCorrelation(
            total_fixes=total_fixes,
            fix_ratio=fix_ratio,
            bug_prone_files=bug_prone,
            fix_commit_sizes=avg_fix_sizes,
            fix_to_feature_lag=lag,
            regression_indicators=regressions,
            quality_trend=trend,
        )

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _compute_quality_score(self, commits: list[Commit]) -> float:
        """
        Compute overall quality score (0-1) based on multiple signals.

        Higher score = better quality:
        - Good commit message quality (conventional commits)
        - Reasonable commit sizes (not too large)
        - Type diversity (not all fixes)
        """
        if not commits:
            return 0.0

        # Message quality: fraction using conventional commits
        conventional = sum(1 for c in commits if c.commit_type != "other")
        msg_quality = conventional / len(commits)

        # Size quality: penalize extremely large commits
        sizes = [c.churn for c in commits]
        avg_size = statistics.mean(sizes)
        # Ideal: 20-200 lines changed per commit
        if avg_size < 20:
            size_quality = avg_size / 20
        elif avg_size > 200:
            size_quality = max(0.5, 1.0 - (avg_size - 200) / 800)
        else:
            size_quality = 1.0

        # Type diversity: good balance of feat/fix/refactor
        types: Counter[str] = Counter(c.commit_type for c in commits)
        type_diversity = len(types) / 5  # Normalize by max expected types

        # Combine (weighted)
        return 0.4 * msg_quality + 0.3 * size_quality + 0.3 * type_diversity

    def _compute_feature_fix_lag(self, commits: list[Commit]) -> float:
        """
        Compute average lag between feature commits and fix commits in same files.

        Returns average number of commits between feat and first fix.
        """
        # Map file → [(index, type), ...]
        file_history: dict[str, list[tuple[int, str]]] = defaultdict(list)

        for idx, commit in enumerate(commits):
            for file_path in commit.files_changed:
                file_history[file_path].append((idx, commit.commit_type))

        # For each file, compute lag from first feat to first fix
        lags = []
        for file_path, history in file_history.items():
            feat_indices = [idx for idx, ctype in history if ctype == "feat"]
            fix_indices = [idx for idx, ctype in history if ctype == "fix"]

            if feat_indices and fix_indices:
                # Find first fix after first feat
                first_feat = min(feat_indices)
                later_fixes = [idx for idx in fix_indices if idx > first_feat]
                if later_fixes:
                    first_fix = min(later_fixes)
                    lags.append(first_fix - first_feat)

        return statistics.mean(lags) if lags else 0.0

    def _detect_regressions(self, commits: list[Commit]) -> list[str]:
        """
        Detect potential regression commits (commits with multiple subsequent fixes).

        Returns SHAs of commits that were followed by 2+ fixes in same files.
        """
        regressions = []

        for idx, commit in enumerate(commits):
            if commit.commit_type in ("feat", "refactor"):
                # Count fixes in same files within next 10 commits
                subsequent_commits = commits[idx + 1 : idx + 11]
                fix_count = 0

                for later_commit in subsequent_commits:
                    if later_commit.commit_type == "fix":
                        # Check if it touches same files
                        overlap = set(commit.files_changed) & set(later_commit.files_changed)
                        if overlap:
                            fix_count += 1

                if fix_count >= 2:
                    regressions.append(commit.sha)

        return regressions[:5]  # Top 5

    def _compute_quality_trend(self, commits: list[Commit]) -> str:
        """
        Compute quality trend over time.

        Returns "improving", "stable", or "degrading" based on fix ratio trend.
        """
        if len(commits) < 20:
            return "stable"  # Not enough data

        # Split into recent vs. older half
        mid = len(commits) // 2
        recent = commits[:mid]
        older = commits[mid:]

        recent_fix_ratio = sum(1 for c in recent if c.commit_type == "fix") / len(recent)
        older_fix_ratio = sum(1 for c in older if c.commit_type == "fix") / len(older)

        # Improving if recent fix ratio is lower
        if recent_fix_ratio < older_fix_ratio - 0.05:
            return "improving"
        elif recent_fix_ratio > older_fix_ratio + 0.05:
            return "degrading"
        else:
            return "stable"


def _gini_coefficient(values: list[int | float]) -> float:
    """
    Compute Gini coefficient for a distribution.

    Returns 0 for perfect equality, 1 for perfect inequality.
    Used to measure author specialization (0=generalist, 1=specialist).
    """
    if not values:
        return 0.0

    sorted_values = sorted(values)
    n = len(sorted_values)
    cumsum = 0.0
    total = sum(sorted_values)

    if total == 0:
        return 0.0

    for i, value in enumerate(sorted_values):
        cumsum += value * (n - i)

    return (n + 1 - 2 * cumsum / total) / n
