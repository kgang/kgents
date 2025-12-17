"""
Tests for brain CLI handler.

Session 5: Crown Jewel Brain CLI

Tests use temporary directory for brain storage to avoid polluting user data.

Note on test isolation:
    The brain handler uses a module-level global (_brain_crystal).
    The autouse fixture resets this between tests, ensuring isolation in sequential
    runs. However, pytest-xdist parallel runs (-n auto) could cause race conditions
    if multiple workers execute brain tests simultaneously. For CI, either:
    - Run brain tests sequentially (no -n flag), OR
    - Use pytest markers to isolate these tests to a single worker
"""

from __future__ import annotations

import io
import os
import sys
from typing import Generator

import pytest
from protocols.cli.handlers.brain import (
    _reset_brain,
    cmd_brain,
)


@pytest.fixture(autouse=True)
def isolate_brain(tmp_path: str) -> Generator[None, None, None]:
    """Isolate brain tests with temp directory and reset between tests.

    This ensures tests don't pollute user data and each test starts fresh.
    """
    from pathlib import Path

    # Use temp directory for brain storage
    brain_dir = Path(tmp_path) / "kgents" / "brain"
    brain_dir.mkdir(parents=True, exist_ok=True)

    # Set environment variable for brain storage location
    old_data_dir = os.environ.get("KGENTS_DATA_DIR")
    os.environ["KGENTS_DATA_DIR"] = str(Path(tmp_path))

    yield

    # Reset brain state after each test
    _reset_brain()

    # Restore original env
    if old_data_dir is not None:
        os.environ["KGENTS_DATA_DIR"] = old_data_dir
    elif "KGENTS_DATA_DIR" in os.environ:
        del os.environ["KGENTS_DATA_DIR"]


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


class TestBrainErrorPaths:
    """Tests for error handling in brain commands."""

    def test_unknown_subcommand(self) -> None:
        """Unknown subcommand returns error."""
        result = cmd_brain(["unknown_cmd"])
        assert result == 1

    def test_capture_whitespace_only(self) -> None:
        """Capture with whitespace-only content shows error."""
        result = cmd_brain(["capture", "   ", "  "])
        assert result == 1

    def test_ghost_whitespace_only(self) -> None:
        """Ghost with whitespace-only context shows error."""
        result = cmd_brain(["ghost", "   "])
        assert result == 1

    def test_multiple_args_capture(self) -> None:
        """Capture with multiple args joins them."""
        result = cmd_brain(["capture", "hello", "world"])
        assert result == 0

    def test_multiple_args_ghost(self) -> None:
        """Ghost with multiple args joins them."""
        result = cmd_brain(["ghost", "machine", "learning"])
        assert result == 0


class TestBrainImport:
    """Tests for brain import command."""

    def test_import_requires_path(self) -> None:
        """Import without --path shows error."""
        result = cmd_brain(["import", "--source", "obsidian"])
        assert result == 1

    def test_import_invalid_source(self, tmp_path: str) -> None:
        """Import with invalid source shows error."""
        from pathlib import Path

        path = Path(tmp_path)
        result = cmd_brain(["import", "--source", "invalid", "--path", str(path)])
        assert result == 1

    def test_import_nonexistent_path(self) -> None:
        """Import with nonexistent path shows error."""
        result = cmd_brain(
            ["import", "--source", "obsidian", "--path", "/nonexistent/path"]
        )
        assert result == 1

    def test_import_empty_vault(self, tmp_path: str) -> None:
        """Import from empty directory returns 0."""
        from pathlib import Path

        path = Path(tmp_path)
        result = cmd_brain(["import", "--source", "obsidian", "--path", str(path)])
        # Empty vault should succeed (no files to import)
        assert result == 0

    def test_import_dry_run(self, tmp_path: str) -> None:
        """Dry run previews import without storing."""
        from pathlib import Path

        path = Path(tmp_path)
        # Create a test file
        (path / "test.md").write_text("# Test\n\nContent")

        result = cmd_brain(
            ["import", "--source", "obsidian", "--path", str(path), "--dry-run"]
        )
        assert result == 0

    def test_import_with_files(self, tmp_path: str) -> None:
        """Import with files imports them."""
        from pathlib import Path

        path = Path(tmp_path)
        # Create test files
        (path / "note1.md").write_text("# Note 1\n\nContent one")
        (path / "note2.md").write_text("# Note 2\n\nContent two")

        result = cmd_brain(["import", "--source", "obsidian", "--path", str(path)])
        assert result == 0

    def test_import_json_output(self, tmp_path: str) -> None:
        """Import with --json returns structured output."""
        from pathlib import Path

        path = Path(tmp_path)
        (path / "test.md").write_text("# Test\n\nContent")

        result = cmd_brain(
            ["import", "--source", "obsidian", "--path", str(path), "--json"]
        )
        assert result == 0

    def test_import_dry_run_json(self, tmp_path: str) -> None:
        """Dry run with --json returns preview data."""
        from pathlib import Path

        path = Path(tmp_path)
        (path / "test.md").write_text("# Test\n\nContent")

        result = cmd_brain(
            [
                "import",
                "--source",
                "obsidian",
                "--path",
                str(path),
                "--dry-run",
                "--json",
            ]
        )
        assert result == 0

    def test_import_markdown_source(self, tmp_path: str) -> None:
        """Import with --source markdown works."""
        from pathlib import Path

        path = Path(tmp_path)
        (path / "test.md").write_text("# Test\n\nContent")

        result = cmd_brain(["import", "--source", "markdown", "--path", str(path)])
        assert result == 0

    def test_import_notion_source(self, tmp_path: str) -> None:
        """Import with --source notion works."""
        from pathlib import Path

        path = Path(tmp_path)
        (path / "test.md").write_text("# Test\n\nContent")

        result = cmd_brain(["import", "--source", "notion", "--path", str(path)])
        assert result == 0

    def test_import_skips_hidden_folders(self, tmp_path: str) -> None:
        """Import skips .obsidian and other hidden folders."""
        from pathlib import Path

        path = Path(tmp_path)
        # Create hidden folder with file
        hidden = path / ".obsidian"
        hidden.mkdir()
        (hidden / "config.json").write_text("{}")

        # Create visible file
        (path / "visible.md").write_text("# Visible\n\nContent")

        result = cmd_brain(["import", "--source", "obsidian", "--path", str(path)])
        assert result == 0


# =============================================================================
# Chat Tests (Phase 2: Brain + ChatFlow)
# =============================================================================


class TestBrainChat:
    """Tests for brain chat command (Phase 2 F-gent integration)."""

    def test_chat_single_query(self) -> None:
        """Chat with query argument does single query mode."""
        # First capture something
        result = cmd_brain(["capture", "Python is great for data science"])
        assert result == 0

        # Then chat query (non-interactive)
        result = cmd_brain(["chat", "Python"])
        assert result == 0

    def test_chat_single_query_json(self) -> None:
        """Chat with --json returns structured output."""
        # First capture something
        result = cmd_brain(["capture", "Machine learning with Python"])
        assert result == 0

        # Then chat query with JSON
        result = cmd_brain(["--json", "chat", "machine learning"])
        assert result == 0

    def test_chat_empty_query_shows_error(self) -> None:
        """Chat with empty query shows error."""
        result = cmd_brain(["chat", "   "])
        assert result == 1

    def test_chat_no_results_graceful(self) -> None:
        """Chat handles no results gracefully."""
        # Query something that won't exist
        result = cmd_brain(["chat", "xyznonexistent123"])
        assert result == 0  # Should succeed even with no results

    def test_chat_multiple_args_joins(self) -> None:
        """Chat with multiple args joins them into query."""
        # First capture something
        result = cmd_brain(["capture", "Category theory for programmers"])
        assert result == 0

        # Then chat with multiple words
        result = cmd_brain(["chat", "category", "theory"])
        assert result == 0
