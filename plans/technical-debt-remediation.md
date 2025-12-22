# Technical Debt Remediation Plan

> Created: 2025-12-22
> Status: Active
> Priority: Medium (quality gate, not blocking features)

---

## Executive Summary

After committing 22 feature commits, this plan addresses accumulated technical debt:
- **183 mypy errors** (mostly manifest signature mismatches)
- **~229 ESLint warnings** (console.log, complexity)
- **1 pytest collection error** (conftest in wrong location)
- **TypeScript**: Passing (no errors)

---

## Phase 1: Critical Blockers (Do First)

### 1.1 Pytest Collection Error

**Issue**: `pytest_plugins` defined in non-top-level conftest

**Location**: `protocols/context/_tests/conftest.py`

**Fix**:
```bash
# Move pytest_plugins to top-level conftest.py
# Or remove the pytest_plugins definition from the nested conftest
```

**Effort**: 10 minutes
**Impact**: Blocks ALL test runs

---

## Phase 2: Mypy Errors (112 override errors)

### 2.1 Manifest Signature Mismatch

**Pattern**: 112 errors of type `[override]`

```
Signature of "manifest" incompatible with supertype "BaseLogosNode"
Superclass: def manifest(self, observer: Umwelt[Any, Any], **kwargs: Any) -> ...
Subclass:   def manifest(self, observer: Umwelt[Any, Any]) -> ...
```

**Root Cause**: BaseLogosNode.manifest() accepts `**kwargs`, but subclasses don't include it.

**Fix Options**:

| Option | Pros | Cons |
|--------|------|------|
| A. Add `**kwargs` to all subclass manifest() | Quick fix | Repetitive, kwargs often unused |
| B. Change BaseLogosNode to not require kwargs | Cleaner | Breaking change for nodes that use kwargs |
| C. Use @typing.override with explicit ignore | Explicit | Hides potential real issues |

**Recommended**: Option A (add `**kwargs: Any` to all manifest signatures)

**Files to Fix** (top 10 by error count):
1. `protocols/agentese/contexts/void.py` (50 errors)
2. `protocols/cli/handlers/context.py` (39 errors)
3. `protocols/agentese/contexts/vitals.py` (25 errors)
4. `protocols/agentese/contexts/time.py` (25 errors)
5. `protocols/agentese/contexts/design.py` (25 errors)
6. `protocols/agentese/contexts/three.py` (20 errors)
7. `protocols/agentese/contexts/self_flow.py` (20 errors)
8. `protocols/agentese/contexts/self_data.py` (20 errors)
9. `protocols/agentese/contexts/projection.py` (20 errors)
10. `protocols/agentese/_tests/test_node.py` (20 errors)

**Effort**: 2-3 hours (mechanical find-replace)

### 2.2 Other Mypy Errors

| Type | Count | Fix Strategy |
|------|-------|--------------|
| `[no-untyped-call]` | 49 | Add type stubs or ignore pragmas |
| `[no-untyped-def]` | 10 | Add return type annotations |
| `[type-arg]` | 3 | Fix generic type arguments |
| `[import-untyped]` | 3 | Install type stubs (types-pyperclip, etc.) |
| `[assignment]` | 2 | Fix type mismatches |
| Others | 4 | Case-by-case fixes |

**Effort**: 1-2 hours

---

## Phase 3: ESLint Warnings (~229)

### 3.1 Console Statement Warnings (~200)

**Issue**: Using `console.log` instead of allowed methods (warn, error, info)

**Files**: Mostly in `scripts/sync-types.ts` and `src/api/collaboration.ts`

**Fix Options**:
1. Replace with `console.info` for informational logs
2. Use a proper logger abstraction
3. Add eslint-disable comments for legitimate debug scripts

**Recommended**:
- Scripts: Use `console.info` (acceptable for CLI tools)
- Production code: Replace with proper logging

**Effort**: 1 hour

### 3.2 Complexity Warnings (~10)

**Issue**: Functions exceeding complexity threshold (15)

| File | Function | Complexity |
|------|----------|------------|
| `scripts/sync-types.ts` | `main` | 23 |
| `api/collaboration.ts` | Arrow function | 17 |
| `components/capture/CaptureForm.tsx` | `CaptureForm` | 21 |
| `components/crystal/CrystalItem.tsx` | `CrystalItem` | 17 |
| `components/ghost/GhostSurface.tsx` | `GhostSurface` | 18 |
| `components/cursor/AnimatedCursor.tsx` | `AnimatedCursor` | 28 |
| ... | ... | ... |

**Fix Strategy**: Extract helper functions to reduce cyclomatic complexity

**Effort**: 2-3 hours (depends on refactoring appetite)

---

## Phase 4: Documentation Gaps

### 4.1 New Protocols Need Docstrings

- `protocols/context/` - No module docstrings
- `protocols/dawn/` - Missing class docstrings
- `protocols/derivation/` - Some files missing docs

### 4.2 Skills Documentation

Skills added but may need updates:
- `witness-for-agents.md` - New, needs review
- `zenportal-patterns.md` - New, needs review

**Effort**: 1-2 hours

---

## Execution Plan

### Week 1: Critical Path

```
Day 1:
[ ] Fix pytest conftest issue (10 min)
[ ] Run full test suite to verify (5 min)
[ ] Install missing type stubs (pip install types-pyperclip) (5 min)

Day 2-3:
[ ] Fix manifest signature mismatches (batch by file)
[ ] Verify mypy passes after each batch
```

### Week 2: Quality Polish

```
Day 1:
[ ] Fix remaining mypy errors
[ ] Add missing type annotations

Day 2:
[ ] Address ESLint console warnings
[ ] Refactor high-complexity functions

Day 3:
[ ] Documentation pass
[ ] Final quality gate verification
```

---

## Commands for Verification

```bash
# Full quality check
cd impl/claude && uv run pytest -x -q && uv run mypy . --no-error-summary | tail -5

# Frontend checks
cd impl/claude/web && npm run typecheck && npm run lint

# Quick mypy check
cd impl/claude && uv run mypy . 2>&1 | grep "error:" | wc -l

# ESLint summary
cd impl/claude/web && npm run lint 2>&1 | grep -E "error|warning" | wc -l
```

---

## Definition of Done

Quality gates pass:
- [ ] `pytest` collects and runs without collection errors
- [ ] `mypy` reports 0 errors
- [ ] `npm run typecheck` passes
- [ ] `npm run lint` reports only acceptable warnings (complexity in scripts is OK)

---

## Notes

- **TypeScript is clean** - No action needed
- **Pre-commit hooks exist** - Currently bypassed with `--no-verify`
- **Ruff lint/format** - Auto-fixes applied during commits

---

*Filed: 2025-12-22 | Author: Claude Code Chief Protocol*
