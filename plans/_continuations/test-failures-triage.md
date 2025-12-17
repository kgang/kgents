# Test Failures Triage

> **Priority**: High - blocking clean pushes
> **Created**: 2025-12-17
> **Context**: Discovered during aggressive archive push

## Your Mission

Investigate and fix the failing tests that are blocking clean pushes. These failures are pre-existing (not caused by recent changes) and need to be triaged and resolved.

## Failing Tests

### Python Tests (4 failures)

```
FAILED agents/b/_tests/test_persistent_hypothesis.py::test_storage_get_hypothesis_by_idx
FAILED agents/b/_tests/test_persistent_hypothesis.py::test_storage_evolution_history
FAILED protocols/synergy/_tests/test_drift_handler.py::TestGestaltToBrainHandler::test_skips_unsupported_events
FAILED infra/ghost/_tests/test_memory_collector.py::TestMemoryCollector::test_collect_includes_four_pillars
```

### Root Cause Hint (B-gent tests)

```
TypeError: PersistentHypothesisStorage.__init__() got an unexpected keyword argument 'path'
```

The B-gent tests are failing because the `PersistentHypothesisStorage` interface changed but tests weren't updated.

### Web Tests (3 failures)

```
FAIL tests/unit/elastic/elastic-laws.test.tsx
  - Law 3: ElasticCard visibility follows container width
  - Law 4: ElasticSplit ratio is preserved on resize
  - Law 5: Placeholder appears when width < minWidth
```

These appear to be timing/race condition issues in the elastic component tests.

## Approach

1. **Start with Python tests** - likely simpler fixes
   - Read the failing test files
   - Check the actual implementation for interface changes
   - Update tests to match current API

2. **Then web tests** - may need React testing adjustments
   - Check if `act()` wrapping is needed
   - Look for timing issues in resize observers

## Commands to Run

```bash
# Run just the failing Python tests
cd impl/claude
uv run pytest agents/b/_tests/test_persistent_hypothesis.py -v
uv run pytest protocols/synergy/_tests/test_drift_handler.py::TestGestaltToBrainHandler::test_skips_unsupported_events -v
uv run pytest infra/ghost/_tests/test_memory_collector.py::TestMemoryCollector::test_collect_includes_four_pillars -v

# Run just the failing web tests
cd impl/claude/web
npm test -- tests/unit/elastic/elastic-laws.test.tsx
```

## Success Criteria

- [ ] All 4 Python tests pass
- [ ] All 3 web tests pass
- [ ] Full test suite passes: `uv run pytest -m "not slow"` (should be ~18,700 tests)
- [ ] Web tests pass: `npm test` in `impl/claude/web/`
- [ ] Clean push works without `--no-verify`

## Files to Investigate

### Python
- `impl/claude/agents/b/_tests/test_persistent_hypothesis.py`
- `impl/claude/agents/b/persistent_hypothesis.py` (or similar - find the storage class)
- `impl/claude/protocols/synergy/_tests/test_drift_handler.py`
- `impl/claude/protocols/synergy/drift.py` (or handlers)
- `impl/claude/infra/ghost/_tests/test_memory_collector.py`
- `impl/claude/infra/ghost/memory_collector.py`

### Web
- `impl/claude/web/tests/unit/elastic/elastic-laws.test.tsx`
- `impl/claude/web/src/components/elastic/ElasticCard.tsx`
- `impl/claude/web/src/components/elastic/ElasticSplit.tsx`

## Notes

- These failures are **pre-existing** - they weren't caused by recent changes
- The codebase has 18,700+ passing tests, so this is a small subset
- Focus on fixing, not refactoring - minimal changes to green the tests
- If a test is testing outdated behavior, update the test (not the impl)

---

*When done, commit with message: `fix(tests): Resolve pre-existing test failures`*
