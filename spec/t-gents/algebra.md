# TruthFunctor Algebra: ProbeOperad & DP Foundations

Mathematical foundations for TruthFunctors through Dynamic Programming and Category Theory.

---

## The Paradigm Shift

**Traditional**: `test(agent, input) → {pass, fail}`

**TruthFunctor**: `verify(agent, state) → PolicyTrace[value, rationale]`

Every verification solves: `V*(s) = max_a [R(s,a) + γ · V*(T(s,a))]`

---

## Part I: The ProbeOperad

### Definition

The **ProbeOperad** defines how TruthFunctors compose:

```python
PROBE_OPERAD = Operad(
    name="ProbeOperad",
    operations={
        "seq": (Probe[A,B], Probe[B,C]) → Probe[A,C],      # Sequential
        "par": (Probe[A,B], Probe[A,C]) → Probe[A,max(B,C)],  # Parallel
        "branch": (Cond, Probe[A,B], Probe[A,B]) → Probe[A,B], # Conditional
        "fix": Probe[A,A] → Probe[A,A],                     # Fixed-point
        "witness": Probe[A,B] → Probe[A,(B,PolicyTrace)],   # Trace emission
    },
    laws=[associativity, identity, commutativity, witness_transparency],
)
```

---

### Operations as DP Primitives

#### seq: Sequential Composition (Bellman Chaining)

**Category Theory**: Morphism composition in `C_Agent`

**DP Interpretation**: Sequential decision-making via Bellman equation

```python
def seq(p1: Probe[A, B], p2: Probe[B, C]) -> Probe[A, C]:
    """V_seq(s) = R₁(s,a₁) + γ · V₂(T₁(s,a₁))"""
    async def composed_value(state: A) -> PolicyTrace[C]:
        trace1 = await p1.value(state)
        trace2 = await p2.value(trace1.states[-1])

        total_value = trace1.value + p1.gamma * trace2.value

        return PolicyTrace(
            states=trace1.states + trace2.states[1:],
            actions=trace1.actions + trace2.actions,
            rewards=trace1.rewards + trace2.rewards,
            rationales=trace1.rationales + trace2.rationales,
            value=total_value,
        )
    return Probe(name=f"{p1.name} >> {p2.name}", value=composed_value)
```

**Bellman Equation**: `V*(s) = R(s,a₁) + γ·V*(T(s,a₁))`

---

#### par: Parallel Composition (Value Maximization)

**Category Theory**: Product in `C_Agent`

**DP Interpretation**: Execute both, select max value

```python
def par(p1: Probe[A, B], p2: Probe[A, C]) -> Probe[A, Union[B, C]]:
    """V_par(s) = max(V₁(s), V₂(s))"""
    async def parallel_value(state: A) -> PolicyTrace:
        trace1, trace2 = await asyncio.gather(p1.value(state), p2.value(state))
        return trace1 if trace1.value >= trace2.value else trace2
    return Probe(name=f"{p1.name} ‖ {p2.name}", value=parallel_value)
```

**Value Equation**: `V*(s) = max(V₁(s), V₂(s))`

---

#### branch: Conditional Composition (Expected Value)

**Category Theory**: Coproduct in `C_Agent`

**DP Interpretation**: Probabilistic action selection

```python
def branch(
    condition: Callable[[A], float],  # Probability ∈ [0,1]
    p1: Probe[A, B],
    p2: Probe[A, B]
) -> Probe[A, B]:
    """V_branch(s) = P(c)·V₁(s) + (1-P(c))·V₂(s)"""
    async def branching_value(state: A) -> PolicyTrace[B]:
        prob = condition(state)
        trace1, trace2 = await asyncio.gather(p1.value(state), p2.value(state))

        expected_value = prob * trace1.value + (1 - prob) * trace2.value
        selected_trace = trace1 if random.random() < prob else trace2

        return PolicyTrace(
            states=selected_trace.states,
            actions=selected_trace.actions,
            rewards=selected_trace.rewards,
            rationales=(f"Branch(P={prob:.2f})",) + selected_trace.rationales,
            value=expected_value,
        )
    return Probe(name=f"if ? {p1.name} : {p2.name}", value=branching_value)
```

**Expected Value**: `V*(s) = Σₐ π(a|s)·[R(s,a) + γ·V*(T(s,a))]`

---

#### fix: Fixed-Point Composition (Value Iteration)

**Category Theory**: Lawvere fixed-point theorem

**DP Interpretation**: Iterative value refinement

```python
def fix(p: Probe[A, A], max_iters: int = 100, epsilon: float = 1e-6) -> Probe[A, A]:
    """V_{k+1}(s) = R(s,a) + γ·V_k(T(s,a))"""
    async def fixed_point_value(state: A) -> PolicyTrace[A]:
        prev_value = 0.0
        current_state = state

        for iteration in range(max_iters):
            trace = await p.value(current_state)
            current_state = trace.states[-1]

            if abs(trace.value - prev_value) < epsilon:
                return trace  # Converged
            prev_value = trace.value

        raise ValueError(f"No convergence after {max_iters} iterations")
    return Probe(name=f"fix({p.name})", value=fixed_point_value)
```

**Value Iteration**: `V_{k+1}(s) = max_a [R(s,a) + γ·V_k(T(s,a))]`

Converges when γ < 1 (Banach fixed-point theorem)

---

#### witness: Trace Emission (PolicyTrace Monad)

**Category Theory**: Writer monad

**DP Interpretation**: Explicit trace of verification decisions

```python
def witness(p: Probe[A, B]) -> Probe[A, Tuple[B, PolicyTrace]]:
    """Every verification auto-witnesses its decisions."""
    async def witnessing_value(state: A) -> PolicyTrace:
        trace = await p.value(state)
        return PolicyTrace(
            states=trace.states + ((trace.states[-1], trace),),
            actions=trace.actions + ("witness",),
            rewards=trace.rewards + (trace.value,),
            rationales=trace.rationales + (f"Witnessed: {trace.value:.2f}",),
            value=trace.value,
        )
    return Probe(name=f"witness({p.name})", value=witnessing_value)
```

**Monad Laws**: Left identity, right identity, associativity (verified)

---

### Composition Laws

The ProbeOperad satisfies category laws:

| Law | Equation | Verification |
|-----|----------|--------------|
| **Associativity** | `(p1 >> p2) >> p3 ≡ p1 >> (p2 >> p3)` | Bellman equation is associative |
| **Identity** | `p >> unit ≡ p ≡ unit >> p` | Unit probe has zero reward |
| **Commutativity (par)** | `p1 ‖ p2 ≡ p2 ‖ p1` | Max is commutative |
| **Distributivity** | `p >> (p1 ‖ p2) ≡ (p >> p1) ‖ (p >> p2)` | Bellman distributes over max |
| **Idempotence (fix)** | `fix(fix(p)) ≡ fix(p)` | Value iteration converges once |
| **Witness Transparency** | `witness(p).value ≡ p.value` | Witnessing preserves value |

**Proof by Execution**:
```python
async def verify_associativity(p1, p2, p3, state):
    left = await ((p1 >> p2) >> p3).value(state)
    right = await (p1 >> (p2 >> p3)).value(state)
    assert abs(left.value - right.value) < 1e-6
```

---

## Part II: Bellman Equations for Verification

### The Fundamental Equation

```
Given DP problem (S, A, T, R, γ):
  S = State space (system configurations)
  A = Action space (verification operations)
  T: S × A → S (transition function)
  R: S × A × S → ℝ (constitutional reward)
  γ ∈ [0,1] (discount factor)

Find optimal policy:
  π*(s) = argmax_a [R(s,a) + γ·V*(T(s,a))]

Via value iteration:
  V_{k+1}(s) = max_a [R(s,a) + γ·V_k(T(s,a))]
```

---

### Constitutional Reward Function

```python
def R(s: State, a: Action, s_: State) -> float:
    """7 constitutional principles, weighted."""
    return (
        2.0 * R_ETHICAL(s, a, s_) +          # Safety first
        1.5 * R_COMPOSABLE(s, a, s_) +       # Architecture
        1.2 * R_JOY_INDUCING(s, a, s_) +     # Kent's aesthetic
        1.0 * R_GENERATIVE(s, a, s_) +
        1.0 * R_TASTEFUL(s, a, s_) +
        1.0 * R_CURATED(s, a, s_) +
        0.8 * R_HETERARCHICAL(s, a, s_)
    ) / 8.5  # Normalize
```

**Source**: `spec/principles.md`

---

### Probe-Specific Bellman Equations

#### NullProbe (Categorical)
```python
V*(s) = max_a [R_COMPOSABLE(s,a) + R_TASTEFUL(s,a)]
π*(s) = return constant that maximizes composition laws
```

#### ChaosProbe (Epistemic)
```python
V*(s) = max_a [R_ETHICAL(s,a) + R_COMPOSABLE(s,a)]
π*(s) = perturbation that maximizes resilience discovery
```

#### WitnessProbe (Dialectical)
```python
V*(s) = max_a [R_ETHICAL(s,a) + R_HETERARCHICAL(s,a)]
π*(s) = observation that maximizes auditability
```

#### JudgeProbe (Generative)
```python
V*(s) = max_a [R_GENERATIVE(s,a) + R_ETHICAL(s,a) + R_JOY_INDUCING(s,a)]
π*(s) = LLM evaluation that maximizes semantic alignment
```

#### TrustProbe (Meta)
```python
V*(s) = max_a [R_CURATED(s,a) + R_ETHICAL(s,a)]
π*(s) = stress coordinate that maximizes failure discovery
```

---

## Part III: Galois Loss for Probe Difficulty

### Motivation

Not all verification problems are equally hard. **Galois loss** measures difficulty by comparing predicted vs actual value.

```python
def galois_loss(probe: Probe, target: Agent, state: State) -> float:
    """L_galois = ||V_actual - V_predicted||²"""
    V_predicted = probe.predict_value(state)
    trace = await probe.value(state)
    V_actual = trace.value
    return (V_actual - V_predicted) ** 2
```

**Interpretation**:
- `L_galois = 0` → Probe perfectly calibrated
- `L_galois > 0` → Probe underestimated difficulty (refine probe)
- High loss → Verification harder than expected

---

### Galois Connection

```
Probes ⟺ Verification Problems

Stronger probe ⟹ Easier to verify hard problems
Weaker probe ⟹ Only verifies easy problems

Galois loss quantifies this gap.
```

---

### Adaptive Probing

Use Galois loss to select probes:

```python
async def adaptive_verify(target: Agent, state: State) -> PolicyTrace:
    """Escalate from simple to complex probes based on Galois loss."""
    probes = [MockProbe(), NoiseProbe(0.1), FailingProbe(), TrustProbe()]
    threshold = 0.01

    for probe in probes:
        trace = await probe.value(state)
        loss = galois_loss(probe, target, state)

        if loss < threshold:
            return trace  # Probe adequate

    raise ValueError("No probe could verify target within loss threshold")
```

---

## Part IV: PolicyTrace Integration

### PolicyTrace as Witness

```python
@dataclass(frozen=True)
class PolicyTrace(Generic[B]):
    """DP-native witness implementing Mark protocol."""
    states: tuple[S, ...]       # Trajectory: s₀, s₁, ..., sₙ
    actions: tuple[A, ...]      # Actions: a₀, a₁, ..., aₙ₋₁
    rewards: tuple[float, ...]  # Rewards: r₀, r₁, ..., rₙ₋₁
    rationales: tuple[str, ...] # Justifications
    value: float                # Total return: Σᵢ γⁱ·rᵢ

    def to_mark(self) -> Mark:
        """Convert to Witness Mark."""
        return Mark(
            action=self.actions[-1] if self.actions else "verify",
            stimulus=str(self.states[0]),
            response=str(self.states[-1]),
            reasoning="\n".join(self.rationales),
            proof=Proof(
                claim=f"Verified: {self.value:.2f}",
                grounds=self.rationales,
                confidence=min(self.value, 1.0),
            ),
        )

    def to_walk(self) -> Walk:
        """Convert to Witness Walk."""
        marks = [
            Mark(
                action=self.actions[i],
                stimulus=str(self.states[i]),
                response=str(self.states[i+1]),
                reasoning=self.rationales[i],
            )
            for i in range(len(self.actions))
        ]
        return Walk(marks=marks, value=self.value)
```

**Isomorphism**: `PolicyTrace ≅ Mark ≅ Walk entry`

---

### The Writer Monad

PolicyTrace is a **Writer monad** carrying verification history:

```python
class PolicyTrace(Monad):
    @staticmethod
    def unit(value: B) -> PolicyTrace[B]:
        """Minimal trace."""
        return PolicyTrace(
            states=(value,), actions=(), rewards=(), rationales=(), value=0.0
        )

    def bind(self, f: Callable[[B], PolicyTrace[C]]) -> PolicyTrace[C]:
        """Compose traces."""
        next_trace = f(self.states[-1])
        return PolicyTrace(
            states=self.states + next_trace.states[1:],
            actions=self.actions + next_trace.actions,
            rewards=self.rewards + next_trace.rewards,
            rationales=self.rationales + next_trace.rationales,
            value=self.value + next_trace.value,
        )
```

---

## Part V: Commutative Diagrams

TruthFunctors enable **commutative diagram verification**—proving path equivalence.

### Example: Retry Equivalence

**Hypothesis**: `RetryWrapper >> FailingProbe(fail=2)` ≡ `MockProbe(success)`

```
Input ──────MockProbe(success)──────> Success (V=1.0)
  │
  └──RetryWrapper >> FailingProbe────> Success (V=1.0)
```

**Verification**:
```python
async def verify_retry_equivalence():
    state = "test_input"

    mock_trace = await MockProbe(output="Success").value(state)

    failing = FailingProbe(FailingConfig(fail_count=2, recovery_token="Success"))
    retry = RetryWrapper(max_retries=3) >> failing
    retry_trace = await retry.value(state)

    assert abs(mock_trace.value - retry_trace.value) < 1e-6
```

---

### Example: Spy Transparency

**Hypothesis**: `SpyProbe` has same value as `Identity`

```
A ──────f──────> B   (V=V₀)
  \              ↑
   \─spy─f──────/    (V=V₀)
```

**Verification**:
```python
async def verify_spy_transparency():
    f = ProductionAgent()
    spy = SpyProbe(label="Test")

    trace_without = await f.value(state)
    trace_with = await (spy >> f).value(state)

    assert abs(trace_without.value - trace_with.value) < 1e-6
    assert spy.history[0] == state  # But spy captured data
```

---

## Success Metrics

A TruthFunctor verification is rigorous if:

1. **DP Formulation**: Explicit `(S, A, T, R, γ)` definition
2. **Constitutional Reward**: All actions scored against 7 principles
3. **Value Convergence**: `fix(probe)` converges in finite iterations
4. **Trace Completeness**: PolicyTrace contains all decisions and rationales
5. **Composition Laws**: Satisfies associativity, identity, commutativity
6. **Galois Calibration**: `L_galois < threshold` (probe adequate for task)

---

## See Also

- [README.md](README.md) - TruthFunctors overview
- [taxonomy.md](taxonomy.md) - Probe type specifications
- [adversarial.md](adversarial.md) - Probe V: Chaos engineering
- [../theory/dp-native-kgents.md](../theory/dp-native-kgents.md) - DP-native architecture
- [../theory/analysis-operad.md](../theory/analysis-operad.md) - Four analysis modes
- [../agents/operad.md](../agents/operad.md) - General operad foundations

---

## References

- Bellman, *Dynamic Programming* (1957)
- Russell & Norvig, *AI: A Modern Approach* (Ch 17: MDPs)
- Milewski, *Category Theory for Programmers* (Ch 8, 10)
- Lawvere, *Diagonal Arguments and Cartesian Closed Categories* (Fixed-point)
- Cheng, *The Joy of Abstraction* (Operads)

---

*"The proof IS the decision. The mark IS the witness. The verification IS the value function."*
