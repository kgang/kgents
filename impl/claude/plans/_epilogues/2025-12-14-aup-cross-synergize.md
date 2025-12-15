# AGENTESE Universal Protocol: CROSS-SYNERGIZE Complete

> *"Composition is not about combining things. It's about discovering they were always meant to fit."*

## Phase: CROSS-SYNERGIZE
## Date: 2025-12-14
## Entropy: 0.01 sipped

---

## Synergy Map (Completed)

```
                    ┌─────────────────────────────────────────┐
                    │      AGENTESE Universal Protocol        │
                    │                                         │
                    │   AgenteseBridgeProtocol                │
                    │   ├── invoke()                          │
                    │   ├── compose()                         │
                    │   ├── stream()                          │
                    │   └── subscribe()                       │
                    └────────────────┬────────────────────────┘
                                     │
         ┌───────────┬───────────────┼───────────────┬───────────┐
         │           │               │               │           │
         ▼           ▼               ▼               ▼           ▼
    ┌─────────┐ ┌─────────┐   ┌─────────────┐ ┌─────────┐ ┌──────────┐
    │Existing │ │Sessions │   │   marimo    │ │   TUI   │ │  Agent   │
    │  API    │ │  API    │   │  notebooks  │ │ screens │ │   Town   │
    └────┬────┘ └────┬────┘   └──────┬──────┘ └────┬────┘ └─────┬────┘
         │           │               │             │            │
      MIGRATE     WRAPPABLE      ALIGNED      DEFERRED      ALIGNED
```

---

## 1. Existing AGENTESE API (`protocols/api/agentese.py`)

### Status: **MIGRATE**

### Contract Analysis

| Current | New (AUP) | Compatibility |
|---------|-----------|---------------|
| `InvokeRequest.path` | `AgenteseRequest` uses URL path | Breaking - path is URL now |
| `InvokeRequest.observer` | `ObserverContext` (frozen) | Compatible with rename |
| `InvokeRequest.kwargs` | `AgenteseRequest.kwargs` | Identical |
| `InvokeResponse.result` | `AgenteseResponse.result` | Identical |
| `InvokeResponse.cached` | `ResponseMeta.cached` | Nested differently |
| `InvokeResponse.tokens_used` | Not in AUP | Feature gap |
| `ErrorResponse` | AUP `ErrorResponse` | Superset (richer) |

### Migration Path

1. **Wrap existing router** with AUP-compliant facade
2. Add `X-Observer-Archetype` header extraction
3. Return `AgenteseResponse` envelope (handle + result + meta)
4. Deprecate `InvokeRequest.path` in body (use URL path instead)

### Blockers: None
### Skip: `tokens_used` tracking deferred to MEASURE phase

---

## 2. Sessions API (`protocols/api/sessions.py`)

### Status: **WRAPPABLE**

### SSE Event Analysis

| Current (`_stream_response`) | AUP (`SSEChunk`) | Compatibility |
|------------------------------|------------------|---------------|
| `event: chunk` + `{text, index}` | `SSEChunk.type="response"` | Wrappable |
| `event: complete` + `{text, tokens_used, chunks}` | `SSECompleteEvent` | Fields match |
| `event: error` + `{error, type}` | `ErrorResponse` | Richer in AUP |

### Integration Point

Sessions API can use `AgenteseBridge.stream()` by:

```python
# sessions.py future integration
async def _stream_via_bridge(bridge, session_id, message, mode):
    async for event in bridge.stream("self.soul.dialogue", observer, kwargs={"message": message}):
        yield event.serialize()
```

### Synergy: NATS Publishing Already Exists

Sessions API already publishes chunks to NATS (`_publish_chunk_to_nats`). This pattern aligns with AUP's `subscribe()` channel architecture:

```
Sessions SSE → NATS (existing) → AUP subscribe("session:{id}") (new)
```

### Blockers: None
### Risk: Parallel SSE formats during transition (mitigate with content negotiation)

---

## 3. marimo Integration (`agents/i/marimo/`)

### Status: **ALIGNED**

### Pattern Analysis

| marimo (`logos_bridge.py`) | AUP (`bridge.py`) | Alignment |
|----------------------------|-------------------|-----------|
| `LogosCell(handle)` | `AgenteseBridge.invoke(handle)` | Direct mapping |
| `MockUmwelt` | `ObserverContext` | Same structure |
| `invoke_sync()` | `AgenteseBridge.invoke()` | Async wrapper |
| `affordances_to_buttons()` | `AgenteseBridge.affordances()` | Complementary |
| `ObserverState` | `ObserverContext` (frozen) | ObserverState is mutable wrapper |

### Already Aligned

marimo's `LogosCell` pattern IS the AUP pattern:

```python
# marimo (current)
cell = LogosCell("world.field.manifest")
result = await cell(observer)

# AUP (new)
response = await bridge.invoke("world.field.manifest", observer)
result = response.result
```

**The only difference**: AUP adds metadata (span_id, timestamp).

### Integration: Add Bridge Adapter

```python
# marimo_bridge_adapter.py (new file, IMPLEMENT phase)
class MarimoAgenteseBridge:
    """Adapt AgenteseBridge for marimo reactive model."""

    def __init__(self, bridge: AgenteseBridgeProtocol):
        self.bridge = bridge

    async def cell(self, handle: str, observer: ObserverState) -> Any:
        """Execute as marimo cell (returns just result)."""
        response = await self.bridge.invoke(handle, observer.observer)
        return response.result
```

### Blockers: None
### Skip: None

---

## 4. TUI Screens (`agents/i/screens/`)

### Status: **DEFERRED**

### Analysis

TUI screens use Textual framework with local data access:

- `KgentsScreen` → Key passthrough for navigation
- `Dashboard` → Local metrics display
- `Terrarium` → Local garden visualization

### Why Deferred

1. TUI works perfectly locally; no API needed for MVP
2. Remote TUI would require:
   - HTTP client in TUI
   - Connection management
   - Offline graceful degradation
3. ROI is low compared to marimo/API priorities

### Future Integration Path (Post-MVP)

```python
# screens/remote.py (future)
class RemoteGardenScreen(KgentsScreen):
    """TUI screen backed by AUP WebSocket."""

    async def on_mount(self):
        subscription = self.bridge.subscribe("garden")
        async for update in subscription:
            self.update_display(update.data)
```

### Blockers: N/A (deferred)
### Risk: None (TUI continues working locally)

---

## 5. Agent Town (`agents/town/`)

### Status: **ALIGNED**

### Contract Alignment

| Agent Town (`town.py`) | AUP (`serializers.py`) | Match |
|------------------------|------------------------|-------|
| `TownResponse` | Custom (not in AUP) | Town-specific, OK |
| `CitizenSummary` | Maps to `EntityState` | Fields compatible |
| SSE events | `WSStateUpdate` channel | Same pattern |
| NATS subjects | `WSSubscribeMessage.channel` | Direct mapping |

### NATS Subject Alignment

Agent Town already uses NATS for streaming (per Phase 5). The subject schema:

```
town.{town_id}.{phase}.{operation}  →  AUP channel: "town:{town_id}"
```

### GardenState Match

AUP's `GardenState`:
```python
class GardenState(BaseModel):
    entities: list[EntityState]  # ← Citizens map here
    pheromones: list[PheromoneState]  # ← Coalition visualization
    entropy: float
    tick: int
```

Agent Town's citizen visualization already produces compatible data.

### Composition Hook: Town Operad Alignment

From `plans/meta.md`:
> "TOWN_OPERAD, NPHASE_OPERAD, SOUL_OPERAD use the same structure"

AUP's `compose()` method can execute town operations:

```python
await bridge.compose([
    "town.smallville.step",      # Advance simulation
    "town.smallville.detect",    # Detect coalitions
    "town.smallville.manifest",  # Get state
], observer)
```

### Blockers: None
### Skip: None

---

## Parallel Track Classification

| Track | Classification | Dependencies | Parallelizable With |
|-------|----------------|--------------|---------------------|
| Existing API Migration | **PARALLEL** | Bridge Protocol (done) | All |
| Sessions SSE Wrapper | **PARALLEL** | Bridge Protocol (done) | All |
| marimo Bridge Adapter | **PARALLEL** | Bridge Protocol (done) | All |
| Agent Town NATS Unification | **PARALLEL** | Bridge Protocol (done) | All |
| TUI Remote Mode | **DEFERRED** | HTTP implementation | — |
| WebSocket Handler | **PARALLEL** | Bridge Protocol (done) | HTTP, SSE |
| OpenAPI Generation | **BLOCKING** | HTTP routes stable | — |

### Implementation Order (IMPLEMENT phase)

**Wave 1 (Parallel):**
- [ ] Wire `AgenteseBridge` to Logos (backed implementation)
- [ ] Existing API migration (add AUP envelope)
- [ ] Sessions SSE content negotiation

**Wave 2 (Parallel):**
- [ ] FastAPI router for AUP endpoints
- [ ] WebSocket handler for subscriptions
- [ ] SSE streaming for soul/challenge

**Wave 3 (Sequential):**
- [ ] OpenAPI generation (needs stable routes)
- [ ] marimo bridge adapter

**Wave 4 (Deferred):**
- [ ] TUI remote mode (post-MVP)

---

## Composition Hooks Identified

### 1. Functor Alignment: AgenteseBridge

The `AgenteseBridgeProtocol` is the functor between:

```
HTTP Request ─────► AgenteseBridge ─────► Logos.invoke()
     ↓                    ↑                    ↓
JSON envelope        Laws preserved       Umwelt-specific result
```

**Law Verification** (from `bridge.py`):
- `assert_identity_law()` → verify manifest consistency
- `assert_associativity_law()` → verify composition grouping
- `assert_observer_polymorphism()` → verify affordance filtering

### 2. Operad Alignment: Composition API

AUP's `compose()` method implements operad-style composition:

```python
# From bridge.py
async def compose(
    self,
    paths: list[str],  # Operad grammar: sequence of operations
    observer: ObserverContext,
    emit_law_check: bool = True,  # Verify laws during execution
) -> CompositionResponse
```

This aligns with NPHASE_OPERAD and TOWN_OPERAD patterns.

### 3. Sheaf Alignment: Observer Polymorphism

Different observers receive different views of the same entity:

```python
# Same handle, different observers → different results
await bridge.invoke("world.house", architect_observer)  # → Blueprint
await bridge.invoke("world.house", poet_observer)       # → Metaphor
```

This IS the sheaf gluing principle: local views (per-observer) compose to global coherence (single handle).

---

## Blockers Surfaced

| Blocker | Owner | Resolution |
|---------|-------|------------|
| (None) | — | — |

All systems are compatible. No blocking dependencies.

---

## Skip Declarations

| Skip | Risk | Reason |
|------|------|--------|
| TUI Remote Mode | Low | TUI works locally; remote is enhancement |
| `tokens_used` in AUP | Low | Can add in MEASURE phase without breaking contract |

---

## Exit Checklist

- [x] Synergy map completed for all 5 subsystems
- [x] Parallel tracks classified (BLOCKING/PARALLEL/DEFERRED)
- [x] Composition hooks identified (functor/operad/sheaf alignment)
- [x] Blockers surfaced with owners (none found)
- [x] Skip declarations documented with risk

---

## Learnings (for `meta.md`)

```
2025-12-14  marimo LogosCell pattern IS AgenteseBridge pattern—direct mapping, no adapter needed
2025-12-14  Sessions API NATS publishing already aligns with AUP subscribe channels
2025-12-14  Agent Town GardenState ≡ AUP GardenState—no translation layer needed
2025-12-14  TUI remote mode is DEFERRED not BLOCKED—local TUI continues working
2025-12-14  CROSS-SYNERGIZE is law verification: existing tests suffice; no new code needed to prove laws
```

---

## Continuation

⟿[IMPLEMENT]

Mission: Wire `AgenteseBridge` backed by Logos; FastAPI routes for invoke/compose/stream; SSE for soul/challenge; WebSocket for garden subscriptions.

---

*"The wires were always there. We just needed to see them."*
