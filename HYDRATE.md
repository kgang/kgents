# HYDRATE.md - Bootstrap Docs Phase 4-6 Status

**Session hydration context for Kent + Claude Code**

---

## Current State

**Location**: Working from `/Users/kentgang/git/kgents/` (root)

**Directory structure**:
- `impl/claude/` - Reference implementation ✓ (contains bootstrap/, agents/, runtime/, evolve.py)
- `impl/claude-openrouter/` - **DELETED by user** ✓ (was causing workspace errors)

### Bootstrap Docs Phases 1-5: **COMPLETE** ✓

See main HYDRATE.md (in root) for full history. Bootstrap documentation is production-ready.

---

## Current Work: Evolution Pipeline Type Check Failures

### Problem

Running `python evolve.py` from `impl/claude/` results in **72/72 experiments failing type checks**.

**Error**: `[Errno 2] No such file or directory: 'mypy'`

**Root cause**: Wrong Python venv being used
- System Python: `/Users/kentgang/git/zenportal/.venv/bin/python` (WRONG)
- Should be: `/Users/kentgang/git/kgents/.venv/bin/python` (CORRECT)

### Why This Happens

1. User has multiple projects (`kgents`, `zenportal`)
2. Shell environment has `VIRTUAL_ENV=/Users/kentgang/git/zenportal/.venv`
3. When running `python evolve.py` from `impl/claude/`, it picks up wrong venv
4. Wrong venv doesn't have mypy installed → all type checks fail

### Solution

**Option 1: Activate kgents venv before running** (RECOMMENDED)

```bash
cd /Users/kentgang/git/kgents
source .venv/bin/activate
cd impl/claude
python evolve.py bootstrap/id --dry-run --quick
```

**Option 2: Use explicit Python path**

```bash
cd /Users/kentgang/git/kgents/impl/claude
../../.venv/bin/python evolve.py bootstrap/id --dry-run --quick
```

**Option 3: Unset conflicting VIRTUAL_ENV**

```bash
unset VIRTUAL_ENV
cd /Users/kentgang/git/kgents
source .venv/bin/activate
cd impl/claude
python evolve.py bootstrap/id --dry-run --quick
```

### Verification

```bash
# Check that mypy is available in kgents venv
cd /Users/kentgang/git/kgents
.venv/bin/mypy --version  # Should show: mypy 1.19.0

# Check Python version
.venv/bin/python --version  # Should show: Python 3.13.0
```

---

## Commands Reference

**From kgents root**:
```bash
# Activate kgents venv
source .venv/bin/activate

# Check dependencies
uv sync  # May fail due to workspace config, but mypy is already installed

# Run evolution from impl/claude/
cd impl/claude
python evolve.py bootstrap/id --dry-run --quick
python evolve.py all --dry-run
```

**From impl/claude/**:
```bash
# Use explicit Python path (if venv not activated)
../../.venv/bin/python evolve.py bootstrap/id --dry-run --quick
```

---

## What to Work On Next

### Option A: Fix Evolution Pipeline (CURRENT)

**Status**: In progress, solution identified

**Tasks**:
1. ✓ Identify root cause (wrong venv)
2. ✓ Document solution (activate kgents venv)
3. Test with: `source .venv/bin/activate && cd impl/claude && python evolve.py bootstrap/id --dry-run --quick`
4. Verify type checks pass

### Option B: Bootstrap Docs Phase 6 (Optional)

**Status**: Not started (Phases 1-5 complete)

**What's needed**:
- Regeneration test validation
- Final Contradict/Judge checks on bootstrap docs

---

## Recent Commits Context

```
16156c8 - Bootstrap Docs Phase 5 Complete (cross-references, GroundParser)
15aaa26 - Bootstrap Docs Phase 4 Complete (pitfalls, troubleshooting, observability)
7ee9dc8 - Bootstrap Docs Phases 1-3 complete
```

---

## Notes for Next Session

1. **Always activate kgents venv first**: `source .venv/bin/activate`
2. **impl/claude-openrouter is deleted** - all code in `impl/claude/`
3. **mypy is installed and working** in kgents venv (version 1.19.0)
4. Evolution pipeline code is correct, just needs right venv

---

## Bootstrap Docs Status Summary

| Phase | Status | Lines Added | Key Additions |
|-------|--------|-------------|---------------|
| 1-3 | ✅ COMPLETE | ~800 | Worked examples, composition verification, error handling |
| 4 | ✅ COMPLETE | ~1350 | Pitfalls, troubleshooting, observability, progress tracking |
| 5 | ✅ COMPLETE | ~155 | Cross-references, dependency graph, GroundParser agent |
| 6 | ❌ NOT STARTED | TBD | Regeneration validation (optional) |

**Total**: ~2287 lines added across all phases
**Documents**: BOOTSTRAP_PROMPT.md (~1545 lines), AUTONOMOUS_BOOTSTRAP_PROTOCOL.md (~1135 lines)
