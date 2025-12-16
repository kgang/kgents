"""
Tests for brain CLI handler.

Session 5: Crown Jewel Brain CLI

Tests use a simple embedder (no network calls) via fixture injection.

Note on test isolation:
    The brain handler uses module-level globals (_brain_logos, _brain_logos_factory).
    The autouse fixture resets these between tests, ensuring isolation in sequential
    runs. However, pytest-xdist parallel runs (-n auto) could cause race conditions
    if multiple workers execute brain tests simultaneously. For CI, either:
    - Run brain tests sequentially (no -n flag), OR
    - Use pytest markers to isolate these tests to a single worker
"""

from __future__ import annotations

import io
import sys
from typing import Generator

import pytest
from protocols.cli.handlers.brain import (
    _reset_brain_logos,
    _set_brain_logos_factory,
    cmd_brain,
)


@pytest.fixture(autouse=True)
def use_simple_embedder() -> Generator[None, None, None]:
    """Use simple embedder for all brain tests (no network calls).

    This fixture ensures tests don't download models or mutate global state.
    """
    from protocols.agentese import create_brain_logos

    def simple_brain_factory() -> object:
        """Create brain logos with simple (non-network) embedder."""
        return create_brain_logos(embedder_type="simple", dimension=64)

    _set_brain_logos_factory(simple_brain_factory)
    yield
    _set_brain_logos_factory(None)
    _reset_brain_logos()


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
