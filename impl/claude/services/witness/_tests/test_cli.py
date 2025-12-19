"""
Tests for Witness CLI Handler (Phase 3).

Tests the `kg witness logs` and `kg witness status` commands.

Pattern: Follows crown-jewel-patterns.md CLI testing approach
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# =============================================================================
# Test: kg witness logs
# =============================================================================


class TestWitnessLogsCommand:
    """Test the witness logs subcommand."""

    @pytest.fixture
    def temp_log_file(self, tmp_path: Path):
        """Create a temporary log file with test content."""
        log_dir = tmp_path / ".kgents"
        log_dir.mkdir(parents=True)
        log_file = log_dir / "witness.log"
        log_file.write_text(
            "2025-01-01 10:00:00 [INFO] Line 1\n"
            "2025-01-01 10:01:00 [INFO] Line 2\n"
            "2025-01-01 10:02:00 [INFO] Line 3\n"
            "2025-01-01 10:03:00 [INFO] Line 4\n"
            "2025-01-01 10:04:00 [INFO] Line 5\n"
        )
        return log_file

    def test_logs_no_file_returns_error(self, tmp_path: Path, capsys) -> None:
        """When log file doesn't exist, return error."""
        from protocols.cli.handlers.witness import cmd_witness

        # Patch Path.home() to use temp directory without log file
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = cmd_witness(["logs"])

        assert result == 1
        captured = capsys.readouterr()
        assert "No log file found" in captured.out

    def test_logs_shows_last_n_lines(self, tmp_path: Path, temp_log_file: Path, capsys) -> None:
        """logs -n N shows last N lines."""
        from protocols.cli.handlers.witness import cmd_witness

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = cmd_witness(["logs", "-n", "3"])

        assert result == 0
        captured = capsys.readouterr()
        assert "Line 3" in captured.out
        assert "Line 4" in captured.out
        assert "Line 5" in captured.out
        assert "Showing 3 of 5 lines" in captured.out

    def test_logs_json_output(self, tmp_path: Path, temp_log_file: Path, capsys) -> None:
        """logs --json returns structured output."""
        import json

        from protocols.cli.handlers.witness import cmd_witness

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = cmd_witness(["logs", "-n", "2", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["total_lines"] == 5
        assert output["showing"] == 2
        assert len(output["lines"]) == 2
        assert "Line 4" in output["lines"][0]
        assert "Line 5" in output["lines"][1]


# =============================================================================
# Test: kg witness status
# =============================================================================


class TestWitnessStatusCommand:
    """Test the witness status subcommand."""

    def test_status_shows_bus_stats(self, capsys) -> None:
        """status shows SynergyBus and EventBus stats."""
        from protocols.cli.handlers.witness import cmd_witness
        from services.witness.bus import get_witness_bus_manager, reset_witness_bus_manager

        # Reset to clean state
        reset_witness_bus_manager()

        result = cmd_witness(["status"])

        assert result == 0
        captured = capsys.readouterr()

        # Check for bus sections
        assert "SynergyBus" in captured.out
        assert "EventBus" in captured.out
        assert "Events emitted:" in captured.out
        assert "Subscribers:" in captured.out

        # Cleanup
        reset_witness_bus_manager()

    def test_status_json_output(self, capsys) -> None:
        """status --json returns structured bus stats."""
        import json

        from protocols.cli.handlers.witness import cmd_witness
        from services.witness.bus import reset_witness_bus_manager

        reset_witness_bus_manager()

        result = cmd_witness(["status", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        # Find the JSON object in output (may have path header before it)
        lines = captured.out.strip().split("\n")
        json_start = next(i for i, line in enumerate(lines) if line.strip().startswith("{"))
        json_text = "\n".join(lines[json_start:])
        output = json.loads(json_text)

        assert "daemon" in output
        assert "uptime" in output
        assert "bus_stats" in output
        assert "synergy_bus" in output["bus_stats"]
        assert "event_bus" in output["bus_stats"]

        reset_witness_bus_manager()

    def test_status_shows_uptime_when_running(self, tmp_path: Path, capsys) -> None:
        """status shows uptime when daemon is running."""
        from protocols.cli.handlers.witness import cmd_witness
        from services.witness.bus import reset_witness_bus_manager

        reset_witness_bus_manager()

        # Create fake PID file to simulate running daemon
        pid_dir = tmp_path / ".kgents"
        pid_dir.mkdir(parents=True)
        pid_file = pid_dir / "witness.pid"
        pid_file.write_text("12345")

        # Mock get_daemon_status to return running
        def mock_daemon_status(config=None):
            return {
                "running": True,
                "pid": 12345,
                "pid_file": str(pid_file),
                "log_file": str(pid_dir / "witness.log"),
                "gateway_url": "http://localhost:8000",
            }

        # Patch at the module level where it's imported inside _handle_status
        with patch(
            "services.witness.daemon.get_daemon_status",
            side_effect=mock_daemon_status,
        ):
            result = cmd_witness(["status"])

        assert result == 0
        captured = capsys.readouterr()
        assert "Uptime:" in captured.out

        reset_witness_bus_manager()


# =============================================================================
# Test: Help and Unknown Commands
# =============================================================================


class TestWitnessHelpAndRouting:
    """Test help text and command routing."""

    def test_help_includes_logs_command(self, capsys) -> None:
        """Help text includes logs command documentation."""
        from protocols.cli.handlers.witness import cmd_witness

        result = cmd_witness(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "kg witness logs" in captured.out
        assert "kg witness status" in captured.out
        assert "-f, --follow" in captured.out
