"""Tests for Agent Operator reconciliation logic.

These tests verify the agent operator works correctly
without requiring a real K8s cluster.
"""

from __future__ import annotations

from typing import Any

import pytest
from infra.k8s.operator import (
    AgentPhase,
    AgentSpec,
    DeployMode,
)
from infra.k8s.operators.agent_operator import (
    MockAgent,
    MockAgentRegistry,
    generate_memory_cr,
    get_mock_registry,
    parse_agent_spec,
    reset_mock_registry,
)


class TestParseAgentSpec:
    """Test parsing CRD spec into AgentSpec."""

    def test_minimal_spec(self) -> None:
        """Parse minimal spec with only required fields."""
        spec = {"genus": "L"}
        meta = {"name": "l-gent", "namespace": "kgents-agents"}

        result = parse_agent_spec(spec, meta)

        assert result.name == "l-gent"
        assert result.namespace == "kgents-agents"
        assert result.genus == "L"
        assert result.deploy_mode == DeployMode.PLACEHOLDER  # Safe default
        assert result.image == "python:3.12-slim"
        assert result.replicas == 1

    def test_full_spec(self) -> None:
        """Parse spec with all fields."""
        spec = {
            "genus": "B",
            "image": "kgents/b-gent:latest",
            "replicas": 2,
            "entrypoint": "agents.b.main",
            "deployMode": "FULL",
            "resources": {
                "limits": {"cpu": "1000m", "memory": "1Gi"},
                "requests": {"cpu": "200m", "memory": "512Mi"},
            },
            "symbiont": {
                "memory": {
                    "enabled": True,
                    "type": "VECTOR",
                    "size": "512Mi",
                    "retentionPolicy": "RETAIN",
                }
            },
            "networkPolicy": {
                "allowedPeers": ["L", "F"],
                "allowEgress": False,
            },
            "config": {"debug": True, "log_level": "DEBUG"},
        }
        meta = {"name": "b-gent", "namespace": "kgents-system"}

        result = parse_agent_spec(spec, meta)

        assert result.name == "b-gent"
        assert result.namespace == "kgents-system"
        assert result.genus == "B"
        assert result.image == "kgents/b-gent:latest"
        assert result.replicas == 2
        assert result.entrypoint == "agents.b.main"
        assert result.deploy_mode == DeployMode.FULL
        assert result.cpu == "1000m"
        assert result.memory == "1Gi"
        assert result.allowed_peers == ["L", "F"]
        assert result.allow_egress is False
        assert result.config == {"debug": True, "log_level": "DEBUG"}

    def test_deploy_mode_mapping(self) -> None:
        """Test all deploy mode strings map correctly."""
        meta = {"name": "test", "namespace": "default"}

        for mode_str, expected in [
            ("FULL", DeployMode.FULL),
            ("PLACEHOLDER", DeployMode.PLACEHOLDER),
            ("DRY_RUN", DeployMode.DRY_RUN),
        ]:
            spec = {"genus": "X", "deployMode": mode_str}
            result = parse_agent_spec(spec, meta)
            assert result.deploy_mode == expected

    def test_invalid_deploy_mode_defaults_to_placeholder(self) -> None:
        """Invalid deploy mode defaults to PLACEHOLDER for safety."""
        spec = {"genus": "X", "deployMode": "INVALID"}
        meta = {"name": "test", "namespace": "default"}

        result = parse_agent_spec(spec, meta)
        assert result.deploy_mode == DeployMode.PLACEHOLDER


class TestGenerateMemoryCR:
    """Test Memory CR generation."""

    def test_basic_memory_cr(self) -> None:
        """Generate basic Memory CR."""
        result = generate_memory_cr(
            agent_name="l-gent",
            namespace="kgents-agents",
            genus="L",
            memory_config={"type": "BICAMERAL", "size": "256Mi"},
            owner_uid="test-uid-123",
        )

        assert result["apiVersion"] == "kgents.io/v1"
        assert result["kind"] == "Memory"
        assert result["metadata"]["name"] == "l-gent-memory"
        assert result["metadata"]["namespace"] == "kgents-agents"
        assert result["metadata"]["labels"]["kgents.io/genus"] == "L"
        assert result["metadata"]["labels"]["kgents.io/owner"] == "l-gent"
        assert result["spec"]["owner"] == "L-gent"
        assert result["spec"]["type"] == "BICAMERAL"
        assert result["spec"]["size"] == "256Mi"

    def test_owner_reference(self) -> None:
        """Memory CR has correct owner reference."""
        result = generate_memory_cr(
            agent_name="b-gent",
            namespace="default",
            genus="B",
            memory_config={"retentionPolicy": "DELETE"},
            owner_uid="uid-456",
        )

        owner_refs = result["metadata"]["ownerReferences"]
        assert len(owner_refs) == 1
        assert owner_refs[0]["kind"] == "Agent"
        assert owner_refs[0]["name"] == "b-gent"
        assert owner_refs[0]["uid"] == "uid-456"
        assert owner_refs[0]["controller"] is True
        # DELETE policy means blockOwnerDeletion=True
        assert owner_refs[0]["blockOwnerDeletion"] is True

    def test_compost_retention_no_block(self) -> None:
        """COMPOST retention doesn't block owner deletion."""
        result = generate_memory_cr(
            agent_name="test",
            namespace="default",
            genus="X",
            memory_config={"retentionPolicy": "COMPOST"},
            owner_uid="uid-789",
        )

        owner_refs = result["metadata"]["ownerReferences"]
        # COMPOST doesn't block - memory can be orphaned
        assert owner_refs[0]["blockOwnerDeletion"] is False


class TestMockAgent:
    """Test the mock agent implementation."""

    def test_create_agent(self) -> None:
        """Can create a mock agent."""
        agent = MockAgent(
            name="l-gent",
            genus="L",
            namespace="kgents-agents",
            replicas=2,
        )

        assert agent.name == "l-gent"
        assert agent.genus == "L"
        assert agent.namespace == "kgents-agents"
        assert agent.replicas == 2
        assert agent.phase == AgentPhase.PENDING
        assert agent.cognitive_health == "UNKNOWN"

    def test_reconcile_creates_resources(self) -> None:
        """Reconcile creates deployment, service, and memory."""
        agent = MockAgent(name="b-gent", genus="B")
        result = agent.reconcile()

        assert result.success is True
        assert agent.phase == AgentPhase.RUNNING
        assert agent.deployment == "b-gent"
        assert agent.service == "b-gent"
        assert agent.memory_cr == "b-gent-memory"
        assert agent.cognitive_health == "HEALTHY"
        assert agent.ready_replicas == 1

    def test_dry_run_no_resources(self) -> None:
        """DRY_RUN mode doesn't create resources."""
        agent = MockAgent(
            name="test-gent",
            genus="X",
            deploy_mode=DeployMode.DRY_RUN,
        )
        result = agent.reconcile()

        assert result.success is True
        assert result.phase == AgentPhase.PENDING
        assert agent.deployment is None
        assert agent.memory_cr is None

    def test_scale_updates_replicas(self) -> None:
        """Can scale agent replicas."""
        agent = MockAgent(name="test", genus="X")
        agent.reconcile()

        agent.scale(3)

        assert agent.replicas == 3
        assert agent.ready_replicas == 3

    def test_delete_sets_terminating(self) -> None:
        """Delete marks agent as terminating."""
        agent = MockAgent(name="test", genus="X")
        agent.reconcile()

        agent.delete()

        assert agent.phase == AgentPhase.TERMINATING


class TestMockAgentRegistry:
    """Test the mock agent registry."""

    def test_create_and_list(self) -> None:
        """Can create and list agents."""
        registry = MockAgentRegistry()
        registry.create("l-gent", "L")
        registry.create("b-gent", "B")

        agents = registry.list()
        assert len(agents) == 2
        assert {a.name for a in agents} == {"l-gent", "b-gent"}

    def test_get_by_name(self) -> None:
        """Can get agent by name."""
        registry = MockAgentRegistry()
        registry.create("l-gent", "L")

        agent = registry.get("l-gent")
        assert agent is not None
        assert agent.genus == "L"

        missing = registry.get("nonexistent")
        assert missing is None

    def test_delete_removes_agent(self) -> None:
        """Delete removes agent from registry."""
        registry = MockAgentRegistry()
        registry.create("l-gent", "L")
        registry.create("b-gent", "B")

        result = registry.delete("l-gent")

        assert result is True
        assert len(registry.list()) == 1
        assert registry.get("l-gent") is None

    def test_delete_nonexistent_returns_false(self) -> None:
        """Delete returns False for nonexistent agent."""
        registry = MockAgentRegistry()
        result = registry.delete("nonexistent")
        assert result is False

    def test_scale_agent(self) -> None:
        """Can scale agent via registry."""
        registry = MockAgentRegistry()
        registry.create("l-gent", "L")

        result = registry.scale("l-gent", 5)

        assert result is True
        agent = registry.get("l-gent")
        assert agent is not None
        assert agent.replicas == 5


class TestGlobalMockRegistry:
    """Test the global mock registry singleton."""

    def setup_method(self) -> None:
        """Reset the global registry before each test."""
        reset_mock_registry()

    def test_get_creates_singleton(self) -> None:
        """get_mock_registry creates a singleton."""
        registry1 = get_mock_registry()
        registry2 = get_mock_registry()
        assert registry1 is registry2

    def test_reset_clears_registry(self) -> None:
        """reset_mock_registry clears the singleton."""
        registry1 = get_mock_registry()
        registry1.create("l-gent", "L")

        reset_mock_registry()
        registry2 = get_mock_registry()

        assert registry1 is not registry2
        assert len(registry2.list()) == 0


class TestAgentSpecValidation:
    """Test AgentSpec validation."""

    def test_valid_minimal_spec(self) -> None:
        """Minimal spec with genus and name is valid."""
        spec = AgentSpec(name="l-gent", namespace="default", genus="L")
        result = spec.validate()

        assert result.valid is True
        assert len(result.errors) == 0

    def test_missing_genus_invalid(self) -> None:
        """Missing genus is invalid."""
        spec = AgentSpec(name="test", namespace="default", genus="")
        result = spec.validate()

        assert result.valid is False
        assert any("genus" in err for err in result.errors)

    def test_missing_name_invalid(self) -> None:
        """Missing name is invalid."""
        spec = AgentSpec(name="", namespace="default", genus="L")
        result = spec.validate()

        assert result.valid is False
        assert any("name" in err for err in result.errors)

    def test_full_mode_base_image_warning(self) -> None:
        """FULL mode with base image generates warning."""
        spec = AgentSpec(
            name="test",
            namespace="default",
            genus="L",
            deploy_mode=DeployMode.FULL,
            image="python:3.12-slim",  # Base image, no agent code
        )
        result = spec.validate()

        assert result.valid is True
        assert len(result.warnings) > 0
        assert any("base Python image" in w for w in result.warnings)

    def test_full_mode_no_entrypoint_warning(self) -> None:
        """FULL mode without entrypoint generates warning."""
        spec = AgentSpec(
            name="test",
            namespace="default",
            genus="L",
            deploy_mode=DeployMode.FULL,
            image="kgents/l-gent:latest",
            entrypoint=None,
        )
        result = spec.validate()

        assert result.valid is True
        assert any("entrypoint" in w for w in result.warnings)


class TestAgentSpecDeployment:
    """Test AgentSpec deployment generation."""

    def test_placeholder_deployment(self) -> None:
        """PLACEHOLDER mode generates sleep command."""
        spec = AgentSpec(
            name="test",
            namespace="default",
            genus="L",
            deploy_mode=DeployMode.PLACEHOLDER,
        )
        deployment = spec.to_deployment()
        container = deployment["spec"]["template"]["spec"]["containers"][0]

        assert "sleep" in str(container["command"])

    def test_full_deployment_with_entrypoint(self) -> None:
        """FULL mode uses entrypoint module."""
        spec = AgentSpec(
            name="test",
            namespace="default",
            genus="L",
            deploy_mode=DeployMode.FULL,
            entrypoint="agents.l.main",
        )
        deployment = spec.to_deployment()
        container = deployment["spec"]["template"]["spec"]["containers"][0]

        assert container["command"] == ["python", "-m", "agents.l.main"]

    def test_deployment_labels(self) -> None:
        """Deployment has correct labels."""
        spec = AgentSpec(name="test", namespace="default", genus="L")
        deployment = spec.to_deployment()

        labels = deployment["metadata"]["labels"]
        assert labels["kgents.io/genus"] == "L"
        assert labels["app.kubernetes.io/part-of"] == "kgents"
        assert labels["app.kubernetes.io/managed-by"] == "agent-operator"

    def test_sidecar_enabled(self) -> None:
        """Sidecar container added when enabled."""
        spec = AgentSpec(
            name="test",
            namespace="default",
            genus="L",
            sidecar_enabled=True,
        )
        deployment = spec.to_deployment()
        containers = deployment["spec"]["template"]["spec"]["containers"]

        assert len(containers) == 2
        container_names = [c["name"] for c in containers]
        assert "logic" in container_names
        assert "d-gent" in container_names

    def test_sidecar_disabled(self) -> None:
        """No sidecar when disabled."""
        spec = AgentSpec(
            name="test",
            namespace="default",
            genus="L",
            sidecar_enabled=False,
        )
        deployment = spec.to_deployment()
        containers = deployment["spec"]["template"]["spec"]["containers"]

        assert len(containers) == 1
        assert containers[0]["name"] == "logic"


class TestAgentSpecNetworkPolicy:
    """Test AgentSpec network policy generation."""

    def test_no_policy_when_egress_allowed_no_peers(self) -> None:
        """No NetworkPolicy when egress allowed and no peer restrictions."""
        spec = AgentSpec(
            name="test",
            namespace="default",
            genus="L",
            allow_egress=True,
            allowed_peers=[],
        )
        result = spec.to_network_policy()
        assert result is None

    def test_policy_restricts_to_peers(self) -> None:
        """NetworkPolicy restricts to allowed peers."""
        spec = AgentSpec(
            name="test",
            namespace="default",
            genus="L",
            allow_egress=False,
            allowed_peers=["B", "M"],
        )
        policy = spec.to_network_policy()

        assert policy is not None
        assert policy["kind"] == "NetworkPolicy"
        egress = policy["spec"]["egress"]
        assert len(egress) == 1
        assert len(egress[0]["to"]) == 2


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    def setup_method(self) -> None:
        """Reset mock registry before each test."""
        reset_mock_registry()

    def test_deploy_alphabet_garden(self) -> None:
        """Deploy multiple agents (the alphabet garden)."""
        registry = get_mock_registry()

        # Deploy L-gent (Lattice)
        l_gent = registry.create("l-gent", "L", replicas=1)
        assert l_gent.phase == AgentPhase.RUNNING

        # Deploy B-gent (Bio/Economics)
        b_gent = registry.create("b-gent", "B", replicas=2)
        assert b_gent.phase == AgentPhase.RUNNING
        assert b_gent.replicas == 2

        # Deploy M-gent (Memory/Map)
        m_gent = registry.create("m-gent", "M")
        assert m_gent.memory_cr == "m-gent-memory"

        # Verify registry state
        agents = registry.list()
        assert len(agents) == 3
        genera = {a.genus for a in agents}
        assert genera == {"L", "B", "M"}

    def test_scale_and_delete_lifecycle(self) -> None:
        """Full lifecycle: create, scale, delete."""
        registry = get_mock_registry()

        # Create
        agent = registry.create("l-gent", "L")
        assert agent.ready_replicas == 1

        # Scale up
        registry.scale("l-gent", 3)
        agent_scaled_up = registry.get("l-gent")
        assert agent_scaled_up is not None
        assert agent_scaled_up.replicas == 3

        # Scale down
        registry.scale("l-gent", 1)
        agent_scaled_down = registry.get("l-gent")
        assert agent_scaled_down is not None
        assert agent_scaled_down.replicas == 1

        # Delete
        registry.delete("l-gent")
        assert registry.get("l-gent") is None
        assert len(registry.list()) == 0

    def test_dry_run_no_side_effects(self) -> None:
        """DRY_RUN mode creates no resources."""
        registry = get_mock_registry()

        agent = registry.create(
            "test-agent",
            "X",
            deploy_mode=DeployMode.DRY_RUN,
        )

        # Agent exists in registry but no resources created
        assert agent.phase == AgentPhase.PENDING
        assert agent.deployment is None
        assert agent.service is None
        assert agent.memory_cr is None


class TestSCUProbe:
    """Test SCU probe functionality."""

    @pytest.mark.asyncio
    async def test_scu_probe_healthy_response(self) -> None:
        """SCU probe returns HEALTHY for successful cognitive response."""
        from unittest.mock import AsyncMock, MagicMock, patch

        import httpx
        from infra.k8s.operators.agent_operator import run_scu_probe

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy", "response": "HEALTHY"}

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(httpx, "AsyncClient") as mock_constructor:
            mock_constructor.return_value.__aenter__ = AsyncMock(
                return_value=mock_client
            )
            mock_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

            status, latency, message = await run_scu_probe("http://test-service")

        assert status == "HEALTHY"
        assert latency > 0
        assert "passed" in message.lower()

    @pytest.mark.asyncio
    async def test_scu_probe_fallback_to_basic_health(self) -> None:
        """SCU probe falls back to basic health when cognitive endpoint missing."""
        from unittest.mock import AsyncMock, MagicMock, patch

        import httpx
        from infra.k8s.operators.agent_operator import run_scu_probe

        # First call to cognitive endpoint returns 404
        cognitive_response = MagicMock()
        cognitive_response.status_code = 404

        # Fallback to basic health
        health_response = MagicMock()
        health_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=cognitive_response)
        mock_client.get = AsyncMock(return_value=health_response)

        with patch.object(httpx, "AsyncClient") as mock_constructor:
            mock_constructor.return_value.__aenter__ = AsyncMock(
                return_value=mock_client
            )
            mock_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

            status, latency, message = await run_scu_probe("http://test-service")

        assert status == "HEALTHY"
        assert "Basic health check" in message

    @pytest.mark.asyncio
    async def test_scu_probe_timeout(self) -> None:
        """SCU probe returns UNRESPONSIVE on timeout."""
        from unittest.mock import AsyncMock, patch

        import httpx
        from infra.k8s.operators.agent_operator import run_scu_probe

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

        with patch.object(httpx, "AsyncClient") as mock_constructor:
            mock_constructor.return_value.__aenter__ = AsyncMock(
                return_value=mock_client
            )
            mock_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

            status, latency, message = await run_scu_probe(
                "http://test-service", timeout=0.1
            )

        assert status == "UNRESPONSIVE"
        assert "timeout" in message.lower()

    @pytest.mark.asyncio
    async def test_scu_probe_connection_error(self) -> None:
        """SCU probe returns UNRESPONSIVE on connection error."""
        from unittest.mock import AsyncMock, patch

        import httpx
        from infra.k8s.operators.agent_operator import run_scu_probe

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(
            side_effect=httpx.ConnectError("connection refused")
        )

        with patch.object(httpx, "AsyncClient") as mock_constructor:
            mock_constructor.return_value.__aenter__ = AsyncMock(
                return_value=mock_client
            )
            mock_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

            status, latency, message = await run_scu_probe("http://test-service")

        assert status == "UNRESPONSIVE"
        assert "Connection failed" in message

    @pytest.mark.asyncio
    async def test_scu_probe_degraded_on_unexpected_response(self) -> None:
        """SCU probe returns DEGRADED when response doesn't contain HEALTHY."""
        from unittest.mock import AsyncMock, MagicMock, patch

        import httpx
        from infra.k8s.operators.agent_operator import run_scu_probe

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "unknown",
            "response": "something else",
        }

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(httpx, "AsyncClient") as mock_constructor:
            mock_constructor.return_value.__aenter__ = AsyncMock(
                return_value=mock_client
            )
            mock_constructor.return_value.__aexit__ = AsyncMock(return_value=None)

            status, latency, message = await run_scu_probe("http://test-service")

        assert status == "DEGRADED"
        assert "Unexpected response" in message
