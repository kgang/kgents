# T-gents Taxonomy: Detailed Specifications

This document provides comprehensive specifications for each type of T-gent, including implementation details, configuration, and usage patterns.

---

## Type I: The Nullifiers

Nullifiers replace computational morphisms with constants or deterministic lookups. They eliminate non-determinism for fast, predictable testing.

### 1.1 MockAgent: The Constant Morphism

**Category Theoretic Definition**: The constant morphism $c_b: A \to B$ where $\forall a \in A: c_b(a) = b$ for fixed $b \in B$.

**Signature**: `MockAgent[A, B](output: B, delay: float = 0.0) :: A → B`

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
```

**Implementation Skeleton**:
```python
class MockAgent(Generic[I, O]):
    """The Constant Morphism b."""

    def __init__(self, output: O, delay: float = 0.0):
        self.name = f"Mock({type(output).__name__})"
        self.output = output
        self.delay = delay
        self.invocation_count = 0
        self.__is_test__ = True

    async def invoke(self, input_data: I) -> O:
        """Always returns self.output, ignoring input."""
        if self.delay > 0:
            await asyncio.sleep(self.delay)

        self.invocation_count += 1
        return self.output

    def reset(self):
        """Reset for test isolation."""
        self.invocation_count = 0
```

**Use Cases**:
```python
# Mock expensive LLM call
mock_hypothesis = MockAgent(
    output=HypothesisOutput(hypotheses=["H1", "H2", "H3"])
)

# Fast pipeline testing
fast_pipeline = mock_hypothesis >> ExperimentAgent() >> ValidateAgent()

# Timing tests
slow_mock = MockAgent(output="Result", delay=0.5)  # Simulates 500ms latency
```

**Laws**:
- **Constancy**: `∀ a1, a2 ∈ A: MockAgent(b).invoke(a1) == MockAgent(b).invoke(a2)`
- **Identity Absorption**: `MockAgent(b) >> f ≠ f` (unless f is also constant)

---

### 1.2 FixtureAgent: The Lookup Morphism

**Category Theoretic Definition**: A morphism $f: A \to B$ defined by a lookup table (hash map).

**Signature**: `FixtureAgent[A, B](fixtures: Dict[A, B], default: Optional[B] = None) :: A → B`

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
```

**Implementation Skeleton**:
```python
class FixtureAgent(Generic[I, O]):
    """Deterministic map f: I → O using fixtures."""

    def __init__(self, fixtures: Dict[I, O], default: Optional[O] = None, strict: bool = True):
        self.name = "Fixture"
        self.fixtures = fixtures
        self.default = default
        self.strict = strict
        self.__is_test__ = True

    async def invoke(self, input_data: I) -> O:
        """Lookup input in fixture table."""
        if input_data in self.fixtures:
            return self.fixtures[input_data]

        if self.default is not None:
            return self.default

        if self.strict:
            raise KeyError(f"No fixture for input: {input_data}")

        raise RuntimeError("FixtureAgent: No default and strict=True")
```

**Use Cases**:
```python
# Regression test fixtures
fixtures = {
    "Fix auth bug": "Added OAuth validation",
    "Optimize query": "Added database index",
}
fixture_agent = FixtureAgent(fixtures)

# Ensure consistency across refactors
result = await fixture_agent.invoke("Fix auth bug")
assert result == "Added OAuth validation"  # Must never change
```

---

## Type II: The Saboteurs

Saboteurs inject controlled chaos to test system resilience.

### 2.1 FailingAgent: The Bottom Morphism

**Category Theoretic Definition**: The morphism $\bot: A \to \emptyset$ that never successfully returns.

**Signature**: `FailingAgent[A, E](config: FailingConfig) :: A → Error`

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

class FailureType(Enum):
    SYNTAX = "syntax_error"
    TYPE = "type_error"
    IMPORT = "import_error"
    RUNTIME = "runtime_error"
    TIMEOUT = "timeout_error"
    NETWORK = "network_error"
    HALLUCINATION = "hallucination"
```

**Implementation Skeleton**:
```python
class FailingAgent(Generic[I, O]):
    """The Bottom Morphism ⊥."""

    def __init__(self, config: FailingConfig):
        self.name = f"FailingAgent({config.error_type.value})"
        self.config = config
        self._current_fails = 0
        self.__is_test__ = True

    async def invoke(self, input_data: I) -> O:
        """Fail according to configuration."""
        # Check if still in failing phase
        if self.config.fail_count == -1 or self._current_fails < self.config.fail_count:
            self._current_fails += 1
            self._raise_error()

        # Recovery phase
        if self.config.recovery_token is not None:
            return self.config.recovery_token

        # Act as identity on recovery
        return input_data

    def _raise_error(self):
        """Raise the configured error type."""
        error_map = {
            FailureType.SYNTAX: SyntaxError,
            FailureType.TYPE: TypeError,
            FailureType.IMPORT: ImportError,
            FailureType.RUNTIME: RuntimeError,
            FailureType.TIMEOUT: TimeoutError,
            FailureType.NETWORK: ConnectionError,
        }
        error_class = error_map.get(self.config.error_type, Exception)
        raise error_class(self.config.error_message)

    def reset(self):
        """Reset failure count for test isolation."""
        self._current_fails = 0
```

**Use Cases**:
```python
# Test retry logic
failing = FailingAgent(FailingConfig(
    error_type=FailureType.NETWORK,
    fail_count=2,
    recovery_token="Success"
))

# Should fail twice, then succeed
for i in range(3):
    try:
        result = await failing.invoke("test")
        assert i == 2, "Should only succeed on 3rd attempt"
    except ConnectionError:
        assert i < 2, "Should only fail first 2 attempts"
```

---

### 2.2 NoiseAgent: Identity with Perturbation

**Category Theoretic Definition**: The morphism $N_\epsilon: A \to A$ where $N_\epsilon(a) = a + \epsilon$ for small perturbation $\epsilon$.

**Signature**: `NoiseAgent[A](level: float, seed: int = None) :: A → A + ε`

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

class NoiseType(Enum):
    CASE = "case_change"            # Change capitalization
    WHITESPACE = "whitespace"       # Add/remove spaces
    TYPOS = "typos"                 # Swap adjacent characters
    SYNONYMS = "synonyms"           # Replace with synonyms
    PUNCTUATION = "punctuation"     # Add/remove punctuation
```

**Implementation Skeleton**:
```python
class NoiseAgent(Generic[A]):
    """Identity with semantic noise N_ε."""

    def __init__(self, level: float = 0.1, seed: Optional[int] = None):
        self.name = f"Noise(ε={level})"
        self.level = level
        self.rng = random.Random(seed)
        self.__is_test__ = True

    async def invoke(self, input_data: A) -> A:
        """Add noise to input while preserving semantics."""
        if isinstance(input_data, str):
            return self._perturb_string(input_data)
        # Add other type handlers as needed
        return input_data

    def _perturb_string(self, s: str) -> str:
        """Apply string perturbations."""
        if self.rng.random() > self.level:
            return s  # No noise this time

        operations = [
            self._change_case,
            self._add_whitespace,
            self._introduce_typo,
        ]
        operation = self.rng.choice(operations)
        return operation(s)

    def _change_case(self, s: str) -> str:
        """Randomly change case."""
        return s.upper() if self.rng.random() > 0.5 else s.lower()

    def _add_whitespace(self, s: str) -> str:
        """Add extra spaces."""
        words = s.split()
        return "  ".join(words)

    def _introduce_typo(self, s: str) -> str:
        """Swap adjacent characters."""
        if len(s) < 2:
            return s
        idx = self.rng.randint(0, len(s) - 2)
        chars = list(s)
        chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]
        return "".join(chars)
```

**Use Cases**:
```python
# Test semantic robustness
noise = NoiseAgent(level=0.3, seed=42)
agent = SemanticAgent()

original = "Fix the authentication bug"
perturbed = await noise.invoke(original)  # Might be "Fix  the  Authentication  Bug"

# Agent should handle both inputs similarly
result_original = await agent.invoke(original)
result_perturbed = await agent.invoke(perturbed)

assert semantic_similarity(result_original, result_perturbed) > 0.9
```

---

### 2.3 LatencyAgent: Identity with Temporal Cost

**Category Theoretic Definition**: The morphism $L_\Delta: (A, t) \to (A, t + \Delta)$ adding temporal delay.

**Signature**: `LatencyAgent[A](delay: float, variance: float = 0.0) :: (A, t) → (A, t + Δ)`

**Implementation Skeleton**:
```python
class LatencyAgent(Generic[A]):
    """Identity with temporal cost."""

    def __init__(self, delay: float, variance: float = 0.0, seed: Optional[int] = None):
        self.name = f"Latency(Δ={delay}s)"
        self.delay = delay
        self.variance = variance
        self.rng = random.Random(seed)
        self.__is_test__ = True

    async def invoke(self, input_data: A) -> A:
        """Add latency, then return input unchanged."""
        actual_delay = self.delay
        if self.variance > 0:
            actual_delay += self.rng.uniform(-self.variance, self.variance)
        actual_delay = max(0, actual_delay)  # Never negative

        await asyncio.sleep(actual_delay)
        return input_data
```

---

### 2.4 FlakyAgent: Probabilistic Failure

**Category Theoretic Definition**: The morphism $F_p: A \to B \cup \{\bot\}$ that fails with probability $p$.

**Implementation Skeleton**:
```python
class FlakyAgent(Generic[I, O]):
    """Probabilistic chaos agent."""

    def __init__(self, wrapped: Agent[I, O], probability: float = 0.1, seed: Optional[int] = None):
        self.name = f"Flaky({wrapped.name}, p={probability})"
        self.wrapped = wrapped
        self.probability = probability
        self.rng = random.Random(seed)
        self.__is_test__ = True

    async def invoke(self, input_data: I) -> O:
        """Randomly fail or delegate to wrapped agent."""
        if self.rng.random() < self.probability:
            raise RuntimeError(f"Flaky failure (p={self.probability})")

        return await self.wrapped.invoke(input_data)
```

---

## Type III: The Observers

Observers are identity morphisms with side effects for inspection and validation.

### 3.1 SpyAgent: The Writer Monad

**Category Theoretic Definition**: The identity morphism with logging: $S: A \to (A, [A])$.

**Signature**: `SpyAgent[A](label: str) :: A → A` (with side effect: append to history)

**Implementation Skeleton**:
```python
class SpyAgent(Generic[A]):
    """Identity morphism with side effects (Writer Monad)."""

    def __init__(self, label: str):
        self.name = f"Spy({label})"
        self.label = label
        self.history: List[A] = []
        self.__is_test__ = True

    async def invoke(self, input_data: A) -> A:
        """Record input and pass through."""
        print(f"[{self.name}] Capturing: {input_data}")
        self.history.append(input_data)
        return input_data

    def reset(self):
        """Clear history for test isolation."""
        self.history.clear()

    def assert_captured(self, expected: A):
        """Assertion helper."""
        assert expected in self.history, f"Expected {expected} not captured"

    def assert_count(self, count: int):
        """Assert invocation count."""
        assert len(self.history) == count, f"Expected {count} invocations, got {len(self.history)}"
```

**Use Cases**:
```python
# Spy on intermediate pipeline data
spy = SpyAgent(label="Hypotheses")
pipeline = GenerateHypotheses() >> spy >> RunExperiments()

await pipeline.invoke(input_data)

# Inspect what was passed
print(spy.history)  # [HypothesisOutput(...)]
spy.assert_count(1)
```

---

### 3.2 PredicateAgent: The Gate Morphism

**Category Theoretic Definition**: $P: A \to A \cup \{\bot\}$ where output succeeds iff $P(a) = \text{True}$.

**Implementation Skeleton**:
```python
class PredicateAgent(Generic[A]):
    """Gate: passes input iff predicate holds."""

    def __init__(self, predicate: Callable[[A], bool], name: str = "Predicate"):
        self.name = f"Gate({name})"
        self.predicate = predicate
        self.__is_test__ = True

    async def invoke(self, input_data: A) -> A:
        """Pass through if predicate holds, else raise."""
        if not self.predicate(input_data):
            raise ValueError(f"Predicate failed for: {input_data}")
        return input_data
```

**Use Cases**:
```python
# Runtime type validation
def is_valid_hypothesis(h: HypothesisOutput) -> bool:
    return len(h.hypotheses) > 0

validator = PredicateAgent(is_valid_hypothesis, name="NonEmptyHypotheses")

# Will raise if hypotheses list is empty
pipeline = GenerateHypotheses() >> validator >> RunExperiments()
```

---

### 3.3 CounterAgent: Invocation Tracker

**Implementation Skeleton**:
```python
class CounterAgent(Generic[A]):
    """Identity with invocation counting."""

    def __init__(self, label: str):
        self.name = f"Counter({label})"
        self.count = 0
        self.__is_test__ = True

    async def invoke(self, input_data: A) -> A:
        """Increment counter and pass through."""
        self.count += 1
        return input_data

    def reset(self):
        """Reset counter."""
        self.count = 0

    def assert_count(self, expected: int):
        """Assert exact invocation count."""
        assert self.count == expected, f"Expected {expected} invocations, got {self.count}"
```

---

### 3.4 MetricsAgent: Performance Profiler

**Implementation Skeleton**:
```python
@dataclass
class PerformanceMetrics:
    invocation_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0

    @property
    def avg_time(self) -> float:
        return self.total_time / self.invocation_count if self.invocation_count > 0 else 0.0

class MetricsAgent(Generic[A]):
    """Identity with performance metrics."""

    def __init__(self, label: str):
        self.name = f"Metrics({label})"
        self.metrics = PerformanceMetrics()
        self.__is_test__ = True

    async def invoke(self, input_data: A) -> A:
        """Record timing and pass through."""
        start = time.time()
        result = input_data  # Identity
        elapsed = time.time() - start

        self.metrics.invocation_count += 1
        self.metrics.total_time += elapsed
        self.metrics.min_time = min(self.metrics.min_time, elapsed)
        self.metrics.max_time = max(self.metrics.max_time, elapsed)

        return result
```

---

## Type IV: The Critics

Critics use LLMs to evaluate semantic correctness, safety, and alignment.

### 4.1 JudgeAgent: LLM-as-Judge

**Signature**: `JudgeAgent[(Intent, Output), Score] :: (A, B) → [0, 1]`

**Implementation Sketch**:
```python
@dataclass
class JudgmentCriteria:
    correctness: float = 1.0   # Weight for correctness
    safety: float = 1.0        # Weight for safety
    style: float = 0.5         # Weight for style

class JudgeAgent:
    """LLM evaluates semantic correctness."""

    def __init__(self, criteria: JudgmentCriteria, llm: LLM):
        self.name = "Judge"
        self.criteria = criteria
        self.llm = llm
        self.__is_test__ = True

    async def invoke(self, interaction: Tuple[Intent, Output]) -> float:
        """Evaluate input/output pair."""
        intent, output = interaction

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
        total = (
            scores["correctness"] * self.criteria.correctness +
            scores["safety"] * self.criteria.safety +
            scores["style"] * self.criteria.style
        )
        weight_sum = self.criteria.correctness + self.criteria.safety + self.criteria.style

        return total / weight_sum
```

---

## Summary Table

| Type | T-gent | Morphism | Purpose |
|------|--------|----------|---------|
| **I** | MockAgent | $A \to b$ | Constant output |
| **I** | FixtureAgent | $A \to B$ | Deterministic lookup |
| **II** | FailingAgent | $A \to \bot$ | Controlled failure |
| **II** | NoiseAgent | $A \to A + \epsilon$ | Semantic noise |
| **II** | LatencyAgent | $(A, t) \to (A, t + \Delta)$ | Temporal delay |
| **II** | FlakyAgent | $A \to B \cup \{\bot\}$ | Probabilistic failure |
| **III** | SpyAgent | $A \to A$ | Logging side effect |
| **III** | PredicateAgent | $A \to A \cup \{\bot\}$ | Runtime validation |
| **III** | CounterAgent | $A \to A$ | Invocation tracking |
| **III** | MetricsAgent | $A \to A$ | Performance profiling |
| **IV** | JudgeAgent | $(A, B) \to [0,1]$ | Semantic evaluation |

---

## See Also

- [README.md](README.md) - T-gents overview
- [algebra.md](algebra.md) - Category Theory foundations
- [adversarial.md](adversarial.md) - Chaos engineering
