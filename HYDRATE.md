# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: Phase 2.5c pushed (Recovery & Learning Layer)
**Branch**: `main` @ dd32fa7
**Mypy**: 0 errors (55 source files, strict)
**Evolution**: 48 experiments, 0 incorporated - needs debugging

---

## Next Session: Start Here

### Priority: Wire Up Recovery Layer

Phase 2.5c modules exist but need integration into evolution pipeline:

```bash
cd /Users/kentgang/git/kgents && source .venv/bin/activate && cd impl/claude
```

1. **Check why 48/48 failed**: Look at `.evolve_logs/evolve_all_20251208_120703.log`
2. **Wire retry.py into evolve.py**: Call `RetryStrategy.should_retry()` on failures
3. **Wire fallback.py**: Use `FallbackStrategy` when retries exhausted
4. **Wire error_memory.py**: Track failures for learning

### Quick Test

```bash
python evolve.py bootstrap/id --dry-run
```

---

## What Exists (Layer 2+3)

**agents/e/parser.py** - Multi-strategy code extraction
**agents/e/validator.py** - Pre-mypy schema validation
**agents/e/repair.py** - AST-based auto-fixes
**agents/e/retry.py** - Failure-aware prompt refinement
**agents/e/fallback.py** - Progressive simplification
**agents/e/error_memory.py** - Failure pattern learning

---

## Session Log

**Dec 8 PM**: Committed dd32fa7 - Phase 2.5c Recovery Layer (retry, fallback, error_memory)
**Dec 8 PM**: d7d3e34 - Phase 2.5b Parsing Layer (parser, validator, repair)
**Dec 8 PM**: 0a7a751 - Fixed all mypy --strict errors (50 → 0)
**Dec 8 PM**: 1ae1e78 - Phase 2.5a Prompt Engineering Layer

---
