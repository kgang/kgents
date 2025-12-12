"""
Tests for tithe CLI handler.

Verifies:
- Basic tithe operation
- Amount parameter parsing
- Status mode
- Error handling when metabolism unavailable
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import MagicMock, patch

import pytest

from ..tithe import _emit_output, _format_status, cmd_tithe

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


class MockInvocationContext:
    """Mock InvocationContext for testing."""

    def __init__(self) -> None:
        self.outputs: list[tuple[str, dict[str, Any]]] = []

    def output(self, human: str, semantic: dict[str, Any]) -> None:
        self.outputs.append((human, semantic))


class MockMetabolicEngine:
    """Mock metabolic engine for testing."""

    def __init__(
        self,
        tithe_result: dict[str, Any] | None = None,
        status_result: dict[str, Any] | None = None,
    ) -> None:
        self._tithe_result = tithe_result or {
            "discharged": 0.1,
            "remaining_pressure": 0.35,
            "gratitude": "The river flows.",
        }
        self._status_result = status_result or {
            "pressure": 0.45,
            "critical_threshold": 1.0,
            "temperature": 0.8,
            "in_fever": False,
        }
        self.tithe_called = False
        self.status_called = False

    def tithe(self, amount: float = 0.1) -> dict[str, Any]:
        self.tithe_called = True
        return self._tithe_result

    def status(self) -> dict[str, Any]:
        self.status_called = True
        return self._status_result


class TestCmdTithe:
    """Tests for cmd_tithe synchronous entry point."""

    def test_help_flag(self) -> None:
        """--help shows documentation."""
        result = cmd_tithe(["--help"])
        assert result == 0

    def test_h_flag(self) -> None:
        """-h shows documentation."""
        result = cmd_tithe(["-h"])
        assert result == 0

    def test_invalid_amount_returns_error(self) -> None:
        """Invalid amount returns error code."""
        ctx = MockInvocationContext()
        result = cmd_tithe(["--amount=invalid"], cast("InvocationContext", ctx))

        assert result == 1
        assert len(ctx.outputs) == 1
        assert "Invalid amount" in ctx.outputs[0][0]


class TestTitheIntegration:
    """Integration tests for tithe command with mock engine."""

    def test_tithe_success(self) -> None:
        """Successful tithe returns 0."""
        ctx = MockInvocationContext()
        mock_engine = MockMetabolicEngine()

        # Create mock module
        mock_module = MagicMock()
        mock_module.get_metabolic_engine = lambda: mock_engine

        with patch.dict(sys.modules, {"protocols.agentese.metabolism": mock_module}):
            result = cmd_tithe([], cast("InvocationContext", ctx))

        assert result == 0
        assert mock_engine.tithe_called
        assert len(ctx.outputs) == 1
        human, semantic = ctx.outputs[0]
        assert "Discharged: 0.10" in human

    def test_tithe_with_amount(self) -> None:
        """Tithe with custom amount works."""
        ctx = MockInvocationContext()
        mock_engine = MockMetabolicEngine()

        mock_module = MagicMock()
        mock_module.get_metabolic_engine = lambda: mock_engine

        with patch.dict(sys.modules, {"protocols.agentese.metabolism": mock_module}):
            result = cmd_tithe(["--amount=0.3"], cast("InvocationContext", ctx))

        assert result == 0

    def test_tithe_status_mode(self) -> None:
        """--status mode shows status without tithing."""
        ctx = MockInvocationContext()
        mock_engine = MockMetabolicEngine()

        mock_module = MagicMock()
        mock_module.get_metabolic_engine = lambda: mock_engine

        with patch.dict(sys.modules, {"protocols.agentese.metabolism": mock_module}):
            result = cmd_tithe(["--status"], cast("InvocationContext", ctx))

        assert result == 0
        assert mock_engine.status_called
        assert not mock_engine.tithe_called

    def test_tithe_import_error(self) -> None:
        """ImportError returns 1 with helpful message."""
        ctx = MockInvocationContext()

        # Remove the module to trigger import error
        with patch.dict(sys.modules, {"protocols.agentese.metabolism": None}):
            result = cmd_tithe([], cast("InvocationContext", ctx))

        assert result == 1
        assert len(ctx.outputs) == 1
        assert "not available" in ctx.outputs[0][0]


class TestFormatStatus:
    """Tests for _format_status helper."""

    def test_normal_status(self) -> None:
        """Formats normal (non-fever) status correctly."""
        status = {
            "pressure": 0.45,
            "critical_threshold": 1.0,
            "temperature": 0.7,
            "in_fever": False,
        }

        result = _format_status(status)

        assert "normal" in result
        assert "Pressure: 0.45" in result
        assert "45%" in result
        assert "Temperature: 0.70" in result

    def test_fever_status(self) -> None:
        """Formats fever status correctly."""
        status = {
            "pressure": 0.95,
            "critical_threshold": 1.0,
            "temperature": 1.4,
            "in_fever": True,
        }

        result = _format_status(status)

        assert "FEVER" in result
        assert "95%" in result

    def test_zero_threshold(self) -> None:
        """Handles zero threshold without division error."""
        status = {
            "pressure": 0.5,
            "critical_threshold": 0,
            "temperature": 0.8,
            "in_fever": False,
        }

        result = _format_status(status)

        # Should not raise, percentage should be 0
        assert "0%" in result


class TestEmitOutput:
    """Tests for _emit_output dual-channel output."""

    def test_with_context(self) -> None:
        """With context, outputs via context.output()."""
        ctx = MockInvocationContext()

        _emit_output("human text", {"key": "value"}, cast("InvocationContext", ctx))

        assert len(ctx.outputs) == 1
        assert ctx.outputs[0] == ("human text", {"key": "value"})

    def test_without_context(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Without context, prints to stdout."""
        _emit_output("human text", {"key": "value"}, None)

        captured = capsys.readouterr()
        assert "human text" in captured.out
