---
path: ideas/impl/qa-strategy
status: active
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  QA and Testing Strategy for all implementation work.
  Covers T-gent five types, coverage targets, parallel testing.
  Gate criteria for each sprint and phase.
---

# QA and Testing Strategy

> *"Untested code is broken code you haven't discovered yet."*

**Purpose**: Ensure quality throughout implementation of 200+ ideas
**Test Target**: 94%+ coverage (match existing standard)
**Framework**: T-gent five-type taxonomy

---

## T-gent Five-Type Test Taxonomy

### Type I: Unit Tests
**Purpose**: Verify individual functions in isolation
**Coverage Target**: 100% of new code paths

**Patterns**:
```python
# tests/unit/test_soul_commands.py
def test_eigenvector_calculation():
    """Type I: Pure function testing."""
    eigenvectors = calculate_eigenvectors(persona_state)
    assert eigenvectors.aesthetic >= 0.0
    assert eigenvectors.aesthetic <= 1.0
    assert sum(eigenvectors.values()) == pytest.approx(1.0)

def test_vibe_synthesis():
    """Type I: Output structure validation."""
    vibe = synthesize_vibe(eigenvectors, mood="contemplative")
    assert "summary" in vibe
    assert "dominant_trait" in vibe
```

**Quick Win Application**:
- Every CLI command gets Type I tests
- Every widget gets Type I tests
- Every helper function gets Type I tests

---

### Type II: Property Tests
**Purpose**: Verify invariants hold across random inputs
**Coverage Target**: Critical algorithms only

**Patterns**:
```python
# tests/property/test_composition.py
from hypothesis import given, strategies as st

@given(st.lists(st.sampled_from(AGENT_NAMES), min_size=2))
def test_composition_associativity(agent_names):
    """Type II: Composition law holds."""
    agents = [get_agent(name) for name in agent_names]

    # (A >> B) >> C == A >> (B >> C)
    left = compose(compose(agents[0], agents[1]), agents[2])
    right = compose(agents[0], compose(agents[1], agents[2]))

    result_left = await left.invoke(test_input)
    result_right = await right.invoke(test_input)
    assert result_left == result_right

@given(st.text(min_size=1))
def test_parse_never_crashes(input_text):
    """Type II: Parser robustness."""
    result = p_gent.parse(input_text)
    assert result.confidence >= 0.0
    assert result.confidence <= 1.0
```

**Crown Jewel Application**:
- `kg compose` composition laws
- Parser confidence bounds
- Eigenvector normalization

---

### Type III: Integration Tests
**Purpose**: Verify component interactions
**Coverage Target**: All CLI commands end-to-end

**Patterns**:
```python
# tests/integration/test_soul_flow.py
async def test_soul_vibe_end_to_end():
    """Type III: Full CLI flow."""
    result = await run_cli("kg soul vibe")

    assert result.exit_code == 0
    assert "dominant:" in result.output
    assert "eigenvectors:" in result.output or "confidence:" in result.output

async def test_pipeline_integration():
    """Type III: Multi-agent pipeline."""
    result = await run_cli("kg analyze --input 'test data'")

    # Verify all stages executed
    assert "ground:" in result.output or result.metadata.get("ground_executed")
    assert "judge:" in result.output or result.metadata.get("judge_executed")
    assert "verdict:" in result.output
```

**Medium Complexity Application**:
- Pipeline Builder produces valid pipelines
- Synthesis Wizard generates valid syntheses
- Time Travel Debugger replays correctly

---

### Type IV: Adversarial Tests
**Purpose**: Verify behavior under hostile/chaotic conditions
**Coverage Target**: All critical paths

**Patterns**:
```python
# tests/adversarial/test_chaos.py
async def test_byzantine_input():
    """Type IV: Saboteur agent testing."""
    saboteur = SaboteurAgent()
    malicious_input = await saboteur.generate_attack("injection")

    result = await run_cli(f"kg parse '{malicious_input}'")

    # System should not crash
    assert result.exit_code in [0, 1]  # Success or handled error
    # No code execution should occur
    assert "eval" not in result.output
    assert "exec" not in result.output

async def test_resource_exhaustion():
    """Type IV: Resource limits respected."""
    huge_input = "x" * 1_000_000

    result = await run_cli(f"kg parse '{huge_input}'", timeout=5)

    assert result.exit_code in [0, 1, 124]  # Success, error, or timeout
    # Memory should not explode
    assert result.max_memory_mb < 500
```

**Cross-Pollination Application**:
- Self-Healing Pipeline handles failures
- "Would Kent Approve?" rejects malicious code
- Circuit breakers trip correctly

---

### Type V: Dialectic Tests
**Purpose**: Verify contradiction detection and resolution
**Coverage Target**: All dialectical agents

**Patterns**:
```python
# tests/dialectic/test_synthesis.py
async def test_contradiction_detection():
    """Type V: Contradict agent finds tensions."""
    thesis = "Move fast"
    antithesis = "Don't break things"

    result = await contradict.detect(thesis, antithesis)

    assert result.tension_detected
    assert result.contradiction_type in ["direct", "indirect", "partial"]

async def test_synthesis_aufheben():
    """Type V: Sublate preserves, negates, elevates."""
    contradiction = Contradiction(
        thesis="Speed",
        antithesis="Stability"
    )

    synthesis = await sublate.resolve(contradiction)

    # Aufheben verification
    assert synthesis.preserved  # Something kept from both
    assert synthesis.negated    # Something rejected from both
    assert synthesis.elevated   # Something new emerges
```

**Crown Jewel Application**:
- `kg dialectic` produces valid syntheses
- `kg shadow` detects genuine shadows
- Three-Lens Replay gives distinct perspectives

---

## QA Gates

### Sprint Gate Criteria

| Sprint | Gate Requirements |
|--------|-------------------|
| 1 (K-gent CLI) | Type I + III for all `soul *` commands |
| 2 (Infrastructure) | Type I + II + IV for parser, reality classifier |
| 3 (H-gent CLI) | Type I + III + V for dialectical commands |
| 4 (Visualization) | Type I + III for all widgets |
| 5 (Cross-Pollination) | Type III + IV + V for all combos |
| 6 (Integration) | Full test suite green |

### Merge Criteria

Every PR must pass:
- [ ] All Type I tests green
- [ ] Type II tests (if applicable) green
- [ ] Type III smoke test green
- [ ] mypy --strict passes
- [ ] ruff check passes
- [ ] Coverage >= 94%
- [ ] No security vulnerabilities

---

## Parallel Testing Strategy

### Test Execution Tracks

```
Track A: Unit Tests (Type I)
├── Run: pytest tests/unit/ -n auto
├── Time: ~30 seconds
└── Agent: Test Runner 1

Track B: Property Tests (Type II)
├── Run: pytest tests/property/ -n auto --hypothesis-profile=ci
├── Time: ~2 minutes
└── Agent: Test Runner 2

Track C: Integration Tests (Type III)
├── Run: pytest tests/integration/ -n auto
├── Time: ~3 minutes
└── Agent: Test Runner 3

Track D: Adversarial Tests (Type IV)
├── Run: pytest tests/adversarial/ --timeout=60
├── Time: ~5 minutes
└── Agent: Test Runner 4

Track E: Dialectic Tests (Type V)
├── Run: pytest tests/dialectic/
├── Time: ~1 minute
└── Agent: Test Runner 5
```

**Total Time (Parallel)**: ~5 minutes
**Total Time (Sequential)**: ~12 minutes

---

## Test Coverage by Feature

### Quick Wins Test Requirements

| Feature Category | Type I | Type II | Type III | Type IV | Type V |
|-----------------|--------|---------|----------|---------|--------|
| Soul CLI | ✓ | - | ✓ | - | - |
| Parse CLI | ✓ | ✓ | ✓ | ✓ | - |
| Reality CLI | ✓ | - | ✓ | ✓ | - |
| Visualization | ✓ | - | ✓ | - | - |
| Dialectic CLI | ✓ | - | ✓ | - | ✓ |

### Crown Jewels Test Requirements

| Feature | Type I | Type II | Type III | Type IV | Type V |
|---------|--------|---------|----------|---------|--------|
| kg whatif | ✓ | - | ✓ | - | ✓ |
| kg soul vibe | ✓ | ✓ | ✓ | - | - |
| kg compose | ✓ | ✓ | ✓ | - | - |
| kg parse | ✓ | ✓ | ✓ | ✓ | - |
| kg shadow | ✓ | - | ✓ | - | ✓ |
| Ethical Review | ✓ | - | ✓ | ✓ | ✓ |

### Cross-Pollination Test Requirements

| Combo | Type I | Type II | Type III | Type IV | Type V |
|-------|--------|---------|----------|---------|--------|
| K + H | ✓ | - | ✓ | - | ✓ |
| U + P + J | ✓ | ✓ | ✓ | ✓ | - |
| I + Flux | ✓ | - | ✓ | - | - |
| M + N | ✓ | - | ✓ | - | - |

---

## Test Data Strategy

### Fixtures

```python
# conftest.py
@pytest.fixture
def minimal_persona():
    """Smallest valid persona for testing."""
    return PersonaState(
        eigenvectors={"aesthetic": 0.5, "categorical": 0.5},
        confidence=0.8
    )

@pytest.fixture
def full_persona():
    """Complete persona with all fields."""
    return PersonaState(
        eigenvectors={
            "aesthetic": 0.15,
            "categorical": 0.20,
            "gratitude": 0.15,
            "heterarchy": 0.15,
            "generativity": 0.20,
            "joy": 0.15
        },
        mood="contemplative",
        confidence=0.92,
        last_updated=datetime.now()
    )

@pytest.fixture
def contradiction_pair():
    """Standard thesis/antithesis for dialectic tests."""
    return {
        "thesis": "Move fast",
        "antithesis": "Don't break things"
    }
```

### Golden Files

```
tests/golden/
├── soul_vibe_output.json       # Expected vibe response
├── parse_confidence.json       # Expected parse results
├── synthesis_aufheben.json     # Expected synthesis structure
└── shadow_detection.json       # Expected shadow output
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/qa.yml
name: QA Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-type: [unit, property, integration, adversarial, dialectic]

    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4

      - name: Run ${{ matrix.test-type }} tests
        run: |
          uv run pytest tests/${{ matrix.test-type }}/ \
            --cov=impl \
            --cov-report=xml \
            -v

  coverage:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Check coverage
        run: |
          coverage=$(cat coverage.xml | grep line-rate | head -1 | grep -oP '\d+\.\d+')
          if (( $(echo "$coverage < 0.94" | bc -l) )); then
            echo "Coverage $coverage below 94% threshold"
            exit 1
          fi
```

---

## Quality Metrics

### Per-Sprint Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Coverage | >= 94% | `pytest --cov` |
| Type Hint Coverage | 100% | `mypy --strict` |
| Lint Score | 0 errors | `ruff check` |
| Security Issues | 0 critical | `bandit -r` |
| Test Duration | < 5 min | CI time |

### Aggregate Metrics

| Metric | Target |
|--------|--------|
| Total Tests Written | 500+ (new) |
| Test/Code Ratio | >= 1:1 |
| Flaky Test Rate | < 1% |
| Mean Time to Fix | < 4 hours |

---

## Security Testing

### OWASP Top 10 Checklist

| Vulnerability | Test Type | Command |
|---------------|-----------|---------|
| Injection | Type IV | `kg parse` with malicious input |
| Broken Auth | Type III | API key handling |
| XSS | Type IV | TUI output sanitization |
| Insecure Design | Type V | Architectural review |
| Misconfig | Type III | Default settings |

### Specific Security Tests

```python
# tests/security/test_injection.py
@pytest.mark.parametrize("payload", [
    "'; DROP TABLE users; --",
    "${7*7}",
    "{{7*7}}",
    "__import__('os').system('id')",
    "<script>alert('xss')</script>"
])
async def test_injection_resistance(payload):
    """Verify no injection vulnerabilities."""
    result = await run_cli(f"kg parse '{payload}'")

    # Command should not execute
    assert "49" not in result.output  # ${7*7} result
    assert "uid=" not in result.output  # os.system result
```

---

## Test Automation Commands

```bash
# Run all tests
uv run pytest

# Run by type
uv run pytest tests/unit/
uv run pytest tests/property/
uv run pytest tests/integration/
uv run pytest tests/adversarial/
uv run pytest tests/dialectic/

# Run with coverage
uv run pytest --cov=impl --cov-report=html

# Run specific feature
uv run pytest -k "soul"
uv run pytest -k "parse"
uv run pytest -k "dialectic"

# Run parallel
uv run pytest -n auto

# Run with verbose output
uv run pytest -v --tb=short
```

---

## QA Checklist Template

### Per-Feature Checklist

```markdown
## Feature: [Name]

### Code Quality
- [ ] Type hints complete
- [ ] Docstrings present
- [ ] No magic numbers
- [ ] Error handling complete

### Tests
- [ ] Type I: Unit tests written
- [ ] Type II: Property tests (if applicable)
- [ ] Type III: Integration test written
- [ ] Type IV: Adversarial test (if applicable)
- [ ] Type V: Dialectic test (if applicable)

### Coverage
- [ ] Line coverage >= 94%
- [ ] Branch coverage >= 90%
- [ ] Edge cases covered

### Security
- [ ] Input validation
- [ ] Output sanitization
- [ ] No secrets in code

### Performance
- [ ] Response time acceptable
- [ ] Memory usage bounded
- [ ] No blocking operations
```

---

*"Quality is not an act, it is a habit."*
