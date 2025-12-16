"""
Gestalt API Router.

REST endpoints for architecture analysis and visualization.

Endpoints:
- GET /v1/world/codebase/manifest -> Full architecture graph
- GET /v1/world/codebase/health -> Health metrics summary
- GET /v1/world/codebase/drift -> Drift violations
- GET /v1/world/codebase/module/{name} -> Module details
- POST /v1/world/codebase/scan -> Force rescan
- GET /v1/world/codebase/topology -> Graph topology for visualization
"""

from __future__ import annotations

from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]
    Query = None  # type: ignore[assignment]
    BaseModel = object  # type: ignore[assignment]
    Field = lambda *a, **k: None  # type: ignore[assignment]

from protocols.gestalt.analysis import ArchitectureGraph, build_architecture_graph
from protocols.gestalt.governance import (
    DriftViolation,
    check_drift,
    create_kgents_config,
)
from protocols.gestalt.handler import (
    get_cached_graph,
    get_cached_violations,
    handle_codebase_manifest,
    handle_drift_witness,
    handle_health_manifest,
    handle_module_manifest,
)

# =============================================================================
# Synchronous Graph Building (for API use)
# =============================================================================

_api_cached_graph: ArchitectureGraph | None = None
_api_cached_violations: list["DriftViolation"] | None = None


def _get_project_root() -> "Path":
    """Get the project root for API scans."""
    from pathlib import Path

    current = Path(__file__).parent
    while current != current.parent:
        if (current / ".kgents").exists():
            return current
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()


def sync_scan_codebase(
    root: "Path | None" = None, language: str = "python"
) -> ArchitectureGraph:
    """
    Synchronously scan codebase for API use.

    Uses build_architecture_graph directly (no async).
    """
    from pathlib import Path

    global _api_cached_graph, _api_cached_violations

    root = root or _get_project_root()
    graph = build_architecture_graph(root, language)
    config = create_kgents_config()
    violations = check_drift(graph, config)

    # Update health with drift scores
    for module in graph.modules.values():
        if module.health:
            module_violations = [
                v for v in violations if v.source_module == module.name
            ]
            module.health.drift = min(1.0, len(module_violations) * 0.2)

    _api_cached_graph = graph
    _api_cached_violations = violations

    return graph


def get_api_cached_graph() -> ArchitectureGraph | None:
    """Get API-cached graph or fallback to handler cache."""
    return _api_cached_graph or get_cached_graph()


def get_api_cached_violations() -> list["DriftViolation"]:
    """Get API-cached violations or fallback to handler cache."""
    if _api_cached_violations is not None:
        return _api_cached_violations
    return get_cached_violations()


# =============================================================================
# Pydantic Models
# =============================================================================


class ModuleNode(BaseModel):
    """A module node for visualization."""

    id: str = Field(..., description="Module identifier (path-based)")
    label: str = Field(..., description="Short display label")
    layer: str | None = Field(None, description="Architectural layer")
    health_grade: str = Field(..., description="Health grade (A+ to F)")
    health_score: float = Field(..., ge=0.0, le=1.0, description="Health score 0-1")
    lines_of_code: int = Field(..., ge=0, description="Lines of code")
    coupling: float = Field(0.0, ge=0.0, le=1.0, description="Coupling score")
    cohesion: float = Field(1.0, ge=0.0, le=1.0, description="Cohesion score")
    instability: float | None = Field(None, description="Martin instability metric")
    x: float = Field(0.0, description="X position for visualization")
    y: float = Field(0.0, description="Y position for visualization")
    z: float = Field(0.0, description="Z position for visualization")


class DependencyLink(BaseModel):
    """A dependency edge for visualization."""

    source: str = Field(..., description="Source module ID")
    target: str = Field(..., description="Target module ID")
    import_type: str = Field("standard", description="Import type")
    is_violation: bool = Field(False, description="Whether this is a drift violation")
    violation_severity: str | None = Field(None, description="Severity if violation")


class TopologyResponse(BaseModel):
    """Graph topology for visualization."""

    nodes: list[ModuleNode] = Field(default_factory=list)
    links: list[DependencyLink] = Field(default_factory=list)
    layers: list[str] = Field(default_factory=list, description="Detected layers")
    stats: dict[str, Any] = Field(default_factory=dict)


class ManifestResponse(BaseModel):
    """Full architecture manifest response."""

    module_count: int
    edge_count: int
    language: str
    average_health: float
    overall_grade: str
    drift_count: int
    modules: list[dict[str, Any]]


class HealthResponse(BaseModel):
    """Health metrics response."""

    average_health: float
    overall_grade: str
    grade_distribution: dict[str, int]
    worst_modules: list[dict[str, Any]]
    best_modules: list[dict[str, Any]]


class DriftResponse(BaseModel):
    """Drift violations response."""

    total_violations: int
    unsuppressed: int
    suppressed: int
    violations: list[dict[str, Any]]


class ModuleResponse(BaseModel):
    """Single module details response."""

    name: str
    path: str | None
    lines_of_code: int
    layer: str | None
    exports: list[str]
    health: dict[str, Any] | None
    dependencies: list[str]
    dependents: list[str]
    violations: list[dict[str, Any]]


class ScanRequest(BaseModel):
    """Request to scan codebase."""

    language: str = Field("python", description="Language to scan")
    path: str | None = Field(None, description="Root path to scan")


class ScanResponse(BaseModel):
    """Response from scan operation."""

    status: str
    module_count: int
    edge_count: int
    overall_grade: str


# =============================================================================
# Router
# =============================================================================


def create_gestalt_router() -> "APIRouter | None":
    """Create and configure the Gestalt API router."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/v1/world/codebase", tags=["gestalt"])

    @router.get("/manifest", response_model=ManifestResponse)
    async def get_manifest() -> ManifestResponse:
        """
        Get full architecture manifest.

        Returns module count, edges, health grades, and top modules.
        """
        result = handle_codebase_manifest([], json_output=True)
        if isinstance(result, str):
            raise HTTPException(status_code=500, detail=result)
        return ManifestResponse(**result)

    @router.get("/health", response_model=HealthResponse)
    async def get_health() -> HealthResponse:
        """
        Get health metrics summary.

        Returns grade distribution and worst/best modules.
        """
        result = handle_health_manifest([], json_output=True)
        if isinstance(result, str):
            raise HTTPException(status_code=500, detail=result)
        return HealthResponse(**result)

    @router.get("/drift", response_model=DriftResponse)
    async def get_drift() -> DriftResponse:
        """
        Get drift violations.

        Returns all architectural drift violations.
        """
        result = handle_drift_witness([], json_output=True)
        if isinstance(result, str):
            raise HTTPException(status_code=500, detail=result)
        return DriftResponse(**result)

    @router.get("/module/{module_name:path}", response_model=ModuleResponse)
    async def get_module(module_name: str) -> ModuleResponse:
        """
        Get details for a specific module.

        Args:
            module_name: Module path (e.g., agents.m.cartographer)
        """
        result = handle_module_manifest(module_name, [], json_output=True)
        if isinstance(result, str):
            if "not found" in result.lower() or "multiple modules" in result.lower():
                raise HTTPException(status_code=404, detail=result)
            raise HTTPException(status_code=500, detail=result)
        return ModuleResponse(**result)

    @router.post("/scan", response_model=ScanResponse)
    async def scan(request: ScanRequest | None = None) -> ScanResponse:
        """
        Force rescan of codebase.

        Args:
            request: Optional scan configuration
        """
        from pathlib import Path

        language = request.language if request else "python"
        root_path = Path(request.path) if request and request.path else None

        graph = sync_scan_codebase(root_path, language)

        return ScanResponse(
            status="scanned",
            module_count=graph.module_count,
            edge_count=graph.edge_count,
            overall_grade=graph.overall_grade,
        )

    @router.get("/topology", response_model=TopologyResponse)
    async def get_topology(
        max_nodes: int = Query(200, ge=10, le=1000, description="Max nodes to return"),
        min_health: float = Query(0.0, ge=0.0, le=1.0, description="Min health filter"),
    ) -> TopologyResponse:
        """
        Get graph topology for visualization.

        Returns nodes and links formatted for force-directed graph rendering.
        Positions are computed using a simple layout algorithm.
        """
        import hashlib
        import math

        graph = get_api_cached_graph()
        if not graph:
            graph = sync_scan_codebase()

        violations = get_api_cached_violations()
        violation_edges = {(v.source_module, v.target_module): v for v in violations}

        # Filter and limit modules
        modules_with_health = [
            m
            for m in graph.modules.values()
            if m.health and m.health.overall_health >= min_health
        ]
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

        # Compute positions using a deterministic spiral layout
        # based on module name hash for consistency
        nodes: list[ModuleNode] = []
        for i, module in enumerate(selected_modules):
            # Use hash for deterministic positioning
            name_hash = int(hashlib.md5(module.name.encode()).hexdigest()[:8], 16)

            # Spiral layout with layer-based z
            angle = (name_hash % 360) * math.pi / 180
            radius = 2 + (i / len(selected_modules)) * 8

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
                ModuleNode(
                    id=module.name,
                    label=module.name.split(".")[-1],  # Short name
                    layer=module.layer,
                    health_grade=module.health.grade if module.health else "?",
                    health_score=module.health.overall_health if module.health else 0.0,
                    lines_of_code=module.lines_of_code,
                    coupling=module.health.coupling if module.health else 0.0,
                    cohesion=module.health.cohesion if module.health else 1.0,
                    instability=module.health.instability if module.health else None,
                    x=round(x, 2),
                    y=round(y, 2),
                    z=round(z, 2),
                )
            )

        # Build links (only between selected modules)
        links: list[DependencyLink] = []
        for edge in graph.edges:
            if edge.source in selected_names and edge.target in selected_names:
                violation = violation_edges.get((edge.source, edge.target))
                links.append(
                    DependencyLink(
                        source=edge.source,
                        target=edge.target,
                        import_type=edge.import_type,
                        is_violation=violation is not None,
                        violation_severity=violation.severity if violation else None,
                    )
                )

        # Compute stats
        health_scores = [n.health_score for n in nodes]
        violation_count = len([l for l in links if l.is_violation])

        return TopologyResponse(
            nodes=nodes,
            links=links,
            layers=sorted(layers_set),
            stats={
                "node_count": len(nodes),
                "link_count": len(links),
                "layer_count": len(layers_set),
                "violation_count": violation_count,
                "avg_health": sum(health_scores) / len(health_scores)
                if health_scores
                else 0,
                "overall_grade": graph.overall_grade,
            },
        )

    return router
