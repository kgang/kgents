# Testing Agents Specification

> Testing is not separate from agent design—test agents ARE agents.

---

## Philosophy

Testing agents satisfy all agent principles:
- **Composable**: `spy_agent >> production_agent >> assert_agent`
- **Morphisms**: `SpyAgent: A → A` (identity + side effect)
- **Categorical**: Laws hold for test agents too

**Key Insight**: Testing is usually external to runtime (CI/CD). T-gents move testing *into* the runtime.

---

## The T-gents Taxonomy

### Type I: Nullifiers (Constants & Fixtures)

Agents that replace expensive operations with known outputs.

| Agent | Signature | Purpose |
|-------|-----------|---------|
| `MockAgent` | `A → b` (constant) | Replace expensive operations |
| `FixtureAgent` | `key → value` (lookup) | Deterministic test data |
| `StubAgent` | `A → default` | Placeholder for unimplemented |

```python
# MockAgent: Always returns the same value
mock = MockAgent(output={"status": "success"})
result = await mock.invoke(anything)  # Always {"status": "success"}

# FixtureAgent: Deterministic lookup
fixture = FixtureAgent({"user_123": User(name="Test")})
user = await fixture.invoke("user_123")  # User(name="Test")
```

**Use Cases**:
- Replace external API calls in tests
- Provide known inputs for deterministic testing
- Isolate units from dependencies

---

### Type II: Saboteurs (Chaos & Perturbation)

Agents that inject failure, noise, and delay to test resilience.

| Agent | Signature | Purpose |
|-------|-----------|---------|
| `FailingAgent` | `A → Error` (controlled) | Test error handling |
| `NoiseAgent` | `A → perturb(A)` | Semantic perturbation |
| `LatencyAgent` | `A → A` (delayed) | Test timeout handling |
| `FlakyAgent` | `A → A | Error` (probabilistic) | Test retry logic |

```python
# FailingAgent: Controlled failures
failing = FailingAgent(
    error_type=ConnectionError,
    message="Simulated network failure"
)

# NoiseAgent: Semantic perturbation
noise = NoiseAgent(
    strategy="typo",       # Or: "synonym", "truncate", "corrupt"
    intensity=0.1          # 10% of content affected
)

# LatencyAgent: Temporal delays
latency = LatencyAgent(
    delay_ms=500,          # Fixed delay
    jitter_ms=100          # Random ± variation
)

# FlakyAgent: Probabilistic failures
flaky = FlakyAgent(
    failure_rate=0.1,      # 10% chance of failure
    success_after=3        # Succeed after 3 attempts
)
```

**Use Cases**:
- Test resilience to network failures
- Verify retry logic works correctly
- Ensure graceful degradation under load
- **Darwinian testing**: Only robust agents survive

**Connection to Accursed Share**: Type II Saboteurs ARE the Accursed Share in action—noise injection is gratitude for the generative chaos.

---

### Type III: Observers (Identity + Side Effects)

Agents that pass through unchanged while recording observations.

| Agent | Signature | Purpose |
|-------|-----------|---------|
| `SpyAgent` | `A → A` + observations | Writer monad pattern |
| `PredicateAgent` | `A → A | reject` | Gate/filter |
| `CounterAgent` | `A → A` + count | Invocation counting |
| `TimerAgent` | `A → A` + duration | Performance measurement |

```python
# SpyAgent: Observe without mutating
spy = SpyAgent()
result = await (spy >> production_agent).invoke(input)
print(spy.observations)  # All inputs that passed through

# PredicateAgent: Gate based on condition
gate = PredicateAgent(lambda x: x.confidence > 0.8)
result = await (producer >> gate >> consumer).invoke(start)
# Consumer only receives high-confidence outputs

# CounterAgent: Track invocation count
counter = CounterAgent()
for _ in range(10):
    await (counter >> agent).invoke(x)
print(counter.count)  # 10
```

**Use Cases**:
- Transparent observation without mutation
- Contract verification (ensure outputs meet criteria)
- Performance profiling in pipelines
- Debugging composition chains

---

### Type IV: Critics (Semantic Evaluation)

Agents that evaluate quality, correctness, and semantic properties.

| Agent | Signature | Purpose |
|-------|-----------|---------|
| `JudgeAgent` | `(A, B) → Verdict` | LLM-as-judge |
| `PropertyAgent` | `A → bool` | Property-based testing |
| `OracleAgent` | `(A, A) → Diff` | Differential testing |
| `CriteriaAgent` | `A → Score` | Multi-criteria evaluation |

```python
# JudgeAgent: LLM-based evaluation
judge = JudgeAgent(
    criteria=["factual_accuracy", "coherence", "safety"],
    model="claude-3-opus"
)
verdict = await judge.invoke((input, output))
# Verdict(accept=True, scores={"factual": 0.9, "coherence": 0.85, "safety": 1.0})

# PropertyAgent: Verify invariants
property = PropertyAgent(lambda x: len(x.code) < 1000)
for _ in range(100):
    input = generator.generate()
    output = await production_agent.invoke(input)
    assert await property.invoke(output)

# OracleAgent: Compare implementations
oracle = OracleAgent(reference_agent, tolerance=0.05)
diff = await oracle.invoke((input, candidate_output))
# Diff(match=True, delta=0.02)
```

**Use Cases**:
- Quality assurance for LLM outputs
- Regression detection via differential testing
- Property-based testing for semantic invariants
- Multi-stakeholder evaluation (safety, quality, style)

---

## Integration with Reliability Stack

### The Socratic Pattern (Type IV Critics)

Critics enable iterative refinement through questioning:

```python
# Pattern: Worker >> Judge
async def socratic_loop(worker, judge, input, max_rounds=3):
    for round in range(max_rounds):
        output = await worker.invoke(input)
        verdict = await judge.invoke((input, output))

        if verdict.accept:
            return output

        # Refine based on feedback
        input = RefineRequest(
            original=input,
            attempt=output,
            feedback=verdict.feedback
        )

    return output  # Best effort after max rounds
```

**The Teacher Who Only Asks**: The judge never produces—only evaluates and questions. The worker improves through dialogue.

*Zen Principle: The finger pointing at the moon is not the moon.*

---

### Chaos Testing (Type II Saboteurs)

Saboteurs reveal weakness before production does:

```python
# Attach chaos to test resilience
chaos_pipeline = (
    latency_agent >>     # Add delay
    noise_agent >>       # Perturb input
    production_agent >>  # System under test
    judge_agent          # Evaluate output quality
)

# If production survives perturbation with acceptable quality, it is robust
async def chaos_test(input, min_quality=0.7):
    verdict = await chaos_pipeline.invoke(input)
    return verdict.score >= min_quality
```

*Zen Principle: The sword is tempered by fire, not by rest.*

---

## Test Agent Marker

All test agents MUST declare:

```python
__is_test__ = True
```

This enables:
- Filtering in production vs test code
- Meta-reasoning about test coverage
- Automatic test discovery
- Safety checks (test agents should not be deployed to production)

---

## Composition Patterns

### Spy Pattern: Observe Without Mutating

```python
spied = spy_agent >> production_agent
result = await spied.invoke(input)
observations = spy_agent.observations
```

### Chaos Pattern: Test Resilience (Darwinian)

```python
chaos = latency_agent >> noise_agent >> production_agent
result = await chaos.invoke(input)  # May fail, may be noisy
```

### Socratic Pattern: Iterative Refinement

```python
socratic = worker >> judge_agent
while (result := await socratic.invoke(input)).needs_revision:
    input = result.suggested_refinement
```

### Property Pattern: Verify Invariants

```python
for _ in range(100):
    input = generator.generate()
    result = await production_agent.invoke(input)
    assert property.check(input, result)
```

### Oracle Pattern: Differential Testing

```python
reference_output = await reference_agent.invoke(input)
candidate_output = await candidate_agent.invoke(input)
diff = await oracle.invoke((reference_output, candidate_output))
assert diff.is_acceptable()
```

---

## Anti-Patterns

- **Testing only in CI**: Tests should run in runtime too
- **Ignoring composition laws for test agents**: Test agents are still agents
- **Non-deterministic mocks**: MockAgent output should be predictable
- **Testing without chaos**: Happy paths don't reveal fragility
- **Judges without criteria**: Evaluation needs explicit standards

---

## See Also

- [t-gents/taxonomy.md](t-gents/taxonomy.md) - Detailed agent specifications
- [t-gents/algebra.md](t-gents/algebra.md) - Algebraic properties of test agents
- [reliability.md](reliability.md) - Multi-layer reliability patterns
- [bootstrap.md](bootstrap.md) - Judge as bootstrap agent
