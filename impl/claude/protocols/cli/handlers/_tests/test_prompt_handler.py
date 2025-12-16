"""
Tests for the Evergreen Prompt CLI Handler.

Wave 6 of the Evergreen Prompt System.

Tests:
- Help display
- Subcommand routing
- Compile with flags
- History command
- Rollback command
- Diff command
- Validate command
- Export command

See: plans/_continuations/evergreen-wave6-living-cli-continuation.md
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the handler
from protocols.cli.handlers.prompt import (
    USAGE,
    _handle_compile,
    _handle_diff,
    _handle_export,
    _handle_history,
    _handle_rollback,
    _handle_show,
    _handle_validate,
    cmd_prompt,
)


class TestCmdPromptRouting:
    """Tests for command routing."""

    def test_help_returns_zero(self) -> None:
        """--help returns 0 and prints usage."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            result = cmd_prompt(["--help"])
            assert result == 0
            output = mock_out.getvalue()
            assert "kg prompt" in output
            assert "USAGE" in output

    def test_h_flag_returns_zero(self) -> None:
        """-h returns 0 and prints usage."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            result = cmd_prompt(["-h"])
            assert result == 0
            output = mock_out.getvalue()
            assert "kg prompt" in output

    def test_unknown_subcommand_returns_one(self) -> None:
        """Unknown subcommand returns 1."""
        with patch("sys.stdout", new_callable=io.StringIO):
            result = cmd_prompt(["unknown_command"])
            assert result == 1


class TestHandleShow:
    """Tests for the show command."""

    @patch("protocols.prompt.cli.compile_prompt")
    def test_show_basic(self, mock_compile: MagicMock) -> None:
        """Basic show works."""
        mock_compile.return_value = "compiled content"
        result = _handle_show([])
        assert result == 0
        mock_compile.assert_called_once()

    @patch("protocols.prompt.cli.compile_prompt")
    def test_show_with_reasoning(self, mock_compile: MagicMock) -> None:
        """Show with --show-reasoning flag."""
        mock_compile.return_value = "compiled content"
        result = _handle_show(["--show-reasoning"])
        assert result == 0
        mock_compile.assert_called_once()
        call_kwargs = mock_compile.call_args[1]
        assert call_kwargs["show_reasoning"] is True

    @patch("protocols.prompt.cli.compile_prompt")
    def test_show_with_habits(self, mock_compile: MagicMock) -> None:
        """Show with --show-habits flag."""
        mock_compile.return_value = "compiled content"
        result = _handle_show(["--show-habits"])
        assert result == 0
        mock_compile.assert_called_once()
        call_kwargs = mock_compile.call_args[1]
        assert call_kwargs["show_habits"] is True


class TestHandleCompile:
    """Tests for the compile command."""

    @patch("protocols.prompt.cli.compile_prompt")
    def test_compile_basic(self, mock_compile: MagicMock) -> None:
        """Basic compile works."""
        mock_compile.return_value = "compiled content"
        result = _handle_compile([])
        assert result == 0

    @patch("protocols.prompt.cli.compile_prompt")
    def test_compile_with_output(self, mock_compile: MagicMock) -> None:
        """Compile with --output flag."""
        mock_compile.return_value = "compiled content"
        result = _handle_compile(["--output", "/tmp/test.md"])
        assert result == 0
        call_kwargs = mock_compile.call_args[1]
        assert call_kwargs["output_path"] == Path("/tmp/test.md")

    @patch("protocols.prompt.cli.compile_prompt")
    def test_compile_with_short_output(self, mock_compile: MagicMock) -> None:
        """Compile with -o flag."""
        mock_compile.return_value = "compiled content"
        result = _handle_compile(["-o", "/tmp/test.md"])
        assert result == 0
        call_kwargs = mock_compile.call_args[1]
        assert call_kwargs["output_path"] == Path("/tmp/test.md")

    @patch("protocols.prompt.cli.compile_prompt")
    def test_compile_no_checkpoint(self, mock_compile: MagicMock) -> None:
        """Compile with --no-checkpoint flag."""
        mock_compile.return_value = "compiled content"
        result = _handle_compile(["--no-checkpoint"])
        assert result == 0
        call_kwargs = mock_compile.call_args[1]
        assert call_kwargs["checkpoint"] is False

    @patch("protocols.prompt.cli.compile_prompt")
    def test_compile_with_feedback(self, mock_compile: MagicMock) -> None:
        """Compile with --feedback flag."""
        mock_compile.return_value = "compiled content"
        result = _handle_compile(["--feedback", "be more concise"])
        assert result == 0
        call_kwargs = mock_compile.call_args[1]
        assert call_kwargs["feedback"] == "be more concise"

    @patch("protocols.prompt.cli.compile_prompt")
    def test_compile_with_auto_improve(self, mock_compile: MagicMock) -> None:
        """Compile with --auto-improve flag."""
        mock_compile.return_value = "compiled content"
        result = _handle_compile(["--auto-improve"])
        assert result == 0
        call_kwargs = mock_compile.call_args[1]
        assert call_kwargs["auto_improve"] is True

    @patch("protocols.prompt.cli.compile_prompt")
    def test_compile_with_preview(self, mock_compile: MagicMock) -> None:
        """Compile with --preview flag."""
        mock_compile.return_value = "compiled content"
        result = _handle_compile(["--preview"])
        assert result == 0
        call_kwargs = mock_compile.call_args[1]
        assert call_kwargs["preview"] is True

    @patch("protocols.prompt.cli.compile_prompt")
    def test_compile_with_emit_metrics(self, mock_compile: MagicMock) -> None:
        """Compile with --emit-metrics flag."""
        mock_compile.return_value = "compiled content"
        result = _handle_compile(["--emit-metrics"])
        assert result == 0
        call_kwargs = mock_compile.call_args[1]
        assert call_kwargs["emit_metrics"] is True

    def test_compile_unknown_arg_returns_one(self) -> None:
        """Unknown argument returns 1."""
        with patch("sys.stdout", new_callable=io.StringIO):
            result = _handle_compile(["--unknown-flag"])
            assert result == 1


class TestHandleHistory:
    """Tests for the history command."""

    @patch("protocols.prompt.cli.show_history")
    def test_history_basic(self, mock_history: MagicMock) -> None:
        """Basic history works."""
        result = _handle_history([])
        assert result == 0
        mock_history.assert_called_once_with(limit=10)

    @patch("protocols.prompt.cli.show_history")
    def test_history_with_limit(self, mock_history: MagicMock) -> None:
        """History with --limit flag."""
        result = _handle_history(["--limit", "5"])
        assert result == 0
        mock_history.assert_called_once_with(limit=5)

    @patch("protocols.prompt.cli.show_history")
    def test_history_with_short_limit(self, mock_history: MagicMock) -> None:
        """History with -n flag."""
        result = _handle_history(["-n", "3"])
        assert result == 0
        mock_history.assert_called_once_with(limit=3)

    def test_history_invalid_limit(self) -> None:
        """Invalid limit returns 1."""
        with patch("sys.stdout", new_callable=io.StringIO):
            result = _handle_history(["--limit", "not_a_number"])
            assert result == 1


class TestHandleRollback:
    """Tests for the rollback command."""

    def test_rollback_no_id_returns_one(self) -> None:
        """Rollback without ID returns 1."""
        with patch("sys.stdout", new_callable=io.StringIO):
            result = _handle_rollback([])
            assert result == 1

    @patch("protocols.prompt.cli.do_rollback")
    def test_rollback_with_id(self, mock_rollback: MagicMock) -> None:
        """Rollback with ID works."""
        result = _handle_rollback(["abc12345"])
        assert result == 0
        mock_rollback.assert_called_once_with("abc12345")


class TestHandleDiff:
    """Tests for the diff command."""

    def test_diff_no_ids_returns_one(self) -> None:
        """Diff without IDs returns 1."""
        with patch("sys.stdout", new_callable=io.StringIO):
            result = _handle_diff([])
            assert result == 1

    def test_diff_one_id_returns_one(self) -> None:
        """Diff with one ID returns 1."""
        with patch("sys.stdout", new_callable=io.StringIO):
            result = _handle_diff(["abc12345"])
            assert result == 1

    @patch("protocols.prompt.cli.show_diff")
    def test_diff_with_two_ids(self, mock_diff: MagicMock) -> None:
        """Diff with two IDs works."""
        result = _handle_diff(["abc12345", "def67890"])
        assert result == 0
        mock_diff.assert_called_once_with("abc12345", "def67890")


class TestHandleValidate:
    """Tests for the validate command."""

    def test_validate_runs(self) -> None:
        """Validate runs without error."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            result = _handle_validate([])
            # Should return 0 or 1 depending on law checks
            assert result in (0, 1)
            output = mock_out.getvalue()
            assert (
                "category law checks" in output.lower()
                or "law checks" in output.lower()
            )


class TestHandleExport:
    """Tests for the export command."""

    @patch("protocols.prompt.cli.compile_prompt")
    def test_export_basic(self, mock_compile: MagicMock) -> None:
        """Basic export works."""
        mock_compile.return_value = "compiled content"
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            result = _handle_export([])
            assert result == 0
            output = mock_out.getvalue()
            assert "Exported" in output or "export" in output.lower()

    @patch("protocols.prompt.cli.compile_prompt")
    def test_export_with_output(self, mock_compile: MagicMock) -> None:
        """Export with --output flag."""
        mock_compile.return_value = "compiled content"
        with patch("sys.stdout", new_callable=io.StringIO):
            result = _handle_export(["--output", "/tmp/custom.md"])
            assert result == 0


class TestIntegration:
    """Integration tests for the full CLI flow."""

    def test_usage_contains_all_commands(self) -> None:
        """USAGE string contains all commands."""
        assert "compile" in USAGE
        assert "history" in USAGE
        assert "rollback" in USAGE
        assert "diff" in USAGE
        assert "validate" in USAGE
        assert "export" in USAGE

    def test_usage_contains_wave6_flags(self) -> None:
        """USAGE string contains Wave 6 flags."""
        assert "--show-reasoning" in USAGE
        assert "--show-habits" in USAGE
        assert "--feedback" in USAGE
        assert "--auto-improve" in USAGE
        assert "--preview" in USAGE
        assert "--emit-metrics" in USAGE

    @patch("protocols.prompt.cli.compile_prompt")
    def test_flag_based_show(self, mock_compile: MagicMock) -> None:
        """Flag-based show mode works."""
        mock_compile.return_value = "compiled content"
        result = cmd_prompt(["--show-reasoning"])
        assert result == 0
        mock_compile.assert_called_once()

    @patch("protocols.prompt.cli.compile_prompt")
    def test_full_compile_workflow(self, mock_compile: MagicMock) -> None:
        """Full compile workflow with multiple flags."""
        mock_compile.return_value = "compiled content"
        result = cmd_prompt(
            [
                "compile",
                "--output",
                "/tmp/test.md",
                "--show-reasoning",
                "--show-habits",
                "--emit-metrics",
            ]
        )
        assert result == 0
        mock_compile.assert_called_once()
        call_kwargs = mock_compile.call_args[1]
        assert call_kwargs["output_path"] == Path("/tmp/test.md")
        assert call_kwargs["show_reasoning"] is True
        assert call_kwargs["show_habits"] is True
        assert call_kwargs["emit_metrics"] is True
