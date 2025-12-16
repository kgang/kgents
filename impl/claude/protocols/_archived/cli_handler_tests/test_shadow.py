"""
Tests for shadow CLI handler.

Tests for `kgents shadow` command using H-gent JungAgent.

Tests verify:
1. cmd_shadow with --help
2. Shadow analysis with default self-image
3. Shadow analysis with custom self-image
4. --json output mode
5. --save persistence mode
6. --drift comparison mode
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from ..shadow import cmd_shadow

# === cmd_shadow Help Tests ===


class TestCmdShadowHelp:
    """Tests for --help flag."""

    def test_help_flag_prints_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--help prints help and returns 0."""
        result = cmd_shadow(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "shadow" in captured.out.lower()
        assert "jung" in captured.out.lower()

    def test_short_help_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """-h prints help and returns 0."""
        result = cmd_shadow(["-h"])

        assert result == 0
        captured = capsys.readouterr()
        assert "shadow" in captured.out.lower()


# === Shadow Analysis Tests (using actual JungAgent) ===


class TestShadowAnalysis:
    """Tests for shadow analysis using JungAgent."""

    def test_shadow_default_runs(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Shadow with no args uses default self-image."""
        result = cmd_shadow([])

        assert result == 0
        captured = capsys.readouterr()
        # Should have shadow analysis output
        assert "SHADOW" in captured.out or "Shadow" in captured.out

    def test_shadow_custom_self_image(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Shadow with custom self-image."""
        result = cmd_shadow(["helpful accurate safe"])

        assert result == 0
        captured = capsys.readouterr()
        # Should detect shadow from keywords
        assert "Shadow" in captured.out or "SHADOW" in captured.out

    def test_shadow_detects_helpful_shadow(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Shadow detects shadow content for 'helpful' claim."""
        result = cmd_shadow(["I am a helpful AI assistant"])

        assert result == 0
        captured = capsys.readouterr()
        # JungAgent should detect shadow for "helpful"
        # Should include reference to refusing/harming (the shadow of helpful)
        output_lower = captured.out.lower()
        assert "shadow" in output_lower
        assert (
            "refuse" in output_lower
            or "harm" in output_lower
            or "inventory" in output_lower
        )

    def test_shadow_detects_accurate_shadow(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Shadow detects shadow content for 'accurate' claim."""
        result = cmd_shadow(["I provide accurate information"])

        assert result == 0
        captured = capsys.readouterr()
        # JungAgent should detect shadow for "accurate"
        output_lower = captured.out.lower()
        assert "shadow" in output_lower
        # Should include reference to confabulation/hallucination
        assert (
            "confabulate" in output_lower
            or "hallucinate" in output_lower
            or "inventory" in output_lower
        )


# === JSON Output Tests ===


class TestShadowJsonOutput:
    """Tests for --json output mode."""

    def test_shadow_json_mode(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--json flag outputs valid JSON."""
        result = cmd_shadow(["helpful", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        # Should be valid JSON
        data = json.loads(captured.out)
        assert "command" in data
        assert data["command"] == "shadow"
        assert "shadow_inventory" in data
        assert "balance" in data

    def test_shadow_json_has_required_fields(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON output has all required fields."""
        result = cmd_shadow(["--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        required_fields = [
            "command",
            "self_image",
            "shadow_inventory",
            "projections",
            "integration_paths",
            "balance",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_shadow_json_inventory_structure(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON shadow_inventory has correct structure."""
        result = cmd_shadow(["helpful", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert isinstance(data["shadow_inventory"], list)
        if data["shadow_inventory"]:
            item = data["shadow_inventory"][0]
            assert "content" in item
            assert "exclusion_reason" in item
            assert "difficulty" in item


# === Integration Tests ===


class TestShadowIntegration:
    """Integration tests for shadow command."""

    def test_shadow_shows_balance(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Shadow output includes balance indicator."""
        result = cmd_shadow([])

        assert result == 0
        captured = capsys.readouterr()
        # Should show balance score
        assert "Balance" in captured.out or "balance" in captured.out

    def test_shadow_shows_integration_paths(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Shadow output includes integration paths when shadow detected."""
        result = cmd_shadow(["helpful accurate safe"])

        assert result == 0
        captured = capsys.readouterr()
        # When shadow is detected, should have integration paths
        assert "Integration" in captured.out or "integration" in captured.out.lower()


# === Save Mode Tests ===


class TestShadowSaveMode:
    """Tests for --save persistence mode."""

    def test_save_flag_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--save flag is documented in help."""
        result = cmd_shadow(["--help"])

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

        result = cmd_shadow(["helpful", "--save"])

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

        result = cmd_shadow(["helpful", "--save", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data.get("saved") is True


# === Drift Mode Tests ===


class TestShadowDriftMode:
    """Tests for --drift comparison mode."""

    def test_drift_flag_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--drift flag is documented in help."""
        result = cmd_shadow(["--help"])

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

        result = cmd_shadow(["helpful", "--drift"])

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
        result1 = cmd_shadow(["helpful", "--save"])
        assert result1 == 0

        # Then check drift
        result2 = cmd_shadow(["helpful", "--drift"])
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
        cmd_shadow(["helpful", "--save"])
        capsys.readouterr()  # Clear capture buffer

        # Get drift as JSON
        result = cmd_shadow(["helpful", "--drift", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "drift" in data
        assert "stability_score" in data["drift"]
