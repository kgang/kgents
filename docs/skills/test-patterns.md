---
path: docs/skills/test-patterns
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Skill: Testing Patterns and Conventions

> Write comprehensive agent tests using T-gent Types I-V taxonomy and testing infrastructure.

**Difficulty**: Easy-Medium
**Prerequisites**: pytest basics, Python async/await
**Files Touched**: `*/_tests/test_*.py`, `impl/claude/testing/`
**References**: `agents/t/`, `testing/__init__.py`

---

## Overview

kgents uses a five-level test taxonomy (T-gent Types I-V) that progresses from contract verification to metamorphic testing. The `testing/` package provides infrastructure for each level.

Tests are the **executable specification**—they define agent behavior more precisely than prose.

### T-gent Types I-V Taxonomy

| Type | Name | Purpose | Tools |
|------|------|---------|-------|
| I | **Contracts** | Preconditions, postconditions, invariants | `pytest`, `PredicateAgent` |
| II | **Saboteurs** | Property-based testing, fuzzing | `Hypothesis`, `NoiseAgent` |
| III | **Spies** | Behavior verification, call tracking | `SpyAgent`, `CounterAgent` |
| IV | **Judges** | Semantic assertions, LLM validation | `Oracle`, `JudgeAgent` |
| V | **Witnesses** | Integration tests, round-trip verification | `Topologist`, `Cortex` |

### Conventions

- **Test directory**: `_tests/` folders next to source files
- **Test naming**: `test_<feature>.py` files, `Test<Class>` classes, `test_<behavior>` methods
- **Async tests**: `@pytest.mark.asyncio` decorator
- **Fixtures**: Centralized in `conftest.py`, module-local for specifics
- **Type-safe mocks**: Use `testing.as_umwelt()` and `testing.as_agent()`
- **Custom markers**: `@pytest.mark.law`, `@pytest.mark.slow`, `@pytest.mark.property`

---

## T-gent Test Agents

The `agents/t/` package provides composable test agents:

| Agent | Purpose | Key Methods |
|-------|---------|-------------|
| `MockAgent` | Constant output | `call_count` |
| `FixtureAgent` | Deterministic lookup | `lookup_count` |
| `FailingAgent` | Controlled failures | `reset()` |
| `SpyAgent` | Identity + observation | `assert_captured()`, `history` |
| `PredicateAgent` | Validation gate | `pass_count`, `fail_count` |
| `NoiseAgent` | Semantic perturbation | `level`, `seed` |
| `LatencyAgent` | Temporal delay | `delay`, `variance` |
| `FlakyAgent` | Probabilistic failure | `probability` |
| `CounterAgent` | Call counting | `count`, `assert_count()` |
| `MetricsAgent` | Timing metrics | `metrics.avg_time` |

### Usage Examples

```python
from agents.t import (
    MockAgent, MockConfig,
    SpyAgent, CounterAgent, MetricsAgent,
    NoiseAgent, LatencyAgent, FlakyAgent,
    PredicateAgent, not_empty,
)

# MockAgent: constant morphism
mock = MockAgent[str, dict](MockConfig(output={"status": "ok"}))
result = await mock.invoke("anything")  # Always {"status": "ok"}
assert mock.call_count == 1

# SpyAgent: identity + observation
spy = SpyAgent[str](label="Pipeline")
await pipeline_with_spy.invoke("input1")
spy.assert_captured("input1")
spy.assert_count(1)

# PredicateAgent: validation gate
validator = PredicateAgent[str](not_empty, name="NonEmpty")
await validator.invoke("hello")  # Passes
# await validator.invoke("")     # Raises ValueError

# NoiseAgent: semantic perturbation (for fuzzing)
noise = NoiseAgent[str](level=0.5, seed=42)
perturbed = await noise.invoke("Fix the bug")  # → "Fix te bug"

# CounterAgent: track invocations
counter = CounterAgent[str](label="Calls")
await counter.invoke("a")
await counter.invoke("b")
counter.assert_count(2)

# MetricsAgent: timing
metrics = MetricsAgent[str](label="Perf")
await metrics.invoke("test")
print(f"Avg time: {metrics.metrics.avg_time:.6f}s")
```

### Composition in Tests

```python
# Pipeline: Counter >> Spy >> Agent Under Test
counter = CounterAgent[str](label="Calls")
spy = SpyAgent[str](label="Inputs")
agent = MyAgent()

pipeline = counter >> spy >> agent

await pipeline.invoke("test")

counter.assert_count(1)
spy.assert_captured("test")
```

---

## Step-by-Step: Basic Test File

### Step 1: Create Test File

**Location**: `impl/claude/<module>/_tests/test_<feature>.py`

**Template**:
```python
"""
Tests for <feature>.

Tests verify:
1. <what is being tested>
2. <another behavior>
3. <edge cases>
"""

from __future__ import annotations

import pytest


class TestFeatureBehavior:
    """Tests for <specific behavior>."""

    def test_basic_case(self) -> None:
        """<What this test verifies>."""
        # Arrange
        thing = MyClass()

        # Act
        result = thing.do_something()

        # Assert
        assert result == expected

    def test_edge_case(self) -> None:
        """<Edge case description>."""
        # Arrange
        thing = MyClass()

        # Act / Assert
        with pytest.raises(ValueError):
            thing.do_invalid()
```

### Step 2: Import from Sibling Module

Use relative imports for the module under test:

```python
# Relative import from parent
from ..my_module import MyClass, my_function

# Or absolute import
from protocols.agentese.contexts.world import WorldNode
```

---

## Step-by-Step: Async Tests

### Step 1: Mark Test as Async

```python
import pytest

class TestAsyncBehavior:
    """Tests for async methods."""

    @pytest.mark.asyncio
    async def test_async_method(self) -> None:
        """Test async invocation."""
        agent = MyAgent()

        result = await agent.invoke("input")

        assert result == "expected"
```

### Step 2: Async Fixtures

```python
@pytest.fixture
async def initialized_store() -> Store:
    """Create and initialize a store."""
    store = Store()
    await store.initialize()
    yield store
    await store.cleanup()  # Cleanup after test
```

---

## Step-by-Step: Using Mock Fixtures

### Step 1: Create MockUmwelt (Common Pattern)

```python
from typing import Any

class MockDNA:
    """Mock DNA for testing."""

    def __init__(
        self,
        name: str = "test",
        archetype: str = "default",
        capabilities: tuple[str, ...] = (),
    ) -> None:
        self.name = name
        self.archetype = archetype
        self.capabilities = capabilities


class MockUmwelt:
    """Mock Umwelt for testing."""

    def __init__(
        self,
        archetype: str = "default",
        name: str = "test",
        capabilities: tuple[str, ...] = (),
    ) -> None:
        self.dna = MockDNA(name=name, archetype=archetype, capabilities=capabilities)
        self.gravity: tuple[Any, ...] = ()
        self.context: dict[str, Any] = {}
```

### Step 2: Use Type-Safe Cast Helper

The `testing` module provides `as_umwelt()` for type-safe casting:

```python
from testing import as_umwelt
from typing import Any
from bootstrap.umwelt import Umwelt

@pytest.fixture
def observer() -> Umwelt[Any, Any]:
    """Default observer fixture."""
    return as_umwelt(MockUmwelt())

@pytest.fixture
def admin_observer() -> Umwelt[Any, Any]:
    """Admin observer fixture."""
    return as_umwelt(MockUmwelt(archetype="admin"))
```

This avoids mypy errors when passing mock objects to functions expecting `Umwelt[A, B]`.

### Step 3: Use in Tests

```python
@pytest.mark.asyncio
async def test_manifest(observer: Umwelt[Any, Any]) -> None:
    """Test manifest for default observer."""
    node = MyNode()

    result = await node.manifest(observer)

    assert result.summary == "Expected"
```

---

## Step-by-Step: Global Fixtures (conftest.py)

### Step 1: Understand Fixture Hierarchy

```
impl/claude/conftest.py         # Root fixtures (used by 3+ files)
impl/claude/agents/conftest.py  # Agent-specific fixtures
impl/claude/protocols/agentese/_tests/conftest.py  # Module fixtures
```

### Step 2: Available Testing Utilities

From `impl/claude/testing/__init__.py`:

| Utility | Type | Description |
|---------|------|-------------|
| `as_umwelt(obj)` | `Umwelt[Any, Any]` | Type-safe cast for mock Umwelts |
| `as_agent(obj)` | `Agent[A, B]` | Type-safe cast for mock Agents |
| `simple_agents()` | Hypothesis strategy | Generates deterministic test agents |
| `agent_chains(min, max)` | Hypothesis strategy | Lists of composable agents |
| `valid_dna()` | Hypothesis strategy | Valid DNA configurations |
| `invalid_dna()` | Hypothesis strategy | Invalid DNA for constraint testing |
| `type_names()` | Hypothesis strategy | Valid type name strings |

**Note**: Root conftest.py focuses on test infrastructure (flinch logging, markers).
Module-specific fixtures should be defined in local `_tests/conftest.py` files.

### Step 3: Create Local Fixtures

For module-specific fixtures, add to `_tests/conftest.py`:

```python
# impl/claude/agents/myagent/_tests/conftest.py
import pytest
from ..agent import MyAgent

@pytest.fixture
def my_agent() -> MyAgent:
    """Pre-configured MyAgent for tests."""
    return MyAgent(config=MyConfig())
```

---

## Step-by-Step: Custom Markers

### Step 1: Available Markers

| Marker | Purpose |
|--------|---------|
| `@pytest.mark.law(name)` | Category law verification |
| `@pytest.mark.law_identity` | Identity law: `Id >> f == f` |
| `@pytest.mark.law_associativity` | `(f >> g) >> h == f >> (g >> h)` |
| `@pytest.mark.law_functor_identity` | `fmap id == id` |
| `@pytest.mark.law_functor_composition` | `fmap (g.f) == fmap g . fmap f` |
| `@pytest.mark.slow` | Slow-running test |
| `@pytest.mark.property` | Property-based test |
| `@pytest.mark.accursed_share` | Exploratory/chaos test |

### Step 2: Use Markers

```python
import pytest

@pytest.mark.law_identity
@pytest.mark.asyncio
async def test_identity_law() -> None:
    """Verify identity law: Id >> f == f == f >> Id."""
    from bootstrap import compose
    from conftest import IdentityAgent

    id_agent = IdentityAgent()
    f = DoubleAgent()

    input_val = 5
    result1 = await compose(id_agent, f).invoke(input_val)
    result2 = await f.invoke(input_val)
    result3 = await compose(f, id_agent).invoke(input_val)

    assert result1 == result2 == result3


@pytest.mark.slow
def test_large_data_processing() -> None:
    """Test with large dataset (takes >5s)."""
    ...
```

### Step 3: Run Specific Markers

```bash
# Run only law tests
uv run pytest -m "law"

# Exclude slow tests
uv run pytest -m "not slow"

# Run property-based tests
uv run pytest -m "property"
```

---

## Step-by-Step: Property-Based Testing (Hypothesis)

### Step 1: Import Strategies

```python
from hypothesis import given, settings
from testing import simple_agents, agent_chains, valid_dna
```

### Step 2: Write Property Test

```python
from hypothesis import given, settings
from testing import simple_agents

@pytest.mark.property
@given(agent=simple_agents())
@settings(max_examples=50)
@pytest.mark.asyncio
async def test_agent_composition_associativity(agent) -> None:
    """Composition is associative for all generated agents."""
    from conftest import IdentityAgent

    id_agent = IdentityAgent()

    # (id >> agent) == agent
    composed = await compose(id_agent, agent).invoke(10)
    direct = await agent.invoke(10)

    assert composed == direct
```

### Step 3: Available Strategies

From `testing.strategies`:

| Strategy | Description |
|----------|-------------|
| `simple_agents()` | Deterministic agents with offset |
| `agent_chains(min_length, max_length)` | Lists of composable agents |
| `valid_dna()` | Valid DNA configurations |
| `invalid_dna()` | Invalid DNA for constraint testing |
| `type_names()` | Valid type name strings |
| `json_like_values()` | JSON-compatible values |
| `boundary_inputs()` | Edge case inputs |

---

## Step-by-Step: Mock Agent Pattern

### Step 1: Minimal Mock

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class EchoAgent:
    """Returns input with prefix."""
    name: str = "Echo"

    async def invoke(self, input: Any) -> str:
        return f"Echo: {input}"
```

### Step 2: Composable Mock

```python
from dataclasses import dataclass
from typing import Any, cast
from bootstrap.types import Agent

@dataclass
class DoubleAgent:
    """Doubles numeric input."""
    name: str = "Double"

    async def invoke(self, input: int) -> int:
        return input * 2

    def __rshift__(self, other: Any) -> Any:
        from bootstrap import compose
        return compose(cast(Agent[Any, Any], self), other)
```

### Step 3: Configurable Mock

```python
@dataclass
class RecordingAgent:
    """Records all invocations for verification."""
    name: str = "Recorder"
    calls: list[Any] = field(default_factory=list)

    async def invoke(self, input: Any) -> Any:
        self.calls.append(input)
        return input

# In test:
def test_agent_called() -> None:
    recorder = RecordingAgent()
    await my_function(recorder)
    assert len(recorder.calls) == 3
```

---

## Verification

### Test 1: Run single test file

```bash
cd impl/claude
uv run pytest path/to/_tests/test_feature.py -v
```

### Test 2: Run with coverage

```bash
uv run pytest path/to/_tests/ --cov=path/to --cov-report=term-missing
```

### Test 3: Run specific test

```bash
uv run pytest path/to/_tests/test_feature.py::TestClass::test_method -v
```

### Test 4: Run all tests

```bash
cd impl/claude
uv run pytest
```

---

## Common Pitfalls

### 1. Missing `@pytest.mark.asyncio`

**Symptom**: `RuntimeWarning: coroutine 'test_foo' was never awaited`

**Fix**: Add the decorator:
```python
@pytest.mark.asyncio
async def test_async_method() -> None:
    ...
```

### 2. Forgetting to cast Umwelt mocks

**Symptom**: mypy errors about incompatible types

**Fix**: Use `as_umwelt()`:
```python
from testing import as_umwelt

observer = as_umwelt(MockUmwelt())
```

### 3. Not awaiting async fixture

**Symptom**: Test passes but doesn't actually test anything

**Fix**: Ensure async fixtures yield properly:
```python
@pytest.fixture
async def store() -> AsyncIterator[Store]:
    store = Store()
    await store.initialize()
    yield store
    await store.cleanup()
```

### 4. Import path issues

**Symptom**: `ModuleNotFoundError`

**Fix**: Run tests from `impl/claude/` directory:
```bash
cd impl/claude
uv run pytest
```

### 5. Test isolation failures

**Symptom**: Tests pass individually but fail together

**Fix**: Don't share mutable state between tests. Use fixtures with `function` scope (default):
```python
@pytest.fixture
def fresh_store() -> Store:
    return Store()  # New instance per test
```

### 6. Flaky async tests

**Symptom**: Test intermittently fails

**Fix**:
- Use `asyncio.wait_for()` with timeout
- Avoid `asyncio.sleep()` for synchronization
- Use events/queues for coordination

---

## Test Organization Best Practices

1. **One test class per behavior**: Group related tests in classes
2. **Descriptive test names**: `test_<condition>_<expected_result>`
3. **Arrange-Act-Assert**: Structure each test clearly
4. **Minimal fixtures**: Only create what's needed
5. **Test one thing**: Each test verifies one behavior
6. **Docstrings**: Document what's being tested

---

## Type IV: Judges (Semantic Assertions)

For LLM outputs where exact matching is impossible. Uses metamorphic relations.

### Oracle Validation

```python
from testing import Oracle, SubsetRelation, PermutationInvarianceRelation

class TestSemanticCorrectness:
    """Semantic validation for LLM outputs."""

    async def test_summary_contains_key_facts(self) -> None:
        """Oracle validates semantic correctness."""
        oracle = Oracle()

        relation = SubsetRelation(
            base_extractor=extract_key_facts,
            derived_extractor=extract_summary_facts,
        )

        document = "..."
        summary = await summarizer.invoke(document)

        result = await oracle.validate(
            base_input=document,
            derived_input=summary,
            relation=relation,
        )

        assert result.passed, f"Missing facts: {result.violations}"
```

### TrustGate for Agent Actions

```python
from agents.t import TrustGate, Proposal, create_trust_gate

gate = create_trust_gate(
    judgment_threshold=0.8,
    risk_threshold=0.3,
)

proposal = Proposal(
    agent="my-agent",
    action="modify database schema",
    diff="ALTER TABLE...",
    risk=0.4,
)

decision = await gate.evaluate(proposal, agent="my-agent")

if decision.approved:
    print("Approved")
elif decision.bypass_cost:
    print(f"Denied. Bypass cost: {decision.bypass_cost}")
```

---

## Type V: Witnesses (Integration)

End-to-end tests verifying full system behavior.

### Topologist for Composition

```python
from testing import Topologist

class TestComposition:
    async def test_associativity_under_noise(self) -> None:
        """(f >> g) >> h == f >> (g >> h) even with noise."""
        topologist = Topologist()

        report = await topologist.verify_associativity(
            agents=[agent_a, agent_b, agent_c],
            inputs=test_inputs,
            noise_level=0.1,
        )

        assert report.passed
```

### Cortex Assurance System

```python
from testing import Cortex, create_enhanced_cortex

class TestSystem:
    async def test_full_assurance(self) -> None:
        """Full Cortex assurance system."""
        cortex = create_enhanced_cortex()

        briefing = await cortex.run_briefing(
            agents=[agent],
            test_inputs=inputs,
            budget_tier="quick",
        )

        print(briefing.summary)
        assert briefing.overall_health >= 0.8
```

---

## Testing Module Exports

```python
from testing import (
    # Fixtures
    as_umwelt, as_agent,
    # Strategies (Hypothesis)
    simple_agents, agent_chains, valid_dna, invalid_dna, type_names,
    # Oracle (Phase 8)
    Oracle, MetamorphicRelation, SubsetRelation,
    IdempotencyRelation, PermutationInvarianceRelation,
    # Topologist
    Topologist, TopologistReport, NoiseFunctor,
    # Analyst
    CausalAnalyst, WitnessStore, DeltaDebugResult,
    # Market
    TestMarket, BudgetManager, BudgetTier,
    # Red Team
    RedTeam, AdversarialInput, MutationScore,
    # Cortex
    Cortex, create_enhanced_cortex, BriefingReport,
)
```

---

## Stress Testing Patterns

The Wave 1 stress tests demonstrate three key patterns for high-confidence reactive code.

### Property-Based Testing (Hypothesis)

Use Hypothesis to test invariants across many generated inputs:

```python
from hypothesis import given, settings, strategies as st
import pytest

from agents.i.reactive.signal import Signal, Snapshot

@given(st.integers())
def test_snapshot_restore_roundtrip(value: int) -> None:
    """Any value can be snapshot and restored."""
    sig = Signal.of(value)
    snap = sig.snapshot()
    sig.set(value + 1)
    sig.restore(snap)
    assert sig.value == value

@given(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1, max_size=50))
def test_generation_monotonic(values: list[int]) -> None:
    """Generation always increases on distinct value changes."""
    sig = Signal.of(values[0])
    prev_gen = sig.generation
    for v in values[1:]:
        if v != sig.value:
            sig.set(v)
            assert sig.generation > prev_gen
            prev_gen = sig.generation

@given(st.text(min_size=0, max_size=100))
def test_signal_text_values(text: str) -> None:
    """Signal works with arbitrary text values."""
    sig = Signal.of(text)
    snap = sig.snapshot()
    sig.set("changed")
    sig.restore(snap)
    assert sig.value == text
```

**Key strategies**:
- `st.integers()` - arbitrary integers
- `st.text()` - unicode strings
- `st.floats(allow_nan=False)` - safe floats
- `st.lists()` - lists of other strategies

### Performance Baselines

Set performance budgets that fail if violated:

```python
import time

def test_signal_snapshot_performance() -> None:
    """Signal snapshot/restore should be fast."""
    sig = Signal.of(0)

    start = time.perf_counter()
    for i in range(10000):
        sig.set(i)
        snap = sig.snapshot()
        sig.restore(snap)
    elapsed = time.perf_counter() - start

    # Should complete 10000 cycles in under 1 second
    assert elapsed < 1.0, f"Signal snapshot cycle too slow: {elapsed:.3f}s"

def test_computed_recompute_performance() -> None:
    """Computed recomputation should be fast."""
    sig = Signal.of(0)
    computed = sig.map(lambda x: x * 2 + 1)

    start = time.perf_counter()
    for i in range(10000):
        sig.set(i)
        _ = computed.value
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0, f"Computed recompute too slow: {elapsed:.3f}s"

def test_subscriber_notification_performance() -> None:
    """Subscriber notifications should be fast."""
    sig = Signal.of(-1)
    count = [0]

    for _ in range(10):
        sig.subscribe(lambda v: count.__setitem__(0, count[0] + 1))

    start = time.perf_counter()
    for i in range(10000):
        sig.set(i)
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0, f"Subscriber notification too slow: {elapsed:.3f}s"
    assert count[0] == 100000  # 10 subscribers * 10000 updates
```

### High-Iteration Stress Tests

Test stability under load:

```python
import random

def test_signal_1000_snapshots() -> None:
    """Signal handles 1000 snapshots without degradation."""
    sig = Signal.of(0)
    snapshots: list[Snapshot[int]] = []

    for i in range(1000):
        sig.set(i)
        snapshots.append(sig.snapshot())

    # Restore 100 random snapshots
    sample = random.sample(snapshots, 100)
    for snap in sample:
        sig.restore(snap)
        assert sig.value == snap.value

def test_signal_100_subscribers() -> None:
    """Signal handles 100 concurrent subscribers."""
    sig = Signal.of(0)
    results: list[list[int]] = [[] for _ in range(100)]

    unsubs = []
    for i in range(100):
        idx = i
        def callback(v: int, idx: int = idx) -> None:
            results[idx].append(v)
        unsubs.append(sig.subscribe(callback))

    for j in range(1, 51):
        sig.set(j)

    for r in results:
        assert r == list(range(1, 51))

    for unsub in unsubs:
        unsub()

def test_modal_scope_deep_nesting() -> None:
    """ModalScope handles 50-deep branch nesting."""
    from agents.d.modal_scope import ModalScope

    root = ModalScope.create_root()
    current = root

    for i in range(50):
        current = current.branch(f"level-{i}", budget=0.99)

    assert current.depth == 50
```

### Boundary Value Tests

Test edge cases explicitly:

```python
@pytest.mark.parametrize("entropy", [0.0, 0.5, 1.0, 0.001, 0.999])
def test_entropy_boundary_values(entropy: float) -> None:
    """entropy_to_distortion handles boundary values."""
    from agents.i.reactive.entropy import entropy_to_distortion

    distortion = entropy_to_distortion(entropy, seed=42, t=0.0)
    assert isinstance(distortion.blur, float)
    assert isinstance(distortion.skew, float)

def test_turn_empty_content() -> None:
    """Turn handles empty content."""
    from protocols.api.turn import Turn

    turn = Turn(speaker="test", content="", timestamp=0.0)
    assert turn.to_cli() == "[test]: "

def test_turn_unicode_content() -> None:
    """Turn handles unicode/emoji content."""
    from protocols.api.turn import Turn

    turn = Turn(speaker="🤖", content="Hello 世界! 🌍", timestamp=0.0)
    cli = turn.to_cli()
    assert "🤖" in cli
    assert "世界" in cli
```

### Running Stress Tests

```bash
cd impl/claude

# Run all stress tests
uv run pytest -k "stress" -v

# Run property-based tests
uv run pytest agents/i/reactive/_tests/test_wave1_stress.py -v

# Run with verbose hypothesis output
uv run pytest --hypothesis-show-statistics agents/i/reactive/_tests/test_wave1_stress.py
```

---

## Related Skills

- [building-agent](building-agent.md) - Creating well-formed agents
- [flux-agent](flux-agent.md) - Testing async streaming agents
- [handler-patterns](handler-patterns.md) - Testing CLI handlers
- [agent-observability](agent-observability.md) - Metrics and debugging
- [reactive-primitives](reactive-primitives.md) - Signal/Computed/Effect
- [modal-scope-branching](modal-scope-branching.md) - Context branching

---

## Changelog

- 2025-12-14: Added stress testing patterns (property-based, performance baselines, boundary tests)
- 2025-12-12: Added T-gent Types I-V taxonomy, T-gent test agents, Oracle, Cortex patterns
- 2025-12-12: Initial version based on conftest.py and testing patterns
