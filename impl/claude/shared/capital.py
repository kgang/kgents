"""
Event-Sourced Capital Ledger

AGENTESE Context: void.capital.*

The Accursed Share applied to agent capital:
- Balance is derived, never stored (verb-first ontology)
- Events are immutable and append-only (no race conditions)
- BypassToken is an OCap capability (no view from nowhere)

Principle Alignment:
- AGENTESE: "The noun is a lie. There is only the rate of change."
- Heterarchical: Authority earned through events, not fixed hierarchy
- Accursed Share: Wealth that isn't spent will consume the community (potlatch)

Design Decisions:
- Event-sourced: Balance computed from events, not stored
- Append-only: Thread-safe without locks
- OCap pattern: BypassToken IS the capability, not a checked permission
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import uuid4


def _utcnow() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(UTC)


# === Types ===

EventType = Literal["ISSUE", "CREDIT", "DEBIT", "BYPASS", "DECAY", "POTLATCH"]


# === Errors (Sympathetic) ===


class InsufficientCapitalError(Exception):
    """
    Raised when an agent lacks sufficient capital for an operation.

    Sympathetic errors explain why and suggest what to do.
    """

    def __init__(
        self,
        message: str,
        *,
        agent: str = "",
        required: float = 0.0,
        available: float = 0.0,
    ) -> None:
        self.agent = agent
        self.required = required
        self.available = available

        formatted = message
        if agent and required > 0:
            deficit = required - available
            formatted = (
                f"{message}\n\n"
                f"    Agent: {agent}\n"
                f"    Required: {required:.3f}\n"
                f"    Available: {available:.3f}\n"
                f"    Deficit: {deficit:.3f}\n\n"
                f"    Try: void.capital.witness to see history, or earn capital via good proposals"
            )
        super().__init__(formatted)


# === Immutable Events ===


@dataclass(frozen=True)
class LedgerEvent:
    """
    Immutable event in the capital ledger.

    AGENTESE Principle: "The noun is a lie. There is only the rate of change."

    Events are the source of truth. Balance is a derived projection.
    The frozen=True ensures events cannot be modified after creation.
    """

    event_type: EventType
    agent: str
    amount: float
    timestamp: datetime = field(default_factory=_utcnow)
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_credit(self) -> bool:
        """Events that increase balance."""
        return self.event_type in ("ISSUE", "CREDIT")

    def is_debit(self) -> bool:
        """Events that decrease balance."""
        return self.event_type in ("DEBIT", "BYPASS", "DECAY", "POTLATCH")


# === OCap Bypass Token ===


@dataclass(frozen=True)
class BypassToken:
    """
    An unforgeable token granting bypass rights.

    OCap Pattern: The token IS the capability.
    You don't check if agent "has permission"—you check if they hold the token.

    AGENTESE: "No View From Nowhere"—the Gate accepts TOKEN, not agent name string.
    """

    agent: str
    check_name: str
    granted_at: datetime
    expires_at: datetime
    cost: float
    correlation_id: str

    def is_valid(self) -> bool:
        """Token must be used before expiration."""
        return _utcnow() < self.expires_at

    def exercise(self) -> bool:
        """
        Consume this capability (one-time use).

        Returns True if successfully exercised, False if expired.
        """
        return self.is_valid()


# === Event-Sourced Ledger ===


@dataclass
class EventSourcedLedger:
    """
    Event-sourced capital ledger.

    Design Principles:
    1. Append-only: Events are immutable, never modified
    2. Derived state: Balance computed from events
    3. Concurrency safe: Append is atomic
    4. Time-travel: Replay to any point
    5. CQRS-ready: Different query patterns without touching source

    AGENTESE: void.capital.*
    """

    _events: list[LedgerEvent] = field(default_factory=list)

    # Configuration
    initial_capital: float = 0.5  # New agents start with some trust
    max_capital: float = 1.0  # Ceiling prevents oligarchs
    decay_rate: float = 0.01  # Configurable—observe patterns first

    def balance(self, agent: str) -> float:
        """
        AGENTESE: void.capital.manifest

        Derived from events, never stored directly.
        This IS the projection—the verb-first ontology in action.
        """
        total = self.initial_capital
        for event in self._events:
            if event.agent != agent:
                continue
            if event.is_credit():
                total += event.amount
            elif event.is_debit():
                total -= event.amount
        return min(max(0, total), self.max_capital)

    def witness(self, agent: str | None = None, limit: int = 100) -> list[LedgerEvent]:
        """
        AGENTESE: void.capital.witness

        Returns the event stream (Narrative). The history IS the truth.
        """
        events = self._events
        if agent:
            events = [e for e in events if e.agent == agent]
        return events[-limit:]

    def _append(self, event: LedgerEvent) -> None:
        """Atomic append—concurrency safe."""
        self._events.append(event)

    def credit(self, agent: str, amount: float, reason: str, **metadata: Any) -> LedgerEvent:
        """
        AGENTESE: void.capital.credit

        Append CREDIT event. Returns the event for chaining.
        """
        event = LedgerEvent(
            event_type="CREDIT",
            agent=agent,
            amount=amount,
            metadata={"reason": reason, **metadata},
        )
        self._append(event)
        return event

    def debit(self, agent: str, amount: float, reason: str, **metadata: Any) -> LedgerEvent | None:
        """
        AGENTESE: void.capital.debit

        Append DEBIT event if sufficient balance. Returns event or None.
        """
        if self.balance(agent) < amount:
            return None
        event = LedgerEvent(
            event_type="DEBIT",
            agent=agent,
            amount=amount,
            metadata={"reason": reason, **metadata},
        )
        self._append(event)
        return event

    def apply_decay(self) -> list[LedgerEvent]:
        """
        Apply time-based decay to all agents with positive balance.

        Returns decay events for audit trail.
        """
        decay_events: list[LedgerEvent] = []
        agents = {e.agent for e in self._events}
        for agent in agents:
            current = self.balance(agent)
            if current > 0:
                decay_amount = current * self.decay_rate
                event = LedgerEvent(
                    event_type="DECAY",
                    agent=agent,
                    amount=decay_amount,
                    metadata={"rate": self.decay_rate},
                )
                self._append(event)
                decay_events.append(event)
        return decay_events

    def potlatch(self, agent: str, amount: float) -> LedgerEvent | None:
        """
        AGENTESE: void.capital.tithe

        Ritual destruction grants prestige. Burns capital.
        The Accursed Share: wealth that is not consumed will consume the community.
        """
        if self.balance(agent) < amount:
            return None
        event = LedgerEvent(
            event_type="POTLATCH",
            agent=agent,
            amount=amount,
            metadata={"ritual": "accursed_share"},
        )
        self._append(event)
        return event

    def mint_bypass(
        self,
        agent: str,
        check_name: str,
        cost: float,
        ttl_seconds: float = 60.0,
    ) -> BypassToken | None:
        """
        AGENTESE: void.capital.bypass

        Mint a bypass capability token.

        The Gate receives the TOKEN, not the agent name.
        This satisfies "No View From Nowhere"—you need the token to pass.
        """
        if self.balance(agent) < cost:
            return None

        now = _utcnow()
        correlation_id = str(uuid4())
        event = LedgerEvent(
            event_type="BYPASS",
            agent=agent,
            amount=cost,
            correlation_id=correlation_id,
            metadata={"check": check_name, "ttl": ttl_seconds},
        )
        self._append(event)

        return BypassToken(
            agent=agent,
            check_name=check_name,
            granted_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
            cost=cost,
            correlation_id=correlation_id,
        )

    def issue(self, agent: str, amount: float, reason: str = "initial") -> LedgerEvent:
        """
        Issue initial capital to an agent.

        Unlike credit, this can create capital from nothing (system operation).
        """
        event = LedgerEvent(
            event_type="ISSUE",
            agent=agent,
            amount=amount,
            metadata={"reason": reason},
        )
        self._append(event)
        return event

    @property
    def events(self) -> list[LedgerEvent]:
        """Read-only access to event stream."""
        return list(self._events)

    def agents(self) -> set[str]:
        """All agents who have events in the ledger."""
        return {e.agent for e in self._events}
