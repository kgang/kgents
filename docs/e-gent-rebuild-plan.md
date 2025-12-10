# E-gent Rebuild Plan: From Bureaucratic to Teleological Thermodynamic

**Status**: Planning
**Date**: 2025-12-10
**Goal**: Rebuild `impl/claude/agents/e/` to faithfully implement the E-gent v2 spec

---

## Executive Summary

The current E-gent implementation (`impl/claude/agents/e/`) represents a **first-generation "bureaucratic" evolution system** with:
- Budget-based token allocation (not market-driven)
- Random/LLM hypothesis generation (not semantic schema-driven)
- Outcome memory (not viral DNA library)
- Judge-based evaluation (not thermodynamic selection)

The spec (`spec/e-gents/`) describes a fundamentally different **teleological thermodynamic system** with:
- Prediction market + grants for token economics
- Gibbs Free Energy selection criterion
- Teleological Demon for parasitic code prevention
- Viral Library with fitness-based evolution
- Phage-based mutation vectors

This rebuild requires a **complete architectural shift**, not incremental changes.

---

## Gap Analysis: Spec vs Current Implementation

### Core Concepts

| Spec Concept | Current Implementation | Gap |
|--------------|----------------------|-----|
| **Phage** (active mutation vector) | `Experiment` (passive data object) | Missing: Active behavior, lineage, odds, staking |
| **Teleological Demon** | `CodeJudge` (heuristic scorer) | Missing: 5-layer selection, intent embedding, cheap rejection |
| **Mutator** (semantic schema) | `HypothesisEngine` (LLM-based) | Missing: L-gent schemas, isomorphic transforms, Gibbs pre-filter |
| **Viral Library** | `ImprovementMemory` (outcome recording) | Missing: Fitness-based evolution, DNA propagation, pruning |
| **Prediction Market** | None (budget-based) | Completely missing |
| **Sun/Grants** | None | Completely missing |
| **Intent Embedding** | None | Completely missing |
| **Gibbs Free Energy** | None | Completely missing |

### Architecture

| Spec Architecture | Current Architecture |
|-------------------|---------------------|
| `Sun → Mutate → Select → Wager → Infect → Payoff` | `Ground → Hypothesis → Experiment → Judge → Sublate → Incorporate` |

The current architecture follows a **linear pipeline** while the spec describes a **thermodynamic cycle** with feedback loops.

### Integration Requirements

| Spec Integration | Current State |
|------------------|---------------|
| **B-gent** (CentralBank, PredictionMarket) | Minimal: `MeteredPromptBuilder` only |
| **L-gent** (SemanticRegistry, embeddings) | None |
| **D-gent** (persistent storage) | `PersistentMemoryAgent` (basic) |
| **O-gent** (observation) | None |
| **N-gent** (chronicle) | None |

---

## Rebuild Strategy

### Principle 7: Generative

The spec is the source of truth. Implementation should be **regenerable from spec**. This means:
1. Types directly mirror spec YAML types
2. Functions implement spec morphisms
3. Architecture follows spec cycle

### Principle 2: Curated

We will **not** preserve backwards compatibility with the current implementation. The old system and new system are philosophically incompatible. The current code will be removed and replaced.

### Principle 5: Composable

Each component will be a **morphism** with clear `A → B` types, composable via `>>`.

---

## Implementation Plan

### Phase 0: Foundation Types (Minimal)

Create new type system matching spec exactly:

```
impl/claude/agents/e/
├── types.py              # Core types: Phage, MutationVector, Intent, Grant
├── thermodynamics.py     # GibbsFreeEnergy, EnthalphyChange, EntropyChange
└── _tests/test_types.py  # Type tests
```

**Types from spec**:
- `MutationSchema`: Semantic transformation pattern
- `MutationVector`: Concrete mutation proposal with thermodynamic properties
- `Phage`: Self-contained evolution unit with DNA
- `Intent`: Teleological field (embedding + source + confidence)
- `Grant`: Exogenous energy from user
- `ViralPattern`: Reusable pattern with fitness
- `InfectionResult`: Success/failure of Phage application

### Phase 1: Teleological Demon (Selection)

The **heart** of E-gent v2 is cheap, intent-aware selection:

```
impl/claude/agents/e/
├── demon.py              # TeleologicalDemon: 5-layer selection
├── intent.py             # Intent: from_user, from_tests, from_structure
└── _tests/test_demon.py
```

**Key**: Layer 3 (Teleological Alignment) prevents parasitic code by checking intent embedding distance before expensive validation.

**Integration**: Requires L-gent `SemanticRegistry.embed_code_intent()` for intent embedding.

### Phase 2: Mutator (Semantic Schema)

Replace LLM-based hypothesis generation with **L-gent schema-driven mutation**:

```
impl/claude/agents/e/
├── mutator.py            # Mutator: schema-based mutation generation
├── schemas.py            # MutationSchema definitions
└── _tests/test_mutator.py
```

**Key**: Mutations are **isomorphic** (preserve type structure), not random. Pre-filtered by Gibbs viability.

**Integration**: Requires L-gent `SemanticRegistry.get_mutation_schemas()`.

### Phase 3: Prediction Market (Economics)

Replace budgets with **market-based self-regulation**:

```
impl/claude/agents/e/
├── market.py             # PredictionMarket: quote, place_bet, settle
└── _tests/test_market.py
```

**Integration**: Requires B-gent `CentralBank` for account management.

### Phase 4: Sun (Grants)

Add **exogenous energy** for high-risk architectural work:

```
impl/claude/agents/e/
├── sun.py                # Sun: issue_grant, has_active_grant, consume_grant
└── _tests/test_sun.py
```

**Key**: Without grants, the system reaches heat death (can only make safe, incremental changes).

### Phase 5: Viral Library (Evolutionary Memory)

Replace passive memory with **fitness-evolving DNA library**:

```
impl/claude/agents/e/
├── library.py            # ViralLibrary: record_success/failure, suggest_mutations, prune
└── _tests/test_library.py
```

**Key**: Patterns with high fitness reproduce; low fitness patterns die. Library **evolves**, doesn't just accumulate.

**Integration**:
- L-gent `SemanticRegistry` for semantic retrieval
- D-gent for persistence
- O-gent for birth/death rate observations

### Phase 6: Phage (Mutation Vector)

Implement **active mutation units** with behavior:

```
impl/claude/agents/e/
├── phage.py              # Phage: infect(), spawn()
└── _tests/test_phage.py
```

**Key**: Phages carry DNA and can infect codebases. Unlike `Experiment`, they have lineage tracking, staking, and odds.

### Phase 7: Thermodynamic Cycle (Integration)

Compose all components into the **teleological thermodynamic cycle**:

```
impl/claude/agents/e/
├── cycle.py              # ThermodynamicCycle: Sun → Mutate → Select → Wager → Infect → Payoff
├── evolution_v2.py       # EvolutionAgent v2 (wraps cycle)
└── _tests/test_cycle.py
```

**Morphism**: `(UserRequest, Codebase) → EvolutionReport`

### Phase 8: Safety (Self-Evolution)

Preserve and adapt existing safety mechanisms:

```
impl/claude/agents/e/
├── safety_v2.py          # SelfEvolutionAgent with thermodynamic constraints
└── _tests/test_safety_v2.py
```

**Key**: Fixed-point iteration with Gibbs convergence criterion.

### Phase 9: Cleanup

Remove obsolete files:
- `evolution.py` → replaced by `evolution_v2.py` + `cycle.py`
- `experiment.py` → replaced by `phage.py`
- `judge.py` → replaced by `demon.py`
- `memory.py` → replaced by `library.py`
- `hypothesis` logic → replaced by `mutator.py`

Preserve (adapt as needed):
- `ast_analyzer.py` (grounding.md)
- `safety.py` → `safety_v2.py`
- `parser/`, `validator.py`, `repair.py` (Layer 2 reliability)
- `preflight.py` (pre-flight checks)

---

## Integration Dependencies

### Required Before E-gent Rebuild

1. **L-gent SemanticRegistry enhancements**:
   - `get_mutation_schemas() → list[MutationSchema]`
   - `embed_text(str) → np.ndarray`
   - `embed_code_intent(str) → np.ndarray`
   - `infer_types(str) → TypeInfo`
   - `types_compatible(TypeInfo, TypeInfo) → bool`
   - `find_similar(embedding, top_k) → list[(name, similarity)]`
   - `register_archetype(name, embedding)`
   - `deregister_archetype(name)`

2. **B-gent CentralBank**:
   - `open_account(name) → Account`
   - `Account.debit(amount)`
   - `Account.credit(amount)`
   - `Account.balance`
   - `Account.is_frozen`

### Can Be Developed In Parallel

- D-gent persistence (already exists)
- O-gent observation (optional for v1)
- N-gent chronicle (optional for v1)

---

## Test Strategy

### Unit Tests (Per Phase)

Each phase includes `_tests/test_*.py` with:
- Type validation
- Morphism behavior
- Edge cases

### Integration Tests

```
_tests/
├── test_cycle_integration.py    # Full cycle test
├── test_lgent_integration.py    # L-gent integration
├── test_bgent_integration.py    # B-gent market integration
└── test_parasitic_prevention.py # Teleological demon effectiveness
```

### Property-Based Tests

For thermodynamic laws:
- Conservation of compute (tokens in = work + waste)
- Entropy increases without selection
- Gibbs viability predicts success

---

## Migration Path

### Step 1: Parallel Development

Build new system in `agents/e/v2/` while preserving existing `agents/e/`.

### Step 2: Feature Parity Test

Verify v2 can evolve the same codebase as v1 with:
- Lower token cost (market efficiency)
- Higher success rate (Demon selection)
- No parasitic code (intent alignment)

### Step 3: Cutover

- Move v2 files to `agents/e/`
- Archive v1 files to `agents/e/_legacy/`
- Update `__init__.py` exports

### Step 4: Cleanup

Remove `_legacy/` after verification period.

---

## Success Criteria

1. **Token Efficiency**: >50% reduction in tokens per successful mutation (market selection)
2. **Selection Rate**: >90% of mutations die before expensive validation (Demon effectiveness)
3. **Parasitic Prevention**: 0 parasitic mutations pass selection (intent alignment)
4. **Fitness Evolution**: Viral Library shows increasing average fitness over time
5. **Composability**: All components compose via `>>`
6. **Law Compliance**: All category laws verified by BootstrapWitness

---

## Risk Assessment

### High Risk: L-gent Integration Depth

The spec requires deep L-gent integration that may not exist. Mitigation: Start with stub implementations, add real L-gent integration incrementally.

### Medium Risk: Market Calibration

Prediction market odds calibration is empirical. Mitigation: Start with conservative defaults, tune based on observed success rates.

### Low Risk: Backwards Compatibility

Breaking changes to E-gent API. Mitigation: This is intentional (Principle 2: Curated). The old API was unsuitable.

---

## Estimated Effort

| Phase | Complexity | Dependencies |
|-------|-----------|--------------|
| 0: Types | Low | None |
| 1: Demon | High | L-gent (stub OK) |
| 2: Mutator | High | L-gent schemas |
| 3: Market | Medium | B-gent CentralBank |
| 4: Sun | Low | None |
| 5: Library | Medium | L-gent, D-gent |
| 6: Phage | Medium | Types, Demon |
| 7: Cycle | High | All above |
| 8: Safety | Medium | Cycle |
| 9: Cleanup | Low | All above |

---

## Philosophical Note

The current E-gent implementation is a **well-engineered v1** that served its purpose: proving the concept of code evolution agents works. However, it suffers from the "Bureaucratic Evolution" anti-pattern described in the spec.

The v2 spec represents a **paradigm shift** from:
- **Bureaucratic** (budgets, schedules, plans) → **Thermodynamic** (markets, selection, starvation)
- **Passive** (envelopes, outcomes, memory) → **Active** (phages, DNA, viral propagation)
- **Test-only validation** → **Test + Intent alignment** (teleological constraint)

This rebuild isn't about fixing bugs—it's about **changing the fundamental model** of how evolution works.

> *"Nature does not budget. Nature starves. Nature selects."*
> *"The Sun gives. The Demon selects. The Phage adapts."*

---

## Appendix: File Mapping

### Current → New

| Current File | New File | Notes |
|--------------|----------|-------|
| `evolution.py` | `cycle.py` + `evolution_v2.py` | Architecture change |
| `experiment.py` | `phage.py` | Passive → Active |
| `judge.py` | `demon.py` | Judgment → Selection |
| `memory.py` | `library.py` | Accumulation → Evolution |
| `ast_analyzer.py` | `ast_analyzer.py` | Keep (grounding) |
| `safety.py` | `safety_v2.py` | Adapt for thermodynamics |
| `preflight.py` | `preflight.py` | Keep |
| `parser/` | `parser/` | Keep (reliability) |
| `validator.py` | `validator.py` | Keep |
| `repair.py` | `repair.py` | Keep |
| `prompts/` | Remove or minimize | LLM role reduced |
| `incorporate.py` | `phage.py` (infect) | Merged into Phage |
| `stages.py` | `cycle.py` | Integrated into cycle |

### New Files

| File | Purpose |
|------|---------|
| `types.py` | Core types matching spec |
| `thermodynamics.py` | Gibbs Free Energy, enthalpy, entropy |
| `intent.py` | Intent embedding and alignment |
| `mutator.py` | Schema-based mutation generation |
| `schemas.py` | Mutation schema definitions |
| `market.py` | Prediction market economics |
| `sun.py` | Grants for exogenous energy |
| `library.py` | Viral Library with fitness evolution |
| `demon.py` | Teleological Demon (5-layer selection) |
| `phage.py` | Active mutation vectors |
| `cycle.py` | Thermodynamic cycle composition |
