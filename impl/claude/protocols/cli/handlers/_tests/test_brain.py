"""
Tests for brain CLI handler.

Session 5: Crown Jewel Brain CLI
"""

from __future__ import annotations

import io
import sys

import pytest
from protocols.cli.handlers.brain import cmd_brain


class TestBrainHelp:
    """Tests for brain --help."""

    def test_help_returns_zero(self) -> None:
        """--help should return 0."""
        result = cmd_brain(["--help"])
        assert result == 0

    def test_help_short_returns_zero(self) -> None:
        """-h should return 0."""
        result = cmd_brain(["-h"])
        assert result == 0


class TestBrainStatus:
    """Tests for brain status command."""

    def test_status_default(self) -> None:
        """Default command (no args) shows status."""
        result = cmd_brain([])
        assert result == 0

    def test_status_explicit(self) -> None:
        """Explicit status command works."""
        result = cmd_brain(["status"])
        assert result == 0

    def test_status_json(self) -> None:
        """Status with --json returns structured output."""
        result = cmd_brain(["status", "--json"])
        assert result == 0


class TestBrainCapture:
    """Tests for brain capture command."""

    def test_capture_requires_content(self) -> None:
        """Capture without content shows error."""
        result = cmd_brain(["capture"])
        assert result == 1

    def test_capture_with_content(self) -> None:
        """Capture with content works."""
        result = cmd_brain(["capture", "test content here"])
        assert result == 0

    def test_capture_json(self) -> None:
        """Capture with --json returns structured output."""
        result = cmd_brain(["--json", "capture", "test content"])
        assert result == 0


class TestBrainGhost:
    """Tests for brain ghost command."""

    def test_ghost_requires_context(self) -> None:
        """Ghost without context shows error."""
        result = cmd_brain(["ghost"])
        assert result == 1

    def test_ghost_with_context(self) -> None:
        """Ghost with context works."""
        result = cmd_brain(["ghost", "test context"])
        assert result == 0


class TestBrainMap:
    """Tests for brain map command."""

    def test_map_works(self) -> None:
        """Map command works."""
        result = cmd_brain(["map"])
        assert result == 0

    def test_map_json(self) -> None:
        """Map with --json returns structured output."""
        result = cmd_brain(["--json", "map"])
        assert result == 0
