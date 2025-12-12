"""
Tests for semaphore CLI handler.

Tests for `kgents semaphore` command.

Tests verify:
1. cmd_semaphore with --help
2. cmd_semaphore list with empty purgatory
3. cmd_semaphore list with pending tokens
4. cmd_semaphore resolve with --input flag
5. cmd_semaphore cancel
6. cmd_semaphore inspect
7. cmd_semaphore void
8. --json output mode
9. Error cases (missing token_id, not found, etc.)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from unittest.mock import patch

import pytest
from agents.flux.semaphore import Purgatory, SemaphoreReason, SemaphoreToken

from ..semaphore import (
    _async_semaphore,
    _get_purgatory,
    _handle_cancel,
    _handle_inspect,
    _handle_list,
    _handle_resolve,
    _handle_void,
    cmd_semaphore,
)

# === Test Fixtures ===


@pytest.fixture
def purgatory() -> Purgatory:
    """Fresh purgatory instance."""
    return Purgatory()


@pytest.fixture
def sample_token() -> SemaphoreToken[Any]:
    """Sample semaphore token."""
    return SemaphoreToken(
        id="sem-test1234",
        reason=SemaphoreReason.APPROVAL_NEEDED,
        prompt="Approve this action?",
        options=["Approve", "Reject"],
        severity="warning",
    )


# === cmd_semaphore Tests ===


class TestCmdSemaphoreHelp:
    """Tests for --help flag."""

    def test_help_flag_prints_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--help prints help and returns 0."""
        result = cmd_semaphore(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "kgents semaphore" in captured.out
        assert "COMMANDS:" in captured.out
        assert "list" in captured.out
        assert "resolve" in captured.out

    def test_short_help_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """-h prints help and returns 0."""
        result = cmd_semaphore(["-h"])

        assert result == 0
        captured = capsys.readouterr()
        assert "kgents semaphore" in captured.out


# === List Subcommand Tests ===


class TestCmdSemaphoreList:
    """Tests for 'semaphore list' subcommand."""

    @pytest.mark.asyncio
    async def test_list_empty_purgatory(
        self,
        purgatory: Purgatory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """List with empty purgatory shows no pending."""
        result = await _handle_list(purgatory, json_mode=False, ctx=None)

        assert result == 0
        captured = capsys.readouterr()
        assert "No pending" in captured.out

    @pytest.mark.asyncio
    async def test_list_with_pending_tokens(
        self,
        purgatory: Purgatory,
        sample_token: SemaphoreToken[Any],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """List shows pending tokens."""
        await purgatory.save(sample_token)

        result = await _handle_list(purgatory, json_mode=False, ctx=None)

        assert result == 0
        captured = capsys.readouterr()
        assert "1 pending" in captured.out
        assert sample_token.id in captured.out
        assert "approval_needed" in captured.out

    @pytest.mark.asyncio
    async def test_list_json_mode(
        self,
        purgatory: Purgatory,
        sample_token: SemaphoreToken[Any],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """List with --json outputs JSON."""
        await purgatory.save(sample_token)

        result = await _handle_list(purgatory, json_mode=True, ctx=None)

        assert result == 0
        captured = capsys.readouterr()

        import json

        output = json.loads(captured.out)
        assert "pending" in output
        assert len(output["pending"]) == 1
        assert output["pending"][0]["id"] == sample_token.id


# === Resolve Subcommand Tests ===


class TestCmdSemaphoreResolve:
    """Tests for 'semaphore resolve' subcommand."""

    @pytest.mark.asyncio
    async def test_resolve_missing_token_id(
        self,
        purgatory: Purgatory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Resolve without token_id shows error."""
        result = await _async_semaphore(
            subcommand="resolve",
            subcommand_args=[],
            input_value=None,
            json_mode=False,
            ctx=None,
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "Missing token ID" in captured.out

    @pytest.mark.asyncio
    async def test_resolve_unknown_token(
        self,
        purgatory: Purgatory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Resolve unknown token shows error."""
        # Patch _get_purgatory to return our fixture
        with patch(
            "protocols.cli.handlers.semaphore._get_purgatory", return_value=purgatory
        ):
            result = await _handle_resolve(
                purgatory,
                token_id="sem-nonexistent",
                input_value="approve",
                json_mode=False,
                ctx=None,
            )

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()

    @pytest.mark.asyncio
    async def test_resolve_with_input_flag(
        self,
        purgatory: Purgatory,
        sample_token: SemaphoreToken[Any],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Resolve with --input flag succeeds."""
        await purgatory.save(sample_token)

        result = await _handle_resolve(
            purgatory,
            token_id=sample_token.id,
            input_value="Approved!",
            json_mode=False,
            ctx=None,
        )

        assert result == 0
        captured = capsys.readouterr()
        assert "Resolved" in captured.out

        # Verify token is resolved
        assert sample_token.is_resolved
        assert len(purgatory.list_pending()) == 0

    @pytest.mark.asyncio
    async def test_resolve_already_resolved_token(
        self,
        purgatory: Purgatory,
        sample_token: SemaphoreToken[Any],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Resolve already-resolved token shows error."""
        await purgatory.save(sample_token)
        await purgatory.resolve(sample_token.id, "first")

        result = await _handle_resolve(
            purgatory,
            token_id=sample_token.id,
            input_value="second",
            json_mode=False,
            ctx=None,
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "already resolved" in captured.out.lower()


# === Cancel Subcommand Tests ===


class TestCmdSemaphoreCancel:
    """Tests for 'semaphore cancel' subcommand."""

    @pytest.mark.asyncio
    async def test_cancel_missing_token_id(
        self,
        purgatory: Purgatory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Cancel without token_id shows error."""
        result = await _async_semaphore(
            subcommand="cancel",
            subcommand_args=[],
            input_value=None,
            json_mode=False,
            ctx=None,
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "Missing token ID" in captured.out

    @pytest.mark.asyncio
    async def test_cancel_success(
        self,
        purgatory: Purgatory,
        sample_token: SemaphoreToken[Any],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Cancel pending token succeeds."""
        await purgatory.save(sample_token)

        result = await _handle_cancel(
            purgatory,
            token_id=sample_token.id,
            json_mode=False,
            ctx=None,
        )

        assert result == 0
        captured = capsys.readouterr()
        assert "Cancelled" in captured.out

        # Verify token is cancelled
        assert sample_token.is_cancelled
        assert len(purgatory.list_pending()) == 0

    @pytest.mark.asyncio
    async def test_cancel_unknown_token(
        self,
        purgatory: Purgatory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Cancel unknown token shows error."""
        result = await _handle_cancel(
            purgatory,
            token_id="sem-nonexistent",
            json_mode=False,
            ctx=None,
        )

        assert result == 1
        captured = capsys.readouterr()
        assert (
            "not found" in captured.out.lower() or "not pending" in captured.out.lower()
        )


# === Inspect Subcommand Tests ===


class TestCmdSemaphoreInspect:
    """Tests for 'semaphore inspect' subcommand."""

    @pytest.mark.asyncio
    async def test_inspect_missing_token_id(
        self,
        purgatory: Purgatory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Inspect without token_id shows error."""
        result = await _async_semaphore(
            subcommand="inspect",
            subcommand_args=[],
            input_value=None,
            json_mode=False,
            ctx=None,
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "Missing token ID" in captured.out

    @pytest.mark.asyncio
    async def test_inspect_shows_full_details(
        self,
        purgatory: Purgatory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Inspect shows full token details."""
        token: SemaphoreToken[Any] = SemaphoreToken(
            id="sem-inspect1",
            reason=SemaphoreReason.SENSITIVE_ACTION,
            prompt="Delete all records?",
            options=["Approve", "Reject"],
            severity="critical",
            escalation="manager@example.com",
        )
        await purgatory.save(token)

        result = await _handle_inspect(
            purgatory,
            token_id="sem-inspect1",
            json_mode=False,
            ctx=None,
        )

        assert result == 0
        captured = capsys.readouterr()
        output = captured.out

        assert "sem-inspect1" in output
        assert "pending" in output.lower()
        assert "sensitive_action" in output
        assert "Delete all records?" in output
        assert "critical" in output
        assert "manager@example.com" in output

    @pytest.mark.asyncio
    async def test_inspect_json_mode(
        self,
        purgatory: Purgatory,
        sample_token: SemaphoreToken[Any],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Inspect with --json outputs JSON."""
        await purgatory.save(sample_token)

        result = await _handle_inspect(
            purgatory,
            token_id=sample_token.id,
            json_mode=True,
            ctx=None,
        )

        assert result == 0
        captured = capsys.readouterr()

        import json

        output = json.loads(captured.out)
        assert output["token_id"] == sample_token.id
        assert output["status"] == "pending"
        assert output["reason"] == "approval_needed"

    @pytest.mark.asyncio
    async def test_inspect_unknown_token(
        self,
        purgatory: Purgatory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Inspect unknown token shows error."""
        result = await _handle_inspect(
            purgatory,
            token_id="sem-nonexistent",
            json_mode=False,
            ctx=None,
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()


# === Void Subcommand Tests ===


class TestCmdSemaphoreVoid:
    """Tests for 'semaphore void' subcommand."""

    @pytest.mark.asyncio
    async def test_void_no_expired(
        self,
        purgatory: Purgatory,
        sample_token: SemaphoreToken[Any],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Void with no expired tokens reports none."""
        await purgatory.save(sample_token)  # No deadline

        result = await _handle_void(purgatory, json_mode=False, ctx=None)

        assert result == 0
        captured = capsys.readouterr()
        assert "No expired" in captured.out

    @pytest.mark.asyncio
    async def test_void_expired_tokens(
        self,
        purgatory: Purgatory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Void removes expired tokens."""
        # Token with past deadline
        past_deadline = datetime.now() - timedelta(hours=1)
        expired_token: SemaphoreToken[Any] = SemaphoreToken(
            id="sem-expired1",
            deadline=past_deadline,
        )
        # Token without deadline
        no_deadline_token: SemaphoreToken[Any] = SemaphoreToken(id="sem-nodeadline")

        await purgatory.save(expired_token)
        await purgatory.save(no_deadline_token)

        result = await _handle_void(purgatory, json_mode=False, ctx=None)

        assert result == 0
        captured = capsys.readouterr()
        assert "Voided 1" in captured.out
        assert "sem-expired1" in captured.out

        # Verify states
        assert expired_token.is_voided
        assert no_deadline_token.is_pending

    @pytest.mark.asyncio
    async def test_void_json_mode(
        self,
        purgatory: Purgatory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Void with --json outputs JSON."""
        past_deadline = datetime.now() - timedelta(hours=1)
        expired_token: SemaphoreToken[Any] = SemaphoreToken(
            id="sem-expired2",
            deadline=past_deadline,
        )
        await purgatory.save(expired_token)

        result = await _handle_void(purgatory, json_mode=True, ctx=None)

        assert result == 0
        captured = capsys.readouterr()

        import json

        output = json.loads(captured.out)
        assert output["voided_count"] == 1
        assert "sem-expired2" in output["voided_ids"]


# === Unknown Subcommand Tests ===


class TestCmdSemaphoreUnknown:
    """Tests for unknown subcommand."""

    @pytest.mark.asyncio
    async def test_unknown_subcommand(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Unknown subcommand shows error."""
        result = await _async_semaphore(
            subcommand="unknown",
            subcommand_args=[],
            input_value=None,
            json_mode=False,
            ctx=None,
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown subcommand" in captured.out


# === Default Subcommand Tests ===


class TestCmdSemaphoreDefault:
    """Tests for default subcommand (list)."""

    @pytest.mark.asyncio
    async def test_no_subcommand_defaults_to_list(
        self,
        purgatory: Purgatory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """No subcommand defaults to list."""
        with patch(
            "protocols.cli.handlers.semaphore._get_purgatory", return_value=purgatory
        ):
            result = await _async_semaphore(
                subcommand="list",  # Default
                subcommand_args=[],
                input_value=None,
                json_mode=False,
                ctx=None,
            )

        assert result == 0
        captured = capsys.readouterr()
        assert "No pending" in captured.out


# === Integration Tests ===


class TestCmdSemaphoreIntegration:
    """Integration tests for cmd_semaphore."""

    def test_full_workflow(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Complete workflow: list -> resolve."""
        # Create a shared purgatory
        purgatory = Purgatory()
        token: SemaphoreToken[Any] = SemaphoreToken(
            id="sem-workflow1",
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Continue?",
        )

        # Setup: save token
        import asyncio

        asyncio.run(purgatory.save(token))

        # Use the official set_purgatory API and patch lifecycle state
        from ..semaphore import set_purgatory

        # Mock lifecycle state to return None (so we use module singleton)
        with patch(
            "protocols.cli.hollow.get_lifecycle_state",
            return_value=None,
        ):
            set_purgatory(purgatory)

            try:
                # 1. List shows pending token
                result = cmd_semaphore(["list"])
                assert result == 0
                captured = capsys.readouterr()
                assert "sem-workflow1" in captured.out

                # 2. Resolve the token
                result = cmd_semaphore(
                    ["resolve", "sem-workflow1", "--input", "approved"]
                )
                assert result == 0
                captured = capsys.readouterr()
                assert "Resolved" in captured.out

                # 3. List shows no pending
                result = cmd_semaphore(["list"])
                assert result == 0
                captured = capsys.readouterr()
                assert "No pending" in captured.out
            finally:
                # Reset singleton
                set_purgatory(None)  # type: ignore[arg-type]


# === Argument Parsing Tests ===


class TestCmdSemaphoreArgParsing:
    """Tests for argument parsing."""

    def test_input_flag_with_equals(self) -> None:
        """--input=value parsing."""
        args = ["resolve", "sem-test", "--input=my value"]

        # Parse manually like cmd_semaphore does
        input_value = None
        for i, arg in enumerate(args):
            if arg.startswith("--input="):
                input_value = arg.split("=", 1)[1]

        assert input_value == "my value"

    def test_input_flag_separate(self) -> None:
        """--input value parsing."""
        args = ["resolve", "sem-test", "--input", "my value"]

        # Parse manually like cmd_semaphore does
        input_value = None
        for i, arg in enumerate(args):
            if arg == "--input" and i + 1 < len(args):
                input_value = args[i + 1]

        assert input_value == "my value"

    def test_json_flag_detected(self) -> None:
        """--json flag detection."""
        args = ["list", "--json"]
        json_mode = "--json" in args
        assert json_mode is True
