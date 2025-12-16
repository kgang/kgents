"""
Tests for Q-gent Job Builder.

Unit tests for building Kubernetes Job specifications.
"""

from __future__ import annotations

import pytest
from agents.q.job_builder import (
    SANDBOX_PYTHON,
    SANDBOX_SHELL,
    ExecutionRequest,
    ExecutionResult,
    ImageSpec,
    JobBuilder,
    JobConfig,
    JobPhase,
    JobSpec,
    JobStatus,
    ResourceLimits,
    create_python_job,
    create_shell_job,
    default_resource_limits,
)


class TestResourceLimits:
    """Tests for ResourceLimits."""

    def test_default_values(self) -> None:
        """Default limits are conservative."""
        limits = ResourceLimits()

        assert limits.cpu == "100m"
        assert limits.memory == "128Mi"
        assert limits.ephemeral_storage == "100Mi"

    def test_to_k8s_dict(self) -> None:
        """Converts to K8s resource dict."""
        limits = ResourceLimits(cpu="200m", memory="256Mi")

        k8s_dict = limits.to_k8s_dict()

        assert k8s_dict["cpu"] == "200m"
        assert k8s_dict["memory"] == "256Mi"
        assert "ephemeral-storage" in k8s_dict

    def test_default_resource_limits_factory(self) -> None:
        """Factory returns default limits."""
        limits = default_resource_limits()

        assert isinstance(limits, ResourceLimits)
        assert limits.cpu == "100m"


class TestImageSpec:
    """Tests for ImageSpec."""

    def test_default_values(self) -> None:
        """Default pull policy is IfNotPresent."""
        image = ImageSpec(name="python:3.12-slim")

        assert image.name == "python:3.12-slim"
        assert image.pull_policy == "IfNotPresent"
        assert image.command is None
        assert image.args is None

    def test_sandbox_images(self) -> None:
        """Pre-defined sandbox images are correct."""
        assert SANDBOX_PYTHON.name == "python:3.12-slim"
        assert SANDBOX_PYTHON.command == ["python", "-c"]

        assert SANDBOX_SHELL.name == "busybox:latest"
        assert SANDBOX_SHELL.command == ["sh", "-c"]


class TestJobConfig:
    """Tests for JobConfig."""

    def test_default_values(self) -> None:
        """Default config is safe for untrusted code."""
        config = JobConfig()

        assert config.timeout_seconds == 30
        assert config.ttl_seconds_after_finished == 60
        assert config.backoff_limit == 0  # No retries
        assert config.network_access is False  # Isolated


class TestJobSpec:
    """Tests for JobSpec."""

    def test_create_spec(self) -> None:
        """Create a basic job spec."""
        spec = JobSpec(
            name="test-job",
            namespace="kgents-ephemeral",
            image=SANDBOX_PYTHON,
            code="print('hello')",
            limits=ResourceLimits(),
            config=JobConfig(),
        )

        assert spec.name == "test-job"
        assert spec.namespace == "kgents-ephemeral"
        assert spec.code == "print('hello')"

    def test_to_k8s_manifest(self) -> None:
        """Convert spec to K8s manifest."""
        spec = JobSpec(
            name="test-job",
            namespace="kgents-ephemeral",
            image=SANDBOX_PYTHON,
            code="print('hello')",
            limits=ResourceLimits(),
            config=JobConfig(),
        )

        manifest = spec.to_k8s_manifest()

        # Top-level structure
        assert manifest["apiVersion"] == "batch/v1"
        assert manifest["kind"] == "Job"
        assert manifest["metadata"]["name"] == "test-job"
        assert manifest["metadata"]["namespace"] == "kgents-ephemeral"

        # Labels
        assert manifest["metadata"]["labels"]["kgents.io/agent"] == "q-gent"
        assert manifest["metadata"]["labels"]["kgents.io/job-type"] == "ephemeral"

        # TTL cleanup
        assert manifest["spec"]["ttlSecondsAfterFinished"] == 60

        # No retries
        assert manifest["spec"]["backoffLimit"] == 0

        # Container
        pod_spec = manifest["spec"]["template"]["spec"]
        container = pod_spec["containers"][0]

        assert container["name"] == "executor"
        assert container["image"] == "python:3.12-slim"
        assert container["command"] == ["python", "-c"]
        assert container["args"] == ["print('hello')"]

        # Security hardening
        sec = container["securityContext"]
        assert sec["runAsNonRoot"] is True
        assert sec["runAsUser"] == 1000
        assert sec["readOnlyRootFilesystem"] is True
        assert sec["allowPrivilegeEscalation"] is False

    def test_manifest_with_labels_and_annotations(self) -> None:
        """Custom labels and annotations are included."""
        spec = JobSpec(
            name="test-job",
            namespace="kgents-ephemeral",
            image=SANDBOX_PYTHON,
            code="x",
            limits=ResourceLimits(),
            config=JobConfig(),
            labels={"custom": "label"},
            annotations={"custom": "annotation"},
        )

        manifest = spec.to_k8s_manifest()

        assert manifest["metadata"]["labels"]["custom"] == "label"
        assert manifest["metadata"]["annotations"]["custom"] == "annotation"


class TestJobStatus:
    """Tests for JobStatus."""

    def test_phases(self) -> None:
        """All job phases are available."""
        assert JobPhase.PENDING.name == "PENDING"
        assert JobPhase.RUNNING.name == "RUNNING"
        assert JobPhase.SUCCEEDED.name == "SUCCEEDED"
        assert JobPhase.FAILED.name == "FAILED"
        assert JobPhase.UNKNOWN.name == "UNKNOWN"

    def test_status_fields(self) -> None:
        """Status has expected fields."""
        status = JobStatus(
            name="test-job",
            phase=JobPhase.SUCCEEDED,
            succeeded=1,
            message="Job completed",
        )

        assert status.name == "test-job"
        assert status.phase == JobPhase.SUCCEEDED
        assert status.succeeded == 1
        assert status.message == "Job completed"


class TestExecutionRequest:
    """Tests for ExecutionRequest."""

    def test_default_values(self) -> None:
        """Default request is safe."""
        req = ExecutionRequest(code="print('hi')")

        assert req.code == "print('hi')"
        assert req.language == "python"
        assert req.timeout_seconds == 30
        assert req.cpu_limit == "100m"
        assert req.memory_limit == "128Mi"
        assert req.network_access is False


class TestExecutionResult:
    """Tests for ExecutionResult."""

    def test_success_result(self) -> None:
        """Success result structure."""
        result = ExecutionResult(
            success=True,
            output="hello\n",
            duration_seconds=0.5,
            job_name="exec-abc123",
        )

        assert result.success is True
        assert result.output == "hello\n"
        assert result.error is None
        assert result.duration_seconds == 0.5

    def test_failure_result(self) -> None:
        """Failure result structure."""
        result = ExecutionResult(
            success=False,
            output="",
            error="Timeout exceeded",
            job_name="exec-abc123",
        )

        assert result.success is False
        assert result.error == "Timeout exceeded"


class TestJobBuilder:
    """Tests for JobBuilder."""

    def test_build_basic_job(self) -> None:
        """Build a basic job with defaults."""
        spec = JobBuilder("test").with_code("print('hi')").build()

        assert spec.name.startswith("test-")
        assert spec.namespace == "kgents-ephemeral"
        assert spec.code == "print('hi')"
        assert spec.image == SANDBOX_PYTHON

    def test_build_with_limits(self) -> None:
        """Build job with custom limits."""
        spec = (
            JobBuilder("test")
            .with_code("x")
            .with_limits(cpu="200m", memory="256Mi")
            .build()
        )

        assert spec.limits.cpu == "200m"
        assert spec.limits.memory == "256Mi"

    def test_build_with_timeout(self) -> None:
        """Build job with custom timeout."""
        spec = JobBuilder("test").with_code("x").with_timeout(60).build()

        assert spec.config.timeout_seconds == 60

    def test_build_with_ttl(self) -> None:
        """Build job with custom TTL."""
        spec = JobBuilder("test").with_code("x").with_ttl(120).build()

        assert spec.config.ttl_seconds_after_finished == 120

    def test_build_with_network(self) -> None:
        """Build job with network access."""
        spec = JobBuilder("test").with_code("x").with_network(True).build()

        assert spec.config.network_access is True

    def test_build_with_shell_image(self) -> None:
        """Build job with shell image."""
        spec = JobBuilder("test").with_code("echo hi").with_image(SANDBOX_SHELL).build()

        assert spec.image == SANDBOX_SHELL

    def test_build_with_labels(self) -> None:
        """Build job with custom labels."""
        spec = (
            JobBuilder("test")
            .with_code("x")
            .with_label("env", "test")
            .with_label("team", "platform")
            .build()
        )

        assert spec.labels["env"] == "test"
        assert spec.labels["team"] == "platform"

    def test_build_with_annotation(self) -> None:
        """Build job with custom annotation."""
        spec = (
            JobBuilder("test")
            .with_code("x")
            .with_annotation("description", "Test job")
            .build()
        )

        assert spec.annotations["description"] == "Test job"

    def test_code_hash_annotation(self) -> None:
        """Code hash annotation is added."""
        spec = JobBuilder("test").with_code("print('hello')").build()

        assert "kgents.io/code-hash" in spec.annotations
        assert len(spec.annotations["kgents.io/code-hash"]) == 16  # SHA256[:16]

    def test_build_without_code_raises(self) -> None:
        """Building without code raises ValueError."""
        with pytest.raises(ValueError, match="Code is required"):
            JobBuilder("test").build()

    def test_fluent_api(self) -> None:
        """All builder methods return self for chaining."""
        builder = JobBuilder("test")

        assert builder.with_name("x") is builder
        assert builder.with_namespace("x") is builder
        assert builder.with_code("x") is builder
        assert builder.with_image(SANDBOX_PYTHON) is builder
        assert builder.with_limits() is builder
        assert builder.with_timeout(10) is builder
        assert builder.with_ttl(10) is builder
        assert builder.with_network() is builder
        assert builder.with_label("k", "v") is builder
        assert builder.with_annotation("k", "v") is builder


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_python_job(self) -> None:
        """Create Python job with defaults."""
        spec = create_python_job("print('hello')")

        assert spec.name.startswith("py-")
        assert spec.image == SANDBOX_PYTHON
        assert spec.code == "print('hello')"

    def test_create_python_job_with_options(self) -> None:
        """Create Python job with custom options."""
        spec = create_python_job(
            "print('hello')",
            timeout=60,
            cpu="200m",
            memory="256Mi",
            network=True,
        )

        assert spec.config.timeout_seconds == 60
        assert spec.limits.cpu == "200m"
        assert spec.limits.memory == "256Mi"
        assert spec.config.network_access is True

    def test_create_shell_job(self) -> None:
        """Create shell job with defaults."""
        spec = create_shell_job("echo hello")

        assert spec.name.startswith("sh-")
        assert spec.image == SANDBOX_SHELL
        assert spec.code == "echo hello"

    def test_create_shell_job_with_options(self) -> None:
        """Create shell job with custom options."""
        spec = create_shell_job(
            "echo hello",
            timeout=10,
            cpu="50m",
        )

        assert spec.config.timeout_seconds == 10
        assert spec.limits.cpu == "50m"
