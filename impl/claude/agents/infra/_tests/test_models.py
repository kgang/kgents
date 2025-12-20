"""
Tests for Infrastructure Data Models

Tests entity creation, health scoring, and topology aggregation.

@see plans/gestalt-live-infrastructure.md
"""

from datetime import UTC, datetime

import pytest

from agents.infra.health import (
    HealthThresholds,
    calculate_entity_health,
    calculate_topology_health,
    grade_to_color,
    health_to_grade,
)
from agents.infra.models import (
    InfraConnection,
    InfraConnectionKind,
    InfraEntity,
    InfraEntityKind,
    InfraEntityStatus,
    InfraEvent,
    InfraEventSeverity,
    InfraTopology,
)

# =============================================================================
# InfraEntity Tests
# =============================================================================


class TestInfraEntity:
    """Tests for InfraEntity model."""

    def test_create_pod_entity(self) -> None:
        """Test creating a basic pod entity."""
        entity = InfraEntity(
            id="pod/default/nginx",
            kind=InfraEntityKind.POD,
            name="nginx",
            namespace="default",
            status=InfraEntityStatus.RUNNING,
        )

        assert entity.id == "pod/default/nginx"
        assert entity.kind == InfraEntityKind.POD
        assert entity.name == "nginx"
        assert entity.namespace == "default"
        assert entity.status == InfraEntityStatus.RUNNING
        assert entity.health == 1.0  # Default healthy

    def test_auto_generate_id(self) -> None:
        """Test automatic ID generation from kind/namespace/name."""
        entity = InfraEntity(
            id="",
            kind=InfraEntityKind.SERVICE,
            name="api-gateway",
            namespace="production",
        )

        assert entity.id == "service/production/api-gateway"

    def test_display_name_with_namespace(self) -> None:
        """Test display name includes namespace."""
        entity = InfraEntity(
            id="test",
            kind=InfraEntityKind.POD,
            name="worker",
            namespace="jobs",
        )

        assert entity.display_name == "jobs/worker"

    def test_display_name_without_namespace(self) -> None:
        """Test display name without namespace."""
        entity = InfraEntity(
            id="test",
            kind=InfraEntityKind.NODE,
            name="node-1",
        )

        assert entity.display_name == "node-1"

    def test_memory_percent_calculation(self) -> None:
        """Test memory percentage calculation."""
        entity = InfraEntity(
            id="test",
            kind=InfraEntityKind.POD,
            name="test",
            memory_bytes=512 * 1024 * 1024,  # 512 MB
            memory_limit=1024 * 1024 * 1024,  # 1 GB
        )

        assert entity.memory_percent == 50.0

    def test_memory_percent_no_limit(self) -> None:
        """Test memory percentage when no limit is set."""
        entity = InfraEntity(
            id="test",
            kind=InfraEntityKind.POD,
            name="test",
            memory_bytes=512 * 1024 * 1024,
        )

        assert entity.memory_percent is None

    def test_health_grade_mapping(self) -> None:
        """Test health score to grade mapping."""
        cases = [
            (1.0, "A+"),
            (0.95, "A+"),
            (0.92, "A"),
            (0.87, "B+"),
            (0.82, "B"),
            (0.75, "C+"),
            (0.65, "C"),
            (0.45, "D"),
            (0.2, "F"),
        ]

        for health, expected_grade in cases:
            entity = InfraEntity(
                id="test",
                kind=InfraEntityKind.POD,
                name="test",
                health=health,
            )
            assert entity.health_grade == expected_grade, (
                f"Health {health} should be grade {expected_grade}"
            )


# =============================================================================
# InfraConnection Tests
# =============================================================================


class TestInfraConnection:
    """Tests for InfraConnection model."""

    def test_create_connection(self) -> None:
        """Test creating a basic connection."""
        conn = InfraConnection(
            source_id="pod/default/frontend",
            target_id="service/default/api",
            kind=InfraConnectionKind.HTTP,
        )

        assert conn.source_id == "pod/default/frontend"
        assert conn.target_id == "service/default/api"
        assert conn.kind == InfraConnectionKind.HTTP

    def test_connection_id(self) -> None:
        """Test connection ID generation."""
        conn = InfraConnection(
            source_id="a",
            target_id="b",
            kind=InfraConnectionKind.NATS,
        )

        assert conn.id == "a->b:nats"


# =============================================================================
# InfraTopology Tests
# =============================================================================


class TestInfraTopology:
    """Tests for InfraTopology model."""

    def test_empty_topology(self) -> None:
        """Test topology with no entities."""
        topology = InfraTopology(
            entities=[],
            connections=[],
            timestamp=datetime.now(UTC),
        )

        assert topology.total_entities == 0
        assert topology.healthy_count == 0
        assert topology.overall_health == 1.0

    def test_topology_statistics(self) -> None:
        """Test topology aggregate statistics."""
        entities = [
            InfraEntity(id="1", kind=InfraEntityKind.POD, name="healthy", health=0.9),
            InfraEntity(id="2", kind=InfraEntityKind.POD, name="warning", health=0.6),
            InfraEntity(id="3", kind=InfraEntityKind.SERVICE, name="critical", health=0.3),
        ]

        topology = InfraTopology(
            entities=entities,
            connections=[],
            timestamp=datetime.now(UTC),
        )

        assert topology.total_entities == 3
        assert topology.healthy_count == 1
        assert topology.warning_count == 1
        assert topology.critical_count == 1
        assert topology.entities_by_kind == {"pod": 2, "service": 1}

    def test_topology_overall_health(self) -> None:
        """Test overall health calculation."""
        entities = [
            InfraEntity(id="1", kind=InfraEntityKind.POD, name="a", health=1.0),
            InfraEntity(id="2", kind=InfraEntityKind.POD, name="b", health=0.8),
            InfraEntity(id="3", kind=InfraEntityKind.POD, name="c", health=0.6),
        ]

        topology = InfraTopology(
            entities=entities,
            connections=[],
            timestamp=datetime.now(UTC),
        )

        assert topology.overall_health == pytest.approx(0.8, abs=0.01)


# =============================================================================
# Health Scoring Tests
# =============================================================================


class TestHealthScoring:
    """Tests for health scoring functions."""

    def test_healthy_running_pod(self) -> None:
        """Test health score for a healthy running pod."""
        entity = InfraEntity(
            id="test",
            kind=InfraEntityKind.POD,
            name="healthy",
            status=InfraEntityStatus.RUNNING,
            cpu_percent=20.0,
            memory_bytes=200 * 1024 * 1024,
            memory_limit=1024 * 1024 * 1024,
        )

        health = calculate_entity_health(entity)
        assert health >= 0.8  # Should be healthy

    def test_high_cpu_reduces_health(self) -> None:
        """Test that high CPU usage reduces health."""
        entity = InfraEntity(
            id="test",
            kind=InfraEntityKind.POD,
            name="busy",
            status=InfraEntityStatus.RUNNING,
            cpu_percent=95.0,  # Critical level
        )

        health = calculate_entity_health(entity)
        # Status is RUNNING (1.0) but CPU is critical (0.0)
        # Weighted average: (1.0*3 + 0.0*1) / 4 = 0.75
        assert health < 0.8  # Should be noticeably unhealthy

    def test_failed_status_low_health(self) -> None:
        """Test that failed status results in low health."""
        entity = InfraEntity(
            id="test",
            kind=InfraEntityKind.POD,
            name="failed",
            status=InfraEntityStatus.FAILED,
        )

        health = calculate_entity_health(entity)
        assert health < 0.3  # Should be very unhealthy

    def test_custom_thresholds(self) -> None:
        """Test health scoring with custom thresholds."""
        entity = InfraEntity(
            id="test",
            kind=InfraEntityKind.POD,
            name="test",
            status=InfraEntityStatus.RUNNING,
            cpu_percent=50.0,
        )

        # Default thresholds: 50% CPU should be fine
        default_health = calculate_entity_health(entity)

        # Stricter thresholds: 50% CPU is warning level
        strict = HealthThresholds(cpu_warning=40.0, cpu_critical=60.0)
        strict_health = calculate_entity_health(entity, strict)

        assert strict_health < default_health

    def test_health_to_grade(self) -> None:
        """Test health to grade conversion."""
        assert health_to_grade(1.0) == "A+"
        assert health_to_grade(0.5) == "D"
        assert health_to_grade(0.0) == "F"

    def test_grade_to_color(self) -> None:
        """Test grade to color conversion."""
        assert grade_to_color("A+") == "#22c55e"  # Green
        assert grade_to_color("F") == "#dc2626"  # Red


# =============================================================================
# Topology Health Tests
# =============================================================================


class TestTopologyHealth:
    """Tests for topology-level health calculations."""

    def test_topology_health_breakdown(self) -> None:
        """Test topology health breakdown by kind and namespace."""
        # Use status to control health - RUNNING = healthy, PENDING = warning
        entities = [
            InfraEntity(
                id="1",
                kind=InfraEntityKind.POD,
                name="a",
                namespace="prod",
                status=InfraEntityStatus.RUNNING,
            ),
            InfraEntity(
                id="2",
                kind=InfraEntityKind.POD,
                name="b",
                namespace="prod",
                status=InfraEntityStatus.RUNNING,
            ),
            InfraEntity(
                id="3",
                kind=InfraEntityKind.POD,
                name="c",
                namespace="dev",
                status=InfraEntityStatus.PENDING,
            ),
            InfraEntity(
                id="4",
                kind=InfraEntityKind.SERVICE,
                name="d",
                namespace="prod",
                status=InfraEntityStatus.RUNNING,
            ),
        ]

        topology = InfraTopology(
            entities=entities,
            connections=[],
            timestamp=datetime.now(UTC),
        )

        health_report = calculate_topology_health(topology)

        # RUNNING status should give healthy scores (>=0.8)
        # PENDING status should give warning scores (0.5-0.8)
        assert health_report["healthy"] >= 2  # At least the RUNNING ones
        assert "pod" in health_report["by_kind"]
        assert "prod" in health_report["by_namespace"]

    def test_worst_entities_list(self) -> None:
        """Test that worst entities are identified."""
        # Use status to control health
        entities = [
            InfraEntity(
                id="1",
                kind=InfraEntityKind.POD,
                name="healthy",
                status=InfraEntityStatus.RUNNING,
            ),
            InfraEntity(
                id="2",
                kind=InfraEntityKind.POD,
                name="sick",
                status=InfraEntityStatus.PENDING,
            ),
            InfraEntity(
                id="3",
                kind=InfraEntityKind.POD,
                name="dying",
                status=InfraEntityStatus.FAILED,
            ),
        ]

        topology = InfraTopology(
            entities=entities,
            connections=[],
            timestamp=datetime.now(UTC),
        )

        health_report = calculate_topology_health(topology)

        worst = health_report["worst_entities"]
        assert len(worst) == 3
        # FAILED should have worst health, RUNNING should have best
        assert worst[0]["name"] == "dying"  # Worst first (FAILED)
        assert worst[-1]["name"] == "healthy"  # Best last (RUNNING)


# =============================================================================
# Event Tests
# =============================================================================


class TestInfraEvent:
    """Tests for InfraEvent model."""

    def test_create_event(self) -> None:
        """Test creating a basic event."""
        event = InfraEvent(
            id="event-123",
            type="Warning",
            reason="FailedScheduling",
            message="No nodes available",
            severity=InfraEventSeverity.WARNING,
            entity_id="pod/default/nginx",
            entity_kind=InfraEntityKind.POD,
            entity_name="nginx",
        )

        assert event.id == "event-123"
        assert event.severity == InfraEventSeverity.WARNING
        assert event.entity_kind == InfraEntityKind.POD

    def test_from_kubernetes_event(self) -> None:
        """Test creating event from Kubernetes event object."""
        k8s_event = {
            "metadata": {"uid": "abc-123"},
            "type": "Warning",
            "reason": "BackOff",
            "message": "Back-off restarting failed container",
            "involvedObject": {
                "kind": "Pod",
                "name": "worker-1",
                "namespace": "default",
            },
            "lastTimestamp": "2025-01-01T00:00:00Z",
            "count": 5,
            "source": {"component": "kubelet", "host": "node-1"},
        }

        event = InfraEvent.from_kubernetes_event(k8s_event)

        assert event.id == "abc-123"
        assert event.reason == "BackOff"
        assert event.severity == InfraEventSeverity.WARNING
        assert event.count == 5
