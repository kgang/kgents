"""
Git History Service: Git Integration for Self-Reflective OS.

Provides comprehensive git history access for the Reflect interface:
- Recent commits with full metadata
- File history and blame information
- Spec/impl pair detection
- Commit search and diff viewing

Philosophy:
    "The git history IS the implementation chronicle."
    "Every commit is a witnessed decision."

AGENTESE Paths (via GitNode):
- self.git.history        - Recent commits
- self.git.file_history   - History for specific file
- self.git.blame          - Who wrote each line
- self.git.diff           - Show commit diff
- self.git.search         - Search commit messages
- self.git.spec_impl      - Linked spec/impl pairs

Usage:
    service = GitHistoryService()
    commits = await service.get_recent_commits(limit=50)
    history = await service.get_file_history("services/self/node.py")
    blame = await service.get_file_blame("services/self/node.py")
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================


@dataclass(frozen=True)
class CommitInfo:
    """
    Information about a git commit.

    Attributes:
        sha: Full commit SHA
        short_sha: Short SHA (first 8 chars)
        message: Commit message (first line)
        full_message: Full commit message
        author: Author name
        author_email: Author email
        date: Commit date
        files_changed: List of changed file paths
        insertions: Lines added
        deletions: Lines deleted
    """

    sha: str
    short_sha: str
    message: str
    full_message: str
    author: str
    author_email: str
    date: datetime
    files_changed: tuple[str, ...]
    insertions: int
    deletions: int

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "sha": self.sha,
            "short_sha": self.short_sha,
            "message": self.message,
            "full_message": self.full_message,
            "author": self.author,
            "author_email": self.author_email,
            "date": self.date.isoformat(),
            "files_changed": list(self.files_changed),
            "insertions": self.insertions,
            "deletions": self.deletions,
        }


@dataclass(frozen=True)
class BlameLine:
    """
    Blame information for a single line.

    Attributes:
        line_number: 1-indexed line number
        content: Line content
        commit_sha: Commit that last modified this line
        short_sha: Short SHA
        author: Author name
        author_email: Author email
        date: Commit date
    """

    line_number: int
    content: str
    commit_sha: str
    short_sha: str
    author: str
    author_email: str
    date: datetime

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "line_number": self.line_number,
            "content": self.content,
            "commit_sha": self.commit_sha,
            "short_sha": self.short_sha,
            "author": self.author,
            "author_email": self.author_email,
            "date": self.date.isoformat(),
        }


@dataclass(frozen=True)
class FileHistory:
    """
    Complete history for a file.

    Attributes:
        path: File path relative to repo root
        commits: List of commits that modified this file
        blame: List of blame lines (if requested)
        total_commits: Total number of commits
    """

    path: str
    commits: tuple[CommitInfo, ...]
    blame: tuple[BlameLine, ...] = ()
    total_commits: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "path": self.path,
            "commits": [c.to_dict() for c in self.commits],
            "blame": [b.to_dict() for b in self.blame],
            "total_commits": self.total_commits,
        }


@dataclass(frozen=True)
class CommitDetail:
    """
    Detailed information about a commit including diff.

    Attributes:
        commit: The commit info
        diff: Full diff output
        parent_sha: Parent commit SHA (first parent)
        stats: File change statistics
    """

    commit: CommitInfo
    diff: str
    parent_sha: str | None
    stats: dict[str, int]  # {file: +additions, -deletions}

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "commit": self.commit.to_dict(),
            "diff": self.diff,
            "parent_sha": self.parent_sha,
            "stats": self.stats,
        }


@dataclass(frozen=True)
class SpecImplPair:
    """
    Linked spec and implementation files.

    Attributes:
        spec_path: Path to spec file
        impl_paths: Paths to implementation files
        confidence: Confidence score [0.0, 1.0]
        link_type: How the link was determined
    """

    spec_path: str
    impl_paths: tuple[str, ...]
    confidence: float
    link_type: str  # "naming", "import", "content"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "spec_path": self.spec_path,
            "impl_paths": list(self.impl_paths),
            "confidence": self.confidence,
            "link_type": self.link_type,
        }


# =============================================================================
# Git History Service
# =============================================================================


class GitHistoryService:
    """
    Git history integration for self-reflection.

    Uses git commands via subprocess to extract history information.
    All operations are async and handle non-git directories gracefully.

    Teaching:
        gotcha: All paths are relative to repo_root, which is auto-detected
                from the current working directory or can be explicitly set.

        gotcha: Blame is expensive for large files. Use with care and
                consider caching results.

        gotcha: Spec/impl pair detection uses heuristics based on naming
                conventions and import analysis. Manual linking may be needed.
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        spec_dir: str = "spec",
        impl_dir: str = "impl/claude",
    ) -> None:
        """
        Initialize GitHistoryService.

        Args:
            repo_root: Root directory of the git repository.
                      Auto-detected if not provided.
            spec_dir: Relative path to spec directory (for spec/impl linking)
            impl_dir: Relative path to impl directory (for spec/impl linking)
        """
        self.repo_root = repo_root or self._detect_repo_root()
        self.spec_dir = spec_dir
        self.impl_dir = impl_dir
        self._is_git_repo: bool | None = None

    def _detect_repo_root(self) -> Path:
        """Detect the git repository root from current directory."""
        cwd = Path.cwd()
        current = cwd
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return cwd

    async def _run_git(
        self,
        *args: str,
        check: bool = True,
        timeout: float = 30.0,
    ) -> tuple[str, str]:
        """
        Run a git command and return stdout/stderr.

        Args:
            *args: Git command arguments
            check: Raise exception on non-zero exit
            timeout: Command timeout in seconds

        Returns:
            Tuple of (stdout, stderr)

        Raises:
            RuntimeError: If not a git repository or command fails
        """
        if self._is_git_repo is False:
            raise RuntimeError(f"Not a git repository: {self.repo_root}")

        cmd = ["git", "-C", str(self.repo_root), *args]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout,
            )

            if check and proc.returncode != 0:
                error = stderr.decode("utf-8", errors="replace")
                if "not a git repository" in error.lower():
                    self._is_git_repo = False
                    raise RuntimeError(f"Not a git repository: {self.repo_root}")
                raise RuntimeError(f"Git command failed: {error}")

            self._is_git_repo = True
            return stdout.decode("utf-8", errors="replace"), stderr.decode(
                "utf-8", errors="replace"
            )

        except asyncio.TimeoutError:
            raise RuntimeError(f"Git command timed out: {' '.join(cmd)}")
        except FileNotFoundError:
            raise RuntimeError("Git is not installed or not in PATH")

    async def is_git_repo(self) -> bool:
        """Check if repo_root is a git repository."""
        if self._is_git_repo is not None:
            return self._is_git_repo

        try:
            await self._run_git("rev-parse", "--git-dir")
            self._is_git_repo = True
        except RuntimeError:
            self._is_git_repo = False

        return self._is_git_repo

    async def get_recent_commits(self, limit: int = 50) -> list[CommitInfo]:
        """
        Get recent commits from the repository.

        Args:
            limit: Maximum number of commits to return

        Returns:
            List of CommitInfo objects
        """
        # Use a format that's easy to parse
        # Format: sha|short_sha|author|email|date|message
        format_str = "%H|%h|%an|%ae|%aI|%s"

        stdout, _ = await self._run_git(
            "log",
            f"--format={format_str}",
            f"-{limit}",
            "--shortstat",
        )

        commits = []
        lines = stdout.strip().split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Parse commit line
            if "|" in line:
                parts = line.split("|", 5)
                if len(parts) >= 6:
                    sha, short_sha, author, email, date_str, message = parts

                    # Parse insertions/deletions from next non-empty line
                    insertions = 0
                    deletions = 0
                    i += 1
                    while i < len(lines) and not lines[i].strip():
                        i += 1

                    if i < len(lines):
                        stat_line = lines[i].strip()
                        if "insertion" in stat_line or "deletion" in stat_line:
                            # Parse: "X files changed, Y insertions(+), Z deletions(-)"
                            ins_match = re.search(r"(\d+) insertion", stat_line)
                            del_match = re.search(r"(\d+) deletion", stat_line)
                            if ins_match:
                                insertions = int(ins_match.group(1))
                            if del_match:
                                deletions = int(del_match.group(1))
                            i += 1
                        else:
                            # Not a stat line, backtrack
                            pass

                    try:
                        date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    except ValueError:
                        date = datetime.now(timezone.utc)

                    commits.append(
                        CommitInfo(
                            sha=sha,
                            short_sha=short_sha,
                            message=message,
                            full_message=message,  # Will be enhanced later if needed
                            author=author,
                            author_email=email,
                            date=date,
                            files_changed=(),  # Populated on detail request
                            insertions=insertions,
                            deletions=deletions,
                        )
                    )
                else:
                    i += 1
            else:
                i += 1

        return commits

    async def get_file_history(
        self,
        path: str,
        limit: int = 50,
        include_blame: bool = False,
    ) -> FileHistory:
        """
        Get commit history for a specific file.

        Args:
            path: File path relative to repo root
            limit: Maximum number of commits
            include_blame: Whether to include blame information

        Returns:
            FileHistory with commits and optional blame
        """
        format_str = "%H|%h|%an|%ae|%aI|%s"

        stdout, _ = await self._run_git(
            "log",
            f"--format={format_str}",
            f"-{limit}",
            "--follow",
            "--",
            path,
        )

        commits = []
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if not line or "|" not in line:
                continue

            parts = line.split("|", 5)
            if len(parts) >= 6:
                sha, short_sha, author, email, date_str, message = parts

                try:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except ValueError:
                    date = datetime.now(timezone.utc)

                commits.append(
                    CommitInfo(
                        sha=sha,
                        short_sha=short_sha,
                        message=message,
                        full_message=message,
                        author=author,
                        author_email=email,
                        date=date,
                        files_changed=(path,),
                        insertions=0,
                        deletions=0,
                    )
                )

        blame: tuple[BlameLine, ...] = ()
        if include_blame:
            blame = tuple(await self.get_file_blame(path))

        # Get total commit count
        count_stdout, _ = await self._run_git(
            "rev-list",
            "--count",
            "HEAD",
            "--",
            path,
        )
        total_commits = (
            int(count_stdout.strip()) if count_stdout.strip().isdigit() else len(commits)
        )

        return FileHistory(
            path=path,
            commits=tuple(commits),
            blame=tuple(blame),
            total_commits=total_commits,
        )

    async def get_file_blame(self, path: str) -> list[BlameLine]:
        """
        Get blame information for a file.

        Args:
            path: File path relative to repo root

        Returns:
            List of BlameLine objects
        """
        # Use porcelain format for easier parsing
        stdout, _ = await self._run_git(
            "blame",
            "--porcelain",
            "--",
            path,
        )

        blame_lines: list[BlameLine] = []
        current_sha = ""
        current_author = ""
        current_email = ""
        current_date = datetime.now(timezone.utc)
        line_number = 0

        for line in stdout.split("\n"):
            # SHA line (starts with 40-char hex)
            if re.match(r"^[0-9a-f]{40} ", line):
                parts = line.split()
                current_sha = parts[0]
                line_number = int(parts[2]) if len(parts) > 2 else line_number + 1

            elif line.startswith("author "):
                current_author = line[7:]

            elif line.startswith("author-mail "):
                current_email = line[12:].strip("<>")

            elif line.startswith("author-time "):
                try:
                    ts = int(line[12:])
                    current_date = datetime.fromtimestamp(ts, tz=timezone.utc)
                except ValueError:
                    pass

            elif line.startswith("\t"):
                # This is the content line
                content = line[1:]  # Remove leading tab
                blame_lines.append(
                    BlameLine(
                        line_number=line_number,
                        content=content,
                        commit_sha=current_sha,
                        short_sha=current_sha[:8],
                        author=current_author,
                        author_email=current_email,
                        date=current_date,
                    )
                )

        return blame_lines

    async def get_commit_detail(self, sha: str) -> CommitDetail:
        """
        Get detailed information about a commit.

        Args:
            sha: Commit SHA (full or short)

        Returns:
            CommitDetail with full diff and stats
        """
        # Get commit info
        format_str = "%H|%h|%an|%ae|%aI|%s|%b|%P"
        stdout, _ = await self._run_git(
            "show",
            f"--format={format_str}",
            "--stat",
            "-p",
            sha,
        )

        lines = stdout.split("\n")
        first_line = lines[0] if lines else ""
        parts = first_line.split("|", 7)

        if len(parts) < 8:
            raise RuntimeError(f"Invalid commit: {sha}")

        full_sha, short_sha, author, email, date_str, subject, body, parents = parts

        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            date = datetime.now(timezone.utc)

        parent_sha = parents.split()[0] if parents.strip() else None

        # Parse files changed from stat section
        files_changed = []
        stats: dict[str, int] = {}
        diff_started = False
        diff_lines = []

        for line in lines[1:]:
            if line.startswith("diff --git"):
                diff_started = True

            if diff_started:
                diff_lines.append(line)
            elif "|" in line and not diff_started:
                # Stats line: " file.py | 10 ++--"
                parts = line.split("|")
                if len(parts) >= 2:
                    file_path = parts[0].strip()
                    if file_path:
                        files_changed.append(file_path)
                        # Parse +/- counts
                        stat_part = parts[1].strip()
                        plus_count = stat_part.count("+")
                        minus_count = stat_part.count("-")
                        stats[file_path] = plus_count - minus_count

        commit = CommitInfo(
            sha=full_sha,
            short_sha=short_sha,
            message=subject,
            full_message=f"{subject}\n\n{body}".strip() if body else subject,
            author=author,
            author_email=email,
            date=date,
            files_changed=tuple(files_changed),
            insertions=sum(v for v in stats.values() if v > 0),
            deletions=abs(sum(v for v in stats.values() if v < 0)),
        )

        return CommitDetail(
            commit=commit,
            diff="\n".join(diff_lines),
            parent_sha=parent_sha,
            stats=stats,
        )

    async def get_diff(self, sha: str) -> str:
        """
        Get the diff for a commit.

        Args:
            sha: Commit SHA

        Returns:
            Diff output as string
        """
        stdout, _ = await self._run_git("show", "--stat", "-p", sha)
        return stdout

    async def search_commits(
        self,
        query: str,
        limit: int = 50,
        author: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[CommitInfo]:
        """
        Search commits by message, author, or date range.

        Args:
            query: Search query (searches commit messages)
            limit: Maximum number of results
            author: Filter by author name/email
            since: Filter commits after this date
            until: Filter commits before this date

        Returns:
            List of matching commits
        """
        format_str = "%H|%h|%an|%ae|%aI|%s"
        args = ["log", f"--format={format_str}", f"-{limit}", "--grep", query]

        if author:
            args.extend(["--author", author])
        if since:
            args.extend(["--since", since.isoformat()])
        if until:
            args.extend(["--until", until.isoformat()])

        stdout, _ = await self._run_git(*args)

        commits = []
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if not line or "|" not in line:
                continue

            parts = line.split("|", 5)
            if len(parts) >= 6:
                sha, short_sha, author_name, email, date_str, message = parts

                try:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except ValueError:
                    date = datetime.now(timezone.utc)

                commits.append(
                    CommitInfo(
                        sha=sha,
                        short_sha=short_sha,
                        message=message,
                        full_message=message,
                        author=author_name,
                        author_email=email,
                        date=date,
                        files_changed=(),
                        insertions=0,
                        deletions=0,
                    )
                )

        return commits

    async def get_spec_impl_pairs(self) -> list[SpecImplPair]:
        """
        Find linked spec and implementation files.

        Uses heuristics based on:
        1. Naming conventions (spec/agents/x.md -> impl/claude/agents/x/)
        2. Import analysis (spec references in docstrings)
        3. Directory structure

        Returns:
            List of SpecImplPair objects
        """
        pairs: list[SpecImplPair] = []

        spec_path = self.repo_root / self.spec_dir
        impl_path = self.repo_root / self.impl_dir

        if not spec_path.exists():
            return pairs

        # Find all spec files
        for spec_file in spec_path.rglob("*.md"):
            relative_spec = str(spec_file.relative_to(self.repo_root))
            impl_paths: list[str] = []

            # Strategy 1: Naming convention
            # spec/agents/d-gent.md -> impl/claude/agents/d/
            stem = spec_file.stem.replace("-", "_").replace("_", "")
            potential_impls = [
                impl_path / spec_file.relative_to(spec_path).parent / stem,
                impl_path / spec_file.relative_to(spec_path).parent / spec_file.stem,
                impl_path / spec_file.relative_to(spec_path).parent / f"{stem}.py",
            ]

            for potential in potential_impls:
                if potential.exists():
                    impl_paths.append(str(potential.relative_to(self.repo_root)))

            # Strategy 2: Look for references in impl files
            if impl_path.exists():
                search_pattern = f"See: {relative_spec}"
                for py_file in impl_path.rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding="utf-8", errors="ignore")
                        if search_pattern in content or spec_file.name in content:
                            impl_rel = str(py_file.relative_to(self.repo_root))
                            if impl_rel not in impl_paths:
                                impl_paths.append(impl_rel)
                    except Exception:
                        continue

            if impl_paths:
                pairs.append(
                    SpecImplPair(
                        spec_path=relative_spec,
                        impl_paths=tuple(impl_paths),
                        confidence=0.8 if len(impl_paths) > 1 else 0.9,
                        link_type="naming" if len(impl_paths) == 1 else "mixed",
                    )
                )

        return pairs

    async def get_current_branch(self) -> str:
        """Get the current branch name."""
        stdout, _ = await self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        return stdout.strip()

    async def get_changed_files(self) -> list[str]:
        """Get list of uncommitted changed files."""
        stdout, _ = await self._run_git("status", "--porcelain")
        files = []
        for line in stdout.strip().split("\n"):
            if line.strip():
                # Format: "XY filename" or "XY filename -> newname"
                parts = line[3:].split(" -> ")
                files.append(parts[-1])
        return files


# =============================================================================
# Factory Functions
# =============================================================================


_git_service: GitHistoryService | None = None


def get_git_service(repo_root: Path | None = None) -> GitHistoryService:
    """
    Get or create the GitHistoryService singleton.

    Args:
        repo_root: Optional repo root (only used on first call)

    Returns:
        GitHistoryService instance
    """
    global _git_service
    if _git_service is None:
        _git_service = GitHistoryService(repo_root=repo_root)
    return _git_service


def reset_git_service() -> None:
    """Reset the GitHistoryService singleton (for testing)."""
    global _git_service
    _git_service = None


__all__ = [
    "CommitInfo",
    "BlameLine",
    "FileHistory",
    "CommitDetail",
    "SpecImplPair",
    "GitHistoryService",
    "get_git_service",
    "reset_git_service",
]
