# Skill: Test Patterns

> *"DI > mocking: set_soul() injection beats patch() for testability."*
> *"Property-based tests catch edge cases humans miss."*

**Purpose**: Writing effective tests for kgents components—agents, Crown Jewels, AGENTESE nodes, React components.

---

## When to Use This Skill

- Writing tests for any new feature
- Debugging flaky tests
- Setting up test isolation
- Adding property-based testing with Hypothesis
- Performance baseline assertions

---

## The Five T-gent Types

| Type | Purpose | Use When |
|------|---------|----------|
| **Type I: Unit** | Isolated function testing | Pure functions, utilities |
| **Type II: Integration** | Component interaction | Service wiring, DI validation |
| **Type III: Property** | Invariant verification | Composition laws, data structures |
| **Type IV: Chaos** | Resilience under failure | Event-driven systems, React components |
| **Type V: Performance** | Baseline assertions | Critical paths, regressions |

---

## Core Principle: DI Over Mocking

**The Rule**: Prefer dependency injection over `patch()`.

```python
# BAD: Mocking couples test to implementation
@patch("services.soul.get_soul")
def test_with_mock(mock_soul):
    mock_soul.return_value = FakeSoul()
    ...

# GOOD: DI allows clean injection
def test_with_di(test_soul: Soul):
    set_soul(test_soul)  # Clean injection
    result = my_service.process()
    assert result.source == test_soul
```

**Why**:
- Mocks couple tests to implementation details
- DI makes tests readable and maintainable
- Services dataclass wires all deps at startup—single source of truth

---

## Test Isolation Patterns

### PID-Based Database Isolation

```python
# Prevents SQLite lockups across parallel workers
import os
pid = os.getpid()
db_path = f"membrane_test_{pid}.db"
```

### Detecting Test Environment

```python
import os

def is_test_env() -> bool:
    return bool(
        os.environ.get("PYTEST_XDIST_WORKER") or
        os.environ.get("PYTEST_CURRENT_TEST")
    )
```

### Session-Scoped Fixtures

```python
# ROOT conftest.py - ensures workers populated
@pytest.fixture(scope="session")
def db_engine():
    engine = create_test_engine()
    yield engine
    engine.dispose()  # Reset singleton each session
```

### Registry Singleton + xdist

```python
# Session-scoped fixtures in ROOT conftest.py
# Ensures workers have populated registry before tests run
@pytest.fixture(scope="session", autouse=True)
def populate_registry():
    from protocols.agentese.gateway import _import_node_modules
    _import_node_modules()
```

---

## Property-Based Testing with Hypothesis

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_composition_associativity(items):
    """(f >> g) >> h == f >> (g >> h)"""
    a = Agent(items)
    b = Agent(items)
    c = Agent(items)

    left = (a >> b) >> c
    right = a >> (b >> c)

    assert left.result == right.result

@given(st.text(min_size=1))
def test_path_roundtrip(path_segment):
    """Path serialization is lossless"""
    path = AgentesePath.parse(f"world.{path_segment}")
    assert str(path) == f"world.{path_segment}"
```

**Key Insight**: Hypothesis found boundary issues humans missed (from learnings).

---

## Chaos Testing (React/Frontend)

### Testing Component Resilience

```typescript
// Testing error boundaries
test('component handles API failure gracefully', async () => {
  // Saboteur pattern: inject failure
  server.use(
    rest.get('/api/data', (req, res, ctx) => {
      return res(ctx.status(500));
    })
  );

  render(<MyComponent />);

  // Should show error state, not crash
  expect(await screen.findByText(/error/i)).toBeInTheDocument();
});
```

### SSE Chaos Testing

```typescript
test('handles SSE disconnect and reconnect', async () => {
  const { result } = renderHook(() => useSSEStream({
    url: '/api/stream',
    autoReconnect: true,
  }));

  // Simulate disconnect
  act(() => {
    server.close();
  });

  expect(result.current.isConnected).toBe(false);
  expect(result.current.reconnectAttempts).toBeGreaterThan(0);
});
```

---

## Performance Baselines

```python
import time

def test_composition_performance():
    """100-widget chains in <10ms"""
    start = time.perf_counter()

    chain = widgets[0]
    for w in widgets[1:100]:
        chain = chain >> w

    elapsed = time.perf_counter() - start
    assert elapsed < 0.010, f"Composition took {elapsed:.3f}s, expected <10ms"

def test_api_latency_baseline():
    """API responses under 200ms"""
    start = time.perf_counter()
    response = client.get("/v1/brain/status")
    elapsed = (time.perf_counter() - start) * 1000

    assert elapsed < 200, f"API took {elapsed:.0f}ms, expected <200ms"
```

---

## Contract Tests (Python ↔ TypeScript)

```python
# Python validators mirror TypeScript interfaces
from pydantic import BaseModel

class BrainStatus(BaseModel):
    """Must match frontend BrainStatus type"""
    spatial_navigable: bool
    crystal_count: int
    last_crystallization: str | None

def test_brain_status_contract():
    """Verify response matches TypeScript interface"""
    response = client.get("/v1/brain/status")
    status = BrainStatus.model_validate(response.json())

    # TypeScript expects these exact fields
    assert hasattr(status, 'spatial_navigable')
    assert hasattr(status, 'crystal_count')
```

---

## Testing AGENTESE Nodes

### Type II: Integration Test

```python
@pytest.fixture
def logos_context():
    """Full AGENTESE context for integration tests"""
    from protocols.agentese.gateway import Logos
    return Logos()

async def test_node_invocation(logos_context):
    """Node responds to invoke"""
    result = await logos_context.invoke(
        "world.brain.manifest",
        test_observer
    )
    assert result is not None
    assert hasattr(result, 'crystals')
```

### Testing DI Resolution

```python
def test_node_dependencies_resolve():
    """All declared dependencies must be registered"""
    from services.providers import container

    # Get all nodes
    nodes = get_registered_nodes()

    for node in nodes:
        for dep_name in node.dependencies:
            assert container.has(dep_name), \
                f"Node {node.path} requires unregistered dep: {dep_name}"
```

---

## Testing Crown Jewel Patterns

### Container-Owns-Workflow Pattern

```python
async def test_container_persists_workflow_ephemeral():
    """Container persists; workflows come and go"""
    container = BrainContainer()

    workflow1 = container.start_workflow("crystallize")
    await workflow1.complete()

    # Container still exists after workflow ends
    assert container.is_active
    assert workflow1.is_complete

    # Can start new workflow
    workflow2 = container.start_workflow("navigate")
    assert workflow2.is_active
```

### Signal Aggregation Pattern

```python
def test_signal_aggregation_transparent():
    """Multiple signals aggregate with confidence + reasons"""
    signals = [
        Signal(value=0.8, reason="test passes"),
        Signal(value=0.6, reason="lint clean"),
        Signal(value=0.9, reason="type check passes"),
    ]

    aggregated = aggregate_signals(signals)

    assert 0.7 < aggregated.confidence < 0.85  # Weighted average
    assert len(aggregated.reasons) == 3  # All reasons preserved
```

---

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| `@patch()` everything | Use DI injection |
| Global test state | PID-based isolation |
| Magic numbers in assertions | Named constants + baselines |
| Skip property tests | Hypothesis catches edge cases |
| Ignore flaky tests | Fix isolation, add chaos tests |
| Test implementation | Test behavior (behavioral isomorphism) |

---

## Quick Reference

```bash
# Run all tests
cd impl/claude && uv run pytest -q

# Run with coverage
uv run pytest --cov=services --cov-report=html

# Run property tests only
uv run pytest -m hypothesis

# Run performance tests
uv run pytest -m performance

# Parallel execution
uv run pytest -n auto

# Frontend tests
cd impl/claude/web && npm test
```

---

## Related Skills

- [validation.md](validation.md) — Measuring propositions and gates
- [polynomial-agent.md](polynomial-agent.md) — Testing state machines
- [agentese-node-registration.md](agentese-node-registration.md) — Testing DI resolution

---

*"If you can't test it, you can't trust it. If you can't inject it, you can't test it."*
