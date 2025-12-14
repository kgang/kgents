"""
Tests for whatif CLI handler.

Tests for `kgents whatif` command - Pro Crown Jewel.

Tests verify:
1. cmd_whatif with --help
2. Generating alternatives with various prompts
3. --n flag for controlling number of alternatives
4. --json output mode
5. Alternative parsing and categorization
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from ..whatif import (
    _parse_alternatives,
    _print_help,
    cmd_whatif,
    set_soul,
)

# === cmd_whatif Help Tests ===


class TestCmdWhatIfHelp:
    """Tests for --help flag."""

    def test_help_flag_prints_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--help prints help and returns 0."""
        result = cmd_whatif(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "whatif" in captured.out.lower()
        assert "alternative" in captured.out.lower()
        assert "--n" in captured.out

    def test_short_help_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """-h prints help and returns 0."""
        result = cmd_whatif(["-h"])

        assert result == 0
        captured = capsys.readouterr()
        assert "alternative" in captured.out.lower()


# === Error Handling Tests ===


class TestWhatIfErrors:
    """Tests for error conditions."""

    def test_no_prompt_returns_error(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """No prompt argument returns error."""
        result = cmd_whatif([])

        assert result == 1
        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "no" in captured.out.lower()

    def test_only_flags_returns_error(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Only flags without prompt returns error."""
        result = cmd_whatif(["--json", "--n", "5"])

        assert result == 1
        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "no" in captured.out.lower()


# === Alternative Parsing Tests ===


class TestParseAlternatives:
    """Tests for _parse_alternatives function."""

    def test_parse_json_alternatives(self) -> None:
        """Parse JSON-formatted alternatives."""
        response = """
Here are some alternatives:

[
  {
    "title": "Direct approach",
    "description": "Just do it simply",
    "reality_type": "realistic",
    "confidence": 0.8
  },
  {
    "title": "Complex solution",
    "description": "Build a framework",
    "reality_type": "pessimistic",
    "confidence": 0.3
  }
]
"""
        result = _parse_alternatives(response, 3)

        assert len(result) == 2
        assert result[0]["title"] == "Direct approach"
        assert result[0]["reality_type"] == "realistic"
        assert result[0]["confidence"] == 0.8
        assert result[1]["title"] == "Complex solution"

    def test_parse_numbered_alternatives(self) -> None:
        """Parse numbered list alternatives."""
        response = """
Here are three approaches:

1. Minimal approach
   Use the simplest solution possible

2. Balanced approach
   Mix of simplicity and completeness

3. Comprehensive approach
   Full-featured solution with all bells and whistles
"""
        result = _parse_alternatives(response, 3)

        assert len(result) >= 1
        # Should extract at least the numbered items
        assert any("minimal" in alt["title"].lower() for alt in result)

    def test_parse_alternatives_limits_output(self) -> None:
        """_parse_alternatives respects the n limit."""
        response = """
[
  {"title": "A", "description": "First", "reality_type": "realistic", "confidence": 0.8},
  {"title": "B", "description": "Second", "reality_type": "optimistic", "confidence": 0.9},
  {"title": "C", "description": "Third", "reality_type": "pessimistic", "confidence": 0.5},
  {"title": "D", "description": "Fourth", "reality_type": "realistic", "confidence": 0.7}
]
"""
        result = _parse_alternatives(response, 2)

        assert len(result) == 2

    def test_parse_alternatives_fallback(self) -> None:
        """_parse_alternatives falls back when no structure found."""
        response = "This is just plain text without structure."

        result = _parse_alternatives(response, 3)

        # Should return at least one fallback alternative
        assert len(result) >= 1
        assert "Direct approach" in result[0]["title"]


# === Integration Tests (with mock) ===


class TestWhatIfIntegration:
    """Integration tests with mocked KgentSoul."""

    def test_whatif_generates_alternatives(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """whatif command generates alternatives."""
        # Mock the soul dialogue
        mock_output = AsyncMock()
        mock_output.response = """
[
  {
    "title": "Quick fix",
    "description": "Patch the issue directly",
    "reality_type": "optimistic",
    "confidence": 0.7
  },
  {
    "title": "Refactor",
    "description": "Redesign the system",
    "reality_type": "realistic",
    "confidence": 0.6
  },
  {
    "title": "Live with it",
    "description": "Accept the limitation",
    "reality_type": "pessimistic",
    "confidence": 0.9
  }
]
"""

        mock_soul = AsyncMock()
        mock_soul.dialogue = AsyncMock(return_value=mock_output)

        # Use set_soul to inject the mock
        set_soul(mock_soul)
        try:
            result = cmd_whatif(["I'm stuck on architecture"])
        finally:
            set_soul(None)  # Reset

        assert result == 0
        captured = capsys.readouterr()
        # Should show alternatives grouped by type
        assert "OPTIMISTIC" in captured.out or "optimistic" in captured.out
        assert "REALISTIC" in captured.out or "realistic" in captured.out
        assert "PESSIMISTIC" in captured.out or "pessimistic" in captured.out

    def test_whatif_n_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--n flag controls number of alternatives."""
        mock_output = AsyncMock()
        mock_output.response = """
[
  {"title": "A", "description": "First", "reality_type": "realistic", "confidence": 0.8},
  {"title": "B", "description": "Second", "reality_type": "optimistic", "confidence": 0.9},
  {"title": "C", "description": "Third", "reality_type": "pessimistic", "confidence": 0.5}
]
"""

        mock_soul = AsyncMock()
        mock_soul.dialogue = AsyncMock(return_value=mock_output)

        # Use set_soul to inject the mock
        set_soul(mock_soul)
        try:
            result = cmd_whatif(["test", "--n", "5"])
        finally:
            set_soul(None)  # Reset

        assert result == 0
        # The dialogue should have been called with n=5 in the prompt
        call_args = mock_soul.dialogue.call_args
        assert call_args is not None
        assert "5" in call_args[0][0]  # Check prompt contains the number

    def test_whatif_json_mode(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--json flag outputs JSON."""
        import json

        mock_output = AsyncMock()
        mock_output.response = """
[
  {"title": "Test", "description": "Test desc", "reality_type": "realistic", "confidence": 0.8}
]
"""

        mock_soul = AsyncMock()
        mock_soul.dialogue = AsyncMock(return_value=mock_output)

        # Use set_soul to inject the mock
        set_soul(mock_soul)
        try:
            result = cmd_whatif(["problem", "--json"])
        finally:
            set_soul(None)  # Reset

        assert result == 0
        captured = capsys.readouterr()
        # Should be valid JSON
        data = json.loads(captured.out)
        assert "command" in data
        assert data["command"] == "whatif"
        assert "alternatives" in data


# === Reality Type Tests ===


class TestRealityTypes:
    """Tests for reality type categorization."""

    def test_alternatives_have_valid_reality_types(self) -> None:
        """All parsed alternatives have valid reality types."""
        response = """
[
  {"title": "A", "description": "Test", "reality_type": "optimistic", "confidence": 0.8},
  {"title": "B", "description": "Test", "reality_type": "REALISTIC", "confidence": 0.7},
  {"title": "C", "description": "Test", "reality_type": "Pessimistic", "confidence": 0.5}
]
"""
        result = _parse_alternatives(response, 5)

        valid_types = {"optimistic", "realistic", "pessimistic"}
        for alt in result:
            assert alt["reality_type"] in valid_types
