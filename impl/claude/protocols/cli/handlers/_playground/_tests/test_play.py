"""Tests for the play command handler."""

from __future__ import annotations

import pytest
from protocols.cli.handlers.play import _print_help, cmd_play


class TestCmdPlay:
    """Tests for the cmd_play function."""

    def test_help_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """cmd_play --help prints help and returns 0."""
        result = cmd_play(["--help"])
        assert result == 0
        captured = capsys.readouterr()
        assert (
            "Interactive Playground" in captured.out or "play" in captured.out.lower()
        )

    def test_help_short_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """cmd_play -h prints help and returns 0."""
        result = cmd_play(["-h"])
        assert result == 0
        captured = capsys.readouterr()
        assert "play" in captured.out.lower()


class TestPlaySubcommands:
    """Tests for play subcommands."""

    def test_unknown_tutorial(self) -> None:
        """Unknown tutorial returns error."""
        result = cmd_play(["nonexistent"])
        assert result == 1

    def test_hello_tutorial_json(self) -> None:
        """hello tutorial runs in JSON mode."""
        result = cmd_play(["hello", "--json"])
        # Should complete (JSON mode doesn't block on input)
        assert result == 0

    def test_compose_tutorial_json(self) -> None:
        """compose tutorial runs in JSON mode."""
        result = cmd_play(["compose", "--json"])
        assert result == 0

    def test_functor_tutorial_json(self) -> None:
        """functor tutorial runs in JSON mode."""
        result = cmd_play(["functor", "--json"])
        assert result == 0

    def test_soul_tutorial_json(self) -> None:
        """soul tutorial runs in JSON mode."""
        result = cmd_play(["soul", "--json"])
        assert result == 0


class TestPrintHelp:
    """Tests for _print_help function."""

    def test_print_help_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """_print_help outputs expected sections."""
        _print_help()
        captured = capsys.readouterr()
        assert "TUTORIALS:" in captured.out
        assert "hello" in captured.out
        assert "compose" in captured.out
        assert "functor" in captured.out
        assert "soul" in captured.out
        assert "repl" in captured.out
        assert "OPTIONS:" in captured.out
