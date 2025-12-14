"""
Tests for I-gent CLI handlers.

Tests for:
- `kgents sparkline` - instant sparkline from numbers
- `kgents weather` - agent activity density visualization
- `kgents glitch` - zalgo text corruption
"""

from __future__ import annotations

import json

import pytest

from ..igent import cmd_glitch, cmd_sparkline, cmd_weather, cmd_whisper


class TestSparklineCommand:
    """Tests for sparkline command."""

    def test_sparkline_basic(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """sparkline renders values as vertical bars."""
        result = cmd_sparkline(["0.1", "0.3", "0.5", "0.8", "0.6", "0.4"])

        assert result == 0
        captured = capsys.readouterr()
        # Should contain sparkline characters
        assert any(c in captured.out for c in "▁▂▃▄▅▆▇█")

    def test_sparkline_with_label(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """sparkline with --label shows label prefix."""
        result = cmd_sparkline(["--label", "CPU", "0.2", "0.4", "0.6"])

        assert result == 0
        captured = capsys.readouterr()
        assert "CPU:" in captured.out

    def test_sparkline_auto_normalize(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """sparkline auto-normalizes values > 1."""
        result = cmd_sparkline(["10", "30", "50", "80", "60"])

        assert result == 0
        captured = capsys.readouterr()
        # Should still contain sparkline characters
        assert any(c in captured.out for c in "▁▂▃▄▅▆▇█")

    def test_sparkline_json_output(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """sparkline --json outputs JSON."""
        result = cmd_sparkline(["--json", "0.2", "0.4", "0.6"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["type"] == "sparkline"
        assert "values" in data
        assert len(data["values"]) == 3

    def test_sparkline_no_values_error(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """sparkline with no numbers shows error."""
        result = cmd_sparkline([])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_sparkline_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """sparkline --help shows help."""
        result = cmd_sparkline(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "sparkline" in captured.out.lower()
        assert "USAGE:" in captured.out


class TestWeatherCommand:
    """Tests for weather command."""

    def test_weather_basic(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """weather shows density field."""
        result = cmd_weather(["--size", "30x10"])

        assert result == 0
        captured = capsys.readouterr()
        assert "[WEATHER]" in captured.out
        # Should contain density runes
        assert any(c in captured.out for c in " ·∴∵◦○◎●◉")

    def test_weather_with_entropy(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """weather respects --entropy option."""
        result = cmd_weather(["--size", "20x8", "--entropy", "0.5"])

        assert result == 0
        captured = capsys.readouterr()
        assert "0.5" in captured.out  # entropy shown in legend

    def test_weather_json_output(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """weather --json outputs JSON."""
        result = cmd_weather(["--json", "--size", "10x5"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["type"] == "density_field"
        assert "width" in data
        assert "height" in data
        assert "entities" in data

    def test_weather_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """weather --help shows help."""
        result = cmd_weather(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "weather" in captured.out.lower()
        assert "USAGE:" in captured.out


class TestGlitchCommand:
    """Tests for glitch command."""

    def test_glitch_basic(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """glitch corrupts text."""
        result = cmd_glitch(["--entropy", "0.1", "Hello"])

        assert result == 0
        captured = capsys.readouterr()
        # Low entropy should mostly preserve text
        assert "H" in captured.out or "e" in captured.out

    def test_glitch_high_entropy(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """glitch with high entropy adds combining characters."""
        result = cmd_glitch(["--entropy", "0.8", "Test"])

        assert result == 0
        captured = capsys.readouterr()
        # High entropy output is typically longer due to combining chars
        assert len(captured.out.strip()) >= 4

    def test_glitch_json_output(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """glitch --json outputs JSON."""
        result = cmd_glitch(["--json", "Hi"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["original"] == "Hi"
        assert "entropy" in data
        assert "glyphs" in data

    def test_glitch_no_text_error(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """glitch with no text shows error."""
        result = cmd_glitch([])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_glitch_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """glitch --help shows help."""
        result = cmd_glitch(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "glitch" in captured.out.lower()
        assert "USAGE:" in captured.out


class TestWhisperCommand:
    """Tests for whisper command (existing)."""

    def test_whisper_basic(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """whisper returns some output."""
        result = cmd_whisper([])

        assert result == 0
        captured = capsys.readouterr()
        # Should have some output (even if just the empty circle)
        assert len(captured.out.strip()) >= 1

    def test_whisper_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """whisper --help shows help."""
        result = cmd_whisper(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "whisper" in captured.out.lower()
