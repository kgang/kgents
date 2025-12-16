"""
Git Pattern Analyzer: Extract developer patterns from git history.

Part of Wave 4 de-risking for the Evergreen Prompt System.

Analyzes:
- Commit message style (conventional commits, length, emoji)
- File change frequency (hot paths, focus areas)
- Commit timing patterns (work schedule hints)
"""

from __future__ import annotations

import logging
import re
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GitPattern:
    """A detected pattern from git history."""

    pattern_type: Literal["commit_style", "file_focus", "timing", "collaboration"]
    description: str
    confidence: float  # 0.0-1.0
    evidence: tuple[str, ...]  # Supporting commits/files/stats
    details: dict[str, float] = field(default_factory=dict)  # Numeric breakdown

    def __str__(self) -> str:
        return f"[{self.pattern_type}] {self.description} (confidence: {self.confidence:.0%})"


class GitAnalyzerError(Exception):
    """Error during git analysis."""

    pass


@dataclass
class GitPatternAnalyzer:
    """
    Analyze git history for developer patterns.

    Thread-safe: all operations use subprocess and are stateless.
    """

    repo_path: Path
    lookback_commits: int = 100
    _validated: bool = False

    def _validate_repo(self) -> None:
        """
        Validate that repo_path is a git repository.

        Raises:
            GitAnalyzerError: If not a valid git repo
        """
        if self._validated:
            return

        # Check directory exists
        if not self.repo_path.exists():
            raise GitAnalyzerError(f"Path does not exist: {self.repo_path}")
        if not self.repo_path.is_dir():
            raise GitAnalyzerError(f"Path is not a directory: {self.repo_path}")

        # Check it's a git repo by running git rev-parse
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise GitAnalyzerError(
                    f"Not a git repository: {self.repo_path}\n{result.stderr}"
                )
            self._validated = True
        except subprocess.TimeoutExpired:
            raise GitAnalyzerError(f"Git validation timed out for: {self.repo_path}")
        except FileNotFoundError:
            raise GitAnalyzerError("Git executable not found. Is git installed?")

    def analyze(self) -> list[GitPattern]:
        """
        Extract patterns from recent commits.

        Returns list of detected patterns, highest confidence first.

        Raises:
            GitAnalyzerError: If repo_path is not a valid git repository
        """
        # Validate repo before analysis
        self._validate_repo()

        patterns = []

        try:
            patterns.append(self._analyze_commit_style())
        except Exception as e:
            logger.warning(f"Failed to analyze commit style: {e}")

        try:
            patterns.append(self._analyze_file_focus())
        except Exception as e:
            logger.warning(f"Failed to analyze file focus: {e}")

        try:
            patterns.append(self._analyze_timing())
        except Exception as e:
            logger.warning(f"Failed to analyze timing: {e}")

        # Sort by confidence descending
        patterns.sort(key=lambda p: p.confidence, reverse=True)

        return patterns

    def _run_git(self, *args: str) -> str:
        """Run a git command and return stdout."""
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git command failed: {result.stderr}")
        return result.stdout

    def _analyze_commit_style(self) -> GitPattern:
        """
        Analyze commit message conventions.

        Detects:
        - Conventional commits (feat:, fix:, etc.)
        - Emoji usage
        - Message length preferences
        - Imperative vs past tense
        """
        output = self._run_git("log", "--oneline", f"-{self.lookback_commits}")
        messages = [
            line.split(" ", 1)[1] if " " in line else line
            for line in output.strip().split("\n")
            if line
        ]

        if not messages:
            return GitPattern(
                pattern_type="commit_style",
                description="No commits found",
                confidence=0.0,
                evidence=(),
            )

        # Detect conventional commits
        conventional_pattern = re.compile(
            r"^(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(\(.+\))?[!:]"
        )
        conventional_count = sum(
            1 for m in messages if conventional_pattern.match(m.lower())
        )
        conventional_ratio = conventional_count / len(messages)

        # Detect emoji usage
        emoji_pattern = re.compile(
            r"[\U0001F300-\U0001F9FF]|[\u2600-\u26FF]|[\u2700-\u27BF]"
        )
        emoji_count = sum(1 for m in messages if emoji_pattern.search(m))
        emoji_ratio = emoji_count / len(messages)

        # Message length stats
        lengths = [len(m) for m in messages]
        avg_length = sum(lengths) / len(lengths)
        short_count = sum(1 for l in lengths if l < 50)
        short_ratio = short_count / len(lengths)

        # Determine primary style
        details = {
            "conventional_ratio": conventional_ratio,
            "emoji_ratio": emoji_ratio,
            "avg_length": avg_length,
            "short_ratio": short_ratio,
        }

        if conventional_ratio > 0.7:
            style = "conventional commits"
            confidence = conventional_ratio
        elif emoji_ratio > 0.5:
            style = "emoji-prefixed commits"
            confidence = emoji_ratio
        elif short_ratio > 0.8:
            style = "concise commits"
            confidence = short_ratio
        else:
            style = "mixed/informal commits"
            confidence = 0.5

        return GitPattern(
            pattern_type="commit_style",
            description=f"Uses {style} (avg {avg_length:.0f} chars)",
            confidence=confidence,
            evidence=tuple(messages[:5]),
            details=details,
        )

    def _analyze_file_focus(self) -> GitPattern:
        """
        Analyze which files/directories get most attention.

        Detects:
        - Hot paths (frequently changed)
        - Focus areas (directory patterns)
        """
        output = self._run_git(
            "log",
            "--name-only",
            "--pretty=format:",
            f"-{self.lookback_commits}",
        )

        files = [f.strip() for f in output.strip().split("\n") if f.strip()]
        if not files:
            return GitPattern(
                pattern_type="file_focus",
                description="No file changes found",
                confidence=0.0,
                evidence=(),
            )

        # Count file frequencies
        file_counts = Counter(files)

        # Aggregate to directory level
        dir_counts: Counter[str] = Counter()
        for file, count in file_counts.items():
            parts = file.split("/")
            if len(parts) >= 2:
                dir_path = "/".join(parts[:2]) + "/"
            else:
                dir_path = parts[0] if parts else "root"
            dir_counts[dir_path] += count

        # Find top directories
        top_dirs = dir_counts.most_common(5)
        total_changes = sum(dir_counts.values())

        # Find top files
        top_files = file_counts.most_common(5)

        # Determine focus pattern
        top_dir, top_count = top_dirs[0] if top_dirs else ("unknown", 0)
        focus_ratio = top_count / total_changes if total_changes > 0 else 0

        details = {
            "total_changes": float(total_changes),
            "unique_files": float(len(file_counts)),
            "unique_dirs": float(len(dir_counts)),
            "top_dir_ratio": focus_ratio,
        }

        # Add top directory ratios
        for i, (dir_path, count) in enumerate(top_dirs[:3]):
            details[f"dir_{i}_ratio"] = (
                count / total_changes if total_changes > 0 else 0
            )

        if focus_ratio > 0.5:
            description = (
                f"Concentrated focus on {top_dir} ({focus_ratio:.0%} of changes)"
            )
            confidence = focus_ratio
        elif len(dir_counts) < 5:
            description = f"Focused on {len(dir_counts)} directories"
            confidence = 0.7
        else:
            description = f"Distributed changes across {len(dir_counts)} directories"
            confidence = 0.5

        return GitPattern(
            pattern_type="file_focus",
            description=description,
            confidence=confidence,
            evidence=tuple(f"{d}: {c}" for d, c in top_dirs[:5]),
            details=details,
        )

    def _analyze_timing(self) -> GitPattern:
        """
        Analyze commit timing patterns.

        Detects:
        - Time of day preferences
        - Day of week patterns
        """
        output = self._run_git(
            "log",
            "--format=%aI",  # ISO 8601 author date
            f"-{self.lookback_commits}",
        )

        dates = []
        for line in output.strip().split("\n"):
            if line.strip():
                try:
                    # Parse ISO 8601 datetime
                    dt = datetime.fromisoformat(line.strip())
                    dates.append(dt)
                except ValueError:
                    continue

        if not dates:
            return GitPattern(
                pattern_type="timing",
                description="No timestamps found",
                confidence=0.0,
                evidence=(),
            )

        # Analyze hours
        hours = [d.hour for d in dates]
        hour_counts = Counter(hours)

        # Define time buckets
        morning = sum(hour_counts.get(h, 0) for h in range(6, 12))
        afternoon = sum(hour_counts.get(h, 0) for h in range(12, 18))
        evening = sum(hour_counts.get(h, 0) for h in range(18, 24))
        night = sum(hour_counts.get(h, 0) for h in range(0, 6))

        total = len(dates)

        # Analyze days of week
        days = [d.weekday() for d in dates]
        weekday_count = sum(1 for d in days if d < 5)
        weekend_count = total - weekday_count

        details = {
            "morning_ratio": morning / total if total > 0 else 0,
            "afternoon_ratio": afternoon / total if total > 0 else 0,
            "evening_ratio": evening / total if total > 0 else 0,
            "night_ratio": night / total if total > 0 else 0,
            "weekday_ratio": weekday_count / total if total > 0 else 0,
        }

        # Determine primary pattern
        time_ratios = [
            ("morning", morning / total if total > 0 else 0),
            ("afternoon", afternoon / total if total > 0 else 0),
            ("evening", evening / total if total > 0 else 0),
            ("night", night / total if total > 0 else 0),
        ]
        primary_time, primary_ratio = max(time_ratios, key=lambda x: x[1])

        weekday_ratio = weekday_count / total if total > 0 else 0

        if primary_ratio > 0.5:
            time_desc = f"primarily {primary_time} ({primary_ratio:.0%})"
            confidence = primary_ratio
        else:
            time_desc = "distributed throughout day"
            confidence = 0.5

        if weekday_ratio > 0.9:
            day_desc = "weekdays only"
        elif weekday_ratio > 0.7:
            day_desc = "mostly weekdays"
        elif weekday_ratio < 0.5:
            day_desc = "includes significant weekend work"
        else:
            day_desc = "balanced week"

        return GitPattern(
            pattern_type="timing",
            description=f"Commits {time_desc}, {day_desc}",
            confidence=confidence,
            evidence=(
                f"Morning: {morning}/{total}",
                f"Afternoon: {afternoon}/{total}",
                f"Evening: {evening}/{total}",
                f"Night: {night}/{total}",
                f"Weekdays: {weekday_count}/{total}",
            ),
            details=details,
        )


def analyze_repo(repo_path: Path | str, lookback: int = 100) -> list[GitPattern]:
    """
    Convenience function to analyze a git repository.

    Args:
        repo_path: Path to the git repository
        lookback: Number of commits to analyze

    Returns:
        List of detected patterns
    """
    analyzer = GitPatternAnalyzer(
        repo_path=Path(repo_path),
        lookback_commits=lookback,
    )
    return analyzer.analyze()


__all__ = [
    "GitPattern",
    "GitPatternAnalyzer",
    "GitAnalyzerError",
    "analyze_repo",
]
