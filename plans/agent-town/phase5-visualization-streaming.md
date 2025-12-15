---
path: plans/agent-town/phase5-visualization-streaming
status: active
progress: 5
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables:
  - agent-town-phase6-llm-autonomy
  - monetization-dashboard
  - town-observability
session_notes: |
  PLAN phase for Agent Town Phase 5. Focus on marimo dashboard + NATS streaming.
  Building on 437 tests from Phase 4.
phase_ledger:
  PLAN: touched  # THIS SESSION
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
  spent: 0.05
  remaining: 0.30
---

# Agent Town Phase 5: Visualization & Streaming

> *"The dashboard is the umwelt through which Kent observes his town."*

## Scope Statement

Phase 5 adds **live visualization** and **real-time event streaming** to Agent Town. A marimo dashboard renders eigenvector space, coalition formation, and citizen activity. NATS JetStream bridges TownFlux events to SSE consumers, enabling multi-client observation of the simulation.

## Exit Criteria (Testable)

| Criterion | Test |
|-----------|------|
| Dashboard renders | `pytest agents/town/viz/` passes (≥30 tests) |
| Eigenvector scatter plot | `test_eigenvector_scatter` shows 25 citizens in 7D→2D projection |
| Coalition overlay | `test_coalition_highlight` colors citizens by coalition membership |
| NATS event bridge | `test_nats_town_bridge` publishes TownEvent to JetStream |
| SSE endpoint | `GET /v1/town/{id}/events` streams events |
| Graceful degradation | Dashboard works without NATS (in-memory fallback) |
| Integration | `test_full_stack_integration` runs simulation with live dashboard |

## Attention Budget

```
Primary Focus (60%):    marimo dashboard (eigenvector viz, citizen cards)
Secondary (25%):        NATS streaming bridge for TownFlux
Maintenance (10%):      API/test hardening
Accursed Share (5%):    Speculative: WebGL acceleration for large towns
```

## Dependencies Mapped

### Existing Infrastructure (Ready)

| Component | Location | Status |
|-----------|----------|--------|
| TownFlux | `agents/town/flux.py` | ✓ Emits TownEvent async iterator |
| Eigenvectors | `agents/town/citizen.py` | ✓ 7D personality space |
| Coalition detection | `agents/town/coalition.py` | ✓ k-clique percolation |
| MarimoAdapter | `agents/i/reactive/adapters/marimo_widget.py` | ✓ Signal→traitlet bridge |
| NATSBridge | `protocols/streaming/nats_bridge.py` | ✓ Circuit breaker, fallback |
| Town API | `protocols/api/town.py` | ✓ REST endpoints |
| KgentsWidget | `agents/i/reactive/widget.py` | ✓ Base widget class |
| Anywidget ESM | `docs/skills/marimo-anywidget.md` | ✓ Skill documented |

### New Components (To Build)

| Component | Location | Purpose |
|-----------|----------|---------|
| TownDashboard | `agents/town/viz/dashboard.py` | Main marimo dashboard |
| EigenvectorScatter | `agents/town/viz/eigenvector.py` | 7D→2D projection scatter |
| CitizenCard | `agents/town/viz/citizen_card.py` | LOD-aware citizen widget |
| CoalitionOverlay | `agents/town/viz/coalition.py` | Coalition highlighting |
| TownNATSBridge | `agents/town/streaming.py` | TownFlux→NATS adapter |
| EventSSE | `protocols/api/town.py` | SSE endpoint addition |

## Non-Goals (Explicitly Out of Scope)

1. **LLM-backed decision making**: Phase 6 territory
2. **Persistent storage (SQLite/Redis)**: Deferred; in-memory sufficient for demo
3. **Incremental coalition detection**: Current O(n³) acceptable for n≤100
4. **3D visualization**: 2D scatter sufficient; 3D adds complexity
5. **Multi-tenant towns**: Single-process for now

## Synergy Opportunities

| ID | Source | Target | Opportunity |
|----|--------|--------|-------------|
| S8 | `agents/i/screens/base.py` | `agents/town/viz/` | Reuse KgentsScreen navigation pattern |
| S9 | `protocols/streaming/nats_bridge.py` | `agents/town/streaming.py` | Extend NATSBridge for TownEvent |
| S10 | `protocols/api/metering.py` | `agents/town/viz/` | Per-turn metering display |
| S11 | `agents/i/reactive/primitives/` | `agents/town/viz/` | Reuse sparkline, bar, glyph |

## Architecture Sketch

```
┌─────────────────────────────────────────────────────────────────┐
│                        TownDashboard (marimo)                    │
├────────────────┬────────────────┬────────────────┬──────────────┤
│ EigenvectorPlot│  CoalitionView │  ActivityFeed  │ CitizenCards │
│   (scatter)    │    (overlay)   │    (stream)    │   (LOD 0-5)  │
└───────┬────────┴───────┬────────┴───────┬────────┴──────┬───────┘
        │                │                │               │
        ▼                ▼                ▼               ▼
┌───────────────────────────────────────────────────────────────┐
│                     MarimoAdapter (anywidget)                  │
│                  Signal[S] → traitlet → JS render              │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                         TownFlux                               │
│              AsyncIterator[TownEvent] simulation               │
└───────────────────────────┬───────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌───────────────────────┐     ┌───────────────────────┐
│     TownNATSBridge    │     │     API /v1/town/     │
│  (circuit breaker)    │     │    (REST + SSE)       │
└───────────┬───────────┘     └───────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────┐
│                      NATS JetStream                            │
│            kgent.town.{town_id}.{event_type}                  │
└───────────────────────────────────────────────────────────────┘
```

## Eigenvector Visualization Strategy

### 7D → 2D Projection

Use PCA or t-SNE for dimensionality reduction:

```python
# Simplified: project to warmth-curiosity plane (first 2 dimensions)
# Production: sklearn.decomposition.PCA or UMAP
def project_eigenvector(ev: Eigenvectors) -> tuple[float, float]:
    return (ev.warmth, ev.curiosity)  # Naive projection
```

### Coalition Coloring

```python
# Citizens in same coalition share color
# Bridge citizens (multiple coalitions) get special indicator
def get_citizen_color(citizen_id: str, coalitions: list[Coalition]) -> str:
    memberships = [c for c in coalitions if citizen_id in c.members]
    if len(memberships) > 1:
        return "gold"  # Bridge node
    elif len(memberships) == 1:
        return coalition_colors[memberships[0].id]
    return "gray"  # Unaffiliated
```

## NATS Event Schema

```json
{
  "subject": "kgent.town.{town_id}.{phase}.{operation}",
  "payload": {
    "type": "town_event",
    "town_id": "abc123",
    "phase": "MORNING",
    "operation": "gossip",
    "participants": ["Alice", "Bob"],
    "success": true,
    "message": "Alice told Bob about Carol.",
    "tokens_used": 150,
    "drama_contribution": 0.3,
    "timestamp": "2025-12-14T12:00:00Z"
  }
}
```

## Entropy Sip (0.05 Spent)

- Explored alternative projection methods (UMAP vs PCA)
- Considered WebSocket vs SSE (chose SSE for simplicity)
- Evaluated Textual vs marimo (marimo wins per meta.md learning)

## Branch Candidates

None identified. Phase 5 is self-contained.

## Blockers

None. All dependencies satisfied.

## Composition Hooks

| Hook | Agent/Operad | Purpose |
|------|--------------|---------|
| `void.sip` | Entropy draw for random projection jitter | Visual interest |
| `time.witness` | Event history for replay | Debugging |
| `self.memory` | Citizen gossip memory integration | M-gent bridge |

## Implementation Order

1. **EigenvectorScatter widget** (foundation)
2. **CitizenCard widget** (LOD-aware)
3. **TownDashboard** (compose widgets)
4. **TownNATSBridge** (streaming adapter)
5. **SSE endpoint** (API addition)
6. **Integration tests** (full stack)

---

## PLAN Checklist

- [x] Scope statement (2-3 sentences)
- [x] Exit criteria (testable)
- [x] Attention budget (60/25/10/5)
- [x] Dependencies mapped
- [x] Non-goals declared
- [x] Entropy sip declared (0.05 spent)
- [x] Architecture sketch
- [x] Implementation order

---

*"The noun is a lie. There is only the rate of change. And now we can watch it change."*
