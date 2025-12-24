"""
Tests for kgentsd CLI (Phase 4A: Visible Presence).

Tests the daemon CLI commands: summon, release, status, thoughts, ask.

Pattern: Follows crown-jewel-patterns.md CLI testing approach
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

# =============================================================================
# Test: kgentsd --help
# =============================================================================


class TestKgentsdHelp:
    """Test help output and version."""

    def test_help_shows_all_commands(self, capsys) -> None:
        """Help text shows all commands."""
        from services.kgentsd.cli import main

        result = main(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "kgentsd summon" in captured.out
        assert "kgentsd release" in captured.out
        assert "kgentsd status" in captured.out
        assert "kgentsd thoughts" in captured.out
        assert "kgentsd ask" in captured.out

    def test_version_shows_version(self, capsys) -> None:
        """--version shows version."""
        from services.kgentsd.cli import main

        result = main(["--version"])

        assert result == 0
        captured = capsys.readouterr()
        assert "kgentsd" in captured.out
        # Version may change, just verify it's a valid semver
        assert any(v in captured.out for v in ["0.1.0", "0.2.0", "0.3.0", "1.0.0"])

    def test_no_args_shows_help(self, capsys) -> None:
        """No arguments shows help text."""
        from services.kgentsd.cli import main

        result = main([])

        assert result == 0
        captured = capsys.readouterr()
        assert "kgentsd - The Witness Daemon" in captured.out


# =============================================================================
# Test: kgentsd status
# =============================================================================


class TestKgentsdStatus:
    """Test the status command."""

    def test_status_not_running(self, tmp_path: Path, capsys) -> None:
        """Status shows 'not running' when daemon is not running."""
        from services.kgentsd.cli import cmd_status
        from services.kgentsd.daemon import DaemonConfig

        # Mock check_daemon_status to return not running
        with patch(
            "services.kgentsd.cli.check_daemon_status",
            return_value=(False, None),
        ):
            with patch(
                "services.kgentsd.cli.get_daemon_status",
                return_value={
                    "running": False,
                    "pid": None,
                    "enabled_watchers": [],
                },
            ):
                result = cmd_status([])

        assert result == 0
        captured = capsys.readouterr()
        assert "Not running" in captured.out or "not running" in captured.out.lower()

    def test_status_running(self, capsys) -> None:
        """Status shows details when daemon is running."""
        from services.kgentsd.cli import cmd_status

        with patch(
            "services.kgentsd.cli.get_daemon_status",
            return_value={
                "running": True,
                "pid": 12345,
                "enabled_watchers": ["git", "tests"],
                "log_file": "/path/to/witness.log",
            },
        ):
            result = cmd_status([])

        assert result == 0
        captured = capsys.readouterr()
        assert "Running" in captured.out or "12345" in captured.out


# =============================================================================
# Test: kgentsd summon
# =============================================================================


class TestKgentsdSummon:
    """Test the summon command."""

    def test_summon_already_running(self, capsys) -> None:
        """Summon fails gracefully when daemon already running."""
        from services.kgentsd.cli import cmd_summon

        with patch(
            "services.kgentsd.cli.check_daemon_status",
            return_value=(True, 12345),
        ):
            result = cmd_summon([])

        assert result == 1
        captured = capsys.readouterr()
        assert "already running" in captured.out.lower()

    def test_summon_help(self, capsys) -> None:
        """summon --help shows help."""
        from services.kgentsd.cli import cmd_summon

        result = cmd_summon(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "--watchers" in captured.out
        assert "--background" in captured.out

    def test_summon_invalid_watcher(self, capsys) -> None:
        """Invalid watcher type shows error."""
        from services.kgentsd.cli import cmd_summon

        with patch(
            "services.kgentsd.cli.check_daemon_status",
            return_value=(False, None),
        ):
            result = cmd_summon(["--watchers", "invalid_watcher"])

        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown watcher type" in captured.out

    def test_summon_background_mode(self, capsys) -> None:
        """Background mode spawns daemon and returns."""
        from services.kgentsd.cli import cmd_summon

        with patch(
            "services.kgentsd.cli.check_daemon_status",
            return_value=(False, None),
        ):
            with patch(
                "services.kgentsd.cli.start_daemon",
                return_value=99999,
            ):
                result = cmd_summon(["--background"])

        assert result == 0
        captured = capsys.readouterr()
        assert "background" in captured.out.lower()
        assert "99999" in captured.out


# =============================================================================
# Test: kgentsd release
# =============================================================================


class TestKgentsdRelease:
    """Test the release command."""

    def test_release_not_running(self, capsys) -> None:
        """Release shows message when not running."""
        from services.kgentsd.cli import cmd_release

        # Mock check_daemon_status to return not running
        # This prevents the test from finding a daemon from another test
        with patch(
            "services.kgentsd.cli.check_daemon_status",
            return_value=(False, None),
        ):
            result = cmd_release([])

        assert result == 0
        captured = capsys.readouterr()
        assert "not running" in captured.out.lower()

    def test_release_success(self, capsys) -> None:
        """Release shows success message."""
        from services.kgentsd.cli import cmd_release

        # Mock check_daemon_status to indicate daemon is running
        # Mock is_process_running to simulate clean exit
        with patch(
            "services.kgentsd.cli.check_daemon_status",
            return_value=(True, 12345),
        ):
            with patch(
                "services.kgentsd.daemon.is_process_running",
                return_value=False,  # Process exits cleanly
            ):
                with patch("services.kgentsd.cli.os.kill"):
                    result = cmd_release([])

        assert result == 0
        captured = capsys.readouterr()
        assert "banished" in captured.out.lower()


# =============================================================================
# Test: kgentsd ask
# =============================================================================


class TestKgentsdAsk:
    """Test the ask command."""

    def test_ask_no_question(self, capsys) -> None:
        """Ask with no question shows usage."""
        from services.kgentsd.cli import cmd_ask

        result = cmd_ask([])

        assert result == 1
        captured = capsys.readouterr()
        assert "Usage" in captured.out

    def test_ask_help(self, capsys) -> None:
        """ask --help shows help."""
        from services.kgentsd.cli import cmd_ask

        result = cmd_ask(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "Direct query" in captured.out

    def test_ask_with_question(self, capsys) -> None:
        """Ask with question shows placeholder response."""
        from services.kgentsd.cli import cmd_ask

        result = cmd_ask(["what should I work on?"])

        assert result == 0
        captured = capsys.readouterr()
        assert "what should I work on?" in captured.out


# =============================================================================
# Test: Command Aliases
# =============================================================================


class TestKgentsdAliases:
    """Test command aliases (start/stop)."""

    def test_start_alias(self, capsys) -> None:
        """'start' is alias for 'summon'."""
        from services.kgentsd.cli import main

        with patch(
            "services.kgentsd.cli.check_daemon_status",
            return_value=(True, 12345),
        ):
            result = main(["start"])

        # Should behave same as summon (already running)
        assert result == 1
        captured = capsys.readouterr()
        assert "already running" in captured.out.lower()

    def test_stop_alias(self, capsys) -> None:
        """'stop' is alias for 'release'."""
        from services.kgentsd.cli import main

        # Mock check_daemon_status to return not running
        with patch(
            "services.kgentsd.cli.check_daemon_status",
            return_value=(False, None),
        ):
            result = main(["stop"])

        assert result == 0
        captured = capsys.readouterr()
        assert "not running" in captured.out.lower()


# =============================================================================
# Test: Unknown Commands
# =============================================================================


class TestKgentsdUnknown:
    """Test unknown command handling."""

    def test_unknown_command(self, capsys) -> None:
        """Unknown command shows error and suggestions."""
        from services.kgentsd.cli import main

        result = main(["invalid_command"])

        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown command" in captured.out
        assert "summon" in captured.out or "Available commands" in captured.out
