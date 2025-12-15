---
path: plans/agent-town/phase5-strategize
status: active
progress: 100
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables:
  - phase5-cross-synergize
  - phase5-implement
session_notes: |
  STRATEGIZE phase complete. Ordered backlog with 3 parallel tracks.
  Prioritized zero-dep chunks (ASCII, SSE) for immediate value.
  NATS deferred to Wave 3 due to external dependency risk.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched  # THIS SESSION
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.05
  spent: 0.03
  returned: 0.02
---

# Agent Town Phase 5 STRATEGIZE: Implementation Backlog

> *"Choose the order of moves that maximizes leverage and minimizes risk."*

## Executive Summary

Three parallel tracks deliver value incrementally:
1. **Track A (CLI)**: Zero-dep ASCII scatter — instant `kg town status` enhancement
2. **Track B (SSE)**: Queue-based streaming — foundation for real-time
3. **Track C (Widget)**: Signal-based scatter → marimo → demo

NATS integration deferred to Wave 3 due to external service dependency. Fallback queue (already built in `nats_bridge.py`) ensures graceful degradation.

---

## Ordered Backlog

### Wave 1: Foundation (Zero External Deps)

| Order | Chunk | Description | Owner | Interface | Checkpoint |
|-------|-------|-------------|-------|-----------|------------|
| 1.1 | A | `project_scatter_to_ascii()` impl | Agent | `ScatterState → str` | Tests green, mypy clean |
| 1.2 | D | `TownSSEEndpoint` impl | Agent | `AsyncIterator[str]` | `test_sse_generates_events` passes |
| 1.3 | B | `EigenvectorScatterWidget` full impl | Agent | `KgentsWidget[ScatterState]` | Functor laws verified |

**Gate 1**: All three pass independently. No cross-dependencies.

### Wave 2: Integration (Mild Deps)

| Order | Chunk | Description | Owner | Interface | Checkpoint |
|-------|-------|-------------|-------|-----------|------------|
| 2.1 | E | SSE FastAPI route | Agent | `GET /v1/town/{id}/events` | curl returns SSE stream |
| 2.2 | C | MarimoAdapter scatter | Agent | `anywidget.AnyWidget` | Widget renders in notebook |
| 2.3 | H | Scatter widget demo | Agent | `marimo.App` | Demo notebook runs |

**Gate 2**: E2E from TownFlux → SSE works. Demo notebook showcases scatter.

### Wave 3: Resilience (External Deps)

| Order | Chunk | Description | Owner | Interface | Checkpoint |
|-------|-------|-------------|-------|-----------|------------|
| 3.1 | F | `TownNATSBridge` impl | Agent | `TownNATSBridgeProtocol` | Fallback queue tested first |
| 3.2 | G | SSE over NATS fallback | Agent | `TownSSEEndpoint._fallback_subscribe` | Circuit breaker tested |
| 3.3 | I | NATS integration tests | Agent (when NATS available) | Test suite | Skip when NATS unavailable |

**Gate 3**: NATS streaming works OR gracefully degrades to queue.

---

## Parallel Tracks

```
Track A (CLI):        [A] ───────────────────────────────────────▶ CLI complete
                           ↑ no deps

Track B (SSE):        [D] ──▶ [E] ──────────────────────────────▶ SSE complete
                                  ↑ depends on D

Track C (Widget):     [B] ──▶ [C] ──▶ [H] ──────────────────────▶ Demo complete
                           ↑ Signal   ↑ anywidget   ↑ B+C

Track D (NATS):       ──────────────────▶ [F] ──▶ [G] ──▶ [I] ──▶ NATS complete
                       (deferred)          ↑ nats-py    ↑ F
```

**Parallelism**: Tracks A, B, C run concurrently in Wave 1-2.
Track D (NATS) starts only after Waves 1-2 green.

---

## Dependency Graph

```
                    ┌─────────────────────────────────────────────┐
                    │                  INPUTS                      │
                    │  ScatterState, TownEvent, Eigenvectors      │
                    └──────────────┬──────────────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
        ┌─────────┐          ┌─────────┐         ┌─────────┐
        │    A    │          │    D    │         │    B    │
        │  ASCII  │          │   SSE   │         │ Widget  │
        └────┬────┘          └────┬────┘         └────┬────┘
             │                    │                    │
             ▼                    ▼                    ▼
        [CLI Output]         ┌─────────┐         ┌─────────┐
                             │    E    │         │    C    │
                             │  Route  │         │ Marimo  │
                             └────┬────┘         └────┬────┘
                                  │                    │
                                  ▼                    ▼
                             [API SSE]           ┌─────────┐
                                  │              │    H    │
                                  │              │  Demo   │
                                  │              └────┬────┘
                                  │                    │
                                  └────────┬───────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │   NATS (Wave 3)  │
                                  │   F → G → I      │
                                  └─────────────────┘
```

---

## Risk Assessment

| Chunk | Risk | Mitigation |
|-------|------|------------|
| A (ASCII) | Low | Pure function, no side effects |
| B (Widget) | Low | Signal already tested; extend pattern |
| C (Marimo) | Med | `anywidget` optional; fallback to JSON |
| D (SSE) | Low | `asyncio.Queue` is stdlib |
| E (Route) | Low | FastAPI pattern well-established |
| F (NATS) | **High** | External service; circuit breaker + fallback queue |
| G (Fallback) | Med | Depends on F; test fallback path first |
| H (Demo) | Low | Depends on C; non-blocking |
| I (NATS tests) | **High** | Mark `@pytest.mark.nats`; skip when unavailable |

**Risk Mitigation Strategy**:
- Wave 3 (NATS) is optional. System ships value with Waves 1-2.
- Fallback queue in `nats_bridge.py` already exists (reuse).
- Circuit breaker pattern already implemented (reuse).

---

## Interfaces

### Track A → CLI

```python
# Input: ScatterState
# Output: str (ASCII art)
def project_scatter_to_ascii(
    state: ScatterState,
    width: int = 60,
    height: int = 20,
) -> str:
    """Contract defined in visualization.py"""
```

### Track B → API

```python
# Input: town_id
# Output: AsyncIterator[str] (SSE wire format)
class TownSSEEndpoint:
    async def generate(self) -> AsyncIterator[str]:
        """Yields SSE-formatted event strings"""
```

### Track C → Notebook

```python
# Input: EigenvectorScatterWidget
# Output: anywidget that renders in marimo
class EigenvectorScatterMarimo(anywidget.AnyWidget):
    state = traitlets.Dict()  # ScatterState.to_dict()
```

### Track D → NATS

```python
# Input: TownEvent
# Output: Published to NATS or fallback queue
class TownNATSBridge(TownNATSBridgeProtocol):
    async def publish_town_event(self, town_id: str, event: TownEvent) -> None
```

---

## Checkpoints

| Checkpoint | Criterion | Tests |
|------------|-----------|-------|
| CP1 | ASCII scatter renders | `test_project_scatter_to_ascii` |
| CP2 | SSE generates valid wire format | `test_sse_event_format` |
| CP3 | Widget satisfies functor laws | `test_identity_law`, `test_composition_law` |
| CP4 | API route returns SSE | `test_town_events_endpoint` |
| CP5 | Marimo adapter works | `test_marimo_scatter_widget` |
| CP6 | Demo notebook runs | Manual: `marimo run agents/town/demo.py` |
| CP7 | NATS fallback works | `test_fallback_queue_when_nats_unavailable` |
| CP8 | Full integration | `test_townflux_to_sse_pipeline` |

---

## Decision Gates

### Gate 1: Wave 1 Complete

**Question**: Are all foundation chunks (A, B, D) passing?
- **Yes**: Proceed to Wave 2
- **No**: Debug; do not proceed

### Gate 2: Wave 2 Complete

**Question**: Can we demo scatter widget in marimo?
- **Yes**: Ship demo; proceed to Wave 3 (optional)
- **No**: Investigate anywidget compatibility; consider JSON-only fallback

### Gate 3: NATS Decision

**Question**: Is NATS infrastructure available?
- **Yes**: Implement F, G, I
- **No**: Ship with fallback queue; NATS is enhancement

---

## Entropy Sip (0.03 Spent)

Explored during strategize:

1. **Reverse order experiment**: What if NATS first?
   - Result: High risk. External dep blocks all progress.
   - Decision: Defer NATS to Wave 3.

2. **Risk probe**: What's scariest?
   - Answer: NATS integration tests (I) require running NATS server.
   - Mitigation: `@pytest.mark.nats` + skip when unavailable.

3. **Parallel discovery**: A and D are independent!
   - Result: Both can start immediately. A is CLI, D is API.
   - This parallelism was hidden in the original list.

4. **Abort criteria**: When do we stop this track?
   - If anywidget fundamentally incompatible with marimo (unlikely).
   - If SSE breaks FastAPI compatibility (unlikely; well-tested).

Returned unused entropy: 0.02

---

## Branch Notes

No branches identified. Phase 5 is self-contained.

---

## Owners

| Track | Primary Owner | Backup |
|-------|--------------|--------|
| A (CLI) | Agent | Kent (review) |
| B (SSE) | Agent | Kent (review) |
| C (Widget) | Agent | Kent (review) |
| D (NATS) | Agent | Kent (decision gate) |

---

## Summary

**Ordered Backlog**:
1. Wave 1: A (ASCII) + D (SSE) + B (Widget) — parallel, zero deps
2. Wave 2: E (Route) + C (Marimo) + H (Demo) — integration
3. Wave 3: F + G + I (NATS) — optional, high-risk

**Key Decisions**:
- NATS deferred due to external dependency risk
- Fallback queue (existing) ensures graceful degradation
- Three parallel tracks maximize throughput

**Exit → CROSS-SYNERGIZE**:
- Backlog ordered
- Interfaces defined
- Ready to hunt compositions with AGENTESE REPL, K-gent, marimo substrate

---

*"The order reveals itself when you name the dependencies."*
