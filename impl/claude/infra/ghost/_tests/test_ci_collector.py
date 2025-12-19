"""Tests for CISignalCollector - CI feedback loop."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import AsyncIterator

import pytest

from infra.ghost.ci_collector import CISignal, CISignalCollector


class TestCISignal:
    """Tests for CISignal dataclass."""

    def test_from_dict_valid(self) -> None:
        """Parse valid CI signal from dict."""
        data = {
            "ts": 1702900000.0,
            "type": "CI_SUCCESS",
            "sha": "abc123def456",
            "ref": "refs/heads/main",
            "run_number": 42,
            "suites": {"unit": "success", "laws": "success", "integration": "success"},
        }
        signal = CISignal.from_dict(data)
        assert signal is not None
        assert signal.type == "CI_SUCCESS"
        assert signal.sha == "abc123def456"
        assert signal.run_number == 42
        assert signal.is_success is True
        assert signal.failed_suites == []
        assert signal.short_sha == "abc123d"

    def test_from_dict_failure(self) -> None:
        """Parse failed CI signal."""
        data = {
            "ts": 1702900000.0,
            "type": "CI_FAILURE",
            "sha": "xyz789",
            "ref": "refs/heads/main",
            "run_number": 43,
            "suites": {"unit": "success", "laws": "failure", "integration": "skipped"},
        }
        signal = CISignal.from_dict(data)
        assert signal is not None
        assert signal.is_success is False
        assert signal.failed_suites == ["laws"]

    def test_from_dict_invalid(self) -> None:
        """Return None for invalid data."""
        signal = CISignal.from_dict({"invalid": "data"})
        # Should still parse but with defaults
        assert signal is not None
        assert signal.type == "UNKNOWN"


class TestCISignalCollector:
    """Tests for CISignalCollector."""

    @pytest.fixture
    def temp_signal_file(self, tmp_path: Path) -> Path:
        """Create temporary signal file path."""
        return tmp_path / "ci_signals.jsonl"

    @pytest.fixture
    def collector(self, temp_signal_file: Path) -> CISignalCollector:
        """Create collector with temp file."""
        return CISignalCollector(signal_path=temp_signal_file)

    @pytest.fixture
    async def populated_collector(self, temp_signal_file: Path) -> AsyncIterator[CISignalCollector]:
        """Create collector with sample data."""
        now = time.time()

        signals = [
            {
                "ts": now - 7200,  # 2 hours ago
                "type": "CI_SUCCESS",
                "sha": "aaa111",
                "ref": "refs/heads/main",
                "run_number": 1,
                "suites": {"unit": "success", "laws": "success", "integration": "success"},
            },
            {
                "ts": now - 3600,  # 1 hour ago
                "type": "CI_FAILURE",
                "sha": "bbb222",
                "ref": "refs/heads/main",
                "run_number": 2,
                "suites": {"unit": "success", "laws": "failure", "integration": "success"},
            },
            {
                "ts": now - 1800,  # 30 min ago
                "type": "CI_SUCCESS",
                "sha": "ccc333",
                "ref": "refs/heads/main",
                "run_number": 3,
                "suites": {"unit": "success", "laws": "success", "integration": "success"},
            },
        ]

        with open(temp_signal_file, "w") as f:
            for signal in signals:
                f.write(json.dumps(signal) + "\n")

        yield CISignalCollector(signal_path=temp_signal_file)

    async def test_collect_no_file(self, collector: CISignalCollector) -> None:
        """Collect returns no_data when file doesn't exist."""
        result = await collector.collect()
        assert result.success is True
        assert result.data["total"] == 0
        assert "no_data" in result.health_line

    async def test_collect_empty_file(
        self, collector: CISignalCollector, temp_signal_file: Path
    ) -> None:
        """Collect returns empty when file exists but is empty."""
        temp_signal_file.touch()
        result = await collector.collect()
        assert result.success is True
        assert result.data["total"] == 0
        assert "empty" in result.health_line

    async def test_collect_with_data(self, populated_collector: CISignalCollector) -> None:
        """Collect analyzes signals correctly."""
        result = await populated_collector.collect()
        assert result.success is True
        assert result.data["total"] == 3
        assert result.data["last_24h"] == 3
        # 2 passed, 1 failed in last 24h
        assert result.data["passed_24h"] == 2
        assert result.data["failed_24h"] == 1
        assert "2/3" in result.health_line or "failing" in result.health_line

    async def test_collect_latest_signal(self, populated_collector: CISignalCollector) -> None:
        """Collect includes latest signal info."""
        result = await populated_collector.collect()
        assert "latest" in result.data
        assert result.data["latest"]["sha"] == "ccc333"
        assert result.data["latest"]["run_number"] == 3

    def test_get_recent_failures(self, populated_collector: CISignalCollector) -> None:
        """get_recent_failures returns failed signals."""
        # Use the sync fixture by running collect first to warm up
        failures = populated_collector.get_recent_failures(limit=5)
        assert len(failures) == 1
        assert failures[0].sha == "bbb222"

    def test_get_suite_stats(self, populated_collector: CISignalCollector) -> None:
        """get_suite_stats counts per-suite results."""
        stats = populated_collector.get_suite_stats()
        assert stats["unit"]["passed"] == 3
        assert stats["unit"]["failed"] == 0
        assert stats["laws"]["passed"] == 2
        assert stats["laws"]["failed"] == 1


class TestHealthLineFormats:
    """Test various health line formats."""

    @pytest.fixture
    def temp_signal_file(self, tmp_path: Path) -> Path:
        return tmp_path / "ci_signals.jsonl"

    async def test_all_pass_health_line(self, temp_signal_file: Path) -> None:
        """All passing shows 'all_pass'."""
        now = time.time()
        signals = [
            {
                "ts": now - 100,
                "type": "CI_SUCCESS",
                "sha": "a",
                "ref": "main",
                "run_number": 1,
                "suites": {},
            },
            {
                "ts": now - 50,
                "type": "CI_SUCCESS",
                "sha": "b",
                "ref": "main",
                "run_number": 2,
                "suites": {},
            },
        ]
        with open(temp_signal_file, "w") as f:
            for s in signals:
                f.write(json.dumps(s) + "\n")

        collector = CISignalCollector(signal_path=temp_signal_file)
        result = await collector.collect()
        assert "all_pass" in result.health_line

    async def test_failing_suites_health_line(self, temp_signal_file: Path) -> None:
        """Recent failure shows failing suites."""
        now = time.time()
        signals = [
            {
                "ts": now - 100,
                "type": "CI_FAILURE",
                "sha": "x",
                "ref": "main",
                "run_number": 1,
                "suites": {"unit": "failure", "laws": "failure"},
            },
        ]
        with open(temp_signal_file, "w") as f:
            for s in signals:
                f.write(json.dumps(s) + "\n")

        collector = CISignalCollector(signal_path=temp_signal_file)
        result = await collector.collect()
        assert "failing" in result.health_line
        assert "laws" in result.health_line or "unit" in result.health_line
