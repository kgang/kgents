"""
Tests for witness CLI handler.

The Witness Crown Jewel (8th Jewel) CLI tests cover:
- Help command
- Manifest (status)
- Thoughts stream
- Trust display
- Capture command
- Daemon start/stop

Note on test isolation:
    Witness tests mock the persistence layer to avoid database dependencies.
    Daemon tests are integration tests that actually spawn/stop processes.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def isolate_witness(tmp_path: Path) -> Generator[None, None, None]:
    """Isolate witness tests with temp directory for PID file."""
    # Set temp directory for witness PID file
    old_home = os.environ.get("HOME")
    os.environ["HOME"] = str(tmp_path)

    # Create .kgents directory
    kgents_dir = tmp_path / ".kgents"
    kgents_dir.mkdir(parents=True, exist_ok=True)

    yield

    # Cleanup
    if old_home is not None:
        os.environ["HOME"] = old_home


@pytest.fixture
def mock_persistence() -> MagicMock:
    """Create a mock WitnessPersistence."""
    from datetime import datetime

    from services.witness.persistence import TrustResult, WitnessStatus
    from services.witness.polynomial import Thought, TrustLevel

    mock = MagicMock()

    # Mock manifest
    mock.manifest = AsyncMock(
        return_value=WitnessStatus(
            total_thoughts=42,
            total_actions=10,
            trust_count=3,
            reversible_actions=5,
            storage_backend="sqlite",
        )
    )

    # Mock get_thoughts
    mock.get_thoughts = AsyncMock(
        return_value=[
            Thought(
                content="Test thought 1",
                source="git",
                tags=("git", "commit"),
                timestamp=datetime.now(),
            ),
            Thought(
                content="Test thought 2",
                source="tests",
                tags=("tests",),
                timestamp=datetime.now(),
            ),
        ]
    )

    # Mock get_trust_level
    mock.get_trust_level = AsyncMock(
        return_value=TrustResult(
            trust_level=TrustLevel.READ_ONLY,
            raw_level=0.0,
            last_active=datetime.now(),
            observation_count=47,
            successful_operations=0,
            confirmed_suggestions=0,
            total_suggestions=0,
            acceptance_rate=0.0,
            decay_applied=False,
        )
    )

    # Mock save_thought
    mock.save_thought = AsyncMock(
        return_value=MagicMock(
            thought_id="thought-abc123",
            content="Test content",
            source="cli",
            tags=["manual", "cli"],
        )
    )

    return mock


# =============================================================================
# Help Tests
# =============================================================================


class TestWitnessHelp:
    """Tests for witness --help."""

    def test_help_returns_zero(self) -> None:
        """--help should return 0."""
        from protocols.cli.handlers.witness import cmd_witness

        result = cmd_witness(["--help"])
        assert result == 0

    def test_help_short_returns_zero(self) -> None:
        """-h should return 0."""
        from protocols.cli.handlers.witness import cmd_witness

        result = cmd_witness(["-h"])
        assert result == 0


# =============================================================================
# Manifest Tests
# =============================================================================


class TestWitnessManifest:
    """Tests for witness manifest command."""

    def test_manifest_default(self, mock_persistence: MagicMock) -> None:
        """Default command (no args) shows manifest."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_persistence

            result = cmd_witness([])
            assert result == 0

    def test_manifest_explicit(self, mock_persistence: MagicMock) -> None:
        """Explicit manifest command works."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_persistence

            result = cmd_witness(["manifest"])
            assert result == 0

    def test_manifest_json(self, mock_persistence: MagicMock) -> None:
        """Manifest with --json returns structured output."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_persistence

            result = cmd_witness(["manifest", "--json"])
            assert result == 0


# =============================================================================
# Thoughts Tests
# =============================================================================


class TestWitnessThoughts:
    """Tests for witness thoughts command."""

    def test_thoughts_default(self, mock_persistence: MagicMock) -> None:
        """Thoughts command shows recent thoughts."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_persistence

            result = cmd_witness(["thoughts"])
            assert result == 0

    def test_thoughts_with_limit(self, mock_persistence: MagicMock) -> None:
        """Thoughts with -n limit works."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_persistence

            result = cmd_witness(["thoughts", "-n", "20"])
            assert result == 0
            mock_persistence.get_thoughts.assert_called_once()

    def test_thoughts_json(self, mock_persistence: MagicMock) -> None:
        """Thoughts with --json returns structured output."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_persistence

            result = cmd_witness(["thoughts", "--json"])
            assert result == 0


# =============================================================================
# Trust Tests
# =============================================================================


class TestWitnessTrust:
    """Tests for witness trust command."""

    def test_trust_requires_email(self) -> None:
        """Trust without email shows error."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock):
            result = cmd_witness(["trust"])
            assert result == 1

    def test_trust_with_email(self, mock_persistence: MagicMock) -> None:
        """Trust with email works."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_persistence

            result = cmd_witness(["trust", "user@example.com"])
            assert result == 0

    def test_trust_json(self, mock_persistence: MagicMock) -> None:
        """Trust with --json returns structured output."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_persistence

            result = cmd_witness(["trust", "user@example.com", "--json"])
            assert result == 0


# =============================================================================
# Capture Tests
# =============================================================================


class TestWitnessCapture:
    """Tests for witness capture command."""

    def test_capture_requires_content(self) -> None:
        """Capture without content shows error."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock):
            result = cmd_witness(["capture"])
            assert result == 1

    def test_capture_with_content(self, mock_persistence: MagicMock) -> None:
        """Capture with content works."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_persistence

            result = cmd_witness(["capture", "Test observation"])
            assert result == 0

    def test_capture_json(self, mock_persistence: MagicMock) -> None:
        """Capture with --json returns structured output."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_persistence

            result = cmd_witness(["capture", "Test observation", "--json"])
            assert result == 0


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestWitnessErrors:
    """Tests for error handling in witness commands."""

    def test_unknown_subcommand(self) -> None:
        """Unknown subcommand returns error."""
        from protocols.cli.handlers.witness import cmd_witness

        result = cmd_witness(["unknown_cmd"])
        assert result == 1

    def test_capture_whitespace_only(self) -> None:
        """Capture with whitespace-only content shows error."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("services.bootstrap.get_service", new_callable=AsyncMock):
            result = cmd_witness(["capture", "   "])
            assert result == 1


# =============================================================================
# Daemon Tests
# =============================================================================


class TestWitnessDaemon:
    """Tests for witness daemon management."""

    def test_daemon_check_status_not_running(self, tmp_path: Path) -> None:
        """Check status when daemon not running."""
        from services.witness.daemon import DaemonConfig, check_daemon_status

        config = DaemonConfig(pid_file=tmp_path / "witness.pid")
        is_running, pid = check_daemon_status(config)

        assert is_running is False
        assert pid is None

    def test_daemon_pid_file_write_read(self, tmp_path: Path) -> None:
        """PID file can be written and read."""
        from services.witness.daemon import read_pid_file, write_pid_file

        pid_file = tmp_path / "witness.pid"
        write_pid_file(pid_file, 12345)

        pid = read_pid_file(pid_file)
        assert pid == 12345

    def test_daemon_pid_file_remove(self, tmp_path: Path) -> None:
        """PID file can be removed."""
        from services.witness.daemon import read_pid_file, remove_pid_file, write_pid_file

        pid_file = tmp_path / "witness.pid"
        write_pid_file(pid_file, 12345)

        remove_pid_file(pid_file)

        pid = read_pid_file(pid_file)
        assert pid is None

    def test_daemon_stale_pid_cleanup(self, tmp_path: Path) -> None:
        """Stale PID file (process not running) is cleaned up."""
        from services.witness.daemon import DaemonConfig, check_daemon_status, write_pid_file

        pid_file = tmp_path / "witness.pid"
        # Write a fake PID that doesn't correspond to a running process
        write_pid_file(pid_file, 999999999)

        config = DaemonConfig(pid_file=pid_file)
        is_running, pid = check_daemon_status(config)

        # Should not be running (PID doesn't exist)
        assert is_running is False
        # PID file should have been cleaned up
        assert not pid_file.exists()


# =============================================================================
# Thin Shim Tests
# =============================================================================


class TestWitnessThin:
    """Tests for witness_thin routing shim."""

    def test_thin_routes_help(self) -> None:
        """Thin shim routes help correctly."""
        from protocols.cli.handlers.witness_thin import cmd_witness

        result = cmd_witness(["--help"])
        assert result == 0

    def test_thin_routes_start_to_full_handler(self) -> None:
        """Thin shim routes daemon commands to full handler."""
        from protocols.cli.handlers.witness_thin import cmd_witness

        # start command should be routed to full handler
        with patch("protocols.cli.handlers.witness.cmd_witness") as mock_full:
            mock_full.return_value = 0
            result = cmd_witness(["start"])
            mock_full.assert_called_once()

    def test_thin_routes_stop_to_full_handler(self) -> None:
        """Thin shim routes stop to full handler."""
        from protocols.cli.handlers.witness_thin import cmd_witness

        with patch("protocols.cli.handlers.witness.cmd_witness") as mock_full:
            mock_full.return_value = 0
            result = cmd_witness(["stop"])
            mock_full.assert_called_once()
