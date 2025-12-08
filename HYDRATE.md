# HYDRATE.md - kgents Session Context

**Quick start for next session**

---

## TL;DR

**Status**: Type fixes complete, E-gents extracted, pushed to main
**Latest**: Dec 8 - Fixed 72 type errors, extracted E-gents
**Branch**: `main` (clean)
**Mypy**: 122 → 50 errors (50 remaining are structural)

---

## What Was Done This Session

### 1. Type Error Fixes (122 → 50 errors)

Fixed API mismatches across multiple files:
- `hegel.py`: Tension/Contradict/Sublate API calls updated
- `autopoiesis.py`: SublateInput, verdict.reasoning
- `self_improve.py`: Same API fixes, type annotations
- `evolve.py`: HegelAgent.invoke(), runtime types
- `hypothesis.py`: Type parameters, _input_error init
- `plan_fixes*.py`: Return types, DialecticOutput attributes
- `runtime/claude.py`, `openrouter.py`: Return type annotations
- `robin.py`: Missing supporting_observations argument

### 2. E-gents Extraction

New `agents/e/` directory with composable evolution agents:
- `ast_analyzer.py` - AST-based code analysis
- `memory.py` - Improvement history tracking
- `experiment.py` - Experiment types & TestAgent
- `judge.py` - Principle-based evaluation
- `incorporate.py` - Git-safe application
- `safety.py` - Safe self-evolution
- `evolution.py` - SelfEvolutionAgent

### 3. Commits Pushed

```
a705261 docs: Add evolution UX brainstorm and reliability plan
9d9bbf0 feat: Extract E-gents (Evolution agents) from evolve.py
82df794 fix: Resolve 72 type errors across impl/claude
```

---

## Next Session: Start Here

### Option 1: Fix Remaining 50 Type Errors

The remaining errors are structural issues in:
- `runtime/base.py` - AsyncComposedAgent type parameters
- `agents/c/functor.py`, `monad.py` - Generic type params
- `agents/a/skeleton.py` - Missing Agent type parameters
- `agents/h/lacan.py` - Missing return types

```bash
cd /Users/kentgang/git/kgents && source .venv/bin/activate && cd impl/claude
python -m mypy . --strict --explicit-package-bases 2>&1 | head -60
```

### Option 2: Phase 2.5a - Reliability Improvements

See `docs/EVOLUTION_RELIABILITY_PLAN.md` for the prompt engineering phase.

```bash
cd /Users/kentgang/git/kgents && source .venv/bin/activate && cd impl/claude
# Create agents/e/prompts.py with rich context builders
```

### Option 3: Test Evolution Pipeline

```bash
cd /Users/kentgang/git/kgents && source .venv/bin/activate && cd impl/claude
python evolve.py bootstrap --dry-run --quick
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

**Dec 8, 2025 (Type Fixes)**:
- Fixed 72 type errors across impl/claude
- Major API mismatches: Contradict, Sublate, Tension
- Extracted E-gents to agents/e/
- Pushed 3 commits to main
- Remaining: 50 structural type errors

---
