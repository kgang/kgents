"""
Tests for dialectic CLI handler.

Tests for `kgents dialectic` command using H-gent HegelAgent.

Tests verify:
1. cmd_dialectic with --help
2. Error handling for missing concepts
3. Integration with HegelAgent
4. --json output mode
5. --save persistence mode
6. --drift comparison mode
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from ..dialectic import cmd_dialectic

# === cmd_dialectic Help Tests ===


class TestCmdDialecticHelp:
    """Tests for --help flag."""

    def test_help_flag_prints_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--help prints help and returns 0."""
        result = cmd_dialectic(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "dialectic" in captured.out.lower()
        assert "hegel" in captured.out.lower() or "synthesis" in captured.out.lower()

    def test_short_help_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """-h prints help and returns 0."""
        result = cmd_dialectic(["-h"])

        assert result == 0
        captured = capsys.readouterr()
        assert "dialectic" in captured.out.lower()


# === Error Handling Tests ===


class TestDialecticErrors:
    """Tests for error conditions."""

    def test_no_concepts_returns_error(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """No concepts returns error."""
        result = cmd_dialectic([])

        assert result == 1
        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "need" in captured.out.lower()


# === Integration Tests (with mock) ===


class TestDialecticIntegration:
    """Integration tests with mocked HegelAgent."""

    def test_dialectic_with_two_concepts(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """dialectic command with two concepts invokes HegelAgent."""
        from agents.h.hegel import DialecticOutput, DialecticStep
        from bootstrap.types import Tension, TensionMode

        mock_output = DialecticOutput(
            synthesis="Rapid refinement",
            sublation_notes="Quality emerges from fast feedback loops",
            productive_tension=False,
            tension=Tension(
                mode=TensionMode.LOGICAL,
                thesis="speed",
                antithesis="quality",
                severity=0.5,
                description="Tension between speed and quality",
            ),
            lineage=[
                DialecticStep(
                    stage="synthesis",
                    thesis="speed",
                    antithesis="quality",
                    result="Rapid refinement",
                    notes="Synthesis achieved",
                ),
            ],
        )

        mock_agent = AsyncMock()
        mock_agent.invoke = AsyncMock(return_value=mock_output)

        with patch("agents.h.hegel.HegelAgent", return_value=mock_agent):
            result = cmd_dialectic(["speed", "quality"])

        assert result == 0
        captured = capsys.readouterr()
        # Should show synthesis output
        assert "Synthesis" in captured.out or "DIALECTIC" in captured.out

    def test_dialectic_with_productive_tension(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """dialectic holds productive tension when sublation fails."""
        from agents.h.hegel import DialecticOutput, DialecticStep
        from bootstrap.types import Tension, TensionMode

        mock_output = DialecticOutput(
            synthesis=None,
            sublation_notes="These values cannot be reconciled without loss",
            productive_tension=True,
            tension=Tension(
                mode=TensionMode.LOGICAL,
                thesis="freedom",
                antithesis="security",
                severity=0.8,
                description="Tension between freedom and security",
            ),
            lineage=[
                DialecticStep(
                    stage="hold_tension",
                    thesis="freedom",
                    antithesis="security",
                    result=None,
                    notes="Holding productive tension",
                ),
            ],
        )

        mock_agent = AsyncMock()
        mock_agent.invoke = AsyncMock(return_value=mock_output)

        with patch("agents.h.hegel.HegelAgent", return_value=mock_agent):
            result = cmd_dialectic(["freedom", "security"])

        assert result == 0
        captured = capsys.readouterr()
        # Should show tension held
        assert "Tension" in captured.out or "DIALECTIC" in captured.out

    def test_dialectic_json_mode(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--json flag outputs valid JSON."""
        from agents.h.hegel import DialecticOutput, DialecticStep
        from bootstrap.types import Tension, TensionMode

        mock_output = DialecticOutput(
            synthesis="Test synthesis",
            sublation_notes="Test notes",
            productive_tension=False,
            tension=Tension(
                mode=TensionMode.LOGICAL,
                thesis="test1",
                antithesis="test2",
                severity=0.5,
                description="Test tension",
            ),
            lineage=[
                DialecticStep(
                    stage="synthesis",
                    thesis="test1",
                    antithesis="test2",
                    result="Test synthesis",
                    notes="Test",
                ),
            ],
        )

        mock_agent = AsyncMock()
        mock_agent.invoke = AsyncMock(return_value=mock_output)

        with patch("agents.h.hegel.HegelAgent", return_value=mock_agent):
            result = cmd_dialectic(["test1", "test2", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        # Should be valid JSON
        data = json.loads(captured.out)
        assert "command" in data
        assert data["command"] == "dialectic"
        assert "synthesis" in data
        assert "thesis" in data
        assert "antithesis" in data

    def test_dialectic_single_concept_surfaces_antithesis(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """dialectic with single concept surfaces antithesis via HegelAgent."""
        from agents.h.hegel import DialecticOutput, DialecticStep
        from bootstrap.types import Tension, TensionMode

        mock_output = DialecticOutput(
            synthesis="Bounded freedom",
            sublation_notes="Freedom implies boundaries",
            productive_tension=False,
            tension=Tension(
                mode=TensionMode.LOGICAL,
                thesis="freedom",
                antithesis="constraint",  # Surfaced by HegelAgent
                severity=0.5,
                description="Freedom implies constraint",
            ),
            lineage=[
                DialecticStep(
                    stage="surface_antithesis",
                    thesis="freedom",
                    antithesis="constraint",
                    result=None,
                    notes="Surfaced antithesis",
                ),
                DialecticStep(
                    stage="synthesis",
                    thesis="freedom",
                    antithesis="constraint",
                    result="Bounded freedom",
                    notes="Synthesis achieved",
                ),
            ],
        )

        mock_agent = AsyncMock()
        mock_agent.invoke = AsyncMock(return_value=mock_output)

        with patch("agents.h.hegel.HegelAgent", return_value=mock_agent):
            result = cmd_dialectic(["freedom"])

        assert result == 0
        captured = capsys.readouterr()
        # Should show synthesis output
        assert "Synthesis" in captured.out or "DIALECTIC" in captured.out


# === Save Mode Tests ===


class TestDialecticSaveMode:
    """Tests for --save persistence mode."""

    def test_save_flag_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--save flag is documented in help."""
        result = cmd_dialectic(["--help"])

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
        from agents.h.hegel import DialecticOutput, DialecticStep
        from bootstrap.types import Tension, TensionMode

        # Use temp directory for soul persistence
        monkeypatch.setenv("HOME", str(tmp_path))

        mock_output = DialecticOutput(
            synthesis="Test synthesis",
            sublation_notes="Test notes",
            productive_tension=False,
            tension=Tension(
                mode=TensionMode.LOGICAL,
                thesis="speed",
                antithesis="quality",
                severity=0.5,
                description="Test tension",
            ),
            lineage=[
                DialecticStep(
                    stage="synthesis",
                    thesis="speed",
                    antithesis="quality",
                    result="Test synthesis",
                    notes="Test",
                ),
            ],
        )

        mock_agent = AsyncMock()
        mock_agent.invoke = AsyncMock(return_value=mock_output)

        with patch("agents.h.hegel.HegelAgent", return_value=mock_agent):
            result = cmd_dialectic(["speed", "quality", "--save"])

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
        from agents.h.hegel import DialecticOutput, DialecticStep
        from bootstrap.types import Tension, TensionMode

        monkeypatch.setenv("HOME", str(tmp_path))

        mock_output = DialecticOutput(
            synthesis="Test synthesis",
            sublation_notes="Test notes",
            productive_tension=False,
            tension=Tension(
                mode=TensionMode.LOGICAL,
                thesis="test1",
                antithesis="test2",
                severity=0.5,
                description="Test tension",
            ),
            lineage=[
                DialecticStep(
                    stage="synthesis",
                    thesis="test1",
                    antithesis="test2",
                    result="Test synthesis",
                    notes="Test",
                ),
            ],
        )

        mock_agent = AsyncMock()
        mock_agent.invoke = AsyncMock(return_value=mock_output)

        with patch("agents.h.hegel.HegelAgent", return_value=mock_agent):
            result = cmd_dialectic(["test1", "test2", "--save", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data.get("saved") is True


# === Drift Mode Tests ===


class TestDialecticDriftMode:
    """Tests for --drift comparison mode."""

    def test_drift_flag_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--drift flag is documented in help."""
        result = cmd_dialectic(["--help"])

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
        from agents.h.hegel import DialecticOutput, DialecticStep
        from bootstrap.types import Tension, TensionMode

        monkeypatch.setenv("HOME", str(tmp_path))

        mock_output = DialecticOutput(
            synthesis="Test synthesis",
            sublation_notes="Test notes",
            productive_tension=False,
            tension=Tension(
                mode=TensionMode.LOGICAL,
                thesis="test1",
                antithesis="test2",
                severity=0.5,
                description="Test tension",
            ),
            lineage=[
                DialecticStep(
                    stage="synthesis",
                    thesis="test1",
                    antithesis="test2",
                    result="Test synthesis",
                    notes="Test",
                ),
            ],
        )

        mock_agent = AsyncMock()
        mock_agent.invoke = AsyncMock(return_value=mock_output)

        with patch("agents.h.hegel.HegelAgent", return_value=mock_agent):
            result = cmd_dialectic(["test1", "test2", "--drift"])

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
        from agents.h.hegel import DialecticOutput, DialecticStep
        from bootstrap.types import Tension, TensionMode

        monkeypatch.setenv("HOME", str(tmp_path))

        mock_output = DialecticOutput(
            synthesis="Test synthesis",
            sublation_notes="Test notes",
            productive_tension=False,
            tension=Tension(
                mode=TensionMode.LOGICAL,
                thesis="speed",
                antithesis="quality",
                severity=0.5,
                description="Test tension",
            ),
            lineage=[
                DialecticStep(
                    stage="synthesis",
                    thesis="speed",
                    antithesis="quality",
                    result="Test synthesis",
                    notes="Test",
                ),
            ],
        )

        mock_agent = AsyncMock()
        mock_agent.invoke = AsyncMock(return_value=mock_output)

        with patch("agents.h.hegel.HegelAgent", return_value=mock_agent):
            # First save a baseline
            result1 = cmd_dialectic(["speed", "quality", "--save"])
            assert result1 == 0

            # Then check drift
            result2 = cmd_dialectic(["speed", "quality", "--drift"])
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
        from agents.h.hegel import DialecticOutput, DialecticStep
        from bootstrap.types import Tension, TensionMode

        monkeypatch.setenv("HOME", str(tmp_path))

        mock_output = DialecticOutput(
            synthesis="Test synthesis",
            sublation_notes="Test notes",
            productive_tension=False,
            tension=Tension(
                mode=TensionMode.LOGICAL,
                thesis="test1",
                antithesis="test2",
                severity=0.5,
                description="Test tension",
            ),
            lineage=[
                DialecticStep(
                    stage="synthesis",
                    thesis="test1",
                    antithesis="test2",
                    result="Test synthesis",
                    notes="Test",
                ),
            ],
        )

        mock_agent = AsyncMock()
        mock_agent.invoke = AsyncMock(return_value=mock_output)

        with patch("agents.h.hegel.HegelAgent", return_value=mock_agent):
            # Save baseline first
            cmd_dialectic(["test1", "test2", "--save"])
            capsys.readouterr()  # Clear capture buffer

            # Get drift as JSON
            result = cmd_dialectic(["test1", "test2", "--drift", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "drift" in data
        assert "stability_score" in data["drift"]
