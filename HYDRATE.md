# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: T-gents specification COMPLETE - Category Theory-based testing framework
**Branch**: `main` (pushed: d73283e)
**New**: Complete `spec/t-gents/` with algebra, taxonomy, and Adversarial Gym

---

## This Session: T-gents Specification (2025-12-08)

### Completed ✅

**Commit d73283e: T-gents Specification**

Created comprehensive Category Theory-based testing specification:

**Files Created:**
- `spec/t-gents/README.md` (10K): Core philosophy, dual mandate, full taxonomy
- `spec/t-gents/algebra.md` (10K): Category laws, functors, monads, commutative diagrams
- `spec/t-gents/taxonomy.md` (19K): Detailed specs for 11+ T-gent types with implementation skeletons
- `spec/t-gents/adversarial.md` (16K): Adversarial Gym chaos engineering framework

**Key Concepts:**
- Testing as **algebraic verification** (not just examples)
- Four T-gent types: Nullifiers, Saboteurs, Observers, Critics
- Commutative diagram testing
- Monte Carlo stress testing via Adversarial Gym
- Integration with E-gents evolution

**Taxonomy:**
- Type I (Nullifiers): MockAgent, FixtureAgent
- Type II (Saboteurs): FailingAgent, NoiseAgent, LatencyAgent, FlakyAgent
- Type III (Observers): SpyAgent, PredicateAgent, CounterAgent, MetricsAgent
- Type IV (Critics): JudgeAgent, CorrectnessAgent, SafetyAgent

Transforms testing from example-based to proof-based reliability.

---

## Previous: J-gents Phase 1 Implementation (2025-12-08)

### Completed ✅

**Commit dc27faa: J-gents Phase 1**

Created `impl/claude/agents/j/` directory with:

**1. promise.py - Promise[T] Data Type**
- `Promise[T]` generic dataclass with Ground fallback
- `PromiseState` enum: pending, resolving, resolved, collapsed, failed
- Entropy budget calculation: `1/(depth+1)`
- Tree structure for PROBABILISTIC decomposition
- `PromiseMetrics` for execution analysis
- Helpers: `promise()`, `child_promise()`, `collect_metrics()`

**2. reality.py - RealityClassifier Agent**
- `Reality` enum: DETERMINISTIC | PROBABILISTIC | CHAOTIC
- `RealityClassifier` agent implementing spec/j-gents/reality.md
- Heuristic keyword-based classification:
  - ATOMIC_KEYWORDS: read, get, fetch, query, return, format, etc.
  - COMPLEX_KEYWORDS: refactor, analyze, fix, implement, etc.
  - CHAOTIC_KEYWORDS: infinite, forever, everything, always, etc.
- Budget-based chaos threshold (default 0.1)
- `classify()` async and `classify_sync()` helpers

**3. __init__.py - Module Exports**
- All Promise types and helpers
- All Reality types and classifier

### Test Results

All classification tests pass:
```
classify("Read config.yaml") → deterministic ✓
classify("Refactor the auth module") → probabilistic ✓
classify("Make everything better forever") → chaotic ✓
classify("Simple task", budget=0.05) → chaotic ✓
```

---

## Previous: Phase 2.5c Recovery Layer (UNCOMMITTED)

Changes in working directory:
- `evolve.py`: Recovery layer integration
- `agents/t/`: T-gents test framework
- `spec/t-gents/`: T-gents spec

---

## Next Session: Start Here

### Priority 1: Implement T-gents (Testing Agents)

Now that spec is complete, implement the T-gents framework:

```bash
cd impl/claude
mkdir -p agents/t
touch agents/t/__init__.py agents/t/core.py
```

**Phase 1 Components:**
- [ ] Core Agent protocol with `__is_test__` flag
- [ ] MockAgent (constant morphism)
- [ ] FixtureAgent (lookup morphism)
- [ ] SpyAgent (writer monad for logging)
- [ ] FailingAgent (bottom morphism for chaos)

**Phase 2 Components:**
- [ ] NoiseAgent (semantic perturbation)
- [ ] PredicateAgent (runtime validation gate)
- [ ] Basic AdversarialGym framework

**Integration:**
- [ ] Use T-gents to test evolution pipeline
- [ ] Create commutative diagram tests
- [ ] Bootstrap Gym with existing agents

### Priority 2: Continue J-gents Implementation

Phase 2 from JGENT_SPEC_PLAN.md:
- [ ] Implement Chaosmonger AST analyzer
- [ ] Add entropy budget to Fix
- [ ] Integrate with SafetyConfig

### Priority 3: Uncommitted Files

Review and commit/discard:
- `impl/claude/docs/PHASE_2_5D_ANALYSIS.md`
- `impl/claude/test_evolution_metrics.py`
- Check if recovery layer changes in `evolve.py` still needed

---

## What Exists

**J-gents Implementation** (`impl/claude/agents/j/`) ✅ Phase 1
- promise.py: Promise[T] lazy computation
- reality.py: RealityClassifier agent
- __init__.py: Module exports

**J-gents Spec** (`spec/j-gents/`) ✅ Complete
- README.md: Overview
- reality.md: Trichotomy spec
- lazy.md: Promise abstraction
- stability.md: Entropy budgets
- JGENT_SPEC_PLAN.md: Implementation phases

**T-gents Spec** (`spec/t-gents/`) ✅ Complete
- README.md: Core philosophy, taxonomy (4 types, 11+ T-gents)
- algebra.md: Category Theory foundations (laws, functors, monads)
- taxonomy.md: Detailed specs with implementation skeletons
- adversarial.md: Adversarial Gym chaos engineering

**Evolution Pipeline** (`agents/e/`)
- prompts.py: API stub extraction
- parser.py: F-string repair
- retry.py, fallback.py, error_memory.py: Recovery layer (awaiting commit)

---

## Session Log

**Dec 8 PM**: d73283e - T-gents specification complete (4 docs, 55K total)
**Dec 8 PM (prev)**: dc27faa - J-gents Phase 1 implementation (Promise[T], RealityClassifier)
**Dec 8 PM (prev)**: db0f802 - HYDRATE.md update
**Dec 8 PM (prev)**: UNCOMMITTED - Phase 2.5c recovery layer + T-gents impl

---

## Quick Commands

```bash
# Test J-gents
cd impl/claude
python -c "from agents.j import classify_sync; print(classify_sync('Fix bug'))"

# Type check J-gents
python -m mypy --strict --explicit-package-bases agents/j/

# Evolution
python evolve.py status
python evolve.py meta --auto-apply
```

---
