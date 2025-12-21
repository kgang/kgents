"""
Git Mining: Parse git history into structured Commit objects.

The git log is a trace monoid of Kent's development choices.
Each commit is a nudge. Each merge is a composition.
The pattern of commits IS the prior.

See: spec/protocols/repo-archaeology.md
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class Commit:
    """
    A single git commit as archaeological evidence.

    Immutable record of a development decision.
    """

    sha: str
    message: str
    author: str
    timestamp: datetime
    files_changed: tuple[str, ...]
    insertions: int
    deletions: int

    @property
    def is_refactor(self) -> bool:
        """Refactors touch many files with low net change."""
        return len(self.files_changed) > 5 and abs(self.insertions - self.deletions) < 50

    @property
    def is_feature(self) -> bool:
        """Features add more than they remove."""
        return self.insertions > self.deletions * 2 and len(self.files_changed) > 1

    @property
    def is_fix(self) -> bool:
        """Fixes are small, targeted changes."""
        return len(self.files_changed) <= 3 and self.insertions < 50

    @property
    def commit_type(self) -> str:
        """Extract commit type from conventional commit message."""
        if ": " in self.message:
            prefix = self.message.split(": ")[0]
            # Handle scoped commits like "feat(brain):"
            if "(" in prefix:
                prefix = prefix.split("(")[0]
            return prefix.lower()
        return "other"

    @property
    def scope(self) -> str | None:
        """Extract scope from conventional commit message."""
        if "(" in self.message and ")" in self.message:
            start = self.message.index("(") + 1
            end = self.message.index(")")
            return self.message[start:end]
        return None

    @property
    def churn(self) -> int:
        """Total lines changed (insertions + deletions)."""
        return self.insertions + self.deletions


@dataclass
class FileActivity:
    """Activity statistics for a file path."""

    path: str
    commit_count: int
    total_insertions: int = 0
    total_deletions: int = 0

    @property
    def churn(self) -> int:
        return self.total_insertions + self.total_deletions


def parse_git_log(
    repo_path: Path | str | None = None,
    max_commits: int | None = None,
) -> list[Commit]:
    """
    Parse git log into structured Commit objects.

    Args:
        repo_path: Path to git repository (defaults to current)
        max_commits: Limit number of commits to parse

    Returns:
        List of Commit objects ordered newest to oldest
    """
    cmd = ["git", "log", "--all", "--format=COMMIT_START%n%H%n%s%n%ae%n%aI", "--numstat"]

    if max_commits:
        cmd.insert(2, f"-n{max_commits}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=repo_path,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Git log failed: {result.stderr}")

    return list(_parse_log_output(result.stdout))


def _parse_log_output(output: str) -> Iterator[Commit]:
    """Parse git log output into Commit objects."""
    commits = output.split("COMMIT_START\n")

    for commit_block in commits:
        if not commit_block.strip():
            continue

        lines = commit_block.strip().split("\n")
        if len(lines) < 4:
            continue

        sha = lines[0]
        message = lines[1]
        author = lines[2]

        try:
            timestamp = datetime.fromisoformat(lines[3])
        except ValueError:
            continue

        # Parse numstat lines (insertions\tdeletions\tfilename)
        files: list[str] = []
        insertions = 0
        deletions = 0

        for line in lines[4:]:
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                try:
                    ins = int(parts[0]) if parts[0] != "-" else 0
                    dels = int(parts[1]) if parts[1] != "-" else 0
                    insertions += ins
                    deletions += dels
                    files.append(parts[2])
                except ValueError:
                    continue

        yield Commit(
            sha=sha,
            message=message,
            author=author,
            timestamp=timestamp,
            files_changed=tuple(files),
            insertions=insertions,
            deletions=deletions,
        )


def get_file_activity(
    repo_path: Path | str | None = None,
    limit: int = 100,
) -> list[FileActivity]:
    """
    Get file activity statistics (most touched files).

    Args:
        repo_path: Path to git repository
        limit: Maximum files to return

    Returns:
        List of FileActivity sorted by commit count descending
    """
    cmd = ["git", "log", "--all", "--format=", "--name-only"]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=repo_path,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Git log failed: {result.stderr}")

    # Count occurrences
    counts: dict[str, int] = {}
    for line in result.stdout.split("\n"):
        line = line.strip()
        if line:
            counts[line] = counts.get(line, 0) + 1

    # Sort by count descending
    sorted_files = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    return [FileActivity(path=path, commit_count=count) for path, count in sorted_files[:limit]]


def get_commit_count(repo_path: Path | str | None = None) -> int:
    """Get total commit count in repository."""
    result = subprocess.run(
        ["git", "rev-list", "--all", "--count"],
        capture_output=True,
        text=True,
        cwd=repo_path,
    )

    if result.returncode != 0:
        return 0

    return int(result.stdout.strip())


def get_authors(repo_path: Path | str | None = None) -> dict[str, int]:
    """Get author commit counts."""
    result = subprocess.run(
        ["git", "shortlog", "-sn", "--all"],
        capture_output=True,
        text=True,
        cwd=repo_path,
    )

    if result.returncode != 0:
        return {}

    authors = {}
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                count = int(parts[0].strip())
                name = parts[1].strip()
                authors[name] = count

    return authors
