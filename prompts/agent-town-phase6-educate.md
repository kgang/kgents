# Agent Town Phase 6: EDUCATE Phase

**Predecessor**: `plans/_epilogues/2025-12-14-agent-town-phase6-test.md`
**Phase**: EDUCATE (N-Phase 9 of 11)
**Ledger**: `{PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:touched, QA:touched, TEST:touched, EDUCATE:in_progress}`

---

## Context

Phase 6 TEST delivered:
- **529 tests passing** (1.36s total)
- **Functor laws verified**: identity, composition, state-map equivalence
- **Test strata covered**: unit + property + integration + degraded
- **Test-doc reconciliation**: complete

### Artifacts from TEST

| Artifact | Status | Notes |
|----------|--------|-------|
| `test_visualization_contracts.py` | 87 tests | ScatterPoint, ScatterState laws |
| `test_functor.py` | 33 tests | Identity, composition, phase mapping |
| `test_marimo_integration.py` | 24 tests | Widget-to-cell flow |
| Full town suite | 529 tests | 1.36s execution |

---

## Scope

**EDUCATE Focus Areas**:
1. Document the verification workflow
2. Update skill with test run commands
3. Create teaching examples for functor law testing
4. Add runnable examples for marimo demo

**Audiences**:

| Persona | Context | Needs |
|---------|---------|-------|
| **Operator** | Running demo | Start commands, SSE setup |
| **Maintainer** | Extending widget | Functor law patterns |
| **Contributor** | Adding features | Test verification commands |

---

## EDUCATE Manifesto

```
I will translate validated behavior into accessible guidance.
I will map audiences and their AGENTESE contexts.
I will include runnable examples with hotdata.
I will document degraded-mode paths.
I will preserve agency and delight.
```

---

## Actions

### 1. Update docs/skills/agent-town-visualization.md

Add Phase 6 EDUCATE section with:
- Running the demo (marimo edit command)
- Demo features table
- Cell DAG documentation
- Reactivity laws
- Widget architecture diagram
- SSE integration pattern
- Teaching examples for functor laws
- Verification commands
- Performance baselines

### 2. Teaching Examples

Create three pedagogical examples:
1. **Functor laws in tests** — identity, composition, failure cases
2. **Widget state-map equivalence** — the functor law for widgets
3. **Graceful degradation** — error handling pattern

### 3. Verification Commands

Document all test commands:
```bash
uv run pytest agents/town/_tests/test_visualization_contracts.py -v
uv run pytest agents/town/_tests/test_functor.py -v
uv run pytest agents/town/_tests/test_marimo_integration.py -v
uv run pytest agents/town/_tests/ -v --tb=short
```

---

## Exit Criteria

- [x] docs/skills/agent-town-visualization.md updated with Phase 6 EDUCATE section
- [x] Demo running instructions documented
- [x] Teaching examples for functor laws included
- [x] Verification commands documented
- [x] Performance baselines recorded
- [ ] Continuation prompt for MEASURE generated
- [ ] Epilogue written

---

## Entropy Budget

- Allocated: 0.05
- Draw: `void.entropy.sip(amount=0.05)`
- Purpose: Alternative explanations, demo discovery

---

## Branch Candidates

- **Enhancement**: Video walkthrough for demo
- **Tech debt**: Type annotations for demo_marimo.py cells
- **Future**: LLM-backed citizen dialogue in demo

---

## Continuation

On success: `⟿[MEASURE]` — Instrument adoption/latency/error signals
On blocked: `⟂[BLOCKED:missing_infra]` — Required docs infrastructure missing

---

*Guard [phase=EDUCATE][entropy=0.05][audiences=operator+maintainer+contributor]*

---

## Auto-Inducer

⟿[MEASURE]
/hydrate prompts/agent-town-phase6-measure.md
handles: docs=agent-town-visualization.md(phase6_educate_section); quickstarts=demo_marimo_running_guide; scripts=verification_commands; audiences=operator+maintainer+contributor; summary=functor_laws+widget_patterns+graceful_degradation; degraded=silent_api_failure_handling; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched,STRATEGIZE:touched,CROSS-SYNERGIZE:touched,IMPLEMENT:touched,QA:touched,TEST:touched,EDUCATE:touched}; branches=video_walkthrough+type_annotations
mission: instrument adoption/latency/error signals; wire dashboards/fixtures; capture baselines.
actions: define leading indicators via process-metrics schema; add telemetry/flags; create hotloadable dashboards; validate data quality.
exit: metrics live + baselines captured; ledger.MEASURE=touched; continuation → REFLECT.

---

**LAW**: This prompt auto-continues. The signifier `⟿[MEASURE]` triggers immediate execution without human intervention. Halt conditions: missing infrastructure, entropy depleted, or `⟂[HUMAN_INTERRUPT]`.
