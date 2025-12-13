"""
Tests for Ghost Daemon.

These tests verify the daemon correctly projects system state
to .kgents/ghost/ files, including trace_summary.json.
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from infra.ghost.collectors import CollectorResult, GhostCollector
from infra.ghost.daemon import GhostDaemon, create_ghost_daemon


class MockCollector(GhostCollector):
    """Mock collector for testing."""

    def __init__(self, name: str, data: dict[str, Any] | None = None):
        self._name = name
        self._data = data or {"health_line": f"{name}:ok"}
        self._success = True
        self._error: str | None = None

    @property
    def name(self) -> str:
        return self._name

    def set_failure(self, error: str) -> None:
        """Configure collector to fail."""
        self._success = False
        self._error = error

    async def collect(self) -> CollectorResult:
        from datetime import datetime

        return CollectorResult(
            source=self._name,
            timestamp=datetime.now().isoformat(),
            success=self._success,
            data=self._data,
            error=self._error,
        )


class TestGhostDaemon:
    """Tests for GhostDaemon."""

    def test_init_with_defaults(self) -> None:
        """Daemon initializes with default values."""
        daemon = GhostDaemon()

        assert daemon.project_root == Path.cwd()
        assert daemon.interval_seconds == 180.0  # 3 minutes
        assert daemon.ghost_dir == Path.cwd() / ".kgents" / "ghost"

    def test_init_with_custom_path(self) -> None:
        """Daemon uses provided project root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = GhostDaemon(project_root=Path(tmpdir))

            assert daemon.project_root == Path(tmpdir)
            assert daemon.ghost_dir == Path(tmpdir) / ".kgents" / "ghost"

    def test_add_collector(self) -> None:
        """Collectors can be added to daemon."""
        daemon = GhostDaemon()
        collector = MockCollector("test")

        daemon.add_collector(collector)

        assert len(daemon._collectors) == 1
        assert daemon._collectors[0].name == "test"

    def test_add_thought(self) -> None:
        """Thoughts can be added to the stream."""
        daemon = GhostDaemon()

        daemon.add_thought("Test thought", source="test", tags=["tag1"])

        assert len(daemon._thoughts) == 1
        assert daemon._thoughts[0]["content"] == "Test thought"
        assert daemon._thoughts[0]["source"] == "test"
        assert daemon._thoughts[0]["tags"] == ["tag1"]

    def test_add_thought_limits_to_50(self) -> None:
        """Thoughts are limited to last 50."""
        daemon = GhostDaemon()

        for i in range(60):
            daemon.add_thought(f"Thought {i}")

        assert len(daemon._thoughts) == 50
        assert daemon._thoughts[0]["content"] == "Thought 10"  # First 10 removed


class TestGhostDaemonProjection:
    """Tests for daemon projection."""

    @pytest.mark.asyncio
    async def test_project_once_creates_ghost_dir(self) -> None:
        """Projection creates .kgents/ghost/ directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = GhostDaemon(project_root=Path(tmpdir))
            daemon.add_collector(MockCollector("test"))

            await daemon.project_once()

            assert daemon.ghost_dir.exists()

    @pytest.mark.asyncio
    async def test_project_once_writes_health_status(self) -> None:
        """Projection writes health.status file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = GhostDaemon(project_root=Path(tmpdir))
            daemon.add_collector(MockCollector("test"))

            result = await daemon.project_once()

            health_path = daemon.ghost_dir / "health.status"
            assert health_path.exists()
            assert "health.status" in result.files_written

    @pytest.mark.asyncio
    async def test_project_once_writes_context_json(self) -> None:
        """Projection writes context.json file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = GhostDaemon(project_root=Path(tmpdir))
            daemon.add_collector(MockCollector("test"))

            result = await daemon.project_once()

            context_path = daemon.ghost_dir / "context.json"
            assert context_path.exists()
            assert "context.json" in result.files_written

            # Verify JSON structure
            context = json.loads(context_path.read_text())
            assert "timestamp" in context
            assert "collectors" in context
            assert "test" in context["collectors"]

    @pytest.mark.asyncio
    async def test_project_once_writes_thought_stream(self) -> None:
        """Projection writes thought_stream.md file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = GhostDaemon(project_root=Path(tmpdir))
            daemon.add_collector(MockCollector("test"))
            daemon.add_thought("Test thought")

            result = await daemon.project_once()

            thought_path = daemon.ghost_dir / "thought_stream.md"
            assert thought_path.exists()
            assert "thought_stream.md" in result.files_written

            content = thought_path.read_text()
            assert "Test thought" in content


class TestTraceSummaryProjection:
    """Tests for trace_summary.json projection."""

    @pytest.mark.asyncio
    async def test_project_writes_trace_summary_when_trace_collector_present(
        self,
    ) -> None:
        """Projection writes trace_summary.json when trace collector succeeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = GhostDaemon(project_root=Path(tmpdir))

            # Add a trace collector with mock data
            trace_data = {
                "static_analysis": {
                    "files_analyzed": 100,
                    "definitions_found": 500,
                    "calls_found": 1000,
                    "is_available": True,
                },
                "runtime": {
                    "total_events": 0,
                    "is_available": False,
                },
                "anomalies": [],
                "health_line": "trace:100files defs:500",
            }
            daemon.add_collector(MockCollector("trace", trace_data))

            result = await daemon.project_once()

            # trace_summary.json should be written
            trace_path = daemon.ghost_dir / "trace_summary.json"
            assert trace_path.exists(), "trace_summary.json should be created"
            assert "trace_summary.json" in result.files_written

            # Verify JSON structure
            trace_summary = json.loads(trace_path.read_text())
            assert trace_summary["static_analysis"]["files_analyzed"] == 100
            assert trace_summary["static_analysis"]["definitions_found"] == 500
            assert trace_summary["health_line"] == "trace:100files defs:500"

    @pytest.mark.asyncio
    async def test_project_skips_trace_summary_when_collector_fails(self) -> None:
        """Projection skips trace_summary.json when trace collector fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = GhostDaemon(project_root=Path(tmpdir))

            # Add a failing trace collector
            trace_collector = MockCollector("trace")
            trace_collector.set_failure("TraceDataProvider unavailable")
            daemon.add_collector(trace_collector)

            result = await daemon.project_once()

            # trace_summary.json should NOT be written
            trace_path = daemon.ghost_dir / "trace_summary.json"
            assert not trace_path.exists()
            assert "trace_summary.json" not in result.files_written

    @pytest.mark.asyncio
    async def test_project_includes_anomalies_in_trace_summary(self) -> None:
        """Projection includes anomalies in trace_summary.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = GhostDaemon(project_root=Path(tmpdir))

            # Add trace collector with anomalies
            trace_data = {
                "static_analysis": {"files_analyzed": 50, "is_available": True},
                "runtime": {"is_available": False},
                "anomalies": [
                    {
                        "type": "deep_recursion",
                        "description": "Recursion depth > 10",
                        "location": "foo.py:42",
                        "severity": "warning",
                        "detected_at": "2025-01-01T00:00:00",
                    }
                ],
                "health_line": "trace:50files anomalies:1",
            }
            daemon.add_collector(MockCollector("trace", trace_data))

            await daemon.project_once()

            trace_path = daemon.ghost_dir / "trace_summary.json"
            trace_summary = json.loads(trace_path.read_text())

            assert len(trace_summary["anomalies"]) == 1
            assert trace_summary["anomalies"][0]["type"] == "deep_recursion"
            assert trace_summary["anomalies"][0]["location"] == "foo.py:42"

    @pytest.mark.asyncio
    async def test_project_includes_hottest_functions(self) -> None:
        """Projection includes hottest functions in trace_summary.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = GhostDaemon(project_root=Path(tmpdir))

            trace_data = {
                "static_analysis": {
                    "files_analyzed": 100,
                    "definitions_found": 500,
                    "is_available": True,
                    "hottest_functions": [
                        {"name": "main", "callers": 50},
                        {"name": "helper", "callers": 25},
                    ],
                },
                "runtime": {"is_available": False},
                "anomalies": [],
                "health_line": "trace:100files",
            }
            daemon.add_collector(MockCollector("trace", trace_data))

            await daemon.project_once()

            trace_path = daemon.ghost_dir / "trace_summary.json"
            trace_summary = json.loads(trace_path.read_text())

            hottest = trace_summary["static_analysis"]["hottest_functions"]
            assert len(hottest) == 2
            assert hottest[0]["name"] == "main"
            assert hottest[0]["callers"] == 50


class TestCreateGhostDaemon:
    """Tests for create_ghost_daemon factory."""

    def test_creates_daemon_with_all_collectors(self) -> None:
        """Factory creates daemon with all standard collectors."""
        daemon = create_ghost_daemon()

        names = [c.name for c in daemon._collectors]
        assert "git" in names
        assert "flinch" in names
        assert "infra" in names
        assert "trace" in names

    def test_creates_daemon_with_custom_interval(self) -> None:
        """Factory respects custom interval."""
        daemon = create_ghost_daemon(interval_seconds=60.0)

        assert daemon.interval_seconds == 60.0

    def test_creates_daemon_with_progress_callback(self) -> None:
        """Factory respects progress callback."""
        messages: list[str] = []

        def on_progress(msg: str) -> None:
            messages.append(msg)

        daemon = create_ghost_daemon(on_progress=on_progress)
        daemon.on_progress("test")

        assert "test" in messages


class TestDaemonErrorHandling:
    """Tests for daemon error handling."""

    @pytest.mark.asyncio
    async def test_collector_exception_captured_in_errors(self) -> None:
        """Collector exceptions are captured in result.errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = GhostDaemon(project_root=Path(tmpdir))

            # Add a collector that will fail
            failing_collector = MockCollector("failing")
            failing_collector.set_failure("Test error")
            daemon.add_collector(failing_collector)

            result = await daemon.project_once()

            assert len(result.errors) > 0
            assert any("failing" in e for e in result.errors)

    @pytest.mark.asyncio
    async def test_projection_continues_after_collector_failure(self) -> None:
        """Projection continues even if one collector fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = GhostDaemon(project_root=Path(tmpdir))

            # Add both working and failing collectors
            daemon.add_collector(MockCollector("working"))
            failing = MockCollector("failing")
            failing.set_failure("Test error")
            daemon.add_collector(failing)

            result = await daemon.project_once()

            # Should still write files
            assert "health.status" in result.files_written
            assert "context.json" in result.files_written


class TestDaemonIntegration:
    """Integration tests for daemon with real collectors."""

    @pytest.mark.asyncio
    async def test_real_projection_with_trace_collector(self) -> None:
        """Real projection includes trace data when available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a minimal Python file to analyze
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            (src_dir / "example.py").write_text("def hello(): pass\n")

            daemon = create_ghost_daemon(project_root=Path(tmpdir))

            result = await daemon.project_once()

            # Should have written files
            assert result.health is not None
            assert "health.status" in result.files_written

            # Check if trace data was collected (may vary based on environment)
            trace_path = daemon.ghost_dir / "trace_summary.json"
            if trace_path.exists():
                trace_summary = json.loads(trace_path.read_text())
                assert "health_line" in trace_summary
