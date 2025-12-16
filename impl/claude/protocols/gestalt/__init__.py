"""
Gestalt: Living Architecture Visualizer.

> "Architecture diagrams rot the moment they're drawn.
>  Gestalt never rots because it never stops watching."

This protocol provides:
- Static analysis for Python + TypeScript codebases
- Architecture health metrics (coupling, cohesion, drift, complexity)
- Layer/ring governance with drift detection
- Reactive Signal[ArchitectureGraph] for live updates
- Multi-target projections (CLI, Web, VR)

AGENTESE Paths:
- world.codebase.manifest         -> Full architecture graph
- world.codebase.module[name]     -> Module details
- world.codebase.drift.witness    -> Drift violations
- world.codebase.health.manifest  -> Health metrics

Phase 1 implements: Core analysis engine (Python + TypeScript)
"""

from .analysis import (
    ArchitectureGraph,
    DependencyEdge,
    Module,
    ModuleHealth,
    analyze_python_imports,
    analyze_typescript_imports,
    build_architecture_graph,
)
from .governance import (
    DriftRule,
    DriftViolation,
    GovernanceConfig,
    LayerRule,
    RingRule,
    check_drift,
)

__all__ = [
    # Analysis
    "ArchitectureGraph",
    "DependencyEdge",
    "Module",
    "ModuleHealth",
    "analyze_python_imports",
    "analyze_typescript_imports",
    "build_architecture_graph",
    # Governance
    "DriftRule",
    "DriftViolation",
    "GovernanceConfig",
    "LayerRule",
    "RingRule",
    "check_drift",
]
