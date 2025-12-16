"""
Git Source: Read context from git commands.

Git sources provide dynamic context about the current repository state:
- Current branch
- Modified files
- Recent commits
- Uncommitted changes

These are medium-rigidity sources (0.6) since git state is
deterministic but changes with user activity.
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from .base import SectionSource, SourcePriority, SourceResult

if TYPE_CHECKING:
    from ..compiler import CompilationContext

logger = logging.getLogger(__name__)


@dataclass
class GitSource(SectionSource):
    """
    Source that reads from git commands.

    Runs git commands to extract repository state information.
    Results are cached per compilation to avoid repeated subprocess calls.
    """

    name: str = "git:status"
    priority: SourcePriority = field(default=SourcePriority.GIT)
    rigidity: float = 0.6
    timeout: float = 5.0  # Seconds

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Run git commands and extract status."""
        traces = ["GitSource: Gathering repository status"]

        # Determine repo root
        repo_root = context.project_root
        traces.append(f"Repository root: {repo_root}")

        if not (repo_root / ".git").exists():
            traces.append("Not a git repository")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        # Gather git info
        try:
            branch = await self._run_git(
                ["git", "branch", "--show-current"],
                repo_root,
                traces,
            )
            traces.append(f"Current branch: {branch}")

            status_output = await self._run_git(
                ["git", "status", "--porcelain"],
                repo_root,
                traces,
            )
            modified_files = self._parse_status(status_output, traces)

            recent_commits = await self._run_git(
                ["git", "log", "--oneline", "-5"],
                repo_root,
                traces,
            )
            traces.append(f"Got {len(recent_commits.splitlines())} recent commits")

            # Build content
            content = self._build_content(
                branch=branch,
                modified_files=modified_files,
                recent_commits=recent_commits,
                traces=traces,
            )

            return SourceResult(
                content=content,
                success=True,
                source_name=self.name,
                source_path=repo_root / ".git",
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        except Exception as e:
            traces.append(f"Error gathering git status: {e}")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

    async def _run_git(
        self,
        cmd: list[str],
        cwd: Path,
        traces: list[str],
    ) -> str:
        """Run a git command and return output."""
        try:
            # Use asyncio subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout,
            )

            if process.returncode != 0:
                traces.append(f"Git command failed: {cmd[1]} - {stderr.decode()}")
                return ""

            return stdout.decode().strip()

        except asyncio.TimeoutError:
            traces.append(f"Git command timed out: {cmd[1]}")
            return ""
        except Exception as e:
            traces.append(f"Git command error: {e}")
            return ""

    def _parse_status(
        self, status_output: str, traces: list[str]
    ) -> dict[str, list[str]]:
        """Parse git status --porcelain output."""
        modified: dict[str, list[str]] = {
            "modified": [],
            "added": [],
            "deleted": [],
            "untracked": [],
        }

        for line in status_output.splitlines():
            if not line:
                continue

            status = line[:2]
            filename = line[3:].strip()

            if status.startswith("??"):
                modified["untracked"].append(filename)
            elif "M" in status:
                modified["modified"].append(filename)
            elif "A" in status:
                modified["added"].append(filename)
            elif "D" in status:
                modified["deleted"].append(filename)

        total = sum(len(v) for v in modified.values())
        traces.append(f"Parsed status: {total} changed files")
        return modified

    def _build_content(
        self,
        branch: str,
        modified_files: dict[str, list[str]],
        recent_commits: str,
        traces: list[str],
    ) -> str:
        """Build the git context content."""
        lines = ["## Git Context"]
        lines.append("")

        # Branch
        lines.append(f"**Branch**: `{branch}`")
        lines.append("")

        # Modified files summary
        total_changes = sum(len(v) for v in modified_files.values())
        if total_changes > 0:
            lines.append("### Working Tree")
            lines.append("")

            if modified_files["modified"]:
                count = len(modified_files["modified"])
                files = ", ".join(
                    f"`{f.split('/')[-1]}`" for f in modified_files["modified"][:5]
                )
                suffix = f" (+{count - 5} more)" if count > 5 else ""
                lines.append(f"- **Modified** ({count}): {files}{suffix}")

            if modified_files["added"]:
                count = len(modified_files["added"])
                files = ", ".join(
                    f"`{f.split('/')[-1]}`" for f in modified_files["added"][:5]
                )
                suffix = f" (+{count - 5} more)" if count > 5 else ""
                lines.append(f"- **Added** ({count}): {files}{suffix}")

            if modified_files["untracked"]:
                count = len(modified_files["untracked"])
                lines.append(f"- **Untracked**: {count} files")

            lines.append("")
        else:
            lines.append("*Working tree clean.*")
            lines.append("")

        # Recent commits (compact)
        if recent_commits:
            lines.append("### Recent Commits")
            lines.append("```")
            for line in recent_commits.splitlines()[:3]:
                lines.append(line)
            lines.append("```")
            lines.append("")

        traces.append(f"Built git content: {len(''.join(lines))} chars")
        return "\n".join(lines)


@dataclass
class GitBranchSource(SectionSource):
    """
    Simple source that returns just the current branch.

    Useful for minimal context injection.
    """

    name: str = "git:branch"
    priority: SourcePriority = field(default=SourcePriority.GIT)
    rigidity: float = 0.8  # More rigid - just the branch name
    timeout: float = 2.0

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Get current branch name."""
        traces = ["GitBranchSource: Getting current branch"]

        repo_root = context.project_root
        if not (repo_root / ".git").exists():
            traces.append("Not a git repository")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                "branch",
                "--show-current",
                cwd=repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout,
            )

            branch = stdout.decode().strip()
            traces.append(f"Branch: {branch}")

            return SourceResult(
                content=f"**Branch**: `{branch}`",
                success=True,
                source_name=self.name,
                source_path=repo_root / ".git",
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        except Exception as e:
            traces.append(f"Error: {e}")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )


__all__ = [
    "GitSource",
    "GitBranchSource",
]
