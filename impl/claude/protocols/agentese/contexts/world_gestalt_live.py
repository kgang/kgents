"""
AGENTESE Gestalt Live Context: Real-time Infrastructure Visualizer.

Migrates protocols/api/infrastructure.py to @node pattern (AD-009 Phase 3).

Routes migrated (8 total):
- GET /api/infra/status → world.gestalt.live.status
- POST /api/infra/connect → world.gestalt.live.connect
- POST /api/infra/disconnect → world.gestalt.live.disconnect
- GET /api/infra/topology → world.gestalt.live.topology
- GET /api/infra/topology/stream → world.gestalt.live.topology_stream (SSE)
- GET /api/infra/events/stream → world.gestalt.live.events_stream (SSE)
- GET /api/infra/health → world.gestalt.live.health
- GET /api/infra/entity/{id} → world.gestalt.live.entity_detail[entity_id=...]

AGENTESE: world.gestalt.live.*

Principle Alignment:
- Joy-Inducing: Real-time 3D visualization with health-based coloring
- Heterarchical: Entities in flux (pods, services, deployments)

See: plans/agentese-router-consolidation.md (Phase 3.3)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, AsyncGenerator

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)

# Gestalt Live affordances available at world.gestalt.live.*
GESTALT_LIVE_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "status",
    "connect",
    "disconnect",
    "topology",
    "topology_stream",
    "events_stream",
    "health",
    "entity_detail",
)

# Entity kinds from infrastructure types
ENTITY_KINDS: dict[str, dict[str, str]] = {
    "pod": {
        "name": "Pod",
        "shape": "sphere",
        "description": "Kubernetes pod - smallest deployable unit",
    },
    "service": {
        "name": "Service",
        "shape": "octahedron",
        "description": "Kubernetes service - network endpoint",
    },
    "deployment": {
        "name": "Deployment",
        "shape": "dodecahedron",
        "description": "Kubernetes deployment - declarative pod management",
    },
    "configmap": {
        "name": "ConfigMap",
        "shape": "box",
        "description": "Kubernetes configmap - configuration data",
    },
    "secret": {
        "name": "Secret",
        "shape": "cone",
        "description": "Kubernetes secret - sensitive data",
    },
    "node": {
        "name": "Node",
        "shape": "cylinder",
        "description": "Kubernetes node - worker machine",
    },
    "namespace": {
        "name": "Namespace",
        "shape": "torus",
        "description": "Kubernetes namespace - resource isolation",
    },
    "custom": {
        "name": "Custom",
        "shape": "sphere",
        "description": "Custom resource",
    },
}

# =============================================================================
# Collector State (Module-level singleton)
# =============================================================================

_collector_instance: Any = None


def get_collector() -> Any:
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
    """Reset the collector instance."""
    global _collector_instance
    _collector_instance = None


# =============================================================================
# Serialization Helpers
# =============================================================================


def _entity_to_dict(entity: Any) -> dict[str, Any]:
    """Convert InfraEntity to API response dict."""
    return {
        "id": entity.id,
        "kind": entity.kind.value,
        "name": entity.name,
        "namespace": entity.namespace,
        "status": entity.status.value,
        "status_message": entity.status_message,
        "health": entity.health,
        "health_grade": entity.health_grade,
        "cpu_percent": entity.cpu_percent,
        "memory_bytes": entity.memory_bytes,
        "memory_limit": entity.memory_limit,
        "memory_percent": entity.memory_percent,
        "custom_metrics": entity.custom_metrics,
        "x": entity.x,
        "y": entity.y,
        "z": entity.z,
        "labels": entity.labels,
        "source": entity.source,
        "created_at": entity.created_at.isoformat() if entity.created_at else None,
    }


def _connection_to_dict(conn: Any) -> dict[str, Any]:
    """Convert InfraConnection to API response dict."""
    return {
        "id": conn.id,
        "source_id": conn.source_id,
        "target_id": conn.target_id,
        "kind": conn.kind.value,
        "requests_per_sec": conn.requests_per_sec,
        "bytes_per_sec": conn.bytes_per_sec,
        "error_rate": conn.error_rate,
        "is_healthy": conn.is_healthy,
    }


def _topology_to_dict(topology: Any) -> dict[str, Any]:
    """Convert InfraTopology to API response dict."""
    return {
        "entities": [_entity_to_dict(e) for e in topology.entities],
        "connections": [_connection_to_dict(c) for c in topology.connections],
        "timestamp": topology.timestamp.isoformat(),
        "total_entities": topology.total_entities,
        "healthy_count": topology.healthy_count,
        "warning_count": topology.warning_count,
        "critical_count": topology.critical_count,
        "overall_health": topology.overall_health,
        "entities_by_kind": topology.entities_by_kind,
        "entities_by_namespace": topology.entities_by_namespace,
    }


def _event_to_dict(event: Any) -> dict[str, Any]:
    """Convert InfraEvent to API response dict."""
    return {
        "id": event.id,
        "type": event.type,
        "reason": event.reason,
        "message": event.message,
        "severity": event.severity.value,
        "entity_id": event.entity_id,
        "entity_kind": event.entity_kind.value,
        "entity_name": event.entity_name,
        "entity_namespace": event.entity_namespace,
        "timestamp": event.timestamp.isoformat()
        if event.timestamp
        else datetime.now(timezone.utc).isoformat(),
        "count": event.count,
    }


# =============================================================================
# GestaltLiveNode
# =============================================================================


@node(
    "world.gestalt.live",
    description="Real-time 3D infrastructure topology visualizer",
)
@dataclass
class GestaltLiveNode(BaseLogosNode):
    """
    world.gestalt.live - Real-time Infrastructure Visualizer interface.

    The Gestalt Live node provides:
    - Real-time 3D topology visualization
    - Health-based coloring (green to red)
    - Entity shapes by kind
    - Namespace grouping with rings
    - Event feed panel
    - SSE streaming for topology and events
    """

    _handle: str = "world.gestalt.live"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Gestalt Live affordances - available to all archetypes."""
        return GESTALT_LIVE_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View real-time infrastructure topology overview",
        examples=["kg gestalt live", "world.gestalt.live.manifest"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Show Gestalt Live overview."""
        lines = [
            "Gestalt Live - Real-time Infrastructure Visualizer",
            "=" * 50,
            "",
            "Real-time 3D visualization of Kubernetes infrastructure.",
            "",
            "Features:",
            "  - 3D force-directed graph of entities",
            "  - Real-time updates via SSE",
            "  - Entity shapes by kind (sphere=pod, octahedron=service, etc.)",
            "  - Health-based coloring (green to red)",
            "  - Namespace grouping with rings",
            "  - Event feed panel",
            "",
            f"Entity Kinds: {len(ENTITY_KINDS)}",
            "",
        ]

        for kind_id, kind_info in ENTITY_KINDS.items():
            lines.append(
                f"  [{kind_info['shape']}] {kind_info['name']}: {kind_info['description']}"
            )

        lines.append("")
        lines.append("Visit /gestalt/live for real-time visualization")
        lines.append("=" * 50)

        return BasicRendering(
            summary="Gestalt Live Infrastructure Visualizer",
            content="\n".join(lines),
            metadata={
                "status": "available",
                "entity_kinds": len(ENTITY_KINDS),
                "kinds": list(ENTITY_KINDS.keys()),
                "route": "/gestalt/live",
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get collector status",
        examples=["world.gestalt.live.status"],
    )
    async def status(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get collector status.

        Returns whether the collector is connected and its type.
        """
        try:
            collector = get_collector()
            return {
                "connected": collector.is_connected,
                "collector_type": type(collector).__name__,
                "health_check": await collector.health_check(),
            }
        except ImportError as e:
            return {"error": str(e), "connected": False}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("infra")],
        help="Connect to infrastructure data source",
        examples=["world.gestalt.live.connect"],
    )
    async def connect(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Connect to infrastructure data source.

        Establishes connection to Kubernetes or other configured source.
        """
        try:
            collector = get_collector()

            if collector.is_connected:
                return {"status": "already_connected"}

            await collector.connect()
            return {"status": "connected"}
        except ImportError as e:
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Failed to connect collector: {e}")
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("infra")],
        help="Disconnect from infrastructure data source",
        examples=["world.gestalt.live.disconnect"],
    )
    async def disconnect(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Disconnect from infrastructure data source."""
        try:
            collector = get_collector()

            if not collector.is_connected:
                return {"status": "already_disconnected"}

            await collector.disconnect()
            return {"status": "disconnected"}
        except ImportError as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get current infrastructure topology",
        examples=[
            "world.gestalt.live.topology",
            "world.gestalt.live.topology[namespaces='default']",
        ],
    )
    async def topology(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get current infrastructure topology.

        Args:
            namespaces: Comma-separated namespaces to filter
            kinds: Comma-separated entity kinds to filter
            min_health: Minimum health filter (0.0-1.0)

        Returns:
            InfraTopologyResponse with entities and connections
        """
        namespaces = kwargs.get("namespaces")
        kinds = kwargs.get("kinds")
        min_health = kwargs.get("min_health", 0.0)

        try:
            collector = get_collector()

            if not collector.is_connected:
                await collector.connect()

            topology_data = await collector.collect_topology()

            # Apply filters
            if namespaces:
                ns_filter = set(namespaces.split(","))
                topology_data.entities = [
                    e for e in topology_data.entities if e.namespace in ns_filter
                ]

            if kinds:
                kind_filter = set(kinds.split(","))
                topology_data.entities = [
                    e for e in topology_data.entities if e.kind.value in kind_filter
                ]

            if min_health > 0:
                topology_data.entities = [
                    e for e in topology_data.entities if e.health >= min_health
                ]

            # Filter connections to only include ones between remaining entities
            entity_ids = {e.id for e in topology_data.entities}
            topology_data.connections = [
                c
                for c in topology_data.connections
                if c.source_id in entity_ids and c.target_id in entity_ids
            ]

            return _topology_to_dict(topology_data)
        except ImportError as e:
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Failed to collect topology: {e}")
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Stream topology updates via SSE",
        examples=["world.gestalt.live.topology_stream"],
    )
    async def topology_stream(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream topology updates via Server-Sent Events.

        Yields incremental updates as entities are added, updated, or removed.
        """
        try:
            collector = get_collector()

            if not collector.is_connected:
                await collector.connect()

            async for update in collector.stream_topology_updates():
                # Convert to JSON-serializable format
                data: dict[str, Any] = {
                    "kind": update.kind.value
                    if hasattr(update.kind, "value")
                    else str(update.kind),
                    "timestamp": update.timestamp.isoformat() if update.timestamp else None,
                }

                if update.entity:
                    data["entity"] = _entity_to_dict(update.entity)
                if update.connection:
                    data["connection"] = _connection_to_dict(update.connection)
                if update.topology:
                    data["topology"] = _topology_to_dict(update.topology)

                yield data

        except asyncio.CancelledError:
            logger.info("Topology stream cancelled")
        except ImportError as e:
            yield {"error": str(e)}
        except Exception as e:
            logger.error(f"Error in topology stream: {e}")
            yield {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Stream infrastructure events via SSE",
        examples=["world.gestalt.live.events_stream"],
    )
    async def events_stream(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream infrastructure events via Server-Sent Events.

        Returns real-time events (pod restarts, deployments, etc.).
        """
        try:
            collector = get_collector()

            if not collector.is_connected:
                await collector.connect()

            async for event in collector.stream_events():
                yield _event_to_dict(event)

        except asyncio.CancelledError:
            logger.info("Event stream cancelled")
        except ImportError as e:
            yield {"error": str(e)}
        except Exception as e:
            logger.error(f"Error in event stream: {e}")
            yield {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get aggregate infrastructure health",
        examples=["world.gestalt.live.health"],
    )
    async def health(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get aggregate infrastructure health.

        Returns health scores by kind, namespace, and worst entities.
        """
        try:
            from agents.infra.health import calculate_topology_health, health_to_grade

            collector = get_collector()

            if not collector.is_connected:
                await collector.connect()

            topology_data = await collector.collect_topology()
            health_data = calculate_topology_health(topology_data)

            return {
                "overall": health_data["overall"],
                "overall_grade": health_to_grade(health_data["overall"]),
                "healthy": health_data["healthy"],
                "warning": health_data["warning"],
                "critical": health_data["critical"],
                "total": health_data["total"],
                "by_kind": health_data["by_kind"],
                "by_namespace": health_data["by_namespace"],
                "worst_entities": health_data["worst_entities"],
            }
        except ImportError as e:
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Failed to collect topology for health: {e}")
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get details for a specific entity",
        examples=["world.gestalt.live.entity_detail[entity_id='pod/default/my-pod']"],
    )
    async def entity_detail(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get details for a specific entity.

        Args:
            entity_id: Entity ID (e.g., pod/default/my-pod)

        Returns:
            Entity details dict
        """
        entity_id = kwargs.get("entity_id")
        if not entity_id:
            return {"error": "entity_id required"}

        try:
            collector = get_collector()

            if not collector.is_connected:
                await collector.connect()

            topology_data = await collector.collect_topology()

            for entity in topology_data.entities:
                if entity.id == entity_id:
                    return _entity_to_dict(entity)

            return {"error": f"Entity not found: {entity_id}"}
        except ImportError as e:
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Failed to collect topology: {e}")
            return {"error": str(e)}

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle gestalt-live-specific aspects."""
        match aspect:
            case "status":
                return await self.status(observer, **kwargs)
            case "connect":
                return await self.connect(observer, **kwargs)
            case "disconnect":
                return await self.disconnect(observer, **kwargs)
            case "topology":
                return await self.topology(observer, **kwargs)
            case "topology_stream":
                return await self.topology_stream(observer, **kwargs)
            case "events_stream":
                return await self.events_stream(observer, **kwargs)
            case "health":
                return await self.health(observer, **kwargs)
            case "entity_detail":
                return await self.entity_detail(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# =============================================================================
# Factory Functions
# =============================================================================

# Global singleton for GestaltLiveNode
_gestalt_live_node: GestaltLiveNode | None = None


def get_gestalt_live_node() -> GestaltLiveNode:
    """Get the global GestaltLiveNode singleton."""
    global _gestalt_live_node
    if _gestalt_live_node is None:
        _gestalt_live_node = GestaltLiveNode()
    return _gestalt_live_node


def set_gestalt_live_node(node: GestaltLiveNode) -> None:
    """Set the global GestaltLiveNode singleton (for testing)."""
    global _gestalt_live_node
    _gestalt_live_node = node


def create_gestalt_live_node() -> GestaltLiveNode:
    """Create a GestaltLiveNode."""
    return GestaltLiveNode()


__all__ = [
    # Constants
    "GESTALT_LIVE_AFFORDANCES",
    "ENTITY_KINDS",
    # Node
    "GestaltLiveNode",
    # Factory
    "get_gestalt_live_node",
    "set_gestalt_live_node",
    "create_gestalt_live_node",
    # Collector
    "get_collector",
    "reset_collector",
]
