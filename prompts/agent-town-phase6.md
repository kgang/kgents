# Agent Town Phase 6: Live Visualization Demo

## ATTACH

/hydrate

You are entering **PLAN** phase for Agent Town Phase 6 (AD-005 N-Phase Cycle).

## Context from Phase 5 REFLECT

Previous cycle (Phase 5: Visualization & Streaming) completed with these outcomes:
- **Tests**: 505 (437 → 505, +68 visualization tests, 87 total viz)
- **Files**: `agents/town/visualization.py` (~1,500 LOC)
- **Deliverables**: EigenvectorScatterWidget, ASCII projection, SSE endpoint, NATS bridge

Key learnings distilled:
1. Render sub-millisecond: 0.03ms p50 for 25-citizen scatter—measure before optimizing
2. Widget functor law: `scatter.map(f) ≡ scatter.with_state(f(state))`—enables filter composition
3. SSE over NATS: circuit breaker + fallback queue ensures graceful degradation
4. Protocol > ABC: `typing.Protocol` allows duck typing without inheritance coupling

Phase 5 artifacts created:
- `agents/town/visualization.py` — ScatterPoint, ScatterState, Widget, SSE, NATS
- `agents/town/_tests/test_visualization_contracts.py` — 87 tests
- `docs/skills/agent-town-visualization.md` — Skill documentation
- 7 epilogues in `impl/claude/plans/_epilogues/`

Handles from REFLECT:
- `agent-town-phase6-marimo` — Live scatter in marimo notebook
- `agent-town-nats-production` — Real NATS cluster testing
- `town-prometheus-metrics` — Instrument visualization.py

## Phase Ledger

```yaml
phase_ledger:
  PLAN: pending  # THIS SESSION
  RESEARCH: pending
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
  spent: 0.0
  remaining: 0.35
```

## Your Mission

Frame the scope for Phase 6. Focus on the **marimo live visualization demo**.

**Principles Alignment**:
- Tasteful: One working demo, not scattered prototypes
- Composable: Build on existing EigenvectorScatterWidget
- Joy-Inducing: Interactive visualization that brings the town to life

## Questions to Answer

1. **Scope**: What does the marimo demo include?
   - Live scatter plot updating from SSE events?
   - Interactive citizen selection?
   - Coalition visualization?

2. **Dependencies**: What enables this?
   - `marimo` + `anywidget` (external)
   - `EigenvectorScatterWidgetImpl.project(RenderTarget.MARIMO)` (stub exists)
   - `TownSSEEndpoint` for streaming updates

3. **Exit criteria**: What does "Phase 6 done" look like?
   - [ ] marimo notebook with live scatter plot
   - [ ] Widget updates from SSE stream
   - [ ] Interactive selection (click citizen → details)
   - [ ] Documentation for running the demo

4. **Attention budget**:
   - 60% — marimo widget integration
   - 25% — SSE subscription + state updates
   - 10% — Demo notebook + docs
   - 5% — Exploration (alternative visualizations)

5. **Non-goals**:
   - Production deployment
   - Authentication/multi-tenancy
   - Persistent storage
   - LLM-backed decision making

## PLAN Checklist

- [ ] Scope statement (2-3 sentences)
- [ ] Exit criteria (testable)
- [ ] Attention budget (60/25/10/5)
- [ ] Dependencies mapped
- [ ] Non-goals declared
- [ ] Entropy sip declared (recommend 0.07)

## Branch Check

At PLAN exit, surface:
- Branch candidates: any tracks that should split off?
- Blockers: anything requiring re-plan?
- Composition hooks: agents/operads to align with?

## Synergy Opportunities

| ID | Source | Target | Opportunity |
|----|--------|--------|-------------|
| S1 | agents/i/reactive/widget.py | agents/town/ | Widget base class for marimo |
| S2 | agents/i/reactive/adapters/marimo.py | agents/town/ | anywidget adapter pattern |
| S3 | protocols/api/town.py | demo notebook | `/scatter` and `/events` endpoints |
| S4 | docs/skills/agent-town-visualization.md | demo | Projection selection UI |

## Technical Context

### Existing Infrastructure

```python
# Widget already supports multiple targets
class EigenvectorScatterWidgetImpl:
    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return project_scatter_to_ascii(self.state.value)
            case RenderTarget.JSON:
                return self.state.value.to_dict()
            case RenderTarget.TUI:
                return self._project_tui()
            case RenderTarget.MARIMO:
                return self._project_marimo()  # TODO: implement
```

### SSE Streaming

```python
# Endpoint exists, needs client consumption
async for event in sse_endpoint.generate():
    # event is SSE wire format: "event: town.status\ndata: {...}\n\n"
    pass
```

### marimo Widget Pattern (from agents/i)

```python
import anywidget
import traitlets

class ScatterWidget(anywidget.AnyWidget):
    _esm = """..."""  # JavaScript render code
    state = traitlets.Dict().tag(sync=True)

    def update_from_sse(self, event_data: dict) -> None:
        # Update state from streaming event
        pass
```

## Auto-Continuation Imperative

**CRITICAL**: Upon completing PLAN phase, you MUST:
1. Generate the continuation prompt for RESEARCH phase
2. End your output with the auto-inducer signifier

Example format:
```
⟿[RESEARCH]

---

This is the *RESEARCH PHASE* for Agent Town Phase 6...
```

This enables self-chaining across sessions.

---

This is the *PLAN PHASE* for Agent Town Phase 6: Live Visualization Demo.

---

## Exit Signifier (LAW)

Upon completing this PLAN phase successfully:

```
⟿[RESEARCH]
/hydrate
handles: scope=marimo-live-viz; ledger={PLAN:touched}; entropy=0.07
mission: map anywidget patterns; find SSE client examples; identify blockers.
exit: file map + integration plan; ledger.RESEARCH=touched; continuation → DEVELOP.
```

Upon encountering blockers:

```
⟂[BLOCKED:dependency_missing] marimo/anywidget not installed or incompatible
⟂[BLOCKED:scope_unclear] Need human decision on demo scope
```

---

*Guard [phase=PLAN][entropy=0.07][law_check=true][minimal_output=true]*
