"""
Tests for AgentServer Operator.

Phase 4 tests covering:
1. AgentServerSpec parsing and validation
2. Manifest generation (Deployment, Service, ConfigMap)
3. Mock registry operations
4. Reconciliation simulation
"""

from __future__ import annotations

from typing import Any

import pytest

from ..agentserver_operator import (
    AgentServerPhase,
    AgentServerSpec,
    MockAgentServer,
    MockAgentServerRegistry,
    get_mock_registry,
    parse_agentserver_spec,
    reset_mock_registry,
)

# === Test AgentServerSpec Parsing ===


class TestAgentServerSpecParsing:
    """Test parsing of AgentServer CRD spec."""

    def test_parse_minimal_spec(self) -> None:
        """Parse minimal spec with defaults."""
        spec: dict[str, Any] = {}
        meta = {"name": "test-server", "namespace": "kgents-system"}

        parsed = parse_agentserver_spec(spec, meta)

        assert parsed.name == "test-server"
        assert parsed.namespace == "kgents-system"
        assert parsed.gateway_replicas == 1
        assert parsed.gateway_port == 8080
        assert parsed.auto_discover is True
        assert parsed.semaphores_enabled is True

    def test_parse_full_spec(self) -> None:
        """Parse fully specified spec."""
        spec = {
            "gateway": {
                "image": "custom/terrarium:v1",
                "replicas": 3,
                "port": 9000,
                "resources": {
                    "limits": {
                        "cpu": "1000m",
                        "memory": "1Gi",
                    }
                },
            },
            "mirror": {
                "maxHistory": 500,
                "broadcastTimeout": "200ms",
                "bufferSize": 200,
            },
            "agents": {
                "autoDiscover": True,
                "genusFilter": ["L", "M", "U"],
            },
            "widgets": {
                "enabled": True,
                "densityField": {
                    "enabled": True,
                },
            },
            "semaphores": {
                "enabled": True,
                "purgatoryEndpoint": True,
            },
            "auth": {
                "observeRequiresAuth": True,
                "perturbRequiresAuth": True,
            },
            "service": {
                "type": "LoadBalancer",
                "annotations": {"external-dns": "true"},
            },
            "metrics": {
                "enabled": True,
                "port": 9191,
            },
        }
        meta = {"name": "prod-server", "namespace": "production"}

        parsed = parse_agentserver_spec(spec, meta)

        assert parsed.name == "prod-server"
        assert parsed.namespace == "production"
        assert parsed.gateway_image == "custom/terrarium:v1"
        assert parsed.gateway_replicas == 3
        assert parsed.gateway_port == 9000
        assert parsed.gateway_cpu_limit == "1000m"
        assert parsed.gateway_memory_limit == "1Gi"
        assert parsed.mirror_max_history == 500
        assert parsed.mirror_broadcast_timeout == "200ms"
        assert parsed.genus_filter == ["L", "M", "U"]
        assert parsed.observe_requires_auth is True
        assert parsed.service_type == "LoadBalancer"
        assert parsed.service_annotations == {"external-dns": "true"}
        assert parsed.metrics_port == 9191


# === Test Manifest Generation ===


class TestManifestGeneration:
    """Test K8s manifest generation."""

    def test_deployment_manifest(self) -> None:
        """Generate Deployment manifest."""
        spec = AgentServerSpec(
            name="test",
            namespace="kgents-system",
            gateway_replicas=2,
            gateway_port=8080,
        )

        deployment = spec.to_deployment()

        assert deployment["kind"] == "Deployment"
        assert deployment["metadata"]["name"] == "test-terrarium"
        assert deployment["metadata"]["namespace"] == "kgents-system"
        assert deployment["spec"]["replicas"] == 2

        container = deployment["spec"]["template"]["spec"]["containers"][0]
        assert container["name"] == "terrarium"
        assert container["ports"][0]["containerPort"] == 8080

    def test_service_manifest(self) -> None:
        """Generate Service manifest."""
        spec = AgentServerSpec(
            name="test",
            namespace="kgents-system",
            service_type="LoadBalancer",
            gateway_port=8080,
        )

        service = spec.to_service()

        assert service["kind"] == "Service"
        assert service["metadata"]["name"] == "test-terrarium"
        assert service["spec"]["type"] == "LoadBalancer"
        assert service["spec"]["ports"][0]["targetPort"] == 8080

    def test_configmap_manifest(self) -> None:
        """Generate ConfigMap manifest."""
        spec = AgentServerSpec(
            name="test",
            namespace="kgents-system",
            mirror_max_history=200,
            genus_filter=["L", "M"],
        )

        configmap = spec.to_configmap()

        assert configmap["kind"] == "ConfigMap"
        assert configmap["metadata"]["name"] == "test-terrarium-config"
        assert configmap["data"]["MIRROR_MAX_HISTORY"] == "200"
        assert configmap["data"]["GENUS_FILTER"] == "L,M"

    def test_service_account_manifest(self) -> None:
        """Generate ServiceAccount manifest."""
        spec = AgentServerSpec(
            name="test",
            namespace="kgents-system",
        )

        sa = spec.to_service_account()

        assert sa["kind"] == "ServiceAccount"
        assert sa["metadata"]["name"] == "test-terrarium"

    def test_cluster_role_binding_manifest(self) -> None:
        """Generate ClusterRoleBinding manifest."""
        spec = AgentServerSpec(
            name="test",
            namespace="kgents-system",
        )

        crb = spec.to_cluster_role_binding()

        assert crb["kind"] == "ClusterRoleBinding"
        assert crb["metadata"]["name"] == "kgents-system-test-terrarium"
        assert crb["subjects"][0]["name"] == "test-terrarium"


# === Test Environment Variables ===


class TestEnvironmentVariables:
    """Test environment variable generation."""

    def test_env_vars_include_semaphore_settings(self) -> None:
        """Environment includes semaphore settings."""
        spec = AgentServerSpec(
            name="test",
            namespace="kgents-system",
            semaphores_enabled=True,
            purgatory_endpoint=True,
        )

        deployment = spec.to_deployment()
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        env_dict = {e["name"]: e["value"] for e in container["env"]}

        assert env_dict["TERRARIUM_SEMAPHORES_ENABLED"] == "true"
        assert env_dict["TERRARIUM_PURGATORY_ENDPOINT"] == "true"

    def test_env_vars_include_auth_settings(self) -> None:
        """Environment includes auth settings."""
        spec = AgentServerSpec(
            name="test",
            namespace="kgents-system",
            observe_requires_auth=True,
            perturb_requires_auth=True,
        )

        deployment = spec.to_deployment()
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        env_dict = {e["name"]: e["value"] for e in container["env"]}

        assert env_dict["TERRARIUM_OBSERVE_AUTH"] == "true"
        assert env_dict["TERRARIUM_PERTURB_AUTH"] == "true"


# === Test MockAgentServer ===


class TestMockAgentServer:
    """Test MockAgentServer for testing without K8s."""

    def test_create_mock_server(self) -> None:
        """Create mock AgentServer."""
        server = MockAgentServer(name="test", namespace="kgents-system")

        assert server.name == "test"
        assert server.phase == AgentServerPhase.PENDING
        assert server.ready_replicas == 0

    def test_reconcile_mock_server(self) -> None:
        """Reconcile mock AgentServer."""
        server = MockAgentServer(name="test", namespace="kgents-system")

        result = server.reconcile()

        assert result["success"] is True
        assert server.phase == AgentServerPhase.RUNNING
        assert server.ready_replicas == server.replicas
        assert "deployment/test-terrarium" in result["resources"]

    def test_scale_mock_server(self) -> None:
        """Scale mock AgentServer."""
        server = MockAgentServer(name="test", replicas=1)
        server.reconcile()

        server.scale(3)

        assert server.replicas == 3
        assert server.ready_replicas == 3

    def test_register_agent(self) -> None:
        """Register agent with mock server."""
        server = MockAgentServer(name="test")
        server.reconcile()

        server.register_agent()
        server.register_agent()

        assert server.registered_agents == 2

    def test_add_observer(self) -> None:
        """Add observer to mock server."""
        server = MockAgentServer(name="test")
        server.reconcile()

        server.add_observer()

        assert server.active_observers == 1

    def test_semaphore_lifecycle(self) -> None:
        """Test semaphore add/resolve."""
        server = MockAgentServer(name="test")
        server.reconcile()

        server.add_semaphore()
        server.add_semaphore()
        assert server.pending_semaphores == 2

        server.resolve_semaphore()
        assert server.pending_semaphores == 1


# === Test MockAgentServerRegistry ===


class TestMockAgentServerRegistry:
    """Test MockAgentServerRegistry."""

    def setup_method(self) -> None:
        """Reset registry before each test."""
        reset_mock_registry()

    def test_create_server(self) -> None:
        """Create server via registry."""
        registry = MockAgentServerRegistry()

        server = registry.create("test-server")

        assert server.name == "test-server"
        assert server.phase == AgentServerPhase.RUNNING

    def test_get_server(self) -> None:
        """Get server by name."""
        registry = MockAgentServerRegistry()
        registry.create("test-server", namespace="test-ns")

        server = registry.get("test-server", namespace="test-ns")

        assert server is not None
        assert server.name == "test-server"

    def test_get_nonexistent_server(self) -> None:
        """Get nonexistent server returns None."""
        registry = MockAgentServerRegistry()

        server = registry.get("nonexistent")

        assert server is None

    def test_list_servers(self) -> None:
        """List all servers."""
        registry = MockAgentServerRegistry()
        registry.create("server-1")
        registry.create("server-2")

        servers = registry.list()

        assert len(servers) == 2

    def test_delete_server(self) -> None:
        """Delete server."""
        registry = MockAgentServerRegistry()
        registry.create("test-server")

        deleted = registry.delete("test-server")

        assert deleted is True
        assert registry.get("test-server") is None

    def test_delete_nonexistent_server(self) -> None:
        """Delete nonexistent server returns False."""
        registry = MockAgentServerRegistry()

        deleted = registry.delete("nonexistent")

        assert deleted is False


# === Test Global Registry ===


class TestGlobalRegistry:
    """Test global mock registry."""

    def setup_method(self) -> None:
        """Reset registry before each test."""
        reset_mock_registry()

    def test_get_creates_registry(self) -> None:
        """get_mock_registry creates registry if needed."""
        registry = get_mock_registry()

        assert registry is not None
        assert isinstance(registry, MockAgentServerRegistry)

    def test_get_returns_same_registry(self) -> None:
        """get_mock_registry returns same instance."""
        registry1 = get_mock_registry()
        registry2 = get_mock_registry()

        assert registry1 is registry2

    def test_reset_clears_registry(self) -> None:
        """reset_mock_registry clears global registry."""
        registry1 = get_mock_registry()
        registry1.create("test")

        reset_mock_registry()
        registry2 = get_mock_registry()

        assert registry2.get("test") is None


# === Test Phase 5 Integration ===


class TestPhase5Integration:
    """Test Phase 5 semaphore integration in AgentServer."""

    def test_semaphore_config_parsing(self) -> None:
        """Semaphore config is parsed correctly."""
        spec = {
            "semaphores": {
                "enabled": True,
                "purgatoryEndpoint": True,
                "webhookNotifications": {
                    "enabled": True,
                    "url": "https://alerts.example.com",
                    "events": ["ejected", "resolved"],
                },
            }
        }
        meta = {"name": "test", "namespace": "kgents-system"}

        parsed = parse_agentserver_spec(spec, meta)

        assert parsed.semaphores_enabled is True
        assert parsed.purgatory_endpoint is True

    def test_semaphore_disabled(self) -> None:
        """Semaphore can be disabled."""
        spec = {
            "semaphores": {
                "enabled": False,
                "purgatoryEndpoint": False,
            }
        }
        meta = {"name": "test", "namespace": "kgents-system"}

        parsed = parse_agentserver_spec(spec, meta)

        assert parsed.semaphores_enabled is False
        assert parsed.purgatory_endpoint is False

        deployment = parsed.to_deployment()
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        env_dict = {e["name"]: e["value"] for e in container["env"]}

        assert env_dict["TERRARIUM_SEMAPHORES_ENABLED"] == "false"
        assert env_dict["TERRARIUM_PURGATORY_ENDPOINT"] == "false"


# === Test Exit Criteria: kubectl apply -f agentserver.yaml ===


class TestExitCriteria:
    """Test that exit criteria is met: kubectl apply deploys working terrarium."""

    def test_minimal_yaml_produces_valid_manifests(self) -> None:
        """Minimal YAML produces all required manifests."""
        # Simulates: kubectl apply -f agentserver.yaml
        # with minimal content: apiVersion, kind, metadata.name
        spec: dict[str, Any] = {}
        meta = {"name": "my-terrarium", "namespace": "default"}

        parsed = parse_agentserver_spec(spec, meta)

        # All manifests should be generated
        deployment = parsed.to_deployment()
        service = parsed.to_service()
        configmap = parsed.to_configmap()
        sa = parsed.to_service_account()

        # Validate structure
        assert deployment["kind"] == "Deployment"
        assert deployment["spec"]["replicas"] >= 1
        assert len(deployment["spec"]["template"]["spec"]["containers"]) >= 1

        assert service["kind"] == "Service"
        assert len(service["spec"]["ports"]) >= 1

        assert configmap["kind"] == "ConfigMap"
        assert len(configmap["data"]) >= 1

        assert sa["kind"] == "ServiceAccount"

    def test_mock_deployment_succeeds(self) -> None:
        """Mock deployment completes successfully."""
        # Simulates reconciliation flow
        registry = MockAgentServerRegistry()

        server = registry.create("my-terrarium", namespace="default")

        assert server.phase == AgentServerPhase.RUNNING
        assert server.ready_replicas >= 1
        assert registry.get("my-terrarium", "default") is server
