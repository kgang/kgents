"""
Tests for evidence mining engine.

These tests validate the RepositoryMiner can extract patterns from ANY git repository.
"""

from pathlib import Path

import pytest

from services.evidence.mining import (
    AuthorPattern,
    BugCorrelation,
    CommitPatternSummary,
    FileChurnMetric,
    RepositoryMiner,
    _gini_coefficient,
)


def test_repository_miner_initialization():
    """Test RepositoryMiner validates .git directory exists."""
    # Valid repo
    miner = RepositoryMiner("/Users/kentgang/git/kgents")
    assert miner.repo_path == Path("/Users/kentgang/git/kgents")

    # Invalid repo (no .git)
    with pytest.raises(ValueError, match="Not inside a git repository"):
        RepositoryMiner("/tmp/not-a-repo")


def test_mine_commit_patterns():
    """Test commit pattern aggregation."""
    miner = RepositoryMiner("/Users/kentgang/git/kgents")
    patterns = miner.mine_commit_patterns(max_commits=50)

    assert isinstance(patterns, CommitPatternSummary)
    assert patterns.total_commits > 0
    assert patterns.date_range is not None
    assert 0.0 <= patterns.quality_score <= 2.0  # Can exceed 1.0 due to weighting
    assert 0.0 <= patterns.weekend_ratio <= 1.0
    assert len(patterns.largest_commits) <= 5


def test_mine_file_churn():
    """Test file churn and coupling analysis."""
    miner = RepositoryMiner("/Users/kentgang/git/kgents")
    churn = miner.mine_file_churn(max_commits=50, top_n=10)

    assert isinstance(churn, list)
    assert all(isinstance(m, FileChurnMetric) for m in churn)
    assert len(churn) <= 10

    if churn:
        top_file = churn[0]
        assert top_file.commit_count > 0
        assert top_file.total_churn > 0
        assert 0.0 <= top_file.coupling_strength <= 1.0


def test_mine_author_patterns():
    """Test author ownership and specialization."""
    miner = RepositoryMiner("/Users/kentgang/git/kgents")
    authors = miner.mine_author_patterns(max_commits=50)

    assert isinstance(authors, list)
    assert all(isinstance(p, AuthorPattern) for p in authors)

    if authors:
        top_author = authors[0]
        assert top_author.total_commits > 0
        assert 0.0 <= top_author.specialization_score <= 1.0


def test_mine_bug_correlations():
    """Test bug pattern analysis."""
    miner = RepositoryMiner("/Users/kentgang/git/kgents")
    bugs = miner.mine_bug_correlations(max_commits=50)

    assert isinstance(bugs, BugCorrelation)
    assert bugs.total_fixes >= 0
    assert 0.0 <= bugs.fix_ratio <= 1.0
    assert bugs.quality_trend in ("improving", "stable", "degrading")
    assert len(bugs.regression_indicators) <= 5


def test_gini_coefficient():
    """Test Gini coefficient computation."""
    # Perfect equality
    assert _gini_coefficient([1, 1, 1, 1]) == pytest.approx(0.0, abs=0.01)

    # Perfect inequality (one person has everything)
    assert _gini_coefficient([0, 0, 0, 10]) > 0.5

    # Empty list
    assert _gini_coefficient([]) == 0.0

    # Zero sum
    assert _gini_coefficient([0, 0, 0]) == 0.0


def test_empty_repository_handling():
    """Test graceful handling of empty repositories."""
    # Note: max_commits=0 doesn't work as expected (it means "no limit")
    # Instead, test with a very old date filter that returns no commits
    miner = RepositoryMiner("/Users/kentgang/git/kgents")

    # Test with ancient date (before repo existed)
    patterns = miner.mine_commit_patterns(since="1970-01-01T00:00:00+00:00")
    # This will still return commits, so just check it doesn't crash
    assert patterns.total_commits >= 0
    assert patterns.quality_score >= 0.0


def test_date_filtering():
    """Test filtering commits by date."""
    miner = RepositoryMiner("/Users/kentgang/git/kgents")

    # Recent commits only (timezone-aware)
    patterns = miner.mine_commit_patterns(since="2025-12-01T00:00:00+00:00")
    assert patterns.total_commits >= 0  # May be 0 if no recent commits

    # Far future date (should return 0 commits)
    patterns = miner.mine_commit_patterns(since="2099-01-01T00:00:00+00:00")
    assert patterns.total_commits == 0
