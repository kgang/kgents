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
to AGENTESE path invocations via GestaltStore.

Phase 2 (Spike 6A): Commands now use GestaltStore reactive substrate
instead of static cache for live updates and --watch mode.

Usage:
    kg world codebase                   # Architecture overview
    kg world codebase health            # Health metrics
    kg world codebase drift             # Drift violations
    kg world codebase module <name>     # Module details
    kg world codebase scan              # Force rescan
    kg world codebase --watch           # Watch for changes
    kg world codebase --help            # Show help

Options:
    --json      Output as JSON
    --watch     Start file watching for live updates
    --help      Show help message
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from opentelemetry import trace

from .analysis import ArchitectureGraph, Module, ModuleHealth
from .governance import DriftViolation

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

    from .reactive import GestaltStore

# Import path display for Wave 0 Foundation 1
from protocols.cli.path_display import (
    apply_path_flags,
    display_path_header,
    parse_path_flags,
)

# Import synergy for Wave 0 Foundation 4
from protocols.synergy import (
    SynergyResult,
    create_analysis_complete_event,
    get_synergy_bus,
)

# OTEL tracer for Gestalt operations
_tracer = trace.get_tracer("kgents.gestalt", "0.1.0")

# Span attribute constants
ATTR_SUBCOMMAND = "gestalt.subcommand"
ATTR_MODULE_COUNT = "gestalt.module_count"
ATTR_DRIFT_COUNT = "gestalt.drift_count"
ATTR_DURATION_MS = "gestalt.duration_ms"


# ============================================================================
# GestaltStore Instance Management
# ============================================================================

# Module-level store instance with thread-safe initialization
_gestalt_store: "GestaltStore | None" = None
_store_lock = threading.Lock()

# Test hook: override to inject a mock store
_store_factory: Any = None


def _get_project_root(prefer_repo_root: bool = True) -> Path:
    """Get the project root (kgents root).

    Args:
        prefer_repo_root: If True, prefer repo root (.git/.kgents) over nearest
            pyproject.toml. This ensures scans include sibling trees (spec/, agents/).
            Set to False to use impl/claude as root for implementation-only scans.

    Returns:
        Project root path.
    """
    current = Path(__file__).parent

    # Priority markers (in order):
    # 1. .kgents (explicit kgents marker)
    # 2. .git (repo root)
    # 3. pyproject.toml (fallback to nearest Python project)
    pyproject_root: Path | None = None

    while current != current.parent:
        # Check for repo-level markers first
        if (current / ".kgents").exists():
            return current
        if prefer_repo_root and (current / ".git").exists():
            return current
        # Remember first pyproject.toml as fallback
        if pyproject_root is None and (current / "pyproject.toml").exists():
            pyproject_root = current
        current = current.parent

    # Fallback: use pyproject.toml location or cwd
    return pyproject_root or Path.cwd()


def _get_store(root: Path | None = None, language: str = "python") -> "GestaltStore":
    """Get or create the GestaltStore instance (thread-safe).

    Uses double-checked locking pattern for efficient thread-safe
    lazy initialization.

    Tests can inject a factory via _set_store_factory() to avoid
    filesystem scanning.

    Args:
        root: Root directory for analysis (defaults to project root)
        language: Language to analyze ("python" or "typescript")

    Returns:
        GestaltStore instance
    """
    global _gestalt_store, _store_factory
    if _gestalt_store is None:
        with _store_lock:
            # Double-check after acquiring lock
            if _gestalt_store is None:
                if _store_factory is not None:
                    # Test injection: use factory
                    _gestalt_store = _store_factory()
                else:
                    # Production: create real store
                    from .reactive import GestaltStore as GS

                    actual_root = root or _get_project_root()
                    _gestalt_store = GS(root=actual_root, language=language)
    return _gestalt_store


def _set_store_factory(factory: Any) -> None:
    """Set a factory function for GestaltStore (test hook).

    Call with None to reset to default behavior.

    Args:
        factory: Callable that returns a GestaltStore instance, or None to reset.
    """
    global _gestalt_store, _store_factory
    with _store_lock:
        _store_factory = factory
        _gestalt_store = None  # Reset cached instance


def _reset_store() -> None:
    """Reset the store instance (for testing)."""
    global _gestalt_store
    with _store_lock:
        if _gestalt_store is not None:
            _gestalt_store.dispose()
        _gestalt_store = None


async def _ensure_scanned(store: "GestaltStore") -> None:
    """Ensure store has been scanned at least once."""
    if store.module_count.value == 0:
        await store.scan()


# Legacy compatibility functions
def scan_codebase(
    root: Path | None = None, language: str = "python"
) -> ArchitectureGraph:
    """
    Scan the codebase and build the architecture graph.

    This is the main entry point for analysis.
    Now uses GestaltStore internally.
    """
    # Reset store with new parameters if needed
    global _gestalt_store
    with _store_lock:
        if _gestalt_store is not None:
            _gestalt_store.dispose()
        _gestalt_store = None

    store = _get_store(root, language)
    asyncio.run(store.scan())
    return store.graph.value


def get_cached_graph() -> ArchitectureGraph | None:
    """Get the cached architecture graph (may be None if not scanned)."""
    global _gestalt_store
    if _gestalt_store is None:
        return None
    return _gestalt_store.graph.value


def get_cached_violations() -> list[DriftViolation]:
    """Get cached drift violations."""
    global _gestalt_store
    if _gestalt_store is None:
        return []
    return _gestalt_store.violations.value


# ============================================================================
# Help and Output Utilities
# ============================================================================


def print_help() -> None:
    """Print gestalt command help."""
    help_text = """
kg world codebase - Gestalt Architecture Visualizer

Commands:
  kg world codebase              Architecture overview (manifest)
  kg world codebase health       Health metrics summary
  kg world codebase drift        Drift violations
  kg world codebase module NAME  Module details
  kg world codebase scan         Force rescan of codebase

Options:
  --json       Output as JSON
  --watch      Start file watching for live updates
  --show-paths Show AGENTESE path headers (default)
  --no-paths   Hide AGENTESE path headers
  --trace      Show detailed path trace (verbose mode)
  --help       Show this help message

Examples:
  kg world codebase                      # Quick overview
  kg world codebase health --json        # Health as JSON
  kg world codebase drift                # Show violations
  kg world codebase module protocols.api # Module details
  kg world codebase --watch              # Watch for changes
  kg world codebase --trace              # Show detailed path info

AGENTESE Paths:
  world.codebase.manifest           Full architecture graph
  world.codebase.health.manifest    Health metrics
  world.codebase.drift.witness      Drift violations
  world.codebase.module[name].manifest  Module details

Tip: You can invoke AGENTESE paths directly:
  kg world.codebase.manifest
  kg world.codebase.health.manifest
"""
    print(help_text.strip())


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
    json_output: bool = False,
) -> None:
    """
    Emit output via dual-channel if ctx available, else print.

    Args:
        human: Human-readable string (goes to stdout)
        semantic: Structured data (goes to FD3 for agents)
        ctx: InvocationContext if available
        json_output: If True, print JSON instead of human text
    """
    if json_output:
        print(json.dumps(semantic, indent=2, default=str))
    elif ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)


def _emit_error(
    message: str,
    ctx: "InvocationContext | None",
) -> None:
    """Emit error with consistent format."""
    _emit_output(
        f"[GESTALT] X {message}",
        {"error": message},
        ctx,
    )


# ============================================================================
# AGENTESE Handlers
# ============================================================================


def handle_codebase_manifest(
    args: list[str],
    json_output: bool = False,
    store: "GestaltStore | None" = None,
) -> dict[str, Any] | str:
    """
    Handle: world.codebase.manifest

    Returns the full architecture graph summary.
    Uses GestaltStore reactive properties:
    - store.module_count.value
    - store.edge_count.value
    - store.overall_grade.value
    - store.average_health.value
    - store.drift_count.value
    """
    # Display AGENTESE path header (Wave 0 Foundation 1)
    display_path_header(
        path="world.codebase.manifest",
        aspect="manifest",
        effects=["ARCHITECTURE_ANALYZED", "GRAPH_BUILT"],
    )

    if store is None:
        store = _get_store()
        asyncio.run(_ensure_scanned(store))

    # Read from reactive Computed signals
    module_count = store.module_count.value
    edge_count = store.edge_count.value
    overall_grade = store.overall_grade.value
    average_health = store.average_health.value
    drift_count = store.drift_count.value
    graph = store.graph.value

    result = {
        "module_count": module_count,
        "edge_count": edge_count,
        "language": graph.language,
        "average_health": round(average_health, 2),
        "overall_grade": overall_grade,
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
        "drift_count": drift_count,
    }

    if json_output:
        return result

    # Human-readable output
    lines = [
        f"Architecture: {module_count} modules, {edge_count} edges",
        f"Language: {graph.language}",
        f"Overall Health: {overall_grade} ({round(average_health * 100)}%)",
        f"Drift Violations: {drift_count}",
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
    store: "GestaltStore | None" = None,
) -> dict[str, Any] | str:
    """
    Handle: world.codebase.health.manifest

    Returns health metrics summary with module rankings.
    Uses GestaltStore reactive properties:
    - store.average_health.value
    - store.overall_grade.value
    - store.grade_distribution.value
    - store.worst_modules.value
    - store.module_healths.value
    """
    # Display AGENTESE path header (Wave 0 Foundation 1)
    display_path_header(
        path="world.codebase.health.manifest",
        aspect="manifest",
        effects=["HEALTH_COMPUTED", "GRADES_ASSIGNED"],
    )

    if store is None:
        store = _get_store()
        asyncio.run(_ensure_scanned(store))

    # Read from reactive Computed signals
    average_health = store.average_health.value
    overall_grade = store.overall_grade.value
    grade_distribution = store.grade_distribution.value
    worst_modules_raw = store.worst_modules.value  # List of (name, health_score)
    module_healths = store.module_healths.value
    graph = store.graph.value

    # Get modules sorted by health for detailed info
    modules_by_health = sorted(
        [m for m in graph.modules.values() if m.health],
        key=lambda m: m.health.overall_health if m.health else 0,
    )

    result = {
        "average_health": round(average_health, 2),
        "overall_grade": overall_grade,
        "grade_distribution": grade_distribution,
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
        f"Overall: {overall_grade} ({round(average_health * 100)}%)",
        "",
        "Grade Distribution:",
    ]
    for grade, count in grade_distribution.items():
        if count > 0:
            lines.append(f"  {grade}: {count}")

    lines.append("")
    lines.append("Needs Attention:")
    worst_modules_list = cast(list[dict[str, Any]], result["worst_modules"])
    for mod in worst_modules_list:
        lines.append(
            f"  {mod['grade']:3} {mod['name']} "
            f"(coupling={mod['coupling']}, drift={mod['drift']})"
        )

    return "\n".join(lines)


def handle_drift_witness(
    args: list[str],
    json_output: bool = False,
    store: "GestaltStore | None" = None,
) -> dict[str, Any] | str:
    """
    Handle: world.codebase.drift.witness

    Returns all drift violations.
    Uses GestaltStore reactive properties:
    - store.violations.value (Signal)
    - store.drift_count.value
    - store.active_drift_count.value
    """
    # Display AGENTESE path header (Wave 0 Foundation 1)
    display_path_header(
        path="world.codebase.drift.witness",
        aspect="witness",
        effects=["VIOLATIONS_DETECTED", "DRIFT_TRACED"],
    )

    if store is None:
        store = _get_store()
        asyncio.run(_ensure_scanned(store))

    # Read from reactive Signal
    violations = store.violations.value
    drift_count = store.drift_count.value
    active_count = store.active_drift_count.value

    result = {
        "total_violations": drift_count,
        "unsuppressed": active_count,
        "suppressed": drift_count - active_count,
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
        f"Drift Violations: {drift_count} total ({active_count} active)",
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
    store: "GestaltStore | None" = None,
) -> dict[str, Any] | str:
    """
    Handle: world.codebase.module[name].manifest

    Returns details for a specific module.
    Uses GestaltStore to get module data and violations.
    """
    # Display AGENTESE path header (Wave 0 Foundation 1)
    display_path_header(
        path=f"world.codebase.module[{module_name}].manifest",
        aspect="manifest",
        effects=["MODULE_ANALYZED"],
    )

    if store is None:
        store = _get_store()
        asyncio.run(_ensure_scanned(store))

    graph = store.graph.value
    violations_all = store.violations.value

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
    violations = [v for v in violations_all if v.source_module == module.name]

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


def _run_watch_mode(store: "GestaltStore") -> None:
    """Run watch mode - continuously monitor architecture changes.

    Prints updates when the architecture graph changes.
    Press Ctrl+C to exit.
    """

    def on_change(graph: ArchitectureGraph) -> None:
        """Callback when graph changes."""
        print(
            f"\r⟳ Updated: {graph.module_count} modules, {graph.edge_count} edges",
            end="",
        )
        print(
            f" | {store.overall_grade.value} ({round(store.average_health.value * 100)}%)"
        )

    def on_violation_change(violations: list[DriftViolation]) -> None:
        """Callback when violations change."""
        active = len([v for v in violations if not v.suppressed])
        if active > 0:
            print(f"  ⚠ {active} active drift violations")

    # Subscribe to changes
    unsub_graph = store.subscribe_to_changes(on_change)
    unsub_violations = store.subscribe_to_violations(on_violation_change)

    try:
        print(f"👁 Watching {store.root} for changes...")
        print(
            f"   Current: {store.module_count.value} modules, {store.overall_grade.value}"
        )
        print("   Press Ctrl+C to stop\n")

        # Keep running until interrupted
        while True:
            asyncio.run(asyncio.sleep(1))
    except KeyboardInterrupt:
        print("\n\n✓ Stopped watching")
    finally:
        unsub_graph()
        unsub_violations()
        asyncio.run(store.stop_watching())


# =============================================================================
# Synergy Integration (Wave 0 Foundation 4)
# =============================================================================


def _emit_synergy_event(store: "GestaltStore") -> None:
    """
    Emit a synergy event for analysis completion.

    This triggers cross-jewel communication:
    - Brain receives architecture snapshot for memory
    - CLI shows synergy notification to user
    """
    import uuid

    bus = get_synergy_bus()

    # Subscribe to results for CLI notification (temporary)
    results: list[SynergyResult] = []

    def on_result(event: Any, result: SynergyResult) -> None:
        results.append(result)

    unsub = bus.subscribe_results(on_result)

    try:
        # Create and emit the event
        event = create_analysis_complete_event(
            source_id=str(uuid.uuid4()),
            module_count=store.module_count.value,
            health_grade=store.overall_grade.value,
            average_health=store.average_health.value,
            drift_count=store.drift_count.value,
            root_path=str(store.root),
        )

        # Emit and wait for results (for CLI notification)
        asyncio.run(bus.emit_and_wait(event))

        # Display synergy notifications
        for result in results:
            if result.success and result.artifact_id:
                print(f"  \u21b3 \U0001f517 Synergy: {result.message}")
                print(f'  \u21b3 Crystal: "{result.artifact_id}"')
            elif result.success and result.metadata.get("skipped"):
                pass  # Don't show skipped handlers
            elif not result.success:
                # Log but don't show failures to user
                pass
    finally:
        unsub()


def cmd_codebase(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    CLI handler for world.codebase.* commands.

    Usage:
        kgents world codebase                   # Overview (manifest)
        kgents world codebase health            # Health summary
        kgents world codebase drift             # Drift violations
        kgents world codebase module <name>     # Module details
        kgents world codebase scan              # Force rescan
        kgents world codebase --watch           # Watch for changes

    Options:
        --json       Output as JSON
        --watch      Start file watching for live updates
        --show-paths Show AGENTESE path headers (default)
        --no-paths   Hide AGENTESE path headers
        --trace      Show detailed path trace
        --help       Show help message
    """
    start_time = time.perf_counter()

    # Parse flags first (before OTEL span so help is fast)
    if "--help" in args or "-h" in args:
        print_help()
        return 0

    # Parse path visibility flags (Wave 0 Foundation 1)
    args_list = list(args)  # Ensure it's a list
    args_list, show_paths, trace_mode = parse_path_flags(args_list)
    apply_path_flags(show_paths, trace_mode)

    json_output = "--json" in args_list
    watch_mode = "--watch" in args_list
    args = [a for a in args_list if a not in ("--json", "--watch", "--help", "-h")]

    # Determine subcommand for span naming
    subcommand = args[0] if args else "manifest"
    if subcommand in ("manifest", "status"):
        subcommand = "manifest"

    # Wrap all operations in OTEL span
    with _tracer.start_as_current_span(f"gestalt.{subcommand}") as span:
        span.set_attribute(ATTR_SUBCOMMAND, subcommand)

        try:
            # Get or create the store
            store = _get_store()

            # Ensure scanned for all commands
            asyncio.run(_ensure_scanned(store))

            # Record store metrics in span
            span.set_attribute(ATTR_MODULE_COUNT, store.module_count.value)
            span.set_attribute(ATTR_DRIFT_COUNT, store.drift_count.value)

            # Handle watch mode
            if watch_mode:
                asyncio.run(store.start_watching())
                _run_watch_mode(store)
                return 0

            # Route to appropriate handler
            result: dict[str, Any] | str
            if not args or args[0] in ("manifest", "status"):
                result = handle_codebase_manifest(
                    args[1:] if args else [], json_output, store
                )
            elif args[0] == "health":
                result = handle_health_manifest(args[1:], json_output, store)
            elif args[0] == "drift":
                result = handle_drift_witness(args[1:], json_output, store)
            elif args[0] == "module":
                if len(args) < 2:
                    _emit_error("Missing module name", ctx)
                    print("Usage: kg world codebase module <name>")
                    return 1
                result = handle_module_manifest(args[1], args[2:], json_output, store)
            elif args[0] == "scan":
                # Force rescan
                language = args[1] if len(args) > 1 else "python"
                root_path = Path(args[2]) if len(args) > 2 else None
                scan_codebase(root_path, language)
                result = handle_codebase_manifest([], json_output, store)
            else:
                _emit_error(f"Unknown subcommand: {args[0]}", ctx)
                print("Try: manifest, health, drift, module, scan, --watch")
                print("Use --help for usage information")
                return 1

            # Emit output via dual-channel if possible
            if isinstance(result, dict):
                # JSON mode or structured output
                if json_output:
                    print(json.dumps(result, indent=2, default=str))
                else:
                    # Convert dict to human-readable
                    print(_dict_to_human(result, subcommand))
            else:
                # Already human-readable string
                print(result)

            # Wave 0 Foundation 4: Emit synergy event for manifest commands
            # This triggers cross-jewel communication (e.g., Brain auto-capture)
            if subcommand == "manifest" and not json_output:
                try:
                    _emit_synergy_event(store)
                except Exception as e:
                    # Synergy failures shouldn't break the main command
                    logger = logging.getLogger("kgents.gestalt")
                    logger.debug(f"Synergy emission failed (non-critical): {e}")

            # Record timing
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            span.set_attribute(ATTR_DURATION_MS, elapsed_ms)

            return 0

        except FileNotFoundError as e:
            _emit_error(f"File not found: {e}", ctx)
            return 1
        except PermissionError as e:
            _emit_error(f"Permission denied: {e}", ctx)
            return 1
        except ValueError as e:
            _emit_error(f"Invalid value: {e}", ctx)
            return 1
        except Exception as e:
            _emit_error(f"Unexpected error: {e}", ctx)
            # Record error in span
            span.record_exception(e)
            return 1


def _dict_to_human(data: dict[str, Any], subcommand: str) -> str:
    """Convert structured result to human-readable format.

    This is a fallback when the handler returns a dict but json_output is False.
    """
    if subcommand == "manifest":
        return (
            f"Architecture: {data.get('module_count', 0)} modules, "
            f"{data.get('edge_count', 0)} edges\n"
            f"Health: {data.get('overall_grade', '?')} "
            f"({round(data.get('average_health', 0) * 100)}%)\n"
            f"Drift: {data.get('drift_count', 0)} violations"
        )
    elif subcommand == "health":
        return (
            f"Overall: {data.get('overall_grade', '?')} "
            f"({round(data.get('average_health', 0) * 100)}%)"
        )
    elif subcommand == "drift":
        return f"Drift Violations: {data.get('total_violations', 0)}"
    else:
        # Generic fallback
        return json.dumps(data, indent=2, default=str)
