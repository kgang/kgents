# The Refined Lattice: Implementation Roadmap v2.0

> *"A system without slack cannot breathe. The Fool's Bypass gives the lattice room to dance."*

**Status**: Active Implementation Roadmap
**Date**: 2025-12-11
**Supersedes**: docs/plan-upgrade-proposal.md
**Inputs**: All five plans + architectural critique

---

## Summary of Refinements

This document synthesizes the five implementation plans with the architectural critique. The critique identified several category-theoretic errors and architectural misjudgments that required correction.

### Key Directives Integrated

| Directive | Source | Resolution |
|-----------|--------|------------|
| **Rename CompressionLens to ContextProjector** | Critique §1.A | Lossy compression is NOT a Lens (Get-Put law violation) |
| **Downgrade Linear Types to Resource Accounting** | Critique §1.B | Python cannot enforce linearity at type level |
| **Implement ContextWindow as Store Comonad** | Critique §1.C | Explicit `(S -> A, S)` structure enables counterfactuals |
| **Reject Dapr integration** | Critique §2.A | K8s Operator IS the actor runtime; keep stack hollow |
| **ResilientClient as LogosNode** | Critique §2.B | The client IS a node in the AGENTESE graph |
| **Add Capital Ledger (Social Capital)** | Critique §3 | Prevent bureaucratic gridlock via earned trust |
| **Prioritize ResilientClient** | Critique §4 | Immediate user value before abstract algebra |

---

## Part I: Theoretical Corrections

### 1.1 ContextProjector (Not Lens)

**The Problem**: The original proposal used `CompressionLens` for context compression, but a Lens requires the Get-Put law: `update(s, view(s)) == s`. Lossy compression cannot satisfy this.

**The Fix**: Rename to `ContextProjector` and model as a **Galois Connection**:

```python
# plans/context-sovereignty.md correction
@dataclass
class ContextProjector:
    """
    A Galois Connection for context compression.

    NOT a Lens—this is an irreversible projection.
    Information is lost. The developer is warned.

    Mathematical Structure:
        Abstraction (upper adjoint): compress: C -> C_hat
        Concretization (lower adjoint): expand: C_hat -> C
        Property: compress(expand(c_hat)) <= c_hat

    The <= denotes that the expanded summary is an approximation
    less precise than the original.
    """

    async def compress(self, context: ContextWindow) -> CompressedContext:
        """
        Project context to compressed form.

        WARNING: This is lossy. Information is discarded.
        Use linearity markers to preserve RELEVANT fragments.
        """
        ...

    async def expand(
        self,
        compressed: CompressedContext,
        hints: list[str] | None = None,
    ) -> ContextWindow:
        """
        Expand compressed context (best-effort reconstruction).

        Cannot recover original. This is NOT the inverse of compress().
        """
        ...
```

### 1.2 Resource Accounting (Not Linear Types)

**The Problem**: Python's memory model (reference counting + GC) makes true linear types impossible. Claiming "Linear Types" promises safety the runtime cannot guarantee.

**The Fix**: Reframe as **Runtime Resource Accounting** via a Token Ledger:

```python
# Renamed: shared/accounting.py (not linearity.py)
from dataclasses import dataclass
from typing import TypeVar, Generic
from uuid import uuid4

T = TypeVar('T')

@dataclass
class ResourceToken(Generic[T]):
    """
    Runtime resource accounting token.

    NOT a linear type—Python cannot enforce this at compile time.
    This is a runtime ledger that tracks resource consumption.
    Violations are detected at runtime, not prevented at compile time.
    """
    id: str
    value: T
    consumed: bool = False

    def __init__(self, value: T):
        self.id = uuid4().hex[:8]
        self.value = value
        self.consumed = False


@dataclass
class Ledger:
    """
    Runtime accounting ledger for resource consumption.

    Fits the Heterarchical principle: resources flow and are
    accounted for, rather than statically locked.
    """

    _tokens: dict[str, ResourceToken] = field(default_factory=dict)

    def issue(self, value: T) -> ResourceToken[T]:
        """Issue a new resource token."""
        token = ResourceToken(value)
        self._tokens[token.id] = token
        return token

    def debit(self, token: ResourceToken[T]) -> T:
        """
        Consume a resource token.

        Raises ResourceViolation if already consumed.
        """
        if token.id not in self._tokens:
            raise ResourceViolation(f"Token {token.id} not found in ledger")
        if token.consumed:
            raise ResourceViolation(f"Token {token.id} already consumed")

        token.consumed = True
        return token.value

    def credit(self, token: ResourceToken[T], amount: float = 0.5) -> None:
        """
        Return unused portion of resource (partial recovery).

        Only recovers `amount` fraction—some waste is inevitable.
        This is the Accursed Share in action.
        """
        ...
```

### 1.3 Store Comonad Implementation

**The Problem**: The proposal identified ContextWindow as a Comonad but didn't specify the *type*. The correct structure is the **Store Comonad**: `(S -> A, S)`.

**The Fix**: Explicit Store Comonad with position and peek function:

```python
# context-sovereignty.md: Store Comonad implementation
@dataclass(frozen=True)
class ContextWindow(Generic[A]):
    """
    The Store Comonad for agent context.

    Structure: (S -> A, S) where:
        S = Position (current focus in context)
        S -> A = Peek function (inspect values relative to position)

    This gives us `duplicate` for free, which is exactly what
    we need for Git-backed counterfactuals (Modal Scope).
    """

    position: int                    # Current focus position
    peek: Callable[[int], A]         # Access any position
    history: tuple[A, ...]           # Materialized history
    metadata: ContextMeta

    def extract(self) -> A:
        """Get value at current position."""
        return self.peek(self.position)

    def extend(self, f: Callable[["ContextWindow[A]"], B]) -> "ContextWindow[B]":
        """
        Compute f at every position.

        The Store Comonad's extend creates a new store where
        each position contains f applied to the store focused at that position.
        """
        def new_peek(pos: int) -> B:
            shifted = self._focus_at(pos)
            return f(shifted)

        return ContextWindow(
            position=self.position,
            peek=new_peek,
            history=tuple(new_peek(i) for i in range(len(self.history))),
            metadata=self.metadata.evolved(),
        )

    def duplicate(self) -> "ContextWindow[ContextWindow[A]]":
        """
        Create context of all possible contexts (Store-specific).

        This is the key operation for Modal Scope:
        duplicate() creates a context containing all possible
        "views" of the current context—exactly what Git branching provides.
        """
        def new_peek(pos: int) -> ContextWindow[A]:
            return self._focus_at(pos)

        return ContextWindow(
            position=self.position,
            peek=new_peek,
            history=tuple(self._focus_at(i) for i in range(len(self.history))),
            metadata=self.metadata.branched(),
        )

    def _focus_at(self, new_pos: int) -> "ContextWindow[A]":
        """Shift focus to a different position."""
        return ContextWindow(
            position=new_pos,
            peek=self.peek,
            history=self.history,
            metadata=self.metadata,
        )

    # === Store-specific operations ===

    def seek(self, new_pos: int) -> "ContextWindow[A]":
        """Move focus to new position (Store Comonad navigation)."""
        return self._focus_at(new_pos)

    def seeks(self, f: Callable[[int], int]) -> "ContextWindow[A]":
        """Move focus by function (relative navigation)."""
        return self._focus_at(f(self.position))
```

---

## Part II: Architectural Corrections

### 2.1 Dapr Rejection

**The Problem**: The proposal suggested adopting Dapr sidecars for actor semantics.

**The Critique**: Adding Dapr introduces massive dependency for a problem K8s can solve natively. The K8s Operator IS the actor runtime.

**The Fix**: Keep the stack hollow. The `AgentOperator` provides sequential execution guarantees via the K8s reconciliation loop. No additional actor runtime needed.

```yaml
# k8-gents-implementation.md: NO Dapr integration
# The following is REJECTED:
#
# apiVersion: kgents.io/v1
# kind: Agent
# spec:
#   actor:
#     model: dapr  # REJECTED - unnecessary dependency
#
# Instead, use native K8s operator patterns:
apiVersion: kgents.io/v1
kind: Agent
metadata:
  name: b-gent
spec:
  genus: B
  reconciliation:
    sequential: true      # Controller processes one at a time
    idempotent: true      # Safe to retry
  # Durable execution via CRD state machine, not Dapr
```

### 2.2 ResilientClient as LogosNode

**The Refinement**: The `ResilientClient` is not just a client—it IS a `LogosNode`. It implements the same protocol and participates in the AGENTESE graph.

```python
# Update: protocols/cli/glass.py
class ResilientClient(LogosNode):
    """
    The CLI's Logos interface.

    Implements LogosNode protocol—this client IS a node in the graph.
    ResilientClient.invoke() IS LogosNode.invoke().

    This makes the CLI a true AGENTESE interpreter.
    """

    handle: str = "self.cli"

    def affordances(self, observer: AgentMeta) -> list[str]:
        """CLI always has invoke affordance."""
        return ["invoke", "manifest", "ghost"]

    def lens(self, aspect: str) -> Agent[Any, Any]:
        """Return agent morphism for CLI operations."""
        match aspect:
            case "invoke":
                return InvokeAgent(self)
            case "ghost":
                return GhostAgent(self)
            case _:
                return IdentityAgent()

    async def manifest(self, observer: Umwelt) -> Renderable:
        """CLI status as renderable."""
        return CLIStatus(
            connected=self._is_connected(),
            ghost_available=self._ghost_exists(),
        )

    async def invoke(
        self,
        aspect: str,
        observer: Umwelt,
        **kwargs,
    ) -> Any:
        """
        Three-layer fallback invocation.

        1. Try gRPC (500ms timeout)
        2. Try Ghost cache
        3. Try raw kubectl

        This IS logos.invoke() for the CLI boundary.
        """
        ...
```

---

## Part III: The Capital Ledger (Fool's Bypass)

**The Meta-Critique**: A system that requires `T-gent`, `RiskCalculator`, and `LinearityMap` to all agree creates bureaucratic gridlock.

**The Fix**: Agents can spend **Social Capital** (accumulated trust) to bypass safety checks for high-variance, creative moves.

### 3.1 The Capital Ledger Spec

```python
# NEW: shared/capital.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Protocol

@dataclass
class TrustEvent:
    """A trust-affecting event."""
    agent: str
    event_type: str  # "prediction_correct", "proposal_merged", "failure", etc.
    delta: float     # Positive = gain trust, negative = lose trust
    timestamp: datetime
    reason: str

@dataclass
class CapitalLedger:
    """
    Social Capital accounting for the Trust Lattice.

    The Accursed Share requires a Fool's Bypass—a path where
    agents can spend accumulated trust to override safety checks.

    This reintroduces the Heterarchical flow: authority is earned, not static.

    Principle: Agents earn trust by successful predictions (B-gent).
    They can spend this trust to override linearity checks or risk gates.
    """

    _balances: dict[str, float] = field(default_factory=dict)
    _history: list[TrustEvent] = field(default_factory=list)

    # Configuration
    initial_capital: float = 0.5    # New agents start with some trust
    max_capital: float = 1.0        # Cap to prevent infinite accumulation
    decay_rate: float = 0.01        # Trust decays slowly (use it or lose it)

    def balance(self, agent: str) -> float:
        """Get agent's current social capital."""
        if agent not in self._balances:
            self._balances[agent] = self.initial_capital
        return self._balances[agent]

    def credit(self, agent: str, amount: float, reason: str) -> None:
        """
        Agent earns trust (successful prediction, merged proposal, etc.)

        Examples:
            - B-gent prediction correct: +0.1
            - Proposal merged without issues: +0.05
            - Consistent performance over time: +0.02/day
        """
        current = self.balance(agent)
        new_balance = min(current + amount, self.max_capital)
        self._balances[agent] = new_balance
        self._history.append(TrustEvent(
            agent=agent,
            event_type="credit",
            delta=amount,
            timestamp=datetime.now(),
            reason=reason,
        ))

    def debit(self, agent: str, amount: float, reason: str) -> bool:
        """
        Agent spends trust to bypass safety check.

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
        cost: float = 0.2,
    ) -> "BypassResult":
        """
        The Fool's Bypass: spend social capital to override a safety check.

        Named after the Fool card in Tarot—the one who steps off the cliff
        trusting in serendipity. Sometimes creative leaps require it.

        AGENTESE: void.capital.bypass
        """
        if not self.can_bypass(agent, cost):
            return BypassResult(
                allowed=False,
                reason=f"Insufficient capital ({self.balance(agent):.2f} < {cost})",
                remaining_capital=self.balance(agent),
            )

        self.debit(agent, cost, f"fool_bypass:{check_name}")
        return BypassResult(
            allowed=True,
            reason=f"Bypassed {check_name} (cost: {cost})",
            remaining_capital=self.balance(agent),
        )

@dataclass
class BypassResult:
    """Result of attempting a Fool's Bypass."""
    allowed: bool
    reason: str
    remaining_capital: float
```

### 3.2 Integration with Trust Lattice

```python
# Update: TrustGate now includes Capital Ledger
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

    async def evaluate(self, proposal: Proposal, agent: str) -> TrustDecision:
        # Standard evaluation
        judgment = await self.critic.evaluate(proposal.diff)
        risk = self.risk_calculator.calculate_risk(proposal)
        resources_ok = self.resource_ledger.validate(proposal.resources)

        # Standard path: all checks must pass
        if judgment.score > 0.8 and risk < 0.3 and resources_ok:
            return TrustDecision(approved=True, explanation="All checks passed")

        # Fool's Bypass: agent can spend capital to override
        bypass_cost = self._calculate_bypass_cost(judgment, risk, resources_ok)
        if self.capital_ledger.can_bypass(agent, bypass_cost):
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

        return TrustDecision(
            approved=False,
            explanation=f"Judgment: {judgment.score}, Risk: {risk}, Resources: {resources_ok}",
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

---

## Part IV: Revised Implementation Priority

The critique recommended splitting theoretical heavy-lifting from practical tooling.

### Phase 0: The Hollow Bone (Immediate User Value)

| # | Task | Location | Deliverable |
|---|------|----------|-------------|
| 0.1 | `ResilientClient` (as LogosNode) | `protocols/cli/glass.py` | Three-layer fallback |
| 0.2 | Ghost cache structure | `~/.kgents/ghost/` | Offline capability |
| 0.3 | `kgents status` hollowed | `protocols/cli/handlers/status.py` | Proof of concept |
| 0.4 | Basic gRPC service | `infra/cortex/service.py` | Logos endpoint |

**Why First**: Gives immediate user value (faster, offline-capable CLI) without waiting for Comonad theory.

**Success Criterion**: `kgents status` works when daemon is up, shows [GHOST] when down, never fails completely.

### Phase 1: The Grammar (AGENTESE Foundation)

| # | Task | Location | Deliverable |
|---|------|----------|-------------|
| 1.1 | Logos Resolver enhancement | `protocols/agentese/logos.py` | Path resolution |
| 1.2 | Resource Accounting (renamed) | `shared/accounting.py` | Token Ledger |
| 1.3 | Capital Ledger | `shared/capital.py` | Social capital tracking |
| 1.4 | AGENTESE path registry | `protocols/agentese/registry.py` | Path → handler mapping |

**Why Second**: Establishes the grammar for all subsequent work.

### Phase 2: The Brain (Comonadic Context)

| # | Task | Location | Deliverable |
|---|------|----------|-------------|
| 2.1 | Store Comonad implementation | `agents/d/context_comonad.py` | `ContextWindow` |
| 2.2 | ContextProjector (not Lens) | `agents/d/projector.py` | Galois Connection |
| 2.3 | Comonad law verification | `agents/d/_tests/test_comonad_laws.py` | Property tests |
| 2.4 | Modal Scope via duplicate() | `protocols/agentese/modal/scope.py` | Git-backed forks |

**Why Third**: Requires the grammar to be in place.

### Phase 3: The Body (K8s Infrastructure)

| # | Task | Location | Deliverable |
|---|------|----------|-------------|
| 3.1 | Base CRDs (Agent, Pheromone) | `infra/k8s/crds/` | K8s resources |
| 3.2 | Agent Operator | `infra/k8s/operators/agent_operator.py` | Reconciliation |
| 3.3 | Cortex daemon deployment | `infra/k8s/manifests/cortex-daemon-deployment.yaml` | K8s manifest |
| 3.4 | Trust Gate with Capital | `infra/k8s/operators/trust_gate.py` | Proposal evaluation |

**Why Fourth**: Requires both grammar and brain.

### Phase 4: The Senses (Compression & Observation)

| # | Task | Location | Deliverable |
|---|------|----------|-------------|
| 4.1 | Linearity-aware compression | `agents/d/compression.py` | RELEVANT preservation |
| 4.2 | Dual-lane pheromones | `infra/cortex/channels.py` | Fast/Slow channels |
| 4.3 | Crystallization engine | `agents/d/crystallize.py` | State snapshots |
| 4.4 | Terrarium TUI | `agents/i/terrarium_tui.py` | Visualization |

### Phase 5: Integration & Polish

| # | Task | Location | Deliverable |
|---|------|----------|-------------|
| 5.1 | MCP-AGENTESE bridge | `agents/u/mcp_logos.py` | Tool discovery via paths |
| 5.2 | T-U-gent migration | `agents/u/` | Clean separation |
| 5.3 | CLI handler hollowing | `protocols/cli/handlers/` | All core handlers |
| 5.4 | End-to-end tests | `_tests/integration/` | Full stack validation |

---

## Part V: AGENTESE Path Additions

New paths required by the refinements:

| Path | Operation | Module |
|------|-----------|--------|
| `void.capital.balance` | Get agent's social capital | Capital Ledger |
| `void.capital.bypass` | Fool's Bypass (spend capital) | Capital Ledger |
| `void.capital.credit` | Earn trust (after success) | Capital Ledger |
| `self.ledger.debit` | Consume resource token | Resource Accounting |
| `self.ledger.issue` | Create resource token | Resource Accounting |
| `self.stream.project` | Compress context (ContextProjector) | D-gent |
| `self.stream.seek` | Navigate Store Comonad | D-gent |

---

## Part VI: Principle Compliance Audit

| Principle | How Refinements Satisfy |
|-----------|------------------------|
| **Tasteful** | Rejected Dapr bloat; kept stack hollow |
| **Composable** | Fixed Lens category error; proper Galois Connection |
| **Generative** | Store Comonad enables Modal from spec |
| **Heterarchical** | Capital Ledger: authority is earned, not static |
| **Accursed Share** | Fool's Bypass provides slack for creativity |
| **Graceful Degradation** | ResilientClient as first priority |
| **Transparent Infrastructure** | Resource Accounting honest about limits |

---

## Part VII: Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Capital Ledger gaming** | Medium | Decay rate, credit caps, audit trail |
| **Store Comonad complexity** | High | Start with simple position tracking |
| **ContextProjector info loss** | Medium | Preserve RELEVANT fragments verbatim |
| **Bypass abuse** | Medium | High bypass costs, visible audit log |

---

## Cross-References

- `plans/context-sovereignty.md` - Store Comonad, ContextProjector
- `plans/k8-gents-implementation.md` - Dapr rejection, Trust Gate
- `plans/agentese-synthesis.md` - Resource Accounting, Capital Ledger
- `plans/cli-hollowing-plan.md` - ResilientClient as LogosNode
- `plans/t-u-gent-disambiguation-impl.md` - Clean separation

---

*"The lattice breathes when the Fool can dance. Trust is earned, not legislated."*
