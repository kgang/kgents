# TruthFunctor Taxonomy: Detailed Specifications

This document provides comprehensive specifications for each type of TruthFunctor (Probes I-V), including DP formulations, constitutional rewards, and usage patterns.

> **Note**: Probe V (TrustProbe) is specified in [adversarial.md](adversarial.md).

---

## Probe I: NullProbe

NullProbes replace computational morphisms with constants or deterministic lookups, enabling **categorical verification** without expensive operations.

### AnalysisMode: CATEGORICAL

**Core Question**: Does X satisfy composition laws (associativity, identity, closure)?

### 1.1 MockProbe: The Constant Morphism

**Category Theoretic Definition**: The constant morphism $c_b: A \to B$ where $\forall a \in A: c_b(a) = b$ for fixed $b \in B$.

**Signature**: `MockProbe[A, B](output: B, delay: float = 0.0) :: A → B`

**DP Formulation**:
```python
class MockProbeFormulation(ProblemFormulation):
    """Verify composition laws via constant morphisms."""

    states: FrozenSet[Config]       # System configurations
    actions: FrozenSet[MockAction]  # {return_constant, simulate_latency}

    def reward(self, s: Config, a: MockAction, s_: Config) -> PrincipleScore:
        """Constitutional reward for mocking."""
        return PrincipleScore(
            composable=self._verify_composition_laws(s, a, s_),
            tasteful=1.0 if s_.purpose_clear else 0.0,
            generative=s_.compression_ratio,  # fixtures compress behavior
            curated=1.0 if s_.intentional_mock else 0.0,
        )

    def _verify_composition_laws(self, s: Config, a: MockAction, s_: Config) -> float:
        """Check associativity and identity laws."""
        laws_satisfied = 0
        laws_total = 3

        # Law 1: Associativity (mock doesn't break it)
        if self._test_associativity(s_):
            laws_satisfied += 1

        # Law 2: Identity (mock >> id = mock)
        if self._test_identity(s_):
            laws_satisfied += 1

        # Law 3: Constancy (always returns same value)
        if s_.is_constant:
            laws_satisfied += 1

        return laws_satisfied / laws_total
```

**Constitutional Reward**:
- **COMPOSABLE** (0.6): Verifies that mocking preserves composition laws
- **TASTEFUL** (0.4): Mock serves clear purpose (not arbitrary)
- **GENERATIVE**: Compression via fixture reuse
- **CURATED**: Intentional selection of mock values

**Properties**:
- **Deterministic**: Always returns the same output
- **Fast**: No LLM calls, minimal computation
- **Transparent**: Can be instrumented with delays for timing tests

**Configuration**:
```python
@dataclass
class MockConfig(Generic[B]):
    output: B                    # The fixed output to return
    delay: float = 0.0           # Simulated latency in seconds
    invocation_limit: int = -1   # Max invocations (-1 = unlimited)
    analysis_mode: AnalysisMode = AnalysisMode.CATEGORICAL
```

**Implementation Skeleton**:
```python
class MockProbe(TruthFunctor[I, O]):
    """The Constant Morphism b."""

    def __init__(self, output: O, delay: float = 0.0):
        self.name = f"MockProbe({type(output).__name__})"
        self.output = output
        self.delay = delay
        self.invocation_count = 0
        self.__is_verification__ = True
        self.analysis_mode = AnalysisMode.CATEGORICAL

    async def value(self, state: I) -> PolicyTrace[O]:
        """Compute value (returns PolicyTrace with mock output)."""
        if self.delay > 0:
            await asyncio.sleep(self.delay)

        self.invocation_count += 1

        # Compute constitutional reward
        reward = self.reward(
            s=state,
            a="return_constant",
            s_=self.output
        )

        return PolicyTrace(
            states=(state, self.output),
            actions=("return_constant",),
            rewards=(reward.total,),
            rationales=(f"Mocked with constant: {self.output}",),
            value=reward.total,
        )
```

**Use Cases**:
```python
# Mock expensive LLM call
mock_hypothesis = MockProbe(
    output=HypothesisOutput(hypotheses=["H1", "H2", "H3"])
)

# Fast pipeline testing
fast_pipeline = mock_hypothesis >> ExperimentAgent() >> ValidateAgent()

# Timing tests
slow_mock = MockProbe(output="Result", delay=0.5)  # Simulates 500ms latency
```

**Laws**:
- **Constancy**: `∀ a1, a2 ∈ A: MockProbe(b).value(a1).value == MockProbe(b).value(a2).value`
- **Identity Absorption**: `MockProbe(b) >> f ≠ f` (unless f is also constant)

---

### 1.2 FixtureProbe: The Lookup Morphism

**Category Theoretic Definition**: A morphism $f: A \to B$ defined by a lookup table (hash map).

**Signature**: `FixtureProbe[A, B](fixtures: Dict[A, B], default: Optional[B] = None) :: A → B`

**DP Formulation**:
```python
class FixtureProbeFormulation(ProblemFormulation):
    """Regression testing via deterministic lookup."""

    def reward(self, s: Input, a: LookupAction, s_: Output) -> PrincipleScore:
        return PrincipleScore(
            composable=1.0 if a == "lookup_success" else 0.0,
            tasteful=1.0 if s_.from_curated_fixture else 0.0,
            generative=len(fixtures) / total_behaviors,  # compression
            ethical=1.0,  # regression testing preserves safety
        )
```

**Properties**:
- **Deterministic**: Same input always yields same output
- **Regression Testing**: Captures known input/output pairs
- **Fast**: O(1) lookup

**Configuration**:
```python
@dataclass
class FixtureConfig(Generic[A, B]):
    fixtures: Dict[A, B]          # Input → Output mapping
    default: Optional[B] = None   # Fallback if input not in fixtures
    strict: bool = True            # Raise error on missing input if True
    analysis_mode: AnalysisMode = AnalysisMode.CATEGORICAL
```

**Implementation Skeleton**:
```python
class FixtureProbe(TruthFunctor[I, O]):
    """Deterministic map f: I → O using fixtures."""

    def __init__(self, fixtures: Dict[I, O], default: Optional[O] = None, strict: bool = True):
        self.name = "FixtureProbe"
        self.fixtures = fixtures
        self.default = default
        self.strict = strict
        self.__is_verification__ = True
        self.analysis_mode = AnalysisMode.CATEGORICAL

    async def value(self, state: I) -> PolicyTrace[O]:
        """Lookup input in fixture table."""
        if state in self.fixtures:
            output = self.fixtures[state]
            action = "lookup_success"
        elif self.default is not None:
            output = self.default
            action = "default_fallback"
        elif self.strict:
            raise KeyError(f"No fixture for input: {state}")
        else:
            raise RuntimeError("FixtureProbe: No default and strict=True")

        reward = self.reward(s=state, a=action, s_=output)

        return PolicyTrace(
            states=(state, output),
            actions=(action,),
            rewards=(reward.total,),
            rationales=(f"Fixture lookup: {state} → {output}",),
            value=reward.total,
        )
```

**Use Cases**:
```python
# Regression test fixtures
fixtures = {
    "Fix auth bug": "Added OAuth validation",
    "Optimize query": "Added database index",
}
fixture_probe = FixtureProbe(fixtures)

# Ensure consistency across refactors
trace = await fixture_probe.value("Fix auth bug")
assert trace.states[-1] == "Added OAuth validation"  # Must never change
```

---

## Probe II: ChaosProbe

ChaosProbes inject controlled chaos to verify **epistemic bounds**—how justified are resilience claims?

### AnalysisMode: EPISTEMIC

**Core Question**: How justified is X? What are the resilience bounds?

### 2.1 FailingProbe: The Bottom Morphism

**Category Theoretic Definition**: The morphism $\bot: A \to \emptyset$ that never successfully returns.

**Signature**: `FailingProbe[A, E](config: FailingConfig) :: A → Error`

**DP Formulation**:
```python
class FailingProbeFormulation(ProblemFormulation):
    """Verify error handling via deliberate failure."""

    def reward(self, s: System, a: FailAction, s_: System) -> PrincipleScore:
        return PrincipleScore(
            ethical=1.0 if s_.safety_preserved_despite_error else 0.0,
            composable=1.0 if s_.error_propagates_correctly else 0.0,
            heterarchical=s_.recovery_strategy_score,
            curated=1.0 if a.failure_type == s.expected_failure else 0.0,
        )
```

**Constitutional Reward**:
- **ETHICAL** (0.5): Safety preserved under failure
- **COMPOSABLE** (0.3): Errors propagate correctly through composition
- **HETERARCHICAL** (0.2): Context-appropriate recovery strategies

**Properties**:
- **Deliberate Failure**: Fails in controlled, reproducible ways
- **Configurable**: Fail N times, then succeed or fail forever
- **Typed Errors**: Different error types (syntax, type, runtime, network)

**Configuration**:
```python
@dataclass
class FailingConfig:
    error_type: FailureType        # Which kind of error to raise
    fail_count: int = -1           # -1 = always fail, N = fail N times
    error_message: str = "Deliberate failure"
    recovery_token: Optional[Any] = None  # What to return after fail_count
    seed: Optional[int] = None     # For deterministic failures
    analysis_mode: AnalysisMode = AnalysisMode.EPISTEMIC

class FailureType(Enum):
    SYNTAX = "syntax_error"
    TYPE = "type_error"
    IMPORT = "import_error"
    RUNTIME = "runtime_error"
    TIMEOUT = "timeout_error"
    NETWORK = "network_error"
    HALLUCINATION = "hallucination"
```

**Use Cases**:
```python
# Test retry logic
failing = FailingProbe(FailingConfig(
    error_type=FailureType.NETWORK,
    fail_count=2,
    recovery_token="Success"
))

# Should fail twice, then succeed
for i in range(3):
    try:
        trace = await failing.value("test")
        assert i == 2, "Should only succeed on 3rd attempt"
    except ConnectionError:
        assert i < 2, "Should only fail first 2 attempts"
```

---

### 2.2 NoiseProbe: Identity with Perturbation

**Category Theoretic Definition**: The morphism $N_\epsilon: A \to A$ where $N_\epsilon(a) = a + \epsilon$ for small perturbation $\epsilon$.

**Signature**: `NoiseProbe[A](level: float, seed: int = None) :: A → A + ε`

**DP Formulation**:
```python
class NoiseProbeFormulation(ProblemFormulation):
    """Verify semantic robustness via perturbation."""

    def reward(self, s: Input, a: PerturbAction, s_: PerturbedInput) -> PrincipleScore:
        resilience = 1.0 - self._semantic_distance(s, s_)
        return PrincipleScore(
            ethical=1.0 if s_.safety_preserved else 0.0,
            composable=resilience,  # semantic stability
            curated=1.0 if a.perturbation_type in allowed_types else 0.0,
        )
```

**Constitutional Reward**:
- **ETHICAL** (0.5): Safety preserved under noise
- **COMPOSABLE** (0.3): Semantic stability (resilience)
- **CURATED** (0.2): Intentional perturbation selection

**Properties**:
- **Semantic Noise**: Changes input while preserving meaning
- **Configurable Level**: 0.0 (no noise) to 1.0 (maximal noise)
- **Deterministic**: Same seed yields same perturbations

**Configuration**:
```python
@dataclass
class NoiseConfig:
    level: float = 0.1              # 0.0 to 1.0
    seed: Optional[int] = None      # For reproducibility
    noise_types: List[NoiseType] = field(default_factory=lambda: [
        NoiseType.CASE, NoiseType.WHITESPACE, NoiseType.TYPOS
    ])
    analysis_mode: AnalysisMode = AnalysisMode.EPISTEMIC

class NoiseType(Enum):
    CASE = "case_change"            # Change capitalization
    WHITESPACE = "whitespace"       # Add/remove spaces
    TYPOS = "typos"                 # Swap adjacent characters
    SYNONYMS = "synonyms"           # Replace with synonyms
    PUNCTUATION = "punctuation"     # Add/remove punctuation
```

**Use Cases**:
```python
# Test semantic robustness
noise = NoiseProbe(level=0.3, seed=42)
agent = SemanticAgent()

original = "Fix the authentication bug"
trace = await noise.value(original)
perturbed = trace.states[-1]  # Might be "Fix  the  Authentication  Bug"

# Agent should handle both inputs similarly
result_original = await agent.invoke(original)
result_perturbed = await agent.invoke(perturbed)

assert semantic_similarity(result_original, result_perturbed) > 0.9
```

---

### 2.3 LatencyProbe: Identity with Temporal Cost

**Category Theoretic Definition**: The morphism $L_\Delta: (A, t) \to (A, t + \Delta)$ adding temporal delay.

**Signature**: `LatencyProbe[A](delay: float, variance: float = 0.0) :: (A, t) → (A, t + Δ)`

**DP Formulation**:
```python
class LatencyProbeFormulation(ProblemFormulation):
    """Verify timeout handling via temporal perturbation."""

    def reward(self, s: TimedInput, a: DelayAction, s_: TimedOutput) -> PrincipleScore:
        within_budget = s_.elapsed < s.timeout_budget
        return PrincipleScore(
            ethical=1.0 if within_budget else 0.5,  # timeout is safety issue
            composable=1.0,  # identity morphism
            heterarchical=1.0 if s_.timeout_strategy_appropriate else 0.0,
        )
```

---

### 2.4 FlakyProbe: Probabilistic Failure

**Category Theoretic Definition**: The morphism $F_p: A \to B \cup \{\bot\}$ that fails with probability $p$.

**Signature**: `FlakyProbe[I, O](wrapped: Agent[I, O], probability: float, seed: int) :: A → B ∪ {⊥}`

**DP Formulation**:
```python
class FlakyProbeFormulation(ProblemFormulation):
    """Verify stochastic resilience."""

    def reward(self, s: System, a: StochasticAction, s_: System) -> PrincipleScore:
        return PrincipleScore(
            ethical=1.0 if s_.degrades_gracefully else 0.0,
            composable=s_.retry_success_rate,
            curated=1.0 if a.probability == s.target_flakiness else 0.0,
        )
```

---

## Probe III: WitnessProbe

WitnessProbes are identity morphisms with side effects, enabling **dialectical verification**—capturing tensions and contradictions.

### AnalysisMode: DIALECTICAL

**Core Question**: What tensions exist? How do contradictions manifest?

### 3.1 SpyProbe: The Writer Monad

**Category Theoretic Definition**: The identity morphism with logging: $S: A \to (A, [A])$.

**Signature**: `SpyProbe[A](label: str) :: A → A` (with side effect: append to history)

**DP Formulation**:
```python
class SpyProbeFormulation(ProblemFormulation):
    """Capture data flow tensions via transparent observation."""

    def reward(self, s: Flow, a: ObserveAction, s_: Flow) -> PrincipleScore:
        return PrincipleScore(
            ethical=s_.auditability_score,  # transparency enables accountability
            heterarchical=s_.context_captured,  # observes relevant context
            generative=s_.trace_compression,  # history compresses behavior
            composable=1.0,  # identity morphism
        )
```

**Constitutional Reward**:
- **ETHICAL** (0.6): Auditability through transparent observation
- **HETERARCHICAL** (0.3): Context-aware observation
- **GENERATIVE** (0.1): Traces compress system behavior

**Implementation Skeleton**:
```python
class SpyProbe(TruthFunctor[A]):
    """Identity morphism with side effects (Writer Monad)."""

    def __init__(self, label: str):
        self.name = f"SpyProbe({label})"
        self.label = label
        self.history: List[A] = []
        self.__is_verification__ = True
        self.analysis_mode = AnalysisMode.DIALECTICAL

    async def value(self, state: A) -> PolicyTrace[A]:
        """Record input and pass through."""
        print(f"[{self.name}] Capturing: {state}")
        self.history.append(state)

        reward = self.reward(s=state, a="observe", s_=state)

        return PolicyTrace(
            states=(state, state),
            actions=("observe",),
            rewards=(reward.total,),
            rationales=(f"Captured: {state}",),
            value=reward.total,
        )
```

**Use Cases**:
```python
# Spy on intermediate pipeline data
spy = SpyProbe(label="Hypotheses")
pipeline = GenerateHypotheses() >> spy >> RunExperiments()

trace = await pipeline.invoke(input_data)

# Inspect what was passed
print(spy.history)  # [HypothesisOutput(...)]
assert len(spy.history) == 1
```

---

### 3.2 PredicateProbe: The Gate Morphism

**Category Theoretic Definition**: $P: A \to A \cup \{\bot\}$ where output succeeds iff $P(a) = \text{True}$.

**DP Formulation**:
```python
class PredicateProbeFormulation(ProblemFormulation):
    """Verify invariants via runtime gates."""

    def reward(self, s: Input, a: GateAction, s_: Output) -> PrincipleScore:
        return PrincipleScore(
            ethical=1.0 if a == "gate_pass" else 0.0,  # invariant held
            composable=1.0,  # identity when predicate holds
            tasteful=1.0 if s.predicate_purpose_clear else 0.0,
        )
```

**Use Cases**:
```python
# Runtime type validation
def is_valid_hypothesis(h: HypothesisOutput) -> bool:
    return len(h.hypotheses) > 0

validator = PredicateProbe(is_valid_hypothesis, name="NonEmptyHypotheses")

# Will raise if hypotheses list is empty
pipeline = GenerateHypotheses() >> validator >> RunExperiments()
```

---

### 3.3 CounterProbe: Invocation Tracker

**DP Formulation**:
```python
class CounterProbeFormulation(ProblemFormulation):
    """Verify invocation frequency."""

    def reward(self, s: Flow, a: CountAction, s_: Flow) -> PrincipleScore:
        return PrincipleScore(
            ethical=1.0 if s_.count < s.expected_max else 0.5,
            heterarchical=1.0,  # tracks context
            composable=1.0,  # identity
        )
```

---

### 3.4 MetricsProbe: Performance Profiler

**DP Formulation**:
```python
class MetricsProbeFormulation(ProblemFormulation):
    """Verify performance bounds."""

    def reward(self, s: TimedFlow, a: MeasureAction, s_: TimedFlow) -> PrincipleScore:
        within_budget = s_.avg_time < s.latency_budget
        return PrincipleScore(
            ethical=1.0 if within_budget else 0.5,
            joy_inducing=s_.performance_insight_score,
            composable=1.0,
        )
```

---

## Probe IV: JudgeProbe

JudgeProbes use LLMs to evaluate semantic correctness, enabling **generative verification**—can X regenerate from axioms?

### AnalysisMode: GENERATIVE

**Core Question**: Can X regenerate from axioms? Is output semantically correct?

### 4.1 SemanticJudge: LLM-as-Judge

**Signature**: `SemanticJudge[(Intent, Output), Score] :: (A, B) → [0, 1]`

**DP Formulation**:
```python
class JudgeProbeFormulation(ProblemFormulation):
    """Verify semantic correctness via LLM evaluation."""

    def reward(self, s: Quality, a: EvalAction, s_: Quality) -> PrincipleScore:
        return PrincipleScore(
            ethical=s_.safety_score,  # LLM evaluates safety
            joy_inducing=s_.insight_provided,  # judgment teaches
            generative=s_.alignment_with_axioms,  # regenerable from principles
            tasteful=s_.evaluation_clarity,
        )
```

**Constitutional Reward**:
- **ETHICAL** (0.4): Safety and alignment verification
- **JOY_INDUCING** (0.2): Evaluation provides insight and teaching
- **GENERATIVE** (0.3): Judgments regenerate from constitutional axioms
- **TASTEFUL** (0.1): Clear evaluation criteria

**Implementation Sketch**:
```python
@dataclass
class JudgmentCriteria:
    correctness: float = 1.0   # Weight for correctness
    safety: float = 1.0        # Weight for safety
    style: float = 0.5         # Weight for style

class JudgeProbe(TruthFunctor):
    """LLM evaluates semantic correctness."""

    def __init__(self, criteria: JudgmentCriteria, llm: LLM):
        self.name = "JudgeProbe"
        self.criteria = criteria
        self.llm = llm
        self.__is_verification__ = True
        self.analysis_mode = AnalysisMode.GENERATIVE

    async def value(self, state: Tuple[Intent, Output]) -> PolicyTrace[float]:
        """Evaluate input/output pair."""
        intent, output = state

        prompt = f"""
        Evaluate this agent interaction:

        Intent: {intent}
        Output: {output}

        Score from 0.0 to 1.0 on:
        - Correctness: Does output satisfy intent?
        - Safety: Is output safe and ethical?
        - Style: Is output well-formatted?

        Return JSON: {{"correctness": 0.0-1.0, "safety": 0.0-1.0, "style": 0.0-1.0}}
        """

        response = await self.llm.generate(prompt)
        scores = json.loads(response)

        # Weighted average
        total_score = (
            scores["correctness"] * self.criteria.correctness +
            scores["safety"] * self.criteria.safety +
            scores["style"] * self.criteria.style
        )
        weight_sum = self.criteria.correctness + self.criteria.safety + self.criteria.style
        final_score = total_score / weight_sum

        reward = self.reward(s=state, a="evaluate", s_=(intent, output, scores))

        return PolicyTrace(
            states=(state, final_score),
            actions=("evaluate",),
            rewards=(reward.total,),
            rationales=(f"LLM judgment: {scores}",),
            value=final_score,
        )
```

---

## Summary Table

| Probe | AnalysisMode | Morphism | DP Reward Focus | Purpose |
|-------|--------------|----------|-----------------|---------|
| **MockProbe** | CATEGORICAL | $A \to b$ | R_COMPOSABLE | Verify composition laws |
| **FixtureProbe** | CATEGORICAL | $A \to B$ | R_GENERATIVE | Regression testing |
| **FailingProbe** | EPISTEMIC | $A \to \bot$ | R_ETHICAL | Error handling bounds |
| **NoiseProbe** | EPISTEMIC | $A \to A + \epsilon$ | R_COMPOSABLE | Semantic robustness |
| **LatencyProbe** | EPISTEMIC | $(A, t) \to (A, t + \Delta)$ | R_ETHICAL | Timeout handling |
| **FlakyProbe** | EPISTEMIC | $A \to B \cup \{\bot\}$ | R_COMPOSABLE | Stochastic resilience |
| **SpyProbe** | DIALECTICAL | $A \to A$ | R_ETHICAL | Transparency/auditability |
| **PredicateProbe** | DIALECTICAL | $A \to A \cup \{\bot\}$ | R_ETHICAL | Invariant verification |
| **CounterProbe** | DIALECTICAL | $A \to A$ | R_HETERARCHICAL | Invocation tracking |
| **MetricsProbe** | DIALECTICAL | $A \to A$ | R_JOY_INDUCING | Performance profiling |
| **JudgeProbe** | GENERATIVE | $(A, B) \to [0,1]$ | R_GENERATIVE | Semantic evaluation |
| **TrustProbe** | META | $Agent \to Report$ | R_CURATED | Chaos engineering |

> **Probe V Details**: See [adversarial.md](adversarial.md) for full TrustProbe specification.

---

## AnalysisMode to Constitutional Principle Mapping

| AnalysisMode | Primary Principle | Secondary Principles | Probe Types |
|--------------|-------------------|----------------------|-------------|
| **CATEGORICAL** | COMPOSABLE | TASTEFUL, GENERATIVE | NullProbe (Mock, Fixture) |
| **EPISTEMIC** | ETHICAL | COMPOSABLE, CURATED | ChaosProbe (Failing, Noise, Latency, Flaky) |
| **DIALECTICAL** | ETHICAL | HETERARCHICAL, GENERATIVE | WitnessProbe (Spy, Predicate, Counter, Metrics) |
| **GENERATIVE** | GENERATIVE | ETHICAL, JOY_INDUCING | JudgeProbe (Semantic, Correctness, Safety) |
| **META** | CURATED | ETHICAL, COMPOSABLE | TrustProbe (Gym, Coordinate, MultiDim) |

---

## See Also

- [README.md](README.md) - TruthFunctors overview
- [algebra.md](algebra.md) - ProbeOperad foundations
- [adversarial.md](adversarial.md) - Probe V: Chaos engineering
- [../theory/dp-native-kgents.md](../theory/dp-native-kgents.md) - DP-native architecture
- [../theory/analysis-operad.md](../theory/analysis-operad.md) - Four analysis modes
