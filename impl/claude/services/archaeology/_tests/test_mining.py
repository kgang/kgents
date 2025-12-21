"""
Tests for git mining functionality.

Tests cover:
- Commit parsing from git log
- File activity extraction
- Commit type classification
"""

from datetime import datetime, timezone

import pytest

from services.archaeology.mining import (
    Commit,
    FileActivity,
    get_commit_count,
    get_file_activity,
    parse_git_log,
)


class TestCommit:
    """Tests for Commit dataclass."""

    def test_commit_is_frozen(self):
        """Commits should be immutable."""
        commit = Commit(
            sha="abc123",
            message="test commit",
            author="kent@example.com",
            timestamp=datetime.now(timezone.utc),
            files_changed=("file.py",),
            insertions=10,
            deletions=5,
        )

        with pytest.raises(AttributeError):
            commit.sha = "different"  # type: ignore

    def test_is_refactor_many_files_low_net_change(self):
        """Refactors touch many files with low net change."""
        commit = Commit(
            sha="abc123",
            message="refactor: rename variables",
            author="kent@example.com",
            timestamp=datetime.now(timezone.utc),
            files_changed=("a.py", "b.py", "c.py", "d.py", "e.py", "f.py"),
            insertions=50,
            deletions=48,  # Net change = 2
        )

        assert commit.is_refactor is True

    def test_is_feature_adds_more_than_removes(self):
        """Features add significantly more than they remove."""
        commit = Commit(
            sha="abc123",
            message="feat: add new capability",
            author="kent@example.com",
            timestamp=datetime.now(timezone.utc),
            files_changed=("new.py", "tests/test_new.py"),
            insertions=150,
            deletions=10,  # insertions > deletions * 2
        )

        assert commit.is_feature is True

    def test_is_fix_small_targeted_change(self):
        """Fixes are small, targeted changes."""
        commit = Commit(
            sha="abc123",
            message="fix: handle edge case",
            author="kent@example.com",
            timestamp=datetime.now(timezone.utc),
            files_changed=("module.py",),
            insertions=15,
            deletions=5,
        )

        assert commit.is_fix is True

    def test_commit_type_extraction(self):
        """Extract commit type from conventional commit."""
        cases = [
            ("feat: add feature", "feat"),
            ("fix(brain): bug fix", "fix"),
            ("refactor(agentese): cleanup", "refactor"),
            ("docs: update readme", "docs"),
            ("plain message without type", "other"),
        ]

        for message, expected in cases:
            commit = Commit(
                sha="abc",
                message=message,
                author="",
                timestamp=datetime.now(timezone.utc),
                files_changed=(),
                insertions=0,
                deletions=0,
            )
            assert commit.commit_type == expected, f"Failed for: {message}"

    def test_scope_extraction(self):
        """Extract scope from conventional commit."""
        commit = Commit(
            sha="abc",
            message="feat(brain): add memory",
            author="",
            timestamp=datetime.now(timezone.utc),
            files_changed=(),
            insertions=0,
            deletions=0,
        )

        assert commit.scope == "brain"

    def test_scope_none_when_missing(self):
        """Scope is None when not present."""
        commit = Commit(
            sha="abc",
            message="feat: add something",
            author="",
            timestamp=datetime.now(timezone.utc),
            files_changed=(),
            insertions=0,
            deletions=0,
        )

        assert commit.scope is None

    def test_churn_calculation(self):
        """Churn is insertions + deletions."""
        commit = Commit(
            sha="abc",
            message="test",
            author="",
            timestamp=datetime.now(timezone.utc),
            files_changed=(),
            insertions=100,
            deletions=50,
        )

        assert commit.churn == 150


class TestFileActivity:
    """Tests for FileActivity dataclass."""

    def test_churn_calculation(self):
        """FileActivity churn is insertions + deletions."""
        activity = FileActivity(
            path="file.py",
            commit_count=10,
            total_insertions=500,
            total_deletions=200,
        )

        assert activity.churn == 700


class TestParseGitLog:
    """Integration tests for git log parsing."""

    @pytest.mark.integration
    def test_parse_returns_commits(self):
        """Parsing should return a list of Commits."""
        # This runs against the actual repo
        commits = parse_git_log(max_commits=10)

        assert len(commits) > 0
        assert all(isinstance(c, Commit) for c in commits)

    @pytest.mark.integration
    def test_commits_have_required_fields(self):
        """Each commit should have all required fields."""
        commits = parse_git_log(max_commits=5)

        for commit in commits:
            assert commit.sha
            assert len(commit.sha) == 40
            assert commit.message
            assert commit.author
            assert commit.timestamp

    @pytest.mark.integration
    def test_commits_ordered_newest_first(self):
        """Commits should be ordered newest to oldest."""
        commits = parse_git_log(max_commits=10)

        if len(commits) >= 2:
            for i in range(len(commits) - 1):
                assert commits[i].timestamp >= commits[i + 1].timestamp


class TestGetFileActivity:
    """Tests for file activity extraction."""

    @pytest.mark.integration
    def test_returns_file_activity(self):
        """Should return list of FileActivity."""
        activity = get_file_activity(limit=10)

        assert len(activity) > 0
        assert all(isinstance(a, FileActivity) for a in activity)

    @pytest.mark.integration
    def test_sorted_by_commit_count(self):
        """Results should be sorted by commit count descending."""
        activity = get_file_activity(limit=10)

        for i in range(len(activity) - 1):
            assert activity[i].commit_count >= activity[i + 1].commit_count


class TestGetCommitCount:
    """Tests for commit count."""

    @pytest.mark.integration
    def test_returns_positive_count(self):
        """Should return a positive commit count."""
        count = get_commit_count()

        assert count > 0
        assert isinstance(count, int)
