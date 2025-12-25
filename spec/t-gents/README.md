# TruthFunctors: DP-Native Verification Probes

> *"Testing is not a separate agent genus—it's an analysis mode. Every agent can be verified."*

---

## Philosophy

**Traditional Testing**: Boolean predicates → pass/fail

**TruthFunctors**: Value functions → constitutional score + witness trace

TruthFunctors treat verification as **Dynamic Programming** where:
- **States** = System configurations being tested
- **Actions** = Verification operations (mock, perturb, observe, judge, stress)
- **Reward** = Constitutional principle satisfaction (TASTEFUL, CURATED, ETHICAL, JOY_INDUCING, COMPOSABLE, HETERARCHICAL, GENERATIVE)
- **Policy** = Optimal testing strategy: `π*(s) = argmax_a [R(s,a) + γ·V*(T(s,a))]`
- **Trace** = Witness of verification (PolicyTrace → Mark → Walk)

Every verification solves the Bellman equation:
```
V*(s) = max_a [R(s,a) + γ · V*(T(s,a))]
```

---

## The Five Probes

TruthFunctors are NOT a separate agent genus. They are **analysis modes** applied to any agent, mapped to the four modes from `spec/theory/analysis-operad.md`:

| Probe | AnalysisMode | Morphism | Reward Focus | Purpose |
|-------|--------------|----------|--------------|---------|
| **NullProbe** | CATEGORICAL | `A → b` | R_COMPOSABLE | Verify composition laws via constants/fixtures |
| **ChaosProbe** | EPISTEMIC | `A → ⊥ ∪ (A+ε)` | R_ETHICAL | Verify resilience bounds via controlled chaos |
| **WitnessProbe** | DIALECTICAL | `A → A` | R_HETERARCHICAL | Capture tensions via transparent observation |
| **JudgeProbe** | GENERATIVE | `(A,B) → [0,1]` | R_GENERATIVE | Verify semantic correctness via LLM evaluation |
| **TrustProbe** | META | `Agent → Report` | R_CURATED | Discover failure modes via chaos engineering |

### Consolidation from 17 to 5

Previously, T-gents were 17 types spread across 5 categories. Now:
- **Probe I (NullProbe)**: MockProbe + FixtureProbe → categorical verification
- **Probe II (ChaosProbe)**: FailingProbe + NoiseProbe + LatencyProbe + FlakyProbe → epistemic bounds
- **Probe III (WitnessProbe)**: SpyProbe + PredicateProbe + CounterProbe + MetricsProbe → dialectical observation
- **Probe IV (JudgeProbe)**: SemanticJudge + CorrectnessJudge + SafetyJudge → generative evaluation
- **Probe V (TrustProbe)**: AdversarialGym + MultiDimensionalGym → meta-verification

---

## DP-Native Signature

Every probe IS a `ValueAgent[S, A, B]` with signature `(S, A, T, R, γ)`:

```python
class TruthFunctor(ValueAgent[S, A, B]):
    """Base class for all verification probes."""

    __is_verification__: bool = True
    analysis_mode: AnalysisMode

    # DP formulation
    states: FrozenSet[S]         # State space
    actions: FrozenSet[A]        # Action space
    transition: Callable         # T: S × A → S
    gamma: float = 0.99          # Discount factor

    def reward(self, s: S, a: A, s_: S) -> PrincipleScore:
        """Constitutional reward: 7 principles weighted."""
        return PrincipleScore(
            tasteful=self._score_tasteful(s, a, s_),
            curated=self._score_curated(s, a, s_),
            ethical=self._score_ethical(s, a, s_),
            joy_inducing=self._score_joy(s, a, s_),
            composable=self._score_composable(s, a, s_),
            heterarchical=self._score_heterarchical(s, a, s_),
            generative=self._score_generative(s, a, s_),
        )

    async def value(self, state: S) -> PolicyTrace[B]:
        """Compute value via Bellman equation. Returns witnessed trace."""
        raise NotImplementedError
```

### Constitutional Reward Weights

From `spec/principles.md`:

```python
DEFAULT_WEIGHTS = {
    "ETHICAL": 2.0,         # Safety first
    "COMPOSABLE": 1.5,      # Architecture second
    "JOY_INDUCING": 1.2,    # Kent's aesthetic
    "GENERATIVE": 1.0,
    "TASTEFUL": 1.0,
    "CURATED": 1.0,
    "HETERARCHICAL": 0.8,
}
```

---

## PolicyTrace as Witness

Every probe emits a **PolicyTrace**—the DP-native witness:

```python
@dataclass(frozen=True)
class PolicyTrace(Generic[B]):
    """Verification trace implementing Mark protocol."""
    states: tuple[S, ...]       # State trajectory
    actions: tuple[A, ...]      # Action sequence
    rewards: tuple[float, ...]  # Constitutional scores
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
                claim=f"Verified with value {self.value:.2f}",
                grounds=self.rationales,
                confidence=min(self.value, 1.0),
            ),
        )
```

**Isomorphism**: `PolicyTrace ≅ Mark ≅ Walk entry`

---

## The ProbeOperad

TruthFunctors compose via the **ProbeOperad**:

| Operation | Signature | DP Interpretation | Example |
|-----------|-----------|-------------------|---------|
| **seq** | `(Probe[A,B], Probe[B,C]) → Probe[A,C]` | Sequential Bellman: `V(s) = R(s,a₁) + γ·V(T(s,a₁))` | `mock >> spy >> judge` |
| **par** | `(Probe[A,B], Probe[A,C]) → Probe[A,max(B,C)]` | Value maximization: `V(s) = max(V₁(s), V₂(s))` | `noise ‖ latency` |
| **branch** | `(Cond, Probe[A,B], Probe[A,B]) → Probe[A,B]` | Expected value: `V(s) = P·V₁(s) + (1-P)·V₂(s)` | `if fast then unit else stress` |
| **fix** | `Probe[A,A] → Probe[A,A]` | Value iteration: `V_{k+1}(s) = R + γ·V_k` | `analysis(analysis_operad)` |
| **witness** | `Probe[A,B] → Probe[A,(B,Trace)]` | PolicyTrace monad (all probes auto-witness) | Every probe |

### Composition Laws

The ProbeOperad satisfies category laws (verified):

| Law | Equation | Verification |
|-----|----------|--------------|
| **Associativity** | `(p1 >> p2) >> p3 ≡ p1 >> (p2 >> p3)` | Bellman equation is associative |
| **Identity** | `p >> unit ≡ p ≡ unit >> p` | Unit probe has zero reward |
| **Commutativity (par)** | `p1 ‖ p2 ≡ p2 ‖ p1` | Max is commutative |
| **Witness Transparency** | `witness(p).value ≡ p.value` | Witnessing preserves value |

---

## Probe Specifications

### NullProbe (Categorical Verification)

**Purpose**: Replace computation with constants or fixtures to verify composition laws without expensive operations.

**DP Formulation**:
```python
def reward(s: Config, a: MockAction, s_: Config) -> float:
    composability = count_laws_satisfied(s_) / total_laws
    tasteful = 1.0 if s_.purpose_clear else 0.0
    return 0.6 * composability + 0.4 * tasteful
```

**Variants**:
- **MockProbe**: Constant morphism `A → b` (fast, deterministic, zero LLM cost)
- **FixtureProbe**: Lookup morphism `A → B` (regression testing via hash map)

**Use Cases**: Fast pipeline testing, composition law validation, performance benchmarking, CI/CD

---

### ChaosProbe (Epistemic Verification)

**Purpose**: Inject controlled chaos to verify resilience bounds—how justified are stability claims?

**DP Formulation**:
```python
def reward(s: System, a: PerturbAction, s_: System) -> float:
    resilience = 1.0 - s_.degradation_ratio
    ethical = 1.0 if s_.safety_preserved else 0.0
    return 0.5 * resilience + 0.5 * ethical
```

**Variants**:
- **FailingProbe**: Bottom morphism `A → ⊥` (controlled failure, N retries)
- **NoiseProbe**: Perturbation `A → A+ε` (semantic noise: case, whitespace, typos)
- **LatencyProbe**: Temporal morphism `(A,t) → (A,t+Δ)` (timeout testing)
- **FlakyProbe**: Probabilistic `A → B ∪ {⊥}` (stochastic failure, p ∈ [0,1])

**Use Cases**: Retry logic validation, fallback strategies, chaos engineering, circuit breaker testing

---

### WitnessProbe (Dialectical Verification)

**Purpose**: Capture tensions and contradictions via transparent observation (identity with side effects).

**DP Formulation**:
```python
def reward(s: Flow, a: ObserveAction, s_: Flow) -> float:
    transparency = s_.auditability_score
    heterarchical = s_.context_captured
    return 0.6 * transparency + 0.4 * heterarchical
```

**Variants**:
- **SpyProbe**: Writer monad `A → (A, [A])` (logging, data flow inspection)
- **PredicateProbe**: Gate morphism `A → A ∪ {⊥}` (runtime invariant validation)
- **CounterProbe**: Identity `A → A` (invocation tracking, frequency analysis)
- **MetricsProbe**: Identity `A → A` (performance profiling, latency measurement)

**Use Cases**: Pipeline debugging, runtime type checking, performance profiling, assertion-based testing

---

### JudgeProbe (Generative Verification)

**Purpose**: Evaluate semantic correctness via LLM judgment—can output regenerate from axioms?

**DP Formulation**:
```python
def reward(s: Quality, a: EvalAction, s_: Quality) -> float:
    correctness = s_.semantic_accuracy
    ethical = s_.safety_score
    joy = s_.insight_provided
    return 0.4 * correctness + 0.4 * ethical + 0.2 * joy
```

**Variants**:
- **SemanticJudge**: `(Intent, Output) → [0,1]` (alignment scoring)
- **CorrectnessJudge**: `(Spec, Impl) → Bool` (specification conformance)
- **SafetyJudge**: `Code → Risk` (vulnerability detection, safety bounds)

**Use Cases**: LLM-as-judge evaluation, semantic correctness beyond syntax, safety validation

---

### TrustProbe (Meta-Verification)

**Purpose**: Discover unknown failure modes via systematic stress exploration (chaos engineering).

**DP Formulation**:
```python
def reward(s: Reliability, a: StressAction, s_: Reliability) -> float:
    coverage = s_.stress_space_explored
    discovery = s_.new_failures_found
    curated = s_.intentional_selection
    return 0.4 * coverage + 0.4 * discovery + 0.2 * curated
```

**Implementation**: Multi-dimensional stress coordinate system exploring `(noise, failure_probability, latency, semantic_drift)` hypercube.

**See**: `adversarial.md` for full AdversarialGym specification.

---

## Integration with kgents Architecture

### AGENTESE Paths

```
concept.verify.categorical.{target}    # NullProbe verification
concept.verify.epistemic.{target}      # ChaosProbe stress testing
concept.verify.dialectical.{target}    # WitnessProbe observation
concept.verify.generative.{target}     # JudgeProbe evaluation
concept.verify.meta.{target}           # TrustProbe chaos engineering
```

### Relation to Analysis Operad

From `spec/theory/analysis-operad.md`:

| AnalysisMode | Question | TruthFunctor |
|--------------|----------|--------------|
| **CATEGORICAL** | Does X satisfy composition laws? | NullProbe verifies associativity/identity |
| **EPISTEMIC** | How justified is X? | ChaosProbe tests resilience bounds |
| **DIALECTICAL** | What tensions exist? | WitnessProbe captures contradictions |
| **GENERATIVE** | Can X regenerate from axioms? | JudgeProbe evaluates semantic correctness |

### Relation to Other Agents

| Genus | TruthFunctor Role |
|-------|-------------------|
| **C-gents** | Verify composition laws via NullProbe |
| **J-gents** | Validate Promise collapse and entropy budgets via ChaosProbe |
| **B-gents** | Evaluate hypothesis quality via JudgeProbe |
| **K-gent** | Ensure persona consistency via attractor basin validation |

---

## Example: Full Pipeline Verification

```python
async def verify_evolution_pipeline():
    """DP-native verification of evolution pipeline."""

    # Compose probes via ProbeOperad
    verification_policy = (
        NullProbe.mock(hypotheses=["H1", "H2", "H3"]) >>
        WitnessProbe.spy(label="Experiments") >>
        ChaosProbe.flaky(probability=0.1) >>
        JudgeProbe.semantic(criteria="correctness")
    )

    # Execute verification (returns PolicyTrace)
    trace = await verification_policy.value(initial_state)

    # Extract constitutional scores
    scores = trace.principle_scores

    # Verify: All principles above threshold
    assert all(s > 0.7 for s in scores.values())

    # Convert to Witness Walk
    walk = trace.to_walk()

    print(f"✓ Pipeline verified: {trace.value:.2f}")
    print(f"✓ Trace: {walk.id}")
```

---

## Implementation Principles

1. **Constitutional Scoring**: Every probe action MUST produce principle scores
2. **Transparency**: `__is_verification__ = True` distinguishes from production agents
3. **Determinism**: All probes reproducible via seed (even ChaosProbe)
4. **Minimal Footprint**: Avoid heavy dependencies unless testing specific integrations
5. **Witness by Default**: Every invocation auto-generates PolicyTrace

---

## Success Criteria

A TruthFunctor is well-designed if:

- ✓ It formulates verification as a DP problem `(S, A, T, R, γ)`
- ✓ Its reward function aligns with constitutional principles
- ✓ It emits PolicyTrace witnesses for all verifications
- ✓ It composes naturally via ProbeOperad operations
- ✓ It provides clear diagnostic information
- ✓ It enables confident refactoring
- ✓ It proves algebraic properties, not just examples

---

## Anti-patterns

- **Non-DP Formulation**: Tests without `(S, A, T, R, γ)` definition
- **Constitutional Bypass**: Verification without principle scoring
- **Traceless Verification**: Tests that don't emit PolicyTrace
- **Non-Compositional**: Probes that break pipeline semantics (>> fails)
- **False Positives**: Tests that fail on valid behavior

---

## Related Specifications

| Document | Description |
|----------|-------------|
| [taxonomy.md](taxonomy.md) | Detailed DP formulations for each probe type |
| [algebra.md](algebra.md) | ProbeOperad foundations, Bellman equations, Galois loss |
| [adversarial.md](adversarial.md) | Probe V: TrustProbe chaos engineering |
| [../theory/dp-native-kgents.md](../theory/dp-native-kgents.md) | DP-native architecture |
| [../theory/analysis-operad.md](../theory/analysis-operad.md) | Four analysis modes |
| [../agents/operad.md](../agents/operad.md) | General operad foundations |

---

## Vision

TruthFunctors transform testing from **example-based** to **proof-based**:

- **Traditional**: "This test case passes"
- **TruthFunctors**: "This pipeline satisfies associativity for all inputs, scored constitutionally at 0.87, witnessed with 15 decision steps"

By grounding verification in Dynamic Programming and constitutional principles, TruthFunctors enable **explainable reliability**—confidence from optimal policies with witnessed rationales, not just empirical observation.

---

*"The proof IS the decision. The mark IS the witness. The verification IS the value function."*
