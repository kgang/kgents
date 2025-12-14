---
path: agents/t-gent
status: dormant
progress: 90
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Types I-IV complete. Type V (AdversarialGym) remaining.
  U-gent separation complete.
---

# T-gents: Testing Agents (Types I-V)

> *"T-gents are endofunctors on Cat_Agent. They do not leave the category."*

**Status**: Types I-IV Implemented, Type V Planned
**Categorical Role**: `T: Cat_Agent → Cat_Agent` (endofunctor)
**Principles**: Composable, Tasteful
AGENTESE pointer: route any T-gent handles/guards through `spec/protocols/agentese.md` when exposing testing paths; keep clause/law alignment in sync.

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Endofunctor** | T-gents transform agents into test agents, stay in Cat_Agent |
| **Five types** | Nullifiers, Saboteurs, Observers, Critics, Adversarial |
| **Separate from U-gents** | T-gents are internal (testing); U-gents are external (tools) |
| **T-gent webhook** | ValidatingAdmissionWebhook for proposals |

---

## Categorical Distinction

T-gents vs U-gents is a fundamental categorical distinction:

| Property | T-gents | U-gents |
|----------|---------|---------|
| **Functor type** | Endofunctor | Boundary morphism |
| **Domain** | Cat_Agent | Cat_Agent |
| **Codomain** | Cat_Agent | Cat_Tool |
| **Error semantics** | Intentional (sabotage) | External (network, API) |
| **Purpose** | Test behavior | Interface with world |

---

## Type I: Nullifiers (✅ DONE)

Constant functors: `Δ_b: A → b`

```python
# Constant morphism - always returns fixed value
MockAgent      # Δ_b: A → b
FixtureAgent   # Lookup morphism from fixture table
```

**Location**: `agents/t/mock.py`, `agents/t/fixture.py`

---

## Type II: Saboteurs (✅ DONE)

Perturbation functors: `Id + ε`

```python
# Identity with intentional errors
FailingAgent   # ⊥: A → Error (bottom morphism)
NoiseAgent     # Id + ε: A → A (identity with noise)
LatencyAgent   # (A, t) → (A, t + Δ) (temporal delay)
FlakyAgent     # A → B | Error (probabilistic)
```

**Location**: `agents/t/failing.py`, `agents/t/noise.py`, etc.

---

## Type III: Observers (✅ DONE)

Identity with side effects: `Id ⊗ log`

```python
# Identity + observation
SpyAgent       # Id ⊗ log: A → A (identity + logging)
PredicateAgent # Gate: A → A | Error (predicate filter)
CounterAgent   # Id ⊗ count: A → A (identity + counting)
MetricsAgent   # Id ⊗ metrics: A → A (identity + metrics)
```

**Location**: `agents/t/spy.py`, `agents/t/predicate.py`, etc.

---

## Type IV: Critics (✅ DONE)

Higher-order evaluation functors:

```python
# Evaluate agent behavior
JudgeAgent     # (A, B) → Score (input/output evaluation)
PropertyAgent  # Agent → Bool (property verification)
OracleAgent    # A → B_expected (ground truth)
```

**Location**: `agents/t/judge.py`, `agents/t/property.py`, etc.

---

## Type V: Adversarial (📋 PLANNED)

Composition of Types I-IV: `∐(Noise × Fail × Latency × Drift)`

```python
@dataclass
class StressCoordinate:
    """A point in the stress-test space."""
    noise: float       # 0.0 - 1.0
    failure: float     # Probability of FailingAgent injection
    latency: float     # Max latency to inject (ms)
    drift: float       # Semantic drift factor


class AdversarialGym:
    """
    Monte Carlo stress testing via T-gent composition.

    The Gym is a functor:
        Gym: Agent → GymReport

    It composes the agent under test with random T-gents
    from Types I-IV and measures resilience.
    """

    async def stress_test(
        self,
        agent: Agent[A, B],
        coordinates: list[StressCoordinate],
        iterations: int = 100,
    ) -> GymReport:
        """Run Monte Carlo stress testing."""
        ...
```

**Location**: `agents/t/adversarial.py` (planned)

---

## T-gent Webhook

T-gents serve as the immune system via ValidatingAdmissionWebhook:

```
Proposal CR → K8s API → T-gent Webhook → ALLOW/DENY
                              │
                    ┌─────────┴─────────┐
                    │ FAST PATH (CEL)   │ SLOW PATH (LLM)
                    │ • No root access  │ • Constitution
                    │ • Resource limits │ • Intent check
                    └───────────────────┘
```

---

## Functor Laws

T-gents must satisfy functor laws:

```python
# Identity law: Spy is transparent
assert (spy >> f).invoke(x) == f.invoke(x)

# Composition law: Mock composes
assert (mock >> f >> g).invoke(x) == (mock >> (f >> g)).invoke(x)

# Perturbation law: Zero noise = identity
assert NoiseAgent(ε=0) ≡ Identity
```

---

## Public API

```python
# agents/t/__init__.py

# Type I - Nullifiers
from .mock import MockAgent, MockConfig
from .fixture import FixtureAgent, FixtureConfig

# Type II - Saboteurs
from .failing import FailingAgent, FailingConfig, FailureType
from .noise import NoiseAgent, NoiseConfig, NoiseType
from .latency import LatencyAgent
from .flaky import FlakyAgent

# Type III - Observers
from .spy import SpyAgent
from .predicate import PredicateAgent
from .counter import CounterAgent
from .metrics import MetricsAgent

# Type IV - Critics
from .judge import JudgeAgent, JudgmentCriteria
from .property import PropertyAgent
from .oracle import OracleAgent

# Type V - Adversarial (planned)
# from .adversarial import AdversarialGym, StressCoordinate
```

---

## Cross-References

- **Plans**: `agents/u-gent.md` (Tool use separation), `world/k8-gents.md` (Webhook)
- **Impl**: `agents/t/` (current implementation)
- **Spec**: `spec/t-gents/README.md`

---

*"T-gents test the system. They do not leave it."*
