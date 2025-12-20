"""
Tests for WitnessDaemon multi-watcher integration.

Covers:
- DaemonConfig validation
- Watcher factory
- Event to thought conversion
- Multi-watcher lifecycle
"""

from __future__ import annotations

from pathlib import Path

import pytest

from services.witness.daemon import (
    DEFAULT_WATCHERS,
    WATCHER_TYPES,
    DaemonConfig,
    WitnessDaemon,
    create_watcher,
    event_to_thought,
)
from services.witness.polynomial import (
    AgenteseEvent,
    CIEvent,
    FileEvent,
    GitEvent,
    TestEvent,
    Thought,
)


# =============================================================================
# DaemonConfig Tests
# =============================================================================


class TestDaemonConfig:
    """Tests for DaemonConfig validation."""

    def test_defaults(self) -> None:
        """Default config has sensible values."""
        config = DaemonConfig()
        assert config.enabled_watchers == DEFAULT_WATCHERS
        assert config.poll_interval == 5.0
        assert config.ci_poll_interval == 60.0
        assert config.file_patterns == ("*.py", "*.tsx", "*.ts", "*.md")

    def test_validate_valid_watchers(self) -> None:
        """Valid watchers pass validation."""
        config = DaemonConfig(enabled_watchers=("git", "filesystem"))
        errors = config.validate()
        assert errors == []

    def test_validate_unknown_watcher(self) -> None:
        """Unknown watcher fails validation."""
        config = DaemonConfig(enabled_watchers=("git", "unknown"))
        errors = config.validate()
        assert len(errors) == 1
        assert "Unknown watcher type: unknown" in errors[0]

    def test_validate_ci_requires_github(self) -> None:
        """CI watcher requires github_owner and github_repo."""
        config = DaemonConfig(enabled_watchers=("ci",))
        errors = config.validate()
        assert len(errors) == 1
        assert "CI watcher requires github_owner and github_repo" in errors[0]

    def test_validate_ci_with_github(self) -> None:
        """CI watcher with github config passes."""
        config = DaemonConfig(
            enabled_watchers=("ci",),
            github_owner="test",
            github_repo="repo",
        )
        errors = config.validate()
        assert errors == []


class TestWatcherTypes:
    """Tests for watcher type constants."""

    def test_all_types_defined(self) -> None:
        """All expected watcher types are defined."""
        expected = {"git", "filesystem", "test", "agentese", "ci"}
        assert WATCHER_TYPES == expected

    def test_default_watchers_valid(self) -> None:
        """Default watchers are valid types."""
        for w in DEFAULT_WATCHERS:
            assert w in WATCHER_TYPES


# =============================================================================
# Watcher Factory Tests
# =============================================================================


class TestCreateWatcher:
    """Tests for watcher factory function."""

    def test_create_git_watcher(self) -> None:
        """Create git watcher."""
        config = DaemonConfig()
        watcher = create_watcher("git", config)
        assert watcher is not None
        assert watcher.__class__.__name__ == "GitWatcher"

    def test_create_filesystem_watcher(self) -> None:
        """Create filesystem watcher."""
        config = DaemonConfig()
        watcher = create_watcher("filesystem", config)
        assert watcher is not None
        assert watcher.__class__.__name__ == "FileSystemWatcher"

    def test_create_test_watcher(self) -> None:
        """Create test watcher."""
        config = DaemonConfig()
        watcher = create_watcher("test", config)
        assert watcher is not None
        assert watcher.__class__.__name__ == "TestWatcher"

    def test_create_agentese_watcher(self) -> None:
        """Create agentese watcher."""
        config = DaemonConfig()
        watcher = create_watcher("agentese", config)
        assert watcher is not None
        assert watcher.__class__.__name__ == "AgenteseWatcher"

    def test_create_ci_watcher(self) -> None:
        """Create CI watcher."""
        config = DaemonConfig(github_owner="test", github_repo="repo")
        watcher = create_watcher("ci", config)
        assert watcher is not None
        assert watcher.__class__.__name__ == "CIWatcher"

    def test_create_unknown_watcher(self) -> None:
        """Unknown watcher returns None."""
        config = DaemonConfig()
        watcher = create_watcher("unknown", config)
        assert watcher is None


# =============================================================================
# Event to Thought Conversion Tests
# =============================================================================


class TestEventToThought:
    """Tests for event_to_thought conversion."""

    def test_git_commit_event(self) -> None:
        """Git commit event converts to thought."""
        event = GitEvent(event_type="commit", sha="abc123def", message="Fix bug")
        thought = event_to_thought(event)

        assert isinstance(thought, Thought)
        assert "abc123d" in thought.content  # 7 char sha
        assert "Fix bug" in thought.content
        assert thought.source == "git"
        assert ("git", "commit") == thought.tags

    def test_git_checkout_event(self) -> None:
        """Git checkout event converts to thought."""
        event = GitEvent(event_type="checkout", branch="feature")
        thought = event_to_thought(event)

        assert "Switched to branch feature" in thought.content
        assert thought.source == "git"
        assert thought.tags == ("git", "checkout")

    def test_git_push_event(self) -> None:
        """Git push event converts to thought."""
        event = GitEvent(event_type="push", branch="main")
        thought = event_to_thought(event)

        assert "Pushed to main" in thought.content
        assert thought.tags == ("git", "push")

    def test_file_event(self) -> None:
        """File event converts to thought."""
        event = FileEvent(event_type="modify", path="/src/app.py")
        thought = event_to_thought(event)

        assert "File modify: /src/app.py" in thought.content
        assert thought.source == "filesystem"
        assert thought.tags == ("file", "modify")

    def test_test_session_event(self) -> None:
        """Test session complete event converts to thought."""
        event = TestEvent(event_type="session_complete", passed=10, failed=2, skipped=1)
        thought = event_to_thought(event)

        assert "10 passed" in thought.content
        assert "2 failed" in thought.content
        assert "1 skipped" in thought.content
        assert thought.source == "tests"
        assert thought.tags == ("tests", "session")

    def test_test_failed_event(self) -> None:
        """Test failure event converts to thought."""
        event = TestEvent(event_type="failed", test_id="test_foo", error="AssertionError")
        thought = event_to_thought(event)

        assert "Test failed: test_foo" in thought.content
        assert "AssertionError" in thought.content
        assert thought.tags == ("tests", "failure")

    def test_agentese_event(self) -> None:
        """AGENTESE event converts to thought."""
        event = AgenteseEvent(path="world.town.citizen", aspect="create", jewel="Town")
        thought = event_to_thought(event)

        assert "AGENTESE: world.town.citizen.create" in thought.content
        assert "(from Town)" in thought.content
        assert thought.source == "agentese"
        assert thought.tags == ("agentese", "Town")

    def test_ci_workflow_complete_event(self) -> None:
        """CI workflow complete event converts to thought."""
        event = CIEvent(
            event_type="workflow_complete",
            workflow="Tests",
            status="success",
            duration_seconds=120,
        )
        thought = event_to_thought(event)

        assert "CI workflow 'Tests' success" in thought.content
        assert "(120s)" in thought.content
        assert thought.source == "ci"
        assert thought.tags == ("ci", "success")

    def test_ci_check_failed_event(self) -> None:
        """CI check failed event converts to thought."""
        event = CIEvent(event_type="check_failed", workflow="Build", status="failure")
        thought = event_to_thought(event)

        assert "CI check failed: Build" in thought.content
        assert thought.tags == ("ci", "failure")


# =============================================================================
# WitnessDaemon Tests
# =============================================================================


class TestWitnessDaemon:
    """Tests for WitnessDaemon."""

    def test_init_with_defaults(self) -> None:
        """Daemon initializes with default config."""
        daemon = WitnessDaemon()
        assert daemon.config.enabled_watchers == DEFAULT_WATCHERS
        assert daemon.is_running is False
        assert daemon.thoughts_sent == 0

    def test_init_with_custom_config(self) -> None:
        """Daemon initializes with custom config."""
        config = DaemonConfig(enabled_watchers=("git", "filesystem"))
        daemon = WitnessDaemon(config=config)
        assert daemon.config.enabled_watchers == ("git", "filesystem")

    @pytest.mark.asyncio
    async def test_start_with_invalid_config(self) -> None:
        """Start with invalid config raises error."""
        config = DaemonConfig(enabled_watchers=("unknown",))
        daemon = WitnessDaemon(config=config)

        with pytest.raises(ValueError, match="Invalid configuration"):
            await daemon.start()


class TestDaemonStats:
    """Tests for daemon statistics tracking."""

    def test_initial_stats(self) -> None:
        """Initial stats are zero."""
        daemon = WitnessDaemon()
        assert daemon.thoughts_sent == 0
        assert daemon.errors == 0
        assert daemon.events_by_watcher == {}
        assert daemon.started_at is None
