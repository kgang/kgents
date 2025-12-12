# The Capital Ledger: Social Trust for the Accursed Share

> *"A system without slack cannot breathe. The Fool's Bypass gives the lattice room to dance."*

**Status**: Spec Proposal
**Date**: 2025-12-11
**Origin**: Architectural critique of plan-upgrade-proposal.md
**Principle**: The Accursed Share

---

## The Meta-Critique Addressed

The unified lattice proposal was hyper-efficient: it tracked every resource (Linearity), optimized every context (Compression), and verified every trust event (Lattice).

**The Danger**: A system without slack cannot breathe. If `T-gent`, `RiskCalculator`, and `LinearityMap` all must agree, you create a **Bureaucracy Agent**—a system that is "safe" but paralyzed.

**The Modification**: The Trust Lattice needs a **Fool's Bypass**—a path where agents can spend accumulated trust to override safety checks for high-variance, creative moves.

---

## Part I: The Capital Ledger

### 1.1 Core Concept

Agents earn **social capital** through successful predictions (B-gent), merged proposals, and consistent behavior. They can spend this capital to bypass bureaucratic gates when creativity demands it.

This reintroduces the **Heterarchical** flow: authority is earned, not just static.

### 1.2 AGENTESE Paths

| Path | Operation | Description |
|------|-----------|-------------|
| `void.capital.balance` | Query | Get agent's current social capital |
| `void.capital.credit` | Earn | Credit trust after successful prediction |
| `void.capital.debit` | Spend | Consume capital for an action |
| `void.capital.bypass` | Fool's Bypass | Spend capital to override a safety check |
| `void.capital.history` | Audit | Get trust event history |

### 1.3 Implementation

```python
# shared/capital.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass
class TrustEvent:
    """A trust-affecting event in the ledger."""
    agent: str
    event_type: str  # "prediction_correct", "proposal_merged", "failure", etc.
    delta: float     # Positive = gain trust, negative = lose trust
    timestamp: datetime
    reason: str

    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "event_type": self.event_type,
            "delta": self.delta,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
        }


@dataclass
class BypassResult:
    """Result of attempting a Fool's Bypass."""
    allowed: bool
    reason: str
    remaining_capital: float
    check_bypassed: str | None = None


@dataclass
class CapitalLedger:
    """
    Social Capital accounting for the Trust Lattice.

    The Accursed Share requires a Fool's Bypass—a path where
    agents can spend accumulated trust to override safety checks.

    ## Design Principles

    1. **Earned Authority**: Trust is accumulated through success
    2. **Spendable Trust**: Capital can be consumed for bypasses
    3. **Decay**: Unused trust decays slowly (use it or lose it)
    4. **Transparency**: All transactions are auditable
    5. **Bounded**: Capital has a ceiling to prevent infinite accumulation

    ## Trust Sources

    - B-gent predictions: Correct predictions credit capital
    - Proposal outcomes: Merged proposals with no issues credit capital
    - Consistent performance: Small daily credits for stable agents
    - Peer endorsements: Other agents can vouch (future)

    ## Trust Sinks

    - Fool's Bypass: Spending capital to override safety
    - Failures: Predictions that fail debit capital
    - Rejected proposals: High-risk proposals that are rejected
    - Time decay: Unused capital slowly decays
    """

    _balances: dict[str, float] = field(default_factory=dict)
    _history: list[TrustEvent] = field(default_factory=list)

    # Configuration
    initial_capital: float = 0.5    # New agents start with some trust
    max_capital: float = 1.0        # Cap to prevent infinite accumulation
    decay_rate: float = 0.01        # Trust decays slowly (use it or lose it)
    min_bypass_cost: float = 0.1    # Floor for bypass costs

    def balance(self, agent: str) -> float:
        """
        Get agent's current social capital.

        AGENTESE: void.capital.balance
        """
        if agent not in self._balances:
            self._balances[agent] = self.initial_capital
            self._history.append(TrustEvent(
                agent=agent,
                event_type="initial_credit",
                delta=self.initial_capital,
                timestamp=datetime.now(),
                reason="New agent initialization",
            ))
        return self._balances[agent]

    def credit(self, agent: str, amount: float, reason: str) -> None:
        """
        Agent earns trust.

        AGENTESE: void.capital.credit

        Examples:
            - B-gent prediction correct: +0.1
            - Proposal merged without issues: +0.05
            - Consistent performance over time: +0.02/day
        """
        current = self.balance(agent)
        new_balance = min(current + amount, self.max_capital)
        actual_delta = new_balance - current

        self._balances[agent] = new_balance
        self._history.append(TrustEvent(
            agent=agent,
            event_type="credit",
            delta=actual_delta,
            timestamp=datetime.now(),
            reason=reason,
        ))

    def debit(self, agent: str, amount: float, reason: str) -> bool:
        """
        Agent spends trust.

        AGENTESE: void.capital.debit

        Returns True if sufficient capital, False otherwise.
        """
        current = self.balance(agent)
        if current < amount:
            return False

        self._balances[agent] = current - amount
        self._history.append(TrustEvent(
            agent=agent,
            event_type="debit",
            delta=-amount,
            timestamp=datetime.now(),
            reason=reason,
        ))
        return True

    def can_bypass(self, agent: str, cost: float) -> bool:
        """Check if agent can afford to bypass a safety check."""
        return self.balance(agent) >= cost

    def fool_bypass(
        self,
        agent: str,
        check_name: str,
        cost: float | None = None,
    ) -> BypassResult:
        """
        The Fool's Bypass: spend social capital to override a safety check.

        Named after the Fool card in Tarot—the one who steps off the cliff
        trusting in serendipity. Sometimes creative leaps require it.

        AGENTESE: void.capital.bypass

        Args:
            agent: The agent requesting bypass
            check_name: Name of the safety check being bypassed
            cost: Cost of bypass (defaults to min_bypass_cost)

        Returns:
            BypassResult with allowed=True if bypass succeeded
        """
        actual_cost = cost if cost is not None else self.min_bypass_cost

        if not self.can_bypass(agent, actual_cost):
            return BypassResult(
                allowed=False,
                reason=f"Insufficient capital ({self.balance(agent):.2f} < {actual_cost:.2f})",
                remaining_capital=self.balance(agent),
            )

        self.debit(agent, actual_cost, f"fool_bypass:{check_name}")

        return BypassResult(
            allowed=True,
            reason=f"Bypassed {check_name} (cost: {actual_cost:.2f})",
            remaining_capital=self.balance(agent),
            check_bypassed=check_name,
        )

    def history(self, agent: str | None = None, limit: int = 100) -> list[TrustEvent]:
        """
        Get trust event history.

        AGENTESE: void.capital.history
        """
        events = self._history
        if agent:
            events = [e for e in events if e.agent == agent]
        return events[-limit:]

    def apply_decay(self) -> None:
        """
        Apply time-based decay to all balances.

        Call periodically (e.g., daily) to ensure unused capital decays.
        """
        for agent in self._balances:
            current = self._balances[agent]
            decay = current * self.decay_rate
            if decay > 0.001:  # Only record non-trivial decay
                self._balances[agent] = current - decay
                self._history.append(TrustEvent(
                    agent=agent,
                    event_type="decay",
                    delta=-decay,
                    timestamp=datetime.now(),
                    reason="Time-based decay",
                ))
```

---

## Part II: Integration with Trust Lattice

### 2.1 TrustGate with Capital

The `TrustGate` now includes the Capital Ledger as an escape valve:

```python
# infra/k8s/operators/trust_gate.py
from shared.capital import CapitalLedger, BypassResult


@dataclass
class TrustDecision:
    """Result of trust evaluation."""
    approved: bool
    explanation: str
    bypassed: bool = False
    capital_spent: float = 0.0
    bypass_available: float | None = None


@dataclass
class TrustGate:
    """
    A gate that combines T-gent judgment with resource accounting
    AND social capital.

    The Capital Ledger provides an escape valve—earned authority
    to bypass the bureaucracy when creativity demands it.
    """
    critic: JudgeAgent           # T-gent Type IV
    risk_calculator: ProposalRiskCalculator  # K8-gents
    resource_ledger: Ledger      # Resource accounting (not linear types)
    capital_ledger: CapitalLedger  # Social capital for bypass

    async def evaluate(
        self,
        proposal: Proposal,
        agent: str,
    ) -> TrustDecision:
        """
        Evaluate proposal with standard checks + bypass option.
        """
        # Standard evaluation
        judgment = await self.critic.evaluate(proposal.diff)
        risk = self.risk_calculator.calculate_risk(proposal)
        resources_ok = self.resource_ledger.validate(proposal.resources)

        # Standard path: all checks must pass
        if judgment.score > 0.8 and risk < 0.3 and resources_ok:
            # Credit trust for submitting a good proposal
            self.capital_ledger.credit(
                agent,
                0.02,
                f"Good proposal: {proposal.name}",
            )
            return TrustDecision(
                approved=True,
                explanation="All checks passed",
            )

        # Calculate bypass cost based on deficit
        bypass_cost = self._calculate_bypass_cost(judgment, risk, resources_ok)

        # Fool's Bypass: agent can spend capital to override
        if self.capital_ledger.can_bypass(agent, bypass_cost):
            # Offer bypass but don't auto-use it
            bypass = self.capital_ledger.fool_bypass(
                agent,
                "trust_gate",
                cost=bypass_cost,
            )
            if bypass.allowed:
                return TrustDecision(
                    approved=True,
                    explanation=f"Bypassed via social capital ({bypass.reason})",
                    bypassed=True,
                    capital_spent=bypass_cost,
                )

        # Failed: report what would be needed
        return TrustDecision(
            approved=False,
            explanation=(
                f"Judgment: {judgment.score:.2f}, "
                f"Risk: {risk:.2f}, "
                f"Resources: {resources_ok}"
            ),
            bypass_available=bypass_cost if self.capital_ledger.can_bypass(agent, bypass_cost) else None,
        )

    def _calculate_bypass_cost(
        self,
        judgment: Judgment,
        risk: float,
        resources_ok: bool,
    ) -> float:
        """
        Higher risk = higher cost to bypass.

        Base cost 0.1, scales with risk and judgment deficit.
        """
        base = 0.1
        risk_factor = risk * 0.3
        judgment_factor = max(0, 0.8 - judgment.score) * 0.2
        resource_factor = 0.1 if not resources_ok else 0
        return base + risk_factor + judgment_factor + resource_factor
```

### 2.2 B-gent Prediction Integration

B-gent predictions credit or debit the capital ledger:

```python
# agents/b/predictions.py

class PredictionOutcomeHandler:
    """Handles prediction outcomes for capital accounting."""

    def __init__(self, capital_ledger: CapitalLedger):
        self.capital = capital_ledger

    async def on_prediction_verified(
        self,
        agent: str,
        prediction: Prediction,
        outcome: Outcome,
    ) -> None:
        """Called when a prediction is verified against reality."""
        if outcome.correct:
            # Correct prediction: credit capital
            credit = self._calculate_credit(prediction, outcome)
            self.capital.credit(
                agent,
                credit,
                f"Prediction correct: {prediction.summary}",
            )
        else:
            # Incorrect prediction: debit capital
            debit = self._calculate_debit(prediction, outcome)
            self.capital.debit(
                agent,
                debit,
                f"Prediction incorrect: {prediction.summary}",
            )

    def _calculate_credit(
        self,
        prediction: Prediction,
        outcome: Outcome,
    ) -> float:
        """
        Credit scales with prediction difficulty.

        - Easy predictions (high confidence, common scenario): low credit
        - Hard predictions (low confidence, rare scenario): high credit
        """
        base = 0.05
        difficulty_factor = 1.0 - prediction.confidence
        rarity_factor = 1.0 - outcome.base_rate
        return base + (difficulty_factor * 0.1) + (rarity_factor * 0.1)

    def _calculate_debit(
        self,
        prediction: Prediction,
        outcome: Outcome,
    ) -> float:
        """
        Debit scales inversely with expressed uncertainty.

        - Confident wrong: high debit
        - Uncertain wrong: low debit (you were honest about uncertainty)
        """
        base = 0.03
        overconfidence_factor = prediction.confidence
        return base * overconfidence_factor
```

---

## Part III: CLI Integration

### 3.1 New Commands

```bash
# Query capital balance
kgents capital balance --agent b-gent
# Output: b-gent: 0.72 (max: 1.0)

# View capital history
kgents capital history --agent b-gent --limit 10
# Output: Recent trust events

# (Internal) Bypass a check
kgents capital bypass --agent b-gent --check trust_gate --cost 0.15
# Output: Bypass result
```

### 3.2 Integration with `kgents propose`

```python
# protocols/cli/handlers/propose.py

async def cmd_propose(args):
    """Submit a proposal with optional capital bypass."""
    client = ResilientClient()

    # First, try standard proposal
    response = await client.invoke(
        "self.deployment.propose",
        observer=get_current_umwelt(),
        proposal=proposal,
    )

    if response.approved:
        print(f"Proposal approved: {response.explanation}")
        return 0

    # Offer bypass if available
    if response.bypass_available:
        print(f"Proposal blocked: {response.explanation}")
        print(f"Bypass available (cost: {response.bypass_available:.2f})")

        if "--bypass" in args:
            bypass_response = await client.invoke(
                "void.capital.bypass",
                agent=current_agent(),
                check_name="trust_gate",
                cost=response.bypass_available,
            )
            if bypass_response.allowed:
                print(f"Bypassed: {bypass_response.reason}")
                return 0

    print(f"Proposal rejected: {response.explanation}")
    return 1
```

---

## Part IV: Safety Considerations

### 4.1 Anti-Gaming Measures

| Risk | Mitigation |
|------|------------|
| **Farming easy predictions** | Difficulty-adjusted credits |
| **Infinite accumulation** | `max_capital` ceiling |
| **Hoarding capital** | Time-based decay |
| **Collusion** | Audit trail, peer review |

### 4.2 Audit Trail

All capital transactions are recorded with timestamps and reasons. This provides:

1. **Accountability**: Who bypassed what, when
2. **Pattern detection**: Identify concerning behavior
3. **Debugging**: Understand trust dynamics

### 4.3 Emergency Override

For critical situations, the system administrator can:

```bash
# Emergency capital injection (use sparingly)
kgents capital admin-credit --agent b-gent --amount 0.5 --reason "Emergency"

# Reset capital (nuclear option)
kgents capital admin-reset --agent b-gent
```

---

## Part V: AGENTESE Integration

### 5.1 Void Context Extension

The Capital Ledger extends the `void` context:

```python
# protocols/agentese/contexts/void.py

class VoidContext(LogosNode):
    """The void context: entropy, serendipity, gratitude, and capital."""

    async def invoke(self, aspect: str, observer: Umwelt, **kwargs) -> Any:
        match aspect:
            case "entropy.sip":
                return await self._sip_entropy(observer, **kwargs)
            case "entropy.tithe":
                return await self._tithe_entropy(observer, **kwargs)
            case "capital.balance":
                return self.capital_ledger.balance(kwargs["agent"])
            case "capital.credit":
                return self.capital_ledger.credit(
                    kwargs["agent"],
                    kwargs["amount"],
                    kwargs["reason"],
                )
            case "capital.bypass":
                return self.capital_ledger.fool_bypass(
                    kwargs["agent"],
                    kwargs["check_name"],
                    kwargs.get("cost"),
                )
            case "capital.history":
                return self.capital_ledger.history(
                    kwargs.get("agent"),
                    kwargs.get("limit", 100),
                )
            case _:
                raise PathNotFoundError(f"void.{aspect}")
```

---

## Cross-References

- `plans/lattice-refinement.md` - Overall integration
- `plans/k8-gents-implementation.md` - Trust Gate usage
- `plans/agentese-synthesis.md` - AGENTESE paths
- `spec/principles.md` - The Accursed Share principle

---

*"The Fool steps off the cliff. Sometimes, that's exactly what's needed."*
