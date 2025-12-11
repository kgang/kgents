"""Tests for Agent Operator."""

from __future__ import annotations

import pytest

from ..operator import (
    AgentOperator,
    AgentPhase,
    AgentSpec,
    DeployMode,
    ReconcileResult,
    ValidationResult,
    create_operator,
)


class TestAgentSpec:
    """Tests for AgentSpec parsing and generation."""

    def test_from_crd_minimal(self) -> None:
        """Parse minimal CRD."""
        manifest = {
            "metadata": {"name": "test-agent", "namespace": "kgents-agents"},
            "spec": {"genus": "B"},
        }

        spec = AgentSpec.from_crd(manifest)

        assert spec.name == "test-agent"
        assert spec.namespace == "kgents-agents"
        assert spec.genus == "B"
        assert spec.image == "python:3.12-slim"
        assert spec.replicas == 1
        assert spec.cpu == "100m"
        assert spec.memory == "256Mi"
        assert spec.sidecar_enabled is True

    def test_from_crd_full(self) -> None:
        """Parse full CRD with all options."""
        manifest = {
            "metadata": {"name": "b-gent", "namespace": "kgents-agents"},
            "spec": {
                "genus": "B",
                "image": "custom/b-gent:v1",
                "replicas": 3,
                "resources": {"cpu": "500m", "memory": "1Gi"},
                "sidecar": {"enabled": False, "image": "custom/d-gent:v1"},
                "entrypoint": "agents.b.main",
                "config": {"token_budget": 10000},
                "networkPolicy": {
                    "allowEgress": True,
                    "allowedPeers": ["L", "F"],
                },
            },
        }

        spec = AgentSpec.from_crd(manifest)

        assert spec.genus == "B"
        assert spec.image == "custom/b-gent:v1"
        assert spec.replicas == 3
        assert spec.cpu == "500m"
        assert spec.memory == "1Gi"
        assert spec.sidecar_enabled is False
        assert spec.entrypoint == "agents.b.main"
        assert spec.config["token_budget"] == 10000
        assert spec.allow_egress is True
        assert spec.allowed_peers == ["L", "F"]

    def test_to_deployment_basic(self) -> None:
        """Generate basic Deployment."""
        spec = AgentSpec(
            name="b-gent",
            namespace="kgents-agents",
            genus="B",
        )

        deployment = spec.to_deployment()

        assert deployment["apiVersion"] == "apps/v1"
        assert deployment["kind"] == "Deployment"
        assert deployment["metadata"]["name"] == "b-gent"
        assert deployment["metadata"]["namespace"] == "kgents-agents"
        assert deployment["spec"]["replicas"] == 1

        # Check containers
        containers = deployment["spec"]["template"]["spec"]["containers"]
        assert len(containers) == 2  # logic + sidecar

        logic = containers[0]
        assert logic["name"] == "logic"
        assert logic["resources"]["limits"]["cpu"] == "100m"
        assert logic["resources"]["limits"]["memory"] == "256Mi"

        # Check security context
        assert logic["securityContext"]["runAsNonRoot"] is True
        assert logic["securityContext"]["allowPrivilegeEscalation"] is False

    def test_to_deployment_no_sidecar(self) -> None:
        """Generate Deployment without sidecar."""
        spec = AgentSpec(
            name="b-gent",
            namespace="kgents-agents",
            genus="B",
            sidecar_enabled=False,
        )

        deployment = spec.to_deployment()
        containers = deployment["spec"]["template"]["spec"]["containers"]

        assert len(containers) == 1
        assert containers[0]["name"] == "logic"

    def test_to_deployment_labels(self) -> None:
        """Verify labels are set correctly."""
        spec = AgentSpec(
            name="b-gent",
            namespace="kgents-agents",
            genus="B",
        )

        deployment = spec.to_deployment()

        labels = deployment["metadata"]["labels"]
        assert labels["app.kubernetes.io/name"] == "b-gent"
        assert labels["app.kubernetes.io/part-of"] == "kgents"
        assert labels["kgents.io/genus"] == "B"

    def test_to_service(self) -> None:
        """Generate Service."""
        spec = AgentSpec(
            name="b-gent",
            namespace="kgents-agents",
            genus="B",
        )

        service = spec.to_service()

        assert service["apiVersion"] == "v1"
        assert service["kind"] == "Service"
        assert service["metadata"]["name"] == "b-gent"
        assert service["spec"]["type"] == "ClusterIP"
        assert service["spec"]["ports"][0]["port"] == 8080

    def test_to_network_policy_default(self) -> None:
        """No NetworkPolicy needed by default."""
        spec = AgentSpec(
            name="b-gent",
            namespace="kgents-agents",
            genus="B",
        )

        policy = spec.to_network_policy()

        # Default is no egress, no peers - generates empty egress policy
        assert policy is not None
        assert policy["spec"]["policyTypes"] == ["Egress"]
        assert policy["spec"]["egress"] == []

    def test_to_network_policy_allow_egress(self) -> None:
        """NetworkPolicy with egress allowed."""
        spec = AgentSpec(
            name="b-gent",
            namespace="kgents-agents",
            genus="B",
            allow_egress=True,
        )

        policy = spec.to_network_policy()

        # Full egress returns None (no policy needed)
        assert policy is None

    def test_to_network_policy_peers(self) -> None:
        """NetworkPolicy with specific peers."""
        spec = AgentSpec(
            name="b-gent",
            namespace="kgents-agents",
            genus="B",
            allowed_peers=["L", "F"],
        )

        policy = spec.to_network_policy()

        assert policy is not None
        egress = policy["spec"]["egress"]
        assert len(egress) == 1
        # Should have podSelector for each peer
        assert len(egress[0]["to"]) == 2

    def test_halve_resource_millicores(self) -> None:
        """Halve CPU millicores."""
        spec = AgentSpec(
            name="test",
            namespace="test",
            genus="B",
        )

        assert spec._halve_resource("100m") == "50m"
        assert spec._halve_resource("200m") == "100m"
        assert spec._halve_resource("50m") == "25m"

    def test_halve_resource_memory(self) -> None:
        """Halve memory values."""
        spec = AgentSpec(
            name="test",
            namespace="test",
            genus="B",
        )

        assert spec._halve_resource("256Mi") == "128Mi"
        assert spec._halve_resource("1Gi") == "512Mi"

    def test_build_env(self) -> None:
        """Build environment variables."""
        spec = AgentSpec(
            name="b-gent",
            namespace="kgents-agents",
            genus="B",
            config={"token_budget": 10000, "debug": "true"},
        )

        env = spec._build_env()

        env_dict = {e["name"]: e["value"] for e in env}
        assert env_dict["KGENTS_GENUS"] == "B"
        assert env_dict["KGENTS_STATE_PATH"] == "/state"
        assert env_dict["KGENTS_TOKEN_BUDGET"] == "10000"
        assert env_dict["KGENTS_DEBUG"] == "true"


class TestAgentOperator:
    """Tests for AgentOperator."""

    def test_create_operator(self) -> None:
        """Create operator with defaults."""
        operator = create_operator()

        assert operator.namespace == "kgents-agents"

    def test_create_operator_custom_namespace(self) -> None:
        """Create operator with custom namespace."""
        operator = create_operator(namespace="custom")

        assert operator.namespace == "custom"

    def test_progress_callback(self) -> None:
        """Progress callback is called."""
        messages: list[str] = []
        operator = create_operator(on_progress=messages.append)

        # Just verify it was set correctly
        operator._on_progress("test message")
        assert messages == ["test message"]


class TestAgentPhase:
    """Tests for AgentPhase enum."""

    def test_phases(self) -> None:
        """Verify phase values."""
        assert AgentPhase.PENDING.value == "Pending"
        assert AgentPhase.RUNNING.value == "Running"
        assert AgentPhase.FAILED.value == "Failed"
        assert AgentPhase.TERMINATING.value == "Terminating"


class TestReconcileResult:
    """Tests for ReconcileResult."""

    def test_success_result(self) -> None:
        """Successful reconcile result."""
        result = ReconcileResult(
            success=True,
            message="Reconciled successfully",
            phase=AgentPhase.RUNNING,
            created=["deployment/b-gent"],
        )

        assert result.success is True
        assert result.phase == AgentPhase.RUNNING
        assert "deployment/b-gent" in result.created

    def test_failure_result(self) -> None:
        """Failed reconcile result."""
        result = ReconcileResult(
            success=False,
            message="Failed to create deployment",
            phase=AgentPhase.FAILED,
        )

        assert result.success is False
        assert result.phase == AgentPhase.FAILED
        assert result.created == []
        assert result.updated == []
        assert result.deleted == []
