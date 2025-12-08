# HYDRATE.md - kgents Session Context

**Quick start for next session**

---

## TL;DR

**Status**: Phase 2.5a (Prompt Engineering) complete and committed
**Latest**: Dec 8 - Reliability improvements: PreFlight + rich prompts
**Branch**: `main` (Phase 2.5a committed: 1ae1e78)
**Mypy**: 122 → 50 errors (50 remaining are structural)

---

## What Was Done This Session

### Previous Work (Dec 8 morning)

1. **Type Error Fixes** (122 → 50 errors): Fixed API mismatches across multiple files
2. **E-gents Extraction**: Created `agents/e/` with composable evolution agents
3. **Planning Docs**: Created `EVOLUTION_RELIABILITY_PLAN.md`

### Current Session: Phase 2.5a Implementation

**Implemented Layer 1 of Evolution Reliability Plan:**

#### New Files Created:
- `agents/e/prompts.py` (484 lines) - Rich prompt context system
  - `PromptContext`: Type signatures, error baseline, similar patterns
  - `build_improvement_prompt()`: Structured, error-aware prompts
  - `build_prompt_context()`: Context gathering from AST + mypy
- `agents/e/preflight.py` (346 lines) - Module health validation
  - `PreFlightChecker`: Syntax, types, imports, completeness
  - Early detection of blocking issues before LLM calls
- `test_prompt_improvements.py` (192 lines) - Validation suite

#### Modified Files:
- `agents/e/evolution.py`: Integrated PreFlight + rich prompts
- `agents/e/__init__.py`: Exported new components
- `agents/c/monad.py`: Fixed missing `Any` import (NameError)

#### Test Results:
✅ All 4 tests passing:
- PreFlight catches syntax errors
- PreFlight detects type error baseline
- PromptContext builds rich context (type annotations, imports, principles)
- build_improvement_prompt generates structured output (3071 chars)

### Commits This Session

```
1ae1e78 feat: Phase 2.5a - Prompt Engineering Layer for Evolution Reliability
```

---

## Next Session: Start Here

### ✅ COMPLETED: Phase 2.5a - Prompt Engineering Layer

Successfully implemented:
- ✅ PreFlightChecker for module health validation
- ✅ Rich PromptContext with type signatures, error baseline
- ✅ Structured prompts with critical requirements
- ✅ All tests passing
- ✅ Committed (1ae1e78)

**Expected Impact:**
- Target: <10% syntax errors (down from ~20-30%)
- Pre-existing error awareness: 100%
- Prompt structure compliance: 100%

### Option 1: Phase 2.5b - Parsing & Validation Layer

**Next reliability phase** (see `docs/EVOLUTION_RELIABILITY_PLAN.md` lines 282-574):

Create robust parsing with multiple fallback strategies:
```bash
cd /Users/kentgang/git/kgents && source .venv/bin/activate && cd impl/claude
# Create agents/e/parser.py - Multi-strategy parsing
# Create agents/e/validator.py - Schema validation (pre-mypy)
# Create agents/e/repair.py - Incremental code repair
```

**Goal:** >95% parse success rate (up from ~70%)

### Option 2: Measure Phase 2.5a Impact

Run full evolution to measure syntax error rate improvement:
```bash
cd /Users/kentgang/git/kgents && source .venv/bin/activate && cd impl/claude
python evolve.py all --dry-run 2>&1 | tee phase_2.5a_results.log
# Analyze: grep -i "syntax error\|type error\|passed\|failed" phase_2.5a_results.log
```

### Option 3: Fix Remaining 50 Type Errors

Structural issues remaining in:
- `runtime/base.py` - AsyncComposedAgent type parameters
- `agents/c/functor.py`, `monad.py` - Generic type params
- `agents/a/skeleton.py` - Missing Agent type parameters

```bash
cd /Users/kentgang/git/kgents && source .venv/bin/activate && cd impl/claude
python -m mypy . --strict --explicit-package-bases 2>&1 | head -60
```

---

## Critical: Venv Activation

**Always activate before running:**
```bash
cd /Users/kentgang/git/kgents
source .venv/bin/activate
cd impl/claude
```

Verify: `which python` → `/Users/kentgang/git/kgents/.venv/bin/python`

---

## Directory Structure

```
kgents/
├── impl/claude/
│   ├── bootstrap/         # 7 bootstrap agents
│   ├── agents/
│   │   ├── e/             # Evolution agents (NEW)
│   │   ├── h/             # Hegelian dialectic
│   │   ├── b/             # Bio/Scientific
│   │   └── ...
│   ├── runtime/           # LLM execution
│   └── evolve.py          # Evolution CLI
├── docs/
│   ├── EVOLUTION_RELIABILITY_PLAN.md
│   └── EVOLVE_UX_BRAINSTORM.md
└── .venv/                 # Python venv
```

---

## Session Log

**Dec 8, 2025 PM (Phase 2.5a - Reliability)**:
- ✅ Implemented Prompt Engineering Layer (Layer 1 of reliability plan)
- ✅ Created `agents/e/prompts.py` (484 lines) - Rich context system
- ✅ Created `agents/e/preflight.py` (346 lines) - Health validation
- ✅ All tests passing (4/4)
- ✅ Committed 1ae1e78: "feat: Phase 2.5a - Prompt Engineering Layer"
- Next: Phase 2.5b (Parsing) or measure impact

**Dec 8, 2025 AM (Type Fixes & E-gents)**:
- Fixed 72 type errors across impl/claude
- Major API mismatches: Contradict, Sublate, Tension
- Extracted E-gents to agents/e/
- Pushed 3 commits to main
- Remaining: 50 structural type errors

---
