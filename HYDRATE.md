# HYDRATE.md - kgents Session Context

**Quick start for next session**

---

## TL;DR

**Status**: evolve.py ENHANCED with self-improvement features ✅
**Latest**: Dec 8 - AST targeting, memory, principle judging pushed
**Branch**: `main` (pushed)

---

## ⚠️ CRITICAL: Running evolve.py with Correct Venv

**The evolution pipeline REQUIRES the kgents venv to be activated before running.**

### ✅ Correct Pattern (USE THIS ALWAYS)

```bash
# Step 1: Navigate to kgents root
cd /Users/kentgang/git/kgents

# Step 2: Activate the venv (CRITICAL - do not skip!)
source .venv/bin/activate

# Step 3: Navigate to impl directory
cd impl/claude

# Step 4: Run evolution
python evolve.py <target> --dry-run --quick
```

### ❌ What Happens If You Skip Venv Activation

Without activating the venv, you'll see errors like:
- `Error: [Errno 2] No such file or directory: 'mypy'`
- `ModuleNotFoundError: No module named 'anthropic'`
- All experiments fail with type check errors

### ✓ How to Verify Venv Is Active

```bash
# Should show: /Users/kentgang/git/kgents/.venv/bin/python
which python

# Should show: mypy 1.19.0 (compiled: yes)
python -m mypy --version
```

### One-Line Command for Evolution

```bash
cd /Users/kentgang/git/kgents && source .venv/bin/activate && cd impl/claude && python evolve.py all --dry-run --quick
```

---

## Dec 8, 2025: evolve.py Self-Improvement Enhancement

Three high-impact improvements to the evolution pipeline:

### 1. AST-Aware Hypothesis Targeting
- **File**: `evolve.py` lines 285-445
- Parses module AST to extract classes, functions, imports
- Generates **targeted** hypotheses like "Refactor class X (12 methods)" instead of generic "improve this file"
- Identifies complexity hints (large classes, long functions, many parameters)
- Cached analysis for performance

### 2. Improvement Memory (Avoid Re-proposals)
- **File**: `evolve.py` lines 163-277, stored in `.evolve_logs/improvement_history.json`
- Tracks accepted/rejected/held improvements with hypothesis hashes
- Filters out previously rejected hypotheses before experimenting
- Prevents wasted cycles re-trying ideas that already failed
- Records outcomes after each experiment

### 3. Principle-Based Code Judging
- **File**: `evolve.py` lines 453-546
- Replaces TODO placeholder with real 7-principle evaluation
- Evaluates: tasteful (line delta), curated (confidence), ethical (unsafe patterns), joyful (readability), composable (agent patterns), heterarchical (god objects), generative (spec refs)
- Returns detailed scores and reasons
- Verdict: ACCEPT (avg≥0.75), REJECT (avg<0.5 or ethical<0.5), REVISE (otherwise)

**Line count change**: ~1006 → ~1510 lines (+504 lines of self-improvement infrastructure)

---

## Dec 8, 2025 Session: Evolution Applied

### 14 Improvements Incorporated

**Id Agent** (3 improvements):
- `__rlshift__` for left-identity law optimization
- Relaxed strict `is` check (now uses equality)
- `__rrshift__` for right-identity symmetry

**Compose** (2 improvements):
- `FixComposedAgent` now total via Either type
- Decoupled Fix pattern refiner (analyzer/transformer split)

**Types** (1 improvement):
- `FixConfig.should_continue` enhanced with iteration context

**Fix** (1 improvement):
- Proximity metric for adaptive convergence strategies

**Judge** (4 improvements):
- Mini-judges refactored to pure functions
- Placeholder checks → explicit `NotImplementedError`
- Mini-judges now delegate to `Principles.check`
- `VerdictAccumulator` made immutable (frozen)

**Contradict** (2 improvements):
- Per-detector timeout and circuit breaker
- `TensionEvidence` tracking for bidirectional learning

**Ground** (1 improvement):
- Simplified: removed unused Fix retry wrapper (static data)

### Bug Fixes
- Fixed `evolve.py`: `verdict.verdict_type` → `verdict.type`
- Fixed `ground.py`: Corrected Fix import path

---

## Next Session: Start Here

### Primary: Test Enhanced Evolution Pipeline

**Status**: evolve.py enhanced with 3 self-improvement features ✅

**Test the new features**:
```bash
cd /Users/kentgang/git/kgents && source .venv/bin/activate && cd impl/claude
python evolve.py bootstrap --dry-run --quick
```

**What to observe**:
- 🎯 AST-targeted hypotheses (specific function/class suggestions)
- ⏭ Memory filtering (skipped previously rejected ideas)
- 📊 7-principle scoring in judgment output

**Memory file location**: `.evolve_logs/improvement_history.json`

### Next Priorities

- **Run full evolution**: Test on all modules to populate memory
- **Tune judgment thresholds**: Adjust principle weights based on results
- **Bootstrap validation**: Run against REGENERATION_VALIDATION_GUIDE.md
- **D/E-gents specs**: Data/Database, Evaluation/Ethics specifications

---

## Bootstrap Docs Status

| Phase | Status | Content |
|-------|--------|---------|
| 1-3 | ✅ COMPLETE | Worked examples, composition verification, error handling (~800 lines) |
| 4 | ✅ COMPLETE | Pitfalls, troubleshooting, observability, progress tracking (~1350 lines) |
| 5 | ✅ COMPLETE | Cross-references, dependency graph, GroundParser agent (~155 lines) |
| 6 | ✅ COMPLETE | Regeneration validation guide and test harness (~300 lines) |

**Total**: ~2587 lines of production-ready bootstrap documentation

**Documents**:
- `docs/BOOTSTRAP_PROMPT.md` - ~1545 lines (implementation guide)
- `AUTONOMOUS_BOOTSTRAP_PROTOCOL.md` - ~1135 lines (meta protocol)
- `impl/claude/bootstrap/REGENERATION_VALIDATION_GUIDE.md` - ~300 lines (validation guide)
- `impl/claude/bootstrap/test_regeneration.py` - Test harness (automated approach)

**Phase 6 Deliverables**:
- ✓ Behavior snapshot script (simple, works)
- ✓ Manual test cases for all 7 bootstrap agents
- ✓ Validation guide with success criteria
- ✓ Reference behavior captured (`bootstrap_reference/behavior_snapshot.json`)
- ⚠️ Full automated test harness (created but has serialization limitations)

---

## Directory Structure

```
kgents/
├── impl/claude/              # Reference implementation (27 modules)
│   ├── bootstrap/            # 7 bootstrap agents + ground_parser
│   ├── agents/               # A, B, C, H, K agent families
│   ├── runtime/              # LLM execution layer
│   └── evolve.py             # Evolution pipeline
├── spec/                     # Specifications (language-agnostic)
├── docs/                     # Bootstrap docs
└── .venv/                    # Python venv (must activate!)
```

**Note**: `impl/claude-openrouter/` was deleted (user action, Dec 8) - all code in `impl/claude/`

---

## Known Issues

**None currently** - Evolution pipeline working as expected

**Previous issues (resolved)**:
- ✅ Wrong venv causing mypy errors (fixed: activate kgents venv)
- ✅ `impl/claude-openrouter` workspace errors (fixed: directory deleted)

---

## Key Deliverables This Session

1. ✅ **Bootstrap Regenerated**: All 8 modules implemented from spec
2. ✅ **Type Safety**: `mypy --strict` passes on all 9 source files
3. ✅ **Dependency Order**: Level 0→4 implementation as planned

**Implemented Modules** (2423 lines total):
| Module | Lines | Description |
|--------|-------|-------------|
| types.py | 480 | Agent[A,B], Result, Tension, Verdict, etc. |
| id.py | 101 | Identity agent (composition unit) |
| ground.py | 163 | Empirical seed (persona, world) |
| compose.py | 163 | Sequential composition (f >> g) |
| contradict.py | 359 | Tension detection with circuit breaker |
| judge.py | 419 | Seven mini-judges (pure functions) |
| sublate.py | 336 | Hegelian synthesis/hold |
| fix.py | 276 | Fixed-point iteration + polling |
| __init__.py | 126 | Module exports |

---

## Quick Commands Reference

```bash
# Always start with this
cd /Users/kentgang/git/kgents
source .venv/bin/activate

# Check mypy is available
python -m mypy --version  # Should show: mypy 1.19.0

# Run evolution
cd impl/claude
python evolve.py <target> --dry-run --quick

# Commit changes
git add -A
git commit -m "Your message"
git push
```

---

## Bootstrap Regeneration Analysis (Old vs New)

Comparison between pre-regeneration (commit 862d256^) and post-regeneration (f292965):

### Line Count Comparison

| Module | Old | New | Delta | Notes |
|--------|-----|-----|-------|-------|
| types.py | 351 | 480 | +129 | Expanded type definitions, new protocols |
| id.py | 59 | 101 | +42 | Added __rlshift__, __eq__, __hash__ |
| ground.py | 154 | 163 | +9 | Minor reorganization |
| compose.py | 208 | 163 | -45 | Simplified, removed complexity |
| contradict.py | 477 | 359 | -118 | Streamlined detectors |
| judge.py | 481 | 419 | -62 | Pure functions vs classes |
| sublate.py | 258 | 336 | +78 | More resolution strategies |
| fix.py | 364 | 276 | -88 | Cleaner iteration logic |
| __init__.py | 150 | 126 | -24 | Simplified exports |
| **Total** | **2502** | **2423** | **-79** | **3% smaller overall** |

### Key Architectural Changes

**Judge (481→419 lines)**:
- OLD: Mini-judges as classes (`JudgeTasteful(Agent)`, etc.)
- NEW: Mini-judges as pure functions (`check_tasteful()`, etc.)
- Impact: Simpler composition, easier testing, less boilerplate

**Contradict (477→359 lines)**:
- OLD: `TensionEvidence` tracking, complex evidence trails
- NEW: Streamlined detector protocol, circuit breaker pattern
- Impact: Cleaner API, removed speculative features

**Fix (364→276 lines)**:
- OLD: Complex `FixConfig` with `proximity_history`, convergence rate
- NEW: Simpler `FixConfig[A]` generic, focused on core iteration
- Impact: More idiomatic, less over-engineering

**Id (59→101 lines)**:
- OLD: Strict `is` identity check, basic composition
- NEW: Equality-based check, `__rlshift__`/`__eq__`/`__hash__`
- Impact: Better composition law optimization

**Types (351→480 lines)**:
- NEW additions: `JudgeInput`, `PartialVerdict`, `SublateInput`, `SublateResult`, `ContradictInput`, `ContradictResult`
- Moved types from individual modules to central types.py
- Impact: Better type safety, clearer contracts

### What Was Removed

- `ground_parser.py` (132 lines) - Not regenerated
- `test_regeneration.py` (456 lines) - Test harness not regenerated
- `TensionEvidence` detailed tracking (speculative feature)
- Complex `proximity_history` analytics in Fix
- Class-based mini-judges in Judge

### What Was Preserved

- All 7 irreducible bootstrap agents (Id, Ground, Compose, Contradict, Judge, Sublate, Fix)
- Core type system (Agent[A,B], Tension, Verdict, Synthesis)
- Composition laws and category-theoretic structure
- Hegelian dialectic pattern (Contradict → Sublate)

### Summary

The regeneration produced a **leaner implementation** (-3% total lines) while **strengthening the type system** (+37% in types.py). Key design decision: prefer pure functions over stateful classes where appropriate.

---

## Session Log

**Dec 8, 2025 (evolve.py Self-Improvement Enhancement)**:
- ✅ Added AST-aware hypothesis targeting (analyze_module_ast, generate_targeted_hypotheses)
- ✅ Added ImprovementMemory class for tracking accepted/rejected ideas
- ✅ Implemented judge_code_improvement() with 7-principle scoring
- ✅ Wired up memory recording after experiment outcomes
- ✅ All changes pass mypy and syntax checks
- ✅ +504 new lines of self-improvement infrastructure (1006→1510)

**Dec 8, 2025 (evolve.py Refactor)**:
- ✅ Analyzed old vs new bootstrap implementations
- ✅ Added `Verdict.accept()`, `Verdict.reject()`, `Verdict.revise()` factory methods
- ✅ Added `make_default_principles()` helper to bootstrap/__init__.py
- ✅ Fixed evolve.py imports (SublateInput, HoldTension, Tension)
- ✅ Added `_get_sublate()` lazy instantiation method
- ✅ Fixed `synthesize()` to properly use Sublate agent
- ✅ All files pass mypy --strict

**Dec 8, 2025 (Bootstrap Implementation)**:
- ✅ Implemented all 8 bootstrap modules from spec
- ✅ Level 0: types.py (Agent[A,B], Result, Tension, Verdict, etc.)
- ✅ Level 1: id.py (identity laws), ground.py (persona/world seed)
- ✅ Level 2: compose.py (f >> g), contradict.py (tension detection)
- ✅ Level 3: judge.py (7 mini-judges), sublate.py (synthesis/hold)
- ✅ Level 4: fix.py (fixed-point iteration)
- ✅ All 9 files pass mypy --strict

**Dec 8, 2025 (Planning Session)**:
- ✅ Created `BOOTSTRAP_REGENERATION_PLAN.md` (475 lines)
- ✅ Researched spec/, docs/, impl/agents, impl/runtime for patterns
- ✅ Defined 8-file implementation with dependency graph
- ✅ Pushed to main

**Dec 8, 2025 (Regeneration Prep)**:
- ✅ Cleared bootstrap agents for regeneration validation
- ✅ Only `REGENERATION_VALIDATION_GUIDE.md` remains in bootstrap/

**Dec 8, 2025 (Evolution Session)**:
- ✅ Ran evolution pipeline on bootstrap modules
- ✅ Fixed `evolve.py` bug: `verdict.verdict_type` → `verdict.type`
- ✅ Applied 14 improvements across 7 modules (Id, Compose, Types, Fix, Judge, Contradict, Ground)
- ✅ Fixed `ground.py` import error after evolution
- ✅ All core bootstrap modules pass type checking
- ✅ Added explicit venv activation instructions to HYDRATE.md (prominent warning section)

**Dec 8, 2025 (PM Session)**:
- ✅ Completed Bootstrap Docs Phase 6: Regeneration Validation
- ✅ Enhanced evolution pipeline logging (JSON export, rich metadata)

**Dec 8, 2025 (AM Session)**:
- ✅ Diagnosed evolution pipeline mypy errors
- ✅ Identified wrong venv as root cause
- ✅ Tested fix: `source .venv/bin/activate` before running
- ✅ Verified: Evolution loads 27 modules, generates hypotheses correctly
- ✅ Updated HYDRATE.md with concise session context

**Previous sessions**:
- Dec 8 earlier: Bootstrap Docs Phases 1-5 complete (~2287 lines)
- Dec 7: Phase 1 type fixes (Fix[A,B] → Fix[A]), EvolutionAgent refactor
- Dec 7: Full-stack evolution (25 modules, 100% pass rate)

---

## Meta-Notes for Future Sessions

**When evolution fails with "mypy not found"**:
1. Check current venv: `which python` (should be `/Users/kentgang/git/kgents/.venv/bin/python`)
2. If wrong venv: `source /Users/kentgang/git/kgents/.venv/bin/activate`
3. Verify: `python -m mypy --version`

**When working across multiple projects**:
- Always check `which python` before running kgents commands
- Shell may inherit `VIRTUAL_ENV` from previous projects
- Use absolute path if needed: `/Users/kentgang/git/kgents/.venv/bin/python`

**Bootstrap docs are production-ready**:
- AUTONOMOUS_BOOTSTRAP_PROTOCOL.md: Complete protocol with pitfalls, observability
- BOOTSTRAP_PROMPT.md: Complete implementation guide with examples, troubleshooting
- Both documents comprehensive and ready for LLM consumption

**Evolution Pipeline Continuous Refinement**:
The evolution pipeline (`evolve.py`) should be continuously refined when sensible:
- ✅ **DO refine**: Better logging, decision-support features, usability improvements
- ✅ **DO refine**: Structured output formats (JSON), rich metadata, error reporting
- ✅ **DO refine**: Better hypotheses, smarter filtering, principle-aware judging
- ⚠️ **BE CAUTIOUS**: Don't add complexity that makes evolution harder to understand
- ❌ **DON'T**: Auto-apply improvements without human judgment (tasteful curation required)

**Latest improvements (Dec 8)**:
- AST-aware hypothesis targeting (targeted instead of generic)
- ImprovementMemory (avoid re-proposing rejected ideas)
- Principle-based judging (7-principle scoring replaces TODO placeholder)
- Memory recording (track outcomes for learning)
