"""
Tests for archetype CLI handler.

Tests for `kgents archetype` command using H-gent identify_archetypes.

Tests verify:
1. cmd_archetype with --help
2. Archetype analysis with default self-image
3. Archetype analysis with custom self-image
4. --json output mode
5. Detection of specific archetypes
6. --save persistence mode
7. --drift comparison mode
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ..archetype import cmd_archetype

# === cmd_archetype Help Tests ===


class TestCmdArchetypeHelp:
    """Tests for --help flag."""

    def test_help_flag_prints_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--help prints help and returns 0."""
        result = cmd_archetype(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "archetype" in captured.out.lower()
        assert "jung" in captured.out.lower()

    def test_short_help_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """-h prints help and returns 0."""
        result = cmd_archetype(["-h"])

        assert result == 0
        captured = capsys.readouterr()
        assert "archetype" in captured.out.lower()


# === Archetype Analysis Tests ===


class TestArchetypeAnalysis:
    """Tests for archetype analysis using identify_archetypes."""

    def test_archetype_default_runs(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Archetype with no args uses default self-image."""
        result = cmd_archetype([])

        assert result == 0
        captured = capsys.readouterr()
        # Should have archetype analysis output
        assert "ARCHETYPE" in captured.out or "Archetype" in captured.out

    def test_archetype_custom_self_image(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Archetype with custom self-image."""
        result = cmd_archetype(["public interface system"])

        assert result == 0
        captured = capsys.readouterr()
        assert "Archetype" in captured.out or "ARCHETYPE" in captured.out

    def test_archetype_detects_persona(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Archetype detects persona archetype for 'public' keyword."""
        result = cmd_archetype(["I present a public interface to users"])

        assert result == 0
        captured = capsys.readouterr()
        # PERSONA archetype should be detected
        output_lower = captured.out.lower()
        assert "persona" in output_lower

    def test_archetype_detects_trickster(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Archetype detects trickster archetype for 'creative' keyword."""
        result = cmd_archetype(["I am creative and unexpected"])

        assert result == 0
        captured = capsys.readouterr()
        # TRICKSTER archetype should be detected
        output_lower = captured.out.lower()
        assert "trickster" in output_lower

    def test_archetype_detects_wise_old_man(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Archetype detects wise_old_man for 'knowledge' keyword."""
        result = cmd_archetype(["I have expert knowledge"])

        assert result == 0
        captured = capsys.readouterr()
        output_lower = captured.out.lower()
        assert "wise_old_man" in output_lower or "wise old man" in output_lower


# === JSON Output Tests ===


class TestArchetypeJsonOutput:
    """Tests for --json output mode."""

    def test_archetype_json_mode(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--json flag outputs valid JSON."""
        result = cmd_archetype(["public interface", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        # Should be valid JSON
        data = json.loads(captured.out)
        assert "command" in data
        assert data["command"] == "archetype"
        assert "active_archetypes" in data
        assert "shadow_archetypes" in data

    def test_archetype_json_has_required_fields(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON output has all required fields."""
        result = cmd_archetype(["--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        required_fields = [
            "command",
            "self_image",
            "active_archetypes",
            "shadow_archetypes",
            "active_and_shadow",
            "total_detected",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_archetype_json_structure(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON archetypes have correct structure."""
        result = cmd_archetype(["public knowledge expert", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        # Should have detected at least one archetype
        all_archetypes = (
            data["active_archetypes"]
            + data["shadow_archetypes"]
            + data["active_and_shadow"]
        )
        assert len(all_archetypes) > 0

        # Check structure of first archetype
        arch = all_archetypes[0]
        assert "archetype" in arch
        assert "manifestation" in arch
        assert "shadow_aspect" in arch


# === Integration Tests ===


class TestArchetypeIntegration:
    """Integration tests for archetype command."""

    def test_archetype_shows_total(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Archetype output includes total count."""
        result = cmd_archetype(["public creative knowledge"])

        assert result == 0
        captured = capsys.readouterr()
        # Should show total count
        assert "Total" in captured.out or "total" in captured.out.lower()

    def test_archetype_empty_detection(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Archetype handles no detections gracefully."""
        result = cmd_archetype(["xyz"])

        assert result == 0
        captured = capsys.readouterr()
        # Should still output something
        assert "ARCHETYPE" in captured.out or "Archetype" in captured.out


# === Save Mode Tests ===


class TestArchetypeSaveMode:
    """Tests for --save persistence mode."""

    def test_save_flag_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--save flag is documented in help."""
        result = cmd_archetype(["--help"])

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

        result = cmd_archetype(["public interface", "--save"])

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

        result = cmd_archetype(["public interface", "--save", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data.get("saved") is True


# === Drift Mode Tests ===


class TestArchetypeDriftMode:
    """Tests for --drift comparison mode."""

    def test_drift_flag_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--drift flag is documented in help."""
        result = cmd_archetype(["--help"])

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

        result = cmd_archetype(["public interface", "--drift"])

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
        result1 = cmd_archetype(["public interface", "--save"])
        assert result1 == 0

        # Then check drift
        result2 = cmd_archetype(["public interface", "--drift"])
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
        cmd_archetype(["public interface", "--save"])
        capsys.readouterr()  # Clear capture buffer

        # Get drift as JSON
        result = cmd_archetype(["public interface", "--drift", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "drift" in data
        assert "stability_score" in data["drift"]
