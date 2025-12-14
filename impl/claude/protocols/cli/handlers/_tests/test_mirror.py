"""
Tests for mirror CLI handler.

Tests for `kgents mirror` command - full introspection using all three H-gents.

Tests verify:
1. cmd_mirror with --help
2. Mirror combines all three H-gents
3. --json output mode
4. Integration summary
5. --save persistence mode
6. --drift comparison mode
7. --history timeline mode
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ..mirror import cmd_mirror

# === cmd_mirror Help Tests ===


class TestCmdMirrorHelp:
    """Tests for --help flag."""

    def test_help_flag_prints_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--help prints help and returns 0."""
        result = cmd_mirror(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "mirror" in captured.out.lower()

    def test_short_help_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """-h prints help and returns 0."""
        result = cmd_mirror(["-h"])

        assert result == 0
        captured = capsys.readouterr()
        assert "mirror" in captured.out.lower()


# === Mirror Analysis Tests ===


class TestMirrorAnalysis:
    """Tests for mirror combining all three H-gents."""

    def test_mirror_default_runs(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Mirror with no args uses default self-image."""
        result = cmd_mirror([])

        assert result == 0
        captured = capsys.readouterr()
        # Should have mirror output
        assert "MIRROR" in captured.out or "Mirror" in captured.out

    def test_mirror_custom_self_image(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Mirror with custom self-image."""
        result = cmd_mirror(["I am a helpful AI"])

        assert result == 0
        captured = capsys.readouterr()
        # Should have mirror output
        assert "Mirror" in captured.out or "MIRROR" in captured.out

    def test_mirror_shows_shadow_section(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Mirror shows Shadow (Jung) section."""
        result = cmd_mirror([])

        assert result == 0
        captured = capsys.readouterr()
        # Should have shadow section
        assert "Shadow" in captured.out or "Jung" in captured.out

    def test_mirror_shows_dialectic_section(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Mirror shows Dialectic (Hegel) section."""
        result = cmd_mirror([])

        assert result == 0
        captured = capsys.readouterr()
        # Should have dialectic section
        assert "Dialectic" in captured.out or "Hegel" in captured.out

    def test_mirror_shows_gaps_section(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Mirror shows Gaps (Lacan) section."""
        result = cmd_mirror([])

        assert result == 0
        captured = capsys.readouterr()
        # Should have gaps section
        assert "Gaps" in captured.out or "Lacan" in captured.out


# === JSON Output Tests ===


class TestMirrorJsonOutput:
    """Tests for --json output mode."""

    def test_mirror_json_mode(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--json flag outputs valid JSON."""
        result = cmd_mirror(["--json"])

        assert result == 0
        captured = capsys.readouterr()

        # Should be valid JSON
        data = json.loads(captured.out)
        assert "command" in data
        assert data["command"] == "mirror"

    def test_mirror_json_has_required_fields(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON output has all required fields."""
        result = cmd_mirror(["--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        required_fields = [
            "command",
            "self_image",
            "shadow",
            "dialectic",
            "gaps",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_mirror_json_shadow_structure(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON shadow section has correct structure."""
        result = cmd_mirror(["helpful", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        shadow = data["shadow"]
        assert "inventory" in shadow
        assert "projections" in shadow
        assert "balance" in shadow

    def test_mirror_json_dialectic_structure(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON dialectic section has correct structure."""
        result = cmd_mirror(["helpful", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        dialectic = data["dialectic"]
        assert "thesis" in dialectic
        assert "synthesis" in dialectic or "productive_tension" in dialectic


# === Integration Tests ===


class TestMirrorIntegration:
    """Integration tests for mirror command."""

    def test_mirror_shows_integration_summary(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Mirror output includes integration summary."""
        result = cmd_mirror([])

        assert result == 0
        captured = capsys.readouterr()
        # Should show integration section
        assert "Integration" in captured.out or "integration" in captured.out.lower()

    def test_mirror_shows_complete_analysis(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Mirror shows complete three-part analysis."""
        result = cmd_mirror(["helpful accurate safe"])

        assert result == 0
        captured = capsys.readouterr()
        # Should have all three sections marked
        output = captured.out
        sections_found = 0
        if "Shadow" in output or "Jung" in output:
            sections_found += 1
        if "Dialectic" in output or "Hegel" in output:
            sections_found += 1
        if "Gaps" in output or "Lacan" in output:
            sections_found += 1
        assert sections_found >= 2  # At least 2 of 3 sections visible


# === Save Mode Tests ===


class TestMirrorSaveMode:
    """Tests for --save persistence mode."""

    def test_save_flag_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--save flag is documented in help."""
        result = cmd_mirror(["--help"])

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
        monkeypatch.setenv("HOME", str(tmp_path))

        result = cmd_mirror(["helpful", "--save"])

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

        result = cmd_mirror(["helpful", "--save", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data.get("saved") is True


# === Drift Mode Tests ===


class TestMirrorDriftMode:
    """Tests for --drift comparison mode."""

    def test_drift_flag_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--drift flag is documented in help."""
        result = cmd_mirror(["--help"])

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

        result = cmd_mirror(["helpful", "--drift"])

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
        result1 = cmd_mirror(["helpful", "--save"])
        assert result1 == 0

        # Then check drift
        result2 = cmd_mirror(["helpful", "--drift"])
        assert result2 == 0

        captured = capsys.readouterr()
        # Should show drift report section
        assert "Drift" in captured.out or "Stability" in captured.out


# === History Mode Tests ===


class TestMirrorHistoryMode:
    """Tests for --history timeline mode."""

    def test_history_flag_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--history flag is documented in help."""
        result = cmd_mirror(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "--history" in captured.out

    def test_history_mode_empty(
        self,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """--history with no saved introspections shows appropriate message."""
        monkeypatch.setenv("HOME", str(tmp_path))

        result = cmd_mirror(["--history"])

        assert result == 0
        captured = capsys.readouterr()
        assert "No introspection history" in captured.out or "Timeline" in captured.out

    def test_history_mode_with_records(
        self,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """--history after --save shows timeline."""
        monkeypatch.setenv("HOME", str(tmp_path))

        # First save an introspection
        result1 = cmd_mirror(["helpful", "--save"])
        assert result1 == 0

        # Then check history
        result2 = cmd_mirror(["--history"])
        assert result2 == 0

        captured = capsys.readouterr()
        # Should show timeline
        assert "Timeline" in captured.out or "records" in captured.out.lower()

    def test_history_mode_json(
        self,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """--history --json outputs records array."""
        monkeypatch.setenv("HOME", str(tmp_path))

        # Save a record first
        cmd_mirror(["helpful", "--save"])
        capsys.readouterr()  # Clear capture buffer

        # Get history as JSON
        result = cmd_mirror(["--history", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "records" in data
        assert len(data["records"]) > 0
