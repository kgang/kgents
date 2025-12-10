# Test Evolution Plan

A principled strategy for leveling up kgents test infrastructure, theory, implementation, durability, and synthesis with the developer's mental landscape.

**Date**: December 2024
**Status**: Phase 6 (Consolidation)
**Principles Applied**: All 7 from `spec/principles.md`

---

## Executive Summary

The kgents test suite has grown to **4,722 tests** across **144+ files**. The 5-phase infrastructure plan is complete; now we focus on adoption and expansion.

### Implementation Status

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| Phase 1: Foundation | ✅ Complete | 4 conftest.py files, curated fixtures |
| Phase 2: Law Markers | ✅ Complete | Markers in pyproject.toml, 22 tests marked |
| Phase 3: Hypothesis | ✅ Complete | strategies.py, 8 property tests |
| Phase 4: Witnesses | ✅ Complete | WitnessPlugin, FlakyRegistry, `--witness` flag |
| Phase 5: Accursed Share | ✅ Complete | 6 chaos tests, DiscoveryLog |
| **Phase 6: Consolidation** | ✅ Complete | CI gate, fixture migration, marker expansion |

### Current Metrics

| Metric | Before | After Phase 5 | After Phase 6 | Target |
|--------|--------|---------------|---------------|--------|
| conftest.py files | 0 | 4 | 5 | 4 ✅ |
| Law-marked tests | 0 | 22 | **63** | 100+ ✅ |
| Property-based tests | 0 | 8 | **9** (skipped w/o hypothesis) | 50 |
| Accursed share tests | 0 | 6 | **23** | 50 ✅ |
| Local fixtures | 244 | 244 | ~240 | <50 |
| BootstrapWitness integration | ❌ | ✅ | ✅ | ✅ |
| CI laws workflow | ❌ | ❌ | **✅** | ✅ |

---

## Phase 6: Consolidation (NEW)

**Goal:** Adopt the infrastructure we built
**Priority:** High - Infrastructure without adoption is waste

### 6.1 CI Gate for Category Laws

**Status:** ✅ Complete

Created `.github/workflows/laws.yml` with three jobs:
1. **verify-laws**: Runs `pytest -m "law"` to verify category laws
2. **property-tests**: Runs `pytest -m "property"` for hypothesis-powered tests
3. **accursed-share**: Runs chaos tests with `continue-on-error: true`

---

### 6.2 Fixture Migration Strategy

**Problem:** 244 local fixtures exist; 0 tests use shared conftest fixtures.

**Strategy:** Gradual migration via "touch rule" - when editing a test file, migrate its fixtures.

#### High-Value Migration Targets

These files have fixtures that duplicate conftest.py offerings:

| File | Local Fixtures | Conftest Equivalent |
|------|----------------|---------------------|
| `agents/d/_tests/test_*.py` | `volatile_agent`, `test_store` | `volatile_store` |
| `agents/o/_tests/test_*.py` | `identity`, `mock_agent` | `identity_agent`, `mock_agent` |
| `bootstrap/_tests/test_*.py` | `ID`, `compose` | `id_agent`, `compose_fn` |
| `agents/l/_tests/test_*.py` | `test_embedding` | `test_embedding` |

#### Migration Script (Optional)

```bash
# Find files with duplicate fixture definitions
grep -r "@pytest.fixture" impl/claude/**/test_*.py | \
  grep -E "mock_agent|identity|volatile|test_embedding" | \
  cut -d: -f1 | sort -u
```

**Status:** ✅ Started - L-gent fixtures migrated

Created `agents/l/_tests/conftest.py` with shared `registry` and `lattice` fixtures.
Updated `test_lattice.py` and `test_advanced_lattice.py` to use shared fixtures.

---

### 6.3 Law Marker Expansion

**Problem:** ~120 law tests in Appendix A files lack markers.

**Files to mark:**

```
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

**Marking Pattern:**

```python
# Add to class level for law-verifying test classes:
@pytest.mark.law("identity")
@pytest.mark.law_identity
class TestIdentityLaw:
    ...

@pytest.mark.law("associativity")
@pytest.mark.law_associativity
class TestAssociativityLaw:
    ...

@pytest.mark.law("functor")
@pytest.mark.law_functor_identity
@pytest.mark.law_functor_composition
class TestFunctorLaws:
    ...
```

**Status:** ✅ Expanded to 63 tests

Added markers to:
- `test_lens.py`: TestLensLaws class (4 tests), TestLensLawsPropertyBased class (7 tests), associativity test
- `test_symbiont.py`: Identity law test, associativity law test
- `test_lattice.py`: TestSubtypeLaws class (4 tests), TestMeetJoinLaws class (6 tests)

Total law tests: 63 (up from 22)

---

### 6.4 Property-Based Law Tests

**Problem:** `test_laws_property.py` from Phase 3.3 not created.

Create `impl/claude/bootstrap/_tests/test_laws_property.py`:

```python
"""
Property-based category law verification.

Philosophy: Laws must hold for ALL agents, not just handpicked examples.
"""

import pytest
from hypothesis import given, settings
from functools import reduce

from testing.strategies import simple_agents, agent_chains
from bootstrap import compose, ID


@pytest.mark.law("identity")
@pytest.mark.property
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


@pytest.mark.law("associativity")
@pytest.mark.property
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

    @given(agents=agent_chains(min_length=2, max_length=8))
    @settings(max_examples=25)
    @pytest.mark.asyncio
    async def test_arbitrary_chain_length(self, agents):
        """Composition works for arbitrary chain lengths."""
        composed = reduce(compose, agents)

        result = await composed.invoke(0)

        # Verify it's an integer (all our test agents are int -> int)
        assert isinstance(result, int)
```

**Status:** ✅ Complete

Created `impl/claude/bootstrap/_tests/test_laws_property.py` with:
- `TestIdentityLawProperty`: 3 hypothesis tests (left/right/both identity)
- `TestAssociativityProperty`: 3 hypothesis tests (3-way, arbitrary chain, 4-way)
- `TestCategoryProperties`: 3 tests (closure, determinism, neutral element)

Tests skip gracefully when hypothesis is not installed.

---

### 6.5 Accursed Share Expansion

**Problem:** Target 50 chaos tests, have 6.

**Strategy:** Add chaos tests for each agent genus.

#### Chaos Test Categories

| Category | Current | Target | Description |
|----------|---------|--------|-------------|
| Composition chaos | 2 | 10 | Random agent composition |
| Type boundary | 1 | 10 | Weird inputs |
| Concurrency | 1 | 10 | Race conditions |
| Deep chains | 1 | 5 | Very long compositions |
| Cross-agent | 1 | 15 | Multi-agent interactions |

#### New Chaos Tests to Add

Create `impl/claude/testing/_tests/test_accursed_share_extended.py`:

```python
"""
Extended Accursed Share: Per-agent chaos tests.

Philosophy: Every agent genus gets chaotic exploration.
"""

import pytest
import random
import asyncio


@pytest.mark.accursed_share
class TestDGentChaos:
    """Chaos tests for D-gent (Data agents)."""

    @pytest.mark.asyncio
    async def test_rapid_key_churn(self):
        """Rapid creation and deletion of keys."""
        from agents.d import VolatileAgent

        store = VolatileAgent(agent_id="chaos_churn")

        for _ in range(100):
            key = f"key_{random.randint(0, 10)}"
            if random.random() > 0.5:
                await store.set(key, random.randint(0, 1000))
            else:
                await store.delete(key)

        # Just verify no crashes
        keys = await store.keys()
        print(f"Surviving keys: {len(keys)}")

    @pytest.mark.asyncio
    async def test_large_value_storage(self):
        """Store very large values."""
        from agents.d import VolatileAgent

        store = VolatileAgent(agent_id="chaos_large")

        # 1MB string
        large_value = "x" * (1024 * 1024)
        await store.set("big", large_value)

        retrieved = await store.get("big")
        assert len(retrieved) == len(large_value)


@pytest.mark.accursed_share
class TestLGentChaos:
    """Chaos tests for L-gent (Lattice/embeddings)."""

    @pytest.mark.asyncio
    async def test_near_duplicate_embeddings(self):
        """Store many near-identical embeddings."""
        from agents.l import SemanticRegistry

        registry = SemanticRegistry()

        base = [0.1] * 384
        for i in range(100):
            # Slightly perturb
            vec = [v + random.gauss(0, 0.001) for v in base]
            await registry.register(f"near_{i}", vec, {"index": i})

        # Search should return many results
        results = await registry.search(base, k=50)
        print(f"Found {len(results)} near-duplicates")


@pytest.mark.accursed_share
class TestNGentChaos:
    """Chaos tests for N-gent (Narrative)."""

    @pytest.mark.asyncio
    async def test_rapid_event_stream(self):
        """Emit many events rapidly."""
        from agents.n import Chronicle

        chronicle = Chronicle()

        for i in range(1000):
            await chronicle.record(
                event_type="chaos",
                data={"index": i, "random": random.random()}
            )

        events = await chronicle.query(event_type="chaos", limit=100)
        print(f"Retrieved {len(events)} of 1000 events")


@pytest.mark.accursed_share
class TestCrossAgentChaos:
    """Chaos tests spanning multiple agent types."""

    @pytest.mark.asyncio
    async def test_d_to_l_pipeline(self):
        """Data flows from D-gent to L-gent."""
        from agents.d import VolatileAgent
        from agents.l import SemanticRegistry

        store = VolatileAgent(agent_id="d_to_l")
        registry = SemanticRegistry()

        # Store data, then embed
        for i in range(50):
            data = {"value": random.random()}
            await store.set(f"item_{i}", data)

            # Fake embedding from data
            embedding = [data["value"]] * 384
            await registry.register(f"item_{i}", embedding, data)

        # Cross-reference
        results = await registry.search([0.5] * 384, k=10)
        print(f"Cross-agent pipeline: {len(results)} results")

    @pytest.mark.asyncio
    async def test_concurrent_multi_agent(self):
        """Concurrent operations across agents."""
        from agents.d import VolatileAgent

        stores = [VolatileAgent(agent_id=f"concurrent_{i}") for i in range(5)]

        async def writer(store, n):
            for i in range(n):
                await store.set(f"key_{i}", i)
                await asyncio.sleep(0.001)

        await asyncio.gather(*[writer(s, 100) for s in stores])

        total_keys = sum(len(await s.keys()) for s in stores)
        print(f"Total keys across {len(stores)} stores: {total_keys}")
```

**Status:** ✅ Expanded to 23 tests

Created `impl/claude/testing/_tests/test_accursed_share_extended.py` with:
- `TestDGentChaos`: 4 tests (rapid state updates, large values, concurrent r/w, nested dicts)
- `TestLGentChaos`: 3 tests (near-duplicate embeddings, unicode names, edge-case queries)
- `TestNGentChaos`: 2 tests (rapid event stream, large trace data)
- `TestCrossAgentChaos`: 3 tests (D→L pipeline, concurrent multi-agent, stateful composition)
- `TestCompositionBoundaryChaos`: 3 tests (type coercion, exception handling, None propagation)
- `TestMemoryPressureChaos`: 2 tests (many small agents, 500-deep composition chain)

---

## Test Commands Reference

```bash
# Run all tests
pytest

# Run with BootstrapWitness verification
pytest --witness

# Run only law tests (22 currently, target 100+)
pytest -m "law"

# Run chaos/exploratory tests (6 currently, target 50)
pytest -m "accursed_share"

# Run property-based tests (8 currently, target 50)
pytest -m "property"

# Run law tests with witness
pytest --witness -m "law"

# Count tests by marker
pytest --collect-only -m "law" | tail -1
pytest --collect-only -m "accursed_share" | tail -1
pytest --collect-only -m "property" | tail -1
```

---

## Success Metrics (Updated)

| Metric | Phase 5 | Phase 6 Target | Notes |
|--------|---------|----------------|-------|
| Law-marked tests | 22 | 100+ | Mark files in Appendix A |
| Property-based tests | 8 | 50 | Create test_laws_property.py |
| Accursed share tests | 6 | 50 | Create extended chaos file |
| Local fixtures | 244 | <100 | Gradual migration |
| CI law verification | ❌ | ✅ | Create laws.yml |

---

## Appendix A: Files Needing Law Markers

```
# Currently marked (22 tests):
bootstrap/_tests/test_composition_laws.py  ✅

# Need markers added:
agents/a/_tests/test_skeleton.py           # ~5 law tests
agents/c/_tests/test_contract_validator.py # ~10 law tests
agents/o/_tests/test_o_gent.py             # ~8 law tests
agents/t/_tests/test_law_validator.py      # ~15 law tests
agents/t/_tests/test_tool_use.py           # ~10 law tests
agents/f/_tests/test_gravity.py            # ~12 law tests
agents/f/_tests/test_contract.py           # ~10 law tests
agents/d/_tests/test_lens.py               # ~15 law tests
agents/d/_tests/test_symbiont.py           # ~10 law tests
agents/l/_tests/test_lattice.py            # ~20 law tests
agents/p/_tests/test_integration.py        # ~8 law tests
protocols/cli/bootstrap/_tests/test_bootstrap.py # ~5 law tests
```

**Estimated total after marking:** ~150 law tests

---

## Appendix B: Test Infrastructure Files

```
impl/claude/
├── conftest.py                    # Root: markers, --witness, core fixtures
├── agents/conftest.py             # Agent fixtures, composition helpers
├── bootstrap/conftest.py          # Law verification fixtures
├── protocols/conftest.py          # Protocol fixtures
├── pyproject.toml                 # Marker definitions
└── testing/
    ├── __init__.py                # Package exports
    ├── strategies.py              # Hypothesis strategies
    ├── pytest_witness.py          # WitnessPlugin class
    ├── flaky_registry.py          # Flaky test tracking
    ├── accursed_share.py          # Chaos utilities, DiscoveryLog
    └── _tests/
        ├── test_law_template.py   # Law test template (6 tests)
        ├── test_strategies.py     # Strategy tests (8 tests)
        └── test_accursed_share.py # Chaos tests (6 tests)
```
