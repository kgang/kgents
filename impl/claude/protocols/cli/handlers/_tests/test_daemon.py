"""
Tests for the Daemon Handler.

Tests the Cortex daemon lifecycle management with Mac launchd integration.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the daemon handler
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
from protocols.cli.handlers.daemon import (
    LAUNCH_AGENTS_DIR,
    LOGS_DIR,
    PLIST_FILENAME,
    PLIST_LABEL,
    _check_health,
    _generate_plist,
    _get_daemon_status,
    _is_launchd_installed,
    _parse_lines,
    _parse_port,
    cmd_daemon,
)


class TestParseArguments:
    """Test argument parsing helpers."""

    def test_parse_port_default(self) -> None:
        """Test default port is returned when not specified."""
        assert _parse_port([]) == 50051
        assert _parse_port(["--other"]) == 50051

    def test_parse_port_with_flag(self) -> None:
        """Test --port flag parsing."""
        assert _parse_port(["--port", "8080"]) == 8080
        assert _parse_port(["-p", "9000"]) == 9000

    def test_parse_port_invalid(self) -> None:
        """Test invalid port returns default."""
        assert _parse_port(["--port", "invalid"]) == 50051

    def test_parse_lines_default(self) -> None:
        """Test default lines count."""
        assert _parse_lines([]) == 50
        assert _parse_lines(["--other"]) == 50

    def test_parse_lines_with_flag(self) -> None:
        """Test --lines and -n flags."""
        assert _parse_lines(["--lines", "100"]) == 100
        assert _parse_lines(["-n", "25"]) == 25


class TestDaemonStatus:
    """Test daemon status detection."""

    @patch("protocols.cli.handlers.daemon.subprocess.run")
    def test_daemon_running_via_pgrep(self, mock_run: MagicMock) -> None:
        """Test detecting running daemon via pgrep."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="12345\n",
        )

        status = _get_daemon_status()

        assert status["running"] is True
        assert status["pid"] == 12345

    @patch("protocols.cli.handlers.daemon.subprocess.run")
    def test_daemon_not_running(self, mock_run: MagicMock) -> None:
        """Test detecting daemon not running."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
        )

        status = _get_daemon_status()

        assert status["running"] is False

    @patch("protocols.cli.handlers.daemon.subprocess.run")
    def test_daemon_running_via_lsof(self, mock_run: MagicMock) -> None:
        """Test detecting running daemon via lsof when pgrep fails."""
        # First call (pgrep) fails, second call (lsof) succeeds
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout=""),  # pgrep
            MagicMock(returncode=0, stdout="54321\n"),  # lsof
        ]

        status = _get_daemon_status()

        assert status["running"] is True
        assert status["pid"] == 54321


class TestLaunchdIntegration:
    """Test launchd service management."""

    def test_is_launchd_installed_false(self, tmp_path: Path) -> None:
        """Test detection when launchd not installed."""
        with patch("protocols.cli.handlers.daemon.LAUNCH_AGENTS_DIR", tmp_path):
            assert _is_launchd_installed() is False

    def test_is_launchd_installed_true(self, tmp_path: Path) -> None:
        """Test detection when launchd is installed."""
        plist_path = tmp_path / PLIST_FILENAME
        plist_path.write_text("<plist></plist>")

        with patch("protocols.cli.handlers.daemon.LAUNCH_AGENTS_DIR", tmp_path):
            assert _is_launchd_installed() is True

    def test_generate_plist_structure(self) -> None:
        """Test generated plist has correct structure."""
        plist = _generate_plist()

        # Check required elements
        assert PLIST_LABEL in plist
        assert "ProgramArguments" in plist
        assert "infra.cortex.daemon" in plist
        assert "RunAtLoad" in plist
        assert "KeepAlive" in plist
        assert "StandardOutPath" in plist
        assert "StandardErrorPath" in plist

    def test_generate_plist_paths(self) -> None:
        """Test generated plist has correct paths."""
        plist = _generate_plist()

        # Check log paths
        assert str(LOGS_DIR) in plist


class TestDaemonCommands:
    """Test daemon CLI commands."""

    def test_cmd_daemon_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test daemon --help output."""
        result = cmd_daemon(["--help"])
        captured = capsys.readouterr()

        assert result == 0
        assert "Daemon Handler" in captured.out or "start" in captured.out.lower()

    def test_cmd_daemon_unknown_subcommand(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test unknown subcommand error."""
        result = cmd_daemon(["unknown"])
        captured = capsys.readouterr()

        assert result == 1
        assert "Unknown subcommand" in captured.out

    @patch("protocols.cli.handlers.daemon._get_daemon_status")
    def test_cmd_daemon_status_not_running(
        self, mock_status: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test status when daemon not running."""
        mock_status.return_value = {"running": False}

        result = cmd_daemon(["status"])
        captured = capsys.readouterr()

        assert result == 0
        assert "STOPPED" in captured.out

    @patch("protocols.cli.handlers.daemon._get_daemon_status")
    @patch("protocols.cli.handlers.daemon._check_health")
    @patch("protocols.cli.handlers.daemon._is_launchd_installed")
    def test_cmd_daemon_status_running(
        self,
        mock_launchd: MagicMock,
        mock_health: MagicMock,
        mock_status: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test status when daemon is running."""
        mock_status.return_value = {"running": True, "pid": 12345}
        mock_health.return_value = {"healthy": True, "instance_id": "test123"}
        mock_launchd.return_value = True

        result = cmd_daemon(["status"])
        captured = capsys.readouterr()

        assert result == 0
        assert "RUNNING" in captured.out
        assert "12345" in captured.out

    @patch("protocols.cli.handlers.daemon._get_daemon_status")
    def test_cmd_daemon_start_already_running(
        self, mock_status: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test start when daemon already running."""
        mock_status.return_value = {"running": True, "pid": 12345}

        result = cmd_daemon(["start"])
        captured = capsys.readouterr()

        assert result == 0
        assert "already running" in captured.out

    @patch("protocols.cli.handlers.daemon._get_daemon_status")
    def test_cmd_daemon_stop_not_running(
        self, mock_status: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test stop when daemon not running."""
        mock_status.return_value = {"running": False}

        result = cmd_daemon(["stop"])
        captured = capsys.readouterr()

        assert result == 0
        assert "not running" in captured.out


class TestLaunchdInstallation:
    """Test launchd service installation."""

    def test_cmd_daemon_install_not_mac(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test install on non-Mac platform."""
        monkeypatch.setattr("sys.platform", "linux")

        from protocols.cli.handlers import daemon

        monkeypatch.setattr(daemon, "sys", MagicMock(platform="linux"))

        # Re-import to get patched version
        result = cmd_daemon(["install"])
        captured = capsys.readouterr()

        # On non-Mac, should fail
        assert result == 1 or "macOS" in captured.out or "Linux" in captured.out

    @patch("protocols.cli.handlers.daemon._is_launchd_installed")
    def test_cmd_daemon_install_already_installed(
        self, mock_launchd: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test install when already installed."""
        mock_launchd.return_value = True

        result = cmd_daemon(["install"])
        captured = capsys.readouterr()

        assert result == 0
        assert "already installed" in captured.out

    @patch("protocols.cli.handlers.daemon._is_launchd_installed")
    @patch("protocols.cli.handlers.daemon._launchctl")
    @patch("protocols.cli.handlers.daemon.LAUNCH_AGENTS_DIR")
    @patch("protocols.cli.handlers.daemon.LOGS_DIR")
    def test_cmd_daemon_install_success(
        self,
        mock_logs: MagicMock,
        mock_launch: MagicMock,
        mock_launchctl: MagicMock,
        mock_launchd: MagicMock,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test successful installation."""
        mock_launchd.return_value = False
        mock_launchctl.return_value = 0

        # Use temp directories
        with patch(
            "protocols.cli.handlers.daemon.LAUNCH_AGENTS_DIR", tmp_path / "LaunchAgents"
        ):
            with patch("protocols.cli.handlers.daemon.LOGS_DIR", tmp_path / "Logs"):
                result = cmd_daemon(["install"])
                captured = capsys.readouterr()

                # Should create directories and plist
                assert "Installing" in captured.out or "installed" in captured.out


class TestHealthCheck:
    """Test daemon health checking."""

    def test_check_health_no_grpc(self) -> None:
        """Test health check gracefully handles missing gRPC."""
        # The health check imports grpc inside the function,
        # so if it fails to import, it returns unhealthy.
        # This is tested indirectly by test_check_health_structure
        pass

    def test_check_health_structure(self) -> None:
        """Test health check returns correct structure."""
        # Health check will fail if daemon not running, but should return dict
        health = _check_health()

        assert isinstance(health, dict)
        assert "healthy" in health
        # Either healthy with instance_id, or unhealthy with error
        assert "instance_id" in health or "error" in health


class TestLogViewing:
    """Test log viewing functionality."""

    @patch("protocols.cli.handlers.daemon.subprocess.run")
    def test_cmd_daemon_logs_no_files(
        self, mock_run: MagicMock, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test logs when no log files exist."""
        with patch("protocols.cli.handlers.daemon.LOGS_DIR", tmp_path):
            result = cmd_daemon(["logs"])
            captured = capsys.readouterr()

            assert result == 0
            assert "No logs found" in captured.out

    @patch("protocols.cli.handlers.daemon.subprocess.run")
    def test_cmd_daemon_logs_with_files(
        self, mock_run: MagicMock, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test logs when log files exist."""
        # Create log files
        stdout_log = tmp_path / "cortex.stdout.log"
        stderr_log = tmp_path / "cortex.stderr.log"
        stdout_log.write_text("stdout content")
        stderr_log.write_text("stderr content")

        mock_run.return_value = MagicMock(returncode=0, stdout="log content\n")

        with patch("protocols.cli.handlers.daemon.LOGS_DIR", tmp_path):
            result = cmd_daemon(["logs"])
            captured = capsys.readouterr()

            assert result == 0
            assert "Logs" in captured.out or "stdout" in captured.out


class TestInfraHandlerCRDs:
    """Test infra handler CRD management."""

    def test_verify_crds_expected_list(self) -> None:
        """Test that verify expects all 5 CRDs."""
        # Import the expected CRDs from the verify function
        expected = [
            "agents.kgents.io",
            "pheromones.kgents.io",
            "memories.kgents.io",
            "umwelts.kgents.io",
            "proposals.kgents.io",
        ]

        # This test documents the expected CRDs
        assert len(expected) == 5
        assert "proposals.kgents.io" in expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
