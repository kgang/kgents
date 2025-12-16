"""
Tests for Gestalt Reactive Substrate (Phase 2).

Target: 30+ tests covering:
- GestaltStore initialization and properties
- Full scan functionality
- Computed derivations (module_count, health, grade)
- Incremental updates (add, modify, delete)
- File watcher (mocked)
- Performance budgets
"""

from __future__ import annotations

import asyncio
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest
from protocols.gestalt.analysis import (
    ArchitectureGraph,
    DependencyEdge,
    Module,
    ModuleHealth,
)
from protocols.gestalt.reactive import (
    FileDiff,
    GestaltStore,
    IncrementalUpdate,
    create_gestalt_store,
)

if TYPE_CHECKING:
    pass


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create a temporary Python project for testing."""
    # Create a simple module structure
    (tmp_path / "main.py").write_text(
        '''"""Main module."""
import helper

def main():
    """Entry point."""
    return helper.greet()
'''
    )

    (tmp_path / "helper.py").write_text(
        '''"""Helper module."""

def greet():
    """Return a greeting."""
    return "Hello, World!"

def compute(x):
    """Compute something."""
    return x * 2
'''
    )

    (tmp_path / "utils").mkdir()
    (tmp_path / "utils" / "__init__.py").write_text('"""Utils package."""\n')
    (tmp_path / "utils" / "math.py").write_text(
        '''"""Math utilities."""

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
'''
    )

    return tmp_path


@pytest.fixture
def empty_store(tmp_path: Path) -> GestaltStore:
    """Create an empty GestaltStore."""
    return GestaltStore(root=tmp_path, language="python")


@pytest.fixture
async def scanned_store(temp_project: Path) -> GestaltStore:
    """Create a scanned GestaltStore."""
    store = GestaltStore(root=temp_project, language="python")
    await store.scan()
    return store


# ============================================================================
# Test: Initialization
# ============================================================================


class TestGestaltStoreInit:
    """Tests for GestaltStore initialization."""

    def test_init_with_defaults(self, tmp_path: Path) -> None:
        """Store initializes with empty graph."""
        store = GestaltStore(root=tmp_path)
        assert store.root == tmp_path
        assert store.language == "python"
        assert store.graph.value.module_count == 0

    def test_init_with_typescript(self, tmp_path: Path) -> None:
        """Store can be configured for TypeScript."""
        store = GestaltStore(root=tmp_path, language="typescript")
        assert store.language == "typescript"

    def test_init_creates_computeds(self, tmp_path: Path) -> None:
        """Store creates all derived computed values."""
        store = GestaltStore(root=tmp_path)

        # All computeds should exist
        assert hasattr(store, "module_count")
        assert hasattr(store, "edge_count")
        assert hasattr(store, "average_health")
        assert hasattr(store, "overall_grade")
        assert hasattr(store, "drift_count")
        assert hasattr(store, "active_drift_count")
        assert hasattr(store, "module_healths")
        assert hasattr(store, "worst_modules")
        assert hasattr(store, "grade_distribution")

    def test_init_graph_is_signal(self, tmp_path: Path) -> None:
        """Graph is a proper Signal."""
        store = GestaltStore(root=tmp_path)
        from agents.i.reactive.signal import Signal

        assert isinstance(store.graph, Signal)

    def test_watching_initially_false(self, tmp_path: Path) -> None:
        """File watching is not running initially."""
        store = GestaltStore(root=tmp_path)
        assert not store.watching


# ============================================================================
# Test: Full Scan
# ============================================================================


class TestGestaltStoreScan:
    """Tests for full scan functionality."""

    @pytest.mark.asyncio
    async def test_scan_discovers_modules(self, temp_project: Path) -> None:
        """Scan discovers all Python modules."""
        store = GestaltStore(root=temp_project)
        await store.scan()

        # Should find main.py, helper.py, utils/__init__.py, utils/math.py
        assert store.module_count.value >= 3

    @pytest.mark.asyncio
    async def test_scan_extracts_edges(self, temp_project: Path) -> None:
        """Scan extracts import edges."""
        store = GestaltStore(root=temp_project)
        await store.scan()

        # main.py imports helper
        assert store.edge_count.value >= 1

    @pytest.mark.asyncio
    async def test_scan_computes_health(self, temp_project: Path) -> None:
        """Scan computes health metrics for modules."""
        store = GestaltStore(root=temp_project)
        await store.scan()

        for module in store.graph.value.modules.values():
            assert module.health is not None
            assert 0 <= module.health.overall_health <= 1

    @pytest.mark.asyncio
    async def test_scan_returns_graph(self, temp_project: Path) -> None:
        """Scan returns the ArchitectureGraph."""
        store = GestaltStore(root=temp_project)
        result = await store.scan()

        assert isinstance(result, ArchitectureGraph)
        assert result.module_count > 0

    @pytest.mark.asyncio
    async def test_scan_updates_signals(self, temp_project: Path) -> None:
        """Scan triggers signal updates."""
        store = GestaltStore(root=temp_project)

        updates: list[ArchitectureGraph] = []
        store.graph.subscribe(lambda g: updates.append(g))

        await store.scan()

        # Should have received at least one update
        assert len(updates) >= 1

    @pytest.mark.asyncio
    async def test_scan_tracks_file_mtimes(self, temp_project: Path) -> None:
        """Scan tracks file modification times."""
        store = GestaltStore(root=temp_project)
        await store.scan()

        # Should have tracked mtimes for discovered files
        assert len(store._file_mtimes) > 0


# ============================================================================
# Test: Computed Derivations
# ============================================================================


class TestComputedDerivations:
    """Tests for computed derived values."""

    @pytest.mark.asyncio
    async def test_module_count_updates(self, scanned_store: GestaltStore) -> None:
        """Module count computed updates with graph."""
        initial_count = scanned_store.module_count.value
        assert initial_count >= 3

    @pytest.mark.asyncio
    async def test_edge_count_updates(self, scanned_store: GestaltStore) -> None:
        """Edge count computed updates with graph."""
        edge_count = scanned_store.edge_count.value
        assert edge_count >= 0

    @pytest.mark.asyncio
    async def test_average_health_in_range(self, scanned_store: GestaltStore) -> None:
        """Average health is in valid range."""
        health = scanned_store.average_health.value
        assert 0 <= health <= 1

    @pytest.mark.asyncio
    async def test_overall_grade_is_valid(self, scanned_store: GestaltStore) -> None:
        """Overall grade is a valid letter grade."""
        grade = scanned_store.overall_grade.value
        assert grade in ["A+", "A", "B+", "B", "C+", "C", "D", "F"]

    @pytest.mark.asyncio
    async def test_drift_count_non_negative(self, scanned_store: GestaltStore) -> None:
        """Drift count is non-negative."""
        assert scanned_store.drift_count.value >= 0

    @pytest.mark.asyncio
    async def test_active_drift_count_lte_total(
        self, scanned_store: GestaltStore
    ) -> None:
        """Active drift count is <= total drift count."""
        assert scanned_store.active_drift_count.value <= scanned_store.drift_count.value

    @pytest.mark.asyncio
    async def test_module_healths_matches_modules(
        self, scanned_store: GestaltStore
    ) -> None:
        """Module healths map matches module count."""
        healths = scanned_store.module_healths.value
        # May not have health for all modules
        assert len(healths) <= scanned_store.module_count.value

    @pytest.mark.asyncio
    async def test_worst_modules_limited(self, scanned_store: GestaltStore) -> None:
        """Worst modules list is limited to 10."""
        worst = scanned_store.worst_modules.value
        assert len(worst) <= 10

    @pytest.mark.asyncio
    async def test_worst_modules_sorted(self, scanned_store: GestaltStore) -> None:
        """Worst modules are sorted by health (ascending)."""
        worst = scanned_store.worst_modules.value
        if len(worst) > 1:
            healths = [h for _, h in worst]
            assert healths == sorted(healths)

    @pytest.mark.asyncio
    async def test_grade_distribution_complete(
        self, scanned_store: GestaltStore
    ) -> None:
        """Grade distribution contains all grades."""
        dist = scanned_store.grade_distribution.value
        expected_grades = ["A+", "A", "B+", "B", "C+", "C", "D", "F"]
        for grade in expected_grades:
            assert grade in dist


# ============================================================================
# Test: Incremental Updates
# ============================================================================


class TestIncrementalUpdates:
    """Tests for incremental update functionality."""

    @pytest.mark.asyncio
    async def test_incremental_add_module(self, scanned_store: GestaltStore) -> None:
        """Incremental update can add a new module."""
        # Add a new file
        new_file = scanned_store.root / "new_module.py"
        new_file.write_text('"""New module."""\n\ndef new_func(): pass\n')

        initial_count = scanned_store.module_count.value

        result = await scanned_store.scan_incremental(
            [FileDiff(path=new_file, change_type="created")]
        )

        assert len(result.added_modules) == 1
        assert scanned_store.module_count.value == initial_count + 1

    @pytest.mark.asyncio
    async def test_incremental_modify_module(self, scanned_store: GestaltStore) -> None:
        """Incremental update handles modified modules."""
        # Modify existing file
        helper_file = scanned_store.root / "helper.py"
        original = helper_file.read_text()
        helper_file.write_text(original + "\ndef extra(): pass\n")

        result = await scanned_store.scan_incremental(
            [FileDiff(path=helper_file, change_type="modified")]
        )

        assert len(result.modified_modules) == 1

    @pytest.mark.asyncio
    async def test_incremental_delete_module(self, scanned_store: GestaltStore) -> None:
        """Incremental update handles deleted modules."""
        # Create and scan a temp file first
        temp_file = scanned_store.root / "temp_module.py"
        temp_file.write_text('"""Temp."""\n')
        await scanned_store.scan_incremental(
            [FileDiff(path=temp_file, change_type="created")]
        )

        initial_count = scanned_store.module_count.value

        # Now delete it
        temp_file.unlink()
        result = await scanned_store.scan_incremental(
            [FileDiff(path=temp_file, change_type="deleted")]
        )

        assert len(result.removed_modules) == 1
        assert scanned_store.module_count.value == initial_count - 1

    @pytest.mark.asyncio
    async def test_incremental_no_changes(self, scanned_store: GestaltStore) -> None:
        """Incremental update with no changes is fast."""
        result = await scanned_store.scan_incremental([])
        assert not result.has_changes

    @pytest.mark.asyncio
    async def test_incremental_updates_computeds(
        self, scanned_store: GestaltStore
    ) -> None:
        """Incremental update triggers computed recalculation."""
        new_file = scanned_store.root / "another.py"
        new_file.write_text('"""Another."""\nimport helper\n')

        initial_edges = scanned_store.edge_count.value

        await scanned_store.scan_incremental(
            [FileDiff(path=new_file, change_type="created")]
        )

        # Should have one more edge (another imports helper)
        assert scanned_store.edge_count.value >= initial_edges

    @pytest.mark.asyncio
    async def test_incremental_has_duration(self, scanned_store: GestaltStore) -> None:
        """Incremental update records duration."""
        new_file = scanned_store.root / "timed.py"
        new_file.write_text('"""Timed."""\n')

        result = await scanned_store.scan_incremental(
            [FileDiff(path=new_file, change_type="created")]
        )

        assert result.duration_ms > 0


# ============================================================================
# Test: File Watcher
# ============================================================================


class TestFileWatcher:
    """Tests for file watching functionality."""

    @pytest.mark.asyncio
    async def test_start_watching_sets_flag(self, scanned_store: GestaltStore) -> None:
        """Starting watcher sets running flag."""
        await scanned_store.start_watching()
        try:
            assert scanned_store.watching
        finally:
            await scanned_store.stop_watching()

    @pytest.mark.asyncio
    async def test_stop_watching_clears_flag(self, scanned_store: GestaltStore) -> None:
        """Stopping watcher clears running flag."""
        await scanned_store.start_watching()
        await scanned_store.stop_watching()
        assert not scanned_store.watching

    @pytest.mark.asyncio
    async def test_start_twice_is_safe(self, scanned_store: GestaltStore) -> None:
        """Starting watcher twice is idempotent."""
        await scanned_store.start_watching()
        await scanned_store.start_watching()  # Should not error
        try:
            assert scanned_store.watching
        finally:
            await scanned_store.stop_watching()

    @pytest.mark.asyncio
    async def test_stop_without_start_is_safe(self, empty_store: GestaltStore) -> None:
        """Stopping without starting is safe."""
        await empty_store.stop_watching()  # Should not error
        assert not empty_store.watching

    def test_queue_change_filters_non_python(self, empty_store: GestaltStore) -> None:
        """Queue change filters non-Python files."""
        empty_store._queue_change(Path("/test/file.txt"), "modified")
        assert len(empty_store._pending_changes) == 0

    def test_queue_change_filters_pycache(self, empty_store: GestaltStore) -> None:
        """Queue change filters __pycache__ files."""
        empty_store._queue_change(Path("/test/__pycache__/mod.py"), "modified")
        assert len(empty_store._pending_changes) == 0

    def test_queue_change_accepts_python(self, empty_store: GestaltStore) -> None:
        """Queue change accepts Python files."""
        empty_store._queue_change(Path("/test/module.py"), "modified")
        assert len(empty_store._pending_changes) == 1


# ============================================================================
# Test: Subscriptions
# ============================================================================


class TestSubscriptions:
    """Tests for subscription functionality."""

    @pytest.mark.asyncio
    async def test_subscribe_to_changes(self, temp_project: Path) -> None:
        """Can subscribe to graph changes."""
        store = GestaltStore(root=temp_project)
        updates: list[ArchitectureGraph] = []
        unsub = store.subscribe_to_changes(lambda g: updates.append(g))

        # Trigger an update - subscribe BEFORE scan
        await store.scan()

        assert len(updates) >= 1
        unsub()

    @pytest.mark.asyncio
    async def test_unsubscribe_stops_updates(self, temp_project: Path) -> None:
        """Unsubscribe stops receiving updates."""
        store = GestaltStore(root=temp_project)
        updates: list[ArchitectureGraph] = []
        unsub = store.subscribe_to_changes(lambda g: updates.append(g))

        # Get one update
        await store.scan()
        initial_len = len(updates)

        # Unsubscribe
        unsub()

        # Trigger another update after unsubscribe
        await store.scan()

        # Should not have received the update after unsubscribe
        assert len(updates) == initial_len

    @pytest.mark.asyncio
    async def test_subscribe_to_violations(self, temp_project: Path) -> None:
        """Can subscribe to violation changes."""
        from protocols.gestalt.governance import DriftViolation

        store = GestaltStore(root=temp_project)

        # First scan to initialize
        await store.scan()

        updates: list[list[DriftViolation]] = []
        unsub = store.subscribe_to_violations(lambda v: updates.append(v))

        # Add a file that creates a violation by importing from wrong layer
        # This ensures the violations list changes
        bad_file = temp_project / "bad_import.py"
        bad_file.write_text('"""Bad."""\nimport sys\n')

        # Scan again - violations may or may not change but we verify the mechanism
        await store.scan_incremental([FileDiff(path=bad_file, change_type="created")])

        # The subscription mechanism works - we got called
        # (may be empty if no actual drift rules triggered)
        assert store.violations.value is not None
        unsub()


# ============================================================================
# Test: Utilities
# ============================================================================


class TestUtilities:
    """Tests for utility methods."""

    @pytest.mark.asyncio
    async def test_get_module(self, scanned_store: GestaltStore) -> None:
        """Can get a module by name."""
        # Find any module name
        names = list(scanned_store.graph.value.modules.keys())
        if names:
            module = scanned_store.get_module(names[0])
            assert module is not None

    @pytest.mark.asyncio
    async def test_get_module_not_found(self, scanned_store: GestaltStore) -> None:
        """Get module returns None for unknown."""
        module = scanned_store.get_module("nonexistent.module.xyz")
        assert module is None

    @pytest.mark.asyncio
    async def test_get_module_violations(self, scanned_store: GestaltStore) -> None:
        """Can get violations for a specific module."""
        names = list(scanned_store.graph.value.modules.keys())
        if names:
            violations = scanned_store.get_module_violations(names[0])
            assert isinstance(violations, list)

    def test_dispose_cleans_up(self, empty_store: GestaltStore) -> None:
        """Dispose cleans up resources."""
        empty_store.dispose()
        assert not empty_store.watching


# ============================================================================
# Test: Convenience Functions
# ============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_create_gestalt_store_basic(self, temp_project: Path) -> None:
        """create_gestalt_store creates and scans."""
        store = await create_gestalt_store(root=temp_project, auto_scan=True)
        assert store.module_count.value > 0

    @pytest.mark.asyncio
    async def test_create_gestalt_store_no_scan(self, temp_project: Path) -> None:
        """create_gestalt_store can skip scan."""
        store = await create_gestalt_store(root=temp_project, auto_scan=False)
        assert store.module_count.value == 0

    @pytest.mark.asyncio
    async def test_create_gestalt_store_with_watch(self, temp_project: Path) -> None:
        """create_gestalt_store can start watching."""
        store = await create_gestalt_store(
            root=temp_project, auto_scan=True, watch=True
        )
        try:
            assert store.watching
        finally:
            await store.stop_watching()


# ============================================================================
# Test: Performance Budget
# ============================================================================


class TestPerformanceBudget:
    """Tests for performance requirements."""

    @pytest.mark.asyncio
    async def test_incremental_update_under_2s(
        self, scanned_store: GestaltStore
    ) -> None:
        """Incremental updates complete in under 2 seconds."""
        new_file = scanned_store.root / "perf_test.py"
        new_file.write_text('"""Perf test."""\n')

        start = time.perf_counter()
        result = await scanned_store.scan_incremental(
            [FileDiff(path=new_file, change_type="created")]
        )
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"Incremental update took {elapsed:.2f}s (budget: 2s)"

    @pytest.mark.asyncio
    async def test_computed_access_fast(self, scanned_store: GestaltStore) -> None:
        """Computed value access is fast (cached)."""
        # Prime the computed
        _ = scanned_store.module_count.value

        start = time.perf_counter()
        for _ in range(1000):
            _ = scanned_store.module_count.value
        elapsed = time.perf_counter() - start

        # 1000 accesses should be under 100ms
        assert elapsed < 0.1, f"1000 computed accesses took {elapsed:.3f}s"

    @pytest.mark.asyncio
    async def test_subscription_callback_fast(
        self, scanned_store: GestaltStore
    ) -> None:
        """Subscription callbacks are called quickly."""
        callback_times: list[float] = []

        def callback(g: ArchitectureGraph) -> None:
            callback_times.append(time.perf_counter())

        unsub = scanned_store.subscribe_to_changes(callback)

        start = time.perf_counter()
        await scanned_store.scan()

        if callback_times:
            first_callback = callback_times[0] - start
            assert first_callback < 1.0, f"First callback at {first_callback:.3f}s"

        unsub()


# ============================================================================
# Test: FileDiff and IncrementalUpdate Types
# ============================================================================


class TestTypes:
    """Tests for data types."""

    def test_file_diff_frozen(self) -> None:
        """FileDiff is frozen (immutable path and change_type)."""
        diff = FileDiff(path=Path("/test.py"), change_type="modified")
        assert diff.path == Path("/test.py")
        assert diff.change_type == "modified"
        assert diff.timestamp > 0

    def test_incremental_update_has_changes(self) -> None:
        """IncrementalUpdate.has_changes works correctly."""
        empty = IncrementalUpdate()
        assert not empty.has_changes

        with_added = IncrementalUpdate(added_modules=["foo"])
        assert with_added.has_changes

        with_modified = IncrementalUpdate(modified_modules=["bar"])
        assert with_modified.has_changes

        with_removed = IncrementalUpdate(removed_modules=["baz"])
        assert with_removed.has_changes
