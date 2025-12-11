# Mypy Error Elimination Plan

**Initial state**: 7,516 strict errors baselined
**Current state**: 3,896 strict errors (48% reduction)
**Goal**: Zero mypy errors under `--strict`

## Progress Summary

| Phase | Description | Errors Fixed |
|-------|-------------|--------------|
| Phase 1 | Add `-> None` to test functions | ~6,304 |
| Phase 2 | Fix fixture return types | ~128 |
| Phase 3 | Fix source file annotations | ~76+ |
| **Total** | | **3,620 errors fixed** |

## Remaining Error Distribution (3,896 errors)

| Error Type | Count | % | Fix Strategy |
|------------|-------|---|--------------|
| Missing type annotations (`no-untyped-def`) | ~1,690 | 43% | Add function signatures |
| Missing variable annotations (`var-annotated`) | ~415 | 11% | Add type annotations |
| Untyped calls (`no-untyped-call`) | ~338 | 9% | Type external functions |
| Missing generic type params (`type-arg`) | ~288 | 7% | Add `dict[str, Any]` etc |
| Argument type mismatch (`arg-type`) | ~290 | 7% | Fix type mismatches |
| Union attribute access (`union-attr`) | ~196 | 5% | Narrow types properly |
| Other (index, operator, etc) | ~679 | 18% | Case-by-case |

## Phase 1: Automated Test Function Annotations (~5,000 errors)

**Strategy**: Create script to add `-> None` to all test functions missing return types.

Target files (by error count):
1. `agents/m/test_m_gents.py` (293)
2. `agents/o/_tests/test_o_gent.py` (291)
3. `agents/i/_tests/test_semantic_field.py` (270)
4. `agents/r/_tests/test_advanced.py` (189)
5. `agents/b/_tests/test_jit_efficiency.py` (184)
... (25+ more test files with 80+ errors each)

**Automation approach**:
```python
# Pattern: def test_xxx(...): → def test_xxx(...) -> None:
# Pattern: async def test_xxx(...): → async def test_xxx(...) -> None:
```

## Phase 2: Source File Type Annotations (~500 errors)

Key source files needing attention:
- `agents/p/core.py` - Parser base class
- `agents/d/lens.py` - Missing dict type params
- `agents/d/queryable.py` - Any returns
- `agents/b/jit_efficiency.py` - Missing annotations
- `agents/p/strategies/*.py` - Various issues

## Phase 3: Generic Type Parameters (~200 errors)

- Replace `dict` → `dict[str, Any]`
- Replace `list` → `list[Any]`
- Replace `Callable` → `Callable[..., Any]`

## Phase 4: Complex Type Issues (~200 errors)

- Union attribute access (`union-attr`)
- Index type mismatches
- Return type overrides
- Liskov substitution violations

## Commands

```bash
# Check current errors
cd impl/claude && uv run mypy --strict --explicit-package-bases agents/ bootstrap/ runtime/ 2>&1 | uv run mypy-baseline filter

# Re-sync baseline after fixes
cd impl/claude && uv run mypy --strict --explicit-package-bases agents/ bootstrap/ runtime/ 2>&1 | uv run mypy-baseline sync
```
