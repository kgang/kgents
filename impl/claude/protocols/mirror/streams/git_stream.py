"""GitStream: Git commit history as event stream."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncIterator, Iterator

try:
    from git import Repo
except ImportError:
    Repo = None  # type: ignore

from .base import Event, Reality, SlidingWindow


@dataclass
class GitStream:
    """Git commit history as event stream."""

    repo_path: Path
    branch: str = "main"

    def __post_init__(self):
        if Repo is None:
            raise ImportError(
                "GitPython is required for GitStream. Install with: pip install gitpython"
            )
        self.repo_path = Path(self.repo_path)

    def classify_reality(self) -> Reality:
        """Git history is PROBABILISTIC."""
        return Reality.PROBABILISTIC

    def is_bounded(self) -> bool:
        """Git history is finite."""
        return True

    def estimate_size(self) -> int:
        """Count commits in branch."""
        repo = Repo(self.repo_path)
        return sum(1 for _ in repo.iter_commits(self.branch))

    def has_cycles(self) -> bool:
        """Git DAG has no cycles."""
        return False

    def events(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> Iterator[Event]:
        """Iterate commits as events."""
        repo = Repo(self.repo_path)
        count = 0

        for commit in repo.iter_commits(self.branch):
            commit_time = datetime.fromtimestamp(commit.committed_date)
            if start and commit_time < start:
                continue
            if end and commit_time > end:
                continue

            # Get diff stats
            diff_data = {}
            files_changed = []
            stats = {}

            try:
                if commit.parents:
                    diff = commit.diff(commit.parents[0])
                    files_changed = [item.a_path or item.b_path for item in diff]
                    stats = dict(commit.stats.files)
                else:
                    # Initial commit
                    files_changed = list(commit.stats.files.keys())
                    stats = dict(commit.stats.files)

                diff_data = {"files": files_changed, "stats": stats}
            except Exception:
                # If diff fails, just record what we can
                diff_data = {"files": [], "stats": {}}

            yield Event(
                id=commit.hexsha,
                timestamp=commit_time,
                actor=commit.author.name,
                event_type="commit",
                data={
                    "message": commit.message,
                    **diff_data,
                },
                metadata={
                    "branch": self.branch,
                    "author_email": commit.author.email,
                    "committer": commit.committer.name,
                },
            )

            count += 1
            if limit and count >= limit:
                break

    async def events_async(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[Event]:
        """Async variant (wraps sync implementation)."""
        for event in self.events(start=start, end=end, limit=limit):
            yield event

    def window(self, duration: timedelta) -> SlidingWindow:
        """Create sliding window view."""
        return SlidingWindow(self, window_size=duration)
