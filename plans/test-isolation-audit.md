---
path: plans/test-isolation-audit
status: complete
priority: high
created: 2025-12-20
last_touched: 2025-12-20
touched_by: claude-opus-4
session_notes: |
  RESOLVED: Test isolation issues fixed.

  Root Cause:
  - _sip() tests used forest_node fixture but _sip() called _collect_plans_from_headers()
  - _collect_plans_from_headers() used _get_project_root() → real plans/ directory
  - Header.get("path", fallback()) eagerly evaluated fallback even when key existed

  Fix:
  1. Tests now create isolated tmp_path/plans/ with YAML-header mock plan files
  2. Tests override node._get_project_root = lambda: tmp_path
  3. PlanFromHeader.from_yaml_header() uses if/else instead of get() with fallback

  All 79 tests pass. Learnings added to meta.md.
---

# Test Isolation Audit: Principled Resolution

> *"DI > mocking: set_soul() injection pattern beats patch() for testability"* — meta.md

---

## The Problem

Pre-push hooks are failing due to **test isolation violations**. Tests are reading from the actual filesystem instead of using isolated fixtures, causing failures when plan files change.

### Failing Tests (Backend - Python)

```
FAILED protocols/agentese/contexts/_tests/test_forest.py::test_sip_selects_longest_dormant
FAILED protocols/agentese/contexts/_tests/test_forest.py::test_sip_empty_dormant
FAILED agents/i/reactive/projection/_tests/test_laws_property.py::TestGlyphProjectionProperties::test_identity_law_cli_property
```

**Root Cause**: `test_forest.py` tests are asserting on hardcoded plan names (`agents/t-gent`) but reading actual plan files from disk. When WARP plans were added, they became the "longest dormant" instead.

### Failing Tests (Frontend - TypeScript)

Many frontend tests failing with various issues (29 test files, 362 tests). These appear to be pre-existing failures, not new regressions.

---

## Investigation Steps

### 1. Audit test_forest.py

```bash
cd impl/claude
cat protocols/agentese/contexts/_tests/test_forest.py
```

Questions to answer:
- Is there a fixture that should provide mock plan data?
- Is there DI that should inject a mock forest state?
- Should tests use `tmp_path` or in-memory state?

### 2. Check the forest context implementation

```bash
cat protocols/agentese/contexts/forest.py
```

Questions:
- How does it discover plans? (filesystem scan vs registry?)
- Is there DI injection point for the plan source?
- Can we inject a mock plan provider?

### 3. Run tests in isolation

```bash
uv run pytest protocols/agentese/contexts/_tests/test_forest.py -v
```

### 4. Check property-based test failure

```bash
uv run pytest agents/i/reactive/projection/_tests/test_laws_property.py::TestGlyphProjectionProperties::test_identity_law_cli_property -v
```

This is a property-based test (Hypothesis) - it may be a flaky test or genuine law violation.

---

## Principled Fix Patterns

### Pattern 1: Fixture Injection (Preferred)

```python
@pytest.fixture
def mock_forest_state():
    """Isolated forest state with controlled plans."""
    return ForestState(
        plans={
            "agents/t-gent": PlanState(status="dormant", last_touched=...),
            "services/brain": PlanState(status="active", ...),
        }
    )

def test_sip_selects_longest_dormant(mock_forest_state):
    # Test uses injected state, not filesystem
    result = sip_entropy(mock_forest_state)
    assert result["selected_plan"] == "agents/t-gent"
```

### Pattern 2: DI Container Override

```python
def test_sip_selects_longest_dormant(container):
    # Override the plan provider in DI container
    container.register("plan_provider", lambda: MockPlanProvider())
    ...
```

### Pattern 3: Monkeypatch Filesystem Access

```python
def test_sip_selects_longest_dormant(monkeypatch, tmp_path):
    # Create controlled plan files in tmp_path
    (tmp_path / "plans" / "agents" / "t-gent.md").write_text("...")
    monkeypatch.setenv("KGENTS_PLANS_DIR", str(tmp_path / "plans"))
    ...
```

---

## Anti-Patterns to Avoid

```
❌ Hardcoding expected values that depend on filesystem state
❌ Skipping tests with pytest.skip() without fixing root cause
❌ Adding KGENTS_SKIP_HEAVY to CI (masks real issues)
❌ Marking tests as xfail without investigation
```

---

## Success Criteria

1. **All 3 Python tests pass** with proper isolation
2. **Tests don't depend on actual plan files** in the repository
3. **DI or fixtures** provide controlled test data
4. **Pre-push hook passes** without skip flags

---

## Execution Command

```bash
# Run the failing tests to reproduce
cd impl/claude
uv run pytest protocols/agentese/contexts/_tests/test_forest.py -v
uv run pytest agents/i/reactive/projection/_tests/test_laws_property.py::TestGlyphProjectionProperties::test_identity_law_cli_property -v

# After fixing, run full test suite
uv run pytest -x -q
```

---

## Context Files

- `protocols/agentese/contexts/_tests/test_forest.py` — failing tests
- `protocols/agentese/contexts/forest.py` — forest context implementation
- `CLAUDE.md` — see "Testing & DevEx" section for patterns
- `plans/meta.md` — see "Testing & DevEx" learnings

---

*Priority: High (blocking pushes) | Estimated: 1-2 hours | Type: Test Infrastructure*
