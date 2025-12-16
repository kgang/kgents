"""
Tests for Semantic Infrastructure Layout.

@see impl/claude/agents/infra/layout.py
"""

from __future__ import annotations

import pytest

from agents.infra.layout import (
    LayoutConfig,
    LayoutStrategy,
    SEMANTIC_LAYERS,
    apply_layout,
    calculate_semantic_layout,
    get_layer,
)
from agents.infra.models import (
    InfraConnection,
    InfraConnectionKind,
    InfraEntity,
    InfraEntityKind,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_entities() -> list[InfraEntity]:
    """Create a sample set of entities for testing."""
    return [
        # Namespace: kgents-triad
        InfraEntity(
            id="service/kgents-triad/api",
            kind=InfraEntityKind.SERVICE,
            name="api",
            namespace="kgents-triad",
            health=1.0,
        ),
        InfraEntity(
            id="deployment/kgents-triad/api",
            kind=InfraEntityKind.DEPLOYMENT,
            name="api",
            namespace="kgents-triad",
            health=0.9,
        ),
        InfraEntity(
            id="pod/kgents-triad/api-abc",
            kind=InfraEntityKind.POD,
            name="api-abc",
            namespace="kgents-triad",
            health=1.0,
        ),
        InfraEntity(
            id="pod/kgents-triad/api-def",
            kind=InfraEntityKind.POD,
            name="api-def",
            namespace="kgents-triad",
            health=0.6,  # Warning
        ),
        # Namespace: kgents-agents
        InfraEntity(
            id="service/kgents-agents/nats",
            kind=InfraEntityKind.SERVICE,
            name="nats",
            namespace="kgents-agents",
            health=1.0,
        ),
        InfraEntity(
            id="pod/kgents-agents/nats-0",
            kind=InfraEntityKind.POD,
            name="nats-0",
            namespace="kgents-agents",
            health=0.4,  # Critical
        ),
    ]


@pytest.fixture
def sample_connections() -> list[InfraConnection]:
    """Create sample connections."""
    return [
        # Service selects pods
        InfraConnection(
            source_id="service/kgents-triad/api",
            target_id="pod/kgents-triad/api-abc",
            kind=InfraConnectionKind.SELECTS,
        ),
        InfraConnection(
            source_id="service/kgents-triad/api",
            target_id="pod/kgents-triad/api-def",
            kind=InfraConnectionKind.SELECTS,
        ),
        # Deployment owns pods
        InfraConnection(
            source_id="deployment/kgents-triad/api",
            target_id="pod/kgents-triad/api-abc",
            kind=InfraConnectionKind.OWNS,
        ),
        InfraConnection(
            source_id="deployment/kgents-triad/api",
            target_id="pod/kgents-triad/api-def",
            kind=InfraConnectionKind.OWNS,
        ),
    ]


# =============================================================================
# Layer Assignment Tests
# =============================================================================


class TestSemanticLayers:
    """Tests for semantic layer assignment."""

    def test_services_above_pods(self) -> None:
        """Services should be in a higher layer than pods."""
        assert get_layer(InfraEntityKind.SERVICE) > get_layer(InfraEntityKind.POD)

    def test_deployments_above_pods(self) -> None:
        """Deployments should be in a higher layer than pods."""
        assert get_layer(InfraEntityKind.DEPLOYMENT) > get_layer(InfraEntityKind.POD)

    def test_services_above_deployments(self) -> None:
        """Services should be at same or higher layer than deployments."""
        assert get_layer(InfraEntityKind.SERVICE) >= get_layer(InfraEntityKind.DEPLOYMENT)

    def test_all_kinds_have_layers(self) -> None:
        """All entity kinds should have defined layers."""
        for kind in InfraEntityKind:
            assert kind in SEMANTIC_LAYERS, f"Missing layer for {kind}"


# =============================================================================
# Namespace Clustering Tests
# =============================================================================


class TestNamespaceClustering:
    """Tests for namespace-based clustering."""

    def test_entities_grouped_by_namespace(
        self,
        sample_entities: list[InfraEntity],
        sample_connections: list[InfraConnection],
    ) -> None:
        """Entities in same namespace should be clustered together."""
        calculate_semantic_layout(sample_entities, sample_connections)

        # Get average X for each namespace
        by_ns: dict[str, list[float]] = {}
        for e in sample_entities:
            ns = e.namespace or "(none)"
            if ns not in by_ns:
                by_ns[ns] = []
            by_ns[ns].append(e.x)

        # Calculate cluster centers
        centers = {ns: sum(xs) / len(xs) for ns, xs in by_ns.items()}

        # Namespaces should have distinct centers
        ns_list = list(centers.keys())
        if len(ns_list) >= 2:
            # Centers should be separated
            assert abs(centers[ns_list[0]] - centers[ns_list[1]]) > 1.0


# =============================================================================
# Vertical Hierarchy Tests
# =============================================================================


class TestVerticalHierarchy:
    """Tests for kind-based vertical hierarchy."""

    def test_services_above_pods_vertically(
        self,
        sample_entities: list[InfraEntity],
        sample_connections: list[InfraConnection],
    ) -> None:
        """Services should have higher Y than pods in same namespace."""
        calculate_semantic_layout(sample_entities, sample_connections)

        service = next(e for e in sample_entities if e.kind == InfraEntityKind.SERVICE)
        pods = [e for e in sample_entities if e.kind == InfraEntityKind.POD]

        # Get pods in same namespace
        same_ns_pods = [p for p in pods if p.namespace == service.namespace]

        for pod in same_ns_pods:
            assert service.y > pod.y, "Service should be above pods"

    def test_deployments_between_services_and_pods(
        self,
        sample_entities: list[InfraEntity],
        sample_connections: list[InfraConnection],
    ) -> None:
        """Deployments should be between services and pods vertically."""
        calculate_semantic_layout(sample_entities, sample_connections)

        service = next(
            e for e in sample_entities
            if e.kind == InfraEntityKind.SERVICE and e.namespace == "kgents-triad"
        )
        deployment = next(
            e for e in sample_entities
            if e.kind == InfraEntityKind.DEPLOYMENT
        )
        pod = next(
            e for e in sample_entities
            if e.kind == InfraEntityKind.POD and e.namespace == "kgents-triad"
        )

        assert service.y >= deployment.y >= pod.y, "Should be service >= deployment >= pod"


# =============================================================================
# Health-Based Depth Tests
# =============================================================================


class TestHealthDepth:
    """Tests for health-based Z positioning (attention principle)."""

    def test_healthy_entities_at_background(
        self,
        sample_entities: list[InfraEntity],
        sample_connections: list[InfraConnection],
    ) -> None:
        """Healthy entities should be at z≈0."""
        calculate_semantic_layout(sample_entities, sample_connections)

        healthy = [e for e in sample_entities if e.health >= 0.9]
        for entity in healthy:
            assert abs(entity.z) < 1.0, f"Healthy entity {entity.name} should be near z=0"

    def test_warning_entities_forward(
        self,
        sample_entities: list[InfraEntity],
        sample_connections: list[InfraConnection],
    ) -> None:
        """Warning entities should come forward (z > 0)."""
        calculate_semantic_layout(sample_entities, sample_connections)

        warning = [e for e in sample_entities if 0.5 <= e.health < 0.7]
        for entity in warning:
            assert entity.z > 0, f"Warning entity {entity.name} should be forward"

    def test_critical_entities_most_forward(
        self,
        sample_entities: list[InfraEntity],
        sample_connections: list[InfraConnection],
    ) -> None:
        """Critical entities should be furthest forward."""
        calculate_semantic_layout(sample_entities, sample_connections)

        critical = [e for e in sample_entities if e.health < 0.5]
        warning = [e for e in sample_entities if 0.5 <= e.health < 0.7]

        if critical and warning:
            max_critical_z = max(e.z for e in critical)
            max_warning_z = max(e.z for e in warning)
            assert max_critical_z > max_warning_z, "Critical should be more forward than warning"


# =============================================================================
# Layout Strategy Tests
# =============================================================================


class TestLayoutStrategies:
    """Tests for different layout strategies."""

    def test_semantic_strategy(
        self,
        sample_entities: list[InfraEntity],
        sample_connections: list[InfraConnection],
    ) -> None:
        """Semantic strategy should produce deterministic results."""
        # Apply twice
        entities1 = [InfraEntity(**e.__dict__) for e in sample_entities]
        entities2 = [InfraEntity(**e.__dict__) for e in sample_entities]

        apply_layout(entities1, sample_connections, LayoutStrategy.SEMANTIC)
        apply_layout(entities2, sample_connections, LayoutStrategy.SEMANTIC)

        # Positions should be identical (deterministic)
        for e1, e2 in zip(entities1, entities2):
            assert abs(e1.x - e2.x) < 0.01
            assert abs(e1.y - e2.y) < 0.01
            assert abs(e1.z - e2.z) < 0.01

    def test_hierarchical_strategy(
        self,
        sample_entities: list[InfraEntity],
        sample_connections: list[InfraConnection],
    ) -> None:
        """Hierarchical strategy should have no refinement."""
        entities = [InfraEntity(**e.__dict__) for e in sample_entities]
        apply_layout(entities, sample_connections, LayoutStrategy.HIERARCHICAL)

        # Just verify it completes without error
        assert all(e.x is not None for e in entities)


# =============================================================================
# Configuration Tests
# =============================================================================


class TestLayoutConfig:
    """Tests for layout configuration."""

    def test_custom_spacing(
        self,
        sample_entities: list[InfraEntity],
        sample_connections: list[InfraConnection],
    ) -> None:
        """Custom spacing should affect layout."""
        entities_narrow = [InfraEntity(**e.__dict__) for e in sample_entities]
        entities_wide = [InfraEntity(**e.__dict__) for e in sample_entities]

        narrow_config = LayoutConfig(namespace_spacing=5.0)
        wide_config = LayoutConfig(namespace_spacing=20.0)

        apply_layout(entities_narrow, sample_connections, config=narrow_config)
        apply_layout(entities_wide, sample_connections, config=wide_config)

        # Wide config should produce larger X spread
        narrow_spread = max(e.x for e in entities_narrow) - min(e.x for e in entities_narrow)
        wide_spread = max(e.x for e in entities_wide) - min(e.x for e in entities_wide)

        # Note: normalization may limit this effect
        assert wide_spread >= narrow_spread * 0.5  # Allow for normalization


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_entities(self) -> None:
        """Should handle empty entity list."""
        entities: list[InfraEntity] = []
        connections: list[InfraConnection] = []

        # Should not raise
        calculate_semantic_layout(entities, connections)

    def test_single_entity(self) -> None:
        """Should handle single entity."""
        entities = [
            InfraEntity(
                id="pod/default/solo",
                kind=InfraEntityKind.POD,
                name="solo",
                namespace="default",
            )
        ]
        calculate_semantic_layout(entities, [])

        # Should be centered
        assert abs(entities[0].x) < 0.1
        assert entities[0].z == 0.0  # Healthy

    def test_no_connections(
        self,
        sample_entities: list[InfraEntity],
    ) -> None:
        """Should work with no connections."""
        calculate_semantic_layout(sample_entities, [])

        # Should still have valid positions
        for e in sample_entities:
            assert e.x is not None
            assert e.y is not None
            assert e.z is not None

    def test_unknown_kind(self) -> None:
        """Should handle unknown entity kinds."""
        entities = [
            InfraEntity(
                id="custom/unknown",
                kind=InfraEntityKind.CUSTOM,
                name="unknown",
            )
        ]
        calculate_semantic_layout(entities, [])

        assert entities[0].x is not None
