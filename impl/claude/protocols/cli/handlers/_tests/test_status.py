"""
Tests for status handler.

Tests trace health line integration and related functionality.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from protocols.cli.handlers.status import _get_trace_health_line


class TestGetTraceHealthLine:
    """Tests for _get_trace_health_line function."""

    def test_returns_none_when_file_missing(self) -> None:
        """Returns None when trace_summary.json doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _get_trace_health_line(Path(tmpdir))
            assert result is None

    def test_returns_none_when_not_available(self) -> None:
        """Returns None when static analysis is not available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ghost_dir = Path(tmpdir) / ".kgents" / "ghost"
            ghost_dir.mkdir(parents=True)

            trace_data = {
                "static_analysis": {"is_available": False},
                "runtime": {},
                "anomalies": [],
            }
            (ghost_dir / "trace_summary.json").write_text(json.dumps(trace_data))

            result = _get_trace_health_line(Path(tmpdir))
            assert result is None

    def test_formats_basic_trace_line(self) -> None:
        """Formats basic trace line with files and defs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ghost_dir = Path(tmpdir) / ".kgents" / "ghost"
            ghost_dir.mkdir(parents=True)

            trace_data = {
                "static_analysis": {
                    "files_analyzed": 100,
                    "definitions_found": 500,
                    "is_available": True,
                },
                "runtime": {},
                "anomalies": [],
            }
            (ghost_dir / "trace_summary.json").write_text(json.dumps(trace_data))

            result = _get_trace_health_line(Path(tmpdir))
            assert result is not None
            assert "[TRACE]" in result
            assert "100 files" in result
            assert "500 defs" in result
            assert "0 anomalies" in result

    def test_formats_large_numbers_with_commas(self) -> None:
        """Large numbers are formatted with commas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ghost_dir = Path(tmpdir) / ".kgents" / "ghost"
            ghost_dir.mkdir(parents=True)

            trace_data = {
                "static_analysis": {
                    "files_analyzed": 1000,
                    "definitions_found": 5000,
                    "is_available": True,
                },
                "runtime": {},
                "anomalies": [],
            }
            (ghost_dir / "trace_summary.json").write_text(json.dumps(trace_data))

            result = _get_trace_health_line(Path(tmpdir))
            assert result is not None
            assert "1,000 files" in result
            assert "5,000 defs" in result

    def test_includes_runtime_depth(self) -> None:
        """Includes runtime depth when available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ghost_dir = Path(tmpdir) / ".kgents" / "ghost"
            ghost_dir.mkdir(parents=True)

            trace_data = {
                "static_analysis": {
                    "files_analyzed": 100,
                    "definitions_found": 500,
                    "is_available": True,
                },
                "runtime": {
                    "avg_depth": 4.2,
                },
                "anomalies": [],
            }
            (ghost_dir / "trace_summary.json").write_text(json.dumps(trace_data))

            result = _get_trace_health_line(Path(tmpdir))
            assert result is not None
            assert "depth:4.2 avg" in result

    def test_includes_anomaly_count(self) -> None:
        """Includes anomaly count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ghost_dir = Path(tmpdir) / ".kgents" / "ghost"
            ghost_dir.mkdir(parents=True)

            trace_data = {
                "static_analysis": {
                    "files_analyzed": 100,
                    "definitions_found": 500,
                    "is_available": True,
                },
                "runtime": {},
                "anomalies": [
                    {"type": "test", "description": "test anomaly"},
                    {"type": "test2", "description": "another anomaly"},
                ],
            }
            (ghost_dir / "trace_summary.json").write_text(json.dumps(trace_data))

            result = _get_trace_health_line(Path(tmpdir))
            assert result is not None
            assert "2 anomalies" in result

    def test_handles_invalid_json_gracefully(self) -> None:
        """Handles invalid JSON gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ghost_dir = Path(tmpdir) / ".kgents" / "ghost"
            ghost_dir.mkdir(parents=True)

            (ghost_dir / "trace_summary.json").write_text("not valid json")

            result = _get_trace_health_line(Path(tmpdir))
            assert result is None

    def test_handles_empty_json_gracefully(self) -> None:
        """Handles empty JSON gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ghost_dir = Path(tmpdir) / ".kgents" / "ghost"
            ghost_dir.mkdir(parents=True)

            (ghost_dir / "trace_summary.json").write_text("{}")

            result = _get_trace_health_line(Path(tmpdir))
            assert result is None

    def test_full_trace_line_format(self) -> None:
        """Full trace line with all components."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ghost_dir = Path(tmpdir) / ".kgents" / "ghost"
            ghost_dir.mkdir(parents=True)

            trace_data = {
                "static_analysis": {
                    "files_analyzed": 512,
                    "definitions_found": 2847,
                    "is_available": True,
                },
                "runtime": {
                    "avg_depth": 4.2,
                },
                "anomalies": [],
            }
            (ghost_dir / "trace_summary.json").write_text(json.dumps(trace_data))

            result = _get_trace_health_line(Path(tmpdir))
            assert result is not None
            assert (
                result == "[TRACE] 512 files | 2,847 defs | depth:4.2 avg | 0 anomalies"
            )
