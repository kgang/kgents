# AGENTESE Universal Protocol: CROSS-SYNERGIZE Phase

> *"The functor lifts the string into action. The wire carries the action to the world."*

## ATTACH

/hydrate

You are entering **CROSS-SYNERGIZE** of the N-Phase Cycle (AD-005) for the AGENTESE Universal Protocol Crown Jewel.

```yaml
handles:
  plan: plans/agentese-universal-protocol.md
  contracts: impl/claude/protocols/api/serializers.py
  bridge: impl/claude/protocols/api/bridge.py
  contract_tests: impl/claude/protocols/api/_tests/test_aup_contracts.py
  existing_api: impl/claude/protocols/api/agentese.py
  marimo: impl/claude/agents/i/marimo/
  tui: impl/claude/agents/i/screens/
  saas: impl/claude/protocols/api/app.py

ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched  # serializers.py, bridge.py, 33 contract tests
  STRATEGIZE: touched
  CROSS-SYNERGIZE: in_progress  # <-- YOU ARE HERE
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  planned: 0.12
  spent: 0.07
  remaining: 0.05
  sip_this_phase: 0.01
```

---

## Your Mission

Identify **composition opportunities** across existing subsystems. This phase produces:

1. **Synergy Map** — Which systems can share AgenteseBridge?
2. **Parallel Tracks** — What can be implemented concurrently?
3. **Composition Hooks** — Where do agents/operads align?
4. **Integration Points** — Contracts between AUP and existing code

You are NOT implementing yet. You are mapping **how the pieces fit together**.

---

## Context from DEVELOP Phase

### Contracts Created

**Serializers** (`protocols/api/serializers.py`):
- `ObserverContext` — archetype, id, capabilities (frozen)
- `AgenteseRequest` / `AgenteseResponse` — standard envelope
- `CompositionRequest` / `CompositionResponse` — pipeline execution
- `LawVerificationResult` — identity_holds, associativity_holds
- SSE types: `SSEChunk`, `SSECompleteEvent`
- WebSocket types: `WSSubscribeMessage`, `WSInvokeMessage`, `WSStateUpdate`
- Garden types: `EntityState`, `PheromoneState`, `GardenState`

**Bridge Protocol** (`protocols/api/bridge.py`):
- `AgenteseBridgeProtocol` — abstract interface with 6 methods
- Law assertions: `assert_identity_law`, `assert_associativity_law`, `assert_observer_polymorphism`
- Error taxonomy: 8 error codes with HTTP status mapping
- `StubAgenteseBridge` — for contract testing

**33 Contract Tests** (`protocols/api/_tests/test_aup_contracts.py`)

---

## Existing Systems to Synergize

### 1. Existing AGENTESE API (`protocols/api/agentese.py`)

Current endpoints:
- `POST /v1/agentese/invoke` — InvokeRequest → InvokeResponse
- `GET /v1/agentese/resolve` — path → ResolveResponse
- `GET /v1/agentese/affordances` — path + archetype → AffordancesResponse

**Synergy Question**: Can existing endpoints adopt new serializers? Or wrap with Bridge?

### 2. K-gent Sessions API (`protocols/api/sessions.py`)

Current endpoints:
- `POST /v1/kgent/sessions` — Create session
- `POST /v1/kgent/sessions/{id}/messages` — SSE streaming

**Synergy Question**: Can sessions use `AgenteseBridge.stream()` for dialogue?

### 3. marimo Integration (`agents/i/marimo/`)

Current patterns:
- `LogosCell` — reactive cell for Logos invocations
- `invoke_sync()` — synchronous wrapper
- Widgets: `StigmergicFieldWidget`, `scatter.py`

**Synergy Question**: Can marimo notebooks use AgenteseBridge directly?

### 4. TUI Screens (`agents/i/screens/`)

Current patterns:
- `BaseScreen` — reactive Textual screens
- `Dashboard` — observability display
- `Terrarium` — garden visualization

**Synergy Question**: Can TUI use AgenteseBridge for remote garden state?

### 5. Agent Town (`agents/town/`)

Current patterns:
- NATS streaming for town events
- SSE for visualization updates
- `GardenState` matches our serializers

**Synergy Question**: Does Agent Town already align with AUP contracts?

---

## Cross-Synergize Exit Criteria

1. **Synergy Map**: Document which systems share which contracts
2. **Parallel Tracks**: Classify implementation work into concurrent streams
3. **Composition Hooks**: Identify functor/operad alignment points
4. **Blockers Surfaced**: Any dependencies that block parallel work
5. **Skip Declarations**: Any synergies intentionally deferred (with risk)

---

## Analysis Tasks

### 1. Existing API Migration Path

Read `protocols/api/agentese.py` and determine:
- Can `InvokeRequest` be replaced by `AgenteseRequest`?
- Can `InvokeResponse` be replaced by `AgenteseResponse`?
- Do error codes align with our error taxonomy?

### 2. Sessions SSE Unification

Read `protocols/api/sessions.py` and determine:
- Does `_stream_response()` produce SSE events matching our `SSEChunk`?
- Can session messages use `AgenteseBridge.stream()`?

### 3. marimo Bridge

Read `agents/i/marimo/` and determine:
- Does `LogosCell` pattern map to `AgenteseBridge.invoke()`?
- Can marimo notebooks become AUP clients?

### 4. Agent Town Alignment

Read `agents/town/` and check:
- Does `town.py` produce events matching `GardenState`?
- Are NATS subjects compatible with `WSSubscribeMessage.channel`?

---

## Synergy Map Template

Complete this map:

```
                    ┌─────────────────────────────────────────┐
                    │      AGENTESE Universal Protocol        │
                    │                                         │
                    │   AgenteseBridge Protocol               │
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
    [STATUS]    [STATUS]        [STATUS]      [STATUS]     [STATUS]
```

Fill in [STATUS]:
- `ALIGNED` — Already uses compatible contracts
- `WRAPPABLE` — Can wrap with adapter
- `MIGRATE` — Needs contract migration
- `DEFERRED` — Skip for now (with risk)

---

## Parallel Track Classification

| Track | Description | Dependencies | Parallelizable With |
|-------|-------------|--------------|---------------------|
| HTTP Implementation | FastAPI routes using Bridge | Bridge Protocol | SSE, WebSocket |
| SSE Streaming | Implement `stream()` method | Bridge Protocol | HTTP, WebSocket |
| WebSocket Handler | Implement `subscribe()` method | Bridge Protocol | HTTP, SSE |
| marimo Adapter | Bridge adapter for notebooks | HTTP working | — |
| OpenAPI Generation | Auto-generate spec | HTTP routes stable | — |

Classify each:
- `BLOCKING` — Must complete before others
- `PARALLEL` — Can run concurrently
- `DEFERRED` — Wait for stable foundation

---

## Branch Candidates (Surface Now)

| Candidate | Classification | Notes |
|-----------|----------------|-------|
| SaaS billing integration | PARALLEL | Can wire OpenMeter to new endpoints |
| Agent Town NATS bridge | COMPOSITION | Town already has NATS; unify with AUP |
| TUI remote mode | DEFERRED | TUI works locally; remote is enhancement |
| React example components | PARALLEL | Can prototype while HTTP settles |

---

## Non-Goals (This Phase)

- Writing implementation code (that's IMPLEMENT phase)
- Running tests (that's TEST phase)
- Performance benchmarks (that's MEASURE phase)
- User documentation (that's EDUCATE phase)

---

## Actions

1. **Read existing API files** to understand current patterns
2. **Map contract alignment** for each subsystem
3. **Classify parallel tracks** for implementation
4. **Surface blockers** that require resolution
5. **Document synergy map** in plan or epilogue
6. **Update phase ledger** in `plans/agentese-universal-protocol.md`

---

## Exit Checklist

- [ ] Synergy map completed for all 5 subsystems
- [ ] Parallel tracks classified (BLOCKING/PARALLEL/DEFERRED)
- [ ] Composition hooks identified (functor/operad alignment)
- [ ] Blockers surfaced with owners
- [ ] Skip declarations documented with risk
- [ ] Ledger updated: `CROSS-SYNERGIZE: touched`

---

## Continuation Imperative

Upon completing this phase, emit the auto-inducer signifier for the next phase.

---

## Auto-Inducer

Upon successful completion of CROSS-SYNERGIZE phase:

```
⟿[IMPLEMENT]
/hydrate
handles: plan=plans/agentese-universal-protocol; synergy_map=plans/_epilogues/2025-12-14-aup-cross-synergize.md; contracts=protocols/api/serializers.py; bridge=protocols/api/bridge.py; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched,STRATEGIZE:touched,CROSS-SYNERGIZE:touched,IMPLEMENT:in_progress}; entropy=0.04
mission: implement AgenteseBridge backed by Logos; wire HTTP endpoints; add SSE streaming for soul/challenge; create FastAPI router.
exit: bridge implementation tested; HTTP endpoints responding; continuation → QA.
```

Or if synergies require design changes:

```
⟂[BLOCKED:contract_mismatch] Existing API contracts conflict with new serializers. Requires decision: migrate or adapt?
```

---

*"Composition is not about combining things. It's about discovering they were always meant to fit."*
