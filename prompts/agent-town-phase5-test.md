# Agent Town Phase 5: TEST Phase

**Predecessor**: `plans/_epilogues/2025-12-14-agent-town-phase5-qa.md`
**Phase**: TEST (N-Phase 8 of 11)
**Ledger**: `{PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:touched, QA:touched, TEST:in_progress}`

---

## Context

Phase 5 QA passed all gates:
- mypy: 0 errors
- ruff: 0 errors (1 fix applied)
- Security: No vulnerabilities
- Functor Laws: 8/8 pass
- Contracts: 63/63 pass
- Exports: All 7 public APIs verified

Edge cases discovered during QA:
1. SSE connection drop handling
2. NATS reconnection after network partition
3. Widget state serialization roundtrip

Current test count: 481 town tests, 63 visualization contract tests.

---

## TEST Objectives

### 1. Edge Case Tests (QA Discoveries)

| Edge Case | Test Strategy | Strata |
|-----------|--------------|--------|
| SSE connection drop | Mock client disconnect mid-stream | Integration |
| NATS reconnection | Simulate network partition with fallback | Integration |
| Widget serialization roundtrip | Property test: `from_dict(to_dict(s)) ≡ s` | Property |

### 2. Law Verification Tests

| Law | Test |
|-----|------|
| Identity | `widget.map(id) ≡ widget` |
| Composition | `widget.map(f).map(g) ≡ widget.map(g . f)` |
| State-Map | `widget.map(f) ≡ widget.with_state(f(state))` |

### 3. Degraded Mode Tests

| Scenario | Expected Behavior |
|----------|------------------|
| NATS unavailable | Fallback to memory queue |
| SSE client slow | Backpressure (queue limit 1000) |
| Invalid projection method | Graceful error, default to PCA |

---

## Actions

1. **Design edge case fixtures**
   - SSE: Create mock async generator that drops
   - NATS: Use `fallback_to_memory=True` mode
   - Widget: Generate random ScatterState via hypothesis

2. **Run targeted tests**
   ```bash
   uv run pytest agents/town/_tests/test_visualization_contracts.py -v -k "sse or nats or widget"
   ```

3. **Add property tests** (if missing)
   - ScatterState roundtrip
   - ScatterPoint immutability
   - Projection coordinate bounds

4. **Verify law tests exist**
   ```bash
   uv run pytest agents/town/_tests/ -v -k "law"
   ```

5. **Run full town suite**
   ```bash
   uv run pytest agents/town/_tests/ -v --tb=short
   ```

---

## Entropy Budget

- Allocated: 0.07
- Draw: `void.entropy.sip(amount=0.07)`
- Purpose: Property test intuition, mutation testing exploration

---

## Branch Candidates

- **Parallel**: Performance benchmarking with realistic load (defer to MEASURE)
- **Deferred**: Integration tests with real NATS cluster (infrastructure dependency)
- **Bounty**: Chaos engineering tests (connection drops, timeouts)

---

## Exit Criteria

- [ ] All edge case tests written and passing
- [ ] Law tests verified (identity, composition, state-map)
- [ ] Degraded mode paths exercised
- [ ] No flaky tests introduced
- [ ] Repro commands documented for any slow tests

---

## Continuation

On success: `⟿[EDUCATE]` - Document visualization APIs for users
On failure: `⟂[TEST:blocked]` - Fix failures before proceeding

---

*Guard [phase=TEST][entropy=0.07][law_check=true][minimal_output=true]*

---

## Auto-Inducer

⟿[TEST]
/hydrate prompts/agent-town-phase5-test.md
handles: scope=agent-town-phase5-visualization; qa_status=PASS; edge_cases=[sse_drop,nats_reconnect,widget_roundtrip]; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched,STRATEGIZE:touched,CROSS-SYNERGIZE:touched,IMPLEMENT:touched,QA:touched,TEST:in_progress}; entropy=0.07
mission: Design and run tests proving grammar + invariants; verify edge cases from QA; prefer property tests; record repros.
actions: Design edge case fixtures; run targeted visualization tests; add property tests for roundtrip/immutability; verify all law tests exist and pass; run full town suite.
exit: edge cases tested + laws verified + no flaky tests → ledger.TEST=touched; continuation → EDUCATE | test failures → ⟂[TEST:blocked].

---

**LAW**: This prompt auto-continues. The signifier `⟿[TEST]` triggers immediate execution without human intervention. Halt conditions: test failures, law violations, flaky tests introduced, or `⟂[HUMAN_INTERRUPT]`.
