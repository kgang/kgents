# T-gents: The Algebra of Reliability

The letter **T** represents **Testing** agents—morphisms designed to verify, perturb, observe, and judge the behavior of other agents through rigorous Category Theory principles.

> **Note**: Tool Use has been migrated to **U-gents** (Utility agents). See [U-gents](../u-gents/) for the Tool Use framework.

---

## Philosophy

> "Testing is not the absence of bugs, but the presence of proofs."

T-gents treat testing as **algebraic verification**. Rather than ad-hoc test cases, T-gents prove that agent pipelines satisfy categorical laws: associativity, identity, and resilience under perturbation.

### The Dual Mandate

T-gents serve two roles:

1. **Subjects of Verification**: T-gents handle failure modes (`Nothing`, `Left`, `Error`) to test recovery strategies
2. **Operators of Verification**: T-gents act as observers and validators of other agents' behavior

This duality mirrors Category Theory: agents are both **objects** (test subjects) and **morphisms** (test operators).

---

## Core Concepts

### Agents as Morphisms in $\mathcal{C}_{Agent}$

Testing in kgents is grounded in Category Theory:

**Objects**: Types/Schemas (Input $A$, Output $B$)
**Morphisms**: Agents transforming $A \to B$
**Composition**: The pipeline operator `>>`
**T-gents**: Special morphisms that validate categorical properties

### The Three Laws of Testability

#### 1. Associativity
```
(f >> g) >> h ≡ f >> (g >> h)
```
Pipeline composition order doesn't matter—T-gents verify this algebraically.

#### 2. Identity
```
f >> Identity ≡ f ≡ Identity >> f
```
Identity agents leave data unchanged—T-gents prove this invariant.

#### 3. Resilience
```
f: A → B  implies  f(a + ε) ≈ f(a)  for small ε
```
Semantic stability under noise—T-gents inject perturbations to verify.

---

## The Taxonomy of T-gents

T-gents are categorized by their effect on the computational stream into **five types**.

| Type | Name | Purpose |
|------|------|---------|
| I | Nullifiers | MockAgent, FixtureAgent (constant/lookup morphisms) |
| II | Saboteurs | FailingAgent, NoiseAgent (perturbation & chaos) |
| III | Observers | SpyAgent, PredicateAgent (identity with side effects) |
| IV | Critics | JudgeAgent, PropertyAgent (LLM evaluators) |
| V | Adversarial | AdversarialGym, StressCoordinate (chaos engineering) |

### Type I: The Nullifiers (Stubs & Mocks)
*Replace computation with constants or lookups.*

| T-gent | Signature | Purpose |
|--------|-----------|---------|
| **MockAgent** | `A → b` | Constant morphism; always returns fixed `b ∈ B` |
| **FixtureAgent** | `A → B` | Deterministic map using fixture data; regression testing |

**Use Cases**:
- Fast testing without LLM calls
- Validating pipeline composition logic
- Performance benchmarking
- Deterministic CI/CD validation

### Type II: The Saboteurs (Perturbation & Chaos)
*Inject entropy to verify system stability.*

| T-gent | Signature | Purpose |
|--------|-----------|---------|
| **FailingAgent** | `A → Error` | Bottom morphism; maps input to exception |
| **NoiseAgent** | `A → A + ε` | Identity with semantic noise (case, typos, synonyms) |
| **LatencyAgent** | `(A, t) → (A, t + Δ)` | Identity with temporal cost |
| **FlakyAgent** | `A → B \| Error` | Probabilistic failure; chaos engineering |

**Use Cases**:
- Testing retry logic and exponential backoff
- Validating fallback strategies
- Chaos engineering for production resilience
- Timeout and circuit breaker validation

### Type III: The Observers (Spies & Validators)
*Identity morphisms with side effects.*

| T-gent | Signature | Purpose |
|--------|-----------|---------|
| **SpyAgent** | `A → A` | Identity; logs input to tape for inspection |
| **PredicateAgent** | `A → A \| Error` | Gate; passes `a` iff `P(a) = True` |
| **CounterAgent** | `A → A` | Identity; tracks invocation count |
| **MetricsAgent** | `A → A` | Identity; records latency/throughput |

**Use Cases**:
- Runtime type checking and invariant validation
- Performance profiling
- Debugging pipeline data flow
- Assertion-based testing

### Type IV: The Critics (LLM Evaluators)
*High-order agents mapping interactions to judgments.*

| T-gent | Signature | Purpose |
|--------|-----------|---------|
| **JudgeAgent** | `(A, B) → Score` | Semantic evaluation of input/output pairs |
| **CorrectnessAgent** | `(Intent, Code) → Bool` | Validates implementation vs. specification |
| **SafetyAgent** | `Code → Risk` | Evaluates generated code for vulnerabilities |

**Use Cases**:
- LLM-as-judge evaluation
- Semantic correctness beyond syntax
- Ethical and safety validation
- User intent alignment testing

### Type V: The Adversarial (Chaos Engineering)
*Automated stress testing through compositional chaos.*

| T-gent | Signature | Purpose |
|--------|-----------|---------|
| **AdversarialGym** | `Agent → GymReport` | Monte Carlo stress testing via T-gent composition |
| **StressCoordinate** | `(noise, failure, latency, drift)` | Point in stress-test space |
| **MultiDimensionalGym** | `Agent → Dict[Coord, Report]` | Grid search across stress dimensions |

**Use Cases**:
- Discover unknown failure modes before production
- Regression testing: verify resilience after refactors
- Property discovery: empirically find algebraic properties
- Evolution fitness: Gym as fitness function for E-gents

**The Gym Principle**: Testing is not validation—it's discovery. The Adversarial Gym discovers what breaks agents before production does.

See [adversarial.md](adversarial.md) for full specification.

---

## Compositional Testing: The Commutative Diagram

T-gents enable **algebraic testing** through commutative diagram verification.

### Example: Testing Retry Logic

**Hypothesis**: A retry wrapper should make a flaky pipeline equivalent to a reliable one.

```
          FailingAgent(fail_count=2)
Input  ─────────────────────────────────> Error
  │                                         ↑
  │                                         │
  └───> RetryWrapper(max=3) >> FailingAgent ──> Success
```

**Test**:
```python
# The flaky agent fails twice, then succeeds
saboteur = FailingAgent(FailingConfig(
    failure_type="network",
    fail_count=2,
    recovery_token="Success"
))

# The robust pipeline retries 3 times
robust = RetryWrapper(max_retries=3) >> saboteur

# Commutative property: robust pipeline ≡ identity after recovery
payload = "Test Input"
result = await robust.invoke(payload)

assert result == "Success"  # Diagram commutes
```

### Example: Testing Associativity

**Hypothesis**: Pipeline composition is associative.

```python
mock_a = MockAgent(output="A")
spy_b = SpyAgent(label="B")
spy_c = SpyAgent(label="C")

# Two ways to compose
pipeline_1 = (mock_a >> spy_b) >> spy_c
pipeline_2 = mock_a >> (spy_b >> spy_c)

# Associativity law
result_1 = await pipeline_1.invoke(None)
result_2 = await pipeline_2.invoke(None)

assert result_1 == result_2  # Law verified
assert spy_b.history == spy_c.history  # Side effects equivalent
```

---

## The Adversarial Gym

The ultimate vision for T-gents: **automated stress testing** through composition.

### Concept

A `GymAgent` automatically composes production agents with random T-gents to discover edge cases.

```python
class AdversarialGym:
    """Monte Carlo testing through T-gent composition."""

    def stress_test(self, production_agent: Agent[A, B], iterations: int = 100):
        # Inject random perturbations
        tests = [
            NoiseAgent(level=random.uniform(0, 1)) >> production_agent,
            production_agent >> FailingAgent(probability=0.1),
            LatencyAgent(delay=random.randint(0, 1000)) >> production_agent,
        ]

        for _ in range(iterations):
            test_pipeline = random.choice(tests)
            try:
                result = await test_pipeline.invoke(random_input())
                # Record success metrics
            except Exception as e:
                # Record failure modes
                pass
```

**Goal**: Discover failure modes before production does.

---

## Implementation Principles

### 1. Transparency
T-gents must be distinguishable from production agents:
```python
class Agent(Protocol):
    name: str
    __is_test__: bool = False  # T-gents set to True
```

### 2. Determinism
Even `FailingAgent` must fail deterministically based on config/seed.
```python
FailingAgent(seed=42)  # Reproducible failures
```

### 3. Minimal Footprint
T-gents avoid heavy dependencies unless testing specific integrations.

### 4. Isomorphism
A `SpyAgent` must be **mathematically equivalent** to `Identity` for data flow:
```python
assert (spy >> f).invoke(x) == f.invoke(x)  # Spy is transparent
```

---

## Success Criteria

A T-gent is well-designed if:

- ✓ It reveals bugs that would otherwise be hidden
- ✓ It fails faster than production would
- ✓ It composes naturally with other agents via `>>`
- ✓ It provides clear diagnostic information
- ✓ It enables confident refactoring
- ✓ It proves algebraic properties, not just examples

---

## Relationship to Other Agent Genera

| Genus | Relationship |
|-------|-------------|
| **C-gents** | T-gents verify C-gents' composition laws |
| **E-gents** | T-gents test evolution pipelines for reliability |
| **J-gents** | T-gents validate Promise collapse and entropy budgets |
| **B-gents** | T-gents evaluate hypothesis quality |
| **K-gent** | T-gents ensure persona consistency |

T-gents are the **quality assurance layer** for all agent genera.

---

## Specifications

| Document | Description |
|----------|-------------|
| [algebra.md](algebra.md) | Category Theory foundations & laws |
| [taxonomy.md](taxonomy.md) | Detailed specifications for Types I-IV |
| [adversarial.md](adversarial.md) | Type V: Adversarial Gym & chaos engineering |

> **Looking for Tool Use?** See [U-gents](../u-gents/) for the Tool Use framework (Types I-VI).

---

## Anti-patterns

- **Non-Determinism**: Random failures without seed/config
- **Heavy Dependencies**: T-gents shouldn't require production libraries
- **Silent Failures**: Errors must be loud and informative
- **Non-Compositional**: T-gents that break pipeline semantics
- **False Positives**: Tests that fail on valid behavior

---

## Example: Full Pipeline Test

```python
async def test_evolution_pipeline():
    """Test the full evolution pipeline with T-gents."""

    # Setup: Mock hypothesis generation
    mock_hypotheses = MockAgent(output=HypothesisOutput(
        hypotheses=["Fix import error", "Add type hints"]
    ))

    # Setup: Spy on experiments
    experiment_spy = SpyAgent(label="Experiments")

    # Setup: Inject occasional failures
    flaky_executor = FlakyAgent(probability=0.1)

    # Compose: The tested pipeline
    pipeline = (
        mock_hypotheses >>
        experiment_spy >>
        flaky_executor >>
        ValidateOutput()
    )

    # Execute: Run with retry
    retry_wrapper = RetryWrapper(max_retries=3)
    robust_pipeline = retry_wrapper >> pipeline

    result = await robust_pipeline.invoke(test_input)

    # Verify: Algebraic properties
    assert len(experiment_spy.history) > 0  # Spy captured data
    assert result.is_success  # Pipeline recovered from flake

    print("✓ Pipeline resilience verified")
```

---

## See Also

- [algebra.md](algebra.md) - Mathematical foundations
- [taxonomy.md](taxonomy.md) - T-gent type specifications (Types I-IV)
- [adversarial.md](adversarial.md) - Type V: Chaos engineering
- [../u-gents/](../u-gents/) - U-gents: Tool Use framework
- [../c-gents/](../c-gents/) - Category Theory basis
- [../j-gents/stability.md](../j-gents/stability.md) - Entropy & collapse
- [../bootstrap.md](../bootstrap.md) - The irreducible kernel

---

## Vision

T-gents transform testing from **example-based** to **proof-based**:

- Traditional: "This test case passes"
- T-gents: "This pipeline satisfies associativity for all inputs"

By grounding testing in Category Theory, T-gents enable **algebraic reliability**—the confidence that comes from mathematical proof, not just empirical observation.
