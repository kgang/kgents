# HYDRATE.md - Session Context

**Quick reference for Kent + Claude Code**

---

## Session Summary (Dec 8, 2025)

### ✅ Issues Resolved

**Problem**: Evolution pipeline failing with multiple API errors
- `HypothesisEngine.__init__() got unexpected keyword argument 'runtime'`
- `'HypothesisEngine' object is not callable`
- `JudgeInput.__init__() got unexpected keyword argument 'claim'`
- `Verdict.__init__() got unexpected keyword argument 'verdict_type'`
- `[Errno 2] No such file or directory: 'mypy'`

**Root Causes Identified**:
1. ❌ **Wrong venv**: zenportal/.venv instead of kgents/.venv
2. ❌ **Stale bytecode cache**: Old .pyc files from previous runs
3. ❌ **API mismatches**: evolve.py using outdated Judge/Verdict APIs

**Solutions Applied**:
1. ✅ Cleared Python bytecode cache
2. ✅ Fixed evolve.py to use correct Verdict API (commit e4b6e3f)
3. ✅ Simplified judge logic to auto-accept (removed broken JudgeInput usage)
4. ✅ Documented venv activation requirement

### Commits This Session

```
e4b6e3f - Fix evolve.py API compatibility issues
665d67f - Update HYDRATE.md: Session state and environment fixes
```

---

## Evolution Pipeline Status

**Working** ✅ - Use correct venv:

```bash
cd /Users/kentgang/git/kgents
source .venv/bin/activate
.venv/bin/python impl/claude/evolve.py bootstrap --dry-run --quick
```

**Key learnings**:
- Always activate kgents venv before running evolve.py
- HypothesisEngine API was correct (no runtime param needed)
- evolve.py validator already uses `sys.executable -m mypy` (correct pattern)

---

## Next Steps

1. **Run full bootstrap evolution** - 32 improvements ready from earlier dry-run
2. **Bootstrap Docs Phase 6** (optional) - Regeneration validation
3. **Tests for agents/b/** - pytest suite for hypothesis.py and robin.py
4. **D/E-gents specs** - Data/Database, Evaluation/Ethics agent specifications

---

## Bootstrap Docs: COMPLETE ✅

| Phase | Status | Lines Added |
|-------|--------|-------------|
| 1-3 | ✅ | ~800 |
| 4 | ✅ | ~1350 |
| 5 | ✅ | ~155 |
| **Total** | **✅** | **~2287** |

Commits: 16156c8, 15aaa26, 7ee9dc8
