# Agent Town Phase 5: RESEARCH Continuation

> *"Map the landscape before you build upon it."*

---

## Auto-Inducer

```
⟿[RESEARCH]
```

This is the **RESEARCH** phase for **Agent Town Phase 5: Visualization & Streaming**.

---

## Hydration Prompt

```
/hydrate
```

---

## Handles

```yaml
scope: plans/agent-town/phase5-visualization-streaming
ledger:
  PLAN: touched
  RESEARCH: in_progress  # THIS SESSION
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.35
  spent: 0.05
  remaining: 0.30
  sip: 0.07  # void.entropy.sip for RESEARCH
```

---

## Mission

Map the terrain for Agent Town Phase 5 visualization and streaming infrastructure:

1. **Verify existing dependencies** from the PLAN:
   - `agents/town/flux.py` — TownFlux emits `TownEvent` async iterator
   - `agents/town/citizen.py` — Eigenvectors (7D personality space)
   - `agents/town/coalition.py` — k-clique percolation detection
   - `agents/i/reactive/adapters/marimo_widget.py` — MarimoAdapter
   - `protocols/streaming/nats_bridge.py` — NATSBridge with circuit breaker
   - `protocols/api/town.py` — Existing REST endpoints

2. **Research external patterns**:
   - marimo widget best practices (anywidget ESM)
   - Scatter plot libraries compatible with marimo (matplotlib? plotly? custom ESM?)
   - SSE endpoint patterns in FastAPI
   - NATS JetStream subject naming conventions

3. **Surface invariants and contracts**:
   - What is the exact shape of `TownEvent`?
   - What are the Eigenvector field names and ranges?
   - What coalitions API does `coalition.py` expose?
   - What is the MarimoAdapter signal interface?

4. **Identify blockers**:
   - Any missing dependencies for visualization?
   - NATS JetStream availability in dev environment?
   - marimo version compatibility?

---

## Actions

```markdown
1. Read and verify each dependency file exists and exposes expected interfaces
2. WebSearch for marimo anywidget scatter plot patterns (2025)
3. WebSearch for FastAPI SSE streaming best practices (2025)
4. Extract TownEvent schema from flux.py
5. Extract Eigenvectors dataclass from citizen.py
6. Document NATSBridge interface from nats_bridge.py
7. Check for existing visualization code in agents/i/reactive/
8. Note any blockers with file:line evidence
9. Surface branch candidates if scope splits emerge
```

---

## Exit Criteria

- [ ] File map with refs for all 6 dependencies
- [ ] TownEvent schema documented
- [ ] Eigenvector field names and ranges documented
- [ ] MarimoAdapter interface documented
- [ ] External research: marimo scatter plot approach chosen
- [ ] External research: SSE pattern chosen
- [ ] Blockers enumerated (or "none")
- [ ] Branch candidates captured (or "none")
- [ ] Entropy ledger updated

---

## Outputs Expected

```markdown
### File Map
| File | Purpose | Key Exports | Status |
|------|---------|-------------|--------|
| agents/town/flux.py | Event stream | TownFlux, TownEvent | ✓/✗ |
| ... | ... | ... | ... |

### Schemas Extracted
- TownEvent: { type, town_id, phase, operation, participants, ... }
- Eigenvectors: { warmth, curiosity, ... }

### External Research
- Scatter plot: [chosen approach] — [source URL]
- SSE streaming: [chosen approach] — [source URL]

### Blockers
- [none] OR [blocker with file:line evidence]

### Branch Candidates
- [none] OR [branch description]
```

---

## Continuation → DEVELOP

Upon exit, generate:

```markdown
⟿[DEVELOP]
/hydrate
handles: files=${files_mapped}; schemas={TownEvent, Eigenvectors, ...}; blockers=${blockers}; external_patterns=${patterns}; ledger={RESEARCH:touched}; entropy=${entropy_remaining}
mission: define contracts for TownDashboard, EigenvectorScatter, CitizenCard, TownNATSBridge; specify inputs/outputs/errors; capture functor laws.
actions: write interface stubs; define widget props; specify NATS subject schema; note composition hooks.
exit: contracts + laws + examples; ledger.DEVELOP=touched; continuation → STRATEGIZE.
```

---

## Halt Conditions

```markdown
⟂[BLOCKED:dependency_missing] Required file/interface not found
⟂[BLOCKED:marimo_incompatible] marimo version doesn't support anywidget
⟂[BLOCKED:nats_unavailable] NATS JetStream not configured in dev
⟂[ENTROPY_DEPLETED] Budget exhausted
```

---

*"The noun is a lie. There is only the rate of change. RESEARCH reveals the rates."*
