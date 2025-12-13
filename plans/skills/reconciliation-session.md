# Skill: Reconciliation Session

> Audit, surface, and sync the forest state—making invisible progress visible.

**Difficulty**: Medium
**Prerequisites**: Understanding of Forest Protocol, plan YAML headers, _forest.md structure
**Files Touched**: `plans/_forest.md`, `plans/_status.md`, `plans/meta.md`, `plans/_epilogues/`
**References**: `plans/principles.md`, `spec/principles.md`

---

## Overview

A reconciliation session audits the planning forest for drift between declared state and actual state, surfaces completed work through demos, and updates meta files to reflect reality. This is **Chief of Staff work**—tending the forest, not implementing features.

### When to Use

- After major work completes (like turn-gents 7 phases)
- When the user asks to "check on" a plan
- When _forest.md feels stale
- Before starting new initiatives (clear the decks)
- Periodically (weekly) as forest maintenance

### The Core Insight

**Runnable beats readable for validation.** A demo script that runs proves completion more than status updates. When auditing:

1. **Read the forest** — understand declared state
2. **Verify through code** — run tests, check files exist
3. **Surface via demo** — make invisible work visible
4. **Update status** — sync meta files to reality

---

## Step-by-Step

### Step 1: Quality Gate First

Before reading anything, verify the forest is healthy:

```bash
cd impl/claude

# Type check
uv run mypy . --no-error-summary 2>&1 | tail -10

# Test count (are we growing?)
uv run pytest --collect-only -q 2>/dev/null | tail -3
```

**Why first?** This prevents drift—you fix issues before they compound. If mypy errors exist, fix them before anything else.

**Exit criteria**: Zero mypy errors in production code. Tests collect successfully.

### Step 2: Read the Forest

Read in this order (dependencies flow down):

1. `plans/_focus.md` — Human intent (READ ONLY)
2. `plans/_forest.md` — Current canopy view
3. `plans/_status.md` — Detailed component status
4. Target plan file (e.g., `plans/architecture/turn-gents.md`)
5. Recent epilogues (`plans/_epilogues/` last 3 days)

**Pattern**: Compare _forest.md claims against actual files:

```bash
# Does the code exist?
ls impl/claude/weave/*.py

# How many tests?
uv run pytest weave/_tests/ --collect-only -q 2>/dev/null | tail -3
```

**Exit criteria**: You understand the declared vs. actual state gap.

### Step 3: Verify Through Code

For each claimed completion, verify through code:

```python
# Claimed: "Turn schema complete with 46 tests"
# Verify:
uv run pytest weave/_tests/test_turn.py -v --tb=no 2>&1 | tail -10
# → Count actual tests, verify they pass
```

**Anti-pattern**: Trusting status files without verification.

**Exit criteria**: You have empirical evidence of completion state.

### Step 4: Fix Drift

If you find issues:

1. **Mypy errors**: Fix surgically (one type annotation, minimal change)
2. **Test failures**: Investigate root cause, fix
3. **Missing files**: Note in session_notes, don't fabricate
4. **Stale counts**: Update with actual numbers

**Pattern**: Surgical fixes > sweeping changes

```python
# Example: Type narrowing fix in inference.py
# Before: sum(1 for b in budgets.values() if b.free_energy > 0)
# After: len([b for b in budgets.values() if b.free_energy > 0])
# → One-line fix, resolves mypy error
```

**Exit criteria**: Quality gate passes again.

### Step 5: Surface Via Demo

Create a demo script if one doesn't exist. This makes invisible work visible:

```python
# File: qa/demo_<feature>.py
"""
Demo script for <Feature>.

Showcases:
1. Core capability A
2. Core capability B
3. Integration point C

Run with:
    uv run python qa/demo_<feature>.py
"""
```

**Key sections in a good demo**:
- **What to show**: Each major capability demonstrated
- **Why it matters**: Brief explanation of purpose
- **Integration points**: Show how it connects to other systems

**Pattern**: Demo functions should be runnable independently:

```python
def demo_feature_a() -> None:
    """Demonstrate feature A."""
    console.print("\n[bold cyan]1. Feature A[/bold cyan]")
    # Actual working code, not pseudocode
    result = actual_function()
    console.print(f"Result: {result}")
```

**Exit criteria**: `uv run python qa/demo_<feature>.py` runs without error.

### Step 6: Update Forest Documentation

Update meta files to reflect verified reality:

**Order matters** (dependencies):

1. **Plan YAML header** — Update progress, status, session_notes
2. **_forest.md** — Update tables, dependency graph
3. **_status.md** — Update component tables with verified counts
4. **_epilogues/** — Write session epilogue

**Pattern**: Atomic updates with evidence:

```yaml
# In plan file header:
progress: 100  # Was 0, now verified complete
status: complete  # Was proposed
session_notes: |
  All 7 phases verified complete. 187 tests passing.
  Demo: qa/demo_turn_gents.py
  Integration points identified: memory, dashboard, k-gent, polynomial.
```

**Exit criteria**: Meta files reflect empirical reality.

### Step 7: Write Epilogue

Create `plans/_epilogues/YYYY-MM-DD-<session-type>.md`:

```markdown
# Session Epilogue: YYYY-MM-DD <Type>

## What We Did
- [Specific actions taken]

## What We Verified
- [Test counts, mypy status, demo runs]

## Integration Synergies
- [Cross-references discovered]

## What's Next
- [Concrete next steps for future sessions]
```

**Exit criteria**: Future agents can continue from your epilogue.

---

## Verification Checklist

Before completing a reconciliation session:

- [ ] Quality gate passes (mypy clean, tests collect)
- [ ] Target plan files read and understood
- [ ] Claimed completions verified through code
- [ ] Drift fixed (mypy errors, test failures)
- [ ] Demo script created/updated and runs
- [ ] _forest.md updated with verified state
- [ ] _status.md updated with actual test counts
- [ ] Epilogue written for next session
- [ ] meta.md updated with atomic learning (if novel insight)

---

## Common Pitfalls

### 1. Trusting Status Without Verification

```
# BAD: Just update _forest.md based on plan file claims
# GOOD: Run tests, check files exist, verify completion
```

### 2. Sweeping Fixes Instead of Surgical

```python
# BAD: Refactor entire file to fix one type error
# GOOD: Add one type annotation to fix the specific error
```

### 3. Forgetting the Demo

```
# BAD: Update status files, claim complete
# GOOD: Create runnable demo that proves functionality
```

### 4. Not Writing Epilogue

```
# BAD: Session ends without state capture
# GOOD: Epilogue enables future session continuity
```

### 5. Modifying _focus.md

```
# BAD: Agent updates human intent file
# GOOD: _focus.md is READ ONLY for agents
```

---

## The Reconciliation Equation

```
Reconciliation =
    quality_gate()
    >> read_forest()
    >> verify_through_code()
    >> fix_drift()
    >> surface_via_demo()
    >> update_status()
    >> write_epilogue()
```

Each step depends on the previous. Skip none.

---

## Success Metrics

A successful reconciliation session:

| Metric | Target |
|--------|--------|
| Mypy errors | 0 (in production code) |
| Tests passing | All collected tests pass |
| Demo runs | Exit code 0 |
| _forest.md | Reflects verified reality |
| Epilogue | Written with next steps |

---

## Related Skills

- [plan-file](plan-file.md) — Writing plan files with YAML headers
- [test-patterns](test-patterns.md) — Verifying through tests
- [handler-patterns](handler-patterns.md) — CLI patterns for demos

---

## Changelog

- 2025-12-13: Initial version from turn-gents reconciliation session
