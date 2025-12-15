# AGENTESE REPL Wave 3: Intelligence

> *"The REPL should anticipate, not just respond."*

## Context

Wave 2.5 (Hardening) complete: 73 tests, security audited, stress tested.
Now entering Wave 3: Intelligence features (fuzzy matching, LLM suggestions, session persistence).

---

## Handles

```
scope: wave3_intelligence
plan: plans/devex/agentese-repl-master-plan.md
impl: protocols/cli/repl.py
tests: protocols/cli/_tests/test_repl.py
ledger: {PLAN:pending, RESEARCH:pending, DEVELOP:pending, STRATEGIZE:pending, IMPLEMENT:pending, QA:pending, TEST:pending}
entropy: 0.07
```

---

## Mission

Add intelligence to the AGENTESE REPL:

| Chunk | Feature | Effort | Dependencies |
|-------|---------|--------|--------------|
| I1 | Fuzzy matching engine | 3h | None |
| I2 | LLM suggestion integration | 4h | I1 |
| I3 | Dynamic Logos completion | 2h | I1 |
| I4 | Session persistence | 2h | None |
| I5 | Script mode (`kg -i < script.repl`) | 2h | None |
| I6 | Command history search (Ctrl+R) | 2h | I1 |

---

## Exit Criteria

1. Fuzzy matching catches 90% of typos (Levenshtein distance ≤ 2)
2. LLM suggestions work for semantic matches (costs 0.01 entropy per suggestion)
3. Tab completion queries live Logos registry when available
4. Session state persists to `~/.kgents_repl_session.json`
5. Script mode executes `.repl` files non-interactively
6. History search with highlighting functional

---

## Non-Goals

- Personality/emotional responses (Wave 4)
- Visual UI changes (Wave 4)
- Breaking changes to Wave 1-2.5 APIs

---

## Research Questions

1. **Fuzzy library**: `rapidfuzz` vs `thefuzz` vs custom Levenshtein?
2. **LLM model**: Haiku for speed/cost or Sonnet for quality?
3. **Session format**: JSON vs pickle vs SQLite?
4. **Script syntax**: Allow comments (#)? Variables?

---

## Parallel Tracks

- I4 (Session persistence) and I5 (Script mode) can run parallel to I1-I3
- I1 must complete before I2, I3, I6

---

## Attention Budget

```
Primary (60%):    I1 → I2 → I3 (fuzzy + LLM + completion)
Secondary (25%):  I4, I5 (session, script)
Polish (10%):     I6 (history search)
Entropy (5%):     Exploration (LLM prompt tuning)
```

---

## Actions

1. **PLAN**: Read this prompt, confirm scope
2. **RESEARCH**: Evaluate fuzzy libraries, check Logos registry API
3. **DEVELOP**: Design FuzzyMatcher and LLMSuggester interfaces
4. **STRATEGIZE**: Sequence I1 → I2 → I3 with I4/I5 parallel
5. **IMPLEMENT**: Code changes with tests
6. **QA**: Lint, type check, security review
7. **TEST**: Run full suite, verify fuzzy accuracy
8. **REFLECT**: Capture learnings, prep Wave 4

---

## Branch Candidates

- **LLM caching**: Cache suggestions to reduce API calls → defer to Wave 4
- **Semantic completion**: Logos path suggestions from meaning → defer to future

---

## Continuation

After PLAN confirmation:

```markdown
⟿[RESEARCH]
/hydrate
handles: scope=wave3_intelligence; chunks=I1-I6; ledger={PLAN:touched}; entropy=0.07
mission: evaluate rapidfuzz, check Logos registry API, design FuzzyMatcher interface.
exit: library chosen; API surface mapped; continuation → DEVELOP.
```

---

This is the **PLAN** phase for **AGENTESE REPL Wave 3: Intelligence**. The goal is to add fuzzy matching, LLM suggestions, and session persistence to make the REPL anticipate user intent. Wave 2.5 hardening (73 tests) provides a solid foundation. Execute `/hydrate plans/devex/agentese-repl-master-plan.md` to begin.

⟿[RESEARCH]
