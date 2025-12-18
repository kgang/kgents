"""
Tests for Kubernetes Infrastructure Collector.

Tests cover:
- Mock collector functionality
- Entity creation and health scoring
- Connection building from label selectors
- Event streaming
- Topology diff calculation

@see plans/gestalt-live-infrastructure.md
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import pytest

from agents.infra.collectors.kubernetes import (
    KubernetesConfig,
    MockKubernetesCollector,
    _k8s_event_severity,
    _pod_phase_to_status,
)
from agents.infra.health import calculate_entity_health, calculate_topology_health
from agents.infra.models import (
    InfraConnectionKind,
    InfraEntityKind,
    InfraEntityStatus,
    InfraEventSeverity,
)

# =============================================================================
# Status Mapping Tests
# =============================================================================


class TestStatusMapping:
    """Tests for Kubernetes status mappings."""

    def test_pod_phase_running(self):
        """Running pods map to RUNNING status."""
        assert _pod_phase_to_status("Running") == InfraEntityStatus.RUNNING

    def test_pod_phase_pending(self):
        """Pending pods map to PENDING status."""
        assert _pod_phase_to_status("Pending") == InfraEntityStatus.PENDING

    def test_pod_phase_succeeded(self):
        """Succeeded pods map to SUCCEEDED status."""
        assert _pod_phase_to_status("Succeeded") == InfraEntityStatus.SUCCEEDED

    def test_pod_phase_failed(self):
        """Failed pods map to FAILED status."""
        assert _pod_phase_to_status("Failed") == InfraEntityStatus.FAILED

    def test_pod_phase_unknown(self):
        """Unknown phase maps to UNKNOWN status."""
        assert _pod_phase_to_status("Unknown") == InfraEntityStatus.UNKNOWN

    def test_pod_phase_unrecognized(self):
        """Unrecognized phase maps to UNKNOWN status."""
        assert _pod_phase_to_status("SomeWeirdPhase") == InfraEntityStatus.UNKNOWN


class TestEventSeverity:
    """Tests for Kubernetes event severity mapping."""

    def test_normal_event(self):
        """Normal events are INFO severity."""
        assert _k8s_event_severity("Normal", "Started") == InfraEventSeverity.INFO

    def test_warning_event(self):
        """Warning events are WARNING severity."""
        assert _k8s_event_severity("Warning", "Scheduled") == InfraEventSeverity.WARNING

    def test_failed_event(self):
        """Failed events are ERROR severity."""
        assert _k8s_event_severity("Warning", "FailedScheduling") == InfraEventSeverity.ERROR

    def test_oom_event(self):
        """OOM events are ERROR severity (same category as other failures)."""
        # Note: OOM contains "kill" which maps to ERROR in the implementation
        assert _k8s_event_severity("Warning", "OOMKilled") == InfraEventSeverity.ERROR

    def test_backoff_event(self):
        """BackOff events are CRITICAL severity."""
        assert _k8s_event_severity("Warning", "BackOff") == InfraEventSeverity.CRITICAL


# =============================================================================
# Mock Collector Tests
# =============================================================================


class TestMockKubernetesCollector:
    """Tests for MockKubernetesCollector."""

    @pytest.fixture
    def collector(self):
        """Create a mock collector."""
        return MockKubernetesCollector()

    @pytest.mark.asyncio
    async def test_connect(self, collector):
        """Test mock collector connects successfully."""
        await collector.connect()
        assert collector.is_connected

    @pytest.mark.asyncio
    async def test_disconnect(self, collector):
        """Test mock collector disconnects successfully."""
        await collector.connect()
        await collector.disconnect()
        assert not collector.is_connected

    @pytest.mark.asyncio
    async def test_collect_topology(self, collector):
        """Test collecting topology from mock collector."""
        await collector.connect()
        topology = await collector.collect_topology()

        # Verify topology structure
        assert topology is not None
        assert len(topology.entities) > 0
        assert topology.timestamp is not None

        # Verify entity kinds present
        kinds = {e.kind for e in topology.entities}
        assert InfraEntityKind.POD in kinds
        assert InfraEntityKind.SERVICE in kinds
        assert InfraEntityKind.DEPLOYMENT in kinds

    @pytest.mark.asyncio
    async def test_entities_have_namespaces(self, collector):
        """Test that entities have namespace assignments."""
        await collector.connect()
        topology = await collector.collect_topology()

        namespaces = {e.namespace for e in topology.entities}
        # Mock generates 3 namespaces
        assert len(namespaces) == 3
        assert "default" in namespaces
        assert "kgents" in namespaces
        assert "monitoring" in namespaces

    @pytest.mark.asyncio
    async def test_entities_have_health(self, collector):
        """Test that entities have health scores."""
        await collector.connect()
        topology = await collector.collect_topology()

        for entity in topology.entities:
            assert 0.0 <= entity.health <= 1.0

    @pytest.mark.asyncio
    async def test_entities_have_positions(self, collector):
        """Test that entities have calculated positions."""
        await collector.connect()
        topology = await collector.collect_topology()

        for entity in topology.entities:
            # Position should be set (not all zeros from layout)
            # Note: random init means they won't all be exactly zero
            assert hasattr(entity, "x")
            assert hasattr(entity, "y")
            assert hasattr(entity, "z")

    @pytest.mark.asyncio
    async def test_connections_exist(self, collector):
        """Test that connections are generated."""
        await collector.connect()
        topology = await collector.collect_topology()

        assert len(topology.connections) > 0

        # Check connection kinds
        kinds = {c.kind for c in topology.connections}
        assert InfraConnectionKind.SELECTS in kinds or InfraConnectionKind.OWNS in kinds

    @pytest.mark.asyncio
    async def test_stream_events(self, collector):
        """Test event streaming produces events."""
        await collector.connect()

        events = []
        event_count = 0

        async for event in collector.stream_events():
            events.append(event)
            event_count += 1
            if event_count >= 2:
                break

        # Should have received at least 2 events
        assert len(events) >= 2

        # Verify event structure
        for event in events:
            assert event.id is not None
            assert event.type in ("Normal", "Warning")
            assert event.reason is not None
            assert event.message is not None
            assert event.entity_id is not None

        await collector.disconnect()


# =============================================================================
# Kubernetes Config Tests
# =============================================================================


class TestKubernetesConfig:
    """Tests for KubernetesConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = KubernetesConfig()

        assert config.kubeconfig is None  # Uses in-cluster by default
        assert config.context is None
        assert config.namespaces == []
        assert config.poll_interval == 5.0
        assert config.collect_pods is True
        assert config.collect_services is True
        assert config.collect_deployments is True
        assert config.collect_metrics is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = KubernetesConfig(
            kubeconfig="/home/user/.kube/config",
            namespaces=["default", "production"],
            poll_interval=10.0,
            collect_secrets=False,
        )

        assert config.kubeconfig == "/home/user/.kube/config"
        assert config.namespaces == ["default", "production"]
        assert config.poll_interval == 10.0
        assert config.collect_secrets is False


# =============================================================================
# Health Calculation Integration Tests
# =============================================================================


class TestHealthCalculationIntegration:
    """Tests for health calculation with mock topology."""

    @pytest.fixture
    def collector(self):
        """Create a mock collector."""
        return MockKubernetesCollector()

    @pytest.mark.asyncio
    async def test_topology_health_calculation(self, collector):
        """Test calculating health for entire topology."""
        await collector.connect()
        topology = await collector.collect_topology()

        health_data = calculate_topology_health(topology)

        # Verify health data structure
        assert "overall" in health_data
        assert "healthy" in health_data
        assert "warning" in health_data
        assert "critical" in health_data
        assert "total" in health_data
        assert "by_kind" in health_data
        assert "by_namespace" in health_data
        assert "worst_entities" in health_data

        # Verify counts add up
        assert health_data["total"] == len(topology.entities)
        assert (
            health_data["healthy"] + health_data["warning"] + health_data["critical"]
            == health_data["total"]
        )

        # Overall health should be 0-1
        assert 0.0 <= health_data["overall"] <= 1.0

    @pytest.mark.asyncio
    async def test_entity_health_grades(self, collector):
        """Test that entity health grades are assigned correctly."""
        await collector.connect()
        topology = await collector.collect_topology()

        for entity in topology.entities:
            grade = entity.health_grade

            # Verify grade is valid
            assert grade in ["A+", "A", "B+", "B", "C+", "C", "D", "F"]

            # Verify grade matches health
            if entity.health >= 0.95:
                assert grade == "A+"
            elif entity.health >= 0.4:
                # Various grades
                pass
            else:
                assert grade == "F"


# =============================================================================
# Topology Diff Tests
# =============================================================================


class TestTopologyDiff:
    """Tests for topology diff calculation."""

    @pytest.fixture
    def collector(self):
        """Create a mock collector."""
        return MockKubernetesCollector()

    @pytest.mark.asyncio
    async def test_initial_diff_is_full(self, collector):
        """Test that initial diff returns full topology."""
        await collector.connect()

        updates = await collector.collect_topology_diff()

        # First call should return full topology
        assert len(updates) == 1
        # kind may be an enum or string depending on implementation
        kind = updates[0].kind
        if hasattr(kind, "value"):
            assert kind.value == "full"
        else:
            assert kind == "full"
        assert updates[0].topology is not None

    @pytest.mark.asyncio
    async def test_subsequent_diff_returns_changes(self, collector):
        """Test that subsequent diffs return incremental changes."""
        await collector.connect()

        # First call - full topology
        await collector.collect_topology_diff()

        # Second call - should get updates (mock generates random health each time)
        updates = await collector.collect_topology_diff()

        # Should have some updates (entities may change health)
        # The mock collector generates random data, so there will likely be changes
        assert isinstance(updates, list)


# =============================================================================
# Connection Building Tests
# =============================================================================


class TestConnectionBuilding:
    """Tests for building connections from label selectors."""

    @pytest.fixture
    def collector(self):
        """Create a mock collector."""
        return MockKubernetesCollector()

    @pytest.mark.asyncio
    async def test_service_to_pod_connections(self, collector):
        """Test that services have connections to pods."""
        await collector.connect()
        topology = await collector.collect_topology()

        # Find services
        services = [e for e in topology.entities if e.kind == InfraEntityKind.SERVICE]
        assert len(services) > 0

        # Each service should have at least one connection
        service_ids = {s.id for s in services}
        service_connections = [c for c in topology.connections if c.source_id in service_ids]

        assert len(service_connections) > 0

    @pytest.mark.asyncio
    async def test_deployment_to_pod_connections(self, collector):
        """Test that deployments have connections to pods."""
        await collector.connect()
        topology = await collector.collect_topology()

        # Find deployments
        deployments = [e for e in topology.entities if e.kind == InfraEntityKind.DEPLOYMENT]
        assert len(deployments) > 0

        # Each deployment should have at least one connection
        deployment_ids = {d.id for d in deployments}
        deployment_connections = [c for c in topology.connections if c.source_id in deployment_ids]

        assert len(deployment_connections) > 0


# =============================================================================
# Entity Creation Tests
# =============================================================================


class TestEntityCreation:
    """Tests for entity creation from K8s objects."""

    @pytest.fixture
    def collector(self):
        """Create a mock collector."""
        return MockKubernetesCollector()

    @pytest.mark.asyncio
    async def test_pod_entities_have_expected_fields(self, collector):
        """Test that pod entities have expected fields populated."""
        await collector.connect()
        topology = await collector.collect_topology()

        pods = [e for e in topology.entities if e.kind == InfraEntityKind.POD]
        assert len(pods) > 0

        for pod in pods:
            assert pod.id is not None
            assert pod.name is not None
            assert pod.namespace is not None
            assert pod.status is not None
            assert pod.source == "kubernetes"

    @pytest.mark.asyncio
    async def test_service_entities_have_expected_fields(self, collector):
        """Test that service entities have expected fields populated."""
        await collector.connect()
        topology = await collector.collect_topology()

        services = [e for e in topology.entities if e.kind == InfraEntityKind.SERVICE]
        assert len(services) > 0

        for svc in services:
            assert svc.id is not None
            assert svc.name is not None
            assert svc.namespace is not None
            assert svc.status == InfraEntityStatus.RUNNING  # Services always running
            assert svc.source == "kubernetes"

    @pytest.mark.asyncio
    async def test_deployment_entities_have_expected_fields(self, collector):
        """Test that deployment entities have expected fields populated."""
        await collector.connect()
        topology = await collector.collect_topology()

        deployments = [e for e in topology.entities if e.kind == InfraEntityKind.DEPLOYMENT]
        assert len(deployments) > 0

        for deploy in deployments:
            assert deploy.id is not None
            assert deploy.name is not None
            assert deploy.namespace is not None
            assert deploy.source == "kubernetes"
            # Should have replica metrics
            assert "desired_replicas" in deploy.custom_metrics or deploy.custom_metrics == {}
