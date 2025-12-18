"""
AGENTESE Gestalt Live Context: Real-time Infrastructure Visualizer.

The world.gestalt.live context provides access to the Gestalt Live visualizer:
- world.gestalt.live.manifest - View infrastructure topology
- world.gestalt.live.subscribe - Subscribe to live updates (SSE)
- world.gestalt.live.entity.manifest - View entity details
- world.gestalt.live.events.witness - View event feed

This module defines GestaltLiveNode which handles live infrastructure visualization.

AGENTESE: world.gestalt.live.*

Principle Alignment:
- Joy-Inducing: Real-time 3D visualization with health-based coloring
- Heterarchical: Entities in flux (pods, services, deployments)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# Gestalt Live affordances available at world.gestalt.live.*
GESTALT_LIVE_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "subscribe",
    "entity",
    "events",
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
# GestaltLiveNode
# =============================================================================


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
        help="View real-time infrastructure topology",
        examples=["kg gestalt live", "world.gestalt.live.manifest"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
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
            lines.append(f"  [{kind_info['shape']}] {kind_info['name']}: {kind_info['description']}")

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
        help="Subscribe to live infrastructure updates (SSE)",
        examples=["world.gestalt.live.subscribe"],
    )
    async def subscribe(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Show subscription info."""
        return BasicRendering(
            summary="Gestalt Live Subscription",
            content=(
                "Real-time infrastructure updates are available via SSE.\n"
                "Visit /gestalt/live to see the live visualization.\n\n"
                "API endpoints:\n"
                "  GET /api/infra/topology - Current topology snapshot\n"
                "  GET /api/infra/stream - SSE stream of updates\n"
                "  GET /api/infra/events - Recent events"
            ),
            metadata={
                "endpoints": [
                    "/api/infra/topology",
                    "/api/infra/stream",
                    "/api/infra/events",
                ],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View entity details",
        examples=["world.gestalt.live.entity.manifest --kind pod"],
    )
    async def entity(
        self,
        observer: "Umwelt[Any, Any]",
        kind: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Show entity kind details."""
        if kind is None:
            # List all kinds
            lines = ["Entity Kinds:", ""]
            for kind_id, info in ENTITY_KINDS.items():
                lines.append(f"  {kind_id}: {info['name']} ({info['shape']})")
            return BasicRendering(
                summary="Entity Kinds",
                content="\n".join(lines),
                metadata={"kinds": list(ENTITY_KINDS.keys())},
            )

        kind_info = ENTITY_KINDS.get(kind)
        if kind_info is None:
            return BasicRendering(
                summary=f"Unknown Entity Kind: {kind}",
                content=f"Available kinds: {', '.join(ENTITY_KINDS.keys())}",
                metadata={"error": "unknown_kind"},
            )

        return BasicRendering(
            summary=f"Entity: {kind_info['name']}",
            content=(
                f"Name: {kind_info['name']}\n"
                f"Shape: {kind_info['shape']}\n"
                f"Description: {kind_info['description']}"
            ),
            metadata={"kind": kind, "info": kind_info},
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View infrastructure events feed",
        examples=["world.gestalt.live.events.witness"],
    )
    async def events(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Show events info."""
        return BasicRendering(
            summary="Infrastructure Events",
            content=(
                "Real-time infrastructure events are displayed in the /gestalt/live UI.\n\n"
                "Event severities:\n"
                "  - info: Normal operations\n"
                "  - warning: Attention needed\n"
                "  - error: Action required\n"
                "  - critical: Immediate action needed"
            ),
            metadata={
                "severities": ["info", "warning", "error", "critical"],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle gestalt-live-specific aspects."""
        match aspect:
            case "subscribe":
                return await self.subscribe(observer, **kwargs)
            case "entity":
                return await self.entity(observer, **kwargs)
            case "events":
                return await self.events(observer, **kwargs)
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
]
