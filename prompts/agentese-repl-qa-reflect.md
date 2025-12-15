# AGENTESE REPL Crown Jewel: QA → REFLECT Phase

> *"The interface that teaches its own structure through use is no interface at all."*

**Phase**: QA → TEST → MEASURE → REFLECT (Wave 2 → Wave 3 Transition)
**Plan**: `plans/devex/agentese-repl-crown-jewel.md`
**Ledger**: `{PLAN:touched, RESEARCH:touched, DEVELOP:skipped, STRATEGIZE:touched, IMPLEMENT:complete, QA:in_progress}`
**Entropy**: 0.05

---

## Context

Wave 2 of the AGENTESE REPL is **COMPLETE**:
- Async execution via Logos (`asyncio.run` per command)
- Pipeline execution (`>>` composition actually runs)
- Observer/Umwelt context switching (`/observer` commands)
- Rich output rendering (tables, panels, colors via `rich`)
- Error sympathy (errors suggest next actions)
- Comprehensive documentation (`docs/skills/agentese-repl.md`)

**Files Modified**:
- `protocols/cli/repl.py` (Wave 2 enhancements)
- `plans/devex/agentese-repl-crown-jewel.md` (progress updated)
- `plans/_forest.md` (65% progress)
- `plans/meta.md` (2 learnings added)
- `docs/skills/agentese-repl.md` (NEW: 551-line guide)
- `docs/skills/README.md` (index updated)

**Tests**: 1338 CLI tests pass | **Mypy**: 0 errors

---

## QA Phase Mission

Verify the REPL is clean, explainable, and reversible before formal testing.

### QA Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Mypy | `uv run mypy protocols/cli/repl.py --ignore-missing-imports` | Success: 0 errors |
| Ruff | `uv run ruff check protocols/cli/repl.py` | No errors |
| CLI Tests | `uv run pytest protocols/cli/ -q` | 1338+ pass |
| Basic REPL | `echo "?\nexit" \| kg -i` | Shows affordances, exits cleanly |
| Navigation | `echo "self\nstatus\n..\nworld\nexit" \| kg -i` | Context switches work |
| Observer | `echo "/observer\n/observer developer\n/observers\nexit" \| kg -i` | Observer commands work |
| Pipeline | `echo "self status >> world agents\nexit" \| kg -i` | Pipeline executes |
| Ctrl+C | Interactive: press Ctrl+C | Shows hint, doesn't crash |

### Degraded Mode Testing

| Scenario | Expected Behavior |
|----------|-------------------|
| Logos unavailable | Falls back to CLI routing |
| Rich not installed | Uses ANSI fallback |
| Observer invalid | Sympathetic error with suggestions |
| Path not found | Sympathetic error with hints |

### Risk Sweep

| Risk | Mitigation |
|------|------------|
| `asyncio.run()` nested loop | Each command is independent |
| Tab completion edge cases | Graceful empty list return |
| Observer cache stale | Invalidated on archetype change |

---

## TEST Phase Mission

Add integration tests for the REPL that verify Wave 2 features.

### Test Categories

| Category | Focus | File |
|----------|-------|------|
| Unit | State management, path parsing | `protocols/cli/_tests/test_repl_unit.py` |
| Integration | Full REPL interactions | `protocols/cli/_tests/test_repl_integration.py` |
| Regression | Ensure Wave 1 still works | Existing test coverage |

### Test Design (Wave 2 Features)

```python
# Test ideas (not exhaustive):

def test_observer_switching():
    """Verify /observer command changes archetype."""

def test_observer_prompt_indicator():
    """Verify prompt shows (E), (D), (A), (*) correctly."""

def test_pipeline_execution():
    """Verify >> executes both paths."""

def test_logos_fallback():
    """Verify CLI fallback when Logos unavailable."""

def test_rich_fallback():
    """Verify ANSI fallback when rich unavailable."""

def test_error_sympathy():
    """Verify errors include suggestions."""

def test_context_switching_from_within():
    """Verify can switch context (e.g., self → world) from anywhere."""
```

---

## EDUCATE Phase (ALREADY COMPLETE)

Documentation created: `docs/skills/agentese-repl.md` (551 lines)

Covers:
- Getting Started
- The Five Contexts
- Observer Archetypes
- Pipeline Composition
- Starter Pack Implementations
- Meta-Cognition: Evolving Workflow
- Maintenance & Extension Patterns
- Ideation Garden

---

## MEASURE Phase Mission

Instrument the REPL for usage telemetry.

### Metrics to Capture

| Metric | Type | Purpose |
|--------|------|---------|
| `repl.session.duration` | Timer | How long sessions last |
| `repl.command.count` | Counter | Commands per session |
| `repl.context.navigation` | Counter | Which contexts visited |
| `repl.observer.switches` | Counter | Observer archetype changes |
| `repl.pipeline.executions` | Counter | Pipeline usage frequency |
| `repl.errors.count` | Counter | Error rate |
| `repl.logos.fallback` | Counter | How often Logos unavailable |

### Implementation Approach

1. **Optional telemetry**: Respect `KGENTS_TELEMETRY_ENABLED`
2. **Lightweight**: Don't slow down REPL responsiveness
3. **Privacy**: No command content, only patterns

---

## REFLECT Phase Mission

Synthesize outcomes, extract learnings, and seed Wave 3.

### Outcomes to Capture

- What shipped in Wave 2
- What worked well (async architecture, observer pattern)
- What was harder than expected
- What emerged as candidates for Wave 3

### Learnings Format (Molasses Test)

One-line zettels for `plans/meta.md`:
```
2025-12-14  REPL observer wrapper: frozen Umwelt needs mutable wrapper for cache tracking
2025-12-14  REPL architecture: Logos → CLI fallback enables graceful degradation across maturity levels
```

### Wave 3 Seeds

| Candidate | Priority | Notes |
|-----------|----------|-------|
| Fuzzy matching | Medium | Typo tolerance |
| Session persistence | Low | Resume from last location |
| Tutorial mode | Medium | `--tutorial` flag |
| LLM suggestions | High | "Did you mean..." |
| Script mode | Medium | `kg -i < script.repl` |
| REPL-as-TUI | High | Evolve into Textual app |

---

## Actions

1. **QA**: Run full checklist, fix any issues
2. **TEST**: Add integration tests for Wave 2 features
3. **MEASURE**: Add telemetry hooks (deferred if time-constrained)
4. **REFLECT**: Write epilogue, update meta.md, seed Wave 3

---

## Exit Criteria

| Criterion | Met? |
|-----------|------|
| QA checklist passes | [ ] |
| Integration tests added | [ ] |
| Telemetry hooks added OR deferred with timebox | [ ] |
| Epilogue written | [ ] |
| Wave 3 seeds captured | [ ] |
| meta.md updated | [ ] |

---

## Continuation Generator

### On QA Complete (auto-continue to TEST):

```markdown
⟿[TEST]
/hydrate
handles: qa=passed; static=mypy+ruff clean; degraded=verified; ledger={QA:touched}; entropy=0.05
mission: add integration tests for Wave 2 features; use fixtures; verify observer/pipeline/fallback.
exit: tests pass; coverage increased; continuation → MEASURE or REFLECT.
```

### On TEST Complete (choose MEASURE or skip to REFLECT):

```markdown
⟿[MEASURE]
/hydrate
handles: tests=passing; coverage=${coverage}; ledger={TEST:touched}; entropy=0.03
mission: add telemetry hooks for REPL usage patterns.
exit: metrics instrumented OR deferred with timebox; continuation → REFLECT.
```

### On REFLECT Complete (session end or Wave 3):

```markdown
⟂[DETACH:cycle_complete] Epilogue: plans/_epilogues/2025-12-14-agentese-repl-wave2.md
```

OR

```markdown
⟿[PLAN]
/hydrate
handles: learnings=${wave2_learnings}; seeds=${wave3_seeds}; ledger={REFLECT:touched}
mission: frame Wave 3 scope (LLM integration, REPL-as-TUI, tutorial mode).
exit: scope defined; attention budget set; continuation → RESEARCH.
```

---

## Invocation

```
/hydrate
handles: plan=plans/devex/agentese-repl-crown-jewel.md; ledger={IMPLEMENT:complete, QA:in_progress}; entropy=0.05
mission: Complete QA → TEST → REFLECT for Wave 2; seed Wave 3.
exit: Wave 2 fully validated; epilogue written; Wave 3 seeds in plan.
```

---

⟿[QA]
