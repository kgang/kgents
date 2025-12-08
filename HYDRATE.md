# HYDRATE.md - kgents Session Context

**Quick start for next session**

---

## TL;DR

**Status**: Evolution pipeline fixed and working ✅
**Latest**: Pushed 3 commits (7d99e18, e4b6e3f, 665d67f) fixing API issues
**Branch**: `main` (synced with origin)

---

## Next Session: Start Here

### Run Evolution Pipeline

```bash
cd /Users/kentgang/git/kgents
source .venv/bin/activate  # ⚠️ CRITICAL - must use kgents venv!
.venv/bin/python impl/claude/evolve.py bootstrap --dry-run --quick
```

**Why venv matters**: Shell may have `VIRTUAL_ENV=/Users/kentgang/git/zenportal/.venv` from other projects. Always activate kgents venv explicitly.

---

## What We Fixed (Dec 8, 2025)

**Problem**: Evolution pipeline failing with 5 different API errors

**Root causes**:
1. Wrong venv → missing mypy
2. Stale bytecode cache
3. evolve.py using outdated Judge/Verdict APIs

**Solutions** (commits pushed):
- `e4b6e3f` - Fixed Verdict API, removed broken Judge usage
- `665d67f` - Cleared bytecode cache, documented venv requirement
- `7d99e18` - Updated HYDRATE.md

---

## Next Priorities

1. **Bootstrap evolution** - Ready to apply improvements
2. **Tests for agents/b/** - pytest for hypothesis.py, robin.py
3. **D/E-gents specs** - Data/Database, Evaluation/Ethics agents
4. Bootstrap Docs Phase 6 (optional) - Regeneration validation

---

## Project Status

**Bootstrap Docs**: ✅ Complete (~2287 lines, commits 16156c8, 15aaa26, 7ee9dc8)
**Bootstrap Agents**: ✅ 7 agents implemented
**Evolution Pipeline**: ✅ Working (after API fixes)
**Meta-evolution**: ✅ Applied 8 improvements to evolve.py, autopoiesis.py

---

## Key Files

- `impl/claude/evolve.py` - Evolution pipeline (fixed)
- `impl/claude/bootstrap/` - 7 bootstrap agents
- `impl/claude/agents/` - a,b,c,h,k-gents
- `docs/BOOTSTRAP_PROMPT.md` - Implementation guide (~1545 lines)
- `AUTONOMOUS_BOOTSTRAP_PROTOCOL.md` - Meta protocol (~1135 lines)
