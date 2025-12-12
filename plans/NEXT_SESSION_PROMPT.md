# Next Session: Phase 1 Implementation (Principles-Aligned)

> **For Claude**: This is your context prompt. Read this first, then execute.
> **Last Revised**: 2025-12-11 (Alignment analysis with spec/principles.md)

---

## Session Context

Plans have been reorganized into AGENTESE-friendly structure at `plans/`. Phase 0 (CLI Hollowing) is complete. Begin Phase 1 (Grammar/Accounting).

**Core Insight** (AGENTESE Meta-Principle):

> "The noun is a lie. There is only the rate of change."
> "Do not build a bank (database of numbers). Build a flow system (stream of events)."

---

## Principles Applied to Phase 1

Before implementation, understand which principles govern each decision:

| Design Decision | Principle | Why It Matters |
|-----------------|-----------|----------------|
| Event-Sourced Ledger | **AGENTESE** (Verb-First) | Balance is projection, not storage. Events ARE the truth. |
| Context Managers | **Joy-Inducing** | Pythonic patterns over fighting the type system. |
| OCap BypassToken | **AGENTESE** (No View From Nowhere) | Gate accepts TOKEN, not agent name string. |
| Algebraic Cost Functions | **Composable** | Costs compose: `A + B`, `0.5 * A`. No ad-hoc formulas. |
| Append-Only Events | **Heterarchical** | No race conditions. Authority earned through events. |
| Configurable Decay | **Accursed Share** | Start simple (0.01), observe patterns. Wealth that isn't spent will consume the community. |
| Reject Phantom Types | **Joy-Inducing** | Don't fight Python. Delight, not frustration. |
| Dependency Injection | **Composable** + **Testable** | Ledger passed to Logos. Fresh fixtures per test. |

---

## Design Decisions (Refined)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Ledger Architecture** | Event-Sourced | Balance is derived, not stored. Aligns with AGENTESE verb-first ontology. |
| **Token Lifecycle** | Context Managers | Pythonic linearity approximation. `with ledger.issue(...) as budget:` |
| **Capital as Capability** | OCap Pattern | BypassToken is an unforgeable object, not a balance check |
| **Cost Functions** | Algebraic Composition | Composable cost factors: `COST = BASE + RISK_PREMIUM + JUDGMENT_DEFICIT` |
| **Concurrency** | Append-Only Events | No race conditions. Events appended atomically. |
| **Decay Rate** | 0.01 (Configurable) | Start simple, observe patterns |
| **Phantom Types** | REJECTED | Fighting Python's type system violates Joy-Inducing |

---

## Scope Boundaries (Curated Principle)

**"Better to have 10 excellent things than 100 mediocre ones."**

### In Scope (Phase 1)

- `EventSourcedLedger` with `balance()`, `credit()`, `debit()`, `witness()`, `potlatch()`
- `BypassToken` (OCap capability)
- `CostFactor` with algebraic composition (`__add__`, `__mul__`)
- `ResourceBudget` with context manager lifecycle
- AGENTESE path registration for `void.capital.*`
- Property-based tests for ledger invariants
- Unit tests for cost algebra

### NOT Now (Explicit Deferral)

| Item | Why Deferred | When |
|------|--------------|------|
| Activity-based decay | Need data before committing to model | After Phase 1 metrics |
| `TrustGate` integration | Depends on capital.py being stable | Phase 2 |
| CLI `kgents capital *` commands | Need ledger working first | After core tests pass |
| Metabolism/FeverStream | Separate void context | Phase 1.3 |
| Persistent ledger storage | In-memory sufficient for now | Phase 3 |
| Decay scheduler | Manual decay for testing | Phase 3 |

**Anti-pattern to avoid**: "While I'm here, let me also add X." Resist. If it's not in scope, it waits.

---

## Critical Concerns Addressed

### 1. Ledger Concurrency (CRITICAL - SOLVED)

**Problem**: Race conditions with mutable balance state.

**Solution**: Event sourcing. Append-only log. Balance computed from events.

```python
def balance(self, agent: str) -> float:
    """Derived from events, never stored directly."""
    total = self.initial_capital
    for event in self._events:
        if event.agent == agent:
            if event.is_credit():
                total += event.amount
            elif event.is_debit():
                total -= event.amount
    return min(max(0, total), self.max_capital)
```

### 2. ResourceToken Linearity (CRITICAL - SOLVED)

**Problem**: Python GC makes `__del__` unreliable. No compile-time linearity.

**Solution**: Context managers enforce scope via syntax.

```python
with issue_budget(ledger, agent, 100) as budget:
    budget.spend(50)
# Budget automatically settled on exit
```

### 3. Test Environment Isolation (HIGH - SOLVED)

**Problem**: Shared state causes test pollution.

**Solution**: Dependency injection. Ledger passed to Logos, not global.

```python
@pytest.fixture
def ledger() -> EventSourcedLedger:
    """Fresh ledger per test—no shared state."""
    return EventSourcedLedger()
```

---

## Graceful Degradation (Operational Principle)

Each component must specify its fallback behavior:

| Component | Degradation Mode | User-Visible Signal |
|-----------|------------------|---------------------|
| `EventSourcedLedger` | In-memory only (no persistence) | Default behavior—no signal needed |
| `BypassToken` | Expired tokens fail gracefully | `bypass_token.is_valid()` returns False |
| `CostFactor` | Cannot degrade (pure computation) | N/A |
| `issue_budget` | Raises `InsufficientCapitalError` | Clear error message with balance info |

**Principle**: Never fail silently. If degraded, signal it. If failing, explain why.

---

## System Voice (Joy-Inducing Principle)

The system has a personality. Even mundane operations should feel considered.

| Context | Voice Example | Anti-Pattern |
|---------|---------------|--------------|
| Success | `b-gent: 0.72 (ceiling: 1.0)` | `{"balance": 0.72, "max": 1.0}` |
| Insufficient funds | `b-gent lacks 0.3 capital (current: 0.2)` | `Error: balance too low` |
| First run | `[kgents] Ledger initialized. All agents start with 0.5 trust.` | (silent) |
| Potlatch | `Potlatch complete. 0.1 returned to the void. Remaining: 0.62` | `Debit: 0.1` |

**Personality Space Coordinates**: Warm but precise. Never robotic, never saccharine. The system has quiet confidence.

---

## Implementation Status

### Phase 0: CLI Hollowing (COMPLETE)
- `GlassClient` with three-layer fallback
- `CortexServicer` gRPC service
- Hollowed handlers, K8s CRDs

### Phase 1: Grammar (NEXT)

Priority order (follow strictly):

1. **Event-Sourced Ledger** (`shared/capital.py`)
   - `LedgerEvent` (frozen dataclass)
   - `EventSourcedLedger` with `balance()`, `credit()`, `debit()`, `witness()`, `potlatch()`
   - `BypassToken` (OCap capability)
   - `mint_bypass()` for Fool's Bypass

2. **Algebraic Cost Functions** (`shared/costs.py`)
   - `CostFactor` with `__add__`, `__mul__`
   - `CostContext` dataclass
   - Standard factors: `BASE_COST`, `RISK_PREMIUM`, `JUDGMENT_DEFICIT`, `RESOURCE_PENALTY`
   - Composed: `BYPASS_COST = BASE + 0.1 * RISK_PREMIUM + 0.1 * JUDGMENT_DEFICIT + RESOURCE_PENALTY`

3. **Resource Budget** (`shared/budget.py`)
   - `ResourceBudget` class
   - `issue_budget()` context manager
   - Automatic settlement on exit

4. **AGENTESE Path Registry** (`protocols/agentese/registry.py`)
   - `void.capital.manifest` -> `ledger.balance()`
   - `void.capital.witness` -> `ledger.witness()`
   - `void.capital.tithe` -> `ledger.potlatch()`
   - `void.capital.bypass` -> `ledger.mint_bypass()`

---

## Key Files to Create

```
impl/claude/shared/
├── __init__.py
├── capital.py         # EventSourcedLedger, LedgerEvent, BypassToken
├── costs.py           # CostFactor, CostContext, standard factors
└── budget.py          # ResourceBudget, issue_budget context manager

impl/claude/shared/_tests/
├── __init__.py
├── test_capital.py    # Event sourcing, bypass, potlatch
├── test_costs.py      # Cost algebra, composition
└── test_budget.py     # Context manager lifecycle
```

---

## Implementation Snippets

### Immutable Events

```python
@dataclass(frozen=True)
class LedgerEvent:
    """Immutable. Events are the source of truth."""
    event_type: EventType
    agent: str
    amount: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)
```

### Composable Cost Functions

```python
@dataclass
class CostFactor:
    name: str
    compute: Callable[[CostContext], float]

    def __add__(self, other: CostFactor) -> CostFactor:
        return CostFactor(
            name=f"{self.name}+{other.name}",
            compute=lambda ctx: self.compute(ctx) + other.compute(ctx),
        )

    def __mul__(self, scalar: float) -> CostFactor:
        return CostFactor(
            name=f"{scalar}*{self.name}",
            compute=lambda ctx: scalar * self.compute(ctx),
        )
```

### OCap Bypass Token

```python
@dataclass(frozen=True)
class BypassToken:
    """Unforgeable capability token. Gate accepts token, not agent name."""
    agent: str
    check_name: str
    granted_at: datetime
    expires_at: datetime
    cost: float
    correlation_id: str

    def is_valid(self) -> bool:
        return datetime.utcnow() < self.expires_at
```

---

## Testing Requirements

### Commands After Implementation

```bash
cd impl/claude
pytest shared/_tests/ -v
uv run mypy --strict --explicit-package-bases shared/
```

### Property-Based Tests (Generative Principle)

Property tests ARE regeneration validators. If the spec is correct, any implementation satisfying these properties is valid:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.tuples(
    st.sampled_from(["CREDIT", "DEBIT"]),
    st.floats(min_value=0, max_value=1),
)))
def test_balance_is_projection(events):
    """
    GENERATIVE PRINCIPLE: This test verifies the spec, not the implementation.
    Any correct implementation will satisfy: balance = sum(credits) - sum(debits)
    """
    # Event sourcing invariant
```

### Specific Tests (Checklist)

- [ ] Balance is derived projection (not stored)
- [ ] Events are immutable (`frozen=True`)
- [ ] Bypass token expires after TTL
- [ ] Cost functions compose algebraically (`(A + B)(ctx) == A(ctx) + B(ctx)`)
- [ ] Context manager settles budget on exit (even on exception)
- [ ] Fresh ledger per test (no pollution)
- [ ] InsufficientCapitalError has informative message

---

## AGENTESE Integration

| Path | Handler | Implementation |
|------|---------|----------------|
| `void.capital.manifest` | `balance()` | Projection from events |
| `void.capital.witness` | `witness()` | Returns event stream |
| `void.capital.tithe` | `potlatch()` | Burns capital (Accursed Share) |
| `void.capital.bypass` | `mint_bypass()` | Returns BypassToken capability |

---

## Plan References

| Topic | Plan File |
|-------|-----------|
| Event-Sourced Ledger | `plans/void/capital.md` |
| Cost Functions | `plans/void/capital.md` |
| Resource Accounting | `plans/self/stream.md` |
| Status Matrix | `plans/_status.md` |
| Decision Log | `plans/README.md` |
| **Design Principles** | `spec/principles.md` |

---

## Validation Checklist

After Phase 1 implementation:

- [ ] `shared/capital.py` with `EventSourcedLedger`, `LedgerEvent`, `BypassToken`
- [ ] `shared/costs.py` with composable `CostFactor`
- [ ] `shared/budget.py` with `issue_budget` context manager
- [ ] Property-based tests for ledger invariants
- [ ] Tests pass, mypy strict passes
- [ ] `plans/_status.md` updated
- [ ] No scope creep (check "NOT Now" list)

---

## Phase 2 Preview (After Phase 1)

Store Comonad implementation:
- `agents/d/context_comonad.py`: `ContextWindow` with extract/extend/duplicate
- `agents/d/projector.py`: `ContextProjector` (Galois Connection)
- Git-backed Modal Scope via `duplicate()` + branch isolation

**Forensic Trace requirement** (Transparent Infrastructure):
- JIT-compiled agents must dump source to `time.trace.{hash}` before execution
- Errors reference trace for debugging

**Y-gent/D-gent/Git Layering** (Puppet Construction):
- Git = Puppet (raw machinery for branching realities)
- D-gent = Lens (reads/writes Git branch as coherent State)
- Y-gent = Weaver (decides when to branch/merge)
- Document patterns as they emerge; implementer discretion on specifics

---

## Start Here

```bash
# 1. Verify Phase 0 complete
ls -la impl/claude/protocols/cli/glass.py

# 2. Create shared module
mkdir -p impl/claude/shared/_tests
touch impl/claude/shared/__init__.py

# 3. Implement in order:
#    - capital.py (EventSourcedLedger, LedgerEvent, BypassToken)
#    - costs.py (CostFactor, standard factors)
#    - budget.py (ResourceBudget, issue_budget)

# 4. Run tests
cd impl/claude && pytest shared/_tests/ -v
```

**Delete this file after completing Phase 1.**

---

*"The river that flows only downhill never discovers the mountain spring."*
