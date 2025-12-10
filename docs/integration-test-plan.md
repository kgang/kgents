# Integration Test Plan for kgents/impl

A comprehensive plan for extensive integration testing across the kgents implementation.

## Current State

### Test Coverage Summary

| Agent | Test Files | Integration Tests | Coverage |
|-------|-----------|-------------------|----------|
| D-gent | 15 | 3 | ~95% |
| L-gent | 14 | 3 | ~85% |
| P-gent | 12 | 2 | ~85% |
| B-gent | 10 | 2 | ~100% |
| T-gent | 9 | 2 | ~90% |
| G-gent | 9 | 3 | ~90% |
| F-gent | 8 | 2 | ~65% |
| J-gent | 6 | 4 | ~85% |
| R-gent | 5 | 1 | ~80% |
| N-gent | 5 | 0 | 40% |
| M-gent | 1 | 0 | ~95% |
| O-gent | 2 | 0 | ~95% |
| I-gent | 3 | 0 | ~85% |
| K-gent | 1 | 0 | ~50% |
| C-gent | 1 | 0 | ~30% |
| H-gent | 0 | 0 | 0% |
| Ψ-gent | 0 | 0 | 0% |

**Total**: ~2800 tests, ~20 dedicated integration test files

### Existing Integration Patterns

1. **Root-level**: `_tests/test_cross_agent_integration.py` (P × J × T)
2. **Per-agent bridges**: `*_integration.py` modules define contracts
3. **Dedicated tests**: `test_*_integration.py` validate contracts

---

## Integration Test Strategy

### Tier 1: Core Pipeline Tests (Priority: HIGH)

These test the fundamental agent composition pipelines.

#### 1.1 Parser Pipeline (P-gent as hub)
**File**: `_tests/test_parser_pipeline_integration.py`

| Test Suite | Agents | Tests |
|------------|--------|-------|
| P × G | P-gent + G-gent | Grammar-guided parsing, tongue synthesis |
| P × E | P-gent + E-gent | Error parsing, recovery strategies |
| P × B | P-gent + B-gent | Hypothesis parsing, validation |
| P × F | P-gent + F-gent | Contract parsing, prototype validation |

**Example Tests**:
```python
class TestParserGrammarIntegration:
    """P × G: Parser uses G-gent grammars."""

    async def test_pgent_with_custom_tongue(self):
        """Test P-gent parsing using G-gent synthesized tongue."""

    async def test_grammar_guided_repair(self):
        """Test P-gent repair using G-gent grammar rules."""

    async def test_tongue_evolution_affects_parsing(self):
        """Test parsing updates when G-gent evolves a tongue."""
```

#### 1.2 Factory Pipeline (J-gent as hub)
**File**: `_tests/test_factory_pipeline_integration.py`

| Test Suite | Agents | Tests |
|------------|--------|-------|
| J × F × T | J-gent + F-gent + T-gent | Prototype → compile → tool |
| J × L | J-gent + L-gent | Source registration, lineage |
| J × B | J-gent + B-gent | Budget-constrained compilation |

**Example Tests**:
```python
class TestJITPrototypePipeline:
    """J × F × T: Full prototype-to-tool pipeline."""

    async def test_prototype_to_compiled_tool(self):
        """F-gent prototype → J-gent compile → T-gent execute."""

    async def test_compilation_with_budget(self):
        """J-gent compilation respects B-gent budget."""

    async def test_compiled_source_registered(self):
        """J-gent output registered in L-gent catalog."""
```

#### 1.3 Memory Pipeline (M-gent as hub)
**File**: `_tests/test_memory_pipeline_integration.py`

| Test Suite | Agents | Tests |
|------------|--------|-------|
| M × D | M-gent + D-gent | Backend persistence |
| M × L | M-gent + L-gent | Vector-based recall |
| M × B | M-gent + B-gent | Budgeted storage/retrieval |
| M × N | M-gent + N-gent | Memory → narrative crystallization |

**Example Tests**:
```python
class TestMemoryPersistencePipeline:
    """M × D: Memory with D-gent persistence."""

    async def test_holographic_store_dgent_backend(self):
        """HolographicMemory stores via D-gent backend."""

    async def test_memory_survives_restart(self):
        """Memory persists across simulated restarts."""

    async def test_memory_budget_enforcement(self):
        """B-gent budget limits memory operations."""
```

---

### Tier 2: Cross-Domain Tests (Priority: HIGH)

These test integration across major domain boundaries.

#### 2.1 Observation Stack
**File**: `_tests/test_observation_stack_integration.py`

| Test Suite | Agents | Tests |
|------------|--------|-------|
| O × W | O-gent + W-gent | Observable → Wire emission |
| O × I | O-gent + I-gent | Observable → TUI display |
| O × B | O-gent + B-gent | VoI-aware observation |
| O × N | O-gent + N-gent | Observation → narrative |

**Example Tests**:
```python
class TestObservationWirePipeline:
    """O × W: Observations flow through wire protocol."""

    async def test_panopticon_emits_to_wire(self):
        """O-gent observations emit via W-gent wire."""

    async def test_observation_to_dashboard(self):
        """O-gent → W-gent → I-gent dashboard display."""

    async def test_voi_filters_observation(self):
        """B-gent VoI economics filters O-gent observations."""
```

#### 2.2 Narrative Stack
**File**: `_tests/test_narrative_stack_integration.py`

| Test Suite | Agents | Tests |
|------------|--------|-------|
| N × M | N-gent + M-gent | Historian + Memory |
| N × K | N-gent + K-gent | Narrative + Persona |
| N × O | N-gent + O-gent | Narrative + Observation |

**Example Tests**:
```python
class TestNarrativeMemoryIntegration:
    """N × M: Narrative crystallizes from memory."""

    async def test_historian_traces_to_memory(self):
        """N-gent Historian writes traces to M-gent."""

    async def test_bard_reads_from_memory(self):
        """N-gent Bard retrieves via M-gent holographic recall."""

    async def test_crystal_persists_via_dgent(self):
        """N-gent crystals persist through D-gent backend."""
```

#### 2.3 Economics Stack
**File**: `_tests/test_economics_stack_integration.py`

| Test Suite | Agents | Tests |
|------------|--------|-------|
| B × G | B-gent + G-gent | Syntax tax, compression economy |
| B × J | B-gent + J-gent | Shared entropy budget |
| B × M | B-gent + M-gent | Memory budget |
| B × O | B-gent + O-gent | VoI economics |
| B × L | B-gent + L-gent | Catalog economics |

**Example Tests**:
```python
class TestEconomicsGrammarIntegration:
    """B × G: Grammar operations have costs."""

    async def test_tongue_synthesis_costs_tokens(self):
        """G-gent tongue synthesis deducts from B-gent budget."""

    async def test_compression_economy_roi(self):
        """G-gent compression measured by B-gent ROI."""

    async def test_jit_efficiency_profit_sharing(self):
        """J-gent × G-gent × B-gent JIT profit allocation."""
```

---

### Tier 3: Bootstrap & Config Tests (Priority: MEDIUM)

These test the fundamental DNA/Umwelt system.

#### 3.1 DNA Lifecycle
**File**: `bootstrap/_tests/test_dna_lifecycle.py`

| Test Suite | Focus | Tests |
|------------|-------|-------|
| DNA → Agent | Config to implementation | DNA constraints affect agent behavior |
| Umwelt → Agent | Environment projection | Agent sees world through Umwelt |
| Gravity → Contract | Gravity enforces contracts | Agent operations validate against Gravity |

**Example Tests**:
```python
class TestDNAAgentLifecycle:
    """Test DNA configuration flows to agent behavior."""

    async def test_dna_constraints_enforced(self):
        """DNA EPISTEMIC_HUMILITY constraint limits claims."""

    async def test_umwelt_filters_state(self):
        """Agent sees state through Umwelt lens."""

    async def test_gravity_validates_operations(self):
        """Gravity contract validates agent operations."""
```

#### 3.2 Composition Laws
**File**: `bootstrap/_tests/test_composition_laws.py`

| Test Suite | Focus | Tests |
|------------|-------|-------|
| Identity | `id >> f == f` | Identity composition |
| Associativity | `(f >> g) >> h == f >> (g >> h)` | Associative composition |
| Functor | `fmap id == id` | Functor laws |

**Example Tests**:
```python
class TestCompositionLaws:
    """Test category theory laws hold for agent composition."""

    async def test_identity_law(self):
        """Agent >> identity == Agent."""

    async def test_associativity_law(self):
        """(A >> B) >> C == A >> (B >> C)."""

    async def test_functor_preservation(self):
        """fmap preserves composition structure."""
```

---

### Tier 4: End-to-End Tests (Priority: MEDIUM)

These test complete user scenarios.

#### 4.1 Agent Creation Lifecycle
**File**: `_tests/test_agent_creation_e2e.py`

```python
class TestAgentCreationLifecycle:
    """End-to-end: spec → DNA → implementation → execution."""

    async def test_spec_to_running_agent(self):
        """
        1. Read spec from spec/{agent}
        2. Create DNA from spec constraints
        3. Build implementation with Umwelt
        4. Execute agent and validate behavior
        """

    async def test_agent_evolution_lifecycle(self):
        """
        1. Create initial agent
        2. E-gent evolves specification
        3. Re-compile with J-gent
        4. Validate evolution preserved semantics
        """
```

#### 4.2 Tool Pipeline Lifecycle
**File**: `_tests/test_tool_pipeline_e2e.py`

```python
class TestToolPipelineLifecycle:
    """End-to-end: prototype → compile → execute → observe."""

    async def test_prototype_to_execution(self):
        """
        1. F-gent creates prototype
        2. J-gent compiles to agent
        3. T-gent executes as tool
        4. O-gent observes execution
        5. N-gent records narrative
        """
```

#### 4.3 Memory Recall Lifecycle
**File**: `_tests/test_memory_recall_e2e.py`

```python
class TestMemoryRecallLifecycle:
    """End-to-end: store → persist → recall → narrate."""

    async def test_memory_full_lifecycle(self):
        """
        1. M-gent stores experience
        2. D-gent persists to backend
        3. L-gent indexes for search
        4. M-gent recalls via holographic query
        5. N-gent Bard creates narrative
        """
```

---

### Tier 5: Gap Coverage Tests (Priority: HIGH)

These specifically address identified gaps.

#### 5.1 H-gent Habituation
**File**: `h/_tests/test_h_gent.py`

```python
class TestHGentCore:
    """H-gent habituation tests (currently missing)."""

    async def test_habit_formation(self):
        """Test habit forms from repeated actions."""

    async def test_habit_decay(self):
        """Test habits decay without reinforcement."""

    async def test_habit_M_integration(self):
        """H-gent habits persist via M-gent."""
```

#### 5.2 C-gent Composition
**File**: `c/_tests/test_c_gent_composition.py`

```python
class TestCGentComposition:
    """C-gent composition tests (currently minimal)."""

    async def test_agent_as_morphism(self):
        """Agents compose as morphisms."""

    async def test_functor_mapping(self):
        """Functors map between agent categories."""

    async def test_monad_sequencing(self):
        """Monadic agents sequence correctly."""
```

#### 5.3 K-gent Persona
**File**: `k/_tests/test_k_gent_integration.py`

```python
class TestKGentIntegration:
    """K-gent persona integration (currently minimal)."""

    async def test_persona_with_memory(self):
        """K-gent persona persists via M-gent."""

    async def test_persona_in_narrative(self):
        """K-gent appears in N-gent narratives."""

    async def test_persona_dialogue(self):
        """K-gent maintains dialogue consistency."""
```

---

## Implementation Phases

### Phase 1: Foundation (Est. ~150 tests)

| File | Tests | Priority |
|------|-------|----------|
| `test_parser_pipeline_integration.py` | 30 | HIGH |
| `test_factory_pipeline_integration.py` | 30 | HIGH |
| `test_memory_pipeline_integration.py` | 30 | HIGH |
| `test_dna_lifecycle.py` | 30 | MEDIUM |
| `test_composition_laws.py` | 30 | MEDIUM |

### Phase 2: Cross-Domain (~120 tests)

| File | Tests | Priority |
|------|-------|----------|
| `test_observation_stack_integration.py` | 30 | HIGH |
| `test_narrative_stack_integration.py` | 30 | HIGH |
| `test_economics_stack_integration.py` | 30 | HIGH |
| H-gent core tests | 30 | HIGH |

### Phase 3: End-to-End (~90 tests)

| File | Tests | Priority |
|------|-------|----------|
| `test_agent_creation_e2e.py` | 30 | MEDIUM |
| `test_tool_pipeline_e2e.py` | 30 | MEDIUM |
| `test_memory_recall_e2e.py` | 30 | MEDIUM |

### Phase 4: Gap Coverage (~90 tests)

| File | Tests | Priority |
|------|-------|----------|
| C-gent composition tests | 30 | MEDIUM |
| K-gent integration tests | 30 | MEDIUM |
| Ψ-gent integration tests | 30 | LOW |

---

## Test Patterns & Conventions

### File Organization

```
impl/claude/agents/
├── _tests/
│   ├── test_cross_agent_integration.py    # Existing P×J×T
│   ├── test_parser_pipeline_integration.py # NEW
│   ├── test_factory_pipeline_integration.py # NEW
│   ├── test_memory_pipeline_integration.py  # NEW
│   ├── test_observation_stack_integration.py # NEW
│   ├── test_narrative_stack_integration.py   # NEW
│   ├── test_economics_stack_integration.py   # NEW
│   ├── test_agent_creation_e2e.py           # NEW
│   ├── test_tool_pipeline_e2e.py            # NEW
│   └── test_memory_recall_e2e.py            # NEW
├── {agent}/
│   └── _tests/
│       └── test_{agent}_integration.py      # Per-agent integration
└── bootstrap/
    └── _tests/
        ├── test_dna_lifecycle.py            # NEW
        └── test_composition_laws.py         # NEW
```

### Naming Conventions

| Pattern | Meaning |
|---------|---------|
| `test_{a}_{b}_integration.py` | A × B bilateral integration |
| `test_{domain}_stack_integration.py` | Multi-agent domain stack |
| `test_{scenario}_e2e.py` | End-to-end scenario |
| `test_{agent}_lifecycle.py` | Agent lifecycle tests |

### Async Pattern

```python
import pytest

class TestSomeIntegration:
    @pytest.fixture
    async def setup_agents(self):
        """Setup agents for integration tests."""
        agent_a = await create_agent_a()
        agent_b = await create_agent_b()
        return agent_a, agent_b

    @pytest.mark.asyncio
    async def test_agents_compose(self, setup_agents):
        """Test A >> B composition."""
        agent_a, agent_b = setup_agents
        composed = agent_a >> agent_b
        result = await composed.invoke(input_data)
        assert result.success
```

### Mock Patterns

```python
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_dgent_backend():
    """Mock D-gent backend for M-gent tests."""
    backend = AsyncMock()
    backend.store.return_value = "stored"
    backend.retrieve.return_value = {"data": "test"}
    return backend

@pytest.fixture
def mock_budget():
    """Mock B-gent budget for constrained tests."""
    budget = MagicMock()
    budget.available = 1000
    budget.deduct = MagicMock(return_value=True)
    return budget
```

---

## Success Criteria

### Metrics

| Metric | Target |
|--------|--------|
| Integration test files | +15 new files |
| Integration tests | +450 new tests |
| Cross-agent coverage | All 17 agent pairs tested |
| E2E scenarios | 5+ complete scenarios |
| Bootstrap tests | DNA → Agent lifecycle covered |

### Coverage Goals

| Domain | Current | Target |
|--------|---------|--------|
| Parser pipeline | 80% | 95% |
| Factory pipeline | 75% | 95% |
| Memory pipeline | 60% | 90% |
| Observation stack | 40% | 85% |
| Narrative stack | 30% | 80% |
| Economics stack | 70% | 90% |
| Bootstrap lifecycle | 50% | 85% |

---

## Next Steps

1. **Create directory structure** for new integration test files
2. **Implement Phase 1** parser/factory/memory pipeline tests
3. **Add fixtures** for common integration scenarios
4. **Run coverage analysis** to identify specific gaps
5. **Iterate** based on test failures and coverage reports
