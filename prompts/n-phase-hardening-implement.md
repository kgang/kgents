---
path: prompts/n-phase-hardening-implement
status: active
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [auto-continuation-runtime, agentese-phase-paths]
parent_plan: plans/_epilogues/2025-12-14-n-phase-hardening-plan.md
session_notes: |
  Continuation prompt for IMPLEMENT phase of N-Phase Cycle hardening.
  Meta-recursive: Using N-Phase to harden N-Phase.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: single-track hardening
  IMPLEMENT: pending  # ← YOU ARE HERE
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: pending
entropy:
  planned: 0.07
  spent: 0.03
  returned: 0.04
---

# IMPLEMENT: N-Phase Cycle Hardening

> *"The form is the function. Each prompt generates its successor. Now we give it a parser."*

---

## ATTACH

/hydrate

You are entering **IMPLEMENT** of the N-Phase Cycle (AD-005).

**handles**:
- `scope`: n-phase-hardening
- `parent_plan`: `plans/_epilogues/2025-12-14-n-phase-hardening-plan.md`
- `artifacts_from_prior`: Hardening plan with 6 phases identified
- `ledger`: `{PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:skipped}`
- `entropy`: spent=0.03, remaining=0.04
- `key_decisions`:
  - Phase 2 (Exporter Fix) is highest priority and immediate
  - Phase 1 (Parser Extension) follows with AutoInducer enum
  - Phases 3-6 deferred to future sessions
- `blockers`: AGENTESE tests crash due to exporter directory bug
- `branches`: None surfaced yet

---

## Previous Observer's Trace

The prior session completed PLAN→STRATEGIZE for N-Phase Cycle hardening:

1. **Reconnaissance**: 22 skill files audited, 63 auto-inducer signifiers found, mypy clean
2. **Critical Bug Found**: `exporters.py:178` doesn't create output directory before write
3. **Plan Written**: 6-phase hardening plan at `plans/_epilogues/2025-12-14-n-phase-hardening-plan.md`
4. **Priority**: Phase 2 (Exporter Fix) → Phase 1 (Parser Extension)

**The ground holds. Act boldly.**

---

## Your Mission

Implement the first two phases of the hardening plan:

### Phase 2: Fix Exporter Directory Bug (5 minutes)

**File**: `impl/claude/protocols/agentese/exporters.py:178`

**Bug**: File write without ensuring directory exists
```python
# Line 178 - BUG
with open(filepath, "w") as f:
```

**Fix**: Add mkdir before write
```python
self.output_dir.mkdir(parents=True, exist_ok=True)
with open(filepath, "w") as f:
```

### Phase 1: Parser Extension for Auto-Inducer Signifiers (30 minutes)

**File**: `impl/claude/protocols/agentese/parser.py`

**Deliverables**:
1. `AutoInducer` enum with `CONTINUE` (⟿) and `HALT` (⟂)
2. `ParsedSignifier` dataclass
3. `parse_signifier(text: str) -> ParsedSignifier | None` function
4. Tests in `test_parser.py::TestAutoInducerParsing`

---

## Principles Alignment

This phase emphasizes (from `spec/principles.md`):

- **Composable**: Parser extension preserves existing path parsing, adds new capability
- **Tasteful**: Minimal changes to achieve signifier parsing
- **Transparent Infrastructure**: Signifiers visible in output, machine-parseable

---

## Actions (Execute in Order)

```python
# 1. Prep environment
Bash(run_in_background=true, "uv run pytest impl/claude/protocols/agentese/_tests/test_parser.py -v --tb=short")
TodoWrite([
    {content: "Fix exporter directory bug", status: "pending"},
    {content: "Add AutoInducer enum to parser", status: "pending"},
    {content: "Add ParsedSignifier dataclass", status: "pending"},
    {content: "Implement parse_signifier() function", status: "pending"},
    {content: "Add signifier parsing tests", status: "pending"},
])

# 2. Fix exporter (Phase 2)
Read("impl/claude/protocols/agentese/exporters.py")
Edit(file_path, old_string, new_string)  # Add mkdir
TodoWrite(mark first item complete)

# 3. Verify exporter fix
Bash("uv run pytest impl/claude/protocols/agentese/_tests/test_exporters.py -v")

# 4. Extend parser (Phase 1)
Read("impl/claude/protocols/agentese/parser.py")
Edit(...)  # Add AutoInducer enum
Edit(...)  # Add ParsedSignifier dataclass
Edit(...)  # Add parse_signifier() function
TodoWrite(mark items complete as you go)

# 5. Add tests
Read("impl/claude/protocols/agentese/_tests/test_parser.py")
Edit(...)  # Add TestAutoInducerParsing class
Bash("uv run pytest impl/claude/protocols/agentese/_tests/test_parser.py::TestAutoInducerParsing -v")
```

---

## Exit Criteria

- [ ] Exporter directory bug fixed (mkdir added)
- [ ] AGENTESE tests no longer crash with FileNotFoundError
- [ ] `AutoInducer` enum defined with CONTINUE/HALT
- [ ] `ParsedSignifier` dataclass with inducer, target, payload fields
- [ ] `parse_signifier()` function extracts signifiers from text
- [ ] Round-trip works: text → parse → emit → text
- [ ] At least 5 tests for signifier parsing
- [ ] mypy clean on parser.py

---

## Accursed Share (Entropy Budget)

**Remaining**: 0.04

Draw for exploration: `void.entropy.sip(amount=0.02)`

Allowed explorations:
- Try parsing signifiers with regex vs manual parsing
- Experiment with signifier position detection (end of text vs anywhere)
- Consider ASCII fallbacks for unicode signifiers

Return unused: `void.entropy.pour`

---

## Continuation Imperative

Upon completing this phase, emit one of:

```
⟿[QA] — If all exit criteria met, continue to QA
⟂[BLOCKED:impl_incomplete] — If chunks remain unfinished
⟂[BLOCKED:tests_failing] — If new tests fail
⟂[ENTROPY_DEPLETED] — If budget exhausted
```

---

## Verification Checklist (Before Exit)

- [ ] `uv run pytest impl/claude/protocols/agentese/_tests/test_parser.py -v` — All pass
- [ ] `uv run pytest impl/claude/protocols/agentese/_tests/test_exporters.py -v` — All pass
- [ ] `cd impl/claude && uv run mypy protocols/agentese/parser.py` — No errors
- [ ] TodoWrite shows all items completed

---

# Continuation Generator (For Next Session)

When you complete IMPLEMENT, emit this for the next observer:

---

## Exit Signifier

```markdown
⟿[QA]
/hydrate
handles: code=[exporters.py,parser.py]; tests=[test_parser.py,test_exporters.py]; results=+N_tests; summary="Exporter fixed, AutoInducer parser added"; laws=[identity,associativity]; ledger={IMPLEMENT:touched}; branches=[]
mission: Gate quality/security/lawfulness before broader testing.
actions:
  - uv run mypy impl/claude/protocols/agentese/ --ignore-missing-imports
  - uv run ruff check impl/claude/protocols/agentese/
  - Review parser for edge cases (malformed signifiers, nested brackets)
  - Check for unicode handling issues
exit: QA checklist status + ledger.QA=touched; continuation → TEST.

⟂[BLOCKED:qa_failures] if mypy/ruff errors found
⟂[BLOCKED:security_issue] if signifier parsing introduces injection risk
```

---

## Full Continuation Prompt (For QA Session)

```markdown
---
path: prompts/n-phase-hardening-qa
status: active
last_touched: ${DATE}
touched_by: ${AGENT}
parent_plan: plans/_epilogues/2025-12-14-n-phase-hardening-plan.md
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped
  IMPLEMENT: touched
  QA: pending  # ← YOU ARE HERE
  TEST: pending
  EDUCATE: pending
  MEASURE: deferred
  REFLECT: pending
entropy:
  planned: 0.07
  spent: ${ENTROPY_SPENT}
  returned: ${ENTROPY_REMAINING}
---

# QA: N-Phase Cycle Hardening

## ATTACH

/hydrate

You are entering **QA** of the N-Phase Cycle (AD-005).

handles:
  scope: n-phase-hardening
  artifacts: [exporters.py, parser.py, test_parser.py, test_exporters.py]
  ledger: {IMPLEMENT:touched}
  entropy: remaining=${ENTROPY_REMAINING}
  impl_summary: "Exporter fixed, AutoInducer parser added with ${TEST_COUNT} tests"

## Your Mission

Gate quality, security, and lawfulness before broader testing.

## Actions

1. **Type check**: `uv run mypy impl/claude/protocols/agentese/ --ignore-missing-imports`
2. **Lint**: `uv run ruff check impl/claude/protocols/agentese/`
3. **Security review**: Check signifier parsing for injection vectors
4. **Edge cases**: Test malformed signifiers, empty targets, missing payloads
5. **Unicode**: Verify ⟿/⟂ handled correctly across platforms

## Exit Criteria

- [ ] mypy: 0 errors
- [ ] ruff: 0 violations
- [ ] No security issues in signifier parsing
- [ ] Edge cases documented and tested

## Continuation

⟿[TEST] — If QA passes
⟂[BLOCKED:qa_failures] — If issues found

---

*"Quality is not an act, it is a habit. QA is where habits are verified."*
```

---

*"The river knows where it flows next. The prompt generates its successor. The meta-recursion closes."*
