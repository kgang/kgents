"""Tests for HYDRATE.md signal appending."""

import tempfile
from pathlib import Path

import pytest
from protocols.cli.devex.hydrate_signal import (
    _SIGNAL_MARKER,
    HydrateEvent,
    append_hydrate_signal,
    get_recent_signals,
)


@pytest.fixture
def temp_project():
    """Create a temporary project with HYDRATE.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        hydrate_path = project_root / "HYDRATE.md"
        hydrate_path.write_text("# HYDRATE.md\n\nSome content here.\n")
        yield project_root


class TestAppendHydrateSignal:
    """Tests for append_hydrate_signal."""

    def test_appends_signal_to_empty_section(self, temp_project) -> None:
        """First signal creates the section."""
        result = append_hydrate_signal(
            HydrateEvent.SESSION_START,
            "focus: agents/m/",
            project_root=temp_project,
        )

        assert result is True

        content = (temp_project / "HYDRATE.md").read_text()
        assert _SIGNAL_MARKER in content
        assert "[session]" in content
        assert "focus: agents/m/" in content

    def test_appends_multiple_signals(self, temp_project) -> None:
        """Multiple signals accumulate."""
        append_hydrate_signal(
            HydrateEvent.SESSION_START, "first", project_root=temp_project
        )
        append_hydrate_signal(
            HydrateEvent.TEST_RUN, "second", project_root=temp_project
        )
        append_hydrate_signal(HydrateEvent.CUSTOM, "third", project_root=temp_project)

        content = (temp_project / "HYDRATE.md").read_text()
        assert content.count("[session]") == 1
        assert content.count("[tests]") == 1
        assert content.count("[note]") == 1

    def test_signal_without_detail(self, temp_project) -> None:
        """Signal can be emitted without detail."""
        append_hydrate_signal(HydrateEvent.SESSION_END, project_root=temp_project)

        content = (temp_project / "HYDRATE.md").read_text()
        assert "[session_end]" in content

    def test_returns_false_for_missing_file(self, temp_project) -> None:
        """Returns False if HYDRATE.md doesn't exist."""
        (temp_project / "HYDRATE.md").unlink()

        result = append_hydrate_signal(
            HydrateEvent.SESSION_START,
            project_root=temp_project,
        )

        assert result is False


class TestGetRecentSignals:
    """Tests for get_recent_signals."""

    def test_returns_empty_for_no_signals(self, temp_project) -> None:
        """Returns empty list when no signals exist."""
        signals = get_recent_signals(project_root=temp_project)
        assert signals == []

    def test_returns_recent_signals(self, temp_project) -> None:
        """Returns signals in reverse chronological order."""
        append_hydrate_signal(
            HydrateEvent.SESSION_START, "first", project_root=temp_project
        )
        append_hydrate_signal(
            HydrateEvent.TEST_RUN, "second", project_root=temp_project
        )
        append_hydrate_signal(HydrateEvent.CUSTOM, "third", project_root=temp_project)

        signals = get_recent_signals(limit=10, project_root=temp_project)

        assert len(signals) == 3
        # Most recent first
        assert "[note]" in signals[0]
        assert "[tests]" in signals[1]
        assert "[session]" in signals[2]

    def test_respects_limit(self, temp_project) -> None:
        """Respects the limit parameter."""
        for i in range(5):
            append_hydrate_signal(
                HydrateEvent.CUSTOM, f"signal-{i}", project_root=temp_project
            )

        signals = get_recent_signals(limit=2, project_root=temp_project)

        assert len(signals) == 2
