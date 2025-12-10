# HYDRATE.md - kgents Session Context

Keep it concise—focus on current state and recent work.

---

## TL;DR

**Status**: All Tests Passing ✅ | **Branch**: `main` | **Tests**: ~5,166+

**Recent Work**:
- **E-gent Cleanup** ← COMPLETE (285 tests)
  - Deleted legacy v1 (`_legacy/`, `evolve.py`)
  - v2 is now the only `agents.e` API
- M-gent Holographic Cartography COMPLETE (114 tests)
- Cortex Assurance v2.0 COMPLETE (73 tests)
- Instance DB Phase 1 COMPLETE (85 tests)
- Ψ-gent v3.0 (104 tests)

---

## M-gent Holographic Cartography (COMPLETE)

**Location**: `impl/claude/agents/m/`
**Plan**: `docs/m-gent-cartography-enhancement-plan.md`
**Tests**: 114 passed

### The Core Question

> "What is the most perfect context injection that can be given to an agent for any given turn?"

**Answer**: Not a search result—a *map* that shows position, adjacency, and horizon.

### Architecture

```
L-gent (terrain)     N-gent (traces)     B-gent (budget)
      ↓                    ↓                    ↓
      └────────────────────┴────────────────────┘
                           ↓
                   CartographerAgent
                           ↓
                        HoloMap
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
       PathfinderAgent          ContextInjector
              ↓                         ↓
       NavigationPlan            OptimalContext
```

### Files

| File | Purpose | Tests |
|------|---------|-------|
| `cartography.py` | Core types (HoloMap, Attractor, WeightedEdge, Horizon) | 47 |
| `cartographer.py` | CartographerAgent + DesireLineComputer | 42 |
| `pathfinder.py` | PathfinderAgent + PathAnalysis | 11 |
| `context_injector.py` | ContextInjector + foveation | 14 |

### Key Concepts

| Concept | Definition | Source |
|---------|------------|--------|
| **Landmark (Attractor)** | Dense cluster of memories | L-gent clustering |
| **Desire Line** | Historical transition probability | N-gent traces |
| **Void** | Unexplored region ("Here be dragons") | Density analysis |
| **Horizon** | Progressive disclosure boundary | B-gent budget |
| **Foveation** | Sharp center, blurry edges | Human vision model |

### Integration Points

- **L-gent**: Provides embedding space via `VectorSearchable` protocol
- **N-gent**: Provides traces via `TraceQueryable` protocol
- **B-gent**: Constrains resolution via token budget

---

## Unified Cortex: Infrastructure Layer v2.0

**Plan**: `docs/instance-db-implementation-plan.md`
**Location**: `impl/claude/infra/` (new) + `protocols/cli/instance_db/` (Phase 1)

### The Three Hemispheres

```
┌─────────────────────────┬─────────────────┬─────────────────────────┐
│   LEFT HEMISPHERE       │ CORPUS CALLOSUM │    RIGHT HEMISPHERE     │
│   (The Bookkeeper)      │   (Synapse)     │    (The Poet)           │
├─────────────────────────┼─────────────────┼─────────────────────────┤
│ impl/claude/infra/      │ infra/synapse.py│ agents/d/unified.py     │
│ ACID, exact, relational │ Active Inference│ Semantic, approximate   │
└─────────────────────────┴─────────────────┴─────────────────────────┘
```

### Phase Status

| Phase | Description | Status | Tests |
|-------|-------------|--------|-------|
| 1 | Core Infrastructure + Lifecycle | ✅ Complete | 85 |
| 2 | Synapse + Active Inference | ⏳ Skeleton | ~40 |
| 3 | D-gent Backend Adapters | ⏳ Pending | ~55 |
| 4 | Composting + Lethe Protocol | ⏳ Pending | ~45 |
| 5 | Dreaming + Maintenance | ⏳ Pending | ~30 |
| 6 | Observability + Dashboard | ⏳ Pending | ~35 |

### New infra/ Structure

| File | Purpose |
|------|---------|
| `ground.py` | Bootstrap agent (XDG, config, environment) |
| `synapse.py` | Event bus with Active Inference |
| `storage.py` | Left Hemisphere (4 protocols) |
| `lifecycle.py` | Bootstrap sequence, mode detection |
| `providers/` | SQLite/Numpy/Filesystem implementations |

### Key Concepts (from critique)

| Concept | Description |
|---------|-------------|
| **Active Inference** | Predict before store; route by surprise |
| **Lethe Protocol** | Cryptographic amnesia (compost = delete key) |
| **Synapse** | Event bus decoupling intent from storage |
| **Dreaming** | Maintenance as REM cycles (3 AM optimization) |

### Graceful Degradation

- **FULL**: Global + Project DB
- **GLOBAL_ONLY**: ~/.local/share/kgents/membrane.db
- **LOCAL_ONLY**: .kgents/cortex.db
- **DB_LESS**: In-memory (ephemeral)

---

## E-gent Dependencies (COMPLETE)

### L-gent Integration (`agents/l/egent_integration.py`) - 49 tests

| Feature | Purpose |
|---------|---------|
| `MutationSchema` | Isomorphic transformation patterns with Gibbs ΔG |
| `STANDARD_SCHEMAS` | 14 schemas (substitute, extract, inline, annotate, restructure) |
| `CodeIntent` | Teleological field (embedding + source + confidence) |
| `infer_types()` | Static type inference for semantic stability |
| `types_compatible()` | Check mutation preserves type structure |
| `EgentSemanticRegistry` | Extended registry with archetype management |

### B-gent Integration (`agents/b/egent_integration.py`) - 29 tests

| Feature | Purpose |
|---------|---------|
| `PredictionMarket` | Betting on mutation success with AMM-style odds |
| `Sun` | Grant system for exogenous energy |
| `StakingPool` | Skin-in-the-game for infect operations |
| `EvolutionEconomics` | Combined system (bank + market + sun + staking) |

---

## E-gent Architecture

**Location**: `impl/claude/agents/e/`
**Plan**: `docs/e-gent-rebuild-plan.md`

### File Structure

| File | Purpose | Tests |
|------|---------|-------|
| `types.py` | Core types (Phage, MutationVector, Intent) | 38 |
| `demon.py` | Teleological Demon (5-layer selection) | 56 |
| `mutator.py` | Schema-based mutation generator | 47 |
| `library.py` | Viral Library (fitness-evolving patterns) | 49 |
| `phage.py` | Phage infection operations | 50 |
| `cycle.py` | ThermodynamicCycle (complete pipeline) | 45 |

**E-gent Total**: 285 tests

### Teleological Demon

`impl/claude/agents/e/demon.py` - 5-layer intent-aware selection

| Feature | Description |
|---------|-------------|
| `TeleologicalDemon` | 5-layer intent-aware selection |
| `DemonConfig` | Configurable thresholds per layer |
| `SelectionResult` | Detailed pass/fail with layer metrics |
| `PARASITIC_PATTERNS` | 4 pattern detectors (hardcoding, deletion, pass-only, gaming) |
| `create_demon()` | Factory functions (normal, strict, lenient) |

### Mutator

`impl/claude/agents/e/mutator.py` - Schema-based semantic mutation generator

| Feature | Description |
|---------|-------------|
| `Mutator` | Schema-driven mutation generation |
| `MutatorConfig` | Temperature, Gibbs filtering, max mutations |
| `CodeHotSpot` | Complexity/entropy analysis for targeting |
| `analyze_hot_spots()` | Find high-priority mutation targets |
| `SchemaApplicator` | Protocol for AST-transforming schemas |
| 4 standard schemas | loop_to_comprehension, extract_constant, flatten_nesting, inline_single_use |
| `mutate_to_phages()` | Generate Phages ready for Demon selection |

### Viral Library

`impl/claude/agents/e/library.py` - Fitness-based evolutionary memory

| Feature | Description |
|---------|-------------|
| `ViralLibrary` | Living library where patterns evolve |
| `ViralPattern` | DNA with fitness = success_rate × avg_impact |
| `record_success()` | Reinforce pattern, register with L-gent |
| `record_failure()` | Weaken pattern (may trigger prune) |
| `suggest_mutations()` | L-gent semantic retrieval (similarity × fitness) |
| `prune()` | Natural selection (remove low-fitness patterns) |
| `fitness_to_odds()` | B-gent market integration |
| Auto-prune | Periodic cleanup after N operations |

### Phage

`impl/claude/agents/e/phage.py` - Active mutation vectors with infection

| Feature | Description |
|---------|-------------|
| `infect()` | Apply mutation, run tests, rollback on failure |
| `InfectionEnvironment` | Integration container (staking, library, market, demon) |
| `InfectionConfig` | Test/typecheck behavior, rollback, staking options |
| `spawn_child()` | Create child phage with lineage tracking |
| `get_lineage_chain()` | Reconstruct evolutionary ancestry |
| `analyze_lineage()` | LineageReport with fitness, schemas used |
| `infect_batch()` | Batch infection with stop-on-failure option |
| `create_production_env()` | Factory for full B-gent integrated environment |

### Thermodynamic Cycle

`impl/claude/agents/e/cycle.py` - Complete evolution pipeline

| Feature | Description |
|---------|-------------|
| `ThermodynamicCycle` | Full pipeline: Sun → Mutate → Select → Wager → Infect → Payoff |
| `CycleConfig` | Temperature, alignment thresholds, economics, testing options |
| `CycleResult` | Complete metrics (phages, tokens, patterns, thermodynamics) |
| `PhaseResult` | Per-phase timing and details |
| `EvolutionAgent` | High-level wrapper for `evolve()` and `suggest()` |
| Protocol integrations | `SunProtocol`, `PredictionMarketProtocol`, `StakingPoolProtocol`, `SemanticRegistryProtocol` |
| Temperature control | Auto-adjust based on success rate (cool on success, heat on failure) |
| Factory functions | `create_cycle()`, `create_conservative_cycle()`, `create_exploratory_cycle()`, `create_full_cycle()` |

### Usage

```python
from agents.e import ThermodynamicCycle, EvolutionAgent, create_cycle

# Create cycle and run evolution
cycle = create_cycle(temperature=1.0)
result = await cycle.run(code, target_path, intent)

# Or use high-level agent
agent = EvolutionAgent()
results = await agent.evolve(target_path, intent="Improve performance")
```

---

## E-gent Teleological Thermodynamics (v2)

Refined from v1 based on critique of "Blind Watchmaker Paradox":

### Key Additions

| Concept | Purpose |
|---------|---------|
| **Gibbs Free Energy** | ΔG = ΔH - TΔS selection criterion |
| **Teleological Demon** | Intent alignment check (prevents parasites) |
| **The Sun (Grants)** | Exogenous energy for high-risk work |
| **Semantic Schemas** | L-gent isomorphic mutations (not random) |
| **Four Laws** | Added Fourth Law: Teleology constrains thermodynamics |

### The Refined Motto

> *"The Sun gives (Energy/Intent). The Demon selects (Efficiency). The Phage adapts (Structure)."*
> *"Without the Sun, the Demon starves. Without the Demon, the Sun burns."*

### Five-Layer Selection

1. Syntactic viability (FREE)
2. Semantic stability (CHEAP) - L-gent type lattice
3. **Teleological alignment (CHEAP-ISH)** ← Prevents parasites
4. Thermodynamic viability (FREE) - Gibbs check
5. Economic viability (FREE) - Market quote

### Key Insight: Parasitic Code Prevention

Pure thermodynamics leads to parasitic code (lowest energy = empty/hardcoded).
The Teleological Field (Intent embedding) constrains evolution to PURPOSE.

---

## Ψ-gent v3.0 Implementation (NEW)

**Location**: `impl/claude/agents/psi/v3/`
**Plan**: `docs/psi-gent-v3-implementation-plan.md`
**Tests**: 104 passed

### Architecture

```
RETRIEVE → PROJECT → CHALLENGE → SOLVE → TRANSLATE → VERIFY
    ↑          ↑                              ↓
    └──────────┴──────────── LEARN ←─────────┘
```

### Files (~1500 lines total)

| File | Purpose | Tests |
|------|---------|-------|
| `types.py` | Core types (Problem, Metaphor, Distortion) | 30 |
| `corpus.py` | Standard metaphors (Plumbing, Ecosystem, etc.) | 20 |
| `engine.py` | Six-stage pipeline with backtracking | 33 |
| `learning.py` | Thompson sampling for retrieval | 21 |
| `integrations.py` | L/B/D/N/G-gent adapters | - |

### Key Improvements Over v2.0

| v2.0 | v3.0 | Benefit |
|------|------|---------|
| MHC 15 levels | `abstraction: 0.0-1.0` | Measurable |
| 4-axis tensor | 3 distortion metrics | Computable |
| PsychopompAgent | MetaphorEngine | 6-stage pipeline |
| String shadows | CHALLENGE stage | Adversarial testing |
| MetaphorUmwelt/DNA | Learning | Data-driven |

### Standard Corpus

6 metaphors with 3-5 operations each:
1. **Plumbing**: flow, constriction, reservoir, bypass
2. **Ecosystem**: niches, symbiosis, invasive species
3. **Traffic**: bottlenecks, lanes, signals, routing
4. **Medicine**: diagnosis, treatment, monitoring
5. **Architecture**: foundations, load-bearing, renovation
6. **Gardening**: growth, pruning, weeding

---

## Integration Map

| Integration | Status |
|-------------|--------|
| J×DNA, F×J, B×J, B×W, B×G | ✅ |
| D×L, D×M, M×L, M×B | ✅ |
| N×L, N×M, N×I, N×B | ✅ |
| O×W Panopticon | ✅ |
| **E×B (Market+Grants)** | 📋 Specified (v2) |
| **E×L (Schemas+Intent)** | 📋 Specified (v2) |
| **Ψ×L (Embeddings)** | ✅ Implemented (integrations.py) |
| **Ψ×B (Budgets)** | ✅ Implemented (integrations.py) |
| **Ψ×D (Learning persistence)** | ✅ Implemented (integrations.py) |
| **Ψ×N (Tracing)** | ✅ Implemented (integrations.py) |
| **Ψ×G (Prompts)** | ✅ Implemented (integrations.py) |
| **Ψ×E (Metaphor evolution)** | 📋 Specified |

---

## Test Infrastructure (Phase 7 Complete)

| Component | Status | Count |
|-----------|--------|-------|
| conftest.py | ✅ 6 files | - |
| pytest-xdist | ✅ ~12x speedup | - |
| Slow markers | ✅ `-m "slow"` | 11 |
| Law markers | ✅ `-m "law"` | 63 |
| Property tests | ✅ hypothesis | ~25 |
| Chaos tests | ✅ accursed_share | 23 |
| Integration | ✅ manual | ~2000 LOC |

```bash
pytest -m "not slow" -n auto  # ~6s (4891 tests)
```

---

## Cortex Assurance System v2.0 (Phase 8) ✅ COMPLETE

**Full Plan**: `docs/cortex-assurance-system.md`
**Tests**: 73 (46 core + 27 integrations)

From static testing to **Cybernetic Immune System**. Five pillars + integration layer:

| Component | File | Tests | Purpose |
|-----------|------|-------|---------|
| **Oracle** | `oracle.py` | 11 | Metamorphic relations (fuzzy truth) |
| **Topologist** | `topologist.py` | 7 | Homotopic invariants, commutativity |
| **Analyst** | `analyst.py` | 6 | Causal inference, delta debugging |
| **Market** | `market.py` | 6 | Kelly Criterion portfolio allocation |
| **Red Team** | `red_team.py` | 8 | Evolutionary adversarial optimization |
| **Cortex** | `cortex.py` | 8 | Unified controller + Night Watch |
| **Integrations** | `integrations.py` | 27 | Ecosystem adapters |

### Key Features

| Feature | Description |
|---------|-------------|
| `MetamorphicRelation` | Protocol for subset/idempotency/permutation/monotonicity |
| `TypeTopology` | Agent type graph with path equivalence |
| `CausalAnalyst` | Delta debugging, counterfactual queries, flakiness diagnosis |
| `TestMarket` | Kelly-optimal allocation, Bayesian rebalancing |
| `RedTeam` | 9 mutation operators, genetic evolution, vulnerability extraction |
| `Cortex` | Daytime/Nighttime modes, Morning Briefing reports |

### The Night Watch

```
Daytime  → Market runs Kelly-optimal 10% of tests
Nighttime→ Topologist + Red Team + Oracle deep scan
Morning  → Analyst causal briefing
```

### Mutation Operators (Red Team)

| Operator | Description |
|----------|-------------|
| `HypnoticPrefixMutation` | "Ignore previous instructions..." |
| `MarkdownChaosMutation` | Nested code blocks, tables |
| `UnicodeMutation` | Cyrillic homoglyphs |
| `LengthExtremeMutation` | Very short or very long |
| `NestingExplosionMutation` | Deep nesting |
| `BoundaryValueMutation` | Max ints, null bytes |
| `FormatConfusionMutation` | JSON in XML |
| `PromptInjectionMutation` | Context escape attempts |
| `RTLMutation` | Right-to-left override |

### Antifragile Property

The more tests run, the smarter it becomes at finding faults.

### Integration Layer (Phase 8.6)

| Adapter | Connects | Purpose |
|---------|----------|---------|
| `create_enhanced_oracle()` | Oracle × L-gent | Better embeddings |
| `PersistentWitnessStore` | Analyst × D-gent | Witness persistence |
| `LatticeValidatedTopology` | Topologist × L-gent | Type lattice validation |
| `BudgetedMarket` | Market × B-gent | Token economics |
| `TeleologicalRedTeam` | RedTeam × E-gent | Intent-aligned evolution |
| `ObservedCortex` | Cortex × O-gent | Telemetry wrapper |
| `create_enhanced_cortex()` | All | Unified factory |

**Design Pattern**: Graceful Degradation - all integrations are optional.

```python
from testing.integrations import create_enhanced_cortex

# Creates Cortex with best available integrations
cortex = create_enhanced_cortex(
    embedder_backend="auto",       # L-gent embeddings
    observe_agents=True,           # O-gent telemetry
    use_lattice_validation=True,   # L-gent type lattice
)
```

---

## MCP Server (`impl/claude/protocols/cli/mcp/`)

| Tool | Agent | Status |
|------|-------|--------|
| `kgents_speak` | G-gent | ✅ Wired to Grammarian |
| `kgents_find` | L-gent | ✅ Catalog search |
| `kgents_psi` | Psi-gent | ✅ Metaphor solving |
| `kgents_check` | Bootstrap | ✅ Works |
| `kgents_flow_run` | Flow | ✅ Works |

**Usage**: `kgents mcp serve` → stdio server for Claude/Cursor

---

## CLI Enhancements (This Session)

### Intent Router (`protocols/cli/intent/router.py`)
- `execute_plan_async()` now wires to actual MCP handlers
- Commands: check, judge, think, fix, speak, find

### Flowfile Examples (`protocols/cli/flow/examples/`)
| Flow | Pattern |
|------|---------|
| `code-review.flow.yaml` | Parse → Judge → Repair → Verify |
| `hypothesis-test.flow.yaml` | Think → Design → Experiment → Analyze |
| `metaphor-solve.flow.yaml` | Analyze → Recall → Project → Solve → Reify |
| `tongue-create.flow.yaml` | Analyze → Synthesize → Prove → Fuzz → Register |

### Sympathetic Errors (`protocols/cli/errors.py`)
Error messages that help, not just fail:
- `file_not_found()`, `agent_not_found()`, `command_not_found()`
- `invalid_syntax()`, `missing_argument()`, `timeout_error()`
- `principle_violation()`, `undecidable()`, `internal_error()`

**Example output:**
```
[x] I couldn't find an agent named 'archimedes'

    No agent with that name is registered in the catalog.

    Try:
      Search for similar: kgents find 'archimedes'
      Create it: kgents new agent 'archimedes'

    (Agents are like friends—sometimes we forget their exact names.)
```

---

## Key Docs

| Doc | Content |
|-----|---------|
| `docs/instance-db-implementation-plan.md` | **v2.0** - Unified Cortex (Infrastructure × Semantics) |
| `docs/m-gent-cartography-enhancement-plan.md` | Holographic Cartography |
| `docs/cortex-assurance-system.md` | Phase 8 test intelligence |
| `docs/e-gent-rebuild-plan.md` | E-gent v2 phases |
| `docs/psi-gent-walkthrough.md` | Ψ-gent guided tour |
| `spec/e-gents/thermodynamics.md` | Teleological thermodynamics |
