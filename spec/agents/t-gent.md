# T-gent: The Testing Agent

> *"Testing is algebraic verification, not just examples."*

**Status**: Canonical | **Layer**: Infrastructure | **Impl**: `impl/claude/agents/t/` (45 tests)

---

## Purpose

T-gent provides category theory-based verification agents for testing kgents components. T-gents prove algebraic properties (associativity, identity, resilience) rather than just validating examples. All T-gents are marked with `__is_test__ = True` and compose with other agents via `>>` operator.

---

## Core Insight

**Verification is a value function.** Every probe solves the Bellman equation:

```
V*(s) = max_a [R(s,a) + γ · V*(T(s,a))]
```

Traditional testing asks: "Does this pass?" TruthFunctors ask: "What is the optimal verification strategy and its expected value?"

---

## Type Signatures

### TruthFunctor Protocol

All T-gents implement the TruthFunctor protocol with DP-native semantics:

```python
@dataclass(frozen=True)
class TruthFunctor(Generic[S, A, B], Protocol):
    """
    Base protocol for verification probes.

    Params:
        S: State space (probe-specific states)
        A: Input domain
        B: Output domain
    """
    # DP Components
    states: FrozenSet[S]                              # State space
    actions: FrozenSet[ProbeAction]                   # Action space
    transition: Callable[[S, A], S]                   # T(s,a) → s'
    reward: Callable[[S, A], ConstitutionalScore]     # R(s,a)
    gamma: float = 0.95                               # Discount factor
    mode: AnalysisMode                                # CATEGORICAL | EPISTEMIC | DIALECTICAL | GENERATIVE

    # Verification
    async def verify(self, agent: Callable[[A], B], input: A) -> PolicyTrace[B]

    # Law validation
    def satisfies(self, law: Law) -> bool
```

### PolicyTrace (Writer Monad)

Accumulated verification trace with constitutional scoring:

```python
@dataclass
class PolicyTrace(Generic[B]):
    """Writer monad for verification traces."""
    value: TruthVerdict[B]           # Final verdict
    entries: list[TraceEntry]        # State-action-reward sequence
    total_reward: float              # Σ γ^t · R(s_t, a_t)

@dataclass
class TruthVerdict(Generic[B]):
    value: B                         # Actual output
    passed: bool                     # Did verification succeed?
    confidence: float                # [0, 1] confidence
    reasoning: str                   # Rationale
```

### ConstitutionalScore

Rewards based on kgents' seven principles:

```python
@dataclass
class ConstitutionalScore:
    """Reward scoring based on constitutional principles."""
    tasteful: float       # [0, 1] - clear purpose, justified design
    curated: float        # [0, 1] - intentional selection
    ethical: float        # [0, 1] - augments humans, preserves judgment
    joy_inducing: float   # [0, 1] - delightful interaction
    composable: float     # [0, 1] - morphism laws satisfied
    heterarchical: float  # [0, 1] - flux, not fixed hierarchy
    generative: float     # [0, 1] - compressed specification

    @property
    def total(self) -> float:
        """Sum of all principles."""
        return sum([
            self.tasteful, self.curated, self.ethical,
            self.joy_inducing, self.composable,
            self.heterarchical, self.generative
        ])
```

---

## The Five Probe Types

T-gent defines five canonical probe types, each with distinct AnalysisMode:

| Probe | Mode | Purpose | Replaces |
|-------|------|---------|----------|
| **NullProbe** | EPISTEMIC | Constant morphism c_b: A → b (ground truth baseline) | MockAgent, FixtureAgent |
| **ChaosProbe** | DIALECTICAL | Perturbation injection (failures, noise, latency, flakiness) | FailingAgent, NoiseAgent, LatencyAgent, FlakyAgent |
| **WitnessProbe** | CATEGORICAL | Law validation (identity, associativity, functor laws) | SpyAgent, CounterAgent, MetricsAgent |
| **JudgeProbe** | EPISTEMIC | Semantic evaluation (LLM-as-judge, oracles, property tests) | JudgeAgent, PropertyAgent, OracleAgent |
| **TrustProbe** | GENERATIVE | Capital-backed gating with Fool's Bypass (OCap pattern) | TrustGate |

### Example: NullProbe

```python
from agents.t.probes import NullProbe

# Constant morphism for differential testing
probe = NullProbe(constant="expected_output", delay_ms=50)
trace = await probe.verify(agent, "any_input")

assert trace.value.value == "expected_output"
assert trace.value.passed is True
assert trace.total_reward > 0  # Constitutional scoring
```

### Example: WitnessProbe

```python
from agents.t.probes import WitnessProbe, IDENTITY_LAW, ASSOCIATIVITY_LAW

# Verify categorical laws
probe = WitnessProbe(laws=[IDENTITY_LAW, ASSOCIATIVITY_LAW])
trace = await probe.verify(f, x)

# Check law satisfaction
assert probe.satisfies(IDENTITY_LAW)
assert len(probe.history) > 0  # Trace captured
```

---

## ProbeOperad: Composition Grammar

T-gents compose via the ProbeOperad, which defines five operations with Bellman semantics:

### Operations

| Operation | Signature | DP Semantics | Use Case |
|-----------|-----------|--------------|----------|
| **seq** | `Probe × Probe → Probe` | `V(p>>q) = R(p) + γ·V(q)` | Sequential verification (run identity, then associativity) |
| **par** | `Probe × Probe → Probe` | `V(p‖q) = max(V(p), V(q))` | Parallel strategies (fast vs thorough) |
| **branch** | `Pred × Probe × Probe → Probe` | `V = P·V(left) + (1-P)·V(right)` | Conditional verification (if complex, use expensive probe) |
| **fix** | `Probe → Probe` | `V = lim_{n→∞} Vⁿ` | Fixed-point iteration (convergence testing) |
| **witness** | `Probe → Probe` | Adds PolicyTrace wrapping | Explicit trace emission |

### Composition Example

```python
from agents.operad.domains.probe import PROBE_OPERAD

# Compose verification strategy
full_check = PROBE_OPERAD.seq(
    NullProbe(constant=baseline),           # Baseline verification
    WitnessProbe(laws=[IDENTITY_LAW])       # Then law validation
)

# Parallel strategies
best_effort = PROBE_OPERAD.par(
    fast_probe,      # Quick heuristic
    thorough_probe   # Exhaustive verification
)

result = await full_check.verify(agent, input)
```

---

## Laws/Invariants

### ProbeOperad Laws

1. **Associativity**: `(p >> q) >> r ≡ p >> (q >> r)`
2. **Identity**: `Id >> p ≡ p ≡ p >> Id` where `Id = NullProbe(identity_fn)`
3. **Commutativity (parallel)**: `p ‖ q ≡ q ‖ p`
4. **Witness Transparency**: `witness(p).verify(...).value.value ≡ p.verify(...).value.value`

### TruthFunctor Laws

1. **Functor Composition**: `F(g ∘ f) = F(g) ∘ F(f)`
2. **Functor Identity**: `F(id) = id`
3. **Monotonicity**: If `p ⊆ q` then `V(p) ≤ V(q)`
4. **Bellman Optimality**: Composed probes satisfy Bellman equation

---

## Integration

### AGENTESE Paths

T-gents are infrastructure—not exposed via AGENTESE. They are testing tools consumed by other agents.

### Composition with Other Agents

```python
from agents.t import NullProbe, WitnessProbe
from agents.a import PolyAgent

# Test a polynomial agent
agent = PolyAgent(...)
probe = WitnessProbe(laws=[IDENTITY_LAW])

# Verify agent satisfies categorical laws
trace = await probe.verify(agent.invoke, test_input)
assert trace.value.passed
```

### Test Helpers

```python
from agents.t.helpers import (
    assert_functor_identity,
    assert_functor_composition,
    assert_composition_associative,
)

# Categorical property verification
assert_functor_identity(my_agent)
assert_functor_composition(my_agent, f, g, x)
assert_composition_associative(p, q, r, x)
```

---

## Anti-Patterns

1. **Don't use T-gents for production logic**: T-gents are testing infrastructure (`__is_test__ = True`). Use them in test suites, not application code.

2. **Don't bypass TruthFunctor protocol**: Legacy types (MockAgent, FailingAgent, etc.) are deprecated. All new testing code should use the five canonical probes.

3. **Don't ignore PolicyTrace**: The trace contains constitutional scores and reasoning. Use it for debugging and understanding verification failures.

4. **Don't compose without operad**: Manual composition bypasses DP semantics. Use `PROBE_OPERAD.seq()`, `.par()`, etc. for principled composition.

5. **Don't test without laws**: T-gents verify algebraic properties. If you're just checking examples without categorical laws, you're missing the point.

---

## Deprecated (Removed 2025-12-25)

The following legacy types were removed during the cleanup:

### Zombie Compatibility Layer (12 classes removed)

All deprecated wrappers in `compat.py` that provided backwards compatibility with pre-TruthFunctor API:

- `MockAgent` → Use `NullProbe`
- `FixtureAgent` → Use `NullProbe` with fixture pattern
- `FailingAgent` → Use `ChaosProbe(chaos_type=ChaosType.FAILURE)`
- `NoiseAgent` → Use `ChaosProbe(chaos_type=ChaosType.NOISE)`
- `LatencyAgent` → Use `ChaosProbe(chaos_type=ChaosType.LATENCY)`
- `FlakyAgent` → Use `ChaosProbe(chaos_type=ChaosType.FLAKINESS)`
- `SpyAgent` → Use `WitnessProbe`
- `PredicateAgent` → Use `WitnessProbe` with predicate
- `CounterAgent` → Use `WitnessProbe` (check `len(probe.history)`)
- `MetricsAgent` → Use `WitnessProbe` (analyze trace entries)
- `JudgeAgent` → Use `JudgeProbe`
- `OracleAgent` → Use `JudgeProbe` with oracle function

**Why removed**: These wrappers bypassed the TruthFunctor protocol, emitted deprecation warnings, and maintained zombie code paths. All functionality now unified under five canonical probe types.

### Stub Probes (Removed)

- `null_probe_fixed.py`: Duplicate implementation that bypassed real NullProbe
- Stub implementations in `compat.py`: Fake ChaosProbe, JudgeProbe, TrustProbe that returned hardcoded results

**Why removed**: Tests must use real probe implementations to validate actual behavior.

### Legacy law_validator.py (Removed)

**Migration**: All law validation functionality moved to `WitnessProbe`:

```python
# Old (law_validator.py)
from agents.t.law_validator import assert_identity_law
assert_identity_law(agent, x)

# New (WitnessProbe)
from agents.t.probes import WitnessProbe, IDENTITY_LAW
probe = WitnessProbe(laws=[IDENTITY_LAW])
trace = await probe.verify(agent, x)
assert trace.value.passed
```

---

## Implementation Reference

See: `impl/claude/agents/t/`

Key files:
- `truth_functor.py`: TruthFunctor protocol, PolicyTrace, ConstitutionalScore
- `probes/null_probe.py`: Constant morphism (EPISTEMIC mode)
- `probes/witness_probe.py`: Law validation (CATEGORICAL mode)
- `probes/chaos_probe.py`: Perturbation injection (DIALECTICAL mode)
- `probes/judge_probe.py`: Semantic evaluation (EPISTEMIC mode)
- `probes/trust_probe.py`: Capital-backed gating (GENERATIVE mode)
- `helpers.py`: Convenience functions for categorical property testing
- `compat.py`: Backwards compatibility layer (DEPRECATED, emits warnings)

Operad:
- `agents/operad/domains/probe.py`: PROBE_OPERAD definition
- `agents/operad/domains/PROBE_OPERAD_README.md`: Full operad documentation

Theoretical foundations:
- `spec/t-gents/algebra.md`: ProbeOperad mathematical foundations
- `spec/theory/dp-native-kgents.md`: DP semantics for agents

---

*"The proof IS the decision. The mark IS the witness. The value IS the composition."*
