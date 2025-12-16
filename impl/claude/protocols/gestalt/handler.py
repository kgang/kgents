"""
Gestalt AGENTESE Handler.

Handles world.codebase.* paths for architecture analysis and governance.

Paths:
- world.codebase.manifest           -> Full architecture graph
- world.codebase.health.manifest    -> Health metrics summary
- world.codebase.module[name]       -> Module details
- world.codebase.drift.witness      -> Drift violations
- world.codebase.drift.refine       -> Challenge/suppress a drift rule

This handler bridges the reactive Gestalt analysis engine
to AGENTESE path invocations.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from .analysis import (
    ArchitectureGraph,
    Module,
    ModuleHealth,
    build_architecture_graph,
)
from .governance import (
    DriftViolation,
    GovernanceConfig,
    check_drift,
    create_kgents_config,
)

if TYPE_CHECKING:
    pass


# ============================================================================
# Cached Analysis State
# ============================================================================

# Global cache for the current analysis (refreshed on scan)
_cached_graph: ArchitectureGraph | None = None
_cached_violations: list[DriftViolation] | None = None
_cached_config: GovernanceConfig | None = None


def _get_project_root() -> Path:
    """Get the project root (kgents root)."""
    # Walk up from this file to find project root
    current = Path(__file__).parent
    while current != current.parent:
        if (current / ".kgents").exists() or (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return Path.cwd()


def scan_codebase(
    root: Path | None = None, language: str = "python"
) -> ArchitectureGraph:
    """
    Scan the codebase and build the architecture graph.

    This is the main entry point for analysis.
    Results are cached for subsequent queries.
    """
    global _cached_graph, _cached_violations, _cached_config

    root = root or _get_project_root()
    _cached_graph = build_architecture_graph(root, language)
    _cached_config = create_kgents_config()

    # Run drift detection
    _cached_violations = check_drift(_cached_graph, _cached_config)

    # Update health with drift scores
    for module in _cached_graph.modules.values():
        if module.health:
            # Count violations for this module
            module_violations = [
                v for v in _cached_violations if v.source_module == module.name
            ]
            violation_count = len(module_violations)
            # Drift score: 0 = no violations, 1 = many violations
            module.health.drift = min(1.0, violation_count * 0.2)

    return _cached_graph


def get_cached_graph() -> ArchitectureGraph | None:
    """Get the cached architecture graph (may be None if not scanned)."""
    return _cached_graph


def get_cached_violations() -> list[DriftViolation]:
    """Get cached drift violations."""
    return _cached_violations or []


# ============================================================================
# AGENTESE Handlers
# ============================================================================


def handle_codebase_manifest(
    args: list[str],
    json_output: bool = False,
) -> dict[str, Any] | str:
    """
    Handle: world.codebase.manifest

    Returns the full architecture graph summary.
    """
    graph = _cached_graph or scan_codebase()

    result = {
        "module_count": graph.module_count,
        "edge_count": graph.edge_count,
        "language": graph.language,
        "average_health": round(graph.average_health, 2),
        "overall_grade": graph.overall_grade,
        "modules": [
            {
                "name": m.name,
                "lines_of_code": m.lines_of_code,
                "layer": m.layer,
                "health_grade": m.health.grade if m.health else "?",
                "health_score": round(m.health.overall_health, 2) if m.health else 0,
            }
            for m in sorted(
                graph.modules.values(),
                key=lambda m: m.health.overall_health if m.health else 0,
                reverse=True,
            )[:20]  # Top 20 by health
        ],
        "drift_count": len(get_cached_violations()),
    }

    if json_output:
        return result

    # Human-readable output
    lines = [
        f"Architecture: {graph.module_count} modules, {graph.edge_count} edges",
        f"Language: {graph.language}",
        f"Overall Health: {graph.overall_grade} ({round(graph.average_health * 100)}%)",
        f"Drift Violations: {len(get_cached_violations())}",
        "",
        "Top Modules by Health:",
    ]
    modules_list = cast(list[dict[str, Any]], result["modules"])
    for mod in modules_list[:10]:
        lines.append(f"  {mod['health_grade']:3} {mod['name']}")

    return "\n".join(lines)


def handle_health_manifest(
    args: list[str],
    json_output: bool = False,
) -> dict[str, Any] | str:
    """
    Handle: world.codebase.health.manifest

    Returns health metrics summary with module rankings.
    """
    graph = _cached_graph or scan_codebase()

    # Get modules sorted by health
    modules_by_health = sorted(
        [m for m in graph.modules.values() if m.health],
        key=lambda m: m.health.overall_health if m.health else 0,
    )

    # Compute distribution
    grades = {"A+": 0, "A": 0, "B+": 0, "B": 0, "C+": 0, "C": 0, "D": 0, "F": 0}
    for m in modules_by_health:
        if m.health:
            grades[m.health.grade] = grades.get(m.health.grade, 0) + 1

    result = {
        "average_health": round(graph.average_health, 2),
        "overall_grade": graph.overall_grade,
        "grade_distribution": grades,
        "worst_modules": [
            {
                "name": m.name,
                "grade": m.health.grade if m.health else "?",
                "coupling": round(m.health.coupling, 2) if m.health else 0,
                "cohesion": round(m.health.cohesion, 2) if m.health else 0,
                "drift": round(m.health.drift, 2) if m.health else 0,
                "complexity": round(m.health.complexity, 2) if m.health else 0,
            }
            for m in modules_by_health[:5]
        ],
        "best_modules": [
            {"name": m.name, "grade": m.health.grade if m.health else "?"}
            for m in reversed(modules_by_health[-5:])
        ],
    }

    if json_output:
        return result

    # Human-readable output
    lines = [
        f"Overall: {graph.overall_grade} ({round(graph.average_health * 100)}%)",
        "",
        "Grade Distribution:",
    ]
    for grade, count in grades.items():
        if count > 0:
            lines.append(f"  {grade}: {count}")

    lines.append("")
    lines.append("Needs Attention:")
    worst_modules = cast(list[dict[str, Any]], result["worst_modules"])
    for mod in worst_modules:
        lines.append(
            f"  {mod['grade']:3} {mod['name']} "
            f"(coupling={mod['coupling']}, drift={mod['drift']})"
        )

    return "\n".join(lines)


def handle_drift_witness(
    args: list[str],
    json_output: bool = False,
) -> dict[str, Any] | str:
    """
    Handle: world.codebase.drift.witness

    Returns all drift violations.
    """
    violations = get_cached_violations()
    if not violations:
        # Try scanning first
        scan_codebase()
        violations = get_cached_violations()

    result = {
        "total_violations": len(violations),
        "unsuppressed": len([v for v in violations if not v.suppressed]),
        "suppressed": len([v for v in violations if v.suppressed]),
        "violations": [
            {
                "rule": v.rule_name,
                "source": v.source_module,
                "target": v.target_module,
                "severity": v.severity,
                "suppressed": v.suppressed,
                "line": v.edge.line_number,
            }
            for v in violations[:50]  # Limit to 50
        ],
    }

    if json_output:
        return result

    # Human-readable output
    if not violations:
        return "No drift violations detected."

    lines = [
        f"Drift Violations: {len(violations)} total ({result['unsuppressed']} active)",
        "",
    ]
    for v in violations[:20]:
        status = "[suppressed] " if v.suppressed else ""
        lines.append(
            f"  {status}{v.severity.upper()}: {v.source_module} -> {v.target_module}"
        )
        lines.append(f"    Rule: {v.rule_name} (line {v.edge.line_number})")

    if len(violations) > 20:
        lines.append(f"\n  ... and {len(violations) - 20} more")

    return "\n".join(lines)


def handle_module_manifest(
    module_name: str,
    args: list[str],
    json_output: bool = False,
) -> dict[str, Any] | str:
    """
    Handle: world.codebase.module[name].manifest

    Returns details for a specific module.
    """
    graph = _cached_graph or scan_codebase()

    # Find module (fuzzy match)
    module = graph.modules.get(module_name)
    if not module:
        # Try partial match
        matches = [m for m in graph.modules.values() if module_name in m.name]
        if len(matches) == 1:
            module = matches[0]
        elif len(matches) > 1:
            return f"Multiple modules match '{module_name}': {[m.name for m in matches[:5]]}"
        else:
            return f"Module not found: {module_name}"

    deps = graph.get_dependencies(module.name)
    dependents = graph.get_dependents(module.name)
    violations = [v for v in get_cached_violations() if v.source_module == module.name]

    result = {
        "name": module.name,
        "path": str(module.path) if module.path else None,
        "lines_of_code": module.lines_of_code,
        "layer": module.layer,
        "exports": module.exported_symbols[:20],
        "health": (
            {
                "grade": module.health.grade,
                "score": round(module.health.overall_health, 2),
                "coupling": round(module.health.coupling, 2),
                "cohesion": round(module.health.cohesion, 2),
                "drift": round(module.health.drift, 2),
                "complexity": round(module.health.complexity, 2),
                "instability": (
                    round(module.health.instability, 2)
                    if module.health.instability is not None
                    else None
                ),
            }
            if module.health
            else None
        ),
        "dependencies": deps[:20],
        "dependents": dependents[:20],
        "violations": [
            {"rule": v.rule_name, "target": v.target_module} for v in violations
        ],
    }

    if json_output:
        return result

    # Human-readable output
    lines = [
        f"Module: {module.name}",
        f"Path: {module.path}",
        f"LOC: {module.lines_of_code}",
        f"Layer: {module.layer or 'unassigned'}",
    ]

    if module.health:
        lines.append(
            f"Health: {module.health.grade} ({round(module.health.overall_health * 100)}%)"
        )
        lines.append(f"  Coupling: {round(module.health.coupling * 100)}%")
        lines.append(f"  Cohesion: {round(module.health.cohesion * 100)}%")
        lines.append(f"  Drift: {round(module.health.drift * 100)}%")
        lines.append(f"  Complexity: {round(module.health.complexity * 100)}%")

    if deps:
        lines.append(f"\nDepends on ({len(deps)}):")
        for d in deps[:10]:
            lines.append(f"  -> {d}")

    if dependents:
        lines.append(f"\nDepended upon by ({len(dependents)}):")
        for d in dependents[:10]:
            lines.append(f"  <- {d}")

    if violations:
        lines.append(f"\nDrift Violations ({len(violations)}):")
        for v in violations[:5]:
            lines.append(f"  {v.rule_name}: -> {v.target_module}")

    return "\n".join(lines)


# ============================================================================
# CLI Command Entry Point
# ============================================================================


def cmd_codebase(args: list[str], ctx: Any = None) -> int:
    """
    CLI handler for world.codebase.* commands.

    Usage:
        kgents world codebase                   # Overview (manifest)
        kgents world codebase health            # Health summary
        kgents world codebase drift             # Drift violations
        kgents world codebase module <name>     # Module details
        kgents world codebase scan              # Force rescan
    """
    json_output = "--json" in args
    args = [a for a in args if a != "--json"]

    if not args or args[0] in ("manifest", "status"):
        result = handle_codebase_manifest(args[1:] if args else [], json_output)
    elif args[0] == "health":
        result = handle_health_manifest(args[1:], json_output)
    elif args[0] == "drift":
        result = handle_drift_witness(args[1:], json_output)
    elif args[0] == "module" and len(args) > 1:
        result = handle_module_manifest(args[1], args[2:], json_output)
    elif args[0] == "scan":
        # Force rescan
        language = args[1] if len(args) > 1 else "python"
        root_path = Path(args[2]) if len(args) > 2 else None
        scan_codebase(root_path, language)
        result = handle_codebase_manifest([], json_output)
    else:
        result = (
            f"Unknown subcommand: {args[0]}. Try: manifest, health, drift, module, scan"
        )

    if json_output and isinstance(result, dict):
        print(json.dumps(result, indent=2, default=str))
    else:
        print(result)

    return 0
