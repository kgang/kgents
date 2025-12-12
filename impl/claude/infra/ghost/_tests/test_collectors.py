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
