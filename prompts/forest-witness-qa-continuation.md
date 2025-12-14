/hydrate meta/forest-agentese continue from QA (Week 4: Epilogue Wiring)

# QA ← IMPLEMENT

handles:
  code: impl/claude/protocols/agentese/contexts/forest.py
  tests: impl/claude/protocols/agentese/contexts/_tests/test_forest.py
  results: +18 tests (37 total forest, 1331 total AGENTESE)
  summary: |
    Wired _witness() to stream actual epilogues from _epilogues/*.md files.
    Added parse_epilogue_file(), _detect_phase(), scan_epilogues() helpers.
    Supports limit, since, phase, law_check parameters.
  laws:
    identity: pass (epilogue paths are stable)
    associativity: skip (witness is read-only)
    minimal_output: pass (streaming single entries)
    append_only: pass (epilogues never modified)
  ledger:
    PLAN: touched
    RESEARCH: touched
    DEVELOP: touched
    STRATEGIZE: touched
    CROSS-SYNERGIZE: touched
    IMPLEMENT: touched
    QA: pending
    TEST: pending
    EDUCATE: pending
    MEASURE: pending
    REFLECT: pending
  branches:
    - candidate: _refine() live wiring (deferred)
    - candidate: _define() JIT scaffold wiring (deferred)
    - candidate: _lint() forest health validation (deferred)
  metrics:
    tests_added: 18
    tests_total: 1331
    mypy_errors: 0
    files_modified: 2
    entropy_spent: 0.03

mission: Gate quality/security/lawfulness before broader testing.

actions:
  - uv run mypy impl/claude/protocols/agentese/contexts/forest.py
  - uv run ruff check impl/claude/protocols/agentese/contexts/
  - Verify graceful degradation (empty _epilogues dir, missing files)
  - Check security (no path traversal in epilogue parsing)
  - Verify EpilogueEntry.phase detection coverage
  - Log tokens/time/entropy/law-checks

checklist:
  - [ ] mypy clean
  - [ ] ruff clean
  - [ ] No silent degradations in empty/missing cases
  - [ ] Path handling is safe (no traversal)
  - [ ] Phase detection covers all 11 N-phases
  - [ ] date parsing handles edge cases
  - [ ] content_preview truncation is correct

exit: QA checklist status + ledger.QA=touched; notes for TEST; continuation → TEST.

Handle: concept.forest.manifest[phase=QA][law_check=true]@span=forest_qa
