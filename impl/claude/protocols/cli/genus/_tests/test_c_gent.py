"""
Tests for C-gent CLI Commands (Capital/Economy).

Tests the capital balance, history, and tithe commands.
"""

from __future__ import annotations

import json
from io import StringIO
from typing import Any
from unittest.mock import patch

import pytest
from protocols.cli.genus.c_gent import (
    _deserialize_ledger,
    _render_balance,
    _render_event,
    _serialize_ledger,
    cmd_capital,
)
from shared.capital import EventSourcedLedger, LedgerEvent

# === Test Fixtures ===


@pytest.fixture
def ledger_with_events() -> EventSourcedLedger:
    """Create a ledger with some test events."""
    ledger = EventSourcedLedger()
    ledger.issue("agent-a", 0.2, "initial")
    ledger.credit("agent-a", 0.1, "good_proposal")
    ledger.credit("agent-b", 0.15, "good_proposal")
    ledger.debit("agent-a", 0.05, "bypass_used")
    return ledger


# === Serialization Tests ===


class TestSerialization:
    """Tests for ledger serialization/deserialization."""

    def test_serialize_empty_ledger(self) -> None:
        """Empty ledger serializes to empty events list."""
        ledger = EventSourcedLedger()
        data = _serialize_ledger(ledger)

        assert data["events"] == []
        assert "config" in data
        assert data["config"]["initial_capital"] == 0.5

    def test_serialize_with_events(
        self, ledger_with_events: EventSourcedLedger
    ) -> None:
        """Ledger with events serializes correctly."""
        data = _serialize_ledger(ledger_with_events)

        assert len(data["events"]) == 4
        assert data["events"][0]["event_type"] == "ISSUE"
        assert data["events"][0]["agent"] == "agent-a"

    def test_roundtrip_preserves_events(
        self, ledger_with_events: EventSourcedLedger
    ) -> None:
        """Serialization → deserialization preserves events."""
        data = _serialize_ledger(ledger_with_events)
        restored = _deserialize_ledger(data)

        assert len(restored.events) == len(ledger_with_events.events)
        assert restored.balance("agent-a") == ledger_with_events.balance("agent-a")
        assert restored.balance("agent-b") == ledger_with_events.balance("agent-b")

    def test_roundtrip_preserves_config(self) -> None:
        """Custom config is preserved through roundtrip."""
        ledger = EventSourcedLedger(
            initial_capital=0.3, max_capital=0.8, decay_rate=0.02
        )
        data = _serialize_ledger(ledger)
        restored = _deserialize_ledger(data)

        assert restored.initial_capital == 0.3
        assert restored.max_capital == 0.8
        assert restored.decay_rate == 0.02


# === Command Tests ===


class TestBalanceCommand:
    """Tests for kgents capital balance."""

    def test_balance_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        """--help shows documentation."""
        result = cmd_capital(["balance", "--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "balance" in captured.out.lower()

    def test_balance_empty_ledger(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Empty ledger shows appropriate message."""
        with patch("protocols.cli.genus.c_gent._get_ledger") as mock:
            mock.return_value = EventSourcedLedger()
            result = cmd_capital(["balance"])

        assert result == 0
        captured = capsys.readouterr()
        assert "No agents" in captured.out

    def test_balance_shows_all_agents(
        self, ledger_with_events: EventSourcedLedger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Balance shows all agents when no agent specified."""
        with patch("protocols.cli.genus.c_gent._get_ledger") as mock:
            mock.return_value = ledger_with_events
            result = cmd_capital(["balance"])

        assert result == 0
        captured = capsys.readouterr()
        assert "agent-a" in captured.out
        assert "agent-b" in captured.out

    def test_balance_single_agent(
        self, ledger_with_events: EventSourcedLedger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Balance shows single agent when specified."""
        with patch("protocols.cli.genus.c_gent._get_ledger") as mock:
            mock.return_value = ledger_with_events
            result = cmd_capital(["balance", "agent-a"])

        assert result == 0
        captured = capsys.readouterr()
        assert "agent-a" in captured.out

    def test_balance_json_mode(
        self, ledger_with_events: EventSourcedLedger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--json outputs valid JSON."""
        with patch("protocols.cli.genus.c_gent._get_ledger") as mock:
            mock.return_value = ledger_with_events
            result = cmd_capital(["balance", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "agents" in data
        assert "agent-a" in data["agents"]


class TestHistoryCommand:
    """Tests for kgents capital history."""

    def test_history_empty_ledger(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Empty ledger shows appropriate message."""
        with patch("protocols.cli.genus.c_gent._get_ledger") as mock:
            mock.return_value = EventSourcedLedger()
            result = cmd_capital(["history"])

        assert result == 0
        captured = capsys.readouterr()
        assert "No events" in captured.out

    def test_history_shows_events(
        self, ledger_with_events: EventSourcedLedger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """History shows ledger events."""
        with patch("protocols.cli.genus.c_gent._get_ledger") as mock:
            mock.return_value = ledger_with_events
            result = cmd_capital(["history"])

        assert result == 0
        captured = capsys.readouterr()
        assert "ISSUE" in captured.out
        assert "CREDIT" in captured.out

    def test_history_filter_by_agent(
        self, ledger_with_events: EventSourcedLedger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """History filters by agent when specified."""
        with patch("protocols.cli.genus.c_gent._get_ledger") as mock:
            mock.return_value = ledger_with_events
            result = cmd_capital(["history", "agent-a"])

        assert result == 0
        captured = capsys.readouterr()
        assert "agent-a" in captured.out
        # agent-b should not appear (only agent-a events)
        lines = [l for l in captured.out.split("\n") if "agent-" in l]
        for line in lines:
            assert "agent-a" in line

    def test_history_json_mode(
        self, ledger_with_events: EventSourcedLedger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--json outputs valid JSON with events."""
        with patch("protocols.cli.genus.c_gent._get_ledger") as mock:
            mock.return_value = ledger_with_events
            result = cmd_capital(["history", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "events" in data
        assert len(data["events"]) == 4

    def test_history_limit_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """--limit N restricts output."""
        import protocols.cli.genus.c_gent as c_gent_module

        # Create a ledger with more than 2 events
        ledger = EventSourcedLedger()
        for i in range(5):
            ledger.credit(f"agent-{i}", 0.1, f"test-{i}")

        # Reset the global ledger and mock _get_ledger
        old_ledger = c_gent_module._LEDGER
        c_gent_module._LEDGER = ledger
        try:
            result = cmd_capital(["history", "--limit", "2", "--json"])
        finally:
            c_gent_module._LEDGER = old_ledger

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data["events"]) == 2


class TestTitheCommand:
    """Tests for kgents capital tithe."""

    def test_tithe_requires_amount(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Tithe requires amount argument."""
        result = cmd_capital(["tithe"])

        assert result == 1
        captured = capsys.readouterr()
        assert "requires" in captured.out.lower()

    def test_tithe_invalid_amount(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Invalid amount shows error."""
        result = cmd_capital(["tithe", "not-a-number"])

        assert result == 1
        captured = capsys.readouterr()
        assert "invalid" in captured.out.lower()

    def test_tithe_insufficient_capital(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Tithe fails if insufficient capital."""
        ledger = EventSourcedLedger()
        # Default agent has 0.5 initial capital
        with (
            patch("protocols.cli.genus.c_gent._get_ledger") as mock_get,
            patch("protocols.cli.genus.c_gent._save_ledger"),
        ):
            mock_get.return_value = ledger
            result = cmd_capital(["tithe", "10.0"])  # More than balance

        assert result == 1
        captured = capsys.readouterr()
        assert "insufficient" in captured.out.lower()

    def test_tithe_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Successful tithe shows confirmation."""
        ledger = EventSourcedLedger()
        ledger.issue("default", 0.3, "test")  # Give some capital

        with (
            patch("protocols.cli.genus.c_gent._get_ledger") as mock_get,
            patch("protocols.cli.genus.c_gent._save_ledger"),
        ):
            mock_get.return_value = ledger
            result = cmd_capital(["tithe", "0.1"])

        assert result == 0
        captured = capsys.readouterr()
        assert "complete" in captured.out.lower() or "✓" in captured.out

    def test_tithe_json_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Successful tithe in JSON mode."""
        ledger = EventSourcedLedger()
        ledger.issue("default", 0.3, "test")

        with (
            patch("protocols.cli.genus.c_gent._get_ledger") as mock_get,
            patch("protocols.cli.genus.c_gent._save_ledger"),
        ):
            mock_get.return_value = ledger
            result = cmd_capital(["tithe", "0.1", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["success"] is True
        assert data["amount_tithed"] == 0.1

    def test_tithe_with_agent_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """--agent flag specifies which agent to tithe from."""
        ledger = EventSourcedLedger()
        ledger.issue("custom-agent", 0.5, "test")

        with (
            patch("protocols.cli.genus.c_gent._get_ledger") as mock_get,
            patch("protocols.cli.genus.c_gent._save_ledger"),
        ):
            mock_get.return_value = ledger
            result = cmd_capital(["tithe", "0.1", "--agent", "custom-agent", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["agent"] == "custom-agent"


class TestUnknownSubcommand:
    """Tests for unknown subcommands."""

    def test_unknown_subcommand(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Unknown subcommand shows error."""
        result = cmd_capital(["unknown"])

        assert result == 1
        captured = capsys.readouterr()
        assert "unknown" in captured.out.lower()


# === Rendering Tests ===


class TestRendering:
    """Tests for output rendering helpers."""

    def test_render_balance_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Balance renders with bar and value."""
        _render_balance("test-agent", 0.75)

        captured = capsys.readouterr()
        assert "test-agent" in captured.out
        assert "0.75" in captured.out
        # Should have some bar characters
        assert "█" in captured.out or "░" in captured.out

    def test_render_event_credit(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Credit event renders with + sign."""
        from datetime import UTC, datetime

        event = LedgerEvent(
            event_type="CREDIT",
            agent="test",
            amount=0.1,
            timestamp=datetime.now(UTC),
            metadata={"reason": "good_proposal"},
        )
        _render_event(event)

        captured = capsys.readouterr()
        assert "+" in captured.out
        assert "CREDIT" in captured.out

    def test_render_event_debit(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Debit event renders with - sign."""
        from datetime import UTC, datetime

        event = LedgerEvent(
            event_type="DEBIT",
            agent="test",
            amount=0.05,
            timestamp=datetime.now(UTC),
            metadata={"reason": "bypass_used"},
        )
        _render_event(event)

        captured = capsys.readouterr()
        assert "-" in captured.out
        assert "DEBIT" in captured.out
