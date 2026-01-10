# Mypy Improvement Continuation Prompt

> **For next agent session**: Copy this prompt to continue mypy improvements.

---

## Context

We completed Phase 1 of mypy improvements (2025-01-10):
- **714 → 639 errors** (10.5% reduction) via config changes
- Added test_*.py patterns, example file patterns, excluded _archive/ and scripts/
- Removed dead module configs (K8s operators, protocols/prompt/, etc.)
- Created `docs/skills/mypy-best-practices.md`

---

## Continuation Prompt

```
/hydrate mypy continuation

Continue improving the mypy system in impl/claude. Phase 1 config improvements are done.

## Your Tasks (Priority Order)

### 1. Install Type Stubs (Quick Win)
Add to pyproject.toml [dependency-groups] dev:
- types-redis
- types-stripe

Then remove these sections from mypy.ini:
- [mypy-redis.*]
- [mypy-stripe.*]

Run mypy to verify error reduction.

### 2. Fix Systematic Errors (High Value)

**services/witness/persistence.py (~29 errors)**
- Model attribute mismatches (WitnessTrust, WitnessAction, WitnessEscalation)
- Likely schema drift - check SQLAlchemy models vs usage

**agents/t/truth_functor.py (~8 errors)**
- Missing type parameters for generic TruthFunctor[S, A, B]
- Add explicit type params at usage sites

**services/zero_seed/navigation.py (~5 errors)**
- Missing dict type parameters
- Change `dict` → `dict[str, Any]` or specific types

### 3. Fix Blanket Type Ignores (Medium Effort)
Run: `uv run mypy . 2>&1 | grep "type: ignore" | wc -l`

Convert blanket ignores to specific error codes:
```python
# Before
x = foo()  # type: ignore

# After
x = foo()  # type: ignore[arg-type]
```

Once fixed, enable in mypy.ini:
```ini
enable_error_code = ignore-without-code
```

### 4. Address Override Errors (18 total)
These indicate Liskov substitution violations. Key files:
- services/kgentsd/pty_bridge.py
- agents/t/truth_functor.py
- agents/t/probes/witness_probe.py

Either fix signatures or add targeted `disable_error_code = override`.

## Reference

- Current mypy.ini: impl/claude/mypy.ini (1034 lines)
- Best practices doc: docs/skills/mypy-best-practices.md
- Error breakdown by type saved in research from Phase 1

## Success Criteria

- Error count < 550 (from current 639)
- No new `ignore_errors = True` added
- All changes documented with reasoning
```

---

*Created: 2025-01-10*
