"""
Tests for gaps CLI handler.

Tests for `kgents gaps` command using H-gent LacanAgent.

Tests verify:
1. cmd_gaps with --help
2. Gaps analysis with default text
3. Gaps analysis with custom text
4. --json output mode
5. Register location output
"""

from __future__ import annotations

import json

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
