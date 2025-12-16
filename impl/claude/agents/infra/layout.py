"""
Semantic Infrastructure Layout

Principled layout algorithm for Gestalt Live following the Projection Protocol.

Design Principles (from spec/protocols/projection.md):
1. "Depth is not decoration—it is information"
2. Layout projection is structural isomorphism—same information, different arrangements
3. Semantic hierarchy should be visually encoded

The Layout Model (v2 - Compact Stacks):
=======================================

The layout creates tight "stacks" of related entities (service → deployment → pods)
arranged as vertical columns. This makes the architecture immediately visible.

Y-axis (vertical) = Abstraction Layer
    Services (entry points) → top
    Deployments/StatefulSets (orchestrators) → middle
    Pods (workers) → bottom

X-axis (horizontal) = Stack Position Within Namespace
    Related entities (connected by ownership/selection) align vertically
    Stacks spread horizontally within their namespace
    Much more compact than spreading all entities

Z-axis (depth) = Namespace + Health
    Namespaces spread in depth (front to back)
    Within namespace, unhealthy entities come forward
    This uses depth for BOTH organization and attention

Visual Result:
    Each namespace forms a "slice" at a Z position
    Within each slice, vertical towers show service→deploy→pod relationships
    Unhealthy pods push forward slightly within their slice

@see spec/protocols/projection.md (Layout Projection, 3D Target Projection)
@see plans/_continuations/gestalt-live-real-k8s.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

from .models import InfraConnection, InfraEntity, InfraEntityKind


# =============================================================================
# Layout Configuration
# =============================================================================


class LayoutStrategy(str, Enum):
    """Available layout strategies."""

    SEMANTIC = "semantic"       # Principled semantic layout (default)
    FORCE_DIRECTED = "force"    # Classic force-directed (fallback)
    HIERARCHICAL = "hierarchical"  # Strict layer-based (for debugging)


@dataclass
class LayoutConfig:
    """Configuration for semantic layout."""

    # Strategy selection
    strategy: LayoutStrategy = LayoutStrategy.SEMANTIC

    # Stack-based spacing (v2 compact layout)
    stack_spacing: float = 3.0          # X distance between stacks within namespace
    namespace_depth: float = 8.0        # Z distance between namespace slices
    layer_spacing: float = 3.0          # Y distance between abstraction layers

    # Legacy spacing (for fallback)
    namespace_spacing: float = 12.0     # X distance between namespace centers
    entity_spacing: float = 2.5         # Minimum distance between entities

    # Z-axis health encoding (within namespace slice)
    health_depth_scale: float = 2.0     # How far unhealthy entities come forward
    warning_threshold: float = 0.7      # Health below this = warning
    critical_threshold: float = 0.5     # Health below this = critical

    # Force-directed refinement (applied after semantic placement)
    refinement_iterations: int = 30
    spring_strength: float = 0.05
    repulsion_strength: float = 50.0

    # Visual bounds
    max_x: float = 30.0
    max_y: float = 15.0
    max_z: float = 20.0


# =============================================================================
# Semantic Layer Definitions
# =============================================================================


# Layer assignment by entity kind (lower = bottom, higher = top)
SEMANTIC_LAYERS: dict[InfraEntityKind, int] = {
    # Layer 3: Entry points (top)
    InfraEntityKind.INGRESS: 3,

    # Layer 2: Services (traffic routing)
    InfraEntityKind.SERVICE: 2,

    # Layer 1: Orchestrators
    InfraEntityKind.DEPLOYMENT: 1,
    InfraEntityKind.STATEFULSET: 1,
    InfraEntityKind.DAEMONSET: 1,

    # Layer 0: Workers (bottom)
    InfraEntityKind.POD: 0,
    InfraEntityKind.CONTAINER: 0,

    # Infrastructure (placed below workers)
    InfraEntityKind.NODE: -1,
    InfraEntityKind.PVC: -1,
    InfraEntityKind.VOLUME: -1,

    # Config/Secrets (same layer as orchestrators)
    InfraEntityKind.CONFIGMAP: 1,
    InfraEntityKind.SECRET: 1,

    # NATS/messaging (parallel to services)
    InfraEntityKind.NATS_SERVER: 2,
    InfraEntityKind.NATS_SUBJECT: 1,
    InfraEntityKind.NATS_STREAM: 1,
    InfraEntityKind.NATS_CONSUMER: 0,

    # Database (infrastructure layer)
    InfraEntityKind.DATABASE: -1,
    InfraEntityKind.DATABASE_CONNECTION: 0,

    # Namespace container (above all)
    InfraEntityKind.NAMESPACE: 4,

    # Catch-all
    InfraEntityKind.CUSTOM: 0,
    InfraEntityKind.NETWORK: -1,
    InfraEntityKind.IMAGE: -2,
}


def get_layer(kind: InfraEntityKind) -> int:
    """Get semantic layer for entity kind."""
    return SEMANTIC_LAYERS.get(kind, 0)


# =============================================================================
# Semantic Layout Algorithm
# =============================================================================


@dataclass
class EntityStack:
    """
    A vertical stack of related entities.

    Represents a service → deployment → pod(s) chain that should
    be rendered as a tight vertical column.
    """

    stack_id: str
    namespace: str
    entities: list[InfraEntity] = field(default_factory=list)
    x: float = 0.0  # X position of this stack


@dataclass
class NamespaceSlice:
    """
    A namespace "slice" containing multiple stacks.

    Each namespace gets a Z position, and its stacks spread along X.
    """

    namespace: str
    stacks: list[EntityStack] = field(default_factory=list)
    z: float = 0.0  # Z position of this namespace slice


def calculate_semantic_layout(
    entities: list[InfraEntity],
    connections: list[InfraConnection],
    config: LayoutConfig | None = None,
) -> None:
    """
    Calculate semantic layout positions for infrastructure entities.

    This is the main entry point for principled layout (v2 - compact stacks).

    The algorithm:
    1. Build connection graph to identify related entities
    2. Group entities into "stacks" (service→deploy→pods chains)
    3. Group stacks into namespace "slices"
    4. Arrange slices in Z (depth)
    5. Arrange stacks in X (within each slice)
    6. Assign Y based on abstraction layer
    7. Adjust Z slightly for health (attention)

    Modifies entities in-place to set x, y, z coordinates.

    Args:
        entities: List of infrastructure entities
        connections: List of connections between entities
        config: Layout configuration (uses defaults if None)
    """
    if not entities:
        return

    config = config or LayoutConfig()

    # Phase 1: Build connection graph
    adjacency = _build_adjacency(entities, connections)

    # Phase 2: Identify stacks (connected components within namespace)
    slices = _identify_stacks(entities, adjacency)

    # Phase 3: Assign namespace Z positions
    _assign_namespace_depth(slices, config)

    # Phase 4: Assign stack X positions within each namespace
    _assign_stack_positions(slices, config)

    # Phase 5: Assign layer Y positions
    _assign_layer_positions(entities, config)

    # Phase 6: Assign entity X from its stack
    _apply_stack_x_positions(slices)

    # Phase 7: Adjust Z for health (attention within slice)
    _assign_health_depth(entities, config)

    # Phase 8: Center and normalize
    _normalize_positions(entities, config)


def _build_adjacency(
    entities: list[InfraEntity],
    connections: list[InfraConnection],
) -> dict[str, set[str]]:
    """Build bidirectional adjacency map from connections."""
    entity_ids = {e.id for e in entities}
    adjacency: dict[str, set[str]] = {e.id: set() for e in entities}

    for conn in connections:
        if conn.source_id in entity_ids and conn.target_id in entity_ids:
            adjacency[conn.source_id].add(conn.target_id)
            adjacency[conn.target_id].add(conn.source_id)

    return adjacency


def _identify_stacks(
    entities: list[InfraEntity],
    adjacency: dict[str, set[str]],
) -> list[NamespaceSlice]:
    """
    Identify stacks of related entities using connected components.

    Within each namespace, finds groups of connected entities and
    creates a stack for each group. Unconnected entities get their own stack.
    """
    # Group by namespace first
    by_namespace: dict[str, list[InfraEntity]] = {}
    for entity in entities:
        ns = entity.namespace or "(none)"
        if ns not in by_namespace:
            by_namespace[ns] = []
        by_namespace[ns].append(entity)

    slices: list[NamespaceSlice] = []

    for ns in sorted(by_namespace.keys()):
        ns_entities = by_namespace[ns]
        ns_entity_ids = {e.id for e in ns_entities}

        # Find connected components within this namespace
        visited: set[str] = set()
        stacks: list[EntityStack] = []
        stack_counter = 0

        for entity in ns_entities:
            if entity.id in visited:
                continue

            # BFS to find connected component
            component: list[InfraEntity] = []
            queue = [entity]

            while queue:
                current = queue.pop(0)
                if current.id in visited:
                    continue
                visited.add(current.id)
                component.append(current)

                # Add neighbors that are in the same namespace
                for neighbor_id in adjacency.get(current.id, set()):
                    if neighbor_id in ns_entity_ids and neighbor_id not in visited:
                        neighbor = next(
                            (e for e in ns_entities if e.id == neighbor_id), None
                        )
                        if neighbor:
                            queue.append(neighbor)

            # Create stack for this component
            stack = EntityStack(
                stack_id=f"{ns}-stack-{stack_counter}",
                namespace=ns,
                entities=component,
            )
            stacks.append(stack)
            stack_counter += 1

        # Create namespace slice
        slice_obj = NamespaceSlice(namespace=ns, stacks=stacks)
        slices.append(slice_obj)

    return slices


def _assign_namespace_depth(
    slices: list[NamespaceSlice],
    config: LayoutConfig,
) -> None:
    """Assign Z positions to namespace slices."""
    if not slices:
        return

    # Center namespaces around Z=0
    total_depth = (len(slices) - 1) * config.namespace_depth
    start_z = -total_depth / 2

    for i, slice_obj in enumerate(slices):
        slice_obj.z = start_z + i * config.namespace_depth


def _assign_stack_positions(
    slices: list[NamespaceSlice],
    config: LayoutConfig,
) -> None:
    """Assign X positions to stacks within each namespace slice."""
    for slice_obj in slices:
        if not slice_obj.stacks:
            continue

        # Sort stacks by size (larger stacks in center for visual balance)
        sorted_stacks = sorted(slice_obj.stacks, key=lambda s: len(s.entities), reverse=True)

        # Spread stacks horizontally, centered at X=0
        n = len(sorted_stacks)
        total_width = (n - 1) * config.stack_spacing
        start_x = -total_width / 2

        # Interleave assignment for balance (large in center)
        positions = []
        for i in range(n):
            positions.append(start_x + i * config.stack_spacing)

        # Assign positions - alternate sides for visual balance
        left_idx = n // 2 - 1
        right_idx = n // 2

        for i, stack in enumerate(sorted_stacks):
            if i % 2 == 0 and right_idx < n:
                stack.x = positions[right_idx]
                right_idx += 1
            elif left_idx >= 0:
                stack.x = positions[left_idx]
                left_idx -= 1
            elif right_idx < n:
                stack.x = positions[right_idx]
                right_idx += 1


def _apply_stack_x_positions(slices: list[NamespaceSlice]) -> None:
    """Apply stack X positions to all entities in each stack."""
    for slice_obj in slices:
        for stack in slice_obj.stacks:
            # All entities in a stack share the same X
            for entity in stack.entities:
                entity.x = stack.x
                # Set base Z from namespace slice
                entity.z = slice_obj.z


# Legacy function for backward compatibility
class NamespaceCluster:
    """Legacy: Represents a cluster of entities within a namespace."""

    def __init__(self, namespace: str):
        self.namespace = namespace
        self.entities: list[InfraEntity] = []
        self.center_x: float = 0.0
        self.width: float = 0.0


def _cluster_by_namespace(entities: list[InfraEntity]) -> list[NamespaceCluster]:
    """Group entities by namespace (legacy)."""
    clusters_by_ns: dict[str, NamespaceCluster] = {}

    for entity in entities:
        ns = entity.namespace or "(none)"
        if ns not in clusters_by_ns:
            clusters_by_ns[ns] = NamespaceCluster(namespace=ns)
        clusters_by_ns[ns].entities.append(entity)

    # Sort namespaces alphabetically for consistent layout
    return [clusters_by_ns[ns] for ns in sorted(clusters_by_ns.keys())]


def _assign_namespace_positions(
    clusters: list[NamespaceCluster],
    config: LayoutConfig,
) -> None:
    """Assign X center positions to namespace clusters."""
    total_width = (len(clusters) - 1) * config.namespace_spacing
    start_x = -total_width / 2

    for i, cluster in enumerate(clusters):
        cluster.center_x = start_x + i * config.namespace_spacing
        # Width based on entity count (for spreading)
        cluster.width = max(
            config.entity_spacing * 2,
            math.sqrt(len(cluster.entities)) * config.entity_spacing,
        )


def _assign_layer_positions(
    entities: list[InfraEntity],
    config: LayoutConfig,
) -> None:
    """Assign Y positions based on semantic layer."""
    # Find layer range
    min_layer = min(get_layer(e.kind) for e in entities)
    max_layer = max(get_layer(e.kind) for e in entities)

    layer_range = max_layer - min_layer
    if layer_range == 0:
        layer_range = 1  # Avoid division by zero

    for entity in entities:
        layer = get_layer(entity.kind)
        # Normalize to 0-1, then scale
        normalized = (layer - min_layer) / layer_range
        entity.y = normalized * config.layer_spacing * layer_range


def _spread_within_clusters(
    clusters: list[NamespaceCluster],
    config: LayoutConfig,
) -> None:
    """Spread entities within each namespace cluster."""
    for cluster in clusters:
        # Group by layer for spreading
        by_layer: dict[int, list[InfraEntity]] = {}
        for entity in cluster.entities:
            layer = get_layer(entity.kind)
            if layer not in by_layer:
                by_layer[layer] = []
            by_layer[layer].append(entity)

        # Spread each layer horizontally within the cluster
        for layer_entities in by_layer.values():
            count = len(layer_entities)
            if count == 1:
                layer_entities[0].x = cluster.center_x
            else:
                # Spread evenly across cluster width
                spread = min(cluster.width, count * config.entity_spacing)
                start_x = cluster.center_x - spread / 2
                step = spread / (count - 1) if count > 1 else 0

                for i, entity in enumerate(layer_entities):
                    entity.x = start_x + i * step


def _assign_health_depth(
    entities: list[InfraEntity],
    config: LayoutConfig,
) -> None:
    """
    Adjust Z positions based on health (attention principle).

    Unhealthy entities come forward RELATIVE to their namespace slice.
    This follows "depth is information" from the projection protocol.

    The base Z was already set from the namespace slice in _apply_stack_x_positions.
    Here we add a health-based offset to bring unhealthy entities forward.
    """
    for entity in entities:
        health_offset = 0.0

        if entity.health >= config.warning_threshold:
            # Healthy: no offset (stays at namespace slice Z)
            health_offset = 0.0
        elif entity.health >= config.critical_threshold:
            # Warning: comes forward proportionally
            normalized = 1.0 - (entity.health - config.critical_threshold) / (
                config.warning_threshold - config.critical_threshold
            )
            health_offset = normalized * config.health_depth_scale * 0.5
        else:
            # Critical: full foreground offset
            normalized = 1.0 - entity.health / config.critical_threshold
            health_offset = (0.5 + normalized * 0.5) * config.health_depth_scale

        # Add health offset to existing Z (which has namespace depth)
        entity.z += health_offset


def _refine_with_connections(
    entities: list[InfraEntity],
    connections: list[InfraConnection],
    config: LayoutConfig,
) -> None:
    """
    Apply connection-aware refinement.

    Connected entities should be closer together within their layers.
    Uses a limited force-directed approach that respects semantic layers.
    """
    if not config.refinement_iterations:
        return

    entity_map = {e.id: e for e in entities}

    # Build adjacency
    adjacency: dict[str, set[str]] = {e.id: set() for e in entities}
    for conn in connections:
        if conn.source_id in adjacency and conn.target_id in entity_map:
            adjacency[conn.source_id].add(conn.target_id)
        if conn.target_id in adjacency and conn.source_id in entity_map:
            adjacency[conn.target_id].add(conn.source_id)

    for _ in range(config.refinement_iterations):
        forces: dict[str, tuple[float, float]] = {e.id: (0.0, 0.0) for e in entities}

        # Repulsion between entities in same layer and namespace
        for i, e1 in enumerate(entities):
            for e2 in entities[i + 1:]:
                # Only repel within same namespace
                if e1.namespace != e2.namespace:
                    continue

                dx = e1.x - e2.x
                dy = e1.y - e2.y
                dist = math.sqrt(dx * dx + dy * dy) + 0.1

                if dist < config.entity_spacing * 2:
                    force = config.repulsion_strength / (dist * dist)
                    # Only apply X force (preserve Y layer)
                    fx = dx / dist * force * 0.5
                    forces[e1.id] = (forces[e1.id][0] + fx, forces[e1.id][1])
                    forces[e2.id] = (forces[e2.id][0] - fx, forces[e2.id][1])

        # Attraction along connections (X only, to group related entities)
        for source_id, neighbors in adjacency.items():
            if source_id not in entity_map:
                continue
            source = entity_map[source_id]

            for target_id in neighbors:
                if target_id not in entity_map:
                    continue
                target = entity_map[target_id]

                # Only attract within same namespace
                if source.namespace != target.namespace:
                    continue

                dx = target.x - source.x
                dist = abs(dx) + 0.1

                force = dist * config.spring_strength
                fx = (dx / dist) * force if dist > 0.1 else 0

                forces[source_id] = (forces[source_id][0] + fx * 0.5, forces[source_id][1])
                forces[target_id] = (forces[target_id][0] - fx * 0.5, forces[target_id][1])

        # Apply forces (X only—preserve semantic Y layers)
        for entity in entities:
            fx, _ = forces[entity.id]
            entity.x += fx * 0.1


def _normalize_positions(
    entities: list[InfraEntity],
    config: LayoutConfig,
) -> None:
    """Center the layout and ensure it fits within bounds."""
    if not entities:
        return

    # Find current bounds
    min_x = min(e.x for e in entities)
    max_x = max(e.x for e in entities)
    min_y = min(e.y for e in entities)
    max_y = max(e.y for e in entities)

    # Center
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    for entity in entities:
        entity.x -= center_x
        entity.y -= center_y

    # Scale if needed
    current_width = max_x - min_x
    current_height = max_y - min_y

    scale_x = config.max_x / current_width if current_width > config.max_x else 1.0
    scale_y = config.max_y / current_height if current_height > config.max_y else 1.0
    scale = min(scale_x, scale_y)

    if scale < 1.0:
        for entity in entities:
            entity.x *= scale
            entity.y *= scale


# =============================================================================
# Layout Application
# =============================================================================


def apply_layout(
    entities: list[InfraEntity],
    connections: list[InfraConnection],
    strategy: LayoutStrategy = LayoutStrategy.SEMANTIC,
    config: LayoutConfig | None = None,
) -> None:
    """
    Apply layout to entities using the specified strategy.

    This is the main API for layout calculation.

    Args:
        entities: List of infrastructure entities
        connections: List of connections
        strategy: Layout strategy to use
        config: Configuration (uses defaults if None)
    """
    config = config or LayoutConfig()
    config.strategy = strategy

    if strategy == LayoutStrategy.SEMANTIC:
        calculate_semantic_layout(entities, connections, config)
    elif strategy == LayoutStrategy.HIERARCHICAL:
        # Strict hierarchical (no refinement)
        hierarchical_config = LayoutConfig(
            refinement_iterations=0,
            namespace_spacing=config.namespace_spacing,
            layer_spacing=config.layer_spacing,
        )
        calculate_semantic_layout(entities, connections, hierarchical_config)
    else:
        # Fall back to original force-directed
        _force_directed_layout(entities, connections, config)


def _force_directed_layout(
    entities: list[InfraEntity],
    connections: list[InfraConnection],
    config: LayoutConfig,
) -> None:
    """
    Classic force-directed layout (fallback).

    This is the original algorithm, preserved for comparison.
    """
    import random

    # Initialize random positions
    for entity in entities:
        entity.x = random.uniform(-10, 10)
        entity.y = random.uniform(-10, 10)
        entity.z = random.uniform(-2, 2)

    entity_map = {e.id: e for e in entities}
    connections_by_entity: dict[str, list[str]] = {}
    for conn in connections:
        if conn.source_id not in connections_by_entity:
            connections_by_entity[conn.source_id] = []
        connections_by_entity[conn.source_id].append(conn.target_id)

    for _ in range(config.refinement_iterations * 2):
        forces: dict[str, tuple[float, float, float]] = {
            e.id: (0.0, 0.0, 0.0) for e in entities
        }

        # Repulsion
        for i, e1 in enumerate(entities):
            for e2 in entities[i + 1:]:
                dx = e1.x - e2.x
                dy = e1.y - e2.y
                dz = e1.z - e2.z
                dist = math.sqrt(dx * dx + dy * dy + dz * dz) + 0.1

                force = config.repulsion_strength / (dist * dist)

                fx, fy, fz = forces[e1.id]
                forces[e1.id] = (
                    fx + dx / dist * force,
                    fy + dy / dist * force,
                    fz + dz / dist * force,
                )
                fx, fy, fz = forces[e2.id]
                forces[e2.id] = (
                    fx - dx / dist * force,
                    fy - dy / dist * force,
                    fz - dz / dist * force,
                )

        # Attraction
        for source_id, targets in connections_by_entity.items():
            if source_id not in entity_map:
                continue
            source = entity_map[source_id]

            for target_id in targets:
                if target_id not in entity_map:
                    continue
                target = entity_map[target_id]

                dx = target.x - source.x
                dy = target.y - source.y
                dz = target.z - source.z
                dist = math.sqrt(dx * dx + dy * dy + dz * dz) + 0.1

                force = dist * config.spring_strength

                fx, fy, fz = forces[source_id]
                forces[source_id] = (
                    fx + dx / dist * force,
                    fy + dy / dist * force,
                    fz + dz / dist * force,
                )
                fx, fy, fz = forces[target_id]
                forces[target_id] = (
                    fx - dx / dist * force,
                    fy - dy / dist * force,
                    fz - dz / dist * force,
                )

        # Apply
        for entity in entities:
            fx, fy, fz = forces[entity.id]
            entity.x += fx * 0.1
            entity.y += fy * 0.1
            entity.z += fz * 0.1

    # Group by namespace (post-hoc adjustment)
    namespaces = sorted(set(e.namespace or "(none)" for e in entities))
    namespace_y = {ns: i * 5 for i, ns in enumerate(namespaces)}

    for entity in entities:
        ns = entity.namespace or "(none)"
        entity.y = namespace_y[ns] + entity.y * 0.3
