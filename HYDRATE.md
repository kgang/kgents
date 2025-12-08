# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: E-gents specification COMPLETE - Full genus spec from first principles
**Branch**: `EEGENTS-5ccbc0bd` (pushed: 4f519f7)
**Achievement**: Comprehensive E-gents spec with dialectical evolution, multi-layer safety, institutional memory
**Next**: J-gents Phase 3 (JIT compilation) OR T-gents Phase 2 OR implement E-gents from spec

---

## This Session: E-gents Specification (2025-12-08)

### Completed ✅

**Commit 4f519f7: E-gents (Evolution Agents) Complete Specification**

Created comprehensive specification from first principles:

**spec/e-gents/README.md** (~200 lines):
- Philosophy: Dialectical evolution through safe experimentation
- 3 new principles: Experimental, Dialectical, Self-Aware
- 6-stage pipeline architecture
- 3-layer reliability (prompt, parse/validate, recovery/learning)

**spec/e-gents/evolution-agent.md** (~800 lines):
- Full YAML specification (input/output types, errors, behavior)
- Detailed pipeline stages: PreFlight → Ground → Hypothesize → Experiment → Judge → Incorporate
- Concrete example: evolving calculate() function through all 6 stages
- Composition patterns with B-gents, H-gents, K-gent
- Anti-patterns and safety guarantees

**spec/e-gents/grounding.md** (~500 lines):
- AST analysis specification (classes, functions, complexity metrics)
- Targeted hypothesis generation from code structure
- Cyclomatic complexity & nesting depth metrics
- Example: analyzing DataProcessor class with complexity 11
- Caching strategy and integration with LLM hypotheses

**spec/e-gents/memory.md** (~600 lines):
- ImprovementMemory: track accepted/rejected/held outcomes
- ErrorMemory: learn from failure patterns across sessions
- Fuzzy matching (Levenshtein similarity, 80% threshold)
- .evolve_memory.json persistence format
- Memory-driven prompt refinement and hypothesis filtering

**spec/e-gents/safety.md** (~600 lines):
- Self-evolution via fixed-point iteration
- Dual similarity metrics (Levenshtein + structural AST)
- Sandbox testing (syntax, types, self-test)
- Convergence detection (threshold 0.95, max iterations 3-5)
- Human approval gates for high-risk changes
- Example: evolve.py evolving itself through 3 iterations

**Design Innovations:**
- Dialectical foundation (thesis/antithesis/synthesis via H-gents)
- Every stage is composable morphism (A → B)
- Multi-layer defense in depth (not single validation)
- Institutional memory prevents wasted re-proposals
- Meta-circular: E-gents can safely evolve themselves

**Total**: ~2,800 lines of specification across 5 files

---

## Previous: J-gents Phase 2 Completion (2025-12-08)

### Completed ✅

**Commit 0107f3f: J-gents Phase 2 - Entropy Budget & Chaosmonger Integration**

**bootstrap/types.py:**
- Add `entropy_budget` field to `FixConfig` (J-gents entropy tracking)
- Add `entropy_remaining` field to `FixResult` (budget consumption tracking)

**bootstrap/fix.py:**
- Implement entropy budget tracking in fixed-point iteration
- Diminishing budget per iteration: `budget / (iteration + 1)`
- Early termination when budget < 0.1 threshold
- Add `entropy_budget` parameter to `fix()` convenience function

**agents/e/safety.py:**
- Add Chaosmonger integration fields to `SafetyConfig`:
  - `chaosmonger_enabled` (default True)
  - `max_cyclomatic_complexity` (20)
  - `max_branching_factor` (5)
  - `allowed_imports` / `forbidden_imports`
- Add `stability_valid` field to `SandboxTestResult`
- Implement `_check_stability()` method using Chaosmonger
- Pre-Judge stability check runs before syntax/type checks

**Test Results:**
```
✓ FixConfig with entropy_budget: 1.0
✓ FixResult with entropy_remaining: 0.5
✓ SafetyConfig.chaosmonger_enabled: True
✓ SafetyConfig.max_cyclomatic_complexity: 20
✓ All syntax checks pass
```

---

## Previous: J-gents Phase 2 - Chaosmonger (2025-12-08)

**Commit b917e2e: Chaosmonger AST Analyzer**

- `impl/claude/agents/j/chaosmonger.py` (~400 lines): Full AST-based stability analyzer
- Features: Import analysis, cyclomatic complexity, unbounded recursion detection
- All tests passing, mypy --strict passes

---

## Previous: T-gents Phase 1 Implementation (2025-12-08)

**Commit 8189e79: T-gents Phase 1**

5 T-gent types implemented:
- MockAgent, FixtureAgent, FailingAgent, SpyAgent, PredicateAgent
- Comprehensive test suite (10 tests, all passing)

---

## Next Session: Start Here

### Priority 1: E-gents Implementation from Spec

Now that spec is complete, implement reference implementation:
- [ ] Align impl/claude/agents/e with spec/e-gents
- [ ] Update EvolutionPipeline to match 6-stage spec
- [ ] Implement PreFlightChecker per grounding.md
- [ ] Enhance ImprovementMemory per memory.md spec
- [ ] Add SafeEvolutionAgent per safety.md

**Or continue with other genera:**

### Priority 2: J-gents Phase 3 - JIT Compilation

From JGENT_SPEC_PLAN.md:
- [ ] Write jit.md spec
- [ ] Implement MetaArchitect agent
- [ ] Sandboxed execution environment
- [ ] Integration with Judge

### Priority 3: T-gents Phase 2 - Additional Observers & Saboteurs

Continue T-gents implementation:
- [ ] NoiseAgent (semantic perturbation - Type II)
- [ ] LatencyAgent (temporal delay - Type II)
- [ ] FlakyAgent (probabilistic failure - Type II)
- [ ] CounterAgent (invocation tracking - Type III)
- [ ] MetricsAgent (performance profiling - Type III)

### Priority 4: J-gents Phase 4 - Coordination

From JGENT_SPEC_PLAN.md:
- [ ] Write lazy.md spec (promises)
- [ ] Implement main JGent coordinator
- [ ] Test-driven reality (test generation)
- [ ] End-to-end integration tests

---

## What Exists

**E-gents Spec** (`spec/e-gents/`) ✅ Complete
- README.md: Philosophy, principles, overview
- evolution-agent.md: Main 6-stage pipeline spec
- grounding.md: AST analysis and targeted hypotheses
- memory.md: Institutional learning and error memory
- safety.md: Self-evolution with convergence detection

**E-gents Implementation** (`impl/claude/agents/e/`) ⚠️ Partial (needs alignment with spec)
- evolution.py, ast_analyzer.py, memory.py, experiment.py, judge.py, incorporate.py
- preflight.py, prompts.py, parser.py, validator.py, repair.py
- retry.py, fallback.py, error_memory.py, safety.py
- Note: Implementation predates spec, may need updates to match

**J-gents Implementation** (`impl/claude/agents/j/`) ✅ Phase 2 COMPLETE
- promise.py: Promise[T] lazy computation
- reality.py: RealityClassifier agent
- chaosmonger.py: AST stability analyzer
- __init__.py: Module exports

**J-gents Bootstrap Integration** ✅ Phase 2 COMPLETE
- bootstrap/types.py: FixConfig.entropy_budget, FixResult.entropy_remaining
- bootstrap/fix.py: Entropy tracking in iteration
- agents/e/safety.py: SafetyConfig + Chaosmonger integration

**T-gents Implementation** (`impl/claude/agents/t/`) ✅ Phase 1 COMPLETE
- mock.py: MockAgent (constant morphism)
- fixture.py: FixtureAgent (deterministic lookup)
- failing.py: FailingAgent (bottom morphism with recovery)
- spy.py: SpyAgent (Writer Monad)
- predicate.py: PredicateAgent (validation gate)

**J-gents Spec** (`spec/j-gents/`) ✅ Complete
- README.md, reality.md, lazy.md, stability.md, JGENT_SPEC_PLAN.md

**T-gents Spec** (`spec/t-gents/`) ✅ Complete
- README.md, algebra.md, taxonomy.md, adversarial.md

---

## Session Log

**Dec 8 (this)**: 4f519f7 - E-gents complete specification from first principles (~2,800 lines)
**Dec 8**: 0107f3f - J-gents Phase 2 completion (entropy budget + Chaosmonger integration)
**Dec 8**: 8189e79 - T-gents Phase 1 implementation
**Dec 8**: b917e2e - J-gents Phase 2 Chaosmonger implementation
**Dec 8**: 0919279 - Phase 2.5d testing & analysis
**Dec 8**: d73283e - T-gents specification complete
**Dec 8**: dc27faa - J-gents Phase 1 (Promise[T], RealityClassifier)

---

## Quick Commands

```bash
# View E-gents specification
cat spec/e-gents/README.md
cat spec/e-gents/evolution-agent.md  # Main pipeline
cat spec/e-gents/grounding.md        # AST analysis
cat spec/e-gents/memory.md           # Institutional learning
cat spec/e-gents/safety.md           # Self-evolution

# Check E-gents implementation alignment
ls -la impl/claude/agents/e/

# Test J-gents entropy budget
cd impl/claude
python -c "
from bootstrap.types import FixConfig, FixResult
config = FixConfig(max_iterations=10, entropy_budget=1.0)
print(f'entropy_budget: {config.entropy_budget}')
"

# Test Chaosmonger
python -c "from agents.j import is_stable; print(is_stable('def f(): pass'))"

# Test SafetyConfig integration
python -c "
from agents.e.safety import SafetyConfig
c = SafetyConfig()
print(f'chaosmonger_enabled: {c.chaosmonger_enabled}')
"

# Type check
python -m mypy --strict --explicit-package-bases bootstrap/types.py bootstrap/fix.py
```

---
