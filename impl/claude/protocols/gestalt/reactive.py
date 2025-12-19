"""
Gestalt Reactive Substrate.

Wraps the architecture analysis engine in reactive primitives:
- Signal[ArchitectureGraph] for the core graph state
- Computed derivations for health, drift, module counts
- File watcher for incremental updates

Phase 2 of Gestalt implementation.

Usage:
    from protocols.gestalt.reactive import GestaltStore

    store = GestaltStore(root=Path("/path/to/project"))
    await store.scan()  # Initial scan

    # Derived values auto-update
    print(store.module_count.value)
    print(store.overall_grade.value)

    # Start watching for changes
    await store.start_watching()

    # Subscribe to changes
    store.graph.subscribe(lambda g: print(f"Updated: {g.module_count} modules"))
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from agents.i.reactive.signal import Computed, Effect, Signal

from .analysis import (
    ArchitectureGraph,
    DependencyEdge,
    Module,
    ModuleHealth,
    analyze_python_file,
    analyze_typescript_file,
    build_architecture_graph,
    discover_python_modules,
    discover_typescript_modules,
)
from .governance import (
    DriftViolation,
    GovernanceConfig,
    check_drift,
    create_kgents_config,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# ============================================================================
# Incremental Diff Types
# ============================================================================


@dataclass(frozen=True)
class FileDiff:
    """Represents a file change for incremental updates."""

    path: Path
    change_type: str  # "created", "modified", "deleted"
    timestamp: float = field(default_factory=time.time)


@dataclass
class IncrementalUpdate:
    """Result of an incremental graph update."""

    added_modules: list[str] = field(default_factory=list)
    modified_modules: list[str] = field(default_factory=list)
    removed_modules: list[str] = field(default_factory=list)
    new_violations: list[DriftViolation] = field(default_factory=list)
    resolved_violations: list[DriftViolation] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def has_changes(self) -> bool:
        """Check if any changes occurred."""
        return bool(
            self.added_modules
            or self.modified_modules
            or self.removed_modules
            or self.new_violations
            or self.resolved_violations
        )


# ============================================================================
# GestaltStore: Reactive Architecture Graph
# ============================================================================


class GestaltStore:
    """
    Reactive store for architecture analysis.

    Wraps ArchitectureGraph in a Signal with derived Computed values.
    Supports incremental updates via file watching.

    The store follows the reactive pattern:
    - graph: Signal[ArchitectureGraph] - the source of truth
    - module_count, drift_count, etc.: Computed[T] - derived values
    - Effects can be attached for side effects (logging, notifications)

    Example:
        store = GestaltStore(root=Path("./my_project"))
        await store.scan()

        # Reactive derivations
        print(f"Modules: {store.module_count.value}")
        print(f"Health: {store.overall_grade.value}")

        # Subscribe to changes
        store.graph.subscribe(lambda g: print(f"Graph updated"))

        # Start watching
        await store.start_watching()
    """

    def __init__(
        self,
        root: Path | None = None,
        language: str = "python",
        config: GovernanceConfig | None = None,
    ) -> None:
        """
        Initialize the store.

        Args:
            root: Root directory to analyze (defaults to cwd)
            language: "python" or "typescript"
            config: Governance configuration (defaults to kgents config)
        """
        self._root = root or Path.cwd()
        self._language = language
        self._config = config or create_kgents_config()

        # Core reactive state
        self._graph: Signal[ArchitectureGraph] = Signal.of(
            ArchitectureGraph(root_path=self._root, language=language)
        )
        self._violations: Signal[list[DriftViolation]] = Signal.of([])

        # File tracking for incremental updates
        self._file_mtimes: dict[Path, float] = {}

        # Watcher state
        self._watcher_running = False
        self._watcher_task: asyncio.Task[None] | None = None
        self._observer: Any = None

        # Debounce state
        self._pending_changes: dict[Path, FileDiff] = {}
        self._debounce_seconds = 0.3
        self._debounce_task: asyncio.Task[None] | None = None

        # Setup derived computeds
        self._setup_computeds()

    def _setup_computeds(self) -> None:
        """Setup derived computed values."""
        # Module count
        self._module_count = Computed.of(
            compute=lambda: self._graph.value.module_count,
            sources=[self._graph],
        )

        # Edge count
        self._edge_count = Computed.of(
            compute=lambda: self._graph.value.edge_count,
            sources=[self._graph],
        )

        # Average health
        self._average_health = Computed.of(
            compute=lambda: self._graph.value.average_health,
            sources=[self._graph],
        )

        # Overall grade
        self._overall_grade = Computed.of(
            compute=lambda: self._graph.value.overall_grade,
            sources=[self._graph],
        )

        # Drift count
        self._drift_count = Computed.of(
            compute=lambda: len(self._violations.value),
            sources=[self._violations],
        )

        # Active (unsuppressed) drift count
        self._active_drift_count = Computed.of(
            compute=lambda: len([v for v in self._violations.value if not v.suppressed]),
            sources=[self._violations],
        )

        # Module health map
        self._module_healths = Computed.of(
            compute=lambda: {
                name: m.health
                for name, m in self._graph.value.modules.items()
                if m.health is not None
            },
            sources=[self._graph],
        )

        # Worst modules (by health)
        self._worst_modules = Computed.of(
            compute=lambda: sorted(
                [
                    (name, m.health.overall_health)
                    for name, m in self._graph.value.modules.items()
                    if m.health
                ],
                key=lambda x: x[1],
            )[:10],
            sources=[self._graph],
        )

        # Grade distribution
        self._grade_distribution = Computed.of(
            compute=self._compute_grade_distribution,
            sources=[self._graph],
        )

    def _compute_grade_distribution(self) -> dict[str, int]:
        """Compute distribution of grades across modules."""
        grades: dict[str, int] = {
            "A+": 0,
            "A": 0,
            "B+": 0,
            "B": 0,
            "C+": 0,
            "C": 0,
            "D": 0,
            "F": 0,
        }
        for module in self._graph.value.modules.values():
            if module.health:
                grade = module.health.grade
                grades[grade] = grades.get(grade, 0) + 1
        return grades

    # ========================================================================
    # Properties: Access reactive values
    # ========================================================================

    @property
    def graph(self) -> Signal[ArchitectureGraph]:
        """The core architecture graph signal."""
        return self._graph

    @property
    def violations(self) -> Signal[list[DriftViolation]]:
        """Drift violations signal."""
        return self._violations

    @property
    def module_count(self) -> Computed[int]:
        """Computed module count."""
        return self._module_count

    @property
    def edge_count(self) -> Computed[int]:
        """Computed edge count."""
        return self._edge_count

    @property
    def average_health(self) -> Computed[float]:
        """Computed average health score."""
        return self._average_health

    @property
    def overall_grade(self) -> Computed[str]:
        """Computed overall grade."""
        return self._overall_grade

    @property
    def drift_count(self) -> Computed[int]:
        """Computed total drift violation count."""
        return self._drift_count

    @property
    def active_drift_count(self) -> Computed[int]:
        """Computed active (unsuppressed) drift count."""
        return self._active_drift_count

    @property
    def module_healths(self) -> Computed[dict[str, ModuleHealth | None]]:
        """Computed map of module names to health."""
        return self._module_healths

    @property
    def worst_modules(self) -> Computed[list[tuple[str, float]]]:
        """Computed list of worst modules by health."""
        return self._worst_modules

    @property
    def grade_distribution(self) -> Computed[dict[str, int]]:
        """Computed grade distribution."""
        return self._grade_distribution

    @property
    def root(self) -> Path:
        """Root directory being analyzed."""
        return self._root

    @property
    def language(self) -> str:
        """Language being analyzed."""
        return self._language

    # ========================================================================
    # Scanning: Full and Incremental
    # ========================================================================

    async def scan(self) -> ArchitectureGraph:
        """
        Perform a full scan of the codebase.

        This rebuilds the entire graph from scratch.
        Use for initial load or when incremental updates
        have gotten out of sync.

        Returns:
            The updated ArchitectureGraph
        """
        start = time.perf_counter()

        # Build the graph
        graph = build_architecture_graph(self._root, self._language)

        # Run drift detection
        violations = check_drift(graph, self._config)

        # Update module health with drift scores
        for module in graph.modules.values():
            if module.health:
                module_violations = [v for v in violations if v.source_module == module.name]
                module.health.drift = min(1.0, len(module_violations) * 0.2)

        # Track file mtimes for incremental updates
        self._file_mtimes.clear()
        for module in graph.modules.values():
            if module.path and module.path.exists():
                self._file_mtimes[module.path] = module.path.stat().st_mtime

        # Update signals (triggers all derived computeds)
        # Force update by creating new list even if empty (Signal uses != check)
        self._graph.set(graph)
        # Always create new list to ensure Signal detects change
        self._violations.set(list(violations))

        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            f"Full scan complete: {graph.module_count} modules, "
            f"{len(violations)} violations in {elapsed:.1f}ms"
        )

        return graph

    async def scan_incremental(self, changes: list[FileDiff]) -> IncrementalUpdate:
        """
        Perform an incremental update based on file changes.

        Only re-analyzes changed files and updates affected metrics.
        Much faster than full scan for small changes.

        Args:
            changes: List of file changes to process

        Returns:
            IncrementalUpdate with details of what changed
        """
        start = time.perf_counter()
        result = IncrementalUpdate()

        if not changes:
            return result

        # Get current graph state - create a new graph to ensure Signal detects change
        old_graph = self._graph.value
        graph = ArchitectureGraph(
            modules=dict(old_graph.modules),
            edges=list(old_graph.edges),
            root_path=old_graph.root_path,
            language=old_graph.language,
        )
        old_violations = set(
            (v.source_module, v.target_module, v.rule_name) for v in self._violations.value
        )

        # Process each change
        for diff in changes:
            if diff.change_type == "deleted":
                # Remove module
                module_name = self._path_to_module_name(diff.path)
                if module_name in graph.modules:
                    del graph.modules[module_name]
                    # Remove edges from/to this module
                    graph.edges = [
                        e
                        for e in graph.edges
                        if e.source != module_name and e.target != module_name
                    ]
                    result.removed_modules.append(module_name)
                    self._file_mtimes.pop(diff.path, None)

            elif diff.change_type in ("created", "modified"):
                # Analyze the file
                if self._language == "python" and diff.path.suffix == ".py":
                    module = analyze_python_file(diff.path)
                elif self._language == "typescript" and diff.path.suffix in (
                    ".ts",
                    ".tsx",
                ):
                    module = analyze_typescript_file(diff.path)
                else:
                    continue

                # Update module name to relative path
                try:
                    rel_path = diff.path.relative_to(self._root)
                    module.name = str(rel_path.with_suffix("")).replace("/", ".")
                except ValueError:
                    pass

                # Track if new or modified
                if module.name in graph.modules:
                    result.modified_modules.append(module.name)
                    # Remove old edges from this module
                    graph.edges = [e for e in graph.edges if e.source != module.name]
                else:
                    result.added_modules.append(module.name)

                # Add/update module and its edges
                graph.modules[module.name] = module
                graph.edges.extend(module.imports)
                self._file_mtimes[diff.path] = diff.timestamp

        # Recompute health for affected modules
        affected = set(result.added_modules + result.modified_modules + result.removed_modules)
        self._recompute_health(graph, affected)

        # Rerun drift detection
        new_violations = check_drift(graph, self._config)

        # Update drift scores in health
        for module in graph.modules.values():
            if module.health:
                module_violations = [v for v in new_violations if v.source_module == module.name]
                module.health.drift = min(1.0, len(module_violations) * 0.2)

        # Compute violation diff
        new_violation_keys = set(
            (v.source_module, v.target_module, v.rule_name) for v in new_violations
        )
        result.new_violations = [
            v
            for v in new_violations
            if (v.source_module, v.target_module, v.rule_name) not in old_violations
        ]
        result.resolved_violations = [
            v
            for v in self._violations.value
            if (v.source_module, v.target_module, v.rule_name) not in new_violation_keys
        ]

        # Update signals
        self._graph.set(graph)
        self._violations.set(new_violations)

        result.duration_ms = (time.perf_counter() - start) * 1000
        logger.debug(
            f"Incremental update: +{len(result.added_modules)} "
            f"~{len(result.modified_modules)} -{len(result.removed_modules)} "
            f"in {result.duration_ms:.1f}ms"
        )

        return result

    def _path_to_module_name(self, path: Path) -> str:
        """Convert a file path to module name."""
        try:
            rel_path = path.relative_to(self._root)
            return str(rel_path.with_suffix("")).replace("/", ".")
        except ValueError:
            return path.stem

    def _recompute_health(self, graph: ArchitectureGraph, affected: set[str]) -> None:
        """Recompute health metrics for affected modules."""
        # Also include dependents of affected modules
        to_update = set(affected)
        for name in affected:
            to_update.update(graph.get_dependents(name))
            to_update.update(graph.get_dependencies(name))

        for name in to_update:
            module = graph.modules.get(name)
            if not module:
                continue

            # Coupling
            out_deps = len(graph.get_dependencies(name))
            in_deps = len(graph.get_dependents(name))
            max_deps = max(graph.module_count - 1, 1)
            coupling = min(1.0, (out_deps + in_deps) / (2 * max_deps))

            # Cohesion
            loc = max(module.lines_of_code, 1)
            export_count = len(module.exported_symbols)
            cohesion = 1.0 - min(1.0, export_count / (loc / 20))

            # Complexity
            complexity = min(1.0, loc / 500)

            # Instability
            instability = graph.compute_instability(name)

            # Preserve drift from previous health or default to 0
            drift = module.health.drift if module.health else 0.0

            module.health = ModuleHealth(
                name=name,
                coupling=coupling,
                cohesion=max(0.0, cohesion),
                complexity=complexity,
                instability=instability,
                drift=drift,
            )

    # ========================================================================
    # File Watching
    # ========================================================================

    async def start_watching(self) -> None:
        """
        Start watching for file changes.

        Uses watchdog for filesystem events with debouncing
        to batch rapid changes.
        """
        if self._watcher_running:
            return

        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            class GestaltHandler(FileSystemEventHandler):
                def __init__(self, store: GestaltStore) -> None:
                    self._store = store

                def on_modified(self, event: Any) -> None:
                    if event.is_directory:
                        return
                    self._store._queue_change(Path(event.src_path), "modified")

                def on_created(self, event: Any) -> None:
                    if event.is_directory:
                        return
                    self._store._queue_change(Path(event.src_path), "created")

                def on_deleted(self, event: Any) -> None:
                    if event.is_directory:
                        return
                    self._store._queue_change(Path(event.src_path), "deleted")

            self._observer = Observer()
            handler = GestaltHandler(self)
            self._observer.schedule(handler, str(self._root), recursive=True)
            self._observer.start()
            self._watcher_running = True

            logger.info(f"Started watching: {self._root}")

        except ImportError:
            logger.warning(
                "watchdog not installed. File watching unavailable. "
                "Install with: pip install watchdog"
            )

    async def stop_watching(self) -> None:
        """Stop watching for file changes."""
        if not self._watcher_running:
            return

        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=2)
            self._observer = None

        if self._debounce_task:
            self._debounce_task.cancel()
            self._debounce_task = None

        self._watcher_running = False
        self._pending_changes.clear()

        logger.info("Stopped watching")

    @property
    def watching(self) -> bool:
        """Check if file watching is active."""
        return self._watcher_running

    def _queue_change(self, path: Path, change_type: str) -> None:
        """Queue a file change for debounced processing."""
        # Filter by language
        if self._language == "python" and path.suffix != ".py":
            return
        if self._language == "typescript" and path.suffix not in (".ts", ".tsx"):
            return

        # Ignore common non-source paths
        parts = path.parts
        if any(
            p in parts
            for p in [
                "__pycache__",
                ".venv",
                "venv",
                "node_modules",
                ".git",
                "dist",
                "build",
                ".mypy_cache",
                ".pytest_cache",
            ]
        ):
            return

        self._pending_changes[path] = FileDiff(
            path=path,
            change_type=change_type,
            timestamp=time.time(),
        )

        # Schedule debounced processing (only if event loop is running)
        try:
            loop = asyncio.get_running_loop()
            if self._debounce_task is None or self._debounce_task.done():
                self._debounce_task = loop.create_task(self._process_pending())
        except RuntimeError:
            # No running event loop - skip async scheduling
            # Changes will be processed on next manual scan_incremental call
            pass

    async def _process_pending(self) -> None:
        """Process pending changes after debounce delay."""
        await asyncio.sleep(self._debounce_seconds)

        if not self._pending_changes:
            return

        changes = list(self._pending_changes.values())
        self._pending_changes.clear()

        try:
            await self.scan_incremental(changes)
        except Exception as e:
            logger.error(f"Error processing changes: {e}")

    # ========================================================================
    # Utilities
    # ========================================================================

    def get_module(self, name: str) -> Module | None:
        """Get a module by name."""
        return self._graph.value.modules.get(name)

    def get_module_violations(self, name: str) -> list[DriftViolation]:
        """Get drift violations for a specific module."""
        return [v for v in self._violations.value if v.source_module == name]

    def subscribe_to_changes(
        self, callback: Callable[[ArchitectureGraph], None]
    ) -> Callable[[], None]:
        """
        Subscribe to graph changes.

        Returns an unsubscribe function.
        """
        return self._graph.subscribe(callback)

    def subscribe_to_violations(
        self, callback: Callable[[list[DriftViolation]], None]
    ) -> Callable[[], None]:
        """
        Subscribe to violation changes.

        Returns an unsubscribe function.
        """
        return self._violations.subscribe(callback)

    def dispose(self) -> None:
        """Clean up resources."""
        # Stop watcher synchronously (best effort)
        if self._observer:
            self._observer.stop()
            self._observer = None

        # Dispose computeds
        self._module_count.dispose()
        self._edge_count.dispose()
        self._average_health.dispose()
        self._overall_grade.dispose()
        self._drift_count.dispose()
        self._active_drift_count.dispose()
        self._module_healths.dispose()
        self._worst_modules.dispose()
        self._grade_distribution.dispose()

        self._watcher_running = False


# ============================================================================
# Convenience Functions
# ============================================================================


async def create_gestalt_store(
    root: Path | str | None = None,
    language: str = "python",
    auto_scan: bool = True,
    watch: bool = False,
) -> GestaltStore:
    """
    Create and initialize a GestaltStore.

    Convenience function for common setup patterns.

    Args:
        root: Root directory to analyze
        language: "python" or "typescript"
        auto_scan: If True, perform initial scan
        watch: If True, start file watching

    Returns:
        Initialized GestaltStore

    Example:
        store = await create_gestalt_store(
            root="./my_project",
            auto_scan=True,
            watch=True
        )
    """
    store = GestaltStore(
        root=Path(root) if root else None,
        language=language,
    )

    if auto_scan:
        await store.scan()

    if watch:
        await store.start_watching()

    return store


# ============================================================================
# GestaltStoreFactory (Builder Pattern)
# ============================================================================


class GestaltStoreFactory:
    """
    Factory for creating GestaltStore instances with customization.

    Provides a builder pattern for configuring stores with:
    - Custom analyzers
    - Custom governance configs
    - Pre-populated graphs (for testing)
    - Custom languages

    Usage:
        # Basic usage
        store = GestaltStoreFactory().create(Path("./project"))

        # With custom config
        store = (
            GestaltStoreFactory()
            .with_config(my_governance_config)
            .with_language("typescript")
            .create(Path("./project"))
        )

        # For testing with mock graph
        store = (
            GestaltStoreFactory()
            .with_graph(mock_graph)
            .with_violations(mock_violations)
            .create(Path("."))
        )

        # With custom analyzer registry
        registry = AnalyzerRegistry()
        registry.register("go", GoAnalyzer())
        store = (
            GestaltStoreFactory()
            .with_analyzer_registry(registry)
            .create(Path("./project"))
        )
    """

    def __init__(self) -> None:
        """Initialize factory with default settings."""
        self._config: GovernanceConfig | None = None
        self._language: str = "python"
        self._graph: ArchitectureGraph | None = None
        self._violations: list[DriftViolation] | None = None
        self._debounce_seconds: float = 0.3

    def with_config(self, config: GovernanceConfig) -> "GestaltStoreFactory":
        """
        Set custom governance configuration.

        Args:
            config: GovernanceConfig with layer/ring rules

        Returns:
            Self for chaining
        """
        self._config = config
        return self

    def with_language(self, language: str) -> "GestaltStoreFactory":
        """
        Set the language to analyze.

        Args:
            language: "python", "typescript", etc.

        Returns:
            Self for chaining
        """
        self._language = language
        return self

    def with_graph(self, graph: ArchitectureGraph) -> "GestaltStoreFactory":
        """
        Pre-populate with an existing graph (for testing).

        When a graph is provided, the store will use it directly
        instead of scanning the filesystem.

        Args:
            graph: Pre-built ArchitectureGraph

        Returns:
            Self for chaining
        """
        self._graph = graph
        return self

    def with_violations(self, violations: list[DriftViolation]) -> "GestaltStoreFactory":
        """
        Pre-populate with violations (for testing).

        Args:
            violations: List of DriftViolation

        Returns:
            Self for chaining
        """
        self._violations = violations
        return self

    def with_debounce(self, seconds: float) -> "GestaltStoreFactory":
        """
        Set debounce delay for file watching.

        Args:
            seconds: Debounce delay in seconds

        Returns:
            Self for chaining
        """
        self._debounce_seconds = seconds
        return self

    def create(self, root: Path | None = None) -> GestaltStore:
        """
        Create the configured GestaltStore.

        Args:
            root: Root directory to analyze (defaults to cwd)

        Returns:
            Configured GestaltStore instance
        """
        store = GestaltStore(
            root=root,
            language=self._language,
            config=self._config,
        )

        # Set debounce
        store._debounce_seconds = self._debounce_seconds

        # Pre-populate if graph provided
        if self._graph is not None:
            store._graph.set(self._graph)

        # Pre-populate violations if provided
        if self._violations is not None:
            store._violations.set(self._violations)

        return store

    def __repr__(self) -> str:
        return (
            f"GestaltStoreFactory("
            f"language={self._language!r}, "
            f"has_config={self._config is not None}, "
            f"has_graph={self._graph is not None})"
        )


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Core
    "GestaltStore",
    "create_gestalt_store",
    # Factory
    "GestaltStoreFactory",
    # Types
    "FileDiff",
    "IncrementalUpdate",
]
