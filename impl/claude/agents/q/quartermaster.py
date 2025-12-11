"""
Quartermaster - Resource Provisioning for K-Terrarium.

Q-gent is the gatekeeper for dangerous operations. Agents never directly
request cluster resources - they ask Q-gent, who decides whether/how to provision.

The "Disposable Dojo" Pattern:
1. Agent requests code execution
2. Q-gent spins up a disposable container in kgents-ephemeral
3. Code runs in complete isolation
4. Results are returned
5. Container auto-deletes after TTL

Dependencies:
- Kubernetes client (optional - graceful degradation)
- Kind cluster running (detect_terrarium_mode)
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

from .job_builder import (
    SANDBOX_PYTHON,
    SANDBOX_SHELL,
    ExecutionRequest,
    ExecutionResult,
    JobBuilder,
    JobConfig,
    JobPhase,
    JobSpec,
    JobStatus,
    ResourceLimits,
)


class ProvisionError(Exception):
    """Error during resource provisioning."""

    pass


class ExecutionMode(Enum):
    """How Q-gent executes code."""

    KUBERNETES = auto()  # Full K8s Job execution
    SUBPROCESS = auto()  # Local subprocess fallback
    DRY_RUN = auto()  # Return spec without execution


@dataclass
class ProvisionResult:
    """Result of a provisioning operation."""

    success: bool
    message: str
    job_name: str = ""
    mode: ExecutionMode = ExecutionMode.KUBERNETES
    elapsed_seconds: float = 0.0
    output: str = ""
    error: str | None = None

    def to_execution_result(self) -> ExecutionResult:
        """Convert to ExecutionResult."""
        return ExecutionResult(
            success=self.success,
            output=self.output,
            error=self.error,
            duration_seconds=self.elapsed_seconds,
            job_name=self.job_name,
        )


@dataclass
class QuartermasterConfig:
    """Configuration for Q-gent."""

    namespace: str = "kgents-ephemeral"
    default_timeout: int = 30
    default_ttl: int = 60
    poll_interval: float = 0.5  # seconds between status checks
    max_concurrent_jobs: int = 10
    fallback_to_subprocess: bool = True  # Use subprocess if K8s unavailable
    dry_run: bool = False  # Don't actually execute


class Quartermaster:
    """
    Resource Provisioning Agent.

    Q-gent provisions resources for other agents, acting as the gatekeeper
    for dangerous operations.

    Example:
        q = Quartermaster()

        # Execute Python code
        result = await q.provision_job(
            ExecutionRequest(code="print('hello')", language="python")
        )
        print(result.output)  # "hello\\n"

        # Execute shell script
        result = await q.provision_job(
            ExecutionRequest(code="echo 'world'", language="shell")
        )
    """

    def __init__(
        self,
        config: QuartermasterConfig | None = None,
        on_progress: Callable[[str], None] | None = None,
    ):
        """
        Initialize Q-gent.

        Args:
            config: Configuration options
            on_progress: Callback for progress messages
        """
        self.config = config or QuartermasterConfig()
        self._on_progress = on_progress or (lambda msg: None)
        self._active_jobs: dict[str, JobSpec] = {}
        self._execution_mode: ExecutionMode | None = None

    def _detect_execution_mode(self) -> ExecutionMode:
        """Detect available execution mode."""
        if self.config.dry_run:
            return ExecutionMode.DRY_RUN

        # Check for Kind cluster
        try:
            result = subprocess.run(
                ["kubectl", "get", "namespace", self.config.namespace],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return ExecutionMode.KUBERNETES
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Fallback to subprocess
        if self.config.fallback_to_subprocess:
            return ExecutionMode.SUBPROCESS

        raise ProvisionError(
            "Kubernetes not available and fallback_to_subprocess=False"
        )

    @property
    def execution_mode(self) -> ExecutionMode:
        """Get (and cache) execution mode."""
        if self._execution_mode is None:
            self._execution_mode = self._detect_execution_mode()
        return self._execution_mode

    async def provision_job(self, request: ExecutionRequest) -> ProvisionResult:
        """
        Execute code in a disposable container.

        The container is:
        - Network-isolated by default
        - Resource-constrained
        - Automatically deleted after TTL

        Args:
            request: Execution request with code and options

        Returns:
            ProvisionResult with output or error
        """
        start_time = time.perf_counter()
        mode = self.execution_mode

        self._on_progress(f"Provisioning job in {mode.name} mode...")

        # Build job spec
        builder = JobBuilder("exec")
        builder = builder.with_code(request.code)

        # Select image based on language
        if request.language.lower() in ("python", "py"):
            builder = builder.with_image(SANDBOX_PYTHON)
        elif request.language.lower() in ("shell", "sh", "bash"):
            builder = builder.with_image(SANDBOX_SHELL)
        else:
            return ProvisionResult(
                success=False,
                message=f"Unsupported language: {request.language}",
                mode=mode,
                error=f"Language must be 'python' or 'shell', got '{request.language}'",
            )

        # Apply limits
        builder = builder.with_limits(
            cpu=request.cpu_limit,
            memory=request.memory_limit,
        )
        builder = builder.with_timeout(request.timeout_seconds)
        builder = builder.with_network(request.network_access)

        spec = builder.build()

        # Execute based on mode
        if mode == ExecutionMode.DRY_RUN:
            return ProvisionResult(
                success=True,
                message="Dry run - job not executed",
                job_name=spec.name,
                mode=mode,
                output=json.dumps(spec.to_k8s_manifest(), indent=2),
            )
        elif mode == ExecutionMode.SUBPROCESS:
            return await self._execute_subprocess(spec, request, start_time)
        else:
            return await self._execute_kubernetes(spec, request, start_time)

    async def _execute_subprocess(
        self, spec: JobSpec, request: ExecutionRequest, start_time: float
    ) -> ProvisionResult:
        """Execute code via local subprocess (fallback mode)."""
        self._on_progress("Executing via subprocess (fallback)...")

        try:
            if request.language.lower() in ("python", "py"):
                proc = await asyncio.create_subprocess_exec(
                    "python",
                    "-c",
                    request.code,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            else:
                proc = await asyncio.create_subprocess_exec(
                    "sh",
                    "-c",
                    request.code,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=request.timeout_seconds
                )
            except asyncio.TimeoutError:
                proc.kill()
                return ProvisionResult(
                    success=False,
                    message="Execution timed out",
                    job_name=spec.name,
                    mode=ExecutionMode.SUBPROCESS,
                    elapsed_seconds=time.perf_counter() - start_time,
                    error=f"Execution exceeded {request.timeout_seconds}s timeout",
                )

            elapsed = time.perf_counter() - start_time
            output = stdout.decode("utf-8") if stdout else ""
            error_output = stderr.decode("utf-8") if stderr else None

            if proc.returncode == 0:
                return ProvisionResult(
                    success=True,
                    message="Execution completed successfully",
                    job_name=spec.name,
                    mode=ExecutionMode.SUBPROCESS,
                    elapsed_seconds=elapsed,
                    output=output,
                )
            else:
                return ProvisionResult(
                    success=False,
                    message=f"Execution failed with code {proc.returncode}",
                    job_name=spec.name,
                    mode=ExecutionMode.SUBPROCESS,
                    elapsed_seconds=elapsed,
                    output=output,
                    error=error_output,
                )

        except Exception as e:
            return ProvisionResult(
                success=False,
                message=f"Subprocess execution failed: {e}",
                job_name=spec.name,
                mode=ExecutionMode.SUBPROCESS,
                elapsed_seconds=time.perf_counter() - start_time,
                error=str(e),
            )

    async def _execute_kubernetes(
        self, spec: JobSpec, request: ExecutionRequest, start_time: float
    ) -> ProvisionResult:
        """Execute code via Kubernetes Job."""
        self._on_progress(f"Creating K8s Job: {spec.name}")

        # Create job
        manifest = spec.to_k8s_manifest()

        try:
            # Apply the job using kubectl
            result = subprocess.run(
                ["kubectl", "apply", "-f", "-"],
                input=json.dumps(manifest),
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return ProvisionResult(
                    success=False,
                    message=f"Failed to create job: {result.stderr}",
                    job_name=spec.name,
                    mode=ExecutionMode.KUBERNETES,
                    elapsed_seconds=time.perf_counter() - start_time,
                    error=result.stderr,
                )

            self._active_jobs[spec.name] = spec

            # Wait for completion
            return await self._wait_for_job(spec, request.timeout_seconds, start_time)

        except subprocess.TimeoutExpired:
            return ProvisionResult(
                success=False,
                message="Timed out creating job",
                job_name=spec.name,
                mode=ExecutionMode.KUBERNETES,
                elapsed_seconds=time.perf_counter() - start_time,
                error="kubectl apply timed out",
            )
        except Exception as e:
            return ProvisionResult(
                success=False,
                message=f"Kubernetes execution failed: {e}",
                job_name=spec.name,
                mode=ExecutionMode.KUBERNETES,
                elapsed_seconds=time.perf_counter() - start_time,
                error=str(e),
            )

    async def _wait_for_job(
        self, spec: JobSpec, timeout: int, start_time: float
    ) -> ProvisionResult:
        """Wait for a Kubernetes Job to complete."""
        deadline = time.perf_counter() + timeout + 10  # Extra buffer

        while time.perf_counter() < deadline:
            status = self._get_job_status(spec)

            if status.phase == JobPhase.SUCCEEDED:
                output = self._get_job_logs(spec)
                self._cleanup_job(spec)
                return ProvisionResult(
                    success=True,
                    message="Job completed successfully",
                    job_name=spec.name,
                    mode=ExecutionMode.KUBERNETES,
                    elapsed_seconds=time.perf_counter() - start_time,
                    output=output,
                )

            if status.phase == JobPhase.FAILED:
                output = self._get_job_logs(spec)
                self._cleanup_job(spec)
                return ProvisionResult(
                    success=False,
                    message=f"Job failed: {status.message}",
                    job_name=spec.name,
                    mode=ExecutionMode.KUBERNETES,
                    elapsed_seconds=time.perf_counter() - start_time,
                    output=output,
                    error=status.message or "Job failed",
                )

            await asyncio.sleep(self.config.poll_interval)

        # Timeout
        self._cleanup_job(spec)
        return ProvisionResult(
            success=False,
            message="Job execution timed out",
            job_name=spec.name,
            mode=ExecutionMode.KUBERNETES,
            elapsed_seconds=time.perf_counter() - start_time,
            error=f"Exceeded {timeout}s timeout",
        )

    def _get_job_status(self, spec: JobSpec) -> JobStatus:
        """Get current job status from Kubernetes."""
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "job",
                    spec.name,
                    "-n",
                    spec.namespace,
                    "-o",
                    "jsonpath={.status}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return JobStatus(
                    name=spec.name,
                    phase=JobPhase.UNKNOWN,
                    message=result.stderr,
                )

            status_json = result.stdout.strip()
            if not status_json:
                return JobStatus(name=spec.name, phase=JobPhase.PENDING)

            status_data = json.loads(status_json)

            # Determine phase
            if status_data.get("succeeded", 0) > 0:
                phase = JobPhase.SUCCEEDED
            elif status_data.get("failed", 0) > 0:
                phase = JobPhase.FAILED
            elif status_data.get("active", 0) > 0:
                phase = JobPhase.RUNNING
            else:
                phase = JobPhase.PENDING

            # Extract conditions for message
            message = ""
            conditions = status_data.get("conditions", [])
            if conditions:
                message = conditions[-1].get("message", "")

            return JobStatus(
                name=spec.name,
                phase=phase,
                succeeded=status_data.get("succeeded", 0),
                failed=status_data.get("failed", 0),
                message=message,
            )

        except Exception as e:
            return JobStatus(
                name=spec.name,
                phase=JobPhase.UNKNOWN,
                message=str(e),
            )

    def _get_job_logs(self, spec: JobSpec) -> str:
        """Get logs from the job's pod."""
        try:
            # Get pod name
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "pods",
                    "-n",
                    spec.namespace,
                    "-l",
                    f"job-name={spec.name}",
                    "-o",
                    "jsonpath={.items[0].metadata.name}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0 or not result.stdout.strip():
                return ""

            pod_name = result.stdout.strip()

            # Get logs
            result = subprocess.run(
                ["kubectl", "logs", pod_name, "-n", spec.namespace],
                capture_output=True,
                text=True,
                timeout=10,
            )

            return result.stdout if result.returncode == 0 else ""

        except Exception:
            return ""

    def _cleanup_job(self, spec: JobSpec) -> None:
        """Clean up completed job."""
        self._active_jobs.pop(spec.name, None)
        # Note: TTL controller will clean up the actual K8s resources

    def get_active_jobs(self) -> list[str]:
        """Get list of active job names."""
        return list(self._active_jobs.keys())


def create_quartermaster(
    fallback: bool = True,
    dry_run: bool = False,
    on_progress: Callable[[str], None] | None = None,
) -> Quartermaster:
    """
    Factory function to create Q-gent.

    Args:
        fallback: Allow subprocess fallback when K8s unavailable
        dry_run: Don't actually execute, return specs
        on_progress: Progress callback

    Returns:
        Configured Quartermaster
    """
    config = QuartermasterConfig(
        fallback_to_subprocess=fallback,
        dry_run=dry_run,
    )
    return Quartermaster(config=config, on_progress=on_progress)
