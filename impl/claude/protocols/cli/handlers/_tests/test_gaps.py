"""
Tests for gaps CLI handler.

Tests for `kgents gaps` command using H-gent LacanAgent.

Tests verify:
1. cmd_gaps with --help
2. Gaps analysis with default text
3. Gaps analysis with custom text
4. --json output mode
5. Register location output
6. --save persistence mode
7. --drift comparison mode
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ..gaps import cmd_gaps

# === cmd_gaps Help Tests ===


class TestCmdGapsHelp:
    """Tests for --help flag."""

    def test_help_flag_prints_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--help prints help and returns 0."""
        result = cmd_gaps(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "gaps" in captured.out.lower()
        assert "lacan" in captured.out.lower()

    def test_short_help_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """-h prints help and returns 0."""
        result = cmd_gaps(["-h"])

        assert result == 0
        captured = capsys.readouterr()
        assert "gaps" in captured.out.lower()


# === Gaps Analysis Tests (using actual LacanAgent) ===


class TestGapsAnalysis:
    """Tests for gaps analysis using LacanAgent."""

    def test_gaps_default_runs(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Gaps with no args uses default text."""
        result = cmd_gaps([])

        assert result == 0
        captured = capsys.readouterr()
        # Should have gaps analysis output
        assert "GAPS" in captured.out or "Gaps" in captured.out

    def test_gaps_custom_text(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Gaps with custom text."""
        result = cmd_gaps(["We are a helpful AI assistant"])

        assert result == 0
        captured = capsys.readouterr()
        # Should have gaps output
        assert "Gaps" in captured.out or "GAPS" in captured.out

    def test_gaps_detects_helpful_gaps(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Gaps detects gaps for 'helpful' claims."""
        result = cmd_gaps(["I am always helpful and understanding"])

        assert result == 0
        captured = capsys.readouterr()
        # LacanAgent should detect gaps
        output_lower = captured.out.lower()
        assert "gaps" in output_lower
        # Should have register analysis
        assert (
            "symbolic" in output_lower
            or "imaginary" in output_lower
            or "register" in output_lower
        )


# === JSON Output Tests ===


class TestGapsJsonOutput:
    """Tests for --json output mode."""

    def test_gaps_json_mode(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--json flag outputs valid JSON."""
        result = cmd_gaps(["helpful", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        # Should be valid JSON
        data = json.loads(captured.out)
        assert "command" in data
        assert data["command"] == "gaps"
        assert "gaps" in data
        assert "register_location" in data

    def test_gaps_json_has_required_fields(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON output has all required fields."""
        result = cmd_gaps(["--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        required_fields = [
            "command",
            "text",
            "gaps",
            "register_location",
            "slippages",
            "knot_status",
            "objet_petit_a",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_gaps_json_register_location_structure(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON register_location has correct structure."""
        result = cmd_gaps(["helpful", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        reg = data["register_location"]
        assert "symbolic" in reg
        assert "imaginary" in reg
        assert "real_proximity" in reg
        # Values should be floats between 0 and 1
        assert 0 <= reg["symbolic"] <= 1
        assert 0 <= reg["imaginary"] <= 1
        assert 0 <= reg["real_proximity"] <= 1


# === Integration Tests ===


class TestGapsIntegration:
    """Integration tests for gaps command."""

    def test_gaps_shows_register_location(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Gaps output includes register location."""
        result = cmd_gaps([])

        assert result == 0
        captured = capsys.readouterr()
        # Should show register location
        assert "Register" in captured.out or "register" in captured.out.lower()

    def test_gaps_shows_knot_status(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Gaps output includes knot status."""
        result = cmd_gaps(["We are helpful"])

        assert result == 0
        captured = capsys.readouterr()
        # Should show knot status
        assert "Knot" in captured.out or "knot" in captured.out.lower()


# === Save Mode Tests ===


class TestGapsSaveMode:
    """Tests for --save persistence mode."""

    def test_save_flag_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--save flag is documented in help."""
        result = cmd_gaps(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "--save" in captured.out

    def test_save_mode_confirms_save(
        self,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """--save flag shows confirmation message."""
        # Use temp directory for soul persistence
        monkeypatch.setenv("HOME", str(tmp_path))

        result = cmd_gaps(["helpful", "--save"])

        assert result == 0
        captured = capsys.readouterr()
        assert "Saved" in captured.out or "saved" in captured.out.lower()

    def test_save_mode_json_has_saved_field(
        self,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """--save --json includes saved field."""
        monkeypatch.setenv("HOME", str(tmp_path))

        result = cmd_gaps(["helpful", "--save", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data.get("saved") is True


# === Drift Mode Tests ===


class TestGapsDriftMode:
    """Tests for --drift comparison mode."""

    def test_drift_flag_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--drift flag is documented in help."""
        result = cmd_gaps(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "--drift" in captured.out

    def test_drift_mode_no_baseline(
        self,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """--drift with no previous save shows appropriate message."""
        monkeypatch.setenv("HOME", str(tmp_path))

        result = cmd_gaps(["helpful", "--drift"])

        assert result == 0
        captured = capsys.readouterr()
        # Should mention no previous analysis
        assert "No previous" in captured.out or "baseline" in captured.out.lower()

    def test_drift_mode_with_baseline(
        self,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """--drift after --save shows drift report."""
        monkeypatch.setenv("HOME", str(tmp_path))

        # First save a baseline
        result1 = cmd_gaps(["helpful", "--save"])
        assert result1 == 0

        # Then check drift
        result2 = cmd_gaps(["helpful", "--drift"])
        assert result2 == 0

        captured = capsys.readouterr()
        # Should show drift report section
        assert "Drift" in captured.out or "Stability" in captured.out

    def test_drift_mode_json_has_drift_field(
        self,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """--drift --json includes drift field when baseline exists."""
        monkeypatch.setenv("HOME", str(tmp_path))

        # Save baseline first
        cmd_gaps(["helpful", "--save"])
        capsys.readouterr()  # Clear capture buffer

        # Get drift as JSON
        result = cmd_gaps(["helpful", "--drift", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "drift" in data
        assert "stability_score" in data["drift"]
