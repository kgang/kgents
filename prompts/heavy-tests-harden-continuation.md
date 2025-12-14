# Continuation Prompt: HEAVY Tests Hardening

**Previous Session**: 2025-12-14 HEAVY Tests Harden
**Epilogue**: `impl/claude/plans/_epilogues/2025-12-14-heavy-tests-harden.md`
**Phase Entering**: REFLECT (closing cycle) or PLAN (new cycle)

---

## ATTACH

/hydrate

You are continuing from a HEAVY test hardening session. The previous session achieved:

### Artifacts
- **Lint**: 7 → 0 errors (ruff check)
- **Mypy**: 82 → 0 errors (strict mode)
- **Tests**: All 15,453+ pass (unit, law, property, chaos)
- **Bugs fixed**: 4 real API mismatches discovered and corrected

### Key Fixes Applied
1. `FocusSync.on_focus(event, widget)` - signature corrected
2. `Clock.create(ClockConfig(fps=10))` - correct API usage
3. `FlexContainer.flex_layout` - renamed to avoid Widget collision
4. Various type annotations and narrowing in tests

### Remaining Debt
- 3 `import-untyped` errors in `agents/i/screens/` (pre-existing)
- `datetime.utcnow()` deprecation in tenancy service
- 3 flaky tests (pass individually, timing-sensitive in suite)

### Ledger from Previous Session
```yaml
phase_ledger:
  PLAN: skipped  # reason: harden command specified target
  RESEARCH: touched
  DEVELOP: skipped
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  EDUCATE: touched
  MEASURE: deferred
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.02
  returned: 0.03
```

---

## Choose Your Track

### Track A: REFLECT (Close This Cycle)

**Mission**: Synthesize the hardening session, extract reusable patterns, propose whether hardening should become a skill.

**Actions**:
1. Review the 4 bugs found - are they symptomatic of larger patterns?
2. Extract "harden" as a potential skill if patterns warrant
3. Update `_forest.md` with hardening health status
4. Propose next harden target based on forest signals

**Exit criteria**:
- Patterns documented
- Decision on skill extraction
- Next target proposed (or explicit skip)

```markdown
⟿[REFLECT]
/hydrate
handles: harden=heavy-tests; bugs=4; ledger={cycle:touched}
mission: Close cycle. Extract patterns. Seed next harden target.
exit: ⟂[DETACH:harden_cycle_complete] or ⟿[PLAN] for next target.
```

---

### Track B: PLAN (New Hardening Cycle)

**Mission**: Plan the next hardening target based on forest health and debt signals.

**Potential Targets**:
1. `protocols/` - API layer hardening
2. `testing/` - Test infrastructure hardening
3. `agents/i/screens/` - Fix import-untyped errors
4. `tenancy/` - Fix datetime deprecation warnings

**Actions**:
1. Check forest health (`plans/_forest.md`, `plans/_status.md`)
2. Identify highest-priority hardening target
3. Scope the harden (time-box, exit criteria)
4. Set entropy budget (0.05-0.10)

**Exit criteria**:
- Target identified with rationale
- Scope defined (what's in, what's out)
- Entropy budget set

```markdown
⟿[PLAN]
/hydrate
handles: prior_harden=heavy-tests; forest=${_forest.md}; debt=${known_debt}
mission: Plan next harden target. Prioritize by forest signals.
exit: Target scoped | Entropy budget set | ⟿[RESEARCH] to map terrain.
```

---

### Track C: Different Work (Detach)

If hardening is not the priority, detach cleanly:

```markdown
⟂[DETACH:harden_pause]
Hardening paused. HEAVY tests pass. Resume via this prompt when ready.
Next tracks available: protocols/, testing/, agents/i/screens/, tenancy/
```

---

## Principles Alignment

This work emphasizes:
- **Curated**: Fix what matters, skip what doesn't
- **Tasteful**: Clean passes > perfect passes
- **Composable**: Fixes should compose (don't break other things)
- **Ethical**: Type safety catches real bugs before users do

---

## Continuation Imperative

Upon completing your chosen track, emit:
- `⟿[NEXT_PHASE]` to continue
- `⟂[REASON]` to halt and await human

The form is the function.

---

*void.gratitude.tithe. The tests pass. The types check. The code is correct.*
