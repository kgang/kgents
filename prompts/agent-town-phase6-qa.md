# Agent Town Phase 6: QA Phase

**Predecessor**: `plans/_epilogues/2025-12-14-agent-town-phase6-implement.md`
**Phase**: QA (N-Phase 7 of 11)
**Ledger**: `{PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:touched, QA:in_progress}`

---

## Context

Phase 6 IMPLEMENT delivered:
- **CP4**: marimo widget display verified (25-citizen scatter)
- **CP5**: click→cell flow wired (scatter.clicked_citizen_id → citizen_details)
- **CP6**: 24 integration tests created (test_marimo_integration.py)
- **529 tests passing** in agents/town/_tests/
- **mypy/ruff clean** on modified files

### Artifacts from IMPLEMENT

| Artifact | Location | Status |
|----------|----------|--------|
| Integration tests | `agents/town/_tests/test_marimo_integration.py` | 24 tests |
| Widget fixes | `agents/i/marimo/widgets/scatter.py` | Import reorder |
| Epilogue | `plans/_epilogues/2025-12-14-agent-town-phase6-implement.md` | Complete |

### Laws Verified in IMPLEMENT

| Law | Test | Status |
|-----|------|--------|
| L1: points serialization | `test_points_serialization_schema` | ✓ |
| L2: sse_connected reflects state | `test_sse_status_tracking` | ✓ |
| L3: clicked_citizen_id triggers re-run | `test_click_sets_citizen_id` | ✓ |
| L4: SVG viewBox 400x300 | JS constant check | ✓ |
| L5: CSS transitions | JS style check | ✓ |
| L6: EventSource auto-reconnect | JS error handler check | ✓ |

---

## Scope

**QA Focus Areas**:
1. Static analysis (mypy, ruff) on ALL modified files
2. Security sweep (no secrets, no injection vectors)
3. Degraded mode testing (SSE disconnect, API unavailable)
4. Documentation hygiene (plan archiving)
5. Rollback plan verification

**Files to audit**:
- `agents/town/demo_marimo.py` — Type annotations, error handling
- `agents/i/marimo/widgets/scatter.py` — Traitlet safety
- `agents/i/marimo/widgets/js/scatter.js` — XSS prevention, error handling
- `agents/town/_tests/test_marimo_integration.py` — Test quality
- `agents/town/visualization.py` — Contract stability

---

## QA Manifesto

```
I will run all checks, not assume they pass.
I will exercise degraded modes, not trust happy paths.
I will audit documentation debt, not ignore stale plans.
I will verify rollback is possible, not hope it works.
I will capture findings, not hide technical debt.
```

---

## Actions

### 1. Static Analysis Pass
```bash
# Full lint pass
uv run ruff check agents/town/ agents/i/marimo/widgets/

# Full type check
uv run mypy agents/town/ agents/i/marimo/widgets/

# Security check (no hardcoded secrets)
grep -rn "password\|secret\|api_key\|token" agents/town/ agents/i/marimo/widgets/ --include="*.py" || echo "No secrets found"
```

### 2. Degraded Mode Testing
```python
# Test: Widget without town_id
scatter = EigenvectorScatterWidgetMarimo(town_id="")
assert scatter.sse_connected is False  # Should gracefully degrade

# Test: SSE disconnect simulation
scatter.sse_connected = False
scatter.sse_error = "Connection lost"
# Widget should still display cached points

# Test: Empty points list
scatter.points = []
# Widget should render empty state gracefully
```

### 3. Documentation Hygiene
- [ ] Check `plans/agent-town/` for archive candidates
- [ ] Verify epilogue captures all learnings
- [ ] Identify spec promotion candidates (functor laws → spec?)

### 4. Rollback Plan
```bash
# Verify changes can be reverted
git diff --stat HEAD~5..HEAD -- agents/town/ agents/i/marimo/

# List new files (would need manual deletion)
git status --porcelain agents/town/_tests/test_marimo_integration.py
```

### 5. Risk Sweep
| Risk | Mitigation | Status |
|------|------------|--------|
| JS injection via citizen_name | Names sanitized in ScatterPoint | Check |
| SSE memory leak | EventSource closed in cleanup | Check |
| Type errors in demo notebook | marimo cells don't require types | Acceptable |
| API unavailable | Widget shows cached data | Check |

---

## QA Checklist

- [ ] `uv run ruff check` — 0 errors
- [ ] `uv run mypy` — 0 errors (on widget/test files)
- [ ] Security sweep — No secrets, no injection vectors
- [ ] Degraded mode — Widget handles missing town_id, SSE disconnect
- [ ] Error messages — Clear, actionable, no stack traces to user
- [ ] Test coverage — 24 integration tests cover happy + edge cases
- [ ] Documentation — Epilogue complete, no stale plans
- [ ] Rollback — `git revert` possible for all changes

### Plans touched during this work
- `plans/_epilogues/2025-12-14-agent-town-phase6-implement.md` — Created

### Archive candidates
- None identified (Phase 6 is ongoing)

### Spec promotion candidates
- Functor laws (L1-L3) → Consider `spec/protocols/visualization-contracts.md`

---

## Exit Criteria

- [ ] All static analysis passes
- [ ] Degraded mode exercised (3 scenarios minimum)
- [ ] Security sweep clean
- [ ] Documentation hygiene checked
- [ ] Rollback plan verified
- [ ] QA findings captured (if any)

---

## Branch Candidates

- **Tech debt**: demo_marimo.py type annotations (defer to future cleanup)
- **Enhancement**: NATS multi-client support (Phase 7)
- **Spec**: Functor law formalization (deferred to REFLECT)

---

## Entropy Budget

- Allocated: 0.05
- Draw: `void.entropy.sip(amount=0.05)`
- Purpose: Edge case exploration, alternative lint rules

---

## Continuation

On success: `⟿[TEST]` — Verify correctness with focused test runs
On blocked: `⟂[QA:blocked]` — mypy/ruff/security errors require resolution

---

*Guard [phase=QA][entropy=0.05][law_check=true][minimal_output=true]*

---

## Auto-Inducer

⟿[QA]
/hydrate prompts/agent-town-phase6-qa.md
handles: scope=agent-town-phase6-qa-gate; impl_status=COMPLETE(CP4-CP6,24_tests,529_passing); static=mypy+ruff; security=sweep; degraded=SSE_disconnect+empty_points+no_town_id; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched,STRATEGIZE:touched,CROSS-SYNERGIZE:touched,IMPLEMENT:touched,QA:in_progress}; entropy=0.05
mission: gate quality before TEST; run full static analysis; exercise degraded modes; audit documentation; verify rollback; capture findings.
actions: Bash(uv run ruff check); Bash(uv run mypy); Python(degraded_mode_tests); Read(plans/); TodoWrite(qa_checklist); Write(qa_findings if any).
exit: all checks pass + degraded modes exercised → ledger.QA=touched; findings captured; continuation → TEST | static analysis fails → ⟂[QA:blocked].

---

**LAW**: This prompt auto-continues. The signifier `⟿[QA]` triggers immediate execution without human intervention. Halt conditions: mypy errors, ruff errors, security issues, or `⟂[HUMAN_INTERRUPT]`.
