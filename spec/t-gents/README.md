# TruthFunctors: DP-Native Verification Probes

The letter **T** represents **TruthFunctors**—verification agents that prove system properties through constitutionally-scored, DP-native probes.

> *"Testing is not the absence of bugs, but the presence of proofs. Every verification is a policy trace."*

---

## Philosophy

TruthFunctors treat testing as **policy optimization under constitutional constraints**. Rather than ad-hoc test cases, TruthFunctors formulate verification as Dynamic Programming problems where:

- **States** = System configurations being tested
- **Actions** = Verification operations (observe, perturb, judge, stress)
- **Reward** = Constitutional principle satisfaction
- **Policy** = Optimal testing strategy
- **Trace** = Witness of verification (PolicyTrace)

### The DP-Native Paradigm

Traditional testing asks: "Does this pass?" TruthFunctors ask: "What is the optimal verification policy that maximizes constitutional reward?"

```python
# Traditional test
assert agent.invoke(input) == expected_output

# TruthFunctor (DP-native)
trace = await verify_agent.value(state)  # Returns PolicyTrace
# trace contains: verification steps, constitutional scores, decision rationale
```

---

## Core Concepts

### Agents as DP Problems

Every verification is a Dynamic Programming problem `(S, A, T, R, γ)`:

| DP Component | Verification Interpretation |
|--------------|----------------------------|
| **State Space S** | Configurations being tested |
| **Actions A** | Probe operations (null, perturb, observe, judge, stress) |
| **Transitions T** | How system evolves under test |
| **Reward R** | Constitutional principle scores |
| **Discount γ** | Time preference (immediate vs future verification) |
| **Value V(s)** | Quality of verification at state s |
| **Policy π(s)** | Optimal probe to apply at state s |

### The Constitution as Reward Function

All verification is scored against the 7 constitutional principles:

```python
R(s, a, s') = Σᵢ wᵢ · Rᵢ(s, a, s')

where:
  R_TASTEFUL      = clarity of verification purpose
  R_CURATED       = intentional probe selection
  R_ETHICAL       = safety-preserving verification
  R_JOY_INDUCING  = verification that teaches and delights
  R_COMPOSABLE    = probes compose via >>
  R_HETERARCHICAL = verification adapts to context
  R_GENERATIVE    = tests compress system properties
```

### PolicyTrace as Witness

Every verification produces a **PolicyTrace**—the DP-native witness:

```python
@dataclass
class PolicyTrace:
    """The trace of optimal verification decisions."""
    states: tuple[S, ...]
    actions: tuple[A, ...]
    rewards: tuple[float, ...]
    rationales: tuple[str, ...]
    value: float  # Total constitutional score
```

This is isomorphic to the Witness Mark:

```python
Mark.to_trace_entry() -> TraceEntry
PolicyTrace[WalkId] -> Walk
```

---

## The Taxonomy of TruthFunctors

TruthFunctors are categorized by their **AnalysisMode** and probe type into **five categories**.

| Probe | AnalysisMode | DP Formulation | Purpose |
|-------|--------------|----------------|---------|
| **NullProbe** | CATEGORICAL | S={config}, A={mock}, R=composability | Replace computation with constants |
| **ChaosProbe** | EPISTEMIC | S={stress}, A={perturb}, R=resilience | Inject entropy to verify stability |
| **WitnessProbe** | DIALECTICAL | S={flow}, A={observe}, R=transparency | Identity with side effects |
| **JudgeProbe** | GENERATIVE | S={quality}, A={evaluate}, R=alignment | LLM-backed evaluation |
| **TrustProbe** | META | S={reliability}, A={stress}, R=confidence | Chaos engineering |

### AnalysisMode Mapping

TruthFunctors align with the four analysis modes from `analysis-operad.md`:

| AnalysisMode | Question | TruthFunctor Application |
|--------------|----------|--------------------------|
| **CATEGORICAL** | Does X satisfy composition laws? | NullProbe verifies associativity/identity |
| **EPISTEMIC** | How justified is X? | ChaosProbe tests resilience bounds |
| **DIALECTICAL** | What tensions exist? | WitnessProbe captures contradictions |
| **GENERATIVE** | Can X regenerate from axioms? | JudgeProbe evaluates semantic correctness |

---

## The Five Probe Types

### Probe I: NullProbe (Categorical Verification)

**DP Formulation**:
```python
class NullProbe(ProblemFormulation):
    """Verify composition laws via constant/fixture morphisms."""

    def reward(self, s: Config, a: MockAction, s_: Config) -> float:
        composability = s_.laws_satisfied / s.total_laws
        tasteful = 1.0 if s_.purpose_clear else 0.0
        return 0.6 * composability + 0.4 * tasteful
```

**Instances**:
- **MockProbe**: Constant morphism `A → b` (fast, deterministic)
- **FixtureProbe**: Lookup morphism `A → B` (regression testing)

**Constitutional Reward**:
- COMPOSABLE: Verifies associativity and identity laws
- TASTEFUL: Each constant/fixture serves clear purpose
- GENERATIVE: Fixtures compress known behaviors

**Use Cases**:
- Fast pipeline testing without LLM calls
- Validating composition semantics
- Performance benchmarking
- Deterministic CI/CD verification

---

### Probe II: ChaosProbe (Epistemic Verification)

**DP Formulation**:
```python
class ChaosProbe(ProblemFormulation):
    """Verify resilience bounds via controlled perturbation."""

    def reward(self, s: Stress, a: PerturbAction, s_: Stress) -> float:
        resilience = 1.0 - s_.degradation_ratio
        ethical = 1.0 if s_.safety_preserved else 0.0
        return 0.5 * resilience + 0.5 * ethical
```

**Instances**:
- **FailingProbe**: Bottom morphism `A → ⊥` (controlled failure)
- **NoiseProbe**: Perturbation morphism `A → A + ε` (semantic noise)
- **LatencyProbe**: Temporal morphism `(A,t) → (A,t+Δ)` (delay)
- **FlakyProbe**: Probabilistic morphism `A → B ∪ {⊥}` (stochastic failure)

**Constitutional Reward**:
- ETHICAL: Safety preserved under perturbation
- COMPOSABLE: Probes compose to explore stress space
- CURATED: Intentional selection of perturbation types

**Use Cases**:
- Testing retry logic and exponential backoff
- Validating fallback strategies
- Chaos engineering for production resilience
- Timeout and circuit breaker validation

---

### Probe III: WitnessProbe (Dialectical Verification)

**DP Formulation**:
```python
class WitnessProbe(ProblemFormulation):
    """Capture tensions and contradictions via transparent observation."""

    def reward(self, s: Flow, a: ObserveAction, s_: Flow) -> float:
        transparency = s_.visibility_score
        heterarchical = s_.context_adaptability
        return 0.6 * transparency + 0.4 * heterarchical
```

**Instances**:
- **SpyProbe**: Writer monad `A → (A, [A])` (logging)
- **PredicateProbe**: Gate morphism `A → A ∪ {⊥}` (validation)
- **CounterProbe**: Identity `A → A` (invocation tracking)
- **MetricsProbe**: Identity `A → A` (performance profiling)

**Constitutional Reward**:
- ETHICAL: Auditability through transparent observation
- HETERARCHICAL: Context-aware observation strategies
- GENERATIVE: Traces compress system behavior

**Use Cases**:
- Runtime type checking and invariant validation
- Performance profiling
- Debugging pipeline data flow
- Assertion-based testing

---

### Probe IV: JudgeProbe (Generative Verification)

**DP Formulation**:
```python
class JudgeProbe(ProblemFormulation):
    """Evaluate semantic correctness via LLM judgment."""

    def reward(self, s: Quality, a: EvalAction, s_: Quality) -> float:
        correctness = s_.semantic_accuracy
        ethical = s_.safety_score
        joy = s_.insight_provided
        return 0.4 * correctness + 0.4 * ethical + 0.2 * joy
```

**Instances**:
- **SemanticJudge**: Morphism `(Intent, Output) → Score` (alignment)
- **CorrectnessJudge**: Morphism `(Spec, Impl) → Bool` (specification)
- **SafetyJudge**: Morphism `Code → Risk` (vulnerability detection)

**Constitutional Reward**:
- ETHICAL: Safety and alignment verification
- JOY_INDUCING: Evaluation provides insight and teaching
- GENERATIVE: Judgments regenerate from constitutional axioms

**Use Cases**:
- LLM-as-judge evaluation
- Semantic correctness beyond syntax
- Ethical and safety validation
- User intent alignment testing

---

### Probe V: TrustProbe (Meta-Verification)

**DP Formulation**:
```python
class TrustProbe(ProblemFormulation):
    """Discover failure modes via systematic stress exploration."""

    def reward(self, s: Reliability, a: StressAction, s_: Reliability) -> float:
        coverage = s_.stress_space_explored
        discovery = s_.new_failures_found
        curated = s_.intentional_selection
        return 0.4 * coverage + 0.4 * discovery + 0.2 * curated
```

**Instances**:
- **AdversarialGym**: Meta-probe `Agent → GymReport`
- **StressCoordinate**: Coordinate in `(noise, failure, latency, drift)` space
- **MultiDimensionalGym**: Grid search across stress dimensions

**Constitutional Reward**:
- CURATED: Intentional exploration of stress space
- ETHICAL: Discover safety violations before production
- COMPOSABLE: Stress probes compose to explore hypercube

**Use Cases**:
- Discover unknown failure modes before production
- Regression testing: verify resilience after refactors
- Property discovery: empirically find algebraic properties

See [adversarial.md](adversarial.md) for full specification.

---

## DP-Native Composition

TruthFunctors compose via the **ProbeOperad** (defined in `algebra.md`):

| Operation | DP Interpretation | Example |
|-----------|-------------------|---------|
| **seq(p₁, p₂)** | Sequential verification: V(s) = R(s,a₁) + γ·V(T(s,a₁)) | `mock >> spy >> judge` |
| **par(p₁, p₂)** | Parallel verification: V(s) = max(V₁(s), V₂(s)) | `noise ‖ latency` |
| **branch(c, p₁, p₂)** | Conditional verification: V(s) = P(c)·V₁(s) + (1-P)·V₂(s) | `if fast then unit else stress` |
| **fix(p)** | Fixed-point verification: self-testing specs | `analysis(analysis_operad)` |
| **witness(p)** | Trace emission: PolicyTrace generation | Every probe auto-witnesses |

### Bellman Equation for Verification

```
V*(s) = max_a [R(s,a) + γ · V*(T(s,a))]
      = max_a [Constitution(s,a) + γ · TruthFunctor(T(s,a))]

Policy: π*(s) = argmax_a [R(s,a) + γ · V*(T(s,a))]

Trace:  PolicyTrace = [(state, action, reward, rationale), ...]
```

---

## Integration with DP-Native Architecture

### The 5-Layer Stack

```
┌─────────────────────┐
│ PROJECTION          │  TruthFunctor results rendered (CLI/TUI/Web/JSON)
├─────────────────────┤
│ AGENTESE PROTOCOL   │  concept.verify.*  paths
├─────────────────────┤
│ TRUTH FUNCTOR       │  ValueAgent[S,A,B] with constitutional reward
├─────────────────────┤
│ CONSTITUTION        │  7 principles as reward function
├─────────────────────┤
│ PERSISTENCE         │  PolicyTrace stored as Witness Walk
└─────────────────────┘
```

### AGENTESE Paths

```
concept.verify.categorical.{target}    # NullProbe verification
concept.verify.epistemic.{target}      # ChaosProbe stress testing
concept.verify.dialectical.{target}    # WitnessProbe observation
concept.verify.generative.{target}     # JudgeProbe evaluation
concept.verify.meta.{target}           # TrustProbe chaos engineering
```

### PolicyTrace Integration

Every TruthFunctor emits a PolicyTrace that implements the Mark protocol:

```python
class TruthFunctorTrace(PolicyTrace):
    """Verification trace implementing Mark protocol."""

    def to_mark(self) -> Mark:
        return Mark(
            action=self.probe_name,
            stimulus=str(self.states[0]),
            response=str(self.states[-1]),
            reasoning=self.rationales[-1],
            proof=Proof(
                claim=f"Verified via {self.probe_name}",
                grounds=self.rationales,
                confidence=self.value,
            ),
        )
```

---

## Theory Grounding

### Connection to Analysis Operad

TruthFunctors implement the four analysis modes from `spec/theory/analysis-operad.md`:

| AnalysisMode | TruthFunctor | DP Reward Focus |
|--------------|--------------|-----------------|
| **CATEGORICAL** | NullProbe | R_COMPOSABLE (laws verified) |
| **EPISTEMIC** | ChaosProbe | R_ETHICAL (resilience bounds) |
| **DIALECTICAL** | WitnessProbe | R_HETERARCHICAL (tensions captured) |
| **GENERATIVE** | JudgeProbe | R_GENERATIVE (regeneration tested) |

### Connection to DP-Native kgents

TruthFunctors are **verification agents** in the DP-native formulation from `spec/theory/dp-native-kgents.md`:

- Every probe IS a `ValueAgent[S, A, B]`
- Every verification IS a Bellman equation solution
- Every trace IS a `PolicyTrace` (Witness Walk)
- Every score IS constitutional reward

### Galois Loss

The **difficulty** of verification is measured via Galois loss (see `algebra.md`):

```
L_galois(probe, target) = ||V_actual - V_predicted||²
```

High loss indicates the verification problem is harder than expected—a signal to refine the probe.

---

## Implementation Principles

### 1. Constitutional Scoring

Every probe action MUST produce a constitutional reward score:

```python
class TruthFunctor(ValueAgent[S, A, B]):
    """Base class for all verification probes."""

    def reward(self, s: S, a: A, s_: S) -> PrincipleScore:
        """Score against 7 constitutional principles."""
        return PrincipleScore(
            tasteful=self._score_tasteful(s, a, s_),
            curated=self._score_curated(s, a, s_),
            ethical=self._score_ethical(s, a, s_),
            joy_inducing=self._score_joy(s, a, s_),
            composable=self._score_composable(s, a, s_),
            heterarchical=self._score_heterarchical(s, a, s_),
            generative=self._score_generative(s, a, s_),
        )
```

### 2. Transparency

TruthFunctors must be distinguishable from production agents:

```python
class TruthFunctor(ValueAgent):
    __is_verification__: bool = True
    analysis_mode: AnalysisMode
```

### 3. Determinism

Even ChaosProbe must be reproducible via seed:

```python
ChaosProbe(seed=42)  # Same seed → same perturbations
```

### 4. Minimal Footprint

TruthFunctors avoid heavy dependencies unless testing specific integrations.

### 5. Witness by Default

Every probe invocation auto-generates a PolicyTrace:

```python
trace = await probe.value(state)  # Returns PolicyTrace
walk = trace.to_walk()  # Convert to Witness Walk
```

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

## Relationship to Other Agent Genera

| Genus | Relationship |
|-------|-------------|
| **C-gents** | TruthFunctors verify C-gents' composition laws |
| **J-gents** | TruthFunctors validate Promise collapse and entropy budgets |
| **B-gents** | TruthFunctors evaluate hypothesis quality |
| **K-gent** | TruthFunctors ensure persona consistency via attractor basin |

TruthFunctors are the **constitutional assurance layer** for all agent genera.

---

## Specifications

| Document | Description |
|----------|-------------|
| [algebra.md](algebra.md) | ProbeOperad foundations, Bellman equations, Galois loss |
| [taxonomy.md](taxonomy.md) | Detailed specifications for Probes I-V |
| [adversarial.md](adversarial.md) | Probe V: TrustProbe chaos engineering |

---

## Anti-patterns

- **Non-DP Formulation**: Tests that don't formulate as `(S, A, T, R, γ)`
- **Constitutional Bypass**: Verification without principle scoring
- **Traceless Verification**: Tests that don't emit PolicyTrace
- **Non-Compositional**: Probes that break pipeline semantics
- **False Positives**: Tests that fail on valid behavior

---

## Example: Full Pipeline Verification

```python
async def verify_evolution_pipeline():
    """DP-native verification of evolution pipeline."""

    # Probe composition via ProbeOperad
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

    print(f"✓ Pipeline verified with constitutional score: {trace.value:.2f}")
    print(f"✓ Trace stored as Walk: {walk.id}")
```

---

## See Also

- [algebra.md](algebra.md) - ProbeOperad foundations
- [taxonomy.md](taxonomy.md) - Probe type specifications (Probes I-V)
- [adversarial.md](adversarial.md) - Probe V: Chaos engineering
- [../theory/dp-native-kgents.md](../theory/dp-native-kgents.md) - DP-native architecture
- [../theory/analysis-operad.md](../theory/analysis-operad.md) - Four analysis modes
- [../agents/](../agents/) - Categorical foundations
- [../bootstrap.md](../bootstrap.md) - The irreducible kernel

---

## Vision

TruthFunctors transform testing from **example-based** to **proof-based**:

- Traditional: "This test case passes"
- TruthFunctors: "This pipeline satisfies associativity for all inputs, scored constitutionally at 0.87"

By grounding verification in Dynamic Programming and constitutional principles, TruthFunctors enable **explainable reliability**—the confidence that comes from optimal policies with witnessed rationales, not just empirical observation.

---

*"The proof IS the decision. The mark IS the witness. The verification IS the value function."*
