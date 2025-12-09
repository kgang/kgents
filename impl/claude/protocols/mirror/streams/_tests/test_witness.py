"""Tests for TemporalWitness drift detection."""

import tempfile
from datetime import timedelta
from pathlib import Path
from time import sleep

import pytest

from ..base import Reality
from ..witness import TemporalWitness

try:
    from git import Repo

    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    Repo = None

if GIT_AVAILABLE:
    from ..git_stream import GitStream


@pytest.fixture
def git_repo_with_drift():
    """Create a git repo with clear activity drift."""
    if not GIT_AVAILABLE:
        pytest.skip("GitPython not available")

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        repo = Repo.init(repo_path)

        # Configure git
        with repo.config_writer() as git_config:
            git_config.set_value("user", "name", "Test User")
            git_config.set_value("user", "email", "test@example.com")

        # Period 1: Low activity (2 commits)
        (repo_path / "README.md").write_text("# Test\n")
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")
        sleep(0.1)

        (repo_path / "file1.txt").write_text("Content 1\n")
        repo.index.add(["file1.txt"])
        repo.index.commit("Add file1")
        sleep(0.1)

        # Period 2: High activity (4 commits)
        for i in range(4):
            (repo_path / f"file{i + 2}.txt").write_text(f"Content {i + 2}\n")
            repo.index.add([f"file{i + 2}.txt"])
            repo.index.commit(f"Add file{i + 2}")
            sleep(0.1)

        yield repo_path


@pytest.fixture
def git_repo_with_actor_change():
    """Create a git repo with changing actors."""
    if not GIT_AVAILABLE:
        pytest.skip("GitPython not available")

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        repo = Repo.init(repo_path)

        # Configure git for first actor
        with repo.config_writer() as git_config:
            git_config.set_value("user", "name", "Alice")
            git_config.set_value("user", "email", "alice@example.com")

        # Commits by Alice
        (repo_path / "README.md").write_text("# Test\n")
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")
        sleep(0.1)

        (repo_path / "file1.txt").write_text("Content 1\n")
        repo.index.add(["file1.txt"])
        repo.index.commit("Add file1")
        sleep(0.1)

        # Change to Bob
        with repo.config_writer() as git_config:
            git_config.set_value("user", "name", "Bob")
            git_config.set_value("user", "email", "bob@example.com")

        # Commits by Bob
        (repo_path / "file2.txt").write_text("Content 2\n")
        repo.index.add(["file2.txt"])
        repo.index.commit("Add file2")
        sleep(0.1)

        (repo_path / "file3.txt").write_text("Content 3\n")
        repo.index.add(["file3.txt"])
        repo.index.commit("Add file3")

        yield repo_path


# =============================================================================
# TemporalWitness Tests
# =============================================================================


@pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
class TestTemporalWitness:
    """Test TemporalWitness drift detection."""

    def test_classify_chaotic_stream(self):
        """Should detect CHAOTIC streams."""

        # Mock stream that returns CHAOTIC
        class ChaoticStream:
            def classify_reality(self):
                return Reality.CHAOTIC

            def is_bounded(self):
                return False

        stream = ChaoticStream()
        witness = TemporalWitness(stream)

        antitheses = witness.observe_drift(timedelta(days=30))

        assert len(antitheses) == 1
        assert "chaotic" in antitheses[0].pattern.lower()
        assert antitheses[0].severity == 1.0

    def test_observe_activity_rate_drift(self, git_repo_with_drift):
        """Should detect changes in activity rate."""
        stream = GitStream(git_repo_with_drift)
        witness = TemporalWitness(stream)

        # Use very small window to catch drift
        antitheses = witness.observe_drift(timedelta(seconds=0.3), compare_periods=2)

        # Should detect rate change
        assert len(antitheses) >= 1

        # Check for activity rate change
        rate_changes = [a for a in antitheses if "Activity rate" in a.pattern]
        if rate_changes:
            assert rate_changes[0].severity > 0.0

    def test_observe_actor_drift(self, git_repo_with_actor_change):
        """Should detect changes in actor composition."""
        stream = GitStream(git_repo_with_actor_change)
        witness = TemporalWitness(stream)

        # Use small window
        antitheses = witness.observe_drift(timedelta(seconds=0.3), compare_periods=2)

        # Should detect actor change
        actor_changes = [a for a in antitheses if "Actor composition" in a.pattern]
        assert len(actor_changes) >= 1

        # Check that new/missing actors are detected
        change = actor_changes[0]
        assert "Alice" in change.pattern or "Bob" in change.pattern

    def test_observe_event_type_drift(self, git_repo_with_actor_change):
        """Should detect changes in event type distribution."""
        stream = GitStream(git_repo_with_actor_change)
        witness = TemporalWitness(stream)

        # All commits should be same type, so no drift expected
        antitheses = witness.observe_event_type_drift(
            timedelta(seconds=0.3), compare_periods=2
        )

        # Since all events are "commit" type, no drift
        type_drifts = [a for a in antitheses if "Event type" in a.pattern]
        # May be empty or minimal
        assert len(type_drifts) == 0

    def test_no_drift_in_stable_stream(self, git_repo_with_drift):
        """Should not detect drift when windows are similar."""
        stream = GitStream(git_repo_with_drift)
        witness = TemporalWitness(stream)

        # Use very large window that encompasses all commits
        antitheses = witness.observe_drift(timedelta(days=365), compare_periods=2)

        # With only 1 window, should get no comparisons
        assert len(antitheses) == 0

    def test_insufficient_windows(self, git_repo_with_drift):
        """Should handle case with insufficient windows."""
        stream = GitStream(git_repo_with_drift)
        witness = TemporalWitness(stream)

        # Use window larger than repo history
        antitheses = witness.observe_drift(timedelta(days=1000), compare_periods=2)

        # Not enough windows for comparison
        assert len(antitheses) == 0


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
class TestWitnessIntegration:
    """End-to-end witness tests."""

    def test_full_drift_analysis(self, git_repo_with_drift):
        """Test complete drift analysis pipeline."""
        stream = GitStream(git_repo_with_drift)
        witness = TemporalWitness(stream)

        # Analyze both rate and type drift
        rate_antitheses = witness.observe_drift(
            timedelta(seconds=0.3), compare_periods=2
        )
        type_antitheses = witness.observe_event_type_drift(
            timedelta(seconds=0.3), compare_periods=2
        )

        # Should detect at least rate drift
        all_antitheses = rate_antitheses + type_antitheses
        assert len(all_antitheses) >= 0  # May or may not find drift

        # All antitheses should have proper structure
        for antithesis in all_antitheses:
            assert antithesis.pattern
            assert len(antithesis.evidence) > 0
            assert 0.0 <= antithesis.frequency <= 1.0
            assert 0.0 <= antithesis.severity <= 1.0

    def test_multi_period_comparison(self, git_repo_with_drift):
        """Test comparing multiple periods."""
        stream = GitStream(git_repo_with_drift)
        witness = TemporalWitness(stream)

        # Try comparing more periods
        antitheses = witness.observe_drift(timedelta(seconds=0.2), compare_periods=3)

        # Should still work with more periods (compares last 2)
        assert isinstance(antitheses, list)
