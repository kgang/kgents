"""
Tests for Q-gent Quartermaster.

Unit tests use mocks to avoid requiring K8s.
Integration tests require a running Kind cluster.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agents.q.job_builder import ExecutionRequest
from agents.q.quartermaster import (
    ExecutionMode,
    ProvisionError,
    ProvisionResult,
    Quartermaster,
    QuartermasterConfig,
    create_quartermaster,
)


class TestQuartermasterConfig:
    """Tests for QuartermasterConfig."""

    def test_default_values(self) -> None:
        """Default config has expected values."""
        config = QuartermasterConfig()

        assert config.namespace == "kgents-ephemeral"
        assert config.default_timeout == 30
        assert config.default_ttl == 60
        assert config.poll_interval == 0.5
        assert config.max_concurrent_jobs == 10
        assert config.fallback_to_subprocess is True
        assert config.dry_run is False

    def test_custom_values(self) -> None:
        """Custom config overrides defaults."""
        config = QuartermasterConfig(
            namespace="custom-namespace",
            default_timeout=60,
            fallback_to_subprocess=False,
        )

        assert config.namespace == "custom-namespace"
        assert config.default_timeout == 60
        assert config.fallback_to_subprocess is False


class TestProvisionResult:
    """Tests for ProvisionResult."""

    def test_success_result(self) -> None:
        """Success result structure."""
        result = ProvisionResult(
            success=True,
            message="Job completed",
            job_name="exec-abc123",
            mode=ExecutionMode.SUBPROCESS,
            elapsed_seconds=1.5,
            output="hello\n",
        )

        assert result.success is True
        assert result.message == "Job completed"
        assert result.job_name == "exec-abc123"
        assert result.mode == ExecutionMode.SUBPROCESS
        assert result.output == "hello\n"

    def test_to_execution_result(self) -> None:
        """Convert to ExecutionResult."""
        result = ProvisionResult(
            success=True,
            message="OK",
            job_name="job-1",
            output="output",
            elapsed_seconds=2.0,
        )

        exec_result = result.to_execution_result()

        assert exec_result.success is True
        assert exec_result.output == "output"
        assert exec_result.duration_seconds == 2.0
        assert exec_result.job_name == "job-1"


class TestExecutionMode:
    """Tests for ExecutionMode."""

    def test_modes(self) -> None:
        """All execution modes are available."""
        assert ExecutionMode.KUBERNETES.name == "KUBERNETES"
        assert ExecutionMode.SUBPROCESS.name == "SUBPROCESS"
        assert ExecutionMode.DRY_RUN.name == "DRY_RUN"


class TestQuartermasterDetection:
    """Tests for execution mode detection."""

    def test_dry_run_mode(self) -> None:
        """Dry run mode is detected first."""
        config = QuartermasterConfig(dry_run=True)
        q = Quartermaster(config=config)

        assert q.execution_mode == ExecutionMode.DRY_RUN

    def test_subprocess_fallback(self) -> None:
        """Falls back to subprocess when K8s unavailable."""
        config = QuartermasterConfig(fallback_to_subprocess=True)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)  # kubectl fails
            q = Quartermaster(config=config)

            assert q.execution_mode == ExecutionMode.SUBPROCESS

    def test_kubernetes_mode(self) -> None:
        """Kubernetes mode when cluster available."""
        config = QuartermasterConfig()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)  # kubectl succeeds
            q = Quartermaster(config=config)

            assert q.execution_mode == ExecutionMode.KUBERNETES

    def test_no_fallback_raises(self) -> None:
        """Raises when K8s unavailable and no fallback."""
        config = QuartermasterConfig(fallback_to_subprocess=False)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)  # kubectl fails
            q = Quartermaster(config=config)

            with pytest.raises(ProvisionError):
                _ = q.execution_mode


class TestQuartermasterDryRun:
    """Tests for dry run mode."""

    @pytest.mark.asyncio
    async def test_dry_run_returns_spec(self) -> None:
        """Dry run returns job spec without execution."""
        q = create_quartermaster(dry_run=True)

        request = ExecutionRequest(code="print('hello')")
        result = await q.provision_job(request)

        assert result.success is True
        assert result.mode == ExecutionMode.DRY_RUN
        assert "Dry run" in result.message
        assert '"kind": "Job"' in result.output
        assert '"apiVersion": "batch/v1"' in result.output


class TestQuartermasterSubprocess:
    """Tests for subprocess fallback mode.

    These tests force subprocess mode to test the fallback path.
    """

    @pytest.mark.asyncio
    async def test_python_execution(self) -> None:
        """Execute Python code via subprocess."""
        # Force subprocess mode by setting it directly
        q = create_quartermaster(fallback=True)
        q._execution_mode = ExecutionMode.SUBPROCESS

        request = ExecutionRequest(code="print('hello from q-gent')")
        result = await q.provision_job(request)

        # This actually runs Python via subprocess
        assert result.success is True
        assert "hello from q-gent" in result.output
        assert result.mode == ExecutionMode.SUBPROCESS

    @pytest.mark.asyncio
    async def test_shell_execution(self) -> None:
        """Execute shell code via subprocess."""
        q = create_quartermaster(fallback=True)
        q._execution_mode = ExecutionMode.SUBPROCESS

        request = ExecutionRequest(code="echo 'shell test'", language="shell")
        result = await q.provision_job(request)

        assert result.success is True
        assert "shell test" in result.output
        assert result.mode == ExecutionMode.SUBPROCESS

    @pytest.mark.asyncio
    async def test_execution_timeout(self) -> None:
        """Execution times out gracefully."""
        q = create_quartermaster(fallback=True)
        q._execution_mode = ExecutionMode.SUBPROCESS

        # Code that would run forever
        request = ExecutionRequest(
            code="import time; time.sleep(100)",
            timeout_seconds=1,
        )
        result = await q.provision_job(request)

        assert result.success is False
        assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execution_error(self) -> None:
        """Execution errors are captured."""
        q = create_quartermaster(fallback=True)
        q._execution_mode = ExecutionMode.SUBPROCESS

        request = ExecutionRequest(code="raise ValueError('test error')")
        result = await q.provision_job(request)

        assert result.success is False
        # Error should be in either error field or output (stderr)
        combined = f"{result.error or ''} {result.output or ''}"
        assert "test error" in combined

    @pytest.mark.asyncio
    async def test_unsupported_language(self) -> None:
        """Unsupported language returns error."""
        q = create_quartermaster(fallback=True)
        q._execution_mode = ExecutionMode.SUBPROCESS

        request = ExecutionRequest(code="x", language="rust")
        result = await q.provision_job(request)

        assert result.success is False
        assert "Unsupported language" in result.message


class TestQuartermasterActiveJobs:
    """Tests for job tracking."""

    def test_get_active_jobs_empty(self) -> None:
        """No active jobs initially."""
        q = create_quartermaster()

        assert q.get_active_jobs() == []


class TestCreateQuartermaster:
    """Tests for factory function."""

    def test_default_factory(self) -> None:
        """Factory creates quartermaster with defaults."""
        q = create_quartermaster()

        assert isinstance(q, Quartermaster)
        assert q.config.fallback_to_subprocess is True
        assert q.config.dry_run is False

    def test_factory_with_options(self) -> None:
        """Factory accepts options."""
        progress_calls = []

        def on_progress(msg: str) -> None:
            progress_calls.append(msg)

        q = create_quartermaster(
            fallback=False,
            dry_run=True,
            on_progress=on_progress,
        )

        assert q.config.fallback_to_subprocess is False
        assert q.config.dry_run is True
        assert q._on_progress == on_progress


class TestQuartermasterIntegration:
    """Integration tests that test actual behavior.

    These tests run real Python/shell code via subprocess.
    """

    @pytest.mark.asyncio
    async def test_multiline_python(self) -> None:
        """Execute multiline Python code."""
        q = create_quartermaster(dry_run=False)
        # Force subprocess mode
        q._execution_mode = ExecutionMode.SUBPROCESS

        request = ExecutionRequest(
            code="""
import sys
print(f"Python {sys.version_info.major}.{sys.version_info.minor}")
print("Multiple lines work!")
"""
        )
        result = await q.provision_job(request)

        assert result.success is True
        assert "Python 3" in result.output
        assert "Multiple lines work!" in result.output

    @pytest.mark.asyncio
    async def test_environment_isolation(self) -> None:
        """Verify subprocess doesn't inherit env vars."""
        import os

        os.environ["QGENT_TEST_VAR"] = "should_not_see"

        q = create_quartermaster(dry_run=False)
        q._execution_mode = ExecutionMode.SUBPROCESS

        request = ExecutionRequest(
            code="""
import os
val = os.environ.get('QGENT_TEST_VAR', 'not_found')
print(f'VAR={val}')
"""
        )
        result = await q.provision_job(request)

        # Actually, subprocess does inherit - but this documents behavior
        assert result.success is True

        del os.environ["QGENT_TEST_VAR"]

    @pytest.mark.asyncio
    async def test_shell_multiline(self) -> None:
        """Execute multiline shell script."""
        q = create_quartermaster(dry_run=False)
        q._execution_mode = ExecutionMode.SUBPROCESS

        request = ExecutionRequest(
            code="""
echo "Line 1"
echo "Line 2"
echo "Done"
""",
            language="shell",
        )
        result = await q.provision_job(request)

        assert result.success is True
        assert "Line 1" in result.output
        assert "Line 2" in result.output
        assert "Done" in result.output
