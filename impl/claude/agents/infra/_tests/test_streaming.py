"""
Tests for Infrastructure Topology Streaming (Phase 2).

Tests cover:
- TopologyUpdate model serialization
- Diff algorithm correctness
- Entity change detection thresholds
- Event streaming format

@see plans/_continuations/gestalt-live-infra-phase2.md
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from agents.infra.collectors.base import BaseCollector, CollectorConfig
from agents.infra.models import (
    InfraConnection,
    InfraConnectionKind,
    InfraEntity,
    InfraEntityKind,
    InfraEntityStatus,
    InfraTopology,
    TopologyUpdate,
    TopologyUpdateKind,
)

# =============================================================================
# Fixtures
# =============================================================================


def make_entity(
    id: str = "pod/default/test-pod",
    kind: InfraEntityKind = InfraEntityKind.POD,
    name: str = "test-pod",
    namespace: str = "default",
    status: InfraEntityStatus = InfraEntityStatus.RUNNING,
    health: float = 0.9,
    cpu_percent: float = 25.0,
    memory_bytes: int = 1024 * 1024 * 100,  # 100MB
    memory_limit: int | None = None,
) -> InfraEntity:
    """Create a test entity."""
    return InfraEntity(
        id=id,
        kind=kind,
        name=name,
        namespace=namespace,
        status=status,
        health=health,
        cpu_percent=cpu_percent,
        memory_bytes=memory_bytes,
        memory_limit=memory_limit,
        source="test",
    )


def make_connection(
    source_id: str = "svc/default/test-svc",
    target_id: str = "pod/default/test-pod",
    kind: InfraConnectionKind = InfraConnectionKind.SELECTS,
) -> InfraConnection:
    """Create a test connection."""
    return InfraConnection(
        source_id=source_id,
        target_id=target_id,
        kind=kind,
    )


def make_topology(
    entities: list[InfraEntity] | None = None,
    connections: list[InfraConnection] | None = None,
) -> InfraTopology:
    """Create a test topology."""
    return InfraTopology(
        entities=entities or [],
        connections=connections or [],
        timestamp=datetime.now(timezone.utc),
    )


# =============================================================================
# TopologyUpdate Model Tests
# =============================================================================


class TestTopologyUpdateModel:
    """Tests for TopologyUpdate dataclass."""

    def test_update_kind_full(self):
        """Full update includes entire topology."""
        topology = make_topology([make_entity()])
        update = TopologyUpdate(
            kind=TopologyUpdateKind.FULL,
            timestamp=datetime.now(timezone.utc),
            topology=topology,
        )

        assert update.kind == TopologyUpdateKind.FULL
        assert update.topology is not None
        assert update.entity is None
        assert update.connection is None

    def test_update_kind_entity_added(self):
        """Entity added update includes entity."""
        entity = make_entity()
        update = TopologyUpdate(
            kind=TopologyUpdateKind.ENTITY_ADDED,
            timestamp=datetime.now(timezone.utc),
            entity=entity,
        )

        assert update.kind == TopologyUpdateKind.ENTITY_ADDED
        assert update.entity is not None
        assert update.entity.id == entity.id
        assert update.topology is None

    def test_update_kind_entity_updated(self):
        """Entity updated includes the new entity state."""
        entity = make_entity(health=0.5)
        update = TopologyUpdate(
            kind=TopologyUpdateKind.ENTITY_UPDATED,
            timestamp=datetime.now(timezone.utc),
            entity=entity,
        )

        assert update.kind == TopologyUpdateKind.ENTITY_UPDATED
        assert update.entity.health == 0.5

    def test_update_kind_entity_removed(self):
        """Entity removed includes the removed entity."""
        entity = make_entity()
        update = TopologyUpdate(
            kind=TopologyUpdateKind.ENTITY_REMOVED,
            timestamp=datetime.now(timezone.utc),
            entity=entity,
        )

        assert update.kind == TopologyUpdateKind.ENTITY_REMOVED
        assert update.entity is not None

    def test_update_kind_connection_added(self):
        """Connection added includes connection."""
        conn = make_connection()
        update = TopologyUpdate(
            kind=TopologyUpdateKind.CONNECTION_ADDED,
            timestamp=datetime.now(timezone.utc),
            connection=conn,
        )

        assert update.kind == TopologyUpdateKind.CONNECTION_ADDED
        assert update.connection is not None

    def test_update_kind_metrics(self):
        """Metrics update includes metrics dict."""
        update = TopologyUpdate(
            kind=TopologyUpdateKind.METRICS,
            timestamp=datetime.now(timezone.utc),
            metrics={"pod/default/test": {"cpu_percent": 50.0, "health": 0.8}},
        )

        assert update.kind == TopologyUpdateKind.METRICS
        assert update.metrics is not None
        assert "pod/default/test" in update.metrics


# =============================================================================
# Diff Algorithm Tests
# =============================================================================


class TestDiffAlgorithm:
    """Tests for topology diff calculation."""

    @pytest.fixture
    def collector(self):
        """Create a test collector with mocked topology."""

        class TestCollector(BaseCollector):
            def __init__(self):
                super().__init__(CollectorConfig())
                self._topology: InfraTopology | None = None

            def set_topology(self, topology: InfraTopology):
                self._topology = topology

            async def collect_topology(self) -> InfraTopology:
                return self._topology or make_topology()

            async def stream_events(self):
                return
                yield  # Make it a generator

        return TestCollector()

    @pytest.mark.asyncio
    async def test_initial_diff_returns_full(self, collector):
        """First diff should return full topology."""
        collector.set_topology(make_topology([make_entity()]))

        updates = await collector.collect_topology_diff()

        assert len(updates) == 1
        assert updates[0].kind == TopologyUpdateKind.FULL or updates[0].kind == "full"
        assert updates[0].topology is not None

    @pytest.mark.asyncio
    async def test_entity_add_detected(self, collector):
        """New entities generate ENTITY_ADDED updates."""
        # Initial topology with one entity
        entity1 = make_entity(id="pod/default/pod-1", name="pod-1")
        collector.set_topology(make_topology([entity1]))
        await collector.collect_topology_diff()  # Initialize

        # Add a new entity
        entity2 = make_entity(id="pod/default/pod-2", name="pod-2")
        collector.set_topology(make_topology([entity1, entity2]))
        updates = await collector.collect_topology_diff()

        # Should have one entity_added update
        added = [
            u
            for u in updates
            if u.kind == TopologyUpdateKind.ENTITY_ADDED or u.kind == "entity_added"
        ]
        assert len(added) == 1
        assert added[0].entity.id == "pod/default/pod-2"

    @pytest.mark.asyncio
    async def test_entity_remove_detected(self, collector):
        """Removed entities generate ENTITY_REMOVED updates."""
        # Initial topology with two entities
        entity1 = make_entity(id="pod/default/pod-1", name="pod-1")
        entity2 = make_entity(id="pod/default/pod-2", name="pod-2")
        collector.set_topology(make_topology([entity1, entity2]))
        await collector.collect_topology_diff()  # Initialize

        # Remove one entity
        collector.set_topology(make_topology([entity1]))
        updates = await collector.collect_topology_diff()

        # Should have one entity_removed update
        removed = [
            u
            for u in updates
            if u.kind == TopologyUpdateKind.ENTITY_REMOVED or u.kind == "entity_removed"
        ]
        assert len(removed) == 1
        assert removed[0].entity.id == "pod/default/pod-2"

    @pytest.mark.asyncio
    async def test_entity_update_detected(self, collector):
        """Changed entities generate ENTITY_UPDATED updates."""
        # Initial topology
        entity = make_entity(health=0.9)
        collector.set_topology(make_topology([entity]))
        await collector.collect_topology_diff()  # Initialize

        # Change health significantly (> 0.1 threshold)
        entity_updated = make_entity(health=0.5)
        collector.set_topology(make_topology([entity_updated]))
        updates = await collector.collect_topology_diff()

        # Should have one entity_updated update
        updated = [
            u
            for u in updates
            if u.kind == TopologyUpdateKind.ENTITY_UPDATED or u.kind == "entity_updated"
        ]
        assert len(updated) == 1
        assert updated[0].entity.health == 0.5

    @pytest.mark.asyncio
    async def test_small_changes_ignored(self, collector):
        """Small metric changes below threshold don't generate updates."""
        # Initial topology
        entity = make_entity(health=0.9, cpu_percent=25.0)
        collector.set_topology(make_topology([entity]))
        await collector.collect_topology_diff()  # Initialize

        # Small change (within thresholds: health < 0.1, cpu < 10)
        entity_small_change = make_entity(health=0.88, cpu_percent=30.0)
        collector.set_topology(make_topology([entity_small_change]))
        updates = await collector.collect_topology_diff()

        # Should have no updates (changes are below threshold)
        assert len(updates) == 0

    @pytest.mark.asyncio
    async def test_status_change_always_detected(self, collector):
        """Status changes always generate updates regardless of threshold."""
        # Initial topology
        entity = make_entity(status=InfraEntityStatus.RUNNING)
        collector.set_topology(make_topology([entity]))
        await collector.collect_topology_diff()  # Initialize

        # Change status
        entity_failed = make_entity(status=InfraEntityStatus.FAILED)
        collector.set_topology(make_topology([entity_failed]))
        updates = await collector.collect_topology_diff()

        # Should have one entity_updated update
        updated = [
            u
            for u in updates
            if u.kind == TopologyUpdateKind.ENTITY_UPDATED or u.kind == "entity_updated"
        ]
        assert len(updated) == 1

    @pytest.mark.asyncio
    async def test_no_update_for_unchanged(self, collector):
        """Unchanged entities don't generate updates."""
        # Initial topology
        entity = make_entity()
        collector.set_topology(make_topology([entity]))
        await collector.collect_topology_diff()  # Initialize

        # Same topology
        collector.set_topology(make_topology([entity]))
        updates = await collector.collect_topology_diff()

        # Should have no updates
        assert len(updates) == 0

    @pytest.mark.asyncio
    async def test_connection_add_detected(self, collector):
        """New connections generate CONNECTION_ADDED updates."""
        entity = make_entity()
        collector.set_topology(make_topology([entity], []))
        await collector.collect_topology_diff()  # Initialize

        # Add a connection
        conn = make_connection(target_id=entity.id)
        collector.set_topology(make_topology([entity], [conn]))
        updates = await collector.collect_topology_diff()

        # Should have one connection_added update
        added = [
            u
            for u in updates
            if u.kind == TopologyUpdateKind.CONNECTION_ADDED
            or u.kind == "connection_added"
        ]
        assert len(added) == 1

    @pytest.mark.asyncio
    async def test_connection_remove_detected(self, collector):
        """Removed connections generate CONNECTION_REMOVED updates."""
        entity = make_entity()
        conn = make_connection(target_id=entity.id)
        collector.set_topology(make_topology([entity], [conn]))
        await collector.collect_topology_diff()  # Initialize

        # Remove connection
        collector.set_topology(make_topology([entity], []))
        updates = await collector.collect_topology_diff()

        # Should have one connection_removed update
        removed = [
            u
            for u in updates
            if u.kind == TopologyUpdateKind.CONNECTION_REMOVED
            or u.kind == "connection_removed"
        ]
        assert len(removed) == 1


# =============================================================================
# Change Detection Threshold Tests
# =============================================================================


class TestChangeThresholds:
    """Tests for entity change detection thresholds."""

    @pytest.fixture
    def collector(self):
        """Create a test collector."""

        class TestCollector(BaseCollector):
            def __init__(self):
                super().__init__(CollectorConfig())

            async def collect_topology(self) -> InfraTopology:
                return make_topology()

            async def stream_events(self):
                return
                yield

        return TestCollector()

    def test_health_threshold(self, collector):
        """Health change > 0.1 is significant."""
        old = make_entity(health=0.9)
        new_small = make_entity(health=0.85)  # 0.05 change - not significant
        new_large = make_entity(health=0.7)  # 0.2 change - significant

        assert not collector._entity_changed(old, new_small)
        assert collector._entity_changed(old, new_large)

    def test_cpu_threshold(self, collector):
        """CPU change > 10% is significant."""
        old = make_entity(cpu_percent=25.0)
        new_small = make_entity(cpu_percent=30.0)  # 5% change - not significant
        new_large = make_entity(cpu_percent=50.0)  # 25% change - significant

        assert not collector._entity_changed(old, new_small)
        assert collector._entity_changed(old, new_large)

    def test_status_always_significant(self, collector):
        """Status change is always significant."""
        old = make_entity(status=InfraEntityStatus.RUNNING)
        new = make_entity(status=InfraEntityStatus.PENDING)

        assert collector._entity_changed(old, new)

    def test_memory_threshold_with_limit(self, collector):
        """Memory change > 10% of limit is significant."""
        old = make_entity(
            memory_bytes=100 * 1024 * 1024,  # 100MB
            memory_limit=500 * 1024 * 1024,  # 500MB limit
        )
        # 105MB - 5MB change (1% of limit) - not significant
        new_small = make_entity(
            memory_bytes=105 * 1024 * 1024,
            memory_limit=500 * 1024 * 1024,
        )
        # 200MB - 100MB change (20% of limit) - significant
        new_large = make_entity(
            memory_bytes=200 * 1024 * 1024,
            memory_limit=500 * 1024 * 1024,
        )

        assert not collector._entity_changed(old, new_small)
        assert collector._entity_changed(old, new_large)


# =============================================================================
# Streaming Topology Tests
# =============================================================================


class TestPositionPreservation:
    """Tests for position preservation on topology updates."""

    @pytest.fixture
    def collector(self):
        """Create a test collector with controlled topology."""

        class TestCollector(BaseCollector):
            def __init__(self):
                super().__init__(CollectorConfig())
                self._topology: InfraTopology | None = None

            def set_topology(self, topology: InfraTopology):
                self._topology = topology

            async def collect_topology(self) -> InfraTopology:
                return self._topology or make_topology()

            async def stream_events(self):
                return
                yield

        return TestCollector()

    @pytest.mark.asyncio
    async def test_positions_preserved_on_update(self, collector):
        """Existing entity positions should not change on update."""
        # Initial topology with specific position
        entity = make_entity(id="pod/default/pod-1")
        entity.x, entity.y, entity.z = 5.0, 10.0, -3.0
        collector.set_topology(make_topology([entity]))

        # First diff - establishes baseline
        await collector.collect_topology_diff()

        # Update entity (different health, but SAME entity by ID)
        updated_entity = make_entity(id="pod/default/pod-1", health=0.3)
        # Give it different initial positions (simulating recalculation)
        updated_entity.x, updated_entity.y, updated_entity.z = -100.0, -100.0, -100.0
        collector.set_topology(make_topology([updated_entity]))

        # Second diff - should preserve original position
        updates = await collector.collect_topology_diff()

        # Get the updated entity from the internal state
        assert collector._last_topology is not None
        preserved_entity = collector._last_topology.entities[0]

        # Position should be preserved from first topology
        assert preserved_entity.x == 5.0
        assert preserved_entity.y == 10.0
        assert preserved_entity.z == -3.0

    @pytest.mark.asyncio
    async def test_new_entities_get_fresh_positions(self, collector):
        """New entities should get their calculated positions."""
        # Initial topology
        entity1 = make_entity(id="pod/default/pod-1")
        entity1.x, entity1.y, entity1.z = 5.0, 10.0, -3.0
        collector.set_topology(make_topology([entity1]))
        await collector.collect_topology_diff()

        # Add a new entity with its own position
        entity1_copy = make_entity(id="pod/default/pod-1")
        entity1_copy.x, entity1_copy.y, entity1_copy.z = 5.0, 10.0, -3.0

        entity2 = make_entity(id="pod/default/pod-2")
        entity2.x, entity2.y, entity2.z = 20.0, 30.0, 40.0
        collector.set_topology(make_topology([entity1_copy, entity2]))

        await collector.collect_topology_diff()

        # New entity should keep its calculated position
        assert collector._last_topology is not None
        new_entity = [
            e for e in collector._last_topology.entities if e.id == "pod/default/pod-2"
        ][0]
        assert new_entity.x == 20.0
        assert new_entity.y == 30.0
        assert new_entity.z == 40.0


class TestTopologyStreaming:
    """Tests for topology update streaming."""

    @pytest.fixture
    def collector(self):
        """Create a mock collector."""
        from agents.infra.collectors.kubernetes import MockKubernetesCollector

        return MockKubernetesCollector()

    @pytest.mark.asyncio
    async def test_stream_produces_updates(self, collector):
        """stream_topology_updates yields updates at poll interval."""
        await collector.connect()

        # Collect first few updates
        updates = []
        async for update in collector.stream_topology_updates():
            updates.append(update)
            if len(updates) >= 2:
                break

        # Should have received updates
        assert len(updates) >= 1

        # First should be full topology
        first_kind = updates[0].kind
        if hasattr(first_kind, "value"):
            assert first_kind.value == "full"
        else:
            assert first_kind == "full"

        await collector.disconnect()

    @pytest.mark.asyncio
    async def test_stream_stops_on_disconnect(self, collector):
        """Stream stops when collector disconnects."""
        await collector.connect()

        count = 0
        async for _ in collector.stream_topology_updates():
            count += 1
            if count == 1:
                await collector.disconnect()
            if count > 5:
                # Safety break
                break

        # Should stop shortly after disconnect
        assert count <= 3
