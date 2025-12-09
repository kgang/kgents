"""Integration tests for EventStream protocol with git fixtures."""

import tempfile
from datetime import timedelta
from pathlib import Path

import pytest

from ..base import EntropyBudget, Event, Reality, process_stream_with_budget
from ..composition import ComposedStream, FilteredStream, MappedStream

try:
    from git import Repo

    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    Repo = None

if GIT_AVAILABLE:
    from ..git_stream import GitStream


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def git_repo():
    """Create a temporary git repository with some commits."""
    if not GIT_AVAILABLE:
        pytest.skip("GitPython not available")

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        repo = Repo.init(repo_path)

        # Configure git
        with repo.config_writer() as git_config:
            git_config.set_value("user", "name", "Test User")
            git_config.set_value("user", "email", "test@example.com")

        # Create initial commit
        (repo_path / "README.md").write_text("# Test Repo\n")
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")

        # Add more commits
        (repo_path / "file1.txt").write_text("Content 1\n")
        repo.index.add(["file1.txt"])
        repo.index.commit("Add file1")

        (repo_path / "file2.txt").write_text("Content 2\n")
        repo.index.add(["file2.txt"])
        repo.index.commit("Add file2")

        # Modify a file
        (repo_path / "file1.txt").write_text("Content 1 updated\n")
        repo.index.add(["file1.txt"])
        repo.index.commit("Update file1")

        yield repo_path


# =============================================================================
# GitStream Tests
# =============================================================================


@pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
class TestGitStream:
    """Test GitStream implementation."""

    def test_classify_reality(self, git_repo):
        """GitStream should classify as PROBABILISTIC."""
        stream = GitStream(git_repo)
        assert stream.classify_reality() == Reality.PROBABILISTIC

    def test_is_bounded(self, git_repo):
        """GitStream is bounded."""
        stream = GitStream(git_repo)
        assert stream.is_bounded() is True

    def test_has_cycles(self, git_repo):
        """GitStream has no cycles."""
        stream = GitStream(git_repo)
        assert stream.has_cycles() is False

    def test_estimate_size(self, git_repo):
        """Should estimate correct number of commits."""
        stream = GitStream(git_repo)
        size = stream.estimate_size()
        assert size == 4  # 4 commits in fixture

    def test_events(self, git_repo):
        """Should iterate through commit events."""
        stream = GitStream(git_repo)
        events = list(stream.events())

        assert len(events) == 4
        assert all(isinstance(e, Event) for e in events)
        assert all(e.event_type == "commit" for e in events)

        # Check commit messages
        messages = [e.data["message"] for e in events]
        assert "Initial commit" in messages
        assert "Add file1" in messages
        assert "Add file2" in messages
        assert "Update file1" in messages

    def test_events_with_limit(self, git_repo):
        """Should respect limit parameter."""
        stream = GitStream(git_repo)
        events = list(stream.events(limit=2))
        assert len(events) == 2

    def test_window(self, git_repo):
        """Should create sliding windows."""
        stream = GitStream(git_repo)
        windowed = stream.window(timedelta(days=365))

        windows = list(windowed.windows())
        assert len(windows) >= 1

        # All events should be in at least one window
        all_window_events = set()
        for window in windows:
            for event in window.events:
                all_window_events.add(event.id)

        all_stream_events = {e.id for e in stream.events()}
        assert all_window_events == all_stream_events


# =============================================================================
# Composition Tests
# =============================================================================


@pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
class TestComposition:
    """Test stream composition utilities."""

    def test_filtered_stream(self, git_repo):
        """Should filter events by predicate."""
        stream = GitStream(git_repo)

        # Filter for commits that mention "file1"
        filtered = FilteredStream(stream, lambda e: "file1" in e.data["message"])

        events = list(filtered.events())
        assert len(events) == 2  # "Add file1" and "Update file1"
        assert all("file1" in e.data["message"] for e in events)

    def test_mapped_stream(self, git_repo):
        """Should transform events."""
        stream = GitStream(git_repo)

        # Add a tag to each event
        def add_tag(event: Event) -> Event:
            return Event(
                id=event.id,
                timestamp=event.timestamp,
                actor=event.actor,
                event_type=event.event_type,
                data={**event.data, "tagged": True},
                metadata=event.metadata,
            )

        mapped = MappedStream(stream, add_tag)
        events = list(mapped.events())

        assert len(events) == 4
        assert all(e.data.get("tagged") is True for e in events)

    def test_composed_stream(self, git_repo):
        """Should merge multiple streams."""
        stream1 = GitStream(git_repo)
        stream2 = GitStream(git_repo)

        composed = ComposedStream(stream1, stream2)

        # Should get all events from both streams
        events = list(composed.events())
        assert len(events) == 8  # 4 from each stream

        # Should be sorted by timestamp
        timestamps = [e.timestamp for e in events]
        assert timestamps == sorted(timestamps)

    def test_composed_reality_classification(self, git_repo):
        """Composed stream inherits most chaotic reality."""
        stream1 = GitStream(git_repo)
        stream2 = GitStream(git_repo)

        composed = ComposedStream(stream1, stream2)

        # Both PROBABILISTIC → PROBABILISTIC
        assert composed.classify_reality() == Reality.PROBABILISTIC


# =============================================================================
# EntropyBudget Tests
# =============================================================================


class TestEntropyBudget:
    """Test entropy budget management."""

    def test_remaining_budget(self):
        """Budget should diminish with depth."""
        budget0 = EntropyBudget(depth=0)
        budget1 = EntropyBudget(depth=1)
        budget2 = EntropyBudget(depth=2)

        assert budget0.remaining == 1.0
        assert budget1.remaining == 0.5
        assert budget2.remaining == pytest.approx(0.333, rel=0.01)

    def test_can_afford(self):
        """Should check if operation is affordable."""
        budget = EntropyBudget(depth=1)  # remaining = 0.5

        assert budget.can_afford(0.3) is True
        assert budget.can_afford(0.5) is True
        assert budget.can_afford(0.6) is False

    def test_descend(self):
        """Should create child budget with increased depth."""
        budget = EntropyBudget(depth=0)
        child = budget.descend()

        assert child.depth == 1
        assert child.remaining == 0.5

    def test_max_depth(self):
        """Budget should be exhausted at max depth."""
        budget = EntropyBudget(depth=3, max_depth=3)
        assert budget.remaining == 0.0
        assert budget.can_afford(0.01) is False

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_process_stream_with_budget(self, git_repo):
        """Should process stream respecting budget."""
        stream = GitStream(git_repo)
        budget = EntropyBudget(depth=0)

        events = process_stream_with_budget(stream, budget)

        # Should process events within budget
        assert len(events) >= 1
        assert len(events) <= 100  # DETERMINISTIC limit


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
class TestIntegration:
    """End-to-end integration tests."""

    def test_full_pipeline(self, git_repo):
        """Test complete pipeline: stream → filter → window → analyze."""
        # Create stream
        stream = GitStream(git_repo)

        # Filter for interesting commits
        filtered = FilteredStream(
            stream,
            lambda e: "Add" in e.data["message"] or "Update" in e.data["message"],
        )

        # Create windows
        windowed = filtered.window(timedelta(days=365))
        windows = list(windowed.windows())

        # Verify pipeline worked
        assert len(windows) >= 1

        for window in windows:
            assert window.event_count >= 1
            for event in window.events:
                assert (
                    "Add" in event.data["message"] or "Update" in event.data["message"]
                )

    def test_entropy_budget_integration(self, git_repo):
        """Test stream processing with entropy budget."""
        stream = GitStream(git_repo)
        budget = EntropyBudget(depth=0, max_depth=2)

        # Process with budget
        events = process_stream_with_budget(stream, budget)

        # Should respect budget
        assert len(events) >= 1
        assert budget.remaining > 0  # Should not exhaust budget for small stream
