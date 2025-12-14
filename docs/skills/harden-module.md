# Skill: Module Hardening

Hardening is the process of making a module robust, type-safe, and production-ready through systematic verification.

## When to Use

- Before merging significant changes
- When a module has accumulated debt
- After major API refactors
- Periodically for demo/integration files (they drift)

## Process

### 1. Lint Check (ruff)

```bash
cd impl/claude && uv run ruff check <target>
```

**Common fixes**:
- Prefix unused variables with `_`
- Convert one-line lambdas to `def` when cleaner
- Remove unused imports

### 2. Type Check (mypy)

```bash
cd impl/claude && uv run mypy <target> --strict
```

**Common fixes**:
- Add explicit type parameters: `App[object]` not `App`
- Use `cast()` for test mocks
- Add type narrowing: `assert x is not None` before accessing

**Demo file exception**: If a file uses notebook patterns (`@app.cell`), add:
```python
# mypy: ignore-errors
```

### 3. Test Verification

```bash
cd impl/claude && uv run pytest <target>/_tests/ -v
```

### 4. Bug Pattern Recognition

Watch for these patterns:

#### Pattern A: Demo File Drift
- **Signal**: Type errors in demo/example files
- **Cause**: APIs evolved, demos didn't
- **Fix**: Update demos to current API usage

#### Pattern B: External Library Mismatch
- **Signal**: Type errors in integration code (Textual, FastAPI, etc.)
- **Cause**: Mental model differs from actual API
- **Fix**: Read library source, adjust signatures

### 5. Document Decisions

If making non-obvious choices:
- Renaming to avoid collisions (`layout` → `flex_layout`)
- Adding `# mypy: ignore-errors` to specific files
- Breaking API changes (e.g., adding required parameters)

Document in the epilogue.

## Exit Criteria

| Check | Target |
|-------|--------|
| `ruff check` | 0 errors |
| `mypy --strict` | 0 errors (or only pre-existing `import-untyped`) |
| `pytest` | All pass |
| Real bugs | Fixed and documented |

## Anti-Patterns

- **Don't ignore warnings globally**: Fix them or document why specific ignores are acceptable
- **Don't add `# type: ignore` without comment**: Always explain why
- **Don't skip test runs**: Type-correct code can still have logic bugs

## Priority Order for Harden Targets

1. **Recently modified** — Changes may have introduced issues
2. **Integration layers** — `protocols/api/`, external library adapters
3. **Demo files** — High drift rate, low test coverage
4. **Pre-existing debt** — `import-untyped`, deprecation warnings

## Example Session

```bash
# Target: agents/i/reactive/adapters/
uv run ruff check agents/i/reactive/adapters/
# Fix: 7 errors (unused vars)

uv run mypy agents/i/reactive/adapters/ --strict
# Fix: 82 errors (type params, narrowing, API mismatches)
# Discovered: 4 real bugs (Clock API, FocusSync signature)

uv run pytest agents/i/reactive/adapters/_tests/ -v
# All pass

# Document in epilogue
```

## Related Skills

- `test-patterns.md` — Testing conventions
- `handler-patterns.md` — CLI handler patterns
- `three-phase.md` — Research → Develop → Implement cycle
