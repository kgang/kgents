# TruthFunctor Algebra: DP-Native Foundations

This document formalizes the mathematical foundations of TruthFunctors through Dynamic Programming and Category Theory, establishing verification as policy optimization under constitutional constraints.

---

## The Core Paradigm Shift

**Traditional Testing**: Verification as boolean predicates
**TruthFunctors**: Verification as value functions maximizing constitutional reward

```
Traditional:  test(agent, input) → {pass, fail}
TruthFunctor: verify(agent, state) → PolicyTrace[value, rationale]
```

Every verification is solving:
```
V*(s) = max_a [R(s,a) + γ · V*(T(s,a))]
```

---

## Part I: The ProbeOperad

### 1.1 Formal Definition

The **ProbeOperad** defines how TruthFunctors compose to build complex verification strategies.

```python
PROBE_OPERAD = Operad(
    name="ProbeOperad",
    operations={
        "seq": Operation(
            arity=2,
            signature="(Probe[A,B], Probe[B,C]) → Probe[A,C]",
            compose=sequential_composition,
            dp_interpretation="Bellman equation chaining"
        ),
        "par": Operation(
            arity=2,
            signature="(Probe[A,B], Probe[A,C]) → Probe[A,max(B,C)]",
            compose=parallel_composition,
            dp_interpretation="Value function maximization"
        ),
        "branch": Operation(
            arity=3,
            signature="(Condition, Probe[A,B], Probe[A,B]) → Probe[A,B]",
            compose=conditional_composition,
            dp_interpretation="Expected value over actions"
        ),
        "fix": Operation(
            arity=1,
            signature="Probe[A,A] → Probe[A,A]",
            compose=fixed_point,
            dp_interpretation="Value iteration until convergence"
        ),
        "witness": Operation(
            arity=1,
            signature="Probe[A,B] → Probe[A,(B,PolicyTrace)]",
            compose=trace_emission,
            dp_interpretation="PolicyTrace monad"
        ),
    },
    laws=[...],  # See section 1.3
)
```

### 1.2 Operations as DP Primitives

#### seq: Sequential Composition (Bellman Chaining)

**Category Theory**: Morphism composition in $\mathcal{C}_{Agent}$
**DP Interpretation**: Sequential decision-making

```python
def seq(p1: Probe[A, B], p2: Probe[B, C]) -> Probe[A, C]:
    """
    Sequential composition via Bellman equation.

    V_seq(s) = R₁(s,a₁) + γ · V₂(T₁(s,a₁))
    """
    async def composed_value(state: A) -> PolicyTrace[C]:
        # Execute first probe
        trace1 = await p1.value(state)
        intermediate = trace1.states[-1]

        # Execute second probe
        trace2 = await p2.value(intermediate)

        # Combine rewards (Bellman equation)
        total_value = trace1.value + p1.gamma * trace2.value

        # Merge traces
        return PolicyTrace(
            states=trace1.states + trace2.states[1:],
            actions=trace1.actions + trace2.actions,
            rewards=trace1.rewards + trace2.rewards,
            rationales=trace1.rationales + trace2.rationales,
            value=total_value,
        )

    return Probe(name=f"{p1.name} >> {p2.name}", value=composed_value)
```

**Bellman Equation**:
```
V*(s) = R(s, a₁) + γ · V*(T(s, a₁))
      = R₁(s, a₁) + γ · [R₂(s', a₂) + γ · V*(T(s', a₂))]
```

---

#### par: Parallel Composition (Value Maximization)

**Category Theory**: Product in $\mathcal{C}_{Agent}$
**DP Interpretation**: Simultaneous action selection, choose max value

```python
def par(p1: Probe[A, B], p2: Probe[A, C]) -> Probe[A, Union[B, C]]:
    """
    Parallel composition via value maximization.

    V_par(s) = max(V₁(s), V₂(s))
    """
    async def parallel_value(state: A) -> PolicyTrace[Union[B, C]]:
        # Execute both probes in parallel
        trace1, trace2 = await asyncio.gather(
            p1.value(state),
            p2.value(state)
        )

        # Select probe with higher constitutional value
        if trace1.value >= trace2.value:
            return trace1
        else:
            return trace2

    return Probe(name=f"{p1.name} ‖ {p2.name}", value=parallel_value)
```

**Value Equation**:
```
V*(s) = max(V₁(s), V₂(s))
```

---

#### branch: Conditional Composition (Expected Value)

**Category Theory**: Coproduct in $\mathcal{C}_{Agent}$
**DP Interpretation**: Probabilistic action selection

```python
def branch(
    condition: Callable[[A], float],  # Returns probability ∈ [0,1]
    p1: Probe[A, B],
    p2: Probe[A, B]
) -> Probe[A, B]:
    """
    Conditional composition via expected value.

    V_branch(s) = P(c) · V₁(s) + (1 - P(c)) · V₂(s)
    """
    async def branching_value(state: A) -> PolicyTrace[B]:
        prob = condition(state)

        # Execute both branches
        trace1, trace2 = await asyncio.gather(
            p1.value(state),
            p2.value(state)
        )

        # Compute expected value
        expected_value = prob * trace1.value + (1 - prob) * trace2.value

        # Select branch (stochastic or deterministic)
        if random.random() < prob:
            selected_trace = trace1
            branch_name = p1.name
        else:
            selected_trace = trace2
            branch_name = p2.name

        return PolicyTrace(
            states=selected_trace.states,
            actions=selected_trace.actions,
            rewards=selected_trace.rewards,
            rationales=(f"Branched to {branch_name} (P={prob:.2f})",) + selected_trace.rationales,
            value=expected_value,
        )

    return Probe(name=f"if ? {p1.name} : {p2.name}", value=branching_value)
```

**Expected Value Equation**:
```
V*(s) = Σₐ π(a|s) · [R(s,a) + γ · V*(T(s,a))]
      = P(c) · V₁(s) + (1-P(c)) · V₂(s)
```

---

#### fix: Fixed-Point Composition (Value Iteration)

**Category Theory**: Lawvere fixed-point theorem
**DP Interpretation**: Iterative value function refinement

```python
def fix(p: Probe[A, A], max_iters: int = 100, epsilon: float = 1e-6) -> Probe[A, A]:
    """
    Fixed-point composition via value iteration.

    V_{k+1}(s) = R(s,a) + γ · V_k(T(s,a))
    Converges to V*(s) when ||V_{k+1} - V_k|| < ε
    """
    async def fixed_point_value(state: A) -> PolicyTrace[A]:
        prev_value = 0.0
        current_state = state
        iteration = 0

        while iteration < max_iters:
            trace = await p.value(current_state)
            current_state = trace.states[-1]

            # Check convergence
            if abs(trace.value - prev_value) < epsilon:
                trace.rationales += (f"Converged at iteration {iteration}",)
                return trace

            prev_value = trace.value
            iteration += 1

        raise ValueError(f"Fixed-point did not converge after {max_iters} iterations")

    return Probe(name=f"fix({p.name})", value=fixed_point_value)
```

**Value Iteration**:
```
V_{k+1}(s) = max_a [R(s,a) + γ · V_k(T(s,a))]

Converges to V*(s) when γ < 1 (Banach fixed-point theorem)
```

---

#### witness: Trace Emission (PolicyTrace Monad)

**Category Theory**: Writer monad
**DP Interpretation**: Explicit trace of verification decisions

```python
def witness(p: Probe[A, B]) -> Probe[A, Tuple[B, PolicyTrace]]:
    """
    Trace emission via PolicyTrace monad.

    Every verification automatically witnesses its decisions.
    """
    async def witnessing_value(state: A) -> PolicyTrace[Tuple[B, PolicyTrace]]:
        trace = await p.value(state)

        # The trace IS the witness
        return PolicyTrace(
            states=trace.states + ((trace.states[-1], trace),),
            actions=trace.actions + ("witness",),
            rewards=trace.rewards + (trace.value,),
            rationales=trace.rationales + (f"Witnessed trace with value {trace.value:.2f}",),
            value=trace.value,
        )

    return Probe(name=f"witness({p.name})", value=witnessing_value)
```

**Monad Laws**:
```
1. Left identity:  witness(unit(x)).bind(f) ≡ f(x)
2. Right identity: trace.bind(witness) ≡ trace
3. Associativity:  (trace.bind(f)).bind(g) ≡ trace.bind(λx. f(x).bind(g))
```

---

### 1.3 Composition Laws

The ProbeOperad satisfies these categorical laws:

| Law | Equation | DP Interpretation |
|-----|----------|-------------------|
| **Associativity** | `(p1 >> p2) >> p3 ≡ p1 >> (p2 >> p3)` | Bellman equation is associative |
| **Identity** | `p >> unit ≡ p ≡ unit >> p` | Identity probe has zero reward |
| **Commutativity (par)** | `p1 ‖ p2 ≡ p2 ‖ p1` | Max is commutative |
| **Distributivity** | `p >> (p1 ‖ p2) ≡ (p >> p1) ‖ (p >> p2)` | Bellman distributes over max |
| **Idempotence (fix)** | `fix(fix(p)) ≡ fix(p)` | Value iteration converges once |
| **Witness Transparency** | `witness(p).value ≡ p.value` | Witnessing doesn't change value |

**Verification**:
```python
async def verify_associativity(p1, p2, p3, state):
    """Prove associativity through execution."""
    left = await ((p1 >> p2) >> p3).value(state)
    right = await (p1 >> (p2 >> p3)).value(state)

    assert abs(left.value - right.value) < 1e-6, "Associativity violated!"
```

---

## Part II: Bellman Equations for Verification

### 2.1 The Fundamental Equation

Every TruthFunctor solves this DP problem:

```
Given:
  S = State space (system configurations)
  A = Action space (verification operations)
  T: S × A → S (transition function)
  R: S × A × S → ℝ (constitutional reward)
  γ ∈ [0,1] (discount factor)

Find optimal verification policy:
  π*(s) = argmax_a [R(s,a) + γ · V*(T(s,a))]

Via value iteration:
  V_{k+1}(s) = max_a [R(s,a) + γ · V_k(T(s,a))]
```

### 2.2 Constitutional Reward Function

The reward function encodes the 7 constitutional principles:

```python
def R(s: State, a: Action, s_: State) -> float:
    """Constitutional reward function."""
    return (
        w_TASTEFUL * R_TASTEFUL(s, a, s_) +
        w_CURATED * R_CURATED(s, a, s_) +
        w_ETHICAL * R_ETHICAL(s, a, s_) +
        w_JOY_INDUCING * R_JOY_INDUCING(s, a, s_) +
        w_COMPOSABLE * R_COMPOSABLE(s, a, s_) +
        w_HETERARCHICAL * R_HETERARCHICAL(s, a, s_) +
        w_GENERATIVE * R_GENERATIVE(s, a, s_)
    )
```

**Default Weights** (from `CONSTITUTION.md`):
```python
weights = {
    "ETHICAL": 2.0,         # Safety first
    "COMPOSABLE": 1.5,      # Architecture second
    "JOY_INDUCING": 1.2,    # Kent's aesthetic
    "GENERATIVE": 1.0,
    "TASTEFUL": 1.0,
    "CURATED": 1.0,
    "HETERARCHICAL": 0.8,
}
```

### 2.3 Probe-Specific Formulations

Each probe type instantiates the Bellman equation differently:

#### NullProbe (Categorical Verification)

```python
class NullProbeDP:
    """DP formulation for categorical verification."""

    def reward(self, s: Config, a: MockAction, s_: Config) -> float:
        composability = self._count_laws_satisfied(s_) / self._total_laws
        tasteful = 1.0 if s_.purpose_clear else 0.0
        return 0.6 * composability + 0.4 * tasteful

    def optimal_policy(self, s: Config) -> MockAction:
        """π*(s) = return constant that maximizes composition laws."""
        actions = ["return_constant", "simulate_latency"]
        return max(actions, key=lambda a: self.reward(s, a, self.transition(s, a)))
```

#### ChaosProbe (Epistemic Verification)

```python
class ChaosProbeDP:
    """DP formulation for resilience verification."""

    def reward(self, s: System, a: PerturbAction, s_: System) -> float:
        resilience = 1.0 - s_.degradation_ratio
        ethical = 1.0 if s_.safety_preserved else 0.0
        return 0.5 * resilience + 0.5 * ethical

    def optimal_policy(self, s: System) -> PerturbAction:
        """π*(s) = perturbation that maximizes resilience discovery."""
        actions = ["inject_noise", "inject_failure", "inject_latency"]
        return max(actions, key=lambda a: self.reward(s, a, self.transition(s, a)))
```

#### WitnessProbe (Dialectical Verification)

```python
class WitnessProbeDP:
    """DP formulation for transparency verification."""

    def reward(self, s: Flow, a: ObserveAction, s_: Flow) -> float:
        transparency = s_.auditability_score
        heterarchical = s_.context_captured
        return 0.6 * transparency + 0.4 * heterarchical

    def optimal_policy(self, s: Flow) -> ObserveAction:
        """π*(s) = observation that maximizes auditability."""
        actions = ["spy", "predicate_gate", "count", "measure"]
        return max(actions, key=lambda a: self.reward(s, a, self.transition(s, a)))
```

#### JudgeProbe (Generative Verification)

```python
class JudgeProbeDP:
    """DP formulation for semantic verification."""

    def reward(self, s: Quality, a: EvalAction, s_: Quality) -> float:
        correctness = s_.semantic_accuracy
        ethical = s_.safety_score
        joy = s_.insight_provided
        return 0.4 * correctness + 0.4 * ethical + 0.2 * joy

    def optimal_policy(self, s: Quality) -> EvalAction:
        """π*(s) = LLM evaluation that maximizes semantic alignment."""
        actions = ["semantic_judge", "correctness_judge", "safety_judge"]
        return max(actions, key=lambda a: self.reward(s, a, self.transition(s, a)))
```

---

## Part III: Galois Loss for Probe Difficulty

### 3.1 Motivation

Not all verification problems are equally hard. **Galois loss** measures the difficulty of a verification task by comparing predicted vs actual value.

**Intuition**: If `V_predicted(s) >> V_actual(s)`, the probe underestimated difficulty.

### 3.2 Definition

```python
def galois_loss(probe: Probe, target: Agent, state: State) -> float:
    """
    Measure verification difficulty via Galois loss.

    L_galois(probe, target, s) = ||V_actual(s) - V_predicted(s)||²

    High loss → verification harder than expected → refine probe
    """
    # Predicted value (from prior or heuristic)
    V_predicted = probe.predict_value(state)

    # Actual value (from value iteration)
    trace = await probe.value(state)
    V_actual = trace.value

    return (V_actual - V_predicted) ** 2
```

### 3.3 Galois Connection

The **Galois connection** between verification difficulty and probe complexity:

```
Probes ⟺ Verification Problems

Stronger probe ⟹ Easier to verify hard problems
Weaker probe ⟹ Only verifies easy problems

Galois loss quantifies this gap:
  L_galois = 0   ⟹ probe perfectly calibrated
  L_galois > 0   ⟹ probe underestimated difficulty
  L_galois < 0   ⟹ probe overestimated (rare)
```

### 3.4 Adaptive Probing

Use Galois loss to adaptively select probes:

```python
async def adaptive_verify(target: Agent, state: State) -> PolicyTrace:
    """
    Adaptively select probe based on Galois loss.

    Algorithm:
    1. Start with simplest probe (MockProbe)
    2. Measure Galois loss
    3. If loss too high, escalate to stronger probe
    4. Repeat until loss < threshold
    """
    probes = [
        MockProbe(output="test"),
        NoiseProbe(level=0.1),
        FailingProbe(FailingConfig(fail_count=1)),
        AdversarialGym(iterations=100),
    ]

    for probe in probes:
        trace = await probe.value(state)
        loss = galois_loss(probe, target, state)

        if loss < threshold:
            return trace  # Probe adequate

    # All probes exhausted
    raise ValueError("No probe could verify target within loss threshold")
```

---

## Part IV: PolicyTrace Integration

### 4.1 PolicyTrace as Witness

Every TruthFunctor emits a **PolicyTrace**—the DP-native witness:

```python
@dataclass(frozen=True)
class PolicyTrace(Generic[B]):
    """
    The trace of optimal verification decisions.

    Isomorphic to Witness Mark.
    """
    states: tuple[Any, ...]       # State trajectory: s₀, s₁, ..., sₙ
    actions: tuple[str, ...]      # Action sequence: a₀, a₁, ..., aₙ₋₁
    rewards: tuple[float, ...]    # Reward sequence: r₀, r₁, ..., rₙ₋₁
    rationales: tuple[str, ...]   # Justifications for each action
    value: float                   # Total return: Σᵢ γⁱ · rᵢ

    def to_mark(self) -> Mark:
        """Convert to Witness Mark."""
        return Mark(
            action=self.actions[-1] if self.actions else "verify",
            stimulus=str(self.states[0]),
            response=str(self.states[-1]),
            reasoning="\n".join(self.rationales),
            proof=Proof(
                claim=f"Verified with value {self.value:.2f}",
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

### 4.2 The Writer Monad

PolicyTrace is a **Writer monad** carrying verification history:

```python
class PolicyTrace(Monad):
    """Writer monad for verification traces."""

    @staticmethod
    def unit(value: B) -> PolicyTrace[B]:
        """Monadic return: minimal trace."""
        return PolicyTrace(
            states=(value,),
            actions=(),
            rewards=(),
            rationales=(),
            value=0.0,
        )

    def bind(self, f: Callable[[B], PolicyTrace[C]]) -> PolicyTrace[C]:
        """Monadic bind: compose traces."""
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

TruthFunctors enable **commutative diagram verification**—proving that different paths through a system are equivalent.

### 5.1 Example: Retry Equivalence

**Hypothesis**: `RetryWrapper >> FailingProbe(fail_count=2)` has same value as `MockProbe(success)`

```
Input ──────MockProbe(success)──────> Success (V=1.0)
  │
  │  RetryWrapper >> FailingProbe(fails=2, then success)
  └────────────────────────────────────> Success (V=1.0)
```

**Verification**:
```python
async def verify_retry_equivalence():
    """Prove retry and mock probes have equivalent value."""
    state = "test_input"

    # Path 1: Direct success
    mock_trace = await MockProbe(output="Success").value(state)

    # Path 2: Retry after failures
    failing = FailingProbe(FailingConfig(fail_count=2, recovery_token="Success"))
    retry = RetryWrapper(max_retries=3) >> failing
    retry_trace = await retry.value(state)

    # Values should be equivalent
    assert abs(mock_trace.value - retry_trace.value) < 1e-6
```

### 5.2 Example: Spy Transparency

**Hypothesis**: `SpyProbe` has same value as `Identity`

```
A ──────f──────> B   (without spy, V=V₀)
  \              ↑
   \─spy─f──────/     (with spy, V=V₀)
```

**Verification**:
```python
async def verify_spy_transparency():
    """Prove spy doesn't change value function."""
    f = ProductionAgent()
    spy = SpyProbe(label="Test")
    state = "test_input"

    # Path without spy
    trace_without = await f.value(state)

    # Path with spy
    trace_with = await (spy >> f).value(state)

    # Values must be identical (spy is identity morphism)
    assert abs(trace_without.value - trace_with.value) < 1e-6

    # But spy captured the data (side effect)
    assert spy.history[0] == state
```

---

## Part VI: Success Metrics

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

- Richard Bellman, *Dynamic Programming* (1957)
- Stuart Russell & Peter Norvig, *Artificial Intelligence: A Modern Approach* (Ch 17: MDPs)
- Bartosz Milewski, *Category Theory for Programmers* (Ch 8: Functoriality, Ch 10: Natural Transformations)
- Lawvere, *Diagonal Arguments and Cartesian Closed Categories* (Fixed-point theorem)
- Eugenia Cheng, *The Joy of Abstraction* (Operads)

---

*"The proof IS the decision. The mark IS the witness. The verification IS the value function."*
