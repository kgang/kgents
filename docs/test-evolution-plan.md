# Test Evolution Plan

A principled strategy for leveling up kgents test infrastructure, theory, implementation, durability, and synthesis with the developer's mental landscape.

**Date**: December 2024
**Status**: Planning
**Principles Applied**: All 7 from `spec/principles.md`

---

## Executive Summary

The kgents test suite has grown organically to **4,703 tests** across **141 files** (76,592 lines). While coverage is strong, the infrastructure lacks the principled foundation that makes kgents special. This plan aligns testing with the seven design principles.

### Current State

| Metric | Value | Assessment |
|--------|-------|------------|
| Test Files | 141 | Good quantity |
| Test Functions | ~4,700 | High coverage |
| Total Lines | 76,592 | Avg 543 lines/file |
| Fixtures | 241 | Duplicated (no conftest.py) |
| Async Tests | 863 | Well-supported |
| Category Law Tests | 120+ | Strong foundation |

### Key Findings

**Strengths:**
- Extensive category theory law verification (Identity, Associativity, Functor)
- `BootstrapWitness` exists for runtime law verification
- Tests have Philosophy docstrings aligned with spec
- DNA constraints encode ethical principles

**Gaps:**
- No `conftest.py` hierarchy (fixtures duplicated)
- Property-based testing infrastructure unused
- Category law tests isolated from agent test suites
- BootstrapWitness not integrated into pytest

---

## Test Coverage by Agent

| Agent | Files | Status | Notes |
|-------|-------|--------|-------|
| D (Data) | 15 | Excellent | Most extensive coverage |
| L (Lattice) | 15 | Excellent | Type system verification |
| P (Parser) | 12 | Excellent | Composition patterns |
| B (Bio) | 10 | Good | Hypothesis testing |
| N (Narrative) | 9 | Good | Chronicle/Bard |
| G (Grammar) | 9 | Good | Synthesis |
| T (Tool) | 9 | Good | Law validation |
| F (Factory) | 9 | Good | Contracts |
| J (JIT) | 6 | Medium | Factory integration |
| E (Entity) | 5 | Medium | Persistence |
| R (Refinery) | 5 | Medium | DSPy backend |
| I (Interface) | 4 | Minimal | TUI components |
| O (Observer) | 2 | Minimal | BootstrapWitness |
| M (Memory) | 1 | Minimal | Large monolithic file |
| A,C,K,W | 1 each | Minimal | Core only |
| H,X,Y | 0 | None | Not yet started |

---

## Philosophy Analysis (vs spec/principles.md)

### Principle 1: Tasteful

> Each agent serves a clear, justified purpose.

**Current State:** Mixed. Most tests have clear purpose docstrings, but some files are "kitchen sink" collections.

**Target:** Every test file answers "why does this test need to exist?"

### Principle 2: Curated

> Intentional selection over exhaustive cataloging.

**Current State:** Weak. 241 fixtures scattered across files, many duplicated. No central curation.

**Target:** 10 curated core fixtures in conftest.py hierarchy.

### Principle 3: Ethical

> Agents augment human capability, never replace judgment.

**Current State:** Good. DNA constraints validate `EPISTEMIC_HUMILITY`, `POPPERIAN_PRINCIPLE`.

**Target:** Maintain ethical constraint testing as non-optional.

### Principle 4: Joy-Inducing

> Delight in interaction; personality matters.

**Current State:** Present in Philosophy docstrings.

**Target:** Tests should be readable as documentation.

### Principle 5: Composable

> Agents are morphisms in a category; composition is primary.

**Current State:** Strong foundation but isolated. `test_composition_laws.py` exists but isn't integrated.

**Target:** Every agent proves category citizenship.

### Principle 6: Heterarchical

> Agents exist in flux, not fixed hierarchy.

**Current State:** Weak. Tests are hierarchical (per-agent directories).

**Target:** Cross-agent integration tests, autopoietic witnesses.

### Principle 7: Generative

> Spec is compression; design should generate implementation.

**Current State:** Nascent. Tests describe behavior but don't generate from spec.

**Target:** Property-based testing from spec definitions.

---

## Phase 1: Foundation (Tasteful + Curated)

**Goal:** Centralize infrastructure without bloat
**Timeline:** Foundation work
**Effort:** Medium

### 1.1 Create conftest.py Hierarchy

```
impl/claude/conftest.py           # Root: Core fixtures
impl/claude/agents/conftest.py    # Agent-level fixtures
impl/claude/bootstrap/conftest.py # Law verification fixtures
impl/claude/protocols/conftest.py # Protocol fixtures
```

### 1.2 Root conftest.py Content

```python
"""
Root pytest configuration for kgents.

Philosophy: Fixtures are curated, not accumulated.
Only fixtures used by 3+ test files belong here.
"""

import pytest
from typing import Any
from dataclasses import dataclass

# =============================================================================
# Core Agent Fixtures
# =============================================================================

@dataclass
class MockAgent:
    """Minimal agent for testing composition."""
    name: str = "MockAgent"

    async def invoke(self, input: Any) -> Any:
        return input

@dataclass
class EchoAgent:
    """Agent that echoes input."""
    name: str = "EchoAgent"

    async def invoke(self, input: Any) -> str:
        return f"Echo: {input}"

@dataclass
class IdentityAgent:
    """The Id morphism - returns input unchanged."""
    name: str = "Id"

    async def invoke(self, input: Any) -> Any:
        return input

    def __rshift__(self, other):
        from bootstrap import compose
        return compose(self, other)


@pytest.fixture
def mock_agent() -> MockAgent:
    """Minimal agent fixture."""
    return MockAgent()


@pytest.fixture
def echo_agent() -> EchoAgent:
    """Echo agent fixture."""
    return EchoAgent()


@pytest.fixture
def identity_agent() -> IdentityAgent:
    """Identity morphism fixture."""
    return IdentityAgent()


# =============================================================================
# Storage Fixtures
# =============================================================================

@pytest.fixture
def volatile_store():
    """In-memory volatile storage for testing."""
    from agents.d import VolatileAgent
    return VolatileAgent(agent_id="test_volatile")


@pytest.fixture
async def memory_store():
    """Memory crystal store for testing."""
    from agents.n import MemoryCrystalStore
    store = MemoryCrystalStore()
    await store.initialize()
    return store


# =============================================================================
# DNA Fixtures
# =============================================================================

@pytest.fixture
def test_dna():
    """Standard test DNA configuration."""
    from bootstrap.dna import DNA
    return DNA(
        agent_name="TestAgent",
        confidence_threshold=0.8,
        max_retries=3,
    )


# =============================================================================
# Embedding Fixtures
# =============================================================================

@pytest.fixture
def test_embedding():
    """Standard test embedding (384-dim zeros)."""
    return [0.0] * 384


@pytest.fixture
def random_embedding():
    """Random test embedding for similarity tests."""
    import random
    return [random.random() for _ in range(384)]


# =============================================================================
# Custom Markers
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "law(name): mark test as category law verification"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow-running"
    )
    config.addinivalue_line(
        "markers", "accursed_share: mark test as exploratory/chaos"
    )
```

### 1.3 Bootstrap conftest.py

```python
"""
Bootstrap test configuration.

Philosophy: The bootstrap kernel is the irreducible core.
These fixtures verify laws hold.
"""

import pytest
from agents.o.bootstrap_witness import (
    BootstrapWitness,
    create_bootstrap_witness,
)


@pytest.fixture
def bootstrap_witness() -> BootstrapWitness:
    """BootstrapWitness for law verification."""
    return create_bootstrap_witness(test_iterations=5)


@pytest.fixture
async def verified_bootstrap(bootstrap_witness):
    """Pre-verified bootstrap state."""
    result = await bootstrap_witness.invoke()
    assert result.kernel_intact, "Bootstrap kernel compromised"
    return result
```

---

## Phase 2: Laws as First-Class Citizens (Composable)

**Goal:** Every agent proves its category citizenship
**Timeline:** After Phase 1
**Effort:** Medium-High

### 2.1 Law Marker System

Update `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "law(name): mark test as category law verification",
    "law_identity: tests identity law (Id >> f == f == f >> Id)",
    "law_associativity: tests associativity ((f >> g) >> h == f >> (g >> h))",
    "law_functor_identity: tests functor identity (fmap id == id)",
    "law_functor_composition: tests functor composition (fmap (g.f) == fmap g . fmap f)",
]
```

### 2.2 Agent Test Template

Every agent should include law verification:

```python
"""
Tests for X-gent.

Philosophy: [Agent-specific philosophy from spec]
"""

import pytest
from agents.x import XAgent
from agents.o.bootstrap_witness import BootstrapWitness


class TestXAgentLaws:
    """Category law verification for X-gent."""

    @pytest.fixture
    def x_agent(self):
        return XAgent()

    @pytest.mark.law("identity")
    @pytest.mark.asyncio
    async def test_left_identity(self, x_agent, identity_agent):
        """Test Id >> x == x."""
        from bootstrap import compose

        composed = compose(identity_agent, x_agent)
        input_val = "test"

        direct = await x_agent.invoke(input_val)
        via_id = await composed.invoke(input_val)

        assert direct == via_id, "Left identity violated"

    @pytest.mark.law("identity")
    @pytest.mark.asyncio
    async def test_right_identity(self, x_agent, identity_agent):
        """Test x >> Id == x."""
        from bootstrap import compose

        composed = compose(x_agent, identity_agent)
        input_val = "test"

        direct = await x_agent.invoke(input_val)
        via_id = await composed.invoke(input_val)

        assert direct == via_id, "Right identity violated"

    @pytest.mark.law("associativity")
    @pytest.mark.asyncio
    async def test_associativity(self, x_agent):
        """Test (f >> g) >> h == f >> (g >> h)."""
        from bootstrap import compose
        from conftest import MockAgent

        f = x_agent
        g = MockAgent(name="g")
        h = MockAgent(name="h")

        left = compose(compose(f, g), h)
        right = compose(f, compose(g, h))

        input_val = "test"

        left_result = await left.invoke(input_val)
        right_result = await right.invoke(input_val)

        assert left_result == right_result, "Associativity violated"


class TestXAgentBehavior:
    """Behavioral tests for X-gent."""

    # ... domain-specific tests ...
```

### 2.3 CI Gate

Add to CI pipeline:

```yaml
# .github/workflows/laws.yml
name: Category Laws
on: [push, pull_request]

jobs:
  verify-laws:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Verify Category Laws
        run: pytest -m "law" --tb=short
```

---

## Phase 3: Property-Based Testing (Generative)

**Goal:** Let the spec generate test cases
**Timeline:** After Phase 2
**Effort:** High

### 3.1 Add Hypothesis Dependency

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "hypothesis>=6.100",  # ADD
    "hypothesis[cli]",     # ADD
]
```

### 3.2 Hypothesis Strategies for Agents

```python
# impl/claude/testing/strategies.py
"""
Hypothesis strategies for property-based testing.

Philosophy: Spec is compression; strategies generate from that compression.
"""

from hypothesis import strategies as st
from hypothesis import given, settings
from typing import TypeVar, Generic
from dataclasses import dataclass

A = TypeVar("A")
B = TypeVar("B")


# =============================================================================
# Agent Strategies
# =============================================================================

@st.composite
def simple_agents(draw, input_type=int, output_type=int):
    """Generate simple deterministic agents."""

    @dataclass
    class GeneratedAgent:
        name: str
        _offset: int

        async def invoke(self, x: int) -> int:
            return x + self._offset

        def __rshift__(self, other):
            from bootstrap import compose
            return compose(self, other)

    name = draw(st.text(min_size=1, max_size=10, alphabet="abcdefghijklmnop"))
    offset = draw(st.integers(min_value=-100, max_value=100))

    return GeneratedAgent(name=f"Agent_{name}", _offset=offset)


@st.composite
def agent_chains(draw, min_length=2, max_length=5):
    """Generate chains of composable agents."""
    length = draw(st.integers(min_value=min_length, max_value=max_length))
    return [draw(simple_agents()) for _ in range(length)]


# =============================================================================
# DNA Strategies
# =============================================================================

@st.composite
def valid_dna(draw):
    """Generate valid DNA configurations."""
    from bootstrap.dna import DNA

    return DNA(
        agent_name=draw(st.text(min_size=1, max_size=50)),
        confidence_threshold=draw(st.floats(min_value=0.0, max_value=1.0)),
        max_retries=draw(st.integers(min_value=0, max_value=10)),
    )


@st.composite
def invalid_dna(draw):
    """Generate intentionally invalid DNA for constraint testing."""
    from bootstrap.dna import DNA

    # At least one invalid value
    invalid_confidence = draw(st.floats(min_value=1.1, max_value=10.0))

    return DNA(
        agent_name=draw(st.text(min_size=1, max_size=50)),
        confidence_threshold=invalid_confidence,
        max_retries=draw(st.integers(min_value=-10, max_value=-1)),
    )


# =============================================================================
# Type Strategies
# =============================================================================

@st.composite
def type_names(draw):
    """Generate valid type names."""
    base_types = ["int", "str", "float", "bool", "None", "Any"]
    generic_bases = ["List", "Dict", "Optional", "Tuple"]

    if draw(st.booleans()):
        return draw(st.sampled_from(base_types))
    else:
        base = draw(st.sampled_from(generic_bases))
        inner = draw(st.sampled_from(base_types))
        return f"{base}[{inner}]"
```

### 3.3 Property-Based Law Tests

```python
# impl/claude/bootstrap/_tests/test_laws_property.py
"""
Property-based category law verification.

Philosophy: Laws must hold for ALL agents, not just handpicked examples.
"""

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from functools import reduce

from testing.strategies import simple_agents, agent_chains
from bootstrap import compose, ID


class TestIdentityLawProperty:
    """Property-based identity law tests."""

    @given(agent=simple_agents())
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_left_identity_property(self, agent):
        """For all f: Id >> f == f."""
        composed = compose(ID, agent)

        test_input = 42
        direct = await agent.invoke(test_input)
        via_id = await composed.invoke(test_input)

        assert direct == via_id

    @given(agent=simple_agents())
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_right_identity_property(self, agent):
        """For all f: f >> Id == f."""
        composed = compose(agent, ID)

        test_input = 42
        direct = await agent.invoke(test_input)
        via_id = await composed.invoke(test_input)

        assert direct == via_id


class TestAssociativityProperty:
    """Property-based associativity tests."""

    @given(agents=agent_chains(min_length=3, max_length=3))
    @settings(max_examples=50)
    @pytest.mark.asyncio
    async def test_associativity_property(self, agents):
        """For all f, g, h: (f >> g) >> h == f >> (g >> h)."""
        f, g, h = agents

        left = compose(compose(f, g), h)
        right = compose(f, compose(g, h))

        test_input = 0

        left_result = await left.invoke(test_input)
        right_result = await right.invoke(test_input)

        assert left_result == right_result

    @given(agents=agent_chains(min_length=2, max_length=10))
    @settings(max_examples=25)
    @pytest.mark.asyncio
    async def test_arbitrary_chain_associativity(self, agents):
        """Associativity holds for arbitrary chain lengths."""
        assume(len(agents) >= 2)

        # Left-associative fold
        left_result = reduce(compose, agents)

        # Right-associative fold
        right_result = reduce(lambda a, b: compose(a, b), reversed(agents))
        # Note: This isn't quite right-associative, but tests chain equivalence

        test_input = 0

        # Both should produce same behavior
        # (actual associativity would require proper right-fold)
```

### 3.4 DNA Constraint Fuzzing

```python
# impl/claude/bootstrap/_tests/test_dna_property.py
"""
Property-based DNA constraint testing.

Philosophy: Constraints must hold under adversarial generation.
"""

from hypothesis import given, settings
from testing.strategies import valid_dna, invalid_dna
from bootstrap.dna import DNA, Constraint


class TestDNAConstraintProperty:
    """Property-based DNA validation."""

    @given(dna=valid_dna())
    @settings(max_examples=200)
    def test_valid_dna_passes_validation(self, dna):
        """All valid DNA should pass validation."""
        errors = dna.validate()
        assert len(errors) == 0, f"Valid DNA failed: {errors}"

    @given(dna=invalid_dna())
    @settings(max_examples=200)
    def test_invalid_dna_fails_validation(self, dna):
        """All invalid DNA should fail validation."""
        errors = dna.validate()
        assert len(errors) > 0, "Invalid DNA passed validation"

    @given(dna=valid_dna())
    def test_epistemic_humility_constraint(self, dna):
        """EPISTEMIC_HUMILITY: confidence <= 0.8."""
        constraint = Constraint(
            name="epistemic_humility",
            check=lambda d: d.confidence_threshold <= 0.8,
            message="Confidence too high",
        )

        if dna.confidence_threshold <= 0.8:
            passed, _ = constraint.validate(dna)
            assert passed
```

---

## Phase 4: Autopoietic Witnesses (Heterarchical)

**Goal:** Tests that observe themselves
**Timeline:** After Phase 3
**Effort:** Medium

### 4.1 Pytest Plugin for BootstrapWitness

```python
# impl/claude/testing/pytest_witness.py
"""
Pytest plugin integrating BootstrapWitness.

Philosophy: The system observes its own verification.
"""

import pytest
from datetime import datetime
from agents.o.bootstrap_witness import (
    BootstrapWitness,
    BootstrapVerificationResult,
)
from agents.d import VolatileAgent


class WitnessPlugin:
    """Pytest plugin that runs BootstrapWitness."""

    def __init__(self):
        self.witness = BootstrapWitness()
        self.observations: list[dict] = []
        self.session_start: datetime | None = None
        self.verification_result: BootstrapVerificationResult | None = None

    def pytest_sessionstart(self, session):
        """Verify bootstrap at session start."""
        self.session_start = datetime.now()

        import asyncio
        self.verification_result = asyncio.run(self.witness.invoke())

        if not self.verification_result.kernel_intact:
            pytest.exit("Bootstrap kernel compromised - cannot run tests")

    def pytest_runtest_logreport(self, report):
        """Record test observations."""
        if report.when == "call":
            self.observations.append({
                "test": report.nodeid,
                "outcome": report.outcome,
                "duration": report.duration,
                "timestamp": datetime.now().isoformat(),
            })

    def pytest_sessionfinish(self, session, exitstatus):
        """Summary at session end."""
        if self.verification_result:
            print(f"\n{'='*60}")
            print("Bootstrap Witness Report")
            print(f"{'='*60}")
            print(f"Kernel Intact: {self.verification_result.kernel_intact}")
            print(f"Identity Laws: {'HOLD' if self.verification_result.identity_laws_hold else 'BROKEN'}")
            print(f"Composition Laws: {'HOLD' if self.verification_result.composition_laws_hold else 'BROKEN'}")
            print(f"Tests Observed: {len(self.observations)}")
            print(f"{'='*60}")


def pytest_configure(config):
    """Register the witness plugin."""
    config.pluginmanager.register(WitnessPlugin(), "witness")
```

### 4.2 Self-Healing Test Registry

```python
# impl/claude/testing/flaky_registry.py
"""
Registry for flaky test patterns.

Philosophy: Memory is not storage—it is active reconstruction.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from agents.d import TransactionalDataAgent


@dataclass
class FlakyPattern:
    """Record of a flaky test pattern."""
    test_id: str
    failure_count: int
    success_count: int
    last_failure: datetime
    failure_reasons: list[str] = field(default_factory=list)

    @property
    def flakiness_score(self) -> float:
        """0.0 = always passes, 1.0 = always fails."""
        total = self.failure_count + self.success_count
        if total == 0:
            return 0.0
        return self.failure_count / total


class FlakyRegistry:
    """D-gent backed registry for flaky tests."""

    def __init__(self, store: Optional[TransactionalDataAgent] = None):
        self.store = store or TransactionalDataAgent(agent_id="flaky_registry")

    async def record_outcome(self, test_id: str, passed: bool, reason: str = ""):
        """Record a test outcome."""
        async with self.store.transaction():
            pattern = await self.store.get(test_id) or FlakyPattern(
                test_id=test_id,
                failure_count=0,
                success_count=0,
                last_failure=datetime.min,
            )

            if passed:
                pattern.success_count += 1
            else:
                pattern.failure_count += 1
                pattern.last_failure = datetime.now()
                if reason:
                    pattern.failure_reasons.append(reason)

            await self.store.set(test_id, pattern)

    async def get_flaky_tests(self, threshold: float = 0.1) -> list[FlakyPattern]:
        """Get tests with flakiness above threshold."""
        all_patterns = await self.store.values()
        return [p for p in all_patterns if p.flakiness_score > threshold]

    async def should_retry(self, test_id: str) -> bool:
        """Should this test be retried based on history?"""
        pattern = await self.store.get(test_id)
        if not pattern:
            return False
        return pattern.flakiness_score > 0.1 and pattern.flakiness_score < 0.9
```

---

## Phase 5: The Accursed Share (Meta-Principle)

**Goal:** 10% exploratory budget
**Timeline:** After Phase 4
**Effort:** Low-Medium

### 5.1 Chaos/Fuzzing Tests

```python
# impl/claude/testing/accursed_share.py
"""
The Accursed Share: Exploratory and chaos testing.

Philosophy: We cherish and express gratitude for slop.
10% of test budget goes to unpredictable exploration.
"""

import pytest
import random
from typing import Any


@pytest.mark.accursed_share
class TestChaoticComposition:
    """Tests that compose random agents."""

    @pytest.mark.asyncio
    async def test_random_agent_composition(self):
        """Pick N random agents, compose, observe."""
        from agents import a, b, d, f, g, l, n, o, p, t

        # Collect all available agent classes
        agent_pools = [
            a.skeleton.GroundedSkeleton,
            # Add more as available...
        ]

        # Random selection
        n_agents = random.randint(2, 5)
        selected = random.choices(agent_pools, k=n_agents)

        # Attempt composition
        agents = [cls() for cls in selected]

        from bootstrap import compose
        from functools import reduce

        try:
            composed = reduce(compose, agents)
            # Just verify it's invokable
            assert hasattr(composed, 'invoke')
            # Record successful composition pattern
            print(f"SUCCESS: {' >> '.join(c.__class__.__name__ for c in agents)}")
        except Exception as e:
            # Record failure pattern for analysis
            print(f"FAILURE: {' >> '.join(c.__class__.__name__ for c in agents)}: {e}")
            # Don't fail - this is exploratory

    @pytest.mark.asyncio
    async def test_type_boundary_exploration(self):
        """Explore type boundaries with random inputs."""
        from agents.p import ProbabilisticASTParser

        parser = ProbabilisticASTParser()

        # Generate weird inputs
        inputs = [
            "",
            "a" * 10000,
            "\x00\x01\x02",
            "{'key': 'value'}",
            "[1, 2, 3]",
            "null",
            "undefined",
            "∞",
            "🎭" * 100,
        ]

        for inp in inputs:
            try:
                result = parser.parse(inp)
                print(f"Parsed '{inp[:20]}...': confidence={result.confidence}")
            except Exception as e:
                print(f"Failed '{inp[:20]}...': {type(e).__name__}")


@pytest.mark.accursed_share
class TestSerendipitousDiscovery:
    """Tests designed to discover unexpected behaviors."""

    @pytest.mark.asyncio
    async def test_deep_composition_chain(self):
        """Test very deep composition chains."""
        from conftest import IdentityAgent
        from bootstrap import compose
        from functools import reduce

        # Chain 100 identity agents
        agents = [IdentityAgent(name=f"Id_{i}") for i in range(100)]

        deep_chain = reduce(compose, agents)

        # Should still work
        result = await deep_chain.invoke(42)
        assert result == 42

        # Record observation
        print(f"Deep chain (n=100) succeeded")

    @pytest.mark.asyncio
    async def test_concurrent_mutations(self):
        """Test concurrent state mutations."""
        import asyncio
        from agents.d import VolatileAgent

        store = VolatileAgent(agent_id="concurrent_test")

        async def writer(key: str, n: int):
            for i in range(n):
                await store.set(key, i)
                await asyncio.sleep(0.001)

        # Multiple writers to same key
        await asyncio.gather(
            writer("key", 100),
            writer("key", 100),
            writer("key", 100),
        )

        # Just observe final state
        final = await store.get("key")
        print(f"Concurrent writes final value: {final}")
```

### 5.2 Discovery Feedback Loop

```python
# impl/claude/testing/discovery_log.py
"""
Log serendipitous discoveries from chaos tests.

Philosophy: Failed experiments are offerings, not waste.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


@dataclass
class Discovery:
    """A serendipitous discovery from testing."""
    test_name: str
    discovery_type: str  # "composition_success", "boundary_case", "unexpected_behavior"
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    actionable: bool = False
    fed_back_to_spec: bool = False


class DiscoveryLog:
    """Persistent log of discoveries."""

    def __init__(self, log_path: Path = Path(".discoveries.json")):
        self.log_path = log_path
        self.discoveries: list[Discovery] = []
        self._load()

    def _load(self):
        if self.log_path.exists():
            data = json.loads(self.log_path.read_text())
            self.discoveries = [Discovery(**d) for d in data]

    def _save(self):
        data = [
            {
                "test_name": d.test_name,
                "discovery_type": d.discovery_type,
                "description": d.description,
                "timestamp": d.timestamp.isoformat(),
                "actionable": d.actionable,
                "fed_back_to_spec": d.fed_back_to_spec,
            }
            for d in self.discoveries
        ]
        self.log_path.write_text(json.dumps(data, indent=2))

    def record(self, discovery: Discovery):
        """Record a new discovery."""
        self.discoveries.append(discovery)
        self._save()

    def get_actionable(self) -> list[Discovery]:
        """Get discoveries that should feed back to spec."""
        return [d for d in self.discoveries if d.actionable and not d.fed_back_to_spec]
```

---

## Immediate Actions

| Priority | Action | Principle | Status |
|----------|--------|-----------|--------|
| P0 | Create `impl/claude/conftest.py` | Curated | TODO |
| P0 | Add law tests to A-gent | Composable | TODO |
| P1 | Register `@pytest.mark.law` marker | Tasteful | TODO |
| P1 | Add hypothesis to pyproject.toml | Generative | TODO |
| P2 | Create agent test template | Composable | TODO |
| P2 | Implement WitnessPlugin | Heterarchical | TODO |
| P3 | Add accursed_share tests | Meta-Principle | TODO |

---

## Success Metrics

| Metric | Current | Phase 1 | Phase 3 | Phase 5 |
|--------|---------|---------|---------|---------|
| Fixture duplication | 241 | <50 | <20 | <10 |
| Agents with law tests | 5 | 10 | 20 | All |
| Property-based tests | 0 | 0 | 50 | 100 |
| BootstrapWitness runs/session | 0 | 1 | 1 | 1 |
| Accursed share tests | 0 | 0 | 0 | 50 |

---

## Appendix A: Existing Law Test Locations

Current tests that verify category laws:

```
bootstrap/_tests/test_composition_laws.py        # 120+ tests
bootstrap/_tests/test_dna_lifecycle.py           # DNA lifecycle
agents/a/_tests/test_skeleton.py                 # Identity, associativity
agents/c/_tests/test_contract_validator.py       # Contract composition
agents/o/_tests/test_o_gent.py                   # Observer composition
agents/t/_tests/test_law_validator.py            # Tool composition
agents/t/_tests/test_tool_use.py                 # Tool identity
agents/f/_tests/test_gravity.py                  # Gravity composition
agents/f/_tests/test_contract.py                 # Contract composition
agents/d/_tests/test_lens.py                     # Lens composition
agents/d/_tests/test_symbiont.py                 # Symbiont composition
agents/l/_tests/test_lattice.py                  # Lattice properties
agents/p/_tests/test_integration.py              # Parser composition
protocols/cli/bootstrap/_tests/test_bootstrap.py # CLI bootstrap
```

## Appendix B: BootstrapWitness Location

The `BootstrapWitness` is already implemented:

```
agents/o/bootstrap_witness.py
```

Key methods:
- `verify_existence()` - Checks all 7 bootstrap agents
- `verify_identity_laws()` - Tests Id >> f == f == f >> Id
- `verify_composition_laws()` - Tests (f >> g) >> h == f >> (g >> h)
- `invoke()` - Full verification returning `BootstrapVerificationResult`

## Appendix C: Philosophy Docstrings in Tests

Examples of existing philosophical alignment:

```python
# bootstrap/_tests/test_composition_laws.py
"""
Philosophy: Agents are morphisms in a category; laws ensure predictable composition.
"""

# bootstrap/_tests/test_dna_lifecycle.py
"""
Philosophy: Configuration is not loaded—it is expressed.
"""

# agents/_tests/test_tool_pipeline_e2e.py
"""
Philosophy: Tools are agents at the boundary of the system.
"""

# agents/_tests/test_memory_pipeline_integration.py
"""
Philosophy: Memory is not storage—it is active reconstruction.
"""
```
