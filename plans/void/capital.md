# Capital Ledger: void.capital.* Implementation

> *"The noun is a lie. There is only the rate of change."*

**AGENTESE Context**: `void.capital.*`
**Status**: Planned (Refined 2025-12-11)
**Principles**: Heterarchical, Accursed Share, Verb-First Ontology

---

## Design Decisions (2025-12-11 Refinement)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Ledger Architecture** | Event-Sourced | Balance is derived, not stored. Aligns with AGENTESE verb-first. Audit trail is automatic. |
| **Token Lifecycle** | Context Managers | Pythonic linearity approximation. `with ledger.issue(...) as budget:` |
| **Capital as Capability** | OCap Pattern | BypassToken is an unforgeable object, not a balance check against string ID |
| **Cost Functions** | Algebraic Composition | `COST = BaseCost() + RiskPremium(factor=2.0)` |
| **Concurrency** | Append-Only Events | No race conditions. Events appended atomically. |
| **Decay Rate** | 0.01 (Configurable) | Start simple, observe patterns, may add activity-based later |
| **Phantom Types** | REJECTED | Fighting Python's type system violates Joy-Inducing |

---

## The Problem

A system without slack cannot breathe. When T-gent, RiskCalculator, and LinearityMap must all agree, **bureaucratic gridlock** prevents creative leaps.

Traditional ledger design commits the **Noun Fallacy**: storing `balance` as mutable state. This creates:
1. Race conditions in concurrent access
2. No audit trail without explicit logging
3. Violation of AGENTESE's verb-first ontology

---

## The Solution: Event-Sourced Accursed Ledger

### Core Insight

> "Do not build a bank (database of numbers). Build a flow system (stream of events)."

Balance is a **projection**, not a stored value. All mutations are events.

```python
@dataclass(frozen=True)
class LedgerEvent:
    """Immutable event in the capital ledger."""
    event_type: Literal["ISSUE", "CREDIT", "DEBIT", "BYPASS", "DECAY", "POTLATCH"]
    agent: str
    amount: float
    timestamp: datetime
    correlation_id: str
    metadata: dict[str, Any]
```

### AGENTESE Mapping

| Path | Operation | Event Sourcing |
|------|-----------|----------------|
| `void.capital.witness` | View history | Returns event stream (Narrative) |
| `void.capital.manifest` | View balance | Computes projection from events |
| `void.capital.tithe` | Burn capital | Appends POTLATCH event (Accursed Share) |
| `void.capital.bypass` | Fool's Bypass | Appends BYPASS event, returns BypassToken |

---

## Event-Sourced Ledger (Refined Design)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4
from contextlib import contextmanager

EventType = Literal["ISSUE", "CREDIT", "DEBIT", "BYPASS", "DECAY", "POTLATCH"]


@dataclass(frozen=True)
class LedgerEvent:
    """
    Immutable event in the capital ledger.

    AGENTESE Principle: "The noun is a lie. There is only the rate of change."

    Events are the source of truth. Balance is a derived projection.
    """
    event_type: EventType
    agent: str
    amount: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_credit(self) -> bool:
        """Events that increase balance."""
        return self.event_type in ("ISSUE", "CREDIT")

    def is_debit(self) -> bool:
        """Events that decrease balance."""
        return self.event_type in ("DEBIT", "BYPASS", "DECAY", "POTLATCH")


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
    initial_capital: float = 0.5    # New agents start with some trust
    max_capital: float = 1.0        # Ceiling prevents oligarchs
    decay_rate: float = 0.01        # Configurable—observe patterns first

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

    def credit(self, agent: str, amount: float, reason: str) -> LedgerEvent:
        """
        AGENTESE: void.capital.credit

        Append CREDIT event. Returns the event for chaining.
        """
        event = LedgerEvent(
            event_type="CREDIT",
            agent=agent,
            amount=amount,
            metadata={"reason": reason},
        )
        self._append(event)
        return event

    def debit(self, agent: str, amount: float, reason: str) -> LedgerEvent | None:
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
            metadata={"reason": reason},
        )
        self._append(event)
        return event

    def apply_decay(self) -> list[LedgerEvent]:
        """
        Apply time-based decay to all agents with positive balance.

        Returns decay events for audit trail.
        """
        decay_events = []
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
```

**Location**: `shared/capital.py`

---

## Capital as Capability (OCap Pattern)

### Core Insight

Capital is not a balance checked against a string ID. Capital IS a capability token.

```python
@dataclass(frozen=True)
class BypassToken:
    """
    An unforgeable token granting bypass rights.

    OCap Pattern: The token IS the capability.
    You don't check if agent "has permission"—you check if they hold the token.
    """
    agent: str
    check_name: str
    granted_at: datetime
    expires_at: datetime
    cost: float
    correlation_id: str

    def is_valid(self) -> bool:
        """Token must be used before expiration."""
        return datetime.utcnow() < self.expires_at

    def exercise(self) -> bool:
        """
        Consume this capability (one-time use).

        Returns True if successfully exercised, False if expired.
        """
        return self.is_valid()
```

### Bypass Flow

```python
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

    now = datetime.utcnow()
    event = LedgerEvent(
        event_type="BYPASS",
        agent=agent,
        amount=cost,
        metadata={"check": check_name, "ttl": ttl_seconds},
    )
    self._append(event)

    return BypassToken(
        agent=agent,
        check_name=check_name,
        granted_at=now,
        expires_at=now + timedelta(seconds=ttl_seconds),
        cost=cost,
        correlation_id=event.correlation_id,
    )
```

---

## Algebraic Cost Functions

### Core Insight

Cost functions should be composable, not ad-hoc formulas.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any
import math


@dataclass
class CostContext:
    """Context for cost calculation."""
    risk: float              # 0.0 to 1.0
    judgment_score: float    # 0.0 to 1.0 (from T-gent)
    resources_ok: bool       # Resource constraints satisfied


@dataclass
class CostFactor:
    """
    A composable cost function component.

    Costs compose algebraically:
    - Addition: cost_a + cost_b (factors sum)
    - Scaling: 0.5 * cost_a (factor scales)
    """
    name: str
    compute: Callable[[CostContext], float]

    def __call__(self, ctx: CostContext) -> float:
        return self.compute(ctx)

    def __add__(self, other: CostFactor) -> CostFactor:
        """Costs add."""
        return CostFactor(
            name=f"{self.name}+{other.name}",
            compute=lambda ctx: self.compute(ctx) + other.compute(ctx),
        )

    def __mul__(self, scalar: float) -> CostFactor:
        """Scale a cost."""
        return CostFactor(
            name=f"{scalar}*{self.name}",
            compute=lambda ctx: scalar * self.compute(ctx),
        )

    def __rmul__(self, scalar: float) -> CostFactor:
        return self.__mul__(scalar)


# Standard cost factors
BASE_COST = CostFactor("base", lambda _: 0.1)

RISK_PREMIUM = CostFactor(
    "risk",
    lambda ctx: math.exp(ctx.risk * 2) - 1  # Exponential scaling
)

JUDGMENT_DEFICIT = CostFactor(
    "judgment",
    lambda ctx: max(0, 0.8 - ctx.judgment_score)
)

RESOURCE_PENALTY = CostFactor(
    "resource",
    lambda ctx: 0.1 if not ctx.resources_ok else 0
)

# Compose into bypass cost
BYPASS_COST = BASE_COST + 0.1 * RISK_PREMIUM + 0.1 * JUDGMENT_DEFICIT + RESOURCE_PENALTY
```

### Usage

```python
ctx = CostContext(risk=0.7, judgment_score=0.6, resources_ok=True)
cost = BYPASS_COST(ctx)  # Algebraically computed
```

---

## Resource Token as Context Manager

### Core Insight

Python cannot enforce linearity at the type level. Context managers are Python's native lifecycle mechanism.

```python
from contextlib import contextmanager
from typing import Generator


@dataclass
class ResourceBudget:
    """
    A scoped resource budget.

    Usage:
        async with ledger.issue_budget(agent, 100) as budget:
            # Budget is live
            budget.spend(50)
        # Budget automatically settled on exit
    """
    agent: str
    initial: float
    remaining: float
    ledger: EventSourcedLedger
    _settled: bool = False

    def spend(self, amount: float) -> bool:
        """Spend from budget. Returns False if insufficient."""
        if amount > self.remaining:
            return False
        self.remaining -= amount
        return True

    def settle(self) -> None:
        """Return unused budget to ledger."""
        if self._settled:
            return
        unused = self.remaining
        if unused > 0:
            self.ledger.credit(
                self.agent,
                unused * 0.5,  # 50% recovery for unused budget
                "budget_return",
            )
        self._settled = True


@contextmanager
def issue_budget(
    ledger: EventSourcedLedger,
    agent: str,
    amount: float,
) -> Generator[ResourceBudget, None, None]:
    """
    Issue a scoped resource budget.

    Pythonic approximation of linear types via context manager.
    """
    # Debit upfront
    event = ledger.debit(agent, amount, "budget_issue")
    if event is None:
        raise InsufficientCapitalError(f"{agent} lacks {amount} capital")

    budget = ResourceBudget(
        agent=agent,
        initial=amount,
        remaining=amount,
        ledger=ledger,
    )

    try:
        yield budget
    finally:
        budget.settle()
```

---

## Test Environment Isolation

### Dependency Injection

The Logos resolver accepts a specific Ledger instance:

```python
@dataclass
class Logos:
    root: DataAgent
    registry: Catalog
    projector: Projector
    ledger: EventSourcedLedger  # Injected, not global
```

### Test Fixtures

```python
import pytest

@pytest.fixture
def ledger() -> EventSourcedLedger:
    """Fresh ledger per test—no shared state."""
    return EventSourcedLedger()

@pytest.fixture
def funded_ledger() -> EventSourcedLedger:
    """Ledger with test agent funded."""
    ledger = EventSourcedLedger()
    ledger.credit("test-agent", 0.5, "test_setup")
    return ledger
```

---

## Trust Gate Integration (Refined)

```python
@dataclass
class TrustGate:
    """
    Gate that combines T-gent judgment with capital bypass.

    OCap Pattern: Gate accepts BypassToken, not agent name.
    """
    critic: JudgeAgent
    risk_calculator: ProposalRiskCalculator
    capital_ledger: EventSourcedLedger
    cost_function: CostFactor = BYPASS_COST

    async def evaluate(
        self,
        proposal: Proposal,
        agent: str,
        bypass_token: BypassToken | None = None,
    ) -> TrustDecision:
        # Standard evaluation
        judgment = await self.critic.evaluate(proposal.diff)
        risk = self.risk_calculator.calculate_risk(proposal)

        ctx = CostContext(
            risk=risk,
            judgment_score=judgment.score,
            resources_ok=True,  # Simplified
        )

        # Standard path: all checks must pass
        if judgment.score > 0.8 and risk < 0.3:
            self.capital_ledger.credit(agent, 0.02, "good_proposal")
            return TrustDecision(approved=True)

        # Fool's Bypass: agent presents token
        if bypass_token and bypass_token.is_valid():
            if bypass_token.check_name == "trust_gate":
                return TrustDecision(
                    approved=True,
                    bypassed=True,
                    capital_spent=bypass_token.cost,
                )

        return TrustDecision(
            approved=False,
            bypass_cost=self.cost_function(ctx),
        )
```

---

## CLI Commands

```bash
# Query capital balance (void.capital.manifest)
kgents capital balance --agent b-gent
# Output: b-gent: 0.72 (max: 1.0)

# View capital history (void.capital.witness)
kgents capital history --agent b-gent --limit 10
# Output: Event stream with timestamps

# Tithe to void (void.capital.tithe)
kgents capital tithe --agent b-gent --amount 0.1
# Output: Potlatch complete. Remaining: 0.62
```

---

## Property-Based Tests

```python
from hypothesis import given, strategies as st

@given(st.lists(st.tuples(
    st.sampled_from(["CREDIT", "DEBIT"]),
    st.floats(min_value=0, max_value=1),
)))
def test_balance_is_projection(events: list[tuple[str, float]]) -> None:
    """Balance equals sum of credits minus sum of debits."""
    ledger = EventSourcedLedger()
    for event_type, amount in events:
        if event_type == "CREDIT":
            ledger.credit("agent", amount, "test")
        else:
            ledger.debit("agent", amount, "test")

    expected = ledger.initial_capital
    for event_type, amount in events:
        if event_type == "CREDIT":
            expected = min(expected + amount, ledger.max_capital)
        else:
            expected = max(0, expected - amount)

    assert abs(ledger.balance("agent") - expected) < 0.001


def test_events_are_immutable() -> None:
    """Events cannot be modified after creation."""
    event = LedgerEvent(event_type="CREDIT", agent="a", amount=1.0)
    with pytest.raises(AttributeError):
        event.amount = 2.0  # frozen=True prevents this
```

---

## Cross-References

- **Plans**: `world/k8-gents.md` (Trust Gate), `void/entropy.md` (Accursed Share)
- **Impl**: `shared/capital.py` (planned)
- **Spec**: `spec/principles.md` (Heterarchical, Accursed Share, Verb-First)

---

*"The river that flows only downhill never discovers the mountain spring."*
