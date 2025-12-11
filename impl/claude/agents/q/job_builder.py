"""
Job Builder for K-Terrarium Ephemeral Execution.

Builds Kubernetes Job specifications for disposable code execution.
Jobs run in kgents-ephemeral namespace with strict resource limits.

Design Principles:
1. Immutable specs - JobSpec is a frozen dataclass
2. Builder pattern - Fluent API for customization
3. Safe defaults - Network isolated, resource constrained
4. TTL cleanup - Jobs auto-delete after completion
"""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class JobPhase(Enum):
    """Current phase of a Kubernetes Job."""

    PENDING = auto()  # Not yet scheduled
    RUNNING = auto()  # Actively executing
    SUCCEEDED = auto()  # Completed successfully
    FAILED = auto()  # Execution failed
    UNKNOWN = auto()  # Cannot determine phase


@dataclass(frozen=True)
class ResourceLimits:
    """
    Resource constraints for job containers.

    Mapped to Kubernetes resource limits. These are HARD limits -
    the kernel will enforce them via cgroups.

    Defaults are conservative for untrusted code.
    """

    cpu: str = "100m"  # 100 millicores (0.1 CPU)
    memory: str = "128Mi"  # 128 MiB
    ephemeral_storage: str = "100Mi"  # Disk space

    def to_k8s_dict(self) -> dict[str, str]:
        """Convert to Kubernetes resource dict."""
        return {
            "cpu": self.cpu,
            "memory": self.memory,
            "ephemeral-storage": self.ephemeral_storage,
        }


def default_resource_limits() -> ResourceLimits:
    """Get conservative default resource limits."""
    return ResourceLimits()


@dataclass(frozen=True)
class ImageSpec:
    """
    Container image specification.

    Includes image name and optional pull policy.
    """

    name: str
    pull_policy: str = "IfNotPresent"  # Never pull in Kind (faster)
    command: list[str] | None = None  # Override entrypoint
    args: list[str] | None = None  # Arguments to command


# Pre-defined sandbox images
SANDBOX_PYTHON = ImageSpec(
    name="python:3.12-slim",
    command=["python", "-c"],
)

SANDBOX_SHELL = ImageSpec(
    name="busybox:latest",
    command=["sh", "-c"],
)


@dataclass(frozen=True)
class JobConfig:
    """
    Configuration for job execution behavior.

    Controls timeouts, retries, and cleanup.
    """

    timeout_seconds: int = 30  # Max execution time
    ttl_seconds_after_finished: int = 60  # Cleanup delay after completion
    backoff_limit: int = 0  # No retries for untrusted code
    active_deadline_seconds: int | None = None  # Hard deadline (defaults to timeout)
    network_access: bool = False  # Isolated by default


@dataclass(frozen=True)
class JobSpec:
    """
    Complete specification for a Kubernetes Job.

    Immutable - create new specs for modifications.
    """

    name: str
    namespace: str
    image: ImageSpec
    code: str
    limits: ResourceLimits
    config: JobConfig
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    def to_k8s_manifest(self) -> dict[str, Any]:
        """
        Convert to Kubernetes Job manifest.

        Returns a dict suitable for kubectl apply or kubernetes client.
        """
        # Build command
        command = self.image.command or ["sh", "-c"]
        args = [self.code] if self.image.args is None else self.image.args + [self.code]

        # Build container spec
        container = {
            "name": "executor",
            "image": self.image.name,
            "imagePullPolicy": self.image.pull_policy,
            "command": command,
            "args": args,
            "resources": {
                "limits": self.limits.to_k8s_dict(),
                "requests": {
                    "cpu": "25m",
                    "memory": "64Mi",
                },
            },
            # Security hardening
            "securityContext": {
                "runAsNonRoot": True,
                "runAsUser": 1000,
                "readOnlyRootFilesystem": True,
                "allowPrivilegeEscalation": False,
                "capabilities": {"drop": ["ALL"]},
            },
        }

        # Build pod spec
        pod_spec = {
            "restartPolicy": "Never",  # Don't restart failed jobs
            "containers": [container],
            # Write to /tmp for read-only root
            "volumes": [{"name": "tmp", "emptyDir": {"sizeLimit": "50Mi"}}],
        }

        # Add volume mount
        container["volumeMounts"] = [{"name": "tmp", "mountPath": "/tmp"}]

        # Active deadline
        active_deadline = (
            self.config.active_deadline_seconds or self.config.timeout_seconds + 10
        )
        pod_spec["activeDeadlineSeconds"] = active_deadline

        # Build labels
        labels = {
            "app.kubernetes.io/part-of": "kgents",
            "kgents.io/agent": "q-gent",
            "kgents.io/job-type": "ephemeral",
            **self.labels,
        }

        # Build annotations
        annotations = {
            "kgents.io/created-at": str(int(time.time())),
            **self.annotations,
        }

        # Complete Job manifest
        return {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
                "labels": labels,
                "annotations": annotations,
            },
            "spec": {
                "ttlSecondsAfterFinished": self.config.ttl_seconds_after_finished,
                "backoffLimit": self.config.backoff_limit,
                "template": {
                    "metadata": {"labels": labels},
                    "spec": pod_spec,
                },
            },
        }


@dataclass(frozen=True)
class JobStatus:
    """Status of a running or completed job."""

    name: str
    phase: JobPhase
    start_time: float | None = None
    completion_time: float | None = None
    succeeded: int = 0
    failed: int = 0
    message: str = ""


@dataclass(frozen=True)
class ExecutionRequest:
    """
    Request to execute code in an ephemeral container.

    This is the high-level API for Q-gent clients.
    """

    code: str
    language: str = "python"
    timeout_seconds: int = 30
    cpu_limit: str = "100m"
    memory_limit: str = "128Mi"
    network_access: bool = False


@dataclass(frozen=True)
class ExecutionResult:
    """Result of ephemeral code execution."""

    success: bool
    output: str
    error: str | None = None
    duration_seconds: float = 0.0
    job_name: str = ""


class JobBuilder:
    """
    Fluent builder for JobSpec.

    Example:
        spec = (
            JobBuilder("my-job")
            .with_code("print('hello')")
            .with_image(SANDBOX_PYTHON)
            .with_limits(cpu="200m", memory="256Mi")
            .build()
        )
    """

    def __init__(self, name_prefix: str = "exec"):
        """
        Initialize builder with name prefix.

        A random suffix is added to ensure uniqueness.
        """
        suffix = secrets.token_hex(4)
        self._name = f"{name_prefix}-{suffix}"
        self._namespace = "kgents-ephemeral"
        self._image = SANDBOX_PYTHON
        self._code = ""
        self._limits = default_resource_limits()
        self._config = JobConfig()
        self._labels: dict[str, str] = {}
        self._annotations: dict[str, str] = {}

    def with_name(self, name: str) -> JobBuilder:
        """Set explicit job name (no random suffix)."""
        self._name = name
        return self

    def with_namespace(self, namespace: str) -> JobBuilder:
        """Set target namespace (default: kgents-ephemeral)."""
        self._namespace = namespace
        return self

    def with_code(self, code: str) -> JobBuilder:
        """Set code to execute."""
        self._code = code
        # Add code hash as annotation for deduplication
        code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
        self._annotations["kgents.io/code-hash"] = code_hash
        return self

    def with_image(self, image: ImageSpec) -> JobBuilder:
        """Set container image."""
        self._image = image
        return self

    def with_limits(
        self,
        cpu: str | None = None,
        memory: str | None = None,
        ephemeral_storage: str | None = None,
    ) -> JobBuilder:
        """Set resource limits."""
        self._limits = ResourceLimits(
            cpu=cpu or self._limits.cpu,
            memory=memory or self._limits.memory,
            ephemeral_storage=ephemeral_storage or self._limits.ephemeral_storage,
        )
        return self

    def with_timeout(self, seconds: int) -> JobBuilder:
        """Set execution timeout."""
        self._config = JobConfig(
            timeout_seconds=seconds,
            ttl_seconds_after_finished=self._config.ttl_seconds_after_finished,
            backoff_limit=self._config.backoff_limit,
            network_access=self._config.network_access,
        )
        return self

    def with_ttl(self, seconds: int) -> JobBuilder:
        """Set cleanup TTL after job completion."""
        self._config = JobConfig(
            timeout_seconds=self._config.timeout_seconds,
            ttl_seconds_after_finished=seconds,
            backoff_limit=self._config.backoff_limit,
            network_access=self._config.network_access,
        )
        return self

    def with_network(self, enabled: bool = True) -> JobBuilder:
        """Enable/disable network access."""
        self._config = JobConfig(
            timeout_seconds=self._config.timeout_seconds,
            ttl_seconds_after_finished=self._config.ttl_seconds_after_finished,
            backoff_limit=self._config.backoff_limit,
            network_access=enabled,
        )
        return self

    def with_label(self, key: str, value: str) -> JobBuilder:
        """Add a label."""
        self._labels[key] = value
        return self

    def with_annotation(self, key: str, value: str) -> JobBuilder:
        """Add an annotation."""
        self._annotations[key] = value
        return self

    def build(self) -> JobSpec:
        """Build the JobSpec."""
        if not self._code:
            raise ValueError("Code is required - use with_code()")

        return JobSpec(
            name=self._name,
            namespace=self._namespace,
            image=self._image,
            code=self._code,
            limits=self._limits,
            config=self._config,
            labels=self._labels,
            annotations=self._annotations,
        )


def create_python_job(code: str, **kwargs: Any) -> JobSpec:
    """
    Convenience function to create a Python execution job.

    Args:
        code: Python code to execute
        **kwargs: Additional options:
            - timeout: int (default 30)
            - cpu: str (default "100m")
            - memory: str (default "128Mi")
            - network: bool (default False)

    Returns:
        JobSpec ready for execution.
    """
    builder = JobBuilder("py").with_code(code).with_image(SANDBOX_PYTHON)

    if "timeout" in kwargs:
        builder = builder.with_timeout(kwargs["timeout"])
    if "cpu" in kwargs or "memory" in kwargs:
        builder = builder.with_limits(
            cpu=kwargs.get("cpu"),
            memory=kwargs.get("memory"),
        )
    if kwargs.get("network"):
        builder = builder.with_network(True)

    return builder.build()


def create_shell_job(script: str, **kwargs: Any) -> JobSpec:
    """
    Convenience function to create a shell execution job.

    Args:
        script: Shell script to execute
        **kwargs: Same as create_python_job

    Returns:
        JobSpec ready for execution.
    """
    builder = JobBuilder("sh").with_code(script).with_image(SANDBOX_SHELL)

    if "timeout" in kwargs:
        builder = builder.with_timeout(kwargs["timeout"])
    if "cpu" in kwargs or "memory" in kwargs:
        builder = builder.with_limits(
            cpu=kwargs.get("cpu"),
            memory=kwargs.get("memory"),
        )
    if kwargs.get("network"):
        builder = builder.with_network(True)

    return builder.build()
