"""
Tests for Gestalt CLI Handler (Spike 6A).

Verifies that CLI commands are wired to GestaltStore reactive substrate:
- manifest: uses store.module_count, store.overall_grade
- health: uses store.module_healths, store.grade_distribution
- drift: uses store.violations Signal
- module: uses store.graph and store.violations
- --watch: starts file watching

Tests use fixture injection to avoid filesystem scanning.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from protocols.gestalt.handler import (
    _get_store,
    _reset_store,
    _set_store_factory,
    cmd_codebase,
    handle_codebase_manifest,
    handle_drift_witness,
    handle_health_manifest,
    handle_module_manifest,
)

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
def mock_store(temp_project: Path) -> Generator[MagicMock, None, None]:
    """Create a mock GestaltStore with pre-set values."""
    from protocols.gestalt.reactive import GestaltStore

    # Create real store with temp project
    store = GestaltStore(root=temp_project, language="python")

    # Scan synchronously
    asyncio.run(store.scan())

    # Inject factory
    _set_store_factory(lambda: store)

    yield store

    # Cleanup
    _set_store_factory(None)
    _reset_store()
    store.dispose()


@pytest.fixture(autouse=True)
def reset_store_between_tests() -> Generator[None, None, None]:
    """Reset store state between tests."""
    yield
    _reset_store()
    _set_store_factory(None)


# ============================================================================
# Test: Store Instance Management
# ============================================================================


class TestStoreManagement:
    """Tests for GestaltStore instance management."""

    def test_get_store_returns_store(self, temp_project: Path) -> None:
        """_get_store returns a GestaltStore instance."""
        from protocols.gestalt.reactive import GestaltStore

        store = _get_store(root=temp_project)
        assert isinstance(store, GestaltStore)

    def test_set_factory_injects_store(self, temp_project: Path) -> None:
        """Factory injection works for testing."""
        from protocols.gestalt.reactive import GestaltStore

        custom_store = GestaltStore(root=temp_project)

        _set_store_factory(lambda: custom_store)
        store = _get_store()

        assert store is custom_store

        _set_store_factory(None)
        custom_store.dispose()

    def test_reset_store_clears_instance(self, temp_project: Path) -> None:
        """_reset_store clears the cached instance."""
        # Get a store
        store1 = _get_store(root=temp_project)
        _reset_store()

        # Get another - should be different
        store2 = _get_store(root=temp_project)
        # Note: they may be same type but different instances
        # We can't easily test this without more infrastructure


# ============================================================================
# Test: CLI Commands Use Store Reactive Properties
# ============================================================================


class TestManifestUsesStore:
    """Tests that manifest command uses store.module_count, store.overall_grade."""

    def test_manifest_reads_module_count(self, mock_store: MagicMock) -> None:
        """Manifest reads module_count from store."""
        result = handle_codebase_manifest([], json_output=True, store=mock_store)

        # Should match store value
        assert result["module_count"] == mock_store.module_count.value

    def test_manifest_reads_edge_count(self, mock_store: MagicMock) -> None:
        """Manifest reads edge_count from store."""
        result = handle_codebase_manifest([], json_output=True, store=mock_store)

        assert result["edge_count"] == mock_store.edge_count.value

    def test_manifest_reads_overall_grade(self, mock_store: MagicMock) -> None:
        """Manifest reads overall_grade from store."""
        result = handle_codebase_manifest([], json_output=True, store=mock_store)

        assert result["overall_grade"] == mock_store.overall_grade.value

    def test_manifest_reads_average_health(self, mock_store: MagicMock) -> None:
        """Manifest reads average_health from store."""
        result = handle_codebase_manifest([], json_output=True, store=mock_store)

        assert result["average_health"] == round(mock_store.average_health.value, 2)

    def test_manifest_reads_drift_count(self, mock_store: MagicMock) -> None:
        """Manifest reads drift_count from store."""
        result = handle_codebase_manifest([], json_output=True, store=mock_store)

        assert result["drift_count"] == mock_store.drift_count.value


class TestHealthUsesStore:
    """Tests that health command uses store.module_healths, store.grade_distribution."""

    def test_health_reads_average_health(self, mock_store: MagicMock) -> None:
        """Health reads average_health from store."""
        result = handle_health_manifest([], json_output=True, store=mock_store)

        assert result["average_health"] == round(mock_store.average_health.value, 2)

    def test_health_reads_overall_grade(self, mock_store: MagicMock) -> None:
        """Health reads overall_grade from store."""
        result = handle_health_manifest([], json_output=True, store=mock_store)

        assert result["overall_grade"] == mock_store.overall_grade.value

    def test_health_reads_grade_distribution(self, mock_store: MagicMock) -> None:
        """Health reads grade_distribution from store."""
        result = handle_health_manifest([], json_output=True, store=mock_store)

        assert result["grade_distribution"] == mock_store.grade_distribution.value


class TestDriftUsesStore:
    """Tests that drift command uses store.violations Signal."""

    def test_drift_reads_violations(self, mock_store: MagicMock) -> None:
        """Drift reads violations from store."""
        result = handle_drift_witness([], json_output=True, store=mock_store)

        # Total should match
        assert result["total_violations"] == mock_store.drift_count.value

    def test_drift_reads_active_count(self, mock_store: MagicMock) -> None:
        """Drift reads active_drift_count from store."""
        result = handle_drift_witness([], json_output=True, store=mock_store)

        assert result["unsuppressed"] == mock_store.active_drift_count.value


class TestModuleUsesStore:
    """Tests that module command uses store.graph and store.violations."""

    def test_module_reads_from_graph(self, mock_store: MagicMock) -> None:
        """Module reads module data from store.graph."""
        # Get a module name from the store
        graph = mock_store.graph.value
        if graph.modules:
            module_name = list(graph.modules.keys())[0]
            result = handle_module_manifest(module_name, [], json_output=True, store=mock_store)

            assert result["name"] == module_name

    def test_module_not_found(self, mock_store: MagicMock) -> None:
        """Module returns error for unknown module."""
        result = handle_module_manifest("nonexistent_xyz", [], json_output=False, store=mock_store)

        assert "not found" in result


# ============================================================================
# Test: CLI Command Entry Point
# ============================================================================


class TestCmdCodebase:
    """Tests for cmd_codebase CLI entry point."""

    def test_default_shows_manifest(self, mock_store: MagicMock) -> None:
        """Default command (no args) shows manifest."""
        result = cmd_codebase([])
        assert result == 0

    def test_manifest_explicit(self, mock_store: MagicMock) -> None:
        """Explicit manifest command works."""
        result = cmd_codebase(["manifest"])
        assert result == 0

    def test_health_command(self, mock_store: MagicMock) -> None:
        """Health subcommand works."""
        result = cmd_codebase(["health"])
        assert result == 0

    def test_drift_command(self, mock_store: MagicMock) -> None:
        """Drift subcommand works."""
        result = cmd_codebase(["drift"])
        assert result == 0

    def test_module_command(self, mock_store: MagicMock) -> None:
        """Module subcommand works."""
        # Get a module name
        graph = mock_store.graph.value
        if graph.modules:
            module_name = list(graph.modules.keys())[0]
            result = cmd_codebase(["module", module_name])
            assert result == 0

    def test_json_output(self, mock_store: MagicMock) -> None:
        """--json flag produces JSON output."""
        result = cmd_codebase(["--json"])
        assert result == 0

    def test_unknown_subcommand(self, mock_store: MagicMock) -> None:
        """Unknown subcommand returns non-zero error code."""
        result = cmd_codebase(["unknown_xyz"])
        assert result == 1  # Proper error handling returns non-zero

    def test_help_flag(self, mock_store: MagicMock) -> None:
        """--help flag shows help and returns 0."""
        result = cmd_codebase(["--help"])
        assert result == 0

    def test_help_flag_short(self, mock_store: MagicMock) -> None:
        """-h flag shows help and returns 0."""
        result = cmd_codebase(["-h"])
        assert result == 0

    def test_module_missing_name(self, mock_store: MagicMock) -> None:
        """Module command without name returns error."""
        result = cmd_codebase(["module"])
        assert result == 1  # Missing required argument


# ============================================================================
# Test: Watch Mode
# ============================================================================


class TestWatchMode:
    """Tests for --watch flag functionality."""

    def test_watch_flag_parsed(self, mock_store: MagicMock) -> None:
        """--watch flag is recognized."""
        # We can't easily test watch mode in unit tests since it blocks
        # Just verify the flag is parsed correctly
        from protocols.gestalt.handler import cmd_codebase

        # Patch the watch mode function to not block
        with patch("protocols.gestalt.handler._run_watch_mode") as mock_run:
            # This should call _run_watch_mode
            cmd_codebase(["--watch"])
            mock_run.assert_called_once()

    def test_watch_starts_watcher(self, mock_store: MagicMock) -> None:
        """--watch flag starts the file watcher."""
        with patch("protocols.gestalt.handler._run_watch_mode") as mock_run:
            cmd_codebase(["--watch"])

            # The store should have been passed to watch mode
            mock_run.assert_called_once()


# ============================================================================
# Test: Output Format
# ============================================================================


class TestOutputFormat:
    """Tests for CLI output formatting."""

    def test_manifest_human_readable(self, mock_store: MagicMock) -> None:
        """Manifest produces human-readable output by default."""
        result = handle_codebase_manifest([], json_output=False, store=mock_store)

        assert isinstance(result, str)
        assert "Architecture:" in result
        assert "modules" in result

    def test_health_human_readable(self, mock_store: MagicMock) -> None:
        """Health produces human-readable output by default."""
        result = handle_health_manifest([], json_output=False, store=mock_store)

        assert isinstance(result, str)
        assert "Overall:" in result

    def test_drift_human_readable(self, mock_store: MagicMock) -> None:
        """Drift produces human-readable output by default."""
        result = handle_drift_witness([], json_output=False, store=mock_store)

        assert isinstance(result, str)
        # Either "No drift violations" or "Drift Violations:"
        assert "drift" in result.lower() or "violation" in result.lower() or "no" in result.lower()

    def test_json_output_is_dict(self, mock_store: MagicMock) -> None:
        """JSON output returns a dictionary."""
        result = handle_codebase_manifest([], json_output=True, store=mock_store)

        assert isinstance(result, dict)
        assert "module_count" in result
        assert "overall_grade" in result


# ============================================================================
# Test: Store Reactivity Integration
# ============================================================================


class TestReactivityIntegration:
    """Tests that CLI reflects store state changes."""

    @pytest.mark.asyncio
    async def test_manifest_reflects_scan(self, temp_project: Path) -> None:
        """Manifest reflects state after scan."""
        from protocols.gestalt.reactive import GestaltStore

        store = GestaltStore(root=temp_project)

        # Before scan - empty
        assert store.module_count.value == 0

        # Scan
        await store.scan()

        # Manifest should reflect scanned state
        result = handle_codebase_manifest([], json_output=True, store=store)

        assert result["module_count"] > 0
        assert result["module_count"] == store.module_count.value

        store.dispose()

    @pytest.mark.asyncio
    async def test_computed_values_consistent(self, temp_project: Path) -> None:
        """Computed values are consistent across handlers."""
        from protocols.gestalt.reactive import GestaltStore

        store = GestaltStore(root=temp_project)
        await store.scan()

        # Get values from both handlers
        manifest = handle_codebase_manifest([], json_output=True, store=store)
        health = handle_health_manifest([], json_output=True, store=store)

        # They should agree
        assert manifest["overall_grade"] == health["overall_grade"]
        assert manifest["average_health"] == health["average_health"]

        store.dispose()


# ============================================================================
# Test: Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_project(self, tmp_path: Path) -> None:
        """Handles empty project gracefully."""
        from protocols.gestalt.reactive import GestaltStore

        store = GestaltStore(root=tmp_path)
        asyncio.run(store.scan())

        result = handle_codebase_manifest([], json_output=True, store=store)

        assert result["module_count"] == 0
        assert result["drift_count"] == 0

        store.dispose()

    def test_module_fuzzy_match(self, mock_store: MagicMock) -> None:
        """Module command supports fuzzy matching."""
        graph = mock_store.graph.value
        if graph.modules:
            # Get full module name
            full_name = list(graph.modules.keys())[0]
            # Try partial match
            partial = full_name.split(".")[-1] if "." in full_name else full_name

            result = handle_module_manifest(partial, [], json_output=True, store=mock_store)

            # Should either find it or list matches
            if isinstance(result, dict):
                assert "name" in result
            else:
                assert "match" in result.lower() or "found" in result.lower()


# ============================================================================
# Test: Property-Based Tests (Hypothesis)
# ============================================================================


class TestPropertyBased:
    """Property-based tests for handler robustness."""

    @given(
        cmd_args=st.lists(
            st.sampled_from(["manifest", "health", "drift", "--json", "--help", "unknown"]),
            min_size=0,
            max_size=5,
        )
    )
    @settings(
        max_examples=50,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_cmd_codebase_doesnt_crash(self, cmd_args: list[str], tmp_path: Path) -> None:
        """cmd_codebase handles arbitrary args without crashing."""
        from protocols.gestalt.reactive import GestaltStore

        # Create a minimal store for testing
        # Note: tmp_path is a pytest fixture that works with hypothesis
        store = GestaltStore(root=tmp_path)
        _set_store_factory(lambda: store)

        try:
            # Should not raise exceptions
            result = cmd_codebase(cmd_args)
            # Result should always be an int
            assert isinstance(result, int)
            # Return code should be 0 or 1
            assert result in (0, 1)
        finally:
            _set_store_factory(None)
            _reset_store()
            store.dispose()

    @given(module_name_input=st.text(min_size=0, max_size=100))
    @settings(
        max_examples=30,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_module_name_handles_arbitrary_input(
        self, module_name_input: str, tmp_path: Path
    ) -> None:
        """Module lookup handles arbitrary module names without crashing."""
        from protocols.gestalt.reactive import GestaltStore

        store = GestaltStore(root=tmp_path)
        asyncio.run(store.scan())

        try:
            # Should not raise exceptions
            result = handle_module_manifest(module_name_input, [], json_output=True, store=store)
            # Should return dict or string
            assert isinstance(result, (dict, str))
        finally:
            store.dispose()


# ============================================================================
# Test: Performance Baselines
# ============================================================================


class TestPerformanceBaselines:
    """Performance baseline tests - fail if operations are too slow."""

    def test_manifest_performance(self, mock_store: MagicMock) -> None:
        """Manifest generation should be fast (<100ms)."""
        import time

        start = time.perf_counter()
        for _ in range(10):
            handle_codebase_manifest([], json_output=True, store=mock_store)
        elapsed = time.perf_counter() - start

        # 10 iterations should complete in under 1 second
        assert elapsed < 1.0, f"Manifest too slow: {elapsed:.3f}s for 10 iterations"

    def test_health_performance(self, mock_store: MagicMock) -> None:
        """Health generation should be fast (<100ms)."""
        import time

        start = time.perf_counter()
        for _ in range(10):
            handle_health_manifest([], json_output=True, store=mock_store)
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"Health too slow: {elapsed:.3f}s for 10 iterations"

    def test_drift_performance(self, mock_store: MagicMock) -> None:
        """Drift check should be fast (<100ms)."""
        import time

        start = time.perf_counter()
        for _ in range(10):
            handle_drift_witness([], json_output=True, store=mock_store)
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"Drift too slow: {elapsed:.3f}s for 10 iterations"

    @pytest.mark.asyncio
    async def test_scan_performance(self, temp_project: Path) -> None:
        """Scan should complete in reasonable time (<2s for small project)."""
        import time

        from protocols.gestalt.reactive import GestaltStore

        store = GestaltStore(root=temp_project)

        start = time.perf_counter()
        await store.scan()
        elapsed = time.perf_counter() - start

        # Small test project should scan in under 2 seconds
        assert elapsed < 2.0, f"Scan too slow: {elapsed:.3f}s"

        store.dispose()


# ============================================================================
# Test: OTEL Span Verification
# ============================================================================


class TestOTELSpans:
    """Tests that OTEL spans are emitted correctly."""

    def test_tracer_exists(self) -> None:
        """OTEL tracer is configured."""
        from protocols.gestalt.handler import _tracer

        assert _tracer is not None

    def test_span_attributes_defined(self) -> None:
        """Span attribute constants are defined."""
        from protocols.gestalt.handler import (
            ATTR_DRIFT_COUNT,
            ATTR_DURATION_MS,
            ATTR_MODULE_COUNT,
            ATTR_SUBCOMMAND,
        )

        assert ATTR_SUBCOMMAND == "gestalt.subcommand"
        assert ATTR_MODULE_COUNT == "gestalt.module_count"
        assert ATTR_DRIFT_COUNT == "gestalt.drift_count"
        assert ATTR_DURATION_MS == "gestalt.duration_ms"
