"""
C-gent CLI Commands - Capital/Economy operations.

AGENTESE Context: void.capital.*

Commands:
    kgents capital balance [agent]    # Show capital balance
    kgents capital history [agent]    # Show ledger event history
    kgents capital tithe <amount>     # Voluntary discharge (potlatch)

This module provides power-user access to the capital system.
See: shared/capital.py for the EventSourcedLedger implementation.
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from typing import Any


def cmd_capital(args: list[str]) -> int:
    """
    C-gent Capital CLI handler.

    Usage:
        kgents capital balance [agent]    # Show balance(s)
        kgents capital history [agent]    # Show event history
        kgents capital tithe <amount>     # Potlatch (voluntary discharge)
        kgents capital --json             # JSON output
        kgents capital --help             # This help
    """
    # Parse args
    help_mode = "--help" in args or "-h" in args
    json_mode = "--json" in args

    # Extract --limit and --agent values
    limit = 20
    agent_flag: str | None = None
    skip_next = False
    positional: list[str] = []

    for i, a in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if a == "--limit" and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
                skip_next = True
            except ValueError:
                pass
        elif a == "--agent" and i + 1 < len(args):
            agent_flag = args[i + 1]
            skip_next = True
        elif not a.startswith("-"):
            positional.append(a)

    if help_mode:
        print(__doc__)
        return 0

    # Determine subcommand
    subcommand = positional[0] if positional else "balance"

    if subcommand == "balance":
        agent = positional[1] if len(positional) > 1 else None
        return asyncio.run(_async_balance(agent, json_mode))
    elif subcommand == "history":
        agent = positional[1] if len(positional) > 1 else None
        return asyncio.run(_async_history(agent, limit, json_mode))
    elif subcommand == "tithe":
        if len(positional) < 2:
            print("Error: tithe requires <amount> argument")
            print("Usage: kgents capital tithe <amount> [--agent <name>]")
            return 1
        try:
            amount = float(positional[1])
        except ValueError:
            print(f"Error: invalid amount '{positional[1]}'")
            return 1
        agent = agent_flag or "default"
        return asyncio.run(_async_tithe(agent, amount, json_mode))
    else:
        print(f"Unknown subcommand: {subcommand}")
        print("Valid subcommands: balance, history, tithe")
        return 1


# === Async Implementations ===


async def _async_balance(agent: str | None, json_mode: bool) -> int:
    """Show capital balance(s)."""
    ledger = _get_ledger()

    if agent:
        # Single agent balance
        balance = ledger.balance(agent)
        if json_mode:
            print(json.dumps({"agent": agent, "balance": balance}, indent=2))
        else:
            _render_balance(agent, balance)
    else:
        # All agents
        agents = ledger.agents()
        if not agents:
            if json_mode:
                print(
                    json.dumps(
                        {"agents": [], "message": "No agents in ledger"}, indent=2
                    )
                )
            else:
                print("[CAPITAL] No agents in ledger")
                print("         Agents appear when they interact with TrustGate")
            return 0

        if json_mode:
            balances = {a: ledger.balance(a) for a in sorted(agents)}
            print(json.dumps({"agents": balances}, indent=2))
        else:
            print("[CAPITAL] Agent Balances")
            print("─" * 40)
            for a in sorted(agents):
                _render_balance(a, ledger.balance(a))

    return 0


async def _async_history(agent: str | None, limit: int, json_mode: bool) -> int:
    """Show ledger event history."""
    ledger = _get_ledger()
    events = ledger.witness(agent=agent, limit=limit)

    if not events:
        if json_mode:
            print(
                json.dumps({"events": [], "message": "No events in ledger"}, indent=2)
            )
        else:
            agent_str = f" for {agent}" if agent else ""
            print(f"[CAPITAL] No events{agent_str}")
        return 0

    if json_mode:
        event_dicts = [
            {
                "type": e.event_type,
                "agent": e.agent,
                "amount": e.amount,
                "timestamp": e.timestamp.isoformat(),
                "correlation_id": e.correlation_id,
                "metadata": e.metadata,
            }
            for e in events
        ]
        print(json.dumps({"events": event_dicts, "count": len(events)}, indent=2))
    else:
        agent_str = f" ({agent})" if agent else ""
        print(f"[CAPITAL] Event History{agent_str} (last {len(events)})")
        print("─" * 60)
        for e in events:
            _render_event(e)

    return 0


async def _async_tithe(agent: str, amount: float, json_mode: bool) -> int:
    """Perform potlatch (voluntary discharge)."""
    ledger = _get_ledger()

    # Check current balance
    current = ledger.balance(agent)
    if current < amount:
        if json_mode:
            print(
                json.dumps(
                    {
                        "success": False,
                        "error": "insufficient_capital",
                        "agent": agent,
                        "required": amount,
                        "available": current,
                    },
                    indent=2,
                )
            )
        else:
            print("[CAPITAL] ✗ Insufficient capital for tithe")
            print(f"          Agent: {agent}")
            print(f"          Required: {amount:.3f}")
            print(f"          Available: {current:.3f}")
        return 1

    # Perform potlatch
    event = ledger.potlatch(agent, amount)
    if event is None:
        # Race condition (shouldn't happen in single-threaded CLI)
        if json_mode:
            print(json.dumps({"success": False, "error": "potlatch_failed"}, indent=2))
        else:
            print("[CAPITAL] ✗ Potlatch failed")
        return 1

    # Persist the ledger after mutation
    _save_ledger(ledger)

    new_balance = ledger.balance(agent)
    if json_mode:
        print(
            json.dumps(
                {
                    "success": True,
                    "agent": agent,
                    "amount_tithed": amount,
                    "new_balance": new_balance,
                    "correlation_id": event.correlation_id,
                },
                indent=2,
            )
        )
    else:
        print("[CAPITAL] ✓ Potlatch complete (Accursed Share)")
        print(f"          Agent: {agent}")
        print(f"          Tithed: {amount:.3f}")
        print(f"          New balance: {new_balance:.3f}")
        print(f"          Correlation: {event.correlation_id[:8]}...")

    return 0


# === Rendering Helpers ===


def _render_balance(agent: str, balance: float) -> None:
    """Render a single agent's balance."""
    bar_width = 20
    filled = int(balance * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"  {agent:20} [{bar}] {balance:.3f}")


def _render_event(event: Any) -> None:
    """Render a single ledger event."""
    from shared.capital import LedgerEvent

    e: LedgerEvent = event
    # Color-code by event type
    type_symbols = {
        "ISSUE": "⊕",
        "CREDIT": "+",
        "DEBIT": "-",
        "BYPASS": "⚡",
        "DECAY": "↓",
        "POTLATCH": "🔥",
    }
    symbol = type_symbols.get(e.event_type, "?")

    # Format timestamp
    ts = e.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # Format amount with sign
    if e.is_credit():
        amount_str = f"+{e.amount:.3f}"
    else:
        amount_str = f"-{e.amount:.3f}"

    # Get reason from metadata
    reason = e.metadata.get("reason", e.metadata.get("ritual", ""))

    print(f"  {symbol} {e.event_type:8} {amount_str:>8}  {e.agent:15} {reason:20} {ts}")


# === Ledger Access ===

# Global ledger instance (loaded lazily)
_LEDGER: Any = None


def _get_ledger() -> Any:
    """
    Get the capital ledger instance.

    Uses the Store Comonad persistence layer when available,
    falls back to in-memory with Ghost cache.
    """
    global _LEDGER

    if _LEDGER is not None:
        return _LEDGER

    from shared.capital import EventSourcedLedger

    # Try to load from Ghost cache
    ledger_data = _load_from_ghost()
    if ledger_data:
        _LEDGER = _deserialize_ledger(ledger_data)
    else:
        _LEDGER = EventSourcedLedger()

    return _LEDGER


def _save_ledger(ledger: Any) -> None:
    """Persist ledger to Ghost cache."""
    _save_to_ghost(_serialize_ledger(ledger))


def _serialize_ledger(ledger: Any) -> dict[str, Any]:
    """Serialize ledger to JSON-compatible dict."""
    return {
        "events": [
            {
                "event_type": e.event_type,
                "agent": e.agent,
                "amount": e.amount,
                "timestamp": e.timestamp.isoformat(),
                "correlation_id": e.correlation_id,
                "metadata": e.metadata,
            }
            for e in ledger.events
        ],
        "config": {
            "initial_capital": ledger.initial_capital,
            "max_capital": ledger.max_capital,
            "decay_rate": ledger.decay_rate,
        },
    }


def _deserialize_ledger(data: dict[str, Any]) -> Any:
    """Deserialize ledger from JSON-compatible dict."""
    from shared.capital import EventSourcedLedger, LedgerEvent

    config = data.get("config", {})
    ledger = EventSourcedLedger(
        initial_capital=config.get("initial_capital", 0.5),
        max_capital=config.get("max_capital", 1.0),
        decay_rate=config.get("decay_rate", 0.01),
    )

    # Replay events
    for e_data in data.get("events", []):
        event = LedgerEvent(
            event_type=e_data["event_type"],
            agent=e_data["agent"],
            amount=e_data["amount"],
            timestamp=datetime.fromisoformat(e_data["timestamp"]),
            correlation_id=e_data["correlation_id"],
            metadata=e_data.get("metadata", {}),
        )
        ledger._append(event)

    return ledger


def _load_from_ghost() -> dict[str, Any] | None:
    """Load ledger from Ghost cache."""
    from pathlib import Path

    ghost_path = Path.home() / ".kgents" / "ghost" / "capital.json"
    if not ghost_path.exists():
        return None

    try:
        with open(ghost_path, "r") as f:
            data: dict[str, Any] = json.load(f)
            return data
    except (json.JSONDecodeError, OSError):
        return None


def _save_to_ghost(data: dict[str, Any]) -> None:
    """Save ledger to Ghost cache."""
    from pathlib import Path

    ghost_dir = Path.home() / ".kgents" / "ghost"
    ghost_dir.mkdir(parents=True, exist_ok=True)
    ghost_path = ghost_dir / "capital.json"

    try:
        with open(ghost_path, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass  # Silent failure for cache
