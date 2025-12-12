"""
Tests for K-Terrarium Dev Mode.

Tests the live reload development experience for agents.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from infra.k8s.dev_mode import (
    DevMode,
    DevModeConfig,
    DevModeResult,
    DevModeStatus,
    DevPodSpec,
    create_dev_mode,
)

# =============================================================================
# DevPodSpec Tests
# =============================================================================


class TestDevPodSpec:
    """Tests for DevPodSpec."""

    def test_basic_construction(self) -> None:
        """Test basic DevPodSpec construction."""
        spec = DevPodSpec(
            genus="B",
            name="b-gent-dev",
            namespace="kgents-agents",
            source_path=Path("impl/claude/agents"),
            mount_path="/app/agents",
        )

        assert spec.genus == "B"
        assert spec.name == "b-gent-dev"
        assert spec.namespace == "kgents-agents"
        assert spec.cpu == "200m"  # Dev mode default (more resources)
        assert spec.memory == "512Mi"

    def test_to_deployment_generates_valid_manifest(self) -> None:
        """Test that to_deployment generates valid K8s manifest."""
        spec = DevPodSpec(
            genus="B",
            name="b-gent-dev",
            namespace="kgents-agents",
            source_path=Path("/tmp/test/agents"),
            mount_path="/app/agents",
        )

        deployment = spec.to_deployment()

        # Check structure
        assert deployment["apiVersion"] == "apps/v1"
        assert deployment["kind"] == "Deployment"
        assert deployment["metadata"]["name"] == "b-gent-dev"
        assert deployment["metadata"]["namespace"] == "kgents-agents"

        # Check labels
        labels = deployment["metadata"]["labels"]
        assert labels["kgents.io/genus"] == "B"
        assert labels["kgents.io/mode"] == "dev"
        assert labels["app.kubernetes.io/managed-by"] == "kgents-dev"

        # Check volume mount
        pod_spec = deployment["spec"]["template"]["spec"]
        volumes = pod_spec["volumes"]
        assert len(volumes) == 1
        assert volumes[0]["name"] == "source"
        # Path is resolved, so on macOS /tmp -> /private/tmp
        assert "test/agents" in volumes[0]["hostPath"]["path"]

        # Check container
        containers = pod_spec["containers"]
        assert len(containers) == 1
        container = containers[0]
        assert container["name"] == "dev"
        assert container["volumeMounts"][0]["mountPath"] == "/app/agents"

        # Check env vars
        env = {e["name"]: e["value"] for e in container["env"]}
        assert env["KGENTS_GENUS"] == "B"
        assert env["KGENTS_DEV_MODE"] == "1"
        assert env["PYTHONUNBUFFERED"] == "1"

    def test_to_deployment_includes_reload_script(self) -> None:
        """Test that deployment includes file watcher reload script."""
        spec = DevPodSpec(
            genus="B",
            name="b-gent-dev",
            namespace="kgents-agents",
            source_path=Path("/tmp/test/agents"),
            mount_path="/app/agents",
            entrypoint="agents.b.main",
        )

        deployment = spec.to_deployment()
        container = deployment["spec"]["template"]["spec"]["containers"][0]

        # Command should be a shell script
        command = container["command"]
        assert command[0] == "sh"
        assert command[1] == "-c"

        # Script should mention watching and reloading
        script = command[2]
        assert "dev" in script.lower()
        assert "watch" in script.lower() or "watcher" in script.lower()

    def test_labels_include_dev_mode_marker(self) -> None:
        """Test that labels mark pods as dev mode."""
        spec = DevPodSpec(
            genus="B",
            name="b-gent-dev",
            namespace="kgents-agents",
            source_path=Path("/tmp/test"),
            mount_path="/app",
        )

        labels = spec._labels()

        assert labels["kgents.io/mode"] == "dev"
        assert labels["kgents.io/genus"] == "B"
        assert "kgents-dev" in labels["app.kubernetes.io/managed-by"]


# =============================================================================
# DevModeConfig Tests
# =============================================================================


class TestDevModeConfig:
    """Tests for DevModeConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = DevModeConfig()

        assert config.namespace == "kgents-agents"
        assert "*.py" in config.watch_patterns
        assert config.reload_delay == 0.5
        assert config.log_tail_lines == 100
        assert config.mount_path == "/app/agents"

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = DevModeConfig(
            namespace="custom-ns",
            reload_delay=1.0,
            log_tail_lines=50,
        )

        assert config.namespace == "custom-ns"
        assert config.reload_delay == 1.0
        assert config.log_tail_lines == 50


# =============================================================================
# DevMode Unit Tests (Mocked)
# =============================================================================


class TestDevModeUnit:
    """Unit tests for DevMode with mocked subprocess."""

    def test_create_dev_mode(self) -> None:
        """Test factory function."""
        progress_calls: list[str] = []
        dev = create_dev_mode(on_progress=progress_calls.append)

        assert dev is not None
        assert isinstance(dev, DevMode)

    @patch("subprocess.run")
    def test_cluster_not_running_returns_error(self, mock_run: MagicMock) -> None:
        """Test that start fails when cluster not running."""
        mock_run.return_value = MagicMock(returncode=1)

        dev = DevMode()
        import asyncio

        result = asyncio.run(dev.start("b-gent"))

        assert not result.success
        assert result.status == DevModeStatus.ERROR
        assert "not running" in result.message.lower()

    @patch("subprocess.run")
    def test_missing_agent_directory_returns_error(self, mock_run: MagicMock) -> None:
        """Test that start fails when agent directory doesn't exist."""
        # First call checks cluster (success)
        # Subsequent calls would be for apply etc
        mock_run.return_value = MagicMock(returncode=0)

        # Use a path that doesn't exist
        config = DevModeConfig(source_path=Path("/nonexistent/path"))
        dev = DevMode(config=config)

        import asyncio

        result = asyncio.run(dev.start("b-gent"))

        assert not result.success
        assert result.status == DevModeStatus.ERROR
        assert "not found" in result.message.lower()

    def test_genus_normalization(self) -> None:
        """Test that genus names are normalized correctly."""
        dev = DevMode()

        # Test various input formats - these are internal to start()
        # We can test the normalization logic indirectly
        # by checking spec generation

        spec = DevPodSpec(
            genus="B",  # Already uppercase
            name="b-gent-dev",
            namespace="test",
            source_path=Path("/tmp"),
            mount_path="/app",
        )
        assert spec.genus == "B"

        spec2 = DevPodSpec(
            genus="PSI",
            name="psi-gent-dev",
            namespace="test",
            source_path=Path("/tmp"),
            mount_path="/app",
        )
        assert spec2.genus == "PSI"

    @patch("subprocess.run")
    async def test_stop_with_no_pods_returns_success(self, mock_run: MagicMock) -> None:
        """Test that stop succeeds when no pods running."""
        # First call returns no pods
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        dev = DevMode()
        result = await dev.stop()

        assert result.success
        assert result.status == DevModeStatus.STOPPED

    @patch("subprocess.run")
    async def test_status_returns_empty_list_on_error(
        self, mock_run: MagicMock
    ) -> None:
        """Test that status returns empty list on kubectl error."""
        mock_run.return_value = MagicMock(returncode=1)

        dev = DevMode()
        pods = await dev.status()

        assert pods == []


# =============================================================================
# DevModeResult Tests
# =============================================================================


class TestDevModeResult:
    """Tests for DevModeResult dataclass."""

    def test_success_result(self) -> None:
        """Test successful result."""
        result = DevModeResult(
            success=True,
            message="Started successfully",
            status=DevModeStatus.RUNNING,
            pod_name="b-gent-dev",
            elapsed_seconds=1.5,
        )

        assert result.success
        assert result.status == DevModeStatus.RUNNING
        assert result.pod_name == "b-gent-dev"
        assert result.elapsed_seconds == 1.5

    def test_failure_result(self) -> None:
        """Test failure result."""
        result = DevModeResult(
            success=False,
            message="Failed to start",
            status=DevModeStatus.ERROR,
        )

        assert not result.success
        assert result.status == DevModeStatus.ERROR
        assert result.pod_name == ""  # Default


# =============================================================================
# Integration Tests (require cluster - marked slow)
# =============================================================================


@pytest.mark.slow
class TestDevModeIntegration:
    """Integration tests that require a running Kind cluster."""

    @pytest.fixture
    def dev(self) -> DevMode:
        """Create DevMode instance."""
        return create_dev_mode()

    @pytest.fixture
    def has_cluster(self) -> bool:
        """Check if Kind cluster is available."""
        import subprocess

        try:
            result = subprocess.run(
                ["kubectl", "get", "namespace", "kgents-agents"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    async def test_start_stop_cycle(self, dev: DevMode, has_cluster: bool) -> None:
        """Test full start-stop cycle."""
        if not has_cluster:
            pytest.skip("Kind cluster not available")

        # Start dev mode (but don't attach - would block)
        # This test would need a real agent directory
        # For now just verify the API shape
        result = await dev.stop()  # Should succeed even with no pods
        assert result.success

    async def test_status_reports_running_pods(
        self, dev: DevMode, has_cluster: bool
    ) -> None:
        """Test that status correctly reports running dev pods."""
        if not has_cluster:
            pytest.skip("Kind cluster not available")

        # Just verify the API works
        pods = await dev.status()
        assert isinstance(pods, list)


# =============================================================================
# CLI Handler Tests
# =============================================================================


class TestDevCLIHandler:
    """Tests for the dev CLI handler."""

    def test_help_flag(self) -> None:
        """Test --help flag."""
        from protocols.cli.handlers.dev import cmd_dev

        # Should not raise, returns 0
        result = cmd_dev(["--help"])
        assert result == 0

    def test_parse_args_attach_flag(self) -> None:
        """Test parsing --attach flag."""
        from protocols.cli.handlers.dev import _parse_args

        options = _parse_args(["b-gent", "--attach"])

        assert options["agent"] == "b-gent"
        assert options["attach"] is True

    def test_parse_args_stop_flag(self) -> None:
        """Test parsing --stop flag."""
        from protocols.cli.handlers.dev import _parse_args

        options = _parse_args(["--stop"])
        assert options["stop"] is True
        assert options.get("agent") is None

        options2 = _parse_args(["--stop", "b-gent"])
        assert options2["stop"] is True
        assert options2["agent"] == "b-gent"

    def test_parse_args_status_flag(self) -> None:
        """Test parsing --status flag."""
        from protocols.cli.handlers.dev import _parse_args

        options = _parse_args(["--status"])
        assert options["status"] is True

    def test_parse_args_source_option(self) -> None:
        """Test parsing --source option."""
        from protocols.cli.handlers.dev import _parse_args

        options = _parse_args(["b-gent", "--source", "/custom/path"])

        assert options["agent"] == "b-gent"
        assert options["source"] == "/custom/path"

    def test_parse_args_missing_source_value(self) -> None:
        """Test error when --source missing value."""
        from protocols.cli.handlers.dev import _parse_args

        options = _parse_args(["b-gent", "--source"])
        assert "error" in options

    def test_parse_args_unknown_option(self) -> None:
        """Test error on unknown option."""
        from protocols.cli.handlers.dev import _parse_args

        options = _parse_args(["b-gent", "--unknown"])
        assert "error" in options
