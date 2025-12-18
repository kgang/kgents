"""
Gestalt AGENTESE Node: @node("world.codebase")

Wraps Gestalt analysis as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- world.codebase.manifest  - Full architecture graph
- world.codebase.health    - Health metrics summary
- world.codebase.topology  - 3D visualization data
- world.codebase.drift     - Drift violations
- world.codebase.module    - Module details
- world.codebase.scan      - Force rescan

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node
from protocols.gestalt.analysis import ArchitectureGraph

# Import handler functions from protocols.gestalt
from protocols.gestalt.handler import (
    _ensure_scanned_sync,
    _get_store,
    handle_codebase_manifest,
    handle_drift_witness,
    handle_health_manifest,
    handle_module_manifest,
    scan_codebase,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.gestalt.reactive import GestaltStore


# === GestaltNode Rendering ===


@dataclass(frozen=True)
class GestaltManifestRendering:
    """Rendering for codebase architecture manifest."""

    module_count: int
    edge_count: int
    overall_grade: str
    average_health: float
    drift_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "codebase_manifest",
            "module_count": self.module_count,
            "edge_count": self.edge_count,
            "overall_grade": self.overall_grade,
            "average_health": round(self.average_health, 2),
            "drift_count": self.drift_count,
        }

    def to_text(self) -> str:
        return (
            f"Architecture: {self.module_count} modules, {self.edge_count} edges\n"
            f"Health: {self.overall_grade} ({round(self.average_health * 100)}%)\n"
            f"Drift: {self.drift_count} violations"
        )


@dataclass(frozen=True)
class TopologyRendering:
    """Rendering for 3D topology visualization data."""

    nodes: list[dict[str, Any]]
    links: list[dict[str, Any]]
    layers: list[str]
    stats: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "topology",
            "nodes": self.nodes,
            "links": self.links,
            "layers": self.layers,
            "stats": self.stats,
        }

    def to_text(self) -> str:
        return (
            f"Topology: {len(self.nodes)} nodes, {len(self.links)} links\n"
            f"Layers: {', '.join(self.layers)}"
        )


# === GestaltNode ===


@node(
    "world.codebase",
    description="Gestalt Architecture Visualizer - living garden where code breathes",
    dependencies=(),  # No DI required - uses module-level GestaltStore
)
class GestaltNode(BaseLogosNode):
    """
    AGENTESE node for Gestalt Crown Jewel.

    Exposes codebase architecture analysis through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/world/codebase/topology
        {"max_nodes": 200, "min_health": 0.0}

        # Via Logos directly
        await logos.invoke("world.codebase.topology", observer, max_nodes=200)

        # Via CLI
        kgents world codebase
    """

    def __init__(self) -> None:
        """
        Initialize GestaltNode.

        Unlike BrainNode, GestaltNode uses module-level GestaltStore
        rather than DI. This matches the existing handler pattern.
        """
        pass

    @property
    def handle(self) -> str:
        return "world.codebase"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        All archetypes get read access. Mutation (scan) is restricted.
        """
        base = ("manifest", "health", "topology", "drift", "module")

        if archetype in ("developer", "admin", "system", "architect"):
            return base + ("scan",)
        else:
            return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest codebase architecture to observer.

        AGENTESE: world.codebase.manifest
        """
        store = _get_store()
        _ensure_scanned_sync(store)

        return GestaltManifestRendering(
            module_count=store.module_count.value,
            edge_count=store.edge_count.value,
            overall_grade=store.overall_grade.value,
            average_health=store.average_health.value,
            drift_count=store.drift_count.value,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to handler functions.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        store = _get_store()
        _ensure_scanned_sync(store)

        if aspect == "health":
            result = handle_health_manifest([], json_output=True, store=store)
            return result

        elif aspect == "topology":
            # Build topology response for 3D visualization
            # This matches the format expected by the frontend
            max_nodes = kwargs.get("max_nodes", 200)
            min_health = kwargs.get("min_health", 0.0)
            role = kwargs.get("role")

            return await self._build_topology(store, max_nodes, min_health, role)

        elif aspect == "drift":
            result = handle_drift_witness([], json_output=True, store=store)
            return result

        elif aspect == "module":
            module_name = kwargs.get("module_name") or kwargs.get("name")
            if not module_name:
                return {"error": "module_name required"}
            result = handle_module_manifest(
                module_name, [], json_output=True, store=store
            )
            return result

        elif aspect == "scan":
            # Force rescan
            language = kwargs.get("language", "python")
            scan_codebase(None, language)
            result = handle_codebase_manifest([], json_output=True, store=store)
            return result

        else:
            return {"error": f"Unknown aspect: {aspect}"}

    async def _build_topology(
        self,
        store: "GestaltStore",
        max_nodes: int = 200,
        min_health: float = 0.0,
        role: str | None = None,
    ) -> dict[str, Any]:
        """
        Build topology response for 3D visualization.

        This replicates the logic from protocols/api/gestalt.py's get_topology
        endpoint but works through the AGENTESE node interface.
        """
        import hashlib
        import math

        graph = store.graph.value
        violations = store.violations.value
        violation_edges = {(v.source_module, v.target_module): v for v in violations}

        # Filter and limit modules
        modules_with_health = [
            m
            for m in graph.modules.values()
            if m.health and m.health.overall_health >= min_health
        ]

        # Sort by health (best first for importance)
        modules_with_health.sort(
            key=lambda m: m.health.overall_health if m.health else 0,
            reverse=True,
        )
        selected_modules = modules_with_health[:max_nodes]
        selected_names = {m.name for m in selected_modules}

        # Detect layers
        layers_set: set[str] = set()
        for m in selected_modules:
            if m.layer:
                layers_set.add(m.layer)

        # Build nodes with 3D positions
        nodes: list[dict[str, Any]] = []
        for i, module in enumerate(selected_modules):
            # Deterministic positioning based on name hash
            name_hash = int(hashlib.md5(module.name.encode()).hexdigest()[:8], 16)

            # Spiral layout with layer-based z
            angle = (name_hash % 360) * math.pi / 180
            radius = 2 + (i / max(len(selected_modules), 1)) * 8

            # Layer-based z coordinate
            layer_idx = (
                sorted(layers_set).index(module.layer)
                if module.layer and module.layer in layers_set
                else 0
            )
            z_offset = layer_idx * 2 - len(layers_set)

            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            z = z_offset + (name_hash % 100) / 100 * 2 - 1

            nodes.append(
                {
                    "id": module.name,
                    "label": module.name.split(".")[-1],
                    "layer": module.layer,
                    "health_grade": module.health.grade if module.health else "?",
                    "health_score": module.health.overall_health
                    if module.health
                    else 0.0,
                    "lines_of_code": module.lines_of_code,
                    "coupling": module.health.coupling if module.health else 0.0,
                    "cohesion": module.health.cohesion if module.health else 1.0,
                    "instability": module.health.instability if module.health else None,
                    "x": round(x, 2),
                    "y": round(y, 2),
                    "z": round(z, 2),
                }
            )

        # Build links (only between selected modules)
        links: list[dict[str, Any]] = []
        for edge in graph.edges:
            if edge.source in selected_names and edge.target in selected_names:
                violation = violation_edges.get((edge.source, edge.target))
                links.append(
                    {
                        "source": edge.source,
                        "target": edge.target,
                        "import_type": edge.import_type,
                        "is_violation": violation is not None,
                        "violation_severity": violation.severity if violation else None,
                    }
                )

        # Compute stats
        health_scores = [n["health_score"] for n in nodes]
        violation_count = len([l for l in links if l.get("is_violation")])

        return {
            "nodes": nodes,
            "links": links,
            "layers": sorted(layers_set),
            "stats": {
                "node_count": len(nodes),
                "link_count": len(links),
                "layer_count": len(layers_set),
                "violation_count": violation_count,
                "avg_health": sum(health_scores) / len(health_scores)
                if health_scores
                else 0,
                "overall_grade": graph.overall_grade,
            },
        }


# === Exports ===

__all__ = [
    "GestaltNode",
    "GestaltManifestRendering",
    "TopologyRendering",
]
