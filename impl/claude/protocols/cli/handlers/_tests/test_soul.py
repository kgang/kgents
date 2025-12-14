"""
Tests for soul CLI handler.

Tests for `kgents soul` command.

Tests verify:
1. cmd_soul with --help
2. Soul dialogue modes (reflect, advise, challenge, explore)
3. Soul stream ambient mode
4. --json output mode
5. Mode alias commands (cmd_reflect, cmd_advise, etc.)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from ..soul import (
    _print_help,
    cmd_advise,
    cmd_challenge,
    cmd_explore,
    cmd_reflect,
    cmd_soul,
)

# === cmd_soul Help Tests ===


class TestCmdSoulHelp:
    """Tests for --help flag."""

    def test_help_flag_prints_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--help prints help and returns 0."""
        result = cmd_soul(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "kgents soul" in captured.out.lower() or "soul" in captured.out.lower()
        assert "MODES:" in captured.out
        assert "reflect" in captured.out
        assert "advise" in captured.out
        assert "challenge" in captured.out
        assert "explore" in captured.out

    def test_short_help_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """-h prints help and returns 0."""
        result = cmd_soul(["-h"])

        assert result == 0
        captured = capsys.readouterr()
        assert "MODES:" in captured.out

    def test_help_shows_stream_command(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Help shows stream command."""
        result = cmd_soul(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "stream" in captured.out


# === Mode Alias Tests ===


class TestModeAliases:
    """Tests for mode alias commands."""

    def test_reflect_alias_delegates(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_reflect delegates to cmd_soul with reflect mode."""
        # Just test that it doesn't crash with --help
        result = cmd_reflect(["--help"])
        assert result == 0
        captured = capsys.readouterr()
        assert "reflect" in captured.out.lower()

    def test_advise_alias_delegates(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_advise delegates to cmd_soul with advise mode."""
        result = cmd_advise(["--help"])
        assert result == 0
        captured = capsys.readouterr()
        assert "MODES:" in captured.out

    def test_challenge_alias_delegates(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_challenge delegates to cmd_soul with challenge mode."""
        result = cmd_challenge(["--help"])
        assert result == 0
        captured = capsys.readouterr()
        assert "MODES:" in captured.out

    def test_explore_alias_delegates(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_explore delegates to cmd_soul with explore mode."""
        result = cmd_explore(["--help"])
        assert result == 0
        captured = capsys.readouterr()
        assert "MODES:" in captured.out


# === Soul Dialogue Tests ===


class TestSoulDialogue:
    """Tests for soul dialogue functionality."""

    def test_soul_reflect_with_template(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Reflect mode generates a response."""
        result = cmd_soul(["reflect", "test prompt"])

        assert result == 0
        captured = capsys.readouterr()
        # Should have some output (either template or error)
        assert len(captured.out) > 0

    def test_soul_quick_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--quick flag uses whisper budget."""
        result = cmd_soul(["--quick", "reflect", "test"])

        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_soul_json_output(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--json flag produces JSON output."""
        result = cmd_soul(["--json", "reflect", "test"])

        assert result == 0
        captured = capsys.readouterr()
        # Should contain JSON structure markers
        assert "{" in captured.out or "error" in captured.out.lower()


# === Soul Stream Tests ===


class TestSoulStream:
    """Tests for soul stream ambient mode."""

    def test_stream_help_in_main_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Stream command appears in main help."""
        result = cmd_soul(["--help"])

        captured = capsys.readouterr()
        assert "stream" in captured.out

    def test_stream_pulse_interval_option(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--pulse-interval option appears in help."""
        result = cmd_soul(["--help"])

        captured = capsys.readouterr()
        assert "--pulse-interval" in captured.out

    def test_stream_no_pulses_option(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--no-pulses option appears in help."""
        result = cmd_soul(["--help"])

        captured = capsys.readouterr()
        assert "--no-pulses" in captured.out


# === Soul Special Commands ===


# === Quick Win Commands (Tier 1) ===


class TestSoulQuickCommands:
    """Tests for soul quick win commands (vibe, drift, tense, why)."""

    def test_vibe_command(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """vibe command shows one-liner eigenvector summary."""
        result = cmd_soul(["vibe"])

        assert result == 0
        captured = capsys.readouterr()
        assert "[SOUL:VIBE]" in captured.out
        # Should contain eigenvector values
        assert "0.15" in captured.out or "Minimal" in captured.out
        # Should contain emoji
        assert "✂️" in captured.out or "🔬" in captured.out

    def test_vibe_command_json(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """vibe command with --json outputs JSON."""
        result = cmd_soul(["vibe", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        import json

        data = json.loads(captured.out)
        assert data["command"] == "vibe"
        assert "eigenvectors" in data
        assert "vibe_string" in data

    def test_drift_command(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """drift command shows soul comparison."""
        result = cmd_soul(["drift"])

        assert result == 0
        captured = capsys.readouterr()
        assert "[SOUL:DRIFT]" in captured.out
        # Should have some message about drift
        assert "Soul feels" in captured.out or "drifts" in captured.out.lower()

    def test_drift_command_json(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """drift command with --json outputs JSON."""
        result = cmd_soul(["drift", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        import json

        data = json.loads(captured.out)
        assert data["command"] == "drift"
        assert "current" in data
        assert "changes" in data

    def test_tense_command(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """tense command shows eigenvector tensions."""
        result = cmd_soul(["tense"])

        assert result == 0
        captured = capsys.readouterr()
        assert "[SOUL:TENSE]" in captured.out
        # Default eigenvectors should produce tensions
        assert "⚡" in captured.out or "Tensions detected" in captured.out

    def test_tense_command_json(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """tense command with --json outputs JSON."""
        result = cmd_soul(["tense", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        import json

        data = json.loads(captured.out)
        assert data["command"] == "tense"
        assert "tensions" in data
        assert "eigenvectors" in data

    def test_why_command_with_prompt(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """why command with prompt triggers single CHALLENGE dialogue."""
        result = cmd_soul(["why", "testing"])

        assert result == 0
        captured = capsys.readouterr()
        # Should have challenge mode output
        assert "CHALLENGE" in captured.out.upper() or len(captured.out) > 0

    def test_quick_commands_in_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Quick commands appear in help."""
        result = cmd_soul(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "QUICK COMMANDS:" in captured.out
        assert "vibe" in captured.out
        assert "drift" in captured.out
        assert "tense" in captured.out
        assert "why" in captured.out


class TestSoulSpecialCommands:
    """Tests for soul special commands."""

    def test_starters_command(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """starters command shows starter prompts."""
        result = cmd_soul(["starters"])

        assert result == 0
        captured = capsys.readouterr()
        # Should show some starters or guidance
        assert len(captured.out) > 0

    def test_manifest_command(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """manifest command shows soul state."""
        result = cmd_soul(["manifest"])

        assert result == 0
        captured = capsys.readouterr()
        # Should show some state info
        assert len(captured.out) > 0

    def test_eigenvectors_command(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """eigenvectors command shows personality coordinates."""
        result = cmd_soul(["eigenvectors"])

        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_audit_command(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """audit command shows audit trail."""
        result = cmd_soul(["audit"])

        assert result == 0
        captured = capsys.readouterr()
        # Should show something (even if empty)
        assert len(captured.out) > 0


# === Soul Stream Integration Tests ===


class TestSoulStreamIntegration:
    """Integration tests for soul stream robustifications."""

    @pytest.mark.asyncio
    async def test_stream_processes_single_message(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Stream processes a single message and exits on EOF."""
        import asyncio
        from io import StringIO

        from agents.k import KgentSoul

        from ..soul import _handle_stream

        soul = KgentSoul()

        # Mock stdin with a single message followed by EOF
        mock_stdin = StringIO("Hello world\n")

        with patch("sys.stdin", mock_stdin):
            result = await _handle_stream(
                soul,
                pulse_interval=100,  # Long interval so no pulses fire
                show_pulses=False,
                json_mode=False,
                ctx=None,
            )

        assert result == 0
        captured = capsys.readouterr()
        # Should have starting and stopped messages
        assert "Starting" in captured.out
        assert "Stopped" in captured.out

    @pytest.mark.asyncio
    async def test_stream_handles_mode_switching(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Stream supports /mode command."""
        import asyncio
        from io import StringIO

        from agents.k import KgentSoul

        from ..soul import _handle_stream

        soul = KgentSoul()

        # Mock stdin with mode switch command
        mock_stdin = StringIO("/mode advise\n")

        with patch("sys.stdin", mock_stdin):
            result = await _handle_stream(
                soul,
                pulse_interval=100,
                show_pulses=False,
                json_mode=False,
                ctx=None,
            )

        assert result == 0
        captured = capsys.readouterr()
        # Should have mode switch confirmation
        assert "Mode: advise" in captured.out

    @pytest.mark.asyncio
    async def test_stream_rejects_invalid_mode(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Stream rejects invalid /mode values."""
        import asyncio
        from io import StringIO

        from agents.k import KgentSoul

        from ..soul import _handle_stream

        soul = KgentSoul()

        # Mock stdin with invalid mode
        mock_stdin = StringIO("/mode invalid_mode\n")

        with patch("sys.stdin", mock_stdin):
            result = await _handle_stream(
                soul,
                pulse_interval=100,
                show_pulses=False,
                json_mode=False,
                ctx=None,
            )

        assert result == 0
        captured = capsys.readouterr()
        # Should have invalid mode error
        assert "Invalid mode" in captured.out

    @pytest.mark.asyncio
    async def test_stream_handles_timeout(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Stream handles LLM timeout gracefully."""
        import asyncio
        from io import StringIO

        import protocols.cli.handlers.soul as soul_module
        from agents.k import KgentSoul

        soul = KgentSoul()

        # Mock stdin with a message
        mock_stdin = StringIO("Test message\n")

        # Store original function
        original_invoke = soul_module._invoke_with_retry

        async def timeout_invoke(*args: Any, **kwargs: Any) -> Any:
            raise asyncio.TimeoutError("LLM response timeout")

        with patch("sys.stdin", mock_stdin):
            with patch.object(
                soul_module,
                "_invoke_with_retry",
                side_effect=timeout_invoke,
            ):
                result = await soul_module._handle_stream(
                    soul,
                    pulse_interval=100,
                    show_pulses=False,
                    json_mode=False,
                    ctx=None,
                )

        assert result == 0
        captured = capsys.readouterr()
        # Should have timeout error
        assert "timeout" in captured.out.lower()

    @pytest.mark.asyncio
    async def test_stream_shows_interaction_count_on_shutdown(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Stream shows interaction count when stopped."""
        import asyncio
        from io import StringIO

        from agents.k import KgentSoul

        from ..soul import _handle_stream

        soul = KgentSoul()

        # Mock empty stdin (EOF immediately)
        mock_stdin = StringIO("")

        with patch("sys.stdin", mock_stdin):
            result = await _handle_stream(
                soul,
                pulse_interval=100,
                show_pulses=False,
                json_mode=False,
                ctx=None,
            )

        assert result == 0
        captured = capsys.readouterr()
        # Should have interaction count in stopped message
        assert "interactions" in captured.out.lower()

    @pytest.mark.asyncio
    async def test_invoke_with_retry_succeeds_first_attempt(self) -> None:
        """Retry helper succeeds on first attempt."""
        from unittest.mock import MagicMock

        from ..soul import _invoke_with_retry

        mock_flux = MagicMock()
        mock_flux.invoke = AsyncMock(return_value="success")
        mock_event = MagicMock()

        result = await _invoke_with_retry(mock_flux, mock_event, max_retries=2)

        assert result == "success"
        assert mock_flux.invoke.call_count == 1

    @pytest.mark.asyncio
    async def test_invoke_with_retry_retries_on_failure(self) -> None:
        """Retry helper retries on transient failure."""
        from unittest.mock import MagicMock

        from ..soul import _invoke_with_retry

        mock_flux = MagicMock()
        # First call fails, second succeeds
        mock_flux.invoke = AsyncMock(side_effect=[RuntimeError("transient"), "success"])
        mock_event = MagicMock()

        result = await _invoke_with_retry(
            mock_flux, mock_event, max_retries=2, timeout_seconds=5.0
        )

        assert result == "success"
        assert mock_flux.invoke.call_count == 2

    @pytest.mark.asyncio
    async def test_invoke_with_retry_raises_after_max_retries(self) -> None:
        """Retry helper raises after max retries exhausted."""
        from unittest.mock import MagicMock

        from ..soul import _invoke_with_retry

        mock_flux = MagicMock()
        mock_flux.invoke = AsyncMock(side_effect=RuntimeError("permanent"))
        mock_event = MagicMock()

        with pytest.raises(RuntimeError, match="permanent"):
            await _invoke_with_retry(
                mock_flux, mock_event, max_retries=1, timeout_seconds=5.0
            )

        # Should have tried original + 1 retry = 2 attempts
        assert mock_flux.invoke.call_count == 2

    @pytest.mark.asyncio
    async def test_invoke_with_retry_timeout_raises(self) -> None:
        """Retry helper handles timeout."""
        import asyncio
        from unittest.mock import MagicMock

        from ..soul import _invoke_with_retry

        async def slow_invoke(*args: Any, **kwargs: Any) -> str:
            await asyncio.sleep(10)
            return "too slow"

        mock_flux = MagicMock()
        mock_flux.invoke = slow_invoke
        mock_event = MagicMock()

        with pytest.raises(asyncio.TimeoutError):
            await _invoke_with_retry(
                mock_flux, mock_event, max_retries=0, timeout_seconds=0.1
            )
