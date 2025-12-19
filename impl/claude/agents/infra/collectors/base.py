"""
Base Infrastructure Collector

Abstract base class for all infrastructure data collectors.

Collectors are responsible for:
1. Connecting to their data source (K8s API, Docker socket, etc.)
2. Collecting topology snapshots on demand
3. Streaming real-time events
4. Calculating entity positions using force-directed layout

@see plans/gestalt-live-infrastructure.md
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator

from ..models import (
    InfraConnection,
    InfraEntity,
    InfraEvent,
    InfraTopology,
    TopologyUpdate,
)

# =============================================================================
# Configuration
# =============================================================================


@dataclass
class CollectorConfig:
    """Base configuration for all collectors."""

    # Polling interval for topology updates (seconds)
    poll_interval: float = 5.0

    # Maximum entities to return (for large clusters)
    max_entities: int = 1000

    # Whether to calculate positions (force-directed layout)
    calculate_positions: bool = True

    # Position calculation parameters
    layout_iterations: int = 100
    layout_spring_strength: float = 0.1
    layout_repulsion_strength: float = 100.0


# =============================================================================
# Base Collector
# =============================================================================


class BaseCollector(ABC):
    """
    Abstract base class for infrastructure collectors.

    Subclasses must implement:
    - collect_topology(): Collect current topology snapshot
    - stream_events(): Stream real-time events

    Optional overrides:
    - connect(): Establish connection to data source
    - disconnect(): Close connection
    - health_check(): Check if data source is accessible
    """

    def __init__(self, config: CollectorConfig | None = None):
        self.config = config or CollectorConfig()
        self._connected = False
        self._last_topology: InfraTopology | None = None

    # =========================================================================
    # Connection Management
    # =========================================================================

    async def connect(self) -> None:
        """Establish connection to the data source."""
        self._connected = True

    async def disconnect(self) -> None:
        """Close connection to the data source."""
        self._connected = False

    async def health_check(self) -> bool:
        """Check if the data source is accessible."""
        return self._connected

    @property
    def is_connected(self) -> bool:
        """Whether the collector is currently connected."""
        return self._connected

    # =========================================================================
    # Topology Collection
    # =========================================================================

    @abstractmethod
    async def collect_topology(self) -> InfraTopology:
        """
        Collect current infrastructure topology.

        Returns:
            InfraTopology: Complete topology snapshot with entities and connections
        """
        ...

    async def collect_topology_diff(
        self,
        since: datetime | None = None,
    ) -> list[TopologyUpdate]:
        """
        Collect topology changes since a timestamp.

        Default implementation does a full refresh and diffs against last known state.
        Subclasses can override for more efficient implementations.

        IMPORTANT: Preserves positions for existing entities to prevent jumping.
        """
        new_topology = await self.collect_topology()

        if self._last_topology is None:
            self._last_topology = new_topology
            return [
                TopologyUpdate(kind="full", timestamp=new_topology.timestamp, topology=new_topology)
            ]

        # Preserve positions from previous topology for existing entities
        old_positions = {e.id: (e.x, e.y, e.z) for e in self._last_topology.entities}
        for entity in new_topology.entities:
            if entity.id in old_positions:
                entity.x, entity.y, entity.z = old_positions[entity.id]

        updates = self._diff_topologies(self._last_topology, new_topology)
        self._last_topology = new_topology
        return updates

    def _diff_topologies(
        self,
        old: InfraTopology,
        new: InfraTopology,
    ) -> list[TopologyUpdate]:
        """Calculate incremental updates between two topologies."""
        updates = []
        now = new.timestamp

        old_entities = {e.id: e for e in old.entities}
        new_entities = {e.id: e for e in new.entities}

        # Find added entities
        for entity_id, entity in new_entities.items():
            if entity_id not in old_entities:
                updates.append(
                    TopologyUpdate(
                        kind="entity_added",
                        timestamp=now,
                        entity=entity,
                    )
                )

        # Find removed entities
        for entity_id in old_entities:
            if entity_id not in new_entities:
                updates.append(
                    TopologyUpdate(
                        kind="entity_removed",
                        timestamp=now,
                        entity=old_entities[entity_id],
                    )
                )

        # Find updated entities (changed metrics or status)
        for entity_id, new_entity in new_entities.items():
            if entity_id in old_entities:
                old_entity = old_entities[entity_id]
                if self._entity_changed(old_entity, new_entity):
                    updates.append(
                        TopologyUpdate(
                            kind="entity_updated",
                            timestamp=now,
                            entity=new_entity,
                        )
                    )

        # Similar for connections...
        old_connections = {c.id: c for c in old.connections}
        new_connections = {c.id: c for c in new.connections}

        for conn_id, conn in new_connections.items():
            if conn_id not in old_connections:
                updates.append(
                    TopologyUpdate(
                        kind="connection_added",
                        timestamp=now,
                        connection=conn,
                    )
                )

        for conn_id in old_connections:
            if conn_id not in new_connections:
                updates.append(
                    TopologyUpdate(
                        kind="connection_removed",
                        timestamp=now,
                        connection=old_connections[conn_id],
                    )
                )

        return updates

    def _entity_changed(self, old: InfraEntity, new: InfraEntity) -> bool:
        """Check if an entity has changed significantly."""
        # Status change is always significant
        if old.status != new.status:
            return True

        # Health change > 0.1 is significant
        if abs(old.health - new.health) > 0.1:
            return True

        # Significant metric changes
        if abs(old.cpu_percent - new.cpu_percent) > 10:
            return True
        if old.memory_limit and old.memory_limit > 0:
            old_mem_pct = old.memory_bytes / old.memory_limit
            new_mem_pct = new.memory_bytes / (new.memory_limit or old.memory_limit)
            if abs(old_mem_pct - new_mem_pct) > 0.1:
                return True

        return False

    # =========================================================================
    # Event Streaming
    # =========================================================================

    @abstractmethod
    async def stream_events(self) -> AsyncIterator[InfraEvent]:
        """
        Stream real-time infrastructure events.

        Yields:
            InfraEvent: Events as they occur
        """
        ...

    async def stream_topology_updates(self) -> AsyncIterator[TopologyUpdate]:
        """
        Stream topology updates at the configured poll interval.

        Yields:
            TopologyUpdate: Incremental topology updates
        """
        import asyncio

        while self._connected:
            try:
                updates = await self.collect_topology_diff()
                for update in updates:
                    yield update
            except Exception as e:
                # Log error but continue streaming
                print(f"Error collecting topology: {e}")

            await asyncio.sleep(self.config.poll_interval)

    # =========================================================================
    # Layout Calculation
    # =========================================================================

    def calculate_positions(
        self,
        entities: list[InfraEntity],
        connections: list[InfraConnection],
    ) -> None:
        """
        Calculate 3D positions for entities using semantic layout.

        Follows the Projection Protocol principles:
        - Y-axis = abstraction layer (services → deployments → pods)
        - X-axis = namespace clustering
        - Z-axis = health/attention (unhealthy forward)

        Modifies entities in-place to set x, y, z coordinates.

        @see impl/claude/agents/infra/layout.py
        @see spec/protocols/projection.md (Layout Projection, 3D Target Projection)
        """
        if not self.config.calculate_positions:
            return

        from ..layout import LayoutConfig, LayoutStrategy, apply_layout

        # Configure layout based on collector config
        layout_config = LayoutConfig(
            strategy=LayoutStrategy.SEMANTIC,
            refinement_iterations=self.config.layout_iterations,
            spring_strength=self.config.layout_spring_strength,
            repulsion_strength=self.config.layout_repulsion_strength,
        )

        apply_layout(entities, connections, LayoutStrategy.SEMANTIC, layout_config)
