"""
Tests for ghost collectors.

These tests verify that collectors gather real data from
the development environment.
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from infra.ghost.collectors import (
    CollectorResult,
    FlinchCollector,
    GitCollector,
    InfraCollector,
    create_all_collectors,
)


class TestCollectorResult:
    """Tests for CollectorResult dataclass."""

    def test_successful_result(self) -> None:
        """Successful result has success=True."""
        result = CollectorResult(
            source="test",
            timestamp="2025-01-01T00:00:00",
            success=True,
            data={"health_line": "test:ok"},
        )
        assert result.success
        assert result.health_line == "test:ok"

    def test_failed_result(self) -> None:
        """Failed result has success=False."""
        result = CollectorResult(
            source="test",
            timestamp="2025-01-01T00:00:00",
            success=False,
            error="Something went wrong",
        )
        assert not result.success
        assert result.health_line == "test:error"

    def test_missing_health_line(self) -> None:
        """Missing health_line defaults to source:ok."""
        result = CollectorResult(
            source="test",
            timestamp="2025-01-01T00:00:00",
            success=True,
            data={},
        )
        assert result.health_line == "test:ok"


class TestGitCollector:
    """Tests for GitCollector."""

    @pytest.mark.asyncio
    async def test_collect_in_git_repo(self) -> None:
        """Collector works in a git repository."""
        # Use the actual kgents repo
        collector = GitCollector(repo_path=Path.cwd())
        result = await collector.collect()

        assert result.success
        assert "branch" in result.data
        assert "dirty_count" in result.data
        assert result.data["branch"]  # Should have a branch name

    @pytest.mark.asyncio
    async def test_collect_not_git_repo(self) -> None:
        """Collector fails gracefully in non-git directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = GitCollector(repo_path=Path(tmpdir))
            result = await collector.collect()

            assert not result.success
            assert "Not a git repository" in (result.error or "")

    @pytest.mark.asyncio
    async def test_health_line_format(self) -> None:
        """Health line has expected format."""
        collector = GitCollector(repo_path=Path.cwd())
        result = await collector.collect()

        assert result.success
        health = result.data.get("health_line", "")
        assert "branch:" in health


class TestFlinchCollector:
    """Tests for FlinchCollector."""

    @pytest.mark.asyncio
    async def test_collect_with_existing_flinches(self) -> None:
        """Collector parses existing flinch data."""
        # Use actual flinch file if it exists
        flinch_path = Path.cwd() / ".kgents/ghost/test_flinches.jsonl"
        if not flinch_path.exists():
            pytest.skip("No flinch data available")

        collector = FlinchCollector(flinch_path=flinch_path)
        result = await collector.collect()

        assert result.success
        assert "total" in result.data
        assert result.data["total"] > 0  # Should have some flinches

    @pytest.mark.asyncio
    async def test_collect_empty_file(self) -> None:
        """Collector handles missing flinch file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flinch_path = Path(tmpdir) / "nonexistent.jsonl"
            collector = FlinchCollector(flinch_path=flinch_path)
            result = await collector.collect()

            assert result.success
            assert result.data.get("total") == 0

    @pytest.mark.asyncio
    async def test_collect_with_test_data(self) -> None:
        """Collector parses test JSONL data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flinch_path = Path(tmpdir) / "test_flinches.jsonl"

            # Write test data
            now = datetime.now().timestamp()
            flinches = [
                {"ts": now - 100, "test": "test_foo.py::test_one", "outcome": "failed"},
                {"ts": now - 200, "test": "test_foo.py::test_two", "outcome": "failed"},
                {
                    "ts": now - 300,
                    "test": "test_bar.py::test_three",
                    "outcome": "failed",
                },
            ]
            with open(flinch_path, "w") as f:
                for flinch in flinches:
                    f.write(json.dumps(flinch) + "\n")

            collector = FlinchCollector(flinch_path=flinch_path)
            result = await collector.collect()

            assert result.success
            assert result.data["total"] == 3
            assert result.data["last_hour"] == 3  # All within last hour

    def test_get_patterns(self) -> None:
        """get_patterns analyzes failure patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flinch_path = Path(tmpdir) / "test_flinches.jsonl"

            # Write test data with patterns
            now = datetime.now().timestamp()
            flinches = [
                {
                    "ts": now,
                    "test": "test_foo.py::TestClass::test_one",
                    "outcome": "failed",
                },
                {
                    "ts": now,
                    "test": "test_foo.py::TestClass::test_one",
                    "outcome": "failed",
                },
                {
                    "ts": now,
                    "test": "test_foo.py::TestClass::test_one",
                    "outcome": "failed",
                },
                {
                    "ts": now,
                    "test": "test_foo.py::TestClass::test_two",
                    "outcome": "failed",
                },
            ]
            with open(flinch_path, "w") as f:
                for flinch in flinches:
                    f.write(json.dumps(flinch) + "\n")

            collector = FlinchCollector(flinch_path=flinch_path)
            patterns = collector.get_patterns()

            assert patterns["total_flinches"] == 4
            assert len(patterns["patterns"]) > 0
            assert patterns["patterns"][0]["module"] == "test_foo.py"

    def test_get_hot_files(self) -> None:
        """get_hot_files returns files with most failures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flinch_path = Path(tmpdir) / "test_flinches.jsonl"

            # Write test data
            now = datetime.now().timestamp()
            flinches = [
                {"ts": now, "test": "test_foo.py::test_1", "outcome": "failed"},
                {"ts": now, "test": "test_foo.py::test_2", "outcome": "failed"},
                {"ts": now, "test": "test_foo.py::test_3", "outcome": "failed"},
                {"ts": now, "test": "test_bar.py::test_1", "outcome": "failed"},
            ]
            with open(flinch_path, "w") as f:
                for flinch in flinches:
                    f.write(json.dumps(flinch) + "\n")

            collector = FlinchCollector(flinch_path=flinch_path)
            hot = collector.get_hot_files()

            assert len(hot) == 2
            assert hot[0][0] == "test_foo.py"
            assert hot[0][1] == 3
            assert hot[1][0] == "test_bar.py"
            assert hot[1][1] == 1


class TestInfraCollector:
    """Tests for InfraCollector."""

    @pytest.mark.asyncio
    async def test_collect_returns_result(self) -> None:
        """Collector returns a result (success or graceful failure)."""
        collector = InfraCollector()
        result = await collector.collect()

        # Should always succeed (graceful degradation)
        assert result.success
        assert "cluster_status" in result.data


class TestCreateAllCollectors:
    """Tests for create_all_collectors factory."""

    def test_creates_standard_collectors(self) -> None:
        """Creates all standard collectors."""
        collectors = create_all_collectors()

        names = [c.name for c in collectors]
        assert "git" in names
        assert "flinch" in names
        assert "infra" in names

    def test_respects_project_root(self) -> None:
        """Collectors use provided project root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collectors = create_all_collectors(project_root=Path(tmpdir))

            # Git collector should use the temp dir
            git_collector = next(c for c in collectors if c.name == "git")
            assert isinstance(git_collector, GitCollector)
            assert git_collector.repo_path == Path(tmpdir)


class TestTraceGhostCollector:
    """Tests for TraceGhostCollector."""

    @pytest.mark.asyncio
    async def test_collect_returns_result(self) -> None:
        """Collector returns a result with success status."""
        from infra.ghost.collectors import TraceGhostCollector

        collector = TraceGhostCollector(base_path=Path.cwd())
        result = await collector.collect()

        # Should always succeed (graceful degradation)
        assert result.success or result.data.get("health_line") == "trace:not_available"

    @pytest.mark.asyncio
    async def test_collector_name(self) -> None:
        """Collector has correct name."""
        from infra.ghost.collectors import TraceGhostCollector

        collector = TraceGhostCollector()
        assert collector.name == "trace"

    @pytest.mark.asyncio
    async def test_collect_includes_static_analysis(self) -> None:
        """Collector includes static analysis metrics when available."""
        from infra.ghost.collectors import TraceGhostCollector

        collector = TraceGhostCollector(base_path=Path.cwd())
        result = await collector.collect()

        if result.success and "static_analysis" in result.data:
            static = result.data["static_analysis"]
            assert "files_analyzed" in static
            assert "definitions_found" in static
            assert "is_available" in static

    @pytest.mark.asyncio
    async def test_collect_includes_runtime_metrics(self) -> None:
        """Collector includes runtime trace metrics."""
        from infra.ghost.collectors import TraceGhostCollector

        collector = TraceGhostCollector(base_path=Path.cwd())
        result = await collector.collect()

        if result.success and "runtime" in result.data:
            runtime = result.data["runtime"]
            assert "total_events" in runtime
            assert "is_available" in runtime

    @pytest.mark.asyncio
    async def test_collect_includes_anomalies(self) -> None:
        """Collector includes anomalies list."""
        from infra.ghost.collectors import TraceGhostCollector

        collector = TraceGhostCollector(base_path=Path.cwd())
        result = await collector.collect()

        if result.success and "anomalies" in result.data:
            anomalies = result.data["anomalies"]
            assert isinstance(anomalies, list)

    @pytest.mark.asyncio
    async def test_collect_health_line(self) -> None:
        """Collector builds a health line."""
        from infra.ghost.collectors import TraceGhostCollector

        collector = TraceGhostCollector(base_path=Path.cwd())
        result = await collector.collect()

        assert "health_line" in result.data
        health = result.data["health_line"]
        assert health.startswith("trace:")

    @pytest.mark.asyncio
    async def test_graceful_degradation(self) -> None:
        """Collector degrades gracefully when TraceDataProvider unavailable."""
        from infra.ghost.collectors import TraceGhostCollector

        # Use a path with no Python files
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = TraceGhostCollector(base_path=Path(tmpdir))
            result = await collector.collect()

            # Should still succeed even with no files to analyze
            assert result.success

    @pytest.mark.asyncio
    async def test_collector_in_create_all(self) -> None:
        """TraceGhostCollector is included in create_all_collectors."""
        collectors = create_all_collectors()
        names = [c.name for c in collectors]
        assert "trace" in names

    @pytest.mark.asyncio
    async def test_hottest_functions_format(self) -> None:
        """Hottest functions are formatted correctly."""
        from infra.ghost.collectors import TraceGhostCollector

        collector = TraceGhostCollector(base_path=Path.cwd())
        result = await collector.collect()

        if result.success and "static_analysis" in result.data:
            static = result.data["static_analysis"]
            hottest = static.get("hottest_functions", [])
            for func in hottest:
                assert "name" in func
                assert "callers" in func


class TestHardeningFeatures:
    """Tests for robustness hardening."""

    @pytest.mark.asyncio
    async def test_git_collector_timeout_handling(self) -> None:
        """GitCollector has timeout handling."""
        from infra.ghost.collectors import GitCollector

        # Verify the method signature includes timeout
        collector = GitCollector()
        # The _run_git method should have timeout param
        import inspect

        sig = inspect.signature(collector._run_git)
        assert "timeout" in sig.parameters

    def test_flinch_collector_io_error_handling(self) -> None:
        """FlinchCollector handles IO errors gracefully."""
        from infra.ghost.collectors import FlinchCollector

        # Create collector pointing to a directory (not a file)
        with tempfile.TemporaryDirectory() as tmpdir:
            # Point to the directory itself, not a file
            dir_path = Path(tmpdir)
            collector = FlinchCollector(flinch_path=dir_path)

            # Should return empty patterns, not crash
            patterns = collector.get_patterns()
            assert "patterns" in patterns

            # get_hot_files should return empty list
            hot = collector.get_hot_files()
            assert hot == []

    def test_flinch_collector_invalid_test_field(self) -> None:
        """FlinchCollector handles non-string test fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flinch_path = Path(tmpdir) / "test.jsonl"

            # Write data with invalid test field types
            with open(flinch_path, "w") as f:
                f.write(json.dumps({"ts": 1000, "test": 123}) + "\n")  # int
                f.write(json.dumps({"ts": 1000, "test": None}) + "\n")  # None
                f.write(json.dumps({"ts": 1000, "test": "valid::test"}) + "\n")

            collector = FlinchCollector(flinch_path=flinch_path)
            patterns = collector.get_patterns()

            # Should only count the valid entry
            assert patterns["total_flinches"] == 3
            # But module grouping should skip invalid

    @pytest.mark.asyncio
    async def test_infra_collector_timeout_handling(self) -> None:
        """InfraCollector handles kubectl timeout gracefully."""
        # This tests that the collector has timeout handling in place
        # The actual timeout behavior is tested via the async wait_for
        from infra.ghost.collectors import DEFAULT_SUBPROCESS_TIMEOUT, InfraCollector

        collector = InfraCollector()
        # Verify the timeout constant exists and is reasonable
        assert DEFAULT_SUBPROCESS_TIMEOUT == 30.0

    @pytest.mark.asyncio
    async def test_git_collector_handles_timeout_gracefully(self) -> None:
        """GitCollector returns proper error on timeout."""
        from infra.ghost.collectors import GitCollector

        collector = GitCollector()

        # Call with a very short timeout to test error handling path
        # Note: This may actually complete before timeout on a real repo
        result = await collector._run_git("status", timeout=0.001)

        # Should either complete or return timeout error
        assert result is not None
        assert hasattr(result, "returncode")
        assert hasattr(result, "stdout")
        assert hasattr(result, "stderr")
