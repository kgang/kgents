"""
Infrastructure API Router.

REST and SSE endpoints for live infrastructure monitoring (Gestalt Live).

Endpoints:
- GET /api/infra/topology -> Current infrastructure topology
- GET /api/infra/topology/stream -> SSE stream of topology updates
- GET /api/infra/events/stream -> SSE stream of infrastructure events
- GET /api/infra/health -> Aggregate health summary
- GET /api/infra/entity/{entity_id} -> Single entity details

@see plans/gestalt-live-infrastructure.md
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncIterator

try:
    from fastapi import APIRouter, HTTPException, Query
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]
    Query = None  # type: ignore[assignment]
    StreamingResponse = None  # type: ignore[assignment]
    BaseModel = object  # type: ignore[assignment]

    def Field(*a, **k):
        return None


logger = logging.getLogger(__name__)


# =============================================================================
# Collector State (Module-level singleton)
# =============================================================================

# We'll lazily initialize the collector based on configuration
_collector_instance: Any = None


def get_collector():
    """
    Get or create the infrastructure collector.

    Uses environment-aware configuration:
    - KGENTS_ENV=production -> Real Kubernetes collector with ProductionK8sConfig
    - KGENTS_ENV=development -> Real Kubernetes collector with DevelopmentK8sConfig
    - KGENTS_ENV=test or GESTALT_USE_MOCK=true -> Mock collector

    Returns:
        BaseCollector instance (KubernetesCollector or MockKubernetesCollector).
    """
    global _collector_instance

    if _collector_instance is None:
        from agents.infra.collectors.config import (
            get_collector_config,
            should_use_mock,
        )

        if should_use_mock():
            from agents.infra.collectors.kubernetes import MockKubernetesCollector

            _collector_instance = MockKubernetesCollector()
            logger.info("Using MockKubernetesCollector (mock mode enabled)")
        else:
            from agents.infra.collectors.kubernetes import KubernetesCollector

            config = get_collector_config()
            _collector_instance = KubernetesCollector(config)
            logger.info(
                f"Using KubernetesCollector with config: "
                f"namespaces={config.namespaces}, "
                f"collect_metrics={config.collect_metrics}"
            )

    return _collector_instance


def reset_collector() -> None:
    """
    Reset the collector instance.

    Use this to force re-initialization after config changes.
    Primarily useful for testing.
    """
    global _collector_instance
    _collector_instance = None


def set_use_mock(use_mock: bool) -> None:
    """
    Set whether to use mock collector (for development).

    DEPRECATED: Use GESTALT_USE_MOCK environment variable instead.
    """
    import os
    import warnings

    warnings.warn(
        "set_use_mock() is deprecated. Set GESTALT_USE_MOCK=true instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    os.environ["GESTALT_USE_MOCK"] = str(use_mock).lower()
    reset_collector()


# =============================================================================
# Pydantic Models (for API responses)
# =============================================================================


class InfraEntityKindEnum(str, Enum):
    """Entity kinds for API."""

    namespace = "namespace"
    node = "node"
    pod = "pod"
    service = "service"
    deployment = "deployment"
    container = "container"
    nats_subject = "nats_subject"
    nats_stream = "nats_stream"
    database = "database"
    volume = "volume"
    custom = "custom"


class InfraEntityStatusEnum(str, Enum):
    """Entity status for API."""

    running = "running"
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    terminating = "terminating"
    unknown = "unknown"


class InfraEntityResponse(BaseModel):
    """A single infrastructure entity."""

    id: str = Field(..., description="Unique entity identifier")
    kind: str = Field(..., description="Entity kind (pod, service, etc.)")
    name: str = Field(..., description="Entity name")
    namespace: str | None = Field(None, description="Kubernetes namespace")
    status: str = Field(..., description="Current status")
    status_message: str | None = Field(None, description="Status details")
    health: float = Field(..., ge=0.0, le=1.0, description="Health score 0-1")
    health_grade: str = Field(..., description="Health grade (A+ to F)")

    # Metrics
    cpu_percent: float = Field(0.0, description="CPU utilization percentage")
    memory_bytes: int = Field(0, description="Memory usage in bytes")
    memory_limit: int | None = Field(None, description="Memory limit in bytes")
    memory_percent: float | None = Field(None, description="Memory utilization percentage")

    # Custom metrics
    custom_metrics: dict[str, float] = Field(default_factory=dict)

    # Position (for visualization)
    x: float = Field(0.0, description="X position")
    y: float = Field(0.0, description="Y position")
    z: float = Field(0.0, description="Z position")

    # Metadata
    labels: dict[str, str] = Field(default_factory=dict)
    source: str = Field("unknown", description="Data source")
    created_at: str | None = Field(None, description="Creation timestamp")


class InfraConnectionResponse(BaseModel):
    """A connection between two entities."""

    id: str = Field(..., description="Connection identifier")
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    kind: str = Field(..., description="Connection type")
    requests_per_sec: float = Field(0.0, description="Request rate")
    bytes_per_sec: float = Field(0.0, description="Throughput")
    error_rate: float = Field(0.0, ge=0.0, le=1.0, description="Error rate")
    is_healthy: bool = Field(True, description="Connection health")


class InfraTopologyResponse(BaseModel):
    """Complete infrastructure topology."""

    entities: list[InfraEntityResponse] = Field(default_factory=list)
    connections: list[InfraConnectionResponse] = Field(default_factory=list)
    timestamp: str = Field(..., description="Snapshot timestamp")

    # Aggregates
    total_entities: int = Field(0, description="Total entity count")
    healthy_count: int = Field(0, description="Healthy entities")
    warning_count: int = Field(0, description="Warning entities")
    critical_count: int = Field(0, description="Critical entities")
    overall_health: float = Field(1.0, ge=0.0, le=1.0, description="Overall health")

    # Breakdowns
    entities_by_kind: dict[str, int] = Field(default_factory=dict)
    entities_by_namespace: dict[str, int] = Field(default_factory=dict)


class InfraHealthResponse(BaseModel):
    """Aggregate health summary."""

    overall: float = Field(..., ge=0.0, le=1.0, description="Overall health score")
    overall_grade: str = Field(..., description="Overall health grade")
    healthy: int = Field(..., description="Healthy entity count")
    warning: int = Field(..., description="Warning entity count")
    critical: int = Field(..., description="Critical entity count")
    total: int = Field(..., description="Total entity count")
    by_kind: dict[str, Any] = Field(default_factory=dict)
    by_namespace: dict[str, Any] = Field(default_factory=dict)
    worst_entities: list[dict[str, Any]] = Field(default_factory=list)


class InfraEventResponse(BaseModel):
    """An infrastructure event."""

    id: str = Field(..., description="Event ID")
    type: str = Field(..., description="Event type (Normal, Warning)")
    reason: str = Field(..., description="Event reason")
    message: str = Field(..., description="Event message")
    severity: str = Field(..., description="Severity level")
    entity_id: str = Field(..., description="Related entity ID")
    entity_kind: str = Field(..., description="Related entity kind")
    entity_name: str = Field(..., description="Related entity name")
    entity_namespace: str | None = Field(None, description="Entity namespace")
    timestamp: str = Field(..., description="Event timestamp")
    count: int = Field(1, description="Event occurrence count")


class CollectorStatusResponse(BaseModel):
    """Collector status response."""

    connected: bool = Field(..., description="Whether collector is connected")
    collector_type: str = Field(..., description="Collector type (mock, kubernetes)")
    health_check: bool = Field(..., description="Health check result")


# =============================================================================
# Serialization Helpers
# =============================================================================


def _entity_to_response(entity) -> InfraEntityResponse:
    """Convert InfraEntity to API response."""
    return InfraEntityResponse(
        id=entity.id,
        kind=entity.kind.value,
        name=entity.name,
        namespace=entity.namespace,
        status=entity.status.value,
        status_message=entity.status_message,
        health=entity.health,
        health_grade=entity.health_grade,
        cpu_percent=entity.cpu_percent,
        memory_bytes=entity.memory_bytes,
        memory_limit=entity.memory_limit,
        memory_percent=entity.memory_percent,
        custom_metrics=entity.custom_metrics,
        x=entity.x,
        y=entity.y,
        z=entity.z,
        labels=entity.labels,
        source=entity.source,
        created_at=entity.created_at.isoformat() if entity.created_at else None,
    )


def _connection_to_response(conn) -> InfraConnectionResponse:
    """Convert InfraConnection to API response."""
    return InfraConnectionResponse(
        id=conn.id,
        source_id=conn.source_id,
        target_id=conn.target_id,
        kind=conn.kind.value,
        requests_per_sec=conn.requests_per_sec,
        bytes_per_sec=conn.bytes_per_sec,
        error_rate=conn.error_rate,
        is_healthy=conn.is_healthy,
    )


def _topology_to_response(topology) -> InfraTopologyResponse:
    """Convert InfraTopology to API response."""
    return InfraTopologyResponse(
        entities=[_entity_to_response(e) for e in topology.entities],
        connections=[_connection_to_response(c) for c in topology.connections],
        timestamp=topology.timestamp.isoformat(),
        total_entities=topology.total_entities,
        healthy_count=topology.healthy_count,
        warning_count=topology.warning_count,
        critical_count=topology.critical_count,
        overall_health=topology.overall_health,
        entities_by_kind=topology.entities_by_kind,
        entities_by_namespace=topology.entities_by_namespace,
    )


def _event_to_response(event) -> InfraEventResponse:
    """Convert InfraEvent to API response."""
    return InfraEventResponse(
        id=event.id,
        type=event.type,
        reason=event.reason,
        message=event.message,
        severity=event.severity.value,
        entity_id=event.entity_id,
        entity_kind=event.entity_kind.value,
        entity_name=event.entity_name,
        entity_namespace=event.entity_namespace,
        timestamp=event.timestamp.isoformat()
        if event.timestamp
        else datetime.now(timezone.utc).isoformat(),
        count=event.count,
    )


# =============================================================================
# Router
# =============================================================================


def create_infrastructure_router() -> "APIRouter | None":
    """Create and configure the Infrastructure API router."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/infra", tags=["infrastructure"])

    @router.get("/status", response_model=CollectorStatusResponse)
    async def get_status() -> CollectorStatusResponse:
        """
        Get collector status.

        Returns whether the collector is connected and its type.
        """
        collector = get_collector()

        return CollectorStatusResponse(
            connected=collector.is_connected,
            collector_type=type(collector).__name__,
            health_check=await collector.health_check(),
        )

    @router.post("/connect")
    async def connect() -> dict[str, Any]:
        """
        Connect to infrastructure data source.

        Establishes connection to Kubernetes or other configured source.
        """
        collector = get_collector()

        if collector.is_connected:
            return {"status": "already_connected"}

        try:
            await collector.connect()
            return {"status": "connected"}
        except Exception as e:
            logger.error(f"Failed to connect collector: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/disconnect")
    async def disconnect() -> dict[str, Any]:
        """
        Disconnect from infrastructure data source.
        """
        collector = get_collector()

        if not collector.is_connected:
            return {"status": "already_disconnected"}

        await collector.disconnect()
        return {"status": "disconnected"}

    @router.get("/topology", response_model=InfraTopologyResponse)
    async def get_topology(
        namespaces: str | None = Query(None, description="Comma-separated namespaces to filter"),
        kinds: str | None = Query(None, description="Comma-separated entity kinds to filter"),
        min_health: float = Query(0.0, ge=0.0, le=1.0, description="Minimum health filter"),
    ) -> InfraTopologyResponse:
        """
        Get current infrastructure topology.

        Returns all entities and connections with positions for visualization.
        """
        collector = get_collector()

        if not collector.is_connected:
            await collector.connect()

        try:
            topology = await collector.collect_topology()
        except Exception as e:
            logger.error(f"Failed to collect topology: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        # Apply filters
        if namespaces:
            ns_filter = set(namespaces.split(","))
            topology.entities = [e for e in topology.entities if e.namespace in ns_filter]

        if kinds:
            kind_filter = set(kinds.split(","))
            topology.entities = [e for e in topology.entities if e.kind.value in kind_filter]

        if min_health > 0:
            topology.entities = [e for e in topology.entities if e.health >= min_health]

        # Filter connections to only include ones between remaining entities
        entity_ids = {e.id for e in topology.entities}
        topology.connections = [
            c
            for c in topology.connections
            if c.source_id in entity_ids and c.target_id in entity_ids
        ]

        return _topology_to_response(topology)

    @router.get("/topology/stream")
    async def stream_topology() -> StreamingResponse:
        """
        Stream topology updates via Server-Sent Events.

        Returns incremental updates as entities are added, updated, or removed.
        """
        collector = get_collector()

        if not collector.is_connected:
            await collector.connect()

        async def generate() -> AsyncIterator[str]:
            try:
                async for update in collector.stream_topology_updates():
                    # Convert to JSON-serializable format
                    data = {
                        "kind": update.kind.value
                        if hasattr(update.kind, "value")
                        else str(update.kind),
                        "timestamp": update.timestamp.isoformat() if update.timestamp else None,
                    }

                    if update.entity:
                        data["entity"] = _entity_to_response(update.entity).model_dump()
                    if update.connection:
                        data["connection"] = _connection_to_response(update.connection).model_dump()
                    if update.topology:
                        data["topology"] = _topology_to_response(update.topology).model_dump()

                    yield f"data: {json.dumps(data)}\n\n"

            except asyncio.CancelledError:
                logger.info("Topology stream cancelled")
            except Exception as e:
                logger.error(f"Error in topology stream: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get("/events/stream")
    async def stream_events() -> StreamingResponse:
        """
        Stream infrastructure events via Server-Sent Events.

        Returns real-time events (pod restarts, deployments, etc.).
        """
        collector = get_collector()

        if not collector.is_connected:
            await collector.connect()

        async def generate() -> AsyncIterator[str]:
            try:
                async for event in collector.stream_events():
                    data = _event_to_response(event).model_dump()
                    yield f"data: {json.dumps(data)}\n\n"

            except asyncio.CancelledError:
                logger.info("Event stream cancelled")
            except Exception as e:
                logger.error(f"Error in event stream: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get("/health", response_model=InfraHealthResponse)
    async def get_health() -> InfraHealthResponse:
        """
        Get aggregate infrastructure health.

        Returns health scores by kind, namespace, and worst entities.
        """
        from agents.infra.health import calculate_topology_health, health_to_grade

        collector = get_collector()

        if not collector.is_connected:
            await collector.connect()

        try:
            topology = await collector.collect_topology()
        except Exception as e:
            logger.error(f"Failed to collect topology for health: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        health_data = calculate_topology_health(topology)

        return InfraHealthResponse(
            overall=health_data["overall"],
            overall_grade=health_to_grade(health_data["overall"]),
            healthy=health_data["healthy"],
            warning=health_data["warning"],
            critical=health_data["critical"],
            total=health_data["total"],
            by_kind=health_data["by_kind"],
            by_namespace=health_data["by_namespace"],
            worst_entities=health_data["worst_entities"],
        )

    @router.get("/entity/{entity_id:path}", response_model=InfraEntityResponse)
    async def get_entity(entity_id: str) -> InfraEntityResponse:
        """
        Get details for a specific entity.

        Args:
            entity_id: Entity ID (e.g., pod/default/my-pod)
        """
        collector = get_collector()

        if not collector.is_connected:
            await collector.connect()

        try:
            topology = await collector.collect_topology()
        except Exception as e:
            logger.error(f"Failed to collect topology: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        for entity in topology.entities:
            if entity.id == entity_id:
                return _entity_to_response(entity)

        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_id}")

    return router
