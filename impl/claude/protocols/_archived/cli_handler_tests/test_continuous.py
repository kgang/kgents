"""
Tests for continuous CLI handler.

Tests for `kgents continuous` command using H-gent ContinuousDialectic.

Tests verify:
1. cmd_continuous with --help
2. Continuous dialectic with two theses
3. Continuous dialectic with multiple theses
4. --json output mode
5. --max flag for iteration limit
6. Error handling for insufficient theses
"""

from __future__ import annotations

import json

import pytest

from ..continuous import cmd_continuous

# === cmd_continuous Help Tests ===


class TestCmdContinuousHelp:
    """Tests for --help flag."""

    def test_help_flag_prints_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--help prints help and returns 0."""
        result = cmd_continuous(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "continuous" in captured.out.lower()
        assert "dialectic" in captured.out.lower()

    def test_short_help_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """-h prints help and returns 0."""
        result = cmd_continuous(["-h"])

        assert result == 0
        captured = capsys.readouterr()
        assert "continuous" in captured.out.lower()


# === Continuous Dialectic Tests ===


class TestContinuousDialectic:
    """Tests for continuous dialectic using ContinuousDialectic."""

    def test_continuous_two_theses(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Continuous dialectic with two theses."""
        result = cmd_continuous(["speed", "quality"])

        assert result == 0
        captured = capsys.readouterr()
        # Should have continuous dialectic output
        assert "CONTINUOUS" in captured.out or "Continuous" in captured.out

    def test_continuous_three_theses(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Continuous dialectic with three theses."""
        result = cmd_continuous(["speed", "quality", "simplicity"])

        assert result == 0
        captured = capsys.readouterr()
        assert "CONTINUOUS" in captured.out or "Continuous" in captured.out
        # Should show steps
        assert "Step" in captured.out

    def test_continuous_shows_theses(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Continuous dialectic shows the input theses."""
        result = cmd_continuous(["freedom", "security"])

        assert result == 0
        captured = capsys.readouterr()
        assert "freedom" in captured.out.lower() or "Theses" in captured.out

    def test_continuous_shows_result(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Continuous dialectic shows final result."""
        result = cmd_continuous(["abstract", "concrete"])

        assert result == 0
        captured = capsys.readouterr()
        # Should show result (either synthesis or tension)
        assert "Result" in captured.out or "result" in captured.out


# === Error Handling Tests ===


class TestContinuousErrors:
    """Tests for error handling."""

    def test_continuous_one_thesis_fails(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Continuous with one thesis fails with helpful error."""
        result = cmd_continuous(["lonely"])

        assert result == 1
        captured = capsys.readouterr()
        assert "at least two" in captured.out.lower()

    def test_continuous_no_theses_fails(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Continuous with no theses fails with helpful error."""
        result = cmd_continuous([])

        assert result == 1
        captured = capsys.readouterr()
        assert "at least two" in captured.out.lower()


# === JSON Output Tests ===


class TestContinuousJsonOutput:
    """Tests for --json output mode."""

    def test_continuous_json_mode(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--json flag outputs valid JSON."""
        result = cmd_continuous(["speed", "quality", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        # Should be valid JSON
        data = json.loads(captured.out)
        assert "command" in data
        assert data["command"] == "continuous"
        assert "theses" in data
        assert "steps" in data

    def test_continuous_json_has_required_fields(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON output has all required fields."""
        result = cmd_continuous(["A", "B", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        required_fields = [
            "command",
            "theses",
            "max_iterations",
            "steps",
            "iterations",
            "final_synthesis",
            "ended_in_tension",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_continuous_json_steps_structure(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON steps have correct structure."""
        result = cmd_continuous(["X", "Y", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert len(data["steps"]) > 0

        step = data["steps"][0]
        assert "thesis" in step
        assert "antithesis" in step
        assert "synthesis" in step
        assert "productive_tension" in step
        assert "notes" in step


# === Max Iterations Tests ===


class TestContinuousMaxIterations:
    """Tests for --max flag."""

    def test_continuous_max_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--max flag sets iteration limit."""
        result = cmd_continuous(["A", "B", "C", "D", "--max", "2", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert data["max_iterations"] == 2
        # Should respect the limit
        assert data["iterations"] <= 2

    def test_continuous_max_equals_format(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--max=N format works."""
        result = cmd_continuous(["A", "B", "--max=3", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert data["max_iterations"] == 3
