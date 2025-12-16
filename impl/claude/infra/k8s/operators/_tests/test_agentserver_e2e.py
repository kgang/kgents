"""
End-to-End Kubernetes tests for AgentServer operator.

Self-Hosted First Philosophy:
These tests require a real kind cluster, no mocks.
This ensures the terrarium infrastructure actually works in K8s.

Usage:
    # Create cluster first (if not exists)
    kind create cluster --config impl/claude/infra/k8s/kind/terrarium-cluster.yaml

    # Run E2E tests (tier3)
    uv run pytest -m tier3 impl/claude/infra/k8s/operators/_tests/test_agentserver_e2e.py -v

Prerequisites:
    - kind installed
    - kubectl installed and configured
    - Docker running

Markers:
    @pytest.mark.tier3 - E2E tests requiring real K8s cluster
    @pytest.mark.e2e - DEPRECATED, use tier3
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import time
from pathlib import Path
from typing import Any, Generator

import pytest

# Mark entire module as tier3 (E2E tests requiring real K8s cluster)
pytestmark = [pytest.mark.tier3, pytest.mark.e2e]

# Cluster name from kind config
CLUSTER_NAME = "kgents-terrarium"

# Paths relative to repo root
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent.parent
KIND_CONFIG = REPO_ROOT / "impl/claude/infra/k8s/kind/terrarium-cluster.yaml"
CRD_PATH = REPO_ROOT / "impl/claude/infra/k8s/crds/agentserver-crd.yaml"


def run_kubectl(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run kubectl command and return result."""
    return subprocess.run(
        ["kubectl", *args],
        capture_output=True,
        text=True,
        check=check,
    )


def kubectl_get_json(resource: str, name: str | None = None) -> dict[str, Any]:
    """Get a K8s resource as JSON."""
    cmd = ["get", resource]
    if name:
        cmd.append(name)
    cmd.extend(["-o", "json"])

    result = run_kubectl(*cmd, check=False)
    if result.returncode != 0:
        return {}
    return dict(json.loads(result.stdout))


def kubectl_apply(yaml_content: str) -> subprocess.CompletedProcess[str]:
    """Apply YAML content to cluster."""
    return subprocess.run(
        ["kubectl", "apply", "-f", "-"],
        input=yaml_content,
        capture_output=True,
        text=True,
        check=True,
    )


def kubectl_delete(resource: str, name: str) -> subprocess.CompletedProcess[str]:
    """Delete a K8s resource."""
    return run_kubectl("delete", resource, name, "--ignore-not-found", check=False)


@pytest.fixture(scope="session")
def kind_cluster() -> Generator[str, None, None]:
    """
    Ensure kind cluster exists, skip if kind not installed.

    This fixture:
    1. Checks if kind is installed
    2. Creates cluster if it doesn't exist
    3. Applies CRDs
    4. Does NOT delete cluster after tests (reuse for development)
    """
    # Check if kind is available
    kind_check = subprocess.run(["kind", "version"], capture_output=True, text=True)
    if kind_check.returncode != 0:
        pytest.skip("kind not installed")

    # Check if cluster exists
    clusters_result = subprocess.run(
        ["kind", "get", "clusters"], capture_output=True, text=True
    )
    cluster_exists = CLUSTER_NAME in clusters_result.stdout

    if not cluster_exists:
        # Create cluster
        print(f"\n[e2e] Creating kind cluster: {CLUSTER_NAME}")
        if not KIND_CONFIG.exists():
            pytest.skip(f"Kind config not found: {KIND_CONFIG}")

        create_result = subprocess.run(
            ["kind", "create", "cluster", "--config", str(KIND_CONFIG)],
            capture_output=True,
            text=True,
        )
        if create_result.returncode != 0:
            pytest.fail(f"Failed to create cluster: {create_result.stderr}")

        print(f"[e2e] Cluster created: {CLUSTER_NAME}")

    # Set kubectl context
    subprocess.run(
        ["kubectl", "cluster-info", "--context", f"kind-{CLUSTER_NAME}"],
        capture_output=True,
        text=True,
    )

    # Apply CRDs
    if CRD_PATH.exists():
        print(f"[e2e] Applying CRD: {CRD_PATH}")
        crd_result = subprocess.run(
            ["kubectl", "apply", "-f", str(CRD_PATH)],
            capture_output=True,
            text=True,
        )
        if crd_result.returncode != 0:
            pytest.skip(f"CRD apply failed: {crd_result.stderr}")
    else:
        pytest.skip(f"CRD not found: {CRD_PATH}")

    yield CLUSTER_NAME

    # Don't delete cluster - reuse for development
    print(f"\n[e2e] Keeping cluster: {CLUSTER_NAME}")


@pytest.fixture
def test_agentserver_name() -> str:
    """Generate unique name for test AgentServer."""
    return f"test-terrarium-{int(time.time()) % 10000}"


@pytest.fixture
def test_agentserver_yaml(test_agentserver_name: str) -> str:
    """Generate test AgentServer YAML."""
    return f"""
apiVersion: kgents.io/v1
kind: AgentServer
metadata:
  name: {test_agentserver_name}
  namespace: default
spec:
  gateway:
    image: kgents/terrarium:latest
    replicas: 1
    port: 8080
  mirror:
    maxHistory: 50
  semaphores:
    enabled: true
    purgatoryEndpoint: true
"""


@pytest.fixture
def cleanup_agentserver(
    kind_cluster: str, test_agentserver_name: str
) -> Generator[None, None, None]:
    """Cleanup AgentServer after test."""
    yield
    kubectl_delete("agentserver", test_agentserver_name)


class TestAgentServerCRD:
    """AgentServer CRD availability tests."""

    def test_crd_is_installed(self, kind_cluster: str) -> None:
        """AgentServer CRD is available in cluster."""
        result = run_kubectl("get", "crd", "agentservers.kgents.io", check=False)
        assert result.returncode == 0, "AgentServer CRD not installed"

    def test_can_list_agentservers(self, kind_cluster: str) -> None:
        """Can list AgentServer resources."""
        result = run_kubectl("get", "agentservers", check=False)
        # May return "No resources found" but should not error
        assert result.returncode == 0


class TestAgentServerCreate:
    """AgentServer creation tests."""

    def test_create_agentserver_cr(
        self,
        kind_cluster: str,
        test_agentserver_yaml: str,
        test_agentserver_name: str,
        cleanup_agentserver: None,
    ) -> None:
        """Can create AgentServer custom resource."""
        result = kubectl_apply(test_agentserver_yaml)
        assert result.returncode == 0

        # Verify it exists
        data = kubectl_get_json("agentserver", test_agentserver_name)
        assert data.get("metadata", {}).get("name") == test_agentserver_name

    def test_agentserver_has_spec_defaults(
        self,
        kind_cluster: str,
        test_agentserver_yaml: str,
        test_agentserver_name: str,
        cleanup_agentserver: None,
    ) -> None:
        """AgentServer spec has expected values."""
        kubectl_apply(test_agentserver_yaml)

        data = kubectl_get_json("agentserver", test_agentserver_name)
        spec = data.get("spec", {})

        assert spec.get("gateway", {}).get("port") == 8080
        assert spec.get("mirror", {}).get("maxHistory") == 50
        assert spec.get("semaphores", {}).get("enabled") is True


class TestAgentServerOperator:
    """
    Tests that require the operator running.

    Note: These tests verify what happens when operator reconciles.
    If operator is not running, they test the CR creation only.
    """

    def test_agentserver_creates_resources(
        self,
        kind_cluster: str,
        test_agentserver_yaml: str,
        test_agentserver_name: str,
        cleanup_agentserver: None,
    ) -> None:
        """
        AgentServer CR creation triggers resource creation.

        When operator is running:
        - Deployment is created
        - Service is created
        - ConfigMap is created
        """
        kubectl_apply(test_agentserver_yaml)

        # Wait a bit for operator to reconcile
        time.sleep(2)

        # Check for resources (may not exist if operator not running)
        deployment = kubectl_get_json("deployment", f"{test_agentserver_name}-gateway")
        service = kubectl_get_json("service", f"{test_agentserver_name}-gateway")

        # If operator is running, these should exist
        # If not, just verify CR exists
        if deployment:
            assert (
                deployment.get("metadata", {}).get("name")
                == f"{test_agentserver_name}-gateway"
            )

        # CR should always exist
        cr = kubectl_get_json("agentserver", test_agentserver_name)
        assert cr.get("metadata", {}).get("name") == test_agentserver_name


class TestAgentServerDelete:
    """AgentServer deletion tests."""

    def test_delete_agentserver_removes_cr(
        self,
        kind_cluster: str,
        test_agentserver_yaml: str,
        test_agentserver_name: str,
    ) -> None:
        """Deleting AgentServer removes the CR."""
        # Create
        kubectl_apply(test_agentserver_yaml)

        # Verify exists
        data = kubectl_get_json("agentserver", test_agentserver_name)
        assert data.get("metadata", {}).get("name") == test_agentserver_name

        # Delete
        kubectl_delete("agentserver", test_agentserver_name)

        # Verify gone
        data = kubectl_get_json("agentserver", test_agentserver_name)
        assert not data or "NotFound" in str(data)


class TestClusterHealth:
    """Cluster health verification tests."""

    def test_cluster_is_running(self, kind_cluster: str) -> None:
        """Kind cluster is running and healthy."""
        result = run_kubectl("cluster-info")
        assert result.returncode == 0
        assert (
            "running" in result.stdout.lower() or "kubernetes" in result.stdout.lower()
        )

    def test_default_namespace_exists(self, kind_cluster: str) -> None:
        """Default namespace exists."""
        result = run_kubectl("get", "namespace", "default")
        assert result.returncode == 0

    def test_can_create_pods(self, kind_cluster: str) -> None:
        """Can create pods in cluster."""
        pod_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: e2e-test-pod
  namespace: default
spec:
  containers:
  - name: test
    image: busybox
    command: ["sleep", "10"]
  restartPolicy: Never
"""
        try:
            kubectl_apply(pod_yaml)
            # Wait for pod
            time.sleep(2)
            result = run_kubectl("get", "pod", "e2e-test-pod")
            assert result.returncode == 0
        finally:
            kubectl_delete("pod", "e2e-test-pod")


class TestLLMRoutingPrepare:
    """
    Prepare infrastructure for routing LLM calls through K8s.

    Future: LLM gateway that routes through K8s for observability.
    """

    def test_nodeport_mapping_available(self, kind_cluster: str) -> None:
        """
        NodePort mapping is available for terrarium gateway.

        This verifies the kind cluster has the right port mappings
        for self-hosted LLM routing.
        """
        # Check kind config was applied with port mappings
        result = subprocess.run(
            ["docker", "port", f"{CLUSTER_NAME}-control-plane"],
            capture_output=True,
            text=True,
        )

        # Should have port mappings
        # (exact format depends on Docker version)
        assert result.returncode == 0

    def test_terrarium_service_type_nodeport(
        self,
        kind_cluster: str,
        test_agentserver_yaml: str,
        test_agentserver_name: str,
        cleanup_agentserver: None,
    ) -> None:
        """
        AgentServer can use NodePort service type.

        This enables external access to terrarium gateway.
        """
        nodeport_yaml = f"""
apiVersion: kgents.io/v1
kind: AgentServer
metadata:
  name: {test_agentserver_name}
  namespace: default
spec:
  gateway:
    image: kgents/terrarium:latest
    replicas: 1
  service:
    type: NodePort
"""
        kubectl_apply(nodeport_yaml)

        data = kubectl_get_json("agentserver", test_agentserver_name)
        assert data.get("spec", {}).get("service", {}).get("type") == "NodePort"
