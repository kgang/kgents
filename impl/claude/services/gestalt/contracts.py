"""
Gestalt AGENTESE Contract Definitions.

Defines request and response types for Gestalt @node contracts.
These enable BE/FE contract synchronization via AGENTESE discovery.

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest, health, topology, drift)
- Contract() for mutation aspects (scan, module)

Types here are used by:
1. @node(contracts={...}) in node.py
2. /discover?include_schemas=true endpoint
3. web/scripts/sync-types.ts for FE type generation

See: plans/autopoietic-architecture.md (Phase 7)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# === Manifest Response ===


@dataclass(frozen=True)
class GestaltManifestResponse:
    """Gestalt architecture manifest response."""

    module_count: int
    edge_count: int
    overall_grade: str
    average_health: float
    drift_count: int


# === Health Types ===


@dataclass(frozen=True)
class ModuleHealth:
    """Health metrics for a single module."""

    name: str
    health_grade: str
    health_score: float
    lines_of_code: int
    coupling: float
    cohesion: float
    instability: float | None


@dataclass(frozen=True)
class HealthResponse:
    """Response for health manifest aspect."""

    overall_grade: str
    average_health: float
    module_count: int
    modules: list[ModuleHealth]


# === Topology Types ===


@dataclass(frozen=True)
class TopologyNode:
    """A node in the 3D topology visualization."""

    id: str
    label: str
    layer: str | None
    health_grade: str
    health_score: float
    lines_of_code: int
    coupling: float
    cohesion: float
    instability: float | None
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class TopologyLink:
    """A link between topology nodes."""

    source: str
    target: str
    import_type: str
    is_violation: bool
    violation_severity: str | None


@dataclass(frozen=True)
class TopologyStats:
    """Statistics for the topology."""

    node_count: int
    link_count: int
    layer_count: int
    violation_count: int
    avg_health: float
    overall_grade: str


@dataclass(frozen=True)
class TopologyRequest:
    """Request for topology visualization data."""

    max_nodes: int = 200
    min_health: float = 0.0
    role: str | None = None


@dataclass(frozen=True)
class TopologyResponse:
    """Response for topology visualization."""

    nodes: list[TopologyNode]
    links: list[TopologyLink]
    layers: list[str]
    stats: TopologyStats


# === Drift Types ===


@dataclass(frozen=True)
class DriftViolation:
    """A single drift violation."""

    source_module: str
    target_module: str
    severity: str
    violation_type: str
    message: str


@dataclass(frozen=True)
class DriftResponse:
    """Response for drift violations."""

    violation_count: int
    violations: list[DriftViolation]


# === Module Types ===


@dataclass(frozen=True)
class ModuleRequest:
    """Request for module details."""

    module_name: str


@dataclass(frozen=True)
class ModuleDependency:
    """A module dependency."""

    target: str
    import_type: str


@dataclass(frozen=True)
class ModuleDependent:
    """A module that depends on this one."""

    source: str
    import_type: str


@dataclass(frozen=True)
class ModuleResponse:
    """Response for module details."""

    name: str
    path: str
    layer: str | None
    lines_of_code: int
    health_grade: str
    health_score: float
    coupling: float
    cohesion: float
    instability: float | None
    dependencies: list[ModuleDependency]
    dependents: list[ModuleDependent]


# === Scan Types ===


@dataclass(frozen=True)
class ScanRequest:
    """Request to rescan codebase."""

    language: str = "python"


@dataclass(frozen=True)
class ScanResponse:
    """Response after rescanning."""

    module_count: int
    edge_count: int
    overall_grade: str
    scanned_at: str


# === Exports ===

__all__ = [
    # Manifest
    "GestaltManifestResponse",
    # Health
    "ModuleHealth",
    "HealthResponse",
    # Topology
    "TopologyNode",
    "TopologyLink",
    "TopologyStats",
    "TopologyRequest",
    "TopologyResponse",
    # Drift
    "DriftViolation",
    "DriftResponse",
    # Module
    "ModuleRequest",
    "ModuleDependency",
    "ModuleDependent",
    "ModuleResponse",
    # Scan
    "ScanRequest",
    "ScanResponse",
]
