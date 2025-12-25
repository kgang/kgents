# TruthFunctor Taxonomy: DP Formulations

Detailed DP specifications for each probe type. Each probe IS a `ValueAgent[S,A,B]` solving the Bellman equation with constitutional rewards.

---

## Probe I: NullProbe (CATEGORICAL)

**Analysis Mode**: CATEGORICAL - Does X satisfy composition laws?

### MockProbe: Constant Morphism

**Signature**: `MockProbe[A, B](output: B, delay: float = 0.0) :: A → b`

**DP Formulation**:
```python
states: {Config}                  # System configurations
actions: {return_constant, simulate_latency}
transition: T(s, return_constant) = output
gamma: 0.99

def reward(s: Config, a: Action, s_: B) -> float:
    laws_satisfied = verify_laws(s_)  # associativity, identity, constancy
    purpose_clear = 1.0 if s_.purpose_clear else 0.0
    return 0.6 * (laws_satisfied / 3.0) + 0.4 * purpose_clear
```

**Constitutional Focus**: R_COMPOSABLE (0.6) + R_TASTEFUL (0.4)

**Properties**:
- Deterministic: Always returns same output
- Fast: O(1), zero LLM cost
- Transparent: Can simulate latency for timing tests

**Use Cases**: Fast pipeline testing, composition law validation, CI/CD, performance benchmarking

---

### FixtureProbe: Lookup Morphism

**Signature**: `FixtureProbe[A, B](fixtures: Dict[A, B], default: B | None) :: A → B`

**DP Formulation**:
```python
states: {Input}
actions: {lookup_success, default_fallback, raise_error}
transition: T(s, lookup) = fixtures[s] if s in fixtures else default
gamma: 0.99

def reward(s: Input, a: Action, s_: Output) -> float:
    correctness = 1.0 if a == "lookup_success" else 0.5
    compression = len(fixtures) / total_behaviors
    return 0.5 * correctness + 0.3 * compression + 0.2 * curated
```

**Constitutional Focus**: R_GENERATIVE (compression) + R_COMPOSABLE

**Use Cases**: Regression testing, known input/output pairs, deterministic CI

---

## Probe II: ChaosProbe (EPISTEMIC)

**Analysis Mode**: EPISTEMIC - How justified is X? What are resilience bounds?

### FailingProbe: Bottom Morphism

**Signature**: `FailingProbe[A, E](config: FailingConfig) :: A → ⊥`

**DP Formulation**:
```python
states: {System}
actions: {fail_syntax, fail_type, fail_network, fail_timeout}
transition: T(s, fail) = Error if count < fail_count else recovery_token
gamma: 0.99

def reward(s: System, a: FailAction, s_: System) -> float:
    safety_preserved = 1.0 if s_.no_data_loss else 0.0
    error_propagates = 1.0 if s_.correct_error_type else 0.0
    recovery = s_.recovery_success_rate
    return 0.5 * safety_preserved + 0.3 * error_propagates + 0.2 * recovery
```

**Constitutional Focus**: R_ETHICAL (safety) + R_COMPOSABLE (error propagation)

**Config**:
```python
@dataclass
class FailingConfig:
    error_type: FailureType  # SYNTAX, TYPE, NETWORK, TIMEOUT
    fail_count: int = -1     # -1 = always fail
    recovery_token: Any = None
    seed: int | None = None
```

**Use Cases**: Retry logic, error handling, circuit breakers, exponential backoff

---

### NoiseProbe: Perturbation Morphism

**Signature**: `NoiseProbe[A](level: float, seed: int) :: A → A + ε`

**DP Formulation**:
```python
states: {Input}
actions: {perturb_case, perturb_whitespace, perturb_typos, perturb_synonyms}
transition: T(s, perturb) = s + noise(level, seed)
gamma: 0.99

def reward(s: Input, a: PerturbAction, s_: Input) -> float:
    semantic_distance = measure_distance(s, s_)
    resilience = 1.0 - semantic_distance
    safety = 1.0 if s_.no_harmful_drift else 0.0
    return 0.5 * resilience + 0.5 * safety
```

**Constitutional Focus**: R_ETHICAL (safety under noise) + R_COMPOSABLE (semantic stability)

**Use Cases**: Semantic robustness testing, typo handling, case insensitivity validation

---

### LatencyProbe: Temporal Morphism

**Signature**: `LatencyProbe[A](delay: float, variance: float) :: (A, t) → (A, t+Δ)`

**DP Formulation**:
```python
states: {TimedInput}
actions: {add_delay}
transition: T((a, t), add_delay) = (a, t + delay + random(-variance, +variance))
gamma: 0.99

def reward(s: TimedInput, a: Action, s_: TimedOutput) -> float:
    within_budget = 1.0 if s_.elapsed < s.timeout_budget else 0.0
    graceful_timeout = 1.0 if s_.timeout_handled else 0.0
    return 0.6 * within_budget + 0.4 * graceful_timeout
```

**Constitutional Focus**: R_ETHICAL (timeout safety) + R_HETERARCHICAL (context-aware timeouts)

**Use Cases**: Timeout handling, latency tolerance, slow network simulation

---

### FlakyProbe: Probabilistic Morphism

**Signature**: `FlakyProbe[A, B](wrapped: Agent, probability: float, seed: int) :: A → B ∪ {⊥}`

**DP Formulation**:
```python
states: {System}
actions: {succeed, fail_stochastically}
transition: T(s, a) = wrapped(s) if random() > p else Error
gamma: 0.99

def reward(s: System, a: Action, s_: System) -> float:
    retry_success = s_.retry_eventually_succeeded
    graceful_degradation = s_.fallback_activated
    return 0.6 * retry_success + 0.4 * graceful_degradation
```

**Constitutional Focus**: R_COMPOSABLE (retry resilience) + R_ETHICAL (graceful degradation)

**Use Cases**: Stochastic failure testing, flaky integration validation

---

## Probe III: WitnessProbe (DIALECTICAL)

**Analysis Mode**: DIALECTICAL - What tensions exist? How do contradictions manifest?

### SpyProbe: Writer Monad

**Signature**: `SpyProbe[A](label: str) :: A → A` (with side effect: history.append)

**DP Formulation**:
```python
states: {Flow}
actions: {observe}
transition: T(s, observe) = s  # Identity morphism
gamma: 0.99

def reward(s: Flow, a: ObserveAction, s_: Flow) -> float:
    auditability = s_.trace_completeness
    context_captured = s_.relevant_metadata_logged
    compression = s_.trace_compression_ratio
    return 0.6 * auditability + 0.3 * context_captured + 0.1 * compression
```

**Constitutional Focus**: R_ETHICAL (auditability) + R_HETERARCHICAL (context awareness)

**Side Effect**: Appends to `self.history: List[A]` for inspection

**Use Cases**: Pipeline debugging, data flow inspection, intermediate value logging

---

### PredicateProbe: Gate Morphism

**Signature**: `PredicateProbe[A](predicate: Callable[[A], bool], name: str) :: A → A ∪ {⊥}`

**DP Formulation**:
```python
states: {Input}
actions: {gate_pass, gate_fail}
transition: T(s, gate_pass) = s if predicate(s) else Error
gamma: 0.99

def reward(s: Input, a: GateAction, s_: Output) -> float:
    invariant_held = 1.0 if a == "gate_pass" else 0.0
    purpose_clear = 1.0 if predicate_purpose_documented else 0.0
    return 0.7 * invariant_held + 0.3 * purpose_clear
```

**Constitutional Focus**: R_ETHICAL (invariants enforce safety) + R_TASTEFUL (clear purpose)

**Use Cases**: Runtime type validation, invariant checking, assertion-based testing

---

### CounterProbe: Invocation Tracker

**Signature**: `CounterProbe[A](name: str, max_invocations: int = -1) :: A → A`

**DP Formulation**:
```python
states: {Flow}
actions: {count}
transition: T(s, count) = s  # Identity
gamma: 0.99

def reward(s: Flow, a: CountAction, s_: Flow) -> float:
    within_limit = 1.0 if s_.count < s.max_invocations else 0.0
    tracking_accurate = 1.0
    return 0.8 * within_limit + 0.2 * tracking_accurate
```

**Constitutional Focus**: R_ETHICAL (detect runaway loops) + R_HETERARCHICAL (context tracking)

**Use Cases**: Invocation frequency analysis, loop detection, performance profiling

---

### MetricsProbe: Performance Profiler

**Signature**: `MetricsProbe[A](name: str, latency_budget: float) :: A → A`

**DP Formulation**:
```python
states: {TimedFlow}
actions: {measure}
transition: T(s, measure) = s  # Identity, but records timing
gamma: 0.99

def reward(s: TimedFlow, a: MeasureAction, s_: TimedFlow) -> float:
    within_budget = 1.0 if s_.avg_time < latency_budget else 0.5
    insight_provided = s_.performance_insight_score
    return 0.6 * within_budget + 0.4 * insight_provided
```

**Constitutional Focus**: R_ETHICAL (performance budgets) + R_JOY_INDUCING (insight)

**Use Cases**: Performance profiling, latency measurement, bottleneck detection

---

## Probe IV: JudgeProbe (GENERATIVE)

**Analysis Mode**: GENERATIVE - Can X regenerate from axioms? Is output semantically correct?

### SemanticJudge: LLM Evaluation

**Signature**: `JudgeProbe[(Intent, Output), Score](criteria: JudgmentCriteria, llm: LLM) :: (A,B) → [0,1]`

**DP Formulation**:
```python
states: {Quality}
actions: {evaluate_correctness, evaluate_safety, evaluate_style}
transition: T(s, eval) = llm.judge(s.intent, s.output, criteria)
gamma: 0.99

def reward(s: Quality, a: EvalAction, s_: Quality) -> float:
    correctness = s_.semantic_accuracy
    safety = s_.safety_score
    insight = s_.judgment_insight_provided
    return 0.4 * correctness + 0.4 * safety + 0.2 * insight
```

**Constitutional Focus**: R_GENERATIVE (axiom alignment) + R_ETHICAL (safety) + R_JOY_INDUCING (insight)

**JudgmentCriteria**:
```python
@dataclass
class JudgmentCriteria:
    correctness: float = 1.0   # Weight
    safety: float = 1.0
    style: float = 0.5
```

**Use Cases**: LLM-as-judge evaluation, semantic correctness, alignment testing

---

### CorrectnessJudge: Specification Conformance

**Signature**: `CorrectnessJudge[(Spec, Impl), Bool] :: (Spec, Code) → {True, False}`

**DP Formulation**:
```python
states: {SpecImpl}
actions: {check_conformance}
transition: T(s, check) = spec_matches_impl(s.spec, s.impl)
gamma: 0.99

def reward(s: SpecImpl, a: Action, s_: bool) -> float:
    conformance = 1.0 if s_ else 0.0
    generative = spec_can_regenerate_impl(s.spec, s.impl)
    return 0.7 * conformance + 0.3 * generative
```

**Constitutional Focus**: R_GENERATIVE (impl regenerates from spec)

**Use Cases**: Spec-impl drift detection, conformance testing

---

### SafetyJudge: Vulnerability Detection

**Signature**: `SafetyJudge[Code, Risk] :: Code → [0,1]`

**DP Formulation**:
```python
states: {Code}
actions: {scan_vulnerabilities}
transition: T(s, scan) = vulnerability_score(s)
gamma: 0.99

def reward(s: Code, a: Action, s_: float) -> float:
    safety = 1.0 - s_  # Lower risk = higher reward
    actionable = 1.0 if s_.has_fix_suggestions else 0.5
    return 0.8 * safety + 0.2 * actionable
```

**Constitutional Focus**: R_ETHICAL (safety bounds) + R_CURATED (actionable findings)

**Use Cases**: Security scanning, safety validation, vulnerability detection

---

## Probe V: TrustProbe (META)

**Analysis Mode**: META - What are the unknown failure modes?

**Purpose**: Discover failure modes via systematic exploration of stress coordinate space.

**DP Formulation**:
```python
states: {Reliability}
actions: {explore_coordinate(noise, failure_prob, latency, drift)}
transition: T(s, explore) = gym_report(s, coordinate)
gamma: 0.99

def reward(s: Reliability, a: StressAction, s_: Reliability) -> float:
    coverage = s_.stress_space_explored / total_space
    discovery = s_.new_failures_found / total_tests
    curated = 1.0 if a.coordinate_intentional else 0.5
    return 0.4 * coverage + 0.4 * discovery + 0.2 * curated
```

**Constitutional Focus**: R_CURATED (intentional exploration) + R_ETHICAL (pre-production discovery)

**Stress Coordinate**:
```python
@dataclass
class StressCoordinate:
    noise_level: float         # [0.0, 1.0]
    failure_probability: float # [0.0, 1.0]
    latency_ms: int           # [0, 10000]
    semantic_drift: float      # [0.0, 1.0]
```

**See**: `adversarial.md` for full AdversarialGym specification and multi-dimensional sweep implementation.

---

## Summary Table

| Probe Variant | Morphism | States | Actions | R_Primary | Use Case |
|---------------|----------|--------|---------|-----------|----------|
| MockProbe | `A → b` | Config | {constant, latency} | COMPOSABLE | Fast testing |
| FixtureProbe | `A → B` | Input | {lookup, fallback} | GENERATIVE | Regression |
| FailingProbe | `A → ⊥` | System | {fail_N_times} | ETHICAL | Error handling |
| NoiseProbe | `A → A+ε` | Input | {perturb_type} | ETHICAL | Robustness |
| LatencyProbe | `(A,t) → (A,t+Δ)` | TimedInput | {delay} | ETHICAL | Timeout |
| FlakyProbe | `A → B∪{⊥}` | System | {stochastic_fail} | COMPOSABLE | Retry |
| SpyProbe | `A → A` | Flow | {observe} | ETHICAL | Debugging |
| PredicateProbe | `A → A∪{⊥}` | Input | {gate} | ETHICAL | Invariants |
| CounterProbe | `A → A` | Flow | {count} | HETERARCHICAL | Profiling |
| MetricsProbe | `A → A` | TimedFlow | {measure} | JOY_INDUCING | Performance |
| JudgeProbe | `(A,B) → [0,1]` | Quality | {evaluate} | GENERATIVE | Semantics |
| TrustProbe | `Agent → Report` | Reliability | {stress} | CURATED | Discovery |

---

## AnalysisMode Mapping

| AnalysisMode | Probes | Primary Principle | Question Answered |
|--------------|--------|-------------------|-------------------|
| **CATEGORICAL** | NullProbe (Mock, Fixture) | COMPOSABLE | Does X satisfy composition laws? |
| **EPISTEMIC** | ChaosProbe (Failing, Noise, Latency, Flaky) | ETHICAL | How justified is X's resilience? |
| **DIALECTICAL** | WitnessProbe (Spy, Predicate, Counter, Metrics) | HETERARCHICAL | What tensions/contradictions exist? |
| **GENERATIVE** | JudgeProbe (Semantic, Correctness, Safety) | GENERATIVE | Can X regenerate from axioms? |
| **META** | TrustProbe (Gym) | CURATED | What are unknown failure modes? |

---

## See Also

- [README.md](README.md) - TruthFunctors overview and philosophy
- [algebra.md](algebra.md) - ProbeOperad foundations, Bellman equations, Galois loss
- [adversarial.md](adversarial.md) - Probe V: TrustProbe chaos engineering
- [../theory/dp-native-kgents.md](../theory/dp-native-kgents.md) - DP-native architecture
- [../theory/analysis-operad.md](../theory/analysis-operad.md) - Four analysis modes
- [../principles.md](../principles.md) - Seven constitutional principles

---

*"Every probe is a value function. Every verification is a Bellman solution. Every trace is a witness."*
