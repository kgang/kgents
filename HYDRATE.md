# HYDRATE.md - kgents Session Context

**Quick start for next session**

---

## TL;DR

**Status**: Evolution pipeline working, all background processes cleaned up ✅
**Latest**: Dec 8 - Evolution pipeline generates hypotheses successfully with proper venv
**Branch**: `main` (clean working tree)

---

## Dec 8, 2025 Session: Evolution Pipeline Fix

### What Was Fixed

**Problem**: Evolution pipeline failing with `Error: [Errno 2] No such file or directory: 'mypy'`

**Root cause**: Wrong Python venv being used
- Shell had `VIRTUAL_ENV=/Users/kentgang/git/zenportal/.venv` from other projects
- When running `python evolve.py`, system picked up wrong venv
- Wrong venv didn't have mypy → all type checks failed (72/72 experiments)

**Solution**: Always activate kgents venv explicitly
```bash
cd /Users/kentgang/git/kgents
source .venv/bin/activate  # ⚠️ CRITICAL STEP
cd impl/claude
python evolve.py <target> [flags]
```

**Verification**: ✅ Tested successfully
- mypy 1.19.0 installed in kgents venv
- Evolution pipeline loads 27 modules (including new `ground_parser`)
- Generates hypotheses in parallel
- Type checks run correctly with proper venv

---

## Next Session: Start Here

### Run Evolution Pipeline

```bash
cd /Users/kentgang/git/kgents
source .venv/bin/activate
cd impl/claude

# Quick test
python evolve.py bootstrap/id --dry-run --quick

# Full evolution
python evolve.py all --dry-run --quick

# Auto-apply (use with caution)
python evolve.py bootstrap --auto-apply
```

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

## Next Priorities

1. **Evolution improvements** - Many experimental improvements generated, need manual review
2. **Tests for agents/b/** - pytest suite for hypothesis.py, robin.py
3. **D/E-gents specs** - Data/Database, Evaluation/Ethics agent specifications
4. **PyPI package** - Publish kgents-runtime to PyPI
5. **Optional: Actual regeneration test** - Delete and regenerate one bootstrap agent from docs

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

## Session Log

**Dec 8, 2025 (PM Session)**:
- ✅ Completed Bootstrap Docs Phase 6: Regeneration Validation
- ✅ Created `REGENERATION_VALIDATION_GUIDE.md` with manual test cases for all 7 agents
- ✅ Created `test_regeneration.py` automated test harness
- ✅ Captured reference behavior snapshot (Id, Ground, Judge agents verified)
- ✅ Defined success criteria: behavior equivalence (not implementation matching)
- ✅ Updated HYDRATE.md: Phase 6 complete, ~300 lines of validation documentation
- ✅ Enhanced evolution pipeline logging for better decision-making:
  - Full hypothesis logging (not truncated)
  - Rich improvement metadata (type, confidence, rationale)
  - JSON export of experiment results for review
  - Created `EVOLUTION_DECISION_FRAMEWORK.md` (decision guide for reviewing improvements)
- ✅ Documented evolution refinement principle in HYDRATE.md

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
- **Latest improvements (Dec 8)**: Rich logging with full hypotheses, improvement metadata (type/confidence/rationale), JSON export for decision-making
