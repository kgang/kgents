"""
Tests for collective-shadow CLI handler.

Tests for `kgents collective-shadow` command using H-gent CollectiveShadowAgent.

Tests verify:
1. cmd_collective_shadow with --help
2. Collective shadow analysis with defaults
3. Custom agents and behaviors
4. --json output mode
"""

from __future__ import annotations

import json

import pytest

from ..collective_shadow import cmd_collective_shadow

# === cmd_collective_shadow Help Tests ===


class TestCmdCollectiveShadowHelp:
    """Tests for --help flag."""

    def test_help_flag_prints_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--help prints help and returns 0."""
        result = cmd_collective_shadow(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "collective" in captured.out.lower()
        assert "shadow" in captured.out.lower()

    def test_short_help_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """-h prints help and returns 0."""
        result = cmd_collective_shadow(["-h"])

        assert result == 0
        captured = capsys.readouterr()
        assert "collective" in captured.out.lower()


# === Collective Shadow Analysis Tests ===


class TestCollectiveShadowAnalysis:
    """Tests for collective shadow analysis using CollectiveShadowAgent."""

    def test_collective_shadow_default_runs(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Collective shadow with no args uses defaults."""
        result = cmd_collective_shadow([])

        assert result == 0
        captured = capsys.readouterr()
        # Should have collective shadow output
        assert "COLLECTIVE-SHADOW" in captured.out or "Collective" in captured.out

    def test_collective_shadow_shows_agents(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Collective shadow shows agents analyzed."""
        result = cmd_collective_shadow([])

        assert result == 0
        captured = capsys.readouterr()
        assert "Agent" in captured.out

    def test_collective_shadow_custom_agents(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Collective shadow with custom agents."""
        result = cmd_collective_shadow(["--agents", "Agent X,Agent Y,Agent Z"])

        assert result == 0
        captured = capsys.readouterr()
        assert "COLLECTIVE-SHADOW" in captured.out or "Collective" in captured.out

    def test_collective_shadow_custom_behaviors(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Collective shadow with custom behaviors."""
        result = cmd_collective_shadow(["--behaviors", "Behavior A,Behavior B"])

        assert result == 0
        captured = capsys.readouterr()
        assert "COLLECTIVE-SHADOW" in captured.out or "Collective" in captured.out


# === JSON Output Tests ===


class TestCollectiveShadowJsonOutput:
    """Tests for --json output mode."""

    def test_collective_shadow_json_mode(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--json flag outputs valid JSON."""
        result = cmd_collective_shadow(["--json"])

        assert result == 0
        captured = capsys.readouterr()

        # Should be valid JSON
        data = json.loads(captured.out)
        assert "command" in data
        assert data["command"] == "collective-shadow"
        assert "shadow_inventory" in data

    def test_collective_shadow_json_has_required_fields(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON output has all required fields."""
        result = cmd_collective_shadow(["--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        required_fields = [
            "command",
            "system_description",
            "agent_personas",
            "emergent_behaviors",
            "collective_persona",
            "shadow_inventory",
            "system_level_projections",
            "emergent_shadow_content",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_collective_shadow_json_custom_agents(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """JSON reflects custom agents."""
        result = cmd_collective_shadow(["--agents", "Test Agent", "--json"])

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert "Test Agent" in data["agent_personas"]


# === Integration Tests ===


class TestCollectiveShadowIntegration:
    """Integration tests for collective-shadow command."""

    def test_collective_shadow_shows_summary(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Collective shadow output includes summary."""
        result = cmd_collective_shadow([])

        assert result == 0
        captured = capsys.readouterr()
        # Should show summary
        assert "Summary" in captured.out or "summary" in captured.out.lower()

    def test_collective_shadow_equals_format(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--agents=X and --behaviors=Y format works."""
        result = cmd_collective_shadow(
            [
                "--agents=A,B,C",
                "--behaviors=X,Y",
                "--json",
            ]
        )

        assert result == 0
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert data["agent_personas"] == ["A", "B", "C"]
        assert data["emergent_behaviors"] == ["X", "Y"]
